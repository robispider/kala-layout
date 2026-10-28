"""Training-only top-ten selection, two-mode scoring and fixed-map benchmarks."""
from __future__ import annotations
import argparse
from collections import defaultdict
from fractions import Fraction
from itertools import groupby
import json
from pathlib import Path
import random
import time

from bangla_dh import challenge
from bangla_dh.paths import PROJECT_ROOT as ROOT,write_json,write_text,hash_outputs
from bangla_dh.reference import sha256_file
from bangla_dh.experimental.artifact_storage import write_csv,write_json_compressed,verify_artifact
from bangla_dh.experimental.balance_study import PairEngine,order_values,average
from bangla_dh.experimental.balance_v1_reports import baseline_rows
from bangla_dh.experimental.inputs import TRAIN,HELDOUT,read_json
from bangla_dh.experimental.joint_search import atomic_json
from bangla_dh.experimental.shared_problem import pareto_offer
from bangla_dh.experimental.shared_relaxed import RelaxedProblem
from bangla_dh.experimental.shared_explore import cid
from bangla_dh.experimental.shared_search import table
from bangla_dh.experimental.shared_storage import StoredArtifacts
from bangla_dh.search.anneal import _random_pair
from bangla_dh.search.problem import slot_name

FOUR=ROOT/'results/shared-layout-relaxed-v1/run-4b-v1'
PILOT=ROOT/'results/shared-exploration-pilot-v1/run-100m-v1'
METRICS=('J1','key_effort','pair_effort','shift_effort','cross_rate','cross_distance',
         'within_rate','within_distance','order_lower','order_upper','order_coverage',
         'shift_share','escaped_share','pair_coverage','cross_coverage','engram_pair_lower',
         'engram_pair_upper','dvorak_lower','dvorak_upper')
LOWER=('J1','within_distance','cross_distance')


def frontier(rows):
    """Exact binary64 two-score dominance, grouping equal score vectors."""
    ordered=sorted(rows,key=lambda r:(*r['R'],r['id']))
    result=[];best=float('inf')
    for scores,group in groupby(ordered,key=lambda r:tuple(r['R'])):
        tied=list(group)
        if scores[1]<best:result.extend(tied)
        best=min(best,scores[1])
    return result


def top_layers(rows,n=10):
    """Pareto layers, then alternate A/D ascending lists; no R aggregation."""
    remaining=list(rows);selected=[];layer=0
    while remaining and len(selected)<n:
        layer+=1;part=frontier(remaining)
        seen=set();interleaved=[]
        a=sorted(part,key=lambda r:(r['R'][0],r['R'][1],r['id']))
        d=sorted(part,key=lambda r:(r['R'][1],r['R'][0],r['id']))
        for pair in zip(a,d):
            for row in pair:
                if row['id'] not in seen:interleaved.append(row);seen.add(row['id'])
        selected.extend({**r,'layer':layer} for r in interleaved[:n-len(selected)])
        remaining=[r for r in remaining if r['id'] not in seen]
    return selected


def mean_metrics(rows):
    if not rows:raise ValueError('empty mean')
    result={k:sum(float(r[k]) for r in rows)/len(rows) for k in METRICS}
    if all('J1_exact' in r for r in rows):
        result['J1_exact']=str(sum((Fraction(r['J1_exact']) for r in rows),Fraction())/len(rows))
    return result


def favorable_envelope(rows):
    return {**{k:min(r[k] for r in rows) for k in LOWER},
        'order_upper':max(r['order_upper'] for r in rows),
        'order_lower':min(r['order_lower'] for r in rows)}


def fast_gate(problem,perm):
    # Same test as the original six-QAP screen, with early rejection only.
    for i,key in enumerate(('EA','ED','WA','WD')):
        limit=problem.references[i]*(1.0075 if i<2 else 1.075)+1e-12
        if problem.instances[key].score(perm)>limit:return False
    return True


class Scores:
    def __init__(self,problem):self.problem=problem;self.cache={}
    def score(self,perm):
        key=tuple(perm)
        if key not in self.cache:
            self.cache[key]=self.problem.evaluate_training(list(perm))
        return self.cache[key]
    def record(self,perm,origin):
        scores=self.score(perm)
        if not all(scores[s]['balance']['eligible'] for s in ('A','D')):return None
        return {'id':cid(self.problem,perm),'perm':list(perm),
            'R':[scores[s]['balance']['R'] for s in ('A','D')],
            'training':scores,'origins':[origin]}


def replay_four(problem,scores,pool,settings,expected):
    """Replay the old final filter/refinement, capturing all full-score records."""
    seen=set();records={};archive=[];evaluations=0
    def offer(perm,origin):
        nonlocal evaluations
        key=tuple(perm)
        if key in seen or not fast_gate(problem,perm):return
        seen.add(key);evaluations+=1
        row=scores.record(perm,origin)
        if row is not None:
            records[row['id']]=row
            pareto_offer(archive,{'perm':list(perm),'R':row['R']},settings['frontier_limit'])
    for i,row in enumerate(pool):
        offer(row['perm'],'4b retained training pool')
        if (i+1)%20000==0:print(f'4b replay: {i+1:,}/{len(pool):,} screened; {evaluations} fully scored.',flush=True)
    rng=random.Random(settings['first_seed']+999999)
    for _ in range(settings['balance_refine_steps']):
        if not archive:break
        p=list(archive[rng.randrange(len(archive))]['perm'])
        i,j=_random_pair(rng,problem.n);p[i],p[j]=p[j],p[i]
        offer(p,'4b original final refinement')
    assert evaluations==expected['refinement']['full_R_evaluations'],(evaluations,expected['refinement'])
    assert len(records)==expected['refinement']['jointly_eligible_evaluations']
    expected_front=read_json(FOUR/'selection.json')['frontier']
    assert [(r['perm'],r['R']) for r in archive]==[(r['perm'],r['R']) for r in expected_front]
    return records,{'full_evaluations':evaluations,'eligible_records':len(records),'legacy_bounded_frontier_reproduced':True}


def pilot_union(scores,data):
    result={}
    for variant,points in data['full_scored_points'].items():
        for point in points:
            row=scores.record(point['perm'],'pilot '+variant)
            assert row is not None
            assert all(abs(a-b)<1e-10 for a,b in zip(row['R'],point['R']))
            if row['id'] in result:result[row['id']]['origins'].append('pilot '+variant)
            else:result[row['id']]=row
    return result


def mapping_alias():
    folder=ROOT/'data/kala/kala/layout/bn'
    unijoy=read_json(folder/'UniJoy.json');bijoy=read_json(folder/'bn_bijoy_layout.json')
    same={k:unijoy['layers'].get(k)==bijoy.get(k) for k in ('normal','shift','altgr')}
    assert all(same.values())
    return {'physical_layers_equal':same,'raw_files_identical':(folder/'UniJoy.json').read_bytes()==(folder/'bn_bijoy_layout.json').read_bytes(),
        'bijoy_has_own_vowel_rules':'combinations' in bijoy or 'rules' in bijoy,
        'comparison':'Bijoy key positions with explicitly borrowed UniJoy vowel-rule proxy; not commercial Bijoy validation',
        'source_sha256':{p.name:sha256_file(p) for p in (folder/'UniJoy.json',folder/'bn_bijoy_layout.json')}}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',default=str(Path(__file__).resolve().parent))
    args=parser.parse_args();out=Path(args.out).resolve()
    if out.exists() and any(p.name not in ('analyze.py','README.md','__pycache__') for p in out.iterdir()):
        raise FileExistsError('new output directory required')
    inputs=[Path(__file__).resolve(),ROOT/'tests/test_shared_top10.py',
        Path(__file__).resolve().parent/'README.md',ROOT/'results/shared-storage-v1/storage-manifest.json',
        FOUR/'run-manifest.json',FOUR/'selection.json',FOUR/'results.json',FOUR/'training-pool.json.gz',
        PILOT/'run-manifest.json',PILOT/'results.json',ROOT/'results/balance-v1/public-baseline-metrics.csv',
        ROOT/'results/balance-v1/run-manifest.json',ROOT/'data/baselines/registry.json',
        ROOT/'data/kala/kala/layout/bn/UniJoy.json',ROOT/'data/kala/kala/layout/bn/bn_bijoy_layout.json',
        ROOT/'results/phase3-crosscheck/crosscheck.json']
    for season in ('e2','e3'):
        inputs.extend([ROOT/f'results/evaluator-{season}/run-v1/scores.json.gz',
                       ROOT/f'results/evaluator-{season}/run-v1/run-manifest.json'])
    four_manifest=read_json(FOUR/'run-manifest.json')
    inputs.extend(ROOT/name for name in four_manifest['input_sha256'])
    inputs=sorted(set(inputs));before=hash_outputs(inputs)
    write_json(out/'analysis-plan.json',{'selection':'training-only Pareto layers, alternating A/D order within layers',
        'joint_top_n':10,'extra_mode_lists':'top ten separately per mode and pool',
        'pilot_pool':'deduplicated union of control/enhanced fully scored eligible maps; origins retained',
        '4b_pool':'deterministic capture/replay of the original final selection and refinement',
        'baseline_scope':'all six fixed registry maps; Bijoy physical-map proxy explicitly labelled',
        'baseline_comparison':'three held-out domains, two fingerings; per-metric favorable baseline envelope',
        'model_changed':False,'new_search':False,'input_sha256':before})
    began=time.perf_counter()
    with StoredArtifacts() as evidence:
        evidence.verify_containers()
        for name,expected in four_manifest['input_sha256'].items():evidence.hash(name,expected)
        evidence.hash('results/shared-layout-relaxed-v1/run-4b-v1/training-pool.json',
            four_manifest['output_sha256']['results/shared-layout-relaxed-v1/run-4b-v1/training-pool.json'])
        pool=evidence.read_json('results/shared-layout-relaxed-v1/run-4b-v1/training-pool.json')['candidates']
        pilot_manifest=read_json(PILOT/'run-manifest.json')
        evidence.hash('results/shared-exploration-pilot-v1/run-100m-v1/results.json',
            pilot_manifest['output_sha256']['results/shared-exploration-pilot-v1/run-100m-v1/results.json'])
    problem=RelaxedProblem();scores=Scores(problem)
    four,checks=replay_four(problem,scores,pool,four_manifest['settings'],read_json(FOUR/'results.json'))
    del pool
    pilot=pilot_union(scores,read_json(PILOT/'results.json'))
    pools={'4b':four,'pilot100m':pilot}
    selection={};modes=[];all_selected={}
    for name,rows in pools.items():
        selection[name]=top_layers(list(rows.values()))
        assert len(selection[name])==10
        for rank,r in enumerate(selection[name],1):
            r['label']=('B' if name=='4b' else 'P')+f'{rank:02d}'
            all_selected[r['id']]=r
        for i,mode in enumerate(('A','D')):
            top=sorted(rows.values(),key=lambda r:(r['R'][i],r['R'][1-i],r['id']))[:10]
            for rank,r in enumerate(top,1):
                modes.append({'pool':name,'mode':mode,'rank':rank,'id':r['id'],'R':r['R'][i]})
                all_selected[r['id']]=r
    write_json(out/'selection.json',{'joint_top_ten':selection,'mode_top_tens':modes,
        'source_counts':{k:len(v) for k,v in pools.items()},'replay_checks':checks,
        'heldout_used_for_selection':False})
    selected_hash=sha256_file(out/'selection.json')
    write_json_compressed(out/'eligible-training-pools.json',pools)
    baseline=baseline_rows()
    for season in ('e2','e3'):
        base=ROOT/f'results/evaluator-{season}/run-v1'
        verify_artifact(base/'scores.json.gz',read_json(base/'run-manifest.json'))
    expected=read_json(ROOT/'results/balance-v1/run-manifest.json')
    verify_artifact(ROOT/'results/balance-v1/public-baseline-metrics.csv',expected)
    alias=mapping_alias()
    # Include published Kala and independently balanced references in their own modes.
    references=[]
    for identity,style,title in [('A-18fe73cb912ae3f1','A','Original Kala Goti'),
        ('D-e4a6be48881da590','D','Original Kala Jhor'),('A-a280bdc4ca72c6c7','A','Separate Balance Goti'),
        ('D-9ad5412603069cd6','D','Separate Balance Jhor')]:
        raw=read_json(ROOT/'results/balance-v1/layouts'/(identity+'.json'))
        layout={s:tuple(v.split('/')) for s,v in raw['layout'].items()}
        references.append({'id':identity,'style':style,'title':title,'layout':layout})
    raw_rows=[];outputs=[]
    public=challenge.load_scorer(challenge.SCRIPT);data,data_hash=public.load_data();public_model=public.Model(data)
    for identity,r in all_selected.items():
        layout=problem.assignment(r['perm'])
        for mode in ('A','D'):
            result=public.evaluate({'name':identity,'style':mode,'layout':challenge._key_layout(layout)},data,data_hash,public_model)
            assert result['valid'] and Fraction(result['J1_exact'])==Fraction(r['training'][mode]['metrics']['J1_exact'])
        outputs.append(write_json(out/'layouts'/(identity+'.json'),{'id':identity,'experimental_only':True,
            'layout':{s:slot_name(v) for s,v in layout.items()},'styles':['A','D'],'training':r['training']}))
    print(f'Selection frozen: {len(all_selected)} unique joint/mode-list maps. Scoring sources and fingerings.',flush=True)
    for mode in ('A','D'):
        cases=[{'id':identity,'layout':problem.assignment(r['perm']),'kind':'candidate'} for identity,r in all_selected.items()]
        cases.extend({**r,'kind':'internal reference'} for r in references if r['style']==mode)
        for fingering in ('model-optimal','traditional'):
            for corpus in (*TRAIN,*HELDOUT):
                engine=PairEngine(mode,corpus,fingering)
                for case in cases:
                    m=engine.evaluate(case['layout']);m.update(order_values(mode,corpus,fingering,case['layout']))
                    raw_rows.append({'id':case['id'],'style':mode,'kind':case['kind'],'corpus':corpus,'fingering':fingering,**m})
    assert sha256_file(out/'selection.json')==selected_hash
    means=[]
    groups=defaultdict(list)
    for r in raw_rows+[{**r,'kind':'fixed baseline'} for r in baseline]:
        if r['corpus'] in HELDOUT:groups[r['id'],r['style'],r['fingering'],r['kind']].append(r)
    for key,rows in groups.items():
        assert len(rows)==3
        means.append({'id':key[0],'style':key[1],'fingering':key[2],'kind':key[3],**mean_metrics(rows)})
    bnames=sorted({r['name'] for r in baseline})
    legacy=read_json(ROOT/'results/phase3-crosscheck/crosscheck.json')['baselines']
    envelopes={}
    for name in bnames:
        rows=[r for r in means if r['id']=='baseline:'+name]
        env=favorable_envelope(rows)
        env['published_favorable_J1']=sum(min(g['J1'] for g in legacy[name]['scores'][c].values()) for c in HELDOUT)/3
        env['escaped_share']=rows[0]['escaped_share'];envelopes[name]=env
    comparisons=[]
    for pool_name,top in selection.items():
        for r in top:
            for mode in ('A','D'):
                candidates=[x for x in means if x['id']==r['id'] and x['style']==mode]
                for name,env in envelopes.items():
                    lower_adv={k:100*(1-max(x[k] for x in candidates)/env[k]) for k in LOWER}
                    order=('candidate' if min(x['order_lower'] for x in candidates)>env['order_upper'] else
                        'baseline' if env['order_lower']>max(x['order_upper'] for x in candidates) else 'unresolved')
                    comparisons.append({'pool':pool_name,'label':r['label'],'id':r['id'],'mode':mode,'baseline':name,
                        **{k+'_reduction_percent_worst_vs_best':v for k,v in lower_adv.items()},
                        'J1_reduction_percent_vs_published_favorable':100*(1-max(x['J1'] for x in candidates)/env['published_favorable_J1']),
                        'order_interval_winner_across_fingerings':order})
    overlap=sorted(set(r['id'] for r in selection['4b']) & set(r['id'] for r in selection['pilot100m']))
    full_overlap=set(four)&set(pilot)
    combined={**four,**pilot}
    fronts={k:[r['id'] for r in frontier(list(v.values()))] for k,v in pools.items()}
    fronts['combined']=[r['id'] for r in frontier(list(combined.values()))]
    first=selection['4b'][0]
    reference_map=problem.assignment(first['perm']);differences=[];shortlist=[]
    for pool_name,top in selection.items():
        for r in top:
            layout=problem.assignment(r['perm'])
            moved=[s for s in sorted(layout) if layout[s]!=reference_map[s]]
            shortlist.append({'pool':pool_name,'label':r['label'],'id':r['id'],'layer':r['layer'],
                'moved_symbols_vs_B01':len(moved),'origins':'; '.join(r['origins'])})
            for symbol in moved:
                differences.append({'pool':pool_name,'label':r['label'],'id':r['id'],'symbol':symbol,
                    'B01_slot':slot_name(reference_map[symbol]),'candidate_slot':slot_name(layout[symbol])})
    rankings=[]
    for name,rows in pools.items():
        rank_a={r['id']:i for i,r in enumerate(sorted(rows.values(),key=lambda r:(*r['R'],r['id'])),1)}
        rank_d={r['id']:i for i,r in enumerate(sorted(rows.values(),key=lambda r:(r['R'][1],r['R'][0],r['id'])),1)}
        for r in rows.values():
            rankings.append({'pool':name,'id':r['id'],'R_A':r['R'][0],'R_D':r['R'][1],
                'rank_A':rank_a[r['id']],'rank_D':rank_d[r['id']],'origins':'; '.join(r['origins'])})
    outputs += [write_csv(out/'all-training-ranks.csv',rankings),write_csv(out/'mode-top-tens.csv',modes),
        write_csv(out/'per-source-metrics.csv',raw_rows),write_csv(out/'baseline-source-metrics.csv',baseline),
        write_csv(out/'heldout-means.csv',means),write_csv(out/'baseline-favorable-envelopes.csv',[{'name':k,**v} for k,v in envelopes.items()]),
        write_csv(out/'candidate-baseline-comparison.csv',comparisons),
        write_csv(out/'shortlist-overview.csv',shortlist),write_csv(out/'candidate-map-differences.csv',differences)]
    findings={'selection_counts':{k:len(v) for k,v in pools.items()},'joint_top10_overlap':overlap,
        'distinct_top10_union':len({r['id'] for top in selection.values() for r in top}),
        'distinct_joint_and_mode_list_maps':len(all_selected),'replay_checks':checks,'bijoy_proxy':alias,
        'full_score_pool_overlap':len(full_overlap),'pilot_maps_absent_from_4b_full_score_pool':len(set(pilot)-set(four)),
        'unbounded_frontier_ids':fronts,'shortlist_structure':shortlist,
        'pairwise_comparisons':comparisons,'elapsed_seconds':time.perf_counter()-began}
    outputs.append(write_json(out/'analysis.json',findings))
    render_report(out,selection,modes,means,envelopes,comparisons,findings,references,pools,raw_rows)
    outputs += [out/'REPORT.md',out/'LAYOUTS.md',out/'analysis-plan.json',out/'selection.json',out/'eligible-training-pools.json.gz']
    assert hash_outputs(inputs)==before
    write_json(out/'run-manifest.json',{'version':'shared-top10-comparison-v1','new_search':False,'seeds':[],
        'parameters':{'top_n':10,'ranking':'Pareto layers / alternating mode extremes','model_changed':False,
            'baseline_encoder':'existing verified e2/e3 canonical actions','fingering':'both; favorable envelopes for robust comparisons'},
        'input_sha256':before,'output_sha256':hash_outputs(outputs),
        'checks':{'original_4b_final_filter_replayed':checks,'all_selected_exact_challenge_scores_match':True,
            'pilot_saved_scores_reproduced':True,'selection_frozen_before_heldout':True,'model_inputs_preserved':True,
            'baseline_source_scores_verified':True,'bijoy_physical_mapping_only':True}})
    print(json.dumps({'report':str(out/'REPORT.md'),'findings':{k:v for k,v in findings.items() if k!='pairwise_comparisons'}}),flush=True)


def comparison_summary(selection,means,comparisons,findings,pools,raw_rows):
    def metric(identity,mode,scope,grid='model-optimal'):
        if scope=='held-out':
            return next(r for r in means if r['id']==identity and r['style']==mode and r['fingering']==grid)
        return mean_metrics([r for r in raw_rows if r['id']==identity and r['style']==mode
                            and r['fingering']==grid and r['corpus'] in TRAIN])
    def delta(candidate,reference):
        return [f"{100*(candidate[k]/reference[k]-1):+.3f}%" for k in LOWER]+[
            f"{100*(candidate['order_lower']-reference['order_lower']):+.3f}"]
    first,second=selection['4b'][:2]
    a,b=first['id'],second['id']
    assert [r['id'] for r in selection['pilot100m'][:2]]==[a,b]
    assert all(set(v)=={a,b} for v in findings['unbounded_frontier_ids'].values())
    lines=['## Main findings','',
        '**The 100-million pilot did not improve the leading two-mode trade-off.** The 4-billion, pilot and combined fully scored pools all have exactly the same two non-dominated maps. Each ten-map list therefore contains two finalists and eight dominated backups. Six maps occur in both lists. More retained or fully scored maps did not translate into a better frontier in this pilot.','',
        table(['Experiment','Eligible fully scored maps','Non-dominated maps','Symbol changes vs B01 across its top ten'],
            [[name,len(pools[name]),len(findings['unbounded_frontier_ids'][name]),
              str(min(x['moved_symbols_vs_B01'] for x in findings['shortlist_structure'] if x['pool']==name))+'–'+
              str(max(x['moved_symbols_vs_B01'] for x in findings['shortlist_structure'] if x['pool']==name))]
             for name in selection]),'',
        f"The complete fully scored pools share {findings['full_score_pool_overlap']} maps. The pilot contributes {findings['pilot_maps_absent_from_4b_full_score_pool']} maps absent from the recovered 4-billion full-score collection. Absence there does not prove the earlier search never visited or mechanically retained a map. The leading maps were supplied to the pilot as common starts, so matching them is not an independent rediscovery.",'',
        '**For a shared-layout prototype, B01/P01 is my preferred starting point.** This is a judgment favoring the better Goti score while retaining the leading Jhor trade-off, not a numerical overall winner. Keep B02/P02 as the Jhor-favoring alternative. Their only position difference is swapping the rare vowel signs ৈ and ৌ between Shift+X and Shift+W. No measured speed or learning advantage is established.','',
        table(['Finalist','Full ID','Goti R (lower)','Jhor R (lower)'],
            [[r['label']+'/'+('P01' if i==0 else 'P02'),r['id'],f"{r['R'][0]:.6f}",f"{r['R'][1]:.6f}"]
             for i,r in enumerate((first,second))]),'',
        'The pilot-specific backups offer small local alternatives, not an improved leading arrangement. The top ten differ from B01 by at most seven symbol positions in the 4-billion pool and five in the pilot; all share the same entry-rule choice and frozen problem. Exact changes and control/enhanced origins are in candidate-map-differences.csv and shortlist-overview.csv.','',
        '## What the shared arrangement costs against separate Kala layouts','',
        'Changes below compare B01/B02 with the original independently optimized layout for the same mode, using model-optimal fingering. Negative E/W/X means improvement; positive means additional cost. Order change is the difference in lower credit bounds in percentage points; it is a diagnostic, not an interval-separated win claim. Training is the fixed 50/50 training-source mixture; held-out is the equal mean of the three held-out sources.','']
    refs={'A':'A-18fe73cb912ae3f1','D':'D-e4a6be48881da590'}
    rows=[]
    for r in (first,second):
        for mode in ('A','D'):
            for scope in ('training','held-out'):
                rows.append([r['label'],mode,scope,*delta(metric(r['id'],mode,scope),metric(refs[mode],mode,scope))])
    lines += [table(['Finalist','Mode','Source scope','Effort change','Within change','Cross change','Order lower change (pp)'],rows),'',
        'For B01 on the held-out mean, sharing costs about **0.61% effort in Goti and 0.45% in Jhor** versus the original layouts. Its Goti within-word distance is essentially unchanged there, but cross-space distance increases about **25.75%**; Jhor within/cross increases are about **1.35% / 3.92%**. The low effort cost should not obscure the Goti cross-space trade-off. Training movement changes and held-out changes differ.','',
        'The separately optimized Balance leaders are another relevant target. B01 versus each same-mode leader on the held-out mean, model-optimal fingering:','',
        table(['Mode','Separate Balance reference','Effort change','Within change','Cross change','Order lower change (pp)'],
            [[mode,identity,*delta(metric(a,mode,'held-out'),metric(identity,mode,'held-out'))]
             for mode,identity in [('A','A-a280bdc4ca72c6c7'),('D','D-9ad5412603069cd6')]]),'',
        'These values do not establish that sharing improves the separate Balance designs. Its intended benefit is one remembered arrangement; that benefit is outside the frozen mechanical formula.','',
        'Fingering sensitivity also matters. B01 versus the original same-mode layout under traditional fingering on the held-out mean:','',
        table(['Mode','Effort change','Within change','Cross change','Order lower change (pp)'],
            [[mode,*delta(metric(a,mode,'held-out','traditional'),metric(refs[mode],mode,'held-out','traditional'))]
             for mode in ('A','D')]),'',
        'The experimental +0.75%/+7.5% caps apply to the model-optimal training mix, so they do not promise those bounds on each source or on traditional fingering.','',
        '## B01 against known fixed layouts','',
        'Conservative percentage reductions on the equal held-out mean: take B01\'s worse value over the two fingerings and the baseline\'s better value. Effort uses the extra favorable published effort benchmark; movement uses the canonical action metrics. Positive favors B01. The UniJoy row also represents the explicitly stated Bijoy-positions / UniJoy-rule proxy.','',
        table(['Fixed layout','Goti effort reduction','Jhor effort reduction','Goti within reduction','Jhor within reduction'],
            [[('UniJoy / Bijoy positions proxy' if name=='UniJoy' else name),
              *[f"{next(r for r in comparisons if r['pool']=='4b' and r['label']=='B01' and r['baseline']==name and r['mode']==mode)[key]:.2f}%"
                for key,mode in [('J1_reduction_percent_vs_published_favorable','A'),('J1_reduction_percent_vs_published_favorable','D'),
                                 ('within_distance_reduction_percent_worst_vs_best','A'),('within_distance_reduction_percent_worst_vs_best','D')]]]
             for name in ('UniJoy','National (Jatiya)','Windows Default','Munir Optima (uni)','Probhat','Bornona')]),'',
        'All twenty shortlist entries in both modes improve these aggregate effort and within-word metrics against all six fixed maps under this conservative check. This is not a win on every dimension: **Bornona and Probhat have less cross-space same-finger distance**, and **Windows Default has a higher key-order credit interval** across both fingerings. Goti clears Probhat\'s order interval; many Jhor comparisons with Probhat remain unresolved. Windows Default also escapes about 2.57% of corpus units, versus roughly 0.02% for the shared candidates, which favors its zero-cost escape scores.','',
        'I would carry the two existing finalists into direct typing evaluation before scaling this same search much further. The enhanced pilot expands candidate coverage but supplies no evidence yet that another order of magnitude will improve the leading compromise. This is a recommendation from the observed search behavior, not a probability estimate or proof that a better layout does not exist.','']
    return lines


def render_report(out,selection,modes,means,envelopes,comparisons,findings,references,pools,raw_rows):
    def mean(identity,mode,grid='model-optimal'):
        return next(x for x in means if x['id']==identity and x['style']==mode and x['fingering']==grid)
    text=['# Top ten shared layouts: 4-billion search, 100-million pilot and fixed baselines','',
        '**The pilot keeps the same two leading shared layouts.** Two requested top-ten lists are selected from the experiments\' fully scored, jointly eligible maps using training alone. Goti (A) and Jhor (D) R values remain separately calibrated. Additional top-ten lists for each mode are exported, so the report ordering does not invent one combined Balance score.','']
    text += comparison_summary(selection,means,comparisons,findings,pools,raw_rows)
    text += [
        '## Selection and provenance','',
        f"Replayed the original 4-billion final filter/refinement, recovering **{findings['selection_counts']['4b']}** eligible full-score records and reproducing its saved bounded frontier. The pilot pool is the deduplicated union of control and enhanced fully scored maps: **{findings['selection_counts']['pilot100m']}** layouts. Origins remain explicit. Only these evaluated/saved scopes are ranked; this is not a ranking of every proposal.",'',
        'The report takes the first non-dominated layer, then the next layer, until ten slots are filled. Within each layer, ascending Goti and Jhor lists are interleaved, starting with Goti, and duplicate maps are removed. Companion R and layout ID break exact ties only. This is a declared display/shortlist rule, not a fitted ergonomic score. Backups below layer 1 are dominated and should not be presented as equally competitive finalists.','',
        f"The joint lists share **{len(findings['joint_top10_overlap'])} of ten maps**. The combined joint lists contain {findings['distinct_top10_union']} distinct maps; joint and extra mode lists together contain {findings['distinct_joint_and_mode_list_maps']}. Existing held-out sources and both fingerings are scored only after this selection was frozen.",'']
    for pool,top in selection.items():
        text += ['## '+('4-billion top ten' if pool=='4b' else '100-million pilot top ten'),'',
            table(['Slot','Layer','Candidate','Goti R','Jhor R','Goti held-out J1','Jhor held-out J1'],
                [[r['label'],r['layer'],r['id'],f"{r['R'][0]:.6f}",f"{r['R'][1]:.6f}",
                  f"{mean(r['id'],'A')['J1']:.6f}",f"{mean(r['id'],'D')['J1']:.6f}"] for r in top]),'',
            'Held-out J1 is the equal mean of Wikipedia, newspaper and BARD novels under model-optimal fingering; lower is better. It does not determine the slots. Complete per-source and traditional-fingering values are in per-source-metrics.csv.','',
            table(['Slot','Mode','Within SF distance','Cross-space SF distance','Order credit bounds','Shift share','Escaped share'],
                [[r['label'],s,f"{mean(r['id'],s)['within_distance']:.6f}",f"{mean(r['id'],s)['cross_distance']:.6f}",
                  f"{mean(r['id'],s)['order_lower']:.5f}–{mean(r['id'],s)['order_upper']:.5f}",
                  f"{100*mean(r['id'],s)['shift_share']:.2f}%",f"{100*mean(r['id'],s)['escaped_share']:.3f}%"] for r in top for s in ('A','D')]),'']
    text += ['## Fixed-layout benchmarks','',
        'All six registered fixed maps are included, including Bornona. Probhat is the registry spelling of the requested Probhats. The vendored Bijoy normal/Shift maps equal UniJoy\'s positions, but its raw file lacks vowel-conversion rules. The **Bijoy positions / UniJoy-rule proxy** therefore shares the UniJoy row under that explicit rule assumption. This is not an independently verified commercial Bijoy version or a byte-identical file claim. Bijoy is not counted as an extra independent benchmark.','',
        'The table gives the favorable value of each metric over model-optimal and traditional fingering after equal per-source normalization. These columns form a conservative envelope, not one physical fingering or one combined score. The extra published J1 column also permits the older scoreboard\'s recorded grid/encoder choices, including rounded-grid values, making that effort check favorable to each baseline.','',
        table(['Fixed layout','Canonical best J1','Published favorable J1','Best within distance','Best cross distance','Largest order upper bound','Escaped share'],
            [[('UniJoy / Bijoy positions proxy' if n=='UniJoy' else n),f"{e['J1']:.6f}",f"{e['published_favorable_J1']:.6f}",
              f"{e['within_distance']:.6f}",f"{e['cross_distance']:.6f}",f"{e['order_upper']:.6f}",
              f"{100*e['escaped_share']:.3f}%"] for n,e in sorted(envelopes.items(),key=lambda x:x[1]['published_favorable_J1'])]),'',
        'Baseline actions and metrics come from the hash-verified e2/e3 canonical encoder. Minimum-press encoding uses traditional-effort tie breaks held fixed across both fingerings. No corpus text is rebuilt. Escaped units cost no effort and break movement/order windows, which can flatter layouts with missing coverage; Windows Default\'s larger escape share must be considered when reading its scores.','',
        '## Conservative comparison across both fingerings','',
        'Each cell below is the range of percentage reductions over the ten selected maps in that mode, using the candidate\'s worse fingering against the baseline\'s better fingering for that metric. Positive favors the shared map; negative favors the baseline. E uses the additional published favorable J1 benchmark. W/X use the verified canonical movement envelope. These are comparisons of normalized modeled metrics, not speed or comfort percentages.','']
    for pool in selection:
        summary=[]
        for mode in ('A','D'):
            for name in envelopes:
                part=[r for r in comparisons if r['pool']==pool and r['mode']==mode and r['baseline']==name]
                fields=('J1_reduction_percent_vs_published_favorable','within_distance_reduction_percent_worst_vs_best',
                        'cross_distance_reduction_percent_worst_vs_best')
                summary.append([mode,name,*[f"{min(r[k] for r in part):+.2f}% to {max(r[k] for r in part):+.2f}%" for k in fields],
                    ', '.join(sorted(set(r['order_interval_winner_across_fingerings'] for r in part)))])
        text += ['### '+pool,'',table(['Mode','Fixed baseline','Effort reduction range','Within reduction range','Cross reduction range','Order interval result'],summary),'']
    text += ['## Interpretation and practical limits','',
        'Lower effort does not guarantee every mechanical advantage. Inspect cross-space movement and order bounds explicitly: a layout can have lower J1 and much less within-word SF distance while losing a cross-space or order comparison. Unsupported order-credit mass retains its full coverage interval; interval overlap is unresolved, not a win. Higher credit is better, whereas E/W/X are lower-is-better.','',
        'These shared maps are constrained against the original same-mode layouts on the training mix. The +0.75% E / +7.5% W limits do not apply automatically to every held-out source or traditional fingering. Full per-source rows retain those exceptions. Existing benchmark data are exploratory and are not fresh confirmation.','',
        'Fixed baselines are not assigned a shared-layout R rank: they have their own encoders, coverage and key domains and generally fail the shared-layout eligibility region. Raw components supply the comparison without inventing a common calibrated comfort total. No phonetic layout is included.','',
        'Mode-specific top-ten lists are in mode-top-tens.csv and full training ranks in all-training-ranks.csv. LAYOUTS.md and layouts/ hold the selected key arrangements. All scientific inputs, original results and the published layouts remain unchanged. Claims are best found within the stated scopes, not optimality or measured learning/speed/comfort.','']
    write_text(out/'REPORT.md','\n'.join(text))
    layouts=['# Selected shared key arrangements','',
             'Positions stay identical when switching Goti/Jhor entry rules. Upper row is Shift, lower row base. Digits and punctuation retain their frozen positions.','']
    rows={r['id']:r for part in selection.values() for r in part}
    # Mode-only additions also have exported JSON maps.
    for path in sorted((out/'layouts').glob('*.json')):
        raw=read_json(path);inverse={tuple(v.split('/')):s for s,v in raw['layout'].items()}
        layouts += ['## '+raw['id'],'']
        for keys in ('QWERTYUIOP','ASDFGHJKL','ZXCVBNM'):
            layouts += [table(['Layer',*keys],[[l,*[inverse[k,l] for k in keys]] for l in ('shift','base')]),'']
    write_text(out/'LAYOUTS.md','\n'.join(layouts))


if __name__=='__main__':main()
