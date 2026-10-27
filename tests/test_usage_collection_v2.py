"""Audit-only /2 cases: these never admit recordings to a fitted model."""
import copy
import unittest

from bangla_dh.usage_collection_v2 import SCHEMA, validate
from bangla_dh.usage_metric import InvalidData, audit_package
from bangla_dh.usage_schema import validate as validate_legacy
from test_usage_metric import fixture


def collection_fixture():
    p = fixture()
    p["schema"] = SCHEMA
    p["session"]["keyboard_category"] = "unknown"
    p["collection"] = {"notice_version": "test-1", "wave": "test-1", "category_source": "unknown",
        "geometry_source": "unknown", "render_geometry": "ansi", "bank_sha256": "b" * 64,
        "runtime": None, "engine_events": [], "deliveries": [], "probes": [], "limitations": ["runtime-unavailable"],
        "active_seconds_observed": 2, "assignment": {}, "prompt_selection_version": "variant-selector-history-aware-1",
        "linkage": "local-store-lineage-unverified-person", "modifier_convention": "before-transition",
        "validation_scope": "provisional-collection-not-person-validation"}
    p["prompts"][0]["task"] = {"kind": "natural", "block": 0, "source_family": "test", "domain": "test",
        "selection_version": "test-1", "local_exposure_count": None, "exposure_history": "unknown",
        "planned_start": 20, "planned_duration": 80, "cue": None}
    return p


class CollectionAuditTests(unittest.TestCase):
    def test_step_transition_pause_is_collection_only_and_does_not_admit_model(self):
        p = collection_fixture()
        p["boundaries"].insert(2, {"seq": 6, "t": 2000, "kind": "pause", "reason": "step-transition"})
        p["boundaries"][3]["seq"] = 7
        p["boundaries"][4]["seq"] = 8
        self.assertFalse(validate(p)["model_eligible"])

        # Preserve strict /1 reason validation, even with an otherwise valid /1 package.
        legacy = fixture()
        legacy["boundaries"] = copy.deepcopy(p["boundaries"])
        with self.assertRaises(InvalidData):
            validate_legacy(legacy)
        p["boundaries"][2]["kind"] = "resume"
        with self.assertRaises(InvalidData):
            validate(p)

    def test_unknowns_remain_unknown_and_no_model_admission(self):
        p = collection_fixture()
        original = copy.deepcopy(p)
        report = validate(p)
        self.assertEqual(p, original)
        self.assertEqual(report["keyboard_category"], "unknown")
        self.assertFalse(report["model_eligible"])
        self.assertFalse(report["engine_semantics_validated"])
        with self.assertRaises(InvalidData):
            audit_package(p)

    def test_claim_or_modifier_semantics_cannot_be_promoted(self):
        for field in ("linkage", "validation_scope", "modifier_convention"):
            p = collection_fixture()
            p["collection"][field] = "verified"
            with self.assertRaises(InvalidData):
                validate(p)

    def test_engine_observation_cannot_link_future_or_upstroke(self):
        for key_seq in (5, 99):
            p = collection_fixture()
            p["collection"]["engine_events"] = [{"seq": 8, "t": 2000, "key_seq": key_seq,
                "kind": "translation", "before": "", "after": ""}]
            with self.assertRaises(InvalidData):
                validate(p)

    def test_text_and_global_event_replay_are_independent(self):
        p = collection_fixture()
        p["prompts"][0]["final_text"] = "খ"
        with self.assertRaises(InvalidData):
            validate(p)
        p = collection_fixture()
        p["collection"]["deliveries"] = [{"seq": 4, "t": 510, "key_seq": 3}]
        with self.assertRaises(InvalidData):
            validate(p)

    def test_missing_runtime_is_not_silently_complete(self):
        p = collection_fixture()
        p["collection"]["limitations"] = []
        with self.assertRaises(InvalidData):
            validate(p)


if __name__ == "__main__":
    unittest.main()
