#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""법령 갱신 후 조문 단위 변경 목록: git 의 기준 커밋(기본 HEAD)에 있는 sources/laws/<컬렉션>/<level>.json 과
작업 트리의 같은 파일을 비교해, 신설·삭제·내용 변경·제목 변경 조문과 별표 변경을 주제 스킬과 함께 보여 준다.

usage: python -I tools/laws/diff_laws.py [--base <커밋>] [--markdown] [컬렉션id ...]
  --markdown : CHANGELOG 에 붙일 표 형식으로 출력
종료 코드: 변경이 있으면 1, 없으면 0
"""
import json, pathlib, re, subprocess, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from lawstruct import keynum

ROOT = pathlib.Path(__file__).resolve().parents[2]
CAT = json.loads((ROOT / 'tools/laws/catalog.json').read_text(encoding='utf-8'))

def git_json(base, rel):
    r = subprocess.run(['git', 'show', f'{base}:{rel}'], cwd=ROOT, capture_output=True)
    return json.loads(r.stdout.decode('utf-8')) if r.returncode == 0 else None

def norm(lines):
    # 개정 표시(<개정 …>, [본조신설 …])만 바뀐 경우를 내용 변경과 구분하기 위해 따로 비교
    t = ' '.join(lines)
    return re.sub(r'\s+', ' ', t).strip(), re.sub(r'\s+', ' ', re.sub(r'<(개정|신설)[^>]*>|\[[^\]]*(개정|신설|이동|삭제)[^\]]*\]', '', t)).strip()

def owner_map(cid):
    f = ROOT / f'tools/laws/topics/{cid}.json'
    if not f.exists():
        return {}
    cfg = json.loads(f.read_text(encoding='utf-8'))
    c = next(x for x in CAT['collections'] if x['id'] == cid)
    out = {}
    for t in cfg['topics']:
        for lv, rng in t['assign'].items():
            d = json.loads((ROOT / f'sources/laws/{cid}/{lv}.json').read_text(encoding='utf-8'))
            keys = [a['key'] for a in d['articles']]
            for r in rng:
                if '-' in r:
                    a, b = r.split('-'); lo, hi = keynum(a), keynum(b)
                    for k in keys:
                        if lo <= keynum(k) <= hi:
                            out[(lv, k)] = f"{c['prefix']}-{t['slug']}"
                else:
                    out[(lv, r)] = f"{c['prefix']}-{t['slug']}"
    return out

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    base = sys.argv[sys.argv.index('--base') + 1] if '--base' in sys.argv else 'HEAD'
    md = '--markdown' in sys.argv
    only = [a for a in sys.argv[1:] if not a.startswith('--') and a != base]
    rows = []
    for c in CAT['collections']:
        if only and c['id'] not in only:
            continue
        own = owner_map(c['id'])
        for d in c['docs']:
            rel = f"sources/laws/{c['id']}/{d['level']}.json"
            old, new = git_json(base, rel), json.loads((ROOT / rel).read_text(encoding='utf-8'))
            if old is None:
                rows.append((c['id'], d['label'], '(신규 수집)', '', '', '')); continue
            if (old['lsiSeq'], old['efYd']) == (new['lsiSeq'], new['efYd']) and old['articles'] == new['articles']:
                continue
            ver = f"시행 {old['efYd']}→{new['efYd']}"
            oa = {a['key']: a for a in old['articles']}
            na = {a['key']: a for a in new['articles']}
            for k in sorted(set(oa) | set(na), key=keynum):
                a, b = oa.get(k), na.get(k)
                tgt = own.get((d['level'], k), '(미배정 — 배정표 갱신 필요)' if b else '')
                if a is None:
                    rows.append((c['id'], d['label'], ver, f'제{k}조', f'신설: {b["title"]}', tgt))
                elif b is None:
                    rows.append((c['id'], d['label'], ver, f'제{k}조', f'조문 없어짐: {a["title"]}', tgt))
                elif a['deleted'] != b['deleted'] and b['deleted']:
                    rows.append((c['id'], d['label'], ver, f'제{k}조', f'삭제: {a["title"]}', tgt))
                else:
                    (fa, ca), (fb, cb) = norm(a['lines']), norm(b['lines'])
                    if a['title'] != b['title']:
                        rows.append((c['id'], d['label'], ver, f'제{k}조', f'제목 변경: {a["title"]} → {b["title"]}', tgt))
                    elif ca != cb:
                        rows.append((c['id'], d['label'], ver, f'제{k}조', f'내용 변경: {b["title"]}', tgt))
                    elif fa != fb:
                        rows.append((c['id'], d['label'], ver, f'제{k}조', f'개정 표시만 변경: {b["title"]}', tgt))
            ot = {x['title'] for x in old.get('annexes', [])}
            nt = {x['title'] for x in new.get('annexes', [])}
            for x in sorted(nt - ot):
                rows.append((c['id'], d['label'], ver, '별표·서식', f'신설·변경: {x}', ''))
            for x in sorted(ot - nt):
                rows.append((c['id'], d['label'], ver, '별표·서식', f'없어짐·변경 전: {x}', ''))
    if md:
        print('| 컬렉션 | 법령 | 판본 | 조문 | 변경 | 영향 스킬 |\n|---|---|---|---|---|---|')
        for r in rows:
            print('| ' + ' | '.join(r) + ' |')
    else:
        for r in rows:
            print(' | '.join(r))
        print(f'# 변경 {len(rows)}건', file=sys.stderr)
    return 1 if rows else 0

if __name__ == '__main__':
    sys.exit(main())
