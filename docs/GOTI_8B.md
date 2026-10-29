# Kala Goti: eight-billion-proposal J1 search

A new Goti search evaluated eight billion annealing proposals, plus local search, from 8,000 seeded starts. It found no lower-J1 layout: 514 starts returned the exact published arrangement, `A-18fe73cb912ae3f1`. This is substantial additional best-found evidence under the stated frozen model and training data. It proves no global optimum and measures no human typing speed or comfort.

## Scope

| Item | Value |
| --- | --- |
| Annealing proposals | 8,000,000,000 |
| Starts / exact hits | 8,000 / 514 |
| Retained endpoints | 241 |
| Seed range | 20270001–20278000 |
| Workers / reported seconds | 28 / 12,746 |
| Training J1 | 1.8496860307151324 |

Proposals may revisit arrangements. The 241 endpoints do not count every visited map. Three final local-search confirmation attempts found no improvement. Time and workers come from the original terminal record, not a controlled performance benchmark. Previously examined held-out sources were reused diagnostically; they are not fresh independent text confirmation. This run covered Goti only. No new eight-billion Jhor search was performed. The earlier Wikipedia-only Phase 4 bounds do not certify these mixed-corpus maps.

## Verify durable evidence

The [complete report](../results/goti-j1-8b-v1/REPORT.md), [archive and reading instructions](../results/goti-j1-8b-v1/README.md), [original manifest](../results/goti-j1-8b-v1/source-run-manifest.json), [archive manifest](../results/goti-j1-8b-v1/run-manifest.json) and [all search records](../results/goti-j1-8b-v1/search/A.json.gz) are retained in Git. This command checks archive hashes, all 52 assignments and exact integer scores for every endpoint; it runs no search.

```powershell
$env:PYTHONPATH = 'src'
python -m bangla_dh.goti_evidence
```

See the [selection criterion](PUBLICATION_DECISION.md) and [typing rules](LAYOUTS.md).
