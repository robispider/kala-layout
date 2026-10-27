# Modeling-plan execution — 27 October 2026

The collection fixes and repeatable empirical pipeline are implemented. The observed human pilot and a learned layout evaluator remain pending. All original packages, frozen search inputs, J0/J1 scores, reproduction locks and published Kala layouts are preserved.

The plan at `results/usage-metric-audit-v1/MODELING_PLAN.md` was expanded during this work to require a transferable evaluator and improvement search. Those edits are preserved. The collection uses **Kala's existing research skill check**. Volunteers should use a familiar fixed layout; they do not need to learn every candidate the evaluator will inspect.

## Delivered and remaining

| Stage | Implemented evidence | Remaining gate |
| --- | --- | --- |
| Measurement | Extended Right Shift position and held-state handling; conservative delivery correlation; explicit capture-v2 engine suffix; empty-response and within-prompt idle flags without changing time; mutation/capture tests | Physical external/laptop recordings and a fresh consented package |
| Whole collection path | Targeted receiver tests; real loopback HTTP probe using current client serialization/uploader source: 201 upload, 200 identical retry with stable receipt, 409 conflicting retry, 202 withdrawal, 410 late retry | Observe participant UI, offline outbox restart, actual receiver restart, public publication/removal and queued retries, external applications |
| Independent audit | Strict session field/type adapter, UTF-16 replay, pinned Unicode 15.0 graphemes, score and qualification recalculation; all four packages pass | New segmenters/protocol behavior need an explicit adapter |
| Registries | Exact UniJoy mapping bytes, client hash convention and alternate-style hash rule; historical engine source hashes; bank hashes, source-work/family identities, preparation and selection hashes | Exact historical UniBijoy runtime mapping is missing; engine replay and near-duplicate family reviews remain pending |
| Features | Sessions, prompts, key/edit events, down-down intervals, dwell, flight, repeats and correction outcomes; compressed stable schemas; package/event provenance and reason-coded exclusions | Modifier/space/composition strata are retained, but do not yet have validated transferable timing models |
| Fit and evaluation | Contributor-weighted median and additive ridge; frozen-effort feature baseline; contributor and family holdouts; contributor bootstrap/refits, residual and stratum reports; separate correction-action baseline | Actual fit correctly returns insufficient_data; adequate independent replication and pilot evidence are absent |
| Layout evaluator | Explicit style A–D and finite sequence-replacement keymap adapters; NFC replay checks; real Shift downstrokes; identical reference condition and text; support/extrapolation refusal; paired bootstrap differences | Full-layout scoring needs validated operation models, exact imported grammar adapters where applicable, and transfer evidence |
| Improvement search | Deterministic symbol/Shift-slot swaps, locked symbols, change budget, held-out text exclusion, support and uncertainty guards; synthetic improving/no-improvement cases | No empirical proposal is produced without a supported fitted model |

## Current dataset result

Four sessions, two contributor IDs, four distinct protocols. All 547 missing Right Shift labels are recovered **only in derived fields** using `vk=0xA1, sc=0x36`; the original nulls and raw flags remain. The unknown-source exact-linked edit remains excluded from attribution; neighboring pairs are not bridged.

There are 1,076 eligible primary intervals. Including idle-flagged sessions gives 1,320; this is a separately labeled sensitivity analysis. Original speed denominators are unchanged. The 53-second empty prompt remains visible.

The cohort proposal is 20 contributors with at least two familiar-layout sessions each, under one frozen protocol/bank/build. These are execution floors, not a power calculation. Coverage, family review, engine recovery, independent contributors and observed pilot evidence are all separate gates. Thousands of event rows cannot replace independent people.

## Commands

Run from the kala-layout root:

```powershell
$env:PYTHONPATH = "src"
python -m bangla_dh audit-usage-data
python -m bangla_dh build-usage-features
python -m bangla_dh verify-usage-run results/usage-metric-pipeline-v1
python -m bangla_dh fit-usage-model
```

A fit attempt writes a new run directory by default. Exit **2** means no validated fit was released; exit **1** means invalid/stale inputs or an attempted overwrite. Fresh feature builds use the current manifest, so withdrawals disappear from rebuilt tables. `verify-usage-run` rejects changed manifests, packages, policies, registries, implementation files or derived outputs. Old snapshots are historical evidence, not permission to train on withdrawn data.

Registry snapshots are immutable. Supply a recovered exact runtime file into a **new** snapshot:

```powershell
python -m bangla_dh register-usage-data --kala-root 'D:/git repo/kala' --mapping 'PATH/TO/EXACT/layout.json' --out data/usage-metric-registry/v2/registry.json
```

A verified mapping hash does not by itself validate composition. Family/near-duplicate and engine replay statuses must be backed by reviewed evidence before enabling a production fit. New protocol adapters must preserve historical sentence and timed-passage behavior separately.

To exercise the evaluator with downloaded public corpora:

```powershell
python -m bangla_dh evaluate-usage-layouts data/usage-metric-registry/candidates/kala-goti.json data/usage-metric-registry/candidates/kala-jhor.json --reference kala-jhor --fit-run results/usage-empirical-v1/readiness-2026-10-27 --benchmark data/corpus/bangla-corpus-v1/bnwiki-heldout.jsonl.gz --search-benchmark data/corpus/bangla-corpus-v1/bnwiki-train.jsonl.gz --limit 5 --out work/empirical-layout-check
```

This adapter check returns **2 / insufficient_data** on the received sample. The five-document prefixes exercise mechanics; they are not a validated final benchmark. Original text stays in the ignored corpus files; reports contain hashes and physical/symbol-level metadata. No J0/J1 score is substituted for missing empirical costs. Sums of predicted log-interval medians are explicitly distinguished from expected time, page completion, WPM or comfort.

The usage-data workflow now runs all usage tests, the independent audit, clean extraction and snapshot verification on relevant data/code pushes. This local work does not claim the hosted workflow has run.

## Pilot handoff

`pilot-freeze.json` identifies the local Release validation binary, capture source hashes, r5/1.4.0 bank and preparation rules. It does not claim that the shipping installer was deployed or observed. `pilot-evidence.template.json` intentionally marks every observed scenario pending. Copy it into a new evidence record and record actual observers, content-free evidence hashes, package/receipt hashes and outcomes. Never put withdrawal secrets, credentials or private external-app text in this repository.

See [PILOT_CHECKLIST.md](PILOT_CHECKLIST.md). Wider recruitment, actual model fitting and replacing a published layout are not signed off by synthetic tests. Publishing a replacement remains a separate research season.
