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

OUT = PROJECT_ROOT / 'work/goti-j1-8b-v1'

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))

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
    hash_checks[name] = sha256_file(PROJECT_ROOT / name) == expected
    assert hash_checks[name], name
assert all(value == published_manifest['inputs'][name] for name, value in manifest['inputs'].items())
output_checks = {}
for name, expected in manifest['outputs'].items():
    output_checks[name] = sha256_file(PROJECT_ROOT / name) == expected
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
summary = {
    'title': 'Kala Goti: eight-billion-proposal J1 search',
    'style': 'A', 'objective': '0.5 bnwiki/train J1 + 0.5 newspaper/train J1',
    'classification': 'best found; exact reproduction of the original separate Goti arrangement',
    'reference_id': identity(old_layout), 'same_layout': True,
    'proposal_count': sum(row['schedule']['steps'] for row in runs),
    'starts': len(runs), 'greedy_starts': 1, 'random_starts': 7999,
    'seed_range': [20270001, 20278000], 'workers': 28,
    'worker_count_source': 'User-provided executed command; original run manifest does not record workers',
    'elapsed_wall_seconds': wall_seconds,
    'elapsed_source': 'User-provided completed-search terminal output',
    'run_manifest_generated_time_dhaka': end_local.isoformat(),
    'best_score': float(reference_score), 'best_score_exact': str(reference_score),
    'best_hits': hits, 'best_hit_percent': hits / len(runs) * 100,
    'distinct_best_retained_layouts': len(best_endpoints),
    'distinct_retained_search_endpoints': len(counts), 'unique_visited_layouts': None,
    'median_final_J1': median_score, 'worst_final_J1': worst_score,
    'nearest_distinct_endpoint': next_distinct,
    'retained_candidate_summary': candidates, 'source_scores': score_rows,
    'certification': 'No new optimality certificate or global bound produced by this run',
    'validation': validation,
}

lines = [
    '# Kala Goti: eight-billion-proposal J1 search report', '',
    '**Result: the search rediscovered the exact original published Kala Goti arrangement. No lower-J1 layout was found.** All 52 symbol positions are identical to the original separate Goti map, `A-18fe73cb912ae3f1`; this is not the shared B01 arrangement.', '',
    f'Run-manifest completion time: **{end_local:%d %B %Y, %H:%M:%S} Asia/Dhaka**. Classification: **best found**, strengthened by reproduction from fresh seeds. This run produces no new optimality certificate.', '',
    '## Search scope and budget', '',
    '| Item | Recorded configuration |', '| --- | --- |',
    '| Style | Goti / A only; original UniJoy-style hasant-plus-sign vowel grammar |',
    '| Objective | J_mix = 0.5 J1(Wikipedia training) + 0.5 J1(newspaper training) |',
    '| Model | Frozen J1 key + pair + Shift effort; model-optimal ANSI fingering; middle-index benefit retained |',
    '| Search space | Same 52 symbols on the original 52 base/Shift positions; fixed digits and punctuation |',
    '| Seed range | 20270001–20278000; disjoint from the original mixed-search range |',
    '| Starts | 8,000: one greedy start and 7,999 random starts |',
    '| Annealing proposals | 1,000,000 per start; **8,000,000,000 total** |',
    '| Local search | Steepest descent and 1,000 ILS iterations per start; perturbation strengths 2–6 |',
    '| Confirmation | Three 5,000-iteration ILS runs from the best result, strengths 2–6, 4–10 and 8–16 |',
    '| Earlier-layout polish | None; the terminal reported 0 polish runs |',
    '| Parallel workers | 28, from the executed command |',
    '| Elapsed search time | 12,746 s = **3 h 32 min 26 s**, from completed-search terminal output |',
    '| Run revision | `' + manifest['repo_commit'] + '`; run manifest records a clean working tree |', '',
    'The 8 billion count covers annealing proposals only. Local descent, ILS and confirmation add further work. Revisited proposals are possible; the total number of unique visited arrangements was not recorded. Timing is not a controlled performance benchmark: a process-level Windows performance preference was applied during this run.', '',
    '## Dataset', '',
    '| Training source | Documents | Word tokens | Objective weight |',
    '| --- | ---: | ---: | ---: |',
    '| Bangla Wikipedia | 171,685 | 58,136,180 | 50% |',
    '| Bangla newspaper | 386,205 | 110,175,696 | 50% |',
    '| Total | **557,890** | **168,311,876** | **100%** |', '',
    'The run reused the original frozen style-A frequency tables. Each source is normalized separately before the equal-weight mean; this is not pooling counts by corpus size. All nine inputs listed in this run manifest have identical hashes to the corresponding original publication inputs. Held-out Wikipedia, newspaper and non-overlapping BARD news were scored after selection. They are previously examined benchmarks, so this repeat provides no fresh independent text validation. The historical key `bard-novel` denotes BARD news, not literary novels.', '',
    '## Findings', '',
    '| Measurement | Verified result |', '| --- | ---: |',
    f'| Best training J1 | **{float(reference_score):.16f}** |',
    f'| Exact frozen-grid mixed score | `{reference_score}` |',
    '| Change from original published Goti | **0** |',
    f'| Search starts reaching that exact arrangement | **{hits:,} / {len(runs):,} = {hits / len(runs) * 100:.3f}%** |',
    '| Successful start types | All 514 successes came from random starts; the greedy start did not reach the best |',
    f'| Distinct layouts tied at the lowest exact score among retained endpoints | **{len(best_endpoints)}** |',
    f'| Distinct retained final search layouts | **{len(counts)}** |',
    '| Symbol assignments differing from published Goti | **0 / 52** |',
    '| Confirmation improvement | None in all three runs |',
    f'| Median final J1 across the 8,000 starts | {median_score:.12f} ({(median_score / float(reference_score) - 1) * 100:+.6f}%) |',
    f'| Worst final J1 across the 8,000 starts | {worst_score:.12f} ({(worst_score / float(reference_score) - 1) * 100:+.6f}%) |', '',
    '**241 counts distinct saved final layouts, not every layout visited during annealing and local search.** The hit rate describes these particular seeded runs; it is not a probability that Goti is globally optimal. Integer-coefficient verification rules out a hidden rounding tie or a better saved endpoint.', '',
    '### Ten lowest-scoring distinct saved endpoints', '',
    '| Rank | Candidate ID | Mixed training J1 | Above published | Runs ending here | Changed assignments |',
    '| --- | --- | ---: | ---: | ---: | ---: |',
]
for rank, candidate in enumerate(candidates[:10], 1):
    lines.append(f"| {rank} | `{candidate['id']}` | {candidate['training_J1']:.12f} | {candidate['change_percent']:+.6f}% | {candidate['retained_search_runs']} | {candidate['assignments_different_from_published']} |")
lines += [
    '', 'Ranks refer only to the final endpoints retained by these 8,000 runs. The candidate IDs use the existing research identity convention. Complete exact scores and counts for all 241 endpoints are in [report-data.json](report-data.json).', '',
    '## Comparison with the original separate Goti search', '',
    '| Measurement | Original published search | New search |', '| --- | ---: | ---: |',
    '| Starts | 512 | 8,000 |',
    '| Annealing proposals | 512,000,000 | 8,000,000,000 |',
    '| Starts reaching the winner | 36 / 512 (7.031%) | 514 / 8,000 (6.425%) |',
    f'| Best mixed training J1 | {float(reference_score):.12f} | {float(reference_score):.12f} |',
    '| Winning arrangement | Original published Goti | Identical original Goti |', '',
    'The new annealing budget is **15.625 times** the original Goti budget. The original search also polished the earlier Wikipedia/news winners; this repeat omitted those seeded polish runs and used three confirmation runs only after its fresh-start searches. Thus it is a larger repeat under the same scoring problem, with the recorded start protocol rather than an exact replay of the original run.', '',
    '## Source-by-source scores', '',
    '| Source / scope | New winner J1 | Published Goti J1 | Difference |', '| --- | ---: | ---: | ---: |',
    f'| 50/50 training mixture | {float(reference_score):.12f} | {float(reference_score):.12f} | 0 |',
]
scope_labels = {'bnwiki/train': 'Wikipedia training', 'newspaper/train': 'Newspaper training',
                'bnwiki/heldout': 'Wikipedia held-out', 'newspaper/heldout': 'Newspaper held-out',
                'bard-novel/heldout': 'BARD news held-out'}
for row in score_rows:
    lines.append(f"| {scope_labels[row['scope']]} | {row['J1']:.12f} | {row['J1']:.12f} | 0 |")
lines += [
    '', 'The equality follows from identical symbol assignments and was independently checked from the frozen count tables. These are modeled effort scores, not measured typing speed or comfort.', '',
    '## Verification and interpretation', '',
    '- Verified all 9 recorded input hashes and both original run output hashes.',
    '- Verified the complete seed range, all 8,000 recorded one-million-step annealing schedules, per-run ILS settings and all three confirmation runs.',
    '- Independently re-scored all 241 distinct saved endpoints with exact integer coefficients and rational source weighting; no endpoint beats the published reference.',
    '- Checked all 8,000 saved floating scores against those exact endpoint scores (maximum difference: ' + f'{max_float_difference:.3g}' + ').',
    '- Verified the exported layout and all 52 winner assignments against the original published Goti map.',
    '- Independently checked all five source scores; the saved training-objective/table-scorer agreement check also passes.', '',
    '**Conclusion:** retain the original separate Goti as the incumbent for its original mixed-training J1 objective. This larger fresh-seed search found no improvement and repeatedly rediscovered its exact arrangement. It strengthens search-stability evidence, while establishing neither global optimality nor a global gap. No new local certificate was computed, and old Wikipedia-only Phase 4 certificates do not transfer to this mixed-corpus run. The result does not decide the Balance objective, Jhor, human typing performance or the practical value of sharing positions.', '',
    '## Evidence and repeat command', '',
    '- [Original completed-run manifest](run-manifest.json)',
    '- [All search and confirmation records](search/A.json)',
    '- [Saved published-map comparison](comparison.json)',
    '- [Source-score evaluation](mix-search.json)',
    '- [Exported candidate layout](A-layout.json)',
    '- [Report data and verification](report-data.json)',
    '- [Report provenance and hashes](report-manifest.json)', '',
    'From the repository root, use a new empty output directory:', '',
    '```powershell', "$env:PYTHONPATH = 'src'",
    'python -u -m bangla_dh generate-layout `',
    '  --style A --seeds 8000 --first-seed 20270001 --workers 28 `',
    '  --weights bnwiki/train=0.5 newspaper/train=0.5 `',
    '  --out work/goti-j1-8b-repeat', '```', '',
    'The command has no intermediate checkpoints. Repeating it repeats the recorded seeds; a new research exploration should use a separately recorded seed range. Report generation itself runs no search.', '',
]
data_path = write_json(OUT / 'report-data.json', summary)
report_path = write_text(OUT / 'REPORT.md', '\n'.join(lines))
report_inputs = [OUT / name for name in ['search/A.json', 'run-manifest.json', 'comparison.json', 'mix-search.json', 'A-layout.json', 'build_report.py']]
report_inputs += [PROJECT_ROOT / 'results/mix-search/search/A.json', PROJECT_ROOT / 'results/mix-search/run-manifest.json', PROJECT_ROOT / 'results/phase3-crosscheck/REPORT.md']
report_inputs += [PROJECT_ROOT / name for name in manifest['inputs']]
report_inputs += [PROJECT_ROOT / name for name in ['src/bangla_dh/search/integer.py', 'src/bangla_dh/scoring/model.py', 'src/bangla_dh/mix.py']]
adjustment = PROJECT_ROOT / 'work/goti-j1-8b-v1-performance-adjustment.json'
if adjustment.exists():
    report_inputs.append(adjustment)
write_json(OUT / 'report-manifest.json', {
    'kind': 'Post-run report and independent saved-endpoint verification',
    'generated_utc': datetime.now(timezone.utc).isoformat(),
    'input_sha256': {relative_to_project(path): sha256_file(path) for path in report_inputs},
    'output_sha256': {relative_to_project(path): sha256_file(path) for path in [report_path, data_path]},
    'reported_wall_seconds_source': 'User-provided terminal output: search done, 12746 s',
    'reported_workers_source': 'User-provided executed command: --workers 28',
    'original_search_artifacts_modified': False,
})
print(json.dumps({'report': str(report_path), 'distinct_endpoints': len(counts), 'exact_hits': hits,
                  'best_exact_J1': str(reference_score), 'nearest_distinct': next_distinct,
                  'input_hashes_verified': len(hash_checks), 'output_hashes_verified': len(output_checks)}, ensure_ascii=False))
