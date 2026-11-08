#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Offline regression tests for histories, date selection, and Markdown prose."""
import datetime, io, json, pathlib, sys, tempfile, unittest
from unittest.mock import patch
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import fetch_version
import fetch_versions
from fetch_versions import parse_history
from fetch_version import choose
import lawgo
import build_index
import fetch_laws
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from markdown_prose import normalize


class Output(io.StringIO):
    def reconfigure(self, **kwargs):
        pass


def item(seq, anc, ef, name):
    return f"<li><a onclick=\"lsViewLsHst2('{seq}', '{anc}', '00100', '{ef}', 'N', '0', '일부개정')\"><b>1. {name}</b></a></li>"


class VersionsTest(unittest.TestCase):
    def test_status_and_english(self):
        page = item('4', '20260101', '20270101', '새 법') + item('3', '20250101', '20260101', '새 법') + item('2', '20200101', '20200101', '새법') + item('1', '19900101', '19900101', '옛법')
        page += "<li><a onclick=\"lsViewEngLsHst('8', '010203')\"><b>영문</b></a></li>"
        rows = parse_history(page, '새 법', '3', '20261108')
        self.assertEqual([v['status'] for v in rows], ['scheduled', 'current', 'past', 'predecessor'])
        self.assertEqual(choose(rows, '20210101')['lsiSeq'], '2')
        self.assertEqual(choose(rows, '19900101')['lsiSeq'], '1')
        with self.assertRaises(ValueError):
            choose(rows, '19800101')
        with self.assertRaises(ValueError):
            parse_history(page, '다른 법', '3', '20261108')

    def test_staggered_snapshots_and_addenda(self):
        rows = [dict(lsiSeq='7', efYd=ef, ancYd='20200101', ancNo='1', name='법')
                for ef in ('20200101', '20210101')]
        with self.assertRaises(ValueError):
            fetch_version.select(rows, '7')
        with self.assertRaises(ValueError):
            fetch_version.select(rows, '7', '19990101')
        self.assertEqual(fetch_version.select(rows[:1], '7'), rows[0])
        self.assertEqual(choose(rows, '20200601'), rows[0])
        self.assertEqual(choose(rows, '20210601'), rows[1])
        body = dict(headings=[], articles=[], annexes=[], addenda=['부칙 경과조치'])
        with tempfile.TemporaryDirectory() as tmp:
            src = pathlib.Path(tmp)
            base = src / 'test' / 'versions'
            base.mkdir(parents=True)
            (base / 'act.json').write_text(json.dumps(dict(versions=rows)), encoding='utf-8')
            (src / 'test' / 'act.json').write_text('{}', encoding='utf-8')
            cat = dict(collections=[dict(id='test', docs=[dict(level='act', label='법')])])
            with patch.object(fetch_version, 'SRC', src), patch.object(fetch_version, 'CAT', cat), \
                 patch.object(lawgo, 'fetch_body', return_value='page') as fetch, \
                 patch.object(lawgo, 'verify_body') as verify, patch.object(lawgo, 'parse', return_value=body), \
                 patch.object(lawgo, 'hidden', return_value='009471'), patch('sys.stdout', Output()):
                for ef in ('2020-01-01', '2021-01-01'):
                    with patch.object(sys, 'argv', ['fetch_version', 'test', 'act', '7', '--ef', ef]):
                        self.assertEqual(fetch_version.main(), 0)
                self.assertEqual(fetch.call_args_list[0].args, ('7', '20200101'))
                self.assertEqual(fetch.call_args_list[1].args, ('7', '20210101'))
                self.assertEqual(verify.call_args_list[1].args, ('page', '법', '7', '20210101'))
                saved = {p: p.read_bytes() for p in base.rglob('*.json')}
                verify.side_effect = ValueError('시행일 efYd 불일치')
                with patch.object(sys, 'argv', ['fetch_version', 'test', 'act', '7', '--ef', '2021-01-01']), \
                     patch('sys.stderr', Output()):
                    self.assertEqual(fetch_version.main(), 1)
                self.assertEqual({p: p.read_bytes() for p in base.rglob('*.json')}, saved)
            for row in rows:
                data = json.loads((base / 'act' / f"7-{row['efYd']}.json").read_text(encoding='utf-8'))
                self.assertEqual(data['efYd'], row['efYd'])
                self.assertEqual(data['addenda'], body['addenda'])

    def test_store_whole_repeal(self):
        row = dict(lsiSeq='7', efYd='20270909', ancYd='20260908', ancNo='1',
                   name='시험 법', kind='타법폐지')
        identity = ('<input id="lsNm" value="시험 법"><input id="lsiSeq" value="7">'
                    '<input id="efYd" value="20270909"><input id="lsId" value="000001">')
        sentence = '「시험 법」을 폐지한다.'
        addenda = '<div id="arDivArea"><p class="pty3_dep1">' + sentence + '</p></div>'
        with tempfile.TemporaryDirectory() as tmp:
            src = pathlib.Path(tmp)
            base = src / 'test' / 'versions'
            base.mkdir(parents=True)
            history = base / 'act.json'
            (src / 'test' / 'act.json').write_text('{}', encoding='utf-8')
            cat = dict(collections=[dict(id='test', docs=[dict(level='act', label='법')])])
            output = base / 'act' / '7-20270909.json'
            cases = [
                ('타법폐지', identity + addenda, True),
                ('폐지', identity + addenda.replace('」을', '」를'), True),
                ('타법폐지', identity, False),
                ('일부개정', identity + addenda, False),
                ('폐지제정', identity + addenda, False),
                ('타법폐지', (identity + addenda).replace('value="시험 법"', 'value="다른 법"'), False),
                ('타법폐지', (identity + addenda).replace('value="7"', 'value="8"'), False),
                ('타법폐지', (identity + addenda).replace('value="20270909"', 'value="20270910"'), False),
                ('타법폐지', identity + addenda.replace(sentence, '「다른 법」을 폐지한다.'), False),
                ('타법폐지', identity + addenda.replace(sentence, '<script>' + sentence + '</script>'), False),
                ('타법폐지', identity + '<p class="pty3_dep1">' + sentence + '</p>', False),
                ('타법폐지', identity + addenda.replace('폐지한다.', '폐지한다는 뜻이다.'), False),
            ]
            with patch.object(fetch_version, 'SRC', src), patch.object(fetch_version, 'CAT', cat), \
                 patch.object(sys, 'argv', ['fetch_version', 'test', 'act', '7', '--ef', '2027-09-09']), \
                 patch('sys.stdout', Output()), patch('sys.stderr', Output()):
                for kind, page, accepted in cases:
                    with self.subTest(kind=kind, page=page):
                        history.write_text(json.dumps(dict(versions=[dict(row, kind=kind)])), encoding='utf-8')
                        before = output.read_bytes() if output.exists() else None
                        with patch.object(lawgo, 'fetch_body', return_value=page):
                            self.assertEqual(fetch_version.main(), 0 if accepted else 1)
                        if accepted:
                            saved = json.loads(output.read_text(encoding='utf-8'))
                            self.assertEqual(saved['articles'], [])
                            self.assertIn('폐지한다.', saved['addenda'])
                            self.assertEqual((saved['lsiSeq'], saved['efYd']), ('7', '20270909'))
                        else:
                            self.assertEqual(output.read_bytes() if output.exists() else None, before)
            # The shared verifier must still reject article-less bodies.
            with self.assertRaisesRegex(ValueError, '조문 없음'):
                lawgo.verify_body(identity + addenda, row['name'], row['lsiSeq'], row['efYd'])

    def test_check_scheduled_exit_status(self):
        page = item('7', '20200101', '20990101', '새 법') + item('6', '20200101', '20200101', '법')
        rows = parse_history(page, '법', '6')
        with tempfile.TemporaryDirectory() as tmp:
            src = pathlib.Path(tmp)
            base = src / 'test' / 'versions'
            base.mkdir(parents=True)
            history = base / 'act.json'
            history.write_text(json.dumps(dict(lsId='009471', versions=rows)), encoding='utf-8')
            man = src / 'manifest.json'
            man.write_text(json.dumps({'test/act': dict(lsiSeq='6', efYd='20200101')}), encoding='utf-8')
            cat = dict(collections=[dict(id='test', docs=[dict(level='act', name='법')])])
            before = history.read_bytes(), man.read_bytes()
            output = Output()
            with patch.object(fetch_versions, 'SRC', src), patch.object(fetch_versions, 'MAN', man), \
                 patch.object(fetch_versions, 'CAT', cat), patch.object(lawgo, 'fetch_body', return_value='body'), \
                 patch.object(lawgo, 'verify_body'), patch.object(lawgo, 'hidden', return_value='009471'), \
                 patch.object(lawgo, '_get', return_value=page.encode()), patch.object(fetch_versions.time, 'sleep'), \
                 patch.object(sys, 'argv', ['fetch_versions', '--check']), patch('sys.stdout', output):
                self.assertEqual(fetch_versions.main(), 0)
                self.assertIn('SCHEDULED test/act 7', output.getvalue())
                self.assertEqual((history.read_bytes(), man.read_bytes()), before)
                truncated = page.replace('새 법', '새...').replace('1. 법', '1. 법...')
                with patch.object(lawgo, '_get', return_value=truncated.encode()), \
                     patch.object(fetch_versions, 'resolve_title') as resolve:
                    self.assertEqual(fetch_versions.main(), 0)
                    resolve.assert_not_called()
                    with patch.object(sys, 'argv', ['fetch_versions']):
                        self.assertEqual(fetch_versions.main(), 0)
                    resolve.assert_not_called()
                changed = truncated.replace('00100', '00200')
                with patch.object(lawgo, '_get', return_value=changed.encode()), \
                     patch.object(fetch_versions, 'resolve_title', side_effect=['새 법', '법']) as resolve:
                    self.assertEqual(fetch_versions.main(), 1)
                    self.assertEqual(resolve.call_count, 2)
                    self.assertIn('CHANGED test/act', output.getvalue())
                history.write_text('{}', encoding='utf-8')
                self.assertEqual(fetch_versions.main(), 1)
                with patch.object(lawgo, 'fetch_body', side_effect=ValueError('failure')):
                    self.assertEqual(fetch_versions.main(), 1)

    def test_inline_triple_backticks(self):
        self.assertEqual(normalize('```literal```\nrange 1~3\n'), '```literal```\nrange 1–3\n')
        self.assertEqual(normalize('   ````1~3````\nrange 1~3\n'), '   ````1~3````\nrange 1–3\n')
        self.assertEqual(normalize('```python\n1~3\n```\nrange 1~3\n'), '```python\n1~3\n```\nrange 1–3\n')

    def test_unmatched_backticks_are_prose(self):
        self.assertEqual(normalize('stray `\nrange 1~3\n'), 'stray `\nrange 1–3\n')
        self.assertEqual(normalize('stray ``text`\nrange 1~3\n'), 'stray ``text`\nrange 1–3\n')
        self.assertEqual(normalize('`multi\n1~3`\nrange 1~3\n'), '`multi\n1~3`\nrange 1–3\n')

    def test_scheduled_rename(self):
        page = item('8', '20260101', '20270909', '새 이름')
        page += item('7', '20200101', '20200101', '현행 이름')
        page += item('6', '19990101', '19990101', '옛 이름')
        rows = parse_history(page, '현행 이름', '7', '20261108')
        self.assertEqual([v['status'] for v in rows], ['scheduled', 'current', 'predecessor'])
        self.assertEqual(rows[0]['name'], '새 이름')
        self.assertEqual(choose(rows, '20270909')['lsiSeq'], '8')
        with self.assertRaises(ValueError):
            parse_history(item('8', '20270101', '20270909', '새 이름') + page,
                          '현행 이름', '7', '20261108')

    def test_korean_date_boundary(self):
        before = datetime.datetime(2026, 11, 7, 14, 59, tzinfo=datetime.timezone.utc)
        after = before + datetime.timedelta(minutes=1)
        self.assertEqual(fetch_versions.korea_today(before).isoformat(), '2026-11-07')
        self.assertEqual(fetch_versions.korea_today(after).isoformat(), '2026-11-08')
        page = item('8', '20260101', '20261108', '법') + item('7', '20200101', '20200101', '법')
        with patch.object(fetch_versions, 'korea_today', return_value=fetch_versions.korea_today(after)):
            self.assertEqual(parse_history(page, '법', '7')[0]['status'], 'current')
            self.assertEqual(parse_history(page, '법', '7', '20261107')[0]['status'], 'scheduled')

    def test_staged_anchor(self):
        page = item('7', '20200101', '20270101', '새 이름') + item('7', '20200101', '20200101', '법')
        rows = parse_history(page, '법', '7', '20261108', anchor_ef='20200101')
        self.assertEqual([v['status'] for v in rows], ['scheduled', 'current'])
        reverse = item('7', '20200101', '20200101', '법') + item('7', '20200101', '20270101', '새 이름')
        self.assertEqual(parse_history(reverse, '법', '7', '20261108', anchor_ef='20200101'), rows)
        with self.assertRaises(ValueError):
            parse_history(page, '법', '7', '20261108', anchor_ef='20270101')
        with self.assertRaises(ValueError):
            parse_history(page, '법', '7', '20261108', anchor_ef='20190101')

    def test_truncated_titles_resolved_before_status(self):
        page = item('8', '20200101', '20270101', '공통...')
        page += item('7', '20200101', '20200101', '공통 현행법')
        page += item('6', '19900101', '19900101', '공통...')
        calls = []
        def resolve(seq, ef):
            calls.append((seq, ef))
            return {'8': '공통 미래법', '6': '공통 옛법'}[seq]
        rows = parse_history(page, '공통 현행법', '7', '20261108',
                             anchor_ef='20200101', title_resolver=resolve)
        self.assertEqual([v['name'] for v in rows], ['공통 미래법', '공통 현행법', '공통 옛법'])
        self.assertEqual([v['status'] for v in rows], ['scheduled', 'current', 'predecessor'])
        self.assertEqual(calls, [('8', '20270101'), ('6', '19900101')])
        staged = item('7', '20200101', '20270101', '공통...') + item('7', '20200101', '20200101', '공통...')
        rows = parse_history(staged, '공통 현행법', '7', '20261108', anchor_ef='20200101',
                             title_resolver=lambda seq, ef: '공통 미래법' if ef == '20270101' else '공통 현행법')
        self.assertEqual([v['name'] for v in rows], ['공통 미래법', '공통 현행법'])

    def test_stored_titles_reused_and_changes_resolved(self):
        full = item('7', '20200101', '20200101', '공통 현행법')
        full += item('6', '19900101', '19900101', '공통 옛법')
        stored = parse_history(full, '공통 현행법', '7', '20261108')
        truncated = full.replace('공통 현행법', '공통...').replace('공통 옛법', '공통...')
        with patch.object(fetch_versions, 'resolve_title') as resolve:
            self.assertEqual(parse_history(truncated, '공통 현행법', '7', '20261108',
                                           stored_versions=stored), stored)
            resolve.assert_not_called()
        future = item('8', '20260101', '20270101', '공통...') + truncated
        with patch.object(fetch_versions, 'resolve_title', return_value='공통 미래법') as resolve:
            rows = parse_history(future, '공통 현행법', '7', '20261108', stored_versions=stored)
            resolve.assert_called_once_with('8', '20270101')
            self.assertNotEqual(rows, stored)
            self.assertEqual(rows[0]['name'], '공통 미래법')
        for old, new in (('00100', '00200'), ('일부개정', '전부개정'),
                         ('19900101', '19910101'), ('공통...', '다른...')):
            changed = truncated.replace(old, new)
            with patch.object(fetch_versions, 'resolve_title', return_value='공통 현행법') as resolve:
                rows = parse_history(changed, '공통 현행법', '7', '20261108', stored_versions=stored)
                self.assertTrue(resolve.called)
                self.assertNotEqual(rows, stored)
        for title in ('', '공통...', None):
            incomplete = [dict(row, name=title) for row in stored]
            with patch.object(fetch_versions, 'resolve_title', return_value='공통 현행법') as resolve:
                parse_history(truncated, '공통 현행법', '7', '20261108', stored_versions=incomplete)
                self.assertEqual(resolve.call_count, 2)

    def test_resolve_title_without_articles(self):
        body = '<input id="lsNm" value="옛 법"><input id="lsiSeq" value="6"><input id="efYd" value="19900101">'
        with patch.object(lawgo, 'fetch_body', return_value=body), patch.object(fetch_versions.time, 'sleep'):
            self.assertEqual(fetch_versions.resolve_title('6', '19900101'), '옛 법')
            with self.assertRaises(ValueError):
                fetch_versions.resolve_title('7', '19900101')

    def test_span_block_boundaries(self):
        text = 'stray `\n```text\n` 1~3\n```\nrange 1~3\n'
        self.assertEqual(normalize(text), text.replace('range 1~3', 'range 1–3'))
        for boundary in ('\n', '# heading\n', '- list\n', '> quote\n', '~~~text\n', '===\n'):
            text = 'stray ` 1~3\n' + boundary + '`next 1~3\n'
            self.assertTrue(normalize(text).startswith('stray ` 1–3\n'))
        self.assertEqual(normalize('`multi\nline 1~3`\nrange 1~3'), '`multi\nline 1~3`\nrange 1–3')

    def test_body_identity(self):
        with self.assertRaises(ValueError):
            lawgo.verify_body('<html>현재 사용자가 많아</html>', '법', '1')
        self.assertEqual(lawgo.hidden('<input value="009471" name="lsId" id="lsId">', 'lsId'), '009471')

    def test_staged_response_identity(self):
        body = '<input id="lsNm" value="법"><input id="lsiSeq" value="7"><input id="efYd" value="20200101">'
        with patch.object(lawgo, 'parse', return_value={'articles': [1]}):
            lawgo.verify_body(body, '법', '7', '20200101')
            with self.assertRaisesRegex(ValueError, 'efYd 불일치'):
                lawgo.verify_body(body, '법', '7', '20210101')
        with patch.object(lawgo, 'fetch_body', return_value=body), patch.object(fetch_versions.time, 'sleep'):
            with self.assertRaisesRegex(ValueError, 'efYd 불일치'):
                fetch_versions.resolve_title('7', '20210101')

    def test_repeal_dates(self):
        for kind in ('폐지', '타법폐지'):
            page = item('8', '20260908', '20270909', '법').replace('일부개정', kind)
            page += item('7', '20200101', '20200101', '법')
            page += item('6', '19900101', '19900101', '옛법')
            before = parse_history(page, '법', '7', '20261108')
            self.assertEqual([v['status'] for v in before], ['scheduled', 'current', 'predecessor'])
            self.assertEqual(choose(before, '20270908')['lsiSeq'], '7')
            for at in ('20270909', '20270910'):
                rows = parse_history(page, '법', '7', at)
                self.assertEqual([v['status'] for v in rows], ['repealed', 'past', 'past'])
                with self.assertRaisesRegex(ValueError, '폐지'):
                    choose(rows, at)
        path = pathlib.Path(__file__).resolve().parents[2] / 'sources/laws/public-works-acts/versions/pw028.json'
        history = json.loads(path.read_text(encoding='utf-8'))
        repeal = next(v for v in history['versions'] if v['lsiSeq'] == '289321')
        self.assertEqual((repeal['kind'], repeal['efYd'], repeal['status']), ('타법폐지', '20270909', 'scheduled'))
        self.assertEqual(choose(history['versions'], '20261108')['lsiSeq'], '230205')
        with self.assertRaisesRegex(ValueError, '폐지'):
            choose(history['versions'], '20270909')

    def test_index_current_matches_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            (root / 'test/versions').mkdir(parents=True)
            (root / 'tools/laws/topics').mkdir(parents=True)
            meta = dict(lsiSeq='7', efYd='20200101', ancYd='20190101', ancNo='1', lsId='000001')
            (root / 'manifest.json').write_text(json.dumps({'test/act': meta}), encoding='utf-8')
            (root / 'tools/laws/topics/test.json').write_text('{"topics": []}', encoding='utf-8')
            doc = dict(meta, name='법', articles=[])
            valid = dict(meta, status='current')
            cases = ([valid], [], [dict(valid, status='past')], [valid, valid],
                     [dict(valid, lsiSeq='8')], [dict(valid, efYd='20210101')])
            with patch.object(build_index.B, 'SRC', root), patch.object(build_index.B, 'ROOT', root), \
                 patch.object(build_index.B, 'CAT', {'collections': [{'id': 'test'}]}), \
                 patch.object(build_index.B, 'load', return_value={'act': doc}), \
                 patch.object(build_index.lawindex, 'owner_index', return_value={}), \
                 patch.object(build_index.S, 'parse', return_value=[]):
                for i, rows in enumerate(cases):
                    (root / 'test/versions/act.json').write_text(json.dumps(dict(lsId='000001', name='법', versions=rows)), encoding='utf-8')
                    if i == 0:
                        self.assertEqual(len(build_index.build()['laws']), 1)
                    else:
                        with self.assertRaisesRegex(ValueError, 'exactly one current row matching manifest'):
                            build_index.build()

    def test_indented_code(self):
        for indent in ('    ', '\t'):
            text = indent + '1~3\n' + indent + '4~5\n\nrange 1~3\n'
            self.assertEqual(normalize(text), text.replace('range 1~3', 'range 1–3'))
            text = 'paragraph\n' + indent + '1~3\n'
            self.assertEqual(normalize(text), text.replace('1~3', '1–3'))
        text = '- list\n\n    continuation 1~3\n'
        self.assertEqual(normalize(text), text.replace('1~3', '1–3'))

    def test_html_span_boundaries(self):
        for opener in ('<!-- comment', '<?processing', '<!DOCTYPE html>', '<!X declaration>', '<![CDATA['):
            text = 'stray ` 1~3\n' + opener + '\n`next 1~3\n'
            self.assertTrue(normalize(text).startswith('stray ` 1–3\n'))

    def test_escaped_backticks(self):
        self.assertEqual(normalize(r'\` 1~3 `'), r'\` 1–3 `')
        self.assertEqual(normalize(r'\\` 1~3 `'), r'\\` 1~3 `')
        self.assertEqual(normalize(r'\``1~3`'), r'\``1~3`')
        self.assertEqual(normalize(r'`1~3\`'), r'`1~3\`')

    def test_real_repeal_reenactments(self):
        root = pathlib.Path(__file__).resolve().parents[2] / 'sources/laws'
        for relative, at in (('land-compensation-act/versions/act.json', '20030101'),
                             ('public-works-acts/versions/pw014.json', '19731101')):
            history = json.loads((root / relative).read_text(encoding='utf-8'))
            row = choose(history['versions'], at)
            self.assertEqual(row['kind'], '폐지제정')
            self.assertEqual(row['efYd'], at)
            page = item(row['lsiSeq'], row['ancYd'], row['efYd'], row['name']).replace('일부개정', row['kind'])
            rows = parse_history(page, row['name'], row['lsiSeq'], at)
            self.assertEqual(rows[0]['status'], 'current')
        for kind in ('폐지', '타법폐지'):
            self.assertTrue(lawgo.is_repeal(kind))
        for kind in ('폐지제정', '제정', '일부개정', '전부개정', '타법개정'):
            self.assertFalse(lawgo.is_repeal(kind))

    def test_current_fetch_rejects_stage_fallback(self):
        body = '<input id="lsNm" value="산림기본법"><input id="lsiSeq" value="285139"><input id="efYd" value="20251001">'
        with tempfile.TemporaryDirectory() as tmp:
            src = pathlib.Path(tmp)
            man = src / 'manifest.json'
            man.write_text('{}', encoding='utf-8')
            cat = {'collections': [{'id': 'test', 'docs': [{'level': 'act', 'name': '산림기본법'}]}]}
            with patch.object(fetch_laws, 'SRC', src), patch.object(fetch_laws, 'MAN', man), \
                 patch.object(fetch_laws, 'CAT', cat), patch.object(sys, 'argv', ['fetch_laws']), \
                 patch.object(lawgo, 'resolve', return_value={'lsiSeq': '285139', 'efYd': '20261001'}), \
                 patch.object(lawgo, 'fetch_body', return_value=body) as fetch, patch('sys.stdout', Output()):
                with self.assertRaisesRegex(ValueError, 'efYd 불일치'):
                    fetch_laws.main()
                fetch.assert_called_once_with('285139', '20261001')
            self.assertEqual(man.read_text(encoding='utf-8'), '{}')
            self.assertFalse((src / 'test').exists())

    def test_raw_html_blocks(self):
        for tag in ('pre', 'script', 'style', 'textarea'):
            text = f'<{tag}>\n1~3\n\n` 4~5\n</{tag}>\nrange 1~3\n'
            self.assertEqual(normalize(text), text.replace('range 1~3', 'range 1–3'))
        for start, end in (('<!--', '-->'), ('<?processing', '?>'),
                           ('<![CDATA[', ']]>'), ('<!DOCTYPE html [', '>')):
            text = f'{start}\n1~3\n\n4~5\n{end}\nrange 1~3\n'
            self.assertEqual(normalize(text), text.replace('range 1~3', 'range 1–3'))
        for tag in ('div', 'table', 'custom-element attr="value"'):
            text = f'<{tag}>\n1~3\n` 4~5\n\nrange 1~3\n'
            self.assertEqual(normalize(text), text.replace('range 1~3', 'range 1–3'))
        self.assertEqual(normalize('paragraph\n<custom>\n1~3\n'), 'paragraph\n<custom>\n1–3\n')
        self.assertEqual(normalize('<!-- 1~3 -->\nrange 1~3\n'), '<!-- 1~3 -->\nrange 1–3\n')
        self.assertEqual(normalize('```html\n<div>\n```\nrange 1~3\n'), '```html\n<div>\n```\nrange 1–3\n')

    def test_markdown(self):
        self.assertEqual(normalize('1~3 `1~3`\n```\n1~3\n```\n4~5\n'), '1–3 `1~3`\n```\n1~3\n```\n4–5\n')
        self.assertEqual(normalize('~~~text\n1~3\n~~~\n'), '~~~text\n1~3\n~~~\n')


if __name__ == '__main__':
    unittest.main()
