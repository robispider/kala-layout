"""Verify and interpret the completed 4-billion run without altering its files."""
from __future__ import annotations
import argparse
from collections import Counter
import csv
from fractions import Fraction
import json
from pathlib import Path

from bangla_dh import challenge
from bangla_dh.paths import PROJECT_ROOT as ROOT, hash_outputs, write_json, write_text
from bangla_dh.reference import sha256_file
from bangla_dh.experimental.artifact_storage import write_csv
from bangla_dh.experimental.inputs import HELDOUT, read_json
from bangla_dh.experimental.joint_search import settings_digest
from bangla_dh.experimental.shared_relaxed import RelaxedProblem
from bangla_dh.experimental.shared_search import table

RUN=ROOT/'results/shared-layout-relaxed-v1/run-4b-v1'
PREVIOUS=ROOT/'results/shared-layout-relaxed-v1/run-100m-v1'
ORIGINAL={'A':'shared-8cab7309b3311430','D':'shared-b2c5b3f8b2196605'}
BALANCED={'A':'shared-de3178d2ceb5108b','D':'shared-39dccebe0bb8d6ca'}
METRICS=('J1','within_distance','cross_distance','order_lower','order_upper')


def delta(a,b,k):
    return 100*(a[k]/b[k]-1)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',default=str(Path(__file__).resolve().parent))
    out=Path(parser.parse_args().out).resolve()
    if out.exists() and any(p.name!='analyze.py' for p in out.iterdir()):
        raise FileExistsError('use a new interpretation directory')
    manifest=read_json(RUN/'run-manifest.json')
    verification={}
    for group in ('input_sha256','output_sha256','protected_sha256'):
        for name,digest in manifest[group].items():
            if sha256_file(ROOT/name)!=digest:
                raise ValueError('hash mismatch: '+name)
        verification[group]=len(manifest[group])
    previous_manifest=read_json(PREVIOUS/'run-manifest.json')
    for name,digest in previous_manifest['output_sha256'].items():
        if sha256_file(ROOT/name)!=digest:
            raise ValueError('previous run output changed: '+name)
    preset=read_json(ROOT/'experiments/shared-4b-v1/preset.json')
    settings=manifest['settings']
    assert settings['seeds']==preset['seeds_per_track']==10000
    assert settings['steps']==preset['steps_per_seed']==200000
    assert settings['first_seed']==preset['first_seed']
    assert manifest['workers']==preset['workers']==32
    assert settings['effort_allowance_exact']=='3/400' and settings['within_allowance']==.075
    progress=read_json(RUN/'progress.json')['completed']
    result=read_json(RUN/'results.json')
    prior=read_json(PREVIOUS/'results.json')
    selected=result['selected']
    lookup={r['id']:r for r in selected}
    finalists=sorted([r for r in selected if any(s.startswith('relaxed-eligibility') for s in r['roles'])],
                     key=lambda r:r['training']['A']['balance']['R'])
    prior_front=[r for r in prior['selected'] if any(s.startswith('relaxed-eligibility') for s in r['roles'])]
    selection=read_json(RUN/'selection.json')
    perms={r['id']:tuple(r['perm']) for r in selection['selected']}
    counts=Counter();starts=Counter();times=Counter();occurrences=Counter();endpoints=Counter()
    ordinals={'effort':set(),'balance':set()}
    run_paths=sorted((RUN/'runs').glob('*.json'))
    for path in run_paths:
        r=read_json(path)
        arm=r['arm'];offset=0 if arm=='effort' else 100000
        assert r['version']==manifest['version'] and r['settings_sha256']==settings_digest(settings)
        assert r['seed']==settings['first_seed']+offset+r['ordinal']
        assert r['id']==path.stem and path.stem in progress
        assert progress[path.stem]==manifest['output_sha256'][path.relative_to(ROOT).as_posix()]
        assert r['ordinal'] not in ordinals[arm]
        ordinals[arm].add(r['ordinal'])
        counts[arm]+=1;starts[arm+':'+r['start']]+=1;times[arm]+=r['seconds']
        for f in finalists:
            if any(tuple(point['perm'])==perms[f['id']] for point in r['archive']):
                occurrences[f['id']]+=1
            if tuple(r['endpoint'])==perms[f['id']]:
                endpoints[f['id']]+=1
    assert len(progress)==len(run_paths)==20000
    assert all(ordinals[a]==set(range(10000)) for a in ordinals)
    assert sum(counts.values())*settings['steps']==4000000000
    print('Verified all hashes and 20,000 seed checkpoints.',flush=True)
    pool=read_json(RUN/'training-pool.json')['candidates']
    assert len(pool)==result['retained_pool_count']==113550
    seen=set();origins={}
    for row in pool:
        perm=tuple(row['perm'])
        assert len(perm)==52 and set(perm)==set(range(52)) and perm not in seen
        seen.add(perm)
        for f in finalists:
            if perm==perms[f['id']]:
                origins[f['id']]=row['origins']
    del pool,seen
    problem=RelaxedProblem()
    public=challenge.load_scorer(challenge.SCRIPT)
    data,data_hash=public.load_data();model=public.Model(data)
    layouts={}
    for f in finalists:
        cid=f['id'];perm=list(perms[cid]);layout=problem.assignment(perm);layouts[cid]=layout
        independent=problem.evaluate_training(perm)
        for s in ('A','D'):
            assert independent[s]['balance']['eligible']
            for k in METRICS:
                assert abs(independent[s]['metrics'][k]-f['training'][s]['metrics'][k])<1e-11
            assert independent[s]['balance']['R']==f['training'][s]['balance']['R']
            scored=public.evaluate({'name':cid,'style':s,'layout':challenge._key_layout(layout)},data,data_hash,model)
            assert scored['valid'] and Fraction(scored['J1_exact'])==Fraction(f['training'][s]['metrics']['J1_exact'])
    with (RUN/'scores.csv').open(encoding='utf-8',newline='') as stream:
        saved=[{**r,**{k:float(r[k]) for k in METRICS}} for r in csv.DictReader(stream)]
    index={(r['id'],r['style'],r['corpus'],r['fingering']):r for r in saved}
    scenarios=[];means=[];comparison=[];differences=[]
    for f in finalists:
        cid=f['id']
        for s in ('A','D'):
            m=f['training'][s]['metrics'];ref=problem.config['styles'][s]['reference']
            b=f['training'][s]['balance']
            comparison.append({'id':cid,'mode':s,'scope':'primary training','effort_change_percent':delta(m,ref,'J1'),
                'within_change_percent':delta(m,ref,'within_distance'),'cross_change_percent':delta(m,ref,'cross_distance'),
                'R':b['R'],'original_v1_eligible':b['original_balance_v1_eligible'],
                'order_lower':m['order_lower'],'order_upper':m['order_upper']})
            for fingering in ('model-optimal','traditional'):
                for corpus in ('bnwiki/train','newspaper/train',*HELDOUT):
                    row=index[cid,s,corpus,fingering];base=index[ORIGINAL[s],s,corpus,fingering]
                    scenarios.append({'id':cid,'mode':s,'corpus':corpus,'fingering':fingering,
                        **{k+'_change_percent':delta(row,base,k) for k in ('J1','within_distance','cross_distance')}})
                for reference_name,reference_id in (('original',ORIGINAL[s]),('Balance v1 leader',BALANCED[s])):
                    mean={k:sum(index[cid,s,c,fingering][k] for c in HELDOUT)/3 for k in METRICS}
                    base={k:sum(index[reference_id,s,c,fingering][k] for c in HELDOUT)/3 for k in METRICS}
                    means.append({'id':cid,'mode':s,'fingering':fingering,'reference':reference_name,**mean,
                                  **{k+'_change_percent':delta(mean,base,k) for k in ('J1','within_distance','cross_distance')}})
        for label,reference_id in [('other finalist',finalists[1 if cid==finalists[0]['id'] else 0]['id']),
                                   *[(name,reference_id) for name,reference_id in [('original Goti',ORIGINAL['A']),
                                     ('original Jhor',ORIGINAL['D']),('Balance Goti',BALANCED['A']),('Balance Jhor',BALANCED['D'])]]]:
            reference=problem.assignment(list(perms[reference_id]))
            for symbol in layout_symbols(layouts[cid],reference):
                differences.append({'id':cid,'reference':label,'symbol':symbol,
                    'reference_slot':'/'.join(reference[symbol]),'candidate_slot':'/'.join(layouts[cid][symbol]),
                    'physical_key_changed':reference[symbol][0]!=layouts[cid][symbol][0],
                    'layer_changed':reference[symbol][1]!=layouts[cid][symbol][1]})
    dominance=[]
    for f in finalists:
        for old in prior_front:
            domination=all(f['training'][s]['balance']['R']<old['training'][s]['balance']['R'] for s in ('A','D'))
            dominance.append({'new':f['id'],'previous':old['id'],'strictly_lower_R_in_both_modes':domination})
    assert all(r['strictly_lower_R_in_both_modes'] for r in dominance)
    primary,alternative=finalists
    elapsed=(RUN/'run-manifest.json').stat().st_mtime-(RUN/'search-plan.json').stat().st_mtime
    verification.update(seed_checkpoint_count=len(run_paths),unique_retained_bijections=113550,
        proposal_budget=4000000000,independent_finalist_scoring=True,official_exact_finalist_J1=True,
        earlier_frontier_dominated_in_both_R=True,reported_run_checks=manifest['checks'])
    text=['# Four-billion shared-layout experiment: interpretation','',
        f"**Primary typing-test candidate: {primary['id']}.** The larger run found a better shared arrangement than either 100-million alternative under both mode-specific Balance scores. Retain {alternative['id']} as the small Jhor-score trade-off. These are experimental choices for testing, not a replacement release or a proven optimum.",'',
        '## What completed and what was checked','',
        f"The configured run completed **4 billion annealing proposals**, split equally between two tracks, on **32 workers**: 10,000 starts per track and 200,000 proposals per start, plus 30 ILS trials per start. File timestamps indicate approximately **{elapsed/3600:.2f} hours** from the frozen plan to final manifest. This includes final scoring; it is an elapsed-time diagnostic, not a universal benchmark.",'',
        'There are **113,550 distinct retained assignments**. **961** qualifying shared maps received the full frozen-expression score during final selection/refinement, including order; the final bounded score frontier retains **two alternatives**. Four billion proposals can repeat arrangements and are not four billion unique maps or full Balance evaluations.','',
        f"Verified {verification['input_sha256']} input hashes, {verification['output_sha256']} output hashes, {verification['protected_sha256']} protected-artifact hashes, every seed identity/signature/progress entry, and all retained maps' 52-slot bijections. Both finalists independently reproduce direct mechanics, full scores and the official exact challenge J1 under A and D. The 100-million output hashes also match.",'',
        '## Primary training result','',
        'Changes are versus each mode\'s original published map on the original independently normalized 50/50 Wikipedia/newspaper mix and model-optimal fingering. E is J1 per text unit. W is within-word SF different-key distance per text unit. X is cross-space SF different-key endpoint distance per spanning window. X and W have different denominators.','',
        table(['Candidate','Mode','E change','W change','X change','Experimental R','Original v1 eligible'],
              [[r['id'],r['mode'],f"{r['effort_change_percent']:+.3f}%",f"{r['within_change_percent']:+.2f}%",
                f"{r['cross_change_percent']:+.2f}%",f"{r['R']:.6f}",r['original_v1_eligible']] for r in comparison]),'',
        'Both finalists satisfy the requested **+0.75% E / +7.5% W** limits in both modes on this primary mix. The first candidate\'s movement also satisfies the original +5% W cap in both modes. Its Jhor mode satisfies original Balance v1 eligibility; its Goti mode still exceeds the original +0.5% effort cap. Neither is an original-policy two-mode success.','',
        'The remaining physical trade-off is clear: **cross-space distance rises about 25.6% in Goti and 5.9% in Jhor** for the primary candidate. X has no hard cap in this experiment, but remains positively penalized in the full score. Passing the E/W caps is not an all-movement improvement.','',
        '## Why keep the first candidate as the primary test','',
        f"{primary['id']} has the lower Goti R, lower Goti effort and within-word distance, and lower Jhor cross-space distance. {alternative['id']} has a slightly lower Jhor R. The Goti R difference is {alternative['training']['A']['balance']['R']-primary['training']['A']['balance']['R']:.6f}, whereas the Jhor R gain of the alternative is {primary['training']['D']['balance']['R']-alternative['training']['D']['balance']['R']:.6f}. These are separate same-mode score differences; they are not combined into one winner or interpreted as comfort percentages.",'',
        'The maps differ only by swapping the vowel-sign labels **ৈ and ৌ between Shift+X and Shift+W**. This offers a narrow, concrete preference test without learning a second complete arrangement. The first-map recommendation is a practical testing priority, not a formal shared scalar-score optimum.','',
        '## Improvement over the smaller experiment','',
        table(['Candidate','Goti R','Jhor R'],
              [[r['id'],f"{r['training']['A']['balance']['R']:.6f}",f"{r['training']['D']['balance']['R']:.6f}"]
               for r in [*prior_front,*finalists]]),'',
        'Each 4-billion alternative has a strictly lower Goti R and a strictly lower Jhor R than each of the two 100-million frontier alternatives under the same frozen expression and revised eligibility. Thus the larger run improves both score endpoints, rather than merely moving the old trade-off. These R changes are modeled shortfalls against fixed calibration, not measured speed or comfort improvements.','',
        'The lowest-effort retained map reduces the worst relative effort loss to **0.6230%**, from **0.6402%** in the 100-million run. Its within-word movement rises about 33%/30%, so it fails the movement cap and should not be treated as the balanced result.','',
        '## Comparison with the separate-mode layouts','',
        table(['Mode','Original published R','Separate Balance leader R','Primary shared R'],
              [[s,f"{lookup[ORIGINAL[s]]['training'][s]['balance']['R']:.6f}",
                f"{lookup[BALANCED[s]]['training'][s]['balance']['R']:.6f}",
                f"{primary['training'][s]['balance']['R']:.6f}"] for s in ('A','D')]),'',
        'Within each mode, the shared arrangement has a higher modeled Balance cost than its independently optimized Balance leader and than the original published map. Its potential benefit is one remembered arrangement across vowel modes, a learning/product benefit not included in these scores. It does not establish a new mechanical winner over keeping the separate arrangements.','',
        'Primary order-credit coverage intervals follow. Higher is better; non-overlap can establish that narrow diagnostic ranking, while overlap leaves it unresolved. Compared with the published originals, the primary shared map improves order credit in both modes; the Goti Balance leader still has substantially greater credit.','',
        table(['Mode','Original order bounds','Separate Balance bounds','Shared order bounds'],
              [[s,*[f"{lookup[i]['training'][s]['metrics']['order_lower']:.6f}–{lookup[i]['training'][s]['metrics']['order_upper']:.6f}"
                       for i in (ORIGINAL[s],BALANCED[s],primary['id'])]] for s in ('A','D')]),'',
        '## Held-out diagnostics and generalization','',
        'The following are equal means of the three already examined held-out sources under model-optimal fingering. Means normalize each source first; they do not pool raw counts. Selection was frozen before these diagnostics.','',
        table(['Candidate','Mode','Mean held-out J1','E change','W change','X change'],
              [[r['id'],r['mode'],f"{r['J1']:.6f}",f"{r['J1_change_percent']:+.3f}%",
                f"{r['within_distance_change_percent']:+.2f}%",f"{r['cross_distance_change_percent']:+.2f}%"]
               for r in means if r['fingering']=='model-optimal' and r['reference']=='original']),'',
        'The E/W caps apply to the declared training mix and fingering, not every source or alternative fingering. Important observed exceptions include Jhor within-word distance of roughly +11.16% on held-out Wikipedia under model-optimal fingering, and Goti effort/within distance of roughly +1.64%/+26.96% on held-out BARD news with traditional fingering for the primary candidate. These exceed the corresponding cap percentages in those diagnostics. Do not describe the shared layout as uniformly within the caps across domains or fingerings. scenario-changes.csv retains every context.','',
        'Known held-out evidence is exploratory, not a fresh confirmation set. Coverage bounds are not statistical confidence intervals. More annealing alone cannot establish actual learning or sustained comfort.','',
        '## Primary shared key arrangement','',
        'The same 52 positions serve both modes. Only the vowel-entry recipe changes. Shift is above base; digits and punctuation retain their frozen positions. Learning this shared map still requires relocation from the existing maps; layout-differences.csv records those edits, not measured learning difficulty.','']
    inverse={slot:s for s,slot in layouts[primary['id']].items()}
    for keys in ('QWERTYUIOP','ASDFGHJKL','ZXCVBNM'):
        text += [table(['Layer',*keys],[[layer,*[inverse[k,layer] for k in keys]] for layer in ('shift','base')]),'']
    text += ['## Search limits and next use','',
        'The mechanical proposal archive is bounded; full order scoring follows that filter and does not occur at every annealing step. The R archive is bounded as well. Seed recurrences and starting-map provenance are retained in analysis.json; shared starts are not independent rediscoveries. This search does not enumerate the assignment space or prove optimality or impossibility.','',
        'Use the first candidate as an exploratory shared-layout typing-test option, with the second as the two-key vowel alternative. Compare learning, errors and sustained performance against keeping each separate-mode layout. Any application integration or replacement publication is a later decision. Original layouts, scoring constants, challenge version, locks and website numbers remain unchanged.','',
        '## Reproduce this interpretation','',
        '```powershell','$env:PYTHONPATH = "src"',
        'python results/shared-layout-relaxed-v1/interpretation-4b-v1/analyze.py --out work/evaluator-experiments/interpretation-4b-repeat','```','']
    outputs=[write_text(out/'REPORT.md','\n'.join(text))]
    outputs += [write_csv(out/'primary-comparison.csv',comparison),write_csv(out/'scenario-changes.csv',scenarios),
                write_csv(out/'heldout-means.csv',means),write_csv(out/'layout-differences.csv',differences)]
    outputs += [write_json(out/'analysis.json',{'verification':verification,'elapsed_seconds_by_file_timestamps':elapsed,
        'seed_counts':dict(counts),'summed_seed_wall_seconds':dict(times),'start_counts':dict(starts),
        'seed_archive_occurrences':dict(occurrences),'seed_endpoint_occurrences':dict(endpoints),
        'finalist_pool_origins':origins,'prior_frontier_comparisons':dominance,
        'primary_typing_test_candidate':primary['id'],'alternative':alternative['id'],
        'recommendation_scope':'exploratory testing priority; no combined R or replacement decision'})]
    inputs=[Path(__file__).resolve(),RUN/'run-manifest.json',RUN/'results.json',RUN/'selection.json',
        RUN/'training-pool.json',RUN/'scores.csv',PREVIOUS/'run-manifest.json',PREVIOUS/'results.json',
        ROOT/'experiments/shared-4b-v1/preset.json']
    inputs += list((RUN/'layouts').glob('*.json'))
    outputs.append(write_json(out/'validation.json',verification))
    write_json(out/'run-manifest.json',{'version':'interpretation-shared-4b-v1','new_search':False,'seeds':[],
        'input_sha256':hash_outputs(inputs),'output_sha256':hash_outputs(outputs),
        'source_run_manifest_sha256':sha256_file(RUN/'run-manifest.json'),
        'checks':verification,'source_run_unmodified':True,'report_selection_basis':'training metrics only'})
    print(json.dumps({'report':str(out/'REPORT.md'),'primary':primary['id'],'alternative':alternative['id'],
                      'elapsed_hours':elapsed/3600,'verification':verification}),flush=True)


def layout_symbols(layout,reference):
    return sorted(s for s in layout if layout[s]!=reference[s])


if __name__=='__main__':
    main()
