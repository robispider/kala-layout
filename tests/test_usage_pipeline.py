"""Empirical pipeline guards, Unicode conformance, and independent numeric cases."""
import copy
import csv
import gzip
import hashlib
import json
import math
from pathlib import Path
import tempfile
import unittest
import contextlib
import io

from bangla_dh.paths import PROJECT_ROOT, output_path, write_json
from bangla_dh.usage_metric import audit_package, InvalidData, COLUMNS
from bangla_dh.usage_graphemes import ROOT, graphemes
from bangla_dh.usage_scores import calculate, align
from bangla_dh.usage_registry import digest, immutable_json, load, mapping_hash
from bangla_dh.usage_features import extract, POSITION_VERSION, SCHEMAS
from bangla_dh.usage_fit import grouped_folds, ridge, predict, evaluate, correction_baseline, FEATURES
from bangla_dh.usage_pipeline import build, verify_run, POLICY, pilot_gate, gates
from test_usage_metric import fixture


def two_keys():
    p = fixture()
    p["prompts"][0].update(target_text="কখ", final_text="কখ", final_text_nfc="কখ", attempted_units=2)
    p["key_events"]["rows"] = [
        [3, 500, 75, 37, 0, 0, 0, "AC08", 0, 1, 500],
        [5, 550, 70, 33, 0, 0, 0, "AC04", 0, 1, 550],
        [7, 600, 75, 37, 0, 1, 0, "AC08", 0, 1, 600],
        [8, 650, 70, 33, 0, 1, 0, "AC04", 0, 1, 650]]
    p["text_events"].append(dict(p["text_events"][0], seq=6, t=560, key_seq=5, start=1, end=1,
                                 inserted="খ", sel_before=[1, 0], sel_after=[2, 0]))
    p["boundaries"][-2]["seq"] = 9; p["boundaries"][-1]["seq"] = 10
    p["summary"]["anchor_first_wpm5"] = 6
    return p


def registry(p):
    return {"schema": "kala.usage-metric.registry/1", "mappings": [], "protocols": [
        {"protocol": p["session"]["protocol_version"], "bank_version": p["session"]["prompt_bank_version"],
         "prompts": [{"prompt_id": "synthetic", "target_sha256": digest(p["prompts"][0]["target_text"].encode()), "family": "work:synthetic"}]}]}


def derived(p):
    meta = audit_package(p)[0]; meta["package_sha256"] = "a"*64
    return extract(p, meta, registry(p))


class GraphemeTests(unittest.TestCase):
    def test_official_unicode15_conformance_and_source_hashes(self):
        manifest = json.loads((ROOT / "SOURCES.json").read_bytes())
        for name, source in manifest["files"].items():
            self.assertEqual(digest((ROOT / name).read_bytes()), source["sha256"])
        count = 0
        for line in (ROOT / "GraphemeBreakTest.txt").read_text(encoding="utf8").splitlines():
            tokens = line.split("#")[0].split()
            if not tokens: continue
            expected, cluster = [], ""
            for token in tokens:
                if token == "÷":
                    if cluster: expected.append(cluster); cluster = ""
                elif token != "×": cluster += chr(int(token, 16))
            text = "".join(expected)
            self.assertEqual(graphemes(text), expected, f"Unicode case {count}")
            count += 1
        self.assertGreater(count, 500)

    def test_frozen_bangla_joiners_surrogates_and_emoji(self):
        for text, expected in (("", []), ("কি", ["কি"]), ("ক্‍ষ", ["ক্‍", "ষ"]),
                               ("ক্‌ষ", ["ক্‌", "ষ"]), ("ড়", ["ড়"]),
                               ("😀ক", ["😀", "ক"]), ("👨‍👩‍👧", ["👨‍👩‍👧"]),
                               ("🇧🇩🇬🇧🇧", ["🇧🇩", "🇬🇧", "🇧"])):
            self.assertEqual(graphemes(text), expected)

    def test_score_golden_qualification_nfc_and_alignment_ties(self):
        p = two_keys(); p["summary"].update(accuracy=100, correct_gpm=None, first_try_accuracy=100)
        audit_package(p)
        p["summary"]["accuracy"] = 99
        with self.assertRaises(InvalidData): audit_package(p)
        self.assertEqual(align(["a", "b"], ["b", "a"]), (2, 1))
        p = fixture(); p["text_events"][0]["inserted"] = "ড়"
        p["prompts"][0].update(target_text="ড়", final_text="ড়", final_text_nfc="ড়")
        self.assertEqual(calculate(p)[0]["accuracy"], 100)

    def test_attempted_unit_and_segmenter_mutations_fail(self):
        for field, value in (("attempted_units", 0), ("segmenter", "unknown"), ("unicode_version", "16.0")):
            p = fixture(); p["prompts"][0][field] = value
            with self.assertRaises(InvalidData): audit_package(p)

    def test_timeout_scores_only_declared_attempted_prefix(self):
        p = fixture(); p["prompts"][0].update(target_text="কখগ", end_reason="timeout")
        self.assertEqual(calculate(p)[0]["accuracy"], 100)
        p["prompts"][0]["end_reason"] = "enter"
        self.assertAlmostEqual(calculate(p)[0]["accuracy"], 100/3)

    def test_qualified_speed_and_null_summary_are_verified(self):
        p = fixture(); text = "ক"*100
        p["text_events"][0].update(inserted=text, sel_after=[100, 0])
        p["prompts"][0].update(target_text=text, final_text=text, final_text_nfc=text, attempted_units=100, end_ticks=60000)
        for b in p["boundaries"][-2:]: b["t"] = 60000
        p["session"]["active_seconds"] = 60
        p["summary"].update(wpm5=19.8, anchor_first_wpm5=19.8, correct_gpm=100, accuracy=100, first_try_accuracy=100)
        self.assertEqual(audit_package(p)[0]["unverified_summary_fields"], [])
        p["summary"]["wpm5"] = None
        with self.assertRaises(InvalidData): audit_package(p)

    def test_final_accuracy_and_first_try_correction_are_separate(self):
        p = two_keys()
        p["prompts"][0].update(target_text="ক", final_text="ক", final_text_nfc="ক", attempted_units=1)
        p["text_events"][0]["inserted"] = "খ"
        p["text_events"][1].update(op="replace", start=0, end=1, removed="খ", inserted="ক", source="native-key", sel_after=[1, 0])
        p["key_events"]["rows"][1][2:5] = [8, 14, 0]
        p["key_events"]["rows"][3][2:5] = [8, 14, 0]
        p["summary"].update(anchor_first_wpm5=0, backspace_presses=1, correction_episodes=1, accuracy=100, first_try_accuracy=0)
        result = audit_package(p)[0]
        self.assertEqual(result["score_counts"]["first_try_words"], 0)
        self.assertEqual(result["score_counts"]["matched_graphemes"], 1)


class SchemaTests(unittest.TestCase):
    def test_missing_fields_wrong_types_and_unexpected_fields(self):
        cases = [("session", "os_version", 10), ("session", "randomization_seed", True),
                 ("session", "session_number", 0), ("input", "origin", "unknown"),
                 ("clock", "origin_ticks", False), ("session", "started_utc", "2026-10-27T00:00:12Z"),
                 ("session", "quality_flags", ["invented"]), ("summary", "accuracy", True)]
        for section, field, value in cases:
            p = fixture(); p[section][field] = value
            with self.subTest(section=section, field=field), self.assertRaises(InvalidData): audit_package(p)
        for section in ("session", "input", "clock", "integrity"):
            p = fixture(); p[section]["unexpected"] = None
            with self.assertRaises(InvalidData): audit_package(p)

    def test_excessive_json_depth_is_rejected_without_recursion_failure(self):
        from bangla_dh.usage_metric import strict_json
        for depth in (33, 2000):
            with self.assertRaises(InvalidData): strict_json("["*depth + "0" + "]"*depth)


class FeatureTests(unittest.TestCase):
    def test_overlap_and_provenance_no_raw_text(self):
        p = two_keys(); before = copy.deepcopy(p); tables = derived(p)
        pair = tables["intervals"][0]
        self.assertEqual(pair["decision"], "accepted")
        self.assertAlmostEqual(pair["down_down_seconds"], .05)
        self.assertAlmostEqual(pair["flight_seconds"], -.05)
        self.assertEqual((pair["from_seq"], pair["to_seq"]), (3, 5))
        self.assertEqual(p, before)
        self.assertNotIn("কখ", json.dumps(tables, ensure_ascii=False))
        for name, rows in tables.items():
            for row in rows: self.assertEqual(set(row), set(SCHEMAS[name]))

    def test_unknown_source_exact_link_does_not_become_known(self):
        p = two_keys(); p["text_events"][0]["source"] = "unknown"
        tables = derived(p)
        self.assertEqual(tables["intervals"][0]["decision"], "excluded")
        self.assertIn("unknown_or_native_source", tables["intervals"][0]["reasons"])
        self.assertIn("unknown_source", tables["edits"][0]["reasons"])
        self.assertEqual(tables["sessions"][0]["aggregate_decision"], "review")

    def test_modifier_breaks_adjacency_instead_of_being_skipped(self):
        p = two_keys()
        # Insert a physical modifier before the second text action, shifting IDs.
        for stream in (p["key_events"]["rows"],):
            for row in stream:
                if row[0] >= 5: row[0] += 1
        for row in p["text_events"]:
            if row["seq"] >= 5: row["seq"] += 1; row["key_seq"] += 1
        for row in p["boundaries"][-2:]: row["seq"] += 2
        p["key_events"]["rows"].insert(1, [5, 530, 0xA1, 0x36, 1, 0, 0, None, 0, 0, 530])
        p["key_events"]["rows"].append([10, 700, 0xA1, 0x36, 1, 1, 0, None, 0, 0, 700])
        tables = derived(p)
        self.assertEqual(len(tables["intervals"]), 2)
        self.assertTrue(all(r["decision"] == "excluded" for r in tables["intervals"]))
        shift = next(r for r in tables["events"] if r["seq"] == 5)
        self.assertIsNone(shift["raw_position"]); self.assertEqual(shift["derived_position"], "RSHF")
        self.assertEqual(shift["position_rule"], POSITION_VERSION)
        self.assertTrue(next(r for r in tables["events"] if r["seq"] == 6)["shift_right_before"])

    def test_pause_boundary_censors_dwell_and_pairs(self):
        p = two_keys()
        # Extractor segmentation tested independently of semantic audit.
        meta = audit_package(p)[0]; meta["package_sha256"] = "a"*64
        p["boundaries"].insert(2, {"seq": 4.2, "t": 520, "kind": "pause"})
        p["boundaries"].insert(3, {"seq": 4.3, "t": 540, "kind": "resume"})
        tables = extract(p, meta, registry(p))
        self.assertIn("boundary", tables["intervals"][0]["reasons"])
        self.assertTrue(tables["dwell"][0]["censored"])

    def test_idle_is_session_exclusion_and_separate_sensitivity(self):
        p = two_keys(); p["session"]["quality_flags"] = ["idle-over-30s"]
        tables = derived(p)
        self.assertEqual(tables["intervals"][0]["decision"], "excluded")
        self.assertTrue(tables["intervals"][0]["idle_sensitivity_eligible"])
        self.assertEqual(tables["sessions"][0]["active_seconds"], 2)

    def test_repeat_breaks_adjacency_and_dwell_eligibility(self):
        p = two_keys(); meta = audit_package(p)[0]; meta["package_sha256"] = "a"*64
        p["key_events"]["rows"].insert(1, [4.5, 530, 75, 37, 0, 0, 1, "AC08", 0, 1, 530])
        tables = extract(p, meta, registry(p))
        self.assertEqual(len(tables["repeats"]), 1)
        self.assertTrue(all(r["decision"] == "excluded" for r in tables["intervals"]))
        self.assertIn("held_autorepeat", tables["dwell"][0]["reasons"])

    def test_composition_and_spaces_are_retained_but_not_primary(self):
        for text in ("খগ", " "):
            p = two_keys(); p["text_events"][1]["inserted"] = text
            p["text_events"][1]["sel_after"] = [1+len(text), 0]
            p["prompts"][0].update(target_text="ক"+text, final_text="ক"+text, final_text_nfc="ক"+text, attempted_units=len(graphemes("ক"+text)))
            p["summary"]["anchor_first_wpm5"] = len(text)*6
            self.assertEqual(derived(p)["intervals"][0]["decision"], "excluded")


def numeric_rows():
    rows = []
    for cid in range(10):
        for family in range(5):
            for i in range(5):
                distance = i + 1
                row = dict(distance_u=distance, same_key=False, same_finger=i%2==0, hand_alternation=i%2==1,
                    to_shift_left=False, to_shift_right=False, shift_transition=False, from_row=1, to_row=2,
                    elapsed_active_seconds=i*10, session_number=1, target_codepoints=100, previously_seen=False, repeat_of=None,
                    frozen_pair_effort=1+distance/10, stage="natural-1", log_down_down_seconds=-2+.1*distance,
                    down_down_seconds=math.exp(-2+.1*distance), contributor_id=f"c{cid}", family=f"f{family}",
                    package_sha256="a"*64, session_id=f"s{cid}", prompt_order=family, from_seq=i*2, to_seq=i*2+1,
                    from_position="AC08", to_position="AC04", from_shift_left=False, from_shift_right=False, geometry="ansi")
                rows.append(row)
    return rows


class FittingTests(unittest.TestCase):
    def test_contributor_and_family_folds_never_leak(self):
        rows = numeric_rows()
        for group in ("contributor_id", "family"):
            first, assignment = grouped_folds(rows, group, 5, 42)
            self.assertEqual(assignment, grouped_folds(rows[::-1], group, 5, 42)[1])
            for train, test in first:
                self.assertFalse({r[group] for r in train} & {r[group] for r in test})

    def test_regularized_fit_learns_only_training_statistics(self):
        train = numeric_rows(); model = ridge(train, .001, ["distance_u", "to_shift_left"])
        row = dict(train[0], distance_u=9)
        self.assertAlmostEqual(predict(model, row), -1.1, places=3)
        self.assertIn("to_shift_left", model["unsupported_features"])
        self.assertIsNone(model["coefficients"]["to_shift_left"])
        mean = model["means"][0]; row["distance_u"] = 100000
        predict(model, row)
        self.assertEqual(model["means"][0], mean)

    def test_full_synthetic_grouped_evaluation_beats_median(self):
        policy = json.loads(POLICY.read_bytes()); policy["minimum_intervals_per_fold"] = 1
        result, predictions = evaluate(numeric_rows(), policy)
        self.assertEqual(result["status"], "experimental_fit")
        for axis in ("contributor_id", "family"):
            metrics = result["evaluations"][axis]["metrics"]
            self.assertLess(metrics["additive_ridge"]["participant_weighted_log_mae"], metrics["training_median"]["participant_weighted_log_mae"])
            self.assertEqual(metrics["additive_ridge"]["bootstrap_unit"], "contributor")
        self.assertEqual(len(predictions), len(numeric_rows())*6)

    def test_pilot_gate_rejects_synthetic_success_without_observation(self):
        policy = json.loads(POLICY.read_bytes())
        self.assertTrue(pilot_gate(None, policy))
        fake = {"status": "tests_passed", "methodology": policy["methodology"], "scenarios": []}
        self.assertIn("pilot_not_observed_pass", pilot_gate(fake, policy))

    def test_correction_baseline_stays_separate_and_grouped(self):
        policy = json.loads(POLICY.read_bytes()); policy["minimum_contributors"] = 10; rows = []
        for r in numeric_rows(): rows.append(dict(r, decision="accepted", correction_observed=r["from_seq"]%4==0))
        result = correction_baseline(rows, policy)
        self.assertEqual(result["target"], "observed_correction_action")
        self.assertGreater(result["participant_weighted_brier"], 0)

    def test_no_validation_gain_does_not_release_transfer_model(self):
        policy = json.loads(POLICY.read_bytes()); policy["minimum_intervals_per_fold"] = 1
        rows = numeric_rows()
        for r in rows: r["log_down_down_seconds"] = -2; r["down_down_seconds"] = math.exp(-2)
        result, _ = evaluate(rows, policy)
        self.assertEqual(result["status"], "validation_failed")
        self.assertNotIn("final_interval_model", result)


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        root = output_path(PROJECT_ROOT / "work/usage-pipeline-tests/placeholder").parent
        self.temp = tempfile.TemporaryDirectory(dir=root); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name); self.dataset = self.root / "dataset"
        self.p = two_keys()
        relative = f"sessions/{self.p['session']['contributor_id']}/{self.p['session']['session_id']}.json.gz"
        raw = gzip.compress(json.dumps(self.p).encode(), mtime=0)
        output_path(self.dataset / relative).write_bytes(raw)
        self.entry = dict(path=relative, contributor_id=self.p['session']['contributor_id'], session_id=self.p['session']['session_id'],
                          package_sha256=digest(raw), size_bytes=len(raw), git_blob_sha=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest())
        self.manifest = {"schema": "kala.usage-metric.dataset/1", "session_schema": self.p["schema"], "sessions": [self.entry]}
        write_json(self.dataset / "manifest.json", self.manifest)
        self.registry = self.root / "registry.json"; write_json(self.registry, registry(self.p))

    def test_no_fit_with_small_sample_and_all_artifact_hashes(self):
        record, _ = build(self.dataset, self.root / "out", self.registry, fit=True)
        self.assertEqual(record["status"], "insufficient_data")
        self.assertFalse(record["training_performed"])
        self.assertTrue(verify_run(self.root / "out", self.dataset))
        write_json(self.root / "out/model.json", {"tampered": True})
        with self.assertRaises(InvalidData): verify_run(self.root / "out", self.dataset)

    def test_collection_manifest_retains_snapshot_but_never_enters_legacy_model(self):
        from test_usage_collection_v2 import collection_fixture
        package = collection_fixture()
        relative = self.entry["path"]
        raw = gzip.compress(json.dumps(package).encode(), mtime=0)
        output_path(self.dataset / relative).write_bytes(raw)
        self.entry.update(session_schema=package["schema"], size_bytes=len(raw), package_sha256=digest(raw),
                          git_blob_sha=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest())
        write_json(self.dataset / "manifest.json", {"schema": "kala.usage-metric.dataset/2",
                   "session_schemas": [package["schema"]], "sessions": [self.entry]})
        record, _ = build(self.dataset, self.root / "collection-out", self.registry, fit=True)
        self.assertEqual(record["collection_audit"]["sessions_excluded_from_model"], 1)
        self.assertFalse(record["training_performed"])
        self.assertFalse(record["collection_audit"]["model_eligible"])
        self.assertEqual(record["strata"], [])
        self.assertTrue(verify_run(self.root / "collection-out", self.dataset))

    def test_withdrawal_invalidates_snapshot_and_refresh_clears_rows(self):
        build(self.dataset, self.root / "out", self.registry)
        self.manifest["sessions"] = []; write_json(self.dataset / "manifest.json", self.manifest)
        (self.dataset / self.entry["path"]).unlink()
        with self.assertRaises(InvalidData): verify_run(self.root / "out", self.dataset)
        record, _ = build(self.dataset, self.root / "refreshed", self.registry, fit=True)
        self.assertEqual(record["coverage"]["denominators"]["events"]["raw_rows"], 0)
        self.assertEqual(json.loads((self.root / "refreshed/model.json").read_bytes())["models"], [])
        for name in SCHEMAS:
            with gzip.open(self.root / "refreshed" / (name + ".csv.gz"), "rt", encoding="utf8") as stream:
                reader = csv.DictReader(stream)
                self.assertEqual(reader.fieldnames, SCHEMAS[name]); self.assertEqual(list(reader), [])

    def test_registry_is_immutable_and_alt_style_hash_uses_client_convention(self):
        p = self.root / "immutable.json"
        immutable_json(p, {"a": 1}); immutable_json(p, {"a": 1})
        with self.assertRaises(InvalidData): immutable_json(p, {"a": 2})
        raw = b'{"layers":{}}'
        expected = digest((digest(raw)+":avro-old").encode())
        self.assertEqual(mapping_hash(raw, "avro-modern", "avro-old"), "sha256:"+expected)
        self.assertEqual(mapping_hash(raw, "avro-modern", "avro-modern"), "sha256:"+digest(raw))

    def test_registry_verifies_actual_file_bytes_and_identity(self):
        raw = b'{"layers":{}}'; write_json(self.root / "mapping.json", {"layers": {}})
        # Preserve exact bytes for the client's hash convention.
        output_path(self.root / "mapping.json").write_bytes(raw)
        reg = registry(self.p)
        reg["mappings"] = [dict(mapping_hash=mapping_hash(raw, "native", "native"), engine_version="e", status="verified_mapping",
            file="mapping.json", file_sha256=digest(raw), default_style="native", style="native", mapping={"layers": {}})]
        write_json(self.registry, reg); load(self.registry)
        output_path(self.root / "mapping.json").write_bytes(b'{}')
        with self.assertRaises(InvalidData): load(self.registry)

    def test_fit_cli_returns_two_for_insufficient_data_and_one_for_reuse(self):
        from bangla_dh.cli import main
        args = ["fit-usage-model", "--dataset", str(self.dataset), "--registry", str(self.registry), "--out", str(self.root / "cli-run")]
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(args), 2)
            self.assertEqual(main(args), 1)


if __name__ == "__main__": unittest.main()
