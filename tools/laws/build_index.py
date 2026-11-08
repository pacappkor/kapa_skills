#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Generate the deterministic current-law and practice-standard interface index."""
import argparse, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import build_laws as B
import lawindex
sys.path.insert(0, str(B.ROOT / 'tools'))
import split_standard as S


def build():
    manifest = json.loads((B.SRC / 'manifest.json').read_text(encoding='utf-8'))
    index = dict(schema=1, laws={}, articles={}, standards={})
    shared_owners = lawindex.owner_index()
    for c in B.CAT['collections']:
        docs = B.load(c)
        cfg = json.loads((B.ROOT / 'tools/laws/topics' / f"{c['id']}.json").read_text(encoding='utf-8'))
        owners = {}
        for topic in cfg['topics']:
            for lv, ranges in topic['assign'].items():
                for key in B.expand(ranges, [a['key'] for a in docs[lv]['articles']]):
                    if (lv, key) in owners:
                        raise ValueError(f'duplicate assignment: {c["id"]}/{lv}/{key}')
                    owners[lv, key] = f"laws/{c['id']}/{B.skill_dir(c, topic['slug'])}"
        for lv, doc in docs.items():
            meta = manifest[f"{c['id']}/{lv}"]
            law_id = meta['lsId']
            if any(meta[k] != doc[k] for k in ('lsiSeq', 'efYd', 'ancYd', 'ancNo')):
                raise ValueError(f'manifest/body version mismatch: {c["id"]}/{lv}')
            history = json.loads((B.SRC / c['id'] / 'versions' / f'{lv}.json').read_text(encoding='utf-8'))
            if history['lsId'] != law_id or history['name'] != doc['name']:
                raise ValueError(f'history identity mismatch: {c["id"]}/{lv}')
            current = [v for v in history['versions'] if v['status'] == 'current']
            if len(current) != 1 or any(current[0][k] != meta[k] for k in ('lsiSeq', 'efYd')):
                raise ValueError(f'history current mismatch: {c["id"]}/{lv}: '
                                 'exactly one current row matching manifest (lsiSeq, efYd) required')
            entry = dict(name=doc['name'], collection=c['id'], level=lv,
                         current={k: doc[k] for k in ('lsiSeq', 'efYd', 'ancYd', 'ancNo')},
                         versions_file=f"sources/laws/{c['id']}/versions/{lv}.json")
            old = index['laws'].get(law_id)
            if old and old['current'] != entry['current']:
                raise ValueError(f'inconsistent versions for law/{law_id}')
            index['laws'].setdefault(law_id, entry)
            for article in doc['articles']:
                owner = owners.get((lv, article['key']))
                if not owner:
                    if c.get('tier') in ('B', 'C'):
                        continue
                    raise ValueError(f'unassigned article: {c["id"]}/{lv}/{article["key"]}')
                if (lawindex._norm(doc['name']), article['key']) not in shared_owners:
                    raise ValueError('article absent from lawindex owner index')
                aid = f"law/{law_id}@{doc['lsiSeq']}#a{article['key'].replace('의', '-')}"
                # A/B/C catalog order gives the broader collection priority for shared laws.
                index['articles'].setdefault(aid, dict(title=article['title'], deleted=article['deleted'], skill=owner + '/SKILL.md'))
    for section in S.parse(S.SRC.read_text(encoding='utf-8')):
        owner = S.owner(section['code'])
        if owner:
            index['standards'][f"apps@{S.SEQ}#{section['code']}"] = dict(title=section['title'], skill=f'{S.COLL}/{owner}/SKILL.md')
    return index


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--check', action='store_true')
    args = p.parse_args()
    try:
        index = build()
        data = (json.dumps(index, ensure_ascii=False, indent=1, sort_keys=True) + '\n').encode('utf-8')
        path = B.ROOT / 'docs/law-index.json'
        if args.check:
            if not path.exists() or path.read_bytes() != data:
                print('ERROR docs/law-index.json 갱신 필요')
                return 1
        else:
            path.write_bytes(data)
        print(f'law-index: laws {len(index["laws"])}; articles {len(index["articles"])}; standards {len(index["standards"])}')
        return 0
    except (KeyError, ValueError, OSError) as exc:
        print(f'ERROR law-index: {exc}')
        return 1

if __name__ == '__main__':
    sys.exit(main())
