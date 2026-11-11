#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Stage tracked Markdown for MkDocs without modifying canonical documents."""
import argparse
from collections import defaultdict
import html
import json
from pathlib import Path
import posixpath
import re
import shutil
import subprocess
import sys
from urllib.parse import quote, unquote, urlsplit, urlunsplit

sys.path.insert(0, str(Path(__file__).resolve().parent))
from markdown_prose import prose_parts

ROOT = Path(__file__).resolve().parents[1]
REPO = 'https://github.com/pacappkor/kapa_skills'
HEADER = '<!-- SPDX-License-Identifier: GPL-3.0-only -->\n\n'
INLINE = re.compile(r'(!?\[[^\]\n]*\]\()(?P<url><[^>]+>|[^\s)]+)(?P<tail>[^\n)]*\))')
REFERENCE = re.compile(r'(?m)^( {0,3}\[[^\]\n]+\]:\s*)(?P<url><[^>]+>|\S+)')
HTML_URL = re.compile(r'(?P<prefix>\b(?:href|src)=[\"\x27])(?P<url>[^\"\x27]+)', re.I)


def tracked_files(root):
    data = subprocess.check_output(['git', '-C', str(root), 'ls-files', '-z'])
    return {Path(p) for p in data.decode('utf-8').split('\0') if p}


def relative(target, source):
    return posixpath.relpath(target.as_posix(), source.parent.as_posix())


def rewrite_links(text, source, root, pages, tracked, broken):
    """Rewrite local Markdown/HTML/reference links, leaving code examples intact."""
    def url(value):
        angled = value.startswith('<') and value.endswith('>')
        value = value[1:-1] if angled else value
        parts = urlsplit(html.unescape(value))
        if parts.scheme or parts.netloc or not parts.path:
            return '<' + value + '>' if angled else value
        raw = unquote(parts.path)
        target = Path(posixpath.normpath(posixpath.join(source.parent.as_posix(), raw)))
        if raw.startswith('/') or target.as_posix().startswith('../'):
            broken.append(f'{source}: outside repository: {value}')
            return value
        if target in pages:
            path = quote(relative(pages[target], pages.get(source, source)), safe='/.-_')
        elif target in tracked and (root / target).is_file():
            if target.suffix.lower() in {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp'}:
                path = quote(relative(target, pages.get(source, source)), safe='/.-_')
            else:
                # Non-document source data/code is browsed on GitHub, never loaded as text.
                path = REPO + '/blob/main/' + quote(target.as_posix(), safe='/.-_')
        else:
            broken.append(f'{source}: missing target: {value}')
            return value
        result = urlunsplit(('', '', path, parts.query, parts.fragment))
        return '<' + result + '>' if angled else result

    def prose(part):
        part = INLINE.sub(lambda m: m[1] + url(m['url']) + m['tail'], part)
        part = REFERENCE.sub(lambda m: m[1] + url(m['url']), part)
        return HTML_URL.sub(lambda m: m['prefix'] + url(m['url']), part)

    # prose_parts intentionally protects HTML blocks; handle their attributes separately.
    return ''.join(prose(part) if active else HTML_URL.sub(
        lambda m: m['prefix'] + url(m['url']), part) if part.lstrip().startswith('<') else part
        for active, part in prose_parts(text))


def skill_index(skills):
    groups = defaultdict(list)
    for path in sorted(skills):
        category = '/'.join(path.parts[:-2]) or '입구'
        groups[category].append(path)
    lines = [HEADER + '# 스킬 색인', '분류별 입구·작업 절차·내용 스킬. 원문과 판본을 함께 확인한다.']
    for category, paths in sorted(groups.items()):
        lines += ['', '## ' + category, '']
        lines += [f'- [{p.parent.name}]({p.as_posix()})' for p in paths]
    return '\n'.join(lines) + '\n'


def law_index(index):
    lines = [HEADER + '# 법령·실무기준 색인', '수집된 현행 판본의 색인이다. 현시점의 법적 유효성을 보증하지 않는다.']
    for law_id, law in sorted(index['laws'].items(), key=lambda pair: (pair[1]['collection'], pair[1]['name'])):
        seq = law['current']['lsiSeq']
        lines += ['', '## ' + law['name'], '',
                  f"- 컬렉션: {law['collection']} · 시행일: {law['current']['efYd']} · lsiSeq: {seq}",
                  f'- [국가법령정보센터 원문](https://www.law.go.kr/LSW/lsInfoP.do?lsiSeq={seq})', '']
        for key, article in sorted(index['articles'].items()):
            if key.startswith(f'law/{law_id}@'):
                label = key.split('#', 1)[1] + ' ' + article['title']
                if article.get('deleted'):
                    label += ' (삭제)'
                lines.append(f"- [{label}]({article['skill']})")
    lines += ['', '## 감정평가 실무기준', '']
    for key, section in sorted(index['standards'].items()):
        lines.append(f"- [{key.split('#', 1)[1]} {section['title']}]({section['skill']})")
    return '\n'.join(lines) + '\n'


def build(root=ROOT, output=None, strict=False):
    root = root.resolve()
    output = (output or root / '.site-src').resolve()
    # Only this dedicated, disposable staging directory may be removed.
    if output != root / '.site-src':
        raise ValueError('output must be the repository .site-src directory')
    if output.is_symlink():
        raise ValueError('staging directory must not be a symlink')
    tracked = tracked_files(root)
    markdown = sorted(p for p in tracked if p.suffix.lower() == '.md'
                      and not any(part.startswith('.') for part in p.parts))
    pages = {p: p.with_name('overview.md') if p.name == 'README.md' else p for p in markdown}
    directories = {Path('.')}
    for p in markdown:
        directories.update(p.parents)
    generated = {}
    for directory in sorted(directories):
        readme = directory / 'README.md'
        dest = pages[readme] if readme in pages else directory / 'index.md'
        pages[directory] = dest
        if readme not in pages:
            children = [p for p in markdown if p.parent == directory]
            subdirs = sorted(d for d in directories if d != directory and d.parent == directory)
            generated[dest] = HEADER + '# ' + (directory.as_posix() if directory != Path('.') else '문서') + '\n\n' + '\n'.join(
                f'- [{p.name}]({relative(p, dest)})' for p in children + subdirs) + '\n'
    skills = {p.parent.name: p for p in markdown if p.name == 'SKILL.md'}
    graph = json.loads((root / 'docs/graph.json').read_text(encoding='utf-8'))
    related = defaultdict(set)
    for edge in graph:
        if edge['src'] not in skills or edge['dst'] not in skills:
            raise ValueError(f'graph references unknown skill: {edge}')
        related[edge['src']].add(edge['dst'])
        related[edge['dst']].add(edge['src'])
    generated[Path('skills-index.md')] = skill_index(skills.values())
    generated[Path('law-index.md')] = law_index(json.loads((root / 'docs/law-index.json').read_text(encoding='utf-8')))
    # Root README links share the home's base directory. Keep its introduction current.
    intro = (root / 'README.md').read_text(encoding='utf-8').split('\n## ', 1)[0]
    start = (root / '00-kapa-start/SKILL.md').read_text(encoding='utf-8')
    description = re.search(r'(?m)^description:\s*(.+)$', start)
    generated[Path('index.md')] = HEADER + intro.rstrip() + '\n\n## 업무별 시작\n\n' + (
        description[1] + '\n\n' if description else '') + '\n'.join([
        '- [저장소 안내](README.md)', '- [00-kapa-start: 업무별 시작](00-kapa-start/SKILL.md)',
        '- [분류별 스킬 색인](skills-index.md)', '- [법령·실무기준 색인](law-index.md)',
        '- [읽기 규칙](rules/skill-reading-rules/SKILL.md)', '- [라이선스와 출처·면책](NOTICE.md)']) + '\n'
    pages.update({p: p for p in generated})
    documents = {p: (root / p).read_text(encoding='utf-8') for p in markdown}
    for p in markdown:
        if p.name == 'SKILL.md' and related[p.parent.name]:
            documents[p] += '\n## 관련 스킬 (인용 그래프)\n\n' + '\n'.join(
                f'- [{name}]({relative(skills[name], p)})' for name in sorted(related[p.parent.name])) + '\n'
    for p, text in list(documents.items()):
        # Generated views have no editable source; overview aliases edit the canonical README.
        if not text.startswith('---\n'):
            documents[p] = f'---\nedit_uri: {p.as_posix()}\n---\n\n' + text
    documents.update({p: '---\nedit_uri: ""\n---\n\n' + text for p, text in generated.items()})
    broken = []
    rendered = {pages[p]: rewrite_links(text, p, root, pages, tracked, broken) for p, text in documents.items()}
    for issue in broken:
        print(issue)
    if strict and broken:
        raise ValueError(f'{len(broken)} broken local links')
    if output.exists():
        shutil.rmtree(output)
    output.mkdir()
    for p, text in rendered.items():
        dest = output / p
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding='utf-8', newline='\n')
    for p in tracked:
        if p.parts[0] == 'sources' and p.suffix.lower() in {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp'}:
            dest = output / p
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(root / p, dest)
    print(f'Staged {len(rendered)} pages; {len(broken)} broken local links')
    return len(rendered), broken


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--strict', action='store_true')
    args = parser.parse_args()
    try:
        build(strict=args.strict)
    except (ValueError, OSError) as exc:
        parser.exit(1, f'{exc}\n')


if __name__ == '__main__':
    main()
