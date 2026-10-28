"""Exhaustive, numerically conservative shared-map neighbourhood checks.

No solver or corpus download. The scope is the frozen shared challenge's
binary64 scorer, not a new scalar objective or a global optimality problem.
"""
from __future__ import annotations

import base64
from collections import Counter
from fractions import Fraction
import hashlib
import itertools
import json
import math
from pathlib import Path
import platform
import sys
import time

from .paths import (PROJECT_ROOT as ROOT, output_path, write_json, write_text,
                    gzip_text_writer, hash_outputs, repo_state)
from .publication import DESCRIPTOR, descriptor
from .shared_challenge import SCRIPT, load_scorer
from .reference import sha256_file

VERSION = 'shared-certification-v1'
DEFAULT = ROOT / 'results' / VERSION


def input_digest(path):
    """Python semantics survive CRLF/LF checkout; other inputs are byte-pinned."""
    path = Path(path)
    raw = path.read_bytes()
    if path.suffix == '.py': raw = raw.replace(b'\r\n',b'\n')
    return hashlib.sha256(raw).hexdigest()
TRAIN = ('bnwiki/train', 'newspaper/train')


class Interval:
    """Outward-rounded binary64 interval, matching the public scorer's ops."""
    def __init__(self, lo, hi=None):
        self.lo, self.hi = float(lo), float(lo if hi is None else hi)
        if not (math.isfinite(self.lo) and math.isfinite(self.hi) and self.lo <= self.hi):
            raise ValueError('invalid finite interval')

    @staticmethod
    def wrap(x):
        return x if isinstance(x, Interval) else Interval(x)

    @classmethod
    def rounded(cls, lo, hi):
        return cls(math.nextafter(lo, -math.inf), math.nextafter(hi, math.inf))

    def __add__(self, other):
        other = self.wrap(other)
        return self.rounded(self.lo + other.lo, self.hi + other.hi)

    __radd__ = __add__

    def __sub__(self, other):
        other = self.wrap(other)
        return self.rounded(self.lo - other.hi, self.hi - other.lo)

    def __rsub__(self, other):
        return self.wrap(other) - self

    def __mul__(self, other):
        other = self.wrap(other)
        vals = [a*b for a in (self.lo, self.hi) for b in (other.lo, other.hi)]
        return self.rounded(min(vals), max(vals))

    __rmul__ = __mul__

    def __truediv__(self, other):
        other = self.wrap(other)
        if other.lo <= 0 <= other.hi:
            raise ValueError('interval division through zero')
        vals = [a/b for a in (self.lo, self.hi) for b in (other.lo, other.hi)]
        return self.rounded(min(vals), max(vals))

    @classmethod
    def maximum(cls, rows):
        rows = [cls.wrap(x) for x in rows]
        return cls(max(x.lo for x in rows), max(x.hi for x in rows))

    @classmethod
    def summation(cls, rows):
        # CPython 3.10/3.11 uses sequential summation; newer versions use
        # compensated summation. Enclose the exact endpoint sums plus a
        # conservative absolute error allowance for either implementation.
        rows = [cls.wrap(x) for x in rows]
        lo = sum((Fraction(x.lo) for x in rows),Fraction())
        hi = sum((Fraction(x.hi) for x in rows),Fraction())
        magnitude = sum((max(abs(Fraction(x.lo)),abs(Fraction(x.hi))) for x in rows),Fraction())
        n = 4*len(rows)+16
        allowance = Fraction(n,2**53-n)*magnitude
        return cls.rounded(float(lo-allowance),float(hi+allowance))

    def json(self):
        return [self.lo, self.hi]


def enclosure(value: Fraction, operations: int):
    """Enclose a nonnegative sum/product/divide/mean of stored float terms.

    Each count is exactly representable. With u=2^-53, gamma_n=n*u/(1-n*u)
    bounds relative error in n rounded operations (no under/overflow here).
    Positive summands allow a bound relative to their exact total. An extra
    nextafter on each converted rational endpoint encloses conversion too.
    """
    if value < 0 or not 0 <= operations < 2**52:
        raise ValueError('nonnegative finite-sum bound required')
    gamma = Fraction(operations, 2**53 - operations)
    return Interval.rounded(float(value*(1-gamma)), float(value*(1+gamma)))


def balance_interval(values, calibration):
    scores = []
    for setting in calibration['settings']:
        weights = setting['weights']
        terms = [w*(x-a)/t for x, a, t, w in zip(
            values, calibration['aspirations'], calibration['scales'], weights)]
        b = (Interval.maximum(terms) + setting['rho']*Interval.summation(terms))/sum(weights)
        scores.append(Interval.maximum([0., b-setting['b_minus']]))
    return Interval.maximum(scores)


class PairPolynomial:
    """Integer quadratic polynomial and exact sparse reassignment deltas.

    Directed counts are combined only after checking that the cost table is
    symmetric. The linear delta holds all other labels fixed; corrections for
    each pair of changed labels remove its double-counted old interactions.
    """
    def __init__(self, ids, variable_count, unary, pairs, key_cost, pair_cost, denominator):
        self.ids, self.n, self.denominator = ids, variable_count, denominator
        self.table, self.width = pair_cost, len(key_cost)
        w, table = self.width, pair_cost
        if any(table[i*w+j] != table[j*w+i] for i in range(w) for j in range(w)):
            raise ValueError('asymmetric cost table')
        self.edges = Counter()
        for i, j, count in pairs:
            self.edges[min(i,j), max(i,j)] += count
        neighbours = [[] for _ in ids]
        diag = [0]*len(ids)
        for (i,j), count in self.edges.items():
            if i == j:
                diag[i] += count
            else:
                neighbours[i].append((j,count)); neighbours[j].append((i,count))
        self.base = sum(c*key_cost[ids[i]] for i,c in unary.items()) + sum(
            c*table[ids[i]*w+ids[j]] for (i,j),c in self.edges.items())
        self.delta = []
        for i in range(variable_count):
            old = ids[i]
            self.delta.append([
                unary.get(i,0)*(key_cost[new]-key_cost[old])
                + diag[i]*(table[new*w+new]-table[old*w+old])
                + sum(c*(table[new*w+ids[j]]-table[old*w+ids[j]]) for j,c in neighbours[i])
                for new in ids[:variable_count]])

    def numerator(self, changes):
        """changes: (label index, index of label whose old slot it takes)."""
        value = self.base + sum(self.delta[i][target] for i,target in changes)
        w, t, ids = self.width, self.table, self.ids
        for (i, a), (j, b) in itertools.combinations(changes, 2):
            count = self.edges.get((min(i,j),max(i,j)),0)
            oi, oj, ni, nj = ids[i], ids[j], ids[a], ids[b]
            value += count*(t[ni*w+nj]-t[ni*w+oj]-t[oi*w+nj]+t[oi*w+oj])
        return value

    def value(self, changes=()):
        return Fraction(self.numerator(changes), self.denominator)


def neighbourhood(size, radius=3):
    for i,j in itertools.combinations(range(size),2):
        yield ((i,j),(j,i))
    if radius == 3:
        for i,j,k in itertools.combinations(range(size),3):
            yield ((i,j),(j,k),(k,i))
            yield ((i,k),(j,i),(k,j))


class Checker:
    def __init__(self):
        self.scorer = load_scorer()
        self.data, self.digest = self.scorer.load_data()
        self.model = model = self.data['models']['model-optimal']
        self.symbols = sorted(self.data['symbols'])
        if len(self.symbols) != 52 or len(set(self.symbols)) != 52:
            raise ValueError('this certificate requires the frozen 52-symbol problem')
        if self.data['policy']['effort_cap_ratio'] != '403/400' or self.data['policy']['within_cap_ratio'] != 1.075 or self.data['policy']['within_absolute_tolerance'] != 1e-14:
            raise ValueError('unsupported eligibility policy')
        self.layout = self.scorer.parse_layout(self.submission(), self.data)
        self.actions = [self.layout[s] for s in self.symbols]
        self.reference = self.scorer.evaluate(self.submission(), self.data)
        if not self.reference['eligible']:
            raise ValueError('reference is ineligible')
        if self.reference['R'] != [self.data['reference']['training'][s]['balance']['R'] for s in ('A','D')]:
            raise ValueError('reference score disagrees with frozen calibration bundle')
        action_index = {tuple(a):i for i,a in enumerate(model['actions'])}
        all_labels = set(self.symbols)
        for style in ('A','D'):
            for name in TRAIN:
                all_labels.update(self.data['counts'][style][name]['labels'])
        self.labels = self.symbols + sorted(all_labels-set(self.symbols))
        self.index = {s:i for i,s in enumerate(self.labels)}
        fixed = {s:tuple(a) for s,a in model['fixed'].items()}
        fixed[' '] = ('SPACE','base')
        self.ids = [action_index[self.layout[s] if s in self.layout else fixed[s]] for s in self.labels]
        ratios = [float(d).as_integer_ratio() for d in model['dist']]
        if any(d < 0 for d in model['dist']):
            raise ValueError('distance sums must be nonnegative')
        distance_scale = max(q for p,q in ratios)
        distances = [p*(distance_scale//q) for p,q in ratios]
        if any(abs(n) >= 2**53 for style in ('A','D') for c in self.data['counts'][style].values()
               for row in (*c['pairs'], *c['cross']) for n in row):
            raise ValueError('counts must convert to binary64 exactly')
        self.kernels, self.order, self.caps, self.errors = {}, {}, {}, {}
        for style in ('A','D'):
            counts = [self.data['counts'][style][name] for name in TRAIN]
            self.kernels[style] = {}
            for metric, total, field, costs, unit in [
                ('J1','N','pairs',model['B'],1000000),
                ('W','N','pairs',distances,distance_scale),
                ('C','cross_total','cross',distances,distance_scale)]:
                common = math.lcm(*(2*c[total] for c in counts))
                u, pairs = Counter(), Counter()
                for c in counts:
                    factor = common//(2*c[total])
                    if metric == 'J1':
                        for i,n in c['u']:
                            u[self.index[c['labels'][i]]] += n*factor
                    for i,j,n in c[field]:
                        pairs[self.index[c['labels'][i]],self.index[c['labels'][j]]] += n*factor
                keys = [a+b for a,b in zip(model['K'],model['M'])] if metric=='J1' else [0]*len(model['K'])
                self.kernels[style][metric] = PairPolynomial(self.ids,len(self.symbols),u,
                    [(i,j,n) for (i,j),n in pairs.items()],keys,costs,common*unit)
            # Integer order credit: combine source-normalized triple counts exactly.
            totals = [sum(row[3] for row in c['triples']) for c in counts]
            common = math.lcm(*(2*t for t in totals))
            triples = Counter()
            for c,total in zip(counts,totals):
                for a,b,d,n in c['triples']:
                    triples[self.index[a],self.index[b],self.index[d]] += n*(common//(2*total))
            keys = {k:i for i,k in enumerate(model['order_keys'])}
            physical = [keys.get(model['actions'][i][0],-1) for i in self.ids]
            table, w = base64.b64decode(model['order_table']), len(keys)
            def credit(t):
                i,j,k = (physical[x] for x in t)
                return 0 if min(i,j,k)<0 else table[(i*w+j)*w+k]
            rows = [(t,n,credit(t)) for t,n in sorted(triples.items())]
            adjacent = [set() for _ in self.symbols]
            for ix,(t,n,old) in enumerate(rows):
                for label in set(t):
                    if label < len(adjacent): adjacent[label].add(ix)
            self.order[style] = (rows,adjacent,physical,table,w,common,sum(n*v for t,n,v in rows))
            cal = self.data['calibration'][style]
            self.caps[style] = (Fraction(cal['reference']['J1_exact'])*Fraction(403,400),
                                cal['reference']['within_distance']*1.075+1e-14)
            # m products + m additions + source division + the two-source mean.
            # gamma_(m+6) covers m+1 rounding stages per term, then mean.
            self.errors[style] = {'J1':4, 'W':max(len(c['pairs']) for c in counts)+6,
                                  'C':max(len(c['cross']) for c in counts)+6, 'O':4}

    def submission(self, changes=()):
        if not changes:
            rows = self.data['reference']['layout']
        else:
            layout = dict(self.layout)
            for i,j in changes: layout[self.symbols[i]] = self.actions[j]
            rows = {key:['',''] for key in self.scorer.LETTERS}
            for symbol,(key,layer) in layout.items(): rows[key][layer=='shift'] = symbol
        return {'season':self.scorer.DATA_VERSION, 'name':'Kala Layout certification candidate', 'layout':rows}

    def order_value(self, style, changes=()):
        rows,adjacent,physical,table,w,den,base = self.order[style]
        mapping = list(physical)
        affected = set()
        for i,j in changes:
            mapping[i] = physical[j]; affected.update(adjacent[i])
        total = base
        for ix in sorted(affected):
            t,n,old = rows[ix]
            i,j,k = (mapping[x] for x in t)
            value = 0 if min(i,j,k)<0 else table[(i*w+j)*w+k]
            total += n*(value-old)
        return Fraction(total,den)

    def intervals(self, changes, with_order=True):
        result = {}
        for style in ('A','D'):
            values = {key:enclosure(kernel.value(changes),self.errors[style][key])
                      for key,kernel in self.kernels[style].items()}
            if with_order:
                values['O'] = enclosure(self.order_value(style,changes),self.errors[style]['O'])
                values['R'] = balance_interval([values['J1'],values['C'],values['W'],1-values['O']],
                                               self.data['calibration'][style])
            result[style] = values
        return result

    def check(self, changes):
        row = {'changes':[list(c) for c in changes]}
        # Exact integer/rational filter, no floating-point pruning here.
        for style in ('A','D'):
            effort = self.kernels[style]['J1'].value(changes)
            if effort > self.caps[style][0]:
                return dict(row,status='effort_ineligible',witness_style=style,exact_J1=str(effort))
        intervals = self.intervals(changes,with_order=False)
        for style in ('A','D'):
            if intervals[style]['W'].lo > self.caps[style][1]:
                return dict(row,status='within_ineligible',witness_style=style,
                            within_interval=intervals[style]['W'].json())
        for style in ('A','D'):
            v = intervals[style]
            v['O'] = enclosure(self.order_value(style,changes),self.errors[style]['O'])
            v['R'] = balance_interval([v['J1'],v['C'],v['W'],1-v['O']],self.data['calibration'][style])
        row['intervals'] = {s:{k:v.json() for k,v in values.items()} for s,values in intervals.items()}
        for ix,style in enumerate(('A','D')):
            if intervals[style]['R'].lo > self.reference['R'][ix]:
                return dict(row,status='cannot_dominate',witness_style=style)
        within = all(intervals[s]['W'].hi <= self.caps[s][1] for s in ('A','D'))
        rs = [intervals[s]['R'] for s in ('A','D')]
        dominates = all(r.hi <= ref for r,ref in zip(rs,self.reference['R'])) and any(
            r.hi < ref for r,ref in zip(rs,self.reference['R']))
        # An interval straddling a boundary is explicitly unresolved even if a
        # direct float evaluation happens to classify it on this machine.
        row['observed'] = self.scorer.evaluate(self.submission(changes),self.data)
        return dict(row,status='dominates' if within and dominates else 'unresolved')

    def verify_reference(self):
        result = {}
        intervals = self.intervals(())
        for style in ('A','D'):
            actual = self.reference['scores'][style]
            result[style+' exact effort'] = self.kernels[style]['J1'].value() == Fraction(actual['training']['J1_exact'])
            for key,field in [('J1','J1'),('W','within_distance'),('C','cross_distance'),('O','order_lower')]:
                bound = intervals[style][key]
                result[style+' '+key+' enclosure'] = bound.lo <= actual['training'][field] <= bound.hi
            bound = intervals[style]['R']
            result[style+' R enclosure'] = bound.lo <= actual['balance']['R'] <= bound.hi
        if not all(result.values()): raise ValueError('reference verification failed')
        return result

    def scope(self, radius):
        return {'radius':radius,'symbols':self.symbols,'variable_positions':52,
                'training':dict.fromkeys(TRAIN,0.5),'fingering':'model-optimal',
                'policy':self.data['policy'],'objective':'joint eligibility then separate R Pareto dominance',
                'numerics':'exact effort; conservative binary64 enclosures for movement, order and R; unresolved prevents proof'}


def run(out=DEFAULT, radius=3, log=print):
    if radius not in (2,3): raise ValueError('radius must be 2 or 3')
    out = output_path(Path(out)/'certificate.json').parent
    if any(out.iterdir()): raise ValueError('use an empty output directory; existing certificates are preserved')
    started = time.perf_counter()
    checker = Checker()
    checks = checker.verify_reference()
    log('Reference verified; enumerating all swaps'+(' and three-symbol cycles' if radius==3 else ''),flush=True)
    counts = {2:Counter(),3:Counter()}
    candidates, files, unresolved = [], [], []
    with gzip_text_writer(out/'evaluations.jsonl.gz') as stream:
        for number,changes in enumerate(neighbourhood(len(checker.symbols),radius),1):
            row = checker.check(changes)
            counts[len(changes)][row['status']] += 1
            stream.write(json.dumps(row,ensure_ascii=False,separators=(',',':'))+'\n')
            if row['status'] in ('dominates','unresolved'):
                name = f'candidate-{number:05d}.json'
                files.append(write_json(out/name,checker.submission(changes)))
                (candidates if row['status']=='dominates' else unresolved).append(name)
            if number%2000==0: log(f'{number:,} checked; {time.perf_counter()-started:.1f}s',flush=True)
    expected = math.comb(len(checker.symbols),2) + (2*math.comb(len(checker.symbols),3) if radius==3 else 0)
    actual = sum(sum(c.values()) for c in counts.values())
    if actual != expected: raise ValueError('incomplete enumeration')
    checks['enumeration count'] = True
    certificate = {'version':VERSION,'arrangement_id':descriptor()['arrangement_id'],
        'map_sha256':checker.reference['layout_sha256'],'challenge_data_sha256':checker.digest,
        'scope':checker.scope(radius),
        'reference':checker.reference,'reference_checks':checks,
        'expected_alternatives':expected,'checked_alternatives':actual,
        'counts':{str(k):dict(sorted(v.items())) for k,v in counts.items() if v},
        'dominating_candidates':candidates,'unresolved_candidates':unresolved,
        'classification':'counterexample found' if candidates else 'inconclusive' if unresolved else 'certified neighbourhood non-dominance',
        'global_optimality':False,'seconds':time.perf_counter()-started}
    files.extend([out/'evaluations.jsonl.gz',write_json(out/'certificate.json',certificate)])
    files.append(write_text(out/'REPORT.md',report(certificate,out)))
    commit,clean = repo_state()
    sources = [DESCRIPTOR,SCRIPT,SCRIPT.with_name('scoring-data.json.gz'),ROOT/descriptor()['source_map'],
               ROOT/descriptor()['calibration'],ROOT/'tests/test_shared_certification.py']
    sources.extend(sorted((ROOT/'src/bangla_dh').rglob('*.py')))
    manifest = {'version':VERSION,'git_commit':commit,'git_clean':clean,'python':sys.version,
                'parameters':certificate['scope'],'seeds':[],'method':'complete deterministic enumeration',
                'input_hash_normalization':'Python source CRLF normalized to LF; all other inputs hashed byte-for-byte',
                'platform':platform.platform(),'command':f'python -m bangla_dh certify-shared --radius {radius} --out {out.relative_to(ROOT).as_posix()}',
                'input_sha256':{p.relative_to(ROOT).as_posix():input_digest(p) for p in sorted(sources)},
                'output_sha256':hash_outputs(files)}
    write_json(out/'run-manifest.json',manifest)
    log(certificate['classification'],flush=True)
    return certificate


def report(c, out):
    lines = ['# Kala Layout: shared neighbourhood certificate','',
        f"Research identifier B01; `{c['arrangement_id']}`. Result: **{c['classification']}**.",'',
        f"All {c['checked_alternatives']:,} alternatives moving two through {c['scope']['radius']} symbols were checked. "
        'Every symbol may move across base/Shift layers; all other positions stay fixed. Both styles always share the same map.','',
        '| Symbols moved | Exact effort failures | Within-distance failures | Cannot dominate | Dominators | Unresolved |',
        '| --- | --- | --- | --- | --- | --- |']
    for radius,counts in c['counts'].items():
        lines.append('| '+str(radius)+' | '+' | '.join(str(counts.get(k,0)) for k in (
            'effort_ineligible','within_ineligible','cannot_dominate','dominates','unresolved'))+' |')
    lines += ['', '## Exact scope','',
        'Frozen shared challenge season, 52 searched symbols, model-optimal ANSI fingering, equal Wikipedia/newspaper training weights, '
        'original same-style effort cap +0.75%, within-word distance cap +7.5% (including the existing 1e-14 tolerance), and frozen style-specific Balance calibration. '
        'A dominator must be eligible in both styles, no worse in either R, and strictly better in at least one. R values are never added.','',
        f"Reference R: Goti {c['reference']['R'][0]:.15f}; Jhor {c['reference']['R'][1]:.15f}.",'',
        '## Numerical safeguards','',
        'Effort uses exact integers and rational source normalization. Stored binary64 distance coefficients are lifted to exact integers with a common power-of-two denominator. '
        'Order credit uses exact integer triple counts. These exact totals are centres of conservative intervals enclosing the public scorer: '
        'nonnegative movement sums use gamma_(m+6), u=2^-53, where m is the maximum source pair count; source ratios and equal means use gamma_4. '
        'Balance arithmetic is enclosed outward with nextafter; term sums additionally allow gamma_(4n+16) times their absolute magnitudes for sequential or compensated summation. '
        'Counts must convert exactly to binary64; the pinned tables have no underflow/overflow. '
        'Only an exact effort failure, a lower within bound above its cap, or a lower R bound above the reference can exclude a candidate. '
        'Any undecided boundary is saved as unresolved and prevents certification. No scoring tolerance or calibration is changed.','',
        '## Reproduce and inspect','',
        'Use an empty destination; existing runs are never overwritten. No corpus text or extra dependency is needed.','',
        '```powershell', '$env:PYTHONPATH = "src"',
        f"python -m bangla_dh certify-shared --radius {c['scope']['radius']} --out work/shared-certificate-repeat",
        'python -m bangla_dh verify-shared-certificate '+out.relative_to(ROOT).as_posix(), '```','',
        '[Certificate](certificate.json), [all candidate decisions](evaluations.jsonl.gz), [input/output hashes](run-manifest.json). '
        'The verifier checks hashes, replays the conservative checker and independently recomputes every exclusion witness from the raw source counts or direct portable scorer. '
        'Python-source hashes normalize CRLF to LF so Windows/Linux checkouts agree; all other input/output hashes are byte-exact. '
        'Small exhaustive tests check the delta mathematics independently. This is executable computational evidence, not a standalone solver proof.','',
        '## Limits','',
        'This does not prove global Pareto optimality, minimum per-style effort, a global optimality gap, or superiority to another non-dominated trade-off such as B02. '
        'It says nothing about measured speed, comfort or learning. Original Phase 4 certificates remain separate and unchanged. '
        'The selected map, public scores, challenge season and installed Kala application are unchanged.']
    if c['dominating_candidates'] or c['unresolved_candidates']:
        lines += ['', '## Candidates needing review','']
        for name in c['dominating_candidates']+c['unresolved_candidates']: lines.append(f'- [{name}]({name})')
    return '\n'.join(lines)+'\n'


class DirectWitness:
    """Separate full-sum verification, without polynomial deltas or intervals."""
    def __init__(self, checker):
        self.checker = checker
        model = checker.data['models']['model-optimal']
        self.actions = {tuple(a):i for i,a in enumerate(model['actions'])}
        self.fixed = {s:tuple(a) for s,a in model['fixed'].items()}
        self.fixed[' '] = ('SPACE','base')
        self.model = model

    def effort(self, submission, style):
        layout = self.checker.scorer.parse_layout(submission,self.checker.data)
        mapping = {**layout,**self.fixed}
        model, values = self.model, []
        width = len(model['actions'])
        for name in TRAIN:
            c = self.checker.data['counts'][style][name]
            ids = [self.actions[mapping[s]] for s in c['labels']]
            numerator = sum(n*model['K'][ids[i]] for i,n in c['u'])
            numerator += sum(n*model['M'][ids[i]] for i,n in c['u'])
            numerator += sum(n*model['B'][ids[i]*width+ids[j]] for i,j,n in c['pairs'])
            values.append(Fraction(numerator,c['N']*1000000))
        return sum(values)/2

    def check(self, row, changes):
        c = self.checker
        submission = c.submission(changes)
        status, style = row['status'], row.get('witness_style')
        if status == 'effort_ineligible':
            exact = self.effort(submission,style)
            if exact != Fraction(row['exact_J1']) or exact <= c.caps[style][0]:
                raise ValueError('independent effort witness failed')
        else:
            actual = c.scorer.evaluate(submission,c.data)
            if status == 'within_ineligible':
                v = actual['scores'][style]['training']['within_distance']
                lo,hi = row['within_interval']
                if not lo <= v <= hi or v <= c.caps[style][1]:
                    raise ValueError('independent within witness failed')
            elif status == 'cannot_dominate':
                if actual['improves_reference']:
                    raise ValueError('direct scorer found a dominator')
                for s in ('A','D'):
                    for key,field in [('J1','J1'),('W','within_distance'),('C','cross_distance'),('O','order_lower')]:
                        lo,hi = row['intervals'][s][key]
                        if not lo <= actual['scores'][s]['training'][field] <= hi:
                            raise ValueError('direct metric outside enclosure')
                    r = actual['scores'][s]['balance']['R']
                    if r is not None:
                        lo,hi = row['intervals'][s]['R']
                        if not lo <= r <= hi: raise ValueError('direct R outside enclosure')
            elif actual != row['observed']:
                raise ValueError('direct candidate evaluation differs')
            if status == 'dominates' and not actual['improves_reference']:
                raise ValueError('direct scorer rejects claimed dominator')


def verify(folder=DEFAULT, log=print):
    """Read-only full replay, including exact decision records and enumeration."""
    import gzip
    folder = Path(folder)
    manifest = json.loads((folder/'run-manifest.json').read_text(encoding='utf-8'))
    if manifest.get('input_hash_normalization') != 'Python source CRLF normalized to LF; all other inputs hashed byte-for-byte':
        raise ValueError('unsupported input hash normalization')
    for key in ('input_sha256','output_sha256'):
        for name,digest in manifest[key].items():
            actual = input_digest(ROOT/name) if key=='input_sha256' else sha256_file(ROOT/name)
            if actual != digest: raise ValueError('hash mismatch: '+name)
    saved = json.loads((folder/'certificate.json').read_text(encoding='utf-8'))
    checker = Checker()
    direct = DirectWitness(checker)
    if checker.digest != saved['challenge_data_sha256'] or checker.reference != saved['reference']:
        raise ValueError('reference changed')
    if checker.verify_reference() != {k:v for k,v in saved['reference_checks'].items() if k!='enumeration count'}:
        raise ValueError('reference checks differ')
    if saved['version'] != VERSION or saved['scope']['radius'] not in (2,3) or saved['scope']['symbols'] != checker.symbols:
        raise ValueError('unsupported certificate scope')
    if saved['scope'] != checker.scope(saved['scope']['radius']):
        raise ValueError('scope disagrees with frozen challenge')
    if saved['map_sha256'] != checker.reference['layout_sha256'] or saved['arrangement_id'] != descriptor()['arrangement_id']:
        raise ValueError('wrong arrangement')
    count, statuses = 0, {2:Counter(),3:Counter()}
    candidates, unresolved = [], []
    with gzip.open(folder/'evaluations.jsonl.gz','rt',encoding='utf-8') as stream:
        for changes in neighbourhood(len(checker.symbols),saved['scope']['radius']):
            line = stream.readline()
            if not line or json.loads(line) != checker.check(changes):
                raise ValueError(f'decision mismatch at {count+1}')
            row = json.loads(line)
            direct.check(row,changes)
            statuses[len(changes)][row['status']] += 1
            count += 1
            if row['status'] in ('dominates','unresolved'):
                name = f'candidate-{count:05d}.json'
                if json.loads((folder/name).read_text(encoding='utf-8')) != checker.submission(changes):
                    raise ValueError('candidate map disagrees')
                (candidates if row['status']=='dominates' else unresolved).append(name)
            if count%4000==0: log(f'{count:,} replayed',flush=True)
        if stream.read(): raise ValueError('extra decisions')
    expected = math.comb(52,2)+(2*math.comb(52,3) if saved['scope']['radius']==3 else 0)
    if count != expected or count != saved['checked_alternatives'] or count != saved['expected_alternatives']:
        raise ValueError('wrong scope count')
    if {str(k):dict(sorted(v.items())) for k,v in statuses.items() if v} != saved['counts']:
        raise ValueError('summary counts differ')
    classification = 'counterexample found' if candidates else 'inconclusive' if unresolved else 'certified neighbourhood non-dominance'
    if saved['classification'] != classification or saved['dominating_candidates'] != candidates or saved['unresolved_candidates'] != unresolved or saved['global_optimality'] is not False:
        raise ValueError('summary claim disagrees with replay')
    log(f'PASS: hashes, all {count:,} decisions replayed and independently checked',flush=True)
    return True
