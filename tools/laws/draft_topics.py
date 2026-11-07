#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""배정표 초안 생성: 법의 장(章)(조문이 많으면 절)을 주제로 삼고, 시행령·시행규칙 조문을
'법 제N조' 인용 → 같은 이름의 장 → 바로 앞 조문의 주제 순으로 붙인다. 결과는 사람이 검토해 slug·제목·범위를 고친다.

usage: python -I tools/laws/draft_topics.py <컬렉션id> [--split N]   # 장의 조문 수가 N(기본 25)을 넘으면 절 단위로 나눔
출력: tools/laws/topics/<컬렉션id>.draft.json 과 요약표(표준출력)
"""
import json, pathlib, re, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from lawstruct import keynum, parent_of

ROOT = pathlib.Path(__file__).resolve().parents[2]

def chap(path, depth):
    return ' > '.join(path[:depth]) if path else '(장 없음)'

def runs(keys, order):
    out, cur = [], []
    for k in keys:
        if cur and order[k] == order[cur[-1]] + 1:
            cur.append(k)
        else:
            if cur:
                out.append(cur)
            cur = [k]
    if cur:
        out.append(cur)
    return [r[0] if len(r) == 1 else f'{r[0]}-{r[-1]}' for r in out]

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    cid = sys.argv[1]
    split = int(sys.argv[sys.argv.index('--split') + 1]) if '--split' in sys.argv else 25
    cat = json.loads((ROOT / 'tools/laws/catalog.json').read_text(encoding='utf-8'))
    c = next(x for x in cat['collections'] if x['id'] == cid)
    docs = {d['level']: json.loads((ROOT / f'sources/laws/{cid}/{d["level"]}.json').read_text(encoding='utf-8')) for d in c['docs']}
    act = docs['act']
    # 장별 조문 수
    cnt = {}
    for a in act['articles']:
        cnt[chap(a['path'], 1)] = cnt.get(chap(a['path'], 1), 0) + 1
    topic_of_act, topics = {}, []
    for a in act['articles']:
        ch = chap(a['path'], 1)
        name = chap(a['path'], 2) if cnt[ch] > split and len(a['path']) > 1 else ch
        if not topics or topics[-1]['title'] != name:
            topics.append(dict(slug=f't{len(topics) + 1:02d}', title=name, assign={lv: [] for lv in docs}))
        topics[-1]['assign']['act'].append(a['key'])
        topic_of_act[a['key']] = len(topics) - 1
    chname = {re.sub(r'^제\d+(?:의\d+)?장\s*', '', t['title'].split(' > ')[0]): i for i, t in enumerate(topics)}
    other = [lv for lv in docs if lv != 'act']
    for lv in other:
        d = docs[lv]
        prev = 0
        for a in d['articles']:
            idx = None
            par = parent_of(a, d['label'])
            cited = None
            if par and par[0] == '법' and par[1] in topic_of_act:
                cited = topic_of_act[par[1]]
            elif par and par[0] == '영' and lv != 'decree':
                cited = docs['decree'].get('_t', {}).get(par[1])
            cands = []
            if a['path']:
                nm = re.sub(r'^제\d+(?:의\d+)?장\s*', '', a['path'][0])
                cands = [i for i, tp in enumerate(topics)
                         if re.sub(r'^제\d+(?:의\d+)?장\s*', '', tp['title'].split(' > ')[0]) == nm]
            if cands:
                if cited in cands:
                    idx = cited
                elif len(a['path']) > 1:
                    sec = re.sub(r'^제\d+(?:의\d+)?절\s*', '', a['path'][1])
                    m = [i for i in cands if ' > ' in topics[i]['title'] and
                         re.sub(r'^제\d+(?:의\d+)?절\s*', '', topics[i]['title'].split(' > ')[1]) == sec]
                    idx = m[0] if m else (prev if prev in cands else cands[0])
                else:
                    idx = prev if prev in cands else cands[0]
            elif cited is not None:
                idx = cited
            if idx is None:
                idx = prev
            topics[idx]['assign'][lv].append(a['key'])
            d.setdefault('_t', {})[a['key']] = idx
            prev = idx
    for t in topics:
        for lv in docs:
            order = {a['key']: i for i, a in enumerate(docs[lv]['articles'])}
            ks = sorted(t['assign'][lv], key=lambda k: order[k])
            t['assign'][lv] = runs(ks, order)
    out = ROOT / f'tools/laws/topics/{cid}.draft.json'
    out.write_bytes((json.dumps(dict(collection=cid, topics=topics), ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
    for t in topics:
        print(t['slug'], '|', t['title'], '|', ' ; '.join(f'{docs[lv]["label"]} ' + ','.join(v) for lv, v in t['assign'].items() if v))
    print('->', out.relative_to(ROOT))

if __name__ == '__main__':
    main()
