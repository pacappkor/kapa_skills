#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""법령 조문 → 법령 스킬 색인. 다른 생성기(실무기준 split_standard.py 등)가 본문의 법령 인용을 스킬 링크로 바꿀 때 쓴다.

find_law_refs(text, aliases) → [(인용 표기, 'laws/<컬렉션>/<스킬>')]
"""
import json, pathlib, re, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from lawstruct import keynum, other_law_cites

ROOT = pathlib.Path(__file__).resolve().parents[2]
OLD_NAMES = {'항공법': '항공안전법', '주식회사의 외부감사에 관한 법률': '주식회사 등의 외부감사에 관한 법률',
             '부동산 거래신고에 관한 법률': '부동산 거래신고 등에 관한 법률'}

def _norm(s):
    return re.sub(r'\s+', '', s)

def owner_index():
    """{(법령명 정규화, 조문키): 'laws/<c>/<skill>'}"""
    cat = json.loads((ROOT / 'tools/laws/catalog.json').read_text(encoding='utf-8'))
    idx = {}
    for c in cat['collections']:
        f = ROOT / f'tools/laws/topics/{c["id"]}.json'
        if not f.exists():
            continue
        cfg = json.loads(f.read_text(encoding='utf-8'))
        names = {d['level']: d['name'] for d in c['docs']}
        for t in cfg['topics']:
            sk = f'laws/{c["id"]}/{c["prefix"]}-{t["slug"]}'
            for lv, rng in t['assign'].items():
                jf = ROOT / f'sources/laws/{c["id"]}/{lv}.json'
                if not jf.exists():
                    continue
                keys = [a['key'] for a in json.loads(jf.read_text(encoding='utf-8'))['articles']]
                for r in rng:
                    if '-' in r:
                        a, b = r.split('-'); lo, hi = keynum(a), keynum(b)
                        ks = [k for k in keys if lo <= keynum(k) <= hi]
                    else:
                        ks = [r]
                    for k in ks:
                        idx[(_norm(names[lv]), k)] = sk
    return idx

def stale_map():
    f = ROOT / 'tools/laws/stale_citations.json'
    if not f.exists():
        return {}
    d = json.loads(f.read_text(encoding='utf-8'))
    return {tuple(k.split('|')): v for k, v in d.items() if not k.startswith('_')}

def find_law_refs(text, aliases=None):
    """aliases: {'토지보상법 시행규칙': '공익사업을 위한 ... 시행규칙', '법': '감정평가 및 ...', ...}"""
    idx = owner_index()
    stale = stale_map()
    def resolve(law, k, shown):
        cur = stale.get((law, k))
        if cur:
            sk = idx.get((_norm(law), cur['current']))
            return (f'{shown} (개정 전 번호 → 현행 제{cur["current"]}조)', sk) if sk else (None, None)
        return shown, idx.get((_norm(law), k))
    aliases = aliases or {}
    out = []
    t = re.sub(r'\s+', ' ', text)
    # 1) 「법령명」 제N조 (… 및 제M조, 같은 법 제K조 처럼 이어지는 인용 포함)
    found, t = other_law_cites(t)
    for nm, k in found:
        cur = OLD_NAMES.get(nm, nm)
        lab, sk = resolve(cur, k, f'「{nm}」 제{k.replace("의", "조의", 1) if "의" in k else k + "조"}'.replace('조조', '조'))
        if sk:
            out.append((lab, sk))
    # 2) 약칭 (긴 것부터) — '법', '규칙' 같은 한 글자 약칭은 앞에 한글이 붙지 않은 경우만
    for ab in sorted(aliases, key=len, reverse=True):
        pat = (r'(?<![가-힣])' if len(ab) <= 2 else '') + re.escape(ab) + r'\s*제(\d+)조(?:의(\d+))?'
        def rep(m, ab=ab):
            k = m.group(1) + (f'의{m.group(2)}' if m.group(2) else '')
            lab, sk = resolve(aliases[ab], k, f'{ab} 제{k}조')
            if sk:
                out.append((lab, sk))
            return ' '
        t = re.sub(pat, rep, t)
    return out
