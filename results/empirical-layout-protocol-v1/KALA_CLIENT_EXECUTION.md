# Kala client collection execution

Date: 27 October 2026, Asia/Dhaka. Governing plan: [KCC-v1](KALA_CLIENT_COLLECTION_PLAN.md); protocol [BHE-v1.1](RESEARCH_PROTOCOL.md).

**Provisional client implementation is present and tested. Full protocol collection/release acceptance is not complete.** The production receiver/publisher and empirical evaluator were not deployed or promoted. This report distinguishes code from unperformed observations.

## Implemented behavior

The client now produces versioned /2 collection records while keeping /1 readers and original queued bytes. It records actual prompt versions, explicit unknown/provenance metadata, lineage semantics, saved task assignments and bounded local exposure history. The selected composer is matched against the replay binding. Raw mapping/alphabet bytes are frozen while the actual composer is built; raw-file, effective-style and build identities are separate. Changes of the live runtime interrupt collection.

Physical capture retains its bounded hook path, Shift/Space/prefix events, original clocks and repeat distinctions. Starts/resumes wait for released keys outside the active timer. Capture is scoped to the owned task field; keys from another field are not retained and loss of continuity ends the attempt. Initial-state/clock/field cases have synthetic evidence; no physical keyboard observation is implied.

Engine observations now include zero-output actions, proposed versus acknowledged output, native rule identifiers and compact native/imported composer state. Delivery and edit records retain physical-key links and uncertainty. Native Goti/Jhor output is unchanged under the affected tests. Imported branch semantics still require their pinned replay adapter; a family label is not independent semantic validation.

The 260-second scheduler has four counterbalanced coverage subblocks, with two text and two physical-key blocks. The probe surface draws a common staggered block, accepts either Shift, logs actual attempts and preserves incomplete suffixes without fabricating output. It is a declared geometry/cue assumption, not verified hardware. Text summaries exclude probe/warm-up time and output; incomplete text remains available. New notices/preview explain raw layout/composition data, voluntary sharing, uncertain local identity and public-history withdrawal limits.

## Version and content scope

Current packages use kala.typing-check.session/2, pilot protocol 2026.10-bhe-pilot-r3, schedule bhe-task-schedule-2 and capture-v5-keyboard-step-ready. The original implementation evidence below and client-execution.json describe the preceding r1/capture-v3 checkpoint. The [timed-step correction](STEP_TRANSITION_FIX.md) records the latest sources and checks. The existing bank 1.4.0 remains unchanged and is explicitly labeled a literary/calibration pilot. A new reviewed multi-domain/targeted bank is still required. Source-family review, native wording review, common-block geometry assumptions and observed-pilot limits remain visible in package limitations. No questionnaire, identity recovery or inferred expertise was added.

Known incompatible receiver capabilities block sharing. The local mock supports both schemas; HTTP tests exercise original-byte retries, conflicts, receipts and withdrawal. The deployed production receiver remains /1-only in the reviewed source, and mixed-schema publisher/index support is unfinished. Offline consented queueing does not imply production admission.

## Checkpoints

| Checkpoint | Actual status |
| --- | --- |
| C0 | client contract and synthetic parity implemented; production compatibility acceptance pending |
| C1 | implemented; unknown metadata and unverified lineage retained |
| C2 | runtime snapshots and active-style checks implemented; independent registry/semantic acceptance pending |
| C3 | bounded/scoped capture, continuity stop and initial-state wait implemented; granular loss spans and observed hardware/callback measurements pending |
| C4 | native rule/compact state plus engine/delivery records implemented; imported rules use family/state replay, independent semantic adapters pending |
| C5 | scheduler and task provenance implemented; existing bank reused as explicit pilot, reviewed broader/targeted bank pending |
| C6 | common-block physical probes and incomplete attempts implemented; geometry/cue assumptions and observed transfer remain unvalidated |
| C7 | task-aware summaries, preview/consent and bilingual UI implemented; native wording review pending |
| C8 | client/in-memory and local HTTP mock support verified for both formats; production receiver/publisher/index not implemented here |
| C9 | targeted automated and rendered-UI evidence passed; observed participant/deployment pilot pending |
| C10 | not released; collection-ready acceptance not achieved |

## Validation evidence

- Baseline: 84 targeted Release checks passed before implementation.
- Expanded affected Release gate: 692 passed, 0 failed. Later scope/incomplete-probe corrections: 124 passed, 0 failed. Two-version local HTTP gate: 2 passed, 0 failed. These runs overlap; do not add their counts.
- Earlier supporting gates include 496 external/style/output regressions and subsequent native rule/state observation comparisons. The evidence JSON preserves each run, including the initial obsolete screen-metadata assertions that failed before their intentional /2 expectations were updated.
- Research usage suite: 68 passed, 0 failed. Its new independent /2 auditor accepted synthetic empty, physical-probe and zero-output packages, preserved unknowns, and reported model_eligible=false and engine_semantics_validated=false.
- Resource checks pass: 98 Bangla typing-check translations, zero neutral fallbacks. English/Bangla and light/dark probe renders were generated; English/light and Bangla/dark surfaces were visually inspected, including the corrected staggered placement.
- Release assembly/build, source files, test results and synthetic fixture hashes are in [client-execution.json](client-execution.json). No full Kala suite, participant collection, actual hardware pilot, installed-client rollout, production upload or publication/removal experiment was performed.

## Remaining acceptance work

Complete the reviewed bank and family registry; obtain native review of the new Bangla wording; implement and validate production /2 admission and mixed-schema dataset/index handling; finish independent engine semantic replay adapters and finer loss/capacity measurements; then observe the intended Release/installer on the required physical keyboards, composition, focus/pause, consent, retry and withdrawal/publication scenarios. Only those observations can close their gates.

Forty development sessions across multiple dates and material mappings remains a future engineering milestone. It is not evidence of forty people or sufficient power. No model, numerical layout ranking or optimized replacement Goti/Jhor layout was created. Frozen J0/J1 inputs/scores/layouts remain separate.

Code lives in the Kala repository; its [local execution record](../../../kala/plans/typing-collection-v2/EXECUTION.md) and [wire contract](../../../kala/plans/typing-collection-v2/CONTRACT.md) link this handoff. No pre-existing work was reset or committed. Rollback keeps original queue bytes and withdrawal access and never strips /2 evidence to masquerade as /1.

## Timed-step correction

Timed steps now pause capture and the clock before showing the next task. Continued letters and held Enter/repeats cannot resume collection. The user chooses Begin next step or a fresh Enter after released keys; capture waits for released keys and a fresh field/composer. Reading time is excluded; late timer delivery is retained separately and does not consume the next task. See [the correction report](STEP_TRANSITION_FIX.md) and [current evidence](step-transition-execution.json). Full protocol acceptance and deployment remain pending.

The latest [keyboard transition amendment](KEYBOARD_TRANSITION_FIX.md) adds prominent paused/start notices, fresh Enter confirmation and Tab access to Stop. Current tests passed 85 in each client configuration and 69 research checks; the rebuilt installer is ready for user installation. The earlier mouse-only transition report is historical.
