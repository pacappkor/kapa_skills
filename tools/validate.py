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
  - rules/: 읽기 규칙(skill-reading-rules)과 갱신 절차(skill-update-maintenance)의 분리.
    갱신 명령·절차는 갱신 스킬에만, 입구·AGENTS·CLAUDE 는 읽기 규칙을 가리킨다
  - laws: tools/laws/build_laws.py --check (조문 배정·생성물 최신·요약의 조문 인용 누락)
  - appraisal-practice-standards: 입구(00-practice-standards-start)와 workflows/ 가 모든 스킬을 언급하고,
    tools/split_standard.py --check 가 통과함(원문 배정·생성 블록 최신)
종료 코드: 오류가 있으면 1.
"""
import pathlib, re, subprocess, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from markdown_prose import original_text, prose_parts

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

# 읽기 규칙과 갱신 절차의 분리 (rules/)
RULES = {'skill-reading-rules': 'reading', 'skill-update-maintenance': 'update'}
MAINT = re.compile(r'python -I|tools/|\b[a-z_]+\.py\b|fetch_laws|build_laws|split_standard|handoff_scan|annex_prep|diff_laws|CHANGELOG|\bgit\b')
MAINT_READING = re.compile(r'배정표|브랜치|커밋|\bPR\b')
READING_HEAD = re.compile(r'^##\s.*(읽는 순서|인용 형식|우선순위|판본)', re.M)
ENTRIES = ['00-kapa-start/SKILL.md', 'laws/00-laws-start/SKILL.md',
           'appraisal-practice-standards/00-practice-standards-start/SKILL.md', 'AGENTS.md', 'CLAUDE.md']

def check_rules(skills, errors):
    rules_dir = ROOT / 'rules'
    found = {f.parent.name for f in skills if rules_dir in f.parents}
    if found != set(RULES):
        errors.append(f'rules/: 스킬은 정확히 {sorted(RULES)} 이어야 함 (현재 {sorted(found)})')
    update_dir = rules_dir / 'skill-update-maintenance'
    for f in skills:
        if f.parent == update_dir:
            continue
        rel_dir = f.parent.relative_to(ROOT).as_posix()
        for md in sorted(f.parent.rglob('*.md')):
            t = md.read_text(encoding='utf-8')
            rel = md.relative_to(ROOT).as_posix()
            for m in MAINT.finditer(t):
                line = t.count('\n', 0, m.start()) + 1
                errors.append(f'{rel}:{line}: 갱신 절차 내용({m.group(0)!r})은 skill-update-maintenance 에만 둔다')
                break
            if md.name == 'SKILL.md' and 'skill-update-maintenance/SKILL.md' in t and \
                    rel not in ENTRIES and f.parent.name != 'skill-reading-rules':
                errors.append(f'{rel}: skill-update-maintenance 링크는 입구 스킬과 skill-reading-rules 에서만 둔다')
            if f.parent.name == 'skill-reading-rules' and MAINT_READING.search(t):
                errors.append(f'{rel}: 읽기 규칙에 갱신 작업 용어({MAINT_READING.search(t).group(0)!r})가 있음')
    upd = update_dir / 'SKILL.md'
    if upd.exists():
        t = upd.read_text(encoding='utf-8')
        if READING_HEAD.search(t):
            errors.append(f'rules/skill-update-maintenance/SKILL.md: 읽기 규칙 절({READING_HEAD.search(t).group(0)!r})은 skill-reading-rules 에 둔다')
        if 'skill-reading-rules/SKILL.md' not in t:
            errors.append('rules/skill-update-maintenance/SKILL.md: skill-reading-rules 를 범위 밖으로 링크해야 함')
    for e in ENTRIES:
        f = ROOT / e
        if f.exists() and 'skill-reading-rules' not in f.read_text(encoding='utf-8'):
            errors.append(f'{e}: skill-reading-rules 를 가리켜야 함')

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
        if not original_text(md.relative_to(ROOT)) and any('~' in part for prose, part in prose_parts(t) if prose):
            errors.append(f'{md.relative_to(ROOT).as_posix()}: Markdown 본문의 물결표는 en dash(–)로 쓴다')
        for target in re.findall(r'\]\(([^)\s]+)\)', t):
            if re.match(r'[a-z]+:', target) or target.startswith('#'):
                continue
            if not (md.parent / target.split('#')[0]).exists():
                errors.append(f'{md.relative_to(ROOT).as_posix()}: 깨진 링크 {target}')
    check_rules(skills, errors)
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
    if (ROOT / 'laws').exists():
        r = subprocess.run([sys.executable, '-I', str(ROOT / 'tools' / 'laws' / 'build_laws.py'), '--check'],
                           capture_output=True, text=True, encoding='utf-8')
        if r.returncode:
            bad = [l for l in r.stdout.splitlines() if l.startswith('ERROR')]
            errors.append(f'build_laws.py --check 실패 ({len(bad)}건): ' + '; '.join(bad[:5]))
    r = subprocess.run([sys.executable, '-I', str(ROOT / 'tools' / 'graph.py'), '--check'],
                       capture_output=True, text=True, encoding='utf-8')
    if r.returncode:
        errors.append('graph.py --check 실패(들어오는 연결 블록 갱신 필요): ' + r.stdout.strip().splitlines()[0])
    r = subprocess.run([sys.executable, '-I', str(ROOT / 'tools/laws/build_index.py'), '--check'],
                       capture_output=True, text=True, encoding='utf-8')
    if r.returncode:
        errors.append('build_index.py --check 실패: ' + (r.stdout + r.stderr).strip())
    print(f'skills: {len(skills)}  errors: {len(errors)}')
    for e in errors:
        print('ERROR', e)
    return 1 if errors else 0

if __name__ == '__main__':
    sys.exit(main())
