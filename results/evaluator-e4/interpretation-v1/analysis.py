"""Interpret the immutable e4 run and its stored per-seed archives (stdlib only)."""
from __future__ import annotations

import argparse
from collections import Counter
import datetime as dt
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import platform
import statistics
import sys
import time

from bangla_dh import challenge
from bangla_dh.experimental.inputs import load_candidates, read_json, TRAIN, HELDOUT
from bangla_dh.experimental.joint_problem import JointProblem, achievement
from bangla_dh.experimental.joint_search import evaluate_layout, preserved
from bangla_dh.experimental.evaluate import MODELS
from bangla_dh.experimental.safety import new_run_directory
from bangla_dh.paths import PROJECT_ROOT, write_json, write_text, hash_outputs, repo_state
from bangla_dh.reference import sha256_file
from bangla_dh.scoring.model import KeyModel
from bangla_dh.search.problem import slot_name

VERSION = 'e4-interpretation-v1'
CAPS = (Fraction(0), Fraction('0.01'), Fraction('0.03'), Fraction('0.1'), Fraction('0.5'), Fraction(1))


def frontier(rows):
    out, lowest = [], None
    for row in sorted(rows, key=lambda r: (r['j'], r['s'], r['perm'])):
        if lowest is None or row['s'] < lowest:
            out.append(row)
            lowest = row['s']
    return out


def compact(row):
    continuous = row['continuous']
    mechanics, triples = row['mechanics'], row['engram_order']
    return {'corpus': row['corpus'], 'scenario': row['scenario'], 'reference': row['reference'],
        'diagnostics': row['diagnostics'],
        'continuous': {k: continuous[k] for k in ('coverage', 'spanning_count', 'bounds',
            'same_finger_distance_u_per_spanning_window', 'space_touching_share', 'within_word_share')},
        'mechanics': {k: mechanics[k] for k in ('pair_coverage', 'bounds', 'conditional_means')},
        'engram_order': {k: triples[k] for k in ('coverage', 'bounds', 'conditional_mean')}}


def changes(row, reference):
    a, b = row['continuous'], reference['continuous']
    return {'J1_percent': 100 * (row['reference']['J1'] / reference['reference']['J1'] - 1),
        'movement_percent': 100 * (a['bounds']['same_finger_different_key']['lower'] /
                                  b['bounds']['same_finger_different_key']['lower'] - 1),
        'movement_pp': 100 * (a['bounds']['same_finger_different_key']['lower'] -
                             b['bounds']['same_finger_different_key']['lower']),
        'repeat_pp': 100 * (a['bounds']['same_key']['lower'] - b['bounds']['same_key']['lower']),
        'same_hand_pp': 100 * (a['bounds']['same_hand']['lower'] - b['bounds']['same_hand']['lower']),
        'shift_pp': 100 * (row['diagnostics']['shift_share_of_non_space_presses'] -
                          reference['diagnostics']['shift_share_of_non_space_presses']),
        'distance_percent': 100 * (a['same_finger_distance_u_per_spanning_window'] /
                                  b['same_finger_distance_u_per_spanning_window'] - 1),
        'engram_pair_lower_change': row['mechanics']['bounds']['engram_avg4']['lower'] -
                                    reference['mechanics']['bounds']['engram_avg4']['lower'],
        'engram_order_lower_change': row['engram_order']['bounds']['lower'] -
                                     reference['engram_order']['bounds']['lower']}


def mixed_changes(rows, references, scenario='model-optimal'):
    mixed = {}
    for side, collection in (('candidate', rows), ('reference', references)):
        chosen = [r for r in collection if r['corpus'] in TRAIN and r['scenario'] == scenario]
        mixed[side] = {'J1': sum(r['reference']['J1'] for r in chosen)/2,
            'movement': sum(r['continuous']['bounds']['same_finger_different_key']['lower'] for r in chosen)/2,
            'repeat': sum(r['continuous']['bounds']['same_key']['lower'] for r in chosen)/2,
            'shift': sum(r['diagnostics']['shift_share_of_non_space_presses'] for r in chosen)/2,
            'distance': sum(r['continuous']['same_finger_distance_u_per_spanning_window'] for r in chosen)/2,
            'engram_pair': sum(r['mechanics']['bounds']['engram_avg4']['lower'] for r in chosen)/2,
            'engram_order': sum(r['engram_order']['bounds']['lower'] for r in chosen)/2}
    a, b = mixed['candidate'], mixed['reference']
    return {'J1_percent': 100*(a['J1']/b['J1']-1),
        'movement_percent': 100*(a['movement']/b['movement']-1),
        'distance_percent': 100*(a['distance']/b['distance']-1),
        'repeat_pp': 100*(a['repeat']-b['repeat']), 'shift_pp': 100*(a['shift']-b['shift']),
        'engram_pair_lower_change': a['engram_pair']-b['engram_pair'],
        'engram_order_lower_change': a['engram_order']-b['engram_order']}


def render(data):
    lines = ['# Interpreting the completed e4 search', '',
        '**The search did not meet the stated goal of lower J1 plus better modeled movement.** '
        'It found no lower-J1 layout in the saved archives and no strict joint improvement. '
        'Kala Goti and Kala Jhor remain the preferred maps for that goal. The new evaluator does '
        'expose meaningful movement/effort trade-offs, including useful candidates omitted by the '
        'small final summary. Those trade-offs do not qualify as replacements under the owner’s objective.', '',
        'This interpretation reads the completed [run](../rigorous-v1/REPORT.md) and all 1,024 '
        'saved per-seed archives. It writes a separate analysis directory; every original layout, '
        'run result and manifest remains unchanged.', '', '## What was run', '',
        'The run used 512 seeds for each style, 1,000,000 annealing proposals and 1,000 ILS '
        'trials per seed: 1.024 billion proposals and 1.024 million ILS trials in total. '
        'Wikipedia and newspaper training each receive half the weight after independent '
        'normalization. The primary fingering is the frozen model-optimal grid; held-out '
        'scores do not guide search.', '',
        'Per style, 86 seeds use J1 alone, 86 use direction 0.1, and 85 each use 0.25, 0.5, '
        '0.75 and 0.9. There are 103 published-reference starts, 103 retained-map starts, '
        'and 102 each from perturbed references, random permutations and the greedy J1 map.', '',
        f"The filesystem timestamps indicate approximately {data['timing']['approx_end_to_end_minutes']:.1f} "
        'minutes from the saved plan to the final manifest, including final verification. '
        'This is an approximate duration, not a persisted wall-time measurement. Summed per-seed '
        f"elapsed time is {data['timing']['summed_worker_elapsed_hours']:.2f} worker-hours; "
        'that is not measured CPU time. The final invocation used 28 workers.', '',
        '## Result against the objective', '',
        '| Reference | Training J1 | Cross-space SF movement rate | Distinct saved maps | Reconstructed frontier | Final summary points |',
        '| --- | ---: | ---: | ---: | ---: | ---: |']
    for style, info in data['styles'].items():
        ref = info['reference']
        lines.append(f"| {ref['name']} ({style}) | {float(Fraction(ref['J1_exact'])):.12f} | "
            f"{100*float(Fraction(ref['movement_exact'])):.6f}% | {info['distinct_saved_maps']:,} | "
            f"{len(info['frontier'])} | {info['final_summary_points']} |")
    lines += ['', 'All 64 final-summary points comprise two unchanged reference maps and 62 '
        'higher-J1 movement trade-offs. None improves both training objectives; none is marked '
        'as improving both objectives on all three held-out sources under the primary fingering. '
        'Scanning the per-seed archives did not uncover a missed joint success.', '',
        'Both references appear in all their style’s archives because the implementation inserts '
        'them explicitly. They must not be described as 512 independent rediscoveries. Every run’s '
        'attained exploration energy is zero to floating-point precision: the reference remains '
        'the best retained energy when no joint win is found. That behavior follows from including '
        'the reference as an incumbent, and does not establish global optimality.', '',
        '## Movement means a specific event', '',
        'The new objective counts **different physical keys assigned to the same finger on the '
        'two sides of one space**. It skips the intervening thumb press when classifying the endpoints. '
        'Same-key repeats, Shift effort, distance, within-word pair costs and Engram order remain '
        'separate. A lower value is evidence of fewer such modeled movements; it is not a claim '
        'that all movement, human comfort or typing speed improves.', '',
        'Rates use all valid key–space–key windows in each source, not all keystrokes or all '
        'trigrams. For these style maps endpoint coverage is complete. Percentage changes below '
        'are relative; percentage-point changes describe the absolute change in this event rate.', '',
        '## Trade-offs recovered from the saved archives', '',
        'The caps below are analytical comparison bands, not a relaxation of the accepted goal. '
        'Each row selects the lowest movement rate within that J1-increase cap from the stored '
        'training frontier. Selection uses training data only. Zero cap recovers the reference.', '',
        '| Style | Allowed J1 increase | Actual J1 increase | SF movement reduction | Rate decrease (percentage points) | Source seed |',
        '| --- | ---: | ---: | ---: | ---: | --- |']
    for style, info in data['styles'].items():
        for row in info['cap_choices']:
            lines.append(f"| {style} | {row['cap_percent']:g}% | {row['J1_change_percent']:+.6f}% | "
                f"{-row['movement_change_percent']:.4f}% | {-row['movement_change_pp']:.6f} | {row['source_run']} |")
    lines += ['', 'At a 0.1% J1 budget, the stored search can cut cross-space SF movement by '
        'about 13.92% for A and 3.99% for D. At a 0.5% budget, the reductions are about '
        '29.91% and 26.71%. These are material changes in this narrow metric, but their '
        'J1 costs are positive. The owner’s strict goal rejects all of them.', '',
        '## Why the automatic summary understates the trade-offs', '',
        'The final report keeps only 32 points per style. Its archive prunes repeatedly using '
        'evenly spaced indices in J1 order. That can remove useful intermediate points and '
        'cannot be treated as an exhaustive frontier. The per-seed archives retain additional '
        'candidates, so this interpretation reconstructs their union before selecting comparison '
        'bands. Per-seed pruning still applies: this is the frontier of stored points, not every '
        'layout visited or every feasible layout.', '',
        '| Style | J1 cap | SF reduction shown by 32-point report | SF reduction in stored union |',
        '| --- | ---: | ---: | ---: |']
    for style, info in data['styles'].items():
        for cap in (.1, .5, 1):
            choice = next(r for r in info['cap_choices'] if r['cap_percent'] == cap)
            lines.append(f"| {style} | {cap:g}% | {-choice['reported_movement_change_percent']:.4f}% | "
                         f"{-choice['movement_change_percent']:.4f}% |")
    lines += ['', 'This summary loss affects how much movement improvement appears available '
        'at a cost; it does not conceal a strict joint win. The run also protects observed '
        'joint-goal points during pruning, and the stored-union audit independently found none.', '',
        '## Do the useful trade-offs carry over?', '',
        'The following candidates were selected only by the training caps of 0.1%, 0.5% and '
        '1%, then rescored on all sources under both fingerings. Held-out changes below use '
        'the primary model-optimal fingering. A negative J1 change is favorable; a positive '
        'movement reduction is favorable. These already examined benchmarks provide exploratory '
        'checks, not new confirmatory validation.', '',
        '| Candidate | Held-out source | J1 change | SF movement reduction | Distance reduction |',
        '| --- | --- | ---: | ---: | ---: |']
    for c in data['review_candidates']:
        for row in c['scores']:
            if row['corpus'] in HELDOUT and row['scenario'] == 'model-optimal':
                ch = row['changes']
                lines.append(f"| {c['label']} | {row['corpus']} | {ch['J1_percent']:+.6f}% | "
                             f"{-ch['movement_percent']:.4f}% | {-ch['distance_percent']:.4f}% |")
    lines += ['', 'A reduction in event count should also be assessed against distance, repeat '
        'frequency and movement within words. The next table is the 50/50 training comparison '
        'under the primary fingering. Engram values are changes in lower coverage bounds, '
        'so they are descriptive differences rather than complete comfort rankings.', '',
        '| Candidate | Labels moved | Shift change (pp) | Repeats change (pp) | Distance reduction | Engram pair lower change | Engram order lower change |',
        '| --- | ---: | ---: | ---: | ---: | ---: | ---: |']
    for c in data['review_candidates']:
        ch = c['mixed_changes']['model-optimal']
        lines.append(f"| {c['label']} | {len(c['label_moves'])} | {ch['shift_pp']:+.6f} | "
            f"{ch['repeat_pp']:+.6f} | {-ch['distance_percent']:.4f}% | "
            f"{ch['engram_pair_lower_change']:+.6f} | {ch['engram_order_lower_change']:+.6f} |")
    lines += ['', 'All scores for traditional fingering, per-source coverage, and symbol moves '
        'are in [analysis.json](analysis.json); the CSV provides the complete per-source '
        'comparison for these candidates. The copies in [layouts/](layouts/) identify '
        'experimental trade-offs, not replacements for the published layouts.', '',
        '## What the new evaluator contributed', '',
        'It contributed an independently measurable cross-word movement criterion and found '
        'alternative layouts that improve it at an explicit J1 cost. Reconstructing the stored '
        'archives is necessary to see that benefit. It did not find a lower-J1 layout or '
        'deliver the strict joint improvement sought here.', '',
        'The exploration function itself favors the reference when J1 cannot improve: for '
        'nonzero directions, a J1 increase makes the relative Chebyshev energy positive even '
        'if SF movement drops substantially. This explains why trade-offs live mainly in the '
        'archives rather than winning the per-run energy. There is no evidence here that adding '
        'this movement criterion makes the unchanged J1 optimum easier to beat.', '',
        '## Research decision and next work', '',
        'Keep Kala Goti and Kala Jhor for the current objective. Retain the e3/e4 movement '
        'evaluators as diagnostic evidence and preserve the recovered frontier for comparisons. '
        'Do not update the official layouts, challenge version, reproduction lock or website '
        'layout scores on the basis of this run.', '',
        'Before another joint search, improve archive reporting so useful low-cost trade-offs '
        'survive into the final summary, for example by retaining the nondominated union after '
        'the runs and explicitly preserving points within declared J1 bands. That addresses '
        'report completeness; it would not turn these trade-offs into joint successes.', '',
        'If the objective stays strict, the unresolved task is finding a lower-J1 layout first '
        'or alongside the movement gate. Additional J1-focused starts or a separately scoped '
        'mixed-corpus bound/certificate would investigate that bottleneck. This run supplies '
        'no promise that more seeds will help and no proof that a joint improvement is impossible. '
        'If a J1 budget is later accepted, that is an explicit owner decision; it is not assumed '
        'in this report.', '',
        '## Evidence and reproducibility', '',
        'The analysis checked every run-manifest output hash, pinned input hash, protected '
        'original-file hash, checkpoint digest and expected seed identity. The reconstructed '
        'frontier and all near-reference saved maps were rescored with exact rational J1 and '
        'movement. Each reviewed trade-off additionally agrees exactly with the independent '
        'official challenge scorer. All source-run and original-layout hashes were rechecked '
        'after writing the interpretation.', '',
        'This directory contains its own manifest, exact reconstructed frontier, selected '
        'comparison bands, compact secondary scores, layout copies and the analysis script. '
        'Reproduce into a new directory from the repository root:', '', '```powershell',
        '$env:PYTHONPATH = "src"',
        'python results/evaluator-e4/interpretation-v1/analysis.py --source results/evaluator-e4/rigorous-v1 --out work/evaluator-experiments/e4-interpretation-repeat',
        '```', '', 'Claims concern best found layouts under the stated search and modeled '
        'scores. They are neither optimality proofs nor measured typing-speed or comfort results.', '']
    return '\n'.join(lines)


def run(source, out):
    start = time.perf_counter()
    source = Path(source).resolve()
    manifest = read_json(source / 'run-manifest.json')
    audit_counts = {}
    for category in ('input_sha256', 'output_sha256', 'protected_original_sha256'):
        for name, digest in manifest[category].items():
            if sha256_file(PROJECT_ROOT / name) != digest:
                raise ValueError(f'{category} hash mismatch: {name}')
        audit_counts[category] = len(manifest[category])
    inputs = {**manifest['input_sha256'], **manifest['output_sha256'],
              **manifest['protected_original_sha256'], **hash_outputs([source/'run-manifest.json', Path(__file__)])}
    original = preserved()
    d = read_json(source / 'results.json')
    progress = read_json(source / 'progress.json')['completed']
    if len(progress) != d['search_run_count']:
        raise ValueError('incomplete checkpoint')
    expected = {f'{style}-{seed}' for style, bounds in manifest['seeds'].items()
                for seed in range(bounds[0], bounds[1]+1)}
    if set(progress) != expected or {r['id'] for r in d['runs']} != expected:
        raise ValueError('seed identity mismatch')
    target = new_run_directory(out)
    refs, _ = load_candidates(False)
    problems = {r.style: JointProblem(r.style, r.layout, PROJECT_ROOT/manifest['parameters']['counts_from']) for r in refs}
    reference_layouts = {r.style: r.layout for r in refs}
    summary = {'version': VERSION, 'source': source.relative_to(PROJECT_ROOT).as_posix(),
        'source_run_count': len(expected), 'checks': {'source_hashes': True, 'seed_coverage': True},
        'hash_count_checks': audit_counts, 'styles': {}, 'review_candidates': []}
    models = {s: KeyModel.from_grid(path) for s, path in MODELS.items()}
    public = challenge.load_scorer(challenge.SCRIPT)
    public_data, public_hash = public.load_data()
    public_model = public.Model(public_data)
    outputs, comparison_rows = [], []
    for style, problem in problems.items():
        if problem.reference_j != Fraction(d['references'][style]['J1_exact']) or problem.reference_s != Fraction(d['references'][style]['movement_exact']):
            raise ValueError('reference does not match completed run')
        saved, archive_entries = {}, 0
        runs = [r for r in d['runs'] if r['style'] == style]
        for name in sorted(n for n in progress if n.startswith(style+'-')):
            path = source/'runs'/(name+'.json')
            if sha256_file(path) != progress[name]:
                raise ValueError('checkpoint digest differs')
            result = read_json(path)
            if not result['verified'] or result['id'] != name:
                raise ValueError('unverified saved run')
            for row in result['archive']:
                archive_entries += 1
                perm = tuple(row['perm'])
                if perm in saved and (saved[perm]['j'], saved[perm]['s']) != (row['j'], row['s']):
                    raise ValueError('same permutation has inconsistent scores')
                saved.setdefault(perm, {**row, 'source_run': name})
        candidates = frontier(saved.values())
        near_reference = [row for row in saved.values() if row['j'] <= problem.ref_j + 1e-12]
        exact = {}
        for row in candidates + near_reference:
            perm = tuple(row['perm'])
            if perm not in exact:
                j, s = problem.verify(perm)
                if (float(j), float(s)) != (row['j'], row['s']):
                    raise ValueError('stored score differs from independent exact rescore')
                exact[perm] = {**row, 'j': j, 's': s}
        complete = frontier(exact[tuple(row['perm'])] for row in candidates)
        if any(problem.success(row['j'], row['s']) for row in exact.values()):
            raise ValueError('unexpected missed joint improvement: revise interpretation')
        if min(row['j'] for row in saved.values()) != problem.ref_j:
            raise ValueError('unexpected lower-J1 result: revise interpretation')
        info = {'reference': {k:v for k,v in d['references'][style].items() if k!='scores'},
            'archive_entries': archive_entries, 'distinct_saved_maps': len(saved),
            'near_reference_exact_checks': len(near_reference), 'frontier_exact_checks': len(complete),
            'final_summary_points': sum(c['style']==style for c in d['candidates']),
            'directions': dict(Counter(str(r['direction']) for r in runs)),
            'starts': dict(Counter(r['start'].split('-map-')[0] for r in runs)),
            'maximum_absolute_endpoint_energy': max(abs(r['endpoint_energy']) for r in runs),
            'frontier': [], 'cap_choices': []}
        for row in complete:
            info['frontier'].append({'J1_exact': str(row['j']), 'movement_exact': str(row['s']),
                'J1': float(row['j']), 'movement': float(row['s']), 'perm': row['perm'], 'source_run': row['source_run']})
        for cap in CAPS:
            chosen = min((r for r in complete if r['j'] <= problem.reference_j*(1+cap/100)),
                         key=lambda r:(r['s'],r['j'],r['perm']))
            limited = min((c for c in d['candidates'] if c['style']==style and
                Fraction(c['training_J1_exact']) <= problem.reference_j*(1+cap/100)),
                key=lambda c:(Fraction(c['training_movement_exact']),Fraction(c['training_J1_exact'])))
            info['cap_choices'].append({'cap_percent': float(cap), 'source_run': chosen['source_run'],
                'J1_exact': str(chosen['j']), 'movement_exact': str(chosen['s']),
                'J1_change_percent': 100*float(chosen['j']/problem.reference_j-1),
                'movement_change_percent': 100*float(chosen['s']/problem.reference_s-1),
                'movement_change_pp': 100*float(chosen['s']-problem.reference_s),
                'reported_candidate': limited['id'],
                'reported_movement_change_percent': limited['training_movement_change_percent']})
            if cap not in (Fraction('.1'),Fraction('.5'),Fraction(1)):
                continue
            layout = problem.assignment(chosen['perm'])
            identity = hashlib.sha256(json.dumps([style, sorted(layout.items())],ensure_ascii=False).encode()).hexdigest()[:16]
            cid = f'{style}-{identity}'
            submission = {'name': f'Experimental joint search {cid}', 'style':style,'layout':challenge._key_layout(layout)}
            official = public.evaluate(submission,public_data,public_hash,public_model)
            if not official['valid'] or Fraction(official['J1_exact']) != chosen['j']:
                raise ValueError('official J1 verification failed')
            file = write_json(target/'layouts'/(cid+'.json'),submission)
            outputs.append(file)
            scores = [compact(r) for r in evaluate_layout(style,layout,PROJECT_ROOT/manifest['parameters']['counts_from'],models)]
            reference_scores = [compact(r) for r in d['references'][style]['scores']]
            reference_index = {(r['corpus'],r['scenario']):r for r in reference_scores}
            for row in scores:
                row['changes'] = changes(row,reference_index[row['corpus'],row['scenario']])
                comparison_rows.append({'candidate':cid,'label':f'{style}, cap {float(cap):g}%',
                    'corpus':row['corpus'],'fingering':row['scenario'],**row['changes']})
            label_moves = [{'label':label,'from':slot_name(reference_layouts[style][label]),'to':slot_name(slot)}
                for label,slot in sorted(layout.items()) if reference_layouts[style][label] != slot]
            c = {'id':cid,'label':f'{style}, cap {float(cap):g}%', 'style':style,'cap_percent':float(cap),
                'source_run':chosen['source_run'],'layout_file':file.relative_to(PROJECT_ROOT).as_posix(),
                'J1_exact':str(chosen['j']),'movement_exact':str(chosen['s']),
                'joint_training_improvement':False,'label_moves':label_moves,'scores':scores,
                'mixed_changes':{s:mixed_changes(scores,reference_scores,s) for s in models}}
            summary['review_candidates'].append(c)
            print(f"Scored {c['label']}: {cid}; {len(label_moves)} symbol placements change",flush=True)
        summary['styles'][style] = info
        print(f'{style}: {len(saved)} distinct stored maps; {len(complete)} frontier points exact-checked',flush=True)
    summary['timing'] = {'approx_end_to_end_minutes':
        (dt.datetime.fromisoformat(manifest['generated_utc']).timestamp()-(source/'search-plan.json').stat().st_mtime)/60,
        'summed_worker_elapsed_hours':sum(r['seconds'] for r in d['runs'])/3600,
        'median_seed_elapsed_seconds':statistics.median(r['seconds'] for r in d['runs'])}
    summary['checks'].update(exact_frontier_rescored=True, official_J1_for_review_candidates=True,
        no_joint_success_in_stored_union=True, original_layouts_preserved=True)
    from bangla_dh.experimental.report import csv_text
    outputs += [write_json(target/'analysis.json',summary),
        write_text(target/'comparison.csv',csv_text(comparison_rows,list(comparison_rows[0]))),
        write_text(target/'REPORT.md',render(summary)),write_text(target/'analysis.py',Path(__file__).read_text(encoding='utf-8'))]
    if preserved()!=original:
        raise ValueError('original scientific/layout files changed')
    for name,digest in inputs.items():
        if sha256_file(PROJECT_ROOT/name)!=digest:
            raise ValueError('source changed during interpretation: '+name)
    revision,clean=repo_state()
    write_json(target/'run-manifest.json',{'season':'e4','version':VERSION,
        'generated_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
        'git_revision':revision,'working_tree_clean':clean,'python':platform.python_version(),
        'parameters':{'source':summary['source'],'caps_percent':[str(c) for c in CAPS],
            'secondary_review_caps_percent':['0.1','0.5','1'], 'selection':'training-only stored union frontier'},
        'input_sha256':inputs,'output_sha256':hash_outputs(outputs),'checks':summary['checks'],
        'elapsed_seconds':round(time.perf_counter()-start,3)})
    print('Finished interpretation:',target/'REPORT.md',flush=True)


if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,default=Path('results/evaluator-e4/rigorous-v1'))
    parser.add_argument('--out',type=Path,default=Path('results/evaluator-e4/interpretation-v1'))
    args=parser.parse_args()
    run(args.source,args.out)
