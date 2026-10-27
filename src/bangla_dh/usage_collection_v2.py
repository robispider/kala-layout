"""Independent, audit-only reader for the provisional Kala collection /2 contract.

This does not register a protocol, fit a model, or admit /2 to the /1 extractor.
Unknown metadata stay unknown. Engine semantics still require an exact adapter.
"""
import base64
import copy
import gzip
import hashlib
import json
import unicodedata
from pathlib import Path

from .usage_metric import COLUMNS, apply_edit, integer, number, require, strict_json

SCHEMA = "kala.typing-check.session/2"
LIMIT = 2 * 1024 * 1024


def validate(package):
    from .usage_schema import validate as common_validate
    require(package.get("schema") == SCHEMA, "unsupported collection schema")
    require(type(package.get("collection")) is dict, "collection object required")
    collection = package["collection"]
    common = copy.deepcopy(package)
    del common["collection"]
    for prompt in common["prompts"]:
        require(type(prompt.get("task")) is dict, "task required")
        del prompt["task"]
    # Validate the unchanged common fields without replacing unknown categories.
    common_validate(common, allow_unknown_category=True, allow_step_transition=True)
    require(collection.get("linkage") == "local-store-lineage-unverified-person", "unverified lineage semantics")
    require(collection.get("modifier_convention") == "before-transition", "modifier convention")
    require(collection.get("validation_scope") == "provisional-collection-not-person-validation", "claim scope")
    require(collection.get("prompt_selection_version") == "variant-selector-history-aware-1", "selection version")
    require(number(collection.get("active_seconds_observed")) and collection["active_seconds_observed"] >= 0, "observed time")
    require(collection.get("category_source") in {"unknown", "existing-unverified-selection"} and
            collection.get("geometry_source") in {"unknown", "existing-unverified-selection"}, "metadata provenance")
    require(collection.get("render_geometry") in {"ansi", "iso"}, "render profile")
    require(type(collection.get("assignment")) is dict and len(collection["assignment"]) <= 8, "assignment")
    require(type(collection.get("limitations")) is list and len(collection["limitations"]) <= 32, "limitations")
    require(package["key_events"]["columns"] == COLUMNS, "key columns")
    require(len(package["key_events"]["rows"]) <= 16384 and len(package["prompts"]) <= 500 and len(package["text_events"]) <= 10000, "common limits")
    keys = []
    for row in package["key_events"]["rows"]:
        require(type(row) is list and len(row) == 11, "key row")
        key = dict(zip(COLUMNS, row))
        require(all(type(key[n]) is int and key[n] in {0, 1} for n in ("ext", "up", "rep", "consumed")), "key flags")
        require(all(integer(key[n]) and key[n] <= 255 for n in ("vk", "sc", "mods")), "key code")
        require(integer(key["hook_ms"]) and key["hook_ms"] < 2**32, "hook clock")
        keys.append(key)
    key_index = {k["seq"]: k for k in keys}
    events = []
    streams = [keys, package["text_events"], package["boundaries"]]
    for name, maximum in (("engine_events", 16384), ("deliveries", 10000)):
        stream = collection.get(name)
        require(type(stream) is list and len(stream) <= maximum, "collection stream limit")
        streams.append(stream)
        for event in stream:
            key = event.get("key_seq")
            require(key is None or key in key_index and key < event["seq"] and key_index[key]["up"] == 0, "collection key link")
            if name == "engine_events":
                require(event.get("kind") in {"translation", "reset", "acknowledgement", "delivery-failed"}, "engine kind")
                require(all(type(event.get(n)) is str and len(event[n]) <= 2048 for n in ("before", "after")), "engine context")
    for stream in streams:
        previous = (-1, -1)
        for e in stream:
            pair = (e["seq"], e["t"])
            require(integer(pair[0]) and integer(pair[1]) and pair[0] > previous[0] and pair[1] >= previous[1], "stream ordering")
            previous = pair
            events.append(pair)
    events.sort()
    require(all(a[0] < b[0] and a[1] <= b[1] for a, b in zip(events, events[1:])), "global sequence/clock ordering")
    bounds = package["boundaries"]
    if events:
        require(bounds and bounds[0]["kind"] == "start" and bounds[-1]["kind"] in {"stop", "timeout"}, "capture boundaries")
    for order, prompt in enumerate(package["prompts"]):
        task = prompt["task"]
        require(prompt["order"] == order, "prompt order")
        require(task.get("kind") in {"ready", "warmup", "natural", "targeted", "physical-probe", "anchor"}, "task kind")
        require(task.get("local_exposure_count") is None or integer(task["local_exposure_count"]), "local exposure")
        require(task.get("exposure_history") in {"unknown", "bounded-local-history"}, "exposure provenance")
        start = [b for b in bounds if b["kind"] == "prompt-shown" and b.get("prompt_order") == order]
        end = [b for b in bounds if b["kind"] == "prompt-ended" and b.get("prompt_order") == order]
        require(len(start) == len(end) == 1, "prompt boundaries")
        text = ""
        for edit in package["text_events"]:
            if start[0]["seq"] < edit["seq"] < end[0]["seq"]:
                text = apply_edit(text, edit)
        require(text == prompt["final_text"] and unicodedata.normalize("NFC", text) == prompt["final_text_nfc"], "text replay")
    probes = collection.get("probes")
    require(type(probes) is list and len(probes) <= 2000, "probe limit")
    for attempt in probes:
        require(integer(attempt.get("prompt_order")) and attempt["prompt_order"] < len(package["prompts"]), "probe prompt")
        cue = package["prompts"][attempt["prompt_order"]]["task"].get("cue")
        require(type(cue) is list and 2 <= len(cue) <= 4, "probe cue")
        actual = []
        for seq in attempt["key_seqs"]:
            require(seq in key_index and key_index[seq]["up"] == key_index[seq]["rep"] == 0, "probe physical action")
            actual.append(key_index[seq]["pos"])
        correct = len(actual) == len(cue) and all(a == c or c == "SHFT" and a in {"LSHF", "RSHF"} for a, c in zip(actual, cue))
        if "completed" in attempt:
            require(type(attempt["completed"]) is bool and attempt["completed"] == (len(actual) == len(cue)), "probe completion")
        require(type(attempt.get("correct")) is bool and attempt["correct"] == correct, "probe correctness")
    runtime = collection.get("runtime")
    if runtime is not None:
        require(type(runtime) is dict and len(runtime.get("files", [])) == 2, "runtime files")
        require(sorted(f["name"] for f in runtime["files"]) == ["alphabet", "mapping"], "runtime names")
        for file in runtime["files"]:
            raw = base64.b64decode(file["base64"], validate=True)
            require(len(raw) <= 128 * 1024 and hashlib.sha256(raw).hexdigest() == file["sha256"], "runtime bytes hash")
        identity = "\n".join(f["name"] + ":" + f["sha256"] for f in runtime["files"])
        identity += "\n" + runtime["style"] + "\n" + runtime["translator"] + "\n" + runtime["build_sha256"]
        require(hashlib.sha256(identity.encode()).hexdigest() == runtime["effective_hash"], "effective runtime hash")
    else:
        require("runtime-unavailable" in collection["limitations"], "missing runtime reason")
    return {"status": "provisional_collection_audit", "schema": SCHEMA, "session_id": package["session"]["session_id"],
            "keyboard_category": package["session"]["keyboard_category"], "geometry": package["session"]["geometry"],
            "keys": len(keys), "engine_events": len(collection["engine_events"]), "probe_attempts": len(probes),
            "limitations": collection["limitations"], "engine_semantics_validated": False, "model_eligible": False}


def read(path):
    raw = Path(path).read_bytes()
    require(len(raw) <= LIMIT, "compressed limit")
    import io
    with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
        payload = stream.read(LIMIT + 1)
    require(len(payload) <= LIMIT, "expanded limit")
    return validate(strict_json(payload))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path)
    args = parser.parse_args()
    print(json.dumps(read(args.package), ensure_ascii=True, indent=2))
