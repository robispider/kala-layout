# Mitigation plan: observable typing records without questionnaires

Date: 27 October 2026, Asia/Dhaka. Aligned protocol: BHE-v1.1-draft-2026-10-27.
Status: proposed implementation handoff; documentation only. No client, receiver, model, dataset or published score is changed by this plan.

This replaces the earlier mitigation recommendations for questionnaires, identity recovery, verified experience and independent-person recruitment. The [revised protocol](RESEARCH_PROTOCOL.md) governs the study; the [amendment](AMENDMENT_NO_QUESTIONNAIRE.md) explains the change. The [initial review](REVIEW.md) remains historical source evidence. This plan adds implementation detail without changing the protocol's proposed numerical gates.

## 1. Decisions and limits

Keep complete physical/text recording, exact composition replay, capture checks, varied common tasks, mapping/rule transfer tests and guarded candidate search. Volunteers may use their selected fixed layout; they do not need to learn every candidate. Prior familiarity remains unknown.

Remove experience, finger-use, habits, demographics, comfort and device questionnaires. Do not add accounts, identity recovery, hardware fingerprints, IP-based matching or typing-based identity inference. Consent, optional sharing and withdrawal still apply under the existing contract.

Interpret ContributorId as a local research-store lineage. It can include several people, and one person can appear under several lineages. Retain already-consented grouping where available; otherwise analyze whole sessions. A lineage is neither a verified person nor a physical device. No transport rename is needed merely to clarify this interpretation.

Forty eligible development sessions across multiple days and at least three materially different mappings is an engineering milestone. Repeats are encouraged but optional. Twenty IDs, forty sessions or a later collection date cannot establish independent people or population power. The earlier mandatory paired-person rule and 60–90-person budget do not apply to this collection mode.

Scoring, separate A/D searches and a reproducible model-score challenge remain deliverables. Their claims concern predicted cost under the frozen recording distribution and declared profile. New-person speed, experienced-user speed, learning benefit, comfort and causal switching effects require separate evidence.

## 2. Minimal client data contract

Record provenance for metadata: app-observed, event-derived, existing unverified selection, assumed or unknown. Missing values stay unknown. Do not infer experience from speed/accuracy, Space thumb from a scan code, or physical geometry from the OS layout. Existing selected category/geometry may be retained with its unverified source label; do not add a device survey.

| Record | Keep or add within the consented predefined task | Acceptance requirement |
| --- | --- | --- |
| Consent and grouping | Applicable consent/protocol/schema versions, session ID, existing lineage and local session sequence where available | No new identity tracking; no public deletion/recovery secrets; linkage mode is explicit |
| Session and capture | Exact build/engine identity, OS, monotonic clock frequency/origin, reliable configuration, focus/pause/task/capture boundaries | Versions and clocks are interpretable; unavailable hardware properties remain unknown |
| Mapping and rules | Exact runtime mapping bytes or immutable retrievable reference, mapping/rule/settings hashes, effective layers and repeat/timeout/reset behavior | Independent replay uses exact inputs, never a display name; unresolved historical imports remain attribution-ineligible |
| Prompt and task | Exact target or cue, task kind, source/near-duplicate family, domain, immutable bank/selection identity, seed, order, local exposure/repeat information | Task assignment is reproducible; local exposure does not claim first-ever exposure or same-person return |
| Physical events | All downs/ups including both Shift keys, Space, correction keys and zero-output prefixes; sequence/time, scan/extended code, position, modifiers, autorepeat and consumed state; hook clock | No intentional omission of operations; manual repetition and autorepeat remain distinguishable |
| Engine and text | Exact edits/selections and source, key links with confidence, composition rule/state transition, transaction identity allowing multiple keys/edits, observed delivery timestamps | Constructive replacements and zero-output actions can be replayed; uncertain links are explicitly uncertain |
| Discontinuities and integrity | Prompt/task/pause/focus/mode/layout changes, reliably observable configuration/capture changes, drop diagnostics and reasons | No interval crosses a discontinuity; unknown state and loss are localized where reliably observable |

Expose device-change information only when reliably available. A low-level key hook does not itself establish a physical-device identity. Unknown required geometry can make a profile unsupported without invalidating unrelated replay or text outcomes.

Derive target alignment, correct/error/repair partitions, eligible timing, observed Shift side, overlaps, repeated-block changes and support tables in the research pipeline. Keep client summaries as independent cross-checks. Timing distributions describe recordings; they do not certify mastery, identify people or measure finger force.

## 3. Gaps, mitigations and residual risks

| Priority and gap | Mitigation | What remains unresolved |
| --- | --- | --- |
| Critical: Shift, Space and composition excluded by current analysis | Build a full action ledger including zero-output prefixes and valid replacements; compare with exact engine replay | More clean-letter intervals alone cannot validate these operations |
| Critical: incomplete engine attribution or imported mapping | Register exact runtime inputs and add rule/state/transaction provenance; retain conservative unknown links | Historical absent bytes or state cannot be guessed; exclude only affected outcomes |
| Critical: capture loss or uncertain modifier state | Verify both Shift sides, holds, fast edits and boundaries; establish an all-keys-released start/resume or reliably observed initial state | Ending held keys are censored; uncertain intervals stay ineligible |
| Critical: unknown person overlap across IDs | Group all known-linked sessions; report lineage/session modes, concentration and hypothetical hidden-dependence sensitivity | Hidden repeat-person leakage cannot be ruled out or statistically repaired from these records alone |
| High: unmeasured experience and technique | Use within-session variation, session/task/source effects, optional lineage effects and common counterbalanced tasks | Session intercepts do not remove key-specific familiarity or layout-selection confounding |
| High: sparse or confounded key/rule coverage | Collect materially different mappings/rules and targeted task blocks from observed deficits; inspect mapping-removal sensitivity | Count floors and geometry assumptions do not establish transfer |
| High: prompt repetition and source leakage | Track local exposure, source works/near-duplicates, seeds and task domain; keep families together in splits | Repeats outside the local store and lifetime practice remain unknown |
| High: incompatible new package fields | Finalize minimal contract; version only necessary wire changes across client, receiver, publisher and research adapters | A new bank/protocol label cannot bypass /1 validation constraints |
| High: optimization exploits model error | Freeze support rules, separate search/development/confirmation, shortlist before later evaluation, inspect unusual action bundles | A lower frozen model score alone does not prove a human speed benefit |
| High: log-time output mistaken for expected time | Training-only mean retransformation and held-out aggregate calibration; retain diagnostic label if it fails | A geometric-scale or median-sum diagnostic is not expected completion time |

Do not normalize every interval by session WPM and interpret the remainder as pure physical cost. Do not use a held-out session's evaluation outcomes to estimate its intercept. Do not select only fast/high-accuracy recordings and claim general-user performance.

## 4. Ordered implementation and acceptance artifacts

The separate [Kala client collection plan](KALA_CLIENT_COLLECTION_PLAN.md) maps client changes to current files, proposed package records, checkpoints, targeted tests and observed Release acceptance.

Each step is future work. An acceptance artifact must contain observed or computed evidence, not a manually promoted status. Synthetic tests support engineering but cannot close observed-device scenarios. Compiler and verifier engineering may proceed in parallel with data preparation; synthetic scores never become empirical rankings.

| Step | Owner and work | Acceptance artifact |
| --- | --- | --- |
| 0. Freeze observable contract | kala-layout coordinates field definitions, unknown/provenance semantics, linkage mode, exclusions, weighting, task assignment and proposed gates with both other repositories | Dated contract and protocol manifest; no questionnaire/recovery requirements; limits and amendment policy recorded |
| 1. Close existing instrumentation pilot | Kala and receiver observe the exact intended Release build and end-to-end route | Scenario evidence, build/configuration and package hashes, replay/summary agreement, consent/retry/withdrawal outcomes; unresolved failures block broader collection |
| 2. Implement necessary collection additions | Kala adds task/cue, engine-transaction and capture-boundary metadata; receiver adds corresponding validation/read/publication compatibility; kala-layout adds historical/new adapters | Compatibility matrix, bounded synthetic golden packages, observed new-format package, original-byte retry and withdrawal proof; /1 queued uploads remain supported |
| 3. Register immutable inputs | kala-layout registers runtime maps, grammar/engine versions, bank/selection identities, Unicode and reviewed source families | Hash-pinned registry, replay evidence and unresolved-import report; no guessing historical metadata |
| 4. Build complete action tables | kala-layout derives full ledger, state before/after, alignment, eligibility and correction partitions | Event accounting and golden traces including Shift/Space/composition; every exclusion has a reason; no intervals bridge excluded actions |
| 5. Collect development recordings | Kala runs frozen waves; receiver retains consented original packages; kala-layout reports observed coverage | Initial 40 eligible sessions over multiple days and at least three material mappings, raw/eligible counts, rule coverage and concentration dashboard; no automatic release at the count |
| 6. Fit and test transfer | kala-layout fits M0/M1/M2/MJ with session/task/source and optional lineage effects; validates grouped/text/mapping/rule/context transfer and mean calibration | Frozen split lists, out-of-fold predictions, parameter diagnostics, weighting/influence/dependence sensitivity and explicit failed gates |
| 7. Freeze evaluator | kala-layout freezes compiler, strategy/profile, reference distribution, support tiers, scorer and independent verifier | Full text round trips, deterministic trace costs, renaming invariance, coefficient/calibration export and independent agreement within protocol tolerance |
| 8. Search Goti/A and Jhor/D separately | kala-layout optimizes only on search/development material with frozen grammar/slot and support constraints | Reproducible manifests, support/uncertainty reports and a small hashed shortlist, or a no-improvement result |
| 9. Confirm once | Kala/receiver collect a later wave; kala-layout evaluates frozen model/shortlist on untouched source families | Untuned report with known development lineages excluded where available, paired conditional intervals and unusual-action checks; no new-person claim |
| 10. Release model-score challenge | kala-layout publishes separate empirical season, exact inputs/model/compiler/scorer and eligible tracks | Reproduction kit, model card with linkage/unknown-experience caveats, supported rankings and provisional/unsupported reasons; bilingual publication requirements apply |

Step 1 checks current instrumentation before expansion; step 2 must repeat affected observed cases for the final changed format/build. Neither an old pilot nor passing serializer tests clears newly changed capture behavior.

For step 2, choose /2 only if the finalized fields/semantics require it. Preserve original compressed bytes for existing queued sessions. Do not deploy new fields before receiver admission, publication/index handling and research reads work. A sidecar alternative needs an explicit hash binding, consent, withdrawal and atomic-publication contract first.

## 5. Collection tasks and observed quality

Retain 260 active seconds, with setup and breaks outside the timer:

| Task | Seconds | Required labeling |
| --- | ---: | --- |
| Warm-up | 20 | Excluded from primary fit |
| Natural passage 1 | 80 | Source family/domain, exact text and local exposure |
| Coverage | 80 | Two targeted Bangla and two physical-action probe blocks, 20 seconds each; cue/task kind and repetition |
| Natural passage 2 | 60 | Different source family/domain where specified |
| Anchor repeat | 20 | Exact repeat relationship; analyzed separately |

Counterbalance common tasks across mappings and available observed device strata; save seeds and assignment versions. Freeze waves before inspecting outcomes. Cover vowels/signs, hasant, conjuncts, nukta sequences, repeated keys, Shift entry/exit/hold/switch, Space, punctuation and digits. Measure what was actually typed correctly, not just the coverage of the planned bank. Fresh prompts on returning lineages reduce known repetition but do not prove a new exposure for that person.

Physical probes remain a separate task domain and enter the official fit only after improving prespecified held-out natural-text transfer. If probes are not yet captured faithfully, postpone them explicitly rather than labeling them natural typing. Do not force a Shift hand or fingering.

The observed pilot should exercise laptop/external and ANSI/ISO where known, bundled/imported mappings, both Shift sides and holds, Space, fast composition and native correction, held keys at start/resume/timeout, focus/pause/mode/layout changes, incomplete output, decline sharing, offline restart, identical/conflicting retries, receiver restart and withdrawal with queued retries/public removal. Observe available configuration/device-change scenarios without inventing reliable automatic device identification. Record observer, date, profile provenance, build/configuration hashes, scenario, package/receipt/evidence hashes and outcome; never publish secrets or private external-app text.

For each admitted package, check immutable-byte identity, clocks, drops, UTF-16 edit replay and NFC output, exact engine replay where attributable, down/up/modifier consistency, summary denominators and current withdrawal membership. Keep valid negative flight and repeated manual presses. Censor incomplete dwell, isolate zero-resolution intervals and avoid log(0). Do not charge dwell and flight again in a down-down interval sum. Exclude unfinished target suffixes from error counting. Package validity and per-outcome eligibility remain separate.

## 6. Grouping, validation and uncertainty

Use existing lineage grouping wherever known; otherwise whole sessions. Keep known-linked sessions together in every split and resampling stage. Define mixed availability explicitly before fitting: do not assign incomplete records to a guessed lineage, and report the session-only portion. No random key-event split.

In lineage mode weight lineages equally and sessions equally within lineage; also report equal-session sensitivity. In session-only mode weight sessions equally. Report how much eligible data the largest groups contribute, earliest-eligible-session-per-lineage sensitivity and leave-one-lineage-out changes. These are recording-group weights and diagnostics, not person counts.

Withhold source/near-duplicate families, complete mappings, semantic rule families and selected physical contexts. For mapping/rule holdouts remove every known lineage using the held-out mapping/rules, including its sessions on other maps. Joint group/text tests train only on rows sharing neither held-out group nor held-out family. Calibrate and tune only inside training. No held-out session intercept is estimated from scored outcomes.

For release uncertainty use at least 1,000 lineage-cluster or session-cluster refits under the declared mode, refitting preprocessing and mean calibration. Candidate/reference use paired draws. Publish intervals as grouping-conditional. Separately report benchmark source-family uncertainty.

Freeze hypothetical hidden-dependence scenarios before confirmation, including the protocol's examples of 2, 4 or 8 apparent groups sharing a latent person effect. Document scenario assignment, variance assumptions and seeds; do not infer actual identities or claim these scenarios are worst-case bounds. If conclusions change materially, withhold a robust-gain claim. No bootstrap or arbitrary error inflation establishes unknown person independence.

## 7. Coverage, release and stopping decisions

Apply protocol sections 11–12 and 14, with their proposed thresholds frozen before confirmation:

- Direct support D: at least 30 eligible occurrences across five known lineages, or five sessions without linkage, plus required date/block/mapping variation. Report concentration. These are recording-support floors, not independent-person evidence.
- Generalized support G: sparse exact context with supported components and successful analogous context/mapping transfer; broader conditional uncertainty.
- Unsupported U: missing required geometry/features, unvalidated operations/rules/strategy or failed transfer. No missing action has zero cost.
- Initial ranked-candidate coverage: at least 95% D, at most 5% G and zero U, with operation-specific and cost-weighted shares. Count floors alone cannot pass transfer.
- Predictive value: at least 5% group-macro log-MAE improvement over the applicable strongest M0 on group and joint group/text tests, positive pooled mapping improvement and no unresolved essential-operation failure.
- Mean calibration: predicted/observed eligible time ratio within 0.90–1.10 overall and in adequately replicated essential strata, with uncertainty. Otherwise retain a correctly named diagnostic and keep an expected-time challenge closed.
- Confirmation: model, shortlist, policies and text hashes frozen before later evaluation. The proposed 2% meaningful gain and 1-percentage-point precision target concern conditional model contrasts. A substantial supported gain follows the protocol's paired confirmation and sensitivity rules, not merely a lower point estimate.

Freeze the observed-recording reference distribution and the same supported strategy/profile weights for all candidates. Keep unknown geometry unsupported when required; do not silently choose ANSI or a favorable fingering. Observed Shift side is measurable, Space thumb is not. Include physical-key-only and supported strategy/profile sensitivity. No new-rule ranking follows merely because its physical pairs are common.

Stop collection for unexplained loss, unreplayable edits, privacy-boundary failure or broken consent/withdrawal/grouping integrity. Stop or narrow a ranking claim for unsupported operations, failed transfer/calibration, concentrated evidence or sensitivity to hidden dependence. Report experimental/provisional outcomes and target missing task data. Forty sessions never overrides those failures.

Publish one of the protocol's evidence-backed scopes: experimental recording-based model, validated within recording scope under stated grouping assumptions, or unsupported/provisional candidate. New-person, experienced-user and causal claims remain unavailable from these anonymous records alone. A defensible no-improvement result still completes the search deliverable.

## 8. Documentation update record

This plan implements the no-questionnaire amendment at the planning level. It links from the protocol and amendment and is included in their artifact manifest. Validation for this update is limited to documentation links, alignment with revision 1.1 and output hashes. No software tests, participant collection, deployment, model fitting or empirical ranking were performed. Earlier test counts remain historical evidence.
