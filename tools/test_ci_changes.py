# SPDX-License-Identifier: GPL-3.0-only
"""Test the selector extracted from the workflow, without running event handling."""
import ast
import os
import subprocess
import sys
import tempfile
from pathlib import Path
import textwrap
import unittest


workflow = (Path(__file__).resolve().parents[1] / '.github/workflows/ci.yml').read_text(encoding='utf-8')
inline = textwrap.dedent(workflow.split("python -I -B - <<'PY'\n", 1)[1].split('\n          PY', 1)[0])
selector = next(node for node in ast.parse(inline).body
                if isinstance(node, ast.FunctionDef) and node.name == 'select_checks')
namespace = {}
exec(compile(ast.Module(body=[selector], type_ignores=[]), '<CI selector>', 'exec'), namespace)
select_checks = namespace['select_checks']


class ChangeSelectionTests(unittest.TestCase):
    def test_selection(self):
        cases = [
            ('LICENSE', (False, False, True, False)),
            ('assets/example.png', (False, False, True, False)),
            ('README.md', (False, False, True, False)),
            ('docs/law-index.json', (False, True, True, False)),
            ('docs/graph.json', (False, False, True, False)),
            ('tools/test_ci_changes.py', (False, False, True, True)),
            ('tools/split_standard.py', (True, True, True, True)),
            ('sources/laws/example.json', (True, True, True, True)),
            ('sources/laws/public-works-acts/versions/pw028.json', (True, True, True, True)),
            ('.github/workflows/ci.yml', (True, True, True, True)),
        ]
        for path, expected in cases:
            with self.subTest(path=path):
                flags, _ = select_checks([path])
                self.assertEqual(tuple(flags.values()), expected)

    def test_manual_fallback(self):
        flags, _ = select_checks([], 'manual run')
        self.assertTrue(all(flags.values()))

    def test_no_changes(self):
        flags, _ = select_checks([])
        self.assertFalse(any(flags.values()))

    def test_missing_base_selects_all(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'tools').mkdir()
            (root / 'tools/ci_base.sh').write_text(
                (Path(__file__).parent / 'ci_base.sh').read_text())
            subprocess.run(['git', 'init', '-q', str(root)], check=True)
            for event in ('push', 'pull_request'):
                with self.subTest(event=event):
                    output = root / f'{event}-output'
                    result = subprocess.run([sys.executable, '-I', '-B', '-c', inline], cwd=root,
                        env={**os.environ, 'CI_EVENT': event, 'CI_BASE': 'f' * 40, 'CI_BEFORE': 'f' * 40,
                             'GITHUB_OUTPUT': str(output),
                             'GITHUB_STEP_SUMMARY': str(root / 'summary')},
                        capture_output=True, text=True)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    flags = dict(line.split('=') for line in output.read_text().splitlines())
                    flags.pop('whitespace_base')
                    self.assertEqual(flags, dict.fromkeys(
                        ('standards', 'laws', 'validation', 'tests'), 'true'))
