#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Fetch one historical body by lsiSeq or the version in force on --at YYYY-MM-DD."""
import argparse, datetime, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import lawgo
from fetch_laws import CAT, SRC, wbytes


def choose(versions, at):
    # Include predecessor laws when the requested date precedes the present law.
    available = [v for v in versions if v['efYd'] <= at and v['ancYd'] <= at]
    if not available:
        raise ValueError('해당 날짜에 시행 중인 저장 연혁 없음')
    selected = max(available, key=lambda v: (v['efYd'], v['ancYd'], int(v['lsiSeq'])))
    if lawgo.is_repeal(selected.get('kind', '')):
        raise ValueError('해당 날짜에는 폐지되어 시행 중인 판본 없음')
    return selected


def select(versions, seq, ef=None):
    rows = [v for v in versions if v['lsiSeq'] == seq and (ef is None or v['efYd'] == ef)]
    if len(rows) != 1:
        raise ValueError('판본 없음 또는 lsiSeq 중복: --ef YYYY-MM-DD 또는 --at YYYY-MM-DD 로 시행일 지정 필요')
    return rows[0]


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('collection')
    p.add_argument('level')
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument('lsiSeq', nargs='?')
    group.add_argument('--at')
    p.add_argument('--ef', help='effective date YYYY-MM-DD; required for an ambiguous lsiSeq')
    args = p.parse_args()
    if args.ef and args.at:
        p.error('--ef requires lsiSeq, not --at')
    try:
        c = next(c for c in CAT['collections'] if c['id'] == args.collection)
        d = next(d for d in c['docs'] if d['level'] == args.level)
        base = SRC / c['id'] / 'versions'
        history = json.loads((base / f"{d['level']}.json").read_text(encoding='utf-8'))
        if args.at:
            at = datetime.date.fromisoformat(args.at).strftime('%Y%m%d')
            v = choose(history['versions'], at)
        else:
            ef = datetime.date.fromisoformat(args.ef).strftime('%Y%m%d') if args.ef else None
            v = select(history['versions'], args.lsiSeq, ef)
        page = lawgo.fetch_body(v['lsiSeq'], v['efYd'])
        lawgo.verify_body(page, v['name'], v['lsiSeq'], v['efYd'])
        body = lawgo.parse(page)
        out = dict(name=v['name'], level=d['level'], label=d['label'],
                   lsiSeq=v['lsiSeq'], efYd=v['efYd'], ancYd=v['ancYd'], ancNo=v['ancNo'],
                   lsNm=lawgo.hidden(page, 'lsNm'), lsId=lawgo.hidden(page, 'lsId'),
                   lsClsCd=json.loads((SRC / c['id'] / f"{d['level']}.json").read_text(encoding='utf-8')).get('lsClsCd', ''),
                   headings=body['headings'], articles=body['articles'], annexes=body['annexes'],
                   addenda=body['addenda'])
        path = base / d['level'] / f"{v['lsiSeq']}-{v['efYd']}.json"
        wbytes(path, json.dumps(out, ensure_ascii=False, indent=1) + '\n')
        print(f'{path}: 시행 {v["efYd"]}, 조문 {len(body["articles"])}')
        return 0
    except (ValueError, StopIteration, OSError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 1

if __name__ == '__main__':
    sys.exit(main())
