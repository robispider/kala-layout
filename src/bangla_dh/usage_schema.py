"""Strict field/type adapter for kala.typing-check.session/1, frozen 2026-10-27.

Protocol labels remain metadata at receiver admission. Analysis support is
separately resolved by the protocol registry; unknown metadata never pools.
"""
import datetime
import re

VERSION = "usage-schema-v1"
FLAGS = {"focus-loss", "layout-change", "mode-change", "paste-attempted", "onscreen-keyboard-used",
         "physical-events-missing", "text-replay-mismatch", "events-dropped", "clock-jump",
         "idle-over-30s", "roman-output-detected"}


def validate(package, *, allow_unknown_category=False, allow_step_transition=False):
    from .usage_metric import require, integer, number

    def fields(obj, required, optional=""):
        require(type(obj) is dict, "schema object required")
        names, extra = set(required.split()), set(optional.split())
        require(names <= obj.keys() and obj.keys() <= names | extra and all(obj[n] is not None for n in names),
                "schema missing or unexpected fields")

    def strings(obj, names):
        require(all(type(obj.get(n)) is str for n in names.split()), "schema string required")

    def ints(obj, names, minimum=0):
        require(all(integer(obj.get(n), minimum) for n in names.split()), "schema integer required")

    def choice(obj, name, allowed):
        require(type(obj.get(name)) is str and obj[name] in allowed.split(), "schema unsupported choice")

    def boolean(obj, name):
        require(type(obj.get(name)) is bool, "schema boolean required")

    def optional_int(obj, name):
        require(obj.get(name) is None or integer(obj[name]), "schema nullable integer required")

    fields(package, "schema session input clock prompts key_events text_events boundaries integrity", "summary")
    strings(package, "schema")
    s = package["session"]
    fields(s, "contributor_id session_id session_number protocol_version prompt_bank_version variant_id randomization_seed kala_version build_configuration os_version keyboard_category geometry started_utc completion active_seconds quality_flags")
    strings(s, "contributor_id session_id protocol_version prompt_bank_version variant_id kala_version os_version started_utc")
    ints(s, "session_number", 1)
    require(type(s["randomization_seed"]) is int and -2**31 <= s["randomization_seed"] < 2**31, "invalid seed")
    for n in ("protocol_version", "prompt_bank_version"):
        require(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._+\-]{0,127}", s[n]) is not None, "invalid version label")
    require(re.fullmatch(r"c_[0-9a-f]{32}", s["contributor_id"]) is not None and
            re.fullmatch(r"s_[0-9A-Za-z]{20,40}", s["session_id"]) is not None, "invalid package identity")
    require(re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", s["os_version"]) is not None, "invalid OS version")
    require(re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::00(?:\.0{1,7})?)?Z", s["started_utc"]) is not None,
            "start must have minute precision")
    try:
        datetime.datetime.fromisoformat(s["started_utc"].replace("Z", "+00:00"))
    except ValueError:
        require(False, "invalid start date")
    choice(s, "build_configuration", "Debug Release")
    choice(s, "keyboard_category", "laptop-builtin external unknown" if allow_unknown_category else "laptop-builtin external")
    choice(s, "geometry", "ansi iso unknown")
    choice(s, "completion", "completed stopped interrupted")
    require(number(s["active_seconds"]) and 0 <= s["active_seconds"] <= 260, "invalid duration")
    require(type(s["quality_flags"]) is list and all(type(f) is str and f in FLAGS for f in s["quality_flags"]), "invalid quality flags")
    inp = package["input"]
    fields(inp, "layout_id layout_name origin input_family mapping_hash engine_version composition_only autocorrect_enabled spelling_correction_enabled suggestions_enabled spelling_marks_enabled personal_rules_enabled")
    strings(inp, "layout_id layout_name mapping_hash engine_version")
    require(len(inp["layout_name"]) <= 80, "layout name too long")
    choice(inp, "origin", "bundled imported"); choice(inp, "input_family", "fixed phonetic")
    for name in ("composition_only autocorrect_enabled spelling_correction_enabled suggestions_enabled spelling_marks_enabled personal_rules_enabled").split():
        boolean(inp, name)
    fields(package["clock"], "frequency origin_ticks")
    ints(package["clock"], "frequency", 1); ints(package["clock"], "origin_ticks")
    fields(package["key_events"], "columns rows")
    for name in ("prompts", "text_events", "boundaries"):
        require(type(package[name]) is list, "schema array required")
    for name in ("columns", "rows"):
        require(type(package["key_events"][name]) is list, "schema key array required")
    for p in package["prompts"]:
        fields(p, "prompt_id prompt_version target_text stage order measured shown_ticks end_ticks end_reason final_text final_text_nfc attempted_units segmenter", "repeat_of previously_seen first_key_ticks unicode_version")
        strings(p, "prompt_id target_text final_text final_text_nfc segmenter")
        ints(p, "prompt_version", 1); ints(p, "order shown_ticks end_ticks attempted_units")
        boolean(p, "measured")
        if "previously_seen" in p: boolean(p, "previously_seen")
        if "unicode_version" in p: strings(p, "unicode_version")
        optional_int(p, "first_key_ticks"); optional_int(p, "repeat_of")
        choice(p, "stage", "ready warmup natural-1 coverage natural-2 anchor-repeat")
        choice(p, "end_reason", "enter timeout stop layout-change")
    for e in package["text_events"]:
        fields(e, "seq t op start end removed inserted sel_before sel_after source link", "key_seq correction")
        ints(e, "seq t start end"); strings(e, "removed inserted")
        choice(e, "op", "insert delete replace selection")
        choice(e, "source", "kala-delivery native-key undo mouse unknown")
        choice(e, "link", "exact inferred unknown"); optional_int(e, "key_seq")
        require(e.get("correction") is None, "composition-only correction payload")
        for n in ("sel_before", "sel_after"):
            require(type(e[n]) is list and len(e[n]) == 2 and all(integer(v) for v in e[n]), "invalid edit selection")
    for b in package["boundaries"]:
        fields(b, "seq t kind", "reason prompt_order"); ints(b, "seq t")
        choice(b, "kind", "start ready-check-passed prompt-shown prompt-ended pause resume layout-change stop timeout")
        require(b.get("reason") is None or b["reason"] in {"focus-loss", "button", "mode-change"} or
                allow_step_transition and b["kind"] == "pause" and b["reason"] == "step-transition", "invalid boundary reason")
        optional_int(b, "prompt_order")
    fields(package["integrity"], "text_replay_ok injected_events_seen dropped_events")
    boolean(package["integrity"], "text_replay_ok"); ints(package["integrity"], "injected_events_seen dropped_events")
    summary = package.get("summary")
    if summary is not None:
        fields(summary, "", "wpm5 correct_gpm accuracy first_try_accuracy correction_episodes backspace_presses anchor_first_wpm5 anchor_repeat_wpm5 scorer")
        for name, value in summary.items():
            if name == "scorer": strings(summary, name)
            elif name in {"correction_episodes", "backspace_presses"}: ints(summary, name)
            else: require(value is None or number(value), "invalid summary number")
