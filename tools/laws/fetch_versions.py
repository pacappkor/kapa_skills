#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Fetch Korean law histories; --check reports changes and scheduled amendments without writing."""
import argparse, datetime, html, json, pathlib, re, sys, time, urllib.parse
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import lawgo
from fetch_laws import ROOT, SRC, MAN, CAT, wbytes


def norm(name):
    return re.sub(r'\s+', '', name)


def resolve_title(seq, ef):
    """Resolve each staged body independently; truncated prefixes are not identities."""
    body = lawgo.fetch_body(seq, ef)
    time.sleep(1)
    name = lawgo.hidden(body, 'lsNm')
    if not name or name.endswith('...'):
        raise ValueError('연혁 전체 법령명 확인 실패')
    # Repealed historical bodies may have no parsed articles; title resolution
    # needs the verified response identity, not a nonempty article collection.
    lawgo.verify_identity(body, seq, ef)
    return name


def korea_today(now=None):
    """Korean legal calendar date; fixed UTC+9 needs no host tz database."""
    now = now if now is not None else datetime.datetime.now(datetime.timezone.utc)
    return now.astimezone(datetime.timezone(datetime.timedelta(hours=9))).date()


def parse_history(page, name, seq, today=None, anchor_ef=None, title_resolver=None):
    today = today or korea_today().strftime('%Y%m%d')
    versions = []
    for item in re.findall(r'<li\b[^>]*>(.*?)</li>', page, re.S):
        call = re.search(r'lsViewLsHst2\((.*?)\)', item)
        if not call:
            continue
        vals = re.findall(r"'([^']*)'", html.unescape(call.group(1)))
        if len(vals) != 7:
            raise ValueError('연혁 인자 형식 변경')
        s, anc, no, ef, _, _, kind = vals
        title = re.search(r'<b>(.*?)</b>', item, re.S)
        if not title or not all(re.fullmatch(r'\d+', x) for x in (s, anc, no, ef)):
            raise ValueError('연혁 필수 필드 누락')
        shown = re.sub(r'^\d+\.\s*', '', lawgo._text(title.group(1)))
        if shown.endswith('...'):
            shown = (title_resolver or resolve_title)(s, ef)
        same = norm(shown) == norm(name)
        versions.append(dict(lsiSeq=s, efYd=ef, ancYd=anc, ancNo=no,
                             name=name if same else shown, kind=kind,
                             status='past' if same else 'predecessor'))
    anchor = [v for v in versions if v['lsiSeq'] == seq
              and (v['efYd'] == anchor_ef if anchor_ef is not None else v['efYd'] <= today)]
    if not anchor or not any(v['name'] == name for v in anchor):
        raise ValueError('연혁 법령명/현행 lsiSeq 불일치 (잘못된 lsId 가능)')
    versions.sort(key=lambda v: (v['efYd'], v['ancYd'], int(v['lsiSeq'])), reverse=True)
    active = False
    repealed = False
    for v in versions:
        if v['ancYd'] > today:
            raise ValueError('공포일이 미래인 연혁')
        # A future row in this lsId lineage is an amendment, even if renamed.
        if v['efYd'] > today:
            v['status'] = 'scheduled'
        elif not active and lawgo.is_repeal(v['kind']):
            v['status'] = 'repealed'
            active = True
            repealed = True
        elif repealed:
            v['status'] = 'past'
        elif v['status'] == 'predecessor':
            continue
        elif not active:
            v['status'] = 'current'
            active = True
    return versions


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('collections', nargs='*', choices=None)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    known = {c['id'] for c in CAT['collections']}
    if set(args.collections) - known:
        parser.error('unknown collection')
    man = json.loads(MAN.read_text(encoding='utf-8'))
    failures, changed, count, scheduled = [], [], 0, 0
    for c in CAT['collections']:
        if args.collections and c['id'] not in args.collections:
            continue
        for d in c['docs']:
            key = f"{c['id']}/{d['level']}"
            try:
                meta = man[key]
                # Read identifiers from the actual body, never infer lsId from lsiSeq.
                page = lawgo.fetch_body(meta['lsiSeq'], meta['efYd'])
                time.sleep(1)
                lawgo.verify_body(page, d['name'], meta['lsiSeq'], meta['efYd'])
                law_id = lawgo.hidden(page, 'lsId')
                if not re.fullmatch(r'\d{6}', law_id):
                    raise ValueError('invalid lsId')
                if meta.get('lsId', law_id) != law_id:
                    raise ValueError('manifest lsId mismatch')
                if not args.check:
                    meta['lsId'] = law_id
                    wbytes(MAN, json.dumps(dict(sorted(man.items())), ensure_ascii=False, indent=1) + '\n')
                data = urllib.parse.urlencode(dict(lsiSeq=meta['lsiSeq'], lsId=law_id, chrClsCd='010202')).encode()
                history = lawgo._get(lawgo.BASE + '/LSW/lsHstListR.do', data).decode('utf-8', 'replace')
                time.sleep(1)
                versions = parse_history(history, d['name'], meta['lsiSeq'], anchor_ef=meta['efYd'])
                result = dict(lsId=law_id, name=d['name'], fetched=korea_today().isoformat(), versions=versions)
                path = SRC / c['id'] / 'versions' / f"{d['level']}.json"
                old = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
                if old.get('versions') != versions or old.get('lsId') != law_id:
                    changed.append(key)
                    print(f'CHANGED {key}')
                for v in versions:
                    if v['status'] == 'scheduled':
                        scheduled += 1
                        print(f'SCHEDULED {key} {v["lsiSeq"]} 공포 {v["ancYd"]} 시행 {v["efYd"]} — 부칙·경과조치 확인 필요')
                if not args.check:
                    wbytes(path, json.dumps(result, ensure_ascii=False, indent=1) + '\n')
                    meta['lsId'] = law_id
                    wbytes(MAN, json.dumps(dict(sorted(man.items())), ensure_ascii=False, indent=1) + '\n')
                count += 1
                print(f'OK {key}: {len(versions)} versions', flush=True)
            except Exception as exc:
                failures.append(key)
                print(f'FAIL {key}: {exc}', flush=True)
    print(f'documents: {count}; changed: {len(changed)}; failures: {len(failures)}')
    return 1 if failures or (args.check and changed) else 0

if __name__ == '__main__':
    sys.exit(main())
