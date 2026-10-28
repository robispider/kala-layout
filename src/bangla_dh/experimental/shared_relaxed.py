"""Shared experiment with owner-requested +0.75% E / +7.5% W caps.

The original Balance v1 implementation, calibration and eligibility stay intact.
This module reuses its score expression under separately named eligibility.
"""
from __future__ import annotations

import argparse
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
from ..paths import PROJECT_ROOT as ROOT, hash_outputs, output_path, repo_state, write_json, write_text
from ..reference import sha256_file
from ..search.anneal import _random_pair
from ..search.problem import slot_name
from .artifact_storage import write_csv
from .balance_study import PairEngine, order_values, preserved_files
from .balance_v1 import evaluate as original_evaluate, cost, credit_deficit
from .inputs import TRAIN, HELDOUT, read_json
from .joint_search import atomic_json, settings_digest
from .mechanics import verify_sources
from .shared_problem import SharedProblem, SharedState, START_IDS
from .shared_search import full_balance_frontier, input_hashes as original_inputs, table

VERSION = 'shared-layout-relaxed-v1'
EFFORT_ALLOWANCE = Fraction(3,400)
WITHIN_ALLOWANCE = .075
PRIOR = ROOT/'results/shared-layout-v1/run-v1'
PRIOR_ID = 'shared-65cdcd9b9364f827'
START_NAMES = (*START_IDS, PRIOR_ID)
_problem = None


def relaxed_evaluate(metrics,calibration):
    """Frozen R expression with new eligibility; never an official v1 rank."""
    original = original_evaluate(metrics,calibration)
    ref = calibration['reference']
    effort = Fraction(metrics['J1_exact']) <= Fraction(ref['J1_exact'])*(1+EFFORT_ALLOWANCE)
    within = metrics['within_distance'] <= ref['within_distance']*(1+WITHIN_ALLOWANCE)+1e-14
    result = {'eligible':effort and within,'effort_cap_pass':effort,'within_cap_pass':within,
              'R':None,'original_balance_v1_eligible':original['eligible'],
              'original_balance_v1_R':original['R'],'score_scope':VERSION,'worst_setting':None}
    if not result['eligible']:
        return result
    _,upper_deficit = credit_deficit(metrics['order_lower'],metrics['order_upper'])
    values = [metrics['J1'],metrics['cross_distance'],metrics['within_distance'],upper_deficit]
    scores = []
    for setting in calibration['settings']:
        b = cost(values,calibration['aspirations'],calibration['scales'],setting['weights'],setting['rho'])
        scores.append((max(0.,b-setting['b_minus']),setting['id'],b,setting['b_minus']))
    if len(scores)!=81:
        raise ValueError('requires all 81 frozen settings')
    worst = max(scores,key=lambda r:(r[0],r[1]))
    result.update(R=worst[0],worst_setting=worst[1],worst_B_plus=worst[2],worst_b_minus=worst[3])
    if original['eligible'] and result['R']!=original['R']:
        raise ValueError('relaxed expression changed an original eligible R')
    return result


def energy(values,references,arm,direction=.5):
    r = [x/ref for x,ref in zip(values,references)]
    if arm=='effort':
        return max(r[:2])-1
    if arm!='balance' or not 0<=direction<=1:
        raise ValueError('invalid arm/direction')
    over = [max(0.,(r[k]-1)/(float(EFFORT_ALLOWANCE) if k<2 else WITHIN_ALLOWANCE)-1) for k in range(4)]
    secondary = (1-direction)*(r[4]+r[5])/2+direction*(r[2]+r[3])/2+.05*(r[0]+r[1])/2
    return max(over)+.001*sum(over)+.0001*secondary


class RelaxedProblem(SharedProblem):
    def __init__(self):
        super().__init__()
        layout = {s:tuple(v.split('/')) for s,v in read_json(PRIOR/'layouts'/(PRIOR_ID+'.json'))['layout'].items()}
        self.starts.append(self.perm_of(layout))

    def eligible_fast(self,values):
        return all(values[k]<=self.references[k]*(1+(float(EFFORT_ALLOWANCE) if k<2 else WITHIN_ALLOWANCE))+1e-12
                   for k in range(4))

    def evaluate_training(self,perm,with_order=True):
        scores = super().evaluate_training(perm,with_order)
        if with_order:
            for style in ('A','D'):
                scores[style]['balance'] = relaxed_evaluate(scores[style]['metrics'],self.config['styles'][style])
        return scores


class RelaxedState(SharedState):
    @property
    def energy(self):
        return energy([s.score for s in self.states],self.problem.references,self.arm,self.direction)

    def delta(self,i,j):
        changes = [s.delta(i,j) for s in self.states]
        new = energy([s.score+d for s,d in zip(self.states,changes)],self.problem.references,self.arm,self.direction)
        return new-self.energy,changes


def initialize():
    global _problem
    _problem = RelaxedProblem()


def search_one(problem,job,settings):
    arm,ordinal,seed = job
    rng = random.Random(seed)
    kind = ordinal % 7
    direction = (0.,.5,1.)[ordinal % 3]
    if kind<5:
        start,name = list(problem.starts[kind]),START_NAMES[kind]
    elif kind==5:
        start,name = list(problem.starts[4]),'perturbed-'+PRIOR_ID
        for _ in range(8):
            i,j = _random_pair(rng,problem.n)
            start[i],start[j] = start[j],start[i]
    else:
        start,name = list(range(problem.n)),'random'
        rng.shuffle(start)
    state = RelaxedState(problem,start,arm,direction)
    retained = {}
    def offer():
        key = tuple(state.perm)
        retained[key] = {'perm':list(key),'energy':state.energy}
        if len(retained)>settings['archive_limit']:
            del retained[max(retained,key=lambda k:(retained[k]['energy'],k))]
    def descend():
        moves = 0
        while True:
            best,selected = -1e-12,None
            for i in range(problem.n-1):
                for j in range(i+1,problem.n):
                    d,ds = state.delta(i,j)
                    if d<best:
                        best,selected = d,(i,j,ds)
            if selected is None:
                offer()
                return moves
            state.swap(*selected)
            moves += 1
    started = time.perf_counter()
    offer()
    best,best_perm = state.energy,list(state.perm)
    uphill = [d for d in (state.delta(*_random_pair(rng,problem.n))[0] for _ in range(512)) if d>0]
    t0 = sum(uphill)/len(uphill)/math.log(2) if uphill else .001
    temperature = t0
    factor = settings['t_ratio']**(1/max(1,settings['steps']-1))
    accepted = 0
    for _ in range(settings['steps']):
        i,j = _random_pair(rng,problem.n)
        d,ds = state.delta(i,j)
        if d<=0 or rng.random()<math.exp(-d/temperature):
            state.swap(i,j,ds)
            accepted += 1
            if accepted % 10000 == 0:
                state.reset(state.perm)
            if state.energy<best-1e-12:
                best,best_perm = state.energy,list(state.perm)
                offer()
        temperature *= factor
    state.reset(best_perm)
    moves = descend()
    best,best_perm = state.energy,list(state.perm)
    improvements = 0
    for _ in range(settings['ils_iterations']):
        for _ in range(rng.randint(2,6)):
            i,j = _random_pair(rng,problem.n)
            _,ds = state.delta(i,j)
            state.swap(i,j,ds)
        moves += descend()
        if state.energy<best-1e-12:
            best,best_perm = state.energy,list(state.perm)
            improvements += 1
        else:
            state.reset(best_perm)
    state.reset(best_perm)
    offer()
    # The attained endpoint remains protected independently of archive pruning.
    retained[tuple(state.perm)] = {'perm':list(state.perm),'energy':state.energy}
    return {'id':f'{arm}-{seed}','version':VERSION,'settings_sha256':settings_digest(settings),
            'arm':arm,'seed':seed,'ordinal':ordinal,'start':name,'direction':direction,
            'accepted':accepted,'descent_moves':moves,'ils_improvements':improvements,'initial_temperature':t0,
            'endpoint':list(state.perm),'archive':sorted(retained.values(),key=lambda r:(r['energy'],r['perm'])),
            'seconds':round(time.perf_counter()-started,3)}


def worker(args):
    return search_one(_problem,*args)


def input_hashes():
    paths = [ROOT/'results/shared-layout-relaxed-v1/README.md',ROOT/'tests/test_shared_relaxed.py',
             PRIOR/'run-manifest.json',PRIOR/'results.json',PRIOR/'layouts'/(PRIOR_ID+'.json')]
    return {**original_inputs(),**hash_outputs(paths)}


def prepare(out,settings,inputs,resume=False):
    target = Path(out).resolve()
    if not any(target.is_relative_to(r.resolve()) and target!=r.resolve()
               for r in (ROOT/'results/shared-layout-relaxed-v1',ROOT/'work/evaluator-experiments')):
        raise ValueError('output must be a new relaxed-experiment or workspace experiment child')
    state = {'version':VERSION,'settings':settings,'input_sha256':inputs,
             'python':platform.python_version(),'platform':platform.platform()}
    if not resume:
        if target.exists():
            raise FileExistsError('run exists; choose a new directory or explicit --resume')
        before = preserved_files(target)
        write_json(target/'search-plan.json',{**state,'protected_sha256':before})
        atomic_json(target/'progress.json',{'completed':{}})
    else:
        saved = read_json(target/'search-plan.json')
        if any(saved.get(k)!=v for k,v in state.items()):
            raise ValueError('resume refused: inputs, code, settings or environment changed')
        if (target/'run-manifest.json').exists():
            raise ValueError('completed run cannot be overwritten')
        before = saved['protected_sha256']
        for name,digest in before.items():
            if sha256_file(ROOT/name)!=digest:
                raise ValueError('protected file changed: '+name)
    jobs = {f'{arm}-{settings["first_seed"]+offset+ordinal}':(arm,ordinal,settings['first_seed']+offset+ordinal)
            for arm,offset in (('effort',0),('balance',100000)) for ordinal in range(settings['seeds'])}
    progress = read_json(target/'progress.json')
    for path in sorted((target/'runs').glob('*.json')):
        if path.stem not in jobs:
            raise ValueError('unexpected checkpoint')
        data = read_json(path)
        arm,ordinal,seed = jobs[path.stem]
        if (data.get('version'),data.get('settings_sha256'),data.get('id'),data.get('arm'),data.get('ordinal'),data.get('seed')) != (
                VERSION,settings_digest(settings),path.stem,arm,ordinal,seed):
            raise ValueError('invalid checkpoint provenance')
        digest = sha256_file(path)
        if path.stem in progress['completed'] and progress['completed'][path.stem]!=digest:
            raise ValueError('checkpoint hash mismatch')
        progress['completed'][path.stem] = digest
    for name,digest in progress['completed'].items():
        if name not in jobs or sha256_file(target/'runs'/(name+'.json'))!=digest:
            raise ValueError('checkpoint missing or hash mismatch')
    atomic_json(target/'progress.json',progress)
    return target,before,progress,jobs


def finish(target,settings,inputs,before,progress,workers):
    problem = RelaxedProblem()
    candidates = {tuple(p):{'perm':p,'origins':['start:'+identity]} for identity,p in zip(START_NAMES,problem.starts)}
    for name in sorted(progress['completed']):
        for r in read_json(target/'runs'/(name+'.json'))['archive']:
            perm = r['perm']
            problem.assignment(perm)
            candidates.setdefault(tuple(perm),{'perm':perm,'origins':[]})['origins'].append(name)
    pool = []
    for row in candidates.values():
        perm = row['perm']
        exact = [problem.exact_effort(perm,s) for s in ('A','D')]
        values = problem.values(perm)
        if any(abs(float(exact[k])-values[k])>1e-10 for k in range(2)):
            raise ValueError('integer effort disagrees')
        row.update(values=values,J1_exact=list(map(str,exact)))
        pool.append(row)
    refs = [Fraction(problem.config['styles'][s]['reference']['J1_exact']) for s in ('A','D')]
    def effort_key(row):
        ratios = [Fraction(row['J1_exact'][k])/refs[k] for k in range(2)]
        return max(ratios),sum(ratios),row['perm']
    best = min(pool,key=effort_key)
    print('Seed search complete. Full relaxed-eligibility Balance scoring/refinement.',flush=True)
    frontier,refinement = full_balance_frontier(problem,[r['perm'] for r in pool],settings)
    selected = {}
    def select(perm,role):
        layout = problem.assignment(perm)
        cid = 'shared-'+hashlib.sha256(json.dumps(sorted(layout.items()),ensure_ascii=False).encode()).hexdigest()[:16]
        selected.setdefault(cid,{'id':cid,'perm':perm,'roles':[]})['roles'].append(role)
    select(best['perm'],'lowest retained exact worst relative J1')
    for r in frontier:
        select(r['perm'],'relaxed-eligibility R_A/R_D Pareto alternative')
    if not frontier:
        closest = min(pool,key=lambda r:(energy(r['values'],problem.references,'balance'),r['perm']))
        select(closest['perm'],'closest retained relaxed-restoration endpoint; ineligible')
    for name,perm in zip(START_NAMES,problem.starts):
        select(perm,'comparison: '+name)
    write_json(target/'selection.json',{'basis':'training only; relaxed eligibility','selected':list(selected.values()),
                                      'frontier':frontier,'refinement':refinement})
    selection_hash = sha256_file(target/'selection.json')
    write_json(target/'training-pool.json',{'candidates':pool,'heldout_used_for_selection':False,'bounded_archives':True})
    outputs,summary,rows = [],[],[]
    public = challenge.load_scorer(challenge.SCRIPT)
    data,data_hash = public.load_data()
    model = public.Model(data)
    for cid,row in selected.items():
        perm = row['perm']
        layout = problem.assignment(perm)
        training = problem.evaluate_training(perm)
        for s in ('A','D'):
            result = public.evaluate({'name':cid,'style':s,'layout':challenge._key_layout(layout)},data,data_hash,model)
            if not result['valid'] or Fraction(result['J1_exact'])!=Fraction(training[s]['metrics']['J1_exact']):
                raise ValueError('official exact challenge scorer disagrees')
        summary.append({'id':cid,'roles':row['roles'],'training':training,
                        'jointly_eligible':all(training[s]['balance']['eligible'] for s in ('A','D'))})
        outputs.append(write_json(target/'layouts'/(cid+'.json'),{'id':cid,'experiment':VERSION,'experimental_only':True,
                       'styles':['A','D'],'layout':{s:slot_name(v) for s,v in layout.items()},'roles':row['roles'],
                       'application_export':False}))
    print('Selection frozen. Evaluating held-out/fingering diagnostics.',flush=True)
    for style in ('A','D'):
        for fingering in ('model-optimal','traditional'):
            for corpus in (*TRAIN,*HELDOUT):
                engine = PairEngine(style,corpus,fingering)
                for cid,row in selected.items():
                    layout = problem.assignment(row['perm'])
                    metrics = engine.evaluate(layout)
                    metrics.update(order_values(style,corpus,fingering,layout))
                    rows.append({'id':cid,'style':style,'fingering':fingering,'corpus':corpus,**metrics})
    if sha256_file(target/'selection.json')!=selection_hash:
        raise ValueError('selection changed during held-out diagnostics')
    outputs += [write_csv(target/'scores.csv',rows),write_json(target/'results.json',{'selected':summary,
                'refinement':refinement,'jointly_eligible_frontier_count':len(frontier),'retained_pool_count':len(pool),
                'original_worst_relative_J1_exact':str(effort_key(best)[0]-1)})]
    text = ['# Shared-layout experiment: relaxed eligibility','',
            '**Owner-requested limits: +0.75% J1 effort and +7.5% within-word SF distance, separately for Goti and Jhor.** This is a new experimental eligibility policy chosen after examining v1; it is not independent confirmation or an official Balance v1 ranking. Frozen Balance v1 aspirations, scales, settings, order bounds and calibration constants remain unchanged.','',
            f"Completed {2*settings['seeds']} seed runs on {workers} workers, {2*settings['seeds']*settings['steps']:,} annealing proposals plus local search; {len(pool)} distinct retained shared maps. Full score refinement: {refinement}.",'',
            f'**{len(frontier)} retained jointly eligible relaxed-score Pareto alternatives.** A and D R values retain separate calibration and are never added or compared across styles. No single Balance winner is asserted.','',
            '## Training-selected maps','',
            'Changes compare with each mode\'s original published map on the independently normalized 50/50 training mix and model-optimal fingering. R below means the unchanged frozen expression evaluated under this experiment\'s relaxed eligibility. Separate original Balance v1 flags are saved in results.json.','']
    values = []
    for r in summary:
        line = [r['id'],'; '.join(r['roles'])]
        for s in ('A','D'):
            m,b = r['training'][s]['metrics'],r['training'][s]['balance']
            ref = problem.config['styles'][s]['reference']
            line += [f"{100*(m['J1']/ref['J1']-1):+.3f}%",f"{100*(m['within_distance']/ref['within_distance']-1):+.2f}%",
                     f"{100*(m['cross_distance']/ref['cross_distance']-1):+.2f}%",f"{b['R']:.6f}" if b['eligible'] else 'ineligible']
        values.append(line)
    text += [table(['Assignment','Role','A effort','A within','A cross','A R','D effort','D within','D cross','D R'],values),'',
             f"The lowest retained worst relative J1 loss is {100*float(effort_key(best)[0]-1):.4f}%. This is a finite best-found result; it carries no optimality or comfort proof.",'',
             '## Protocol, reproducibility and limits','',
             'The original-effort objective is unchanged. Mechanical proposal energy replaces allowances 0.005/0.05 by 0.0075/0.075 in the separately recorded v1 exploration formula. Actual relaxed eligibility uses exact rational effort and direct-distance comparisons with tolerance 1e-14. Full R scoring/refinement follows proposal generation; it does not occur in every annealing step.','',
             'Both original maps, both original Balance leaders and the earlier shared best are retained as starting/comparison maps. Per-run archives and the R frontier are bounded and may miss improvements. The full-score frontier uses componentwise same-style dominance. Known held-out data never tune limits, search parameters or selection. Selection is frozen before all held-out/fingering diagnostics. Scores are modeled mechanics, not measured speed, learning or comfort.','',
             'Research assignment files are not Kala app imports. Published layouts, frozen scoring, challenge acceptance and website numbers remain unchanged.','',
             '```powershell','$env:PYTHONPATH = "src"',
             f"python -m bangla_dh.experimental.shared_relaxed --out work/evaluator-experiments/shared-relaxed-repeat --seeds {settings['seeds']} --steps {settings['steps']} --ils-iterations {settings['ils_iterations']} --workers {workers} --first-seed {settings['first_seed']} --archive-limit {settings['archive_limit']} --frontier-limit {settings['frontier_limit']} --balance-refine-steps {settings['balance_refine_steps']}",
             '```','', 'Use --resume after interruption with identical settings. Completed runs cannot be overwritten.','']
    outputs.append(write_text(target/'REPORT.md','\n'.join(text)))
    for name,digest in before.items():
        if sha256_file(ROOT/name)!=digest:
            raise ValueError('protected artifact changed: '+name)
    if input_hashes()!=inputs:
        raise ValueError('inputs or code changed during run')
    outputs += [target/'search-plan.json',target/'progress.json',target/'selection.json',target/'training-pool.json']
    outputs += sorted((target/'runs').glob('*.json'))
    head,clean = repo_state()
    write_json(target/'run-manifest.json',{'version':VERSION,'settings':settings,'workers':workers,
               'input_sha256':inputs,'output_sha256':hash_outputs(outputs),'protected_sha256':before,
               'seeds':sorted(progress['completed']),'repository_commit':head,'working_tree_clean':clean,
               'python':platform.python_version(),'platform':platform.platform(),
               'checks':{'official_exact_challenge_scores_agree':True,'integer_and_independent_metrics_agree':True,
               'original_balance_formula_preserved':True,'published_artifacts_preserved':True,
               'training_selection_frozen_before_heldout':True,'inputs_and_code_preserved':True}})
    print('Complete:',target/'REPORT.md',flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',required=True)
    parser.add_argument('--seeds',type=int,default=250)
    parser.add_argument('--steps',type=int,default=200000)
    parser.add_argument('--ils-iterations',type=int,default=30)
    parser.add_argument('--workers',type=int,default=28)
    parser.add_argument('--first-seed',type=int,default=2026102832)
    parser.add_argument('--archive-limit',type=int,default=8)
    parser.add_argument('--frontier-limit',type=int,default=8)
    parser.add_argument('--balance-refine-steps',type=int,default=2048)
    parser.add_argument('--resume',action='store_true')
    args = parser.parse_args()
    if min(args.seeds,args.steps,args.workers)<1 or min(args.ils_iterations,args.balance_refine_steps)<0:
        parser.error('positive seeds/steps/workers; nonnegative ILS/refinement')
    if min(args.archive_limit,args.frontier_limit)<2:
        parser.error('archive limits must be at least 2')
    settings = {k:v for k,v in vars(args).items() if k not in ('out','workers','resume')}
    settings.update(t_ratio=.0001,effort_allowance_exact=str(EFFORT_ALLOWANCE),within_allowance=WITHIN_ALLOWANCE,
                    version=VERSION,prior_shared_start=PRIOR_ID,calibration='unchanged frozen Balance v1')
    verify_sources()
    inputs = input_hashes()
    target,before,progress,jobs = prepare(args.out,settings,inputs,args.resume)
    pending = [(job,settings) for name,job in jobs.items() if name not in progress['completed']]
    print(f'Frozen relaxed protocol: {len(jobs)} seeds, {len(pending)} pending; {args.workers} workers.',flush=True)
    if pending:
        with mp.Pool(args.workers,initializer=initialize) as pool:
            for result in pool.imap_unordered(worker,pending):
                path = atomic_json(target/'runs'/(result['id']+'.json'),result)
                progress['completed'][result['id']] = sha256_file(path)
                atomic_json(target/'progress.json',progress)
                print(f"{len(progress['completed'])}/{len(jobs)} {result['id']}: {result['seconds']:.1f}s",flush=True)
    finish(target,settings,inputs,before,progress,args.workers)


if __name__=='__main__':
    main()
