#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""국가법령정보센터(law.go.kr) 현행 법령 수집·파싱 공용 모듈.

- resolve(name): 법령명(띄어쓰기 무관) → 현행 lsiSeq·시행일(efYd)·공포정보
- fetch_body(lsiSeq, efYd): 본문 HTML (lsInfoP.do 화면이 AJAX 로 부르는 lsInfoR.do)
- parse(html): 편·장·절·관 제목, 조문(번호·제목·본문 줄), 별표 목록, 부칙 원문
조문 번호는 '70', '70의2' 형식의 키로 다룬다.
"""
import html as H, re, time, urllib.parse, urllib.request

UA = {'User-Agent': 'Mozilla/5.0'}
BASE = 'https://www.law.go.kr'

def _get(url, data=None, referer=None, tries=3):
    h = dict(UA)
    if referer:
        h['Referer'] = referer
    for k in range(tries):
        try:
            req = urllib.request.Request(url, data=data, headers=h)
            return urllib.request.urlopen(req, timeout=90).read()
        except Exception:
            if k == tries - 1:
                raise
            time.sleep(3 * (k + 1))

def resolve(name):
    """법령명 → dict(lsiSeq, efYd, ancYd, ancNo, lsNm, lsClsCd). 현행(시행 중) 판본."""
    nm = re.sub(r'\s+', '', name)
    t = _get(f"{BASE}/{urllib.parse.quote('법령')}/{urllib.parse.quote(nm)}").decode('utf-8', 'replace')
    m = re.search(r'lsiSeq=(\d+)&amp;chrClsCd=\d+&amp;urlMode=lsInfoP&amp;efYd=(\d+)', t)
    if not m:
        raise LookupError(f'법령을 찾지 못함: {name}')
    seq, ef = m.group(1), m.group(2)
    p = _get(f'{BASE}/LSW/lsInfoP.do?lsiSeq={seq}&efYd={ef}').decode('utf-8', 'replace')
    val = lambda i: (re.search(rf'id="{i}" value="([^"]*)"', p) or [None, ''])[1]
    return dict(lsiSeq=seq, efYd=ef, ancYd=val('ancYd'), ancNo=val('ancNo'), lsNm=val('lsNm'), lsClsCd=val('lsClsCd'))

def fetch_body(seq, ef):
    data = urllib.parse.urlencode(dict(lsiSeq=seq, efYd=ef, chrClsCd='010202', ancYnChk='0',
                                       nwJoYnInfo='Y', efGubun='Y', vSct='*')).encode()
    return _get(f'{BASE}/LSW/lsInfoR.do', data=data,
                referer=f'{BASE}/LSW/lsInfoP.do?lsiSeq={seq}').decode('utf-8', 'replace')

def _text(fragment):
    s = re.sub(r'(?is)<(script|style)\b.*?</\1>', ' ', fragment)
    s = re.sub(r'(?i)<input[^>]*>', ' ', s)
    # 본문 속 산식·도표 이미지: 자리 표시로 남긴다 (fetch_laws.py 가 원본을 저장, build_laws.py 가 전사를 넣음)
    s = re.sub(r'(?i)<img[^>]*src="[^"]*flDownload\.do\?flSeq=(\d+)[^"]*"[^>]*>', r' [이미지 flSeq=\1] ', s)
    s = H.unescape(re.sub(r'<[^>]+>', ' ', s))
    return re.sub(r'\s+', ' ', s).strip()

ART = re.compile(r'^제(\d+)조(?:의(\d+))?\s*(?:\(([^)]*(?:\([^)]*\)[^)]*)*)\))?\s*(.*)$')

def parse(page):
    """→ dict(headings=[{key, level, title, before}], articles=[{key, no, title, lines, deleted, path}], annexes=[...], addenda=str)"""
    i_add = page.find('<!-- 부칙')
    if i_add < 0:
        i_add = len(page)
    i_byl = page.find('<!-- 별표 서식 시작')
    body = page[:min(i_add, i_byl if i_byl > 0 else len(page))]
    # 블록 순서대로: 제목(gtit) / 조문(lawcon)
    tokens = []
    for m in re.finditer(r'<p class="gtit"[^>]*>(.*?)</p>|<div class="lawcon">(.*?)</div>\s*</div>', body, re.S):
        if m.group(1) is not None:
            tokens.append(('h', _text(m.group(1))))
        else:
            tokens.append(('a', m.group(2)))
    heads, arts, path = [], [], {}
    order = {'편': 1, '장': 2, '절': 3, '관': 4}
    for kind, val in tokens:
        if kind == 'h':
            title = re.sub(r'\s*<[^>]*>\s*$', '', val).strip()
            mm = re.match(r'^제\s*\d+\s*(?:의\s*\d+\s*)?(편|장|절|관)', title)
            lvl = order[mm.group(1)] if mm else 5
            for k in list(path):
                if k >= lvl:
                    del path[k]
            path[lvl] = title
            heads.append(dict(level=lvl, title=title, before=len(arts)))
            continue
        paras = re.findall(r'<p[^>]*>(.*?)</p>', val, re.S)
        lines = [_text(p) for p in paras]
        lines = [l for l in lines if l]
        if not lines:
            continue
        m = ART.match(lines[0])
        if not m:
            # 조문이 아닌 블록(전문 등)은 직전 조문에 붙인다
            if arts:
                arts[-1]['lines'] += lines
            continue
        no = m.group(1) + (f'의{m.group(2)}' if m.group(2) else '')
        title = (m.group(3) or '').strip()
        first = m.group(4).strip()
        deleted = (not title) and first.startswith('삭제')
        arts.append(dict(key=no, title=title, deleted=deleted,
                         lines=([first] if first else []) + lines[1:],
                         path=[path[k] for k in sorted(path)]))
    annexes = []
    if i_byl > 0:
        for m in re.finditer(r"bylInfoDiv\('(\d+)'\);\" href=\"#AJAX\">\s*(\[[^<]*?)</a>(.*?)</span>", page[i_byl:i_add if i_add > i_byl else len(page)], re.S):
            pdf = re.search(r'flSeq=(\d+)&amp;bylClsCd=\d+" target="_blank">\s*<img alt="PDF', m.group(3))
            hwp = re.search(r'flSeq=(\d+)&amp;bylClsCd=\d+" target="_blank">\s*<img alt="HWP', m.group(3))
            annexes.append(dict(id=m.group(1), title=_text(m.group(2)),
                                pdf=pdf.group(1) if pdf else None, hwp=hwp.group(1) if hwp else None))
    addenda = _text(page[i_add:]) if i_add < len(page) else ''
    return dict(headings=heads, articles=arts, annexes=annexes, addenda=addenda)

def download(flseq, seq):
    return _get(f'{BASE}/LSW/flDownload.do?gubun=&flSeq={flseq}&bylClsCd=110201',
                referer=f'{BASE}/LSW/lsInfoP.do?lsiSeq={seq}')
