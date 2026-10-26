"""Adversarial tests for received measurements; fixtures contain synthetic text."""
import copy
import gzip
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from bangla_dh.paths import PROJECT_ROOT, output_path, write_json
from bangla_dh.usage_metric import (
    COLUMNS, InvalidData, active_seconds, apply_edit, audit_dataset, audit_package,
    pauses, run, strict_json, utf16_index, wpm5,
)


def fixture():
    return {
        "schema": "kala.typing-check.session/1",
        "session": {"contributor_id": "c_" + "1"*32, "session_id": "s_" + "2"*32,
                    "session_number": 1, "protocol_version": "test-1", "prompt_bank_version": "1.0",
                    "variant_id": "v01", "started_utc": "2026-10-27T00:00Z", "kala_version": "test",
                    "build_configuration": "Debug", "geometry": "ansi", "keyboard_category": "external",
                    "completion": "completed", "active_seconds": 2, "quality_flags": []},
        "input": {"layout_id": "test-fixed", "layout_name": "test", "mapping_hash": "sha256:" + "3"*64,
                  "input_family": "fixed", "engine_version": "test", "composition_only": True,
                  "autocorrect_enabled": False, "spelling_correction_enabled": False,
                  "suggestions_enabled": False, "spelling_marks_enabled": False, "personal_rules_enabled": False},
        "clock": {"frequency": 1000, "origin_ticks": 0},
        "prompts": [{"order": 0, "prompt_id": "synthetic", "target_text": "ক", "final_text": "ক",
                     "final_text_nfc": "ক", "stage": "natural-1", "measured": True, "attempted_units": 1,
                     "shown_ticks": 0, "first_key_ticks": 500, "end_ticks": 2000, "end_reason": "enter"}],
        "key_events": {"columns": COLUMNS[:], "rows": [
            [3, 500, 75, 37, 0, 0, 0, "AC08", 0, 1, 500],
            [5, 600, 75, 37, 0, 1, 0, "AC08", 0, 1, 600]]},
        "text_events": [{"seq": 4, "t": 510, "op": "insert", "start": 0, "end": 0,
                         "removed": "", "inserted": "ক", "sel_before": [0, 0], "sel_after": [1, 0],
                         "source": "kala-delivery", "link": "exact", "key_seq": 3, "correction": None}],
        "boundaries": [{"seq": 1, "t": 0, "kind": "start"},
                       {"seq": 2, "t": 0, "kind": "prompt-shown", "prompt_order": 0},
                       {"seq": 6, "t": 2000, "kind": "prompt-ended", "prompt_order": 0},
                       {"seq": 7, "t": 2000, "kind": "timeout"}],
        "summary": {"wpm5": None, "backspace_presses": 0, "correction_episodes": 0,
                    "anchor_first_wpm5": 0, "anchor_repeat_wpm5": None},
        "integrity": {"text_replay_ok": True, "dropped_events": 0, "injected_events_seen": 0},
    }


class MeasurementTests(unittest.TestCase):
    def assertInvalid(self, mutate):
        package = fixture()
        mutate(package)
        with self.assertRaises((InvalidData, KeyError, TypeError)):
            audit_package(package)

    def test_valid_bangla_replay_and_dwell(self):
        result, prompts, dwell, pairs = audit_package(fixture())
        self.assertEqual(result["warnings"], [])
        self.assertAlmostEqual(dwell[0]["seconds"], .1)
        self.assertEqual(prompts[0]["final_codepoints"], 1)
        self.assertEqual(pairs, [])

    def test_utf16_astral_offsets_and_surrogate_split(self):
        self.assertEqual(utf16_index("ক😀খ", 3), 2)
        with self.assertRaises(InvalidData):
            utf16_index("ক😀খ", 2)
        edit = dict(start=1, end=3, removed="😀", inserted="গ", op="replace",
                    sel_before=[1, 2], sel_after=[2, 0])
        self.assertEqual(apply_edit("ক😀খ", edit), "কগখ")

    def test_selection_does_not_mutate_text(self):
        edit = dict(start=0, end=0, removed="", inserted="", op="selection", sel_before=[0, 0], sel_after=[0, 1])
        self.assertEqual(apply_edit("ক", edit), "ক")
        edit["inserted"] = "খ"
        with self.assertRaises(InvalidData):
            apply_edit("ক", edit)

    def test_replay_removed_text_and_final_text(self):
        self.assertInvalid(lambda p: p["text_events"][0].update(removed="খ"))
        self.assertInvalid(lambda p: p["prompts"][0].update(final_text="খ"))
        self.assertInvalid(lambda p: p["text_events"][0].update(sel_after=[2, 0]))

    def test_nfc_decomposed_nukta(self):
        p = fixture()
        p["text_events"][0].update(inserted="ড়")
        p["prompts"][0].update(final_text="ড়", final_text_nfc="ড়")
        audit_package(p)
        p["prompts"][0]["final_text_nfc"] = "ড়"
        with self.assertRaises(InvalidData):
            audit_package(p)

    def test_key_links_must_exist_and_precede_edit(self):
        self.assertInvalid(lambda p: p["text_events"][0].update(key_seq=100))
        self.assertInvalid(lambda p: p["text_events"][0].update(key_seq=5))
        self.assertInvalid(lambda p: p["text_events"][0].update(key_seq=None))

    def test_duplicate_seq_and_global_clock_reversal(self):
        self.assertInvalid(lambda p: p["text_events"][0].update(seq=3))
        self.assertInvalid(lambda p: p["text_events"][0].update(t=490))

    def test_boundary_and_first_key_consistency(self):
        self.assertInvalid(lambda p: p["prompts"][0].update(end_ticks=1999))
        self.assertInvalid(lambda p: p["prompts"][0].update(first_key_ticks=501))
        self.assertInvalid(lambda p: p["boundaries"].pop(1))

    def test_disabled_assistance_and_boolean_types(self):
        self.assertInvalid(lambda p: p["input"].update(autocorrect_enabled=True))
        self.assertInvalid(lambda p: p["input"].update(composition_only=1))
        self.assertInvalid(lambda p: p["clock"].update(frequency=True))
        self.assertInvalid(lambda p: p["key_events"]["rows"][0].__setitem__(5, False))

    def test_duration_is_independently_checked(self):
        self.assertInvalid(lambda p: p["session"].update(active_seconds=3))

    def test_wpm_scalar_definition(self):
        self.assertEqual(wpm5("ক😀খ", 60), .4)
        self.assertIsNone(wpm5("ক", 0))
        self.assertInvalid(lambda p: p["summary"].update(anchor_first_wpm5=10))
        self.assertInvalid(lambda p: p["summary"].update(backspace_presses=1))
        self.assertInvalid(lambda p: p["summary"].update(correction_episodes=1))

    def test_pause_clipping_and_unclosed_terminal_pause(self):
        b = [{"kind": "pause", "t": 2}, {"kind": "resume", "t": 4},
             {"kind": "pause", "t": 8}, {"kind": "stop", "t": 10}]
        self.assertEqual(active_seconds(0, 10, 1, pauses(b)), 6)
        self.assertEqual(active_seconds(3, 9, 1, pauses(b)), 4)
        with self.assertRaises(InvalidData):
            pauses([{"kind": "resume", "t": 1}])

    def test_future_repeat_reference_is_rejected(self):
        self.assertInvalid(lambda p: p["prompts"][0].update(repeat_of=0))

    def test_quality_flags_and_unknown_sources_remain_visible(self):
        p = fixture()
        p["session"]["quality_flags"] = ["focus-loss"]
        p["text_events"][0]["source"] = "unknown"
        row = audit_package(p)[0]
        self.assertIn("unattributed_text_edits", row["warnings"])
        self.assertEqual(row["quality_flags"], ["focus-loss"])

    def test_hook_clock_unsigned_rollover(self):
        p = fixture()
        p["key_events"]["rows"][0][10] = 2**32 - 50
        p["key_events"]["rows"][1][10] = 50
        row = audit_package(p)[0]
        self.assertEqual(row["timing_counts"]["clock_disagreements_over_250ms"], 0)

    def test_no_interval_crosses_prompt_or_pause(self):
        p = fixture()
        # Two keydowns separated by pause/resume must produce no pair/dwell.
        p["key_events"]["rows"].extend([[8, 800, 70, 33, 0, 0, 0, "AC04", 0, 1, 800],
                                          [11, 1000, 70, 33, 0, 1, 0, "AC04", 0, 1, 1000]])
        p["boundaries"] = p["boundaries"][:2] + [
            {"seq": 9, "t": 850, "kind": "pause"}, {"seq": 10, "t": 950, "kind": "resume"},
            {"seq": 12, "t": 2000, "kind": "prompt-ended", "prompt_order": 0},
            {"seq": 13, "t": 2000, "kind": "timeout"}]
        p["session"]["active_seconds"] = 1.9
        row, _, dwell, pairs = audit_package(p)
        self.assertEqual(len(dwell), 1)
        self.assertEqual(row["timing_counts"]["unmatched_keyups"], 1)
        self.assertEqual(len(pairs), 1)  # 500 -> 800 occurs before pause.

    def test_strict_json(self):
        for raw in ('{"a": 1, "a": 2}', '{"a": NaN}', '{"a": Infinity}', '{"a": 1e999}'):
            with self.assertRaises(InvalidData):
                strict_json(raw)

    def test_missing_right_shift_position_is_visible(self):
        p = fixture()
        p["key_events"]["rows"][0][2:5] = [0xA1, 0x36, 1]
        p["key_events"]["rows"][1][2:5] = [0xA1, 0x36, 1]
        p["key_events"]["rows"][0][7] = None
        p["key_events"]["rows"][1][7] = None
        row = audit_package(p)[0]
        self.assertEqual(row["timing_counts"]["right_shift_unknown_position_events"], 2)
        self.assertIn("unknown_physical_positions", row["warnings"])

    def test_dropped_events_are_not_a_clean_pass(self):
        p = fixture()
        p["integrity"]["dropped_events"] = 1
        self.assertIn("dropped_or_injected_events", audit_package(p)[0]["warnings"])


class DatasetAuditTests(unittest.TestCase):
    def setUp(self):
        scratch = output_path(PROJECT_ROOT / "work" / "usage-audit-tests" / "placeholder").parent
        self.temp = tempfile.TemporaryDirectory(dir=scratch)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.package = fixture()
        self.entry = self.store(self.package)

    def store(self, package):
        sid, cid = package["session"]["session_id"], package["session"]["contributor_id"]
        relative = f"sessions/{cid}/{sid}.json.gz"
        raw = gzip.compress(json.dumps(package, ensure_ascii=False).encode(), mtime=0)
        output_path(self.root / relative).write_bytes(raw)
        entry = dict(session_id=sid, contributor_id=cid, path=relative, size_bytes=len(raw),
                     package_sha256=hashlib.sha256(raw).hexdigest(),
                     git_blob_sha=hashlib.sha1(b"blob " + str(len(raw)).encode()+b"\0"+raw).hexdigest())
        self.manifest = {"schema": "kala.usage-metric.dataset/1", "session_schema": package["schema"], "sessions": [entry]}
        self.save()
        return entry

    def save(self):
        write_json(self.root / "manifest.json", self.manifest)

    def test_audit_is_read_only_and_repeatable(self):
        before = (self.root / self.entry["path"]).read_bytes()
        first = audit_dataset(self.root)
        self.assertEqual(first, audit_dataset(self.root))
        self.assertEqual(first[0]["valid_sessions"], 1)
        self.assertEqual(before, (self.root / self.entry["path"]).read_bytes())

    def test_size_hash_and_git_blob(self):
        for field, value in (("size_bytes", 1), ("package_sha256", "0"*64), ("git_blob_sha", "0"*40)):
            old = self.entry[field]
            self.entry[field] = value
            self.save()
            result = audit_dataset(self.root)[0]
            self.assertEqual(len(result["errors"]), 1)
            self.assertEqual(result["valid_sessions"], 0)
            self.entry[field] = old

    def test_duplicate_manifest_session(self):
        self.manifest["sessions"].append(copy.deepcopy(self.entry))
        self.save()
        self.assertTrue(audit_dataset(self.root)[0]["errors"])

    def test_traversal_and_identity(self):
        self.entry["path"] = "../outside.json.gz"
        self.save()
        self.assertTrue(audit_dataset(self.root)[0]["errors"])
        self.entry["path"] = f"sessions/{self.entry['contributor_id']}/{self.entry['session_id']}.json.gz"
        self.entry["session_id"] = "s_" + "4"*32
        self.save()
        self.assertTrue(audit_dataset(self.root)[0]["errors"])

    def test_unlisted_packages_and_withdrawal_refresh(self):
        self.manifest["sessions"] = []
        self.save()
        self.assertTrue(audit_dataset(self.root)[0]["errors"])
        (self.root / self.entry["path"]).unlink()
        result = audit_dataset(self.root)[0]
        self.assertFalse(result["errors"])
        self.assertEqual(result["contributors"], 0)
        self.assertEqual(result["status"], "no_data")
        _, paths = run(self.root, self.root / "empty-out")
        prompt_csv = next(p for p in paths if p.name == "prompts.csv")
        self.assertIn("target_sha256", prompt_csv.read_text())

    def test_corrupt_gzip_and_wrong_payload_identity(self):
        # Change the payload but recompute transport hashes: semantic checks must
        # still catch it after the byte checks succeed.
        path = self.root / self.entry["path"]
        for raw in (b"not gzip", gzip.compress(json.dumps(dict(self.package, schema="wrong")).encode())):
            output_path(path).write_bytes(raw)
            self.entry.update(size_bytes=len(raw), package_sha256=hashlib.sha256(raw).hexdigest(),
                              git_blob_sha=hashlib.sha1(b"blob " + str(len(raw)).encode()+b"\0"+raw).hexdigest())
            self.save()
            self.assertEqual(audit_dataset(self.root)[0]["valid_sessions"], 0)

    def test_expanded_size_limit(self):
        raw = gzip.compress(b" " * (2 * 1024 * 1024 + 1))
        output_path(self.root / self.entry["path"]).write_bytes(raw)
        self.entry.update(size_bytes=len(raw), package_sha256=hashlib.sha256(raw).hexdigest(),
                          git_blob_sha=hashlib.sha1(b"blob " + str(len(raw)).encode()+b"\0"+raw).hexdigest())
        self.save()
        self.assertEqual(audit_dataset(self.root)[0]["errors"][0]["reason"], "expanded package exceeds limit")

    def test_generated_artifacts_have_verified_hashes(self):
        result, paths = run(self.root, self.root / "out")
        manifest = json.loads(paths[-1].read_text(encoding="utf-8"))
        for name, digest in manifest["output_sha256"].items():
            self.assertEqual(hashlib.sha256((PROJECT_ROOT / name).read_bytes()).hexdigest(), digest)
        self.assertFalse(result["model_ready"])


if __name__ == "__main__":
    unittest.main()
