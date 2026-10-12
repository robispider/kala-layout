"""J0, the Colemak-fidelity objective (RESEARCH_SPEC section 6.5):

    J0(L) = Σ_i u_i K(L(c_i)) + Σ_{i≠j} v_ij B(L(c_i), L(c_j))

Two evaluation routes that must agree for single-action layouts:

* ``score_units``: from unit frequencies u and adjacent-unit frequencies v
  (the optimizer's form; every unit maps to one key action);
* ``score_tokens``: from a table of whitespace-delimited tokens, encoding each
  token with a key map. This also scores layouts that need several
  keystrokes for one unit (UniJoy's আ = ্ + া), where J0 sums the efforts
  of all keystrokes and the penalties of all consecutive keystroke pairs.

Both divide by the same N, the number of counted units in the corpus
(including space), so scores of different layouts on one corpus compare
directly. Space is typed by the thumb: K = 0, no penalty, and it separates
tokens, so cross-space pairs never carry a penalty.

Both routes also report J1 = J0 + M (RESEARCH_SPEC 6.6, Phase 3): M sums the
modifier effort of every keystroke (``KeyModel.modifier_effort``). J1 is
None for a layout that uses AltGr, which has no v1 cost.
"""
from __future__ import annotations

from collections import defaultdict

from ..bangla.grammar import Action, Escape, KeyMap
from .model import KeyModel

COMPONENTS = ("same_finger", "neighbour_penalty", "neighbour_benefit")


def _result(e1: float, parts: dict[str, float], m: float | None, extra: dict) -> dict:
    e2 = sum(parts.values())
    return {"J0": e1 + e2, "E1": e1, "E2": e2, **{f"E2_{k}": parts[k] for k in COMPONENTS},
            "M": m, "J1": None if m is None else e1 + e2 + m, **extra}


def score_units(assignment: dict[str, Action], u: dict[str, float], v: dict[tuple[str, str], float],
                model: KeyModel) -> dict:
    """J0 from unit tables. ``assignment`` maps unit → its single action;
    units without an action (space, unplaced units) cost nothing."""
    e1 = 0.0
    m: float | None = 0.0
    uncovered = 0.0
    for unit, freq in u.items():
        action = assignment.get(unit)
        if action is None:
            uncovered += freq
        else:
            e1 += freq * model.effort(action.key)
            modifier = model.modifier_effort(action.key, action.layer)
            m = None if m is None or modifier is None else m + freq * modifier
    parts = dict.fromkeys(COMPONENTS, 0.0)
    sfb = 0.0
    for (a, b), freq in v.items():
        if a == b:
            continue
        action_a, action_b = assignment.get(a), assignment.get(b)
        if action_a is None or action_b is None:
            continue
        kind, value = model.penalty_keys(action_a.key, action_b.key, action_a == action_b)
        if kind != "none":
            parts[kind] += freq * value
            if kind == "same_finger":
                sfb += freq
    return _result(e1, parts, m, {"same_finger_bigram_frequency": sfb, "unassigned_unit_frequency": uncovered})


def token_cost(steps, model: KeyModel, pairs: dict | None = None, weight: int = 1
               ) -> tuple[float, dict[str, float], int, int, float | None]:
    """(Σ K, penalties by kind, keystrokes, escapes, Σ M) of one encoded
    token. With ``pairs``, adds weight × penalty per (kind, action, action)."""
    e1 = 0.0
    m: float | None = 0.0
    parts = defaultdict(float)
    keystrokes = escapes = 0
    previous = None
    for step in steps:
        if isinstance(step, Escape):
            escapes += 1
            previous = None
            continue
        keystrokes += 1
        e1 += model.effort(step.key)
        modifier = model.modifier_effort(step.key, step.layer)
        m = None if m is None or modifier is None else m + modifier
        if previous is not None:
            kind, value = model.penalty_keys(previous.key, step.key, previous == step)
            if kind != "none":
                parts[kind] += value
                if pairs is not None:
                    pair = (kind, previous, step)
                    pairs[pair] = pairs.get(pair, 0.0) + weight * value
        previous = step
    return e1, parts, keystrokes, escapes, m


def describe_pair(kind: str, a: Action, b: Action, value: float) -> dict:
    return {"kind": kind, "keys": f"{a} → {b}", "outputs": a.output + " → " + b.output, "contribution": value}


def score_tokens(keymap: KeyMap, tokens, total_units: int, model: KeyModel, top_pairs: int = 15) -> dict:
    """J0 from (token, count) pairs; ``total_units`` is the corpus N."""
    e1 = 0.0
    m: float | None = 0.0
    parts = dict.fromkeys(COMPONENTS, 0.0)
    keystrokes = escapes = 0
    escaped_chars: dict[str, int] = defaultdict(int)
    pairs: dict = {}
    for token, count in tokens:
        steps = keymap.encode(token)
        t_e1, t_parts, t_keys, t_esc, t_m = token_cost(steps, model, pairs, count)
        e1 += count * t_e1
        m = None if m is None or t_m is None else m + count * t_m
        for kind, value in t_parts.items():
            parts[kind] += count * value
        keystrokes += count * t_keys
        if t_esc:
            escapes += count * t_esc
            for step in steps:
                if isinstance(step, Escape):
                    escaped_chars[step.char] += count
    n = float(total_units)
    return _result(e1 / n, {k: v / n for k, v in parts.items()}, None if m is None else m / n,
                   {"keystrokes_excluding_space": keystrokes, "escaped_characters": escapes,
                    "escaped_top": sorted(escaped_chars.items(), key=lambda kv: -kv[1])[:20],
                    "top_penalty_pairs": [describe_pair(kind, a, b, value / n) for (kind, a, b), value in
                                          sorted(pairs.items(), key=lambda kv: -abs(kv[1]))[:top_pairs]]})
