# Recruitment readiness and the empirical typing-model pipeline

27 October 2026. Proposed plan; only the received-data audit and initial diagnostic
exports are implemented. This is separate from the frozen layout-search model.

## Objective and decision

The owner's target is a **transferable empirical evaluator of Bangla fixed
layouts**: learn costs from people typing Bangla, then apply those learned costs
to the physical action sequences required by any compatible existing or new
layout. Volunteers provide training observations; they are not required to type
every layout the evaluator will score. Direct head-to-head layout experiments
are an optional later validation method, not the collection design or primary
deliverable.

First verify that the measurements are complete and recoverable. Then learn
physical-action/transition costs, build the layout-to-action scoring adapter, and
use the evaluator to search for improvements. All three are required deliverables;
an interval predictor alone does not complete the research objective. Actual
long-term typing speed and discomfort remain separate outcomes, not quantities
directly established by short recordings or physical key positions.

The four existing packages are a useful integration fixture. They pass the
implemented integrity checks and snapshot-specific score cross-check, with
important review items in [FINDINGS.md](FINDINGS.md). Current decision: **controlled
pilot after the measurement issues are addressed; broad recruitment remains
pending pilot evidence**. No model fit or layout ranking is justified yet.

## Stage 0 — Close measurement gaps

1. Reproduce the Right Shift null-position tuple with a physical external keyboard
   and a laptop keyboard. Check left/right Shift, repeated/held Shift, punctuation,
   number row and ISO-only keys. Fix or explicitly version its position mapping
   before producing complete Shift features. Historical repair must derive a new
   label from preserved raw fields, retain the original null, and record its rule.
2. Reproduce delivery-source correlation under fast composition, replacements,
   native Backspace/Delete, selection and delayed notifications. Verify that an
   exact key link is never used as evidence of a known delivery source. Retain a
   reason-coded exclusion for the existing unknown-source edit.
3. Define idle handling before looking at outcomes: preserve wall/active time,
   flag empty measured prompts over 30 seconds and within-prompt key gaps over
   30 seconds, and report analyses both including and excluding affected sessions.
   Never silently subtract idle time from the client speed denominator.
4. Create an immutable registry keyed by mapping hash plus engine/style version.
   Include imported mapping contents, composition rules, symbol labels and their
   hashes; verify the registry hash using the actual client hashing convention.
   Resolve layout identity by hash, not localized display name or import ID.
5. Freeze one current protocol/bank/client build for the pilot. Archive its bank,
   preparation/selection rules and comparison policy. Maintain historical protocol
   adapters. r1/r3 sentence-based and r4/r5 timed passage behavior must remain
   separate. Changes to collection behavior require a recorded methodology version.

Acceptance: synthetic mutation tests and physical recordings verify the corrected
labels/attribution; every required key category has recognized positions or a
documented exclusion; all package scores can be independently reproduced. The
current Python audit intentionally leaves grapheme-dependent fields unverified.
Add a version-pinned, tested Unicode segmenter before treating that command as a
complete automated score verifier. Keep the standard-library rule; importing a
new third-party package requires owner approval. Do not substitute code-point or
drawn-glyph counts for grapheme counts.

## Stage 1 — Demonstrate the whole collection path

Use a few consenting internal testers first, then approximately 5–10 consenting
pilot volunteers with varied skills across laptop/external and ANSI/ISO keyboards
and bundled/imported **fixed** layouts. People should normally use a layout they
already know, so unfamiliar-layout learning does not dominate the training
observations. Aim for varied physical key, pair and Shift coverage; participants
do not need to switch between Kala Jhor and Kala Goti. This is a coverage target
for the pilot, not a statistical sample-size justification. Use public prompts
and observe the current shipping
Release build as well as diagnostic builds where needed.

| Scenario | Evidence needed to pass |
| --- | --- |
| Ordinary 4:20 check | Observe physical typing; retain consented pre-upload gzip hash; receiver and public package match exactly; complete timing and score audit passes. |
| Pause/resume and focus loss | No captured out-of-scope typing; pauses excluded from active time; no interval crosses pause/focus boundaries; flags and boundaries explain behavior. |
| Fast typing, corrections, long/repeated keys | No dropped events; Shift and composition replacements remain reconstructable; inspect text-source and key link quality. |
| Timed stage/Enter boundary | Preserve unfinished text; match stage transition and timeout reasons; no cross-prompt motor interval; repeats identify the actual earlier target. |
| Stop and interruption | Mark incomplete explicitly; preserve valid partial records without treating them as full sessions. |
| Decline sharing | Local result remains usable; no research upload/public package appears. |
| Offline and reconnect | Explicitly consented outbox survives restart; upload resumes once; gzip hash and session ID remain stable. |
| Duplicate retry and receiver restart | One original package/manifest entry; stable receipt; no overwritten or duplicated measurement. |
| Withdrawal with queued data | Use a disposable consenting test identity; current server/public packages and manifest disappear; queued retries cannot republish it; refreshed derived outputs exclude it. |
| Ordinary external typing | The recording boundary remains limited to the study; verify the app's existing typing/correction behavior in representative external apps. |

Record build, OS, keyboard, geometry, mapping hash, protocol/bank, scenario,
observer, result, package/receipt hashes and exclusion reason. Keep credentials,
deletion secrets and private external-app text out of the research repository.
Withdrawal removes current data; historical Git copies may remain, as documented
in the dataset README. Refresh withdrawals before each later analysis.

Acceptance for wider recruitment: no unexplained missing text/key events, no
checksum/identity/replay failures, independent scores agree, all required scenarios
have observed results, and every remaining warning has a tested recovery or
predefined exclusion. Recheck affected scenarios when changing the capture build.
An upload success or passing synthetic tests alone does not meet this gate.

## Stage 2 — Make the data pipeline repeatable

Proposed flow:

```text
current manifest + unchanged gzip packages + mapping/protocol registries
  -> immutable analysis snapshot and content hashes
  -> independent validation and reason-coded quality decisions
  -> versioned session / prompt / edit / physical-event tables
  -> eligible motor intervals and text/error outcomes
  -> coverage and split-readiness report
  -> contributor-grouped fit / calibration / held-out evaluation
  -> transferable physical-action cost model
  -> candidate layout + typing grammar + standard Bangla benchmark texts
  -> round-trip-verified physical action sequences and predicted layout costs
  -> improvement search, coverage/uncertainty report and reproducible run manifest
```

Already implemented:

```powershell
$env:PYTHONPATH = "src"
python -m bangla_dh audit-usage-data
python -m bangla_dh audit-usage-data --out work/usage-audit
python -m unittest discover -s tests -p test_usage_metric.py
```

The command writes `audit.json`, `REPORT.md`, `prompts.csv`, `dwell.csv`,
`key-pairs.csv` and `run-manifest.json`, using the repository write guard. It uses
the standard library, reads packages without modifying them, rejects integrity
errors with nonzero exit status and preserves review warnings. The dedicated
`usage-data.yml` workflow covers data-only pushes that the main CI skips. Local
checks do not prove that workflow has run on GitHub.

Remaining implementation:

- Add complete schema/protocol adapters, including all field types/allowed values,
  pinned grapheme scoring and frozen golden cases. The present audit checks
  measurement invariants; it is not a complete port of the receiver validator.
- Add a session table and canonical event/edit tables, stable schemas even for
  empty inputs, and `accepted`, `excluded`, `review` decisions by analysis target.
  An unknown-source edit may exclude symbol attribution while leaving aggregate
  final-text analysis valid. Propagate session quality to every candidate row.
- Preserve raw/derived position labels and version the mapping resolver. Represent
  Shift key identity, held state and modifier transitions separately from letters.
- Derive down-down intervals, dwell (up minus down), and flight (next down minus
  prior up). Negative flight reflects overlap and must not be discarded as bad
  timing. Censor boundary/held-key intervals; exclude autorepeat from primary motor
  fits and retain a separate repeat stream.
- Identify consecutive clean text-producing actions. Do not bridge over excluded
  correction/modifier events to invent a new adjacency. Flag transitions involving
  spaces, corrections, selection, unknown sources, multi-code-point composition and
  repeats. Use per-operation models or predefined strata where appropriate.
- Record geometry, hand/finger **assignment assumption**, key row/column/distance,
  same-key/same-finger/hand alternation, Shift state, stage, elapsed practice/session
  number, target length, repeated/seen status and protocol/engine. Actual fingering
  and physical keyboard dimensions are unknown; never present inferred fingers as
  observed finger choices.
- Link each derived row back to package hash, session, prompt order and event IDs.
  Keep targets only in original packages; derived text identities use hashes. If
  character labels are needed, store approved symbol-level labels rather than
  copying passages into results.
- Write a coverage matrix by contributor × layout hash × protocol × keyboard,
  plus key/pair/Shift/event-attribution coverage. Report excluded counts and raw
  denominators at every stage. Rebuild from the current manifest so withdrawals
  remove data from fresh outputs and invalidate older analyses/model versions.

Current CSVs are diagnostic candidates. They contain warm-up/unmeasured rows and
may include corrections and modifiers; they do not implement these clean training
eligibility rules. In particular, pairs with null positions are omitted. Do not
feed them directly into a fit.

## Stage 3 — Learn transferable physical-action costs

Define the primary prediction as **log down-down interval for eligible consecutive
physical text actions**, conditional on participant, prompt and context. Report
milliseconds too. Fit correction/error probability separately; combine speed and
error only with an explicitly chosen, validated objective. Dwell is a useful
secondary target, not a direct estimate of travel effort or discomfort.

Start with a training-set median baseline, then an additive regularized regression
using a small set of key geometry, pair, Shift and stage features. A standard-library
implementation is feasible for this baseline. Test it against the frozen effort
score as a feature/baseline; do not interpret J0/J1 units as measured milliseconds.
Keep participant/session/prompt effects or grouped residual summaries so one fast
typist does not define the key costs. Use partial pooling when there is enough
replication; any external fitting library remains a separate approval decision.

For layout scoring, standardize participant, prompt length, stage, familiarity
and other nuisance settings to a declared reference condition. Do not reward a
candidate because its original contributors happened to type faster. The shared
costs must use physical keys, geometry, transitions and modifier/composition
context that can also be constructed for an untested layout. A table of average
WPM by contributor or layout name cannot perform this task. Separate structural
features from symbol/language context and test transfer rather than assuming
that correlations observed on one mapping are causal motor costs.

Before a more complex model, require enough independent contributors and varied
prompts for the chosen features; report unsupported coefficients instead of
pretending sparse key pairs are estimated. Later sample-size planning should use
pilot variance, a chosen minimum useful effect and simulation at participant level.
Do not choose a final volunteer count from the number of key events.

Twenty contributors with at least two sessions each are a proposed initial
training collection, with both sessions normally on their familiar layout.
The repeats help assess measurement stability and day/session variation. This
does not guarantee sufficient coverage or accuracy, but it does not require
twenty people to learn each candidate layout. Missing key/pair/Shift contexts
should guide later targeted collection. Model development can begin before
precision or unseen-layout validation is sufficient for strong ranking claims.

## Stage 4 — Evaluate without leakage

- Split by contributor first. All sessions, repeats and derived rows for an ID
  stay in one fold. Never random-split key events. Record split IDs and seeds.
- Test a second generalization axis using held-out prompt/passage families or
  source works, not just exact prompt IDs. Near-duplicates and repeated passage
  parts need one family identity even when IDs differ. Learn preprocessing,
  trimming rules, normalizers and hyperparameters only from training folds.
- Keep protocol/bank/build strata separate initially. Pool only after documenting
  adapter equivalence and testing sensitivity. Hold out one layout/mapping when
  assessing transfer to unseen layouts; ordinary person holdout cannot establish it.
- Report log-time and millisecond MAE, median error, error by key/Shift/geometry/
  stage and participant-weighted performance. For error predictions report log
  loss/Brier score and calibration. Confidence intervals resample contributors,
  not individual keystrokes. Compare every candidate with the simple baseline.
- An optional later direct comparison can test whether a model-proposed
  improvement works in use. That separate experiment would need experienced
  users or recorded learning/exposure; it is not required of every training
  volunteer. Experience is absent from current packages; add it only through an
  explicitly versioned study decision. Keep all comparisons fixed-layout only.

With two contributor IDs and four protocols, the current data can test pipeline
execution and leakage guards only. It cannot support credible validation folds,
population confidence intervals or causal layout comparisons. A production fit
command should return `insufficient_data` until its preregistered coverage and
split gates are met, rather than publish a misleading model.

## Stage 5 — Score existing and untested layouts

Build a versioned evaluator with three inputs: the fitted cost model, a candidate
fixed-layout mapping plus its actual composition/vowel-entry rules, and a common
Bangla benchmark corpus. The candidate need not occur in the training dataset.

For each benchmark text, produce a valid physical action sequence, including
Shift, hasant and multi-action composition. Verify that replay yields the target
NFC code points; report unreachable characters and never silently skip them.
Specify an achievable typing strategy when several sequences can produce the
same text. An idealized cheapest strategy must be labeled as such. Do not assume
one code point, one glyph or one grapheme equals one keystroke.

Extract the same structural action/transition features used during training and
apply the standardized model. Sum interval predictions over a nonoverlapping
definition of the sequence: do not add dwell and down-down predictions as though
they were independent elapsed-time components. A model trained on log intervals
must explicitly distinguish summed conditional medians from expected time and
validate any log-to-mean correction. Reading pauses, novice learning and fatigue
are not automatically predicted by a motor-interval sum.

Required output for each candidate:

- A normalized empirical keying-cost score on identical texts, with a declared
  reference layout set to 100. Also report the underlying modeled time units,
  such as predicted keying milliseconds per 1,000 NFC code points. Do not label
  this as observed page completion time or mastered-layout WPM.
- A breakdown by keys, transitions, Shift and composition recipes, plus stroke
  count per output unit. Show which common Bangla sequences contribute most.
- Input/round-trip coverage and model-support coverage. Distinguish observations
  supported across contributors from feature-based extrapolation or fallback
  assumptions. A numerical score alone must not conceal unsupported contexts.
- Uncertainty in scores and candidate differences, propagated through the whole
  scoring process by refitting/resampling contributors where feasible. Report
  sensitivity to fingering assumptions and benchmark domains separately.
- A separate correction-risk estimate only for targets/contexts whose transfer
  has been validated. Do not manufacture a universal error or comfort score from
  timing observations. Do not merge speed and error into one number without an
  explicit objective and sensitivity report.

Acceptance: the same physical sequence gets the same standardized cost regardless
of layout display name; distinct vowel recipes can produce distinct action costs;
round-trip failures and unsupported contexts are visible; benchmark inputs and
parameters are identical for candidates; person and text holdouts beat a simple
baseline, with additional layout holdouts when diverse mappings are available.
Until transfer is tested, scores for unobserved layouts are experimental model
predictions. This does not prevent evaluating them; it limits the strength of
the resulting claims.

## Stage 6 — Use the evaluator to improve layouts

Run a constrained search over symbol swaps, Shift placements and explicitly
supported typing recipes, minimizing the empirical benchmark score. Permit
constraints that retain familiar positions or limit the number of changed keys.
Report predicted improvement, changed mappings, driving text/action patterns,
uncertainty and unsupported-context share for each retained candidate.

Keep an untouched text benchmark for final candidate evaluation. Prevent the
optimizer from exploiting gaps in the model: penalize or reject poorly supported
contexts according to a predeclared policy, compare several plausible models
and fingering assumptions, and retain candidates whose gains survive those
checks. Model-only improvement remains a prediction; targeted human testing can
subsequently validate the strongest changes. Volunteers need not type every
candidate searched by the computer.

Acceptance: reproducible candidate scores, valid round trips, a concrete set of
proposed changes with explained gains, and an honest conclusion when uncertainty
does not support an improvement. Publishing a replacement Kala layout is a new
research season, not an automatic consequence of fitting this evaluator.

## Stage 7 — Release an empirical evaluator separately

Every fit writes a new `results/<empirical-phase>/<run>/` with input snapshot and
hashes, code revision/hash, feature/schema/protocol versions, normalization and
exclusion policy, mapping registry, split IDs, seeds, model parameters, evaluation,
uncertainty, limitations and a machine-readable model card. Include quality and
coverage gates in the run result. Preserve an audit-only mode even when fitting
cannot proceed. Do not train from withdrawn/currently unlisted packages.

Deliver the cost model, layout-scoring adapter and candidate-improvement report
together, with their validation status. Changing the published search objective
or Kala layouts requires a **new research season**, with the required
lock/challenge/docs/website updates together. Existing J0/J1, Kala layouts and
published rankings remain frozen during experimental evaluator development.

## Recommended order of work

1. Resolve Right Shift and delivery attribution; verify a fresh controlled package.
2. Complete the observed upload/retry/withdrawal and physical-key pilot matrix.
3. Add portable grapheme verification, registries, clean features and coverage gates.
4. Collect familiar-layout Bangla typing from the cohort using the frozen protocol, monitor audit
   failures on every batch, and stop a faulty collection batch promptly.
5. Learn and validate transferable action costs as independent coverage permits.
6. Score any compatible fixed layout through its verified action sequences on
   common Bangla texts; report coverage, uncertainty and extrapolation.
7. Search for concrete layout improvements and validate promising predictions.

This sequence lets the existing small dataset exercise the machinery immediately
while protecting new volunteers' time from untested collection assumptions.
