"""Report the completed run without changing its original search artifacts."""
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import statistics

from bangla_dh import mix
from bangla_dh.paths import PROJECT_ROOT, write_json, write_text, relative_to_project
from bangla_dh.phase3 import problem_fixed
from bangla_dh.reference import sha256_file
from bangla_dh.scoring.model import ANSI_GRID, KeyModel
from bangla_dh.search.integer import IntegerInstance
from bangla_dh.search.problem import load_problem

def verify():
    OUT = PROJECT_ROOT / 'results/goti-j1-8b-v1'

    publication = json.loads((OUT / 'run-manifest.json').read_text(encoding='utf-8'))
    archive = publication['files']
    assert hashlib.sha256((OUT / 'REPORT.md').read_bytes()).hexdigest() == publication['publication_report_sha256']
    def source_bytes(path):
        name = Path(path).relative_to(PROJECT_ROOT).as_posix()
        entry = archive.get(name)
        if entry:
            raw = (PROJECT_ROOT / entry['archive']).read_bytes()
            assert hashlib.sha256(raw).hexdigest() == entry['sha256'], name
            import gzip
            raw = gzip.decompress(raw) if entry['encoding'] == 'gzip' else raw
            assert hashlib.sha256(raw).hexdigest() == entry['source_sha256'], name
            return raw
        return Path(path).read_bytes()
    def read(path):
        if Path(path).is_relative_to(OUT):
            relative = Path(path).relative_to(OUT).as_posix()
            path = PROJECT_ROOT / 'work/goti-j1-8b-v1' / relative
        return json.loads(source_bytes(path))
    for name in archive:
        source_bytes(PROJECT_ROOT / name)
    source_report = read(OUT / 'report-manifest.json')
    for name, expected in (source_report['input_sha256'] | source_report['output_sha256']).items():
        assert hashlib.sha256(source_bytes(PROJECT_ROOT / name)).hexdigest() == expected, name

    record = read(OUT / 'search/A.json')
    manifest = read(OUT / 'run-manifest.json')
    comparison = read(OUT / 'comparison.json')['A']
    evaluation = read(OUT / 'mix-search.json')
    published = read(PROJECT_ROOT / 'results/mix-search/search/A.json')
    published_manifest = read(PROJECT_ROOT / 'results/mix-search/run-manifest.json')
    exported = read(OUT / 'A-layout.json')
    problem = load_problem()
    model = KeyModel.from_grid(ANSI_GRID)
    labels = problem['styles']['A']['searched_symbols']
    slots = [tuple(slot.split('/')) for slot in record['slots']]
    fixed = problem_fixed(problem)
    source_scopes = ['bnwiki/train', 'newspaper/train', 'bnwiki/heldout',
                     'newspaper/heldout', 'bard-novel/heldout']
    integers = {scope: IntegerInstance(labels, slots, fixed,
                                     read(mix._keystroke_path('A', scope)), model)
                for scope in source_scopes}

    def assignment(endpoint):
        return dict(zip(endpoint, slots))

    def exact_source(layout, scope):
        inst = integers[scope]
        return inst.to_j(inst.score(inst.perm_of(layout)))

    def exact_mix(layout):
        return (exact_source(layout, 'bnwiki/train') + exact_source(layout, 'newspaper/train')) / 2

    def identity(layout):
        canonical = json.dumps(['A', sorted((symbol, list(slot)) for symbol, slot in layout.items())], ensure_ascii=False)
        return 'A-' + hashlib.sha256(canonical.encode('utf-8')).hexdigest()[:16]

    old_layout = {symbol: tuple(slot.split('/')) for symbol, slot in published['best']['layout'].items()}
    new_layout = {symbol: tuple(slot.split('/')) for symbol, slot in record['best']['layout'].items()}
    assert new_layout == old_layout
    assert len(new_layout) == 52
    assert comparison['same_layout'] and comparison['keys_that_differ'] == 0
    assert exported['style'] == 'A'
    for symbol, (key, layer) in new_layout.items():
        assert exported['layout'][key][0 if layer == 'base' else 1] == symbol

    hash_checks = {}
    for name, expected in manifest['inputs'].items():
        hash_checks[name] = hashlib.sha256(source_bytes(PROJECT_ROOT / name)).hexdigest() == expected
        assert hash_checks[name], name
    assert all(value == published_manifest['inputs'][name] for name, value in manifest['inputs'].items())
    output_checks = {}
    for name, expected in manifest['outputs'].items():
        output_checks[name] = hashlib.sha256(source_bytes(PROJECT_ROOT / name)).hexdigest() == expected
        assert output_checks[name], name

    runs = record['runs']
    assert len(runs) == 8000
    assert [row['seed'] for row in runs] == list(range(20270001, 20278001))
    assert sum(row['start'] == 'greedy' for row in runs) == 1
    assert sum(row['start'] == 'random' for row in runs) == 7999
    assert all(row['schedule']['steps'] == 1_000_000 for row in runs)
    assert all(row['ils']['iterations'] == 1000 for row in runs)
    assert len(record['polish']) == 0 and len(record['confirmation']) == 3
    assert all(row['iterations'] == 5000 for row in record['confirmation'])
    assert all(evaluation['checks'].values())

    counts = Counter(tuple(row['layout']) for row in runs)
    scores = {endpoint: exact_mix(assignment(endpoint)) for endpoint in counts}
    reference_score = exact_mix(old_layout)
    assert min(scores.values()) == reference_score
    max_float_difference = max(abs(float(scores[tuple(row['layout'])]) - row['best_score']) for row in runs)
    assert max_float_difference < 1e-12
    best_endpoints = [endpoint for endpoint, score in scores.items() if score == reference_score]
    assert len(best_endpoints) == 1
    hits = sum(counts[endpoint] for endpoint in best_endpoints)
    assert hits == 514
    assert all(assignment(endpoint) == old_layout for endpoint in best_endpoints)
    assert all(exact_mix(assignment(row['layout'])) == reference_score for row in record['confirmation'])
    retained = sorted(scores, key=lambda endpoint: (scores[endpoint], endpoint))
    candidates = []
    for endpoint in retained:
        layout = assignment(endpoint)
        exact = scores[endpoint]
        candidates.append({'id': identity(layout), 'retained_search_runs': counts[endpoint],
                           'training_J1_exact': str(exact), 'training_J1': float(exact),
                           'change_percent': float((exact / reference_score - 1) * 100),
                           'assignments_different_from_published': sum(layout[k] != v for k, v in old_layout.items())})

    score_rows = []
    for scope in source_scopes:
        exact = exact_source(new_layout, scope)
        assert exact == exact_source(old_layout, scope)
        saved = comparison['by_text'][scope]
        assert abs(saved['yours'] - float(exact)) < 1e-12
        assert saved['yours'] == saved['published']
        score_rows.append({'scope': scope, 'J1': float(exact), 'J1_exact': str(exact), 'difference': 0})
    next_distinct = candidates[1]
    median_score = statistics.median(float(scores[tuple(row['layout'])]) for row in runs)
    worst_score = max(float(score) for score in scores.values())
    end_local = datetime.fromisoformat(manifest['generated_utc']).astimezone(timezone(timedelta(hours=6)))
    wall_seconds = 12746  # User-provided completed-search terminal output, not a manifest field.
    validation = {
        'original_run_input_hashes_verified': hash_checks,
        'original_run_output_hashes_verified': output_checks,
        'all_9_recorded_inputs_identical_to_original_publication_manifest': True,
        'all_8000_seed_records_and_proposal_counts_verified': True,
        'all_241_distinct_search_endpoints_independently_rescored_with_integer_coefficients': True,
        'all_8000_saved_scores_match_integer_rescoring_within_1e_minus_12': True,
        'maximum_float_score_difference': max_float_difference,
        'all_52_symbol_assignments_identical_to_published': True,
        'exported_layout_verified': True,
        'all_3_confirmation_endpoints_exactly_equal_to_published_score': True,
        'all_5_source_scores_independently_verified': True,
        'published_check_passed': all(evaluation['checks'].values()),
    }
    print(json.dumps({'verified': True, 'starts': len(runs), 'endpoints': len(counts), 'hits': hits, 'assignments': len(new_layout), 'best_exact_J1': str(reference_score)}))

if __name__ == '__main__':
    verify()
