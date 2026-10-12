# Challenge submissions

Add one JSON layout file here in a pull request to enter the [layout challenge](../docs/CHALLENGE.md). Start from a reference layout:

```bash
python challenge/bangla_dh_challenge.py --template D --out submissions/my-layout.json
```

Edit `name` and add `author` (your GitHub name), change the layout, then check it:

```bash
python challenge/bangla_dh_challenge.py submissions/my-layout.json
PYTHONPATH=src python -m bangla_dh leaderboard --check submissions/my-layout.json
```

A workflow re-scores every changed file with the public scorer when you open the pull request. The scores written in a file are never trusted: only its layout counts. The ranking is in [LEADERBOARD.md](LEADERBOARD.md), rebuilt after each merge.

Rules in short: style A or D; place each of the 52 symbols once on the 26 letter keys, base and Shift; a layout beats Kala only with a strictly lower J1; the same layout counts once. Files must stay under 64,000 bytes.
