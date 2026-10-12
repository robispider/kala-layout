# Mixed-corpus search: styles A and D on Wikipedia + news

Owner request of 10 October 2026: styles A and D go to typing tests with people, searched on Wikipedia and news text together (D4 changed from Wikipedia only). Command:

```bash
bangla-dh mix-optimize --styles A D --seeds 512 --workers 32
```

Machine-readable record: [mix-search.json](mix-search.json); every run with its layout: [search/](search/); hashes of every input and output: [run-manifest.json](run-manifest.json). Code: `src/bangla_dh/mix.py`. This report was written from those files.

**Objective.** J1 as in Phase 3 (model-optimal ANSI grid, D3 default; middle–index benefit kept, D6 default) on the mix 0.5 × bnwiki/train + 0.5 × newspaper/train. Each text gets its weight, not its size (newspaper/train is 1.8 × bnwiki/train), so J_mix = 0.5 J_wiki + 0.5 J_news exactly. bard-novel was not searched and serves as an unseen news check. Every layout below is **best found** (RESEARCH_SPEC section 14). Phase 4 certificates apply to the Phase 3 layouts, not to these.

**Search per style.** 512 runs of the Phase 3 search (annealing 1,000,000 steps, steepest descent, 1,000 iterations of iterated local search; seeds 20261101–20261612, the first from the greedy layout), plus iterated local search (5,000 iterations, strengths 2–6, 4–10, 8–16) from the Phase 3 and news-trained best layouts, plus the same from the final best. 1,793 s on 32 processes.

Check: the search objective equals the weighted table scorer on the training splits for every layout scored: PASS.

## 1. Summary

| Style | Best mixed J1 | Search runs reaching it | Distinct best layouts | Next distinct layout | Polish from Phase 3 / news layouts | Confirmation |
| --- | --- | --- | --- | --- | --- | --- |
| A | 1.849686 | 36 / 512 | 1 | +0.0009 % (7 Shift labels moved) | all 6 reach the same layout | no improvement |
| D | 1.808796 | 24 / 512 | 1 | +0.29 % (34 labels moved) | all 6 reach the same layout | no improvement |

Run spread: A median +0.26 %, worst +0.65 %; D median +0.46 %, worst +0.66 % over the best.

## 2. Held-out J1 of each layout

| Style | Layout | bnwiki/heldout | newspaper/heldout | bard-novel/heldout (unseen) | Mixed J1 (train) |
| --- | --- | --- | --- | --- | --- |
| A | **mixed** | 1.8689 | 1.8300 | 1.8308 | **1.849686** |
| A | Phase 3 (Wikipedia) | 1.8675 | 1.8342 | 1.8348 | 1.850990 |
| A | cross-check (newspaper) | 1.8801 | 1.8252 | 1.8256 | 1.852781 |
| D | **mixed** | 1.8348 | 1.7822 | 1.7830 | **1.808796** |
| D | Phase 3 (Wikipedia) | 1.8343 | 1.7847 | 1.7854 | 1.809815 |
| D | cross-check (newspaper) | 1.8391 | 1.7803 | 1.7812 | 1.809924 |

The mixed layout costs at most 0.08 % over the Wikipedia layout on Wikipedia and 0.26 % over the news layout on news (D: 0.03 % and 0.11 %).

## 3. Base layer

All 1,024 runs agree on 24 base letters: । ক গ জ ট ত দ ন প ব ম য য় র ল শ স হ ◌া ◌ি ◌ু ◌ে ◌ো ◌্. The last two base slots go to two of ◌ী, চ, ছ (each about 0.7–1.0 % of keystrokes; চ ranks 26th on Wikipedia, ছ 25th on news):

| Style | Best layout | Runs with another base set |
| --- | --- | --- |
| A | ◌ী and ছ | ◌ী → চ: 216; ছ → চ: 41 |
| D | ◌ী and চ | ◌ী → ছ: 446; চ → ছ: 22 |

Against the earlier layouts:

* **D:** the base layer is identical to Phase 3 (26 of 26 on the same keys); 6 Shift labels move (ঠ ধ ফ ড় ড খ). Against the news layout, চ and ছ swap layers and 15 Shift labels move.
* **A:** 3 base changes against Phase 3 (◌ী and । swap T and G; ছ replaces চ on B, চ goes to Shift J) and 12 other Shift moves; against the news layout 16 base letters differ (that layout is a different arrangement).

## 4. Near-ties

* A has a twin 0.0009 % worse that differs only on the Shift layer (ঠ ষ ড় ড ◌ং ভ ধ), and two layouts about 0.03 % worse with 4 or 1 base changes. The base layer of A is settled, its Shift layer has free choices within the model's resolution.
* D has no near-tie: the next distinct layout is 0.29 % worse and moves 34 labels, 13 of them on the base layer.

## 5. Best layouts

### Style A (mixed)

| | Q | W | E | R | T | Y | U | I | O | P |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Shift | ◌ঃ | ঝ | ঠ | ◌ৈ | ◌ৌ | ঘ | ষ | ড় | ◌ঁ | ঙ |
| base | গ | দ | ল | ◌ো | ◌ী | শ | স | য় | প | হ |

| | A | S | D | F | G | H | J | K | L |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Shift | ফ | ণ | খ | অ | ঢ় | ড | চ | ◌ং | ভ |
| base | ব | ন | র | ◌া | । | জ | ক | ◌্ | ◌ে |

| | Z | X | C | V | B | N | M |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Shift | ঢ | ৎ | ◌ূ | ◌ৃ | ঞ | ধ | থ |
| base | ট | ম | ◌ি | ◌ু | ছ | য | ত |

### Style D (mixed)

| | Q | W | E | R | T | Y | U | I | O | P |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Shift | ঢ | ঙ | ঠ | ◌ৈ | ◌ঃ | ঘ | ধ | ◌ং | ণ | ◌ঁ |
| base | ট | দ | ল | ◌ো | । | শ | স | প | য | গ |

| | A | S | D | F | G | H | J | K | L |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Shift | ফ | ড় | ষ | ◌ূ | ঢ় | ড | ছ | ভ | অ |
| base | ব | ন | র | ◌া | ◌ী | জ | ক | ◌ে | ◌ি |

| | Z | X | C | V | B | N | M |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Shift | ৎ | ঞ | ◌ৃ | ◌ৌ | ঝ | খ | থ |
| base | হ | ম | ◌্ | ◌ু | চ | য় | ত |

## 6. What is and is not established

* Both layouts are **best found** on the mixed objective; many independent runs and every polish run reach the same layout, which is evidence the search is not stuck, not a proof.
* Not re-certified: the Phase 4 bounds and scoped proofs were computed for the Phase 3 (Wikipedia) layouts. D's mixed layout shares its whole base layer with the certified Phase 3 D layout.
* The weights 0.5 / 0.5 are a choice; other weights can be run with `--weights`.
