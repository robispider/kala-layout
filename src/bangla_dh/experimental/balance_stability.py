"""Constrained near-best stability on saved balance metrics; no layout search.

PYTHONPATH=src python -m bangla_dh.experimental.balance_stability --out results/balance-stability-v1
"""
from __future__ import annotations
import argparse
import csv
from fractions import Fraction
import itertools
import json
from pathlib import Path
import time

from ..paths import PROJECT_ROOT as ROOT, write_json, write_text, hash_outputs
from .artifact_storage import artifact_sha256 as sha256_file,hash_artifacts as hash_outputs,open_text,verify_artifact
from .balance_study import csv_write, preserved_files, PairEngine, order_values, MANDATORY

SOURCE=ROOT/'results/balance-study-v2'
REFS={'A':'A-18fe73cb912ae3f1','D':'D-e4a6be48881da590'}
SCOPES=[('mix','model-optimal'),('bnwiki/train','model-optimal'),('newspaper/train','model-optimal'),
        ('mix','traditional'),('bnwiki/train','traditional'),('newspaper/train','traditional')]
NAMED=['A-4dfc1837861ac886','D-8e3f1abe1434b3ea','D-8ed0c088f68ad80a',MANDATORY]
FIELDS=['J1','cross_distance','within_distance','order_deficit_lower','order_deficit_upper',
        'order_lower','order_upper','engram_pair_lower','engram_pair_upper','dvorak_lower','dvorak_upper',
        'shift_share','escaped_share','order_coverage']


def eligible(row,reference,effort_percent,within_percent):
    return (Fraction(row['J1_exact'])<=Fraction(reference['J1_exact'])*(1+Fraction(str(effort_percent))/100)
        and row['within_distance']<=reference['within_distance']*(1+within_percent/100)+1e-14)


def balance(r,weights,rho):
    """Normalize the whole weight vector; winner identity is unchanged."""
    if len(r)!=len(weights) or rho<=0 or any(w<=0 for w in weights): raise ValueError('invalid positive parameters')
    terms=[w*x for w,x in zip(weights,r)]
    return (max(terms)+rho*sum(terms))/sum(weights)


def regret_bounds(lower,upper):
    if len(lower)!=len(upper) or not lower or any(a>b for a,b in zip(lower,upper)):
        raise ValueError('invalid score intervals')
    low_best,high_best=min(lower),min(upper)
    return [(max(0,a-high_best),max(0,b-low_best)) for a,b in zip(lower,upper)]


def read_metrics():
    result={}
    with open_text(SOURCE/'candidate-metrics.csv',newline='') as stream:
        for row in csv.DictReader(stream):
            result[row['id'],row['corpus'],row['fingering']]={k:float(row[k]) for k in FIELDS} | {
                'J1_exact':row['J1_exact'],'style':row['style']}
    return result


def protocol(scales):
    return {'version':'balance-stability-v1','source_package':'results/balance-study-v2',
        'purpose':'find small worst shortfalls within declared acceptable priorities; no official selection',
        'primary':'50/50 independently normalized Wikipedia/newspaper training; model-optimal fingering',
        'heldout':'already examined, exploratory diagnostics after selection only',
        'eligibility':'same-style primary J1 cap and within-word-distance cap; exact effort fractions, distance tolerance 1e-14',
        'effort_budget_percent':[.5,1],'within_distance_budget_percent':[0,5,10],
        'primary_guardrail_percent':5,'references':REFS,'style_ranking':'separate, never combined',
        'scales_and_aspirations':scales,'scale_policy':'retain v2 acceptable-change anchors/scales; no percentile scaling or refitting',
        'component_sets':{'3':['J1','cross_distance','within_distance'],
                          '4':['J1','cross_distance','within_distance','Engram order deficit interval']},
        'weights':{'effort':[6,8,10],'cross_distance':[1],'within_distance':[.75,1,1.25],'order_deficit':[.75,1,1.25]},
        'rho':[.025,.05,.075], 'central':{'weights_3':[8,1,1],'weights_4':[8,1,1,1],'rho':.05},
        'weight_policy':'divide all weights by their sum; preserves setting-wise ranking, fixes overall score scale for regret comparisons',
        'formula':'(max(w*r)+rho*sum(w*r))/sum(w); r=(x-a)/t; no negative clipping',
        'regret':'B(candidate)-min(B) over the same fixed eligible set in each setting/scenario',
        'normalizer':{'positive_fixed_score_tolerance':.05,'report':'regret/.05; tolerance multiples, never comfort percentages',
                      'near_best':'worst upper regret <=.05 across declared finite settings'},
        'coverage_regret_bounds':'[max(0,B_lower-min(B_upper)), B_upper-min(B_lower)]; conservative unsupported-event envelope, not confidence interval',
        'rankings':['primary grid minimax regret','six-training-scope grid minimax regret, separate sensitivity ranking'],
        'scenario_policy':'freeze primary eligible set; apply same primary anchors to all training scenarios; disclose later guardrail violations separately',
        'training_scopes':[{'corpus':c,'fingering':f} for c,f in SCOPES],
        'shortlist':'top five of each style/budget/guard/component/ranking plus references and critic-named maps',
        'requested_candidate':{'id':MANDATORY,'policy':'include diagnostics; never waive the explicit effort/within-word caps to make it eligible'},
        'parameters':'exploratory design priorities chosen after critic feedback, not calibrated ergonomic constants',
        'continuous_regions':'finite grid only; no continuous parameter certificate',
        'precision':'inherited exact effort fractions; distances, composites and regrets binary64',
        'new_search':False,'dependencies':'standard library only'}


def parameter_grid(n):
    for weights in itertools.product([6,8,10],[1],[.75,1,1.25], *([[.75,1,1.25]] if n==4 else [])):
        for rho in [.025,.05,.075]: yield weights,rho


def evaluate_region(ids,metrics,style,scales,n,budget,guard,tolerance):
    a,t=scales['aspirations'],scales['scales']
    # Normalize once; evaluate the unchanged score for every finite setting.
    vectors={}
    for scope in SCOPES:
        vectors[scope]=[]
        for identity in ids:
            row=metrics[identity,*scope]
            base=[(row[k]-a[i])/t[i] for i,k in enumerate(['J1','cross_distance','within_distance'])]
            lo=base+([(row['order_deficit_lower']-a[3])/t[3]] if n==4 else [])
            hi=base+([(row['order_deficit_upper']-a[3])/t[3]] if n==4 else [])
            vectors[scope].append((lo,hi))
    # Bounds on each map's worst regret, and endpoint scenarios as separate diagnostics.
    stats={identity:{'primary_lower':0.,'primary_upper':0.,'training_lower':0.,'training_upper':0.,
        'primary_optimistic':0.,'primary_pessimistic':0.,'primary_wins':0,'primary_rank_min':len(ids),'primary_rank_max':1,
        'worst_scope':'','worst_weights':'','worst_rho':0.} for identity in ids}
    outcomes=[]
    for weights,rho in parameter_grid(n):
        for scope in SCOPES:
            scores=[(balance(lo,weights,rho),balance(hi,weights,rho)) for lo,hi in vectors[scope]]
            lower,upper=map(list,zip(*scores)); intervals=regret_bounds(lower,upper)
            ordered=sorted(range(len(ids)),key=lambda i:(upper[i],ids[i]))
            is_primary=scope==SCOPES[0]
            winner=ordered[0]
            outcomes.append({'style':style,'effort_budget_percent':budget,'within_budget_percent':guard,'components':n,
                'weights':json.dumps(weights),'rho':rho,'corpus':scope[0],'fingering':scope[1],
                'endpoint_winner':ids[winner],'best_score_lower':min(lower),'best_score_upper':min(upper),
                'endpoint_winner_unique_under_bounds':upper[winner]<min((lower[i] for i in range(len(ids)) if i!=winner),default=float('inf'))-1e-12,
                'eligible_count':len(ids)})
            ranks={i:rank for rank,i in enumerate(ordered,1)} if is_primary else {}
            for i,identity in enumerate(ids):
                s=stats[identity]; lo,hi=intervals[i]
                s['training_lower']=max(s['training_lower'],lo)
                if hi>s['training_upper']:
                    s['training_upper']=hi; s['worst_scope']='/'.join(scope); s['worst_weights']=json.dumps(weights); s['worst_rho']=rho
                if is_primary:
                    s['primary_lower']=max(s['primary_lower'],lo); s['primary_upper']=max(s['primary_upper'],hi)
                    s['primary_optimistic']=max(s['primary_optimistic'],lower[i]-min(lower))
                    s['primary_pessimistic']=max(s['primary_pessimistic'],upper[i]-min(upper))
                    s['primary_wins']+=i==winner
                    s['primary_rank_min']=min(s['primary_rank_min'],ranks[i]); s['primary_rank_max']=max(s['primary_rank_max'],ranks[i])
    output=[]
    for identity,s in stats.items():
        output.append({'id':identity,'style':style,'effort_budget_percent':budget,'within_budget_percent':guard,'components':n,
            'eligible_count':len(ids),'primary_grid_settings':len(list(parameter_grid(n))),**s,
            'primary_worst_tolerance_units':s['primary_upper']/tolerance,'training_worst_tolerance_units':s['training_upper']/tolerance,
            'primary_near_best_under_bounds':s['primary_upper']<=tolerance+1e-12,
            'training_near_best_under_bounds':s['training_upper']<=tolerance+1e-12})
    primary_order=sorted(output,key=lambda r:(r['primary_upper'],r['id']))
    training_order=sorted(output,key=lambda r:(r['training_upper'],r['id']))
    for rank,r in enumerate(primary_order,1): r['primary_minimax_rank']=rank
    for rank,r in enumerate(training_order,1): r['training_minimax_rank']=rank
    return output,outcomes,primary_order[:5],training_order[:5]


def main():
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--out',required=True)
    target=Path(parser.parse_args().out).resolve()
    if target.exists(): raise ValueError('new nonexisting directory required')
    protected=preserved_files(target)
    manifest=json.loads((SOURCE/'run-manifest.json').read_text(encoding='utf-8'))
    inputs=[SOURCE/p for p in ['candidate-metrics.csv','candidate-provenance.json.gz','frozen-scales-3.json','frozen-scales-4.json','run-manifest.json']]
    for p in inputs[:-1]: verify_artifact(p,manifest)
    scales={str(n):{s:json.loads((SOURCE/f'frozen-scales-{n}.json').read_text())[str((s,'acceptable-change'))] for s in REFS} for n in [3,4]}
    conf=protocol(scales); write_json(target/'experiment-config.json',conf)
    config_hash=sha256_file(target/'experiment-config.json')
    print('Protocol frozen: fixed tolerances; 27 three-component and 81 four-component narrow settings.',flush=True)
    metrics=read_metrics(); ids=sorted({k[0] for k in metrics if k[1:]==SCOPES[0]})
    all_results=[]; all_sweep=[]; short=set(NAMED)|set(REFS.values()); selections=[]
    start=time.perf_counter()
    for style,budget,guard,n in itertools.product(REFS,[.5,1],[0,5,10],[3,4]):
        ref=metrics[REFS[style],*SCOPES[0]]
        pool=[i for i in ids if metrics[i,*SCOPES[0]]['style']==style and eligible(metrics[i,*SCOPES[0]],ref,budget,guard)]
        result,sweep,primary,training=evaluate_region(pool,metrics,style,scales[str(n)][style],n,budget,guard,.05)
        all_results.extend(result); all_sweep.extend(sweep)
        for ranking,rows in [('primary',primary),('training-robust',training)]:
            short.update(r['id'] for r in rows)
            selections.append({'style':style,'effort_budget_percent':budget,'within_budget_percent':guard,'components':n,
                'ranking':ranking,'winner':rows[0]['id'],'worst_regret_lower':rows[0][ranking=='training-robust' and 'training_lower' or 'primary_lower'],
                'worst_regret_upper':rows[0][ranking=='training-robust' and 'training_upper' or 'primary_upper'],
                'near_best_count':sum(r[ranking=='training-robust' and 'training_near_best_under_bounds' or 'primary_near_best_under_bounds'] for r in result),
                'eligible_count':len(pool)})
        print(style,budget,guard,n,'eligible',len(pool),'elapsed',round(time.perf_counter()-start,1),flush=True)
    csv_write(target/'candidate-stability.csv',all_results); csv_write(target/'formula-sweep.csv',all_sweep)
    csv_write(target/'selections.csv',selections)
    import gzip
    with gzip.open(SOURCE/'candidate-provenance.json.gz','rt',encoding='utf-8') as f:
        layouts={c['id']:{s:tuple(v.split('/')) for s,v in c['layout'].items()} for c in json.load(f) if c['id'] in short}
    # Previously examined held-out benchmarks never influence pool/grid/minimax selection.
    newly_evaluated=0
    engines={}
    from .inputs import HELDOUT, frequency_path
    for identity in sorted(short):
        style=metrics[identity,*SCOPES[0]]['style']
        for c,f in itertools.product(HELDOUT,['model-optimal','traditional']):
            if (identity,c,f) not in metrics:
                engine=engines.setdefault((style,c,f),None)
                if engine is None: engines[style,c,f]=engine=PairEngine(style,c,f)
                value=engine.evaluate(layouts[identity]); value.update(order_values(style,c,f,layouts[identity]))
                metrics[identity,c,f]={k:value[k] for k in FIELDS}|{'J1_exact':value['J1_exact'],'style':style}
                newly_evaluated+=1
    diagnostic=[]
    for identity in sorted(short):
        style=metrics[identity,*SCOPES[0]]['style']; p=metrics[identity,*SCOPES[0]]; ref=metrics[REFS[style],*SCOPES[0]]
        scopes=[(c,f) for i,c,f in metrics if i==identity]
        changes={k:[100*(metrics[identity,c,f][k]/metrics[REFS[style],c,f][k]-1) for c,f in scopes] for k in ['J1','cross_distance','within_distance']}
        row={'id':identity,'style':style,'J1':p['J1'],'J1_change_percent':100*(p['J1']/ref['J1']-1),
            'cross_distance_change_percent':100*(p['cross_distance']/ref['cross_distance']-1),
            'within_distance_change_percent':100*(p['within_distance']/ref['within_distance']-1),
            'order_credit_change':p['order_lower']-ref['order_lower'],'worst_J1_change_percent':max(changes['J1']),
            'worst_cross_distance_change_percent':max(changes['cross_distance']),
            'worst_within_distance_change_percent':max(changes['within_distance']),
            'all_observed_cross_distance_improve':max(changes['cross_distance'])<0,
            'order_improvement_survives_all_observed_bounds':all(metrics[identity,c,f]['order_lower']>metrics[REFS[style],c,f]['order_upper'] for c,f in scopes),
            'mandatory_diagnostic_only':identity==MANDATORY,
            'ineligible_regions':json.dumps([{'effort':b,'within':g} for b,g in itertools.product([.5,1],[0,5,10]) if not eligible(p,ref,b,g)])}
        for b,g in itertools.product([.5,1],[0,5,10]):
            row[f'all_observed_feasible_{b}_{g}']=all(eligible(metrics[identity,c,f],metrics[REFS[style],c,f],b,g) for c,f in scopes)
        diagnostic.append(row)
    csv_write(target/'shortlist.csv',diagnostic)
    csv_write(target/'shortlist-stability.csv',[r for r in all_results if r['id'] in short])
    write_json(target/'shortlist-layouts.json',{i:{s:'/'.join(v) for s,v in layout.items()} for i,layout in layouts.items()})
    render(target,conf,selections,diagnostic,all_results,newly_evaluated)
    assert sha256_file(target/'experiment-config.json')==config_hash
    for p,h in protected.items(): assert sha256_file(ROOT/p)==h,p
    inputs += [Path(__file__),ROOT/'tests/test_balance_stability.py', ROOT/'src/bangla_dh/experimental/balance_study.py']
    inputs += [frequency_path(s,c) for s,c in itertools.product(REFS,HELDOUT)]
    inputs += [p for p in (ROOT/'results/evaluator-e2/run-v1/counts').glob('*')]
    inputs += [p for p in (ROOT/'results/evaluator-e3/run-v1/counts').glob('*')]
    write_json(target/'run-manifest.json',{'version':conf['version'],'configuration_sha256':config_hash,'parameters':conf,
        'input_sha256':hash_outputs(inputs),'output_sha256':hash_outputs([p for p in target.iterdir() if p.is_file()]),
        'preserved_original_sha256':protected,'source_candidates':len(ids),'shortlisted_maps':len(short),
        'additional_exploratory_heldout_rows':newly_evaluated,'new_search_seeds':[],
        'checks':{'configuration_frozen_before_selection':True,'original_files_preserved':True,'heldout_not_used_for_selection':True}})
    print('Completed',target,'shortlist',len(short),flush=True)


def render(target,conf,selections,diagnostic,results,newrows):
    lines=['# Feedback: constrained near-best stability','',
        'Fixed acceptable-change scales and explicit eligibility limits were used before scoring. This is an exploratory follow-up on already examined data; no layout search or official selection occurred.','',
        'Effort caps: 0.5% and 1%. Primary within-word-distance cap: 5%, with 0%/10% sensitivity checks. Priorities vary narrowly: effort weight 6/8/10, cross weight 1, within/order weights 0.75/1/1.25, augmentation 0.025/0.05/0.075. These are declared choices, not ergonomic constants.','',
        'Worst regret means the largest score difference from the best eligible saved map across the declared settings. We divide by a fixed positive tolerance of 0.05 score units, rather than by the winning score. Whole weight vectors sum to one, keeping the score scale interpretable across settings. Three-component comparisons use point values; four-component minimax rankings use conservative coverage-regret upper bounds.','',
        '| Style | Effort cap | Components | Ranking | Candidate | Worst regret bound | Near-best maps |',
        '| --- | ---: | ---: | --- | --- | ---: | ---: |']
    for r in selections:
        if r['within_budget_percent']==5:
            lines.append(f"| {r['style']} | {r['effort_budget_percent']}% | {r['components']} | {r['ranking']} | {r['winner']} | {r['worst_regret_upper']:.6f} | {r['near_best_count']} |")
    lines += ['','Near-best counts require worst regret ≤0.05 across the finite grid; they are neither probabilities nor a continuous-region proof. Primary and six-training-scope rankings remain separate. The eligible set is fixed using the primary mix; a sensitivity winner can violate the same cap on another source/fingering. shortlist.csv discloses those violations and actual worst observed effort/movement regressions.','',
        f'{len(diagnostic)} distinct shortlisted/reference/named maps have complete training and exploratory held-out diagnostics; {newrows} held-out rows were newly recovered from existing derived counts after selection. The requested A-7c36e8f26e6c7142 is included diagnostically, but the effort caps exclude it.','',
        'Keep three questions separate: eligibility, score regret within the declared priorities, and actual movement regressions across sources/fingerings. A small regret alone does not establish ergonomic superiority. A four-component coverage envelope can be too conservative because it permits adversarial unknown credits; it remains a bound, not a statistical confidence interval.','',
        'Review the primary minimax candidates that also retain small observed regressions. If their order changes between component sets, guardrails or training scenarios, report the alternatives and their explicit priorities rather than selecting one natural balance. New independent text and Bangla human trials remain necessary to test generalization and comfort.']
    write_text(target/'FEEDBACK.md','\n'.join(lines)+'\n')
    report=['# Constrained near-best stability methods','',
        'The complete configuration, including inherited numerical aspirations/scales, was saved before any selection. Source metrics and their hashes come from balance-study-v2. Existing published results, model constants, challenge scoring, locks and prior experimental artifacts are preserved.','',
        'Eligibility uses exact rational J1 and binary64 within-distance comparisons with absolute tolerance 1e-14. Cross and within distances retain distinct denominators; only their normalized components enter the score. References and rankings remain per style. The primary 5% guardrail is declared rather than selected from outcomes.','',
        'For each setting, let candidate score lie in [l_i,u_i]. Its regret against the unknown best is bounded by [max(0,l_i-min_j u_j), u_i-min_j l_j]. Maxima across settings/scenarios bound its worst regret. Endpoint regret uses all optimistic or all pessimistic credits and is saved separately; it is not substituted for the conservative bound. A positive fixed 0.05 score-unit normalizer avoids division by zero, negative scores and reference-dependent percentage interpretations.','',
        'Weights are normalized by their total before score calculation. This positive common multiplier preserves each setting\'s winner, but makes regret magnitudes insensitive to multiplying the entire weight vector by a constant. The weight ranges represent a narrow, declared design region. No prior optimum or held-out result fits them.','',
        'Every primary eligible saved map is evaluated on all six existing training scenarios. The same primary eligible pool and frozen primary anchors are used throughout. Primary and training-robust minimax choices are reported separately; training/held-out cap violations are diagnostics, not silently ignored or used to retune the primary selection.','',
        'Reproduce from the root with PYTHONPATH=src: `python -m bangla_dh.experimental.balance_stability --out work/balance-stability-repeat`. Repeated runs require new directories. Finite grids do not prove continuous weight-region competitiveness; coverage bounds do not supply statistical confidence; existing Phase 4 certificates do not certify this score.','',*lines[2:]]
    write_text(target/'REPORT.md','\n'.join(report)+'\n')


if __name__=='__main__': main()
