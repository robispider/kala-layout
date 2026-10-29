# Cross-repository implementation and delivery record

29 October 2026. The owner-approved plan has been executed locally across all four
repositories. Implementation, automated checks and local package preparation are
complete. Release is pending controlled live-app checks, native-speaker Bangla
meaning review, release CI and final publishing authorization. No branch was
pushed, no site deployed, and no installed app or personal profile changed.

## Checkpoints and publication

| Checkpoint | Result |
| --- | --- |
| 0: durable evidence | Complete; evidence commit `354ce67`, clean-checkout verification passes without ignored work files |
| 1: research publication/defaults | Complete; active selector chooses separate original maps; original J1 scoring season unchanged |
| 2: native assets | Complete; every original position and native grammar preserved; B01 fixtures retained |
| 3: packs, bank and progress | Complete locally; forward literature 1.1.2 / bank 1.4.2, validated aliases, historical data retained |
| 4: web trainer | Complete locally; importer, generated bindings, recipes, cues and synthetic progress/backup cases pass |
| 5: bilingual product guides | Complete locally; ordinary-development presentation, current maps, preserved historical snapshot |
| 6: automated validation | Passed, with repaired initial failures recorded below; manual live/language gates pending |
| 7: coordinated delivery | Feature-branch commits and local installer prepared; deployment/install smoke checks pending |

Current publication: `kala-separate-publication-v1`, selected by
`data/layout-publications/current.json`. Goti is `A-18fe73cb912ae3f1`; Jhor is
`D-e4a6be48881da590`. Their frozen mixed-training J1 scores remain
1.8496860307151324 and 1.8087958948695027. All 52 positions per style agree among
research, desktop assets, imported web maps and the guide snapshot after NFC.
The actual installer payload bytes also match the native sources. Native file
schema remains 1.0. Both styles differ at 31 assignments and keep their original
vowel/composition/backspace semantics, including all 950 approved Jhor outputs.

The archived Goti run contains all 8,000 seeded records, all 241 retained endpoint
identities/scores/counts, three confirmation records, settings, comparisons and
all 52 assignments. It has 8 billion annealing proposals plus local search,
514 exact reproductions and no improvement. The source search/report manifests
and source report are byte-identical; the separate archive manifest records
relocation and compressed/decompressed hashes. No corpus texts were added.
This is Goti-only best-found evidence under frozen mixed-training J1, with no
new certificate, global bound or human performance measurement. Jhor retains
its original evidence. Known held-out sources are diagnostic reuse.

## Automated evidence

| Area | Recorded result |
| --- | --- |
| Research unit suite | 312 passed; final added active-selector/archive tests: 2 passed; affected shared-publication rerun: 9 passed |
| Durable Goti verification | All source/output hashes, 8,000 records, 241 exact integer endpoint scores, 514 hits and 52 positions passed |
| Clean archive checkout | Passed at evidence commit 354ce67, with no ignored work directory |
| Original scorer | Default challenge-kit regenerated scorer, data, references and guides byte-identically; only new bookkeeping manifest differed and was saved separately |
| Reference scores | Default original A/D references agree exactly with independent project scorer; explicit shared reference also passes |
| Reproduction lock | All old groups unchanged; additive current-publication and Goti-archive groups pass |
| Historical certificate | All 45,526 decisions and hashes replayed independently from pinned original source bytes at 010ee328 |
| Preserved research | 20,657 baseline research files verified byte-identical by SHA-256 |
| Historical desktop packs | 73 files across literature 1.0.3/1.1.0/1.1.1 and banks 1.4.0/1.4.1 remain byte-identical |
| Native gate | 96 passed, 0 failed/skipped |
| Native regression gate | Initial 499 passed / 2 failed; corrected raw-authoring inputs; targeted rerun 8 passed (3 composition, 5 modifier) |
| Map/bank/progress gate | 11 passed, including both styles' original-only, B01-only, both-history and empty profiles |
| Prompt generation | Eight real-decoder-validated forms per supplied layout; Goti/Jhor each reach 559/569 prompts |
| Web trainer | 35 tests passed; production build passed |
| Research site | Content parity and production build passed; 36 pages, 1,739 local links/assets/anchors |
| Product guide site | Content parity and production build passed; 38 pages, 2,194 local links/assets/anchors |
| Installer | Self-contained Release installer built; embedded payload extracted/tested in isolation, no OS registration |
| Resources and inputs | UI resource validation and Git input/size checks passed; no full local Kala suite was run |

The old certificate verifier deliberately rejects changed CLI source in the current
checkout. Its manifest was not rewritten. Full replay used an isolated checkout
with every recorded historical input hash matching; that temporary checkout was
retained as a clean historical checkout. Old artifact verification and pinned-source replay are distinct.

Other initial issues and repairs: stale B01 web fixtures/examples were replaced
with original physical strokes while retaining expected output; synthetic backup
tests stopped comparing absent properties to explicit undefined values; a concurrent
native build encountered a locked test DLL and was rerun in an independent build
root; isolated package inspection needed an explicit source-root setting. All
successful reruns are recorded separately. Existing packaging/compiler and web
TypeScript warnings remain in their logs; successful builds do not establish live
external compatibility.

## Browser and data checks

English/Bangla desktop previews were inspected for the research homepage, product
overview and Goti course. At 390 × 844, the product overview and research evidence
page fit in both language layouts; the Bangla course exposed an intrinsic-width
keyboard/grid overflow, which was corrected. The final course, guide and research
page each reported no page-level horizontal overflow. Ordinary product copy no
longer contains shared-position promises, experimental search counters or reversal
announcements. Historical shared maps, search accounts, mechanics, challenge rules,
board and certificate remain available under explicitly historical research routes.
Goti/UniJoy and Jhor context-vowel prior-art credits remain intact.

Web original/B01 positional history, sessions, bookmarks, settings and activity
are preserved by validated map identity; JSON backup/reload tests cover both styles.
Native synthetic profile persistence tests and course-transition tests passed.
Custom imported layouts are not selected or overwritten by display name. No real
profile or study dataset was opened or migrated. Receiver compatibility was
inspected in source: version/protocol labels are metadata rather than an admission
list, so the forward bank requires no receiver change; no server test/deployment
is claimed.

## Remaining release gates

- Controlled Word, Notepad, browser-field and Paint/Photoshop text-tool checks with
  the actual foreground hook: physical/on-screen input, switching, vowels, repeats,
  conjuncts, Backspace, enabled corrections and shortcuts. The app startup has no
  supported isolated profile switch and acquires the ordinary singleton/profile.
  A controlled isolated Windows session is needed to honor the no-real-profile
  requirement; hidden editor fixtures are not substituted for these checks.
- Native-speaker meaning review of changed Bangla claims and usage text. Structural
  parity and this agent's browser inspection are not human language sign-off.
- The normal release CI gate, exact coordinated release identity, final publishing
  authorization, deployed EN/BN/download/hash smoke checks, and actual isolated
  fresh-install/B01-upgrade smoke checks. The prepared installer is a local source
  validation build using the repository version; it is not a new public release.

## Delivery and recovery

All changes use `codex/published-layouts`. See `DEPENDENCIES.json` for the four
implementation revisions, native/source/pack hashes and installer identity.
Publish research evidence/current references before public copy depends on them;
then coordinate the app, web trainer and guides. Kala main auto-publishes installers;
the sites deploy from main. Do not merge/push an intermediate mixed state.

Recovery must be a forward versioned change to a known tested publication and pack
snapshot. Keep original and B01 maps, old packs/banks and all personal history.
Never delete profiles, relabel old sessions, or downgrade a bank and assume catalog
selection follows it. The unchanged original handoff and SOURCE_SNAPSHOT.json are
planning provenance; this execution record supplies the current status.
