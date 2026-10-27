# Research protocol: a human-data evaluator for Bangla fixed keyboard layouts

Protocol ID: BHE-v1.1-draft-2026-10-27  
Date: 27 October 2026, Asia/Dhaka  
Status: proposed implementation and preregistration specification; no empirical model or ranking released  
Companion: [review of existing work](REVIEW.md)

Revision 1.1 removes questionnaires and verified-person/experience assumptions. See [amendment and mitigation assessment](AMENDMENT_NO_QUESTIONNAIRE.md). All quantitative validation claims now use the recording/linkage scope specified below. The [updated mitigation plan](MITIGATION_PLAN.md) gives the observable-data contract, repository responsibilities and acceptance artifacts.

## 1. Purpose and deliverables

Build an evaluator that learns from people typing Bangla on ordinary physical keyboards and predicts a comparable keying-cost score for a compatible fixed layout, including a layout absent from the training data. Use it to search for better placements within Kala Goti's style A and Kala Jhor's style D, and let other researchers submit layouts or typing styles against a frozen, reproducible challenge.

Required deliverables are:

1. A versioned, audited human typing dataset with mapping and composition registries.
2. A transferable action-cost model, uncertainty estimates, coverage reports and model card.
3. A deterministic layout-to-action compiler and standalone scorer with a reference index.
4. Separate improvement searches for style A and style D.
5. An open-style challenge with explicit eligibility rules and an unsupported/provisional route for genuinely new operations.
6. Reproduction instructions, independent verification, a validation report and a machine-readable release manifest.

Invite volunteers to use a fixed layout they normally use; familiarity is not verified. They do not test every candidate. Candidate names never determine predicted cost. A candidate is evaluated through its physical actions, composition rules, declared strategy and benchmark text.

“Any fixed layout” is an extensible software goal, not a promise of equally reliable prediction everywhere. The system must accept a description or give a precise unsupported reason. Numerical ranking requires validated operation coverage. A new arrangement of familiar operations is a different transfer problem from an entirely new typing rule.

## 2. Scope, population and claims

Primary hardware scope remains ordinary ANSI/ISO row-staggered laptop and external keyboards, initially captured on Windows through Kala. No special keyboard, sensor, camera or questionnaire is required. Where geometry, device category or physical arrangement cannot be established from reliable existing information, record unknown. A scan code or OS layout does not prove the keyboard's physical geometry.

The target dataset is consenting fixed-layout Bangla typing recordings with unknown prior experience and potentially unknown person linkage. Invite people to use a layout they normally use, but do not treat that instruction as verified familiarity. Do not claim an adult-only, experienced, touch-typing, two-handed or representative population without separate evidence. This protocol adds no demographic, skill, experience, handedness, comfort or device questionnaire.

The primary output is a standardized model-predicted keying cost for the observed recording distribution and a declared strategy/profile. It is not mastered-layout speed, pure motor effort, comfort, injury risk or a causal switching benefit. Differences in familiarity and technique remain partly unmeasured.

### 2.1 Identity and linkage

Real-world identity is unnecessary. The existing Kala ResearchStore generates a random ContributorId and stores it locally with its withdrawal secret. Treat this as a **collection-lineage ID**, meaning records sharing the same local research store. It is not proof of a unique person or physical device: people can share a store, one person can use several stores, and reset/reinstall can create a new ID.

Retain already-consented lineage linkage where available; add no account, name, email, recovery questionnaire, hardware fingerprint, IP-based identification or timing-based identity matching. Do not silently expand tracking to make the analysis easier. Do not change the existing consent/withdrawal contract in this documentation task.

Support two analysis modes:

| Mode | Reliable grouping | Interpretation |
| --- | --- | --- |
| Existing lineage available | Keep every session of a lineage together in data splits and resampling | New-lineage prediction; not demonstrated new-person prediction |
| Session-only | Group the entire uninterrupted session; cross-session linkage is unknown | New-recording prediction; hidden repeat-person leakage cannot be ruled out |

Consent and the ability to decline remain necessary; they are distinct from a research questionnaire. If lineage removal is later requested, design session-level withdrawal and queued-upload behavior explicitly before changing collection.

Keep J0/J1 and original Kala layouts frozen. A separately reproducible empirical model-score challenge remains possible, but claims must match the linkage mode. Generalization to new people is unverified unless independently supported by study design; fresh IDs or later dates alone cannot establish it.

## 3. Questions and preregistered decisions

Primary questions:

- Do shared physical-action features improve prediction over group-balanced baselines on held-out recording groups and texts?
- Does that improvement survive withholding complete mappings and composition-rule families?
- Can complete action traces be scored without excluding Shift, spaces or valid Bangla composition?
- Do candidate gains survive model uncertainty, device/strategy sensitivity and later-wave confirmation under the declared grouping assumptions?
- Can an independent researcher reproduce the score and submit a valid improvement?

Before main collection, freeze a protocol manifest containing: population definition, hardware profiles, task schedule, bank versions, source families, sampling/randomization, exclusion rules, score equation, reference layout, model candidates, split algorithm/seeds, precision target, support tiers, stopping rules and challenge eligibility.

Defaults in this document are recommendations to make implementation concrete. They are not existing policy settings or claims established by the cited literature. Pilot-only revisions are allowed before confirmation data are examined; date and explain each amendment. Never relax a gate because a preferred layout fails it.

## 4. Collection design without questionnaires

Use three stages, with no required identity, experience or strategy questions.

| Stage | Collection target | What it establishes |
| --- | --- | --- |
| Instrumentation pilot | Observe coverage of laptop/external, ANSI/ISO where known, bundled/imported mappings, both Shift keys and composition; 5–10 consenting testers is a practical pilot budget, not a population estimate | Capture and end-to-end delivery work |
| Development recordings | Initial engineering milestone: 40 eligible sessions across multiple days and at least three materially different mappings; encourage repeat sessions without requiring them | Enough data to exercise fitting and reveal coverage gaps; not evidence of 20 people |
| Later confirmation wave | Freeze model and texts, then collect a later wave with untouched source families and, where available, lineages absent from development | Temporal/new-lineage recording validation; no automatic new-person claim |

The earlier 20-person/two-session rule, 60–90-person budget and verified experience criteria are withdrawn for this collection mode. Counts of sessions and local IDs cannot replace independent people in a power calculation.

Use common, counterbalanced prompt families across mappings and observed device strata. Preserve randomization seeds. Target missing action/rule coverage, not preferred rankings. Do not require volunteers to learn Goti, Jhor or every candidate. Multiple substantially different mappings and composition families are still necessary to assess transfer. Aliases of the same map/rules do not count as diversity.

Record session and lineage counts separately, concentration by lineage, dates/waves, mappings and rules. Report the share of all events coming from the largest lineages. Where linkage is known, cap influence by weighting lineages equally and sessions equally within lineage; report an equal-session sensitivity analysis. Session-only mode cannot prevent the same prolific person from dominating through multiple sessions.

Repeat visits are optional. If the same lineage returns, offer fresh prompts and preserve its local exposure history. A repeat lineage is not necessarily the same person; absence from local history is not proof of first exposure elsewhere.

After pilot/development data, simulate precision conditional on the actual grouping unit. Include assumptions about hidden repeated people and dependence. The proposed 2% minimum useful score improvement and 1-percentage-point interval half-width remain model-development targets, not guaranteed population power. Do not claim a statistically sufficient number of independent typists when it is unknown. Persistent sensitivity or sparse coverage means collecting more varied recordings or narrowing the release claim.

## 5. Session tasks on general keyboards

Retain the short 260-active-second format as the core, with breaks and setup outside the timer. An optional repeat takes total active typing to about nine minutes; no mandatory paired-person design is assumed. The existing stage names and timing can remain, but added task metadata and changed behavior require a new validated collection version.

| Stage | Seconds | Purpose |
| --- | ---: | --- |
| Warm-up | 20 | Familiarize the participant with the task; exclude from primary fit |
| Natural passage 1 | 80 | Connected Bangla text on the selected fixed layout |
| Coverage | 80 | Two 20-second targeted Bangla blocks and two 20-second physical-action probe blocks |
| Natural passage 2 | 60 | Different text/source family; observe later-session behavior |
| Anchor repeat | 20 | Repeat a recorded earlier passage segment for stability; analyze separately |

Counterbalance which domain appears first and the order of the four coverage blocks. Preserve passage order within continuous text. Randomize with saved seeds; balance common anchor content across mappings and device groups. If a local lineage returns, offer fresh natural passages plus a documented anchor repeat; this does not establish the same person returned. Known repeated exposure stays in one text family.

Targeted Bangla blocks deliberately cover independent/dependent vowels, hasant, conjuncts, nukta sequences, repeated keys, Shift entry/exit/hold/switch, spaces, punctuation and digits. They use meaningful short text where possible. A coverage optimizer chooses blocks from missing feature categories, not from which layout currently looks better. Freeze each collection wave before inspecting its outcomes.

Physical-action probes display short position cues on an ordinary keyboard diagram, using the participant's normal hands and comfortable pace. Sample balanced pairs and short three/four-key sequences, including Shift and Space. They help separate physical placement from language frequency and fill rare contexts. Give brief practice; record cue, repetition index, correctness and task kind. Do not assume repeated tapping predicts fluent Bangla. Fit a separate task-domain term and require transfer to natural typing before these observations influence the official score. If the probe UI cannot yet be captured correctly, postpone that module rather than disguising it as ordinary text entry.

Instructions: type accurately at a comfortable usual pace; correct errors as normally done; pause when interrupted; never force an unfamiliar fingering or Shift hand. Preserve incomplete text at timeout. Do not count an unfinished suffix as an error. Optional extra sessions can target coverage or longer-session fatigue, but are separately labeled and do not silently change the core score.

## 6. Data contract: observable records, no questionnaire

Keep immutable original packages and versioned derived tables. Every metadata value needs provenance: observed by app, derived from events, existing unverified selection, assumed, or unknown. Do not fill missing experience/device information with inferred certainty.

| Level | Collect or retain automatically within the consented task | Do not claim |
| --- | --- | --- |
| Consent/linkage | Consent and schema version; session ID; existing local lineage ID and local session sequence if present | Real identity, unique person, same person across sessions |
| Session/capture | Build/OS/engine versions, monotonic clock, focus/pause/task boundaries, capture health, reliable configuration and change events | Physical hardware properties the app cannot reliably observe |
| Device/geometry | Existing selected category/geometry with source label; reliable app-visible geometry/configuration; otherwise unknown | Verified keyboard dimensions, switch type, connection type or same physical device from a local ID |
| Mapping/rules | Exact runtime mapping bytes or immutable reference, mapping/rule hashes, effective composition settings, repeat/reset behavior | Equivalence inferred from a layout name |
| Prompt/task | Exact target/cue, task kind, source family/domain, bank/selection version, seed, order, local exposure count and repeats | Lifetime practice history or first-ever exposure |
| Physical events | All down/up events including Shift, Space, corrections and zero-output prefixes; time, order, position, scan/extended codes, modifiers, repeats and consumed state | Actual finger, pressure, gaze, handedness or intent |
| Text/engine events | Exact edits/selections, source, key links, grammar state/rule and transaction IDs, reliably observed delivery timestamps | That every replacement is an error or every insertion is correct |
| Outcomes, derived | Correctness/alignment, correction/repair, keying time, pause patterns, observed Shift-side behavior and repeated-block changes | Experience in years, mastery, general skill, fatigue diagnosis or comfort |

Remove planned experience, usage-frequency, finger-count, handedness, age, discomfort and keyboard-description questions. Existing user-entered fields can remain historical evidence labeled unverified; do not add new questionnaires or use such fields as ground truth. No account, identity recovery task or cross-device matching is required.

Observed accuracy, timing distributions, rollover and within-session stability help describe the **recording**, not certify the user as experienced. Do not select only fast/high-accuracy sessions and then claim general user performance. Exclusions concern capture validity, task scope and explicit target alignment. Keep observable difficulty and errors in separate outcomes.

Consent is still explicit, including any publication of original predefined-task text/events and Git-history withdrawal limitations. No background or everyday application typing is collected. Keep withdrawal secrets out of public packages. Pseudonymous timing records are not guaranteed anonymous.

Removing questionnaires reduces fields but does not eliminate the remaining format changes. Explicit engine transactions, new task/probe fields and capture boundaries still require a compatible client/receiver/research contract. The current /1 reader rejects unknown fields and enforces stage/duration constraints; a new protocol label does not change that. Choose /2 only when necessary for the finalized observable-data contract, retain /1 reads and queued uploads, and test publication/withdrawal compatibility. Do not change transport merely to rename ContributorId in analysis; document its lineage semantics.

## 7. Measurement and quality gate

Before broader collection, complete the existing observed pilot matrix using the exact intended Release build and receiver: physical laptop/external keys; left/right/held Shift; fast composition and native corrections; focus and pause; timeouts; stop; decline sharing; offline restart; identical/conflicting retry; receiver restart; withdrawal while retries are queued; and public package publication/removal.

Record observer, date, build/configuration hashes, keyboard/profile, scenario, package/receipt/evidence hashes and outcome. Evidence must be observed; synthetic tests cannot mark these scenarios complete. Never publish deletion secrets.

Required checks for every package:

- Original compressed SHA-256, session identity, admitted schema, clock monotonicity and drop/capture diagnostics.
- UTF-16 edit replay and independent final NFC comparison; version-pinned grapheme verification for display/error outcomes.
- Exact mapping and engine replay for attributed operations; no guessing from a layout display name.
- Valid down/up matching, modifier-state transitions, boundaries and censored held keys.
- Independent reproduction of declared summary scores and their denominators.
- Current consent/dataset membership and withdrawal status.

Separate package invalidity from per-outcome eligibility. A missing keyup may censor dwell without losing valid down-down timing. An ambiguous edit can exclude symbol attribution without losing a final-text outcome. Never rewrite raw packages to make them pass.

For continuity with the current policy, flag gaps or empty measured periods over 30 seconds. Preserve original active and wall clocks. Preregister the primary eligible-session policy and a sensitivity analysis retaining affected sessions with interrupted segments excluded. Do not delete slow intervals merely because the model dislikes them; reading/planning latency remains part of recorded behavior. Any threshold change creates a protocol amendment.

## 8. Canonical actions, alignment and timing ledger

Create collection-lineage (where available), session, observed-device/configuration, prompt, key-event, edit, engine-state, action, interval, correction and quality tables. Unknown metadata remain unknown. Every derived row links to immutable package hash, source event IDs and transformation version.

An action is a physical keydown plus its modifier and engine context. A valid action may emit zero, one or several NFC code points, or replace earlier output as part of composition. Do not use “one insertion equals one key” or “replacement equals error.”

The timing ledger contains every consecutive non-autorepeat physical downstroke within an uninterrupted task segment, including Shift and Space. Partition it into valid keying, correction/recovery, probe, interruption and unknown strata. Never remove an excluded action and connect its neighbors. Analyze manual repeated presses separately from operating-system autorepeat.

For adjacent downstrokes a and b:

    DDI(a,b) = down_time(b) − down_time(a)
    dwell(a) = up_time(a) − down_time(a)
    flight(a,b) = down_time(b) − up_time(a)

Negative flight is valid overlap. Dwell and flight are diagnostics, not extra time added to DDI. Retain zero-resolution intervals as a timing-quality stratum; do not take log(0) or invent positive values. Hardware/capture artifacts must be distinguished from human behavior.

Use sequence IDs to break equal-timestamp ties. Define state-before and state-after for every key transition, and use the identical convention in collection features and candidate compilation. Attach a modifier or zero-output prefix to its verified grammar episode rather than demanding its own text insertion.

Track Shift down/up, held side, switching side, same/opposite-hand use under the declared finger assumption, and run length. Keyups update state but do not independently add elapsed cost to a DDI sum. Release waits, if real, are reflected in subsequent intervals. First-response latency and final-release time are separate endpoint quantities.

Replay the exact engine to label each composition operation and target alignment. A single-code-point insertion with an exact key link can still be wrong. Derive accepted correct-path intervals only where alignment and grammar provenance are unambiguous. A correct hasant/vowel replacement is eligible keying. Corrected mistakes, repairs and ambiguous alignments remain visible. Do not discard all error-containing sessions or treat final accuracy as proof of every action's correctness.

## 9. Text design and benchmark separation

Human collection texts and layout-scoring texts serve different purposes. Build a licensed, native-reviewed prompt bank with modern prose, news/expository writing, administrative text, literary text and everyday-message-like authored passages. Include realistic spaces, digits and punctuation. Do not rely exclusively on poetry or repeated short anchors.

Proposed benchmark domains: news/expository, educational/encyclopedic, administrative, literary and everyday authored prose, each 20%. These weights are an explicit benchmark choice, not an estimate of all Bangla usage. Report domain-specific scores. If a domain cannot be sourced and reviewed, release a narrower named benchmark with new weights before scoring; do not silently replace it.

Use at least 20 independent source families per domain as an initial construction target, then check score stability under family resampling. Keep exact source/licence, normalization, cleaning and deduplication versions. Search corpora remain outside Git; original study packages follow the existing narrow exception.

Define three separate text sets by source work and near-duplicate family:

1. Search text: visible to optimizers.
2. Development text: used for model/candidate choices.
3. Confirmation text: locked before those choices; evaluated once for the frozen shortlist.

Old published held-out texts are useful development references, but are no longer novel confirmation material for a researcher who has repeatedly inspected their rankings.

Freeze the exact accepted text and output repertoire for a season. Normalize to NFC; pin Unicode behavior. Never delete a candidate's unreachable symbols from its denominator. All candidates in one track receive identical text. Publish filtering losses relative to the broader source. Joiners, rare punctuation or mixed-script characters outside the first release's repertoire belong to a named extended benchmark, not an undisclosed escape route.

For the primary time score, count NFC Unicode code points, including benchmark spaces and punctuation; exclude only predeclared structural document delimiters consistently for everyone. Report grapheme-normalized results separately using a pinned segmenter. Neither unit is a physical keystroke or a Bangla word.

## 10. Model specification with unknown experience and person linkage

### 10.1 Targets and adjustment

Primary learning target remains log down-down interval for verified correct keying, including Shift, Space and composition. Preserve errors/repairs separately and distinguish natural typing from probes.

Compare M0 (group-balanced constant and operation-stratified baselines), M1 (regularized physical/action model with session/task/source effects), M2 (supported key/pair and selected three-action effects), and MJ (separate frozen-effort-assisted comparator). M1/M2 are learned independently of fixed J0/J1 weights.

    log DDI = intercept
              + physical/action-context terms
              + observed task and language-context terms
              + session effect
              + optional collection-lineage effect
              + prompt/source-family effect
              + residual.

A lineage effect is a recording-group adjustment, not a participant effect. Session effects absorb some baseline speed variation, but cannot fully remove unmeasured familiarity, technique or layout preference. Key-specific familiarity may remain even after a session intercept. Do not replace questionnaire answers with guessed experience labels.

Use regularized group intercepts and identifiable centered contrasts; a standard-library penalized least-squares implementation is feasible. Equal group weights and intercepts address different problems. Check numerical conditioning, shrinkage and synthetic parameter recovery. No new dependency without repository approval.

Learn costs primarily from variation within sessions and shared action classes across sessions/mappings. Do not simply divide every timing by that session's overall WPM: WPM itself depends on the layout and text, so this can remove real differences or introduce bias. Balanced common tasks and probes help but do not prove causal identification.

### 10.2 Features available for an unseen layout

Use physical position/geometry, key identity, key pair, repetition, Shift-side state and changes, Space transitions, composition operation/position/length, and selected three-action contexts. Finger/hand relationships based on a grid are assumed features; include a physical-key-only sensitivity model. Unknown geometry must not silently become ANSI or the most favorable profile.

Language/output context is a nuisance variable: common symbols may be fast because they are familiar. Multiple mappings and physical probes help separate symbol from key effects. Inspect collinearity, disconnected coverage and mapping-removal sensitivity. A single map cannot identify arbitrary independent symbol and key costs.

Center session/lineage nuisance terms for candidate scoring, with a fixed reference distribution for everyone. Declare retained language terms and assign word-level costs only at common output boundaries, not at every internal composition key. Report matched-text-context sensitivity; do not choose the specification that favors Kala.

Observed dwell, flight, rollover rate, total WPM, errors or estimated session fluency may be diagnostic outcomes. They must not become required inputs to a scorer for a layout nobody has typed. If an auxiliary calibrated-session analysis uses warm-up data, freeze that calibration before its evaluation block, use the same procedure in validation, and label it separately from uncalibrated transfer. Never estimate a held-out session intercept from its scored outcomes.

### 10.3 Time scale and reference population

Exponentiated predicted log time is a geometric-scale prediction, not automatically an arithmetic mean or median. Keep that diagnostic separate.

For a mean-time score, use training-only grouped out-of-fold retransformation, for example:

    predicted_mean_ms(x) = 1000 × exp(predicted_log_seconds(x)) × smearing_factor(x)

Estimate factors with the same lineage/session weights as the reference distribution, with operation-specific factors only when supported. Out-of-group residuals include unpredicted group variation; do not add that variation again. Check aggregate predicted versus observed eligible keying time. Failed mean calibration prevents calling the diagnostic expected time.

The reference population is the frozen observed-recording distribution under a declared weighting and task/profile—not verified experienced typists or all Bangla users. Use natural transcription after warm-up, a documented local-exposure condition, and fixed nuisance settings. Unknown familiarity stays unknown. Preserve the same reference weights and calibration for every candidate.

Publish only supported geometry/device profiles and their provenance. Unknown-device data can support an explicitly unspecified-device profile only if its feature model does not require missing geometry. Do not optimize assumptions separately for each candidate.

Observe actual left/right Shift key use and holds directly. Use a validated, fixed strategy for candidate compilation; no questionnaire is needed for those event-level observations. Space's physical event is observed, but its thumb/finger is not. Fingering remains a sensitivity assumption. A strategy popular in the observed sample is not a universal optimal strategy.

### 10.4 Errors and behavioral diagnostics

Fit correction, repair-duration and remaining-error targets separately. Native Backspace is not a universal symbol error label; composition replacement is not repair. Show accuracy and exclusion shares alongside timing. A timing-only model cannot establish comfort or a total performance benefit.

Derived metrics such as correct-path timing spread, repeated-anchor change and observed Shift consistency describe task behavior. Use them to inspect heterogeneity and failures, not identify people or certify mastery. Do not infer people from timing similarity, cluster recordings into “users,” or use inferred identity to claim person-level validation.

### 10.5 Reproducible fitting recipe

1. Fix seed 20261027 for group/family assignment and 20261028 for resampling. Group by lineage where present, otherwise whole session. Keep known-linked sessions together. Publish the linkage mode.
2. Use five outer group folds and five family folds where counts permit. Inner grouped validation selects structural and group-effect ridge penalties from {0.1, 1, 10, 100}. Fit scales/contrasts only on training data; do not penalize the global intercept.
3. In lineage mode, weight lineages equally in total and sessions equally within lineage. In session-only mode weight sessions equally. Publish both weighting sensitivities where possible. Do not call these person weights.
4. Fit natural-only M1 first. Include probe data only if separately modeled task-domain effects improve held-out natural-text prediction. M2 adds shrunk pair terms and prespecified same-key runs, same-finger returns under an assumption, hand-pattern and Shift-run context.
5. Prefer M2 only for at least 2% inner group-macro log-MAE improvement with no unresolved mapping-transfer failure. Keep MJ as a comparator. No confirmation-driven feature selection.
6. Calibrate mean time from inner out-of-fold residuals, then refit on outer training only. Confirmation remains untouched until model, candidate shortlist and text hashes are fixed.
7. Export coefficients, category levels, scales, centering, mean calibration, group semantics, reference weights and numerical tolerances. Independent scoring must agree to relative tolerance 1e-9 on frozen traces.

No fitted model, bootstrap or large session count can make unknown independent-person counts known.

## 11. Validation and uncertainty under imperfect linkage

Never random-split key events. Use the strongest known grouping and report what it establishes.

| Test | Required split | Valid interpretation |
| --- | --- | --- |
| New-lineage | All known sessions of a local lineage held out together | New local collection group; person overlap may remain across lineages |
| New-session, when lineage absent | Whole sessions held out | New recording; same people may appear in both sets |
| New-text | Source works/near-duplicate families held out together | Transfer beyond recorded source families |
| Joint group/text | Hold out both groups and families; train only on rows in neither group; test their intersection | Combined recording/text transfer under the stated grouping assumption |
| New-mapping | Withhold complete mapping; also withhold every known lineage appearing on that mapping, including its other mappings | Mapping transfer with known cross-group leakage blocked |
| New-rule family | Same rule for semantic grammar families and equivalent aliases | Transfer to other composition behavior |
| Context holdout | Withhold chosen pair/three-action contexts while retaining broader structural support | Validate generalized predictions |
| Later-wave confirmation | Freeze model/texts before a later collection wave; exclude known development lineages where possible | Temporal replication, not guaranteed independent people |

For joint folds, rows sharing either held-out group or held-out text family cannot be training rows. Report small/empty cells. Unknown person overlap in any split remains unknown, even when dates and ID hashes differ.

Measure group-macro log MAE, millisecond MAE, bias, aggregate time calibration and paired improvement over M0/MJ. Break down by operation, mapping, rule, task, wave and available device/geometry. Unknown experience is not a validated skill stratum. Report within-session action contrasts separately from absolute predictions; they help inspect physical effects but do not establish layout causality.

Proposed recording-scope gates:

- Integrity: observed capture/replay/consent/transport pilot passes; no unresolved integrity failures in admitted data.
- Coverage: multiple sessions, dates, mappings and rules supply the required operations. Forty sessions is an engineering milestone, not a power threshold.
- Predictive value: at least 5% improvement in group-macro log MAE over the strongest applicable M0 on group and joint group/text tests; pooled mapping tests improve with no unresolved essential-operation failure.
- Mean calibration: predicted/observed eligible keying-time ratio within 0.90–1.10 overall and in adequately replicated essential strata. Report uncertainty and sparse failures.
- Candidate validity: complete round trip and zero unsupported essential-operation share, with coverage tier semantics below.
- Robustness: gains survive weighting, group influence, plausible hidden-dependence assumptions and supported device/strategy/domain sensitivity.
- Confirmation: frozen model evaluated on later recordings and untouched text without tuning.

Resample complete lineages where available, otherwise sessions, with at least 1,000 refits for a release analysis. Refit preprocessing and calibration, preserve grouping multiplicity, and use paired draws for candidate/reference. Name intervals “lineage-cluster conditional” or “session-cluster conditional,” never participant-population confidence intervals.

Run concentration checks, leave-one-lineage-out analyses, an earliest-eligible-session-per-lineage analysis, and frozen hidden-dependence simulations. For example, evaluate scenarios in which 2, 4 or 8 apparent lineages/sessions share a latent person effect. These are hypothetical sensitivity scenarios, not inferred identities or guaranteed worst-case bounds. If conclusions depend on the independence assumption, say so and withhold a robust improvement claim. Completely unobserved dependence cannot be repaired by bootstrap or by inflating errors with an arbitrary constant.

The earlier 1-percentage-point precision target and 2% meaningful gain threshold can describe conditional model contrasts only. Meeting them does not verify independent people or general population precision. A separate observed design could later support person independence without names or a questionnaire; it is not a hidden prerequisite for exploratory scoring.

Release labels:

- Experimental recording-based model: supports development and a clearly labeled model-score challenge.
- Validated within recording scope: required transfer/calibration gates pass under explicitly stated grouping assumptions.
- New-person or experienced-user validation: unavailable from this collection alone; requires separate evidence.

Do not reopen new-person claims simply because many local IDs or repeated sessions accumulated.

## 12. Coverage and the right to abstain

Report raw and eligible counts by transition, operation, mapping, rule, source family, session, lineage when available, and collection wave. Count observed correct action contexts, not planned prompts.

| Tier | Evidence | Treatment |
| --- | --- | --- |
| D: directly observed recording support | At least 30 eligible occurrences across at least five known lineages, or five sessions if linkage is unavailable, with multiple dates/blocks and mapping variation where identification requires it | Recording support only; report linkage mode and concentration |
| G: validated structural generalization | Sparse/unseen exact context, supported components and operation class, and successful analogous held-out context/mapping tests | Broader conditional uncertainty |
| U: unsupported | Unknown required geometry, new unvalidated rule/operation/strategy, absent feature range or failed transfer | No complete official score |

These replace the draft's “five people” requirement; they do not claim equivalent statistical strength. Repeated uploads, duplicate packages and multiple prompts in one recording do not create more groups. Sparse operation classes remain unsupported regardless of total event count.

For a recording-scope model-score challenge, retain proposed thresholds of at least 95% D, at most 5% G and zero U, with operation-specific and cost-weighted shares. Passing these numerical floors alone does not establish transfer: section 11 gates and sensitivity also apply. Publish the linkage caveat on every score/model card.

A new arrangement of known operations can receive a provisional prediction. A new composition rule may be cognitively unfamiliar despite familiar physical pairs; keep it provisional until applicable rule-transfer evidence exists. Collect targeted task data, not questionnaires, to investigate the gap.

No missing or unsupported action gets zero cost. Unknown experience does not invalidate all data, but it limits the population and learning claims. Freeze any later changes to support thresholds as a new version, applied equally to all candidates.

## 13. Candidate compiler and score

A candidate submission must specify exact physical mapping, geometry/layers, deterministic composition state machine, Unicode output and normalization, repeated-key rules, boundary/reset behavior, supported inventory and typing strategy. Store hashes and version identities. A name is optional metadata.

Support the existing A/D grammars first, then exact registered imported fixed grammars. The eventual adapter interface should accept a declarative, bounded deterministic transducer. It must not access target text, corpus IDs, filenames, the clock, network or scorer internals. Arbitrary executable submission code is not part of the challenge.

Compile each benchmark paragraph to an achievable key sequence; simulate keydown/keyup state and composition; verify final output equals the complete NFC target. A zero-output prefix key still costs time. Check legal modifier release and held-key behavior, repeated keys, vowels, hasant/conjuncts, spaces and punctuation. Test standalone words and their continuous-text contexts.

When alternatives exist, use the preregistered strategy: by default, fewest nonmodifier presses with fixed deterministic tie-breaking, then the common validated Shift policy. This avoids giving each candidate an unconstrained model-oracle strategy. If minimum predicted-cost encoding is studied, label it an ideal-strategy track and validate its realizability separately.

For candidate L, fixed profile q, domain d and benchmark paragraphs t:

    C_d(L,q) = 1000 × [sum_t sum_i predicted_mean_DDI_ms(L,q,t,i)]
                      / [sum_t NFC_codepoints(t)]

    C(L) = sum_q profile_weight(q) × sum_d domain_weight(d) × C_d(L,q)

    BHE_index(L) = 100 × C(L) / C(reference)

Lower is better. Set the exact frozen UniJoy mapping/grammar/profile as the proposed reference = 100, provided it passes the same coverage and round-trip gates. Do not substitute an unresolved UniBijoy import. If a different reference is necessary, choose it before fitting comparisons and identify its hash.

The interval sum covers consecutive physical downs within each fixed continuous paragraph, including Shift/Space/composition. It excludes prompt-to-first-down and final-release latency. Paragraph boundaries are fixed for every layout and cannot be chosen by submissions. Require substantial continuous paragraphs (target 200–500 NFC code points), report omitted endpoint counts, and reject traces without at least two downs. The score is predicted eligible keying time, not total task completion. A later onset-inclusive score is a new target, not a silent adjustment.

Illustration only: if the reference predicts 200,000 ms per 1,000 code points and a candidate predicts 190,000, its index is 95 and its predicted cost reduction is 5%. This does not establish 5% faster real-world typing.

Report the absolute score, index, paired difference/ratio intervals, raw downstrokes per output unit, domain/profile values, round-trip coverage, D/G/U shares, assumptions and excluded operation counts. Include key/transition/composition contributions with an accounting decomposition that sums to the total. Counterfactual swap attribution is a model prediction, not a causal explanation of finger physiology. No single mixed “ergonomics” number combines time, accuracy and subjective comfort.

## 14. Search for Goti and Jhor improvements

Run two initial tracks:

- A: keep Goti's hasant-plus-vowel-sign grammar, including its actual contextual exceptions; search legal placements.
- D: keep Jhor's context-sensitive vowels and repeated-key rules; search legal placements.

Keep the published inventory and fixed digits/punctuation constraints for direct within-style comparisons. Offer separate search budgets for unrestricted legal placement and limited-change variants (for example, at most four moved symbols). Count changes explicitly; a swap moves two symbols. Keep whole symbol outputs intact under NFC.

Search only on search text and frozen training/development model artifacts. Suggested progression: exhaustive single swaps around each reference, then reproducible multi-start annealing/iterated local search. Record seeds, evaluations, constraints, time and best-so-far archives. A pair-cost lookup is valid only if it exactly represents the chosen model; three-action, held-Shift and grammar effects require corresponding state-aware updates and verification.

Reject candidates with U coverage. Use a preregistered conservative objective such as the upper 95% model-uncertainty estimate of cost, with fixed support constraints; keep nominal score visible. Do not hide arbitrary unsupported penalties inside the official score. Compare plausible models and strategy/device profiles.

Choose a small fixed shortlist on development data, freeze its hashes, then evaluate confirmation text once. Searching many layouts can exploit systematic model bias; bootstrap agreement used during search is not independent evidence. Collect a later targeted wave for the shortlist's unusual action bundles, using unseen known lineages where possible. A separate observed learning-aware comparison may strengthen claims, but is not assumed from anonymous recordings. If the scientific claim is only model score, label it accordingly.

A substantial supported model-score improvement requires a paired, explicitly grouping-conditional confirmation interval whose lower bound for percentage cost reduction exceeds the preregistered 2% threshold, with section 11 sensitivity checks. It is not a population or causal confidence claim. Smaller positive changes can be reported as numerical improvements or uncertain predictions; do not inflate them. Apply simultaneous intervals or a prespecified multiple-comparison rule to a multi-candidate shortlist.

Deliver best found mappings, exact score verification, changed positions, drivers of predicted gains, coverage, uncertainty, sensitivity and a no-improvement conclusion when appropriate. Do not automatically install or publish a replacement Kala layout.

## 15. Public challenge

Publish the empirical model, feature definitions, compiler, reference mappings, scorer, benchmark counts/text retrieval instructions, hashes, model card and golden vectors. Preserve standard-library runtime scoring. The empirical challenge has a distinct season/version from the J1 challenge. Its header and every model card must state recording-scope validation, linkage mode and unknown experience; no person-generalization claim follows from the leaderboard.

Three tracks:

| Track | Allowed changes | Success |
| --- | --- | --- |
| Goti/A placement | Placements within the frozen A grammar and slot constraints | Lower reproducible BHE score under that track |
| Jhor/D placement | Placements within the frozen D grammar and slot constraints | Lower reproducible BHE score under that track |
| Open fixed style | New deterministic grammar and/or placement on the declared general keyboard/layers | Valid full output, admissible rule system and the same support/transfer requirements |

For the first open-style season allow base and Shift, ordinary sequential keystrokes and documented finite symbol/conjunct composition. No predictions, autocorrection, dictionary word/phrase macros, paste, corpus-specific shortcuts, timing-dependent tricks or extra hardware. Define a finite allowed output-unit inventory before submissions; new conjunct inventory choices need a declared separate track/version. New AltGr layers, chords or additional state classes can be future tracks once measured. These restrictions define comparable research problems; they do not prohibit investigating excluded techniques separately.

A genuinely new grammar can enter a public experimental gallery with its adapter checks, provisional score if meaningful, and missing evidence. It becomes ranked only after its operation/rule transfer is supported under a model version applied equally to every candidate. Beating a score must not mean exploiting an unmeasured cognitive operation.

Distinguish “lower numerical score on the frozen model” from “supported improvement” and “human-confirmed benefit.” Show ties/uncertain differences. Reject invalid mappings and unreachable text without silently altering the benchmark.

A public benchmark is an optimization target. Do not describe repeated public leaderboard improvements as unseen-text validation. Optionally run scheduled confirmation rounds on concealed source families with a small frozen submission limit; publish those texts/counts after the round and retire their holdout status. A new model/data/grammar policy creates a new season and rescoring of all references/submissions. Withdrawn data trigger a documented model-version review; historical scores remain labeled historical.

## 16. Exact implementation path and acceptance artifacts

The following are future work instructions, not a claim that commands already implement this protocol.

| Step | Responsible repository and work | Acceptance artifact; do not advance without it |
| --- | --- | --- |
| 0. Freeze protocol | kala-layout: finalize this draft, parameters and reference profile; preserve historical results | Signed/date-stamped protocol manifest and amendment policy |
| 1. Close instrumentation pilot | Kala plus receiver: observe the existing scenario matrix on intended build | Observed pilot evidence, exact package hashes, independent replay/score agreement |
| 2. Version collection | Kala: observable metadata, task-kind/cues, engine attribution without questionnaires; receiver: necessary schema/read/validation/publication compatibility; research: historical/new adapters | Schema contract, compatibility matrix, synthetic golden packages, observed new-format package, retry/withdrawal proof |
| 3. Register inputs | kala-layout: exact mappings, rule engines, banks, Unicode, source-family and near-duplicate review | Immutable registry with evidence for every validated status; missing historical imports quarantined |
| 4. Build complete action tables | kala-layout: full ledger, target alignment, Shift/Space/composition, correct/error/repair partitions | Event-conservation/replay checks; no bridged exclusions; coverage report and golden traces |
| 5. Collect development | Existing usage-metric route with frozen waves and consent | Recording milestone and observed-coverage/concentration dashboard; grouping-conditional precision/dependence simulation, no independent-person claim |
| 6. Fit and validate | kala-layout: M0/M1/M2/MJ, nuisance adjustment, mean calibration, grouped/transfer tests | Models, split lists, out-of-fold predictions, parameter/identifiability diagnostics, model card; explicit failed gates |
| 7. Freeze evaluator | kala-layout: candidate compiler, profiles, support tiers, scorer and independent verifier | Exact round trips, trace costs, identical-name/renaming tests, independent recomputation and deterministic reference scores |
| 8. Search A and D | kala-layout: constrained reproducible optimization on search/development only | Frozen shortlist, search manifests, verified improvements or no-improvement report |
| 9. Confirm | Later recordings and untouched texts; exclude known development lineages where possible; targeted gaps and optional separate observed checks | Untuned confirmation report, paired uncertainty and claim-tier decision |
| 10. Release challenge | Separate empirical season; apply repository publication rules | Reproducible scorer/model/data versions, track rules, leaderboard and bilingual publication materials |

Dependency note: compiler engineering and golden tests can proceed with synthetic models before cohort collection, but synthetic scores must never appear as empirical reference rankings. Do not wait for recruitment to discover that the evaluator cannot represent Space or composition.

Existing commands available today include audit-usage-data, register-usage-data, build-usage-features, verify-usage-run, fit-usage-model and evaluate-usage-layouts. These are foundations, not an implementation of the new gates above. Keep audit-only and insufficient_data behavior. Use new output folders for reruns; never run default writers over historical evidence merely to inspect it.

Proposed future result statuses:

    invalid_data
    insufficient_data
    experimental_fit
    transfer_validation_failed
    unsupported_candidate
    provisional_prediction
    validated_within_recording_scope

Define exit-code behavior and machine-readable reasons consistently when implementing them. A status string is backed by evidence, never manually promoted to unlock fitting.

Every future phase writes a new results directory with a readable report, machine-readable result, run manifest, input/output hashes, source revision plus dirty-file hashes, policy, seeds, versions, split identities and withdrawal snapshot. Route writers through bangla_dh.paths.output_path. Keep large search texts ignored. A future website document needs its Bangla pair and native-speaker review; this English research draft is deliberately outside the website source.

## 17. Completion and stopping conditions

The project is complete only when a researcher can supply an admissible unseen mapping, obtain a reproducible supported score with uncertainty, search within A and D, and submit a valid open-style challenge under published rules.

It is not complete when only a timing regression fits or all software tests pass. Conversely, no improved Kala layout is guaranteed: a defensible no-improvement result still completes the search deliverable.

Stop a collection wave for unexplained capture loss, privacy-boundary failure, unreplayable edits or broken identity/withdrawal behavior. Stop a ranking claim when operation coverage, mapping transfer or precision fails. Retain an experimental release and target the missing data. Do not silently broaden recording-scope predictions into experienced-user, new-person, comfort or universal speed claims.

## 18. Research basis and interpretation

These primary sources motivate measurement choices; they do not validate Bangla transfer, this sample size or the proposed numerical gates.

- Dhakal et al., CHI 2018, [Observations on Typing from 136 Million Keystrokes](https://userinterfaces.aalto.fi/136Mkeystrokes/). Large natural typing data show variation in typing behavior and common overlapping keypresses. This supports retaining down/up data and analyzing person differences rather than assuming one universal timing pattern.
- İşeri and Ekşioğlu, 2015, [Estimation of digraph costs for keyboard layout optimization](https://doi.org/10.1016/j.ergon.2015.04.006), with [institutional publication record](https://ie.bogazici.edu.tr/content/estimation-digraph-costs-keyboard-layout-optimization). Empirical pair-tapping costs are an established optimization approach. Here, such probes supplement Bangla transcription and need task-transfer validation.
- Soukoreff and MacKenzie, 2003, [Metrics for text entry research](https://www.yorku.ca/mack/chi03.html), and 2004, [Recent developments in text-entry error rate measurement](https://www.yorku.ca/mack/chi2004.html). Presented text, final text and the input stream answer different error questions; constructive multi-action entry requires care in assigning errors. This motivates separate composition, error and repair ledgers.
- Sarcar, Arif and Mazalek, [Metrics for Bengali Text Entry Research](https://arxiv.org/abs/1706.08205), presented as a CHI 2015 workshop position paper and deposited in 2017. It specifically addresses adapting text-entry metrics to Bengali. This protocol states its own NFC/grapheme/action definitions rather than assuming English five-character WPM is a universal Bangla outcome.

- Chaibub Neto et al., 2019, [Detecting the impact of subject characteristics on machine learning-based diagnostic applications](https://www.nature.com/articles/s41746-019-0178-x). Repeated measurements crossing training/test partitions can confound evaluation. This is methodological evidence from another domain, not Bangla validation; the application here motivates conservative grouping and explicit unknown-person limits.

All prespecified defaults and release tolerances above are this protocol's design recommendations. The central unresolved empirical question is whether shared action costs predict the required out-of-mapping and out-of-rule behavior well enough to justify the intended comparisons.
