"""Paired pilot: diverse archives and earlier full Balance; frozen model."""
from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import json
import math
import multiprocessing as mp
from pathlib import Path
import platform
import random
import time

from .. import challenge
from ..paths import PROJECT_ROOT as ROOT, hash_outputs, output_path, write_json, write_text
from ..reference import sha256_file
from ..search.anneal import _random_pair
from ..search.problem import slot_name
from .artifact_storage import write_csv
from .balance_study import PairEngine, order_values, preserved_files
from .inputs import TRAIN, HELDOUT, read_json
from .joint_search import atomic_json, settings_digest
from .mechanics import verify_sources
from .shared_problem import dominates, pareto_offer
from .shared_relaxed import RelaxedProblem, RelaxedState, energy, input_hashes as old_inputs, START_NAMES
from .shared_search import full_balance_frontier, table

VERSION='shared-exploration-pilot-v1'
FOUR_B=ROOT/'results/shared-layout-relaxed-v1/run-4b-v1'
INCUMBENTS=('shared-76c9b9dbfc689d0b','shared-7083b1ebfa5aa3a7')
_problem=None


def cid(problem,perm):
    layout=problem.assignment(perm)
    return 'shared-'+hashlib.sha256(json.dumps(sorted(layout.items()),ensure_ascii=False).encode()).hexdigest()[:16]


def encode(perm):
    return sum(v<<(6*i) for i,v in enumerate(perm))


def hamming_encoded(a,b,n):
    x=a^b
    spread=x|(x>>1)|(x>>2)|(x>>3)|(x>>4)|(x>>5)
    return (spread & sum(1<<(6*i) for i in range(n))).bit_count()


class CandidateArchive:
    """Control keeps low q; enhanced protects metrics and diverse assignments."""
    def __init__(self,limit,diverse=False):
        self.limit,self.diverse=limit,diverse
        self.rows={}

    def offer(self,perm,q,values):
        key=tuple(perm)
        if key in self.rows:
            return
        self.rows[key]={'perm':list(key),'q':q,'values':list(values),'encoded':encode(key)}
        if len(self.rows)<=self.limit:
            return
        if not self.diverse:
            del self.rows[max(self.rows,key=lambda k:(self.rows[k]['q'],k))]
            return
        keys=list(self.rows)
        protected={min(keys,key=lambda k:(self.rows[k]['q'],k))}
        for metric in range(6):
            protected.add(min(keys,key=lambda k:(self.rows[k]['values'][metric],self.rows[k]['q'],k)))
        removable=[k for k in keys if k not in protected]
        if not removable:
            removable=keys
        n=len(keys[0])
        def redundancy(k):
            near=min(hamming_encoded(self.rows[k]['encoded'],self.rows[j]['encoded'],n) for j in keys if j!=k)
            return near,-self.rows[k]['q'],k
        del self.rows[min(removable,key=redundancy)]

    def retained(self):
        return [{k:v for k,v in r.items() if k!='encoded'} for r in sorted(self.rows.values(),key=lambda r:(r['q'],r['perm']))]


class PilotProblem(RelaxedProblem):
    def __init__(self):
        super().__init__()
        self.names=list(START_NAMES)
        for name in INCUMBENTS:
            saved=read_json(FOUR_B/'layouts'/(name+'.json'))
            layout={s:tuple(slot.split('/')) for s,slot in saved['layout'].items()}
            self.starts.append(self.perm_of(layout));self.names.append(name)


class BalanceOracle:
    """Only training counts; exact eligibility and unchanged full-score expression."""
    def __init__(self,problem,limit=256,frontier_limit=16):
        self.problem,self.limit,self.frontier_limit=problem,limit,frontier_limit
        self.cache={};self.frontier=[]
        self.stats=Counter()

    def score(self,perm,values=None):
        key=tuple(perm)
        if key in self.cache:
            self.stats['cache_hits']+=1
            return self.cache[key]
        if self.stats['full_evaluations']>=self.limit:
            self.stats['budget_skips']+=1
            return None
        values=self.problem.values(perm) if values is None else values
        self.stats['mechanical_screens']+=1
        if not self.problem.eligible_fast(values):
            self.stats['mechanical_rejections']+=1
            return None
        scores=self.problem.evaluate_training(perm)
        self.stats['full_evaluations']+=1
        if not all(scores[s]['balance']['eligible'] for s in ('A','D')):
            self.cache[key]=None
            return None
        row={'perm':list(perm),'R':[scores[s]['balance']['R'] for s in ('A','D')],
             'order_lower':[scores[s]['metrics']['order_lower'] for s in ('A','D')],
             'values':self.problem.values(perm)}
        self.cache[key]=row
        self.stats['eligible_evaluations']+=1
        pareto_offer(self.frontier,row,self.frontier_limit)
        return row

    def points(self):
        return sorted((r for r in self.cache.values() if r is not None),key=lambda r:(r['R'],r['perm']))


def paired_start(problem,ordinal,seed):
    """Identical start and random stream for both variants of a pair."""
    rng=random.Random(seed)
    if ordinal<len(problem.starts):
        return list(problem.starts[ordinal]),problem.names[ordinal]
    perm=list(problem.starts[-2])
    if ordinal%3==0:
        for _ in range(4):
            i,j=rng.sample(range(problem.n),2);perm[i],perm[j]=perm[j],perm[i]
        name='perturbed-4b-primary'
    elif ordinal%3==1:
        rng.shuffle(perm);name='random'
    else:
        i,j,k=rng.sample(range(problem.n),3)
        perm[i],perm[j],perm[k]=perm[k],perm[i],perm[j]
        name='three-cycle-4b-primary'
    return perm,name


def balance_walk(problem,oracle,rng,steps,ordinal):
    """Full R decides local acceptance; trade-offs are protected separately."""
    stats=Counter()
    if not oracle.frontier:
        return None,stats
    initial=oracle.frontier[ordinal%len(oracle.frontier)]
    state=RelaxedState(problem,initial['perm'],'balance',.5)
    current=initial
    for _ in range(steps):
        if oracle.stats['full_evaluations']>=oracle.limit:
            break
        stats['neighbor_proposals']+=1
        choice=rng.random()
        if choice<.6:
            swaps=[_random_pair(rng,problem.n)]
        elif choice<.8:
            i,j,k=rng.sample(range(problem.n),3);swaps=[(i,j),(j,k)]
        else:
            i,j,k,l=rng.sample(range(problem.n),4);swaps=[(i,j),(k,l)]
        undo=[]
        for i,j in swaps:
            _,ds=state.delta(i,j);state.swap(i,j,ds);undo.append((i,j,ds))
        values=[s.score for s in state.states]
        point=oracle.score(state.perm,values)
        # Accept a full-score improvement or a genuine same-style trade-off;
        # never combine the two differently calibrated R numbers.
        accept=point is not None and not dominates(current['R'],point['R'])
        if accept:
            current=point;stats['full_R_accepted']+=1
        else:
            for i,j,ds in reversed(undo):
                state.swap(i,j,[-d for d in ds])
        if stats['neighbor_proposals']%32==0:
            state.reset(state.perm)
    return list(state.perm),stats


def initialize():
    global _problem
    _problem=PilotProblem()


def search_one(problem,variant,ordinal,seed,settings):
    enhanced=variant=='enhanced'
    if variant not in ('control','enhanced'):
        raise ValueError('unknown pilot variant')
    start,name=paired_start(problem,ordinal,seed)
    arm='effort' if ordinal%2==0 else 'balance'
    direction=(0.,.5,1.)[ordinal%3]
    state=RelaxedState(problem,start,arm,direction)
    rng=random.Random(seed);full_rng=random.Random(seed+700000)
    archive=CandidateArchive(settings['diverse_archive'] if enhanced else settings['control_archive'],enhanced)
    oracle=BalanceOracle(problem,settings['early_full_budget'],settings['frontier_limit']) if enhanced else None
    counts=Counter();started=time.perf_counter()
    def offer():
        values=[s.score for s in state.states] if len(state.states)==6 else problem.values(state.perm)
        archive.offer(state.perm,state.energy,values)
    def checkpoint(number):
        if not enhanced:
            return
        counts['early_checkpoints']+=1
        feasible=[r for r in archive.retained() if problem.eligible_fast(r['values'])]
        # Wider scoring bypasses the old top-q-only final filter.
        for r in sorted(feasible,key=lambda r:r['perm'])[:settings['early_score_batch']]:
            oracle.score(r['perm'],r['values'])
        perm,stats=balance_walk(problem,oracle,full_rng,settings['early_neighbor_steps'],number)
        counts.update(stats)
        if perm is not None:
            state.reset(perm);offer();counts['full_R_restarts']+=1
    def descend():
        while True:
            best,selected=-1e-12,None
            for i in range(problem.n-1):
                for j in range(i+1,problem.n):
                    d,ds=state.delta(i,j)
                    if d<best:best,selected=d,(i,j,ds)
            if selected is None:
                offer();return
            state.swap(*selected);counts['descent_moves']+=1
    offer()
    if enhanced:
        # These same known maps are included in control's final comparison pool.
        for perm in problem.starts[-3:]:oracle.score(perm)
    best,best_perm=state.energy,list(state.perm)
    uphill=[d for d in (state.delta(*_random_pair(rng,problem.n))[0] for _ in range(512)) if d>0]
    t0=sum(uphill)/len(uphill)/math.log(2) if uphill else .001
    temperature=t0;factor=settings['t_ratio']**(1/max(1,settings['steps']-1))
    for step in range(settings['steps']):
        i,j=_random_pair(rng,problem.n);d,ds=state.delta(i,j)
        if d<=0 or rng.random()<math.exp(-d/temperature):
            state.swap(i,j,ds);counts['accepted']+=1
            if counts['accepted']%10000==0:state.reset(state.perm)
            if state.energy<best-1e-12:
                best,best_perm=state.energy,list(state.perm);offer()
        if enhanced and (step+1)%settings['diversity_interval']==0:offer()
        if enhanced and (step+1)%settings['full_interval']==0:checkpoint((step+1)//settings['full_interval'])
        temperature*=factor
    state.reset(best_perm);descend();best,best_perm=state.energy,list(state.perm)
    for iteration in range(settings['ils_iterations']):
        for _ in range(rng.randint(2,6)):
            i,j=_random_pair(rng,problem.n);_,ds=state.delta(i,j);state.swap(i,j,ds)
        descend()
        if state.energy<best-1e-12:
            best,best_perm=state.energy,list(state.perm);counts['ils_improvements']+=1
        else:state.reset(best_perm)
        if enhanced and (iteration+1)%10==0:checkpoint(1000+iteration)
    state.reset(best_perm);offer()
    rows=archive.retained()
    if not any(r['perm']==list(state.perm) for r in rows):
        rows.append({'perm':list(state.perm),'q':state.energy,'values':problem.values(state.perm)})
    return {'version':VERSION,'variant':variant,'ordinal':ordinal,'seed':seed,'arm':arm,'start':name,
        'start_perm':start,'settings_sha256':settings_digest(settings),'archive':rows,'endpoint':list(state.perm),
        'early_full_points':oracle.points() if enhanced else [],'early_full_stats':dict(oracle.stats) if enhanced else {},
        'search_stats':dict(counts),'seconds':round(time.perf_counter()-started,3)}


def worker(args):
    return search_one(_problem,*args)


def input_hashes():
    return {**old_inputs(),**hash_outputs([ROOT/'results/shared-exploration-pilot-v1/README.md',
        ROOT/'tests/test_shared_explore.py',FOUR_B/'run-manifest.json',FOUR_B/'selection.json',FOUR_B/'results.json',
        *[FOUR_B/'layouts'/(i+'.json') for i in INCUMBENTS]])}


def run(out,settings,workers):
    target=Path(out).resolve()
    if not any(target.is_relative_to(r.resolve()) and target!=r.resolve()
               for r in (ROOT/'results/shared-exploration-pilot-v1',ROOT/'work/evaluator-experiments')):
        raise ValueError('new pilot child directory required')
    if target.exists():raise FileExistsError('choose a new pilot output')
    verify_sources();inputs=input_hashes();before=preserved_files(target)
    write_json(target/'experiment-plan.json',{'version':VERSION,'settings':settings,'workers':workers,
        'model':'unchanged frozen J1 and Balance v1 expression; existing relaxed eligibility',
        'input_sha256':inputs,'protected_sha256':before,'heldout_used_for_selection':False})
    jobs=[(variant,ordinal,settings['first_seed']+ordinal,settings)
          for variant in ('control','enhanced') for ordinal in range(settings['pairs'])]
    began=time.perf_counter();runs=[]
    with mp.Pool(workers,initializer=initialize) as pool:
        for r in pool.imap_unordered(worker,jobs):
            atomic_json(target/'runs'/f"{r['variant']}-{r['ordinal']:03d}.json",r);runs.append(r)
            print(f"{len(runs)}/{len(jobs)} {r['variant']} pair {r['ordinal']}: {r['seconds']:.1f}s",flush=True)
    finish(target,settings,inputs,before,runs,workers,began)


def finish(target,settings,inputs,before,runs,workers,began):
    problem=PilotProblem();summaries={};all_frontiers={};all_points={}
    seed_perms={tuple(p) for p in problem.starts}
    for variant in ('control','enhanced'):
        part=sorted((r for r in runs if r['variant']==variant),key=lambda r:r['ordinal'])
        perms=set(seed_perms);mechanical=set();early=set();stat=Counter()
        for r in part:
            mechanical.update(tuple(x['perm']) for x in r['archive'])
            early.update(tuple(x['perm']) for x in r['early_full_points'])
            stat.update(r['early_full_stats'])
        perms.update(mechanical);perms.update(early)
        oracle=BalanceOracle(problem,limit=100000,frontier_limit=settings['frontier_limit'])
        for perm in sorted(perms):oracle.score(perm)
        final_rng=random.Random(settings['first_seed']+999999)
        # Same full-score final refinement budget in both variants.
        _,walk_stats=balance_walk(problem,oracle,final_rng,settings['final_neighbor_steps'],0)
        frontier=oracle.frontier;all_frontiers[variant]=frontier;all_points[variant]=oracle.points()
        encoded=[encode(p) for p in sorted(mechanical)]
        distances=[hamming_encoded(a,b,problem.n) for i,a in enumerate(encoded) for b in encoded[i+1:]]
        summaries[variant]={'annealing_proposals':len(part)*settings['steps'],'paired_starts':len(part),
            'mechanical_saved_unique':len(mechanical),'early_full_saved_unique':len(early),
            'retained_union':len(perms),'eligible_full_scored_unique':len(oracle.points()),
            'non_start_eligible_unique':sum(tuple(p['perm']) not in seed_perms for p in oracle.points()),
            'frontier_count':len(frontier),'non_start_frontier_count':sum(tuple(p['perm']) not in seed_perms for p in frontier),
            'mean_mechanical_pair_hamming':sum(distances)/len(distances) if distances else 0.,
            'summed_seed_seconds':sum(r['seconds'] for r in part),'early_full_stats':dict(stat),
            'final_walk_stats':dict(walk_stats)}
    # Pairing and proposal arithmetic are checked from actual completed runs.
    for ordinal in range(settings['pairs']):
        pair=[r for r in runs if r['ordinal']==ordinal]
        assert len(pair)==2 and pair[0]['start_perm']==pair[1]['start_perm'] and pair[0]['seed']==pair[1]['seed']
    assert sum(s['annealing_proposals'] for s in summaries.values())==settings['total_proposals']
    common_scores=[problem.evaluate_training(p) for p in problem.starts[-2:]]
    comparison=[]
    for variant in ('control','enhanced'):
        other='enhanced' if variant=='control' else 'control'
        for point in all_frontiers[variant]:
            comparison.append({'variant':variant,'id':cid(problem,point['perm']),'R_A':point['R'][0],'R_D':point['R'][1],
                'not_a_common_start':tuple(point['perm']) not in seed_perms,
                'dominates_any_other_frontier':any(dominates(point['R'],x['R']) for x in all_frontiers[other]),
                'dominated_by_other_frontier':any(dominates(x['R'],point['R']) for x in all_frontiers[other]),
                'dominates_any_4b_incumbent':any(dominates(point['R'],[x[s]['balance']['R'] for s in ('A','D')]) for x in common_scores)})
    # Freeze this selection before looking at held-out scores.
    selected={}
    for variant,frontier in all_frontiers.items():
        for point in frontier:selected.setdefault(cid(problem,point['perm']),point)
    write_json(target/'selection.json',{'basis':'training only','frontiers':all_frontiers,'selected':selected})
    selected_hash=sha256_file(target/'selection.json')
    public=challenge.load_scorer(challenge.SCRIPT);data,digest=public.load_data();model=public.Model(data)
    metrics=[];outputs=[]
    for identity,point in selected.items():
        layout=problem.assignment(point['perm']);training=problem.evaluate_training(point['perm'])
        for style in ('A','D'):
            official=public.evaluate({'name':identity,'style':style,'layout':challenge._key_layout(layout)},data,digest,model)
            assert official['valid'] and Fraction(official['J1_exact'])==Fraction(training[style]['metrics']['J1_exact'])
            assert training[style]['balance']['eligible']
            assert abs(training[style]['balance']['R']-point['R'][0 if style=='A' else 1])<1e-10
        outputs.append(write_json(target/'layouts'/(identity+'.json'),{'id':identity,'styles':['A','D'],
            'experimental_only':True,'layout':{s:slot_name(v) for s,v in layout.items()},'training':training}))
    print('Training comparison frozen; evaluating known held-out diagnostics.',flush=True)
    for style in ('A','D'):
        for fingering in ('model-optimal','traditional'):
            for corpus in (*TRAIN,*HELDOUT):
                engine=PairEngine(style,corpus,fingering)
                for identity,point in selected.items():
                    layout=problem.assignment(point['perm']);m=engine.evaluate(layout)
                    m.update(order_values(style,corpus,fingering,layout))
                    metrics.append({'id':identity,'style':style,'corpus':corpus,'fingering':fingering,**m})
    assert sha256_file(target/'selection.json')==selected_hash
    outputs += [write_csv(target/'scores.csv',metrics),write_csv(target/'frontier-comparison.csv',comparison),
                write_json(target/'results.json',{'summaries':summaries,'frontiers':all_frontiers,'comparison':comparison,
                    'full_scored_points':all_points,'elapsed_seconds':time.perf_counter()-began})]
    text=['# Diverse/earlier-Balance search: matched 10-million pilot','',
        '**The model is unchanged.** This pilot changes search retention and the timing/use of full Balance scores. Frozen J1, Balance components, 81 settings, calibration, geometry, encoders and +0.75% effort/+7.5% within-word caps are reused exactly.','',
        f"Total budget: **{settings['total_proposals']:,} annealing proposals**, half control and half enhanced, plus separately recorded local/full-score neighbor checks. Each variant has {settings['pairs']} paired starts with identical initial maps and seed values. Both have the same current 4-billion incumbents available. Equal proposal budget is not equal compute time.",'',
        '## Results','',table(['Measure','Control','Enhanced'],
             [[k,*[f"{summaries[v][k]:.3f}" if isinstance(summaries[v][k],float) else summaries[v][k] for v in ('control','enhanced')]]
              for k in ('annealing_proposals','mechanical_saved_unique','early_full_saved_unique','retained_union',
                        'eligible_full_scored_unique','non_start_eligible_unique','frontier_count','non_start_frontier_count',
                        'mean_mechanical_pair_hamming','summed_seed_seconds')]),'',
        '## Full Balance alternatives','',
        table(['Variant','Candidate','Goti R','Jhor R','New vs starts','Beats other frontier point','Beats a 4b incumbent'],
              [[r['variant'],r['id'],f"{r['R_A']:.6f}",f"{r['R_D']:.6f}",r['not_a_common_start'],
                r['dominates_any_other_frontier'],r['dominates_any_4b_incumbent']] for r in comparison]),'',
        'Lower R is better only within the same mode. Dominance means no worse in both mode-specific scores and strictly better in at least one. More saved layouts alone is not evidence of better layouts: the enhanced retention limit is intentionally larger. Eligible discoveries, non-dominated discoveries, score improvements and compute cost must be considered together. A small paired pilot supplies exploratory evidence, not a probability or proof of superiority.','',
        '## What changed in the search','',
        'Control uses the existing effort/movement proposal objective with a small top-energy archive and full scoring after seed completion. Enhanced protects per-metric representatives and removes near-duplicate assignments from a larger archive. Periodic full-score evaluations seed interleaved one-swap, three-cycle and double-swap exploration; full R controls local acceptance/restarts. The two R numbers are never added. Full-score points are protected from later mechanical pruning.','',
        'Both variants receive the same final full-score neighbor-proposal budget. Enhanced also has additional early full-score work, recorded separately in results.json. Thus any observed gain is a return on extra scoring/retention, not a claim of equal runtime. Controls share initial maps/seeds, but enhanced restarts intentionally change subsequent paths. This combines changes 1 and 2 and does not isolate their individual contributions.','',
        'The common 4-billion candidates are warm starts/comparisons, not new discoveries. Full scoring is still gated by unchanged eligibility, and is bounded per enhanced seed. Known held-out diagnostics run only after training selection is frozen. No held-out outcome tunes the pilot. No published result, layout, challenge score or website number changes. Findings are best found; these metrics are not measured typing speed or comfort.','',
        '## Reproduce','', '```powershell','$env:PYTHONPATH = "src"',
        f"python -m bangla_dh.experimental.shared_explore --out work/evaluator-experiments/shared-explore-repeat --pairs {settings['pairs']} --steps {settings['steps']} --workers {workers}",'```','']
    outputs.append(write_text(target/'REPORT.md','\n'.join(text)))
    for name,d in before.items():assert sha256_file(ROOT/name)==d,name
    assert input_hashes()==inputs
    outputs += [target/'experiment-plan.json',target/'selection.json',*sorted((target/'runs').glob('*.json'))]
    write_json(target/'run-manifest.json',{'version':VERSION,'settings':settings,'workers':workers,
        'input_sha256':inputs,'output_sha256':hash_outputs(outputs),'protected_sha256':before,
        'seeds':sorted(set(r['seed'] for r in runs)),'checks':{'paired_starts_verified':True,
        'proposal_total_verified':True,'model_and_existing_artifacts_preserved':True,'official_exact_finalist_scores':True,
        'full_score_cache_verified_for_finalists':True,'training_selection_frozen':True,'inputs_preserved':True}})
    print('Complete:',target/'REPORT.md',flush=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',required=True)
    parser.add_argument('--pairs',type=int,default=10)
    parser.add_argument('--steps',type=int,default=500000)
    parser.add_argument('--workers',type=int,default=32)
    args=parser.parse_args()
    if min(args.pairs,args.steps,args.workers)<1:parser.error('positive pairs, steps and workers required')
    settings={'pairs':args.pairs,'steps':args.steps,'first_seed':2026113082,'ils_iterations':30,'t_ratio':.0001,
        'control_archive':8,'diverse_archive':64,'frontier_limit':16,'early_full_budget':256,
        'full_interval':50000,'diversity_interval':5000,'early_score_batch':8,'early_neighbor_steps':64,
        'final_neighbor_steps':2048,'total_proposals':2*args.pairs*args.steps,'version':VERSION}
    run(args.out,settings,args.workers)


if __name__=='__main__':main()
