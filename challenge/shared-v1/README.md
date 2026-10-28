# Shared arrangement challenge

One map, both Goti (A) and Jhor (D). Season `bangla-dh-shared-challenge-v1`.
Keep `score.py`, `scoring-data.json.gz` and `LICENSE-mechanics.txt` together. Python 3.10+, no dependencies or corpus download.

```bash
python challenge/shared-v1/score.py --reference
python challenge/shared-v1/score.py --template my-shared.json
python challenge/shared-v1/score.py my-shared.json --diagnostics
```

Submit one map to `submissions/shared-v1/`. Both styles must pass the frozen relaxed-policy effort/within limits against the originals. Ranking uses separate R values and Pareto dominance; never their sum. A strictly smaller same-style J1 alone is insufficient. B01 is provisional. Scores model mechanics, not speed or comfort. Known held-out texts are diagnostic only.

The original independent-style J1 challenge remains in the parent directory; it is a different season. Rules: [docs/CHALLENGE.md](../../docs/CHALLENGE.md). Data SHA-256 `36be11511d89e2aecf1041418aa27f61abe97fa257f3cdcc44b2b8d1fe5bd757`. The package uses MIT-licensed source-derived mechanics tables; attribution is included.
