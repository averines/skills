"""Run: python -m unittest discover -s tests -v from the repository root."""
import importlib.util
import io
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest import mock


ROOT = Path(__file__).resolve().parents[1] / 'skills' / 'check-env'
HELPER = ROOT / 'check-python-packages.py'
spec = importlib.util.spec_from_file_location('check_python_packages', HELPER)
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)


class MetadataTests(unittest.TestCase):
    def test_reads_metadata_without_importing_distribution(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            info = root / 'fixture_av_check_env-1.2.3.dist-info'
            info.mkdir()
            (info / 'METADATA').write_text('Metadata-Version: 2.1\nName: fixture-av-check-env\nVersion: 1.2.3\n', encoding='utf-8')
            (root / 'fixture_av_check_env.py').write_text("raise RuntimeError('must not import')\n", encoding='utf-8')
            result = subprocess.run([sys.executable, str(HELPER), 'fixture-av-check-env'],
                                    capture_output=True, text=True, encoding='utf-8',
                                    env={**os.environ, 'PYTHONPATH': temporary})
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('[OK] fixture-av-check-env 1.2.3', result.stdout)
            self.assertIn(sys.executable, result.stdout)

    def test_missing_distribution_uses_environment_suggestion(self):
        result = subprocess.run([sys.executable, str(HELPER), 'av-check-env-nonexistent-fixture-987654321'],
                                capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('[MISSING]', result.stdout)
        self.assertIn('-m pip install', result.stdout)
        self.assertNotIn('--break-system-packages', result.stdout)

    def test_metadata_failure_is_unknown_not_missing(self):
        output = io.StringIO()
        with mock.patch.object(sys, 'argv', ['helper', 'fixture']), \
             mock.patch('importlib.metadata.version', side_effect=RuntimeError('fixture')), \
             redirect_stdout(output):
            self.assertEqual(helper.main(), 0)
        self.assertIn('[UNKNOWN] fixture', output.getvalue())
        self.assertNotIn('[MISSING]', output.getvalue())

    def test_invalid_package_name_does_not_produce_shell_command(self):
        result = subprocess.run([sys.executable, str(HELPER), 'pkg;echo unsafe'],
                                capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(result.returncode, 2)
        self.assertNotIn('pip install', result.stdout)


@unittest.skipUnless(os.name == 'nt', 'PowerShell command fixtures require Windows')
class PowerShellTests(unittest.TestCase):
    def test_missing_failed_and_application_probes_in_both_shells(self):
        shells = [path for path in (shutil.which('powershell'), shutil.which('pwsh')) if path]
        self.assertTrue(shells)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name, contents in {
                'git': '@echo fixture-git\n@exit /b 0\n',
                'node': '@echo version-failed 1>&2\n@exit /b 7\n',
                'curl': '@echo fixture-curl-application\n@exit /b 0\n',
            }.items():
                (root / (name + '.cmd')).write_text(contents, encoding='ascii')
            for shell in shells:
                with self.subTest(shell=shell):
                    result = subprocess.run([
                        shell, '-NoProfile', '-File', str(ROOT / 'check-packages.ps1'),
                        '-SkipPythonPackages',
                    ], capture_output=True, text=True, timeout=30,
                       env={**os.environ, 'PATH': temporary})
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertIn('[OK] git fixture-git', result.stdout)
                    self.assertIn('[OK] curl fixture-curl-application', result.stdout)
                    self.assertIn('[UNKNOWN] node', result.stdout)
                    self.assertIn('[MISSING] jq', result.stdout)
                    self.assertIn('[MISSING] Python executable not found.', result.stdout)
                    self.assertNotIn('Press Enter', result.stdout)


if __name__ == '__main__':
    unittest.main()
