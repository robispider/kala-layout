"""Repeatable empirical pipeline, with explicit pilot and split gates."""
from collections import Counter, defaultdict
import gzip
import io
import json
import csv
from pathlib import Path
import re

from .paths import DATA, PROJECT_ROOT, hash_outputs, output_path, repo_state, write_json, write_text, gzip_text_writer
from .usage_metric import LIMIT, audit_dataset, require, strict_json, _csv
from .usage_registry import DEFAULT as REGISTRY, digest, load as load_registry
from .usage_features import SCHEMAS, VERSION as FEATURES, POSITION_VERSION, ASSIGNMENT, extract, coverage
from .usage_fit import VERSION as FIT, evaluate, correction_baseline

VERSION = "usage-empirical-v1"
POLICY = DATA / "usage-metric-policy-v1.json"
STRATUM = ("protocol_version", "prompt_bank_version", "build_configuration", "engine_version")


def pilot_gate(evidence, policy):
    if not evidence: return ["observed_pilot_pending"]
    reasons = []
    if evidence.get("methodology") != policy["methodology"]: reasons.append("pilot_methodology_mismatch")
    valid_hash = lambda value: isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None
    if not valid_hash(evidence.get("release_build_sha256")) or not evidence.get("observer"): reasons.append("pilot_build_or_observer_missing")
    if evidence.get("status") != "observed_pass": reasons.append("pilot_not_observed_pass")
    scenarios = evidence.get("scenarios", [])
    for required in policy["required_scenarios"]:
        rows = [s for s in scenarios if s.get("scenario") == required]
        if not rows or not all(r.get("status") == "observed_pass" and r.get("observer") and valid_hash(r.get("evidence_sha256")) for r in rows):
            reasons.append("pilot_scenario_pending:" + required)
    return reasons


def gates(rows, sessions, registry, policy, pilot_reasons):
    reasons = list(pilot_reasons)
    counts = Counter(r["contributor_id"] for r in rows)
    if len(counts) < policy["minimum_contributors"]: reasons.append("too_few_independent_contributors")
    session_counts = Counter(s["contributor_id"] for s in sessions)
    if not session_counts or any(session_counts[cid] < policy["minimum_sessions_per_contributor"] for cid in counts):
        reasons.append("contributor_session_replication_floor")
    if not counts or min(counts.values()) < policy["minimum_intervals_per_contributor"]: reasons.append("contributor_interval_floor")
    families = {r["family"] for r in rows if r["family"]}
    if len(families) < policy["minimum_families"]: reasons.append("too_few_prompt_families")
    if any(r["family"] is None for r in rows): reasons.append("unresolved_prompt_family")
    if registry.get("family_review", {}).get("status") != "reviewed": reasons.append("near_duplicate_family_review_pending")
    if any(s["mapping_status"] != "verified_mapping" for s in sessions): reasons.append("mapping_registry_incomplete")
    if any(m["engine_rules_status"] != "validated_replay" for m in registry["mappings"] if any(s["mapping_hash"] == m["mapping_hash"] and s["engine_version"] == m["engine_version"] for s in sessions)):
        reasons.append("engine_replay_validation_pending")
    return sorted(set(reasons))


def _check_inputs(inputs, dataset):
    for name, expected in inputs.items():
        path = (dataset / name[len("dataset/"):]) if name.startswith("dataset/") else PROJECT_ROOT / name
        require(path.is_file() and digest(path.read_bytes()) == expected, "analysis snapshot changed or withdrawn; rebuild")


def build(dataset=DATA / "usage-metric-dataset", out=PROJECT_ROOT / "results/usage-metric-pipeline-v1",
          registry_path=REGISTRY, policy_path=POLICY, pilot_path=None, fit=False):
    dataset, out = Path(dataset).resolve(), output_path(Path(out) / "result.json").parent
    require(not fit or not (out / "run-manifest.json").exists(), "fit runs are immutable; choose a new run directory")
    audit, _, _, _ = audit_dataset(dataset)
    require(not audit["errors"], "audit failed; no features or model may be released")
    registry, inputs = load_registry(registry_path)
    inputs.update({"dataset/"+name: value for name, value in audit["input_sha256"].items()})
    policy_path = Path(policy_path).resolve()
    policy_raw = policy_path.read_bytes(); policy = strict_json(policy_raw)
    require(policy["schema"] == "kala.usage-metric.policy/1" and policy["idle_seconds"] == 30 and policy["folds"] >= 2,
            "unsupported empirical policy")
    inputs[policy_path.relative_to(PROJECT_ROOT).as_posix()] = digest(policy_raw)
    pilot = None
    if pilot_path:
        pilot_path = Path(pilot_path).resolve(); raw = pilot_path.read_bytes(); pilot = strict_json(raw)
        inputs[pilot_path.relative_to(PROJECT_ROOT).as_posix()] = digest(raw)
    pilot_reasons = pilot_gate(pilot, policy)
    tables = {name: [] for name in SCHEMAS}
    manifest = strict_json((dataset / "manifest.json").read_bytes())
    metadata = {s["session_id"]: s for s in audit["sessions"]}
    for entry in manifest["sessions"]:
        compressed = (dataset / entry["path"]).read_bytes()
        require(digest(compressed) == entry["package_sha256"], "package changed after audit")
        with gzip.GzipFile(fileobj=io.BytesIO(compressed)) as stream: raw = stream.read(LIMIT + 1)
        require(len(raw) <= LIMIT, "expanded package exceeds limit")
        package = strict_json(raw)
        if package["schema"] == "kala.typing-check.session/2":
            continue  # Separately audited, not compatible with the /1 feature/model contract.
        derived = extract(package, metadata[entry["session_id"]], registry)
        for name in tables: tables[name].extend(derived[name])
    matrix = coverage(tables)
    prompt_lengths = {(p["session_id"], p["prompt_order"]): p["target_codepoints"] for p in tables["prompts"]}
    strata, session_strata = defaultdict(list), defaultdict(list)
    for s in tables["sessions"]: session_strata[tuple(s[n] for n in STRATUM)].append(s)
    for r in tables["intervals"]:
        if r["decision"] == "accepted":
            r = dict(r, target_codepoints=prompt_lengths[r["session_id"], r["prompt_order"]])
            strata[tuple(r[n] for n in STRATUM)].append(r)
    results, predictions = [], []
    for identity, sessions in sorted(session_strata.items()):
        rows = strata[identity]
        reasons = gates(rows, sessions, registry, policy, pilot_reasons)
        result = {"stratum": dict(zip(STRATUM, identity)), "contributors": len({r["contributor_id"] for r in rows}),
                  "eligible_intervals": len(rows), "gate_reasons": reasons,
                  "status": "insufficient_data" if reasons else "ready_for_experimental_fit"}
        if fit and not reasons:
            fitted, pred = evaluate(rows, policy)
            result["interval_model"] = fitted; result["status"] = fitted["status"]
            outcomes = [r for r in tables["outcomes"] if tuple(r[n] for n in STRATUM) == identity]
            result["correction_baseline"] = correction_baseline(outcomes, policy)
            predictions.extend(dict(p, stratum=digest(json.dumps(identity).encode())) for p in pred)
        results.append(result)
    snapshot = digest(json.dumps(inputs, sort_keys=True, separators=(",", ":")).encode())
    status = "insufficient_data" if not results or all(r["gate_reasons"] for r in results) else (
        "experimental_fit" if any(r["status"] == "experimental_fit" for r in results) else
        "validation_failed" if any(r["status"] == "validation_failed" for r in results) else
        "insufficient_data" if fit else "audit_only")
    record = {"schema": "kala.usage-metric.empirical/1", "version": VERSION, "snapshot_sha256": snapshot,
              "status": status,
              "fit_requested": fit, "training_performed": any("interval_model" in r for r in results),
              "collection_audit": {"sessions_excluded_from_model": len(audit["collection_sessions"]),
                                   "reason": "collection_v2_audit_only", "model_eligible": False},
              "strata": results, "pilot_gate_reasons": pilot_reasons, "coverage": matrix,
              "policy": policy, "features": FEATURES, "position_resolver": POSITION_VERSION,
              "finger_assignment": ASSIGNMENT, "registry_sha256": digest(Path(registry_path).read_bytes()),
              "input_sha256": inputs,
              "limitations": ["No layout comparison, population validation or comfort claim.",
                              "Observed pilot and historical mapping/engine recovery still require evidence.",
                              "Correction baseline predicts observed correction actions, not latent symbol errors.",
                              "Primary intervals exclude spaces and multi-codepoint composition; excluded strata remain in canonical tables."]}
    _check_inputs(inputs, dataset)
    paths = []
    for name, rows in tables.items():
        path = output_path(out / (name + ".csv.gz"))
        with gzip_text_writer(path) as stream:
            writer = csv.DictWriter(stream, fieldnames=SCHEMAS[name]); writer.writeheader(); writer.writerows(rows)
        paths.append(path)
    paths += [write_json(out / "result.json", record), write_json(out / "snapshot.json", {"snapshot_sha256": snapshot, "input_sha256": inputs}),
              write_json(out / "model.json", {"status": record["status"], "snapshot_sha256": snapshot,
                                             "models": [r for r in results if r["status"] == "experimental_fit"]}),
              write_json(out / "predictions.json", predictions)]
    card = {"schema": "kala.usage-metric.model-card/1", "status": record["status"], "training_performed": record["training_performed"],
            "snapshot_sha256": snapshot, "targets": ["log down-down seconds", "observed correction-action probability"],
            "prohibited_claims": ["typing speed ranking", "causal layout effect", "measured comfort", "observed fingering"],
            "evaluation_unit": "contributor", "secondary_holdout": "reviewed prompt/source-work family",
            "withdrawal": "Rebuild from current manifest; verify-usage-run rejects stale inputs. Earlier Git history can retain data.",
            "limitations": record["limitations"]}
    paths.append(write_json(out / "model-card.json", card))
    report = ("# Empirical typing pipeline\n\n" + f"Status: **{record['status']}**; training performed: **{record['training_performed']}**.\n\n"
              f"{len(tables['sessions'])} sessions; {len({s['contributor_id'] for s in tables['sessions']})} contributor IDs. "
              f"{matrix['repaired_position_events']} position labels recovered as a derived field; raw labels and packages preserved.\n\n"
              f"Eligible intervals: {matrix['idle_sensitivity']['primary_accepted_intervals']} primary; "
              f"{matrix['idle_sensitivity']['including_idle_sessions']} including idle-flagged sessions. "
              "Recorded score denominators are unchanged.\n\n"
              "Tables include every candidate, its provenance and reasons for exclusion. "
              "Negative flight is retained as key overlap. Modifier/Shift events and autorepeats have separate identities. "
              "The frozen effort column is a physical-key feature, not milliseconds or a new layout score.\n\n"
              "| Protocol | Bank | Build | Eligible contributors | Eligible intervals | Gates |\n| --- | --- | --- | --- | --- | --- |\n")
    for r in results:
        st = r["stratum"]
        report += f"| {st['protocol_version']} | {st['prompt_bank_version']} | {st['build_configuration']} | {r['contributors']} | {r['eligible_intervals']} | {', '.join(r['gate_reasons'])} |\n"
    report += "\nNo model was inferred from the number of keystrokes. Engineering floors are not a sample-size power analysis. "
    report += "Observed physical-key, consent, offline retry, receiver restart and withdrawal scenarios remain required.\n"
    paths.append(write_text(out / "REPORT.md", report))
    commit, clean = repo_state()
    implementation = sorted((PROJECT_ROOT / "src/bangla_dh").glob("usage_*.py")) + [PROJECT_ROOT / "src/bangla_dh/cli.py", PROJECT_ROOT / "src/bangla_dh/paths.py"]
    implementation += sorted((DATA / "unicode/15.0.0").glob("*"))
    implementation += [PROJECT_ROOT / "src/bangla_dh/geometry/keyboards.py", PROJECT_ROOT / "src/bangla_dh/scoring/model.py"]
    implementation += [PROJECT_ROOT / f"results/phase1/effort-grids/{g}-traditional.json" for g in ("ansi", "iso")]
    paths.append(write_json(out / "run-manifest.json", {"phase": VERSION, "commit": commit, "working_tree_clean": clean,
        "input_sha256": inputs, "snapshot_sha256": snapshot, "implementation_sha256": hash_outputs(implementation),
        "parameters": {"policy": policy, "training_requested": fit, "feature_schema": SCHEMAS, "seed": policy['seed']}, "output_sha256": hash_outputs(paths)}))
    return record, paths


def verify_run(run_dir, dataset=DATA / "usage-metric-dataset"):
    manifest = strict_json((Path(run_dir) / "run-manifest.json").read_bytes())
    _check_inputs(manifest["input_sha256"], Path(dataset).resolve())
    for name, expected in {**manifest["output_sha256"], **manifest["implementation_sha256"]}.items():
        path = (PROJECT_ROOT / name).resolve()
        require(path.is_relative_to(PROJECT_ROOT) and path.is_file() and digest(path.read_bytes()) == expected,
                "derived artifact changed; rebuild")
    return True
