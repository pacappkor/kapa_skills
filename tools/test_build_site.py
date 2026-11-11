# SPDX-License-Identifier: GPL-3.0-only
"""Small offline fixtures for the site staging contract."""
import contextlib
import io
import json
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch

from tools import build_site as site
from tools import graph, site_hooks, validate
from types import SimpleNamespace


class SiteTests(unittest.TestCase):
    def test_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'tool.py').write_text('# code', encoding='utf-8')
            pages = {Path('a/SKILL.md'): Path('a/SKILL.md'),
                     Path('README.md'): Path('overview.md'),
                     Path('b'): Path('b/index.md')}
            errors = []
            text = ('[home](../README.md#title) [dir](../b/)\n'
                    '[ref]: ../README.md "Title"\n'
                    '<a href="../README.md">home</a>\n\n'
                    '[tool](../tool.py) [web](https://example.org/a)\n'
                    '`[example](missing.md)`\n```md\n[x](missing.md)\n```\n')
            result = site.rewrite_links(text, Path('a/SKILL.md'), root, pages,
                                        {Path('tool.py')}, errors)
            self.assertFalse(errors)
            self.assertIn('../overview.md#title', result)
            self.assertIn('../b/index.md', result)
            self.assertIn('[ref]: ../overview.md "Title"', result)
            self.assertIn('href="../overview.md"', result)
            self.assertIn(site.REPO + '/blob/main/tool.py', result)
            self.assertIn('`[example](missing.md)`', result)

    def test_disposable_skill_copies_are_excluded(self):
        self.assertIn('.site-src', graph.SKIP)
        self.assertIn('.site-src', validate.SKIP)
        self.assertIn('site', validate.BUILD_DIRS)

    def test_edit_links(self):
        config = {'repo_url': site.REPO}
        page = SimpleNamespace(meta={'edit_uri': 'README.md'}, edit_url='incorrect')
        site_hooks.on_page_context({}, page, config, None)
        self.assertEqual(page.edit_url, site.REPO + '/edit/main/README.md')
        page.meta['edit_uri'] = ''
        site_hooks.on_page_context({}, page, config, None)
        self.assertIsNone(page.edit_url)

    def test_broken_links(self):
        errors = []
        site.rewrite_links('[bad](missing.md) [escape](../../outside.md)',
                           Path('a/SKILL.md'), Path('.'), {}, set(), errors)
        self.assertEqual(len(errors), 2)
        self.assertIn('missing target', errors[0])
        self.assertIn('outside repository', errors[1])

    def test_indexes(self):
        skills = site.skill_index([Path('laws/example/topic/SKILL.md'),
                                   Path('rules/read/SKILL.md')])
        self.assertIn('## laws/example', skills)
        self.assertIn('[topic](laws/example/topic/SKILL.md)', skills)
        index = site.law_index({
            'laws': {'1': {'name': '법', 'collection': 'example',
                           'current': {'lsiSeq': '99', 'efYd': '20260101'}}},
            'articles': {'law/1@99#a1': {'title': '목적', 'deleted': False,
                                        'skill': 'laws/example/topic/SKILL.md'}},
            'standards': {'apps@9#100': {'title': '총칙', 'skill': 'standard/SKILL.md'}}})
        self.assertIn('lsiSeq=99', index)
        self.assertIn('시행일: 20260101', index)
        self.assertIn('[a1 목적](laws/example/topic/SKILL.md)', index)
        self.assertIn('[100 총칙](standard/SKILL.md)', index)

    def test_staging_strict_and_related(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            files = {'README.md': '# Home\n[bad](missing.md)\n',
                     '00-kapa-start/SKILL.md': '# Start\n',
                     'rules/skill-reading-rules/SKILL.md': '# Rules\n',
                     'NOTICE.md': '# Notice\n',
                     'docs/graph.json': json.dumps([{'src': '00-kapa-start',
                                                      'dst': 'skill-reading-rules'}]),
                     'docs/law-index.json': json.dumps({'laws': {}, 'articles': {}, 'standards': {}})}
            for name, text in files.items():
                p = root / name
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(text, encoding='utf-8')
            tracked = {Path(p) for p in files}
            with patch.object(site, 'tracked_files', return_value=tracked), contextlib.redirect_stdout(io.StringIO()):
                with self.assertRaisesRegex(ValueError, 'broken local links'):
                    site.build(root, strict=True)
                self.assertFalse((root / '.site-src').exists())
                (root / 'README.md').write_text('# Home\n', encoding='utf-8')
                count, errors = site.build(root, strict=True)
            self.assertFalse(errors)
            self.assertGreater(count, 4)
            staged = root / '.site-src'
            self.assertIn('관련 스킬', (staged / '00-kapa-start/SKILL.md').read_text(encoding='utf-8'))
            self.assertIn('edit_uri: README.md', (staged / 'overview.md').read_text(encoding='utf-8'))
            self.assertIn('[저장소 안내](overview.md)', (staged / 'index.md').read_text(encoding='utf-8'))
            self.assertEqual((root / 'README.md').read_text(encoding='utf-8'), '# Home\n')
            with self.assertRaises(ValueError):
                site.build(root, root / 'canonical', strict=True)


class PagesWorkflowTests(unittest.TestCase):
    def test_action_pins_and_permissions(self):
        root = Path(__file__).resolve().parents[1]
        workflow = (root / '.github/workflows/pages.yml').read_text(encoding='utf-8')
        actions = re.findall(r'uses: (actions/[\w-]+)@([^\s]+) # (v[\d.]+)', workflow)
        self.assertEqual(len(actions), 5)
        for _, sha, _ in actions:
            self.assertRegex(sha, r'^[0-9a-f]{40}$')
        build, deploy = workflow.split('  deploy:\n')
        self.assertNotIn('pages: write', build)
        self.assertNotIn('id-token: write', build)
        self.assertIn('pages: write', deploy)
        self.assertIn('id-token: write', deploy)
        self.assertIn('group: pages', workflow)
        self.assertIn('branches: [main]', workflow)
        self.assertIn('workflow_dispatch:', workflow)
        self.assertIn('mkdocs build --strict', build)
        ci = (root / '.github/workflows/ci.yml').read_text(encoding='utf-8')
        self.assertIn('  offline-checks:', ci)
        self.assertIn('  docs-build:', ci)
        self.assertIn('mkdocs build --strict', ci)


if __name__ == '__main__':
    unittest.main()
