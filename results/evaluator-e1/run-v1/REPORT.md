# Experimental evaluation season e1

This is an additional diagnostic track. The published layouts, J0/J1, challenge and website are unchanged.

## Evidence decision

**Full-layout preference scoring and comfort-based candidate selection are withheld.**
The source supplies 288 predicted pair values, covering same-hand pairs in two 12-key blocks. Shift/chords, cross-hand pairs and central keys lack support. Right-hand values use a symmetry assumption. No rule-generated values were added.

| Evidence check | Result |
| --- | --- |
| Pinned source files and lookup benchmark | PASS |
| Independent reproduction of held-out preference prediction | Not performed; no verified prediction artifact supplied |
| Bangla human validation | Not performed |
| Full-layout coverage / admission | FAIL; partial diagnostic only |

The lookup benchmark verifies calculations, not predictive validity. Source per-pair uncertainties do not establish a layout confidence interval.

Sources: [distributed pair table](https://raw.githubusercontent.com/binarybottle/keyboard_layout_scorers/179e1c08b220ae1b02f6c425a7d1cbd1150c1db2/prep/input/comfort_keypair_scores_24keys.csv), [learning repository](https://github.com/binarybottle/typing_preferences_to_comfort_scores), [research paper](https://doi.org/10.1080/10447318.2026.2665409).

## Stage 1: published layouts

Canonical baseline encoding minimizes presses with frozen traditional-grid effort tie-breaking. The same encoded actions are scored under both fingering scenarios. Traditional-grid J0/J1 agree with recorded historical baseline scores; model-optimal baseline scores may differ from published scores because their encoding policy is held fixed here.

J1 is modeled effort per counted unit including space. Pair support is the share of non-space action pairs matching source keys, base layers and traditional finger assignments. The conditional preference mean describes a different supported subset for each layout; **do not compare these means as complete comfort scores**.

### traditional fingering

| Layout | Text | J1 | Source pair support | Conditional preference (partial) | Escaped units |
| --- | --- | --- | --- | --- | --- |
| Bornona | bard-novel/heldout | 2.669473 | 18.8% | -0.669645 | 0.02% |
| Kala Goti | bard-novel/heldout | 1.965560 | 34.0% | -0.662037 | 0.02% |
| Kala Jhor | bard-novel/heldout | 1.951118 | 33.3% | -0.668564 | 0.02% |
| Munir Optima (uni) | bard-novel/heldout | 2.588542 | 14.0% | -0.768604 | 0.05% |
| National (Jatiya) | bard-novel/heldout | 2.855387 | 12.3% | -0.749994 | 0.07% |
| Probhat | bard-novel/heldout | 2.613367 | 19.2% | -0.801751 | 0.02% |
| UniJoy | bard-novel/heldout | 2.844738 | 13.4% | -0.778460 | 0.01% |
| Windows Default | bard-novel/heldout | 2.212036 | 15.7% | -0.761069 | 2.38% |
| Bornona | bnwiki/heldout | 2.714494 | 18.2% | -0.671105 | 0.01% |
| Kala Goti | bnwiki/heldout | 2.028508 | 32.7% | -0.664276 | 0.02% |
| Kala Jhor | bnwiki/heldout | 2.029837 | 32.0% | -0.682677 | 0.02% |
| Munir Optima (uni) | bnwiki/heldout | 2.592096 | 14.5% | -0.768529 | 0.17% |
| National (Jatiya) | bnwiki/heldout | 2.891292 | 12.3% | -0.763460 | 0.07% |
| Probhat | bnwiki/heldout | 2.682925 | 19.5% | -0.799482 | 0.01% |
| UniJoy | bnwiki/heldout | 2.834521 | 13.3% | -0.797106 | 0.01% |
| Windows Default | bnwiki/heldout | 2.209895 | 14.3% | -0.748409 | 2.95% |
| Bornona | newspaper/heldout | 2.669556 | 18.7% | -0.672011 | 0.02% |
| Kala Goti | newspaper/heldout | 1.963833 | 33.9% | -0.660857 | 0.03% |
| Kala Jhor | newspaper/heldout | 1.948095 | 33.1% | -0.665982 | 0.03% |
| Munir Optima (uni) | newspaper/heldout | 2.578256 | 13.8% | -0.769073 | 0.07% |
| National (Jatiya) | newspaper/heldout | 2.850310 | 12.2% | -0.755830 | 0.07% |
| Probhat | newspaper/heldout | 2.616031 | 19.0% | -0.800963 | 0.02% |
| UniJoy | newspaper/heldout | 2.839142 | 13.3% | -0.781486 | 0.02% |
| Windows Default | newspaper/heldout | 2.209591 | 15.7% | -0.762359 | 2.39% |

### model-optimal fingering

| Layout | Text | J1 | Source pair support | Conditional preference (partial) | Escaped units |
| --- | --- | --- | --- | --- | --- |
| Bornona | bard-novel/heldout | 2.596689 | 17.4% | -0.637140 | 0.02% |
| Kala Goti | bard-novel/heldout | 1.830752 | 24.8% | -0.550356 | 0.02% |
| Kala Jhor | bard-novel/heldout | 1.783031 | 23.4% | -0.540496 | 0.02% |
| Munir Optima (uni) | bard-novel/heldout | 2.594219 | 10.8% | -0.684805 | 0.05% |
| National (Jatiya) | bard-novel/heldout | 2.903110 | 6.6% | -0.623473 | 0.07% |
| Probhat | bard-novel/heldout | 2.536180 | 16.6% | -0.758516 | 0.02% |
| UniJoy | bard-novel/heldout | 2.810624 | 8.5% | -0.696417 | 0.01% |
| Windows Default | bard-novel/heldout | 2.159434 | 11.9% | -0.685379 | 2.38% |
| Bornona | bnwiki/heldout | 2.659600 | 16.8% | -0.634805 | 0.01% |
| Kala Goti | bnwiki/heldout | 1.868918 | 23.6% | -0.548706 | 0.02% |
| Kala Jhor | bnwiki/heldout | 1.834823 | 21.2% | -0.537095 | 0.02% |
| Munir Optima (uni) | bnwiki/heldout | 2.593318 | 10.9% | -0.667617 | 0.17% |
| National (Jatiya) | bnwiki/heldout | 2.937549 | 6.4% | -0.642815 | 0.07% |
| Probhat | bnwiki/heldout | 2.608252 | 17.2% | -0.758580 | 0.01% |
| UniJoy | bnwiki/heldout | 2.808428 | 7.9% | -0.702934 | 0.01% |
| Windows Default | bnwiki/heldout | 2.147984 | 11.0% | -0.676285 | 2.95% |
| Bornona | newspaper/heldout | 2.598949 | 17.2% | -0.637543 | 0.02% |
| Kala Goti | newspaper/heldout | 1.830018 | 24.7% | -0.549494 | 0.03% |
| Kala Jhor | newspaper/heldout | 1.782223 | 23.3% | -0.538401 | 0.03% |
| Munir Optima (uni) | newspaper/heldout | 2.585003 | 10.7% | -0.685512 | 0.07% |
| National (Jatiya) | newspaper/heldout | 2.896098 | 6.4% | -0.629066 | 0.07% |
| Probhat | newspaper/heldout | 2.539983 | 16.4% | -0.757677 | 0.02% |
| UniJoy | newspaper/heldout | 2.805607 | 8.4% | -0.698774 | 0.02% |
| Windows Default | newspaper/heldout | 2.155563 | 11.9% | -0.686494 | 2.39% |

## Stage 2: retained candidates

101 distinct A/D maps were evaluated. 1024 stored search outcomes were included; no new search ran.

Every map is checked against the frozen inventory and 52-slot bijection, with fixed digits/punctuation retained. Training reference scores and descriptive frontier memberships are in candidates.json. The frontier uses existing J1, existing Shift effort M per text unit and same-finger/different-key count per text unit under model-optimal fingering. It is a diagnostic trade-off set, not a comfort recommendation. The preference diagnostic is excluded from rankings, frontiers and selection.

No comfort shortlist or replacement layout was selected. The source evidence/coverage gate did not admit a complete preference evaluator. Candidate maps and corpus comparisons remain available for examination. These candidates were originally found under J1, so they are not a sample of the whole layout space.

## Checks and reproducibility

- pinned_source_lookup: PASS
- candidate_inventory_and_bijection: PASS
- action_reference_matches_existing_scorer: PASS
- all_baseline_NFC_round_trips: PASS
- baseline_traditional_reference_matches_history: PASS
- original_files_byte_identical: PASS

The independent lookup benchmark, unit tests and original score agreement check software fidelity. None validates human comfort or speed. Published held-out texts are known benchmarks; they were not used to choose a new comfort winner.

Derived numeric reports contain no corpus text. Input/output hashes, parameters, encoding policies and code revision are in run-manifest.json.

## Next research requirement

Obtain independently verifiable held-out preference predictions and data for central keys, cross-hand transitions and modifiers. Validate relevant conditions with Bangla typists before promoting this diagnostic to a whole-layout evaluator.
