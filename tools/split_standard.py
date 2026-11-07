#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""「감정평가 실무기준」 원문 텍스트를 스킬 단위로 나눠 각 스킬 폴더에 source.md 를 쓰고,
SKILL.md 의 자동 생성 블록(조항 목차·참조 관계)을 갱신한다.

usage: python -I tools/split_standard.py [--check]
  --check : 파일을 쓰지 않고, 모든 조항이 정확히 하나의 스킬에 배정됐는지와 생성 결과가 최신인지 검사(불일치 시 종료 코드 1)

- 원문: sources/appraisal-practice-standards/<SEQ>.txt (tools/fetch_standard.py 출력)
- 배정표: 아래 SKILLS (스킬 경로 → 조항 선택자 목록). 선택자 '610-3.1' 은 610-3.1 과 그 하위(610-3.1.x)를 포함한다.
- SKILL.md 는 사람이 쓴 부분을 보존하고 <!-- BEGIN GENERATED:x --> ~ <!-- END GENERATED:x --> 사이만 다시 쓴다.
  SKILL.md 가 없으면 머리말(frontmatter)과 빈 틀을 만든다.
"""
import pathlib, re, sys, collections

ROOT = pathlib.Path(__file__).resolve().parent.parent
COLL = 'appraisal-practice-standards'
SEQ = '2100000229230'
SRC = ROOT / 'sources' / COLL / f'{SEQ}.txt'
NOTICE = '국토교통부고시 제2023-522호(2023. 9. 13. 일부개정, 시행 2023. 9. 13.)'
URL = f'https://www.law.go.kr/LSW/admRulInfoP.do?admRulSeq={SEQ}'

# 스킬 경로(컬렉션 기준) -> 조항 선택자
SKILLS = {
    'foundations/foundation-general-provisions': ['100', '900', '부칙'],
    'foundations/foundation-ethics': ['200'],
    'foundations/foundation-engagement': ['300'],
    'foundations/foundation-procedure-and-approaches': ['400'],
    'foundations/foundation-appraisal-report': ['500'],
    'assets/real-estate/asset-land': ['610-1'],
    'assets/real-estate/asset-building': ['610-2'],
    'assets/real-estate/asset-condominium': ['610-3.1'],
    'assets/real-estate/asset-land-building-composite': ['610-3.2'],
    'assets/real-estate/asset-forest': ['610-4'],
    'assets/real-estate/asset-orchard': ['610-5'],
    'assets/real-estate/asset-salt-farm': ['610-6'],
    'assets/real-estate/asset-suspended-construction': ['610-7'],
    'assets/industrial/asset-factory-foundation': ['620-1'],
    'assets/industrial/asset-mining-foundation': ['620-2'],
    'assets/industrial/asset-machinery': ['630'],
    'assets/movables/asset-vehicle': ['640-1'],
    'assets/movables/asset-construction-machinery': ['640-2'],
    'assets/movables/asset-ship': ['640-3'],
    'assets/movables/asset-aircraft': ['640-4'],
    'assets/intangibles/asset-mining-right': ['650-1'],
    'assets/intangibles/asset-fishery-right': ['650-2'],
    'assets/intangibles/asset-goodwill': ['650-3'],
    'assets/intangibles/asset-intellectual-property': ['650-4'],
    'assets/intangibles/asset-stock': ['660-1'],
    'assets/intangibles/asset-bond': ['660-2'],
    'assets/intangibles/asset-enterprise-value': ['660-3'],
    'assets/movables/asset-movable': ['670-1'],
    'assets/income-and-loss/asset-noise-value-loss': ['670-2'],
    'assets/income-and-loss/asset-rent': ['670-3'],
    'assets/income-and-loss/asset-key-money': ['670-4'],
    'assets/asset-other': ['670-5'],
    'overlays/purpose/overlay-collateral': ['710'],
    'overlays/purpose/overlay-auction': ['720'],
    'overlays/purpose/overlay-urban-redevelopment': ['730'],
    'overlays/purpose/overlay-financial-reporting': ['740'],
    'overlays/purpose/overlay-consulting': ['750'],
    'overlays/compensation/overlay-compensation-land-acquisition': ['810'],
    'overlays/compensation/overlay-compensation-land-use': ['820'],
    'overlays/compensation/overlay-compensation-rights': ['830'],
    'overlays/compensation/overlay-compensation-business-loss': ['840'],
}
# 원문 본문에 이미지로만 실린 산식 — 이미지(sources/.../img-<flSeq>.gif)를 사람이 보고 전사한 것.
# 개정으로 이미지가 바뀌면(flSeq 변경) 다시 전사해야 하며, 전사가 없으면 split 이 실패한다.
IMAGE_TEXT = {
    '133045689': '감정평가액 = 해당 토지의 감정평가액 - 해당 토지에 관한 소유권 외의 권리에 대한 감정평가액',
    '133045687': '입체이용저해율 = 건축물 등 이용저해율 + 지하부분 이용저해율 + 그 밖의 이용저해율',
    '133046461': ('연간 영업이익 = 통계법 제3조제3호에 따른 통계작성기관이 같은 법 제18조에 따라 승인을 얻어 '
                  '작성ㆍ공표한 제조부문 보통인부의 노임단가 × 25(일) × 12(월)'),
}
IMG = re.compile(r'^\[원문 이미지 flSeq=(\d+)\]$')

# 제목만 있고 본문이 없는 상위 장(章) — 배정 검사에서 제외
TITLE_ONLY = {'600', '610', '610-3', '620', '640', '650', '660', '670', '700', '800'}

HEAD = re.compile(r'^(\d+(?:\.\d+)*) (\S.*)$')
PART = re.compile(r'^(\d{3}) (\S.*)$')

def parse(text):
    """-> list of sections: dict(code, title, depth, lines)"""
    lines = text.split('\n')
    # 머리말 3줄(제목·시행·소관) 건너뜀
    i = next(k for k, l in enumerate(lines) if PART.match(l))
    secs, part = [], None
    body = [l.strip() for l in lines[i:] if l.strip()]
    for k, l in enumerate(body):
        # 원문 표기 오류: '5. 자동가치산정모형 사용 윤리'처럼 장 번호 뒤에 마침표가 붙은 제목 — 다음 줄이 'N.1 ' 이면 제목으로 본다
        m = re.match(r'^(\d+)\. (\S.{0,40})$', l)
        if m and part and k + 1 < len(body) and body[k + 1].startswith(m.group(1) + '.1 '):
            l = f'{m.group(1)} {m.group(2)}'
        m = PART.match(l)
        if m and len(l) < 45 and int(m.group(1)) % 10 == 0:
            part = m.group(1)
            secs.append(dict(code=part, title=m.group(2), lines=[]))
            continue
        m = re.match(r'^부칙 (<제[^>]+>)$', l)
        if m:
            secs.append(dict(code='부칙', title=m.group(1), lines=[]))
            part = '부칙'
            continue
        m = HEAD.match(l)
        if m and part and part != '부칙' and len(l) < 45 and not l.endswith('다.') and not l.endswith('.'):
            num = m.group(1)
            base = part
            secs.append(dict(code=f'{base}-{num}', title=m.group(2), lines=[]))
            continue
        secs[-1]['lines'].append(l)
    return secs

def selected(code, sel):
    if sel == '부칙':
        return code == '부칙'
    return code == sel or code.startswith(sel + '.') or (re.fullmatch(r'\d{3}', sel) and code.startswith(sel + '-'))

def owner(code):
    for path, sels in SKILLS.items():
        if any(selected(code, s) for s in sels):
            return path
    return None

def depth(code):
    if code == '부칙':
        return 1
    if '-' not in code:
        return 1
    return 2 + code.split('-', 1)[1].count('.')

REF = re.compile(r'\[(\d{3}(?:-[\d.]+)?)(?:-[①-⑳](?:-\d+)?)?(?:[^\]]*)\]')

def ref_target(code):
    """'610-1.5.2.1' -> 그 조항을 담은 스킬 경로 (가장 긴 일치)"""
    c = code.rstrip('.')
    while True:
        o = owner(c)
        if o:
            return o, c
        if '.' in c:
            c = c.rsplit('.', 1)[0]
        elif '-' in c:
            c = c.split('-')[0]
        else:
            return None, code

def skill_name(path):
    return path.rsplit('/', 1)[1]

def rel(from_path, to_path):
    a, b = from_path.split('/'), to_path.split('/')
    return '../' * len(a) + '/'.join(b) + '/SKILL.md'

def build(secs):
    by_skill = collections.defaultdict(list)
    unassigned = []
    for s in secs:
        o = owner(s['code'])
        if o:
            by_skill[o].append(s)
        elif s['code'] not in TITLE_ONLY or s['lines']:
            unassigned.append(s['code'])
    titles = {s['code']: s['title'] for s in secs}
    # 참조 관계
    out_refs, in_refs = collections.defaultdict(set), collections.defaultdict(set)
    for path, ss in by_skill.items():
        for s in ss:
            for l in s['lines']:
                for m in REF.finditer(l):
                    tgt, c = ref_target(m.group(1))
                    if tgt and tgt != path:
                        out_refs[path].add((m.group(0), tgt))
                        in_refs[tgt].add((m.group(0), path))
    files = {}
    for path, ss in by_skill.items():
        # 상위 장 제목(문맥)
        ctx = []
        first = ss[0]['code']
        if first != '부칙' and '-' in first:
            p = first.split('-')[0]
            for anc in [p[0] + '00', p, f"{p}-{first.split('-')[1].split('.')[0]}"]:
                if anc in titles and anc != first and anc not in [c for c, _ in ctx]:
                    ctx.append((anc, titles[anc]))
        src = [f'# 원문 — {skill_name(path)}', '',
               f'> 출처: 「감정평가 실무기준」 {NOTICE}, 국가법령정보센터 <{URL}>  ',
               '> 이 파일은 tools/split_standard.py 가 원문에서 자동 생성한다. 직접 고치지 말 것(원문 그대로).', '']
        if ctx:
            src += ['상위 장: ' + ' › '.join(f'[{c}] {t}' for c, t in ctx), '']
        for s in ss:
            d = depth(s['code'])
            h = '#' * min(2 + max(d - depth(ss[0]['code']), 0), 6)
            label = s['code'] if s['code'] != '부칙' else '부칙'
            src += [f'{h} [{label}] {s["title"]}', '']
            for l in s['lines']:
                m = IMG.match(l)
                if m:
                    fl = m.group(1)
                    if fl not in IMAGE_TEXT:
                        raise SystemExit(f'원문 이미지 flSeq={fl} 의 전사(IMAGE_TEXT)가 없습니다')
                    img = '../' * (len(path.split('/')) + 1) + f'sources/{COLL}/img-{fl}.gif'
                    src += [f'> {IMAGE_TEXT[fl]}', '>',
                            f'> (원문에는 산식이 이미지로 실려 있음 — 위는 전사. [원본 이미지]({img}))', '']
                    continue
                src += [l, '']
        files[f'{COLL}/{path}/source.md'] = '\n'.join(src).rstrip() + '\n'
        # 생성 블록
        outline = []
        for s in ss:
            d = depth(s['code'])
            ind = '  ' * max(d - depth(ss[0]['code']), 0)
            outline.append(f'{ind}- [{s["code"]}] {s["title"]}')
        refs = []
        if out_refs[path]:
            refs.append('이 스킬의 원문이 인용하는 다른 조항:')
            for r, t in sorted(out_refs[path]):
                refs.append(f'- `{r}` → [{skill_name(t)}]({rel(path, t)})')
        if in_refs[path]:
            refs.append('')
            refs.append('이 스킬의 조항을 인용하는 다른 스킬:')
            for r, t in sorted(in_refs[path], key=lambda x: (x[1], x[0])):
                refs.append(f'- [{skill_name(t)}]({rel(path, t)}) — `{r}`')
        if not refs:
            refs = ['(다른 조항을 명시적으로 인용하지 않음)']
        refs += ['', '> 원문의 `[코드]` 인용을 자동 추출한 목록이라 완전한 체크리스트가 아니다. '
                 '"[100 총칙]부터 [600 물건별 감정평가]까지" 같은 범위 인용은 첫 조항만 잡히고, '
                 '관계법규(「…법」) 인용은 포함하지 않는다.']
        nchar = sum(len(l) for s in ss for l in s['lines'])
        gen = {
            'source': [f'- 근거: 「감정평가 실무기준」 {NOTICE}',
                       f'- 범위: ' + ', '.join(f'[{c}]' for c in SKILLS[path]) + f' (원문 약 {nchar:,}자)',
                       f'- 원문 전문: [source.md](source.md) — 판단·인용은 반드시 원문으로 확인한다',
                       f'- 아래 "함께 읽을 스킬"은 후보 목록이다. 의뢰의 결정 사실(목적·대상물건 등)에 해당하는 것만 읽는다 — '
                       f'[workflow-appraisal]({rel(path, "workflows/workflow-appraisal")}) 2-1단계'],
            'outline': outline,
            'refs': refs,
        }
        files[f'{COLL}/{path}/SKILL.md'] = gen
    return files, unassigned

def render_skill(existing, path, gen):
    name = skill_name(path)
    if existing is None:
        existing = (f'---\nname: {name}\ndescription: TODO\n---\n\n# {name}\n\n'
                    '<!-- BEGIN GENERATED:source -->\n<!-- END GENERATED:source -->\n\n'
                    '## 언제 읽나\n\nTODO\n\n## 핵심 내용\n\nTODO\n\n## 적용 시 확인사항\n\nTODO\n\n'
                    '## 조항 목차\n\n<!-- BEGIN GENERATED:outline -->\n<!-- END GENERATED:outline -->\n\n'
                    '## 참조 관계\n\n<!-- BEGIN GENERATED:refs -->\n<!-- END GENERATED:refs -->\n')
    for k, v in gen.items():
        pat = re.compile(rf'(<!-- BEGIN GENERATED:{k} -->\n).*?(<!-- END GENERATED:{k} -->)', re.S)
        if not pat.search(existing):
            raise SystemExit(f'{path}/SKILL.md: GENERATED:{k} 블록이 없습니다')
        existing = pat.sub(lambda m: m.group(1) + '\n'.join(v) + '\n' + m.group(2), existing)
    return existing

ROUTER = 'workflows/lookup-clause'
DEF = re.compile(r'(?:^\d+\. |^[①-⑳] |^)["“]?([^"“”]{1,40}?)["”]?(?:이)?란 ')
CHO = 'ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ'

# 실무 표현·동의어 → 원문 용어. 블라인드 사용성 검토에서 색인 검색이 실패한 낱말을 중심으로 이 저장소가 붙였다.
# (별칭, 원문 용어, 조항, 비고). 생성 시 '원문 용어'가 그 조항(하위 포함) 원문에 실제로 있는지 검사한다.
ALIASES = [
    ('미불용지', '미지급용지', '810-6.2.3', '보상'),
    ('송전선로', '송전선로', '810-6.2.7', '보상: 보상이 이루어지지 않은 송전선로 등은 구애됨이 없이 평가'),
    ('송전선', '고압선등', '610-1.7.13', '일반 평가: 고압선등 통과 토지'),
    ('고압선', '고압선등', '610-1.7.13', '일반 평가'),
    ('어선', '선박', '640-3', ''),
    ('어장', '어장', '650-2.3.2', '어업권 평가에서 어장 전체 가액과 시설가액'),
    ('지장물', '건축물 등', '810-3', '정의만 있음. 건축물 등의 보상평가 절은 실무기준에 없음(관계법규 확인)'),
    ('아파트', '구분소유 부동산', '610-3.1', ''),
    ('오피스텔', '구분소유 부동산', '610-3.1', ''),
    ('집합건물', '구분소유 부동산', '610-3.1', ''),
    ('대지권', '대지사용권', '610-3.1', ''),
    ('상가 권리금', '권리금', '670-4', ''),
    ('투자부동산', '재무보고평가', '740', 'K-IFRS 공정가치'),
    ('K-IFRS', '한국채택국제회계기준', '740', ''),
    ('공정가치', '공정가치', '740-3', ''),
    ('재개발', '재개발사업등', '730-1', ''),
    ('재건축', '재건축사업', '730-1', ''),
    ('매도청구', '매도청구', '730-3.4', ''),
    ('수용', '토지등의 수용등', '730-3.5', '도시정비의 수용등은 토지보상법과 [800]을 따름'),
    ('구분지상권', '구분지상권', '820-5.2.1', ''),
    ('영업보상', '영업손실', '840', ''),
    ('휴업보상', '영업의 휴업', '840-6', ''),
    ('폐업보상', '영업의 폐지', '840-5', ''),
    ('일조', '일조침해', '670-2', ''),
    ('소음', '소음등', '670-2', ''),
    ('진동', '진동', '670-2', ''),
    ('환경오염', '환경오염', '670-2', ''),
    ('시가', '시장가치', '100-2', ''),
    ('감가상각', '감가수정', '400-3.2.1.3', ''),
    ('AVM', '자동가치산정모형', '200-5', ''),
    ('임대 중인 건물', '수익환원법', '400-3.4', '임대료 평가(670-3)가 아니라 수익방식 검토 자료'),
]

def section_text(secs, code):
    return '\n'.join(s['title'] + '\n' + '\n'.join(s['lines']) for s in secs
                     if s['code'] == code or s['code'].startswith(code + '.') or
                     (re.fullmatch(r'\d{3}', code) and s['code'].startswith(code + '-')))

def terms_index(secs):
    entries = set()
    for alias, term, code, note in ALIASES:
        if term not in section_text(secs, code):
            raise SystemExit(f'별칭 {alias}: 원문 용어 "{term}" 이(가) [{code}] 에 없습니다')
        o, _ = ref_target(code)
        entries.add((alias, code, o, f'별칭 → {term}' + (f' ({note})' if note else '')))
    for s in secs:
        o = owner(s['code'])
        if not o:
            continue
        for l in s['lines']:
            m = DEF.match(l)
            if m:
                term = re.sub(r'\(.*?\)', '', m.group(1)).strip()
                if term:
                    entries.add((term, s['code'], o, '정의'))
    count = collections.Counter(s['title'] for s in secs)
    for s in secs:
        o = owner(s['code'])
        # 여러 곳에 반복되는 제목(정의, 적용, 자료의 수집 및 정리 등)은 찾기에 쓸모가 없어 뺀다
        if o and s['code'] != '부칙' and count[s['title']] == 1:
            entries.add((s['title'], s['code'], o, '조항 제목'))
    def key(e):
        return e
    def initial(t):
        c = t[0]
        return CHO[(ord(c) - 0xAC00) // 588] if '가' <= c <= '힣' else '기타'
    L = ['# 용어·조항 색인 — 감정평가 실무기준', '',
         '> tools/split_standard.py 가 원문에서 자동 생성한다(직접 고치지 말 것).',
         '> 원문의 정의 조항("…"이란 …을 말한다)에 나오는 용어와 한 번만 쓰인 조항 제목, 그리고 실무 표현을',
         '> 원문 용어로 잇는 "별칭"(이 저장소가 붙인 것, tools/split_standard.py 의 ALIASES)을 모았다.',
         '> 여기서 못 찾으면 원문을 직접 검색한다: grep -rn "<낱말>" appraisal-practice-standards --include=source.md',
         '> 질문·의뢰서의 낱말로 이 파일을 검색(grep)해 조항과 스킬을 찾은 뒤, 그 스킬의 source.md 로 확인한다.', '']
    cur = None
    for e in sorted(entries, key=key):
        ini = initial(e[0])
        if ini != cur:
            if cur is not None:
                L.append('')
            L += [f'## {ini}', '', '| 용어 | 종류 | 조항 | 스킬 |', '|---|---|---|---|']
            cur = ini
        up = '../' * len(ROUTER.split('/'))
        L.append(f'| {e[0]} | {e[3]} | [{e[1]}] | [{skill_name(e[2])}]({up}{e[2]}/SKILL.md) |')
    return '\n'.join(L) + '\n'

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    check = '--check' in sys.argv
    secs = parse(SRC.read_text(encoding='utf-8'))
    files, unassigned = build(secs)
    bad = 0
    if unassigned:
        print('배정되지 않은 조항:', unassigned); bad = 1
    for rp, content in files.items():
        f = ROOT / rp
        if rp.endswith('SKILL.md'):
            old = f.read_text(encoding='utf-8') if f.exists() else None
            content = render_skill(old, rp[len(COLL) + 1:-len('/SKILL.md')], content)
        else:
            old = f.read_text(encoding='utf-8') if f.exists() else None
        if old != content:
            if check:
                print('갱신 필요:', rp); bad = 1
            else:
                f.parent.mkdir(parents=True, exist_ok=True)
                f.write_bytes((content).encode('utf-8'))
    # 컬렉션 README 색인
    titles = {s['code']: s['title'] for s in secs}
    rows = ['| 조항 | 제목 | 스킬 |', '|---|---|---|']
    for path, sels in SKILLS.items():
        for c in sels:
            title = '부칙(개정 이력)' if c == '부칙' else titles.get(c, '')
            rows.append(f'| [{c}] | {title} | [{skill_name(path)}]({path}/SKILL.md) |')
    readme = ROOT / COLL / 'README.md'
    old = readme.read_text(encoding='utf-8')
    new = re.sub(r'(<!-- BEGIN GENERATED:index -->\n).*?(<!-- END GENERATED:index -->)',
                 lambda m: m.group(1) + '\n'.join(rows) + '\n' + m.group(2), old, flags=re.S)
    if new != old:
        if check:
            print('갱신 필요:', readme.relative_to(ROOT)); bad = 1
        else:
            readme.write_bytes((new).encode('utf-8'))
    # 라우터의 찾기용 색인(terms.md): 원문의 정의 용어 + 고유한 조항 제목 → 조항 → 스킬
    tf = ROOT / COLL / ROUTER / 'terms.md'
    tnew = terms_index(secs)
    told = tf.read_text(encoding='utf-8') if tf.exists() else None
    if tnew != told:
        if check:
            print('갱신 필요:', tf.relative_to(ROOT)); bad = 1
        else:
            tf.write_bytes((tnew).encode('utf-8'))
    total = sum(len(s['lines']) for s in secs)
    print(f'조항 {len(secs)}개, 본문 {total}줄, 스킬 {len(SKILLS)}개' + (' — 검사 통과' if check and not bad else ''))
    return bad

if __name__ == '__main__':
    sys.exit(main())
