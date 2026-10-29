## Additional layout checks

An experimental check compares eight fixed layouts and examines 101 retained search candidates. Two diagnostics show what the combined effort score can hide:

| Diagnostic | Kala Jhor | Kala Goti | Windows Default |
| --- | --- | --- | --- |
| Shift use (% of non-space key presses) | 8.7% | 8.3% | 13.2% |
| Same-finger key changes per 100 text units | 1.56 | 1.40 | 5.18 |

Each number is an equal-weight average across held-out Wikipedia, newspaper and non-overlapping BARD news, using model-optimal fingering. A key change means consecutive non-space key presses on different physical keys assigned to the same finger; text units include spaces. These are calculated typing patterns, not measured speed or comfort.

Both Kala layouts have lower counts on these two diagnostics than Windows Default under these assumptions. Goti has fewer same-finger key changes and less Shift use than Jhor, while Jhor has lower published J1 effort. The comparison exposes a trade-off, rather than a new overall winner.

We also tested the Engram research’s learned key-pair preference table. Its coverage is incomplete, and its predictions have not been independently validated here or tested with Bangla typists, so we publish no whole-layout comfort ranking. The existing J1 results and challenge ranking remain unchanged.

[Read the full experimental report](https://github.com/robispider/kala-layout/blob/main/results/evaluator-e1/run-v1/REPORT.md), including all eight layouts, both fingering scenarios, candidate trade-offs and evidence limitations.

Source-verified Dvorak-7 and Engram movement checks add another trade-off: under traditional fingering, Goti earns more pair credit than Jhor, while Jhor has lower J1. Their pair-score bounds overlap under model-optimal fingering. Windows Default earns more Engram triple-order credit than either Kala layout, with text-escape and modifier limitations. [See all eight layouts and the explanation](MECHANICS.md).
