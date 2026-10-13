"""Freeze experimental Balance v1 and produce two reproducible research reports.

Run from root: python -m bangla_dh.experimental.balance_v1_reports --out results/balance-v1
No official layout, objective, reproduction lock or prior output is changed.
"""
from __future__ import annotations
import argparse
from collections import Counter
import csv
from fractions import Fraction
import gzip
import html
import itertools
import json
from pathlib import Path
import unicodedata

from ..paths import PROJECT_ROOT as ROOT,write_json,write_text,hash_outputs
from .artifact_storage import artifact_sha256 as sha256_file,hash_artifacts as hash_outputs,open_text,verify_artifact as verify_stored_artifact
from ..search.problem import load_problem
from .balance_study import csv_write,preserved_files,PairEngine,order_values,average
from .balance_v1 import evaluate,cost,credit_deficit
from .inputs import TRAIN,HELDOUT,frequency_path
from .mechanics_counts import read_counts

STUDY=ROOT/'results/balance-study-v2'
STABILITY=ROOT/'results/balance-stability-v1'
REFS={'A':'A-18fe73cb912ae3f1','D':'D-e4a6be48881da590'}
EXTRAS=['A-4dfc1837861ac886','A-7c36e8f26e6c7142','D-48319b4b30582e8c',
        'D-8e3f1abe1434b3ea','D-8ed0c088f68ad80a','D-072c558b633d1019']
NUMERIC=['J1','key_effort','pair_effort','shift_effort','cross_rate','cross_distance','within_rate','within_distance',
    'order_lower','order_upper','order_coverage','engram_pair_lower','engram_pair_upper','dvorak_lower','dvorak_upper',
    'pair_coverage','cross_coverage','repeat_per_unit','repeat_share_pairs','cross_repeat','shift_share','escaped_share']


def read_csv(path):
    with path.open(encoding='utf-8',newline='') as f: return list(csv.DictReader(f))


def parse_row(r):
    return {k:float(r[k]) for k in NUMERIC}|{k:r[k] for k in ['id','style','corpus','fingering','J1_exact']}


def verify_artifact(path,manifest_path):
    m=json.loads(manifest_path.read_text(encoding='utf-8'))
    verify_stored_artifact(path,m)


def freeze(primary):
    source=json.loads((STABILITY/'experiment-config.json').read_text(encoding='utf-8'))
    sweep=read_csv(STABILITY/'formula-sweep.csv')
    recipe={'name':'Balance v1','status':'experimental adopted formula; published Jhor/Goti retained',
        'adoption_date':'2026-10-14','user_policy':'cross-space regression allowed when the overall compromise is worthwhile',
        'scope':'A/D frozen symbol problem; original independently normalized 50/50 training mix; model-optimal fingering',
        'eligibility':{'J1_multiplier':'201/200','within_distance_multiplier':1.05,'within_numeric_tolerance':1e-14},
        'formula':'R=max_theta max(0,B_plus-b_minus); B=(max(w*r)+rho*sum(w*r))/sum(w); r=(x-a)/t',
        'order_policy':'credit [c_lower,c_upper] becomes deficit [1-c_upper,1-c_lower]; B_plus uses 1-c_lower',
        'future_candidates':'retain numerical aspirations, scales, references, 81 settings and b_minus; never recalibrate automatically',
        'ineligible':'no eligible R or rank; metrics may be displayed diagnostically',
        'rankings':'separate A and D; R values must not be compared across styles',
        'calibration_source':'results/balance-stability-v1/formula-sweep.csv best_score_lower',
        'calibration_filter':{'components':4,'effort_budget_percent':.5,'within_budget_percent':5,'corpus':'mix','fingering':'model-optimal'},
        'calibration_provenance':'already examined saved archive; adoption after exploratory comparisons, not independent confirmation',
        'precision':'J1 eligibility uses exact fractions; distances, balance costs and frozen baselines are binary64',
        'styles':{}}
    for style,identity in REFS.items():
        anchors=source['scales_and_aspirations']['4'][style]
        chosen=[r for r in sweep if (r['style'],r['components'],r['effort_budget_percent'],r['within_budget_percent'],r['corpus'],r['fingering'])
            ==(style,'4','0.5','5','mix','model-optimal')]
        assert len(chosen)==81
        settings=[]
        for i,r in enumerate(chosen,1):
            settings.append({'id':f'{style}-{i:02d}','weights':json.loads(r['weights']),'rho':float(r['rho']),
                'b_minus':float(r['best_score_lower']),'calibration_candidate_count':int(r['eligible_count'])})
        combinations={(tuple(s['weights']),s['rho']) for s in settings}
        expected={(w,rho) for w in itertools.product([6,8,10],[1],[.75,1,1.25],[.75,1,1.25]) for rho in [.025,.05,.075]}
        assert combinations==expected
        recipe['styles'][style]={'reference_id':identity,'reference':{k:primary[identity][k] for k in ['J1','J1_exact','cross_distance','within_distance']},
            'components':anchors['components'],'aspirations':anchors['aspirations'],'scales':anchors['scales'],'settings':settings}
    return recipe


def display(symbol):
    return ('◌'+symbol) if symbol and unicodedata.category(symbol[0]).startswith('M') else symbol


def table(headers,rows):
    return ['| '+' | '.join(headers)+' |','| '+' | '.join('---' for _ in headers)+' |']+[
        '| '+' | '.join(str(x).replace('|','\\|') for x in row)+' |' for row in rows]


def interval(row,prefix): return f"{row[prefix+'_lower']:.5f}–{row[prefix+'_upper']:.5f}"
def delta(row,ref,k): return 100*(row[k]/ref[k]-1)


def layout_counts(a,b):
    changed=[s for s in a if a[s]!=b[s]]
    return len(changed),sum(a[s][0]!=b[s][0] for s in changed),sum(a[s][1]!=b[s][1] for s in changed)


def key_svg(layout,reference,title):
    inverse={tuple(v):s for s,v in layout.items()}
    text=['<svg xmlns="http://www.w3.org/2000/svg" width="1140" height="380" viewBox="0 0 1140 380">',
        '<rect width="1140" height="380" fill="white"/>',f'<text x="25" y="32" font-size="20">{html.escape(title)}</text>',
        '<text x="25" y="57" font-size="14">Upper: Shift; lower: base. Orange = assignment differs from published same-style reference.</text>']
    for row,keys in enumerate(['QWERTYUIOP','ASDFGHJKL','ZXCVBNM']):
        for col,key in enumerate(keys):
            x=25+row*38+col*106;y=80+row*95
            changed=any(reference.get(inverse.get((key,layer)))!=(key,layer) for layer in ['base','shift'])
            text.append(f'<rect x="{x}" y="{y}" width="98" height="86" rx="8" fill="{"#fff1dc" if changed else "#edf3f8"}" stroke="#8495a5"/>')
            text.append(f'<text x="{x+8}" y="{y+18}" font-size="12">{key}</text>')
            for layer,dy in [('shift',42),('base',72)]:
                s=inverse[key,layer]
                text.append(f'<text x="{x+50}" y="{y+dy}" text-anchor="middle" font-family="Noto Sans Bengali, Vrinda, sans-serif" font-size="24">{html.escape(display(s))}</text>')
    text.append('</svg>'); return '\n'.join(text)


def baseline_rows():
    e2=read_counts(ROOT/'results/evaluator-e2/run-v1/scores.json.gz')['scores']
    e3=read_counts(ROOT/'results/evaluator-e3/run-v1/scores.json.gz')['scores']
    boundary={(r['id'],r['corpus'],r['scenario']):r['continuous'] for r in e3}
    result=[]
    for r in e2:
        if not r['id'].startswith('baseline:'): continue
        d=r['diagnostics'];m=r['mechanics'];o=r['engram_order'];b=boundary[r['id'],r['corpus'],r['scenario']]
        result.append({'id':r['id'],'name':r['name'],'style':'baseline','corpus':r['corpus'],'fingering':r['scenario'],
            'J1':r['reference']['J1'],'key_effort':r['reference']['E1'],'pair_effort':r['reference']['E2'],'shift_effort':r['reference']['M'],
            'cross_rate':b['bounds']['same_finger_different_key']['lower'],'cross_distance':b['same_finger_distance_u_per_spanning_window'],
            'within_rate':d['same_finger_different_key_per_unit'],'within_distance':d['same_finger_center_distance_u_per_unit'],
            'order_lower':o['bounds']['lower'],'order_upper':o['bounds']['upper'],'order_coverage':o['coverage'],
            'engram_pair_lower':m['bounds']['engram_avg4']['lower'],'engram_pair_upper':m['bounds']['engram_avg4']['upper'],
            'dvorak_lower':m['bounds']['dvorak7']['lower'],'dvorak_upper':m['bounds']['dvorak7']['upper'],
            'pair_coverage':m['pair_coverage'],'cross_coverage':b['coverage'],
            'repeat_per_unit':d['same_physical_key_repeat_count']/read_corpus_N(r['corpus']),
            'repeat_share_pairs':d['same_physical_key_repeat_count']/d['non_space_pair_count'],
            'cross_repeat':b['bounds']['same_key']['lower'],'shift_share':d['shift_share_of_non_space_presses'],
            'escaped_share':d['escaped_unit_share']})
    return result


def read_corpus_N(corpus):
    from .inputs import unit_path
    return json.loads(unit_path(corpus).read_text(encoding='utf-8'))['N']


def mean_rows(rows):
    if not rows: raise ValueError('missing comparison rows')
    return {k:sum(r[k] for r in rows)/len(rows) for k in NUMERIC}


def mathematical_report(recipe,ranked,primary,results,checks):
    lines=['# Balance v1: mathematics and candidate-selection process','',
        '**Balance v1 is adopted as an experimental analysis formula. Kala Goti and Kala Jhor remain the published layouts.** This report explains the measured components, fixed design priorities, frozen calibration and finite saved-candidate selection. It makes no human comfort or global-optimality claim.','',
        '## 1. How the candidates arose','',
        'The original mixed-corpus research searched J1 using 512 seeds per style. Experimental e4 then explored J1 and cross-space same-finger different-key rate, with 512 seeds per style, one million annealing proposals and 1,000 ILS trials per seed. Its per-seed archives retain movement/effort trade-offs, including candidates that lose the original reference-centered exploration objective. No search has been launched for this report or for Balance v1.','',
        'Rigorous e4 contains 26,892 distinct style/complete-assignment pairs: 12,622 A and 14,270 D. Earlier retained maps and smoke archives expand the evaluated union to 27,019: 12,704 A and 14,315 D. Deduplication preserves every origin in balance-study-v2/candidate-provenance.json.gz. Archive pruning means this union is not every visited or feasible layout.','',
        'All saved union maps were evaluated on both original training sources under model-optimal and traditional fingerings. Balance v1 selection uses only the original 50/50 training mix under model-optimal fingering. Known held-out benchmarks were examined after selection and remain exploratory.','',
        '## 2. The measured inputs','',
        *table(['Symbol','Meaning','Denominator and direction'],[
            ['E','J1 = key effort + directed-pair effort + Shift effort','Effort per text unit N; lower'],
            ['X','SF different-key endpoint distance across key–space–key','Key-pitch units per valid spanning window; lower'],
            ['W','Within-word SF different-key center-distance sum','Key-pitch units per text unit N; lower'],
            ['O','1 − Engram triple-order credit','Deficit per valid within-word triple; lower']]),'',
        'For each metric, normalize each source using its own denominator, then average the two source values: x_mix = 0.5 x_wiki + 0.5 x_newspaper. This is not pooling counts. X and W have different denominators and are not added as raw distances. The score combines their dimensionless deviations against separately declared scales.','',
        'A and D preserve their own vowel encoders. Space is explicit in the cross-space stream. Escapes, paragraph ends and document ends break windows. Within-word pairs/triples never cross spaces or escapes. Movement projects base/Shift actions onto physical keys and excludes separate modifier motion. Repeated physical keys are separate from SF different-key movement. J1 still prices every key and Shift press, and treats identical-action pairs differently from same-key pairs across layers.','',
        '## 3. Eligibility and references','',
        '$$E(L)\le1.005E_{\rm ref},\qquad W(L)\le1.05W_{\rm ref}.$$','',
        'Use Goti for A and Jhor for D. Cross-space deterioration is permitted, but its positive component weight penalizes it. No exception waives these two caps. An ineligible map may be described diagnostically, but receives no eligible score or rank. The requested A-7c36e8f26e6c7142 remains in the comparison as an explicitly ineligible diagnostic.','']
    caprows=[]
    for s,c in recipe['styles'].items():
        ref=c['reference'];caprows.append([s,ref['J1'],float(Fraction(ref['J1_exact'])*Fraction(201,200)),ref['within_distance'],1.05*ref['within_distance'],len(ranked[s])])
    lines+=table(['Style','Reference E','Maximum E','Reference W','Maximum W','Eligible saved maps'],caprows)
    lines+=['','Effort eligibility uses exact fractions against the frozen decimal effort grid. Distance eligibility uses binary64 with a declared 1e-14 absolute comparison tolerance. No distance or composite score is called exact.','',
        '## 4. Freeze aspirations and scales','',
        '$$r_k(L)=\frac{x_k(L)-a_k}{t_k},\qquad t_k>0.$$','',
        'The numerical aspirations and acceptable-change scales are copied from balance-stability-v1/experiment-config.json. They are frozen constants, not recomputed when candidates are added. Aspirations originated as componentwise training minima in the saved union; that ideal vector need not correspond to one eligible layout. Later candidates may beat an aspiration, producing negative r; those deviations are not clipped.','']
    for s,c in recipe['styles'].items():
        lines+=['',f'### Style {s}', '']+table(['Component','Aspiration a','Fixed scale t'],[[k,f'{a:.15g}',f'{t:.15g}'] for k,a,t in zip(['E','X','W','O'],c['aspirations'],c['scales'])])
    lines+=['','Scales express: 0.5% of reference E, 20% of reference X, 5% of reference W, and 0.02 absolute order deficit. Weights divided by scales determine each component’s coefficient; changing normalization would change priorities. Percentile normalization is therefore excluded from Balance v1.','',
        '## 5. The 81 fixed priority settings','',
        '$$B_\theta(L)=\frac{\max_k(w_kr_k(L))+\rho\sum_kw_kr_k(L)}{\sum_kw_k}.$$','',
        '$$w_E\in\{6,8,10\},\quad w_X=1,\quad w_W,w_O\in\{0.75,1,1.25\},\quad \rho\in\{0.025,0.05,0.075\}.$$','',
        'There are 3 × 1 × 3 × 3 × 3 = 81 settings. Users do not choose one at scoring time. All are evaluated. Division by the weight sum fixes the overall scale and preserves each setting’s ranking. The maximum discourages a badly unbalanced component; the small positive augmentation accounts for the remaining components. These are fixed design priorities, not calibrated ergonomic weights.','',
        '## 6. Credit bounds and frozen calibration','',
        '$$c(L)\in[c^-(L),c^+(L)]\quad\Rightarrow\quad O(L)\in[1-c^+(L),1-c^-(L)].$$','',
        'Higher Engram credit is better. B+ uses 1−c−, the pessimistic deficit; B− uses 1−c+, the optimistic deficit. Unsupported triple mass retains its full 0..1 credit range. These are coverage bounds, not confidence intervals. The score is monotone in the deficit, so endpoint substitution bounds the candidate’s balance cost.','',
        '$$b_\theta^- = \min_{L\in\mathcal C_{\rm eligible}} B_\theta^-(L).$$','',
        'The 81 b− values per style are copied, not refitted, from best_score_lower in the existing stability sweep: four components, 0.5% effort cap, 5% within cap, mix, model-optimal. Their calibration pools contain 681 A maps and 466 D maps. This report independently recomputes the old calibration minima only as a verification, then retains the saved values as authoritative constants. The complete constants are in balance-v1-config.json.','',
        'A new map is compared with these constants. Adding it does not alter any earlier R. Even if it improves every old calibration candidate, positive-part truncation can give R=0; do not automatically rebase the benchmark. A future deliberate recalibration would require a newly named experimental formula version.','',
        '## 7. One number for each eligible layout','',
        '$$\boxed{R(L)=\max_{\theta\in\Theta}\max\{0,B_\theta^+(L)-b_\theta^-\}.}$$','',
        'Lower R is better within the same style. R is a conservative worst shortfall from the frozen optimistic benchmark across the 81 settings. It is not an effort percentage, comfort percentage, probability or measured error. This is the primary mixed-training score; a different corpus/fingering changes the scenario and is reported as sensitivity, not silently substituted into Balance v1.','',
        'The prior worst-regret tolerance of 0.05 is not part of eligibility or the adopted R definition. Both winning R values exceed it. They are the lowest observed eligible R values, not candidates satisfying that earlier near-best label.','',
        '## 8. Worked calculations for the winners','']
    for s in ['A','D']:
        winner=ranked[s][0];r=primary[winner['id']];c=recipe['styles'][s];setting=next(v for v in c['settings'] if v['id']==winner['worst_setting'])
        values=[r['J1'],r['cross_distance'],r['within_distance'],1-r['order_lower']]
        deviations=[(x-a)/t for x,a,t in zip(values,c['aspirations'],c['scales'])]
        terms=[w*d for w,d in zip(setting['weights'],deviations)]
        lines += [f"### {winner['id']} — style {s}",'',
            f"The controlling setting is {setting['id']}: weights {setting['weights']}, rho={setting['rho']}. The following values produce its largest shortfall.",'']
        lines+=table(['Component','Pessimistic x','a','t','r','w × r'],[[k,f'{x:.12f}',f'{a:.12f}',f'{t:.12f}',f'{d:.9f}',f'{z:.9f}'] for k,x,a,t,d,z in zip(['E','X','W','O'],values,c['aspirations'],c['scales'],deviations,terms)])
        lines += ['',f"B+ = ({max(terms):.12f} + {setting['rho']} × {sum(terms):.12f}) / {sum(setting['weights'])} = {winner['worst_B_plus']:.12f}.",
            f"Frozen b− = {winner['worst_b_minus']:.12f}; R = B+ − b− = **{winner['R']:.12f}**. All other settings have no larger shortfall.",'']
    lines += ['## 9. Finite ranking and gaps','']
    for s in ['A','D']:
        lines += [f'### Style {s}', '']+table(['Rank','Candidate','R','Gap above first'],[[i,r['id'],f"{r['R']:.9f}",f"{r['R']-ranked[s][0]['R']:.9f}"] for i,r in enumerate(ranked[s][:5],1)])
    lines += ['','Rankings exhaust the eligible saved union under the stated configuration. They do not exhaust the layout search space. A/D scores use different style encoders, references, anchors and calibration minima, so comparing A’s R with D’s R is invalid.','',
        '## 10. Mathematical properties and limits','',
        'At fixed positive weights/scales/rho, B strictly respects componentwise dominance: an improvement decreases the weighted sum while the maximum cannot rise. For the finite 81-setting grid, a strict componentwise improvement strictly lowers R when the original R is positive. Final R is only weakly dominance-respecting overall because the zero floor can tie improved maps at R=0. Incomparable maps can also tie at the same worst shortfall. With fixed calibration, R is nonnegative and candidate additions cannot change earlier scores. Changing units of x, a and t together leaves the score unchanged.','',
        'Finite grid evaluation verifies each stated saved-set ranking. It does not prove a continuous weight region, global optimality, human comfort or speed. Existing Phase 4 certificates cover their original J1 problem/corpus, not Balance v1. Frozen b− are empirical calibration minima, not certified lower bounds over all possible layouts.','',
        '## 11. Verification and reproduction','',
        'The implementation is src/bangla_dh/experimental/balance_v1.py. It accepts one metric record and frozen calibration, not a candidate pool; consequently it cannot silently refit b−. Reports are generated by balance_v1_reports.py. Reproduce into a new directory with PYTHONPATH=src: `python -m bangla_dh.experimental.balance_v1_reports --out work/balance-v1-report-repeat`.','',
        f"Verification results: {json.dumps(checks,ensure_ascii=False)}. Original results and pre-existing edits are protected by SHA-256; run-manifest.json records input/code/output hashes. validation.json records repository checks. Published layouts, challenge scoring, locks and website content remain unchanged."]
    return '\n'.join(lines)+'\n'


def comparison_report(target,recipe,ranked,primary,metrics,selected,layouts,origins,results,baselines,pair_rows):
    winner_ids={s:ranked[s][0]['id'] for s in REFS}
    lines=['# Balance v1: candidate analysis, layout differences and public-layout comparison','',
        '**This report compares experimental candidates. It does not replace Kala Goti or Kala Jhor.** The leading eligible saved candidates are A-a280bdc4ca72c6c7 and D-9ad5412603069cd6 under the frozen four-component Balance v1 score. Scores are modeled diagnostics; held-out comparisons are exploratory.','',
        'Report 1, MATH_AND_SELECTION.md, gives the complete formula, eligibility, frozen calibration and worked calculations. This report profiles the top five of each style, both published references, and earlier requested trade-offs. Full source/fingering metrics, calibration, rankings and every same-style symbol difference are supplied as CSV/JSON artifacts.','',
        '## 1. Reading the measurements','',
        'E=J1 effort per text unit; X=cross-space SF different-key distance in key-pitch units per spanning window; W=within-word SF different-key distance per text unit. Lower is better. Engram pair/order and Dvorak-7 are credit: higher is better, with unsupported-event coverage bounds. Shift share counts shifted nonspace actions. Escapes are text units typed outside the movement domain. Repeated physical keys are counted separately from different-key movement.','',
        'Training results below use the 50/50 source mix and same-style reference. Held-out averages give each of the three already examined sources one third; counts are not pooled. Fingering scenarios are kept separate. Percentage changes are modeled changes, never typing-speed percentages.','',
        'Published reference identifiers: **Kala Goti = A-18fe73cb912ae3f1**, **Kala Jhor = D-e4a6be48881da590**. Rankings remain separate by style. The diagrams show the 26 searched letter keys and both layers; fixed punctuation/digits are omitted from the pictures and retained in scoring.','',
        '## 2. Primary training summary','']
    for s in ['A','D']:
        ids=[i for i in selected if primary[i]['style']==s];ref=primary[REFS[s]]
        lines += [f'### Style {s}: '+('Goti / UniJoy-style independent vowels' if s=='A' else 'Jhor / context vowels'),'']
        lines+=table(['Candidate','Eligible rank','R','J1','E change %','X change %','W change %','Order credit bounds'],[
            [i,results[i].get('rank','—'),f"{results[i]['R']:.6f}" if results[i]['R'] is not None else 'ineligible',
             f"{primary[i]['J1']:.6f}",f"{delta(primary[i],ref,'J1'):+.3f}",f"{delta(primary[i],ref,'cross_distance'):+.2f}",
             f"{delta(primary[i],ref,'within_distance'):+.2f}",interval(primary[i],'order')] for i in ids])
    lines += ['','The top-five ordering follows R, not one movement metric. A’s leader accepts a cross-space regression for a larger within-word/order improvement. D’s leader improves both primary distances at a small effort cost. The larger cross-space gains of several earlier trade-offs do not automatically produce a lower worst-case balance cost.','',
        '## 3. Individual candidate profiles','']
    for identity in selected:
        style=primary[identity]['style'];refid=REFS[style];leader=winner_ids[style];r=primary[identity];ref=primary[refid]
        assignment=layouts[identity];counts=layout_counts(layouts[refid],assignment);peer=layout_counts(layouts[leader],assignment)
        label='published reference, retained' if identity==refid else 'experimental candidate'
        if identity=='A-7c36e8f26e6c7142': label='requested diagnostic; ineligible under the adopted effort cap'
        score=results[identity]
        lines += [f'### {identity} — {label}','',
            f"**Balance v1:** {'eligible rank '+str(score['rank'])+', R='+format(score['R'],'.9f') if score['eligible'] else 'ineligible; no eligible R/rank'}. "
            f"Primary changes versus its published reference: effort {delta(r,ref,'J1'):+.3f}%, cross distance {delta(r,ref,'cross_distance'):+.2f}%, within distance {delta(r,ref,'within_distance'):+.2f}%.",'',
            f"Assignment changes versus {refid}: {counts[0]} symbols; {counts[1]} change physical key; {counts[2]} change base/Shift layer. Versus Balance leader {leader}: {peer[0]} symbols, {peer[1]} physical-key changes, {peer[2]} layer changes. These count edits, not learned switching difficulty.",'',
            f"Provenance: {len(origins[identity])} retained records. First record: `{json.dumps(origins[identity][0],ensure_ascii=False)}`. Duplicate appearances and inserted references are not independent rediscoveries.",'']
        if identity!=leader:
            best=primary[leader]
            order_difference=[r['order_lower']-best['order_upper'],r['order_upper']-best['order_lower']]
            lines += [f"**Against the same-style Balance leader:** this map has E {delta(r,best,'J1'):+.3f}%, X {delta(r,best,'cross_distance'):+.2f}%, and W {delta(r,best,'within_distance'):+.2f}%. "
                f"Its order-credit difference, allowing both maps' unsupported-event bounds, is [{order_difference[0]:+.5f}, {order_difference[1]:+.5f}]. "
                'These differences explain which component benefits are exchanged; R determines the ordering across all 81 settings rather than declaring a single component sufficient.','']
        if score['eligible']:
            cal=recipe['styles'][style];setting=next(v for v in cal['settings'] if v['id']==score['worst_setting'])
            vals=[r['J1'],r['cross_distance'],r['within_distance'],1-r['order_lower']]
            terms=[w*(x-a)/t for w,x,a,t in zip(setting['weights'],vals,cal['aspirations'],cal['scales'])]
            active=['effort','cross-space distance','within-word distance','order deficit'][max(range(4),key=lambda j:terms[j])]
            lines += [f"**What controls its Balance v1 result:** at setting {setting['id']} (weights {setting['weights']}, rho {setting['rho']}), "
                f"{active} is the largest weighted deviation. B+ is {score['worst_B_plus']:.9f}, the frozen optimistic calibration cost is {score['worst_b_minus']:.9f}, "
                f"and their shortfall is R={score['R']:.9f}. This is the candidate's worst setting, not a weight choice fitted specifically to favor or reject it.",'']
        if delta(r,ref,'cross_distance')>0:
            lines += [f"**Accepted cross-space cost:** primary X rises {delta(r,ref,'cross_distance'):.2f}%. "
                f"Within-word distance changes {delta(r,ref,'within_distance'):+.2f}%; order-credit lower endpoint changes {r['order_lower']-ref['order_lower']:+.5f}. This states the traded quantities without converting them into human comfort.",'']
        part=[metrics[identity,c,f] for c in (*TRAIN,*HELDOUT) for f in ['model-optimal','traditional']]
        worst={k:max(delta(p,metrics[refid,p['corpus'],p['fingering']],k) for p in part) for k in ['J1','cross_distance','within_distance']}
        order_all=all(p['order_lower']>metrics[refid,p['corpus'],p['fingering']]['order_upper'] for p in part)
        pair_all=all(p['engram_pair_lower']>metrics[refid,p['corpus'],p['fingering']]['engram_pair_upper'] for p in part)
        lines += [f"Across individual training/held-out sources and both fingerings, worst observed changes are E {worst['J1']:+.3f}%, X {worst['cross_distance']:+.2f}%, W {worst['within_distance']:+.2f}%. "
            f"Order-credit superiority over the reference survives every observed coverage interval: **{'yes' if order_all else 'no'}**. Engram pair superiority survives every interval: **{'yes' if pair_all else 'no'}**. A 'no' includes overlap or reversal; it does not automatically imply inferiority.",'',
            '#### Effort components and secondary diagnostics on the training mix','']
        rows=[]
        for f in ['model-optimal','traditional']:
            p=metrics[identity,'mix',f];q=metrics[refid,'mix',f]
            rows.append([f,f"{p['key_effort']:.6f}",f"{p['pair_effort']:.6f}",f"{p['shift_effort']:.6f}",
                f"{100*p['shift_share']:.3f}%",f"{100*p['repeat_share_pairs']:.3f}%",f"{100*p['escaped_share']:.4f}%",
                interval(p,'engram_pair'),interval(p,'dvorak')])
        lines += table(['Fingering','Key effort','Pair effort','Shift effort','Shift share','Repeated-pair share','Escapes','Engram pair credit','Dvorak-7 credit'],rows)
        lines += ['','#### Individual-source scores','']
        lines += table(['Source','Fingering','J1','X (u/window)','W (u/unit)','Cross SF rate','Within SF/unit','Order credit bounds'],[
            [p['corpus'],p['fingering'],f"{p['J1']:.6f}",f"{p['cross_distance']:.6f}",f"{p['within_distance']:.6f}",
             f"{100*p['cross_rate']:.3f}%",f"{p['within_rate']:.6f}",interval(p,'order')] for p in part])
        lines += ['','#### Key map and symbol relocations','',
            f"[Full base/Shift keyboard diagram](layouts/{identity}.svg). Orange keys differ from the published same-style reference.",'']
        diff=[s for s in sorted(assignment) if assignment[s]!=layouts[refid][s] or assignment[s]!=layouts[leader][s]]
        if diff:
            lines+=table(['Symbol','NFC code points','Published reference','Balance leader','This candidate'],[
                [display(s),' '.join(f'U+{ord(ch):04X}' for ch in s),'/'.join(layouts[refid][s]),'/'.join(layouts[leader][s]),'/'.join(assignment[s])] for s in diff])
        else: lines+=['No symbol changes against the reference or leader.']
        lines+=['','Only the 52 searched symbol assignments differ. Fixed digits/punctuation and the style grammar remain unchanged. A layer change on the same physical key can change J1/Shift without changing projected physical-key movement. Full differences against every other reported same-style candidate are in layout-differences.csv.','']
    lines += ['## 4. Differences between candidates of the same style','',
        'Each cell is changed symbol assignments. Zero means identical complete searched assignments. Physical-key and layer-change counts, and the individual symbols, are in the companion CSVs. A and D are not mixed in this comparison.','']
    for s in ['A','D']:
        ids=[i for i in selected if primary[i]['style']==s]
        aliases={i:f'{s}{n}' for n,i in enumerate(ids,1)}
        lines += [f'### Style {s}','']+table(['Alias','Candidate'],[[aliases[i],i] for i in ids])+['']
        lines+=table(['From / to',*[aliases[i] for i in ids]],[[aliases[a],*[layout_counts(layouts[a],layouts[b])[0] for b in ids]] for a in ids])+['']
    lines += ['## 5. Public fixed Bangla layouts: a matched held-out comparison','',
        'The six registered fixed-layout baselines are UniJoy, National (Jatiya), Bornona, Probhat, Windows Default and Munir Optima (uni). Their frozen maps/provenance are under data/baselines/; UniJoy uses the vendored Kala file. This is the registry’s fixed-layout comparison set, not a claim to cover every publicly available Bangla keyboard version. Phonetic layouts are excluded by the repository’s owner decision. No new baseline has been added.','',
        'Baseline action encodings use minimum presses with traditional-grid tie-breaks fixed across fingerings, including their supported formatting and vowel rules. The tables below score every layout under the same fingering and the same equal-weight three-source held-out average. They do not combine per-metric best-of-grid numbers into one fictitious scenario. Historical official baseline tables may differ slightly because their optimal-grid encoder was not fixed in the same way.','',
        'No baseline receives a Balance v1 R/rank: the formula’s frozen A/D symbol problem, reference, training calibration and coverage rules are not defined for these different layout grammars. Ranking their held-out J1 or credit diagnostics is a separate comparison.','']
    public_ids=selected+[r['id'] for r in baselines if r['corpus']==HELDOUT[0] and r['fingering']=='model-optimal']
    blookup={(r['id'],r['corpus'],r['fingering']):r for r in baselines}
    for f in ['model-optimal','traditional']:
        aggregate=[]
        for identity in public_ids:
            p=mean_rows([(blookup if identity.startswith('baseline:') else metrics)[identity,c,f] for c in HELDOUT])
            aggregate.append((identity,p))
        aggregate.sort(key=lambda z:z[1]['J1'])
        lines += [f'### {f}: effort and movement','']+table(['Layout','J1','X (u/window)','W (u/unit)','Cross SF rate','Shift share','Escaped units'],[
            [i,f"{p['J1']:.6f}",f"{p['cross_distance']:.6f}",f"{p['within_distance']:.6f}",f"{100*p['cross_rate']:.3f}%",f"{100*p['shift_share']:.3f}%",f"{100*p['escaped_share']:.4f}%"] for i,p in aggregate])+['']
        lines += table(['Layout','Engram pair credit','Engram order credit','Dvorak-7 credit','Pair coverage','Triple coverage'],[
            [i,interval(p,'engram_pair'),interval(p,'order'),interval(p,'dvorak'),f"{100*p['pair_coverage']:.3f}%",f"{100*p['order_coverage']:.3f}%"] for i,p in aggregate])+['']
        for style in ['A','D']:
            leader=winner_ids[style];a=next(p for i,p in aggregate if i==leader)
            lines += [f'#### {leader} against each public baseline','']+table(['Baseline','Candidate J1 change','Candidate X change','Candidate W change','Pair-credit relation','Order-credit relation'],[
                [i.removeprefix('baseline:'),f"{delta(a,p,'J1'):+.2f}%",f"{delta(a,p,'cross_distance'):+.2f}%",f"{delta(a,p,'within_distance'):+.2f}%",
                 relation(a,p,'engram_pair'),relation(a,p,'order')] for i,p in aggregate if i.startswith('baseline:')])+['']
            public=[(i,p) for i,p in aggregate if i.startswith('baseline:')]
            lower_effort=[i.removeprefix('baseline:') for i,p in public if a['J1']<p['J1']]
            cross_worse=[i.removeprefix('baseline:') for i,p in public if a['cross_distance']>p['cross_distance']]
            order_lower=[i.removeprefix('baseline:') for i,p in public if relation(a,p,'order')=='candidate lower, bounds separated']
            lines += [f"**Reading this comparison:** under {f}, {leader} has lower held-out modeled J1 than {len(lower_effort)} of the six registered baselines. "
                f"Its cross-space distance is higher than: {', '.join(cross_worse) or 'none of these six'}. "
                f"Its order credit is conclusively lower, allowing coverage bounds, than: {', '.join(order_lower) or 'none of these six'}. "
                'These are scope-specific modeled comparisons; escapes and encoding differences remain relevant.','']
    lines += ['## 6. Interpreting the public comparison','',
        'Lower J1, lower SF distances and higher movement credit are distinct modeled findings; no one table establishes overall comfort. Interval-separated credit superiority is stated explicitly; overlapping intervals remain unresolved. Escaped text is outside the scored movement domain and contributes no modeled key effort: Windows Default’s larger escape share is a material comparison limitation. Extra presses, Shift use and vowel formatting differ between grammars.','',
        'Pair models share finger/row/home features with J1 and with the SF diagnostics. Agreement is robustness to some modeled assumptions, not independent human validation. Engram repeated-key credit differs from J1’s identical-action pair treatment. Distance uses key centers, not measured finger travel. Source/fingering changes can reverse individual diagnostics even for a primary balance winner.','',
        '## 7. Decision status','',
        'Keep Goti and Jhor as published. Balance v1 is the adopted experimental formula with frozen constants; its two leaders are research candidates for comparison. Eligibility applies to the primary training mix, not an automatic promise that every corpus/fingering stays within the same caps. The full per-source CSVs expose these limits. The next validation is independent new text and Bangla human preference/sustained typing studies, with priorities preregistered before examining those outcomes.','',
        'Both reports and their datasets were generated without changing model constants, official search, challenge scoring, reproduction locks, the website or existing results. run-manifest.json records hashes; validation.json records checks.']
    return '\n'.join(lines)+'\n'


def relation(a,b,prefix):
    if a[prefix+'_lower']>b[prefix+'_upper']: return 'candidate higher, bounds separated'
    if a[prefix+'_upper']<b[prefix+'_lower']: return 'candidate lower, bounds separated'
    return 'unresolved: bounds overlap'


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',required=True)
    target=Path(parser.parse_args().out).resolve()
    if target.exists(): raise ValueError('new nonexisting directory required')
    protected=preserved_files(target)
    inputs=[]
    for root,names in [(STUDY,['candidate-metrics.csv','candidate-provenance.json.gz']),
                       (STABILITY,['experiment-config.json','formula-sweep.csv','candidate-stability.csv'])]:
        for name in names:
            path=root/name;verify_artifact(path,root/'run-manifest.json');inputs.append(path)
        inputs.append(root/'run-manifest.json')
    primary={}
    with open_text(STUDY/'candidate-metrics.csv',newline='') as stream:
        for row in csv.DictReader(stream):
            if row['corpus']=='mix' and row['fingering']=='model-optimal': primary[row['id']]=parse_row(row)
    assert len(primary)==27019
    recipe=freeze(primary)
    write_json(target/'balance-v1-config.json',recipe)
    recipe_hash=sha256_file(target/'balance-v1-config.json')
    results={i:evaluate(r,recipe['styles'][r['style']]) for i,r in primary.items()}
    ranked={s:sorted([dict(id=i,**r) for i,r in results.items() if primary[i]['style']==s and r['eligible']],key=lambda r:(r['R'],r['id'])) for s in REFS}
    for s,rows in ranked.items():
        assert len(rows)==recipe['styles'][s]['settings'][0]['calibration_candidate_count']
        for rank,r in enumerate(rows,1):results[r['id']]['rank']=rank
    checks={'saved_candidates':len(primary),'calibration_settings_per_style':81}
    for s in REFS:
        c=recipe['styles'][s];pool=[primary[r['id']] for r in ranked[s]]
        for setting in c['settings']:
            computed=min(cost([r['J1'],r['cross_distance'],r['within_distance'],1-r['order_upper']],c['aspirations'],c['scales'],setting['weights'],setting['rho']) for r in pool)
            assert abs(computed-setting['b_minus'])<1e-12
    checks['all_162_saved_calibration_constants_verified']=True
    previous=read_csv(STABILITY/'candidate-stability.csv');count=0
    for r in previous:
        if (r['components'],r['effort_budget_percent'],r['within_budget_percent'])==('4','0.5','5'):
            assert abs(results[r['id']]['R']-float(r['primary_upper']))<1e-12;count+=1
    checks['all_eligible_scores_match_existing_study']=count
    assert ranked['A'][0]['id']=='A-a280bdc4ca72c6c7' and ranked['D'][0]['id']=='D-9ad5412603069cd6'
    selected=[]
    for s in REFS:
        selected += [REFS[s]]+[r['id'] for r in ranked[s][:5]]+[i for i in EXTRAS if primary[i]['style']==s]
    selected=list(dict.fromkeys(selected))
    with gzip.open(STUDY/'candidate-provenance.json.gz','rt',encoding='utf-8') as stream:
        raw=json.load(stream)
    layouts={r['id']:{s:tuple(v.split('/')) for s,v in r['layout'].items()} for r in raw if r['id'] in selected}
    origins={r['id']:r['origins'] for r in raw if r['id'] in selected};del raw
    metrics={}
    with open_text(STUDY/'candidate-metrics.csv',newline='') as stream:
        for row in csv.DictReader(stream):
            if row['id'] in selected:metrics[row['id'],row['corpus'],row['fingering']]=parse_row(row)
    # Recover missing held-out rows only after frozen primary selection.
    additional=0
    for s,c,f in itertools.product(REFS,HELDOUT,['model-optimal','traditional']):
        missing=[i for i in selected if primary[i]['style']==s and (i,c,f) not in metrics]
        if not missing:continue
        engine=PairEngine(s,c,f)
        for identity in missing:
            row=engine.evaluate(layouts[identity]);row.update(order_values(s,c,f,layouts[identity]))
            metrics[identity,c,f]={k:row[k] for k in NUMERIC}|{'id':identity,'style':s,'corpus':c,'fingering':f,'J1_exact':row['J1_exact']};additional+=1
    baselines=baseline_rows()
    for e in ['e2','e3']:
        path=ROOT/f'results/evaluator-{e}/run-v1/scores.json.gz';verify_artifact(path,path.parent/'run-manifest.json');inputs += [path,path.parent/'run-manifest.json']
    registry=ROOT/'data/baselines/registry.json';inputs.append(registry)
    write_json(target/'candidate-provenance.json',{i:{'origins':origins[i],'layout':{s:'/'.join(v) for s,v in layouts[i].items()}} for i in selected})
    csv_write(target/'candidate-rankings.csv',[{'id':i,'style':primary[i]['style'],**results[i],
        'J1':primary[i]['J1'],'cross_distance':primary[i]['cross_distance'],'within_distance':primary[i]['within_distance'],
        'order_lower':primary[i]['order_lower'],'order_upper':primary[i]['order_upper']} for i in sorted(primary)])
    csv_write(target/'candidate-metrics.csv',[r for k,r in sorted(metrics.items())])
    csv_write(target/'public-baseline-metrics.csv',baselines)
    pair_rows=[];diff_rows=[]
    for s in REFS:
        ids=[i for i in selected if primary[i]['style']==s]
        for a,b in itertools.combinations(ids,2):
            changed,physical,layers=layout_counts(layouts[a],layouts[b])
            pair_rows.append({'style':s,'candidate_a':a,'candidate_b':b,'changed_symbols':changed,'physical_key_changes':physical,'layer_changes':layers})
            for symbol in sorted(layouts[a]):
                if layouts[a][symbol]!=layouts[b][symbol]:
                    diff_rows.append({'style':s,'candidate_a':a,'candidate_b':b,'symbol':symbol,
                        'NFC_code_points':' '.join(f'U+{ord(ch):04X}' for ch in symbol),'slot_a':'/'.join(layouts[a][symbol]),'slot_b':'/'.join(layouts[b][symbol])})
    csv_write(target/'layout-difference-counts.csv',pair_rows);csv_write(target/'layout-differences.csv',diff_rows)
    for identity in selected:
        s=primary[identity]['style'];write_text(target/f'layouts/{identity}.svg',key_svg(layouts[identity],layouts[REFS[s]],identity))
        write_json(target/f'layouts/{identity}.json',{'id':identity,'style':s,'experimental_only':True,'published_replacement':False,'layout':{k:'/'.join(v) for k,v in layouts[identity].items()}})
    checks.update({'eligible_A':len(ranked['A']),'eligible_D':len(ranked['D']),'candidate_profiles':len(selected),
        'additional_exploratory_heldout_rows':additional,'public_baseline_rows':len(baselines),
        'same_style_layout_pair_comparisons':len(pair_rows),'no_search':True,'published_layouts_retained':True})
    write_text(target/'MATH_AND_SELECTION.md',mathematical_report(recipe,ranked,primary,results,checks))
    write_text(target/'CANDIDATE_ANALYSIS.md',comparison_report(target,recipe,ranked,primary,metrics,selected,layouts,origins,results,baselines,pair_rows))
    assert sha256_file(target/'balance-v1-config.json')==recipe_hash
    for p,h in protected.items():assert sha256_file(ROOT/p)==h,p
    inputs += [Path(__file__),ROOT/'src/bangla_dh/experimental/balance_v1.py',ROOT/'src/bangla_dh/experimental/balance_study.py',ROOT/'tests/test_balance_v1.py']
    inputs += [frequency_path(s,c) for s,c in itertools.product(REFS,(*TRAIN,*HELDOUT))]
    inputs += [p for folder in ['results/evaluator-e2/run-v1/counts','results/evaluator-e3/run-v1/counts'] for p in (ROOT/folder).glob('*')]
    write_json(target/'run-manifest.json',{'version':'balance-v1','parameters':recipe,'config_sha256':recipe_hash,
        'input_sha256':hash_outputs(inputs),'output_sha256':hash_outputs([p for p in target.rglob('*') if p.is_file()]),
        'preserved_original_sha256':protected,'checks':checks,'new_search_seeds':[]})
    print('Reports complete',target,checks,flush=True)


if __name__=='__main__': main()
