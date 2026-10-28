"""Versioned publication identity; historical mixed-search readers stay unchanged."""
from __future__ import annotations

import json
from pathlib import Path

from .paths import PROJECT_ROOT as ROOT
from .reference import sha256_file

DESCRIPTOR = ROOT / 'data/layout-publications/shared-v1.json'
RESULTS = ROOT / 'results/shared-publication-v1'
STYLES = {'A': 'Goti', 'D': 'Jhor'}


def descriptor():
    return json.loads(DESCRIPTOR.read_text(encoding='utf-8'))


def shared_layout():
    spec = descriptor()
    path = ROOT / spec['source_map']
    if sha256_file(path) != spec['source_map_sha256']:
        raise ValueError('published shared map hash mismatch')
    raw = json.loads(path.read_text(encoding='utf-8'))
    if raw['id'] != spec['arrangement_id']:
        raise ValueError('published shared map identity mismatch')
    from .experimental.inputs import validate_layout
    layout = {s: tuple(v.split('/')) for s, v in raw['layout'].items()}
    for style in STYLES:
        validate_layout(style, layout)
    return layout


def key_layout(layout=None):
    out = {k: ['', ''] for k in 'QWERTYUIOPASDFGHJKLZXCVBNM'}
    for symbol, (key, layer) in (shared_layout() if layout is None else layout).items():
        out[key][layer == 'shift'] = symbol
    return out


def current_layout(style):
    if style not in STYLES:
        raise ValueError('current publication supports Goti (A) and Jhor (D)')
    return shared_layout()
