"""Experimental fixed-layout adapter and constrained search.

All scores are sums of conditional interval medians, never expected page time.
The current dataset cannot supply a fitted model; no proxy J0/J1 ranking is
substituted when empirical support is absent.
"""
from collections import Counter, defaultdict
import copy
import gzip
import itertools
import json
import math
from pathlib import Path
import statistics
import unicodedata

from .bangla.grammar import Action, Escape, KeyMap
from .bangla.styles import Style
from .paths import PROJECT_ROOT, hash_outputs, output_path, repo_state, write_json, write_text
from .usage_features import geometry, ASSIGNMENT
from .usage_fit import predict, FEATURES
from .usage_metric import require, strict_json
from .usage_pipeline import verify_run
from .usage_registry import digest

VERSION = "usage-layout-evaluator-v1"
REFERENCE = {"elapsed_active_seconds": 120, "session_number": 1, "target_codepoints": 200,
             "previously_seen": False, "repeat_of": None, "stage": "natural-1"}


def _normal(text): return unicodedata.normalize("NFC", text)


def actions(candidate, text):
    """Replay the declared grammar. Escapes never count as reachable typing."""
    require(candidate.get("schema") == "kala.empirical.candidate/1", "unsupported candidate schema")
    kind = candidate["grammar"]
    if kind.startswith("style-"):
        style = Style(kind[-1]); steps = style.encode(_normal(text))
        mapping = candidate["mapping"]
        require(all(v["layer"] in {"base", "shift"} for v in mapping.values()), "unsupported candidate layer")
        slots = [(v["key"], v["layer"]) for v in mapping.values()]
        require(len(slots) == len(set(slots)), "candidate maps different labels to the same slot")
        decoded, pressed = [], []
        for step in steps:
            if isinstance(step, Escape):
                pressed.append(step); decoded.append(step)
            elif step not in mapping:
                pressed.append(Escape(step)); decoded.append(Escape(step))
            else:
                slot = mapping[step]
                pressed.append(Action(slot["key"], slot["layer"], step)); decoded.append(step)
        replay = style.decode(decoded)
        # Prefix replays expose composition replacements as their own stratum.
        def style_prefixes():
            output, last = [], None
            for label in decoded:
                if isinstance(label, Escape): output.append(label.char); last = None
                else: last = style.press(output, last, label)
                yield _normal("".join(output))
        prefixes = style_prefixes()
    else:
        require(kind == "keymap", "grammar adapter unavailable")
        key_actions = [Action(k, layer, output) for layer, mapping in candidate["layers"].items() for k, output in mapping.items() if output]
        require(all(a.layer in {"base", "shift"} for a in key_actions), "unsupported candidate layer")
        keymap = KeyMap("anonymous", sorted(key_actions, key=lambda a: (a.layer, a.key, a.output)), candidate.get("sequences", {}))
        pressed = list(keymap.encode(_normal(text))); replay = keymap.decode(pressed)
        prefixes = (keymap.decode(pressed[:i]) for i in range(1, len(pressed)+1))
    unreachable, ledger, previous, held_shift = [], [], "", None
    positions, _ = geometry(candidate.get("geometry", "ansi"))
    key_positions = {v["name"]: (pos, v) for pos, v in positions.items()}
    for step, current in zip(pressed, prefixes):
        if isinstance(step, Escape) and step.char not in {" ", "\n"}:
            unreachable.append([f"U+{ord(c):04X}" for c in step.char]); previous = current
            ledger.append({"position": None, "kind": "unreachable", "key": None, "left": False, "right": False})
            continue
        if isinstance(step, Escape):
            key, layer = ("SPACE" if step.char == " " else "ENTER"), "base"
        else: key, layer = step.key, step.layer
        info = key_positions.get(key)
        required_shift = None
        if layer == "shift" and info:
            required_shift = "RSHF" if info[1]["finger"] < 5 else "LSHF"
        if required_shift != held_shift:
            held_shift = required_shift
            if held_shift:
                ledger.append({"position": held_shift, "kind": "modifier", "key": held_shift,
                               "left": held_shift == "LSHF", "right": held_shift == "RSHF"})
        common = 0
        while common < min(len(previous), len(current)) and previous[common] == current[common]: common += 1
        removed, inserted = previous[common:], current[common:]
        operation = "space" if key == "SPACE" else "boundary" if key == "ENTER" else "clean" if not removed and len(inserted) == 1 else "composition"
        ledger.append({"position": "SPCE" if key == "SPACE" else "RTRN" if key == "ENTER" else info[0] if info else None,
                       "kind": operation, "key": key, "left": held_shift == "LSHF", "right": held_shift == "RSHF"})
        previous = current
    return {"round_trip": replay == _normal(text), "unreachable": unreachable, "downs": ledger,
            "typing_strategy": "fewest grammar strokes, deterministic key order; opposite-hand Shift held across runs requiring that side",
            "codepoints": len(_normal(text))}


def structural(a, b, kind="ansi"):
    positions, model = geometry(kind)
    pa, pb = positions.get(a["position"]), positions.get(b["position"])
    if not pa or not pb or pa["finger"] is None or pb["finger"] is None: return None
    same = a["position"] == b["position"]
    shift_same = (a["left"], a["right"]) == (b["left"], b["right"])
    return dict(REFERENCE, distance_u=math.hypot(pa["x_u"]-pb["x_u"], pa["y_u"]-pb["y_u"]),
        same_key=same, same_finger=pa["finger"] == pb["finger"], hand_alternation=(pa["finger"] < 5) != (pb["finger"] < 5),
        to_shift_left=b["left"], to_shift_right=b["right"], shift_transition=not shift_same,
        from_row=pa["row"], to_row=pb["row"], frozen_pair_effort=model.effort(pb["name"])+model.penalty_keys(pa["name"], pb["name"], same and shift_same)[1])


def support_key(kind, a, b):
    return json.dumps([kind, a["position"], b["position"], a["left"], a["right"], b["left"], b["right"]], separators=(",", ":"))


def score(candidate, documents, trained, minimum_support=3):
    reasons, breakdown, draws = Counter(), defaultdict(float), []
    total_codepoints = downs = intervals = supported = round_trips = unreachable = 0
    total_ms = 0.0
    bootstraps = trained.get("bootstrap_models", []) if trained else []
    draw_totals = [0.0] * len(bootstraps)
    for text, count in documents:
        trace = actions(candidate, text)
        total_codepoints += trace["codepoints"]*count; downs += len(trace["downs"])*count
        round_trips += trace["round_trip"]*count; unreachable += len(trace["unreachable"])*count
        if not trace["round_trip"]: reasons["round_trip_failure"] += count
        if trace["unreachable"]: reasons["unreachable_codepoints"] += len(trace["unreachable"])*count
        for a, b in zip(trace["downs"], trace["downs"][1:]):
            intervals += count
            row = structural(a, b, candidate.get("geometry", "ansi"))
            clean = a["kind"] == b["kind"] == "clean"
            if not clean: reasons["unsupported_operation:"+a["kind"]+">"+b["kind"]] += count
            if row is None: reasons["unsupported_geometry"] += count
            if trained is None: reasons["no_fitted_empirical_model"] += count; continue
            context = support_key(candidate.get("geometry", "ansi"), a, b)
            coverage = trained.get("support_contributors", {}).get(context, 0)
            if coverage < minimum_support: reasons["insufficient_transition_contributors"] += count
            if not clean or row is None or coverage < minimum_support: continue
            value = predict(trained["final_interval_model"], row)
            require(abs(value) < 50, "unstable layout prediction")
            ms = math.exp(value)*1000*count; total_ms += ms; supported += count
            breakdown[a["position"]+">"+b["position"]] += ms
            for i, model in enumerate(bootstraps):
                log_value = predict(model, row); require(abs(log_value) < 50, "unstable bootstrap prediction")
                draw_totals[i] += math.exp(log_value)*1000*count
    complete = not reasons and intervals > 0 and total_codepoints > 0
    if not intervals: reasons["no_motor_intervals"] += 1
    if not total_codepoints: reasons["empty_benchmark"] += 1
    if complete and len(draw_totals) < 20:
        reasons["score_uncertainty_refits_unavailable"] += 1; complete = False
    modeled = total_ms*1000/total_codepoints if complete else None
    if complete: draws = [x*1000/total_codepoints for x in draw_totals]
    ordered = sorted(draws)
    return {"candidate_sha256": digest(json.dumps(candidate, sort_keys=True, ensure_ascii=False).encode()),
        "status": "experimental_prediction" if complete else "unsupported_contexts" if trained else "insufficient_data",
        "modeled_ms_per_1000_codepoints": modeled, "cost_interpretation": "sum of conditional medians; no log-to-mean correction or reading/learning/fatigue time",
        "downstrokes": downs, "output_codepoints": total_codepoints, "downstrokes_per_codepoint": downs/total_codepoints if total_codepoints else None,
        "motor_intervals": intervals, "supported_intervals": supported, "support_share": supported/intervals if intervals else None,
        "round_trip_documents_weighted": round_trips, "unreachable_units_weighted": unreachable, "exclusions": dict(reasons),
        "transition_breakdown_modeled_ms": dict(sorted(breakdown.items())), "bootstrap_scores": draws,
        "bootstrap_95pct": [ordered[int(.025*len(ordered))], ordered[min(len(ordered)-1,int(.975*len(ordered)))]] if ordered else None,
        "reference_condition": REFERENCE, "finger_assignment": ASSIGNMENT,
        "shift_strategy": "opposite-hand Shift held across adjacent strokes requiring the same side",
        "first_action": "No onset or last-release time predicted; only successive down-down intervals within each document.",
        "error_risk": "unavailable_without_validated_symbol-transfer_model"}


def compare(candidates, reference, documents, trained, minimum_support=3):
    results = {name: score(candidate, documents, trained, minimum_support) for name, candidate in candidates.items()}
    require(reference in results, "reference candidate missing")
    base = results[reference]
    for name, result in results.items():
        value, baseline = result["modeled_ms_per_1000_codepoints"], base["modeled_ms_per_1000_codepoints"]
        result["reference_index"] = value/baseline*100 if value is not None and baseline else None
        pairs = [a-b for a,b in zip(result["bootstrap_scores"], base["bootstrap_scores"])]
        pairs.sort()
        result["difference_95pct_ms_per_1000"] = [pairs[int(.025*len(pairs))], pairs[min(len(pairs)-1,int(.975*len(pairs)))]] if pairs else None
    return results


def search(candidate, search_documents, heldout_documents, trained, locked=(), max_changed=4, steps=10):
    require(candidate["grammar"].startswith("style-"), "swap search requires an explicit style mapping")
    require(not {digest(_normal(t).encode()) for t,_ in search_documents} & {digest(_normal(t).encode()) for t,_ in heldout_documents}, "search and final benchmark overlap")
    baseline = score(candidate, search_documents, trained)
    if baseline["status"] != "experimental_prediction": return {"status": baseline["status"], "baseline": baseline, "candidates": []}
    current, best, retained = copy.deepcopy(candidate), baseline, []
    for iteration in range(steps):
        winner = None
        for a, b in itertools.combinations(sorted(set(candidate["mapping"])-set(locked)), 2):
            trial = copy.deepcopy(current); trial["mapping"][a], trial["mapping"][b] = trial["mapping"][b], trial["mapping"][a]
            changed = [k for k in candidate["mapping"] if trial["mapping"][k] != candidate["mapping"][k]]
            if len(changed) > max_changed: continue
            result = score(trial, search_documents, trained)
            if result["status"] == "experimental_prediction" and result["modeled_ms_per_1000_codepoints"] < best["modeled_ms_per_1000_codepoints"]:
                differences = [x-y for x,y in zip(result["bootstrap_scores"], baseline["bootstrap_scores"])]
                if not differences or max(differences) >= 0: continue  # conservative model-gap guard
                if winner is None or result["modeled_ms_per_1000_codepoints"] < winner[1]["modeled_ms_per_1000_codepoints"]: winner = (trial, result, changed)
        if winner is None: break
        current, best, changed = winner
        retained.append({"iteration": iteration+1, "mapping": current["mapping"], "changed_labels": changed, "search_score": best,
                         "final_benchmark_score": score(current, heldout_documents, trained)})
    return {"status": "experimental_candidates" if retained else "no_supported_improvement", "baseline": baseline, "candidates": retained,
            "constraints": {"locked_labels": list(locked), "max_changed": max_changed, "steps": steps},
            "limitation": "Untouched final text is never used to choose swaps. No layout is published by this command."}


def read_benchmark(path, limit=25):
    require(type(limit) is int and limit > 0, "benchmark limit must be positive")
    path = Path(path); opener = gzip.open if path.suffix == ".gz" else open
    documents = []
    with opener(path, "rt", encoding="utf8") as stream:
        for line in itertools.islice(stream, limit):
            item = strict_json(line)
            require(type(item) is dict, "benchmark object required")
            if type(item.get("text")) is str:
                documents.append((item["text"], 1))
            else:
                require(type(item.get("paragraphs")) is list and all(type(p) is str for p in item["paragraphs"]), "benchmark text/paragraph fields required")
                # Paragraphs are distinct continuous trials, preserving their
                # original strings. Never invent inter-paragraph motor intervals.
                documents.extend((p, 1) for p in item["paragraphs"])
    return documents


def run(candidates, reference, benchmark, fit_run, out, limit=25, search_benchmark=None, locked=(), max_changed=4, steps=10):
    verify_run(fit_run)
    fitted = strict_json((Path(fit_run) / "model.json").read_bytes())
    require(len(fitted["models"]) <= 1, "select a single validated protocol/engine model before transfer scoring")
    trained = fitted["models"][0]["interval_model"] if fitted["models"] else None
    candidate_values, inputs = {}, {}
    for path in candidates:
        path = Path(path).resolve(); raw = path.read_bytes()
        candidate_values[path.stem] = strict_json(raw); inputs[str(path)] = digest(raw)
    require(len(candidate_values) == len(candidates), "duplicate candidate file stems")
    docs = read_benchmark(benchmark, limit); inputs[str(Path(benchmark).resolve())] = digest(Path(benchmark).read_bytes())
    results = compare(candidate_values, reference, docs, trained)
    searched = None
    if search_benchmark:
        source = read_benchmark(search_benchmark, limit)
        inputs[str(Path(search_benchmark).resolve())] = digest(Path(search_benchmark).read_bytes())
        searched = search(candidate_values[reference], source, docs, trained, locked, max_changed, steps)
    out = output_path(Path(out)/"evaluation.json").parent
    record = {"schema": "kala.usage-metric.layout-evaluation/1", "version": VERSION,
              "status": "insufficient_data" if trained is None else "unsupported_contexts" if any(r["modeled_ms_per_1000_codepoints"] is None for r in results.values()) else "experimental", "reference": reference, "results": results, "search": searched,
              "benchmark": {"input_sha256": inputs, "document_limit": limit, "text_hashes": [digest(_normal(t).encode()) for t,_ in docs]},
              "fit_run_sha256": digest((Path(fit_run)/"run-manifest.json").read_bytes()),
              "limitations": ["No empirical ranking without a validated fitted model and complete context support.",
                              "The current clean-interval model cannot price modifier, space and composition intervals.",
                              "The first-25-document default exercises the adapter; it is not a validated final benchmark.",
                              "Alternate fingering and unseen-layout validation remain separate research evidence."]}
    paths = [write_json(out/"evaluation.json", record), write_text(out/"REPORT.md", "# Experimental layout evaluator\n\nStatus: **"+record["status"]+"**.\n\n"
        "All candidates use the same text and reference condition. Round trips, unreachable units, operation strata and missing model support are explicit. "
        "No score or improvement is produced from an unfitted model. No J0/J1 score is substituted. See evaluation.json.\n")]
    commit, clean = repo_state()
    paths.append(write_json(out/"run-manifest.json", {"phase": VERSION, "commit": commit, "working_tree_clean": clean, "input_sha256": inputs,
        "model_run_sha256": record["fit_run_sha256"], "parameters": {"limit": limit, "reference": reference, "search_steps": steps,
            "locked_labels": list(locked), "max_changed": max_changed, "minimum_transition_contributors": 3, "reference_condition": REFERENCE, "seeds": []},
        "implementation_sha256": hash_outputs([Path(__file__), PROJECT_ROOT/"src/bangla_dh/bangla/styles.py", PROJECT_ROOT/"src/bangla_dh/bangla/grammar.py",
            PROJECT_ROOT/"src/bangla_dh/usage_fit.py", PROJECT_ROOT/"src/bangla_dh/usage_features.py"]), "output_sha256": hash_outputs(paths)}))
    return record, paths
