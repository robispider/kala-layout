# Received typing-study data audit

Status: **pass_with_review**. 4 of 4 packages passed the implemented integrity/measurement checks; 2 contributor IDs.

This is a pipeline pilot, not evidence of a layout effect or recruitment sign-off. See MODELING_PLAN.md for the recruitment gates and modeling plan.

| Session | Protocol | Build | Prompts | Keys | Edits | Review items |
| --- | --- | --- | --- | --- | --- | --- |
| s_961ab610458d4beaba4eb7dce149e7da | 2026.10-r1 | Debug | 29 | 2189 | 952 | unknown_physical_positions |
| s_430535cce30b49c1a06727e8bec55e16 | 2026.10-literature-r3 | Debug | 11 | 1405 | 598 | empty_prompt_over_30s, unknown_physical_positions |
| s_8c120ebaf18e4547885d0cf2b557ffa9 | 2026.10-literature-r4 | Release | 11 | 1888 | 815 | unattributed_text_edits, unknown_physical_positions |
| s_d8dd557ac0f646569c6452a19c9ebe76 | 2026.10-literature-r5 | Debug | 10 | 1746 | 743 | unknown_physical_positions |

Checks include compressed-byte and Git blob hashes, bounded gzip/strict JSON, IDs, event ordering, UTF-16 edit replay/selection ranges, NFC, first key, repeats, prompt clocks, disabled assistance, duration reconciliation, scalar WPM, backspaces, edit episodes, anchor WPM and two-clock key intervals.

Measured prompt duration may differ from the session clock by up to 0.5 seconds (versioned audit tolerance for transitions); values are retained in audit.json. The key-clock comparison allows 250 ms, matching the existing client diagnostic. Pairs are consecutive non-repeat keydowns within one prompt and pause segment, with 0 < interval <= 30 seconds; no winsorization. Grapheme scores are unverified by this command.

Cross-boundary releases are matched globally for integrity but censored from dwell samples. Review candidate rows before training. No prompt or final text is copied to these outputs.
