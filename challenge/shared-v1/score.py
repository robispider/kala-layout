#!/usr/bin/env python3
"""Shared-arrangement challenge. Python 3.10+, standard library only.

Keep this script beside scoring-data.json.gz and LICENSE-mechanics.txt.
The bundle contains derived counts and frozen model tables, never corpus text.
Order-credit tables derive from Arno Klein's MIT-licensed Engram code.
"""
from __future__ import annotations

import argparse
import base64
from fractions import Fraction
import gzip
import hashlib
import json
import math
from pathlib import Path
import sys
import unicodedata

SCRIPT_VERSION = '2.0.0'
DATA_VERSION = 'bangla-dh-shared-challenge-v1'
EXPECTED_SHA256 = '36be11511d89e2aecf1041418aa27f61abe97fa257f3cdcc44b2b8d1fe5bd757'
LETTERS = 'QWERTYUIOPASDFGHJKLZXCVBNM'
TRAIN = ('bnwiki/train', 'newspaper/train')
HELDOUT = ('bnwiki/heldout', 'newspaper/heldout', 'bard-novel/heldout')


def load_data(path=None):
    path = Path(path) if path else Path(__file__).with_name('scoring-data.json.gz')
    raw = gzip.decompress(path.read_bytes())
    digest = hashlib.sha256(raw).hexdigest()
    if digest != EXPECTED_SHA256:
        raise ValueError('shared scoring data hash mismatch')
    data = json.loads(raw)
    if data['version'] != DATA_VERSION:
        raise ValueError('wrong challenge season')
    return data, digest


def parse_layout(submission, data):
    if not isinstance(submission, dict) or submission.get('season') != DATA_VERSION:
        raise ValueError('set season to ' + DATA_VERSION + '; legacy style files are a different task')
    if 'style' in submission or 'styles' in submission:
        raise ValueError('submit one layout without style-specific alternatives; both styles are automatic')
    rows = submission.get('layout')
    if not isinstance(rows, dict) or set(rows) != set(LETTERS):
        raise ValueError('layout must contain exactly the 26 uppercase letter keys')
    placed = {}
    for key in LETTERS:
        pair = rows[key]
        if not isinstance(pair, list) or len(pair) != 2 or any(not isinstance(s, str) for s in pair):
            raise ValueError(key + ' requires [base symbol, shift symbol]')
        for layer, symbol in zip(('base', 'shift'), pair):
            symbol = unicodedata.normalize('NFC', symbol.replace('◌', '').strip())
            if symbol in placed:
                raise ValueError('symbol placed twice: ' + symbol)
            placed[symbol] = (key, layer)
    if set(placed) != set(data['symbols']):
        raise ValueError('layout must contain every frozen symbol exactly once')
    return placed


def layout_hash(placed):
    raw = json.dumps(sorted((s, list(a)) for s, a in placed.items()), ensure_ascii=False, separators=(',', ':'))
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()


def metrics(layout, counts, model):
    assignment = {**layout, **{s: tuple(a) for s, a in model['fixed'].items()}, ' ': ('SPACE', 'base')}
    index = {tuple(a): i for i, a in enumerate(model['actions'])}
    ids = [index[assignment[s]] for s in counts['labels']]
    width, N = len(index), counts['N']
    key = sum(n * model['K'][ids[i]] for i, n in counts['u'])
    mod = sum(n * model['M'][ids[i]] for i, n in counts['u'])
    pair = rate = rep = covered = 0
    distance = ec = dc = 0.
    for a, b, n in counts['pairs']:
        p = ids[a] * width + ids[b]
        pair += n * model['B'][p]
        rate += n * model['move'][p]
        rep += n * model['repeat'][p]
        distance += n * model['dist'][p]
        ec += n * model['E'][p]
        dc += n * model['D'][p]
        covered += n * model['support'][p]
    cr = rr = 0
    cd = 0.
    for a, b, n in counts['cross']:
        p = ids[a] * width + ids[b]
        cr += n * model['move'][p]
        cd += n * model['dist'][p]
        rr += n * model['repeat'][p]
    total = counts['pair_total']
    cross_total = counts['cross_total']
    presses = sum(n for _, n in counts['u'])
    shift = sum(n for i, n in counts['u'] if model['actions'][ids[i]][1] == 'shift')
    order_index = {k: i for i, k in enumerate(model['order_keys'])}
    mapping = {s: order_index.get(a[0], -1) for s, a in assignment.items()}
    table = base64.b64decode(model['order_table'])
    w = len(order_index)
    triples = supported = credit = 0
    for a, b, c, n in counts['triples']:
        i, j, k = mapping[a], mapping[b], mapping[c]
        triples += n
        if min(i, j, k) >= 0:
            supported += n
            credit += n * table[(i * w + j) * w + k]
    result = {'J1_exact': str(Fraction(key + mod + pair, N * 1000000)),
              'J1': (key + mod + pair) / (N * 1000000),
              'key_effort': key / (N * 1000000), 'pair_effort': pair / (N * 1000000),
              'shift_effort': mod / (N * 1000000),
              'within_rate': rate / N, 'within_distance': distance / N,
              'cross_rate': cr / cross_total, 'cross_distance': cd / cross_total,
              'cross_repeat': rr / cross_total, 'repeat_share_pairs': rep / total,
              'shift_share': shift / presses, 'escaped_share': counts['escaped'] / N,
              'pair_coverage': covered / total,
              'engram_pair_lower': ec / total, 'engram_pair_upper': (ec + total - covered) / total,
              'dvorak_lower': dc / total, 'dvorak_upper': (dc + total - covered) / total,
              'order_lower': credit / triples, 'order_upper': (credit + triples - supported) / triples,
              'order_coverage': supported / triples}
    return result


def mean(rows):
    result = {k: sum(r[k] for r in rows) / len(rows) for k in rows[0] if k != 'J1_exact'}
    result['J1_exact'] = str(sum((Fraction(r['J1_exact']) for r in rows), Fraction()) / len(rows))
    return result


def balance(metrics, calibration):
    ref = calibration['reference']
    effort = Fraction(metrics['J1_exact']) <= Fraction(ref['J1_exact']) * Fraction(403, 400)
    within = metrics['within_distance'] <= ref['within_distance'] * 1.075 + 1e-14
    result = {'eligible': effort and within, 'effort_cap_pass': effort, 'within_cap_pass': within, 'R': None}
    if not result['eligible']:
        return result
    values = [metrics['J1'], metrics['cross_distance'], metrics['within_distance'], 1 - metrics['order_lower']]
    scores = []
    for setting in calibration['settings']:
        weights = setting['weights']
        terms = [w * (x - a) / t for x, a, t, w in zip(values, calibration['aspirations'], calibration['scales'], weights)]
        b = (max(terms) + setting['rho'] * sum(terms)) / sum(weights)
        scores.append((max(0., b - setting['b_minus']), setting['id']))
    if len(scores) != 81 or any(not math.isfinite(r) for r, _ in scores):
        raise ValueError('invalid frozen calibration')
    result['R'], result['worst_setting'] = max(scores)
    return result


def dominates(a, b):
    return all(x <= y for x, y in zip(a, b)) and any(x < y for x, y in zip(a, b))


def evaluate(submission, data, diagnostics=False):
    placed = parse_layout(submission, data)
    scores = {}
    for style in ('A', 'D'):
        rows = {c: metrics(placed, data['counts'][style][c], data['models']['model-optimal']) for c in TRAIN}
        training = mean(list(rows.values()))
        scores[style] = {'training': training, 'balance': balance(training, data['calibration'][style])}
        if diagnostics:
            scores[style]['diagnostics'] = {
                fingering: {c: metrics(placed, counts, model) for c, counts in data['counts'][style].items()}
                for fingering, model in data['models'].items()}
    eligible = all(s['balance']['eligible'] for s in scores.values())
    R = [scores[s]['balance']['R'] for s in ('A', 'D')]
    reference = [data['reference']['training'][s]['balance']['R'] for s in ('A', 'D')]
    return {'season': DATA_VERSION, 'publication_id': data['publication_id'], 'name': str(submission.get('name', ''))[:120],
            'author': str(submission.get('author', ''))[:120], 'layout_sha256': layout_hash(placed),
            'eligible': eligible, 'scores': scores, 'R': R,
            'improves_reference': eligible and dominates(R, reference),
            'reference_copy': layout_hash(placed) == data['reference']['layout_sha256']}


def read_submission(path):
    if Path(path).stat().st_size > 64000:
        raise ValueError('submission exceeds 64000 bytes')
    def unique(pairs):
        out = {}
        for key, value in pairs:
            if key in out:
                raise ValueError('JSON key given twice: ' + key)
            out[key] = value
        return out
    return json.loads(Path(path).read_text(encoding='utf-8-sig'), object_pairs_hook=unique)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('files', nargs='*')
    p.add_argument('--reference', action='store_true')
    p.add_argument('--template', metavar='FILE')
    p.add_argument('--diagnostics', action='store_true', help='both fingerings and five source scopes; no ranking effect')
    args = p.parse_args(argv)
    data, digest = load_data()
    if args.template:
        target = Path(args.template)
        if target.exists():
            p.error('template output already exists')
        target.write_text(json.dumps({'season': DATA_VERSION, 'name': 'my shared arrangement',
                                     'layout': data['reference']['layout']}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    if args.reference or not (args.files or args.template):
        print(json.dumps({'season': DATA_VERSION, 'data_sha256': digest, 'reference': data['reference'],
                          'policy': data['policy']}, ensure_ascii=False, indent=2))
    invalid = False
    for file in args.files:
        try:
            result = evaluate(read_submission(file), data, args.diagnostics)
            print(json.dumps({'file': file, **result}, ensure_ascii=False, indent=2))
        except (ValueError, TypeError, KeyError, OSError) as error:
            print(f'{file}: invalid: {error}', file=sys.stderr)
            invalid = True
    return 1 if invalid else 0


if __name__ == '__main__':
    raise SystemExit(main())
