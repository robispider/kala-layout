"""Cross-score existing original and Balance v1 maps under both vowel styles.

Run from the repository root with PYTHONPATH=src:
python results/shared-style-check-v1/analyze.py --out work/shared-style-repeat
"""
from __future__ import annotations

import argparse
import csv
import datetime
import json
from pathlib import Path

from bangla_dh.paths import PROJECT_ROOT as ROOT, write_json, write_text, hash_outputs, repo_state
from bangla_dh.experimental.balance_study import PairEngine, average, order_values, preserved_files, csv_write
from bangla_dh.experimental.balance_v1 import evaluate
from bangla_dh.experimental.inputs import TRAIN, HELDOUT, frequency_path, unit_path
from bangla_dh.experimental.mechanics import verify_sources
from bangla_dh.experimental.mechanics_sources import SOURCE, PORTS, GENERATORS
from bangla_dh.reference import sha256_file
from bangla_dh.crosscheck import score_style
from bangla_dh.phase3 import problem_fixed
from bangla_dh.search.problem import load_problem
from bangla_dh.scoring.model import KeyModel, ANSI_GRID, ANSI_TRADITIONAL_GRID

IDS = {
    'A-18fe73cb912ae3f1': 'Original Goti',
    'D-e4a6be48881da590': 'Original Jhor',
    'A-a280bdc4ca72c6c7': 'Balance v1 Goti leader',
    'D-9ad5412603069cd6': 'Balance v1 Jhor leader',
    'D-48319b4b30582e8c': 'Earlier three-component Jhor alternative',
}


def table(headers, rows):
    return '\n'.join(['| ' + ' | '.join(headers) + ' |',
                      '| ' + ' | '.join(['---'] * len(headers)) + ' |'] +
                     ['| ' + ' | '.join(map(str, row)) + ' |' for row in rows])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True)
    out = Path(parser.parse_args().out).resolve()
    if out.exists() and any(p.name != 'analyze.py' for p in out.iterdir()):
        raise ValueError('Use a new output directory')
    preserved = preserved_files(out)
    balance = ROOT / 'results/balance-v1'
    config_path = balance / 'balance-v1-config.json'
    config = json.loads(config_path.read_text(encoding='utf-8'))
    layouts = {}
    inputs = [Path(__file__).resolve(), config_path, balance/'candidate-metrics.csv',
              balance/'candidate-rankings.csv', ROOT/'data/problem-v1.json', ANSI_GRID, ANSI_TRADITIONAL_GRID]
    for identity in IDS:
        path = balance / 'layouts' / (identity + '.json')
        data = json.loads(path.read_text(encoding='utf-8'))
        layouts[identity] = {s: tuple(slot.split('/')) for s, slot in data['layout'].items()}
        inputs.append(path)
    assert all(set(layout) == set(next(iter(layouts.values()))) for layout in layouts.values())
    fixed = problem_fixed(load_problem())
    rows = []
    checks = {'same_52_symbol_set': all(len(m) == 52 and len(set(m.values())) == 52 for m in layouts.values()),
              'official_J1_agrees': True, 'stored_metrics_agree': True, 'stored_R_agrees': True,
              'effort_components_sum': True}
    stored = {}
    with (balance/'candidate-metrics.csv').open(encoding='utf-8', newline='') as stream:
        for r in csv.DictReader(stream):
            stored[r['id'], r['style'], r['corpus'], r['fingering']] = r
    with (balance/'candidate-rankings.csv').open(encoding='utf-8', newline='') as stream:
        rankings = {r['id']: r for r in csv.DictReader(stream) if r['id'] in IDS}
    verify_sources()
    for style in ('A', 'D'):
        cal = config['styles'][style]
        for fingering, grid in (('model-optimal', ANSI_GRID), ('traditional', ANSI_TRADITIONAL_GRID)):
            model = KeyModel.from_grid(grid)
            grouped = {identity: {} for identity in IDS}
            for corpus in (*TRAIN, *HELDOUT):
                print('Scoring', style, fingering, corpus, flush=True)
                engine = PairEngine(style, corpus, fingering)
                for identity, layout in layouts.items():
                    metrics = engine.evaluate(layout)
                    metrics.update(order_values(style, corpus, fingering, layout))
                    direct = score_style(style, layout, corpus, model, fixed)['J1']
                    checks['official_J1_agrees'] &= abs(direct-metrics['J1']) < 1e-10
                    checks['effort_components_sum'] &= abs(metrics['J1']-sum(metrics[k] for k in ('key_effort','pair_effort','shift_effort'))) < 1e-11
                    metrics = {k: v for k, v in metrics.items() if isinstance(v, (int, float, bool, str))}
                    grouped[identity][corpus] = metrics
                inputs += [frequency_path(style, corpus), unit_path(corpus)]
                for season in ('e2', 'e3'):
                    root = ROOT / f'results/evaluator-{season}/run-v1'
                    inputs += [root/'run-manifest.json', root/'counts'/f'style-{style.lower()}-{corpus.replace("/", "-")}.json.gz']
            for identity in IDS:
                grouped[identity]['mix'] = average(*(grouped[identity][c] for c in TRAIN))
                for corpus, metrics in grouped[identity].items():
                    result = evaluate(metrics, cal)
                    primary = corpus == 'mix' and fingering == 'model-optimal'
                    ref = cal['reference']
                    row = {'id': identity, 'name': IDS[identity], 'origin_style': identity[0], 'style': style,
                           'corpus': corpus, 'fingering': fingering, 'primary_balance_scope': primary,
                           **metrics, 'eligible': result['eligible'], 'effort_cap_pass': result['effort_cap_pass'],
                           'within_cap_pass': result['within_cap_pass'],
                           'Balance_R': result['R'] if primary else None,
                           'worst_setting': result['worst_setting'] if primary else None,
                           'J1_change_percent': 100*(metrics['J1']/ref['J1']-1),
                           'cross_change_percent': 100*(metrics['cross_distance']/ref['cross_distance']-1),
                           'within_change_percent': 100*(metrics['within_distance']/ref['within_distance']-1)}
                    prior = stored.get((identity, style, corpus, fingering))
                    if prior:
                        for key in ('J1','cross_distance','within_distance','order_lower','order_upper'):
                            checks['stored_metrics_agree'] &= abs(float(prior[key])-metrics[key]) < 1e-10
                        if primary:
                            previous = rankings[identity]
                            checks['stored_R_agrees'] &= (previous['eligible'] == str(result['eligible']))
                            if result['eligible']:
                                checks['stored_R_agrees'] &= abs(float(previous['R'])-result['R']) < 1e-10
                    rows.append(row)
    primary = {(r['id'],r['style']): r for r in rows if r['primary_balance_scope']}
    held = {(identity,style): sum(r['J1'] for r in rows if r['id']==identity and r['style']==style
            and r['fingering']=='model-optimal' and r['corpus'] in HELDOUT)/3
            for identity in IDS for style in ('A','D')}
    diff = []
    for left,right in ((list(IDS)[0],list(IDS)[1]),(list(IDS)[2],list(IDS)[3])):
        changed = [s for s in layouts[left] if layouts[left][s] != layouts[right][s]]
        diff.append({'left':left,'right':right,'assignment_changes':len(changed),
                     'physical_key_changes':sum(layouts[left][s][0]!=layouts[right][s][0] for s in changed),
                     'layer_changes':sum(layouts[left][s][1]!=layouts[right][s][1] for s in changed)})
    text = ['# One key arrangement with Goti and Jhor vowel styles: existing-map check', '',
            'This diagnostic cross-scores the two published maps, the adopted four-component Balance v1 leaders, and the earlier three-component D alternative. It runs no search and changes no published layout, formula, threshold, calibration or website number.', '',
            'A means Goti vowel entry; D means Jhor context vowels. Each arrangement retains exactly the same 52 symbol positions in both modes. Counts are from each mode\'s own frozen encoder, including repeats, Shift, punctuation and boundary policy.', '',
            '## Primary training effort', '',
            'Original 50/50 Wikipedia/newspaper training mix; model-optimal fingering. Changes compare with the original layout of the SAME mode, not with the other mode. Lower J1 is better.', '',
            table(['Arrangement','Goti J1','Change','Jhor J1','Change','Balance eligibility A / D'],
                  [[IDS[i], f"{primary[i,'A']['J1']:.6f}",f"{primary[i,'A']['J1_change_percent']:+.3f}%",
                    f"{primary[i,'D']['J1']:.6f}",f"{primary[i,'D']['J1_change_percent']:+.3f}%",
                    str(primary[i,'A']['eligible'])+' / '+str(primary[i,'D']['eligible'])] for i in IDS]), '',
            '## Frozen Balance v1', '',
            'Eligibility requires J1 no more than 0.5% above the original same-style layout and within-word same-finger distance no more than 5% above that reference. Cross-space regressions remain permitted and penalized. R is evaluated only for eligible maps on primary training. A and D have separate calibration: their R numbers must not be compared, averaged or combined into a shared score.', '',
            table(['Arrangement','Mode','Effort cap','Within cap','Cross distance change','Within distance change','Order credit bounds','R'],
                  [[IDS[i],s,str(primary[i,s]['effort_cap_pass']),str(primary[i,s]['within_cap_pass']),
                    f"{primary[i,s]['cross_change_percent']:+.2f}%",f"{primary[i,s]['within_change_percent']:+.2f}%",
                    f"{primary[i,s]['order_lower']:.6f}–{primary[i,s]['order_upper']:.6f}",
                    f"{primary[i,s]['Balance_R']:.9f}" if primary[i,s]['eligible'] else 'ineligible'] for i in IDS for s in ('A','D')]), '',
            '## Previously examined held-out texts', '',
            'Equal mean of Wikipedia, newspaper and unseen-news benchmark scores under model-optimal fingering. These are exploratory reused benchmarks, not fresh confirmation; they select no shared arrangement.', '',
            table(['Arrangement','Goti held-out J1','Jhor held-out J1'],[[IDS[i],f"{held[i,'A']:.6f}",f"{held[i,'D']:.6f}"] for i in IDS]), '',
            '## Arrangement differences', '',
            table(['Pair','Changed assignments / 52','Changed physical keys','Changed layer'],
                  [[d['left']+' vs '+d['right'],d['assignment_changes'],d['physical_key_changes'],d['layer_changes']] for d in diff]), '',
            '## Interpretation and scope', '',
            f"{sum(primary[i,'A']['eligible'] and primary[i,'D']['eligible'] for i in IDS)} of these {len(IDS)} existing arrangements pass the adopted Balance v1 eligibility limits in both modes. This finite cross-check does not prove that a jointly eligible shared arrangement is impossible. The original searches optimized styles separately; Balance v1 selected separate style candidates from a saved archive, and no Balance v1 layout search was performed by that report.", '',
            'A shared-map search would be a separate experimental objective, using both original effort references and frozen Balance v1 eligibility limits. Combining A/D R values requires an explicitly defined new rule because their calibration differs. Evaluate both modes separately and retain all movement/order trade-offs. Original J1 scores and published maps remain the reference.', '',
            'scores.csv and scores.json include all five text sets under both fingerings, plus separately normalized training mixes. Only model-optimal training mixes carry Balance v1 R; other rows are sensitivity diagnostics. Order intervals retain unsupported-event coverage bounds. Scores model mechanics and effort, not measured speed or comfort.', '',
            '## Reproduction', '',
            'From the repository root in PowerShell:', '',
            '```powershell', '$env:PYTHONPATH = "src"',
            'python results/shared-style-check-v1/analyze.py --out work/shared-style-repeat', '```', '']
    for name,digest in preserved.items():
        assert sha256_file(ROOT/name) == digest, name
    checks['original_artifacts_preserved'] = True
    assert all(checks.values()), checks
    write_text(out/'REPORT.md', '\n'.join(text))
    write_json(out/'scores.json', {'rows':rows,'layout_differences':diff,'checks':checks})
    csv_write(out/'scores.csv', rows)
    lock = json.loads((SOURCE/'source-lock.json').read_text(encoding='utf-8'))
    inputs += [SOURCE/'source-lock.json']+[SOURCE/entry['file'] for entry in lock['files']]
    inputs += [PORTS/(name+'.py') for name in GENERATORS]
    inputs += list((ROOT/'src/bangla_dh/experimental').glob('*.py'))
    inputs += list((ROOT/'src/bangla_dh/scoring').glob('*.py'))
    inputs += [ROOT/'src/bangla_dh/search/integer.py',ROOT/'src/bangla_dh/search/problem.py',
               ROOT/'src/bangla_dh/crosscheck.py',ROOT/'src/bangla_dh/phase3.py',ROOT/'src/bangla_dh/paths.py']
    head,clean = repo_state()
    write_json(out/'run-manifest.json', {'version':'shared-style-check-v1','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
               'repository_commit':head,'working_tree_clean':clean,'candidate_ids':list(IDS),'new_search':False,'seeds':[],
               'parameters':{'styles':['A','D'],'training_weights':dict.fromkeys(TRAIN,0.5),
                             'heldout_weights':dict.fromkeys(HELDOUT,1/3),'fingerings':['model-optimal','traditional'],
                             'calibration':'frozen Balance v1; eligibility and R separate by style'},
               'input_sha256':hash_outputs(sorted(set(inputs))),
               'output_sha256':hash_outputs([out/'REPORT.md',out/'scores.json',out/'scores.csv']),
               'preserved_original_sha256':preserved,'checks':checks})
    print(json.dumps(checks), flush=True)
    print(out/'REPORT.md', flush=True)


if __name__ == '__main__':
    main()
