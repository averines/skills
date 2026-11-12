"""Run: python -m unittest discover -s tests -v from the repository root."""

import datetime as dt
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / 'skills' / 'timespent' / 'timespent.py'
spec = importlib.util.spec_from_file_location('timespent', SCRIPT)
ts = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ts)


class TimespentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def run_cli(self, *arguments, ok=True):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), '--repo', str(self.root), *map(str, arguments)],
            capture_output=True, text=True, encoding='utf-8',
            env={**os.environ, 'PYTHONUTF8': '1'},
        )
        if ok:
            self.assertEqual(result.returncode, 0, result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0)
            self.assertNotIn('Traceback', result.stderr)
        return result

    def write_events(self, rows, name='activity.jsonl'):
        path = self.root / name
        path.write_text('\n'.join(json.dumps(row) for row in rows) + '\n', encoding='utf-8')
        return path

    def event(self, identity, timestamp='2026-11-12T10:00:00+00:00', **changes):
        return {'id': identity, 'timestamp': timestamp, 'role': 'user', 'chars': 42, **changes}

    def git(self, *arguments, env=None):
        result = subprocess.run(['git', '-C', str(self.root), *arguments], capture_output=True,
                                text=True, encoding='utf-8', env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result

    def make_repo(self):
        self.git('init', '-q')
        self.git('config', 'user.name', 'Fixture')
        self.git('config', 'user.email', 'fixture@example.invalid')
        for number, author in enumerate(('Author[one]', 'Other')):
            stamp = f'2026-11-12T10:{number * 20:02d}:00+00:00'
            env = {**os.environ, 'GIT_AUTHOR_NAME': author,
                   'GIT_AUTHOR_DATE': stamp, 'GIT_COMMITTER_DATE': stamp}
            self.git('commit', '-q', '--allow-empty', '-m', f'fixture {number}', env=env)

    def test_git_only_parameters_and_html_match_total(self):
        self.make_repo()
        output, html = self.root / 'report.json', self.root / 'report.html'
        self.run_cli('--cap', 1, '--lead', 2, '--tail', 3, '--gap', 90,
                     '--json', output, '--html', html)
        report = json.loads(output.read_text(encoding='utf-8'))
        self.assertAlmostEqual(report['hours'], 6 / 60)
        self.assertAlmostEqual(sum(report['session_hours']), report['hours'])
        self.assertEqual(report['commits'], 2)
        self.assertEqual(report['messages'], 0)
        self.assertTrue(any('Git-only' in item for item in report['caveats']))
        page = html.read_text(encoding='utf-8')
        self.assertIn('longer than 90 min', page)
        self.assertIn('up to 1 min', page)
        self.assertIn('Add 2 min before and 3 min', page)

    def test_author_filter_is_literal(self):
        self.make_repo()
        output = self.root / 'one.json'
        self.run_cli('--author', 'Author[one]', '--json', output)
        report = json.loads(output.read_text(encoding='utf-8'))
        self.assertEqual(report['commits'], 1)
        self.assertEqual(report['authors'], [['Author[one]', 1]])

    def test_activity_only_and_repeated_exports(self):
        events = self.write_events([
            self.event('source:1', text='PRIVATE_MESSAGE', chars=15),
            self.event('source:2', '2026-11-12T10:20:00+00:00'),
            {'role': 'assistant', 'text': 'not a human event'},
            {'role': 'tool'},
        ])
        output, html = self.root / 'events.json', self.root / 'events.html'
        self.run_cli('--no-git', '--activity', events, '--activity', events,
                     '--lead', 0, '--tail', 0, '--cap', 10, '--json', output, '--html', html)
        report = json.loads(output.read_text(encoding='utf-8'))
        self.assertEqual(report['messages'], 2)
        self.assertEqual(report['chars'], 57)
        self.assertEqual(report['sessions'], 1)
        self.assertAlmostEqual(report['hours'], 10 / 60)
        self.assertNotIn('PRIVATE_MESSAGE', output.read_text(encoding='utf-8'))
        self.assertNotIn('PRIVATE_MESSAGE', html.read_text(encoding='utf-8'))

    def test_conflicting_duplicate_fails(self):
        events = self.write_events([self.event('source:1'), self.event('source:1', chars=43)])
        result = self.run_cli('--no-git', '--activity', events, ok=False)
        self.assertIn('conflicting duplicate id', result.stderr)

    def test_malformed_inputs_fail_instead_of_silently_undercounting(self):
        for number, row in enumerate((
            self.event('source:1', timestamp='2026-11-12T10:00:00'),
            self.event('source:1', chars=True),
            self.event('source:1', chars=-1),
            self.event('source:1', text='private', chars=99),
            self.event('', chars=0),
            {'type': 'user', 'timestamp': '2026-11-12T10:00:00Z'},
            ['not an object'],
        )):
            with self.subTest(number=number):
                events = self.write_events([row], f'bad-{number}.jsonl')
                result = self.run_cli('--no-git', '--activity', events, ok=False)
                self.assertIn(f'{events}:1:', result.stderr)
        bad_json = self.root / 'bad.jsonl'
        bad_json.write_text('{invalid json}', encoding='utf-8')
        self.assertIn('invalid JSON', self.run_cli('--no-git', '--activity', bad_json, ok=False).stderr)

    def test_missing_input_and_empty_activity_fail(self):
        self.run_cli('--no-git', '--activity', self.root / 'missing.jsonl', ok=False)
        self.run_cli('--no-git', ok=False)

    def test_invalid_model_parameters_fail(self):
        for option, value in (('--gap', 0), ('--cap', -1), ('--lead', -1), ('--tail', -1)):
            with self.subTest(option=option):
                self.run_cli('--no-git', option, value, ok=False)

    def test_midnight_splits_minutes_without_splitting_session(self):
        start = dt.datetime(2026, 11, 12, 23, 50).astimezone()
        end = dt.datetime(2026, 11, 13, 0, 10).astimezone()
        sessions = ts.sessionize([start, end], 180)
        self.assertEqual(len(sessions), 1)
        daily = ts.minutes_by_day(sessions, 30, 0, 0)
        self.assertAlmostEqual(daily[start.date()], 10)
        self.assertAlmostEqual(daily[end.date()], 10)

    def test_session_edges_cross_midnight(self):
        moment = dt.datetime(2026, 11, 13, 0, 5).astimezone()
        daily = ts.minutes_by_day([[moment]], 30, 10, 0)
        self.assertAlmostEqual(daily[dt.date(2026, 11, 12)], 5)
        self.assertAlmostEqual(daily[dt.date(2026, 11, 13)], 5)

    def test_overlapping_session_edges_are_not_counted_twice(self):
        start = dt.datetime(2026, 11, 12, 10).astimezone()
        sessions = ts.sessionize([start, start + dt.timedelta(minutes=20)], 10)
        self.assertEqual(len(sessions), 2)
        self.assertAlmostEqual(ts.total_hours(sessions, 30, 15, 15), 50 / 60)

    def test_existing_output_is_preserved(self):
        events = self.write_events([self.event('source:1')])
        output = self.root / 'existing.json'
        output.write_text('KEEP', encoding='utf-8')
        self.run_cli('--no-git', '--activity', events, '--json', output, ok=False)
        self.assertEqual(output.read_text(encoding='utf-8'), 'KEEP')

    def test_zero_minutes_is_valid(self):
        events = self.write_events([self.event('source:1')])
        output = self.root / 'zero.json'
        self.run_cli('--no-git', '--activity', events, '--lead', 0, '--tail', 0,
                     '--cap', 0, '--json', output, '--html', self.root / 'zero.html')
        self.assertEqual(json.loads(output.read_text(encoding='utf-8'))['hours'], 0)

    def test_redirected_output_is_utf8_with_legacy_python_defaults(self):
        environment = {**os.environ, 'PYTHONIOENCODING': 'cp1251', 'PYTHONUTF8': '0'}
        help_result = subprocess.run([sys.executable, str(SCRIPT), '--help'],
                                     capture_output=True, text=True, encoding='utf-8', env=environment)
        self.assertEqual(help_result.returncode, 0, help_result.stderr)
        self.assertIn('Estimate work time from Git', help_result.stdout)
        error_result = subprocess.run([sys.executable, str(SCRIPT), '--gap', '0'],
                                      capture_output=True, text=True, encoding='utf-8', env=environment)
        self.assertNotEqual(error_result.returncode, 0)
        self.assertIn('must be positive', error_result.stderr)


if __name__ == '__main__':
    unittest.main()
