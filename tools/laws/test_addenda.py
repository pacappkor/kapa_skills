#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Offline addenda regressions, using sanitized law.go.kr lsInfoR fragments."""
import pathlib
import sys
import unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import lawgo

# Reduced from 286797 / 20261217, fetched 2026-11-09. No credentials.
HEADER = '''<p class="pty3" style="margin-bottom: -1px;">
<a class="nun" onclick="javascript:arView('ar12913879','<법률 제21810호, 2026. 6. 16.>'); return false;" href="#AJAX">
<img alt="부칙 <법률 제21810호, 2026. 6. 16.>조문목록 접기" src="/LSW/images/button/btn_cocl.gif" /></a>
<input type="checkbox" alt="부칙 <법률 제21810호, 2026. 6. 16.>체크박스" />
<a onclick="arView('ar12913879','<법률 제21810호, 2026. 6. 16.>');return false;" href="#AJAX">
<label><span class="bl"> 부      칙</span></label>
<span class="sfon">&lt;법률 제21810호, 2026. 6. 16.&gt;</span></a></p>'''
ARTICLE = '''<p class="pty3_dep1"><span class="bl">제1조(시행일)</span>
이 법은 공포 후 1년이 경과한 날부터 시행한다.</p>
<div id="ar12913879"><p class="pty3_dep2">별표 제2호(8) 및 (38)의 개정규정은 2027년 9월 9일부터 시행한다.</p></div>'''


class AddendaTest(unittest.TestCase):
    def test_quoted_angles_and_legal_text(self):
        page = '<!-- 부칙 영역 끝 --><div id="arDivArea"><div class="pgroup">' + HEADER + ARTICLE + '</div></div>'
        self.assertEqual(lawgo.parse(page)['addenda'],
                         '부 칙 <법률 제21810호, 2026. 6. 16.> 제1조(시행일) 이 법은 공포 후 1년이 경과한 날부터 시행한다. '
                         '별표 제2호(8) 및 (38)의 개정규정은 2027년 9월 9일부터 시행한다.')

    def test_annex_and_footer_outside_container(self):
        page = '<div id="arDivArea">' + ARTICLE + '</div>'
        expected = lawgo.parse(page)['addenda']
        page += '''<!-- 부칙 영역 끝 --><!-- 별표 서식 시작 -->
<div><p class="pty3"><a href="/LSW/flDownload.do?flSeq=168912195">별표 다운로드</a></p></div>
<button>전체 선택</button><p class="pty3_dep1">목록 닫기 https://www.law.go.kr</p>'''
        self.assertEqual(lawgo.parse(page)['addenda'], expected)

    def test_controls_and_nested_paragraphs(self):
        page = '''<div class='section' id='arDivArea'><div><p class='pty3'>부칙 &lt;2026. 6. 16.&gt;
<button><span>보기</span></button><select><option>다운로드</option></select>
<script>return false;</script><style>p {color:red}</style></p>
<p class='pty3_dep1'>제2조 <a href='#annex'>별표 4</a>에 따른다.
<a href='/LSW/flDownload.do?flSeq=1'>PDF 다운로드</a></p></div></div>'''
        self.assertEqual(lawgo.parse(page)['addenda'], '부칙 <2026. 6. 16.> 제2조 별표 4 에 따른다.')

    def test_absent_addenda_and_annex_before_addenda(self):
        self.assertEqual(lawgo.parse('<!-- 부칙 영역 끝 --><p>다운로드</p>')['addenda'], '')
        self.assertEqual(lawgo.parse('<!-- 별표 서식 시작 --><p>다운로드</p><div id="arDivArea">' + ARTICLE + '</div>')['addenda'],
                         lawgo.parse('<div id="arDivArea">' + ARTICLE + '</div>')['addenda'])


if __name__ == '__main__':
    unittest.main()
