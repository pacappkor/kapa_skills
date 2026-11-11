#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""저장소 전체 인용 그래프: 모든 스킬의 '나가는 인용'(생성 블록 refs)을 모아 뒤집어,
각 스킬의 `<!-- BEGIN GENERATED:incoming -->` 블록에 '들어오는 연결'을 쓴다.
어느 스킬에서 출발해도 양방향으로 이동할 수 있게 하는 것이 목적이다
(예: 도로법 연결 조항 → 토지보상법 → 실무기준 보상평가, 그리고 그 역방향).

간선의 출처
  1. 각 SKILL.md 의 GENERATED:refs 블록에 있는 스킬 링크 (실무기준 생성기·법령 생성기가 원문 인용에서 만든 것)
  2. 법령 원문(source.md)에서 토지보상법을 조문 번호 없이 언급한 경우 → 토지보상법 입구(00-lca-start)
     (예: "「공익사업을 위한 토지 등의 취득 및 보상에 관한 법률」을 준용한다")

usage: python -I tools/graph.py [--check] [--json]
  --check : 쓰지 않고 최신 여부만 검사 (불일치 시 종료 코드 1)
  --json  : docs/graph.json 에 간선 목록도 쓴다
"""
import collections, json, pathlib, posixpath, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKIP = {'.git', 'sources', 'tools', '.site-src', 'site', '.venv-docs'}
REFS = re.compile(r'<!-- BEGIN GENERATED:refs -->\n(.*?)<!-- END GENERATED:refs -->', re.S)
INC = re.compile(r'(<!-- BEGIN GENERATED:incoming -->\n).*?(<!-- END GENERATED:incoming -->)', re.S)
LINK = re.compile(r'\[([a-z0-9-]+)\]\(([^)\s]+/SKILL\.md)\)')
LCA = re.compile(r'「\s*공익사업을\s*위한\s*토지\s*등의\s*취득\s*및\s*보상에\s*관한\s*법률\s*」(?!\s*(?:시행령|시행규칙)?\s*제\s*\d+\s*조)')

def skills():
    out = {}
    for f in sorted(ROOT.rglob('SKILL.md')):
        if SKIP & set(f.relative_to(ROOT).parts):
            continue
        out[f.parent.name] = f
    return out

def coll_of(f):
    p = f.relative_to(ROOT).parts
    return '/'.join(p[:2]) if p[0] == 'laws' and len(p) > 2 else p[0]

def edges(sk):
    E = collections.defaultdict(set)    # (src, dst) -> labels
    for name, f in sk.items():
        t = f.read_text(encoding='utf-8')
        m = REFS.search(t)
        if m:
            # '이 스킬의 조항을 인용하는 다른 스킬' 문단은 들어오는 쪽이므로 건너뛴다
            paras = re.split(r'\n\s*\n', m.group(1))
            out_lines = [l for p in paras if not p.lstrip().startswith('이 스킬의 조항을 인용하는') for l in p.splitlines()]
            for line in out_lines:
                labels = re.findall(r'`([^`]+)`', line)
                for _, target in LINK.findall(line):
                    dst = posixpath.basename(posixpath.dirname(target))
                    if dst in sk and dst != name:
                        E[(name, dst)].update(labels or ['(인용)'])
        src = f.parent / 'source.md'
        if f.relative_to(ROOT).parts[0] == 'laws' and src.exists() and not name.startswith('lca-') and '00-lca-start' in sk:
            if LCA.search(src.read_text(encoding='utf-8')):
                E[(name, '00-lca-start')].add('토지보상법 준용·인용(조문 미특정)')
    return E

def render(name, f, inc, sk):
    if not inc:
        return ['(이 저장소의 다른 스킬이 이 스킬의 원문을 직접 인용하지 않음)']
    groups = collections.defaultdict(list)
    for src, labels in inc:
        groups[coll_of(sk[src])].append((src, labels))
    lines = ['이 스킬의 원문을 인용·준용하는 다른 스킬이다. 출발점이 그쪽이라면 여기로, 여기서 출발했다면 그쪽으로 이동한다.']
    for g in sorted(groups):
        lines += ['', f'**{g}**']
        for src, labels in sorted(groups[g]):
            # 'A 제1조: 「B」 제2조' 형식은 인용하는 조문(A 제1조)별로 묶어 모두 보인다
            byfrom, plain = collections.defaultdict(list), []
            for x in sorted(labels):
                if ': ' in x:
                    a_, b_ = x.split(': ', 1)
                    byfrom[a_].append(re.sub(r'「[^」]*」\s*', '', b_))
                else:
                    plain.append(x)
            parts = [f'`{a_} → {", ".join(sorted(set(v), key=lambda s: [int(n) for n in re.findall(r"\d+", s)] or [0]))}`' for a_, v in sorted(byfrom.items())]
            parts += [f'`{x}`' for x in plain]
            shown = ', '.join(parts)
            rel = posixpath.relpath(sk[src].relative_to(ROOT).as_posix(), f.parent.relative_to(ROOT).as_posix())
            lines.append(f'- [{src}]({rel}) — {shown}')
    return lines

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    check = '--check' in sys.argv
    sk = skills()
    E = edges(sk)
    incoming = collections.defaultdict(list)
    for (s, d), labels in E.items():
        incoming[d].append((s, labels))
    bad = changed = 0
    for name, f in sk.items():
        t = f.read_text(encoding='utf-8')
        if not (f.parent / 'source.md').exists() and not incoming.get(name):
            # 원문이 없는 입구·절차 스킬은 들어오는 연결이 있을 때만 블록을 둔다
            new = re.sub(r'\n*## 들어오는 연결\n\n<!-- BEGIN GENERATED:incoming -->\n.*?<!-- END GENERATED:incoming -->\n', '\n', t, flags=re.S)
            new = new.rstrip('\n') + '\n'
            if new != t:
                if check:
                    print('갱신 필요:', f.relative_to(ROOT).as_posix()); bad = 1
                else:
                    f.write_bytes(new.encode('utf-8')); changed += 1
            continue
        block = render(name, f, incoming.get(name, []), sk)
        if INC.search(t):
            new = INC.sub(lambda m: m.group(1) + '\n'.join(block) + '\n' + m.group(2), t)
        else:
            blk = '## 들어오는 연결\n\n<!-- BEGIN GENERATED:incoming -->\n' + '\n'.join(block) + '\n<!-- END GENERATED:incoming -->\n'
            new = t.rstrip('\n') + '\n\n' + blk
        if new != t:
            if check:
                print('갱신 필요:', f.relative_to(ROOT).as_posix()); bad = 1
            else:
                f.write_bytes(new.encode('utf-8')); changed += 1
    if '--json' in sys.argv and not check:
        (ROOT / 'docs').mkdir(exist_ok=True)
        data = [dict(src=s, dst=d, labels=sorted(l)) for (s, d), l in sorted(E.items())]
        (ROOT / 'docs' / 'graph.json').write_bytes((json.dumps(data, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
    print(f'스킬 {len(sk)}개, 간선 {len(E)}개' + ('' if check else f', 갱신 {changed}개') + (' — 검사 통과' if check and not bad else ''))
    return bad

if __name__ == '__main__':
    sys.exit(main())
