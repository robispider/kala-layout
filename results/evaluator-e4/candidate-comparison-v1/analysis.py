"""Rescore the requested e4 candidates and compare with hashed e2/e3 evidence."""
from __future__ import annotations

import argparse
import csv
import datetime as dt
from fractions import Fraction
import json
from pathlib import Path
import sys
import time

from bangla_dh import challenge
from bangla_dh.experimental.continuous_counts import DEFAULT, verified_result
from bangla_dh.experimental.evaluate import MODELS
from bangla_dh.experimental.inputs import read_json, load_candidates, TRAIN, HELDOUT
from bangla_dh.experimental.joint_problem import JointProblem
from bangla_dh.experimental.joint_search import evaluate_layout, preserved
from bangla_dh.experimental.report import csv_text
from bangla_dh.experimental.safety import new_run_directory
from bangla_dh.paths import PROJECT_ROOT, write_json, write_text, hash_outputs
from bangla_dh.reference import sha256_file
from bangla_dh.scoring.model import KeyModel

REQUESTED = ('A-013e60b38d2caf28','A-7c36e8f26e6c7142','D-7af0f238d12d0b4a',
    'D-29a057973f8e46f1','A-b4106689d404415b','A-14557e4aab2f81f6','D-fb0954976e8c5a32')
ANCHORS = ('D-8ed0c088f68ad80a','D-072c558b633d1019','D-57ae5853f15edfec')


def compact(row):
    return {'corpus':row['corpus'],'scenario':row['scenario'],'reference':row['reference'],
        'diagnostics':row['diagnostics'],
        'continuous':{k:row['continuous'][k] for k in ('coverage','bounds','same_finger_distance_bounds',
            'same_finger_distance_u_per_spanning_window','within_word_share','space_touching_share')},
        'mechanics':{k:row['mechanics'][k] for k in ('score_direction','bounds','pair_coverage')},
        'engram_order':{k:row['engram_order'][k] for k in ('bounds','coverage')}}


def average(rows, corpora):
    if len(rows)!=len(corpora) or {r['corpus'] for r in rows}!=set(corpora):
        raise ValueError('bad source selection')
    def mean(f): return sum(f(r) for r in rows)/len(rows)
    def interval(f): return {side:mean(lambda r:f(r)[side]) for side in ('lower','upper')}
    return {'J1':mean(lambda r:r['reference']['J1']),
        'E1':mean(lambda r:r['reference']['E1']),'E2':mean(lambda r:r['reference']['E2']),
        'modifier_M':mean(lambda r:r['reference']['M']),
        'cross_space_SF':interval(lambda r:r['continuous']['bounds']['same_finger_different_key']),
        'cross_space_SF_distance':interval(lambda r:r['continuous']['same_finger_distance_bounds']),
        'cross_space_repeats':interval(lambda r:r['continuous']['bounds']['same_key']),
        'engram_pair_credit':interval(lambda r:r['mechanics']['bounds']['engram_avg4']),
        'engram_order_credit':interval(lambda r:r['engram_order']['bounds']),
        'dvorak7_credit':interval(lambda r:r['mechanics']['bounds']['dvorak7']),
        'pair_coverage':mean(lambda r:r['mechanics']['pair_coverage']),
        'triple_coverage':mean(lambda r:r['engram_order']['coverage']),
        'cross_space_coverage':mean(lambda r:r['continuous']['coverage']),
        'escaped_unit_percent':100*mean(lambda r:r['diagnostics']['escaped_unit_share']),
        'shift_share_percent':100*mean(lambda r:r['diagnostics']['shift_share_of_non_space_presses']),
        'presses_per_nonspace_unit':mean(lambda r:r['diagnostics']['keystrokes_per_non_space_unit']),
        'within_word_SF_per_unit':mean(lambda r:r['diagnostics']['same_finger_different_key_per_unit']),
        'within_word_SF_distance_per_unit':mean(lambda r:r['diagnostics']['same_finger_center_distance_u_per_unit'])}


def interval_order(a,b,higher=False):
    if a['lower']>b['upper']+1e-12: return 'better' if higher else 'worse'
    if a['upper']<b['lower']-1e-12: return 'worse' if higher else 'better'
    return 'overlap'


def compare(a,b):
    out = {'J1_change_percent':100*(a['J1']/b['J1']-1),
        'cross_space_SF_change_percent':100*(a['cross_space_SF']['lower']/b['cross_space_SF']['lower']-1),
        'cross_space_SF_distance_change_percent':100*(a['cross_space_SF_distance']['lower']/b['cross_space_SF_distance']['lower']-1),
        'within_word_SF_distance_change_percent':100*(a['within_word_SF_distance_per_unit']/b['within_word_SF_distance_per_unit']-1),
        'within_word_SF_per_unit_change_percent':100*(a['within_word_SF_per_unit']/b['within_word_SF_per_unit']-1),
        'cross_space_repeat_change_pp':100*(a['cross_space_repeats']['lower']-b['cross_space_repeats']['lower']),
        'shift_change_pp':a['shift_share_percent']-b['shift_share_percent'],
        'E1_change':a['E1']-b['E1'],'E2_change':a['E2']-b['E2'],'modifier_M_change':a['modifier_M']-b['modifier_M']}
    for metric in ('engram_pair_credit','engram_order_credit','dvorak7_credit'):
        out[metric+'_lower_change']=a[metric]['lower']-b[metric]['lower']
        out[metric+'_interval_comparison']=interval_order(a[metric],b[metric],higher=True)
    return out


def row_csv(name,style,scenario,scope,a):
    return {'layout':name,'style':style or 'fixed-baseline','fingering':scenario,'scope':scope,'J1':a['J1'],
        'cross_space_SF_percent_lower':100*a['cross_space_SF']['lower'],
        'cross_space_SF_percent_upper':100*a['cross_space_SF']['upper'],
        'cross_space_SF_distance_lower':a['cross_space_SF_distance']['lower'],
        'cross_space_SF_distance_upper':a['cross_space_SF_distance']['upper'],
        'within_word_SF_per_unit':a['within_word_SF_per_unit'],
        'within_word_SF_distance_per_unit':a['within_word_SF_distance_per_unit'],
        'engram_pair_credit_lower':a['engram_pair_credit']['lower'],
        'engram_pair_credit_upper':a['engram_pair_credit']['upper'],
        'engram_order_credit_lower':a['engram_order_credit']['lower'],
        'engram_order_credit_upper':a['engram_order_credit']['upper'],
        'dvorak7_credit_lower':a['dvorak7_credit']['lower'],'dvorak7_credit_upper':a['dvorak7_credit']['upper'],
        'shift_percent':a['shift_share_percent'],'escape_percent':a['escaped_unit_percent'],
        'E1':a['E1'],'E2':a['E2'],'modifier_M':a['modifier_M']}


def bounds(x,digits=6): return f"{x['lower']:.{digits}f}–{x['upper']:.{digits}f}"


def render(d):
    lines=['# Requested candidate comparison against earlier run evidence','',
        'This report compares the seven requested A/D placements with Kala Jhor, Kala Goti, three earlier '
        'experimental D candidates, and the six fixed-layout baselines scored in e2/e3. The completed run '
        'and every original layout/result remain unchanged.','',
        '**Evidence scope:** exact corpus-derived modeled scores, not measured typing speed or comfort. '
        'Training uses the original independently normalized 50/50 Wikipedia/newspaper mix. Held-out '
        'comparisons use one third each of Wikipedia, newspaper and BARD novel news. All layouts use their '
        'own frozen encoder; baselines retain the e2/e3 canonical encoder across fingerings. These already '
        'examined held-out sources support exploratory comparisons.','',
        '**Directions:** lower J1, cross-space SF rate and SF distance are favorable. Higher Engram pair, '
        'Engram order and Dvorak-7 credit are favorable. Their coverage bounds are not statistical confidence '
        'intervals. Interval-overlap comparisons remain unresolved.','',
        '## Requested candidates: training comparison','',
        '| Candidate | Style | J1 | J1 change from Jhor | J1 change from same-style published map | Cross-space SF rate | Cross-space SF distance change from Jhor |',
        '| --- | --- | ---: | ---: | ---: | ---: | ---: |']
    for c in sorted(d['candidates'],key=lambda c:c['training']['model-optimal']['J1']):
        if c['id'] not in REQUESTED: continue
        a=c['training']['model-optimal'];ch=c['training_changes']['model-optimal']
        lines.append(f"| [{c['id']}](layouts/{c['id']}.json) | {c['style']} | {a['J1']:.9f} | "
            f"{ch['vs_Jhor']['J1_change_percent']:+.5f}% | {ch['vs_same_style']['J1_change_percent']:+.5f}% | "
            f"{100*a['cross_space_SF']['lower']:.5f}% | {ch['vs_Jhor']['cross_space_SF_distance_change_percent']:+.5f}% |")
    lines += ['', 'For style A, the same-style reference is Goti; for D it is Jhor. The same-style column '
        'avoids attributing A’s vowel-entry recipe cost to placement alone. None of these candidates has '
        'lower primary training J1 than its same-style published map.','',
        '## Held-out comparison with earlier layouts: primary fingering','',
        'Every row below uses the same three held-out sources and model-optimal fingering. It does not '
        'mix a candidate’s training score with a baseline’s held-out score. Within-word SF distance has '
        'a different denominator from cross-space distance and is shown separately.','',
        '| Layout | J1 | Cross-space SF rate | Cross-space SF distance (u/window) | Within-word SF distance (u/text unit) | Engram pair credit bounds ↑ | Engram order credit bounds ↑ | Escaped units |',
        '| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    all_rows = [(name,a['model-optimal']) for name,a in d['public_heldout'].items()]
    all_rows += [(c['id'],c['heldout']['model-optimal']) for c in d['candidates']]
    for name,a in sorted(all_rows,key=lambda x:x[1]['J1']):
        lines.append(f"| {name} | {a['J1']:.6f} | {100*a['cross_space_SF']['lower']:.4f}% | "
            f"{a['cross_space_SF_distance']['lower']:.6f} | {a['within_word_SF_distance_per_unit']:.6f} | "
            f"{bounds(a['engram_pair_credit'])} | {bounds(a['engram_order_credit'])} | {a['escaped_unit_percent']:.4f}% |")
    lines += ['', 'The baseline J1 here is the e2/e3 canonical-encoder score. It can differ from the '
        'original published scoreboard, which independently selects the best encoder/grid result. The '
        'next section also checks the candidates against that more favorable original J1 benchmark.','',
        '## Favorable baseline benchmarks','',
        '| Fixed baseline | Published best J1 (held-out mean) | Lowest cross-space SF rate across the two fingerings | Lowest cross-space SF distance across the two fingerings |',
        '| --- | ---: | ---: | ---: |']
    for name,a in sorted(d['baseline_envelope'].items(),key=lambda x:x[1]['published_best_J1']):
        lines.append(f"| {name} | {a['published_best_J1']:.6f} | {100*a['best_SF_rate']:.4f}% | {a['best_SF_distance']:.6f} |")
    lines += ['', 'Each column is a favorable benchmark for that baseline, not a claim that all those '
        'minima occur under one encoder/fingering. Published J1 takes the best original grid score '
        'per corpus, then averages the three sources. SF rate/distance take the better equal-weight '
        'e3 average across model-optimal and traditional fingerings. No phonetic layout is compared.','',
        'The registry covers Windows Default, Probhat, Munir Optima (uni), Bornona, UniJoy and National '
        '(Jatiya), plus Jhor/Goti as research references. This does not establish a ranking against '
        'every publicly available Bangla layout, alternative typing system or human typist.','',
        '## Candidate-by-candidate held-out changes from Jhor','',
        '| Candidate | J1 change | Cross-space SF change | Cross-space SF-distance change | Within-word SF-distance change | Engram pair credit lower change | Engram order credit lower change |',
        '| --- | ---: | ---: | ---: | ---: | ---: | ---: |']
    for c in sorted(d['candidates'],key=lambda c:c['heldout']['model-optimal']['J1']):
        ch=c['heldout_changes']['model-optimal']['vs_Jhor']
        lines.append(f"| {c['id']} | {ch['J1_change_percent']:+.4f}% | {ch['cross_space_SF_change_percent']:+.4f}% | "
            f"{ch['cross_space_SF_distance_change_percent']:+.4f}% | {ch['within_word_SF_distance_change_percent']:+.4f}% | "
            f"{ch['engram_pair_credit_lower_change']:+.6f} | {ch['engram_order_credit_lower_change']:+.6f} |")
    lines += ['', 'Credit lower-bound changes are descriptive. The JSON separately records whether '
        'full candidate/reference intervals separate or overlap; a favorable change in a bound is '
        'not automatically a conclusive full-score ranking.','',
        '## Fingering sensitivity','',
        '| Candidate | Traditional held-out J1 | Traditional cross-space SF rate | Traditional SF distance | Traditional Engram pair bounds ↑ | Traditional Engram order bounds ↑ |',
        '| --- | ---: | ---: | ---: | ---: | ---: |']
    for c in sorted(d['candidates'],key=lambda c:c['heldout']['traditional']['J1']):
        a=c['heldout']['traditional']
        lines.append(f"| {c['id']} | {a['J1']:.6f} | {100*a['cross_space_SF']['lower']:.4f}% | "
            f"{a['cross_space_SF_distance']['lower']:.6f} | {bounds(a['engram_pair_credit'])} | {bounds(a['engram_order_credit'])} |")
    lines += ['', '## Evidence checks and downloadable data','',
        '* [Complete source/candidate comparison JSON](comparison.json)',
        '* [Training and held-out metrics for both fingerings](metrics.csv)',
        '* [Per-source candidate scores](per-source.csv)',
        '* [All 126 saved-frontier D layouts below J1 1.9](D-under-1.9-frontier.md)',
        '* [All 6,584 distinct saved D maps below J1 1.9](D-under-1.9-all-saved.csv)','',
        'The D cutoff is exact and applies to training J1. The frontier list includes Jhor; its running '
        'J1 differences are recomputed within the filtered D list. These are saved maps, not all '
        'possible layouts. A-7c36e8f26e6c7142 is above 1.9 training J1 and therefore does not meet '
        'that cutoff, although it is included in the requested seven-candidate review.','',
        'Every selected map agrees exactly with the independent official challenge scorer. Existing '
        'e2/e3 stored-output and completed-run hashes are verified. Some e2/e3 historical Python '
        'input hashes differ after later phases; those differences are disclosed in the JSON, '
        'rather than claiming the current checkout reproduces their historical code snapshots. '
        'Current e4 scoring-code and data hashes match. Baseline J1 and continuous/Engram rows are '
        'joined by identity, corpus and fingering, and their reference J1 values must agree. Original '
        'layout and scientific-file preservation hashes are checked after writing the new analysis.','']
    return '\n'.join(lines)


def run(out):
    started=time.perf_counter();before=preserved()
    e2root=PROJECT_ROOT/'results/evaluator-e2/run-v1'
    e3root=PROJECT_ROOT/'results/evaluator-e3/run-v1'
    statsroot=PROJECT_ROOT/'results/evaluator-e4/mechanical-stats-v1'
    source=PROJECT_ROOT/'results/evaluator-e4/rigorous-v1'
    historical_code_changes=[]
    for root in (e2root,e3root,statsroot,source):
        m=read_json(root/'run-manifest.json')
        for group in ('input_sha256','output_sha256'):
            for path,digest in m[group].items():
                if sha256_file(PROJECT_ROOT/path)!=digest:
                    if root in (e2root,e3root) and group=='input_sha256' and path.startswith('src/') and path.endswith('.py'):
                        historical_code_changes.append({'season':root.parent.name,'path':path,'historical_hash':digest,
                            'current_hash':sha256_file(PROJECT_ROOT/path)})
                    else:
                        raise ValueError('input/source hash mismatch: '+path)
    e2,e2path=verified_result(e2root,'scores.json.gz')
    e3,e3path=verified_result(e3root,'scores.json.gz')
    out=new_run_directory(out)
    e2index={(r['id'],r['corpus'],r['scenario']):r for r in e2['scores']}
    public_rows={}
    for row in e3['scores']:
        if not row['public']: continue
        earlier=e2index[row['id'],row['corpus'],row['scenario']]
        if abs(row['reference']['J1']-earlier['reference']['J1'])>1e-10:
            raise ValueError('e2/e3 reference J1 differs')
        merged={**row,'diagnostics':earlier['diagnostics'],'mechanics':earlier['mechanics']}
        public_rows.setdefault(row['name'],[]).append(compact(merged))
    public_heldout={name:{scenario:average([r for r in rows if r['scenario']==scenario],HELDOUT)
        for scenario in MODELS} for name,rows in public_rows.items()}
    models={scenario:KeyModel.from_grid(path) for scenario,path in MODELS.items()}
    references,_=load_candidates(False)
    problems={r.style:JointProblem(r.style,r.layout) for r in references}
    ref_training={}
    for r in references:
        rows=evaluate_layout(r.style,r.layout,DEFAULT,models)
        ref_training['Kala Jhor' if r.style=='D' else 'Kala Goti']={scenario:average(
            [row for row in rows if row['scenario']==scenario and row['corpus'] in TRAIN],TRAIN) for scenario in MODELS}
    points={r['id']:r for r in read_json(statsroot/'summary.json')['frontier']}
    public=challenge.load_scorer(challenge.SCRIPT);pdata,phash=public.load_data();pmodel=public.Model(pdata)
    dataset={'version':'candidate-comparison-v1','requested_ids':list(REQUESTED),'earlier_experimental_anchors':list(ANCHORS),
        'public_heldout':public_heldout,'public_training_references':ref_training,'candidates':[],'baseline_envelope':{},
        'historical_code_hash_changes':historical_code_changes}
    output=[];metrics=[];source_rows=[]
    for cid in (*REQUESTED,*ANCHORS):
        point=points[cid];style=point['style'];p=problems[style]
        layout=p.assignment(point['perm']);j,s=p.verify(point['perm'])
        if j!=Fraction(point['J1_exact']) or s!=Fraction(point['cross_space_SF_exact']):
            raise ValueError('selected stats differ from exact score')
        submission={'name':'Experimental candidate comparison '+cid,'style':style,'layout':challenge._key_layout(layout)}
        official=public.evaluate(submission,pdata,phash,pmodel)
        if not official['valid'] or Fraction(official['J1_exact'])!=j: raise ValueError('official score differs')
        output.append(write_json(out/'layouts'/(cid+'.json'),submission))
        rows=[compact(r) for r in evaluate_layout(style,layout,DEFAULT,models)]
        train={scenario:average([r for r in rows if r['scenario']==scenario and r['corpus'] in TRAIN],TRAIN) for scenario in MODELS}
        held={scenario:average([r for r in rows if r['scenario']==scenario and r['corpus'] in HELDOUT],HELDOUT) for scenario in MODELS}
        same='Kala Jhor' if style=='D' else 'Kala Goti'
        c={'id':cid,'style':style,'source_seed':point['source_seed'],'J1_exact':str(j),'cross_space_SF_exact':str(s),
            'training':train,'heldout':held,'source_scores':rows,
            'training_changes':{scenario:{'vs_Jhor':compare(train[scenario],ref_training['Kala Jhor'][scenario]),
                'vs_same_style':compare(train[scenario],ref_training[same][scenario])} for scenario in MODELS},
            'heldout_changes':{scenario:{'vs_Jhor':compare(held[scenario],public_heldout['Kala Jhor'][scenario]),
                'vs_same_style':compare(held[scenario],public_heldout[same][scenario]),
                'vs_public_layouts':{name:compare(held[scenario],a[scenario]) for name,a in public_heldout.items()}}
                for scenario in MODELS}}
        dataset['candidates'].append(c)
        for scenario in MODELS:
            metrics += [row_csv(cid,style,scenario,'train-50/50',train[scenario]),row_csv(cid,style,scenario,'heldout-equal-third',held[scenario])]
        for r in rows: source_rows.append(row_csv(cid,style,r['scenario'],r['corpus'],average([r],[r['corpus']])))
        print('Scored',cid,'heldout J1',held['model-optimal']['J1'],'SF',100*held['model-optimal']['cross_space_SF']['lower'],flush=True)
    history=read_json(PROJECT_ROOT/'results/phase3-crosscheck/crosscheck.json')
    for name,entry in history['baselines'].items():
        dataset['baseline_envelope'][name]={'published_best_J1':sum(min(grid['J1'] for grid in entry['scores'][corpus].values()) for corpus in HELDOUT)/3,
            'best_SF_rate':min(a['cross_space_SF']['lower'] for a in public_heldout[name].values()),
            'best_SF_distance':min(a['cross_space_SF_distance']['lower'] for a in public_heldout[name].values())}
    for c in dataset['candidates']:
        a=c['heldout']['model-optimal']
        c['vs_favorable_baseline_envelope']={name:{'J1_change_percent':100*(a['J1']/b['published_best_J1']-1),
            'SF_rate_change_percent':100*(a['cross_space_SF']['upper']/b['best_SF_rate']-1),
            'SF_distance_change_percent':100*(a['cross_space_SF_distance']['upper']/b['best_SF_distance']-1)} for name,b in dataset['baseline_envelope'].items()}
    for name,scenarios in public_heldout.items():
        for scenario,a in scenarios.items(): metrics.append(row_csv(name,None,scenario,'heldout-equal-third',a))
    # Earlier requested D cutoff: include both the nondominated list and every stored map.
    for filename,target in (('frontier.csv','D-under-1.9-frontier.csv'),('all-candidates.csv','D-under-1.9-all-saved.csv')):
        with (statsroot/filename).open(encoding='utf-8',newline='') as stream:
            records=[r for r in csv.DictReader(stream) if r['style']=='D' and Fraction(r['J1_exact'])<Fraction(19,10)]
        previous=problems['D'].reference_j
        for index,r in enumerate(records,1):
            j=Fraction(r['J1_exact']);r['row']=index;r['J1_delta_vs_previous']=float(j-previous);r['J1_delta_vs_previous_percent']=100*float(j/previous-1);previous=j
        output.append(write_text(out/target,csv_text(records,list(records[0]))))
        if filename=='frontier.csv':
            lines=['# Saved-frontier D layouts with exact training J1 below 1.9','',
                '126 rows including Kala Jhor. Original 50/50 training mix; model-optimal fingering. Running J1 differences are within this filtered list.','',
                '| Layout | J1 | J1 change from Jhor | J1 step above | Cross-space SF rate | SF distance change from Jhor |',
                '| --- | ---: | ---: | ---: | ---: | ---: |']
            for r in records:
                lines.append(f"| [{r['name']}](../mechanical-stats-v1/layouts/{r['id']}.json) | {float(r['J1']):.9f} | "
                    f"{float(r['J1_delta_vs_Jhor_percent']):+.5f}% | {float(r['J1_delta_vs_previous']):+.9f} | "
                    f"{float(r['cross_space_SF_rate_percent']):.5f}% | {float(r['SF_distance_delta_vs_Jhor_percent']):+.5f}% |")
            output.append(write_text(out/'D-under-1.9-frontier.md','\n'.join(lines)+'\n'))
    output += [write_json(out/'comparison.json',dataset),write_text(out/'REPORT.md',render(dataset)),
        write_text(out/'metrics.csv',csv_text(metrics,list(metrics[0]))),write_text(out/'per-source.csv',csv_text(source_rows,list(source_rows[0]))),
        write_text(out/'analysis.py',Path(__file__).read_text(encoding='utf-8'))]
    inputs={}
    for root in (e2root,e3root,statsroot,source):
        m=read_json(root/'run-manifest.json');inputs.update(m['input_sha256']);inputs.update(m['output_sha256']);inputs.update(hash_outputs([root/'run-manifest.json']))
    inputs.update(hash_outputs([Path(__file__),PROJECT_ROOT/'results/phase3-crosscheck/crosscheck.json']))
    if preserved()!=before: raise ValueError('original scientific files changed')
    for path,digest in inputs.items():
        if sha256_file(PROJECT_ROOT/path)!=digest: raise ValueError('input changed: '+path)
    write_json(out/'run-manifest.json',{'season':'e4','version':'candidate-comparison-v1','generated_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
        'parameters':{'requested_ids':list(REQUESTED),'anchor_ids':list(ANCHORS),'heldout_weights':{c:'1/3' for c in HELDOUT},
            'training_weights':{c:'1/2' for c in TRAIN},'fingerings':list(MODELS),'D_cutoff_exact':'19/10'},
        'input_sha256':inputs,'output_sha256':hash_outputs(output),
        'checks':{'original_files_preserved':True,'selected_exact_J1_and_SF':True,'official_J1_agreement':True,'e2_e3_reference_J1_agreement':True},
        'elapsed_seconds':round(time.perf_counter()-started,3)})
    print('Finished',out/'REPORT.md',flush=True)


if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,default=Path('results/evaluator-e4/candidate-comparison-v1'))
    run(parser.parse_args().out)
