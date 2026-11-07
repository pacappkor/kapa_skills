#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""국가법령정보센터(law.go.kr)에서 「감정평가 실무기준」 본문을 받아 텍스트로 저장한다.

usage: python -I tools/fetch_standard.py [admRulSeq] [admRulId]
       python -I tools/fetch_standard.py --check   현행 고시가 저장소 판본(split_standard.SEQ)과 같은지 확인 (다르면 종료 코드 1)
  인자가 없으면 저장소 판본(split_standard.SEQ)을 다시 받는다. admRulId 기본값 2066025 (「감정평가 실무기준」의 행정규칙 ID).
출력: sources/appraisal-practice-standards/<admRulSeq>.txt (태그 제거, 줄 단위)
      본문 속 산식 이미지는 '[원문 이미지 flSeq=N]' 줄로 남기고 같은 폴더에 img-<N>.gif 로 저장한다.

행정규칙 화면(admRulInfoP.do)은 본문을 AJAX(admRulInfoR.do)로 불러오므로 그 엔드포인트를 직접 호출한다.
개정 고시가 나오면 새 admRulSeq 로 다시 받고 tools/split_standard.py 를 실행한 뒤 차이를 검토한다.
"""
import html, pathlib, re, sys, urllib.parse, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent

def fetch(seq, rid):
    page = f'https://www.law.go.kr/LSW//admRulInfoP.do?admRulSeq={seq}'
    data = urllib.parse.urlencode(dict(admRulSeq=seq, admRulId=rid, joTpYn='N', languageType='KO',
                                       chrClsCd='010202', preview='', urlMode='')).encode()
    req = urllib.request.Request('https://www.law.go.kr/LSW/admRulInfoR.do', data=data,
                                 headers={'User-Agent': 'Mozilla/5.0', 'Referer': page})
    return urllib.request.urlopen(req, timeout=60).read().decode('utf-8', 'replace')

def to_text(h):
    h = re.sub(r'(?is)<(script|style)\b.*?</\1>', ' ', h)
    # 본문 속 산식 이미지: 자리 표시 줄로 남긴다 (전사는 split_standard.py 의 IMAGE_TEXT)
    h = re.sub(r'<img alt="img(\d+)"[^>]*>', r'\n[원문 이미지 flSeq=\1]\n', h)
    h = re.sub(r'(?i)<br\s*/?>|</(p|div|li|tr|h\d)>', '\n', h)
    t = html.unescape(re.sub(r'<[^>]+>', ' ', h))
    lines = [re.sub(r'[ \t ]+', ' ', l).strip() for l in t.split('\n')]
    out = []
    for l in lines:
        # 부칙 제목 줄에 남는 버튼 속성 조각 제거: '... 부 칙 <제2023-522호, 2023. 9. 13.>'
        m = re.search(r'부\s*칙\s*(<제[^>]+>)', l)
        if m and ('href' in l or 'src=' in l):
            l = '부칙 ' + m.group(1)
        if l:
            out.append(l)
    return '\n'.join(out) + '\n'

def current_seq():
    """국가법령정보센터가 현행으로 보여 주는 「감정평가 실무기준」의 admRulSeq."""
    u = 'https://www.law.go.kr/' + urllib.parse.quote('행정규칙') + '/' + urllib.parse.quote('감정평가실무기준')
    h = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'}), timeout=60).read().decode('utf-8', 'replace')
    seqs = sorted(set(re.findall(r'''admRulSeq["'=:\s]+["']?(\d+)''', h)))
    if len(seqs) != 1:
        sys.exit(f'현행 admRulSeq 를 하나로 특정하지 못했습니다: {seqs} (화면 구조 변경 여부 확인)')
    return seqs[0]

def repo_seq():
    """저장소 판본: tools/split_standard.py 의 SEQ."""
    return re.search(r"^SEQ = '(\d+)'", (ROOT / 'tools' / 'split_standard.py').read_text(encoding='utf-8'), re.M).group(1)

def check():
    have = repo_seq()
    cur = current_seq()
    if cur == have:
        print(f'실무기준: 저장소 판본과 같은 현행 고시입니다 (admRulSeq={cur})')
        return 0
    print(f'실무기준: 새 고시가 있습니다 — 저장소 admRulSeq={have}, 현행 admRulSeq={cur}')
    print(f'  화면: https://www.law.go.kr/LSW//admRulInfoP.do?admRulSeq={cur}')
    return 1

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    if '--check' in sys.argv:
        sys.exit(check())
    seq = sys.argv[1] if len(sys.argv) > 1 else repo_seq()
    rid = sys.argv[2] if len(sys.argv) > 2 else '2066025'
    t = to_text(fetch(seq, rid))
    i = t.find('감정평가 실무기준')
    if i < 0:
        sys.exit('본문을 찾지 못했습니다 (엔드포인트/파라미터 변경 여부 확인)')
    out = ROOT / 'sources' / 'appraisal-practice-standards' / f'{seq}.txt'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes((t[i:]).encode('utf-8'))
    for fl in re.findall(r'\[원문 이미지 flSeq=(\d+)\]', t[i:]):
        img = out.parent / f'img-{fl}.gif'
        req = urllib.request.Request(f'https://www.law.go.kr/LSW/flDownload.do?flSeq={fl}',
                                     headers={'User-Agent': 'Mozilla/5.0',
                                              'Referer': f'https://www.law.go.kr/LSW//admRulInfoP.do?admRulSeq={seq}'})
        img.write_bytes(urllib.request.urlopen(req, timeout=60).read())
        print(img.relative_to(ROOT))
    print(out.relative_to(ROOT), len(t[i:]), 'chars')

if __name__ == '__main__':
    main()
