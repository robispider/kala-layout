# Restore the originally published Kala Goti and Kala Jhor

Date: 29 October 2026. Status: **handoff plan; implementation has not started**.

## 1. Owner decision and intended result

Restore the original, separately positioned **Kala Goti** and **Kala Jhor** as the current supplied layouts and recommended arrangements across the research publication, Windows application, learning software and public websites. Preserve each layout's native typing grammar. Keep the shared B01/B02 work, Balance studies, certificates and pilots available as explicitly identified historical experiments.

**Owner's communication clarification:** this is continuous development in an early-stage project. Implement the changes as normal development, without a public restoration, rollback, abandonment or reversal announcement. Kala's product website and learning surfaces describe the published Goti/Jhor layouts and their benefits in the present tense. The experimental history, comparison of alternative paths, reasons for selecting the original arrangements, and detailed search evidence belong in **kala-layout only**.

The user's request authorizes this direction. Do not ask again whether to restore the original maps or discard the experimental records. Work through concrete implementation, verification and release preparation. This document itself changes no application, publication selection, website deployment or installed user profile.

| Layout | Authoritative arrangement | Original search | New evidence |
| --- | --- | --- | --- |
| Kala Goti / A | `A-18fe73cb912ae3f1` | 512 starts; 512 million annealing proposals; 36 starts reached the winner | 8,000 new starts; 8 billion annealing proposals plus local search; 514 starts reproduced the exact original map |
| Kala Jhor / D | `D-e4a6be48881da590` | 512 starts; 512 million annealing proposals; 24 starts reached the winner | No new eight-billion Jhor search was performed |

Both retain the original objective: **J_mix = 0.5 J1(Wikipedia training) + 0.5 J1(newspaper training)**, with the original frozen model, style-specific encoders, count tables, geometry, Shift costs, inventory and fixed punctuation/digits. This is restoration of those exact maps, not selection of the separate Balance leaders.

## 2. Repositories and required reading

The work spans **four repositories**, because Kala's public documentation is maintained separately from the Windows app.

| Repository | Local root | Responsibilities |
| --- | --- | --- |
| kala-layout | `D:/git repo/kala-layout` | Canonical maps, scoring, search evidence, publication selection, challenge, research website |
| kala | `D:/git repo/kala` | Shipped native assets, learning packs, prompt banks, app copy, compatibility, installer |
| kala-typing-master | `D:/git repo/kala-typing-master` | Web learning software, imported layouts/course data, progress, public web pages, historical pilot |
| kala-releases | `D:/git repo/kala-releases` | Public Kala guides, research snapshot, homepages, availability and release links |

Read the applicable `AGENTS.md` files at execution time. The current shared-layout instructions in kala-layout and Kala are superseded by this explicit owner decision for the restoration; update those instructions when implementing so later work does not reintroduce B01 as the default. Preserve their unrelated requirements.

Before app typing work, read `kala/plans/product-refactor/EXTERNAL_APP_CONTRACT.md`, `kala/plans/product-refactor/RULES.md`, `kala/plans/fixed-layout-typing-style/IMPLEMENTATION_PLAN.md` and `kala/kala/Ui/README.md`. Read `kala/plans/shared-layout/VALIDATION.md` and `migration.json` to understand all affected assets. Read `kala-typing-master/artifacts/shared-layout-validation.md`, `RESEARCH.md`, and `kala-releases/SITE.md`.

The associated [SOURCE_SNAPSHOT.json](SOURCE_SNAPSHOT.json) records inspected repository revisions and evidence hashes. Inspect fresh status before editing; preserve unrelated changes. Use `codex/` branches if creating implementation branches. Do not blindly revert migration commits: they also contain native typing, history and compatibility safeguards that must remain.

## 3. Product wording and research records

### Where each kind of content belongs

| Surface | Include | Keep in kala-layout instead |
| --- | --- | --- |
| Kala site (`kala-releases`) | Published Goti/Jhor maps, typing recipes, supported modeled benefits, learning guidance, accurate availability, optional research link | Shared/Balance history, why a path was set aside, restoration narrative, detailed search counts and certificates |
| Kala application | Current layout names, native vowel rules, useful layout benefits and instructions | Announcements about reverting a research direction or explanations of discarded experiments |
| Kala Typing Master Home/Learn/About | The published maps, useful features, lessons and practice instructions, optional research link | Development/reversal narrative, abandoned-path comparisons, detailed eight-billion evidence |
| kala-layout repository and research site | Current maps and objective, full research chronology, rationale, all experimental alternatives, search evidence and precise limits | No announcement-style framing is needed here either; use factual research records |

Internal asset identities, compatibility records, migration tests and preserved raw pilot data remain necessary in their implementation repositories. Those technical records do not authorize adding a research-decision discussion to product pages. Existing experimental tools may retain the identity and operating instructions needed to use them correctly, while directing readers to kala-layout for research history and interpretation.

### Product description draft

> Kala Goti and Kala Jhor are research-designed Bangla keyboard layouts with key positions selected for lower modeled finger effort. Goti uses hasant followed by a vowel sign to enter a full vowel. Jhor selects the sign or full vowel from context and supports repeated-key vowel entry. Explore each layout's key map and practise its typing rules.

Bangla draft for native-speaker review:

> কালা গতি ও কালা ঝড় গবেষণাভিত্তিক বাংলা কিবোর্ড লেআউট। মডেলের হিসাবে আঙুলের পরিশ্রম কমানোর লক্ষ্য নিয়ে অক্ষরগুলোর অবস্থান বেছে নেওয়া হয়েছে। গতিতে পূর্ণ স্বরবর্ণ লিখতে হসন্তের পরে কার চাপতে হয়। ঝড়ে প্রসঙ্গ অনুযায়ী কার বা পূর্ণ স্বরবর্ণ লেখা হয়। প্রতিটি লেআউটের অক্ষরের অবস্থান দেখে লেখার নিয়ম অনুশীলন করুন।

Adapt this wording to the actual page. Retain the distinction between modeled effort and measured human speed/comfort. Product guides may report supported benefit figures with their model/baseline scope; keep competitor comparisons off the homepage as required by the existing Kala site policy. Do not turn the eight-billion search into a product-site counter or a rollback announcement.

### Required research rationale — kala-layout only

1. The owner prioritizes each typing style's original J1 effort objective and the original published arrangements.
2. Sharing addressed one remembered positional map across two vowel-entry styles. It introduced documented mechanical compromises; the intended learning/switching benefit has not been measured.
3. Balance answered a different question by adding explicit within-word distance, cross-space distance and order priorities. Its leaders remain valid results under that formula, including their real gains and regressions. A lower Balance R does not establish lower original J1.
4. The new Goti search used exactly the original scoring problem and fresh seeds. Its larger budget found no lower-J1 arrangement and repeatedly reproduced the original map.
5. This supports the product decision to restore the originals. It does not invalidate the shared local certificate, prove a global optimum, establish superiority on every mechanical metric, or measure human typing performance.

The evidence makes the trade-off concrete. B01 adds **0.689% Goti / 0.439% Jhor training J1** against the original same-style maps; the previously examined held-out means add **0.608% / 0.447%**. Its selection used the relaxed shared policy (+0.75% effort, +7.5% within-word distance) and separate R calibration. The separate Balance leaders also accept higher original training J1 (**+0.288% Goti / +0.273% Jhor**) for other component gains. Under the owner's restored priority, none of these is a lower-J1 replacement. Preserve the source comparisons in `results/shared-publication-v1/REPORT.md` and `results/balance-v1/CANDIDATE_ANALYSIS.md`; do not present a change of product priorities as a mathematical refutation of those experiments. The original J1 weights are also modeling assumptions, not validated human performance measurements.

### Research-record English draft — kala-layout only

> The published Kala Goti and Kala Jhor use separate arrangements selected under the original modeled-effort objective for their respective typing styles. The shared-map experiment examined a common set of key positions, while the Balance studies examined additional movement and finger-order trade-offs. The original J1 objective remains the selection criterion for the published layouts; the alternative experiments and their limitations remain available in the research history.
>
> A new Goti search evaluated eight billion annealing proposals, plus local search, from 8,000 seeded starts. It found no lower-J1 layout: 514 starts returned the exact originally published Goti arrangement. This provides substantial additional evidence that Goti remains the best arrangement found under the stated frozen model and training data. It is not a proof of global optimality or a measurement of typing speed or comfort. Jhor retains its separate original search evidence; the new eight-billion run covered Goti only.

### Research-record Bangla draft for native-speaker review — kala-layout only

> প্রকাশিত কালা গতি ও কালা ঝড়ের অক্ষরের অবস্থান আলাদা। প্রতিটি টাইপিং স্টাইলের জন্য মূল J1 মডেলে কম পরিশ্রমের স্কোরকে অগ্রাধিকার দিয়ে লেআউট দুটি বেছে নেওয়া হয়েছে। অভিন্ন লেআউটের পরীক্ষায় একই অক্ষরের অবস্থান রেখে দুই স্টাইলে লেখার সুবিধা দেখা হয়েছিল। Balance গবেষণায় আঙুলের চলাচল ও ব্যবহারের ক্রমের জন্য বাড়তি অগ্রাধিকার যোগ করা হয়েছিল। প্রকাশিত লেআউট বেছে নেওয়ার মানদণ্ড মূল J1 স্কোর; অন্য পরীক্ষাগুলোর ফল ও সীমাবদ্ধতা গবেষণার ইতিহাসে সংরক্ষিত আছে।
>
> কালা গতির নতুন সার্চে ৮০০ কোটি অ্যানিলিং প্রস্তাবের পাশাপাশি লোকাল সার্চ চালিয়েও কম J1 স্কোরের কোনো লেআউট পাওয়া যায়নি। আলাদা সিডে শুরু করা ৮,০০০ সার্চের মধ্যে ৫১৪টি আগে প্রকাশিত একই লেআউটে পৌঁছেছে। নির্দিষ্ট মডেল ও ট্রেনিং ডেটাসেটে এখন পর্যন্ত পাওয়া সেরা ফলের পক্ষে এটি শক্ত অতিরিক্ত প্রমাণ। সম্ভাব্য সব লেআউটের মধ্যে এটিই চূড়ান্ত সেরা—এমন গাণিতিক প্রমাণ বা মানুষের টাইপিং গতি ও স্বাচ্ছন্দ্যের পরিমাপ এটি নয়। নতুন ৮০০ কোটির সার্চটি শুধু কালা গতির জন্য করা হয়েছে; কালা ঝড়ের আগের আলাদা সার্চের প্রমাণ বহাল আছে।

Keep this discussion and the complete search qualification in kala-layout's research pages. Short product copy may link there without repeating the experimental history or detailed search budget. Within the research record, label **Goti** beside the eight-billion figure. Do not attach it to Jhor or present it as eight billion unique layouts. Do not add the four-billion shared experiment to Goti's search budget as if the objectives were identical. The title "best found" must name the objective and scope; do not replace it with "proven best", "fastest" or a comfort claim.

### Frozen numbers for the restoration

| Measurement | Original Goti | Original Jhor |
| --- | ---: | ---: |
| Mixed training J1 | 1.8496860307151324 | 1.8087958948695027 |
| Three-source held-out mean J1, rounded | 1.843229 | 1.800026 |
| Original recorded effort reduction vs tested UniJoy | 34.1% | 35.7% |

Read exact scores from authoritative artifacts when generating tables. Keep each table's corpus weighting, baseline variant and fingering explicit. The previously examined held-out sources are diagnostic reuse in the new Goti run, not fresh independent text confirmation.

The new Goti run had **241 distinct retained final layouts**, one lowest-scoring retained arrangement, zero positional differences from published Goti, and three unsuccessful improvement attempts in final confirmation. Its reported search time was **12,746 seconds / 3 h 32 min 26 s** with 28 workers. The 241 endpoints do not count all visited arrangements. No new certificate or global bound was produced. Original Phase 4 bounds concern Wikipedia-only predecessors and do not transfer to these mixed-corpus layouts.

## 4. Execute in dependency order

### Checkpoint 0 — preserve the evidence before editing

- [ ] Recheck status and source hashes in all four repositories; record starting revisions and unrelated edits.
- [ ] Preserve `work/goti-j1-8b-v1/` in durable tracked research evidence **before relying on it in public copy**. It is currently ignored by Git. Use a new additive phase such as `results/goti-j1-8b-v1/` with `REPORT.md`, machine-readable summary, complete retained search records and a new provenance manifest.
- [ ] Copy the original run manifest verbatim as a source manifest. Its paths name `work/`; create a separate publication/archive manifest that maps relocated files to their originals and records byte hashes. Do not silently rewrite the original search manifest or the original 512-seed evidence.
- [ ] A lossless `.json.gz` archive is acceptable for the complete 8,000-run records. Record and verify both compressed and decompressed hashes, and document reading/replay. Retain all 241 endpoint identities, scores and counts, all seeds/settings, comparison and final map. No search-corpus texts belong in this phase.
- [ ] Promote or adapt the existing independent report verifier. Recheck all input/output hashes, the 52 original assignments and exact integer scores for every retained endpoint; preserve the distinction between exact score verification and optimality certification.
- [ ] Preserve original mixed-search results, original exports, Phase 4 evidence, Balance studies, shared searches/publications/scorers, B01/B02 maps, the shared local certificate and pilot evidence. Capture relevant baseline hashes so preservation can be checked at the end.

Exit: the eight-billion evidence is reproducible outside this local ignored directory, and the restoration has named, immutable map sources.

### Checkpoint 1 — restore the research publication and defaults

Authoritative original arrangements:

- `results/mix-search/search/A.json` and `D.json` (research source).
- `results/kala-keyboards/kala-goti.json` and `kala-jhor.json` (original research exports).
- Original app snapshots in `kala/kala.BaselineTests/Fixtures/OriginalKalaLayouts/` (runtime compatibility reference; verify against research positions rather than trusting the name).

Implementation:

- [ ] Add an explicit active-publication selector and a restored separate-publication descriptor. Suggested names: `data/layout-publications/current.json` and `separate-restored-v1.json`. Record both original map IDs, style grammar IDs, hashes, scoring season and evidence links. Do not repoint or overwrite the frozen `shared-v1.json` descriptor.
- [ ] Update `site/scripts/publication.mjs`, `sync-content.mjs`, validators and frontend consumers to load the active selector. They currently assume one shared map, one shared summary, shared challenge data and two R values. Generate current separate-map tables from frozen original J1 data; preserve explicit historical shared views.
- [ ] Restore original-J1 defaults for `challenge-kit`, `challenge-verify`, `leaderboard` and `kala-export`. The existing scoring identifier is `legacy-v1`; it can remain that identifier even when its original J1 rules become current again. Keep `--season shared-v1`, `publish-shared`, `certify-shared` and verification of old shared artifacts working explicitly.
- [ ] Preserve the original scorer's mathematical definition, data version and counts. A new publication decision is not permission to rewrite the original scoring season. If implementation actually changes a scorer, grammar, corpus, model or symbol problem, stop treating it as an identical restoration and record the separately required new scoring season.
- [ ] Do not globally repoint `mix.mixed_best_layout`, change model constants, rerun corpus construction, or overwrite `results/mix-search/` to insert the 8,000-start history.
- [ ] Update `.github/workflows/submissions.yml` so season selection is explicit for both the restored original season and the historical shared season; remove reliance on the old default inside shared checks. Preserve existing submissions and board history.
- [ ] Update current README material, `docs/LAYOUTS.md`, `HOW_WE_FOUND_THEM.md`, `REPRODUCE.md`, `CHALLENGE.md`, `SHARED_LAYOUT.md`, `SHARED_CERTIFICATION.md`, `MECHANICS.md` where affected, and matched `translations/bn/docs/` pages. Add a dated research decision record and eight-billion evidence page with its Bangla pair. Keep the rationale in this repository and use factual research language rather than an announcement. Append the decision to `docs/RESEARCH_SPEC.md` rather than rewriting its old decisions.
- [ ] Change shared/B01 entry points to clearly labeled historical research, preserving routes, raw reports, scores and certificate scope. Update navigation, metadata, search labels and links as well as visible headings. Keep Goti/UniJoy and Jhor context-vowel prior-art credits.
- [ ] Update `AGENTS.md` and affected contributor guidance to the new active publication.
- [ ] Extend reproduction coverage for the additive evidence and active publication. Review the lock diff; old research groups must retain their original canonical hashes. Use `check-results --lock` only after verifying and explaining intended additions, never to hide a drift.

Exit: current research pages, downloaded maps, default scorer/board and repeat commands all describe the same two original arrangements; historical shared commands still reproduce their frozen problem.

### Checkpoint 2 — restore Kala's supplied native assets

- [ ] Restore every original symbol position in `kala/layout/bn/KalaGoti.json` and `KalaJhor.json` against the research sources. Preserve native type/style capabilities, valid composition sequences and Jhor context/repeated-key rules.
- [ ] Keep native schema `version: 1.0`; it is a file-format version, not a publication identity. Use explicit arrangement/publication metadata to identify the restored maps. Do not force equal Goti/Jhor layers: their original maps differ at 31 of 52 assignments.
- [ ] Preserve Kala's established atomic/precomposed spellings for native decoder/backspace compatibility where required; compare all 52 positions using NFC. Do not change Unicode semantics while moving keys.
- [ ] Reuse stable built-in catalog IDs where appropriate. Do not overwrite custom imported layouts based only on their name. Preserve user-created copies and imported B01 maps; distinguish them by validated content/identity.
- [ ] Update English/Bangla layout-card metadata and localization resources to describe the published maps, native rules and supported benefits in the present tense. Remove current shared-position promises. Add no research-reversal announcement to cards or other product copy. Restore original-map CC0 notices while retaining notices for archived MIT shared assets and other software.
- [ ] Replace the current shipped-map equality contract in `SharedKalaLayoutTests.cs` with positive restored-map tests against immutable original fixtures. Keep any retained B01 decoder tests explicitly tied to B01 fixtures. Do not delete regression coverage simply because the active publication changes.
- [ ] Restore physical keystrokes for the original Jhor map in map-dependent fixtures. Preserve the approved expected Bangla output for all 950 Jhor cases. Check Goti fixtures as well. Prefer deriving/replaying strokes from canonical symbol maps over manual replacements.
- [ ] Record the original-to-shared-to-restored transition and exact installed asset hashes in a new migration record. Keep `plans/shared-layout/` as history. Update Kala `AGENTS.md`, which currently requires matching shared layers.

Exit: research and shipped native maps agree on all positions; native vowels, repeats, Backspace, shortcuts and enabled corrections still work through both physical and on-screen input.

### Checkpoint 3 — version learning packs, prompt banks and existing progress safely

This is part of the restoration, not an optional follow-up. The desktop currently bundles literature pack **1.1.1** and typing-check bank **1.4.1** for the shared maps.

- [ ] Identify current authoring definitions and exact build/package inputs. Create new forward versions bound to the restored maps (for example 1.1.2 and 1.4.2 **only if those versions are still unused**). Keep old packs/banks byte-identical and readable.
- [ ] Regenerate layout-bound teaching paths and hashes, native decoder-validated prompt variants, coverage reports and provenance. Preserve prompt texts, IDs and attributions unless a separately justified change is required. Report actual coverage rather than carrying B01's numbers forward.
- [ ] Update `kala/Learning/Study/PromptBank.cs`, supported bank/version handling and all relevant source/package selectors. Keep historical bank/protocol pairs accepted. Check any receiver compatibility affected by a new bank; do not relabel or re-upload old study sessions as restored-map data.
- [ ] Ensure the installer/update output selects the new forward pack version. Merely putting an old original-map pack beside a newer B01 pack is insufficient if the catalog chooses the highest version.
- [ ] Preserve existing personal profiles, sessions, activity, bookmarks and backups. Keep positional confidence, key errors and lesson completions separated by validated mapping identity.
- [ ] If earlier original-map positional progress is archived, restore it only after verifying an exact semantic map-and-grammar match. Account for metadata-only file-hash differences through explicit validated aliases; never assume the same display name means the same mapping.
- [ ] Archive current B01 positional progress without applying it to original positions. Make the transition idempotent across reload, upgrade and backup restore. Keep genuinely new learners' progress clean. Do not read or migrate a real personal profile during implementation tests.

Exit: current courses and typing checks teach the restored maps, old sessions retain their original identities, and synthetic upgrade/migration tests demonstrate no cross-map progress mixing or data loss.

### Checkpoint 4 — update Kala Typing Master from verified desktop sources

- [ ] Update `scripts/import-kala.mjs` to select the new forward pack/bank and produce metadata for separate original arrangements. Its current instructions are generated only for `kala-shared-publication-v1`; remove that assumption so restoration cannot silently lose instructions.
- [ ] Import via `npm run import:kala -- ../kala`; do not hand-patch committed generated map/course data while leaving the importer able to regenerate B01. Check source hashes and bindings in `src/data/layouts.json`, `paths.json`, `courses.json`, `source.json`, public pack data and prompt variants.
- [ ] Update `src/lib/i18n.ts`, layout cards, the Home/Learn/About pages and instructions. Present the published layouts, their benefits, distinct keys and native vowel rules as the normal product. Keep research-decision discussion and detailed eight-billion evidence in kala-layout, reachable through an optional research link.
- [ ] Update `src/lib/store.ts` mapping-history transitions as described above. Its current map identity uses source-file SHA-256, so metadata-only hash changes and an archived original map need explicit handling.
- [ ] Replace the ordinary-course shared-key expectation in `tests/shared-layout.test.ts`; retain map identity, same-output Jhor fixtures, decoder, check-bank, progress and course coverage assertions.
- [ ] Preserve `src/data/shared-candidates.json`, `scripts/import-shared-candidates.mjs`, `src/lib/research.ts`, `src/scripts/research.ts` and the B01 pilot's map/protocol identities. Keep any retained pilot clearly identified by its experimental map and protocol; it must not silently inherit published course maps or be promoted as the ordinary product layout. Preserve local research reports and protocol history. Keep necessary operating instructions and technical compatibility notes, but place the research history and decision rationale in kala-layout and link there instead of duplicating that discussion in the trainer. Update `RESEARCH.md` and research tests accordingly.

Exit: ordinary practice, recipes, on-screen cues, finger guidance, typing checks and persisted progress match the restored maps; historical research remains separate and replayable.

### Checkpoint 5 — update Kala's public guides and both website languages

- [ ] In `kala-releases`, make `docs/layouts/kala-goti.md` and `kala-jhor.md` normal current-layout guides. Describe their benefits and typing rules, without "we are returning", "restored", "rollback", "we gave up" or similar development-history banners. Verify every key table and example against the desktop sources.
- [ ] Make `docs/layouts/kala-layout.md` a neutral overview of the published layouts or an appropriate current-guide route. Keep the full shared-layout account in kala-layout. Preserve useful old links with redirects or a short neutral research link, without publishing the abandoned-path discussion on the Kala product site. Retain the old source in Git history.
- [ ] Update `research-and-comparison.md`, the evidence snapshot, homepage components, navigation, Learn links, accurate release-status/availability copy and matched Bangla sources to describe the published layouts and supported benefits. Explain their method and scope where useful; link to kala-layout for experimental history, decision rationale and detailed search evidence. Do not add a restoration announcement, timeline or eight-billion marketing counter.
- [ ] Preserve the historical `docs/reference/layout-research-snapshot.json` provenance. If current product facts need a new snapshot, version it accurately and keep it focused on the published maps and their supported benefits. Record detailed new Goti search evidence and the dated research decision in kala-layout; do not make the old reviewed date/source tag falsely attest to a new run or binary audit.
- [ ] Follow `kala-releases/AGENTS.md` for natural Bangladeshi Bangla. Preserve literal কি/কী, key sequences, source identities, numbers, attribution and placeholders. Obtain native-speaker meaning review for changed Bangla claims; automated parity checks are a separate gate.
- [ ] Edit canonical Markdown/translations and source components, not generated `site/src/content/docs/`. Preserve `kala:latest` and `kala:latest-channel` workflow markers. Do not hand-invent a new installer version or claim an update is installed/published before verifying it.
- [ ] Link the three public sites to consistent, language-matched current maps and instructions, with optional links to kala-layout's research evidence. Keep historical shared research URLs usable in kala-layout. On product-site legacy routes, use an appropriate neutral redirect/reference rather than reproducing the research-decision discussion.

Exit: a user landing on a Kala product homepage or typing guide sees the published layouts, their benefits, usage and accurate availability as normal early-stage development. Research chronology and the reasons for setting aside experiments appear in kala-layout only.

### Checkpoint 6 — validate the complete chain

Research:

```powershell
# From D:/git repo/kala-layout
$env:PYTHONPATH = 'src'
python -m unittest discover -s tests
python -m bangla_dh challenge-kit --season legacy-v1
python -m bangla_dh leaderboard --season legacy-v1
python -m bangla_dh check-results

# Archived shared verification remains explicit
python -m bangla_dh challenge-verify --season shared-v1 challenge/shared-v1/reference.json
python -m bangla_dh verify-shared-certificate results/shared-certification-v1

# Research website, from site/
npm run check
npm run build
```

Also score the restored A and D references through the original portable scorer and independent project scorer, and test default CLI selection after its implementation. Verify new archived search evidence and all preserved frozen hashes. Archive location/season naming may require an intentionally documented command update; do not run `publish-shared` as the active restoration publisher.

Where a historical manifest hashes the original implementation code, perform its full reproduction against the recorded source revision in an isolated checkout. Do not rewrite old manifest hashes to make changed current code appear to be the historical implementation. Record artifact verification and pinned-revision replay as separate checks.

Kala Windows:

- Run targeted native fixed-layout, import, fixture, style isolation, modifier, learning, prompt-bank and affected progress/transition tests from the inspected migration/style plan. Include positive all-52-position tests for both original maps. **Do not run the full local Kala suite unless explicitly requested.** Record failures and separate reruns honestly.
- Run relevant external typing/correction checks and `scripts/validate-ui-resources.ps1`, `scripts/check-git-inputs.ps1`, plus `git diff --check`.
- Build an isolated Release app and prepare/check installer payloads using the repository's release tools. Inspect packaged maps, publication metadata, pack selection and hashes rather than assuming source assets were bundled.
- Record controlled live checks in Word, Notepad, a browser field, and Paint/Photoshop with an active text tool where available. Cover physical/on-screen input, Goti/Jhor switching, vowel recipes, conjuncts, repeated-key rules, Backspace, enabled corrections and shortcuts. A practice editor or hidden fixture alone does not establish live external compatibility. Preserve current real-user activity; record unavailable destinations as pending rather than passed.

Kala Typing Master:

```powershell
# From D:/git repo/kala-typing-master, after desktop sources are finalized
npm run import:kala -- ../kala
npm test
npm run build
```

Inspect English/Bangla desktop and mobile previews, original-map key cues and the live recipes below. Test synthetic original-only, B01-only, both-history and empty profiles; repeat upgrade/reload/backup restore. Verify historical B01 pilot isolation and stored-map identities.

Kala guide website:

```powershell
# From D:/git repo/kala-releases/site
npm run check
npm run build
```

Inspect both languages, tables, links, narrow screens, search results and same-page language switching across all three sites. Verify current-versus-history labels within kala-layout and check that product pages contain no restoration announcement or shared/Balance decision narrative. Structural checks cannot replace Bangla meaning review.

Required restored examples (physical US-QWERTY positions):

| Text | Original Goti | Original Jhor |
| --- | --- | --- |
| আমি | K F X C | F X L |
| কী | J T | J G |
| বই | A K C | A L L |
| তিনিই | M C S C K C | M L S L L L |
| আকাশ | K F J F Y | F J F Y |
| Hasant position | K | C |
| ি position | C | L |

Exit: write a cross-repository validation report with revisions, source/map hashes, command results, generated artifacts, live-test results and remaining release blockers. Do not mark pending human or application checks as completed.

### Checkpoint 7 — coordinated delivery and recovery

- [ ] Prepare reviewable changes and a dependency manifest naming the four repository revisions, evidence phase, publication IDs, asset hashes, pack/bank versions and website builds.
- [ ] Inspect workflow triggers before pushing. **Kala's `.github/workflows/publish-kala.yml` publishes on a push to `main`.** The websites also deploy through their configured workflows. Use feature branches/PR previews during preparation so an intermediate push does not accidentally publish a mixed state.
- [ ] Do not publish/install anything merely to complete this planning task. During implementation, carry existing user authorization forward and obtain only any still-required release authorization after the tested artifacts are concrete. Do not repeatedly seek approval for routine restoration edits.
- [ ] Publish durable research evidence and current-map references before research copy relies on them. Coordinate the validated application release, web trainer and guides as ordinary development updates; use no restoration announcement or abandoned-path story in product release copy. Keep availability copy accurate during any staggered deployment. Let the existing latest-release workflow update installer references.
- [ ] Smoke-test deployed EN/BN pages, downloads and their map hashes. Check fresh install and an isolated upgrade from the shared build, including forward pack selection and preserved history. Record installed binary/asset checks separately from source/build checks.
- [ ] Recovery must be a forward, versioned change to a known validated release/publication snapshot. Keep both original and shared artifacts available; do not delete user profiles, rewrite historical study sessions, or lower a bank version and assume automatic selection will follow it.

## 5. Acceptance checklist

- [ ] Both current research IDs are exactly `A-18fe73cb912ae3f1` and `D-e4a6be48881da590`.
- [ ] All 52 positions per style match research, desktop assets, packaged payload, web trainer and public guides after NFC normalization.
- [ ] Active Goti and Jhor have distinct original positions and preserve their native entry rules.
- [ ] Every ordinary Learn/check source, importer and generated binding teaches the restored maps.
- [ ] Synthetic migration tests preserve and correctly separate old original-map progress, B01 progress, sessions, backups and experimental pilot data.
- [ ] Eight-billion evidence is durably versioned, hash-verified and linked publicly; no essential claim depends on ignored `work/` files.
- [ ] Goti-only search budget, 514/8,000 reproductions, experimental chronology and decision rationale are documented consistently in both languages in kala-layout. Product surfaces describe the published maps and benefits and link to research when useful.
- [ ] Kala's site, app cards and ordinary Typing Master pages contain no restoration/reversal announcement, abandoned-path discussion or detailed eight-billion marketing counter. Both language versions follow this ordinary-development presentation.
- [ ] Jhor is not described as having passed the new eight-billion search. No old or shared certificate is transferred to the restored mixed-corpus maps.
- [ ] Shared/Balance results, their original scores and frozen evidence remain available as history. Their successful scoped claims are preserved.
- [ ] Current CLI defaults, CI season selection, publication loader, scoreboards, downloads and website navigation agree.
- [ ] Applicable automated, packaging, live app and language checks are recorded; unavailable checks remain explicit.
- [ ] Release readiness and actual deployed/installed availability are reported separately. No unrelated edits or personal data are overwritten.

## 6. Copyable implementation handoff

> Implement the owner-approved restoration in `D:/git repo/kala-layout/plans/restore-published-layouts/HANDOFF.md`. Restore the exact original separate Kala Goti (`A-18fe73cb912ae3f1`) and Kala Jhor (`D-e4a6be48881da590`) across kala-layout, kala, kala-typing-master and the kala-releases documentation website. Treat this as continuous early-stage development: Kala's product site, app cards and ordinary Typing Master pages describe the published layouts, their benefits and typing rules in the present tense, with no restoration/reversal announcement. Keep shared/Balance history, reasons for choosing the original path and detailed search evidence in kala-layout only; product pages may link there. Follow the plan's dependency order and preserve each repository's applicable instructions and unrelated edits. First archive and verify `work/goti-j1-8b-v1/` as durable research evidence. Preserve all shared/Balance experiments, original research and user progress with explicit map identities. Update publication/defaults, native assets, forward-versioned learning packs and prompt banks, importers, training progress, tests and both website languages. The 8-billion-plus-local-search result is Goti-only: 514/8,000 fresh starts found the exact published map; no lower original J1 score was found. In the research record, describe this as substantial additional best-found evidence under the frozen model, not global optimality or human speed/comfort. Do not launch another large search or require a new certificate to restore the maps. Complete local changes, verification and release preparation without asking again about the restoration direction. Inspect publishing triggers before pushing; Kala main auto-publishes installers. Report concrete artifacts, checks, unresolved blockers and any final release authorization still needed.
