"""Reason-coded empirical tables. No passage text; raw recordings stay immutable."""
from collections import Counter, defaultdict
from functools import lru_cache
import math

from .geometry.keyboards import KEYBOARDS
from .scoring.model import KeyModel
from .paths import PROJECT_ROOT
from .usage_metric import COLUMNS, SEPARATORS, active_seconds, pauses
from .usage_registry import digest

VERSION = "usage-features-v1"
POSITION_VERSION = "raw-plus-right-shift-a1-36-v1"
ASSIGNMENT = "frozen-traditional-assumption-not-observed-fingering"
COMMON = ("package_sha256 session_id contributor_id session_number mapping_hash engine_version protocol_version "
          "prompt_bank_version build_configuration geometry keyboard_category session_quality aggregate_decision "
          "motor_session_decision motor_session_reasons idle_sensitivity_decision").split()
CONTEXT = "prompt_order stage measured target_sha256 family previously_seen repeat_of elapsed_active_seconds".split()
SCHEMAS = {
    "sessions": COMMON + "completion active_seconds wall_seconds prompt_count key_events text_events idle_affected mapping_status protocol_status".split(),
    "prompts": COMMON + CONTEXT + "prompt_id end_reason active_seconds final_sha256 target_codepoints final_codepoints empty_over_30s".split(),
    "events": COMMON + CONTEXT + ("seq ticks segment vk scan extended up autorepeat raw_position derived_position position_rule "
                                "raw_modifiers shift_left_before shift_right_before shift_left_after shift_right_after consumed "
                                "action_decision action_reasons edit_seqs row column x_u y_u finger_assumption").split(),
    "edits": COMMON + CONTEXT + ("seq ticks key_seq op source link start_utf16 end_utf16 removed_sha256 inserted_sha256 "
                               "removed_codepoints inserted_codepoints selection_before selection_after decision reasons").split(),
    "intervals": COMMON + CONTEXT + ("from_seq to_seq from_edit_seq to_edit_seq segment from_position to_position "
                                   "down_down_seconds log_down_down_seconds flight_seconds flight_censored "
                                   "from_shift_left from_shift_right to_shift_left to_shift_right shift_transition "
                                   "from_row to_row from_column to_column distance_u same_key same_finger hand_alternation "
                                   "finger_assignment frozen_pair_effort decision reasons idle_sensitivity_eligible").split(),
    "dwell": COMMON + CONTEXT + "down_seq up_seq segment position seconds censored decision reasons".split(),
    "repeats": COMMON + CONTEXT + "seq ticks segment position raw_position decision reasons".split(),
    "outcomes": COMMON + CONTEXT + "key_seq edit_seq correction_observed decision reasons".split(),
}


def resolve_position(k):
    if k["pos"] is not None:
        return k["pos"], "recorded"
    if k["vk"] == 0xA1 and k["sc"] == 0x36 and k["ext"] in (0, 1):
        return "RSHF", POSITION_VERSION
    return None, "unresolved"


@lru_cache(maxsize=2)
def geometry(kind):
    if kind not in {"ansi", "iso"}: return {}, None
    keyboard = KEYBOARDS[kind]()
    model = KeyModel.from_grid(PROJECT_ROOT / f"results/phase1/effort-grids/{kind}-traditional.json")
    names = {}
    for prefix, letters in (("AE", "1234567890-="), ("AD", "QWERTYUIOP[]"),
                            ("AC", "ASDFGHJKL;'"), ("AB", "ZXCVBNM,./")):
        names.update({f"{prefix}{i:02}": c for i, c in enumerate(letters, 1)})
    names.update(TLDE="`", BKSL="\\", AC12="#", LSGT="\\", LSHF="LSHIFT", RSHF="RSHIFT")
    result = {}
    for pos, name in names.items():
        try:
            key = keyboard.key(name); assumed = model.keys.get(name)
        except KeyError: continue
        result[pos] = dict(name=name, row=key.row, column=int(pos[2:]) if pos[:2] in {"AE", "AD", "AC", "AB"} else None,
                           x_u=key.center[0], y_u=key.center[1], finger=assumed.finger if assumed else None)
    return result, model


def _reasons(values):
    return "|".join(sorted(set(values)))


def extract(package, meta, registry):
    s, inp = package["session"], package["input"]
    keys = [dict(zip(COLUMNS, r)) for r in package["key_events"]["rows"]]
    edits, boundaries = package["text_events"], package["boundaries"]
    frequency = package["clock"]["frequency"]
    pause_intervals = pauses(boundaries)
    mapping = next((e for e in registry["mappings"] if e["mapping_hash"] == inp["mapping_hash"] and e["engine_version"] == inp["engine_version"]), {})
    protocol = next((e for e in registry["protocols"] if e["protocol"] == s["protocol_version"] and e["bank_version"] == s["prompt_bank_version"]), {})
    idle = any(w in meta["warnings"] for w in ("empty_prompt_over_30s", "idle_key_gap_over_30s")) or "idle-over-30s" in s["quality_flags"]
    session_reasons = []
    if s["completion"] != "completed": session_reasons.append("incomplete_session")
    if inp["input_family"] != "fixed": session_reasons.append("outside_fixed_scope")
    if s["geometry"] not in {"ansi", "iso"}: session_reasons.append("unknown_geometry")
    if any(v for k, v in package["integrity"].items() if k != "text_replay_ok"): session_reasons.append("capture_integrity_warning")
    if s["quality_flags"] and set(s["quality_flags"]) != {"idle-over-30s"}: session_reasons.append("client_quality_flags")
    if any(w in meta["warnings"] for w in ("key_timing_anomaly", "unexplained_key_releases")): session_reasons.append("key_timing_anomaly")
    if not protocol: session_reasons.append("unsupported_protocol_bank")
    without_idle = session_reasons[:]
    if idle: session_reasons.append("idle_session")
    common = {n: s[n] for n in ("session_id", "contributor_id", "session_number", "protocol_version", "prompt_bank_version", "build_configuration", "geometry", "keyboard_category")}
    common.update(package_sha256=meta["package_sha256"], mapping_hash=inp["mapping_hash"], engine_version=inp["engine_version"],
                  session_quality=_reasons(meta["warnings"] + s["quality_flags"]), aggregate_decision="review" if meta["warnings"] else "accepted",
                  motor_session_decision="excluded" if session_reasons else "accepted", motor_session_reasons=_reasons(session_reasons),
                  idle_sensitivity_decision="excluded" if without_idle else "accepted")
    tables = {name: [] for name in SCHEMAS}
    tables["sessions"].append(dict(common, completion=s["completion"], active_seconds=s["active_seconds"],
        wall_seconds=(boundaries[-1]["t"] - boundaries[0]["t"]) / frequency, prompt_count=len(package["prompts"]),
        key_events=len(keys), text_events=len(edits), idle_affected=idle, mapping_status=mapping.get("status", "missing_mapping"),
        protocol_status="registered" if protocol else "unresolved"))
    context_by_seq, prompt_ranges = {}, []
    for p in package["prompts"]:
        lo = next(b for b in boundaries if b["kind"] == "prompt-shown" and b.get("prompt_order") == p["order"])
        hi = next(b for b in boundaries if b["kind"] == "prompt-ended" and b.get("prompt_order") == p["order"])
        target = digest(p["target_text"].encode())
        registered = next((v for v in protocol.get("prompts", []) if v["prompt_id"] == p["prompt_id"] and v["target_sha256"] == target), {})
        context = dict(prompt_order=p["order"], stage=p["stage"], measured=p["measured"], target_sha256=target,
                       family=registered.get("family"), previously_seen=p.get("previously_seen", False), repeat_of=p.get("repeat_of"), elapsed_active_seconds=0)
        prompt_ranges.append((lo, hi, context))
        seconds = active_seconds(lo["t"], hi["t"], frequency, pause_intervals)
        tables["prompts"].append(dict(common, **context, prompt_id=p["prompt_id"], end_reason=p["end_reason"], active_seconds=seconds,
            final_sha256=digest(p["final_text"].encode()), target_codepoints=len(p["target_text"]), final_codepoints=len(p["final_text"]),
            empty_over_30s=p["measured"] and not p["final_text"] and seconds > 30))
        for e in keys + edits:
            if lo["seq"] < e["seq"] < hi["seq"]:
                context_by_seq[e["seq"]] = dict(context, elapsed_active_seconds=active_seconds(boundaries[0]["t"], e["t"], frequency, pause_intervals))
    linked = defaultdict(list)
    for e in edits:
        if e.get("key_seq") is not None: linked[e["key_seq"]].append(e)
        reasons = []
        if e["source"] == "unknown": reasons.append("unknown_source")
        if e["link"] != "exact": reasons.append("nonexact_link")
        if e["op"] == "selection": reasons.append("selection")
        if e["removed"]: reasons.append("replacement_or_correction")
        if len(e["inserted"]) != 1: reasons.append("multi_or_zero_codepoint")
        if e["sel_before"][1] or e["sel_after"][1]: reasons.append("selected_range")
        reasons += session_reasons
        context = context_by_seq[e["seq"]]
        if not context["measured"]: reasons.append("unmeasured")
        if mapping.get("status") != "verified_mapping": reasons.append("missing_mapping_registry")
        # This is label provenance eligibility, not grammar replay validation.
        tables["edits"].append(dict(common, **context, seq=e["seq"], ticks=e["t"], key_seq=e.get("key_seq"), op=e["op"], source=e["source"], link=e["link"],
            start_utf16=e["start"], end_utf16=e["end"], removed_sha256=digest(e["removed"].encode()), inserted_sha256=digest(e["inserted"].encode()),
            removed_codepoints=len(e["removed"]), inserted_codepoints=len(e["inserted"]), selection_before=e["sel_before"][1], selection_after=e["sel_after"][1],
            decision="excluded" if reasons else "accepted", reasons=_reasons(reasons)))
    positions, model = geometry(s["geometry"])
    # Segment at every prompt/pause/resume/layout boundary. Paused keys are
    # excluded explicitly; global release matching cannot create motor samples.
    segment, paused, boundary_index = 0, False, 0
    held, releases, down_segments, repeated_holds = {}, {}, {}, set()
    event_by_seq, action_reasons, down_rows = {}, {}, []
    for k in keys:
        while boundary_index < len(boundaries) and boundaries[boundary_index]["seq"] < k["seq"]:
            b = boundaries[boundary_index]; boundary_index += 1
            if b["kind"] in SEPARATORS:
                segment += 1
                if b["kind"] in {"pause", "resume", "layout-change"}: held = {}
            if b["kind"] == "pause": paused = True
            elif b["kind"] == "resume": paused = False
        context = context_by_seq.get(k["seq"], {n: None for n in CONTEXT})
        pos, rule = resolve_position(k); key_id = (k["sc"], k["ext"])
        left_before = any(v["position"] == "LSHF" for v in held.values())
        right_before = any(v["position"] == "RSHF" for v in held.values())
        if k["up"]:
            down = held.pop(key_id, None)
            if down and down["segment"] == segment: releases[down["seq"]] = k
        elif not k["rep"]:
            held[key_id] = dict(seq=k["seq"], position=pos, segment=segment)
            down_segments[k["seq"]] = segment
        elif key_id in held:
            repeated_holds.add(held[key_id]["seq"])
        local = []
        if paused: local.append("paused")
        if not context["measured"]: local.append("unmeasured_or_outside_prompt")
        if k["rep"]: local.append("autorepeat")
        if k["mods"] & (4 | 8 | 16 | 32 | 64 | 128): local.append("unsupported_nonshift_modifier")
        if (k["mods"] & 1 and not left_before) or (k["mods"] & 2 and not right_before):
            local.append("unresolved_held_shift_state")
        if pos is None: local.append("unknown_position")
        if k["vk"] in {8, 46}: local.append("correction_key")
        if pos in {"LSHF", "RSHF", "LCTL", "RCTL", "LALT", "RALT", "LWIN", "RWIN", "CAPS"}: local.append("modifier")
        ee = linked[k["seq"]]
        if len(ee) != 1: local.append("not_one_text_edit")
        else:
            e = ee[0]
            if e["source"] != "kala-delivery": local.append("unknown_or_native_source")
            if e["link"] != "exact" or not k["consumed"]: local.append("nonexact_or_unconsumed")
            if e["op"] != "insert" or e["removed"]: local.append("replacement_correction_or_selection")
            if len(e["inserted"]) != 1: local.append("multi_or_zero_codepoint")
            if any(c.isspace() for c in e["inserted"]): local.append("space_transition")
            if e["sel_before"][1] or e["sel_after"][1]: local.append("selected_range")
            if context_by_seq.get(e["seq"], {}).get("prompt_order") != context["prompt_order"]: local.append("cross_prompt_attribution")
        info = positions.get(pos, {})
        if info.get("finger") is None: local.append("unsupported_geometry_key")
        row = dict(common, **context, seq=k["seq"], ticks=k["t"], segment=segment, vk=k["vk"], scan=k["sc"], extended=k["ext"], up=k["up"], autorepeat=k["rep"],
            raw_position=k["pos"], derived_position=pos, position_rule=rule, raw_modifiers=k["mods"], shift_left_before=left_before, shift_right_before=right_before,
            shift_left_after=any(v["position"] == "LSHF" for v in held.values()), shift_right_after=any(v["position"] == "RSHF" for v in held.values()),
            consumed=k["consumed"], action_decision="excluded" if local + session_reasons else "accepted", action_reasons=_reasons(local + session_reasons),
            edit_seqs="|".join(str(e["seq"]) for e in ee), row=info.get("row"), column=info.get("column"), x_u=info.get("x_u"), y_u=info.get("y_u"), finger_assumption=info.get("finger"))
        tables["events"].append(row); event_by_seq[k["seq"]] = row; action_reasons[k["seq"]] = local
        if k["rep"] and not k["up"]:
            tables["repeats"].append(dict(common, **context, seq=k["seq"], ticks=k["t"], segment=segment, position=pos, raw_position=k["pos"], decision="excluded", reasons="autorepeat"))
        if not k["up"]: down_rows.append(k)
    for i, k in enumerate(down_rows):
        row = event_by_seq[k["seq"]]; context = {n: row[n] for n in CONTEXT}
        if k["rep"]: continue
        up = releases.get(k["seq"]); seconds = (up["t"] - k["t"]) / frequency if up else None
        local = action_reasons[k["seq"]][:]
        if k["seq"] in repeated_holds: local.append("held_autorepeat")
        if up is None: local.append("boundary_or_terminal_censoring")
        tables["dwell"].append(dict(common, **context, down_seq=k["seq"], up_seq=up["seq"] if up else None, segment=row["segment"], position=row["derived_position"], seconds=seconds,
            censored=up is None, decision="excluded" if local + session_reasons else "accepted", reasons=_reasons(local + session_reasons)))
        # Separate correction outcome with observable attribution. It measures
        # native correction actions, not per-symbol latent error probability.
        ee = linked[k["seq"]]
        observed = len(ee) == 1 and ee[0]["link"] == "exact" and ee[0]["source"] != "unknown" and ee[0]["op"] != "selection"
        correction = observed and bool(ee[0]["removed"]) and ee[0]["source"] in {"native-key", "undo", "mouse"}
        outcome_reasons = session_reasons[:] + ([] if observed else ["unknown_correction_attribution"])
        if not context["measured"]: outcome_reasons.append("unmeasured")
        tables["outcomes"].append(dict(common, **context, key_seq=k["seq"], edit_seq=ee[0]["seq"] if len(ee) == 1 else None,
            correction_observed=int(correction) if observed else None, decision="excluded" if outcome_reasons else "accepted", reasons=_reasons(outcome_reasons)))
    # Consecutive means consecutive in the complete down stream. Never bridge a
    # Shift, correction, unknown edit, zero-output key or repeat to invent a pair.
    for a, b in zip(down_rows, down_rows[1:]):
        ra, rb = event_by_seq[a["seq"]], event_by_seq[b["seq"]]
        context = {n: rb[n] for n in CONTEXT}
        local = action_reasons[a["seq"]] + action_reasons[b["seq"]]
        if ra["segment"] != rb["segment"]: local.append("boundary")
        seconds = (b["t"] - a["t"]) / frequency
        if not 0 < seconds <= 30: local.append("nonpositive_or_idle_interval")
        between = [e for e in edits if a["seq"] < e["seq"] < b["seq"]]
        if any(e.get("key_seq") != a["seq"] or e["op"] == "selection" for e in between): local.append("intervening_edit")
        ea, eb = linked[a["seq"]], linked[b["seq"]]
        if len(ea) == 1 and ea[0]["seq"] > b["seq"]: local.append("delayed_notification")
        pa, pb = positions.get(ra["derived_position"], {}), positions.get(rb["derived_position"], {})
        supported = bool(pa and pb and pa.get("finger") is not None and pb.get("finger") is not None)
        flight = (b["t"] - releases[a["seq"]]["t"]) / frequency if a["seq"] in releases and ra["segment"] == rb["segment"] else None
        frozen = None
        if supported:
            same = ra["derived_position"] == rb["derived_position"] and a["mods"] == b["mods"]
            frozen = model.effort(pb["name"]) + model.penalty_keys(pa["name"], pb["name"], same)[1]
        reasons = local + session_reasons
        tables["intervals"].append(dict(common, **context, from_seq=a["seq"], to_seq=b["seq"], from_edit_seq=ea[0]["seq"] if len(ea) == 1 else None,
            to_edit_seq=eb[0]["seq"] if len(eb) == 1 else None, segment=rb["segment"], from_position=ra["derived_position"], to_position=rb["derived_position"],
            down_down_seconds=seconds, log_down_down_seconds=math.log(seconds) if seconds > 0 else None, flight_seconds=flight, flight_censored=flight is None,
            from_shift_left=ra["shift_left_before"], from_shift_right=ra["shift_right_before"], to_shift_left=rb["shift_left_before"], to_shift_right=rb["shift_right_before"],
            shift_transition=(ra["shift_left_before"], ra["shift_right_before"]) != (rb["shift_left_before"], rb["shift_right_before"]),
            from_row=pa.get("row"), to_row=pb.get("row"), from_column=pa.get("column"), to_column=pb.get("column"),
            distance_u=math.hypot(pa["x_u"]-pb["x_u"], pa["y_u"]-pb["y_u"]) if supported else None,
            same_key=ra["derived_position"] == rb["derived_position"], same_finger=pa["finger"] == pb["finger"] if supported else None,
            hand_alternation=(pa["finger"] < 5) != (pb["finger"] < 5) if supported else None,
            finger_assignment=ASSIGNMENT, frozen_pair_effort=frozen, decision="excluded" if reasons else "accepted", reasons=_reasons(reasons),
            idle_sensitivity_eligible=not (local + without_idle)))
    return tables


def coverage(tables):
    cells = Counter((r["contributor_id"], r["mapping_hash"], r["protocol_version"], r["prompt_bank_version"], r["build_configuration"], r["geometry"], r["keyboard_category"]) for r in tables["sessions"])
    return {"matrix": [dict(zip(("contributor_id", "mapping_hash", "protocol", "bank", "build", "geometry", "keyboard"), k), sessions=n) for k, n in sorted(cells.items())],
            "denominators": {name: {"raw_rows": len(rows), "decisions": dict(Counter(r.get("decision", r.get("motor_session_decision")) for r in rows)),
                                     "reasons": dict(Counter(reason for r in rows for reason in r.get("reasons", "").split("|") if reason))} for name, rows in tables.items()},
            "repaired_position_events": sum(r["position_rule"] == POSITION_VERSION for r in tables["events"]),
            "position_counts": dict(Counter(r["derived_position"] or "unresolved" for r in tables["events"])),
            "attribution": dict(Counter((r["source"] + "/" + r["link"]) for r in tables["edits"])),
            "accepted_pairs": dict(Counter((str(r["from_position"]) + ">" + str(r["to_position"])) for r in tables["intervals"] if r["decision"] == "accepted")),
            "shift_states": dict(Counter(f"L{int(r['shift_left_before'])}R{int(r['shift_right_before'])}" for r in tables["events"] if not r["up"])),
            "idle_sensitivity": {"primary_accepted_intervals": sum(r["decision"] == "accepted" for r in tables["intervals"]),
                                 "including_idle_sessions": sum(r["idle_sensitivity_eligible"] for r in tables["intervals"])}}
