#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""스킬 간 링크를 스킬 이름 기준으로 다시 계산한다 (폴더를 옮긴 뒤 실행).

usage: python -I tools/fix_links.py
`](<무엇이든>/<스킬이름>/SKILL.md)` 형태의 링크를, 저장소에서 그 이름을 가진 스킬 폴더까지의 상대경로로 바꾼다.
source.md 는 split_standard.py 가 만드므로 건드리지 않는다.
"""
import os, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
LINK = re.compile(r'\]\(([^)\s]*?)([a-z0-9-]+)/SKILL\.md\)')

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    loc = {}
    for f in ROOT.rglob('SKILL.md'):
        if '.git' not in f.parts:
            loc[f.parent.name] = f
    changed = 0
    for md in ROOT.rglob('*.md'):
        if '.git' in md.parts or md.name == 'source.md':
            continue
        t = md.read_text(encoding='utf-8')
        def fix(m):
            f = loc.get(m.group(2))
            if not f:
                return m.group(0)
            return '](' + os.path.relpath(f, md.parent).replace(os.sep, '/') + ')'
        t2 = LINK.sub(fix, t)
        if t2 != t:
            md.write_bytes((t2).encode('utf-8')); changed += 1
    print('files changed:', changed)

if __name__ == '__main__':
    main()
