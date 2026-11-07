#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""별표 가공 준비: 스킬에 수록되는 별표마다 원본 PDF 를 받아 페이지 이미지로 렌더링하고 작업 목록을 만든다.
가공(표·목록 마크다운화)은 사람이나 에이전트가 페이지 이미지를 보고 한다. 결과물 위치와 형식은 아래 TARGET 참고.

usage: python -I tools/laws/annex_prep.py <작업폴더> [컬렉션id ...]
  <작업폴더>/<컬렉션>/<level>-<별표id>/page-N.png, original.pdf
  <작업폴더>/manifest.json : [{collection, skill, level, id, title, pdf_flseq, hwp_flseq, pdf_url, pages:[...], raw_txt, target, done}]

TARGET: sources/laws/<컬렉션>/annex-md/<level>-<별표id>.md (저장소에 커밋되는 가공본)
  첫머리 frontmatter:  ---\\nannex: <별표 제목>\\npdf_flseq: <원본 PDF flSeq>\\nstatus: verified-against-pdf\\n---
  build_laws.py 는 가공본이 있으면 source.md 에 넣고, pdf_flseq 가 현행 별표와 다르면(개정) 오류로 알린다.
"""
import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import lawgo
import build_laws as B

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    work = pathlib.Path(sys.argv[1]); only = sys.argv[2:]
    import pymupdf
    man = []
    for c in B.CAT['collections']:
        if only and c['id'] not in only:
            continue
        if not (B.ROOT / 'tools/laws/topics' / f"{c['id']}.json").exists():
            continue
        errs, files = B.build(c, True)
        if errs:
            continue
        docs = B.load(c)
        for rp, v in files.items():
            if not rp.endswith('source.md'):
                continue
            skill = rp.split('/')[2]
            for lv, d in docs.items():
                for x in d['annexes']:
                    if not x['title'].startswith('[별표') or f'### {x["title"]}' not in v:
                        continue
                    key = f"{lv}-{x['id']}"
                    out = work / c['id'] / key
                    out.mkdir(parents=True, exist_ok=True)
                    pages = sorted(str(p) for p in out.glob('page-*.png'))
                    if x['pdf'] and not pages:
                        pdf = lawgo.download(x['pdf'], d['lsiSeq'])
                        (out / 'original.pdf').write_bytes(pdf)
                        doc = pymupdf.open(stream=pdf, filetype='pdf')
                        for i, pg in enumerate(doc, 1):
                            p = out / f'page-{i}.png'
                            pg.get_pixmap(dpi=110).save(str(p))
                            pages.append(str(p))
                    target = B.SRC / c['id'] / 'annex-md' / f'{key}.md'
                    man.append(dict(collection=c['id'], skill=skill, level=lv, id=x['id'], title=x['title'],
                                    pdf_flseq=x['pdf'], hwp_flseq=x['hwp'],
                                    pdf_url=f"https://www.law.go.kr/LSW/flDownload.do?gubun=&flSeq={x['pdf']}&bylClsCd=110201" if x['pdf'] else None,
                                    pages=pages, raw_txt=str(B.SRC / c['id'] / 'annex' / f'{key}.txt'),
                                    target=str(target), done=target.exists()))
    (work / 'manifest.json').write_text(json.dumps(man, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'별표 {len(man)}개, 페이지 {sum(len(m["pages"]) for m in man)}장, 가공본 있음 {sum(m["done"] for m in man)}개 → {work / "manifest.json"}')

if __name__ == '__main__':
    main()
