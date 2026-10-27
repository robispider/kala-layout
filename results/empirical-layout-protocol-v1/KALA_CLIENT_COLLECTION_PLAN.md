# Kala client collection implementation plan

Date: 27 October 2026, Asia/Dhaka. Plan ID: KCC-v1-draft-2026-10-27.
Governing protocol: [BHE-v1.1](RESEARCH_PROTOCOL.md); related [mitigation plan](MITIGATION_PLAN.md) and [no-questionnaire amendment](AMENDMENT_NO_QUESTIONNAIRE.md).
Status: separate proposed client implementation handoff based on current local source. No application changes, builds, software tests, collection or deployment were performed in writing it. Existing uncommitted capture changes are inspected source, not assumed shipping behavior. Exact input hashes and source status are recorded in run-manifest.json.

Implementation update: see the [execution report](KALA_CLIENT_EXECUTION.md) for tested provisional client changes and still-open protocol/release gates. The original checklist below remains the acceptance specification.

## 1. Outcome and boundaries

Update Kala's typing-check collector so voluntarily shared recordings support reconstruction of all physical actions, exact fixed-layout composition, task context and interruptions. Keep the simple flow: select an available fixed layout, read the task notice, type predefined tasks, inspect results/package and optionally share. Retain decline and withdrawal.

No experience, typing-habit, finger-use, demographic, comfort or device questionnaires; no accounts, identity recovery, fingerprints or cross-device matching. Existing random ContributorId means local research-store lineage, not a person or device. Missing answers remain unknown with provenance. Speed/accuracy cannot establish experience.

This implements the client side of protocol sections 2 and 4–8 and collection dependencies in section 16. Alignment, fitting, uncertainty, transfer validation, search and challenge publication remain research work. A client release or forty-session milestone cannot validate the evaluator.

Preserve native Goti/A hasant-plus-sign and Jhor/D context/repeated-key behavior. Study composition-only mode is scoped to the owned study target. Ordinary external-app Bangla typing, enabled corrections, on-screen input and saved output preferences retain accepted behavior. Probes never change global mappings/style/settings.

## 2. Current source assessment

| Surface | Current local source finding | Required work |
| --- | --- | --- |
| [SessionPackage](../../../kala/kala/Learning/Study/SessionPackage.cs) and reader | Strict /1 records already contain physical events, edits, clocks, boundaries and basic metadata | Separate /2 additions; retain /1 reads and original queued bytes |
| [StudyTap](../../../kala/kala/Learning/Study/StudyTap.cs) | Bounded down/up/repeat capture; before-event modifier mask; Arm clears tracked key state | Preserve stream/performance; verify start/resume initial state and loss boundaries |
| [StudyRecorder](../../../kala/kala/Learning/Study/StudyRecorder.cs) | Exact field snapshots and conservative delivery correlation; no persistent engine-transaction ledger; prompt version recorded as 1 | Persist engine/delivery provenance, including zero-output actions; record actual prompt version |
| [TypingCheckForm](../../../kala/kala/Ui/TypingCheck/TypingCheckForm.cs) | Keyboard category is mandatory; unknown geometry binds as ANSI; UI timer is 250 ms | Allow unknown; separate rendering assumptions; record real task/deadline times |
| [TypingCheckController](../../../kala/kala/Learning/Study/TypingCheckController.cs) | Existing 20/80/80/60/20 active-second stages and pause clock | Four 20-second coverage subblocks with task identity and explicit boundaries |
| [PromptBank](../../../kala/kala/Learning/Study/PromptBank.cs), coverage and sequence | Bank 1.4.0 / session protocol r5; passage and repeat support; no physical-cue contract | New reviewed bank/task version; preserve historical labels/behavior |
| [ResearchStore](../../../kala/kala/Learning/Study/ResearchStore.cs) | Random ID/deletion secret; bounded set of seen measured prompt IDs | Retain linkage/withdrawal; add bounded exposure counts and unknown-history semantics |
| [KalaLayoutSources](../../../kala/kala/Learning/Kala/KalaLayoutSources.cs) and host | ContentHash can incorporate alternate style; engine label is app version/class/capture-v2 | Separate raw file and effective runtime identities; match replay to actual active composer |
| [IDeliveryObserver](../../../kala/kala/IDeliveryObserver.cs) and TypingSession | Acknowledged output only; zero-output suppression need not notify it | Separate optional study engine-action observation; no output change |
| [ResearchUploader](../../../kala/kala/Learning/Study/ResearchUploader.cs) and outbox | Capability check uses a global schema constant; consented original bytes are queued/retried | Per-package schema checks and mixed /1-/2 queues |

The client already records many Shift, Space, replacement and multi-code-point events. Their exclusion from current research modeling also needs research-side changes; duplicating physical logs will not fix it.

## 3. Proposed /2 observable-data contract

Plan kala.typing-check.session/2 because new task, engine and provenance records extend strict /1. Freeze names/types/enums/limits with the receiver and research reader before implementation. Names below are proposed, not existing APIs. Preserve historical /1 byte and column meanings.

Keep key columns seq, t, vk, sc, ext, up, rep, pos, mods, consumed, hook_ms. Declare mods as state before the transition; derive state after from scan/extended identity. Add companion records rather than changing an old column silently.

| Record | Addition or clarification | Validation rule |
| --- | --- | --- |
| Session/consent | Applicable notice/consent version, wave/task-manifest identity, build/capture version, existing session/lineage identifiers | Truthful explicit sharing decision; no backdated consent assertion; no secrets in package |
| Configuration | Physical category/geometry with provenance; rendering/probe assumptions separately; observed configuration/change records | Unknown allowed; prior selections unverified; no inferred switch/connection/device identity |
| Runtime inputs | Raw mapping hash/bytes or immutable reference; effective binding, composer/style, grammar/dependency and settings hashes | Raw file hash distinct from style-derived ContentHash; inputs independently retrievable |
| Prompt/task | Actual version, exact target/cue, kind/block/order, source and duplicate family/domain, bank/selection identity, seeds, chosen assignment, exposure/repeats | Unknown history differs from zero known prior exposure; metadata are pinned bank facts |
| Timing | Planned active offsets, actual shown/end ticks, practice status, pause/reset/control events, end reasons | One monotonic timebase; never backdate display onset or hide overruns with clamping |
| Engine events | Event/transaction ID, physical references, semantic rule/operation, replayable bounded state transition, outcome and timestamps | Includes handled zero-output prefixes/resets; unavailable state cannot be recovered from opaque hashes alone |
| Delivery/edit links | Source engine events, delivery identity/outcome/acknowledgement, observed timestamps, edit references and confidence | Multiplicity supported; proposed output is not delivered output; proximity is not exact attribution |
| Probe attempts | Cue/expected physical sequence, attempt/repetition, actual event references, correctness/status and reset | Empty text is valid; never invent edits to satisfy a natural-text validator |
| Integrity | Bounded stream-specific loss counts/spans, uncertain state, capture discontinuities and clock diagnostics | Stop unexplained loss; no silent truncation or fabricated complete capture |

Keep raw UTF-16 edits/selections, original text and NFC comparison copies; pin normalization/grapheme/replay versions. Record actual effective composition-only study settings, not computed constants hiding runtime mismatch. Keep owned-field Unicode independent of the user's saved external output mode.

Use immutable, bounded, consent-previewed runtime bundles: bundled inputs may use retrievable hash-verified registry references; imported inputs need exact bytes/dependencies. Freeze before capture, not by rereading a mutable path on finish. Do not upload unrelated files, absolute user paths or arbitrary imported metadata. If exact inputs cannot be shared/recovered, report unavailable replay and do not call it compliant attributable collection; retain local typing-check access.

Seeds alone cannot reconstruct history-dependent selection. Store chosen assignment, eligible-pool/variant identity and selection-policy version. Describe deterministic selection as deterministic; for probabilistic selection record its defined probability and conditioning pool.

## 4. Ordered client checkpoints

Implement one checkpoint at a time with source/build hashes, affected tests, observed cases and unresolved dependencies. Read Kala's AGENTS.md, external-app contract and UI guide before shared typing-path changes. No new dependency is required. All acceptance artifacts below are future work.

### C0. Freeze contract and baseline

Produce /1-to-/2 field, enum, bound and compatibility matrices and golden-package specification. Cover probes without text, constructive replacement, unknown geometry, partial tasks, loss and consent. Freeze runtime-bundle/operation vocabulary. Identify which shipping build matches the locally changed source.

Acceptance: client, receiver and research reader agree on fixtures and limits; old packages remain unchanged/readable. Production /2 collection waits for receiver admission, publisher/index and research-adapter readiness. New bank labels do not bypass validation.

### C1. Truthful metadata without questions

Files: SessionPackage.cs, SessionPackageReader.cs, ResearchStore.cs, TypingCheckForm.cs/Designer and host metadata wiring.

- Keep random lineage/session IDs and withdrawal scope. No new person/device linkage or recovery.
- Remove mandatory laptop/external answering from the new flow. Reuse a historical selection only with its source, otherwise unknown; do not alter old packages.
- Separate unknown physical geometry from any drawing/recipe fallback. Geometry-dependent probes need support or explicit deferral.
- Snapshot build/engine/configuration before capture. Hash outside callbacks; retain current privacy-preserving UTC precision unless explicitly versioned. Timing uses monotonic ticks.
- Pass prompt.Version instead of hardcoding 1. Migrate seen-ID sets as known prior exposure with unknown count; reset/pruned history is incomplete, not zero lifetime exposure. Bound storage.

Acceptance: collection starts without a new question, unknowns round-trip, resets/multiple store users create no person claim, and research hash changes do not re-key learning progress.

### C2. Exact active mapping, grammar and settings

Files: KalaLayoutSources.cs, MainForm.ProductUi.cs, Ui/HostModels.cs, runtime bundle wiring, SessionPackage.cs and PromptCoverage.cs.

Snapshot the active translator's actual mapping/style/settings after activation. Compare prepared replay binding with the live bundle; native lesson and alternate saved composers may differ. Keep raw-file, effective binding and grammar/dependency identities separate. Interrupt on runtime input/settings replacement instead of mixing versions under one hash.

Keep native Goti/Jhor rules; new bank validation replays the actual registered composer rather than silently using legacy teaching recipes. Treat supported alternate imported styles as distinct rule identities. Unicode study output does not modify the saved external output preference.

Acceptance: isolated replay reconstructs registered native/imported golden traces; rule/settings changes affect identity even with unchanged display name/raw map. Missing historical bytes are not guessed.

### C3. Physical stream, initial state and boundaries

Files: StudyTap.cs, StudyRecorder.cs, ScanCodePositions.cs, hook integration and lifecycle.

Retain all physical downs/ups including Shift, Space, prefixes, corrections/navigation and manual repeats, with autorepeat, consumed status and clocks. Keep bounded nonblocking hook publication; no JSON/disk/network/scoring or full-state serialization in callbacks.

Start/resume from verified all-keys-released state, with waiting outside active time, or a reliably observed initial-state design fixed in C0. Clearing _down is insufficient. Label the resume-trigger key as control; do not leak it into the next task. Record reset/censor boundaries at task transition, pause, focus loss and stop; do not fabricate missing keyups. Focus elsewhere means no task capture.

Preserve rollover/negative flight and equal-timestamp sequence order. Do not add epsilon to avoid log(0). Localize stream loss where possible; never bridge excluded/uncertain segments. Unexplained loss ends the collection attempt with a safe local result and diagnostic status under C0 admission policy. Observation failure never changes delivery or causes output replay.

Acceptance: both Right Shift encodings, held/switching modifiers, manual versus auto repeats, endpoint censoring and generation-safe restart/disposal pass. No interval spans discontinuity or lost state.

### C4. Engine actions and delivery transactions

Files: StudyRecorder.cs, StudyTextRecorder.cs, IDeliveryObserver.cs or a separate study-only interface, TypingSession.cs and applicable fixed-layout managers.

Keep acknowledged-delivery observation's current meaning. Add optional, scoped engine observation for translation attempts, zero-output handled actions, rule/state transitions, resets, rejected/unsupported actions and separate delivery acknowledgements. Emit compact bounded records in the typing path; enrich/serialize after capture. Define state conventions with replay adapters.

Link key-to-engine, engine-to-delivery and delivery-to-edit separately, allowing multiplicity. Never promote time proximity to exact linkage. Observe native Backspace/Delete/selection/undo separately; constructive composition replacement is not correction. Distinguish engine proposals, observed edits and control-induced field clearing.

Scope to the actual registered predefined task target/control, not every field in Kala. Detach on focus loss, stop, decline, disposal and capture failure. Never persist external-app composition, window titles or private text in snapshots; snapshots contain only bounded study context. Keep rule resets replayable.

Acceptance: golden traces cover zero/one/multiple-code-point output, prefixes, Goti full vowels, Jhor context/repetition, hasant/conjuncts/nukta, both Shift sides, errors/repairs, delayed/coalesced edits and failed/partial deliveries. Engine/edit replay agrees where attributed, unknowns stay visible. Observer enabled/disabled yields identical decisions/output; it remains inactive outside the study.

### C5. Task scheduler and reviewed bank

Files: TypingCheckController.cs, PromptBank.cs, PromptCoverage.cs, ResearchPromptSequence.cs, TypingCheckForm.cs and a new versioned bank/task manifest.

Retain 260 active seconds, with setup/breaks outside the timer:

| Stage | Seconds | Required metadata |
| --- | ---: | --- |
| Warm-up | 20 | Excluded from primary fit |
| Natural passage 1 | 80 | Source family/domain, exact text and local exposure |
| Coverage | 80 | Two targeted Bangla and two physical probes, 20 seconds each; task kind, cue and repetition |
| Natural passage 2 | 60 | Different text/source family under the frozen assignment |
| Anchor repeat | 20 | Exact earlier segment and repeat reference; separate analysis |

Counterbalance coverage order and natural domains with saved assignments; preserve passage order. Use source-family/near-duplicate/domain metadata, common reachable anchors and varied licensed/native-reviewed prose rather than a literature-only bank. Keep collection material separate from optimizer and confirmation sets. Freeze waves before outcomes are inspected; choose targeted blocks from feature deficits, not preferred rankings.

Check monotonic active deadlines both on input handling and timer callbacks. Record actual display onset, deadline observation, finalization/reset and overruns; never backdate visible cues to nominal times or hide lateness by clamping a summary. Define deadline event ownership, duplicate Enter and asynchronous finish before implementation. A late key cannot become the next task's input.

Preserve incomplete text at timeout/stop. Boundary Enter and setup/control actions remain distinguished from scored text. No stale field/composition state enters a fresh prompt. Anchor repeat must repeat the recorded segment; preserve passage part identities. Returning lineage gets fresh prompts where possible but does not establish a returning person or first-ever exposure.

Acceptance: fake-clock tests cover all subblock deadlines, pauses, early stop, timer overshoot, simultaneous Enter/timeout, no response and long passages. Assignment is reconstructible, actual prompt versions retained and observed coverage separated from planned coverage. No unreachable symbols silently disappear from a target.

### C6. Faithful physical-action probes

Files: dedicated Designer-declared probe surface, task scheduler, recorder and probe-attempt DTO/validator; reuse supported keyboard geometry drawing.

Show position cues for balanced pairs and short three/four-key sequences including Shift and Space, with brief untimed practice. Identify physical positions, not changing layout characters. Record expected sequence, onset, actual event references, repetition/attempt, correctness and reset. Do not prescribe finger or Shift hand. Unknown required geometry means unsupported/deferred cue, not falsely verified ANSI/ISO.

Use a dedicated owned target/sink; prevent ordinary layout composition from producing unrelated text during probes. Scope routing/suppression to that task, reset explicitly, and restore normal text typing at transition. Preserve wrong keys, controls and repeats. Probe correctness comes from physical events; empty final text/no text-event rows is valid. Make natural-text missing-events/Roman-output/shareability gates task-aware.

Acceptance: cues, holds/rollover, incorrect sequence, autorepeat, retry, pause/focus change and disposal replay faithfully; no background text capture or system-wide probe behavior. If deferred, explicitly label a partial collection wave and protocol amendment. A substitute text block is not a completed physical probe and cannot silently pass full task compliance. Research must validate probe-to-natural transfer before pooling its observations.

### C7. Results, preview, consent and UI

Files: SkillCheckScorer.cs, TypingCheckForm.cs/Designer, TypingCheckPreviewForm, research settings and TypingCheckUiStrings.resx / TypingCheckUiStrings.bn.resx.

Compute natural-text summaries only from eligible measured text tasks; probes/warm-up cannot inflate WPM, accuracy, anchor results or learning evidence. Keep incomplete-suffix handling. Export scorer versions/denominators and separate probe diagnostics. Research correct-path/error classification remains independent; existing observed summaries are not learned layout rankings.

Keep raw packages/runtime context in memory before explicit Send; only the consented outbox persists raw records. Preserve approved numeric-result/history behavior. Explain new mapping/engine/task data, precise timing publication and Git-history withdrawal limits in the notice/preview. Never silently assert pre-task consent where only later sharing was chosen. Preview must identify truncation and exclude secrets/unrelated metadata. Keep Send/Don't send and withdrawal, without adding a survey.

Static controls belong in Designer files; wording in neutral/Bangla .resx. Inspect both languages/themes and compact/large windows, including probe, key-release, unknown and offline states. Put technical rule IDs in advanced preview/package rather than the main task flow.

Acceptance: no mandatory questionnaire or keyboard-category answer; decline/close leaves no raw outbox package; no sharing before explicit consent. Errors remain observations rather than a fast-only sample. Stop/dispose restores temporary study state and preserves accepted external typing/settings.

### C8. Schema, outbox and receiver compatibility

Files: SessionPackageReader.cs, ResearchUploader.cs, ResearchOutbox.cs, versioned result/preview dispatch, mock uploader and tools/typing-study-server. Production receiver/publisher/research changes are coordinated dependencies.

Dispatch on actual package schema before version-specific field validation. Check each queued package's schema/protocol rather than one global current constant. Mixed /1-/2 queues retain gzip bytes, IDs, ownership/proofs, destinations and receipts across app/server restarts. Do not rewrite old packages into /2, recompress retries or strip /2 evidence to downgrade to /1.

Retain HTTPS checks, endpoint/destination binding, existing retry statuses and offline explicit-consent queuing. Distinguish absent configuration from explicitly incompatible configuration. Unsupported /2 is version-wait/incompatible, not an invitation to discard fields. Preserve existing 422 app-version wait policy unless a separate migration explicitly changes it.

Keep current 2 MiB compressed/expanded caps and key/text limits; specify bounded engine/probe/mapping/boundary limits in C0. Measure realistic worst-case complex-composition packages. If limits are inadequate, coordinate a bounded contract revision across readers rather than silently truncating or increasing only the client cap. Disk/queue failure cannot create a falsely shared partial session.

Acceptance: old/new golden packages agree across client, local mock, production receiver validator and research reader. Cover identical/conflicting retry, offline restart, capability change, closed collection, bounds, first-upload withdrawal and queued-retry withdrawal. Public publication/index/removal must be observed before release; local HTTP tests alone are insufficient.

### C9. Targeted tests and observed Release pilot

Run only checkpoint-affected classes, then one focused final collection gate. Do not run the full Kala suite unless requested. Add meaningful tests for the invariants above; existing suite names are starting filters, not evidence the proposed cases exist.

| Changed area | Existing suites and additions | Required evidence |
| --- | --- | --- |
| Capture/state | TypingStudyCaptureTests | Initial state, Shift encodings, prefixes, ordering, loss and no foreign-target records |
| Tasks/bank | TypingCheckControllerTests, TypingCheckPromptTests, ContinuousResearchTests | Four subblocks, deadline races, counterbalance, prompt versions, exposure/family semantics |
| UI/consent/results | TypingCheckUiTests, UnifiedResearchTests | No required survey/category answer, task-aware summaries, preview/decline/Send, localized resources and state restoration |
| Schema/transport | ResearchUploaderTests, TypingStudyServerTests | Mixed formats, malformed /2, bounds, exact-byte retries, capabilities, offline and withdrawal |
| Engine/style integration | TypingSessionTests, CompatibilityTypingTests and affected FixedStyle* classes with typing-style-plan filters | Observer neutrality, native Goti/Jhor/imported fidelity, external composition and corrections preserved |

Example from Kala's root after a capture checkpoint is implemented:

```powershell
dotnet test kala.BaselineTests/kala.BaselineTests.csproj -c Release --filter 'FullyQualifiedName~TypingStudyCaptureTests'
```

Use affected filters for other checkpoints. Build the intended Release client and verify packaging includes the new bank/resources/build metadata/capture code. A local build is not evidence that the deployed installer contains it.

Observe 5–10 consenting testers as a practical instrumentation budget, with the scenario coverage below. It is not an independent-person sample-size gate. Record observer/date, actual build/configuration, scenario and package/receipt/evidence hashes. Never publish secrets or unrelated external text.

| Observed scenario | Required result |
| --- | --- |
| Known laptop/external, ANSI/ISO, bundled/imported rules | Actual key events, runtime identity and replay agree; unknown hardware stays unknown |
| Both Shift sides/holds/switches, Space, fast composition/corrections | Complete physical/engine/edit ledger including prefixes and valid replacements |
| Held keys at start/resume, releases/rollover/repeats | Verified initial state, correct modifiers/repeats and endpoint censoring |
| Natural/probe boundaries, Enter/timeout/stop/incomplete output | Task ownership, clocks, resets and independent summaries agree |
| Focus/pause/mode/layout/configuration change and failed delivery | No bridged timing, stale attribution or background recording; safe pause/end |
| Preview/decline/offline/restart/identical and conflicting retry | Explicit consent, original bytes, accurate receipt and safe failure states |
| Withdrawal with pending retries and public publication/removal | Existing contract works through client, receiver and current published dataset |
| External Notepad/Word and affected compatibility targets | Accepted Bangla composition and enabled corrections remain; study observation inactive |

Synthetic/automated tests cannot mark these observed scenarios complete. Practice-field success alone cannot establish external-app compatibility. Any change after the pilot requires repeating affected cases on the final intended build.

### C10. Collection-ready release and handoff

Create a client validation report/manifest with source revision plus dirty-file hashes, build/installer hashes, schema/capture/protocol/bank versions, golden packages, automated results, observed pilot evidence and pending limitations. Include receiver admission/publication and independent research read/replay evidence.

Full collection readiness requires C0–C9 for the enabled scope: exact runtime provenance, truthful unknowns, all required tasks and no unresolved capture/replay/privacy/withdrawal failure. A probe-deferred pilot is useful partial evidence, not silent full BHE-v1.1 task compliance. No automatic raw upload, official layout replacement or learned-ranking publication accompanies the client rollout.

Hand off consented packages and immutable registries to kala-layout. Forty eligible development sessions across dates and three material mappings remains an engineering target, with separate session/lineage counts, concentration, rule diversity and observed action coverage. A local ID or count never verifies independent people, expertise, unseen-person prediction or speed gains.

## 5. External dependencies and rollback

The receiver independently implements /2 admission, nested bounds, cue/engine validation, config schema advertisement, publication/index and withdrawal. Research implements historical/new adapters, reviewed source families, exact replay, complete action eligibility and validation. They are acceptance dependencies, not code changes made by this plan.

Rollback disables the new collection entry while retaining ordinary Kala typing, consented queue bytes and withdrawal access. Do not pass /2 through old parsers or rewrite historical evidence/receipts. Re-enable after affected golden and observed cases pass on the replacement build. Any retained /1 collection is explicitly legacy, not full compliance with this plan.

## 6. Completion checklist

- [ ] No questionnaires, recovery, fingerprinting or inferred expertise/person claims.
- [ ] Existing lineage/withdrawal semantics retained; unknown category/geometry/history supported.
- [ ] Exact active mapping/grammar/settings/build provenance; historical identities preserved.
- [ ] Complete key, engine, delivery and edit evidence including Shift, Space and zero-output actions.
- [ ] Verified initial state, boundaries, loss, clocks and endpoint handling.
- [ ] Reviewed tasks, four coverage subblocks, physical probes and truthful exposure metadata.
- [ ] Task-aware results, preview, explicit sharing/decline and bilingual Designer-based UI.
- [ ] Mixed /1-/2 reads/queues, exact retries, bounded admission and withdrawal verified.
- [ ] Targeted automated evidence and separate observed Release/deployment scenarios recorded.
- [ ] Client readiness distinguished from model/transfer validation and population claims.

All items remain pending implementation/evidence. Documentation checks for this plan cover local links, protocol alignment, source provenance and artifact hashes. No software tests, build, deployed pilot or empirical ranking were performed for this documentation task.
