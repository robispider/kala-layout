"""One-map publication, portable-score parity, eligibility and season isolation."""
from fractions import Fraction
import json
from pathlib import Path
import random
import tempfile
import unittest
import contextlib
import io
from unittest.mock import patch

from bangla_dh.paths import PROJECT_ROOT as ROOT, output_path, write_json
from bangla_dh.publication import descriptor, shared_layout, key_layout, current_layout
from bangla_dh import shared_challenge, shared_leaderboard
from bangla_dh.experimental.shared_relaxed import RelaxedProblem, relaxed_evaluate
from bangla_dh.mix import mixed_best_layout


class SharedPublicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scorer = shared_challenge.load_scorer()
        cls.data, cls.digest = cls.scorer.load_data()
        cls.problem = RelaxedProblem()

    def submission(self, layout=None):
        return {'season': shared_challenge.DATA_VERSION, 'layout': key_layout(layout)}

    def test_one_map_two_styles_and_historical_maps_unchanged(self):
        self.assertEqual(current_layout('A'), current_layout('D'))
        self.assertEqual(descriptor()['arrangement_id'], 'shared-76c9b9dbfc689d0b')
        for style, count in [('A', 43), ('D', 39)]:
            old, new = mixed_best_layout(style), shared_layout()
            self.assertEqual(sum(old[s] != a for s, a in new.items()), count)
        exports = [json.loads((ROOT/f'results/shared-publication-v1/kala-shared-{n}.json').read_text(encoding='utf-8')) for n in ('goti', 'jhor')]
        self.assertEqual(exports[0]['layers'], exports[1]['layers'])
        self.assertNotEqual(exports[0]['about']['style'], exports[1]['about']['style'])

    def test_portable_parity_for_finalists_originals_and_random_maps(self):
        layouts = [shared_layout(), mixed_best_layout('A'), mixed_best_layout('D')]
        raw = json.loads((ROOT/'results/shared-top10-comparison-v1/layouts/shared-7083b1ebfa5aa3a7.json').read_text(encoding='utf-8'))
        layouts.append({s: tuple(v.split('/')) for s, v in raw['layout'].items()})
        rng = random.Random(728)
        for _ in range(2):
            slots = list(shared_layout().values()); rng.shuffle(slots)
            layouts.append(dict(zip(shared_layout(), slots)))
        for layout in layouts:
            actual = self.scorer.evaluate(self.submission(layout), self.data)
            direct = self.problem.evaluate_training(self.problem.perm_of(layout))
            for style in ('A', 'D'):
                a, b = actual['scores'][style], direct[style]
                self.assertEqual(Fraction(a['training']['J1_exact']), Fraction(b['metrics']['J1_exact']))
                self.assertEqual(a['balance']['eligible'], b['balance']['eligible'])
                self.assertEqual(a['balance']['R'], b['balance']['R'])
                for k in ('within_distance', 'cross_distance', 'order_lower', 'order_upper'):
                    self.assertAlmostEqual(a['training'][k], b['metrics'][k], places=12)
            if layout in [mixed_best_layout('A'), mixed_best_layout('D')]:
                self.assertFalse(actual['eligible'])
                self.assertFalse(actual['improves_reference'])

    def test_reference_and_b02_tradeoff_are_not_dominance_improvements(self):
        ref = self.scorer.evaluate(self.submission(), self.data)
        self.assertTrue(ref['eligible']); self.assertTrue(ref['reference_copy'])
        self.assertFalse(ref['improves_reference'])
        alternative = self.submission()
        alternative['layout']['W'][1], alternative['layout']['X'][1] = alternative['layout']['X'][1], alternative['layout']['W'][1]
        row = self.scorer.evaluate(alternative, self.data)
        self.assertTrue(row['eligible']); self.assertFalse(row['improves_reference'])
        self.assertGreater(row['R'][0], ref['R'][0]); self.assertLess(row['R'][1], ref['R'][1])

    def test_frozen_caps_exact_boundaries_and_no_recalibration(self):
        cal = self.data['calibration']['A']
        metrics = self.scorer.evaluate(self.submission(), self.data)['scores']['A']['training']
        boundary = Fraction(cal['reference']['J1_exact'])*Fraction(403,400)
        for exact, within, eligible in [(boundary, cal['reference']['within_distance']*1.075, True),
                (boundary+Fraction(1,10**18), cal['reference']['within_distance'], False),
                (boundary, cal['reference']['within_distance']*1.075+1e-10, False)]:
            m = dict(metrics, J1_exact=str(exact), J1=float(exact), within_distance=within)
            actual = self.scorer.balance(m, cal)
            self.assertEqual(actual['eligible'], eligible)
            self.assertEqual(actual['R'], relaxed_evaluate(m,cal)['R'])

    def test_normalization_malformed_and_cross_season_rejection(self):
        raw = self.submission()
        for key in raw['layout']:
            raw['layout'][key] = ['◌'+s if s in 'ািীুূৃেৈোৌ' else s for s in raw['layout'][key]]
        self.assertEqual(self.scorer.parse_layout(raw, self.data), shared_layout())
        for broken in [dict(raw, season='bangla-dh-challenge-v1'), dict(raw, style='A'),
                       dict(raw, layout={'Q':['ক','ক']})]:
            with self.assertRaises(ValueError): self.scorer.evaluate(broken,self.data)

    def test_board_duplicate_reference_status_and_dominance(self):
        parent=output_path(ROOT/'work/shared-publication-tests'); parent.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=parent) as temp:
            paths=[]
            alternative=self.submission()
            alternative['layout']['W'][1],alternative['layout']['X'][1]=alternative['layout']['X'][1],alternative['layout']['W'][1]
            for name, obj in [('reference',self.submission()),('alternative',alternative),('duplicate',alternative),
                              ('original',self.submission(mixed_best_layout('A'))),('wrong-season',dict(alternative,season='old'))]:
                paths.append(str(write_json(Path(temp)/(name+'.json'),obj)))
            board=shared_leaderboard.score_files(paths)
            entries={r['file']:r for r in board['entries']}
            self.assertEqual(entries['alternative.json']['status'],'frontier')
            self.assertEqual(entries['original.json']['status'],'ineligible')
            self.assertEqual(len(board['problems']),3)
            self.assertTrue(self.scorer.dominates([.1,.2],[.1,.3]))
            self.assertFalse(self.scorer.dominates([.1,.2],[.1,.2]))

    def test_equal_source_mean_and_tampered_data(self):
        self.assertEqual(self.scorer.mean([{'J1':1.,'J1_exact':'1'},{'J1':9.,'J1_exact':'9'}])['J1_exact'],'5')
        with patch.object(self.scorer,'EXPECTED_SHA256','0'*64):
            with self.assertRaisesRegex(ValueError,'hash mismatch'): self.scorer.load_data()

    def test_diagnostics_are_saved_only_to_a_new_repository_directory(self):
        parent=output_path(ROOT/'work/shared-diagnostic-tests'); parent.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=parent) as temp:
            file=write_json(Path(temp)/'reference with spaces.json',self.submission())
            out=Path(temp)/'diagnostics'
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(shared_challenge.verify([file], diagnostics=out),0)
                first=(out/'diagnostics.json').read_bytes()
                self.assertEqual(shared_challenge.verify([file], diagnostics=out),0)
                self.assertEqual((out/'diagnostics.json').read_bytes(),first)
            self.assertTrue((out/'run-manifest.json').is_file())

    def test_duplicate_json_keys_and_dominated_map(self):
        parent=output_path(ROOT/'work/shared-parser-tests'); parent.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=parent) as temp:
            path=Path(temp)/'duplicate.json'
            path.write_text('{"season":"a","season":"b"}',encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'given twice'): self.scorer.read_submission(path)
            raw=json.loads((ROOT/'results/shared-top10-comparison-v1/layouts/shared-1c797d59289ce714.json').read_text(encoding='utf-8'))
            layout={s:tuple(v.split('/')) for s,v in raw['layout'].items()}
            path=write_json(Path(temp)/'dominated.json',dict(self.submission(layout),name='[link](https://example.test) <script>'))
            board=shared_leaderboard.score_files([path])
            self.assertEqual(board['entries'][0]['status'],'dominated')
            rendered=shared_leaderboard.render(board)
            self.assertNotIn('<script>',rendered)
            self.assertIn('\\[link\\]',rendered)


if __name__ == '__main__':
    unittest.main()
