# Pinned Dvorak-7 and Engram mechanics source

Author: Arno Klein. Repository: https://github.com/binarybottle/keyboard_layout_scorers.
Commit: `179e1c08b220ae1b02f6c425a7d1cbd1150c1db2`. License: MIT; original notice in LICENSE.

Original source and generated criterion tables are byte-preserved in upstream/. source-lock.json records every URL and SHA-256. The source-derived ports under src/bangla_dh/experimental/ports/ retain scoring functions and constants verbatim, extracted by the standard-library mechanics_sources module. It omits source writers, visualization and dependency-heavy layout/table drivers. No dependencies were added.

The adapter is experimental/mechanics.py. Primary traditional fingering is unchanged upstream. Model-optimal fingering is an explicit adaptation: source row/column coordinates and inside/outside key set retained, finger/hand assignments changed to the frozen Kala grid. Base/Shift layers are projected to physical keys; modifiers are outside scope. Unsupported keys/AltGr remain missing and retain their mass in fixed-denominator bounds. The number row is already defined by upstream functions; all 42 × 42 pairs are checked against them.

Dvorak-7: sum of seven criteria / 7. Engram avg4: the generator's mean of row_separation, same_row, same_finger and outside. The upstream unifier can include extra columns in a differently constructed score bearing the avg4 name; that composite is not silently substituted. Key preference, scissor and half-scissor are separate components. Engram triple order is separate; no combined pair/triple total is invented.

The source learned comfort table is not used by these mechanics adapters. The e1 evidence gate remains unchanged. Source rules are models; numerical agreement does not validate Bangla comfort, speed, training, or authorial comments that differ from code.

Explicit refetch and port extraction: `python -m bangla_dh.experimental.mechanics_sources --fetch`. Different existing source bytes are refused. Ordinary tests/evaluation are offline. A full source-fidelity audit is written with every e2 run: exhaustive original function comparison and 49,152 table rows, at tolerance 1e-6 (observed error about 1e-16).
