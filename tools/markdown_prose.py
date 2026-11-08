# SPDX-License-Identifier: GPL-3.0-only
"""Locate Markdown prose, leaving fenced blocks and backtick code spans intact."""
import re

# Inspected original legal text: the fruit-transplanting-season annex uses literal tildes.
# All generated source.md files stay verbatim, including this annex's copied table.
ORIGINAL_TILDE_FILES = {'sources/laws/land-compensation-act/annex-md/rule-16319785.md'}


def original_text(path):
    return path.name == 'source.md' or path.as_posix() in ORIGINAL_TILDE_FILES


def inline_tail(text):
    """Limit delimiter matching to this paragraph/inline block."""
    lines = text.splitlines(keepends=True)
    tail = lines[:1]
    for line in lines[1:]:
        marker = re.match(r'^ {0,3}(`{3,}|~{3,})(.*)', line)
        fence = marker and (marker[1][0] != '`' or '`' not in marker[2])
        block = re.match(r'^(?: {4}|\t| {0,3}(?:#{1,6}(?:\s|$)|>|[-+*]\s|\d+[.)]\s|(?:[-*_]\s*){3,}$|[=-]+\s*$|</?[A-Za-z]|<!--|<\?|<![A-Z]|<!\[CDATA\[))', line)
        if not line.strip() or fence or block:
            break
        tail.append(line)
    return ''.join(tail)


# CommonMark HTML blocks: raw-text elements (type 1), explicit terminators
# (types 2-5), and blank-line-terminated block/standalone tags (types 6-7).
HTML_BLOCK_TAGS = (
    'address|article|aside|base|basefont|blockquote|body|caption|center|col|colgroup|'
    'dd|details|dialog|dir|div|dl|dt|fieldset|figcaption|figure|footer|form|'
    'frame|frameset|h[1-6]|head|header|hr|html|iframe|legend|li|link|main|menu|'
    'menuitem|nav|noframes|ol|optgroup|option|p|param|search|section|summary|'
    'table|tbody|td|tfoot|th|thead|title|tr|track|ul'
)
HTML_ATTRIBUTE = r'''[A-Za-z_:][A-Za-z0-9_.:-]*(?:\s*=\s*(?:[^\s"'=<>`]+|'[^']*'|"[^"]*"))?'''
HTML_STANDALONE = re.compile(
    r'^ {0,3}(?:<[A-Za-z][A-Za-z0-9-]*(?:\s+' + HTML_ATTRIBUTE +
    r')*\s*/?>|</[A-Za-z][A-Za-z0-9-]*\s*>)\s*$', re.I)


def html_block_end(line, paragraph):
    """Return (is_html, terminator); None means a blank line terminates it."""
    raw = re.match(r'^ {0,3}<(script|pre|style|textarea)(?:\s|>|$)', line, re.I)
    if raw:
        return True, re.compile(r'</' + raw[1] + r'\s*>', re.I)
    for start, end in ((r'<!--', r'-->'), (r'<\?', r'\?>'),
                       (r'<!\[CDATA\[', r'\]\]>'), (r'<![A-Z]', r'>')):
        if re.match(r'^ {0,3}' + start, line):
            return True, re.compile(end)
    if re.match(r'^ {0,3}</?(?:' + HTML_BLOCK_TAGS + r')(?:\s|/?>|$)', line, re.I):
        return True, None
    if not paragraph and HTML_STANDALONE.match(line):
        return True, None
    return False, None


def prose_parts(text):
    fence = None
    # Code spans may cross line boundaries; keep their delimiter until the matching run.
    span = None
    offset = 0
    paragraph = False
    list_indent = None
    html_block = False
    html_end = None
    for line in text.splitlines(keepends=True):
        line_start = offset
        offset += len(line)
        if html_block:
            if html_end is None and not line.strip():
                html_block = False
            else:
                yield False, line
                if html_end is not None and html_end.search(line):
                    html_block = False
                continue
        expanded = line.expandtabs(4)
        indent = len(expanded) - len(expanded.lstrip(' '))
        listing = re.match(r'^ {0,3}(?:[-+*]|\d+[.)])\s+', expanded)
        if listing:
            list_indent = listing.end()
        elif line.strip() and list_indent is not None and indent < list_indent:
            list_indent = None
        continuation = list_indent is not None and indent >= list_indent
        if not span and not fence and indent >= 4 and not paragraph and not continuation:
            yield False, line
            continue
        marker = re.match(r'^ {0,3}(`{3,}|~{3,})', line)
        if fence:
            yield False, line
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence) and not line[marker.end():].strip():
                fence = None
            continue
        if not span:
            is_html, html_end = html_block_end(line, paragraph)
            if is_html:
                html_block = html_end is None or not html_end.search(line)
                paragraph = False
                yield False, line
                continue
        # Backtick fence info strings cannot contain backticks. A same-line
        # closing run is an inline span, not a fence swallowing later prose.
        valid_opener = marker and (marker[1][0] != '`' or '`' not in line[marker.end():])
        if valid_opener and not span:
            fence = marker[1]
            paragraph = False
            yield False, line
            continue
        paragraph = bool(line.strip()) and not re.match(r'^ {0,3}(?:#{1,6}\s|>|(?:[-*_]\s*){3,}$|[=-]+\s*$|<)', line)
        part_offset = line_start
        for part in re.split(r'(`+)', line):
            part_offset += len(part)
            if part.startswith('`'):
                if span is None:
                    prefix = text[:part_offset - len(part)]
                    slashes = len(prefix) - len(prefix.rstrip('\\'))
                    if slashes % 2:
                        yield True, part[:1]
                        part = part[1:]
                        if not part:
                            continue
                if span == part:
                    span = None
                    yield False, part
                elif span is None:
                    # Only a matching run of exactly this length forms a span.
                    # Unmatched delimiters remain prose; lookahead cannot cross
                    # a blank line, fence, or another Markdown block opener.
                    closing = re.search(r'(?<!`)' + re.escape(part) + r'(?!`)', inline_tail(text[part_offset:]))
                    if closing:
                        span = part
                    yield closing is None, part
                else:
                    yield False, part
            else:
                yield span is None, part


def normalize(text):
    return ''.join(part.replace('~', '–') if prose else part for prose, part in prose_parts(text))
