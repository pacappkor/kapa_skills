#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""법령 컬렉션 생성기: sources/laws/ 의 원문과 tools/laws/topics/<컬렉션>.json 배정표로
laws/<컬렉션>/<prefix>-<slug>/{SKILL.md,source.md} 와 입구 스킬의 생성 블록을 만든다.

usage:
  python -I tools/laws/build_laws.py            # 생성·갱신
  python -I tools/laws/build_laws.py --check    # 쓰지 않고 검사 (배정 누락·중복, 생성물 최신 여부, 요약의 조문 인용 누락)
  python -I tools/laws/build_laws.py --coverage # 요약에서 빠진 조문 목록만 출력 (작업 중 확인용)

규칙
- 모든 조문(삭제 조문 포함)은 정확히 한 주제에 배정되어야 한다.
- 별표는 제목의 '(제N조 관련)'으로 그 조문의 주제에 자동 배정한다. 배정되지 않으면 오류(배정표의 "annex" 로 지정).
- SKILL.md 는 사람이 쓴 부분을 보존하고 GENERATED 블록만 다시 쓴다.
- 요약 완전성: 각 주제 SKILL.md 의 사람이 쓴 부분은 그 주제의 삭제되지 않은 조문을 모두 '<약칭> 제N조' 형식으로 인용해야 한다.
"""
import json, pathlib, re, sys, collections
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from lawstruct import keynum, cites, other_law_cites
OLD_NAMES_B = {'항공법': '항공안전법', '주식회사의 외부감사에 관한 법률': '주식회사 등의 외부감사에 관한 법률'}

ROOT = pathlib.Path(__file__).resolve().parents[2]
CAT = json.loads((ROOT / 'tools' / 'laws' / 'catalog.json').read_text(encoding='utf-8'))
SRC = ROOT / 'sources' / 'laws'
OUT = ROOT / 'laws'
STALE = {k: v for k, v in json.loads((ROOT / 'tools' / 'laws' / 'stale_citations.json').read_text(encoding='utf-8')).items() if not k.startswith('_')}
IMG_TEXT = json.loads((ROOT / 'tools' / 'laws' / 'image_text.json').read_text(encoding='utf-8'))
GEN = re.compile(r'(<!-- BEGIN GENERATED:(\w+) -->\n).*?(<!-- END GENERATED:\2 -->)', re.S)

def ymd(s):
    return f'{s[:4]}. {int(s[4:6])}. {int(s[6:])}.' if s and len(s) == 8 else s

def cite_str(label, key):
    n, s = keynum(key)
    return f'{label} 제{n}조' + (f'의{s}' if s else '')

def expand(rng, keys):
    """'24의3-36' 또는 '77' → keys 중 범위에 드는 것"""
    out = []
    for r in rng:
        if '-' in r:
            a, b = r.split('-')
            lo, hi = keynum(a), keynum(b)
            out += [k for k in keys if lo <= keynum(k) <= hi]
        else:
            if r not in keys:
                raise SystemExit(f'배정표 오류: 조문 {r} 없음')
            out.append(r)
    return out

def load(c):
    docs = {}
    for d in c['docs']:
        f = SRC / c['id'] / f"{d['level']}.json"
        docs[d['level']] = json.loads(f.read_text(encoding='utf-8'))
    return docs

def skill_dir(c, slug):
    return f"{c['prefix']}-{slug}"

def rel_link(from_dir, to_dir):
    # tools/fix_links.py 와 같은 최단 상대경로를 쓴다(두 도구가 서로 고쳐 쓰지 않도록)
    import posixpath
    return posixpath.relpath(to_dir + '/SKILL.md', from_dir)

def build(c, check):
    cfg = json.loads((ROOT / 'tools' / 'laws' / 'topics' / f"{c['id']}.json").read_text(encoding='utf-8'))
    docs = load(c)
    labels = {lv: d['label'] for lv, d in docs.items()}
    level_of_label = {v: k for k, v in labels.items()}
    owner = {}          # (level, key) -> slug
    errors = []
    for t in cfg['topics']:
        for lv, rng in t['assign'].items():
            keys = [a['key'] for a in docs[lv]['articles']]
            for k in expand(rng, keys):
                if (lv, k) in owner:
                    errors.append(f'{c["id"]}: {labels[lv]} 제{k}조 중복 배정 ({owner[(lv, k)]}, {t["slug"]})')
                owner[(lv, k)] = t['slug']
    tier_b = c.get('tier') in ('B', 'C')   # B·C층: 배정표의 조문만 수록
    for lv, d in docs.items():
        if tier_b:
            # B층: 배정표에 적은 조문만 수록한다
            docs[lv] = d = dict(d, articles=[a for a in d['articles'] if (lv, a['key']) in owner])
            continue
        for a in d['articles']:
            if (lv, a['key']) not in owner:
                errors.append(f'{c["id"]}: {cite_str(labels[lv], a["key"])}({a["title"]}) 미배정')
    # 별표 배정
    annex_owner = {}
    manual = {}
    for t in cfg['topics']:
        for aid in t.get('annex', []):
            manual[aid] = t['slug']
    for lv, d in docs.items():
        for x in d['annexes']:
            if not x['title'].startswith('[별표'):
                continue
            if x['id'] in manual:
                annex_owner[(lv, x['id'])] = manual[x['id']]; continue
            if tier_b:
                no = re.match(r'\[별표\s*([\d의]+)\]', x['title'])
                for t_ in cfg['topics']:
                    if no and no.group(1) in t_.get('annex_no', {}).get(lv, []):
                        annex_owner[(lv, x['id'])] = t_['slug']
                continue
            m = re.search(r'제(\d+)조(?:의(\d+))?', x['title'])
            k = (m.group(1) + (f'의{m.group(2)}' if m.group(2) else '')) if m else None
            if k and (lv, k) in owner:
                annex_owner[(lv, x['id'])] = owner[(lv, k)]
            else:
                errors.append(f'{c["id"]}: {labels[lv]} {x["title"]} 별표 주제 미정 (배정표 annex 에 id {x["id"]} 지정)')
    if errors:
        return errors, {}
    coll_dir = f'laws/{c["id"]}'
    files = {}
    # 다른 컬렉션 법령명 → (컬렉션, level)
    name_map = {}
    for cc in CAT['collections']:
        for d in cc['docs']:
            name_map[re.sub(r'\s+', '', d['name'])] = (cc, d['level'])
    all_owner = {}
    for cc in CAT['collections']:
        try:
            cfg2 = json.loads((ROOT / 'tools' / 'laws' / 'topics' / f"{cc['id']}.json").read_text(encoding='utf-8'))
            docs2 = load(cc)
        except FileNotFoundError:
            continue
        for t in cfg2['topics']:
            for lv, rng in t['assign'].items():
                for k in expand(rng, [a['key'] for a in docs2[lv]['articles']]):
                    all_owner[(cc['id'], lv, k)] = (cc, t['slug'])
    topics = {t['slug']: t for t in cfg['topics']}
    annex_errors = []
    by_topic = collections.defaultdict(list)
    for lv, d in docs.items():
        for a in d['articles']:
            by_topic[owner[(lv, a['key'])]].append((lv, a))
    for t in cfg['topics']:
        slug = t['slug']; sd = skill_dir(c, slug); here = f'{coll_dir}/{sd}'
        items = by_topic[slug]
        # source.md
        L = [f'# 원문 — {sd}', '',
             f'> {t["title"]}', '>',
             '> 출처: 국가법령정보센터(law.go.kr) 현행 법령. 원문을 그대로 옮긴 자동 생성 파일이다.', '']
        refs_out = set()
        for lv in docs:
            arts = [a for l2, a in items if l2 == lv]
            d = docs[lv]
            anx = [x for x in d['annexes'] if annex_owner.get((lv, x['id'])) == slug]
            if not arts and not anx:
                continue
            L += [f'## {d["label"]} — 「{d["name"]}」', '',
                  f'공포 {ymd(d["ancYd"])} 제{d["ancNo"]}호 · 시행 {ymd(d["efYd"])} · '
                  f'<https://www.law.go.kr/LSW/lsInfoP.do?lsiSeq={d["lsiSeq"]}&efYd={d["efYd"]}>', '']
            cur = None
            for a in arts:
                p = ' > '.join(a['path'])
                if p and p != cur:
                    L += [f'<!-- {p} -->', '']
                    cur = p
                head = cite_str('', a['key']).strip() + (f'({a["title"]})' if a['title'] else '')
                L += [f'### {head}' + (' — 삭제' if a['deleted'] else ''), '']
                for line in a['lines']:
                    for fl in re.findall(r'\[이미지 flSeq=(\d+)\]', line):
                        img = '../' * (len(here.split('/'))) + f'sources/laws/{c["id"]}/img/{fl}.gif'
                        if fl in IMG_TEXT:
                            line = line.replace(f'[이미지 flSeq={fl}]', '')
                            L += ([line, ''] if line.strip() else [])
                            body = IMG_TEXT[fl]
                            L += (body.split('\n') if body.startswith('|') else [f'> {body}']) + ['',
                                  f'> (원문에는 이미지로 실려 있음 — 위는 전사. [원본 이미지]({img}))', '']
                            line = ''
                        else:
                            line = line.replace(f'[이미지 flSeq={fl}]', f'[원문 이미지 — 전사 없음, 원본 확인 필요: {img}]')
                    if line.strip():
                        L += [line, '']
                text = ' '.join(a['lines'])
                # 인용 관계
                found, t2 = other_law_cites(text)
                for nm0, k in found:
                    nm = re.sub(r'\s+', '', OLD_NAMES_B.get(nm0, nm0))
                    if nm in name_map:
                        cc, lv2 = name_map[nm]
                        o = all_owner.get((cc['id'], lv2, k))
                        if o and not (o[0]['id'] == c['id'] and o[1] == slug):
                            # 조문 단위로 보이도록 인용하는 쪽 조문을 앞에 붙인다 (들어오는 연결에서 어느 법 몇 조인지 알 수 있게)
                            refs_out.add((f'{cite_str(d["label"], a["key"])}: 「{nm0}」 제{cite_str("", k).strip()[1:]}', f'laws/{o[0]["id"]}/{skill_dir(o[0], o[1])}'))
                for lab, k in cites(t2):
                    tl = level_of_label.get(lab)
                    if tl and tl != lv and (tl, k) in owner and owner[(tl, k)] != slug:
                        refs_out.add((cite_str(lab, k), f'{coll_dir}/{skill_dir(c, owner[(tl, k)])}'))
                t3 = re.sub(r'(?<![가-힣])(?:법|영|규칙|시행령|시행규칙)\s*제\d+조(?:의\d+)?', ' ', t2)
                for m in re.finditer(r'제(\d+)조(?:의(\d+))?', t3):
                    k = m.group(1) + (f'의{m.group(2)}' if m.group(2) else '')
                    if (lv, k) in owner and owner[(lv, k)] != slug:
                        refs_out.add((cite_str(d['label'], k), f'{coll_dir}/{skill_dir(c, owner[(lv, k)])}'))
            for x in anx:
                links = ' · '.join(f'[원본 {k.upper()}](https://www.law.go.kr/LSW/flDownload.do?gubun=&flSeq={x[k]}&bylClsCd=110201)'
                                   for k in ('pdf', 'hwp') if x.get(k))
                md_f = SRC / c['id'] / 'annex-md' / f'{lv}-{x["id"]}.md'
                L += [f'### {x["title"]}', '']
                if md_f.exists():
                    raw = md_f.read_text(encoding='utf-8')
                    fm = re.match(r'^---\n(.*?)\n---\n', raw, re.S)
                    meta = dict(l.split(':', 1) for l in fm.group(1).splitlines() if ':' in l) if fm else {}
                    meta = {k.strip(): v.strip() for k, v in meta.items()}
                    if meta.get('pdf_flseq') != (x.get('pdf') or ''):
                        annex_errors.append(f'{c["id"]}: 별표 가공본이 현행 별표와 다름(개정 가능성) — {md_f.relative_to(ROOT).as_posix()} pdf_flseq={meta.get("pdf_flseq")} 현행={x.get("pdf")}')
                    if meta.get('status') != 'verified-against-pdf':
                        annex_errors.append(f'{c["id"]}: 별표 가공본 status 가 verified-against-pdf 가 아님 — {md_f.relative_to(ROOT).as_posix()}')
                    body = raw[fm.end():].strip() if fm else raw.strip()
                    L += [f'> 원본 PDF 의 페이지 이미지와 대조해 표·목록으로 가공한 것이다(`{md_f.relative_to(ROOT).as_posix()}`). 다툼이 있으면 원본이 우선한다. {links}', '',
                          body, '']
                else:
                    annex_errors.append(f'{c["id"]}: 별표 가공본 없음 — {md_f.relative_to(ROOT).as_posix()} ({x["title"][:40]})')
                    txt_f = SRC / c['id'] / 'annex' / f'{lv}-{x["id"]}.txt'
                    txt = txt_f.read_text(encoding='utf-8').strip() if txt_f.exists() else '(텍스트 없음)'
                    L += [f'> 아직 가공하지 않은 PDF 텍스트 추출본이다. 표의 칸 배치가 깨질 수 있으니 원본으로 확인한다. {links}', '',
                          '```text', txt, '```', '']
        files[f'{here}/source.md'] = '\n'.join(L).rstrip() + '\n'
        # 생성 블록
        rng_txt = []
        for lv, d in docs.items():
            ks = [a['key'] for l2, a in items if l2 == lv]
            if ks:
                rng_txt.append(f'{d["label"]} ' + ', '.join(cite_str('', k).strip() for k in ks))
        src_blk = [f'- 근거: ' + '; '.join(f'「{d["name"]}」({d["label"]}, 시행 {ymd(d["efYd"])})' for lv, d in docs.items()
                                          if any(l2 == lv for l2, _ in items)),
                   f'- 원문 전문: [source.md](source.md) — 판단·인용은 반드시 원문으로 확인한다',
                   '- 판본은 국가법령정보센터 현행 법령 기준이다. 의뢰의 기준시점에 적용되는 판본이 다르면 연혁 법령을 확인한다.']
        art_blk = ['이 스킬이 맡은 조문이다. 위 요약은 삭제 조문을 뺀 이 조문들을 모두 한 번 이상 인용한다.', '']
        for lv, d in docs.items():
            arts = [a for l2, a in items if l2 == lv]
            if not arts:
                continue
            L2 = []
            for a in arts:
                L2.append(f'- {cite_str(d["label"], a["key"])}' + (f'({a["title"]})' if a['title'] else '') + (' — 삭제' if a['deleted'] else ''))
            art_blk += [f'**{d["label"]}** 「{d["name"]}」', ''] + L2 + ['']
            anx = [x for x in d['annexes'] if annex_owner.get((lv, x['id'])) == slug]
            if anx:
                art_blk += [f'- 별표: ' + '; '.join(x['title'] for x in anx), '']
        refs_blk = []
        if refs_out:
            refs_blk.append('이 스킬의 원문이 인용하는 다른 스킬의 조문:')
            for r, tgt in sorted(refs_out):
                refs_blk.append(f'- `{r}` → [{tgt.rsplit("/", 1)[1]}]({rel_link(here, tgt)})')
        else:
            refs_blk.append('(같은 컬렉션의 다른 주제를 직접 인용하지 않음)')
        refs_blk += ['', '> 원문의 조문 인용을 자동 추출한 목록이다. "대통령령으로 정하는" 같은 위임 문구와 컬렉션에 없는 법령 인용은 포함하지 않는다.']
        files[f'{here}/SKILL.md'] = dict(source=src_blk, articles=art_blk[:-1] if art_blk[-1] == '' else art_blk, refs=refs_blk,
                                         _meta=dict(name=sd, title=t['title'], need=[cite_str(labels[lv], a['key']) for lv, a in items if not a['deleted']]))
    # 입구 스킬 생성 블록
    start = f'{coll_dir}/00-{c["prefix"]}-start'
    ver = ['| 구분 | 법령 | 공포 | 시행 | 조문 수 |', '|---|---|---|---|---|']
    for lv, d in docs.items():
        if tier_b and not d['articles'] and not any(k[0] == lv for k in annex_owner):
            continue
        ver.append(f'| {d["label"]} | 「{d["name"]}」 | {ymd(d["ancYd"])} 제{d["ancNo"]}호 | {ymd(d["efYd"])} | {len(d["articles"])} |')
    mp = ['| 스킬 | 주제 | 조문 |', '|---|---|---|']
    for t in cfg['topics']:
        rng = []
        for lv, d in docs.items():
            order = {a['key']: i for i, a in enumerate(d['articles'])}
            ks = [a['key'] for l2, a in by_topic[t['slug']] if l2 == lv]
            if ks:
                runs, cur = [], [ks[0]]
                for k in ks[1:]:
                    if order[k] == order[cur[-1]] + 1:
                        cur.append(k)
                    else:
                        runs.append(cur); cur = [k]
                runs.append(cur)
                if tier_b:
                    runs = [[k] for k in ks]   # B층은 일부 조문만 수록하므로 범위로 묶지 않는다
                rng.append(f'{d["label"]} ' + ', '.join(r[0] + (f'~{r[-1]}' if len(r) > 1 else '') for r in runs) + '조')
        sd = skill_dir(c, t['slug'])
        mp.append(f'| [{sd}](../{sd}/SKILL.md) | {t["title"]} | {" · ".join(rng)} |')
    forms = []
    for lv, d in docs.items():
        fs = [x['title'] for x in d['annexes'] if not x['title'].startswith('[별표')]
        if fs:
            forms.append(f'- {d["label"]}: ' + '; '.join(fs))
    gen_start = dict(version=ver, map=mp, forms=forms or ['(서식 없음)'], _meta=None)
    if c.get('tier') == 'B':
        gen_start['cited'] = cited_rows(c, docs, owner, annex_owner)
    if c.get('tier') == 'C':
        # 법률별 연결 조문 색인 (원본 전체 법률 기준; 연결 조문이 없는 법률도 표시)
        rows = ['| 법률 | 시행 | 토지보상법을 언급하는 조문 | 스킬 |', '|---|---|---|---|']
        for d0 in c['docs']:
            full = json.loads((SRC / c['id'] / f"{d0['level']}.json").read_text(encoding='utf-8'))
            arts = [a for a in docs[d0['level']]['articles']]
            sk = sorted({owner[(d0['level'], a['key'])] for a in arts})
            rows.append(f"| 「{full['name']}」 | {ymd(full['efYd'])} | " +
                        (', '.join(cite_str('', a['key']).strip() + (f"({a['title']})" if a['title'] else '') for a in arts) or '없음 — 별표의 해당 사업 근거 조항을 원문으로 확인') +
                        ' | ' + (', '.join(f'[{skill_dir(c, s)}](../{skill_dir(c, s)}/SKILL.md)' for s in sk) or '-') + ' |')
        gen_start['index'] = rows
        sp = ['| 법률 | 조문 | 사업인정 의제 | 재결신청 기간 특례 | 토지보상법 준용 | 해당 문구(발췌) |', '|---|---|---|---|---|---|']
        for d0 in c['docs']:
            for a in docs[d0['level']]['articles']:
                txt = re.sub(r'\s+', ' ', ' '.join(a['lines']))
                deem = re.search(r'사업인정[^.。]{0,80}?(?:으로|로)\s*(?:본다|보며|보고|보아|봄)', txt)
                period = re.search(r'제\s*23\s*조[^.]{0,60}제\s*28\s*조[^.]{0,40}불구하고[^.]{0,160}', txt) or                          re.search(r'제\s*28\s*조[^.]{0,40}불구하고[^.]{0,160}', txt)
                apply_ = '준용' in txt
                if not (deem or period or apply_):
                    continue
                ex = (period or deem)
                excerpt = (ex.group(0)[:150] + ('…' if len(ex.group(0)) > 150 else '')) if ex else ''
                sp.append(f"| {d0['label']} | {cite_str('', a['key']).strip()} | {'○' if deem else ''} | {'○' if period else ''} | {'○' if apply_ else ''} | {excerpt.replace('|', '/')} |")
        gen_start['special'] = sp
    files[f'{start}/SKILL.md'] = gen_start
    files['_annex_errors'] = annex_errors
    return [], files

OLD_NAMES = {'항공법': '항공안전법', '주식회사의 외부감사에 관한 법률': '주식회사 등의 외부감사에 관한 법률',
             '외감법': '주식회사 등의 외부감사에 관한 법률', '부동산 거래신고에 관한 법률': '부동산 거래신고 등에 관한 법률'}

def cited_rows(c, docs, owner, annex_owner):
    """B층 입구용: 실무기준·토지보상법 시행규칙 제5장이 인용한 조항 → 수록 스킬"""
    sys.path.insert(0, str(ROOT / 'tools'))
    import split_standard as S
    secs = S.parse(S.SRC.read_text(encoding='utf-8'))
    srcs = [(f'실무기준 [{s["code"]}]', ' '.join(s['lines'])) for s in secs if s['code'] != '부칙']
    r = json.loads((SRC / 'land-compensation-act' / 'rule.json').read_text(encoding='utf-8'))
    srcs += [(f'토지보상법 {cite_str("규칙", a["key"])}', ' '.join(a['lines'])) for a in r['articles']
             if a['path'] and a['path'][0].startswith('제5장')]
    byname = {re.sub(r'\s+', '', d['name']): lv for lv, d in docs.items()}
    rows = collections.defaultdict(set)
    pat = re.compile(r'(?:「([^」]+)」|(외감법))(?:"이라 한다\))?\s*(?:제(\d+)조(?:의(\d+))?|<?\s*별표\s*(\d+)\s*>?)')
    for who, text in srcs:
        text = re.sub(r'\s+', ' ', text)
        for m in pat.finditer(text):
            nm = (m.group(1) or m.group(2)).strip()
            cur = OLD_NAMES.get(nm, nm)
            lv = byname.get(re.sub(r'\s+', '', cur))
            if not lv:
                continue
            if m.group(3):
                k = m.group(3) + (f'의{m.group(4)}' if m.group(4) else '')
                what = f'제{m.group(3)}조' + (f'의{m.group(4)}' if m.group(4) else '')
                slug = owner.get((lv, k))
            else:
                what = f'별표 {m.group(5)}'
                slug = next((s for (l2, aid), s in annex_owner.items() if l2 == lv and re.match(rf'\[별표\s*{m.group(5)}\]',
                             next(x['title'] for x in docs[lv]['annexes'] if x['id'] == aid))), None)
            label = f'「{nm}」' + (f' → 현행 「{cur}」' if cur != nm else '')
            st = STALE.get(f'{cur}|{m.group(3)}' + (f'의{m.group(4)}' if m.group(4) else '')) if m.group(3) else None
            if st:
                what += f' (개정 전 번호 → 현행 제{st["current"]}조)'
                slug = owner.get((lv, st['current']), slug)
            rows[(label, what, slug)].add(who)
    out = ['| 인용된 법령 | 조항 | 인용한 규정 | 수록 스킬 |', '|---|---|---|---|']
    for (label, what, slug), whos in sorted(rows.items(), key=lambda x: (x[0][0], x[0][1])):
        sk = f'[{skill_dir(c, slug)}](../{skill_dir(c, slug)}/SKILL.md)' if slug else '(미수록)'
        out.append(f'| {label} | {what} | {", ".join(sorted(whos))} | {sk} |')
    return out

def render(existing, gen, meta):
    if existing is None:
        if meta is None:
            raise SystemExit('입구 스킬 SKILL.md 가 없습니다(먼저 사람이 작성)')
        existing = (f'---\nname: {meta["name"]}\ndescription: TODO\n---\n\n# {meta["name"]}\n\n> {meta["title"]}\n\n'
                    '<!-- BEGIN GENERATED:source -->\n<!-- END GENERATED:source -->\n\n'
                    '## 언제 읽나\n\nTODO\n\n## 핵심 내용\n\nTODO\n\n## 적용 시 확인사항\n\nTODO\n\n'
                    '## 맡은 조문\n\n<!-- BEGIN GENERATED:articles -->\n<!-- END GENERATED:articles -->\n\n'
                    '## 참조 관계\n\n<!-- BEGIN GENERATED:refs -->\n<!-- END GENERATED:refs -->\n')
    for k, v in gen.items():
        if k.startswith('_'):
            continue
        pat = re.compile(rf'(<!-- BEGIN GENERATED:{k} -->\n).*?(<!-- END GENERATED:{k} -->)', re.S)
        if not pat.search(existing):
            raise SystemExit(f'GENERATED:{k} 블록 없음')
        existing = pat.sub(lambda m: m.group(1) + '\n'.join(v) + '\n' + m.group(2), existing)
    return existing

def coverage(text, need):
    human = GEN.sub('', text)
    human = re.sub(r'\s+', ' ', human)
    miss = []
    for n in need:
        # '법 제75조' 가 '법 제75조의2' 의 일부로만 나오는 경우는 인정하지 않는다
        if not re.search(re.escape(n) + r'(?!의\d)', human):
            miss.append(n)
    return miss

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    check = '--check' in sys.argv
    cov_only = '--coverage' in sys.argv or '--status' in sys.argv
    status = '--status' in sys.argv
    stat = collections.Counter()
    only = [a for a in sys.argv[1:] if not a.startswith('--')]
    bad = 0
    for c in CAT['collections']:
        if only and c['id'] not in only:
            continue
        if not (ROOT / 'tools' / 'laws' / 'topics' / f"{c['id']}.json").exists():
            print(f'{c["id"]}: 배정표 없음(건너뜀)'); continue
        if status:
            print(f'== {c["id"]}')
        errs, files = build(c, check)
        for e in errs:
            print('ERROR', e); bad = 1
        if errs:
            continue
        todo = 0
        aerr = files.pop('_annex_errors', [])
        if check and not cov_only:
            for e in aerr:
                print('ERROR', e); bad = 1
        if status and aerr:
            print(f'  별표 가공 미완료 {len(aerr)}개')
        for rp, content in files.items():
            f = ROOT / rp
            old = f.read_text(encoding='utf-8') if f.exists() else None
            if isinstance(content, dict):
                meta = content.get('_meta')
                if old is None and meta is None:
                    print('ERROR', f'{rp} 없음 (입구 스킬은 사람이 먼저 작성)'); bad = 1; continue
                new = render(old, content, meta)
                if meta:
                    miss = coverage(new, meta['need'])
                    if status:
                        st = 'TODO' if 'TODO' in GEN.sub('', new) else (f'MISSING {len(miss)}' if miss else 'OK')
                        stat[st.split()[0]] += 1
                        print(f'  {st:12s} {meta["name"]}')
                        continue
                    if 'TODO' in GEN.sub('', new):
                        todo += 1
                        if check and not cov_only:
                            print('ERROR', f'{rp}: TODO 남음'); bad = 1
                    elif miss:
                        print(('MISSING ' if cov_only else 'ERROR ') + f'{rp}: 요약에서 인용하지 않은 조문 {len(miss)}개: ' + ', '.join(miss)); bad = 1
            else:
                new = content
            if cov_only:
                continue
            if old != new:
                if check:
                    print('ERROR', f'갱신 필요: {rp}'); bad = 1
                else:
                    f.parent.mkdir(parents=True, exist_ok=True)
                    f.write_bytes(new.encode('utf-8'))
        if not status:
            print(f'{c["id"]}: 주제 {len([k for k in files if k.endswith("SKILL.md")]) - 1}개, 미작성(TODO) {todo}개')
    if status:
        print('합계:', dict(stat))
    return bad

if __name__ == '__main__':
    sys.exit(main())
