# Can the received typing-study data be used?

Investigation date: 27 October 2026 (Asia/Dhaka). Dataset checkout:
`0b2f73be464909a83f25e8d06d75e51492fc6fc6`. Package hashes and exact checks are
in `audit.json`; commands and the next steps are in [MODELING_PLAN.md](MODELING_PLAN.md).

**The four received packages are intact and contain usable text and timing
measurements. Their reported scores can be reproduced. Proceed with a controlled
recruitment pilot after the issues below are resolved or explicitly accounted
for; broad recruitment is not yet signed off.** Downloaded packages cannot prove
the complete consent, retry and withdrawal workflow.

## What was actually received

| Quantity | Observed |
| --- | --- |
| Packages / contributor IDs | 4 / 2 |
| Prompts / measured prompts | 61 / 57 |
| Physical key events / text events | 7,228 / 3,108 |
| Protocols | r1, literature-r3, literature-r4, literature-r5 |
| Prompt banks | 1.0.0, 1.3.0, 1.4.0 |
| Fixed layouts | UniJoy (2 sessions), imported UniBijoy (2 sessions) |
| Keyboard categories / geometries | All external; 1 ANSI, 3 ISO |
| Build configurations | 3 Debug, 1 Release |
| Completion | All completed, each declaring 260 active seconds |
| Client quality flags / dropped / injected counters | All empty / zero / zero |
| Diagnostic dwell / down-down candidate rows | 3,525 / 3,049 |

These are contributor IDs, not verified unique people. One ID has three sessions;
the other has one. There are no Kala Jhor or Kala Goti sessions and no laptop
sessions. Four protocol identities mean zero replication within any one protocol.
Thousands of events do not create thousands of independent participants.

## Checks that passed

- Every compressed package matches its manifest byte length, SHA-256 and Git blob
  SHA. Gzip, strict JSON and package/manifest identities agree. No unlisted
  package, duplicate session or duplicate package was found.
- All edits replay to the exact final text using UTF-16 offsets, with matching
  removed text and valid selections. All recorded NFC copies match. Original
  strings were left unchanged.
- Event streams have increasing sequences, no duplicate sequence IDs and no
  backwards clock movement. Prompt boundary times, first-key times and repeat
  targets agree with their event records. Linked keys exist and precede the edits.
- Physical down/up streams have no unexplained key releases or duplicate initial
  downs. Fifty-six releases cross a prompt boundary and are fully explainable by
  earlier downs. One key remains held at the first session's final timeout. These
  intervals are censored rather than used as within-prompt dwell measurements.
- Within uninterrupted prompt segments, the high-resolution clock agrees with
  the unsigned Windows hook clock to within the client's 250 ms diagnostic limit.
  No interval exceeds that limit. This is a consistency check, not an independent
  laboratory measurement of absolute latency or a claim of 250 ms precision.
- Sum of measured prompt durations, excluding recorded pauses, differs from the
  declared session clock by 0.014–0.264 seconds. Small prompt-transition gaps explain
  the direction; the audit's explicit 0.5-second tolerance passes all four.
- The portable audit independently reproduces five-character WPM, backspace
  presses, correction episodes and both available anchor WPM values, within
  absolute floating-point tolerance `1e-8`.

For this snapshot, a separate investigation used the already installed .NET
8.0.31 `StringInfo` segmenter, pinned against runtime roll-forward, plus an
independent Python alignment and first-attempt implementation. **Accuracy, correct
graphemes/minute, first-try accuracy and attempted-unit counts also agree for all
four sessions.** See `score-crosscheck.json` for counts, comparisons, input hashes,
runtime and the investigation sources. This used no new installed package. It is
snapshot-specific evidence; the portable audit command does not yet implement
Unicode grapheme segmentation and does not silently reuse these results for new
packages. Historical client binaries were not rebuilt.

## Concrete issues to address before wider recruitment

**Right Shift has no recorded physical-position label.** Across the four sessions,
92, 115, 160 and 180 events respectively have `pos = null` (547 events total).
Every one has `vk = 0xA1`, `sc = 0x36`, `ext = 1`. Microsoft's
[virtual-key table](https://learn.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes)
identifies `0xA1` as Right Shift. The inspected client `ScanCodePositions.Position`
returns from its extended-key table before reaching its nonextended Right Shift
case, explaining the null label for these recorded tuples. This is a position
mapping gap; the raw codes survive. Confirm it with physical keyboards, correct
future labels, and version any historical derived-label repair. Do not discard or
rewrite the original packages. Existing `key-pairs.csv` excludes pairs with null
positions, so it cannot yet be used as a complete Shift model input.

**One text event has an unknown delivery source despite an exact key link.** In
session `s_8c120ebaf18e4547885d0cf2b557ffa9`, event 1707 is a two-code-point insertion
with `source = unknown`, linked to physical key 1706. The key is a prior consumed
keydown and replay passes. `link = exact` does not establish a known delivery
source. Quarantine this edit and any neighboring timing/attribution features from
clean symbol-level training until correlation behavior is validated. This does
not invalidate the session's reconstructable final text or aggregate score.

**The r3 session ends with 53.177 seconds of empty input.** Its last measured
prompt is empty with no first key; the session still completes at 260 seconds
with no quality flag. The numeric summary is internally consistent, but the long
empty period affects speed and signals that participant behavior/idle detection
must be observed in a pilot. Do not shorten the denominator after inspecting the
score. Keep a predefined idle-quality policy and report sensitivity separately.

**A mapping hash is not a mapping snapshot.** Packages identify mappings but do
not contain the full key-to-output rules. Preserve the exact mapping/style and
engine versions in a research registry before imported-layout files can be lost.
Physical-key timing is usable now; reliable symbol/grammar features need those
rules. Actual finger choices, comfort and prior experience are not collected.

## What a matching score means

Five-character WPM counts Unicode scalars, with the client's minus-one convention;
it is not Bangla words/minute or graphemes/minute. Session WPM joins measured
prompt responses with spaces, including warm-up and repeats. First-try accuracy
is a word-level measure. Native user corrections are counted separately from
composition replacements. On timeouts, accuracy scores an attempted target prefix
whose length is capped by final-response grapheme count. A high percentage is not
evidence that the entire displayed passage was completed.

Matching arithmetic verifies measurement implementation for these packages. It
does not establish that this metric is the right learning target, that all real
keystrokes were captured, or that one layout is faster. The current four sessions
are enough to build and exercise ingestion, quality checks and feature extraction.
They cannot estimate participant-independent key costs, compare layouts or
validate the frozen effort rankings.

## Evidence still requiring an observed pilot

No live upload, consent flow, offline retry, receipt lookup, server restart or
withdrawal was performed in this investigation. Published bytes were checked
against the published manifest, not against a separately obtained pre-upload
client copy. These end-to-end checks are required in the plan. The current client
source explicitly ships typing checks with Learn in Release; older Debug-only
pilot documents are historical and should not be treated as the current boundary.
The Release package here is consistent with the newer source, but is not itself
proof that the current release passed a complete pilot.

The frozen layout model, search inputs, reproduction lock and published scores
were not changed. No layout performance result was fitted from this sample.
