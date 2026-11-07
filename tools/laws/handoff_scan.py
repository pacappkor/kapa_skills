#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""공익사업 근거법(C층) 연결 조항 스캔.

토지보상법 별표(제4조제8호 관련)에 열거된 법률 가운데 A층에 없는 법률을 받아,
본문에 「공익사업을 위한 토지 등의 취득 및 보상에 관한 법률」(토지보상법)을 언급하는 조문을 고른다.
이 조문들이 개별 공익사업법 → 토지보상법으로 넘어가는 연결점이다(수용·사용 권한, 사업인정 의제,
재결신청 기간 특례, 준용, 보상 특례 등).

usage: python -I tools/laws/handoff_scan.py [--fetch]
  --fetch : 법률을 국가법령정보센터에서 받아 sources/laws/public-works-acts/<id>.json 으로 저장(카탈로그 갱신 포함)
  (없으면 저장된 JSON 으로 선택 결과만 다시 계산)
출력: tools/laws/handoff_selection.json  {doc id: [조문키...]} 와 요약표
"""
import json, pathlib, re, sys, datetime, hashlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import lawgo

ROOT = pathlib.Path(__file__).resolve().parents[2]
CATF = ROOT / 'tools/laws/catalog.json'
SRC = ROOT / 'sources/laws'
KEY = re.compile(r'공익사업을\s*위한\s*토지\s*등의\s*취득\s*및\s*보상에\s*관한\s*법률|토지보상법')

def annex_laws():
    f = next((SRC / 'land-compensation-act/annex').glob('act-*.txt'))
    t = re.sub(r'\s+', '', f.read_text(encoding='utf-8'))
    out = []
    for n in re.findall(r'「([^」]+)」', t):
        if n not in out:
            out.append(n)
    return out

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    cat = json.loads(CATF.read_text(encoding='utf-8'))
    tier_a = {re.sub(r'\s+', '', d['name']) for c in cat['collections'] if c.get('tier') == 'A' for d in c['docs']}
    names = [n for n in annex_laws() if n not in tier_a]
    coll = next((c for c in cat['collections'] if c['id'] == 'public-works-acts'), None)
    if '--fetch' in sys.argv:
        man = json.loads((SRC / 'manifest.json').read_text(encoding='utf-8'))
        docs = []
        for i, n in enumerate(names, 1):
            lid = f'pw{i:03d}'
            r = lawgo.resolve(n)
            p = lawgo.parse(lawgo.fetch_body(r['lsiSeq'], r['efYd']))
            nm = r['lsNm'] or n
            out = dict(name=nm, level=lid, label=nm, **r, headings=p['headings'], articles=p['articles'], annexes=p['annexes'])
            (SRC / 'public-works-acts').mkdir(parents=True, exist_ok=True)
            (SRC / 'public-works-acts' / f'{lid}.json').write_bytes((json.dumps(out, ensure_ascii=False, indent=1) + '\n').encode())
            man[f'public-works-acts/{lid}'] = dict(name=nm, lsiSeq=r['lsiSeq'], ancNo=r['ancNo'], ancYd=r['ancYd'], efYd=r['efYd'],
                                                   fetched=datetime.date.today().isoformat(), articles=len(p['articles']),
                                                   annexes=len(p['annexes']),
                                                   sha256=hashlib.sha256(json.dumps(p['articles'], ensure_ascii=False).encode()).hexdigest()[:16])
            docs.append(dict(level=lid, label=nm, name=nm))
            print(f'{lid} {nm} 시행 {r["efYd"]} 조문 {len(p["articles"])}', flush=True)
        cat['collections'] = [c for c in cat['collections'] if c['id'] != 'public-works-acts']
        cat['collections'].append(dict(id='public-works-acts', prefix='pwa', title='공익사업 근거법 연결 조항 (C층)', tier='C', docs=docs))
        CATF.write_text(json.dumps(cat, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
        (SRC / 'manifest.json').write_bytes((json.dumps(dict(sorted(man.items())), ensure_ascii=False, indent=1) + '\n').encode())
        coll = cat['collections'][-1]
    sel, total = {}, 0
    for d in coll['docs']:
        j = json.loads((SRC / 'public-works-acts' / f'{d["level"]}.json').read_text(encoding='utf-8'))
        ks = [a['key'] for a in j['articles'] if not a['deleted'] and KEY.search(' '.join(a['lines']))]
        sel[d['level']] = ks
        total += len(ks)
    (ROOT / 'tools/laws/handoff_selection.json').write_bytes((json.dumps(sel, ensure_ascii=False, indent=1) + '\n').encode())
    none = [d['label'] for d in coll['docs'] if not sel[d['level']]]
    print(f'법률 {len(coll["docs"])}개, 연결 조문 {total}개, 연결 조문 없는 법률 {len(none)}개: {none}')

if __name__ == '__main__':
    main()
