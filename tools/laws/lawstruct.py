#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""법령 구조 분석 공용 함수: 조문 키 정렬, 상위 법령 조문 연결(위임 추적), 인용 추출."""
import re

def keynum(k):
    """'70의2' → (70, 2)"""
    m = re.match(r'(\d+)(?:의(\d+))?$', k)
    return (int(m.group(1)), int(m.group(2) or 0))

CITE = re.compile(r'(?<![가-힣])(법|영|규칙|시행령|시행규칙)\s*제(\d+)조(?:의(\d+))?')
SELF = re.compile(r'(?<![가-힣「」\w])제(\d+)조(?:의(\d+))?')

def cites(text, labels=('법', '영', '규칙')):
    """본문에서 '법 제N조', '영 제N조', '규칙 제N조' 인용을 순서대로 → [(label, key)]"""
    out = []
    norm = {'시행령': '영', '시행규칙': '규칙'}
    for m in CITE.finditer(text):
        lab = norm.get(m.group(1), m.group(1))
        out.append((lab, m.group(2) + (f'의{m.group(3)}' if m.group(3) else '')))
    return out

def parent_of(article, level_label):
    """하위 법령 조문의 상위 연결 후보: 시행령 → 첫 '법 제N조', 시행규칙 → 첫 '법' 또는 '영' 인용."""
    text = ' '.join(article['lines'])
    for lab, key in cites(text):
        if level_label == '영' and lab == '법':
            return (lab, key)
        if level_label in ('규칙', '평가규칙') and lab in ('법', '영'):
            return (lab, key)
    return None

# 다른 법령 인용: 「법령명」 제A조제1항 및 제B조, 같은 법 시행령 제C조 … 처럼 이어지는 인용을 모두 잡는다
_ART = r'제\s*\d+\s*조(?:\s*의\s*\d+)?(?:\s*제\s*\d+\s*항)?(?:\s*제\s*\d+\s*호)?(?:\s*[가-하]\s*목)?'
_LIST = _ART + r'(?:\s*(?:및|ㆍ|·|,|와|과|또는|부터|내지)\s*' + _ART + r')*(?:\s*까지)?'
_OTHER = re.compile(r'「([^」]+)」\s*(' + _LIST + r')|같은\s*법\s*(시행령|시행규칙)?\s*(' + _LIST + r')')

def other_law_cites(text):
    """→ ([(법령명(문자 그대로), 조문키)], 인용을 지운 텍스트). '같은 법'은 직전에 「」로 이름이 나온 법령을 가리킨다."""
    out, last = [], None
    def keys(lst):
        return [m.group(1) + (f'의{m.group(2)}' if m.group(2) else '')
                for m in re.finditer(r'제\s*(\d+)\s*조(?:\s*의\s*(\d+))?', lst)]
    def rep(m):
        nonlocal last
        if m.group(1) is not None:
            last = m.group(1).strip()
            out.extend((last, k) for k in keys(m.group(2)))
        elif last:
            base = re.sub(r'\s*(시행령|시행규칙)$', '', last)
            nm = base + (f' {m.group(3)}' if m.group(3) else '')
            out.extend((nm, k) for k in keys(m.group(4)))
        return ' '
    # 「」 없이 이름만 나온 법령은 '같은 법'의 대상이 될 수 있도록 순서대로 처리
    cleaned = _OTHER.sub(rep, text)
    return out, cleaned
