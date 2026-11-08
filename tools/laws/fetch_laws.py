#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""카탈로그(tools/laws/catalog.json)의 법령을 국가법령정보센터에서 받아 sources/laws/ 에 저장하거나, 최신 여부를 확인한다.

usage:
  python -I tools/laws/fetch_laws.py [컬렉션id ...]          # 받기 (기본: 전부)
  python -I tools/laws/fetch_laws.py --check [컬렉션id ...]  # 받지 않고 현행 판본과 manifest 비교 → 바뀐 법령 보고 (종료 코드 1)

저장
  sources/laws/<컬렉션>/<level>.json  : 법령명·판본정보·제목(편장절관)·조문·별표 목록
  sources/laws/<컬렉션>/<level>.addenda.txt : 부칙 원문(스킬에는 넣지 않음, 경과조치 확인용)
  sources/laws/<컬렉션>/annex/<level>-<별표id>.txt : 별표 PDF 의 텍스트 추출본(표는 줄 구조가 깨질 수 있음)
  sources/laws/<컬렉션>/img/<flSeq>.gif : 본문 속 산식 이미지(조문 텍스트에는 '[이미지 flSeq=N]' 으로 남음, 전사는 tools/laws/image_text.json)
  sources/laws/manifest.json : 법령별 lsiSeq·공포번호·공포일·시행일·수집일·본문 해시
"""
import datetime, hashlib, json, pathlib, re, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import lawgo

ROOT = pathlib.Path(__file__).resolve().parents[2]
CAT = json.loads((ROOT / 'tools' / 'laws' / 'catalog.json').read_text(encoding='utf-8'))
SRC = ROOT / 'sources' / 'laws'
MAN = SRC / 'manifest.json'

def wbytes(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode('utf-8'))

def pdf_text(data):
    import pymupdf
    doc = pymupdf.open(stream=data, filetype='pdf')
    return '\n'.join(p.get_text() for p in doc)

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    check = '--check' in sys.argv
    man = json.loads(MAN.read_text(encoding='utf-8')) if MAN.exists() else {}
    changed = []
    for c in CAT['collections']:
        if args and c['id'] not in args:
            continue
        for d in c['docs']:
            key = f"{c['id']}/{d['level']}"
            r = lawgo.resolve(d['name'])
            old = man.get(key, {})
            if check:
                if (old.get('lsiSeq'), old.get('efYd')) != (r['lsiSeq'], r['efYd']):
                    changed.append((key, d['name'], old.get('efYd'), r['efYd'], old.get('lsiSeq'), r['lsiSeq']))
                continue
            page = lawgo.fetch_body(r['lsiSeq'], r['efYd'])
            lawgo.verify_body(page, d['name'], r['lsiSeq'], r['efYd'])
            r['lsId'] = lawgo.hidden(page, 'lsId')
            p = lawgo.parse(page)
            out = dict(name=d['name'], level=d['level'], label=d['label'], **r,
                       headings=p['headings'], articles=p['articles'], annexes=p['annexes'])
            body = json.dumps(out, ensure_ascii=False, indent=1)
            wbytes(SRC / c['id'] / f"{d['level']}.json", body + '\n')
            wbytes(SRC / c['id'] / f"{d['level']}.addenda.txt", p['addenda'] + '\n')
            for fl in sorted({m for a in p['articles'] for l in a['lines'] for m in re.findall(r'\[이미지 flSeq=(\d+)\]', l)}):
                img = SRC / c['id'] / 'img' / f'{fl}.gif'
                if not img.exists():
                    img.parent.mkdir(parents=True, exist_ok=True)
                    img.write_bytes(lawgo.download(fl, r['lsiSeq']))
            for a in p['annexes']:
                if a['title'].startswith('[별표') and a['pdf']:
                    try:
                        txt = pdf_text(lawgo.download(a['pdf'], r['lsiSeq']))
                    except Exception as e:
                        txt = f'(PDF 텍스트 추출 실패: {e})'
                    wbytes(SRC / c['id'] / 'annex' / f"{d['level']}-{a['id']}.txt", txt)
            man[key] = dict(name=d['name'], lsId=r['lsId'], lsiSeq=r['lsiSeq'], ancNo=r['ancNo'], ancYd=r['ancYd'], efYd=r['efYd'],
                            fetched=datetime.date.today().isoformat(),
                            articles=len(p['articles']), annexes=len(p['annexes']),
                            sha256=hashlib.sha256(json.dumps(p['articles'], ensure_ascii=False).encode()).hexdigest()[:16])
            print(f"{key}: {d['name']} lsiSeq={r['lsiSeq']} 시행 {r['efYd']} 조문 {len(p['articles'])} 별표·서식 {len(p['annexes'])}")
    if check:
        if changed:
            print('바뀐 법령 (key | 법령명 | 시행일 기존→현행 | lsiSeq 기존→현행):')
            for x in changed:
                print(' | '.join(map(str, x)))
            return 1
        print('모든 법령이 manifest 와 같은 현행 판본입니다.')
        return 0
    wbytes(MAN, json.dumps(dict(sorted(man.items())), ensure_ascii=False, indent=1) + '\n')
    return 0

if __name__ == '__main__':
    sys.exit(main())
