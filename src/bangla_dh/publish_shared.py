"""Generate the shared publication from frozen counts, without running a search."""
from __future__ import annotations

import csv
from fractions import Fraction
import io
import json
from pathlib import Path
import time
import unicodedata

from .paths import PROJECT_ROOT as ROOT, kala_path, write_json, write_text, hash_outputs
from .publication import DESCRIPTOR, RESULTS, STYLES, descriptor, shared_layout, key_layout
from .reference import sha256_file


def examples(layout):
    from .bangla.styles import Style
    from .bangla.grammar import Escape
    words = ['আমি', 'কী', 'বই', 'এবং', 'তিনিই', 'আকাশ', 'ক্ষেত্রে', 'গাই', 'ইই', 'ড়', 'ঢ়', 'য়']
    rows = []
    for style in STYLES:
        machine = Style(style)
        for word in words:
            labels = machine.encode(word)
            if any(isinstance(x, Escape) for x in labels) or machine.decode(labels) != unicodedata.normalize('NFC', word):
                raise ValueError('example failed round trip: ' + word)
            keys = ['Shift+' + layout[s][0] if layout[s][1] == 'shift' else layout[s][0] for s in labels]
            rows.append({'style': style, 'text': word, 'keys': ' '.join(keys), 'labels': ' '.join(labels)})
    return rows


def build():
    from . import shared_challenge
    from .mix import mixed_best_layout
    from .kala_export import keyboard_file, kala_import_problems, key_map_problems
    from .bangla.styles import Style
    from .phase3 import problem_fixed
    from .search.problem import load_problem

    started = time.perf_counter()
    spec, layout = descriptor(), shared_layout()
    source_manifest_path = ROOT/spec['source_run']/'run-manifest.json'
    source_results_path = ROOT/spec['source_run']/'results.json'
    source_manifest = json.loads(source_manifest_path.read_text(encoding='utf-8'))
    source_results = json.loads(source_results_path.read_text(encoding='utf-8'))
    search_provenance = {
        'source_run': spec['source_run'], 'starts': len(source_manifest['seeds']),
        'tracks': len(source_manifest['seeds'])//source_manifest['settings']['seeds'],
        'annealing_proposals_per_start': source_manifest['settings']['steps'],
        'annealing_proposals': len(source_manifest['seeds'])*source_manifest['settings']['steps'],
        'distinct_retained_arrangements': source_results['retained_pool_count'],
        'full_qualifying_evaluations': source_results['refinement']['jointly_eligible_evaluations'],
        'leading_tradeoffs': source_results['jointly_eligible_frontier_count'],
        'scope': 'annealing proposals plus separate local search; proposals may revisit arrangements; finite bounded search'}
    scorer = shared_challenge.load_scorer()
    data, digest = scorer.load_data()
    result = scorer.evaluate({'season': shared_challenge.DATA_VERSION, 'layout': key_layout()}, data, True)
    source = json.loads((ROOT/spec['source_map']).read_text(encoding='utf-8'))
    checks = {'both styles eligible': result['eligible']}
    rows, entries, original_changes = [], [], {}
    columns = dict(zip(scorer.HELDOUT, ('wikipedia', 'newspaper', 'unseenNews')))
    old_public = json.loads((ROOT/'challenge/challenge-data.json').read_text(encoding='utf-8'))['public_layouts']
    changes = []
    for style, name in STYLES.items():
        own = result['scores'][style]
        checks[style+' saved exact effort'] = Fraction(own['training']['J1_exact']) == Fraction(source['training'][style]['metrics']['J1_exact'])
        checks[style+' saved R'] = own['balance']['R'] == source['training'][style]['balance']['R']
        for scenario, sources in own['diagnostics'].items():
            for corpus, metrics in sources.items():
                rows.append({'style': style, 'fingering': scenario, 'corpus': corpus, **metrics})
        heldout = own['diagnostics']['model-optimal']
        j1 = {col: heldout[c]['J1'] for c, col in columns.items()}
        entries.append({'id': spec['arrangement_id']+'-'+style, 'name': f"{spec['public_name']} · {name} style", 'style': style,
                        'kind': 'shared-style', 'j1': j1, 'average': sum(j1.values())/3,
                        'fingering': 'model-optimal', 'developer': 'Kala research'})
        old = mixed_best_layout(style)
        original = scorer.evaluate({'season': shared_challenge.DATA_VERSION, 'layout': key_layout(old)}, data, True)['scores'][style]
        original_changes[style] = {}
        for scenario in data['models']:
            new_mean = scorer.mean([own['diagnostics'][scenario][c] for c in scorer.HELDOUT])
            old_mean = scorer.mean([original['diagnostics'][scenario][c] for c in scorer.HELDOUT])
            original_changes[style][scenario] = {k: 100*(new_mean[k]/old_mean[k]-1)
                for k in ('J1', 'within_distance', 'cross_distance')}
        changes.extend({'style': style, 'symbol': s, 'original': '/'.join(old[s]), 'shared': '/'.join(a)}
                       for s, a in layout.items() if a != old[s])
    entries.extend({'id': 'baseline-'+str(i), **e} for i, e in enumerate(old_public['entries']) if e['kind'] != 'bangla-dh')
    # Historical entries have a different kind spelling in older snapshots; select explicitly by name.
    entries = [e for e in entries if e['kind'] == 'shared-style' or e['name'] not in ('Kala Goti', 'Kala Jhor')]
    entries.sort(key=lambda r: r['average'])
    summary = {'version': spec['version'], 'arrangement_id': spec['arrangement_id'], 'status': spec['status'],
               'public_name': spec['public_name'], 'public_name_bn': spec['public_name_bn'],
               'search_provenance': search_provenance,
               'challenge_version': shared_challenge.DATA_VERSION, 'challenge_data_sha256': digest,
               'metric': 'J1 per text unit; model-optimal shared styles, favorable recorded legacy fixed-layout benchmarks',
               'note': 'One shared arrangement with two typing styles. Equal means of three previously examined held-out sources. Modeled effort, not speed.',
               'texts': columns, 'entries': entries, 'scores': result['scores'], 'historical_entries': old_public['entries'],
               'physical_arrangements': 7, 'evaluation_configurations': 8,
               'map_license': spec['map_license'], 'heldout_changes_vs_original_percent': original_changes}
    checks['six distinct fixed baselines'] = len(entries) == 8
    written = [write_json(RESULTS/'shared-map.json', {'id': spec['arrangement_id'], 'public_name': spec['public_name'], 'styles': STYLES, 'layout': key_layout()}),
               write_json(RESULTS/'public-summary.json', summary), write_json(RESULTS/'examples.json', examples(layout)),
               write_json(RESULTS/'relocations.json', changes)]
    lines = ['# From the original arrangements to Kala Layout', '',
             'Both typing styles use the same positions (research identifier B01). These are symbol relocations, not measured learning difficulty.', '']
    for style, name in STYLES.items():
        lines += [f'## Original {name} arrangement → Kala Layout', '', '| Symbol | Original key/layer | Shared key/layer |', '| --- | --- | --- |']
        lines += [f"| {r['symbol']} | {r['original']} | {r['shared']} |" for r in changes if r['style'] == style]
        lines += ['']
    written.append(write_text(RESULTS/'RELOCATIONS.md', '\n'.join(lines)))
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    written.append(write_text(RESULTS/'scores.csv', stream.getvalue()))
    maps = []
    example_rows = examples(layout)
    for style, name in STYLES.items():
        full = {**layout, **problem_fixed(load_problem())}
        file = keyboard_file(Style(style), full, {'publication': spec['version'], 'arrangementId': spec['arrangement_id'],
            'status': 'provisional', 'style': {'code': style, 'name': name}, 'availability': spec['app_availability']})
        file.update(name=f"{spec['public_name']} — {name} style", comment='Kala Layout (research identifier B01); '+name+' vowel-entry style. Research export; '+spec['app_availability'])
        file['about']['publicName'] = spec['public_name']
        from .kala_export import typing_rule
        file['about']['style']['typingRule'] = typing_rule(Style(style))
        checks[style+' import schema'] = not kala_import_problems(json.dumps(file, ensure_ascii=False).encode('utf-8'))
        checks[style+' key map'] = not key_map_problems(full, file)
        if style == 'A':
            from .kala_export import KalaFixedEngine, type_word, presses_of
            alphabet = json.loads(kala_path('kala/layout/bn/Alphabet.json').read_text(encoding='utf-8'))
            engine = KalaFixedEngine(file, alphabet)
            presses = presses_of(full)
            checks['Goti export engine round trips'] = all(
                unicodedata.normalize('NFC', type_word(engine, [presses[label] for label in Style('A').encode(r['text'])]))
                == unicodedata.normalize('NFC', r['text']) for r in example_rows if r['style'] == 'A')
        maps.append(file['layers'])
        written.append(write_json(RESULTS/f'kala-shared-{name.lower()}.json', file))
    checks['identical application key maps'] = maps[0] == maps[1]
    written.append(write_json(RESULTS/'verification.json', checks))
    table = '\n'.join(f"| {e['name']} | {e['j1']['wikipedia']:.6f} | {e['j1']['newspaper']:.6f} | {e['j1']['unseenNews']:.6f} | {e['average']:.6f} |" for e in entries)
    written.append(write_text(RESULTS/'REPORT.md', f'''# Kala Layout: one arrangement, Goti and Jhor styles

**Kala Layout** is the public name; **B01/P01** is its research shortlist identifier. The underlying map, encoders and scores are unchanged by this naming update of 29 October 2026.

Owner decision, 28 October 2026: provisionally use `{spec['arrangement_id']}` (B01/P01), with Goti (A) and Jhor (D) as typing styles. Changing style preserves every symbol position. Selection is a practical compromise, not a new scalar-score optimum or a measured learning benefit.

## Why share

The original arrangements differ at 31/52 assignments. Using the original Goti arrangement for Jhor costs +1.218% training effort and +24.83% within-word distance; using original Jhor for Goti costs +4.421%/+159.56%. B01 instead costs +0.689%/+4.790% in Goti and +0.439%/+3.766% in Jhor. These pass the shared experiment's +0.75%/+7.5% limits against each original on the independently normalized 50/50 training mix and model-optimal fingering. B01 Goti fails the original strict +0.5% effort policy. Calibration is unchanged; the expanded eligible domain is explicitly a new shared challenge season.

Sharing means one arrangement to remember and maintain across styles. It still requires learning a new arrangement: 43 Goti and 39 Jhor symbols move from the originals. Entry recipes remain different. Learning time, error rate, speed and comfort have not been measured.

## Four-billion search provenance

The source run completed 20,000 starts across two tracks, with 200,000 annealing proposals per start: 4,000,000,000 proposals, plus local search. It retained 113,550 distinct assignments; final screening/refinement fully scored 961 qualifying maps and retained two leading trade-offs. Proposals may revisit maps. This was not an exhaustive test of four billion unique combinations, and is not a proof of optimality. The selected B01 map became the provisional Kala Layout. See the original source-run and interpretation manifests for the exact saved scope.

## Typing-style heritage and credit

Goti preserves the modern fixed-layout consonant-then-sign and hasant-plus-sign core: the original Goti search explicitly used the UniJoy-style grammar. Credit [Ekushey's UniJoy contributors](https://ekushey.org/keyboard-layout/ekusheyr-shadhinota-unijoy-layout/) and [Avro/OmicronLab's fixed-layout documentation](https://www.omicronlab.com/download/pdf/Bangla%20Typing%20with%20Fixed%20Keyboard%20Layouts.pdf), including Mehdi Hasan Khan and the Avro team. These entry conventions are not a Kala invention; the key arrangement was searched separately.

Avro also documents Automatic Vowel Forming, so context-sensitive vowel entry predates Jhor. Jhor's exact timing-free repeated-key rule is specified by this project; the reviewed primary documentation did not establish an identical complete recipe or invention priority. [Typing-style credits and source-review scope](../../docs/TYPING_STYLES.md) explain the distinction. This attribution correction changes no grammar, benchmark or score.

## Trade-offs and alternatives

Training cross-space same-finger distance rises +25.59% in Goti and +5.89% in Jhor. On previously examined held-out sources, effort rises +0.608%/+0.447%, within-word distance changes -0.107%/+1.351%, and cross-space distance rises +25.750%/+3.923%. These caps apply only to primary training/fingering. Separate Balance leaders have lower same-style R than B01; one remembered map is outside that formula.

B01 has Goti R 0.761312 and Jhor R 0.441365. These are separately calibrated; they are never added or compared across styles. B02 (`shared-7083b1ebfa5aa3a7`) exchanges ৈ/ৌ between Shift+X/Shift+W and trades a slightly better Jhor R for worse Goti R. Both are non-dominated in the evaluated full-score pools. B01 is the provisional practical preference. The enhanced pilot used shared starts and is not independent rediscovery. Four billion counts proposals, not unique maps/full R evaluations; no optimality proof transfers.

## Previously examined held-out effort

| Configuration | Wikipedia | Newspaper | BARD news | Mean J1 |
| --- | --- | --- | --- | --- |
{table}

Two style configurations of one shared map plus six fixed baselines: seven physical arrangements, eight evaluations. Fixed baselines retain their favorable recorded original effort scores; canonical mechanical envelopes are separate and are not an overall score. All five sources and both fingerings are in scores.csv; exact training effort and separate R are in public-summary.json. All six maps and conservative mechanical/coverage comparisons are documented in [the top-ten comparison](../shared-top10-comparison-v1/REPORT.md). Bijoy positions use the explicitly borrowed UniJoy-rule proxy, not a separately verified commercial implementation. Bornona and Probhat beat B01 on some cross-space metrics; Windows Default has better order credit with greater escapes. No phonetic layouts are compared.

## Evidence, history and availability

The chain is [existing-map check](../shared-style-check-v1/REPORT.md), [strict shared search](../shared-layout-v1/run-v1/REPORT.md), [relaxed four-billion experiment](../shared-layout-relaxed-v1/run-4b-v1/REPORT.md), [interpretation](../shared-layout-relaxed-v1/interpretation-4b-v1/REPORT.md), then [top-ten/pilot comparison](../shared-top10-comparison-v1/REPORT.md). Original mixed-search results, phase reports, exports and legacy challenge remain unchanged. Known held-out results are exploratory reuse, not fresh confirmation. The token `bard-novel` means non-overlapping BARD news documents, not literary novels; references to BARD novels in the historical comparison prose are a naming error, with no numerical effect.

The new map/exports use the repository MIT license; the original separate maps retain their CC0 dedication. Exports are research artifacts, not an installed application update. Goti uses hasant/sign sequences; Jhor requires the application's context-vowel engine. Confirm compatible support before importing; older installations may retain original arrangements. No companion application was modified.

## Rebuild

```powershell
$env:PYTHONPATH = "src"
python -m bangla_dh challenge-kit
python -m bangla_dh publish-shared
python -m bangla_dh challenge-verify challenge/shared-v1/reference.json
python -m bangla_dh check-results
```

This rebuild reuses frozen derived counts; no new search/text download. Full source search settings/seeds remain in the original run manifest. run-manifest.json pins the descriptor, evidence, scorer, calibration, inputs and outputs. The new portable shared scorer independently agrees with the integer/direct evaluators under both styles. Model constants, text and typing grammars are unchanged. Best found; no claim of proven optimum, measured speed or comfort.
'''))
    inputs = [DESCRIPTOR, ROOT/spec['source_map'], ROOT/spec['calibration'], Path(__file__),
              ROOT/'src/bangla_dh/publication.py', shared_challenge.RESULTS/'run-manifest.json',
              shared_challenge.SCRIPT, shared_challenge.RESULTS/'scoring-data.json.gz',
              source_manifest_path, source_results_path,
              ROOT/'results/shared-top10-comparison-v1/run-manifest.json', ROOT/'challenge/challenge-data.json']
    run = json.loads((ROOT/'results/shared-layout-relaxed-v1/run-4b-v1/run-manifest.json').read_text(encoding='utf-8'))
    written.append(write_json(RESULTS/'run-manifest.json', {'version': spec['version'], 'new_search': False, 'seeds': [],
        'source_run_manifest': spec['source_run']+'/run-manifest.json', 'source_parameters': run.get('settings', run.get('parameters', {})),
        'parameters': data['policy'], 'input_sha256': hash_outputs(inputs), 'output_sha256': hash_outputs(written),
        'checks': checks, 'seconds': time.perf_counter()-started}))
    if not all(checks.values()):
        raise ValueError('publication check failed: '+str([k for k, v in checks.items() if not v]))
    print('Shared publication: all checks passed')
    return written
