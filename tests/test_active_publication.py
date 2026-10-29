"""Current defaults cannot silently select the historical shared problem."""
import contextlib
import io
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from bangla_dh.cli import build_parser
from bangla_dh.goti_evidence import verify
from bangla_dh.paths import PROJECT_ROOT as ROOT
from bangla_dh.publication import active_descriptor, current_layout
from bangla_dh.mix import mixed_best_layout


class ActivePublicationTests(unittest.TestCase):
    def test_all_publication_commands_default_to_frozen_original_j1(self):
        parser = build_parser()
        for command in ('challenge-kit', 'kala-export', 'leaderboard', 'challenge-verify'):
            args = [command] + (['challenge/A-reference.json'] if command == 'challenge-verify' else [])
            self.assertEqual(parser.parse_args(args).season, 'legacy-v1')
            self.assertEqual(parser.parse_args(args + ['--season', 'shared-v1']).season, 'shared-v1')
        spec = active_descriptor()
        self.assertEqual(spec['season'], 'legacy-v1')
        self.assertEqual(spec['styles']['A']['arrangement_id'], 'A-18fe73cb912ae3f1')
        self.assertEqual(spec['styles']['D']['arrangement_id'], 'D-e4a6be48881da590')
        for style in ('A', 'D'):
            self.assertEqual(current_layout(style), mixed_best_layout(style))
        self.assertNotEqual(current_layout('A'), current_layout('D'))

    def test_archived_search_verifies_without_reading_any_ignored_work_file(self):
        read_bytes = Path.read_bytes
        def tracked_only(path):
            self.assertFalse(path.resolve().is_relative_to((ROOT / 'work').resolve()), str(path))
            return read_bytes(path)
        with patch.object(Path, 'read_bytes', tracked_only), contextlib.redirect_stdout(io.StringIO()) as result:
            verify()
        summary = json.loads(result.getvalue())
        self.assertEqual((summary['starts'], summary['endpoints'], summary['hits'], summary['assignments']),
                         (8000, 241, 514, 52))
