# Dvorak-7 and Engram mechanics: evaluation season e2

Eight fixed layouts and all retained A/D maps are evaluated with source-derived upstream scoring code. Higher mechanics values are better within the stated scope. J1 is lower-is-better modeled effort. These results describe modeled key movement, not measured speed or comfort.

## What the comparison adds

Under the unmodified upstream traditional fingering, Goti has higher Dvorak-7 and Engram avg4 credit than Jhor even after allowing the full range for missing pairs, while Jhor has lower J1. Under the adapted model-optimal fingering, their pair-model bounds overlap: neither pair model conclusively orders them. Goti has higher Engram trigram-order credit in both scenarios. Windows Default has higher trigram-order credit than both Kala maps, but escapes about 2.6% of text units and the order score ignores Shift effort. Thus the new criteria expose genuine modeled trade-offs and dependence on fingering; they do not produce an overall comfort winner.

## What was verified

Pinned upstream commit: `179e1c08b220ae1b02f6c425a7d1cbd1150c1db2` (Arno Klein, MIT). The unmodified scoring bodies match the original functions for 1,764 pairs and 74,088 triples. All 49,152 distributed table rows match (maximum absolute error 1.11e-16). Source snapshots, license and SHA-256 hashes are under data/evaluators/mechanics-v1. This proves implementation fidelity, not the ergonomic assumptions.

Dvorak-7 is the source's seven-criterion sum divided by seven. Engram avg4 is exactly the generator's mean of row separation, same-row movement, same-finger movement and outside reach. The upstream table unifier can average additional columns under the same avg4 name; we deliberately use the explicit generator formula. Engram key preferences, scissor and half-scissor are reported as components; Engram trigram order is a separate diagnostic. No new combined comfort total is invented.

## Reading the components

| Component | What earns credit in the pinned code |
| --- | --- |
| Dvorak distribution | Different hands: 1; different fingers on one hand: 0.5; same finger: 0 |
| Dvorak strength | Fraction of the two keys assigned to index/middle fingers |
| Dvorak home | Fraction of the two keys on the home row |
| Dvorak row span | Opposite hands or same row: 1; adjacent rows on one hand: 0.5; larger separation: 0 |
| Dvorak columns | Fraction of keys inside the source's eight finger columns |
| Dvorak remote | Source rule for row, finger adjacency and strong-finger pairs; same-row check comes first, so same-row repeats receive 1 here |
| Dvorak inward | Opposite hands or a sequence toward the thumb: 1; same finger or outward sequence: 0 |
| Engram row separation | Opposite hands or same row: 1; adjacent rows: 0.588; larger separation: 0 |
| Engram same row | Opposite hands: 1; same finger: 0; within a row, outward credit is multiplied by 0.779 and remote columns by 0.750; different rows/fingers: 0.5 |
| Engram same finger | Different hands/fingers: 1; same finger, including repeated keys: 0 |
| Engram outside | No outside keys: 1; one: 0.846; two: 0.716 |
| Engram key preference | Source tier values averaged over the two keys; not included in avg4 |
| Engram scissor / half-scissor | Zero for the source's adjacent-column hurdle / reach condition, otherwise 1; not included in avg4 |
| Engram order | Source-defined hand changes or monotonic three-finger sequences: 1; mixed/repeated-finger cases: 0 |

J1 adds no pair penalty for repeating the identical action; Engram same-finger gives repeated physical keys zero credit. The pair mean also measures credit per transition, while J1 measures effort per text unit and prices extra presses and Shift. These different definitions help explain why the models can favor Goti's movement patterns while Jhor retains lower J1. The exact numerical component differences and important transitions are shown below.

## Scope and coverage

Base and Shift actions are projected to their physical key. Shift presses, chords, timing and modifier transitions are excluded from these mechanics scores. Shift use remains a separate diagnostic. Pairs are directed, include repeated keys, and exclude space transitions. Triples are counted within tokens and never cross a space, escape, paragraph or document boundary. Existing unigram/pair counts are independently reproduced during triple extraction; token tables are checked against their pinned hashes.

The source functions define number-row keys although the distributed tables cover only 32 main keys. We use those unchanged number-row rules, checked against the original functions. Unsupported physical keys (such as minus) and AltGr retain their probability mass. Each interval assigns unknown events the possible range 0 to 1 using the full non-space event denominator. These are missing-coverage bounds, not statistical confidence intervals. Escape shares are shown separately: untyped text is outside the mechanics domain and can bias comparisons. There is no whole-typing comfort ranking.

Canonical baseline encoding minimizes presses with traditional-grid effort tie-breaking, held fixed across scorers. Traditional J0/J1 match historical results. The primary scenario preserves upstream traditional ANSI fingering. The model-optimal scenario changes finger/hand assignments to the frozen Kala grid, retains physical row/column coordinates and the source inside/outside key set, and reassigns inside keys to those fingers. It is an explicit adaptation, not an upstream-verified ergonomic model. Its canonical-baseline J1 can differ from the published board's independently chosen encoding/fingering.

## traditional fingering: equal-weight held-out averages

| Layout | J1 | Dvorak-7 bounds | Engram avg4 bounds | Engram order bounds | Pair coverage | Escaped text units |
| --- | --- | --- | --- | --- | --- | --- |
| Kala Jhor | 1.976350 | 0.759194–0.763823 | 0.876980–0.881609 | 0.678379–0.686651 | 99.537% | 0.024% |
| Kala Goti | 1.985967 | 0.769583–0.774007 | 0.889982–0.894406 | 0.741212–0.749220 | 99.558% | 0.021% |
| Windows Default | 2.210507 | 0.759952–0.779309 | 0.873047–0.892405 | 0.786608–0.818445 | 98.064% | 2.572% |
| Munir Optima (uni) | 2.586298 | 0.693853–0.699321 | 0.822285–0.827753 | 0.624074–0.630554 | 99.453% | 0.097% |
| Probhat | 2.637441 | 0.647842–0.682642 | 0.818740–0.853540 | 0.671286–0.721894 | 96.520% | 0.016% |
| Bornona | 2.684508 | 0.682367–0.687310 | 0.823476–0.828420 | 0.635725–0.644620 | 99.506% | 0.017% |
| UniJoy | 2.839467 | 0.711979–0.716834 | 0.814766–0.819621 | 0.589398–0.598203 | 99.514% | 0.013% |
| National (Jatiya) | 2.865663 | 0.700064–0.704862 | 0.806023–0.810821 | 0.561324–0.569839 | 99.520% | 0.070% |

Each corpus contributes one third: Wikipedia held-out, newspaper held-out and BARD novel held-out. Scores for each source are in scores.csv and scores.json.gz; averages do not replace the source-specific comparisons.

### Agreement and reversals

- dvorak7: 25/28 pairwise orders are separated by coverage bounds; 18 agree with J1 and 7 reverse it. Unseparated intervals remain unresolved.
  - National (Jatiya) has higher dvorak7; Bornona has lower J1 (Bornona minus National (Jatiya): -0.022496 to -0.012754).
  - UniJoy has higher dvorak7; Bornona has lower J1 (Bornona minus UniJoy: -0.034468 to -0.024669).
  - Kala Goti has higher dvorak7; Kala Jhor has lower J1 (Kala Goti minus Kala Jhor: +0.005760 to +0.014813).
  - National (Jatiya) has higher dvorak7; Munir Optima (uni) has lower J1 (Munir Optima (uni) minus National (Jatiya): -0.011009 to -0.000743).
  - UniJoy has higher dvorak7; Munir Optima (uni) has lower J1 (Munir Optima (uni) minus UniJoy: -0.022981 to -0.012658).
  - National (Jatiya) has higher dvorak7; Probhat has lower J1 (National (Jatiya) minus Probhat: +0.017422 to +0.057021).
  - UniJoy has higher dvorak7; Probhat has lower J1 (Probhat minus UniJoy: -0.068993 to -0.029337).
- engram_avg4: 22/28 pairwise orders are separated by coverage bounds; 21 agree with J1 and 1 reverse it. Unseparated intervals remain unresolved.
  - Kala Goti has higher engram_avg4; Kala Jhor has lower J1 (Kala Goti minus Kala Jhor: +0.008373 to +0.017427).
- engram_order: 27/28 pairwise orders are separated by coverage bounds; 22 agree with J1 and 5 reverse it. Unseparated intervals remain unresolved.
  - Bornona has higher engram_order; Munir Optima (uni) has lower J1 (Bornona minus Munir Optima (uni): +0.005171 to +0.020546).
  - Kala Goti has higher engram_order; Kala Jhor has lower J1 (Kala Goti minus Kala Jhor: +0.054561 to +0.070841).
  - Windows Default has higher engram_order; Kala Goti has lower J1 (Kala Goti minus Windows Default: -0.077233 to -0.037388).
  - Windows Default has higher engram_order; Kala Jhor has lower J1 (Kala Jhor minus Windows Default: -0.140066 to -0.099957).
  - Probhat has higher engram_order; Munir Optima (uni) has lower J1 (Munir Optima (uni) minus Probhat: -0.097820 to -0.040732).

### Why Jhor and Goti differ

Component intervals below are equal-weight means; higher means the source rule awards more credit.

| Criterion | Jhor bounds | Goti bounds |
| --- | --- | --- |
| dvorak7_columns | 0.896958–0.901588 | 0.903312–0.907736 |
| dvorak7_distribution | 0.720334–0.724964 | 0.737848–0.742272 |
| dvorak7_home | 0.546783–0.551413 | 0.567557–0.571981 |
| dvorak7_inward | 0.722062–0.726691 | 0.738985–0.743409 |
| dvorak7_remote | 0.896326–0.900956 | 0.906735–0.911159 |
| dvorak7_strength | 0.703149–0.707779 | 0.695824–0.700248 |
| dvorak7_vspan | 0.828745–0.833374 | 0.836822–0.841246 |
| engram_half_scissor | 0.922989–0.927618 | 0.893578–0.898002 |
| engram_key_preference | 0.598344–0.602974 | 0.609261–0.613685 |
| engram_outside | 0.965480–0.970110 | 0.967485–0.971909 |
| engram_row_separation | 0.850838–0.855467 | 0.858357–0.862780 |
| engram_same_finger | 0.923300–0.927929 | 0.949710–0.954134 |
| engram_same_row | 0.768301–0.772930 | 0.784378–0.788802 |
| engram_scissor | 0.980189–0.984819 | 0.984605–0.989029 |

### Frequent transitions that lose credit

Wikipedia held-out examples show the largest frequency-weighted deficits from the maximum value 1. Each contribution is count × (1 − pair score) / all non-space pairs; it is explanatory accounting, not a measured discomfort estimate. Full saved top contributions and unsupported pairs are in scores.json.gz.

| Layout | Model | Transition | Count | Deficit contribution |
| --- | --- | --- | --- | --- |
| Kala Goti | dvorak7 | F/base → D/base | 699072 | 0.004573 |
| Kala Goti | dvorak7 | K/base → N/base | 506469 | 0.004418 |
| Kala Goti | dvorak7 | K/base → L/base | 504408 | 0.004400 |
| Kala Goti | engram_avg4 | D/base → C/base | 241813 | 0.004452 |
| Kala Goti | engram_avg4 | C/base → E/base | 191020 | 0.004374 |
| Kala Goti | engram_avg4 | K/base → N/base | 506469 | 0.004121 |
| Kala Jhor | dvorak7 | C/base → D/base | 572152 | 0.010422 |
| Kala Jhor | dvorak7 | D/base → C/base | 386390 | 0.007039 |
| Kala Jhor | dvorak7 | S/base → C/base | 358359 | 0.004896 |
| Kala Jhor | engram_avg4 | C/base → D/base | 572152 | 0.010998 |
| Kala Jhor | engram_avg4 | D/base → C/base | 386390 | 0.007427 |
| Kala Jhor | engram_avg4 | S/base → C/base | 358359 | 0.002605 |

## model-optimal fingering: equal-weight held-out averages

| Layout | J1 | Dvorak-7 bounds | Engram avg4 bounds | Engram order bounds | Pair coverage | Escaped text units |
| --- | --- | --- | --- | --- | --- | --- |
| Kala Jhor | 1.800026 | 0.778331–0.782960 | 0.893861–0.898490 | 0.747832–0.756104 | 99.537% | 0.024% |
| Kala Goti | 1.843229 | 0.781226–0.785650 | 0.896832–0.901255 | 0.761458–0.769466 | 99.558% | 0.021% |
| Windows Default | 2.154327 | 0.761988–0.781345 | 0.875103–0.894460 | 0.789681–0.821518 | 98.064% | 2.572% |
| Probhat | 2.561472 | 0.646987–0.681787 | 0.819497–0.854297 | 0.692782–0.743389 | 96.520% | 0.016% |
| Munir Optima (uni) | 2.590847 | 0.690848–0.696316 | 0.808623–0.814091 | 0.573627–0.580107 | 99.453% | 0.097% |
| Bornona | 2.618413 | 0.688388–0.693331 | 0.827930–0.832874 | 0.656942–0.665837 | 99.506% | 0.017% |
| UniJoy | 2.808219 | 0.724888–0.729743 | 0.809718–0.814573 | 0.602206–0.611011 | 99.514% | 0.013% |
| National (Jatiya) | 2.912252 | 0.695163–0.699961 | 0.779703–0.784501 | 0.525972–0.534487 | 99.520% | 0.070% |

Each corpus contributes one third: Wikipedia held-out, newspaper held-out and BARD novel held-out. Scores for each source are in scores.csv and scores.json.gz; averages do not replace the source-specific comparisons.

### Agreement and reversals

- dvorak7: 23/28 pairwise orders are separated by coverage bounds; 16 agree with J1 and 7 reverse it. Unseparated intervals remain unresolved.
  - National (Jatiya) has higher dvorak7; Bornona has lower J1 (Bornona minus National (Jatiya): -0.011573 to -0.001832).
  - Bornona has higher dvorak7; Probhat has lower J1 (Bornona minus Probhat: +0.006600 to +0.046344).
  - UniJoy has higher dvorak7; Bornona has lower J1 (Bornona minus UniJoy: -0.041355 to -0.031557).
  - Munir Optima (uni) has higher dvorak7; Probhat has lower J1 (Munir Optima (uni) minus Probhat: +0.009061 to +0.049329).
  - UniJoy has higher dvorak7; Munir Optima (uni) has lower J1 (Munir Optima (uni) minus UniJoy: -0.038895 to -0.028571).
  - National (Jatiya) has higher dvorak7; Probhat has lower J1 (National (Jatiya) minus Probhat: +0.013376 to +0.052974).
  - UniJoy has higher dvorak7; Probhat has lower J1 (Probhat minus UniJoy: -0.082756 to -0.043100).
- engram_avg4: 24/28 pairwise orders are separated by coverage bounds; 23 agree with J1 and 1 reverse it. Unseparated intervals remain unresolved.
  - Bornona has higher engram_avg4; Munir Optima (uni) has lower J1 (Bornona minus Munir Optima (uni): +0.013840 to +0.024251).
- engram_order: 28/28 pairwise orders are separated by coverage bounds; 23 agree with J1 and 5 reverse it. Unseparated intervals remain unresolved.
  - Bornona has higher engram_order; Munir Optima (uni) has lower J1 (Bornona minus Munir Optima (uni): +0.076835 to +0.092210).
  - Kala Goti has higher engram_order; Kala Jhor has lower J1 (Kala Goti minus Kala Jhor: +0.005354 to +0.021634).
  - Windows Default has higher engram_order; Kala Goti has lower J1 (Kala Goti minus Windows Default: -0.060060 to -0.020215).
  - Windows Default has higher engram_order; Kala Jhor has lower J1 (Kala Jhor minus Windows Default: -0.073686 to -0.033577).
  - UniJoy has higher engram_order; Munir Optima (uni) has lower J1 (Munir Optima (uni) minus UniJoy: -0.037385 to -0.022099).

### Why Jhor and Goti differ

Component intervals below are equal-weight means; higher means the source rule awards more credit.

| Criterion | Jhor bounds | Goti bounds |
| --- | --- | --- |
| dvorak7_columns | 0.896958–0.901588 | 0.903312–0.907736 |
| dvorak7_distribution | 0.744572–0.749202 | 0.746735–0.751159 |
| dvorak7_home | 0.546783–0.551413 | 0.567557–0.571981 |
| dvorak7_inward | 0.741891–0.746521 | 0.746281–0.750705 |
| dvorak7_remote | 0.955003–0.959633 | 0.949000–0.953424 |
| dvorak7_strength | 0.732217–0.736847 | 0.722994–0.727418 |
| dvorak7_vspan | 0.830889–0.835519 | 0.832702–0.837126 |
| engram_half_scissor | 0.925500–0.930130 | 0.896226–0.900650 |
| engram_key_preference | 0.598344–0.602974 | 0.609261–0.613685 |
| engram_outside | 0.965480–0.970110 | 0.967485–0.971909 |
| engram_row_separation | 0.852864–0.857493 | 0.854973–0.859397 |
| engram_same_finger | 0.965185–0.969814 | 0.972061–0.976485 |
| engram_same_row | 0.791913–0.796543 | 0.792807–0.797231 |
| engram_scissor | 0.981445–0.986074 | 0.985782–0.990206 |

### Frequent transitions that lose credit

Wikipedia held-out examples show the largest frequency-weighted deficits from the maximum value 1. Each contribution is count × (1 − pair score) / all non-space pairs; it is explanatory accounting, not a measured discomfort estimate. Full saved top contributions and unsupported pairs are in scores.json.gz.

| Layout | Model | Transition | Count | Deficit contribution |
| --- | --- | --- | --- | --- |
| Kala Goti | dvorak7 | F/base → D/base | 699072 | 0.004573 |
| Kala Goti | dvorak7 | K/base → N/base | 506469 | 0.004418 |
| Kala Goti | dvorak7 | K/base → L/base | 504408 | 0.004400 |
| Kala Goti | engram_avg4 | K/base → N/base | 506469 | 0.004121 |
| Kala Goti | engram_avg4 | C/base → E/base | 191020 | 0.002187 |
| Kala Goti | engram_avg4 | K/base → M/base | 290879 | 0.002025 |
| Kala Jhor | dvorak7 | C/base → D/base | 572152 | 0.006514 |
| Kala Jhor | dvorak7 | F/base → D/base | 699046 | 0.004775 |
| Kala Jhor | dvorak7 | M/base → L/base | 254323 | 0.003475 |
| Kala Jhor | engram_avg4 | C/base → D/base | 572152 | 0.004159 |
| Kala Jhor | engram_avg4 | D/base → C/base | 386390 | 0.002808 |
| Kala Jhor | engram_avg4 | S/base → C/base | 358359 | 0.002605 |

## Every layout and every corpus

| Layout | Text | Fingering | Dvorak-7 bounds | Engram avg4 bounds | Engram order bounds |
| --- | --- | --- | --- | --- | --- |
| Kala Goti | bard-novel/heldout | model-optimal | 0.780864–0.784690 | 0.896105–0.899931 | 0.755426–0.762337 |
| Kala Goti | bard-novel/heldout | traditional | 0.770364–0.774191 | 0.890444–0.894271 | 0.740637–0.747548 |
| Kala Goti | bnwiki/heldout | model-optimal | 0.781726–0.787227 | 0.898239–0.903740 | 0.773069–0.782999 |
| Kala Goti | bnwiki/heldout | traditional | 0.767936–0.773438 | 0.889202–0.894703 | 0.743007–0.752937 |
| Kala Goti | newspaper/heldout | model-optimal | 0.781088–0.785032 | 0.896151–0.900095 | 0.755881–0.763061 |
| Kala Goti | newspaper/heldout | traditional | 0.770449–0.774393 | 0.890301–0.894245 | 0.739993–0.747174 |
| Kala Jhor | bard-novel/heldout | model-optimal | 0.779083–0.783093 | 0.893372–0.897383 | 0.743726–0.750896 |
| Kala Jhor | bard-novel/heldout | traditional | 0.760537–0.764548 | 0.877088–0.881099 | 0.677811–0.684981 |
| Kala Jhor | bnwiki/heldout | model-optimal | 0.776544–0.782288 | 0.894677–0.900421 | 0.754838–0.765031 |
| Kala Jhor | bnwiki/heldout | traditional | 0.756138–0.761882 | 0.876555–0.882299 | 0.678787–0.688980 |
| Kala Jhor | newspaper/heldout | model-optimal | 0.779365–0.783499 | 0.893533–0.897667 | 0.744931–0.752386 |
| Kala Jhor | newspaper/heldout | traditional | 0.760907–0.765041 | 0.877296–0.881430 | 0.678539–0.685993 |
| Bornona | bard-novel/heldout | model-optimal | 0.689683–0.693934 | 0.829033–0.833284 | 0.661142–0.668787 |
| Bornona | bard-novel/heldout | traditional | 0.683557–0.687808 | 0.824425–0.828676 | 0.636942–0.644587 |
| Bornona | bnwiki/heldout | model-optimal | 0.686795–0.692998 | 0.826504–0.832707 | 0.650877–0.661969 |
| Bornona | bnwiki/heldout | traditional | 0.681100–0.687303 | 0.822541–0.828744 | 0.635296–0.646387 |
| Bornona | newspaper/heldout | model-optimal | 0.688686–0.693061 | 0.828253–0.832629 | 0.658807–0.666755 |
| Bornona | newspaper/heldout | traditional | 0.682444–0.686820 | 0.823463–0.827839 | 0.634938–0.642886 |
| Munir Optima (uni) | bard-novel/heldout | model-optimal | 0.689884–0.694215 | 0.807082–0.811413 | 0.568628–0.573520 |
| Munir Optima (uni) | bard-novel/heldout | traditional | 0.693564–0.697895 | 0.821178–0.825509 | 0.621050–0.625942 |
| Munir Optima (uni) | bnwiki/heldout | model-optimal | 0.691842–0.699906 | 0.810885–0.818950 | 0.580751–0.590635 |
| Munir Optima (uni) | bnwiki/heldout | traditional | 0.693403–0.701468 | 0.823676–0.831740 | 0.628465–0.638349 |
| Munir Optima (uni) | newspaper/heldout | model-optimal | 0.690820–0.694828 | 0.807901–0.811909 | 0.571501–0.576167 |
| Munir Optima (uni) | newspaper/heldout | traditional | 0.694592–0.698600 | 0.822003–0.826010 | 0.622706–0.627372 |
| National (Jatiya) | bard-novel/heldout | model-optimal | 0.696669–0.700803 | 0.781386–0.785521 | 0.526993–0.534327 |
| National (Jatiya) | bard-novel/heldout | traditional | 0.702230–0.706364 | 0.808891–0.813025 | 0.566812–0.574147 |
| National (Jatiya) | bnwiki/heldout | model-optimal | 0.692064–0.698044 | 0.776362–0.782342 | 0.522928–0.533470 |
| National (Jatiya) | bnwiki/heldout | traditional | 0.695867–0.701847 | 0.800651–0.806631 | 0.550378–0.560920 |
| National (Jatiya) | newspaper/heldout | model-optimal | 0.696756–0.701037 | 0.781360–0.785641 | 0.527996–0.535664 |
| National (Jatiya) | newspaper/heldout | traditional | 0.702096–0.706377 | 0.808528–0.812808 | 0.566782–0.574449 |
| Probhat | bard-novel/heldout | model-optimal | 0.647412–0.682822 | 0.819481–0.854891 | 0.693754–0.744416 |
| Probhat | bard-novel/heldout | traditional | 0.647451–0.682861 | 0.817805–0.853215 | 0.670130–0.720791 |
| Probhat | bnwiki/heldout | model-optimal | 0.646380–0.679433 | 0.820096–0.853149 | 0.692049–0.741827 |
| Probhat | bnwiki/heldout | traditional | 0.648852–0.681905 | 0.820997–0.854050 | 0.673315–0.723093 |
| Probhat | newspaper/heldout | model-optimal | 0.647170–0.683107 | 0.818913–0.854850 | 0.692542–0.743925 |
| Probhat | newspaper/heldout | traditional | 0.647223–0.683160 | 0.817418–0.853356 | 0.670413–0.721796 |
| UniJoy | bard-novel/heldout | model-optimal | 0.724968–0.729095 | 0.808761–0.812887 | 0.596376–0.603846 |
| UniJoy | bard-novel/heldout | traditional | 0.711540–0.715666 | 0.813243–0.817370 | 0.583129–0.590600 |
| UniJoy | bnwiki/heldout | model-optimal | 0.724270–0.730410 | 0.811561–0.817701 | 0.612509–0.623607 |
| UniJoy | bnwiki/heldout | traditional | 0.712185–0.718325 | 0.817526–0.823666 | 0.598959–0.610057 |
| UniJoy | newspaper/heldout | model-optimal | 0.725425–0.729724 | 0.808831–0.813130 | 0.597734–0.605581 |
| UniJoy | newspaper/heldout | traditional | 0.712213–0.716512 | 0.813527–0.817826 | 0.586105–0.593952 |
| Windows Default | bard-novel/heldout | model-optimal | 0.760268–0.779158 | 0.873461–0.892351 | 0.784521–0.815810 |
| Windows Default | bard-novel/heldout | traditional | 0.758352–0.777242 | 0.871912–0.890802 | 0.784421–0.815709 |
| Windows Default | bnwiki/heldout | model-optimal | 0.765366–0.784955 | 0.878423–0.898012 | 0.799992–0.831642 |
| Windows Default | bnwiki/heldout | traditional | 0.763338–0.782927 | 0.875613–0.895202 | 0.791528–0.823178 |
| Windows Default | newspaper/heldout | model-optimal | 0.760329–0.779922 | 0.873425–0.893018 | 0.784530–0.817103 |
| Windows Default | newspaper/heldout | traditional | 0.758165–0.777759 | 0.871617–0.891210 | 0.783876–0.816449 |

## Retained search candidates

101 distinct A/D maps retain provenance for 1024 original search starts, earlier bests, polish and confirmation. All held-out mechanics are reported, including non-public maps. Candidate comparisons and diagnostic frontiers use only the existing 50/50 training mix and traditional fingering, separately by style. A map dominates only if its J1 is no higher and both pair-model lower bounds exceed or equal the other map's upper bounds, with a strict improvement in at least one dimension. Trigram order is reported but does not select candidates. No new search or replacement layout was produced.

- Style A: 69 maps; 8 on the conservative training trade-off frontier.
- Style D: 32 maps; 12 on the conservative training trade-off frontier.

These maps were found under J1; they do not establish best-found or optimal layouts under the new models. Known held-out benchmarks are used for exploratory comparison, not fresh confirmatory validation. The source rules share several characteristics with J1, so agreement is robustness to some assumptions rather than independent scientific validation. No original Phase 4 certificate transfers.

## Challenge and website use

Source-derived pair mechanics can explain reversals and component trade-offs, so they are suitable for optional challenge diagnostics. The official J1 objective, acceptance, ties, ranking and DATA_VERSION remain the published season. Challenge files need only the committed pair counts. Trigram evaluation is shown when committed style triple counts are available; it is separate from the official score. The website presents coverage bounds and scope, alongside the original diagnostic and preference limitations.

## Reproduce and verification

```powershell
$env:PYTHONPATH = "src"
python -m bangla_dh.experimental.mechanics_run --out work/evaluator-experiments/mechanics-repeat --workers 4
python -m unittest discover -s tests
```

The committed derived triple caches let the comparison rerun without corpus downloads. Use --rebuild-counts to independently recreate them from the pinned local token tables. Source refresh is explicit: python -m bangla_dh.experimental.mechanics_sources --fetch. Output directories must be new; all writers use the repository guard. Source-fidelity checks, corpus/code/output SHA-256 hashes and original-resource preservation checks are in source-fidelity.json and run-manifest.json.
