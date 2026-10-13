# Optional challenge diagnostics

**Official J1, submission acceptance and leaderboard ordering are unchanged.**

The preference table is incomplete and lacks independently reproduced predictive/Bangla validation. Its supported-pair diagnostic cannot rank whole layouts. No comfort rank or recommendation is produced.

The counts below retain repeats and directed pairs. Shift share excludes space; finger load excludes modifier presses. Same-finger moves count different physical keys. J1 is effort per text unit including space.

## D-reference.json: Bangla-DH D reference

Style D; official training J1 **1.808796**; +0.0000% versus the reference. Beats reference: False.

The exact official score is stored in submissions.json. Numbers here are descriptive, not additional challenge objectives. The model-optimal scenario is the official one; traditional fingering is a separate scenario.

| Text | Fingering | J1 change vs reference | Same-finger moves per unit (yours / reference) | Repeat share of pairs | Shift share of presses | Preference-table support |
| --- | --- | --- | --- | --- | --- | --- |
| bnwiki/train | model-optimal | +0.0000% | 0.014691 / 0.014691 | 0.79% | 9.18% | 21.19% |
| bnwiki/train | traditional | +0.0000% | 0.047038 / 0.047038 | 0.79% | 9.18% | 31.97% |
| newspaper/train | model-optimal | +0.0000% | 0.016075 / 0.016075 | 0.81% | 8.55% | 23.31% |
| newspaper/train | traditional | +0.0000% | 0.043890 / 0.043890 | 0.81% | 8.55% | 33.17% |
| bnwiki/heldout | model-optimal | +0.0000% | 0.014729 / 0.014729 | 0.79% | 9.18% | 21.20% |
| bnwiki/heldout | traditional | +0.0000% | 0.047029 / 0.047029 | 0.79% | 9.18% | 31.98% |
| newspaper/heldout | model-optimal | +0.0000% | 0.016036 / 0.016036 | 0.81% | 8.55% | 23.29% |
| newspaper/heldout | traditional | +0.0000% | 0.043938 / 0.043938 | 0.81% | 8.55% | 33.14% |
| bard-novel/heldout | model-optimal | +0.0000% | 0.015946 / 0.015946 | 0.82% | 8.35% | 23.37% |
| bard-novel/heldout | traditional | +0.0000% | 0.044083 / 0.044083 | 0.82% | 8.35% | 33.31% |

Detailed per-finger counts, coverage gaps and partial preference values are in submissions.json. The partial values refer to different supported subsets and must not be compared as total comfort scores.

### Source-derived movement diagnostics

Dvorak-7 and Engram avg4 use pinned upstream scoring functions. Higher values award more credit for physical-key mechanics. Both project base/Shift layers onto their keys and exclude modifier effort; they are not whole-typing comfort scores. Bounds retain unsupported pair mass with values between 0 and 1; they are coverage bounds, not confidence intervals. The traditional scenario preserves upstream fingering; model-optimal is an explicitly adapted scenario. Engram order is a separate within-token triple diagnostic.

| Text | Fingering | Dvorak-7 bounds | Change vs reference | Engram avg4 bounds | Change vs reference | Engram order bounds | Pair coverage |
| --- | --- | --- | --- | --- | --- | --- | --- |
| bnwiki/train | model-optimal | 0.776570–0.782240 | -0.005670 to +0.005670 | 0.894668–0.900338 | -0.005670 to +0.005670 | 0.754722–0.764780 | 99.433% |
| bnwiki/train | traditional | 0.756077–0.761747 | -0.005670 to +0.005670 | 0.876468–0.882138 | -0.005670 to +0.005670 | 0.678444–0.688502 | 99.433% |
| newspaper/train | model-optimal | 0.779197–0.783384 | -0.004187 to +0.004187 | 0.893376–0.897563 | -0.004187 to +0.004187 | 0.744415–0.751941 | 99.581% |
| newspaper/train | traditional | 0.760763–0.764950 | -0.004187 to +0.004187 | 0.877187–0.881374 | -0.004187 to +0.004187 | 0.678297–0.685823 | 99.581% |
| bnwiki/heldout | model-optimal | 0.776544–0.782288 | -0.005744 to +0.005744 | 0.894677–0.900421 | -0.005744 to +0.005744 | 0.754838–0.765031 | 99.426% |
| bnwiki/heldout | traditional | 0.756138–0.761882 | -0.005744 to +0.005744 | 0.876555–0.882299 | -0.005744 to +0.005744 | 0.678787–0.688980 | 99.426% |
| newspaper/heldout | model-optimal | 0.779365–0.783499 | -0.004134 to +0.004134 | 0.893533–0.897667 | -0.004134 to +0.004134 | 0.744931–0.752386 | 99.587% |
| newspaper/heldout | traditional | 0.760907–0.765041 | -0.004134 to +0.004134 | 0.877296–0.881430 | -0.004134 to +0.004134 | 0.678539–0.685993 | 99.587% |
| bard-novel/heldout | model-optimal | 0.779083–0.783093 | -0.004011 to +0.004011 | 0.893372–0.897383 | -0.004011 to +0.004011 | 0.743726–0.750896 | 99.599% |
| bard-novel/heldout | traditional | 0.760537–0.764548 | -0.004011 to +0.004011 | 0.877088–0.881099 | -0.004011 to +0.004011 | 0.677811–0.684981 | 99.599% |

Component bounds and the largest frequency-weighted pair deficits are in submissions.json. A positive change interval means more mechanics credit under that model; overlapping zero is unresolved by coverage. These diagnostics never change official challenge acceptance or ordering.

## A-reference.json: Bangla-DH A reference

Style A; official training J1 **1.849686**; +0.0000% versus the reference. Beats reference: False.

The exact official score is stored in submissions.json. Numbers here are descriptive, not additional challenge objectives. The model-optimal scenario is the official one; traditional fingering is a separate scenario.

| Text | Fingering | J1 change vs reference | Same-finger moves per unit (yours / reference) | Repeat share of pairs | Shift share of presses | Preference-table support |
| --- | --- | --- | --- | --- | --- | --- |
| bnwiki/train | model-optimal | +0.0000% | 0.012023 / 0.012023 | 0.51% | 8.92% | 23.56% |
| bnwiki/train | traditional | +0.0000% | 0.031621 / 0.031621 | 0.51% | 8.92% | 32.59% |
| newspaper/train | model-optimal | +0.0000% | 0.015025 / 0.015025 | 0.43% | 8.08% | 24.70% |
| newspaper/train | traditional | +0.0000% | 0.029929 / 0.029929 | 0.43% | 8.08% | 33.93% |
| bnwiki/heldout | model-optimal | +0.0000% | 0.012050 / 0.012050 | 0.50% | 8.91% | 23.59% |
| bnwiki/heldout | traditional | +0.0000% | 0.031687 / 0.031687 | 0.50% | 8.91% | 32.68% |
| newspaper/heldout | model-optimal | +0.0000% | 0.014978 / 0.014978 | 0.42% | 8.09% | 24.70% |
| newspaper/heldout | traditional | +0.0000% | 0.029916 / 0.029916 | 0.42% | 8.09% | 33.91% |
| bard-novel/heldout | model-optimal | +0.0000% | 0.014890 / 0.014890 | 0.43% | 7.91% | 24.78% |
| bard-novel/heldout | traditional | +0.0000% | 0.029809 / 0.029809 | 0.43% | 7.91% | 34.04% |

Detailed per-finger counts, coverage gaps and partial preference values are in submissions.json. The partial values refer to different supported subsets and must not be compared as total comfort scores.

### Source-derived movement diagnostics

Dvorak-7 and Engram avg4 use pinned upstream scoring functions. Higher values award more credit for physical-key mechanics. Both project base/Shift layers onto their keys and exclude modifier effort; they are not whole-typing comfort scores. Bounds retain unsupported pair mass with values between 0 and 1; they are coverage bounds, not confidence intervals. The traditional scenario preserves upstream fingering; model-optimal is an explicitly adapted scenario. Engram order is a separate within-token triple diagnostic.

| Text | Fingering | Dvorak-7 bounds | Change vs reference | Engram avg4 bounds | Change vs reference | Engram order bounds | Pair coverage |
| --- | --- | --- | --- | --- | --- | --- | --- |
| bnwiki/train | model-optimal | 0.781981–0.787411 | -0.005430 to +0.005430 | 0.898472–0.903902 | -0.005430 to +0.005430 | 0.773948–0.783753 | 99.457% |
| bnwiki/train | traditional | 0.768229–0.773659 | -0.005430 to +0.005430 | 0.889442–0.894872 | -0.005430 to +0.005430 | 0.743812–0.753617 | 99.457% |
| newspaper/train | model-optimal | 0.780910–0.784904 | -0.003994 to +0.003994 | 0.895989–0.899982 | -0.003994 to +0.003994 | 0.755500–0.762752 | 99.601% |
| newspaper/train | traditional | 0.770245–0.774238 | -0.003994 to +0.003994 | 0.890145–0.894138 | -0.003994 to +0.003994 | 0.739709–0.746961 | 99.601% |
| bnwiki/heldout | model-optimal | 0.781726–0.787227 | -0.005501 to +0.005501 | 0.898239–0.903740 | -0.005501 to +0.005501 | 0.773069–0.782999 | 99.450% |
| bnwiki/heldout | traditional | 0.767936–0.773438 | -0.005501 to +0.005501 | 0.889202–0.894703 | -0.005501 to +0.005501 | 0.743007–0.752937 | 99.450% |
| newspaper/heldout | model-optimal | 0.781088–0.785032 | -0.003943 to +0.003943 | 0.896151–0.900095 | -0.003943 to +0.003943 | 0.755881–0.763061 | 99.606% |
| newspaper/heldout | traditional | 0.770449–0.774393 | -0.003943 to +0.003943 | 0.890301–0.894245 | -0.003943 to +0.003943 | 0.739993–0.747174 | 99.606% |
| bard-novel/heldout | model-optimal | 0.780864–0.784690 | -0.003827 to +0.003827 | 0.896105–0.899931 | -0.003827 to +0.003827 | 0.755426–0.762337 | 99.617% |
| bard-novel/heldout | traditional | 0.770364–0.774191 | -0.003827 to +0.003827 | 0.890444–0.894271 | -0.003827 to +0.003827 | 0.740637–0.747548 | 99.617% |

Component bounds and the largest frequency-weighted pair deficits are in submissions.json. A positive change interval means more mechanics credit under that model; overlapping zero is unresolved by coverage. These diagnostics never change official challenge acceptance or ordering.

## Verification

Each evaluated submission passed the official parser and frozen inventory/bijection check. Its exact mixed-training J1 matches the repository integer scorer; every model-optimal corpus score matches the official scorer. The original scientific inputs and outputs stayed byte-identical.

Source/data/code hashes and policies are in run-manifest.json. The lookup benchmark verifies arithmetic only. Missing preference values are never replaced with zero or generated rules. This report has no effect on official scores, ties, duplicates, acceptance or leaderboard ordering.
