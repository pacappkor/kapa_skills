#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""국가법령정보센터(law.go.kr) 현행 법령 수집·파싱 공용 모듈.

- resolve(name): 법령명(띄어쓰기 무관) → 현행 lsiSeq·시행일(efYd)·공포정보
- fetch_body(lsiSeq, efYd): 본문 HTML (lsInfoP.do 화면이 AJAX 로 부르는 lsInfoR.do)
- parse(html): 편·장·절·관 제목, 조문(번호·제목·본문 줄), 별표 목록, 부칙 원문
조문 번호는 '70', '70의2' 형식의 키로 다룬다.
"""
import html as H, re, time, urllib.parse, urllib.request
from html.parser import HTMLParser


class _AddendaParser(HTMLParser):
    """Read legal paragraphs only inside arDivArea, not the following annex UI.

    HTMLParser handles literal <...> in quoted onclick/alt attributes; stripping
    tags with a regex mistakes their > for the end of the tag and leaks JS.
    """
    VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
            'link', 'meta', 'param', 'source', 'track', 'wbr'}
    CONTROLS = {'script', 'style', 'button', 'select', 'textarea', 'iframe', 'object'}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.region = None
        self.paragraph = None
        self.parts = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'div' and attrs.get('id') == 'arDivArea':
            self.region = len(self.stack)
        suppressed = (bool(self.stack) and self.stack[-1][1]) or tag in self.CONTROLS
        # Links to legal text remain text; file downloads are page controls.
        if tag == 'a' and re.search(r'flDownload|bylInfoDiv|javascript:.*down',
                                  attrs.get('href', '') + attrs.get('onclick', ''), re.I):
            suppressed = True
        if self.region is not None and tag == 'p':
            classes = attrs.get('class', '').split()
            if any(re.fullmatch(r'pty3(?:_dep\d+)?', c) for c in classes):
                self.paragraph = len(self.stack)
        if tag not in self.VOID:
            self.stack.append((tag, suppressed))
        self.parts.append(' ')

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                if self.paragraph is not None and i <= self.paragraph:
                    self.paragraph = None
                if self.region is not None and i <= self.region:
                    self.region = None
                del self.stack[i:]
                break
        self.parts.append(' ')

    def handle_data(self, data):
        if (self.region is not None and self.paragraph is not None
                and not self.stack[-1][1]):
            self.parts.append(data)


def _addenda(page):
    parser = _AddendaParser()
    parser.feed(page)
    parser.close()
    return re.sub(r'\s+', ' ', ''.join(parser.parts)).strip()

UA = {'User-Agent': 'Mozilla/5.0'}
BASE = 'https://www.law.go.kr'

def _get(url, data=None, referer=None, tries=3):
    h = dict(UA)
    if referer:
        h['Referer'] = referer
    for k in range(tries):
        try:
            req = urllib.request.Request(url, data=data, headers=h)
            body = urllib.request.urlopen(req, timeout=90).read()
            if any(s in body.decode('utf-8', 'replace') for s in ('현재 사용자가 많아', '서비스 이용에 불편을 드려')):
                raise RuntimeError('law.go.kr 오류 응답 (HTTP 200)')
            return body
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

def hidden(page, name):
    """Read a hidden input independently of attribute ordering."""
    for tag in re.findall(r'<input\b[^>]*>', page, re.I):
        attrs = dict(re.findall(r'([\w-]+)=["\']([^"\']*)["\']', tag))
        if attrs.get('id') == name:
            return H.unescape(attrs.get('value', ''))
    raise ValueError(f'법령 본문 식별자 없음: {name}')


def is_repeal(kind):
    """폐지제정 is a new enactment, not the end of a law's force."""
    return kind in {'폐지', '타법폐지'}


def verify_identity(page, seq, ef=None):
    if hidden(page, 'lsiSeq') != str(seq):
        raise ValueError(f'lsiSeq 불일치: {seq}')
    if ef is not None and hidden(page, 'efYd') != str(ef):
        raise ValueError(f'시행일 efYd 불일치: 요청 {ef}')


def verify_body(page, name, seq, ef=None):
    if re.sub(r'\s+', '', hidden(page, 'lsNm')) != re.sub(r'\s+', '', name):
        raise ValueError(f'법령명 불일치: {name}')
    verify_identity(page, seq, ef)
    if not parse(page)['articles']:
        raise ValueError('법령 조문 없음')


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
    # The site's comment before this container can itself say "영역 끝".
    # Use the actual container boundary rather than interpreting that comment.
    add_start = re.search(r'''<div\b[^>]*\bid\s*=\s*["']arDivArea["'][^>]*>''', page, re.I)
    i_add = add_start.start() if add_start else len(page)
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
    addenda = _addenda(page[i_add:]) if i_add < len(page) else ''
    return dict(headings=heads, articles=arts, annexes=annexes, addenda=addenda)

def download(flseq, seq):
    return _get(f'{BASE}/LSW/flDownload.do?gubun=&flSeq={flseq}&bylClsCd=110201',
                referer=f'{BASE}/LSW/lsInfoP.do?lsiSeq={seq}')
