# Licences

The published separate Goti/Jhor maps and original typing rules are CC0. The historical shared B01 map and its research exports use the repository [MIT licence](../LICENSE). [Historical shared publication](../results/shared-publication-v1/REPORT.md).

| Part | Licence |
| --- | --- |
| Code in `src/`, `tests/`, `site/scripts/` and the workflows | [MIT](../LICENSE) |
| The original Kala Jhor and Kala Goti layout maps and their vowel-entry rules (`results/kala-keyboards/`) | [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/) |
| Documentation (`docs/`, `results/*/REPORT.md`) | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) |
| The published Colemak Mod-DH resources in `reference/colemak-dh-resources/` | CC0, from the `colemakmods/mod-dh` project |
| Source-derived Dvorak-7 and Engram ports, source snapshots and criterion tables (`data/evaluators/mechanics-v1/`) | Arno Klein, [MIT](../data/evaluators/mechanics-v1/LICENSE) |
| Fonts on the website (Inter, Noto Sans Bengali) | SIL Open Font License; notices in `site/public/licenses/` |
| Comparison layout key maps (`data/baselines/layouts/`, UniJoy and Bijoy in `data/kala/`) | Their authors' terms; benchmark data only |
| Texts of the ban-dataset-collection | Not in this repository; see [DATASETS.md](DATASETS.md) |

## Layout maps

Kala's original Kala Jhor and Kala Goti layout maps are dedicated to the public domain. Use them, adapt them, share them, or include them in another keyboard implementation, including commercially, without asking permission or paying royalties. The dedication covers the original key and layer maps and their original vowel-entry rules. It does not cover Kala application code, dictionaries, datasets, third-party engines, comparison layouts or brand marks. The owner approved the dedication on 12 October 2026; the same text is published with [Kala's guides](https://github.com/robispider/kala-releases/blob/main/docs/reference/original-layout-license.md).

## The original analyzer

The Colemak Mod-DH analyzer source that Phase 1 reproduced has no licence and is not part of this repository. `python -m bangla_dh fetch-upstream` downloads it at a pinned commit into `reference/upstream/`, which is ignored by Git, only for the optional model-reproduction step.
