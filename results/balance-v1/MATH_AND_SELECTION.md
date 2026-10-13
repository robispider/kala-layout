# Balance v1: mathematics and candidate-selection process

**Balance v1 is adopted as an experimental analysis formula. Kala Goti and Kala Jhor remain the published layouts.** This report explains the measured components, fixed design priorities, frozen calibration and finite saved-candidate selection. It makes no human comfort or global-optimality claim.

## 1. How the candidates arose

The original mixed-corpus research searched J1 using 512 seeds per style. Experimental e4 then explored J1 and cross-space same-finger different-key rate, with 512 seeds per style, one million annealing proposals and 1,000 ILS trials per seed. Its per-seed archives retain movement/effort trade-offs, including candidates that lose the original reference-centered exploration objective. No search has been launched for this report or for Balance v1.

Rigorous e4 contains 26,892 distinct style/complete-assignment pairs: 12,622 A and 14,270 D. Earlier retained maps and smoke archives expand the evaluated union to 27,019: 12,704 A and 14,315 D. Deduplication preserves every origin in balance-study-v2/candidate-provenance.json.gz. Archive pruning means this union is not every visited or feasible layout.

All saved union maps were evaluated on both original training sources under model-optimal and traditional fingerings. Balance v1 selection uses only the original 50/50 training mix under model-optimal fingering. Known held-out benchmarks were examined after selection and remain exploratory.

## 2. The measured inputs

| Symbol | Meaning | Denominator and direction |
| --- | --- | --- |
| E | J1 = key effort + directed-pair effort + Shift effort | Effort per text unit N; lower |
| X | SF different-key endpoint distance across key–space–key | Key-pitch units per valid spanning window; lower |
| W | Within-word SF different-key center-distance sum | Key-pitch units per text unit N; lower |
| O | 1 − Engram triple-order credit | Deficit per valid within-word triple; lower |

For each metric, normalize each source using its own denominator, then average the two source values: x_mix = 0.5 x_wiki + 0.5 x_newspaper. This is not pooling counts. X and W have different denominators and are not added as raw distances. The score combines their dimensionless deviations against separately declared scales.

A and D preserve their own vowel encoders. Space is explicit in the cross-space stream. Escapes, paragraph ends and document ends break windows. Within-word pairs/triples never cross spaces or escapes. Movement projects base/Shift actions onto physical keys and excludes separate modifier motion. Repeated physical keys are separate from SF different-key movement. J1 still prices every key and Shift press, and treats identical-action pairs differently from same-key pairs across layers.

## 3. Eligibility and references

$$E(L)\le1.005E_{m ref},\qquad W(L)\le1.05W_{m ref}.$$

Use Goti for A and Jhor for D. Cross-space deterioration is permitted, but its positive component weight penalizes it. No exception waives these two caps. An ineligible map may be described diagnostically, but receives no eligible score or rank. The requested A-7c36e8f26e6c7142 remains in the comparison as an explicitly ineligible diagnostic.

| Style | Reference E | Maximum E | Reference W | Maximum W | Eligible saved maps |
| --- | --- | --- | --- | --- | --- |
| A | 1.8496860307151324 | 1.8589344608687082 | 0.017924340340626045 | 0.01882055735765735 | 681 |
| D | 1.8087958948695027 | 1.8178398743438502 | 0.01923550981913878 | 0.02019728531009572 | 466 |

Effort eligibility uses exact fractions against the frozen decimal effort grid. Distance eligibility uses binary64 with a declared 1e-14 absolute comparison tolerance. No distance or composite score is called exact.

## 4. Freeze aspirations and scales

$$r_k(L)=rac{x_k(L)-a_k}{t_k},\qquad t_k>0.$$

The numerical aspirations and acceptable-change scales are copied from balance-stability-v1/experiment-config.json. They are frozen constants, not recomputed when candidates are added. Aspirations originated as componentwise training minima in the saved union; that ideal vector need not correspond to one eligible layout. Later candidates may beat an aspiration, producing negative r; those deviations are not clipped.


### Style A

| Component | Aspiration a | Fixed scale t |
| --- | --- | --- |
| E | 1.84968603071513 | 0.00924843015357566 |
| X | 0.0468638691700242 | 0.0236581686531401 |
| W | 0.00998557318567258 | 0.000896217017031302 |
| O | 0.148688761256174 | 0.02 |

### Style D

| Component | Aspiration a | Fixed scale t |
| --- | --- | --- |
| E | 1.8087958948695 | 0.00904397947434751 |
| X | 0.0543540705923342 | 0.0268053067460891 |
| W | 0.014627192548951 | 0.000961775490956939 |
| O | 0.135408705663818 | 0.02 |

Scales express: 0.5% of reference E, 20% of reference X, 5% of reference W, and 0.02 absolute order deficit. Weights divided by scales determine each component’s coefficient; changing normalization would change priorities. Percentile normalization is therefore excluded from Balance v1.

## 5. The 81 fixed priority settings

$$B_	heta(L)=rac{\max_k(w_kr_k(L))+ho\sum_kw_kr_k(L)}{\sum_kw_k}.$$

$$w_E\in\{6,8,10\},\quad w_X=1,\quad w_W,w_O\in\{0.75,1,1.25\},\quad ho\in\{0.025,0.05,0.075\}.$$

There are 3 × 1 × 3 × 3 × 3 = 81 settings. Users do not choose one at scoring time. All are evaluated. Division by the weight sum fixes the overall scale and preserves each setting’s ranking. The maximum discourages a badly unbalanced component; the small positive augmentation accounts for the remaining components. These are fixed design priorities, not calibrated ergonomic weights.

## 6. Credit bounds and frozen calibration

$$c(L)\in[c^-(L),c^+(L)]\quad\Rightarrow\quad O(L)\in[1-c^+(L),1-c^-(L)].$$

Higher Engram credit is better. B+ uses 1−c−, the pessimistic deficit; B− uses 1−c+, the optimistic deficit. Unsupported triple mass retains its full 0..1 credit range. These are coverage bounds, not confidence intervals. The score is monotone in the deficit, so endpoint substitution bounds the candidate’s balance cost.

$$b_	heta^- = \min_{L\in\mathcal C_{m eligible}} B_	heta^-(L).$$

The 81 b− values per style are copied, not refitted, from best_score_lower in the existing stability sweep: four components, 0.5% effort cap, 5% within cap, mix, model-optimal. Their calibration pools contain 681 A maps and 466 D maps. This report independently recomputes the old calibration minima only as a verification, then retains the saved values as authoritative constants. The complete constants are in balance-v1-config.json.

A new map is compared with these constants. Adding it does not alter any earlier R. Even if it improves every old calibration candidate, positive-part truncation can give R=0; do not automatically rebase the benchmark. A future deliberate recalibration would require a newly named experimental formula version.

## 7. One number for each eligible layout

$$oxed{R(L)=\max_{	heta\in\Theta}\max\{0,B_	heta^+(L)-b_	heta^-\}.}$$

Lower R is better within the same style. R is a conservative worst shortfall from the frozen optimistic benchmark across the 81 settings. It is not an effort percentage, comfort percentage, probability or measured error. This is the primary mixed-training score; a different corpus/fingering changes the scenario and is reported as sensitivity, not silently substituted into Balance v1.

The prior worst-regret tolerance of 0.05 is not part of eligibility or the adopted R definition. Both winning R values exceed it. They are the lowest observed eligible R values, not candidates satisfying that earlier near-best label.

## 8. Worked calculations for the winners

### A-a280bdc4ca72c6c7 — style A

The controlling setting is A-19: weights [6, 1, 1.25, 0.75], rho=0.025. The following values produce its largest shortfall.

| Component | Pessimistic x | a | t | r | w × r |
| --- | --- | --- | --- | --- | --- |
| E | 1.855008031951 | 1.849686030715 | 0.009248430154 | 0.575449146 | 3.452694878 |
| X | 0.140537960271 | 0.046863869170 | 0.023658168653 | 3.959481922 | 3.959481922 |
| W | 0.015302254125 | 0.009985573186 | 0.000896217017 | 5.932358835 | 7.415448544 |
| O | 0.177017343284 | 0.148688761256 | 0.020000000000 | 1.416429101 | 1.062321826 |

B+ = (7.415448543590 + 0.025 × 15.889947169806) / 9.0 = 0.868077469204.
Frozen b− = 0.795317684666; R = B+ − b− = **0.072759784538**. All other settings have no larger shortfall.

### D-9ad5412603069cd6 — style D

The controlling setting is D-57: weights [10, 1, 0.75, 0.75], rho=0.075. The following values produce its largest shortfall.

| Component | Pessimistic x | a | t | r | w × r |
| --- | --- | --- | --- | --- | --- |
| E | 1.813731337206 | 1.808795894870 | 0.009043979474 | 0.545715783 | 5.457157826 |
| X | 0.116861500764 | 0.054354070592 | 0.026805306746 | 2.331905050 | 2.331905050 |
| W | 0.017651191647 | 0.014627192549 | 0.000961775491 | 3.144183987 | 2.358137990 |
| O | 0.240846225430 | 0.135408705664 | 0.020000000000 | 5.271875988 | 3.953906991 |

B+ = (5.457157825828 + 0.075 × 14.101107857393) / 12.5 = 0.521179273211.
Frozen b− = 0.381763310199; R = B+ − b− = **0.139415963012**. All other settings have no larger shortfall.

## 9. Finite ranking and gaps

### Style A

| Rank | Candidate | R | Gap above first |
| --- | --- | --- | --- |
| 1 | A-a280bdc4ca72c6c7 | 0.072759785 | 0.000000000 |
| 2 | A-36f3428c3f344a54 | 0.182291295 | 0.109531511 |
| 3 | A-3270b803ada27b63 | 0.184446613 | 0.111686828 |
| 4 | A-cd1cedf0ef5f7fe3 | 0.185457466 | 0.112697682 |
| 5 | A-70dc91ce76c7391e | 0.189785627 | 0.117025842 |
### Style D

| Rank | Candidate | R | Gap above first |
| --- | --- | --- | --- |
| 1 | D-9ad5412603069cd6 | 0.139415963 | 0.000000000 |
| 2 | D-eb3bf7d2da4f048e | 0.161369564 | 0.021953601 |
| 3 | D-a3a1484044fb8d5e | 0.161652545 | 0.022236582 |
| 4 | D-c4028c28dc54b209 | 0.164988475 | 0.025572512 |
| 5 | D-f4e1710b3ec62eb8 | 0.182134413 | 0.042718450 |

Rankings exhaust the eligible saved union under the stated configuration. They do not exhaust the layout search space. A/D scores use different style encoders, references, anchors and calibration minima, so comparing A’s R with D’s R is invalid.

## 10. Mathematical properties and limits

At fixed positive weights/scales/rho, B strictly respects componentwise dominance: an improvement decreases the weighted sum while the maximum cannot rise. For the finite 81-setting grid, a strict componentwise improvement strictly lowers R when the original R is positive. Final R is only weakly dominance-respecting overall because the zero floor can tie improved maps at R=0. Incomparable maps can also tie at the same worst shortfall. With fixed calibration, R is nonnegative and candidate additions cannot change earlier scores. Changing units of x, a and t together leaves the score unchanged.

Finite grid evaluation verifies each stated saved-set ranking. It does not prove a continuous weight region, global optimality, human comfort or speed. Existing Phase 4 certificates cover their original J1 problem/corpus, not Balance v1. Frozen b− are empirical calibration minima, not certified lower bounds over all possible layouts.

## 11. Verification and reproduction

The implementation is src/bangla_dh/experimental/balance_v1.py. It accepts one metric record and frozen calibration, not a candidate pool; consequently it cannot silently refit b−. Reports are generated by balance_v1_reports.py. Reproduce into a new directory with PYTHONPATH=src: `python -m bangla_dh.experimental.balance_v1_reports --out work/balance-v1-report-repeat`.

Verification results: {"saved_candidates": 27019, "calibration_settings_per_style": 81, "all_162_saved_calibration_constants_verified": true, "all_eligible_scores_match_existing_study": 1147, "eligible_A": 681, "eligible_D": 466, "candidate_profiles": 18, "additional_exploratory_heldout_rows": 36, "public_baseline_rows": 36, "same_style_layout_pair_comparisons": 73, "no_search": true, "published_layouts_retained": true, "validation": {"new_focused_tests": {"passed": 6, "includes": "frozen calibration, exact cap, unit invariance, strict dominance at positive R and zero-floor ties"}, "full_repository_tests": {"passed": 181, "seconds": 62.576}, "reproduction_checks": {"passed_groups": 8}, "SVG_XML_checks": {"passed": 18}, "effort_components_sum": "all candidate/source/fingering rows agree within 1e-11", "style_specific_calibration": "162 saved constants verified; 1147 eligible scores reproduced", "published_outputs": "preserved", "site": "unchanged; no site/doc pairs modified by this request"}}. Original results and pre-existing edits are protected by SHA-256; run-manifest.json records input/code/output hashes. validation.json records repository checks. Published layouts, challenge scoring, locks and website content remain unchanged.
