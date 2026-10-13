"""Frozen, read-only saved-candidate balance experiment; standard library only.

Run: python -m bangla_dh.experimental.balance_study --out results/balance-study-v1
Repeat in a new directory. No search, official writer, or corpus text export.
"""
from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
import csv
from fractions import Fraction
import hashlib
import itertools
import json
import math
from pathlib import Path
import platform
import statistics
import subprocess
import time

from .. import challenge
from ..paths import PROJECT_ROOT as ROOT, output_path, write_json, write_text, gzip_text_writer, hash_outputs
from .artifact_storage import artifact_sha256 as sha256_file,hash_artifacts as hash_outputs,write_csv
from ..phase3 import problem_fixed
from ..search.problem import load_problem, slots
from ..search.integer import to_int
from ..scoring.model import KeyModel, ANSI_GRID, ANSI_TRADITIONAL_GRID
from .inputs import TRAIN, HELDOUT, read_json, frequency_path, load_candidates, validate_layout
from .continuous_counts import load_verified, DEFAULT
from .continuous import CENTERS, evaluate_cache
from .mechanics import evaluator
from .mechanics_counts import read_counts, committed_style_triples, map_triples
from .actions import from_style, diagnostics, j_reference

MANDATORY = 'A-7c36e8f26e6c7142'
COMP3 = ['J1', 'cross_distance', 'within_distance']
COMP4 = COMP3 + ['order_deficit']
CAPS = [0, .01, .03, .1, .25, .5, .75, 1, 1.5, 2, 3, 5, 10]
SCENARIOS = [(c, f) for f in ('model-optimal', 'traditional') for c in (*TRAIN, 'mix')]


def cid(style, layout):
    canonical = json.dumps([style, sorted((k, list(v)) for k, v in layout.items())], ensure_ascii=False)
    return style + '-' + hashlib.sha256(canonical.encode()).hexdigest()[:16]


def score(values, aspirations, scales, weights, rho, family='augmented'):
    if rho <= 0 or any(t <= 0 or not math.isfinite(t) for t in scales) or any(w <= 0 for w in weights):
        raise ValueError('positive finite scales, weights and augmentation required')
    if not (len(values) == len(aspirations) == len(scales) == len(weights)):
        raise ValueError('component length mismatch')
    if any(v is None or not math.isfinite(v) for v in values):
        raise ValueError('missing or nonfinite component')
    terms = [w * (x-a)/t for x, a, t, w in zip(values, aspirations, scales, weights)]
    return sum(terms)/sum(weights) if family == 'weighted-sum' else max(terms) + rho*sum(terms)


def deficit(lower, upper):
    if not 0 <= lower <= upper <= 1:
        raise ValueError('invalid credit bounds')
    return 1-upper, 1-lower


def csv_write(path, rows):
    return write_csv(path,rows)


def inventory():
    old, paths = load_candidates(True)
    found, provenance, archive_keys = {}, {}, set()
    labels = {s: load_problem()['styles'][s]['searched_symbols'] for s in ('A', 'D')}
    def add(style, layout, origin, names=()):
        validate_layout(style, layout)
        key = (style, tuple(sorted(layout.items())))
        identity = cid(style, layout)
        if identity in found and found[identity]['layout'] != layout:
            raise ValueError('digest collision')
        found.setdefault(identity, {'id': identity, 'style': style, 'layout': layout, 'names': list(names)})
        provenance.setdefault(identity, []).append(origin)
        return key
    for c in old:
        for origin in c.origins:
            add(c.style, c.layout, origin, c.names)
    run_count = Counter()
    for path in sorted((ROOT/'results/evaluator-e4').glob('*/runs/*.json')):
        data = read_json(path)
        style = data['style']
        paths.append(path)
        for index, row in enumerate(data['archive']):
            layout = dict(zip(labels[style], [slots()[p] for p in row['perm']]))
            key = add(style, layout, {'file': path.relative_to(ROOT).as_posix(), 'seed': data['seed'],
                                    'archive_index': index, 'direction': data['direction'], 'start': data['start']})
            if 'rigorous-v1' in path.parts:
                archive_keys.add(key)
        run_count[path.parent.parent.name] += 1
    # e1/e2/e3 contain retained maps; audit that none is omitted.
    seasons = {}
    for season in ('e1', 'e2', 'e3'):
        path = ROOT/f'results/evaluator-{season}/run-v1/candidates.json'
        data = read_json(path); paths.append(path)
        for c in data:
            if 'layout' in c:
                layout = {k: tuple(v.split('/')) for k, v in c['layout'].items()}
                add(c['style'], layout, {'file': path.relative_to(ROOT).as_posix(), 'kind': season})
        seasons[season] = len(data)
    assert MANDATORY in found, 'requested candidate absent'
    return found, provenance, paths, {'rigorous_e4_distinct': len(archive_keys),
        'rigorous_e4_by_style': dict(Counter(s for s, _ in archive_keys)),
        'all_saved_union': len(found), 'by_style': dict(Counter(c['style'] for c in found.values())),
        'run_counts': dict(run_count), 'earlier_inventory_counts': seasons}


class PairEngine:
    def __init__(self, style, corpus, fingering):
        self.model = KeyModel.from_grid(ANSI_GRID if fingering == 'model-optimal' else ANSI_TRADITIONAL_GRID)
        self.record = r = read_json(frequency_path(style, corpus))
        self.cache, _ = load_verified(DEFAULT, 'style', style, corpus)
        self.mechanics = evaluator(fingering)
        self.labels = sorted(set(r['label_counts']) | {a for a, b, n in r['pair_counts']} | {b for a, b, n in r['pair_counts']})
        self.index = idx = {s:i for i,s in enumerate(self.labels)}
        self.actions = slots() + sorted(set(problem_fixed(load_problem()).values())) + [('SPACE', 'base')]
        self.action_index = {a:i for i,a in enumerate(self.actions)}
        self.u = [(idx[s], n) for s,n in r['label_counts'].items() if s != ' ']
        self.pairs = [(idx[a],idx[b],n) for a,b,n in r['pair_counts'] if a != ' ' and b != ' ']
        self.cross = [(idx[a[0]],idx[c[0]],n) for a,b,c,n in self.cache['boundary_triples'] if b[0]=='SPACE' and a[0]!='SPACE' and c[0]!='SPACE']
        self.cross_total = sum(n for a,b,n in self.cross)
        self.pair_total = sum(n for a,b,n in self.pairs)
        self.K = [to_int(self.model.effort(k)) for k,l in self.actions]
        self.M = [to_int(self.model.modifier_effort(k,l)) for k,l in self.actions]
        self.B, self.move, self.dist, self.repeat, self.E, self.D, self.support = [],[],[],[],[],[],[]
        for a in self.actions:
            for b in self.actions:
                move = a[0] != b[0] and a[0] in self.model.keys and b[0] in self.model.keys and self.model.keys[a[0]].finger==self.model.keys[b[0]].finger
                self.B.append(to_int(self.model.penalty_keys(a[0],b[0],a==b)[1]))
                self.move.append(int(move)); self.dist.append(math.dist(CENTERS[a[0]],CENTERS[b[0]]) if move else 0.)
                self.repeat.append(int(a[0]==b[0]))
                val = self.mechanics.pair(a[0],b[0])
                self.E.append(val['engram_avg4'] if val else 0.)
                self.D.append(val['dvorak7'] if val else 0.)
                self.support.append(int(val is not None))
        self.width = len(self.actions)

    def evaluate(self, layout):
        mapping = {**layout, **problem_fixed(load_problem()), ' ': ('SPACE','base')}
        ids = [self.action_index[mapping[s]] for s in self.labels]
        N, width = self.record['N'], self.width
        key = sum(n*self.K[ids[i]] for i,n in self.u)
        mod = sum(n*self.M[ids[i]] for i,n in self.u)
        pair = rate = rep = covered = 0
        distance = ec = dc = 0.
        for a,b,n in self.pairs:
            p = ids[a]*width+ids[b]
            pair += n*self.B[p]; rate += n*self.move[p]; rep += n*self.repeat[p]
            distance += n*self.dist[p]; ec += n*self.E[p]; dc += n*self.D[p]; covered += n*self.support[p]
        cr = rr = 0; cd = 0.
        for a,b,n in self.cross:
            p = ids[a]*width+ids[b]
            cr += n*self.move[p]; cd += n*self.dist[p]; rr += n*self.repeat[p]
        presses = sum(n for _,n in self.u)
        shift = sum(n for i,n in self.u if self.actions[ids[i]][1]=='shift')
        result = {'J1': (key+mod+pair)/(N*1000000), 'J1_exact': str(Fraction(key+mod+pair,N*1000000)),
            'key_effort': key/(N*1000000), 'key_effort_exact': str(Fraction(key,N*1000000)),
            'pair_effort': pair/(N*1000000), 'pair_effort_exact': str(Fraction(pair,N*1000000)),
            'shift_effort': mod/(N*1000000), 'shift_effort_exact': str(Fraction(mod,N*1000000)),
            'cross_rate': cr/self.cross_total, 'cross_rate_exact': str(Fraction(cr,self.cross_total)),
            'cross_distance': cd/self.cross_total, 'cross_repeat': rr/self.cross_total,
            'within_rate': rate/N, 'within_rate_exact': str(Fraction(rate,N)), 'within_distance': distance/N,
            'repeat_per_unit': rep/N, 'repeat_share_pairs': rep/self.pair_total,
            'shift_share': shift/presses, 'escaped_share': self.record['escaped_unit_count']/N,
            'pair_coverage': covered/self.pair_total, 'cross_coverage': 1.,
            'engram_pair_lower': ec/self.pair_total, 'engram_pair_upper': (ec+self.pair_total-covered)/self.pair_total,
            'dvorak_lower': dc/self.pair_total, 'dvorak_upper': (dc+self.pair_total-covered)/self.pair_total,
            'N': N, 'pair_count': self.pair_total, 'spanning_count': self.cross_total,
            'cross_SF_count': cr, 'within_SF_count': rate, 'repeat_count': rep,
            'cross_distance_sum': cd, 'within_distance_sum': distance, 'shift_count': shift,
            'escaped_count': self.record['escaped_unit_count'], 'order_evaluated': False}
        return result


def average(a,b):
    result = {}
    exacts = {k for k in a if k.endswith('_exact')}
    for k in a:
        if k in exacts:
            result[k] = str((Fraction(a[k])+Fraction(b[k]))/2)
        elif isinstance(a[k], bool):
            result[k] = a[k] and b[k]
        elif isinstance(a[k], (int,float)):
            result[k] = (a[k]+b[k])/2
    # Counts in a mix row are source-average counts, never pooled denominators.
    return result


ENGINES = {}
def initialize():
    global ENGINES
    ENGINES = {(s,c,f): PairEngine(s,c,f) for s in ('A','D') for c in TRAIN for f in ('model-optimal','traditional')}


def worker(candidate):
    output = []
    for f in ('model-optimal','traditional'):
        rows = [ENGINES[candidate['style'],c,f].evaluate(candidate['layout']) for c in TRAIN]
        for c,r in zip((*TRAIN,'mix'), [*rows, average(*rows)]):
            output.append({'id':candidate['id'], 'style':candidate['style'], 'corpus':c,'fingering':f, **r})
    return output


def order_values(style, corpus, fingering, layout):
    triples = committed_style_triples(style,corpus)
    if triples is None:
        raise ValueError('missing verified triples')
    assignment = {**layout, **problem_fixed(load_problem())}
    ev = evaluator(fingering)
    # Table lookup preserves upstream body; 0/1 integer credit and count arithmetic.
    keys = sorted(ev.supported_keys)
    index = {k:i for i,k in enumerate(keys)}; width = len(keys)
    table_key = ('order_table',fingering)
    if table_key not in ORDER_CACHE:
        ORDER_CACHE[table_key] = bytes(int(ev.triple(a,b,c)) for a,b,c in itertools.product(keys, repeat=3))
    table = ORDER_CACHE[table_key]
    mapped = {label:index.get(action[0],-1) for label,action in assignment.items()}
    total = covered = credit = 0
    for (a,b,c),n in triples.items():
        i,j,k = mapped[a[0]],mapped[b[0]],mapped[c[0]]
        total += n
        if min(i,j,k) >= 0:
            covered += n; credit += n*table[(i*width+j)*width+k]
    lower,upper = credit/total,(credit+total-covered)/total
    lo,hi = deficit(lower,upper)
    return {'order_lower':lower,'order_upper':upper,'order_deficit_lower':lo,'order_deficit_upper':hi,
            'order_coverage':covered/total,'order_credit_count':credit,'triple_count':total,'supported_triple_count':covered,
            'order_evaluated':True}


ORDER_CACHE = {}


def order_worker(candidate):
    output=[]
    for f in ('model-optimal','traditional'):
        orders=[order_values(candidate['style'],c,f,candidate['layout']) for c in TRAIN]
        for c,r in zip((*TRAIN,'mix'),[*orders,average(*orders)]):
            output.append({'id':candidate['id'],'corpus':c,'fingering':f,**r})
    return output


def config():
    return {'version':'balance-study-v2', 'discovery':{c:'1/2' for c in TRAIN},
        'primary_fingering':'model-optimal','heldout_role':'previously examined; exploratory only; never formula tuning',
        'style_comparison':'separate A and D; no combined ranking',
        'inclusion':'all saved e4 per-seed archives including smoke, all retained e1-e3 and phase best maps; deduplicate style+complete assignment',
        'mandatory_candidate':MANDATORY,'below_1_9_subset':'descriptive only; mandatory included as labeled exception',
        'coverage':'full denominators; unsupported credit 0..1; escapes disclosed outside movement domain; no imputation',
        'primary_components':COMP3, 'order_components':COMP4,
        'external_diagnostics':['Engram avg4 pair credit','Dvorak-7 credit','repeats','Shift','escapes'],
        'aspirations':'per-style component minimum on model-optimal 50/50 training across full saved union; order minimum deficit lower bound',
        'scales':{'acceptable-change':'J1 0.5% of same-style reference; cross distance 20%; within distance 5%; order deficit 0.02 absolute',
                  'percentile':'training q90-q10, nearest-index quantiles; constant component falls back to acceptable-change positive scale'},
        'frozen_anchor_policy':'primary-training anchors/scales reused for every corpus/fingering scenario; no negative-deviation clipping',
        'grid':{'effort_weights':[2,8,16],'cross_weights':[1], 'within_weights':[.5,2], 'order_weights':[.5,2], 'rho':[.01,.1]},
        'formulas':{'augmented':'max(w*r)+rho*sum(w*r)', 'weighted-sum':'sum(w*r)/sum(w)', 'r':'(x-a)/t'},
        'scenarios':[{'corpus':c,'fingering':f} for c,f in SCENARIOS],
        'worst_scenario':'maximum score across six declared training scenarios; separate ranking; no held-out input',
        'bounds':['optimistic deficit=1-credit_upper','pessimistic deficit=1-credit_lower'],
        'order_screen':'all saved union maps: complete training evaluation under both fingerings; expensive order diagnostics parallelized after measured pilot benchmark',
        'pilot_note':'v1 partial run exposed a missing-order shortlist bug: scenario winners were absent from the primary screen. v2 expands order evaluation to the entire union; formulas and parameter grid unchanged; new protocol frozen before v2 formula comparisons',
        'shortlist':'all three/four-component primary and worst-scenario winners plus primary budget winners plus mandatory and published references',
        'effort_caps_percent':CAPS,'within_distance_guardrail_percent':[0,5,10,None],
        'knees':{'chord':'maximum positive distance above normalized endpoint chord on unique budget-selected points',
                 'slope':'largest adjacent slope drop with both effort intervals >=0.03 percentage points; no forced knee',
                 'stability':'compare metric, guardrail, source and fingering; differing locations imply instability'},
        'precision':'J1/components and rates rational from integer counts; distances and pair credits binary64; formula comparison binary64, ties within 1e-12 reported',
        'parameter_win_fraction':'descriptive fraction of finite tested settings, never probability or continuous-region certificate',
        'dependencies':'Python standard library only','new_search':False}


def anchors(rows, references, components):
    output = {}
    for style in ('A','D'):
        part = [r for r in rows if r['style']==style and r['corpus']=='mix' and r['fingering']=='model-optimal' and (len(components)==3 or r['order_evaluated'])]
        ref = references[style,'mix','model-optimal']
        acceptable = [ref['J1']*.005,ref['cross_distance']*.2,ref['within_distance']*.05,.02]
        columns = [[r[k] if k!='order_deficit' else r['order_deficit_lower'] for r in part] for k in components]
        aspiration = [min(v) for v in columns]
        ranges = []
        for i,values in enumerate(columns):
            v=sorted(values); scale=v[round(.9*(len(v)-1))]-v[round(.1*(len(v)-1))]
            ranges.append(scale if scale>0 else acceptable[i])
        for scheme,t in [('acceptable-change',acceptable[:len(components)]),('percentile',ranges)]:
            output[style,scheme]={'aspirations':aspiration,'scales':t,'components':components}
    return output


def grid(components):
    for weights in itertools.product([2,8,16],[1],[.5,2], *([[.5,2]] if len(components)==4 else [])):
        for rho in (.01,.1):
            yield weights,rho,'augmented'
        yield weights,.01,'weighted-sum'


def formula_sweep(rows, frozen, components, full_path=None):
    outcomes=[]; winners=set(); screen=set(); rank_records=[]
    bounds=('point',) if len(components)==3 else ('optimistic','pessimistic')
    stream = gzip_text_writer(full_path) if full_path else None
    handle = stream.__enter__() if stream else None
    writer=csv.writer(handle) if handle else None
    if writer: writer.writerow(['configuration','id','score_lower','score_upper','rank_pessimistic'])
    try:
        for style in ('A','D'):
            by={}
            for r in rows:
                if r['style']==style and (len(components)==3 or r['order_evaluated']):
                    by.setdefault(r['id'],{})[r['corpus'],r['fingering']]=r
            for scheme in ('acceptable-change','percentile'):
                a=frozen[style,scheme]
                for weights,rho,family in grid(components):
                    setting=f'{len(components)}:{style}:{scheme}:{family}:{weights}:{rho}'
                    scenario_scores={}
                    for c,f in SCENARIOS:
                        pair=[]
                        for identity,scopes in by.items():
                            r=scopes[c,f]
                            vals=[r[k] for k in COMP3]
                            low=score(vals+([r['order_deficit_lower']] if len(components)==4 else []),a['aspirations'],a['scales'],weights,rho,family)
                            high=score(vals+([r['order_deficit_upper']] if len(components)==4 else []),a['aspirations'],a['scales'],weights,rho,family)
                            pair.append((identity,low,high))
                        scenario_scores[c,f]=pair
                    indexed={k:{p[0]:p for p in v} for k,v in scenario_scores.items()}
                    scenario_scores['worst','both']=[(identity,max(indexed[c,f][identity][1] for c,f in SCENARIOS),
                        max(indexed[c,f][identity][2] for c,f in SCENARIOS)) for identity in by]
                    for (c,f),pairs in scenario_scores.items():
                        for bound in bounds:
                            ix=1 if bound in ('optimistic','point') else 2
                            ordered=sorted(pairs,key=lambda p:(p[ix],p[0]))
                            win=ordered[0]
                            o={'configuration':setting,'components':len(components),'style':style,'scheme':scheme,'family':family,
                               'weights':json.dumps(weights),'rho':rho,'corpus':c,'fingering':f,'bound':bound,
                               'winner':win[0],'score':win[ix],'runner_up':ordered[1][0],'gap':ordered[1][ix]-win[ix],
                               'ties_1e_12':sum(abs(p[ix]-win[ix])<=1e-12 for p in ordered), 'candidate_count':len(ordered),
                               'coverage_certified_unique_winner': win[2] < min(p[1] for p in pairs if p[0]!=win[0])-1e-12}
                            outcomes.append(o)
                            if c in ('mix','worst'):
                                winners.add(win[0])
                            if c=='mix' and f=='model-optimal': screen.update(p[0] for p in ordered[:10])
                        if c=='mix' and f=='model-optimal':
                            ordered=sorted(pairs,key=lambda p:(p[2],p[0]))
                            if writer:
                                for rank,p in enumerate(ordered,1): writer.writerow([setting,p[0],p[1],p[2],rank])
    finally:
        if stream: stream.__exit__(None,None,None)
    return outcomes,winners,screen


def budgets(rows, references):
    output=[]; selected=set()
    for style in ('A','D'):
        for c,f in SCENARIOS:
            part=[r for r in rows if (r['style'],r['corpus'],r['fingering'])==(style,c,f)]
            ref=references[style,c,f]
            for metric in ('cross_rate','cross_distance'):
                for guard in (None,0,5,10):
                    previous=None
                    for cap in CAPS:
                        limit=Fraction(ref['J1_exact'])*(1+Fraction(str(cap))/100)
                        eligible=[r for r in part if Fraction(r['J1_exact'])<=limit and (guard is None or r['within_distance']<=ref['within_distance']*(1+guard/100)+1e-14)]
                        best=min(eligible,key=lambda r:(r[metric],Fraction(r['J1_exact']),r['id']))
                        dj=100*float(Fraction(best['J1_exact'])/Fraction(ref['J1_exact'])-1)
                        gain=100*(1-best[metric]/ref[metric])
                        slope=(gain-previous[1])/(dj-previous[0]) if previous and dj>previous[0] else None
                        output.append({'style':style,'corpus':c,'fingering':f,'metric':metric,'guard_percent':'none' if guard is None else guard,
                            'cap_percent':cap,'id':best['id'],'J1':best['J1'],'actual_effort_increase_percent':dj,'movement_gain_percent':gain,
                            'within_distance_change_percent':100*(best['within_distance']/ref['within_distance']-1),
                            'marginal_movement_gain_per_effort_pp':slope})
                        selected.add(best['id']); previous=(dj,gain)
    return output,selected


def knees(frontiers):
    out=[]
    groups={tuple(r[k] for k in ('style','corpus','fingering','metric','guard_percent')) for r in frontiers}
    for group in sorted(groups,key=str):
        seen=set(); points=[]
        for r in frontiers:
            if tuple(r[k] for k in ('style','corpus','fingering','metric','guard_percent'))==group and r['id'] not in seen:
                points.append(r); seen.add(r['id'])
        x=[r['actual_effort_increase_percent'] for r in points]; y=[r['movement_gain_percent'] for r in points]
        chord=slope=None
        if len(points)>=3 and x[-1]>x[0] and y[-1]>y[0]:
            d=[((b-y[0])/(y[-1]-y[0])-(a-x[0])/(x[-1]-x[0]))/math.sqrt(2) for a,b in zip(x,y)]
            k=max(range(1,len(points)-1),key=lambda i:d[i])
            if d[k]>0: chord=points[k]
            drops=[]
            for i in range(1,len(points)-1):
                if x[i]-x[i-1]>=.03 and x[i+1]-x[i]>=.03:
                    left=(y[i]-y[i-1])/(x[i]-x[i-1]); right=(y[i+1]-y[i])/(x[i+1]-x[i])
                    if left>right: drops.append((left-right,i,left,right))
            if drops: slope=points[max(drops)[1]]
        out.append(dict(zip(('style','corpus','fingering','metric','guard_percent'),group)) | {
            'chord_id':chord['id'] if chord else None,'chord_effort_percent':chord['actual_effort_increase_percent'] if chord else None,
            'slope_id':slope['id'] if slope else None,'slope_effort_percent':slope['actual_effort_increase_percent'] if slope else None})
    return out


def definitions():
    common={'training_counts_exist':True,'source_weighting':'normalize each source with its own denominator then average 1/2 each',
            'uncertainty':'deterministic corpus quantities; unsupported-credit bounds are not statistical confidence intervals'}
    descriptions={
        'J1':('key + pair + Shift effort','modeled effort/text unit','lower','N, including space and escaped units','Shift priced per shifted action; repeated identical actions have zero pair penalty; escapes break pairs','frozen J1'),
        'key_effort':('sum action count times frozen key effort','effort/text unit','lower','N','includes repeated presses; excludes modifier presses here','J1 E1'),
        'pair_effort':('sum directed action pair counts times frozen penalty, including neighbor benefit','effort/text unit','lower','N','same action free; same key differing layers penalized; spaces zero','J1 E2; overlaps SF and Engram pair'),
        'shift_effort':('sum Shift actions times other-hand Shift cost','effort/text unit','lower','N','no Shift bigram penalty; no AltGr in A/D','J1 M'),
        'cross_rate':('same finger, different physical endpoint keys across exactly one space','events/spanning window','lower','all valid key-space-key windows','modifiers excluded; repeats separate; escapes and paragraph/document ends reset','e4 objective'),
        'cross_distance':('SF different-key endpoint center distances summed; other windows zero','key pitch/spanning window','lower','all valid key-space-key windows','binary64 Euclidean centers; excludes modifier travel and repeats','cross rate times conditional SF distance'),
        'within_rate':('within-word nonspace consecutive SF different-key count','events/text unit','lower','N','repeats excluded; modifiers excluded; escapes reset','J1 SF component but different event definition'),
        'within_distance':('within-word SF different-key center distance sum','key pitch/text unit','lower','N','binary64; repeats zero; modifier travel excluded; escapes reset','J1 row penalties and within rate'),
        'engram_pair':('source generator mean of row separation, same row, same finger, outside credit','credit/nonspace pair','higher','all within-word nonspace pairs','layers projected; modifiers excluded; repeats retained and SF credit zero','J1 geometry/fingers; Dvorak distribution/row/columns'),
        'order':('upstream alternating hand or strictly monotonic three-finger sequence credit','credit/within-word triple','higher','all valid within-word triples','layers projected; repeated fingers credit zero; unsupported keys retain 0..1 mass; escapes reset','fingers/hand overlap; sequence direction adds information'),
        'order_deficit':('1-credit; endpoints [1-credit_upper,1-credit_lower]','deficit/triple','lower','same as order','same scope as order; do not reverse endpoints incorrectly','order exactly complementary'),
        'dvorak':('source seven-criterion sum/7','credit/nonspace pair','higher','all within-word nonspace pairs','layers projected, modifier excluded; repeats kept; unsupported 0..1','J1 key strength/home/rows; Engram pair'),
        'repeat_per_unit':('same physical-key adjacent within-word pair count','repeats/text unit','descriptive','N','base/Shift same physical key included; Shift presses excluded','Engram same-finger penalizes repeats; J1 identical action free'),
        'repeat_share_pairs':('same physical-key pair count/pair count','fraction','descriptive','all within-word nonspace pairs','same scope as repeat_per_unit','repeat_per_unit'),
        'cross_repeat':('identical physical endpoints across space','fraction','descriptive','all spanning windows','modifiers excluded','excluded from cross SF movement'),
        'shift_share':('shifted nonspace actions/nonspace presses','fraction','descriptive','nonspace presses','counts Shift-marked actions, not separate modifier events','J1 M'),
        'escaped_share':('escaped typing units/N','fraction','lower','N','escaped text not assigned invented movement; outside-inventory also reported by source cache','domain-completeness diagnostic')}
    out={}
    for key,(definition,unit,direction,denominator,events,overlap) in descriptions.items():
        out[key]={**common,'definition':definition,'units':unit,'preferred_direction':direction,'denominator':denominator,
            'event_and_modifier_repeat_escape_policy':events,'overlap':overlap,
            'coverage':'A/D physical SF movement complete; credit bounds sum known credit plus 0..1 unknown mass; missing/zero event denominator rejected'}
    out['distance_combination']={'policy':'never add cross_distance to within_distance; normalized components have separately declared scales; no common-denominator total used'}
    out['mix_counts']={'policy':'mixed count fields are average source counts for audit only; never divide them to reconstruct mixed rates'}
    out['baseline_scope']={'policy':'six fixed baselines use saved canonical encodings; training counts unavailable in e2/e3, exploratory held-out only; historical best-of-fingering J1 not mixed into scenario-specific comparisons'}
    return out


def verify_sample(candidate, rows):
    for r in rows:
        if r['corpus']=='mix': continue
        model=KeyModel.from_grid(ANSI_GRID if r['fingering']=='model-optimal' else ANSI_TRADITIONAL_GRID)
        record=read_json(frequency_path(candidate['style'],r['corpus']))
        tables=from_style(record,{**candidate['layout'],**problem_fixed(load_problem())})
        official=j_reference(tables,model); diag=diagnostics(tables,model)
        assert abs(official['J1']-r['J1'])<1e-11
        assert abs(diag['same_finger_center_distance_u_per_unit']-r['within_distance'])<1e-12
        cache,_=load_verified(DEFAULT,'style',candidate['style'],r['corpus'])
        continuous=evaluate_cache(cache,model,{**candidate['layout'],**problem_fixed(load_problem())})
        assert abs(continuous['same_finger_distance_u_per_spanning_window']-r['cross_distance'])<1e-12
        mechanics=evaluator(r['fingering']).score(tables)
        assert abs(mechanics['bounds']['engram_avg4']['lower']-r['engram_pair_lower'])<1e-12
        if r['order_evaluated']:
            order=evaluator(r['fingering']).score_triples(map_triples(committed_style_triples(candidate['style'],r['corpus']),{**candidate['layout'],**problem_fixed(load_problem())}))
            assert abs(order['bounds']['lower']-r['order_lower'])<1e-12
    if any(r['corpus']=='mix' and r['fingering']=='model-optimal' for r in rows):
        expected=challenge.exact_j1(candidate['style'],candidate['layout'],{c:.5 for c in TRAIN},load_problem())
        observed=next(r for r in rows if r['corpus']=='mix' and r['fingering']=='model-optimal')
        assert expected==Fraction(observed['J1_exact'])


def preserved_files(target):
    tracked=subprocess.run(['git','ls-files','-z'],cwd=ROOT,capture_output=True,check=True).stdout.decode().split('\0')
    paths={ROOT/p for p in tracked if p and (ROOT/p).is_file()}
    paths.update(p for p in (ROOT/'results').rglob('*') if p.is_file() and not p.is_relative_to(target) and '__pycache__' not in p.parts)
    # Include pre-existing untracked experimental source/test files as evidence.
    paths.update((ROOT/p) for p in subprocess.run(['git','ls-files','--others','--exclude-standard','-z'],cwd=ROOT,capture_output=True,check=True).stdout.decode().split('\0') if p and (ROOT/p).is_file() and not (ROOT/p).is_relative_to(target))
    return hash_outputs(list(paths))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',required=True); parser.add_argument('--workers',type=int,default=8)
    args=parser.parse_args(); target=Path(args.out).resolve()
    if target.exists(): raise ValueError('new nonexisting output directory required')
    if not 1<=args.workers<=28: raise ValueError('workers must be 1..28')
    protected=preserved_files(target)
    status=subprocess.run(['git','status','--short'],cwd=ROOT,capture_output=True,text=True,check=True).stdout
    found,provenance,inputs,audit=inventory()
    # Persist protocol before evaluation, screening, scales or formula winners.
    frozen_config=config(); write_json(target/'experiment-config.json',frozen_config)
    config_hash=sha256_file(target/'experiment-config.json')
    write_json(target/'metric-definitions.json',definitions()); write_json(target/'inventory.json',audit)
    with gzip_text_writer(target/'candidate-provenance.json.gz') as stream:
        json.dump([{'id':k,'style':v['style'],'layout':{s:'/'.join(a) for s,a in v['layout'].items()},'names':v['names'],'origins':provenance[k]} for k,v in sorted(found.items())],stream,ensure_ascii=False)
    print('Frozen protocol; inventory:',audit,flush=True)
    initialize()
    sample=[found[k] for k in sorted(found)[:8]]
    start=time.perf_counter(); benchmark_rows=[worker(c) for c in sample]; pair_seconds=time.perf_counter()-start
    start=time.perf_counter(); order_values(sample[0]['style'],TRAIN[0],'model-optimal',sample[0]['layout']); warm=time.perf_counter()-start
    start=time.perf_counter(); order_values(sample[0]['style'],TRAIN[0],'model-optimal',sample[0]['layout']); order_seconds=time.perf_counter()-start
    benchmark={'pair_seconds_8_candidates_6_scopes':pair_seconds,'order_first_source_seconds_including_table':warm,
        'order_warm_source_seconds':order_seconds,'full_order_4_scopes_serial_estimate_seconds':order_seconds*len(found)*4,
        'order_staging_rule':frozen_config['order_screen']}
    write_json(target/'benchmark.json',benchmark); print('Benchmark:',benchmark,flush=True)
    rows=[]; start=time.perf_counter()
    with ProcessPoolExecutor(max_workers=args.workers,initializer=initialize) as pool:
        for i,result in enumerate(pool.map(worker,[found[k] for k in sorted(found)],chunksize=64),1):
            rows.extend(result)
            if i%2000==0: print('Primary candidates',i,'elapsed seconds',round(time.perf_counter()-start,1),flush=True)
    references={(r['style'],r['corpus'],r['fingering']):r for r in rows if found[r['id']]['names'] and any(n in ('Kala Goti','Kala Jhor') for n in found[r['id']]['names'])}
    refs={s:references[s,'mix','model-optimal']['id'] for s in ('A','D')}
    frontiers,budget_screen=budgets(rows,references); csv_write(target/'frontiers.csv',frontiers)
    knee_rows=knees(frontiers); csv_write(target/'knees.csv',knee_rows)
    frozen3=anchors(rows,references,COMP3)
    write_json(target/'frozen-scales-3.json',{str(k):v for k,v in frozen3.items()})
    outcomes3,winners3,screen=formula_sweep(rows,frozen3,COMP3,target/'formula-all-candidates-3.csv.gz')
    earlier={k for k,v in provenance.items() if any(o.get('kind') in ('runs','polish','confirmation','earlier','published','e1','e2','e3') for o in v)}
    screen = set(found)
    write_json(target/'order-screen.json',{'ids':sorted(screen),'rule':frozen_config['order_screen'],'count':len(screen)})
    print('Primary complete:',len(found),'candidates. Full training order coverage:',len(screen),flush=True)
    start=time.perf_counter()
    row_index={(r['id'],r['corpus'],r['fingering']):r for r in rows}
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for i,result in enumerate(pool.map(order_worker,[found[k] for k in sorted(screen)],chunksize=64),1):
            for order in result:
                row_index[order['id'],order['corpus'],order['fingering']].update(order)
            if i%2000==0: print('Order diagnostics',i,'elapsed seconds',round(time.perf_counter()-start,1),flush=True)
    frozen4=anchors(rows,references,COMP4)
    write_json(target/'frozen-scales-4.json',{str(k):v for k,v in frozen4.items()})
    outcomes4,winners4,_=formula_sweep(rows,frozen4,COMP4,target/'formula-all-candidates-4.csv.gz')
    outcomes=outcomes3+outcomes4; csv_write(target/'formula-sweep.csv',outcomes)
    short_ids=winners3|winners4|{r['id'] for r in frontiers if r['corpus']=='mix' and r['fingering']=='model-optimal'}|{MANDATORY}|set(refs.values())
    # Held-out evaluation only after formula choices and shortlist are finished.
    for style in ('A','D'):
        for c in HELDOUT:
            for f in ('model-optimal','traditional'):
                engine=PairEngine(style,c,f)
                for identity in sorted(short_ids):
                    candidate=found[identity]
                    if candidate['style']!=style: continue
                    r={'id':identity,'style':style,'corpus':c,'fingering':f,**engine.evaluate(candidate['layout'])}
                    r.update(order_values(style,c,f,candidate['layout'])); rows.append(r)
                    if identity==refs[style]: references[style,c,f]=r
    shortlist=make_shortlist(short_ids,rows,found,references,outcomes)
    csv_write(target/'shortlist.csv',shortlist)
    csv_write(target/'candidate-metrics.csv',sorted(rows,key=lambda r:(r['id'],r['fingering'],r['corpus'])))
    checks={}
    for identity in sorted(short_ids):
        verify_sample(found[identity],[r for r in rows if r['id']==identity])
    checks['shortlist_official_exact_J1_and_independent_metrics']=len(short_ids)
    # Independently replay deterministic full-row evaluations on a digest sample.
    for c,expected in zip(sample,benchmark_rows): assert worker(c)==expected
    checks['deterministic_replay_candidates']=len(sample)
    legacy=read_counts(ROOT/'results/evaluator-e4/mechanical-stats-v1/all-candidates.json.gz')
    by_primary={r['id']:r for r in rows if r['corpus']=='mix' and r['fingering']=='model-optimal'}
    for r in legacy:
        actual=by_primary[r['id']]
        assert Fraction(actual['J1_exact'])==Fraction(r['J1_exact'])
        assert Fraction(actual['cross_rate_exact'])==Fraction(r['cross_space_SF_exact'])
        assert abs(actual['cross_distance']-r['SF_distance_u_per_spanning_window'])<1e-12
    checks['all_legacy_e4_exact_J1_rate_and_distance']=len(legacy)
    baseline_rows=baseline_inventory(target)
    summary={'inventory':audit,'primary_fully_evaluated':len(found),'all_requested_metrics_training_both_fingerings':len(screen),
        'shortlisted_heldout_both_fingerings':len(short_ids),'formula_settings_outcomes':len(outcomes),
        'baseline_heldout_rows':len(baseline_rows),'checks':checks}
    write_json(target/'summary.json',summary)
    render_reports(target,summary,shortlist,frontiers,knee_rows,outcomes,rows,references,found,benchmark)
    plots(target,frontiers,rows,shortlist,outcomes,references)
    assert sha256_file(target/'experiment-config.json')==config_hash
    current={p:sha256_file(ROOT/p) for p in protected}
    assert current==protected,'original file changed'
    checks['all_original_file_hashes_preserved']=len(protected)
    inputs += [p for p in (ROOT/'src/bangla_dh').rglob('*.py')]
    inputs += [p for p in (ROOT/'tests').glob('*.py')]
    inputs += [p for folder in ('data/evaluators/mechanics-v1','results/evaluator-e2/run-v1/counts','results/evaluator-e3/run-v1/counts') for p in (ROOT/folder).rglob('*') if p.is_file()]
    inputs += [frequency_path(s,c) for s in ('A','D') for c in (*TRAIN,*HELDOUT)]
    inputs += [ANSI_GRID,ANSI_TRADITIONAL_GRID,ROOT/'data/problem-v1.json',ROOT/'data/baselines/registry.json',ROOT/'results/evaluator-e4/mechanical-stats-v1/all-candidates.json.gz']
    outputs=[p for p in target.rglob('*') if p.is_file()]
    manifest={'version':'balance-study-v2','python':platform.python_version(),'platform':platform.platform(),
        'git_revision':subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True).stdout.strip(),
        'working_tree_before':status,'parameters':frozen_config,'workers':args.workers,'new_search_seeds':[],
        'candidate_provenance':'candidate-provenance.json.gz','input_sha256':hash_outputs(sorted(set(inputs))),
        'output_sha256':hash_outputs(outputs),'preserved_original_sha256':protected,'checks':checks,
        'config_frozen_sha256':config_hash,'existing_results_changed':False,
        'manifest_self_hash':'excluded to avoid self-reference; validate all listed artifacts'}
    write_json(target/'run-manifest.json',manifest)
    print('Completed',target,summary,flush=True)


def make_shortlist(ids,rows,found,refs,outcomes):
    output=[]
    for identity in sorted(ids):
        c=found[identity]; style=c['style']
        primary=next(r for r in rows if r['id']==identity and r['corpus']=='mix' and r['fingering']=='model-optimal')
        ref=refs[style,'mix','model-optimal']
        part=[r for r in rows if r['id']==identity]
        wins=[o for o in outcomes if o['winner']==identity]
        changes=lambda k:[100*(r[k]/refs[style,r['corpus'],r['fingering']][k]-1) for r in part]
        output.append({'id':identity,'style':style,'name':', '.join(c['names']) or identity,'J1':primary['J1'],
            'J1_change_percent':100*(primary['J1']/ref['J1']-1),'cross_rate_change_percent':100*(primary['cross_rate']/ref['cross_rate']-1),
            'cross_distance_change_percent':100*(primary['cross_distance']/ref['cross_distance']-1),
            'within_distance_change_percent':100*(primary['within_distance']/ref['within_distance']-1),
            'engram_pair_credit_change':primary['engram_pair_lower']-ref['engram_pair_lower'],
            'order_credit_change':primary['order_lower']-ref['order_lower'], 'order_coverage':primary['order_coverage'],
            'order_credit_improvement_survives_bounds':primary['order_lower']>ref['order_upper'],
            'order_credit_regression_survives_bounds':primary['order_upper']<ref['order_lower'],
            'all_observed_cross_distance_improve':max(changes('cross_distance'))<0,
            'worst_J1_change_percent':max(changes('J1')),'worst_cross_distance_change_percent':max(changes('cross_distance')),
            'worst_within_distance_change_percent':max(changes('within_distance')),
            'fingering_or_source_cross_reversal':min(changes('cross_distance'))<0<max(changes('cross_distance')),
            'primary_grid_wins':sum(o['corpus']=='mix' and o['fingering']=='model-optimal' for o in wins),
            'worst_scenario_grid_wins':sum(o['corpus']=='worst' for o in wins),
            'coverage_certified_grid_wins':sum(o['coverage_certified_unique_winner'] for o in wins),
            'winning_conditions':json.dumps([{k:o[k] for k in ('components','scheme','family','weights','rho','corpus','fingering','bound')} for o in wins],separators=(',',':')),
            'below_1_9':primary['J1']<1.9,'threshold_exception':identity==MANDATORY and primary['J1']>=1.9,
            'symbol_relocations':json.dumps({s:['/'.join(found[ref['id']]['layout'][s]),'/'.join(a)] for s,a in c['layout'].items() if a!=found[ref['id']]['layout'][s]},ensure_ascii=False),
            'key_effort_delta':primary['key_effort']-ref['key_effort'],'pair_effort_delta':primary['pair_effort']-ref['pair_effort'],
            'shift_effort_delta':primary['shift_effort']-ref['shift_effort']})
    return output


def baseline_inventory(target):
    e2=read_counts(ROOT/'results/evaluator-e2/run-v1/scores.json.gz')['scores']
    e3=read_counts(ROOT/'results/evaluator-e3/run-v1/scores.json.gz')['scores']
    lookup={(r['id'],r['corpus'],r['scenario']):r for r in e3}
    out=[]
    for r in e2:
        if not r['id'].startswith('baseline:'): continue
        other=lookup[r['id'],r['corpus'],r['scenario']]
        out.append({'id':r['id'],'name':r['name'],'corpus':r['corpus'],'fingering':r['scenario'],
            'J1':r['reference']['J1'],'pair_coverage':r['mechanics']['pair_coverage'],
            'engram_pair_lower':r['mechanics']['bounds']['engram_avg4']['lower'],
            'engram_pair_upper':r['mechanics']['bounds']['engram_avg4']['upper'],
            'order_lower':r['engram_order']['bounds']['lower'],'order_upper':r['engram_order']['bounds']['upper'],
            'escaped_share':r['diagnostics']['escaped_unit_share'],
            'cross_distance':other['continuous']['same_finger_distance_u_per_spanning_window'],
            'scope':'saved held-out diagnostic; no committed baseline training counts; excluded from formula selection'})
    csv_write(target/'baseline-inventory.csv',out)
    return out


def render_reports(target,summary,shortlist,frontiers,knee_rows,outcomes,rows,refs,found,benchmark):
    # Concrete findings generated from observed numbers, never a predetermined winner.
    primary_out=[o for o in outcomes if o['corpus']=='mix' and o['fingering']=='model-optimal']
    wins=Counter(o['winner'] for o in primary_out)
    lines=['# Feedback: exploratory balance study','',
        '**No stable single winner. No official layout selection or human comfort validation.**','',
        f"1. **Coverage:** independently recovered {summary['inventory']['rigorous_e4_distinct']:,} distinct rigorous-e4 style/layout pairs; full saved union {summary['primary_fully_evaluated']:,}. All union maps have exact training J1/components and rates, binary64 distances and pair-credit bounds under both fingerings and both training sources. All requested metrics including order were evaluated for {summary['all_requested_metrics_training_both_fingerings']:,} training-screened maps. {summary['shortlisted_heldout_both_fingerings']} shortlisted maps received exploratory held-out checks. Four-component results concern the screened set only.",
        '2. **Knee:** endpoint-chord and local-slope-drop methods were applied across both movement metrics, four guardrails, sources and fingerings. Locations below show method/condition dependence; no universal knee is established. Budget caps provide defensible choices without pretending to identify one ergonomic optimum.','',
        '| Style | Metric | Guard | Chord knee effort % | Slope-drop knee effort % |', '| --- | --- | --- | ---: | ---: |']
    for r in knee_rows:
        if r['corpus']=='mix' and r['fingering']=='model-optimal':
            lines.append(f"| {r['style']} | {r['metric']} | {r['guard_percent']} | {r['chord_effort_percent']} | {r['slope_effort_percent']} |")
    lines+=['','3. **Low-effort compromises:** same-style, primary 50/50 training references; rate and distance optimized separately. Negative changes below mean improvement.','',
        '| Style | Effort cap % | Candidate | Actual J1 increase % | Cross-distance gain % | Within-distance change % |', '| --- | ---: | --- | ---: | ---: | ---: |']
    selected=[]
    for style in ('A','D'):
        for cap in (.1,.25,.5,1):
            r=next(r for r in frontiers if r['style']==style and r['corpus']=='mix' and r['fingering']=='model-optimal' and r['metric']=='cross_distance' and r['guard_percent']==5 and r['cap_percent']==cap)
            lines.append(f"| {style} | {cap} | {r['id']} | {r['actual_effort_increase_percent']:.5f} | {r['movement_gain_percent']:.3f} | {r['within_distance_change_percent']:+.3f} |")
            selected.append(r['id'])
    lines+=['','4. **Formula dependence:** training-only component minima make trade-offs selectable. The tested scales and positive effort emphasis are experimental choices, not calibrated ergonomic weights. The primary grid produced '+str(len(wins))+' distinct winners. Most frequent primary winners: '+', '.join(f'{k} ({v} finite settings)' for k,v in wins.most_common(6))+'. Wins count tested settings, never probability. See formula-sweep.csv for source, fingering, weights, scales, augmentation, weighted-sum controls and worst-scenario reversals.','',
        '5. **Hidden regressions:** order and pair credit are higher-is-better. D-072c558b633d1019 was previously misinterpreted: its declining credits are regressions. Cross-space savings can increase within-word distance; the zero/5/10% guardrails expose this. Selected examples and worst observed regressions follow.','',
        '| Candidate | J1 Δ % | Cross distance Δ % | Within distance Δ % | Order credit Δ | Worst cross Δ % | Worst within Δ % |', '| --- | ---: | ---: | ---: | ---: | ---: | ---: |']
    useful=set(selected)|{MANDATORY,'D-072c558b633d1019','D-57ae5853f15edfec'}|{k for k,v in wins.most_common(4)}
    for r in shortlist:
        if r['id'] in useful:
            lines.append(f"| {r['id']} | {r['J1_change_percent']:+.5f} | {r['cross_distance_change_percent']:+.3f} | {r['within_distance_change_percent']:+.3f} | {r['order_credit_change']:+.5f} | {r['worst_cross_distance_change_percent']:+.3f} | {r['worst_within_distance_change_percent']:+.3f} |")
    robust=[r['id'] for r in shortlist if r['all_observed_cross_distance_improve']]
    bound_order=[r['id'] for r in shortlist if r['order_credit_improvement_survives_bounds']]
    lines+=['','6. **Robustness:** '+str(len(robust))+' shortlisted maps improve cross distance on every examined training/held-out source and both fingerings; '+str(len(bound_order))+' have primary order-credit improvements whose intervals are separated from the reference. These are distinct conditions, not evidence that one map improves every metric. All source/fingering training scenarios and a separate worst-scenario score use fixed primary anchors. Known held-out sets are exploratory and did not tune the formulas.','',
        '7. **Evidence levels:** algebraically, fixed positive scales/weights/rho make the augmented score strictly respect componentwise dominance; changing a metric and scale by the same unit factor leaves the score unchanged. Exhaustive saved-set comparisons verify three-component winners only within the fully evaluated union and four-component winners only within the declared order screen. No sampled sweep proves a continuous weight region; no Phase 4 certificate transfers. Diminishing returns, relocation mechanisms and broad competitiveness are empirical patterns, not ergonomic validation.','',
        '8. **Next experiment:** complete triple-order evaluation for the remaining archive before asserting archive-wide four-component superiority, then preregister acceptable changes and test a genuinely new independent corpus. To address comfort, run blinded Bangla pair preferences and sustained crossover typing trials with both fingering conventions. More search alone would not validate the formula.','',
        f"Requested exception: {MANDATORY} is included even when J1 ≥1.9; see threshold_exception in shortlist.csv.",
        '', 'Recommendation: use explicit effort budgets plus within-word guardrails as the clearest current decision aid. The augmented achievement family is suitable for transparent sensitivity analysis with frozen aspirations/scales; this experiment does not justify one calibrated formula or a single replacement layout.']
    write_text(target/'FEEDBACK.md','\n'.join(lines)+'\n')
    report=['# Balance study v1: saved-candidate experiment','',
        'Protocol was persisted and hashed before metric evaluation and formula selection. No search ran. A and D are analyzed separately, with same-style references. All published outputs and pre-existing edits are hash-preserved. Standard library only.','',
        '## Methods','',
        'See experiment-config.json for the immutable protocol, metric-definitions.json for scope/units, candidate-provenance.json.gz for complete assignments and every origin, and frozen-scales-3/4.json for realized training-only anchors. The primary three components use the complete union, including candidates dominated on the earlier J1/rate frontier. Within-word distances and cross-space distances retain their distinct denominators and are never added in raw units. Each source is normalized independently before equal averaging. Mix count columns average raw counts only for audit, not pooled-rate reconstruction.','',
        'J1 and effort components are integer sums over the official six-decimal grids, stored as exact fractions. Directed/repeated pairs remain intact. SF different-key distance uses binary64 Euclidean key centers. Distance assertions use absolute tolerance 1e-12; official J1 checks are rational equality. Pair credit uses source-derived binary64 functions; unsupported events retain full denominator 0..1 coverage bounds. Order credit is 0/1 integer counting. Escapes break event chains and remain disclosed in N. Shift effort is included in J1; separate modifier motion is excluded from movement.','',
        'Triple evaluation is staged by the predeclared training-only union: primary three-component top tens, all budget winners across guardrails/scenarios, all earlier retained maps, references and the requested candidate. Complete four-component superiority across the archive is not claimed. A second screen that changed after seeing order would bias comparisons; none was used. Screen IDs are frozen before any order selection.','',
        'Two scaling schemes use fixed per-style primary training component minima: explicit acceptable changes (0.5% J1, 20% cross distance, 5% within distance, 0.02 order deficit) and q90-q10. A constant percentile component uses its positive acceptable-change fallback. Negative deviations are allowed. Order aspirations use the staged collection and the lower deficit endpoint. Optimistic/pessimistic endpoint rankings retain uncertainty; interval certification requires the winner upper score to be below every other lower score. This is conservative and does not assume unknown-event covariance.','',
        'Full primary candidate scores/ranks for every setting are compressed in formula-all-candidates-3/4.csv.gz. formula-sweep.csv records every declared scenario/grid/bound outcome, winner, runner-up, tie count and coverage certification. Candidate metrics plus frozen scales/grid suffice to recreate all scenario scores. Worst-scenario means max across both source-specific and mixed training results under both fingerings; it is not merged with primary ranking.','',
        'Budget eligibility uses exact J1 fractions; distance guardrails use binary64 + 1e-14 absolute tolerance. Marginal gain is relative movement percentage points saved per additional J1 percentage point, between distinct selected points; zero intervals have no slope. Chord knees normalize endpoints for each condition. Slope knees require both adjacent intervals ≥0.03 effort percentage points and a positive slope drop. These methods depend on range, discrete archive gaps and guardrails.','',
        '## Algebraic checks and proof limits','',
        'If y is componentwise no worse than x with at least one strict improvement, every w_k r_k(y) ≤ w_k r_k(x), so the max cannot rise and the positive augmented sum strictly falls. Thus B(y)<B(x). This property also holds for the weighted sum. Translation by fixed aspirations does not alter dominance. Unit changes cancel when x,a,t change together. Constant components have positive fallback scales; zero scales and missing metrics are rejected.','',
        'Legacy e4 regression: reference (J/Jref−1,S/Sref−1)=(0,0) scores zero. At direction 0.5, a trade-off with J=1.001 Jref and S=0.8 Sref scores max(0.0005,−0.1)=0.0005>0; the reference wins. At direction zero it also loses. New aspirations at component minima remove that structural zero-reference barrier, while still exposing chosen priorities.','',
        'Existing Phase 4 proofs cover only their original scope/corpus/objective. Neither augmented-score optimality nor mixed-layout optimality nor a continuous parameter winner region follows from this experiment.','',
        '## Verification and reproducibility','',
        'Reproduce from the repository root into a new directory: `python -m bangla_dh.experimental.balance_study --out work/balance-study-repeat --workers 8` with PYTHONPATH=src. Worker count changes timing only. Run tests with `python -m unittest discover -s tests`, `python -m bangla_dh check-results`, and site `npm run build`. Actual check output is recorded separately in validation.json.','',
        'Deterministic replay checks full-row equality on eight maps. Every rigorous-e4 legacy J1/rate agrees exactly and every legacy distance agrees within 1e-12. All shortlisted candidates are independently checked against official exact training J1 and established action/window/pair/order evaluators on their evaluated sources. Baselines are six fixed registered layouts, not phonetic: their saved held-out canonical rows are separate because no committed baseline training counts exist. Historical best-of-grid baseline numbers are not treated as one scenario.','',
        'Benchmark (single-process, includes four pair scenarios and two mixes per map): '+json.dumps(benchmark)+'. Costs justify staged order diagnostics. Selection remains archive-biased: e4 was designed around J1/rate, pruned its archives and is not representative of every feasible map. No human comfort, speed, statistical confidence or unbiased generalization claim is supported.','',
        '## Findings','',*lines[2:]]
    write_text(target/'REPORT.md','\n'.join(report)+'\n')


def plots(target,frontiers,rows,shortlist,outcomes,refs):
    for ykey,label,name in [('cross_distance','Cross-space SF distance (u/window)','effort-movement'),('within_distance','Within-word SF distance (u/text unit)','within-tradeoffs')]:
        part=[r for r in rows if r['corpus']=='mix' and r['fingering']=='model-optimal']
        xmin=min(r['J1'] for r in part); xmax=max(r['J1'] for r in part); ymin=min(r[ykey] for r in part); ymax=max(r[ykey] for r in part)
        content=['<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="650" viewBox="0 0 1000 650">','<rect width="1000" height="650" fill="white"/>',f'<text x="70" y="35" font-size="22">Training archive: J1 versus {label}</text>', '<path d="M70 60V580H940" fill="none" stroke="black"/>']
        for r in part:
            x=70+870*(r['J1']-xmin)/(xmax-xmin); y=580-500*(r[ykey]-ymin)/(ymax-ymin)
            content.append(f'<circle cx="{x:.3f}" cy="{y:.3f}" r="1.3" fill="{"#1769aa" if r["style"]=="A" else "#d06020"}" opacity="0.25"><title>{r["id"]}: J1={r["J1"]}; movement={r[ykey]}</title></circle>')
        content += [f'<text x="70" y="610">J1 {xmin:.4f} to {xmax:.4f}; A blue, D orange; separate style comparisons</text>',f'<text x="70" y="635">Movement {ymin:.5f} to {ymax:.5f}; modeled values, not measured comfort</text>','</svg>']
        write_text(target/f'{name}.svg','\n'.join(content))
    primary=[o for o in outcomes if o['components']==3 and o['corpus']=='mix' and o['fingering']=='model-optimal']
    counts=Counter(o['winner'] for o in primary)
    content=['<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="700"><rect width="1000" height="700" fill="white"/><text x="30" y="30" font-size="22">Primary 3-component finite-grid wins (not probabilities)</text>']
    for i,(identity,n) in enumerate(counts.most_common(18)):
        y=65+i*32
        content += [f'<text x="30" y="{y+16}">{identity}</text>',f'<rect x="270" y="{y}" width="{n*15}" height="22" fill="#1769aa"/>',f'<text x="{280+n*15}" y="{y+16}">{n}</text>']
    content.append('</svg>'); write_text(target/'parameter-sensitivity.svg','\n'.join(content))


if __name__=='__main__':
    main()
