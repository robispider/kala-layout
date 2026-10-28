"""Build and independently verify the portable two-style challenge bundle."""
from __future__ import annotations

import base64
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
import time

from .paths import PROJECT_ROOT as ROOT, output_path, write_json, write_text, gzip_text_writer, hash_outputs
from .publication import DESCRIPTOR, descriptor, shared_layout, key_layout
from .reference import sha256_file

DATA_VERSION = 'bangla-dh-shared-challenge-v1'
RESULTS = ROOT / 'challenge/shared-v1'
SCRIPT = RESULTS / 'score.py'
TEMPLATE = Path(__file__).with_name('shared_challenge_template.py')


def load_scorer():
    from .challenge import load_scorer as load
    return load(SCRIPT)


def build():
    from .experimental.balance_study import PairEngine, order_values, average
    from .experimental.shared_relaxed import relaxed_evaluate
    from .experimental.inputs import TRAIN, HELDOUT, frequency_path, unit_path, read_json
    from .experimental.mechanics import evaluator, verify_sources
    from .experimental.mechanics_counts import committed_style_triples
    from .experimental.continuous_counts import DEFAULT
    from .phase3 import problem_fixed
    from .search.problem import load_problem

    started = time.perf_counter()
    verify_sources()
    spec = descriptor()
    layout = shared_layout()
    calibration_path = ROOT / spec['calibration']
    calibration = read_json(calibration_path)['styles']
    data = {'version': DATA_VERSION, 'publication_id': spec['version'], 'arrangement_id': spec['arrangement_id'],
            'symbols': list(layout), 'calibration': calibration, 'models': {}, 'counts': {},
            'policy': {'effort_cap_ratio': '403/400', 'within_cap_ratio': 1.075, 'within_absolute_tolerance': 1e-14,
                       'references': 'original same-style arrangements', 'training_weights': dict.fromkeys(TRAIN, 0.5),
                       'ranking': 'joint eligibility then (R_Goti, R_Jhor) Pareto dominance; no combined R',
                       'heldout': 'previously examined diagnostics only', 'status': 'provisional'},
            'reference': {'layout': key_layout(), 'training': {}},
            'attribution': 'Order tables derive from Arno Klein, MIT; see LICENSE-mechanics.txt.'}
    inputs = [DESCRIPTOR, ROOT / spec['source_map'], calibration_path, TEMPLATE,
              ROOT/'data/problem-v1.json', ROOT/'data/evaluators/mechanics-v1/source-lock.json',
              ROOT/'results/evaluator-e2/run-v1/run-manifest.json', DEFAULT/'run-manifest.json']
    independent = {}
    for scenario in ('model-optimal', 'traditional'):
        ev = evaluator(scenario)
        keys = sorted(ev.supported_keys)
        engine = PairEngine('A', TRAIN[0], scenario)
        data['models'][scenario] = {k: getattr(engine, k) for k in
                                   ('actions', 'K', 'M', 'B', 'move', 'dist', 'repeat', 'E', 'D', 'support')}
        data['models'][scenario].update(fixed=problem_fixed(load_problem()), order_keys=keys,
            order_table=base64.b64encode(bytes(int(ev.triple(*t)) for t in itertools.product(keys, repeat=3))).decode('ascii'))
        inputs.append(ROOT / f'results/phase1/effort-grids/ansi-{scenario.replace("model-", "")}.json')
    for style in ('A', 'D'):
        data['counts'][style] = {}
        independent[style] = []
        for corpus in (*TRAIN, *HELDOUT):
            engine = PairEngine(style, corpus, 'model-optimal')
            counts = {k: getattr(engine, k) for k in ('labels', 'u', 'pairs', 'cross', 'pair_total', 'cross_total')}
            counts.update(N=engine.record['N'], escaped=engine.record['escaped_unit_count'],
                          triples=[[a[0], b[0], c[0], n] for (a, b, c), n in committed_style_triples(style, corpus).items()])
            data['counts'][style][corpus] = counts
            row = engine.evaluate(layout)
            row.update(order_values(style, corpus, 'model-optimal', layout))
            if corpus in TRAIN:
                independent[style].append(row)
            inputs.extend((frequency_path(style, corpus), unit_path(corpus),
                           ROOT/f'results/evaluator-e2/run-v1/counts/style-{style.lower()}-{corpus.replace("/", "-")}.json.gz',
                           DEFAULT/f'counts/style-{style.lower()}-{corpus.replace("/", "-")}.json.gz'))
        metrics = average(*independent[style])
        data['reference']['training'][style] = {'metrics': metrics, 'balance': relaxed_evaluate(metrics, calibration[style])}
    # Canonical placement digest deliberately excludes style: one map is submitted once.
    from .shared_challenge_template import layout_hash
    data['reference']['layout_sha256'] = layout_hash(layout)
    raw = json.dumps(data, ensure_ascii=False, separators=(',', ':'), sort_keys=True)
    digest = hashlib.sha256(raw.encode('utf-8')).hexdigest()
    with gzip_text_writer(RESULTS/'scoring-data.json.gz') as stream:
        stream.write(raw)
    written = [RESULTS/'scoring-data.json.gz', write_text(SCRIPT, TEMPLATE.read_text(encoding='utf-8').replace('@@SHA256@@', digest))]
    written.append(write_text(RESULTS/'LICENSE-mechanics.txt', (ROOT/'data/evaluators/mechanics-v1/LICENSE').read_text(encoding='utf-8')))
    example = {'season': DATA_VERSION, 'name': 'B01 shared reference', 'layout': key_layout()}
    written.append(write_json(RESULTS/'reference.json', example))
    scorer = load_scorer()
    loaded, _ = scorer.load_data()
    checked = scorer.evaluate(example, loaded, diagnostics=True)
    checks = {}
    from .challenge import exact_j1
    for style in ('A', 'D'):
        expected = data['reference']['training'][style]
        actual = checked['scores'][style]
        checks[style+' exact training J1'] = Fraction(actual['training']['J1_exact']) == exact_j1(
            style, layout, dict.fromkeys(TRAIN, Fraction(1, 2)), load_problem())
        checks[style+' independent R'] = actual['balance']['R'] == expected['balance']['R']
        checks[style+' independent mechanics'] = all(abs(actual['training'][k]-expected['metrics'][k]) < 1e-12
            for k in actual['training'] if k != 'J1_exact')
        for scenario in data['models']:
            for corpus, row in actual['diagnostics'][scenario].items():
                e = PairEngine(style, corpus, scenario).evaluate(layout)
                e.update(order_values(style, corpus, scenario, layout))
                checks[f'{style} {scenario} {corpus}'] = all(
                    Fraction(row[k]) == Fraction(e[k]) if k == 'J1_exact' else abs(row[k]-e[k]) < 1e-12 for k in row)
    checks['both styles eligible'] = checked['eligible']
    checks['reference is not its own improvement'] = not checked['improves_reference']
    # Builder/source hashes include the actual implementations, not just the template.
    inputs.extend(Path(__file__).parent.rglob('*.py'))
    inputs.extend((ROOT/'data/evaluators/mechanics-v1').rglob('*'))
    inputs = sorted({p for p in inputs if p.is_file()})
    written.append(write_text(RESULTS/'README.md', f'''# Shared arrangement challenge

One map, both Goti (A) and Jhor (D). Season `{DATA_VERSION}`.
Keep `score.py`, `scoring-data.json.gz` and `LICENSE-mechanics.txt` together. Python 3.10+, no dependencies or corpus download.

```bash
python challenge/shared-v1/score.py --reference
python challenge/shared-v1/score.py --template my-shared.json
python challenge/shared-v1/score.py my-shared.json --diagnostics
```

Submit one map to `submissions/shared-v1/`. Both styles must pass the frozen relaxed-policy effort/within limits against the originals. Ranking uses separate R values and Pareto dominance; never their sum. A strictly smaller same-style J1 alone is insufficient. B01 is provisional. Scores model mechanics, not speed or comfort. Known held-out texts are diagnostic only.

The original independent-style J1 challenge remains in the parent directory; it is a different season. Rules: [docs/CHALLENGE.md](../../docs/CHALLENGE.md). Data SHA-256 `{digest}`. The package uses MIT-licensed source-derived mechanics tables; attribution is included.
'''))
    written.append(write_json(RESULTS/'challenge-data.json', {'version': DATA_VERSION,
        'publication_id': data['publication_id'], 'arrangement_id': data['arrangement_id'],
        'data_sha256': digest, 'scorer_sha256': sha256_file(SCRIPT), 'reference': data['reference'], 'policy': data['policy']}))
    written.append(write_json(RESULTS/'run-manifest.json', {'version': DATA_VERSION, 'data_sha256': digest,
        'parameters': data['policy'], 'seeds': [], 'new_search': False,
        'input_sha256': hash_outputs(inputs), 'output_sha256': hash_outputs(written), 'checks': checks,
        'seconds': time.perf_counter()-started, 'bundle_bytes': sum(p.stat().st_size for p in written)}))
    if not all(checks.values()):
        raise ValueError('shared scorer verification failed: ' + str([k for k, v in checks.items() if not v]))
    print(f'Shared scorer: {len(checks)} checks passed; {sum(p.stat().st_size for p in written):,} bytes; {time.perf_counter()-started:.2f}s build')
    return written


def verify(files, diagnostics=False):
    from .experimental.shared_relaxed import RelaxedProblem
    scorer = load_scorer()
    data, _ = scorer.load_data()
    p = RelaxedProblem()
    ok = True
    records = []
    for file in files:
        try:
            raw = scorer.read_submission(file)
            placed = scorer.parse_layout(raw, data)
            actual = scorer.evaluate(raw, data, diagnostics=bool(diagnostics))
            direct = p.evaluate_training(p.perm_of(placed))
            for style in ('A', 'D'):
                if Fraction(actual['scores'][style]['training']['J1_exact']) != Fraction(direct[style]['metrics']['J1_exact']):
                    raise ValueError('independent exact effort disagrees')
                if actual['scores'][style]['balance'] != {k: direct[style]['balance'][k] for k in actual['scores'][style]['balance']}:
                    raise ValueError('independent eligibility/Balance disagrees')
            print(json.dumps({'file': str(file), 'independent_verification': 'PASS', **actual}, ensure_ascii=False))
            records.append({'file': str(file), **actual})
        except (ValueError, TypeError, KeyError, OSError) as error:
            print(f'{file}: invalid: {error}')
            ok = False
    if isinstance(diagnostics, (str, Path)):
        try:
            out = output_path(diagnostics)
            if out.exists():
                raise FileExistsError('choose a new diagnostics directory')
            out.mkdir()
            written = [write_json(out/'diagnostics.json', {'season': DATA_VERSION, 'records': records})]
            written.append(write_text(out/'REPORT.md', '# Shared-arrangement diagnostics\n\n'
                'Both styles, five source scopes and both fingerings are in diagnostics.json. '
                'Only model-optimal training determines joint eligibility and separate R values. '
                'Order bounds retain unsupported mass; held-out scores are exploratory. '
                'No measured speed or comfort claim.\n'))
            write_json(out/'run-manifest.json', {'version': DATA_VERSION,
                'input_sha256': hash_outputs([Path(f) for f in files]), 'output_sha256': hash_outputs(written)})
        except (OSError, ValueError) as error:
            print(f'Optional diagnostics could not be saved: {error}. Independent scoring results are unchanged.')
    return 0 if ok else 1
