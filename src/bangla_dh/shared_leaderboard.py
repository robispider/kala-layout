"""Season-specific shared-map board; never pool independently calibrated R."""
from __future__ import annotations

import json
import html
import re
from pathlib import Path

from .paths import PROJECT_ROOT as ROOT, write_json, write_text
from . import shared_challenge

RESULTS = ROOT / 'submissions/shared-v1'


def score_files(files=None):
    scorer = shared_challenge.load_scorer()
    data, digest = scorer.load_data()
    paths = [Path(p) for p in files] if files is not None else sorted(
        p for p in RESULTS.glob('*.json') if p.name != 'leaderboard.json')
    entries, problems, seen = [], [], {data['reference']['layout_sha256']: 'B01 reference'}
    for path in paths:
        try:
            row = scorer.evaluate(scorer.read_submission(path), data)
            identity = row['layout_sha256']
            if identity in seen:
                raise ValueError('same map as ' + seen[identity])
            seen[identity] = path.name
            row['file'] = path.name
            entries.append(row)
        except (ValueError, KeyError, TypeError, OSError) as error:
            problems.append({'file': path.name, 'problem': str(error)})
    eligible = [r for r in entries if r['eligible']]
    reference = [data['reference']['training'][s]['balance']['R'] for s in ('A', 'D')]
    for row in entries:
        row['dominated'] = row['eligible'] and (scorer.dominates(reference, row['R']) or any(
            scorer.dominates(other['R'], row['R']) for other in eligible))
        row['status'] = 'ineligible' if not row['eligible'] else 'dominated' if row['dominated'] else 'frontier'
    entries.sort(key=lambda r: (not r['eligible'], r['dominated'], r['file']))
    return {'data_version': shared_challenge.DATA_VERSION, 'data_sha256': digest,
            'publication_id': data['publication_id'], 'arrangement_id': data['arrangement_id'],
            'script_version': scorer.SCRIPT_VERSION, 'reference': data['reference'],
            'display_order': 'frontier, dominated, ineligible; filename within each group (not a scalar rank)',
            'entries': entries, 'problems': problems}


def render(board):
    lines = ['# Shared-arrangement challenge board', '',
             f"Season `{board['data_version']}`; B01 is provisional. One map is evaluated in both styles.", '',
             'Frontier status is relative to B01 and all eligible submissions. Display order is not an overall rank.', '',
             '| Arrangement | Author | Status | Goti R | Jhor R | Improves B01 |',
             '| --- | --- | --- | --- | --- | --- |']
    def safe(value):
        value = html.escape(str(value)).replace('\n', ' ').replace('\r', ' ')
        return re.sub(r'([\\`*_|\[\]])', r'\\\1', value)
    for r in board['entries']:
        scores = [f'{v:.9f}' if v is not None else 'ineligible' for v in r['R']]
        lines.append(f"| {safe(r['name'] or r['file'])} | {safe(r['author'])} | {r['status']} | {' | '.join(scores)} | {r['improves_reference']} |")
    if not board['entries']:
        lines += ['', 'No submissions yet. B01 is the reference; B02 remains a documented trade-off.']
    return '\n'.join(lines) + '\n'


def run(files=None, check=False, diagnostics=None):
    board = score_files(files)
    if check:
        for row in board['entries']:
            print(f"{row['file']}: {row['status']}; Goti/Jhor R={row['R']}; improves B01={row['improves_reference']}")
        for error in board['problems']:
            print(f"{error['file']}: invalid: {error['problem']}")
        # Structurally valid but ineligible maps are reported, not confused with malformed files.
        if diagnostics and files:
            return shared_challenge.verify(files, diagnostics=diagnostics) or bool(board['problems'])
        return 1 if board['problems'] else 0
    write_json(RESULTS/'leaderboard.json', board)
    write_text(RESULTS/'LEADERBOARD.md', render(board))
    return 0
