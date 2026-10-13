"""Record the owner's cross-space trade-off preference without refitting scores.

This documents a post-analysis choice, not a preregistered confirmation.
"""
from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path

from ..paths import PROJECT_ROOT as ROOT, write_json, write_text, hash_outputs
from .artifact_storage import artifact_sha256 as sha256_file,hash_artifacts as hash_outputs
from .balance_study import csv_write, preserved_files

SOURCE=ROOT/'results/balance-stability-v1'
PRIOR=ROOT/'results/balance-study-v2'
NAMED=['A-4dfc1837861ac886','D-8e3f1abe1434b3ea','D-8ed0c088f68ad80a','A-7c36e8f26e6c7142']


def read_csv(path):
    with path.open(encoding='utf-8',newline='') as stream: return list(csv.DictReader(stream))


def main():
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--out',required=True)
    target=Path(parser.parse_args().out).resolve()
    if target.exists(): raise ValueError('new nonexisting directory required')
    preserved=preserved_files(target)
    paths=[SOURCE/name for name in ['experiment-config.json','selections.csv','shortlist.csv','shortlist-stability.csv','run-manifest.json']]
    original=json.loads(paths[-1].read_text(encoding='utf-8'))
    for path in paths[:-1]:
        assert sha256_file(path)==original['output_sha256'][path.relative_to(ROOT).as_posix()],path
    decision={'version':'balance-decision-v1','human_preference':'Allow cross-space regression when other components improve',
        'confirmed_date':'2026-10-13','timing':'confirmed after exploratory results; not preregistered confirmation',
        'source_analysis':'results/balance-stability-v1','effect':'existing eligible regions already permit this; no rescore or changed candidate ordering',
        'cross_space_policy':'no additional hard cap; retain positive cross-space component in the score, so regressions remain penalized',
        'other_improvements':'display actual within-word, effort and order benefits; overlapping order bounds do not establish superiority',
        'limits_retained':{'effort_budget_percent':[.5,1],'primary_within_distance_budget_percent':5,'within_sensitivity_percent':[0,10]},
        'anchors_and_scales':'unchanged fixed acceptable-change scales from balance-study-v2',
        'priority_grid':'unchanged narrow grid from balance-stability-v1',
        'comparison':'same-style references; primary ranking separate from six-training-scope sensitivity ranking',
        'heldout':'already examined, exploratory only; no retuning', 'official_layout_selected':False,'new_search':False}
    write_json(target/'decision-config.json',decision)
    short=read_csv(SOURCE/'shortlist.csv'); stability=read_csv(SOURCE/'shortlist-stability.csv')
    selections=[r for r in read_csv(SOURCE/'selections.csv') if r['within_budget_percent']=='5']
    ids=set(NAMED)|{r['winner'] for r in selections}
    comparison=[]
    for r in short:
        if r['id'] not in ids: continue
        roles=[{k:s[k] for k in ['effort_budget_percent','components','ranking','worst_regret_lower','worst_regret_upper']}
               for s in selections if s['winner']==r['id']]
        comparison.append({**r,'cross_space_regression_permitted':float(r['cross_distance_change_percent'])>0,
            'within_word_improvement':float(r['within_distance_change_percent'])<0,
            'primary_order_credit_increase':float(r['order_credit_change'])>0,
            'selection_roles':json.dumps(roles,separators=(',',':')),
            'interpretation':'trade-off within declared model; not human comfort evidence'})
    csv_write(target/'candidate-comparison.csv',comparison)
    csv_write(target/'stability-comparison.csv',[r for r in stability if r['id'] in ids and r['within_budget_percent']=='5'])
    csv_write(target/'selections.csv',selections)
    lines=['# Feedback: cross-space trade-offs accepted','',
        'The owner permits cross-space regression when other components improve. The existing stability experiment already used this policy: no numerical rerun or refitting is necessary. This preference was confirmed after reviewing exploratory results, so it is not fresh preregistration or confirmation.','',
        'Keep the 0.5%/1% effort caps, the primary 5% within-word-distance cap, fixed acceptable-change scales, positive movement weights and narrow priority grid. Cross-space regression remains a score penalty; it simply does not disqualify a candidate automatically. All real gains and regressions remain visible.','',
        '## Primary minimax candidates','',
        '| Candidate | Role | J1 change | Cross distance change | Within distance change | Order credit change |',
        '| --- | --- | ---: | ---: | ---: | ---: |']
    primary_ids=list(dict.fromkeys(s['winner'] for s in selections if s['ranking']=='primary'))
    for identity in primary_ids:
        r=next(r for r in comparison if r['id']==identity)
        roles='/'.join(sorted({s['components']+' components' for s in selections if s['ranking']=='primary' and s['winner']==identity}))
        lines.append(f"| {identity} | {roles} | {float(r['J1_change_percent']):+.3f}% | {float(r['cross_distance_change_percent']):+.2f}% | {float(r['within_distance_change_percent']):+.2f}% | {float(r['order_credit_change']):+.5f} |")
    lines += ['','A-a280bdc4ca72c6c7 is a legitimate comparison candidate under the accepted policy. It is the primary minimax choice in both component sets and effort bands. Its primary within-word distance falls 14.63%, while cross-space distance rises 18.81%; the worst observed cross-space increase is 29.44%. Across examined sources/fingerings, within distance still improves by at least 3.52%, effort rises by at most 0.326%, and order improvement survives all observed coverage bounds. These are existing modeled observations, not future guarantees.','',
        'For D, keep two priorities visible. D-48319b4b30582e8c is the three-component primary minimax choice with only 0.083% extra effort. D-9ad5412603069cd6 is the order-inclusive minimax choice with 0.273% extra effort and larger primary cross/within reductions. Its positive primary order-credit change does not survive coverage bounds across every examined condition.','',
        'The sensitivity-ranking leaders differ from these primary leaders. Some violate the 5% within-word cap or 0.5% effort cap on other sources/fingerings. candidate-comparison.csv retains all observed feasibility flags and worst regressions, along with the previously named cross-space-oriented alternatives. Do not merge the two rankings or promote a sensitivity winner as uniformly feasible.','',
        'No candidate meets the exploratory worst-regret tolerance of 0.05 across the primary narrow grid at the 5% guardrail. Accepting cross-space trade-offs makes the comparisons consistent with the owner\'s priorities; it does not create a universally near-best layout or calibrate the formula.','',
        'The next research step is to compare these explicit alternatives under a preregistered fixed formula/priority range on genuinely new independent text. Bangla preference and sustained typing trials are required to test comfort. Keep published layouts unchanged.']
    write_text(target/'FEEDBACK.md','\n'.join(lines)+'\n')
    write_text(target/'REPORT.md','# Post-analysis preference record\n\nThis package records the human preference and extracts existing comparison rows. It does not modify frozen scoring, scales, aspirations, metrics, eligibility caps or rankings.\n\n'+ '\n'.join(lines[2:])+'\n')
    for name,h in preserved.items(): assert sha256_file(ROOT/name)==h,name
    paths += [Path(__file__),ROOT/'src/bangla_dh/experimental/balance_study.py']
    write_json(target/'run-manifest.json',{'version':decision['version'],'parameters':decision,
        'input_sha256':hash_outputs(paths),'output_sha256':hash_outputs([p for p in target.iterdir() if p.is_file()]),
        'preserved_original_sha256':preserved,'checks':{'source_hashes_verified':True,'original_artifacts_preserved':True,
        'rescoring_required':False,'scoring_or_rankings_changed':False},'new_search_seeds':[]})
    print('Recorded accepted trade-off policy:',target,'comparison maps',len(comparison),flush=True)


if __name__=='__main__': main()
