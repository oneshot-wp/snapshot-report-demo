import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from report import build_report


def post(**changes):
    row = dict(platform='demo-video', post_id='001',
               published_at='2026-10-26T10:00:00+08:00',
               observed_at='2026-11-01T12:00:00+08:00',
               views=100, likes=10, comments=2, shares=1)
    row.update(changes)
    return row


class ReportTests(unittest.TestCase):
    def test_latest_snapshot_deduplicates_without_double_counting(self):
        result = build_report([post(views=50, observed_at='2026-10-31T00:00:00+08:00'), post()], '2026-10-26')
        self.assertEqual(result['platforms'][0]['views'], 100)
        self.assertEqual(result['platforms'][0]['posts'], 1)
        self.assertEqual(result['duplicate_snapshots'], 1)

    def test_platform_is_part_of_identity(self):
        result = build_report([post(), post(platform='demo-notes')], '2026-10-26')
        self.assertEqual(len(result['platforms']), 2)

    def test_date_filter_uses_shanghai_half_open_week(self):
        result = build_report([post(published_at='2026-10-25T16:00:00Z'),
                               post(post_id='out', published_at='2026-11-01T16:00:00Z',
                                    observed_at='2026-11-02T01:00:00+08:00')], '2026-10-26')
        self.assertEqual(result['included_posts'], 1)

    def test_missing_metric_is_not_zero(self):
        result = build_report([post(), post(post_id='002', shares=None)], '2026-10-26')
        platform = result['platforms'][0]
        self.assertIsNone(platform['shares'])
        self.assertIsNone(platform['interaction_rate'])
        self.assertEqual(platform['metric_coverage']['shares'], '1/2')

    def test_zero_views_has_no_rate(self):
        self.assertIsNone(build_report([post(views=0)], '2026-10-26')['platforms'][0]['interaction_rate'])

    def test_invalid_metric_rejected(self):
        for value in [-1, True, '100', 1.2]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                build_report([post(views=value)], '2026-10-26')

    def test_conflicting_same_timestamp_rejected(self):
        with self.assertRaises(ValueError):
            build_report([post(), post(views=200)], '2026-10-26')

    def test_future_and_naive_observations_rejected(self):
        for changes in [dict(observed_at='2026-10-25T00:00:00+08:00'),
                        dict(observed_at='2026-11-01T00:00:00')]:
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                build_report([post(**changes)], '2026-10-26')

    def test_empty_input_valid(self):
        self.assertEqual(build_report([], '2026-10-26')['included_posts'], 0)

    def test_cli_generates_traceable_json_and_readable_report(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            source = folder / 'input.json'
            source.write_text(json.dumps([post()]), encoding='utf-8')
            process = subprocess.run([sys.executable, str(Path(__file__).with_name('report.py')),
                                      str(source), '--week', '2026-10-26', '--output', str(folder / 'out')],
                                     capture_output=True, text=True)
            self.assertEqual(process.returncode, 0, process.stderr)
            result = json.loads((folder / 'out' / 'report.json').read_text(encoding='utf-8'))
            self.assertEqual(result['records'][0]['post_id'], '001')
            self.assertIn('累计', (folder / 'out' / 'report.md').read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
