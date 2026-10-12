"""Layout effort analysis: port of ``KeyboardAnalysis.performAnalysis``,
``LayoutResults`` and the brief/text reports.

Effort components per finger (index 0-9):
  base    sum_c  effort(key(c)) * freq(c)
  s-bigram  sum over same-finger bigrams of distinct characters
            freq(ab) * penalty_same_finger[min(2, rowdiff)], booked to key(a)'s finger
  n-bigram  sum over neighbour-finger bigrams
            freq(ab) * penalty_neighbour[outermost finger][min(2, rowdiff)],
            booked to the outermost finger (negative penalties are benefits)
Totals only include fingers whose base effort is positive, as in the original.
"""
from __future__ import annotations

from dataclasses import dataclass

from .frequency import BigramFreq, CharFreq
from .javacompat import java_format_fixed
from .keyboard import Key, KeyboardLayout, is_neighbour_finger, is_same_finger, outermost_finger


@dataclass
class FingerBigram:
    key1: Key
    key2: Key
    bigram: BigramFreq


@dataclass
class LayoutResults:
    layout: KeyboardLayout
    messages: list[str]
    key_freq: dict[int, float]  # id(key) -> frequency
    finger_freq: list[float]
    hand_alternation: float
    same_finger_bigrams: list[FingerBigram]
    neighbour_penalty_bigrams: list[FingerBigram]
    neighbour_benefit_bigrams: list[FingerBigram]
    finger_effort: list[list[float]]  # [base, same-finger, neighbour][finger]

    def effort_totals(self) -> dict[str, float]:
        base = same = neighbour = overall = 0.0
        for i in range(10):
            b, s, n = (self.finger_effort[c][i] for c in range(3))
            if b > 0:
                base += b
                same += s
                neighbour += n
                overall += b + s + n
        return {"base": base, "same_finger": same, "neighbour_finger": neighbour,
                "bigram": same + neighbour, "total": overall}

    def same_finger_bigram_freq_by_finger(self) -> list[float]:
        result = [0.0] * 10
        for fb in self.same_finger_bigrams:
            if is_same_finger(fb.key1.finger, fb.key2.finger):
                result[fb.key1.finger] += fb.bigram.freq
        return result

    def same_finger_bigram_total(self) -> float:
        per_finger = self.same_finger_bigram_freq_by_finger()
        total = 0.0
        for i in range(5):
            left, right = per_finger[i], per_finger[9 - i]
            if left > 0 or right > 0:
                total += left
                total += right
        return total

    def brief(self) -> dict:
        """Values of the published comparison table (``KeyboardAnalysisBriefHTMLReport``)."""
        totals = self.effort_totals()
        sfb = self.same_finger_bigram_total()
        return {
            "layout": self.layout.name,
            "keyboard_type": self.layout.keyboard_type,
            "base_effort": totals["base"],
            "same_finger_bigram_percent": sfb * 100,
            "bigram_penalty": totals["bigram"],
            "total_effort": totals["total"],
            "display": {
                "base_effort": java_format_fixed(totals["base"], 3),
                "same_finger_bigram_percent": java_format_fixed(sfb * 100, 2) + "%",
                "bigram_penalty": java_format_fixed(totals["bigram"], 3),
                "total_effort": java_format_fixed(totals["total"], 3),
            },
        }


def _lookup_freq(char_freqs: list[CharFreq], ch: str) -> CharFreq | None:
    for cf in char_freqs:
        if cf.char == ch:
            return cf
    return None


def _bigram_keys(layout: KeyboardLayout, bf: BigramFreq) -> tuple[Key | None, Key | None]:
    return layout.lookup_char(bf.string[0]), layout.lookup_char(bf.string[1])


def perform_analysis(layout: KeyboardLayout, char_freqs: list[CharFreq],
                     bigram_freqs: list[BigramFreq]) -> LayoutResults:
    messages = []
    if layout.rows > 4:
        messages.append("Warning: Too many rows")
    messages += layout.missing_letters() + layout.duplicate_letters()

    key_freq: dict[int, float] = {}
    for row in range(layout.rows):
        for col in range(layout.cols):
            key = layout.lookup_pos(row, col)
            if key is not None:
                total = 0.0
                for ch in key.chars:
                    cf = _lookup_freq(char_freqs, ch)
                    if cf is not None:
                        total += cf.freq
                key_freq[id(key)] = total

    finger_freq = [0.0] * 10
    for cf in char_freqs:
        key = layout.lookup_char(cf.char)
        if key is not None:
            finger_freq[key.finger] += cf.freq

    hand_alternation = 0.0
    for bf in bigram_freqs:
        key1, key2 = _bigram_keys(layout, bf)
        if key1 is None or key2 is None:
            continue
        if key1.hand != key2.hand:
            hand_alternation += bf.freq

    same_finger, neighbour_penalty, neighbour_benefit = [], [], []
    for bf in bigram_freqs:
        key1, key2 = _bigram_keys(layout, bf)
        if key1 is None or key2 is None:
            continue
        if bf.string[0] != bf.string[1] and is_same_finger(key1.finger, key2.finger):
            same_finger.append(FingerBigram(key1, key2, bf))
    for benefit, target in ((False, neighbour_penalty), (True, neighbour_benefit)):
        for bf in bigram_freqs:
            key1, key2 = _bigram_keys(layout, bf)
            if key1 is None or key2 is None:
                continue
            if is_neighbour_finger(key1.finger, key2.finger):
                outer = outermost_finger(key1.finger, key2.finger)
                if layout.has_penalty_neighbour_finger(outer) != benefit:
                    target.append(FingerBigram(key1, key2, bf))

    base = [0.0] * 10
    for ch in layout.alphabet():
        key = layout.lookup_char(ch)
        if key is None:
            continue
        cf = _lookup_freq(char_freqs, ch)
        if cf is not None:
            base[key.finger] += key.effort * cf.freq

    same = [0.0] * 10
    for fb in same_finger:
        rowdiff = min(2, abs(fb.key1.row - fb.key2.row))
        same[fb.key1.finger] += fb.bigram.freq * layout.get_penalty_same_finger(rowdiff)

    neighbour = [0.0] * 10
    for fb in neighbour_penalty + neighbour_benefit:
        outer = outermost_finger(fb.key1.finger, fb.key2.finger)
        rowdiff = min(2, abs(fb.key1.row - fb.key2.row))
        neighbour[outer] += fb.bigram.freq * layout.get_penalty_neighbour_finger(outer, rowdiff)

    return LayoutResults(layout, messages, key_freq, finger_freq, hand_alternation,
                         same_finger, neighbour_penalty, neighbour_benefit, [base, same, neighbour])


def text_report(results: LayoutResults, max_same_finger: int = 10, max_neighbour: int = 10) -> str:
    """Port of ``KeyboardAnalysisTextReport`` (Java ``%f`` = 6 decimals, HALF_UP)."""
    def f(value: float, decimals: int = 6, *, is_float32: bool = False, space: bool = False) -> str:
        return java_format_fixed(value, decimals, is_float32=is_float32, space_flag=space)

    out: list[str] = list(results.messages)
    out += ["", "== Finger Frequency =="]
    total_left = total_right = 0.0
    for i in range(5):
        right = 9 - i
        if results.finger_freq[i] > 0 or results.finger_freq[right] > 0:
            out.append(f"finger {i}:  {f(results.finger_freq[i])}      finger {right}:  {f(results.finger_freq[right])}")
        total_left += results.finger_freq[i]
        total_right += results.finger_freq[right]
    out.append(f" total L:  {f(total_left)}       total R:  {f(total_right)}")
    out += ["", "== Bigram stats ==", f"Hand Alternation: {f(results.hand_alternation)}"]

    per_finger = results.same_finger_bigram_freq_by_finger()
    out += ["", "== Finger Bigram Frequency =="]
    total = 0.0
    for i in range(5):
        right = 9 - i
        if per_finger[i] > 0 or per_finger[right] > 0:
            out.append(f"finger {i}:  {f(per_finger[i])}      finger {right}:  {f(per_finger[right])}")
            total += per_finger[i]
            total += per_finger[right]
    out.append(f"        total *:  {f(total)}")

    out += ["", "== Top Same-Finger Bigrams =="]
    for fb in results.same_finger_bigrams[:max(1, max_same_finger)]:
        out.append(f"finger {fb.key1.finger}:  {fb.bigram.string}  {f(fb.bigram.freq, is_float32=True)}")
    out += ["", "== Top Neighbour-Finger Bigrams =="]
    for fb in results.neighbour_penalty_bigrams[:max(1, max_neighbour)]:
        out.append(f"fingers {fb.key1.finger}-{fb.key2.finger}:  {fb.bigram.string}  {f(fb.bigram.freq, is_float32=True)}")

    out += ["", "== Finger Effort ==", "              base s-bigram n-bigram    total"]
    effort = results.finger_effort
    sums = [0.0, 0.0, 0.0]
    for i in range(10):
        if effort[0][i] > 0:
            values = [effort[0][i], effort[1][i], effort[2][i], effort[0][i] + effort[1][i] + effort[2][i]]
            out.append(f"finger {i}:   " + "   ".join(f(v, 3, space=True) for v in values))
            for c in range(3):
                sums[c] += effort[c][i]
    values = sums + [sums[0] + sums[1] + sums[2]]
    out.append(" total *:   " + "   ".join(f(v, 3, space=True) for v in values))
    return "\n".join(out) + "\n"
