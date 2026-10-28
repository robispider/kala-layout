"""Verify and interpret the expanded pilot; the search outputs stay untouched."""
import json
from pathlib import Path

from bangla_dh.paths import PROJECT_ROOT as ROOT, write_json, write_text
from bangla_dh.reference import sha256_file
from bangla_dh.experimental.shared_explore import PilotProblem,cid
from bangla_dh.experimental.shared_problem import dominates,pareto_offer
from bangla_dh.experimental.shared_search import table


def main():
    base=ROOT/'results/shared-exploration-pilot-v1'
    run=base/'run-100m-v1';old=base/'run-v1'
    destination=base/'FINDINGS-100m.md'
    if destination.exists():raise FileExistsError('interpretation already exists')
    manifest=json.loads((run/'run-manifest.json').read_text(encoding='utf-8'))
    before=json.loads((old/'run-manifest.json').read_text(encoding='utf-8'))
    verified={}
    for group in ('input_sha256','output_sha256','protected_sha256'):
        for name,digest in manifest[group].items():assert sha256_file(ROOT/name)==digest,name
        verified[group]=len(manifest[group])
    assert manifest['input_sha256']==before['input_sha256']
    assert {k:v for k,v in manifest['settings'].items() if k not in ('pairs','total_proposals')}=={
        k:v for k,v in before['settings'].items() if k not in ('pairs','total_proposals')}
    assert manifest['settings']['total_proposals']==100000000
    prefix=0
    for path in sorted((old/'runs').glob('*.json')):
        a=json.loads(path.read_text(encoding='utf-8'))
        b=json.loads((run/'runs'/path.name).read_text(encoding='utf-8'))
        for key in ('seconds','settings_sha256'):a.pop(key);b.pop(key)
        assert a==b,path.name
        prefix+=1
    assert prefix==20
    current=json.loads((run/'results.json').read_text(encoding='utf-8'))
    previous=json.loads((old/'results.json').read_text(encoding='utf-8'))
    problem=PilotProblem()
    exact={};covered={}
    for variant in ('control','enhanced'):
        points=current['full_scored_points'][variant]
        frontier=[]
        for point in points:pareto_offer(frontier,point,max(2,len(points)))
        exact[variant]=frontier
        covered[variant]=all(any(f['R']==p['R'] or dominates(f['R'],p['R'])
                                for f in current['frontiers'][variant]) for p in points)
    s=current['summaries'];c=s['control'];e=s['enhanced']
    ratio=e['eligible_full_scored_unique']/c['eligible_full_scored_unique']
    extra=100*(e['summed_seed_seconds']/c['summed_seed_seconds']-1)
    cost_direction='higher' if extra>=0 else 'lower'
    incumbent_scores=[[problem.evaluate_training(p)[mode]['balance']['R'] for mode in ('A','D')]
                      for p in problem.starts[-2:]]
    improvement={v:any(dominates(point['R'],inc) for point in current['full_scored_points'][v]
                      for inc in incumbent_scores) for v in ('control','enhanced')}
    new_to_4b={}
    pool=json.loads((ROOT/'results/shared-layout-relaxed-v1/run-4b-v1/training-pool.json').read_text(encoding='utf-8'))['candidates']
    old_perms={tuple(r['perm']) for r in pool};del pool
    for v in ('control','enhanced'):
        new_to_4b[v]=sum(tuple(r['perm']) not in old_perms for r in current['full_scored_points'][v])
    conclusion=('The expanded pilot found a score improvement over at least one known 4-billion alternative.'
                if any(improvement.values()) else
                'The expanded pilot did not improve either known 4-billion alternative in both mode scores.')
    text=['# Expanded 100-million pilot: findings','',f'**{conclusion}** The scoring model and per-start setup are unchanged.','',
        'The 100-million annealing budget is divided equally between control and enhanced: 50 million each, 100 paired starts per variant, 500,000 proposals per start and 32 workers. Both variants use the same initial maps/seeds and common final refinement. The first ten pairs repeat the smaller pilot; 90 pairs are additional. This is a nested expansion, not an independent fresh replication.','',
        '## Results','',table(['Measure','Control','Enhanced'],[[label,c[key],e[key]] for label,key in (
        ('Annealing proposals','annealing_proposals'),('Mechanical maps saved','mechanical_saved_unique'),
        ('Qualifying distinct maps fully scored','eligible_full_scored_unique'),
        ('Qualifying maps outside common starts','non_start_eligible_unique'),
        ('Retained non-dominated alternatives','frontier_count'),('Non-start frontier alternatives','non_start_frontier_count'))]),'',
        f'The enhanced variant fully scored **{ratio:.2f} times** as many distinct qualifying arrangements. Its summed per-seed wall durations were **{abs(extra):.1f}% {cost_direction}**. Equal proposal budget is not equal compute cost; the two variants ran concurrently and final reporting/scoring adds serial work. More saved maps alone is expected from the larger archive and does not establish better quality.','',
        '## Compared with the 10-million pilot','',table(['Budget','Control qualifying','Enhanced qualifying','Control frontier','Enhanced frontier'],
        [[name,*[r['summaries'][v]['eligible_full_scored_unique'] for v in ('control','enhanced')],
               *[r['summaries'][v]['frontier_count'] for v in ('control','enhanced')]]
         for name,r in [('10 million',previous),('100 million',current)]]),'',
        '## Final score alternatives','',table(['Variant','Candidate','Goti R','Jhor R'],
        [[v,cid(problem,r['perm']),f"{r['R'][0]:.6f}",f"{r['R'][1]:.6f}"]
         for v in ('control','enhanced') for r in current['frontiers'][v]]),'',
        'Lower R is better only within the same mode. A score improvement in this report means no worse in either mode-specific score and strictly better in at least one; the two R values are never added. A trade-off can be a useful new alternative without dominating an old point. Qualifying under the caps is not evidence of measured speed or comfort.','',
        f"All evaluated points are covered by the retained frontier: {covered}. Unbounded non-dominated counts among fully scored points are { {v:len(exact[v]) for v in exact} }. These checks distinguish a small bounded output from the actual evaluated score set; neither describes an exhaustive frontier over all possible layouts.",'',
        f"Fully scored qualifying maps absent from the old 4-billion retained pool: {new_to_4b}. Absence means not saved there, not proof that the old search never visited them.",'',
        '## Model, setup and validation','',
        'Frozen J1, Balance components, calibration, aspirations, scales, all 81 settings, typing rules, geometry and +0.75% effort/+7.5% within-word limits are reused unchanged. The input hash maps match the smaller pilot exactly. Per-start search settings also match exactly; only pair count and total proposal budget differ. All 20 saved prefix runs reproduce the earlier scientific outputs, excluding timing and the settings digest.','',
        'Both variants receive the current 4-billion finalists as common starts/comparisons. The enhanced method retains diverse mechanical candidates and performs bounded full-score local work before completion. The final routine, including its budget, is shared. This combined pilot cannot isolate diversity from earlier scoring or make an equal-wall-time claim.','',
        'Every run-manifest input/output/protected hash matched after completion. The source run already checked paired starts, budget, independent final scores and exact challenge J1. Known held-out data were scored after training selection and did not guide this comparison. Existing results, source model and published layouts are preserved. The engine-generated report title inherits the original 10-million harness label; its actual settings and proposal counts, and this interpretation, describe the 100-million run.','',
        '## Reproduce','', '```powershell','$env:PYTHONPATH = "src"',
        'python -m bangla_dh.experimental.shared_explore --out work/evaluator-experiments/shared-explore-100m-repeat --pairs 100 --steps 500000 --workers 32','```','']
    write_text(destination,'\n'.join(text))
    write_json(base/'validation-100m.json',{'source_run_manifest_sha256':sha256_file(run/'run-manifest.json'),
        'interpreter_sha256':sha256_file(Path(__file__).resolve()),
        'findings_sha256':sha256_file(destination),'verified_hash_counts':verified,'model_inputs_identical':True,
        'per_start_settings_identical':True,'prefix_runs_reproduced':prefix,'qualifying_ratio':ratio,
        'aggregate_seed_time_increase_percent':extra,'unbounded_evaluated_frontier_counts':{v:len(exact[v]) for v in exact},
        'all_evaluated_points_covered_by_reported_frontier':covered,'score_improvement_over_4b':improvement,
        'new_to_4b_saved_pool':new_to_4b,'elapsed_seconds':current['elapsed_seconds']})
    print(json.dumps({'findings':str(destination),'summaries':s,'score_improvement_over_4b':improvement,
                      'prefix_reproduced':prefix,'new_to_4b_saved_pool':new_to_4b}))


if __name__=='__main__':main()
