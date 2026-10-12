# Bangla-DH layout challenge

Can you place the Bangla letters on a keyboard better than Bangla-DH?

| Style | Score to beat (J1, lower is better) |
| --- | --- |
| A (UniJoy-style vowels) | 1.849686 |
| D (context vowels) | 1.808796 |

```bash
python bangla_dh_challenge.py --reference
python bangla_dh_challenge.py --template D --out my-layout.json
python bangla_dh_challenge.py my-layout.json
```

Python 3.10 or newer, nothing else. Read the **[user guide](USER_GUIDE.md)**
for the rules, the file format, how the score works and tips.

Leaderboard and submissions: https://github.com/robispider/kala-layout (submissions/ folder and docs/CHALLENGE.md)

Files: `bangla_dh_challenge.py` (the scorer), `USER_GUIDE.md`,
`A-reference.json` and `D-reference.json` (the layouts to beat, as example
files). Data `bangla-dh-challenge-v1`, SHA-256 `2388d17bd9f375763eff19eac4dc2d4397d62c1f28d574d2597d414febb55b0a`.
