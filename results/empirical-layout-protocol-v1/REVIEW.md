# Review of the human-data layout evaluator work

Revision note, 27 October 2026: this initial review is historical. Its questionnaire, verified-person recruitment and person-level validation recommendations are superseded by the [no-questionnaire amendment](AMENDMENT_NO_QUESTIONNAIRE.md) and revised protocol. The original source findings and earlier test result remain unchanged.

Date: 27 October 2026 (Asia/Dhaka). Scope: local plans, implementation, saved evidence and targeted research tests. This review changes no application code, research code, model, dataset or published score.

## Assessment

The direction is appropriate for the owner's objective: learn a reusable cost model from Bangla typing, compile a candidate fixed layout into physical actions, score those actions on common texts, and search for improvements. Volunteers need not test every candidate. However, a model that predicts ordinary intervals within familiar mappings is not yet evidence that it can reliably rank unfamiliar mappings or new composition styles.

The present implementation is an auditable prototype with useful refusal gates, not a completed empirical evaluator. The next investment should be measurement and transfer design, followed by complete operation models—not a larger optimization run or a ranking from the current sample.

The separate [research protocol](RESEARCH_PROTOCOL.md) makes the evaluator, Goti/Jhor searches, and an independently reproducible challenge required deliverables. Its numerical gates are proposed study decisions, not established statistical facts.

## What is already useful

| Work | Assessment and evidence |
| --- | --- |
| Immutable packages, hashes, independent replay and score checks | Strong foundation. Source inspection finds UTF-16 edit replay, pinned grapheme handling, raw/derived distinctions and snapshot verification. Keep these. |
| Right Shift repair | Derived recovery is appropriate; the saved pipeline reports 547 repaired event labels without rewriting packages. Local Kala capture changes exist. Physical-device and deployed-build evidence is still pending. |
| Reason-coded feature tables | Useful provenance, pause segmentation, negative flight retention and no bridging over excluded events. These should become the canonical audit layer. |
| Guarded model fitting | Correctly refuses the present sample. Participant weighting, contributor resampling and simple baselines are useful components. |
| Layout adapters and search skeleton | NFC replay, explicit grammar identity, deterministic swaps and unsupported-context refusal are the right interfaces. They have synthetic test coverage, not empirical performance evidence. |
| Separation from J0/J1 | Appropriate. The new study should have its own score and season, with the original model retained as a benchmark. |

Saved evidence: [execution record](../usage-metric-pilot-v1/EXECUTION.md), [validation record](../usage-metric-pilot-v1/validation.json), [pipeline report](../usage-metric-pipeline-v1/REPORT.md), and [mapping registry notes](../../data/usage-metric-registry/README.md).

## Changes needed before an empirical ranking

| Priority | Finding | Consequence | Required next work |
| --- | --- | --- | --- |
| Critical | The primary extractor excludes modifier presses, spaces, replacements and multi-code-point insertions. The scorer rejects transitions touching these operations. | Full Bangla texts remain unscoreable even after a larger clean-letter fit. Composition exclusions also remove operations that distinguish Goti from Jhor. | Model the complete physical downstroke stream with explicit Shift and composition state. Space and valid multi-code-point output must be first-class supported operations. |
| Critical | Equal contributor weights are implemented, but participant/session/prompt intercepts are not. | Equal weights do not remove speed differences correlated with layout, device or action distribution. Coefficients can absorb these differences. | Use within-participant information and regularized participant/session effects; validate standardized predictions on entirely new people. |
| Critical | One mapping ties each symbol closely to a physical key; familiar-layout cohorts may also differ in skill. | Key costs and language familiarity cannot generally be separated from one mapping alone. More events from the same people do not solve this. | Recruit several mapping/rule groups, share text families across groups, add short counterbalanced physical-action probes, and test held-out mappings. |
| High | The implemented holdouts are contributor and prompt family, evaluated separately. There is no implemented layout/rule-family holdout. | A pass does not establish transfer to an unseen layout or a new style. | Add joint person/text tests, held-out mapping and grammar-family tests, and a later locked confirmation cohort. |
| High | A trace labeled clean means an attributable single-code-point insertion; it is not necessarily a correct action relative to the target. | Incorrect but uncorrected letters can enter the timing sample. Composition replacements may be incorrectly treated as unusable instead of valid typing. | Validate target alignment and engine state separately from event attribution. Retain errors, repairs and ambiguous alignments as distinct outcomes. |
| High | Current predictions exponentiate log intervals and sum them; the implementation correctly labels these as sums of conditional medians. | They cannot be relabeled expected completion time or measured speed. | Preserve the median-sum diagnostic; introduce a separately versioned expected-interval score only after training-only retransformation and held-out aggregate calibration pass. |
| High | Support is currently exact transition contributor count, with a minimum of three. | This guards unsupported inference, but prevents broad transfer and says little about unseen trigrams, symbol reassignment or rules. | Define direct, validated-generalization and unsupported tiers; validate withholding contexts deliberately. Never substitute J1 costs for missing empirical costs. |
| High | The main ridge features include frozen pair effort. | A fit could inherit existing assumptions rather than independently test them. | Make a human-data-only structural model the primary candidate. Compare a separate J0/J1-assisted model and report ablations. |
| High | The receiver validates an exact session format, stage vocabulary and 260-second limit. | A new protocol label alone cannot carry arbitrary added metadata, task types or durations. | Coordinate versioned client, receiver, serializer and research adapters. Preserve old queued packages. |
| High | Search uses model bootstrap draws that also guide candidate selection; current search emits held-out results during its progress. | A winner can exploit model error. Repeatedly viewing final-text scores compromises their later use as independent confirmation. | Separate search, development selection and one-time confirmation; use fresh human evidence for selected extreme candidates. |
| Medium | Familiarity, actual fingering and sufficiently detailed device history are missing. | Ordinary keyboards can support timing inference, but not observed finger force, movement or universal comfort claims. | Add minimal self-report and device/session metadata. Label fingering inferred; keep optional discomfort ratings separate. |
| Medium | The old plan's opening and several dataset descriptions still say only audit exports exist or grapheme checks remain unimplemented. | Readers can confuse historical pending items with current local implementation. | Use this dated review plus source hashes for status. Update those descriptions during the later implementation task. |

Source anchors: [features](../../src/bangla_dh/usage_features.py), [fit](../../src/bangla_dh/usage_fit.py), [evaluator](../../src/bangla_dh/usage_evaluator.py), [pipeline gates](../../src/bangla_dh/usage_pipeline.py), [current policy](../../data/usage-metric-policy-v1.json). The receiver findings come from kala-usage-metric's PackageValidator.cs and CLIENT_CONTRACT.md; exact reviewed files are hashed in the accompanying manifest.

## Current evidence and its limits

The saved feature build contains four sessions, two contributor IDs and four protocol identities: 1,076 eligible primary intervals, or 1,320 in the idle-session sensitivity analysis. IDs are not independently verified unique people. The original audit describes external keyboards only, with no laptop sessions. An exact historical UniBijoy mapping remains missing. Family review, engine replay evidence and the observed pilot remain pending.

Absence of Goti/Jhor sessions does not itself invalidate learning shared physical costs. Absence of evidence for the required composition operations, typing strategies and transfer does prevent claiming a validated full-layout ranking.

I reran the targeted research suite: **63 usage tests passed**. I did not rerun the full research suite, Kala tests or receiver tests. The saved record reports 250 research tests and targeted Kala/receiver checks; those are previous execution evidence. No live participant, deployed receiver, upload or withdrawal experiment was performed in this review.

The source tree already contained substantial uncommitted implementation work before this review. The assessment applies to those exact local files, not to an assumed published release.

## Recommended decision

Proceed with the separate protocol as the implementation specification. First close the observed pilot and registry gaps, version the collection additions, and expand eligible operation coverage. Then collect a varied familiar-layout cohort and test transfer. Release a public score only at its stated validation tier; allow an explicit unsupported result for a candidate outside that tier.

Twenty people with two sessions is a useful development milestone. It is neither a sample-size justification nor an automatic release threshold. Do not require everyone to learn new layouts, and do not promise empirical ranking of arbitrary novel rules before evidence supports those rules.
