"""One physical assignment, two unchanged vowel encoders; experimental only."""
from __future__ import annotations

from fractions import Fraction
import math

from ..mix import mixed_frequencies
from ..paths import PROJECT_ROOT
from ..phase3 import problem_fixed
from ..scoring.model import ANSI_GRID, KeyModel
from ..search.anneal import Instance, State
from ..search.integer import IntegerInstance
from ..search.problem import load_problem, slots
from .balance_study import PairEngine, average, order_values
from .balance_v1 import evaluate
from .continuous import CENTERS
from .continuous_counts import DEFAULT, load_verified
from .inputs import TRAIN, frequency_path, read_json, validate_layout
from .joint_problem import endpoint_counts

CONFIG = PROJECT_ROOT / 'results/balance-v1/balance-v1-config.json'
START_IDS = ('A-18fe73cb912ae3f1', 'D-e4a6be48881da590',
             'A-a280bdc4ca72c6c7', 'D-9ad5412603069cd6')


class DistanceModel:
    """Separate SF different-key distance, with zero modifier/base cost."""
    def __init__(self, model):
        self.model = model

    def effort(self, key):
        return 0.0

    def penalty_keys(self, a, b, same_action):
        different = a != b and 'SPACE' not in (a, b)
        same_finger = different and self.model.keys[a].finger == self.model.keys[b].finger
        return 'SF-distance', math.dist(CENTERS[a], CENTERS[b]) if same_finger else 0.0


def search_energy(values, references, arm, direction=0.5):
    """Explicit exploration objectives; never called Balance v1 R.

    values/references: E_A,E_D,W_A,W_D,X_A,X_D. Balance restoration uses
    max positive cap overrun, scaled in units of the original allowances.
    A small declared secondary term guides movement exploration. Only exact
    post-scoring decides eligibility; search floating point is not authority.
    """
    r = [x / ref for x, ref in zip(values, references)]
    if arm == 'effort':
        return max(r[0], r[1]) - 1.0
    if arm != 'balance' or not 0 <= direction <= 1:
        raise ValueError('invalid shared search arm/direction')
    over = [max(0., (r[k]-1)/(.005 if k < 2 else .05)-1) for k in range(4)]
    secondary = (1-direction)*(r[4]+r[5])/2 + direction*(r[2]+r[3])/2
    secondary += .05*(r[0]+r[1])/2
    return max(over) + .001*sum(over) + .0001*secondary


class SharedProblem:
    def __init__(self):
        self.config = read_json(CONFIG)
        problem = load_problem()
        self.labels = problem['styles']['A']['searched_symbols']
        if set(self.labels) != set(problem['styles']['D']['searched_symbols']):
            raise ValueError('shared search requires identical A/D symbols')
        self.slots, self.fixed = slots(), problem_fixed(problem)
        self.n = len(self.labels)
        self.model = KeyModel.from_grid(ANSI_GRID)
        distance = DistanceModel(self.model)
        self.instances, self.integers = {}, {}
        self.starts = []
        for identity in START_IDS:
            path = PROJECT_ROOT / 'results/balance-v1/layouts' / (identity + '.json')
            layout = {s: tuple(slot.split('/')) for s, slot in read_json(path)['layout'].items()}
            self.starts.append(self.perm_of(layout))
        for style in ('A', 'D'):
            u, v = mixed_frequencies(style, dict.fromkeys(TRAIN, .5))
            self.instances['E'+style] = Instance(self.labels, self.slots, self.fixed, u, v, self.model, 'J1')
            self.instances['W'+style] = Instance(self.labels, self.slots, self.fixed, {}, v, distance, 'J0')
            movement = {}
            for corpus in TRAIN:
                cache, _ = load_verified(DEFAULT, 'style', style, corpus)
                counts = endpoint_counts(cache)
                total = sum(counts.values())
                for pair, count in counts.items():
                    movement[pair] = movement.get(pair, 0.) + .5*count/total
                self.integers[style,corpus] = IntegerInstance(self.labels, self.slots, self.fixed,
                                                           read_json(frequency_path(style, corpus)), self.model)
            self.instances['X'+style] = Instance(self.labels, self.slots, self.fixed, {}, movement, distance, 'J0')
        self.keys = ('EA','ED','WA','WD','XA','XD')
        self.references = [self.config['styles'][s]['reference'][metric]
                           for metric in ('J1','within_distance','cross_distance') for s in ('A','D')]
        self.engines = {}

    def perm_of(self, layout):
        index = {slot:i for i,slot in enumerate(self.slots)}
        return [index[layout[s]] for s in self.labels]

    def assignment(self, perm):
        if sorted(perm) != list(range(self.n)):
            raise ValueError('shared assignment must be a bijection')
        layout = dict(zip(self.labels, (self.slots[i] for i in perm)))
        for style in ('A','D'):
            validate_layout(style, layout)
        return layout

    def values(self, perm):
        self.assignment(perm)
        return [self.instances[k].score(perm) for k in self.keys]

    def exact_effort(self, perm, style):
        return sum((self.integers[style,c].to_j(self.integers[style,c].score(perm))/2
                    for c in TRAIN), Fraction())

    def eligible_fast(self, values):
        return all(values[k] <= self.references[k]*(1.005 if k<2 else 1.05)+1e-12 for k in range(4))

    def evaluate_training(self, perm, with_order=True):
        layout = self.assignment(perm)
        scores = {}
        for style in ('A','D'):
            rows = []
            for corpus in TRAIN:
                key = (style,corpus)
                if key not in self.engines:
                    self.engines[key] = PairEngine(style,corpus,'model-optimal')
                r = self.engines[key].evaluate(layout)
                if with_order:
                    r.update(order_values(style,corpus,'model-optimal',layout))
                rows.append(r)
            mix = average(*rows)
            if Fraction(mix['J1_exact']) != self.exact_effort(perm,style):
                raise ValueError('independent integer effort disagrees')
            balance = evaluate(mix,self.config['styles'][style]) if with_order else None
            scores[style] = {'metrics':mix,'balance':balance}
        fast = self.values(perm)
        for k,(metric,s) in enumerate((('J1','A'),('J1','D'),('within_distance','A'),
                                      ('within_distance','D'),('cross_distance','A'),('cross_distance','D'))):
            if abs(fast[k]-scores[s]['metrics'][metric]) > 1e-10:
                raise ValueError('cached quadratic metric differs from independent scorer')
        return scores


class SharedState:
    def __init__(self, problem, perm, arm, direction=.5):
        self.problem, self.arm, self.direction = problem, arm, direction
        keys = problem.keys[:2] if arm == 'effort' else problem.keys
        self.states = [State(problem.instances[k],perm) for k in keys]

    @property
    def perm(self):
        return self.states[0].perm

    @property
    def energy(self):
        return search_energy([s.score for s in self.states],self.problem.references,self.arm,self.direction)

    def delta(self,i,j):
        changes = [s.delta(i,j) for s in self.states]
        energy = search_energy([s.score+d for s,d in zip(self.states,changes)],
                               self.problem.references,self.arm,self.direction)
        return energy-self.energy, changes

    def swap(self,i,j,changes):
        for state,delta in zip(self.states,changes):
            state.swap(i,j,delta)

    def reset(self,perm):
        for state in self.states:
            state.perm = list(perm)
            state.rebuild()


def dominates(a,b):
    return all(x<=y for x,y in zip(a,b)) and any(x<y for x,y in zip(a,b))


def pareto_offer(rows, row, limit):
    """Bounded R_A/R_D archive; no sum or cross-style score comparison."""
    if any(r['perm']==row['perm'] or dominates(r['R'],row['R']) for r in rows):
        return
    rows[:] = [r for r in rows if not dominates(row['R'],r['R'])] + [row]
    rows.sort(key=lambda r:(r['R'][0],r['R'][1],r['perm']))
    if len(rows)>limit:
        last = len(rows)-1
        rows[:] = [rows[round(k*last/(limit-1))] for k in range(limit)]
