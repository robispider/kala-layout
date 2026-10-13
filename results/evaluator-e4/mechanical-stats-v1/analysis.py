"""Evidence table for every distinct stored e4 map; no new layout search."""
from __future__ import annotations

import argparse
import datetime as dt
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import sys
import time

from bangla_dh import challenge
from bangla_dh.experimental.continuous import CENTERS, evaluate_cache
from bangla_dh.experimental.continuous_counts import DEFAULT, load_verified
from bangla_dh.experimental.inputs import read_json, load_candidates, TRAIN
from bangla_dh.experimental.joint_problem import JointProblem, WEIGHTS
from bangla_dh.experimental.joint_search import preserved
from bangla_dh.experimental.report import csv_text
from bangla_dh.experimental.safety import new_run_directory
from bangla_dh.paths import PROJECT_ROOT, write_json, write_text, hash_outputs, gzip_text_writer
from bangla_dh.reference import sha256_file
from bangla_dh.search.anneal import Instance


class DistanceModel:
    def __init__(self, model):
        self.model = model

    def effort(self, key):
        return 0.0

    def penalty_keys(self, a, b, same_action):
        if a == b or 'SPACE' in (a, b) or self.model.keys[a].finger != self.model.keys[b].finger:
            return 'cross-space-SF-distance', 0.0
        return 'cross-space-SF-distance', math.dist(CENTERS[a], CENTERS[b])


def distance_instance(problem):
    movement = {}
    for corpus, (counts, total) in problem.raw_pairs.items():
        for pair, n in counts.items():
            movement[pair] = movement.get(pair, 0.0) + float(WEIGHTS[corpus]) * n / total
    return Instance(problem.labels, problem.slots, problem.fixed, {}, movement,
                    DistanceModel(problem.model), 'J0')


def cid_of(style, layout):
    return style+'-'+hashlib.sha256(json.dumps([style, sorted(layout.items())], ensure_ascii=False).encode()).hexdigest()[:16]


def ordered(rows, reference):
    result, previous = [], Fraction(reference['J1_exact'])
    for number, row in enumerate(sorted(rows, key=lambda r: (Fraction(r['J1_exact']), r['style'], r['id'])), 1):
        j, s = Fraction(row['J1_exact']), Fraction(row['cross_space_SF_exact'])
        refj, refs = Fraction(reference['J1_exact']), Fraction(reference['cross_space_SF_exact'])
        r = {**row, 'row': number, 'J1_delta_vs_Jhor': float(j-refj),
            'J1_delta_vs_Jhor_percent': 100*float(j/refj-1),
            'J1_delta_vs_previous': float(j-previous),
            'J1_delta_vs_previous_percent': 100*float(j/previous-1),
            'cross_space_SF_rate_percent': 100*float(s),
            'cross_space_SF_delta_vs_Jhor_pp': 100*float(s-refs),
            'cross_space_SF_delta_vs_Jhor_percent': 100*float(s/refs-1),
            'SF_distance_delta_vs_Jhor_u': row['SF_distance_u_per_spanning_window']-reference['SF_distance_u_per_spanning_window'],
            'SF_distance_delta_vs_Jhor_percent': 100*(row['SF_distance_u_per_spanning_window']/reference['SF_distance_u_per_spanning_window']-1),
            'improves_both_cross_space_measures_vs_Jhor': s < refs and row['SF_distance_u_per_spanning_window'] < reference['SF_distance_u_per_spanning_window']-1e-12}
        result.append(r)
        previous = j
    return result


def csv_rows(rows):
    columns = ('row','name','id','style','J1','J1_delta_vs_Jhor','J1_delta_vs_Jhor_percent',
        'J1_delta_vs_previous','J1_delta_vs_previous_percent','cross_space_SF_rate_percent',
        'cross_space_SF_delta_vs_Jhor_pp','cross_space_SF_delta_vs_Jhor_percent',
        'SF_distance_u_per_spanning_window','SF_distance_delta_vs_Jhor_u',
        'SF_distance_delta_vs_Jhor_percent','improves_both_cross_space_measures_vs_Jhor',
        'source_seed','J1_exact','cross_space_SF_exact')
    return [{key: row[key] for key in columns} for row in rows], list(columns)


def table(rows, linked=True):
    lines = ['| Layout | J1 | J1 Δ from Jhor | J1 Δ from previous row | Cross-space SF rate | SF distance (u/window) | SF distance Δ from Jhor | SF rate + distance improve? |',
        '| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |']
    for r in rows:
        name = f"[{r['name']}](layouts/{r['id']}.json)" if linked else r['name']
        delta = r['SF_distance_delta_vs_Jhor_percent']
        lines.append(f"| {name} | {r['J1']:.9f} | {r['J1_delta_vs_Jhor']:+.9f} "
            f"({r['J1_delta_vs_Jhor_percent']:+.5f}%) | {r['J1_delta_vs_previous']:+.9f} | "
            f"{r['cross_space_SF_rate_percent']:.5f}% | {r['SF_distance_u_per_spanning_window']:.9f} | "
            f"{delta:+.5f}% | {'Yes' if r['improves_both_cross_space_measures_vs_Jhor'] else 'No'} |")
    return lines


def report(data):
    lines = ['# J1 and cross-space movement: complete candidate statistics','',
        '**Kala Jhor is the first row. Every subsequent row is a saved candidate, ordered by increasing J1.** '
        'This report presents the observed compromise between effort and two cross-space movement measures; '
        'it does not combine them into an invented comfort score.','',
        '## Definitions and evidence','',
        '* **J1:** frozen modeled effort per text unit, including its existing Shift cost. Lower is better.',
        '* **J1 Δ from Jhor:** candidate J1 minus Jhor J1. Both the absolute difference and relative percentage are shown.',
        '* **J1 Δ from previous row:** candidate J1 minus the immediately preceding displayed row. This is the requested running difference, not physical finger travel. It depends on which rows a table includes.',
        '* **Cross-space SF rate:** percentage of valid key–space–key windows whose endpoints use the same finger on different physical keys. Lower is better; same-key repeats are separate.',
        '* **SF distance:** summed key-center distance for those same-finger different-key events, divided by all valid spanning windows. Non-SF windows contribute zero. Units are key-pitch units per window, not total hand travel or measured motion.',
        '* **SF distance Δ:** relative change from Jhor’s SF-distance value; negative means less modeled distance.',
        '* **SF rate + distance improve?:** both values must be lower than Jhor. This flag does not assert improvement in every other movement evaluator.','',
        'All numbers use the frozen **model-optimal fingering** and the original **50/50 Wikipedia/newspaper training mix**. '
        'Each source is normalized independently. Each vowel style uses its own encoder. Cross-space endpoint coverage is complete. '
        'These are corpus-derived point values, not human-trial estimates or statistical confidence intervals.','',
        '## Coverage','',
        f"The completed run saved {data['all_candidate_count']:,} distinct style/layout pairs. "
        f"The reconstructed nondominated J1/SF-rate union has {len(data['frontier'])} rows: "
        f"{data['style_frontier_counts']['D']} D and {data['style_frontier_counts']['A']} A, including Jhor and Goti. "
        'These are the frontiers of saved archives; archive pruning means they are not all visited or feasible layouts. '
        'A candidate dominated on J1/SF rate could still differ on another metric, so the full saved collection is also supplied.','',
        f"{data['all_improvement_count']:,} saved rows have both lower cross-space SF rate and lower SF distance than Jhor. "
        'None has lower J1 than Jhor. The strict joint J1/movement objective remains unmet.','',
        '* [All saved candidates, exact J1/SF and distance statistics](all-candidates.csv)',
        '* [All rows improving both cross-space measures](mechanical-improvements.csv)',
        '* [Complete stored J1/SF-rate frontier](frontier.csv)',
        '* [Machine-readable values and permutations](all-candidates.json.gz)',
        '* [Score-direction correction](CORRECTION.md)','',
        'Each CSV computes its running J1 difference within that file’s own increasing-J1 row order. '
        'The improvement-only CSV contains Jhor first as its reference, followed by all qualifying rows. '
        'The table below uses its own displayed rows; its running differences are recomputed for that subset.','',
        '## Selected comparison bands','',
        'For readability, these D examples minimize cross-space SF rate within progressively larger J1-increase bands. '
        'Goti is also included as the published A reference. The bands are analytical examples; they do not change '
        'the accepted strict objective or identify a uniquely best balance.','']
    lines += table(data['preview'])
    lines += ['', '## All candidates on the stored frontier','',
        'The following table contains every row of the reconstructed A/D J1/SF-rate frontier. '
        'A and D are included together and compared with Jhor. Style A uses a different vowel-entry recipe. '
        'All SF-rate and SF-distance changes retain their style-specific denominators.','']
    lines += table(data['frontier'])
    lines += ['', '## Verification and limitations','',
        'Every stored permutation was rescored using exact rational J1 and cross-space SF counts, and compared '
        'with its saved worker result. Distance uses the frozen geometry in binary64. The distance pair-instance '
        'calculation was independently checked against the continuous-window evaluator on reproducibly selected '
        'maps of both styles, including the references and every preview candidate. All frontier exports additionally '
        'agree exactly with the official challenge scorer. Input, output and original-layout hashes are recorded '
        'in this directory’s manifest.','',
        'The original Jhor/Goti files and completed run are preserved. Layout copies here are experimental research '
        'artifacts. There is no new search, changed model constant, measured typing-speed result, optimality proof '
        'or statistical significance claim. Held-out evidence remains in the interpreted report and the balance review; '
        'these tables describe training values only.','',
        'The earlier Engram interpretation was reversed: **Engram pair and triple-order credit is higher-is-better**. '
        'A decrease in its lower-bound score is not an improvement. The J1/SF/count/distance values themselves were '
        'correct. The correction is separate from these requested cross-space statistics.','',
        'To reproduce into a new directory from the repository root:','', '```powershell',
        '$env:PYTHONPATH = "src"',
        'python results/evaluator-e4/mechanical-stats-v1/analysis.py --out work/evaluator-experiments/mechanical-stats-repeat',
        '```','']
    return '\n'.join(lines)


CORRECTION = '''# Correction: direction of Engram scores

Engram pair and triple-order scores award credit: **higher is better**. This is explicit in
[the mechanics documentation](../../../docs/MECHANICS.md) and in the pair evaluator’s
`score_direction = "higher"`. Triple order also awards credit for preferred sequences.

The prose in the earlier interpretation reports and balance review wrongly treated a
decrease in a lower coverage bound as a cost reduction. The stored numbers were correct,
but those Engram gain/regression statements must be reversed. In particular:

* D-072c558b633d1019 lowers both displayed Engram credit bounds under both fingerings;
  those are regressions on these credit measures. Its 17.66% cross-space SF-rate reduction
  and 15.81% SF-distance reduction under primary fingering remain correct.
* The reviewed D candidate at the 0.5% J1 band raises both credit bounds under both
  fingerings; those changes were incorrectly described as Engram regressions.
* The reviewed A candidate at the 0.1% band raises both credit bounds under primary
  fingering; those were incorrectly described as worsening costs.

Lower coverage bounds are not full comfort scores; their changes also need coverage
and source scope to be considered. A cross-space improvement is not evidence that all
mechanical criteria improve. This correction supersedes the earlier Engram prose and
the claim that the balanced D candidate improved both Engram diagnostics. It does not
change any J1, cross-space SF-rate or SF-distance measurement, any found layout, or the
conclusion that the strict primary J1/movement gate found no success.
'''


def run(out):
    started = time.perf_counter()
    source = PROJECT_ROOT/'results/evaluator-e4/rigorous-v1'
    interpretation = PROJECT_ROOT/'results/evaluator-e4/interpretation-v2'
    manifest = read_json(source/'run-manifest.json')
    for group in ('input_sha256','output_sha256','protected_original_sha256'):
        for path, digest in manifest[group].items():
            if sha256_file(PROJECT_ROOT/path) != digest:
                raise ValueError('source hash mismatch: '+path)
    im = read_json(interpretation/'run-manifest.json')
    if sha256_file(interpretation/'analysis.json') != im['output_sha256'][(interpretation/'analysis.json').relative_to(PROJECT_ROOT).as_posix()]:
        raise ValueError('reconstructed frontier hash mismatch')
    frontier_data = read_json(interpretation/'analysis.json')
    before = preserved()
    out = new_run_directory(out)
    references, _ = load_candidates(False)
    problems = {r.style: JointProblem(r.style, r.layout) for r in references}
    distances = {style: distance_instance(p) for style, p in problems.items()}
    refperms = {r.style: tuple(problems[r.style].j1.perm_of(r.layout)) for r in references}
    observed = {}
    for path in sorted((source/'runs').glob('*.json')):
        run = read_json(path)
        if not run['verified']:
            raise ValueError('unverified saved run')
        for row in run['archive']:
            key = run['style'], tuple(row['perm'])
            if key in observed and (observed[key]['j'], observed[key]['s']) != (row['j'], row['s']):
                raise ValueError('inconsistent worker scores for same layout')
            observed.setdefault(key, {**row, 'source_seed': path.stem})
    frontier_keys = {(style, tuple(r['perm'])) for style, info in frontier_data['styles'].items() for r in info['frontier']}
    preview_keys = set(refperms.items())
    for cap in ('0.01','0.03','0.05','0.1','0.2','0.3','0.5','1'):
        p = problems['D']
        row = min((r for r in frontier_data['styles']['D']['frontier'] if
            Fraction(r['J1_exact']) <= p.reference_j*(1+Fraction(cap)/100)),
            key=lambda r: (Fraction(r['movement_exact']), Fraction(r['J1_exact'])))
        preview_keys.add(('D', tuple(row['perm'])))
    # Deterministic independent distance checks, not implementation-mirroring tests.
    check_keys = preview_keys | {k for index,k in enumerate(sorted(observed)) if index%997 == 0}
    caches = {(style,corpus):load_verified(DEFAULT,'style',style,corpus)[0] for style in problems for corpus in TRAIN}
    result, layouts, exports = [], {}, []
    public = challenge.load_scorer(challenge.SCRIPT)
    public_data, public_hash = public.load_data()
    public_model = public.Model(public_data)
    for index, (key, saved) in enumerate(sorted(observed.items()), 1):
        style, perm = key
        p = problems[style]
        j, s = p.exact(perm)
        if (float(j), float(s)) != (saved['j'], saved['s']):
            raise ValueError('exact rescore differs from saved worker result')
        distance = distances[style].score(perm)
        layout = p.assignment(perm)
        cid = cid_of(style, layout)
        name = ('Kala Jhor' if style=='D' else 'Kala Goti') if perm==refperms[style] else cid
        if key in check_keys:
            assignment = {**layout, **p.fixed}
            independent = sum(float(WEIGHTS[corpus])*evaluate_cache(caches[style,corpus],p.model,assignment)
                ['same_finger_distance_u_per_spanning_window'] for corpus in TRAIN)
            if not math.isclose(distance,independent,abs_tol=1e-12,rel_tol=0):
                raise ValueError('distance instance differs from continuous action-window score')
        row = {'id':cid, 'name':name, 'style':style, 'J1':float(j), 'J1_exact':str(j),
            'cross_space_SF_exact':str(s), 'SF_distance_u_per_spanning_window':distance,
            'source_seed':saved['source_seed'], 'perm':list(perm)}
        result.append(row)
        if key in frontier_keys:
            submission = {'name':name if name.startswith('Kala ') else 'Experimental e4 '+cid,
                'style':style,'layout':challenge._key_layout(layout)}
            official = public.evaluate(submission,public_data,public_hash,public_model)
            if not official['valid'] or Fraction(official['J1_exact']) != j:
                raise ValueError('official challenge scorer differs')
            exports.append(write_json(out/'layouts'/(cid+'.json'),submission))
            layouts[cid] = row
        if index%2000==0:
            print(f'{index}/{len(observed)} exact J1/SF rescored and SF distance calculated',flush=True)
    reference = next(r for r in result if r['name']=='Kala Jhor')
    all_rows = ordered(result,reference)
    frontier_rows = ordered(layouts.values(),reference)
    preview = ordered([r for r in result if (r['style'],tuple(r['perm'])) in preview_keys],reference)
    # Improvement-only table retains the explicit first-row reference.
    qualifying = [r for r in all_rows if r['improves_both_cross_space_measures_vs_Jhor']]
    improved_rows = ordered([reference, *qualifying],reference)
    data = {'version':'mechanical-stats-v1','source_run_count':1024,
        'scope':'50/50 separately normalized training sources, model-optimal fingering',
        'all_candidate_count':len(result),'all_improvement_count':len(qualifying),
        'style_frontier_counts':{style:sum(r['style']==style for r in frontier_rows) for style in problems},
        'independent_distance_check_count':len(check_keys),'preview':preview,'frontier':frontier_rows,
        'reference':reference,'metric_directions':{'J1':'lower','cross_space_SF':'lower','SF_distance':'lower',
            'Engram_pair_credit':'higher','Engram_order_credit':'higher'}}
    outputs = exports + [write_json(out/'summary.json',data),write_text(out/'REPORT.md',report(data)),
        write_text(out/'CORRECTION.md',CORRECTION),write_text(out/'analysis.py',Path(__file__).read_text(encoding='utf-8'))]
    for name, rows in (('all-candidates.csv',all_rows),('mechanical-improvements.csv',improved_rows),('frontier.csv',frontier_rows),('preview.csv',preview)):
        records,columns = csv_rows(rows)
        outputs.append(write_text(out/name,csv_text(records,columns)))
    compressed = out/'all-candidates.json.gz'
    with gzip_text_writer(compressed) as stream:
        json.dump(all_rows,stream,ensure_ascii=False,separators=(',',':'))
        stream.write('\n')
    outputs.append(compressed)
    inputs = {**manifest['input_sha256'],**manifest['output_sha256'],**manifest['protected_original_sha256'],
        **hash_outputs([source/'run-manifest.json',interpretation/'run-manifest.json',interpretation/'analysis.json',Path(__file__)])}
    if preserved()!=before:
        raise ValueError('original layout/scientific files changed')
    for path,digest in inputs.items():
        if sha256_file(PROJECT_ROOT/path)!=digest:
            raise ValueError('input changed during analysis: '+path)
    write_json(out/'run-manifest.json',{'season':'e4','version':'mechanical-stats-v1',
        'generated_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
        'parameters':{'training_weights':{c:str(w) for c,w in WEIGHTS.items()},'fingering':'model-optimal',
            'row_order':'increasing exact J1, style, id','running_delta':'J1 minus previous row within each output table',
            'SF_distance_units':'key-pitch units per valid spanning window'},
        'input_sha256':inputs,'output_sha256':hash_outputs(outputs),
        'checks':{'all_saved_J1_and_SF_exact_rescores':True,'independent_distance_checks':len(check_keys),
            'frontier_J1_agrees_with_official_scorer':True,'original_layouts_preserved':True},
        'elapsed_seconds':round(time.perf_counter()-started,3)})
    print('Finished:',out/'REPORT.md',flush=True)


if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,default=Path('results/evaluator-e4/mechanical-stats-v1'))
    args=parser.parse_args()
    run(args.out)
