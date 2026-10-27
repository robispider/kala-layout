"""Independent study summary arithmetic with a pinned grapheme segmenter."""
import re
import unicodedata

from .usage_graphemes import graphemes, VERSION as SEGMENTER

VERSION = "usage-scores-v1"
PROTOCOLS = {"2026.10-r1": "1.0.0", **{
    f"2026.10-literature-r{i}": f"1.{min(i, 4)}.0" for i in range(1, 6)}}


def align(a, b):
    prior = [(i, 0) for i in range(len(b) + 1)]
    for i, aa in enumerate(a, 1):
        row = [(i, 0)]
        for j, bb in enumerate(b, 1):
            row.append(min(((prior[j-1][0] + (aa != bb), prior[j-1][1] + (aa == bb)),
                            (prior[j][0] + 1, prior[j][1]), (row[-1][0] + 1, row[-1][1])),
                           key=lambda v: (v[0], -v[1])))
        prior = row
    return prior[-1]


def calculate(package):
    from .usage_metric import require, utf16_index
    normal = lambda s: unicodedata.normalize("NFC", s)
    units = lambda s: graphemes(normal(s))
    words = lambda s: [v for v in re.split('[ \\n\\t]', s) if v]
    reference = response = distance = matches = word_count = first_count = 0
    prompts = package["prompts"]
    for p in prompts:
        require(p["segmenter"] == "dotnet-8" and p.get("unicode_version", "15.0") == "15.0",
                "unsupported scoring segmenter")
        target, final = units(p["target_text"]), units(p["final_text"])
        require(p["attempted_units"] == min(len(target), len(final)), "attempted units mismatch")
        if not p["measured"]:
            continue
        # The client truncates a normalized target on timeouts, but scores all
        # of the target after Enter. Comparison copies, never original strings.
        attempted = p["target_text"] if p["end_reason"] == "enter" else "".join(target[:p["attempted_units"]])
        rg = units(attempted)
        d, m = align(rg, final)
        reference += len(rg); response += len(final); distance += d; matches += m
        lo = next(b["seq"] for b in package["boundaries"] if b["kind"] == "prompt-shown" and b.get("prompt_order") == p["order"])
        hi = next(b["seq"] for b in package["boundaries"] if b["kind"] == "prompt-ended" and b.get("prompt_order") == p["order"])
        firsts, edited, text = {}, set(), ""
        for e in package["text_events"]:
            if not lo < e["seq"] < hi or e["op"] == "selection":
                continue
            a, b = utf16_index(text, e["start"]), utf16_index(text, e["end"])
            if e["removed"] and e["source"] in {"native-key", "undo", "mouse"}:
                current = text.split(" ")
                for index in range(text[:a].count(" "), text[:b].count(" ") + 1):
                    edited.add(index)
                    firsts.setdefault(index, current[index] if index < len(current) else "")
            text = text[:a] + e["inserted"] + text[b:]
            for index, word in enumerate(text.split(" ")[:-1]):
                firsts.setdefault(index, word)
        typed = words(p["final_text"])
        for i, target_word in enumerate(words(attempted)):
            attempt = firsts.get(i, typed[i] if i < len(typed) else "")
            word_count += 1
            first_count += i not in edited and align(units(target_word), units(attempt))[0] == 0
    seconds = package["session"]["active_seconds"]
    qualifies = seconds >= 60 and reference >= 100
    return {"accuracy": 100 * max(0, 1 - distance / max(reference, response)) if reference + response else None,
            "correct_gpm": matches * 60 / seconds if qualifies else None,
            "first_try_accuracy": 100 * first_count / word_count if word_count else None}, {
                "reference_graphemes": reference, "response_graphemes": response,
                "distance": distance, "matched_graphemes": matches, "words": word_count,
                "first_try_words": first_count, "speed_qualifies": qualifies,
                "segmenter": SEGMENTER, "normalization_database": unicodedata.unidata_version}
