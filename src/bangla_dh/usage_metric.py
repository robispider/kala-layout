"""Independent, standard-library audit of the live typing-study dataset.

This is a measurement audit, not an effort model or the receiver's admission
validator. Raw packages are read only. Grapheme-dependent client scores remain
unverified here until a versioned segmenter is available.
"""
from __future__ import annotations

import csv
import gzip
import hashlib
import io
import json
import math
import re
from collections import Counter
from pathlib import Path

from .paths import DATA, PROJECT_ROOT, hash_outputs, output_path, repo_state, write_json, write_text

VERSION = "usage-audit-v1"
LIMIT = 2 * 1024 * 1024
COLUMNS = "seq t vk sc ext up rep pos mods consumed hook_ms".split()
STAGES = {"ready", "warmup", "natural-1", "coverage", "natural-2", "anchor-repeat"}
SEPARATORS = {"prompt-shown", "prompt-ended", "pause", "resume", "layout-change"}
PROMPT_COLUMNS = ("session_id contributor_id protocol_version prompt_bank_version mapping_hash geometry "
                  "order prompt_id stage measured end_reason repeat_of previously_seen target_sha256 "
                  "target_codepoints final_codepoints active_seconds first_key_latency_seconds key_downs "
                  "text_events correction_episodes backspace_presses").split()
DWELL_COLUMNS = "session_id contributor_id prompt_order stage measured down_seq up_seq position seconds".split()
PAIR_COLUMNS = ("session_id contributor_id prompt_order stage measured from_seq to_seq from_position "
                "to_position down_down_seconds from_mods to_mods correction_key").split()


class InvalidData(ValueError):
    """A structural or measurement invariant failed."""


def require(ok, message):
    if not ok:
        raise InvalidData(message)


def integer(value, minimum=0):
    return type(value) is int and value >= minimum


def number(value):
    return type(value) in (int, float) and math.isfinite(value)


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, "duplicate JSON field")
            result[key] = value
        return result

    def reject(_):
        raise InvalidData("non-finite JSON number")

    def finite_float(value):
        result = float(value)
        require(math.isfinite(result), "non-finite JSON number")
        return result

    return json.loads(raw, object_pairs_hook=pairs, parse_constant=reject, parse_float=finite_float)


def utf16_length(text):
    return len(text.encode("utf-16-le")) // 2


def utf16_index(text, offset):
    require(integer(offset), "invalid UTF-16 offset")
    units = 0
    for index, char in enumerate(text):
        if units == offset:
            return index
        units += 2 if ord(char) > 0xFFFF else 1
    require(units == offset, "UTF-16 offset outside text or inside surrogate pair")
    return len(text)


def selection(text, values):
    require(isinstance(values, list) and len(values) == 2 and all(integer(v) for v in values),
            "invalid selection")
    utf16_index(text, values[0])
    utf16_index(text, values[0] + values[1])


def apply_edit(text, edit):
    start, end = utf16_index(text, edit["start"]), utf16_index(text, edit["end"])
    require(end >= start and text[start:end] == edit["removed"], "removed text disagrees with replay")
    selection(text, edit["sel_before"])
    op = edit["op"]
    require(op in {"insert", "delete", "replace", "selection"}, "unknown edit operation")
    if op == "selection":
        require(not edit["removed"] and not edit["inserted"], "selection changes text")
    else:
        require(op != "insert" or not edit["removed"], "insert removes text")
        require(op != "delete" or not edit["inserted"], "delete inserts text")
        text = text[:start] + edit["inserted"] + text[end:]
    selection(text, edit["sel_after"])
    return text


def pauses(boundaries):
    intervals, opened = [], None
    for row in boundaries:
        if row["kind"] == "pause":
            require(opened is None, "nested pause")
            opened = row["t"]
        elif row["kind"] == "resume":
            require(opened is not None, "resume without pause")
            intervals.append((opened, row["t"]))
            opened = None
    if opened is not None:
        intervals.append((opened, boundaries[-1]["t"]))
    return intervals


def active_seconds(start, end, frequency, pause_intervals):
    return (end - start - sum(max(0, min(end, b) - max(start, a))
                              for a, b in pause_intervals)) / frequency


def wpm5(text, seconds):
    # Kala's labelled five-character WPM uses Unicode scalars, minus one.
    return max(0, len(text) - 1) * 12 / seconds if seconds > 0 else None


def _strings(value):
    if isinstance(value, dict):
        for key, child in value.items():
            _strings(key)
            _strings(child)
    elif isinstance(value, list):
        for child in value:
            _strings(child)
    elif isinstance(value, str):
        value.encode("utf-8")  # Reject unpaired surrogate values.


def audit_package(package):
    """Return metadata and derived rows; raise on contradictory measurements.

    Warnings are research exclusions/review items, separate from corruption.
    This deliberately does not assert complete JSON Schema admission parity.
    """
    import unicodedata

    _strings(package)
    require(package["schema"] == "kala.typing-check.session/1", "unsupported session schema")
    session, inp, clock = package["session"], package["input"], package["clock"]
    frequency = clock["frequency"]
    require(integer(frequency, 1), "invalid clock frequency")
    require(number(session["active_seconds"]) and 0 <= session["active_seconds"] <= 260,
            "invalid active duration")
    require(session["completion"] in {"completed", "interrupted", "stopped"}, "invalid completion")
    require(isinstance(session["quality_flags"], list), "invalid quality flags")
    require(inp["input_family"] in {"fixed", "phonetic"}, "unknown input family")
    require(re.fullmatch(r"sha256:[0-9a-f]{64}", inp["mapping_hash"]) is not None,
            "invalid mapping hash")
    require(inp["composition_only"] is True, "composition-only mode disabled")
    for name in ("autocorrect_enabled", "spelling_correction_enabled", "suggestions_enabled",
                 "spelling_marks_enabled", "personal_rules_enabled"):
        require(inp[name] is False, "assistance enabled: " + name)
    require(package["key_events"]["columns"] == COLUMNS, "unexpected key columns")
    raw_keys = package["key_events"]["rows"]
    require(len(raw_keys) <= 16384, "too many keys")
    keys = []
    for row in raw_keys:
        require(isinstance(row, list) and len(row) == len(COLUMNS), "invalid key row width")
        key = dict(zip(COLUMNS, row))
        for name in ("vk", "sc", "mods", "hook_ms"):
            require(integer(key[name]) and key[name] <= (2**32 - 1 if name == "hook_ms" else 255),
                    "invalid key field: " + name)
        for name in ("ext", "up", "rep", "consumed"):
            require(type(key[name]) is int and key[name] in (0, 1), "invalid key flag")
        require(key["pos"] is None or isinstance(key["pos"], str), "invalid key position")
        keys.append(key)
    edits, boundaries, prompts = package["text_events"], package["boundaries"], package["prompts"]
    require(0 < len(prompts) <= 500 and len(edits) <= 10000, "invalid prompt/edit count")
    combined = []
    for stream in (keys, edits, boundaries):
        previous_seq, previous_time = -1, -1
        for event in stream:
            seq, ticks = event["seq"], event["t"]
            require(integer(seq) and integer(ticks), "invalid event sequence/time")
            require(seq > previous_seq and ticks >= previous_time, "unordered event stream")
            previous_seq, previous_time = seq, ticks
            combined.append((seq, ticks))
    combined.sort()
    require(all(a[0] < b[0] and a[1] <= b[1] for a, b in zip(combined, combined[1:])),
            "duplicate sequence or global clock reversal")
    require(boundaries and boundaries[0]["kind"] == "start", "missing session start")
    require(boundaries[-1]["kind"] in {"stop", "timeout"}, "missing session end")
    require(all(boundaries[0]["seq"] <= seq <= boundaries[-1]["seq"] for seq, _ in combined),
            "events outside session boundaries")
    pause_intervals = pauses(boundaries)
    key_by_seq = {key["seq"]: key for key in keys}
    unknown_sources = inferred_links = 0
    for edit in edits:
        require(edit["source"] in {"kala-delivery", "native-key", "undo", "mouse", "unknown"},
                "unknown source label")
        require(edit["link"] in {"exact", "inferred", "unknown"}, "unknown link label")
        unknown_sources += edit["source"] == "unknown"
        inferred_links += edit["link"] == "inferred"
        linked = edit.get("key_seq")
        if linked is not None:
            require(linked in key_by_seq, "dangling key link")
            key = key_by_seq[linked]
            require(key["seq"] < edit["seq"] and key["t"] <= edit["t"] and not key["up"],
                    "text linked to future key or key release")
        else:
            require(edit["link"] == "unknown", "claimed link without key")

    prompt_rows, key_prompt, edits_seen = [], {}, set()
    previous_end = -1
    correction_episodes = backspaces = 0
    for order, prompt in enumerate(prompts):
        require(type(prompt["order"]) is int and prompt["order"] == order, "invalid prompt order")
        require(prompt["stage"] in STAGES and type(prompt["measured"]) is bool, "invalid stage/measured")
        require(prompt["end_reason"] in {"enter", "timeout", "stop", "layout-change"}, "invalid end reason")
        require(integer(prompt["attempted_units"]), "invalid attempted units")
        shown = [b for b in boundaries if b["kind"] == "prompt-shown" and b.get("prompt_order") == order]
        ended = [b for b in boundaries if b["kind"] == "prompt-ended" and b.get("prompt_order") == order]
        require(len(shown) == len(ended) == 1, "missing/duplicate prompt boundary")
        lo, hi = shown[0], ended[0]
        require(previous_end < lo["seq"] < hi["seq"], "overlapping prompts")
        previous_end = hi["seq"]
        require(prompt["shown_ticks"] == lo["t"] and prompt["end_ticks"] == hi["t"],
                "prompt/boundary time mismatch")
        pkeys = [k for k in keys if lo["seq"] < k["seq"] < hi["seq"]]
        pedits = [e for e in edits if lo["seq"] < e["seq"] < hi["seq"]]
        text, editing, episodes = "", False, 0
        for edit in pedits:
            require(lo["t"] <= edit["t"] <= hi["t"], "edit outside prompt time")
            if edit["op"] != "selection":
                correcting = bool(edit["removed"]) and edit["source"] in {"native-key", "undo", "mouse"}
                episodes += correcting and not editing
                editing = correcting
            text = apply_edit(text, edit)
            edits_seen.add(edit["seq"])
        require(text == prompt["final_text"], "final text disagrees with replay")
        require(unicodedata.normalize("NFC", text) == prompt["final_text_nfc"], "NFC copy mismatch")
        downs = [k for k in pkeys if not k["up"]]
        require(all(lo["t"] <= k["t"] <= hi["t"] for k in pkeys), "key outside prompt time")
        expected_first = downs[0]["t"] if downs else None
        require(prompt.get("first_key_ticks") == expected_first, "first key disagrees with event stream")
        repeat = prompt.get("repeat_of")
        if repeat is not None:
            require(integer(repeat) and repeat < order, "invalid repeat reference")
            require(prompt["target_text"] == prompts[repeat]["target_text"], "repeat target differs")
        seconds = active_seconds(lo["t"], hi["t"], frequency, pause_intervals)
        require(seconds >= 0, "negative active prompt time")
        base = {"session_id": session["session_id"], "contributor_id": session["contributor_id"],
                "protocol_version": session["protocol_version"], "prompt_bank_version": session["prompt_bank_version"],
                "mapping_hash": inp["mapping_hash"], "geometry": session["geometry"]}
        row = dict(base, order=order, prompt_id=prompt["prompt_id"], stage=prompt["stage"],
                   measured=prompt["measured"], end_reason=prompt["end_reason"], repeat_of=repeat,
                   previously_seen=prompt.get("previously_seen"),
                   target_sha256=hashlib.sha256(prompt["target_text"].encode()).hexdigest(),
                   target_codepoints=len(prompt["target_text"]), final_codepoints=len(text),
                   active_seconds=seconds, first_key_latency_seconds=(expected_first-lo["t"])/frequency
                   if expected_first is not None else None, key_downs=len(downs), text_events=len(pedits),
                   correction_episodes=episodes,
                   backspace_presses=sum(k["vk"] == 8 and not k["up"] for k in pkeys))
        prompt_rows.append(row)
        key_prompt.update({k["seq"]: row for k in pkeys})
        if prompt["measured"]:
            correction_episodes += episodes
            backspaces += row["backspace_presses"]
    require(len(edits_seen) == len(edits), "text edit outside all prompts")
    require(sum(b["kind"] == "prompt-shown" for b in boundaries) == len(prompts)
            and sum(b["kind"] == "prompt-ended" for b in boundaries) == len(prompts),
            "extra prompt boundaries")
    integrity = package["integrity"]
    require(integrity["text_replay_ok"] is True, "client reports replay failure")
    for field in ("dropped_events", "injected_events_seen"):
        require(integer(integrity[field]), "invalid integrity counter")
    warnings = []
    if session["quality_flags"]:
        warnings.append("client_quality_flags")
    if integrity["dropped_events"] or integrity["injected_events_seen"]:
        warnings.append("dropped_or_injected_events")
    if unknown_sources:
        warnings.append("unattributed_text_edits")
    if inp["input_family"] != "fixed":
        warnings.append("outside_fixed_layout_scope")
    if session["completion"] != "completed":
        warnings.append("incomplete_session")
    measured = [p for p in prompts if p["measured"]]
    measured_seconds = sum(r["active_seconds"] for r in prompt_rows if r["measured"])
    duration_difference = measured_seconds - session["active_seconds"]
    require(abs(duration_difference) <= 0.5, "active duration differs by more than 0.5 seconds")
    if any(r["key_downs"] == 0 and r["active_seconds"] > 30 for r in prompt_rows if r["measured"]):
        warnings.append("empty_prompt_over_30s")
    summary = package.get("summary") or {}
    calculated = {"wpm5": wpm5(" ".join(p["final_text"] for p in measured), session["active_seconds"]),
                  "backspace_presses": backspaces, "correction_episodes": correction_episodes}
    for stage, label in (("natural-1", "anchor_first_wpm5"), ("anchor-repeat", "anchor_repeat_wpm5")):
        first = next((p for p in prompt_rows if p["stage"] == stage), None)
        calculated[label] = wpm5(prompts[first["order"]]["final_text"], first["active_seconds"]) if first else None
    # WPM qualification also needs >=100 reference graphemes. Null session WPM is
    # left unverified; a non-null value is checked, never inferred from scalars.
    verified = []
    for name, value in calculated.items():
        if name not in summary or name == "wpm5" and summary[name] is None:
            continue
        reported = summary[name]
        if name in {"backspace_presses", "correction_episodes"}:
            require(integer(reported) and reported == value, "summary mismatch: " + name)
            verified.append(name)
            continue
        require((value is None and reported is None) or
                (number(value) and number(reported) and math.isclose(value, reported, rel_tol=0, abs_tol=1e-8)),
                "summary mismatch: " + name)
        verified.append(name)

    dwell, pairs, timing_counts = [], [], Counter()
    held, global_held, prior_down, previous, previous_prompt = {}, {}, None, None, None
    for key in keys:
        prompt = key_prompt.get(key["seq"])
        context = prompt["order"] if prompt else None
        separated = previous is not None and (context != previous_prompt or any(
            previous["seq"] < b["seq"] < key["seq"] and b["kind"] in SEPARATORS for b in boundaries))
        if separated:
            timing_counts["downs_censored_at_boundary"] += len(held)
            held, prior_down, previous = {}, None, None
        if previous is not None:
            delta = (key["t"] - previous["t"]) / frequency
            hook_delta = ((key["hook_ms"] - previous["hook_ms"]) % 2**32) / 1000
            timing_counts["clock_disagreements_over_250ms"] += abs(delta - hook_delta) > .25
            timing_counts["idle_key_gaps_over_30s"] += delta > 30
        identity = key["sc"], key["ext"]
        if key["pos"] is None:
            timing_counts["unknown_position_events"] += 1
            if key["vk"] == 0xA1 and key["sc"] == 0x36:
                timing_counts["right_shift_unknown_position_events"] += 1
        if key["up"]:
            global_down = global_held.pop(identity, None)
            if global_down is None:
                timing_counts["globally_unmatched_keyups"] += 1
            elif any(global_down["seq"] < b["seq"] < key["seq"] and b["kind"] in SEPARATORS
                     for b in boundaries):
                timing_counts["cross_boundary_releases"] += 1
        elif not key["rep"]:
            timing_counts["global_duplicate_downs"] += identity in global_held
            global_held[identity] = key
        if key["up"]:
            down = held.pop(identity, None)
            if down is None:
                timing_counts["unmatched_keyups"] += 1
            elif prompt is not None:
                dwell.append(dict(session_id=session["session_id"], contributor_id=session["contributor_id"],
                                  prompt_order=context, stage=prompt["stage"], measured=prompt["measured"],
                                  down_seq=down["seq"], up_seq=key["seq"], position=key["pos"],
                                  seconds=(key["t"]-down["t"])/frequency))
        elif key["rep"]:
            timing_counts["autorepeat_downs_excluded"] += 1
            prior_down = None
        else:
            if identity in held:
                timing_counts["duplicate_downs"] += 1
            held[identity] = key
            if prior_down is not None and prompt is not None:
                seconds = (key["t"]-prior_down["t"])/frequency
                if 0 < seconds <= 30 and key["pos"] is not None and prior_down["pos"] is not None:
                    pairs.append(dict(session_id=session["session_id"], contributor_id=session["contributor_id"],
                                      prompt_order=context, stage=prompt["stage"], measured=prompt["measured"],
                                      from_seq=prior_down["seq"], to_seq=key["seq"],
                                      from_position=prior_down["pos"], to_position=key["pos"],
                                      down_down_seconds=seconds, from_mods=prior_down["mods"], to_mods=key["mods"],
                                      correction_key=prior_down["vk"] in {8, 46} or key["vk"] in {8, 46}))
            prior_down = key
        previous, previous_prompt = key, context
    timing_counts["downs_censored_at_boundary"] += len(held)
    timing_counts["terminal_held_keys"] = len(global_held)
    if timing_counts["clock_disagreements_over_250ms"] or timing_counts["duplicate_downs"] or timing_counts["global_duplicate_downs"]:
        warnings.append("key_timing_anomaly")
    if timing_counts["idle_key_gaps_over_30s"]:
        warnings.append("idle_key_gap_over_30s")
    if timing_counts["globally_unmatched_keyups"]:
        warnings.append("unexplained_key_releases")
    if timing_counts["unknown_position_events"]:
        warnings.append("unknown_physical_positions")
    metadata = {name: session[name] for name in (
        "session_id", "contributor_id", "session_number", "protocol_version", "prompt_bank_version", "variant_id",
        "started_utc", "kala_version", "build_configuration", "geometry", "keyboard_category", "completion", "active_seconds")}
    metadata.update({name: inp[name] for name in ("layout_id", "layout_name", "mapping_hash", "input_family", "engine_version")})
    metadata.update(prompt_count=len(prompts), measured_prompt_count=len(measured), key_events=len(keys),
                    text_events=len(edits), quality_flags=session["quality_flags"], warnings=warnings,
                    unknown_source_edits=unknown_sources, inferred_links=inferred_links,
                    measured_prompt_seconds=measured_seconds, duration_difference_seconds=duration_difference,
                    independently_calculated=calculated, verified_summary_fields=verified,
                    unverified_summary_fields=[k for k in ("correct_gpm", "accuracy", "first_try_accuracy") if k in summary],
                    timing_counts=dict(timing_counts))
    return metadata, prompt_rows, dwell, pairs


def audit_dataset(root):
    root = Path(root).resolve()
    raw_manifest = (root / "manifest.json").read_bytes()
    manifest = strict_json(raw_manifest)
    require(manifest["schema"] == "kala.usage-metric.dataset/1" and
            manifest["session_schema"] == "kala.typing-check.session/1", "unsupported manifest schema")
    require(isinstance(manifest["sessions"], list), "invalid manifest sessions")
    errors, sessions, prompt_rows, dwell, pairs = [], [], [], [], []
    seen_ids, seen_paths, seen_hashes, listed = set(), set(), set(), set()
    inputs = {"manifest.json": hashlib.sha256(raw_manifest).hexdigest()}
    for entry in manifest["sessions"]:
        label = entry.get("session_id", "unknown") if isinstance(entry, dict) else "unknown"
        try:
            cid, sid, relative = entry["contributor_id"], entry["session_id"], entry["path"]
            require(isinstance(cid, str) and re.fullmatch(r"c_[0-9a-f]{32}", cid), "invalid contributor id")
            require(isinstance(sid, str) and re.fullmatch(r"s_[0-9A-Za-z]{20,40}", sid), "invalid session id")
            require(relative == f"sessions/{cid}/{sid}.json.gz", "noncanonical or escaping package path")
            path = (root / relative).resolve()
            require(path.is_relative_to(root / "sessions"), "package path outside sessions")
            require(sid not in seen_ids and relative not in seen_paths and entry["package_sha256"] not in seen_hashes,
                    "duplicate session/path/package")
            seen_ids.add(sid)
            seen_paths.add(relative)
            seen_hashes.add(entry["package_sha256"])
            listed.add(path)
            require(integer(entry["size_bytes"], 1) and entry["size_bytes"] <= LIMIT, "invalid package size")
            require(path.stat().st_size == entry["size_bytes"], "package size mismatch")
            raw = path.read_bytes()
            digest = hashlib.sha256(raw).hexdigest()
            require(digest == entry["package_sha256"], "package SHA-256 mismatch")
            blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
            require(blob == entry["git_blob_sha"], "Git blob SHA mismatch")
            inputs[relative] = digest
            with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
                expanded = stream.read(LIMIT + 1)
            require(len(expanded) <= LIMIT, "expanded package exceeds limit")
            package = strict_json(expanded)
            require(package["session"]["session_id"] == sid and package["session"]["contributor_id"] == cid,
                    "manifest/package identity mismatch")
            row, prows, drows, krows = audit_package(package)
            row["package_sha256"] = digest
            sessions.append(row)
            prompt_rows.extend(prows)
            dwell.extend(drows)
            pairs.extend(krows)
        except (InvalidData, OSError, ValueError, KeyError, TypeError, IndexError, AttributeError, EOFError) as exc:
            # Never embed exception text from JSON parsers or field values: it can
            # include participant-entered text. Known invariant messages are safe.
            errors.append({"session_id": label, "reason": str(exc) if isinstance(exc, InvalidData)
                           else "unreadable or malformed package (" + type(exc).__name__ + ")"})
    actual = {p.resolve() for p in (root / "sessions").rglob("*.json.gz")}
    if actual - listed:
        errors.append({"session_id": None, "reason": "unlisted packages present", "count": len(actual-listed)})
    require((root / "manifest.json").read_bytes() == raw_manifest, "manifest changed during audit; retry on a stable checkout")
    duplicate_orders = Counter((s["contributor_id"], s["session_number"]) for s in sessions)
    warnings = ["multiple_protocols" ] if len({s["protocol_version"] for s in sessions}) > 1 else []
    if any(n > 1 for n in duplicate_orders.values()):
        warnings.append("duplicate_contributor_session_number")
    result = {"schema": "kala.usage-metric.audit/1", "audit_version": VERSION,
              "status": "fail" if errors else "no_data" if not sessions else
                        "pass_with_review" if warnings or any(s["warnings"] for s in sessions) else "pass",
              "model_ready": False, "recruitment_ready": "controlled_pilot_only_pending_live_checks",
              "manifest_entries": len(manifest["sessions"]), "valid_sessions": len(sessions),
              "contributors": len({s["contributor_id"] for s in sessions}),
              "protocol_counts": dict(Counter(s["protocol_version"] for s in sessions)),
              "mapping_counts": dict(Counter(s["mapping_hash"] for s in sessions)),
              "errors": errors, "warnings": warnings, "sessions": sessions,
              "limitations": ["Not a complete receiver admission validator.",
                              "Grapheme accuracy, correct GPM, first-try accuracy and speed qualification are not verified by this command.",
                              "Down-down pairs include modifiers, spaces, corrections and non-text keys; they are diagnostic candidates, not training rows.",
                              "Physical position is recorded; actual finger identity and mapping content are not captured.",
                              "Local packages cannot verify consent UI, unsent data, receipt/retry, withdrawal or live server operation."],
              "input_sha256": inputs}
    return result, prompt_rows, dwell, pairs


def _csv(path, rows, fields):
    target = output_path(path)
    # Empty output still has a stable header.
    with target.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    return target


def run(root=DATA / "usage-metric-dataset", out=PROJECT_ROOT / "results/usage-metric-audit-v1"):
    out = output_path(Path(out) / "audit.json").parent
    record, prompts, dwell, pairs = audit_dataset(root)
    paths = [write_json(out / "audit.json", record), _csv(out / "prompts.csv", prompts, PROMPT_COLUMNS),
             _csv(out / "dwell.csv", dwell, DWELL_COLUMNS), _csv(out / "key-pairs.csv", pairs, PAIR_COLUMNS)]
    text = ("# Received typing-study data audit\n\n"
            f"Status: **{record['status']}**. {record['valid_sessions']} of {record['manifest_entries']} "
            f"packages passed the implemented integrity/measurement checks; {record['contributors']} contributor IDs.\n\n"
            "This is a pipeline pilot, not evidence of a layout effect or recruitment sign-off. "
            "See MODELING_PLAN.md for the recruitment gates and modeling plan.\n\n"
            "| Session | Protocol | Build | Prompts | Keys | Edits | Review items |\n"
            "| --- | --- | --- | --- | --- | --- | --- |\n")
    for s in record["sessions"]:
        text += (f"| {s['session_id']} | {s['protocol_version']} | {s['build_configuration']} | "
                 f"{s['prompt_count']} | {s['key_events']} | {s['text_events']} | {', '.join(s['warnings']) or 'none'} |\n")
    text += "\nChecks include compressed-byte and Git blob hashes, bounded gzip/strict JSON, IDs, event ordering, "
    text += "UTF-16 edit replay/selection ranges, NFC, first key, repeats, prompt clocks, disabled assistance, "
    text += "duration reconciliation, scalar WPM, backspaces, edit episodes, anchor WPM and two-clock key intervals.\n\n"
    text += "Measured prompt duration may differ from the session clock by up to 0.5 seconds "
    text += "(versioned audit tolerance for transitions); values are retained in audit.json. "
    text += "The key-clock comparison allows 250 ms, matching the existing client diagnostic. "
    text += "Pairs are consecutive non-repeat keydowns within one prompt and pause segment, "
    text += "with 0 < interval <= 30 seconds; no winsorization. Grapheme scores are unverified by this command.\n\n"
    text += "Cross-boundary releases are matched globally for integrity but censored from dwell samples. "
    text += "Review candidate rows before training. No prompt or final text is copied to these outputs.\n"
    if record["errors"]:
        text += "\nErrors:\n" + "".join(f"- {e['session_id']}: {e['reason']}\n" for e in record["errors"])
    paths.append(write_text(out / "REPORT.md", text))
    commit, clean = repo_state()
    manifest = {"phase": VERSION, "commit": commit, "working_tree_clean": clean,
                "input_sha256": record["input_sha256"],
                "implementation_sha256": hash_outputs([Path(__file__), PROJECT_ROOT / "src/bangla_dh/paths.py",
                                                        PROJECT_ROOT / "src/bangla_dh/cli.py"]),
                "parameters": {"max_compressed_and_expanded_bytes": LIMIT, "duration_tolerance_seconds": 0.5,
                               "clock_tolerance_seconds": 0.25, "pair_max_seconds": 30,
                               "seeds": [], "training": False},
                "output_sha256": hash_outputs(paths)}
    paths.append(write_json(out / "run-manifest.json", manifest))
    return record, paths
