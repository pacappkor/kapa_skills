# SPDX-License-Identifier: GPL-3.0-only
"""Normal and empty-tree diffs exclude verbatim artifacts, not authored files."""
from pathlib import Path
import os
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).with_name('ci_whitespace.sh')


class WhitespaceTests(unittest.TestCase):
    def test_empty_tree_checks_authored_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)

            def git(*args):
                return subprocess.check_output(['git', *args], cwd=root, input=b'').decode().strip()

            git('init', '-q')
            git('config', 'user.email', 'test@example.invalid')
            git('config', 'user.name', 'CI test')
            git('config', 'core.autocrlf', 'false')
            readme = root / 'README.md'
            readme.write_text('clean\n', encoding='utf-8', newline='')
            git('add', '.')
            git('commit', '-qm', 'clean fixture')
            empty = git('hash-object', '-t', 'tree', '--stdin')

            def check(base):
                return subprocess.run(['bash', str(SCRIPT), base], cwd=root,
                                      capture_output=True, text=True)

            clean = check(empty)
            self.assertEqual(clean.returncode, 0, clean.stdout + clean.stderr)
            readme.write_text('bad  \n', encoding='utf-8', newline='')
            git('add', '.')
            git('commit', '-qm', 'bad authored fixture')
            result = check(empty)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('README.md', result.stdout)
            skipped = check(git('rev-parse', 'HEAD'))
            self.assertEqual(skipped.returncode, 0)
            self.assertIn('Whitespace check skipped', skipped.stdout)


    def test_empty_tree_checks_authored_annex_markdown(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)

            def git(*args):
                return subprocess.check_output(['git', *args], cwd=root, input=b'').decode().strip()

            git('init', '-q')
            git('config', 'user.email', 'test@example.invalid')
            git('config', 'user.name', 'CI test')
            git('config', 'core.autocrlf', 'false')
            readme = root / 'sources/laws/example/annex-md/example.md'
            readme.parent.mkdir(parents=True)
            raw = root / 'sources/laws/example/annex/example.txt'
            raw.parent.mkdir(parents=True)
            raw.write_text('verbatim  \n', encoding='utf-8', newline='')
            readme.write_text('clean\n', encoding='utf-8', newline='')
            git('add', '.')
            git('commit', '-qm', 'clean fixture')
            empty = git('hash-object', '-t', 'tree', '--stdin')

            def check(base):
                return subprocess.run(['bash', str(SCRIPT), base], cwd=root,
                                      capture_output=True, text=True)

            clean = check(empty)
            self.assertEqual(clean.returncode, 0, clean.stdout + clean.stderr)
            readme.write_text('bad  \n', encoding='utf-8', newline='')
            git('add', '.')
            git('commit', '-qm', 'bad authored fixture')
            result = check(empty)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('sources/laws/example/annex-md/example.md', result.stdout)
            skipped = check(git('rev-parse', 'HEAD'))
            self.assertEqual(skipped.returncode, 0)
            self.assertIn('Whitespace check skipped', skipped.stdout)

    def test_normal_diff_allows_generated_hard_breaks_but_checks_authored(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)

            def git(*args):
                return subprocess.check_output(['git', *args], cwd=root).decode().strip()

            git('init', '-q')
            git('config', 'user.email', 'test@example.invalid')
            git('config', 'user.name', 'CI test')
            git('config', 'core.autocrlf', 'false')
            (root / 'README.md').write_text('clean\n', encoding='utf-8')
            git('add', '.')
            git('commit', '-qm', 'base fixture')
            base = git('rev-parse', 'HEAD')
            generated = root / 'practice/topic/source.md'
            generated.parent.mkdir(parents=True)
            generated.write_text('source: updated NOTICE  \n', encoding='utf-8')
            git('add', '.')
            git('commit', '-qm', 'generated hard break fixture')
            result = subprocess.run(['bash', str(SCRIPT), base], cwd=root,
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            (root / 'README.md').write_text('authored bad  \n', encoding='utf-8')
            git('add', '.')
            git('commit', '-qm', 'authored whitespace fixture')
            result = subprocess.run(['bash', str(SCRIPT), base], cwd=root,
                                    capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('README.md', result.stdout)

    def test_verbatim_annex_exclusion_preserves_authored_checks(self):
        for comparison in ('normal', 'empty-tree'):
            for authored_path in ('sources/laws/example/annex-md/example.md',
                                  'laws/example/topic/SKILL.md'):
                with self.subTest(comparison=comparison, authored_path=authored_path):
                    with tempfile.TemporaryDirectory() as directory:
                        root = Path(directory)

                        def git(*args):
                            return subprocess.check_output(
                                ['git', *args], cwd=root, input=b'').decode().strip()

                        git('init', '-q')
                        git('config', 'user.email', 'test@example.invalid')
                        git('config', 'user.name', 'CI test')
                        git('config', 'core.autocrlf', 'false')
                        (root / 'README.md').write_text('clean\n', encoding='utf-8', newline='')
                        git('add', '.')
                        git('commit', '-qm', 'base fixture')
                        base = (git('rev-parse', 'HEAD') if comparison == 'normal'
                                else git('hash-object', '-t', 'tree', '--stdin'))
                        raw = root / 'sources/laws/example/annex/example.txt'
                        raw.parent.mkdir(parents=True)
                        raw.write_text('verbatim  \n', encoding='utf-8', newline='')
                        git('add', '.')
                        git('commit', '-qm', 'new raw annex fixture')
                        result = subprocess.run(['bash', str(SCRIPT), base], cwd=root,
                                                capture_output=True, text=True)
                        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

                        authored = root / authored_path
                        authored.parent.mkdir(parents=True, exist_ok=True)
                        authored.write_text('authored bad  \n', encoding='utf-8', newline='')
                        git('add', '.')
                        git('commit', '-qm', 'authored whitespace fixture')
                        result = subprocess.run(['bash', str(SCRIPT), base], cwd=root,
                                                capture_output=True, text=True)
                        self.assertNotEqual(result.returncode, 0)
                        self.assertIn(authored_path, result.stdout)


if __name__ == '__main__':
    unittest.main()
