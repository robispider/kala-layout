"""Record the inspected roots and source hashes for the restoration handoff."""
import json
from pathlib import Path
import subprocess
from datetime import datetime, timezone

from bangla_dh.paths import PROJECT_ROOT, write_json
from bangla_dh.reference import sha256_file

sources = {
    'kala-layout': [
        'AGENTS.md', 'results/mix-search/search/A.json', 'results/mix-search/search/D.json',
        'results/kala-keyboards/kala-goti.json', 'results/kala-keyboards/kala-jhor.json',
        'data/layout-publications/shared-v1.json', 'src/bangla_dh/cli.py',
        'site/scripts/publication.mjs', 'site/scripts/sync-content.mjs',
        '.github/workflows/submissions.yml',
        'work/goti-j1-8b-v1/REPORT.md', 'work/goti-j1-8b-v1/search/A.json',
        'work/goti-j1-8b-v1/run-manifest.json', 'work/goti-j1-8b-v1/report-data.json',
        'results/shared-publication-v1/REPORT.md', 'results/balance-v1/CANDIDATE_ANALYSIS.md',
    ],
    'kala': [
        'AGENTS.md', 'plans/shared-layout/VALIDATION.md', 'plans/shared-layout/migration.json',
        'plans/product-refactor/EXTERNAL_APP_CONTRACT.md',
        'plans/fixed-layout-typing-style/IMPLEMENTATION_PLAN.md',
        'kala/layout/bn/KalaGoti.json', 'kala/layout/bn/KalaJhor.json',
        'kala.BaselineTests/Fixtures/OriginalKalaLayouts/KalaGoti.json',
        'kala.BaselineTests/Fixtures/OriginalKalaLayouts/KalaJhor.json',
        'kala.BaselineTests/SharedKalaLayoutTests.cs',
        'kala/Learning/Study/PromptBank.cs', '.github/workflows/publish-kala.yml',
    ],
    'kala-typing-master': [
        'package.json', 'scripts/import-kala.mjs', 'src/lib/store.ts',
        'src/data/layouts.json', 'src/data/shared-candidates.json',
        'tests/shared-layout.test.ts', 'RESEARCH.md', 'artifacts/shared-layout-validation.md',
    ],
    'kala-releases': [
        'AGENTS.md', 'SITE.md', 'docs/layouts/kala-goti.md', 'docs/layouts/kala-jhor.md',
        'docs/layouts/kala-layout.md', 'docs/layouts/research-and-comparison.md',
        'docs/reference/layout-research-snapshot.json', 'site/src/components/KalaHome.astro',
    ],
}
repos = {}
for name, files in sources.items():
    root = PROJECT_ROOT if name == 'kala-layout' else PROJECT_ROOT.parent / name
    def git(*args):
        return subprocess.check_output(['git', '-C', str(root), *args], text=True).strip()
    inputs = {}
    for name_in_repo in files:
        path = root / name_in_repo
        assert path.is_file(), path
        inputs[name_in_repo] = sha256_file(path)
    repos[name] = {
        'root': str(root), 'head': git('rev-parse', 'HEAD'),
        'status_at_snapshot': git('status', '--porcelain'),
        'source_sha256': inputs,
    }
data = json.loads((PROJECT_ROOT/'work/goti-j1-8b-v1/report-data.json').read_text(encoding='utf-8'))
assert data['same_layout'] and data['best_hits'] == 514 and data['proposal_count'] == 8_000_000_000
plan = PROJECT_ROOT/'plans/restore-published-layouts/HANDOFF.md'
snapshot = {
    'created_utc': datetime.now(timezone.utc).isoformat(),
    'purpose': 'Planning baseline only; original-map restoration is not implemented by this snapshot',
    'handoff_sha256': sha256_file(plan), 'repositories': repos,
    'target_arrangements': {'A': 'A-18fe73cb912ae3f1', 'D': 'D-e4a6be48881da590'},
    'communication_policy': {
        'development_stage': 'Continuous early-stage development; no public restoration announcement',
        'product_surfaces': 'Published layouts, supported benefits, current typing instructions and accurate availability',
        'research_discussion_location': 'kala-layout only',
        'research_discussion_scope': 'Shared/Balance experiments, selection rationale, detailed search evidence and limits',
        'product_research_link_allowed': True,
    },
    'goti_research_evidence': {
        'starts': data['starts'], 'annealing_proposals': data['proposal_count'],
        'hits': data['best_hits'], 'hit_percent': data['best_hit_percent'],
        'distinct_saved_endpoints': data['distinct_retained_search_endpoints'],
        'same_published_layout': data['same_layout'],
        'elapsed_wall_seconds': data['elapsed_wall_seconds'],
        'global_optimality_proven': False, 'new_jhor_run_performed': False,
    },
}
target = write_json(PROJECT_ROOT/'plans/restore-published-layouts/SOURCE_SNAPSHOT.json', snapshot)
print(json.dumps({'plan': str(plan), 'snapshot': str(target), 'repositories': len(repos),
                  'verified_source_paths': sum(len(r['source_sha256']) for r in repos.values())}))
