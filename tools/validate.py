#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""스킬 저장소 구조 검증.

usage: python -I tools/validate.py
검사 항목
  - 모든 SKILL.md: frontmatter 의 name 이 폴더 이름과 같고, 저장소 전체에서 유일하며, 소문자·숫자·하이픈만 사용
  - description: 한 줄, 140자 이하, TODO 아님
  - 본문에 TODO 가 남아 있지 않음
  - leaf rule: SKILL.md 가 있는 폴더 아래에 또 다른 SKILL.md 가 없음 (스킬 안의 스킬 금지)
  - 상대 링크(](...)) 대상 파일이 실제로 있음
  - appraisal-practice-standards: 입구(00-practice-standards-start)와 workflows/ 가 모든 스킬을 언급하고,
    tools/split_standard.py --check 가 통과함(원문 배정·생성 블록 최신)
종료 코드: 오류가 있으면 1.
"""
import pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKIP = {'.git', 'sources', 'tools', '.github'}

def frontmatter(t):
    m = re.match(r'^---\n(.*?)\n---\n', t, re.S)
    if not m:
        return None
    d = {}
    for line in m.group(1).split('\n'):
        if ':' in line and not line.startswith(' '):
            k, v = line.split(':', 1)
            d[k.strip()] = v.strip()
    return d

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    errors = []
    skills = sorted(p for p in ROOT.rglob('SKILL.md') if not SKIP & set(p.relative_to(ROOT).parts))
    names = {}
    for f in skills:
        rel = f.relative_to(ROOT).as_posix()
        t = f.read_text(encoding='utf-8')
        fm = frontmatter(t)
        if fm is None:
            errors.append(f'{rel}: frontmatter 없음'); continue
        name, desc = fm.get('name', ''), fm.get('description', '')
        if name != f.parent.name:
            errors.append(f'{rel}: name({name}) != 폴더 이름({f.parent.name})')
        if not re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)*', name):
            errors.append(f'{rel}: name 형식 위반 ({name})')
        if name in names:
            errors.append(f'{rel}: name 중복 ({names[name]})')
        names[name] = rel
        if not desc or desc == 'TODO' or len(desc) > 140:
            errors.append(f'{rel}: description 누락/TODO/140자 초과 ({len(desc)}자)')
        if re.search(r'\bTODO\b', t):
            errors.append(f'{rel}: TODO 남음')
        for anc in f.parent.parents:
            if anc == ROOT:
                break
            if (anc / 'SKILL.md').exists():
                errors.append(f'{rel}: 상위 폴더 {anc.relative_to(ROOT).as_posix()} 도 스킬 (leaf rule 위반)')
    for md in sorted(ROOT.rglob('*.md')):
        if '.git' in md.parts:
            continue
        t = md.read_text(encoding='utf-8')
        for target in re.findall(r'\]\(([^)\s]+)\)', t):
            if re.match(r'[a-z]+:', target) or target.startswith('#'):
                continue
            if not (md.parent / target.split('#')[0]).exists():
                errors.append(f'{md.relative_to(ROOT).as_posix()}: 깨진 링크 {target}')
    coll = ROOT / 'appraisal-practice-standards'
    if coll.exists():
        # 입구와 작업 절차(workflows) 파일들이 컬렉션의 모든 내용 스킬을 한 번 이상 언급해야 한다
        nav = ''.join(f.read_text(encoding='utf-8') for d in [coll / '00-practice-standards-start', coll / 'workflows']
                      for f in d.rglob('*.md'))
        for f in skills:
            if coll in f.parents and f.parent.name not in nav:
                errors.append(f'navigation: {f.parent.name} 이(가) 입구·workflows 어디에도 없음')
        r = subprocess.run([sys.executable, '-I', str(ROOT / 'tools' / 'split_standard.py'), '--check'],
                           capture_output=True, text=True, encoding='utf-8')
        if r.returncode:
            errors.append('split_standard.py --check 실패: ' + r.stdout.strip())
    print(f'skills: {len(skills)}  errors: {len(errors)}')
    for e in errors:
        print('ERROR', e)
    return 1 if errors else 0

if __name__ == '__main__':
    sys.exit(main())
