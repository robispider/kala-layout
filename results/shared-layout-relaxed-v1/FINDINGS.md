# Revised-limit joint search: findings

Completed **100 million annealing proposals on 28 workers** across 500 seed runs, plus local search. The main run took approximately **10.6 minutes** from its frozen plan to final manifest, including final scoring. The retained proposal pool contains **3,371 distinct assignments**. Full-score evaluation examined **65 jointly eligible shared maps**; the final bounded score frontier contains **two alternatives**.

The requested limits are +0.75% modeled J1 effort and +7.5% within-word SF different-key distance, separately against the original same-mode layouts. Cross-space movement is a separate scored component with no new hard cap. Frozen Balance v1 retains its original stricter eligibility. Its score expression, aspirations, scales and calibration are reused unchanged under the separately named experimental policy.

## Qualifying alternatives

All changes below use primary training, normalized independently per source and mixed 50/50. R numbers are compared only within the same mode.

| Candidate | Mode | Effort change | Within-word distance change | Cross-space distance change | Experimental R |
| --- | --- | ---: | ---: | ---: | ---: |
| shared-65cdcd9b9364f827 | Goti | +0.708% | +6.578% | +30.499% | 0.795110 |
| shared-65cdcd9b9364f827 | Jhor | +0.460% | +5.432% | +10.227% | 0.476769 |
| shared-bd53cdb670b32e32 | Goti | +0.720% | +7.166% | +30.498% | 0.816328 |
| shared-bd53cdb670b32e32 | Jhor | +0.456% | +5.433% | +10.296% | 0.470757 |

The earlier shared candidate remains the Goti-score endpoint and has lower Goti within-word movement than the new alternative. The new arrangement makes a small Jhor R improvement while worsening Goti R. Neither dominates the other across the two mode scores. Qualifying under caps does not establish superior typing comfort or speed. Neither alternative meets the original stricter Balance v1 eligibility in both modes.

## Existing held-out diagnostic means

The three already examined benchmarks have equal weight here. They were scored after the training selection was frozen and did not select these alternatives.

| Candidate | Goti held-out J1 | Jhor held-out J1 |
| --- | ---: | ---: |
| shared-65cdcd9b9364f827 | 1.854916 | 1.808578 |
| shared-bd53cdb670b32e32 | 1.855063 | 1.808499 |

The best retained effort-only comparison has a worst-mode effort increase of 0.6402%, but its within-word movement increases exceed 30% in both modes. It therefore fails this experiment's movement cap.

## Shared key maps

Both modes use identical physical positions; only their original vowel-entry rules differ. Shift is shown above base. Layout JSONs are research assignments, not app imports.

### shared-65cdcd9b9364f827

| Layer | Q | W | E | R | T | Y | U | I | O | P |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| shift | ঢ় | ৌ | ৃ | ঠ | ৎ | ঘ | ড | ং | ণ | ঙ |
| base | ী | হ | ু | য | ট | চ | স | প | ব | দ |

| Layer | A | S | D | F | G | H | J | K | L |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| shift | ঁ | ূ | অ | ষ | ঢ | ফ | ছ | ভ | থ |
| base | ি | ্ | া | র | জ | শ | ক | ে | ন |

| Layer | Z | X | C | V | B | N | M |
| --- | --- | --- | --- | --- | --- | --- | --- |
| shift | ঃ | ৈ | ড় | ঞ | ঝ | খ | ধ |
| base | । | ো | ল | ম | গ | য় | ত |

### shared-bd53cdb670b32e32

| Layer | Q | W | E | R | T | Y | U | I | O | P |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| shift | ঢ় | ৈ | ৃ | ঠ | ৎ | ঘ | ড | ং | ণ | ঙ |
| base | ী | হ | ু | য | ট | চ | স | প | ব | দ |

| Layer | A | S | D | F | G | H | J | K | L |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| shift | ঁ | ূ | অ | ষ | ঢ | ফ | ছ | ভ | থ |
| base | ি | ্ | া | র | জ | শ | ক | ে | ন |

| Layer | Z | X | C | V | B | N | M |
| --- | --- | --- | --- | --- | --- | --- | --- |
| shift | ঃ | ৌ | ড় | ঞ | ঝ | খ | ধ |
| base | । | ো | ল | ম | গ | য় | ত |

The two alternatives differ in 2 symbol assignments, with 2 physical-key changes.

## Validation and scope

All 273 repository tests passed; all eight official reproduction groups matched. Every saved manifest input/output/protected hash was independently checked after completion. Exact official challenge J1 agrees under both modes, and count-based mechanics agree with search scores. Earlier published artifacts and strict-run checkpoints remain preserved. The strict interrupted 100-million run is not counted as a completed result.

This is a finite best-found experiment with bounded archives. The relaxed limits were chosen after examining v1; these results are exploratory and do not transfer any earlier optimality certificate. No application setting, published layout, challenge score or website number was changed.
