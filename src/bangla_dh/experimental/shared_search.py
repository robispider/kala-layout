"""Shared-layout v1: two-style effort search and Balance-constrained exploration.

Run as a module from the command line (Windows multiprocessing spawn).
All selection uses training only; held-out diagnostics run after selection.
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
from ..search.problem import PROBLEM_FILE, slot_name
from .artifact_storage import write_csv
from .balance_study import PairEngine, average, order_values, preserved_files
from .continuous_counts import DEFAULT
from .inputs import TRAIN, HELDOUT, frequency_path, unit_path, read_json
from .joint_search import atomic_json, settings_digest
from .mechanics import verify_sources
from .mechanics_sources import SOURCE, PORTS, GENERATORS
from .shared_problem import CONFIG, START_IDS, SharedProblem, SharedState, pareto_offer, search_energy

VERSION = 'shared-layout-v1'
FIRST_SEED = 2026102800
DIRECTIONS = (0., .5, 1.)
_problem = None


def initialize():
    global _problem
    _problem = SharedProblem()


def search_one(problem, job, settings):
    arm, ordinal, seed = job
    rng = random.Random(seed)
    direction = DIRECTIONS[ordinal % len(DIRECTIONS)]
    if ordinal % 6 < 4:
        start = problem.starts[ordinal % 6]
        start_name = START_IDS[ordinal % 6]
    elif ordinal % 6 == 4:
        start = list(problem.starts[ordinal % 4])
        for _ in range(8):
            i,j = _random_pair(rng,problem.n)
            start[i],start[j] = start[j],start[i]
        start_name = 'perturbed-'+START_IDS[ordinal % 4]
    else:
        start = list(range(problem.n))
        rng.shuffle(start)
        start_name = 'random'
    state = SharedState(problem,start,arm,direction)
    retained = {}

    def offer():
        key = tuple(state.perm)
        retained[key] = {'perm':list(key),'energy':state.energy}
        if len(retained)>settings['archive_limit']:
            worst = max(retained,key=lambda k:(retained[k]['energy'],k))
            del retained[worst]

    def descend():
        moves = 0
        while True:
            best, selected = -1e-12,None
            for i in range(problem.n-1):
                for j in range(i+1,problem.n):
                    d,changes = state.delta(i,j)
                    if d<best:
                        best,selected = d,(i,j,changes)
            if selected is None:
                offer()
                return moves
            state.swap(*selected)
            moves += 1

    started = time.perf_counter()
    offer()
    best_energy,best_perm = state.energy,list(state.perm)
    uphill = [v for v in (state.delta(*_random_pair(rng,problem.n))[0] for _ in range(512)) if v>0]
    t0 = sum(uphill)/len(uphill)/math.log(2) if uphill else .001
    temperature = t0
    factor = settings['t_ratio']**(1/max(1,settings['steps']-1))
    accepted = 0
    for _ in range(settings['steps']):
        i,j = _random_pair(rng,problem.n)
        d,changes = state.delta(i,j)
        if d<=0 or rng.random()<math.exp(-d/temperature):
            state.swap(i,j,changes)
            accepted += 1
            if accepted % 10000 == 0:
                state.reset(state.perm)
            if state.energy<best_energy-1e-12:
                best_energy,best_perm = state.energy,list(state.perm)
                offer()
        temperature *= factor
    state.reset(best_perm)
    descent_moves = descend()
    best_energy,best_perm = state.energy,list(state.perm)
    improvements = 0
    for _ in range(settings['ils_iterations']):
        for _ in range(rng.randint(2,6)):
            i,j = _random_pair(rng,problem.n)
            _,changes = state.delta(i,j)
            state.swap(i,j,changes)
        descent_moves += descend()
        if state.energy<best_energy-1e-12:
            best_energy,best_perm = state.energy,list(state.perm)
            improvements += 1
        else:
            state.reset(best_perm)
    state.reset(best_perm)
    offer()
    for row in retained.values():
        problem.assignment(row['perm'])
    return {'id':f'{arm}-{seed}','version':VERSION,'settings_sha256':settings_digest(settings),
            'arm':arm,'seed':seed,'ordinal':ordinal,'start':start_name,'direction':direction,
            'initial_temperature':t0,'accepted':accepted,'descent_moves':descent_moves,'ils_improvements':improvements,
            'endpoint':list(state.perm),'archive':sorted(retained.values(),key=lambda r:(r['energy'],r['perm'])),
            'seconds':round(time.perf_counter()-started,3)}


def search_job(args):
    job,settings = args
    return search_one(_problem,job,settings)


def input_hashes():
    paths = [CONFIG,PROBLEM_FILE,ROOT/'challenge/challenge-data.json',challenge.SCRIPT,
             ROOT/'results/shared-layout-v1/README.md',ROOT/'tests/test_shared_search.py']
    paths += [ROOT/'results/balance-v1/layouts'/(i+'.json') for i in START_IDS]
    paths += list((ROOT/'src/bangla_dh').rglob('*.py'))
    paths += list((ROOT/'results/phase1/effort-grids').glob('ansi-*.json'))
    paths += [SOURCE/'source-lock.json']+[SOURCE/e['file'] for e in read_json(SOURCE/'source-lock.json')['files']]
    paths += [PORTS/(name+'.py') for name in GENERATORS]
    for style in ('A','D'):
        for corpus in (*TRAIN,*HELDOUT):
            paths += [frequency_path(style,corpus),unit_path(corpus)]
            for season in ('e2','e3'):
                root = ROOT/f'results/evaluator-{season}/run-v1'
                paths += [root/'run-manifest.json',root/'counts'/f'style-{style.lower()}-{corpus.replace("/","-")}.json.gz']
    return hash_outputs(sorted(set(paths)))


def checked_target(out):
    target = Path(out).resolve()
    if not any(target.is_relative_to(root.resolve()) and target!=root.resolve()
               for root in (ROOT/'results/shared-layout-v1',ROOT/'work/evaluator-experiments')):
        raise ValueError('output must be a new child of results/shared-layout-v1 or work/evaluator-experiments')
    return target


def prepare(out,settings,inputs,resume=False):
    target = checked_target(out)
    state = {'version':VERSION,'settings':settings,'input_sha256':inputs,
             'python':platform.python_version(),'platform':platform.platform()}
    if not resume:
        if target.exists():
            raise FileExistsError('run exists; use a new directory or explicit --resume')
        before = preserved_files(target)
        write_json(target/'search-plan.json',{**state,'protected_sha256':before})
        atomic_json(target/'progress.json',{'completed':{}})
    else:
        saved = read_json(target/'search-plan.json')
        if any(saved.get(k)!=v for k,v in state.items()):
            raise ValueError('resume refused: code, inputs, settings or environment changed')
        if (target/'run-manifest.json').exists():
            raise ValueError('completed run cannot be overwritten')
        before = saved['protected_sha256']
        for name,digest in before.items():
            if sha256_file(ROOT/name)!=digest:
                raise ValueError('resume refused: protected file changed: '+name)
    progress = read_json(target/'progress.json')
    jobs = {(f'{arm}-{settings["first_seed"]+offset+ordinal}'):(arm,ordinal,settings['first_seed']+offset+ordinal)
            for arm,offset in (('effort',0),('balance',100000)) for ordinal in range(settings['seeds'])}
    for path in sorted((target/'runs').glob('*.json')):
        if path.stem not in jobs:
            raise ValueError('unexpected checkpoint identity')
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


def full_balance_frontier(problem,perms,settings):
    """Full four-component R evaluations and training-only random-swap refinement.

    Feasibility uses independent exact E plus direct W. Pareto dominance compares
    A with A and D with D. Bounded pruning is by A-order indices, preserving
    the endpoints; there is no uncalibrated sum or maximum of A/D R.
    """
    archive,cache = [],{}
    evaluated = feasible = 0

    def offer(perm):
        nonlocal evaluated,feasible
        key = tuple(perm)
        if key in cache:
            return
        values = problem.values(perm)
        if not problem.eligible_fast(values):
            return
        scores = problem.evaluate_training(perm)
        evaluated += 1
        allowed = all(scores[s]['balance']['eligible'] for s in ('A','D'))
        cache[key] = allowed
        if allowed:
            feasible += 1
            pareto_offer(archive,{'perm':list(perm),'R':[scores[s]['balance']['R'] for s in ('A','D')]},settings['frontier_limit'])

    for perm in perms:
        offer(perm)
    initial = len(archive)
    rng = random.Random(settings['first_seed']+999999)
    proposals = 0
    for _ in range(settings['balance_refine_steps']):
        if not archive:
            break
        base = archive[rng.randrange(len(archive))]['perm']
        candidate = list(base)
        i,j = _random_pair(rng,problem.n)
        candidate[i],candidate[j] = candidate[j],candidate[i]
        offer(candidate)
        proposals += 1
    return archive,{'initial_frontier':initial,'refine_proposals':proposals,
                    'full_R_evaluations':evaluated,'jointly_eligible_evaluations':feasible}


def table(headers,rows):
    return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+
                     ['| '+' | '.join(map(str,r))+' |' for r in rows])


def finish(target,settings,before,progress,inputs,workers):
    problem = SharedProblem()
    candidates = {tuple(p):{'perm':p,'origins':['starting-map:'+identity]}
                  for identity,p in zip(START_IDS,problem.starts)}
    for name in sorted(progress['completed']):
        run = read_json(target/'runs'/(name+'.json'))
        for r in run['archive']:
            perm = r['perm']
            problem.assignment(perm)
            key = tuple(perm)
            candidates.setdefault(key,{'perm':perm,'origins':[]})['origins'].append(name)
    # Recompute every retained candidate; no trust in worker scalar energies.
    pool = []
    for row in candidates.values():
        perm = row['perm']
        values = problem.values(perm)
        exact = [problem.exact_effort(perm,s) for s in ('A','D')]
        if any(abs(float(exact[k])-values[k])>1e-10 for k in range(2)):
            raise ValueError('retained candidate effort mismatch')
        row.update(values=values,J1_exact=list(map(str,exact)))
        pool.append(row)
    # Exact rational comparison for the original arm's final minimax selection.
    refs = [Fraction(problem.config['styles'][s]['reference']['J1_exact']) for s in ('A','D')]
    def effort_key(row):
        ratios = [Fraction(row['J1_exact'][i])/refs[i] for i in range(2)]
        return max(ratios),sum(ratios),row['perm']
    original = min(pool,key=effort_key)
    frontier,refinement = full_balance_frontier(problem,[r['perm'] for r in pool],settings)
    selected = {}
    def select(perm,role):
        layout = problem.assignment(perm)
        identity = 'shared-'+hashlib.sha256(json.dumps(sorted(layout.items()),ensure_ascii=False).encode()).hexdigest()[:16]
        selected.setdefault(identity,{'id':identity,'perm':perm,'roles':[]})['roles'].append(role)
    select(original['perm'],'lowest retained exact worst relative J1')
    for row in frontier:
        select(row['perm'],'jointly eligible full Balance v1 Pareto frontier')
    # Keep the closest mechanical restoration endpoint when no map is eligible.
    closest = min(pool,key=lambda r:(search_energy(r['values'],problem.references,'balance',.5),r['perm']))
    if not frontier:
        select(closest['perm'],'closest retained Balance constraint-restoration candidate; ineligible')
    for identity,perm in zip(START_IDS,problem.starts):
        select(perm,'existing comparison: '+identity)
    # This immutable logical selection precedes all held-out reads/scoring.
    write_json(target/'selection.json',{'basis':'training only','selected':list(selected.values()),
                                      'balance_frontier':frontier,'refinement':refinement})
    selection_hash = sha256_file(target/'selection.json')
    write_json(target/'training-pool.json',{'candidates':pool,'bounded_archives':True,
                                          'heldout_used_for_selection':False})
    public = challenge.load_scorer(challenge.SCRIPT)
    public_data,data_hash = public.load_data()
    public_model = public.Model(public_data)
    rows,summary,outputs = [],[],[]
    for identity,selected_row in selected.items():
        perm = selected_row['perm']
        layout = problem.assignment(perm)
        train = problem.evaluate_training(perm)
        for style in ('A','D'):
            submission = {'name':identity,'style':style,'layout':challenge._key_layout(layout)}
            official = public.evaluate(submission,public_data,data_hash,public_model)
            if not official['valid'] or Fraction(official['J1_exact'])!=Fraction(train[style]['metrics']['J1_exact']):
                raise ValueError('official challenge scorer disagrees')
        outputs.append(write_json(target/'layouts'/(identity+'.json'),{'id':identity,'experimental_only':True,
                    'styles':['A','D'],'layout':{s:slot_name(slot) for s,slot in layout.items()},
                    'roles':selected_row['roles'],'application_export':False}))
        summary.append({'id':identity,'roles':selected_row['roles'],'training':train,
                        'jointly_eligible':all(train[s]['balance']['eligible'] for s in ('A','D'))})
    print('Training selection frozen. Evaluating held-out diagnostics.',flush=True)
    # Primary and traditional diagnostics: independent encoders, five sources.
    for style in ('A','D'):
        for fingering in ('model-optimal','traditional'):
            for corpus in (*TRAIN,*HELDOUT):
                engine = PairEngine(style,corpus,fingering)
                for identity,s in selected.items():
                    layout = problem.assignment(s['perm'])
                    metrics = engine.evaluate(layout)
                    metrics.update(order_values(style,corpus,fingering,layout))
                    rows.append({'id':identity,'style':style,'corpus':corpus,'fingering':fingering,**metrics})
    if sha256_file(target/'selection.json')!=selection_hash:
        raise ValueError('selection changed during held-out evaluation')
    csv_path = write_csv(target/'scores.csv',rows)
    outputs += [csv_path,write_json(target/'results.json',{'selected':summary,'refinement':refinement,
                 'original_worst_relative_J1_exact':str(effort_key(original)[0]-1),
                 'jointly_eligible_frontier_count':len(frontier),'retained_pool_count':len(pool)})]
    text = ['# Shared-layout v1 experiment','',
            'One identical 52-symbol assignment serves Goti (A) and Jhor (D). This is an experimental search; all published layouts and frozen scores remain the references. Results are best found, not proven optimal.','',
            f"Run: {settings['seeds']} seeds per arm, {2*settings['seeds']} total; {settings['steps']:,} annealing proposals and {settings['ils_iterations']} ILS trials per seed. The bounded retained pool has {len(pool)} distinct assignments. Full Balance refinement: {refinement}.",'',
            '## Training-selected candidates','',
            'Changes are against the original layout of each mode on the original 50/50 training mix and model-optimal fingering. Effort and within-word distance caps remain +0.5% and +5%. R values have separate style calibration and are never added or compared across styles.','']
    display_rows=[]
    for r in summary:
        item=[r['id'], '; '.join(r['roles'])]
        for style in ('A','D'):
            score = r['training'][style]
            m,bal = score['metrics'],score['balance']
            ref = problem.config['styles'][style]['reference']
            item += [f"{100*(m['J1']/ref['J1']-1):+.3f}%",f"{100*(m['within_distance']/ref['within_distance']-1):+.2f}%",
                     f"{bal['R']:.6f}" if bal['eligible'] else 'ineligible']
        display_rows.append(item)
    text += [table(['Assignment','Role','A effort','A within distance','A R','D effort','D within distance','D R'],display_rows),'',
             f"**{len(frontier)} retained jointly eligible Balance frontier maps.** Finding none is not proof of impossibility. The lowest retained worst relative effort increase is {100*float(effort_key(original)[0]-1):.4f}%. It is selected with exact rational scores; a sum of the two effort ratios breaks ties only.",'',
             '## Best retained effort arrangement','',
             'Upper rows are Shift; lower rows are base. Vowel symbols identify the shared key; the selected mode determines their behavior.','']
    inverse = {slot:s for s,slot in problem.assignment(original['perm']).items()}
    for keys in ('QWERTYUIOP','ASDFGHJKL','ZXCVBNM'):
        text += [table(['Layer',*keys],[[layer,*[inverse[k,layer] for k in keys]] for layer in ('shift','base')]),'']
    text += ['## Protocol and interpretation','',
             'The effort arm minimizes max(E_A/E_Aref, E_D/E_Dref)−1. The balance arm explores the largest normalized violation of the two effort and two within-word caps, with a declared small movement guidance term and three cross/within priorities. That proposal objective is not Balance v1 R. Every retained mechanically feasible candidate is rescored using full frozen four-component Balance v1, including order-coverage bounds. Further seeded pair-swap proposals refine a bounded R_A/R_D Pareto archive using training only. See the frozen search-plan.json and protocol README for exact formulas and limits.','',
             'No raw A/D R sum, shared comfort score or transferred optimality certificate is introduced. Archive bounds and finite stochastic search can miss eligible candidates and Pareto improvements. Starting maps include the original and Balance leaders; original-arm and balance-arm proposals share the final training-only candidate pool. Full Balance scoring follows mechanical exploration rather than entering every annealing proposal.','',
             'selection.json was frozen before held-out evaluation. scores.csv includes every selected assignment under both modes, all five existing text sets and both fingerings. The three known held-out sets remain exploratory diagnostics; no held-out value changes selection or parameters. These metrics are modeled effort and mechanics, not measured speed, learning or comfort.','',
             'Layout files are research assignments with both supported styles; they are not application-ready Kala imports. Switching modes also changes vowel-entry rules, even though all physical positions stay fixed.','',
             '## Reproduce','', '```powershell','$env:PYTHONPATH = "src"',
             f"python -m bangla_dh.experimental.shared_search --out work/evaluator-experiments/shared-repeat --seeds {settings['seeds']} --steps {settings['steps']} --ils-iterations {settings['ils_iterations']} --workers {workers} --first-seed {settings['first_seed']} --archive-limit {settings['archive_limit']} --frontier-limit {settings['frontier_limit']} --balance-refine-steps {settings['balance_refine_steps']}",
             '```','', 'For interruption recovery repeat with --resume. Completed outputs cannot be overwritten.','']
    outputs.append(write_text(target/'REPORT.md','\n'.join(text)))
    for name,digest in before.items():
        if sha256_file(ROOT/name)!=digest:
            raise ValueError('protected original changed: '+name)
    if input_hashes()!=inputs:
        raise ValueError('input/code changed during the run')
    outputs += [target/'selection.json',target/'training-pool.json',target/'search-plan.json',target/'progress.json']
    outputs += sorted((target/'runs').glob('*.json'))
    head,clean = repo_state()
    write_json(target/'run-manifest.json',{'version':VERSION,'settings':settings,'input_sha256':inputs,
               'output_sha256':hash_outputs(outputs),'seeds':[r for r in sorted(progress['completed'])],
               'repository_commit':head,'working_tree_clean':clean,'workers':workers,
               'python':platform.python_version(),'platform':platform.platform(),
               'protected_sha256':before,'checks':{'official_exact_challenge_scores_agree':True,
               'integer_and_independent_metrics_agree':True,'published_artifacts_preserved':True,
               'training_selection_frozen_before_heldout':True,'inputs_and_code_preserved':True}})
    print('Complete:',target/'REPORT.md',flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',required=True)
    parser.add_argument('--seeds',type=int,default=32,help='per arm; total is twice this')
    parser.add_argument('--steps',type=int,default=200000)
    parser.add_argument('--ils-iterations',type=int,default=30)
    parser.add_argument('--first-seed',type=int,default=FIRST_SEED)
    parser.add_argument('--workers',type=int,default=max(1,min(8,mp.cpu_count()-2)))
    parser.add_argument('--archive-limit',type=int,default=8)
    parser.add_argument('--frontier-limit',type=int,default=8)
    parser.add_argument('--balance-refine-steps',type=int,default=2048)
    parser.add_argument('--resume',action='store_true')
    args = parser.parse_args()
    if min(args.seeds,args.steps,args.workers)<1 or args.ils_iterations<0 or args.balance_refine_steps<0:
        parser.error('positive seeds/steps/workers and nonnegative ILS/refinement required')
    if args.archive_limit<2 or args.frontier_limit<2:
        parser.error('archive/frontier limits must be at least 2')
    settings = {k:v for k,v in vars(args).items() if k not in ('out','resume','workers')}
    settings.update(t_ratio=.0001,directions=list(DIRECTIONS),proposal_objective_version=VERSION)
    verify_sources()
    inputs = input_hashes()
    target,before,progress,jobs = prepare(args.out,settings,inputs,args.resume)
    pending = [(job,settings) for name,job in jobs.items() if name not in progress['completed']]
    print(f'Frozen protocol: {len(jobs)} runs, {len(pending)} pending; {args.workers} workers.',flush=True)
    if pending:
        with mp.Pool(args.workers,initializer=initialize) as pool:
            for result in pool.imap_unordered(search_job,pending):
                path = atomic_json(target/'runs'/(result['id']+'.json'),result)
                progress['completed'][result['id']] = sha256_file(path)
                atomic_json(target/'progress.json',progress)
                print(f"{len(progress['completed'])}/{len(jobs)} {result['id']}: {result['seconds']:.1f}s",flush=True)
    finish(target,settings,before,progress,inputs,args.workers)


if __name__ == '__main__':
    main()
