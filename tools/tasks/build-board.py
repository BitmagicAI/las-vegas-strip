#!/usr/bin/env python3
"""Builds the contributor task board from the project's own records. Run it after changing a block record, the
building inventory or tasks/curated.json; never edit its outputs by hand.

Inputs (all committed):
  tools/resort-blocks/queue.json + <block>.json            one exterior task per block (its `remaining` list, or the
                                                           unresolved issues and pending gates of a seven-gate record)
  docs/project-records/city-exteriors-2026-10-12/inventory.json
                                                           mapped buildings: attached to their block, or grouped by
                                                           owner when no block record covers them
  build-time facts listed in INTERIORS below               casino resorts that have hotel floors but no authored
                                                           public interior
  tasks/curated.json                                       hand-written release, tooling, performance and film tasks
Outputs:
  tasks/index.json   every task, machine-readable (tools/tasks/pick.mjs and tools/tasks/sync-issues.mjs read it)
  tasks/BOARD.md     the same, for people
  STATUS.md          what is built and what is missing, in numbers

python3 tools/tasks/build-board.py"""
import collections
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RB = ROOT / 'tools/resort-blocks'
INVENTORY = 'docs/project-records/city-exteriors-2026-10-12/inventory.json'
DONE = {'implemented-visually-reviewed', 'exterior-pass-reviewed', 'obsolete-footprint-removed'}

# Hotel sets with guest floors (build/hotels/<set>-room.glb) and the authored public interiors (venues.json entries that
# are not exteriorOnly). Kept here so the board builds without build/; refresh with the snippet in tasks/README.md.
HOTEL_SETS = {
    'allure': 'Allure', 'aria': 'ARIA', 'bellagio': 'Bellagio', 'bellagio-spa': 'Bellagio Spa Tower',
    'caesars': 'Caesars Palace', 'circus-circus': 'Circus Circus', 'cosmopolitan': 'The Cosmopolitan', 'elara': 'Elara',
    'encore': 'Encore', 'flamingo': 'Flamingo', 'fontainebleau': 'Fontainebleau', 'grand-chateau': "Marriott's Grand Chateau",
    'harrahs': "Harrah's", 'hgv-boulevard': 'Hilton Grand Vacations Boulevard', 'horseshoe': 'Horseshoe (Versailles tower)',
    'horseshoe-east': 'Horseshoe East Tower', 'linq': 'The LINQ', 'luxor': 'Luxor', 'mandalay-bay': 'Mandalay Bay',
    'martin': 'The Martin', 'mgm-grand': 'MGM Grand', 'mirage': 'The Mirage', 'new-york': 'New York-New York',
    'palazzo': 'The Palazzo', 'palms': 'Palms', 'panorama': 'Panorama Towers', 'paris': 'Paris', 'park-mgm': 'Park MGM',
    'planet-hollywood': 'Planet Hollywood', 'polo': 'Polo Towers', 'resorts-world': 'Resorts World', 'rio': 'Rio',
    'sahara': 'SAHARA', 'signature': 'The Signature at MGM Grand', 'sky': 'Sky Las Vegas', 'springhill': 'SpringHill Suites',
    'strat': 'The STRAT', 'treasure-island': 'Treasure Island', 'trump': 'Trump International', 'turnberry-place': 'Turnberry Place',
    'turnberry-towers': 'Turnberry Towers', 'vanderpump': 'The Vanderpump Hotel', 'vdara': 'Vdara', 'veer': 'Veer Towers',
    'venetian': 'The Venetian', 'w-las-vegas': 'W Las Vegas', 'waldorf': 'Waldorf Astoria', 'westgate': 'Westgate', 'wynn': 'Wynn',
}
AUTHORED_INTERIORS = {
    'build/strip-landmarks': ['linq', 'vanderpump', 'fashion', 'venetian', 'arena', 'park', 'palazzo', 'ti', 'harrahs', 'polo'],
    'build/resort-blocks/cosmo': ['cosmo', 'cosmoL1', 'cosmoL2', 'cosmoL3', 'cosmoL4', 'cosmoL14'],
    'build/resort-blocks/bellagio': ['bellagioBlock', 'bellagioLobby', 'bellagioGarden', 'bellagioConservatory', 'bellagioPromenade'],
    'build/resort-blocks/paris': ['parisBlock', 'parisDining', 'parisPool'],
}
# Casino resorts with a compressed, photo-informed lobby and casino in the city level (build/public-resorts/DESIGN.md,
# 2026-10-02), not laid out to a floor plan.
COMPRESSED = ['caesars', 'flamingo', 'horseshoe', 'planet-hollywood', 'aria']
# Casino resorts with no authored public interior on record: only the generic hotel lobby, corridors and rooms.
INTERIORS = COMPRESSED + ['circus-circus', 'encore', 'wynn', 'fontainebleau', 'luxor', 'mandalay-bay', 'mgm-grand',
                          'mirage', 'new-york', 'palms', 'resorts-world', 'rio', 'sahara', 'strat', 'westgate']
EXTERIOR_ACCEPTANCE = [
    'Each listed item is fixed, or stays in the record\'s `remaining` list with a sentence on why',
    'Matching before/after game views from the same cameras are attached to the pull request (tools/render-resort-comparison.mjs or tools/probe-views.mjs)',
    'Walkable surfaces still pass the collision/walk audit for the block (tools/city-exteriors/audit-*.py or the block\'s own audit)',
    'The changed GLBs are re-optimized (AGENTS.md: optimize-runtime-glbs.mjs, then install-optimized.mjs) and their version.json revision is bumped',
    'python3 tools/resort-blocks/review.py passes, and the block record lists the new evidence',
]
INTERIOR_ACCEPTANCE = [
    'A public interior (casino floor, main lobby and the routes between them and the Strip) streams in like the existing venues (StripLandmarks / venues.json)',
    'It goes through lightInterior() and adds no runtime lights (AGENTS.md)',
    'Doors open both ways and nothing crosses a doorway; walk audit passes',
    'Floor plan source is linked in the record; no third-party image is shipped',
    'Frame time measured before and after with tools/probe-interiors.mjs',
]


def load(path):
    with open(ROOT / path) as f:
        return json.load(f)


def slug(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


def bname(x):
    n = x.get('name')
    return n if n and n.lower() not in ('yes', 'unnamed building') else 'Unnamed building'


def size_of(n):
    return 'S' if n <= 2 else 'M' if n <= 5 else 'L'


def tool_index():
    """Text of every committed builder script, for finding which ones mention a block."""
    out = {}
    for p in sorted((ROOT / 'tools').rglob('*')):
        rel = p.relative_to(ROOT).as_posix()
        if p.suffix in ('.py', '.mjs') and p.is_file() and '/.venv/' not in rel and '/adapter/' not in rel and '__pycache__' not in rel:
            try:
                out[rel] = p.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                pass
    return out


def builders_for(names, tools, limit=6):
    hits = []
    for rel, text in tools.items():
        if rel.startswith(('tools/tasks/', 'tools/release/', 'tools/info-video/')):
            continue
        score = sum(text.count(n) for n in names if n)
        if score:
            hits.append((-score, rel))
    return [rel for _, rel in sorted(hits)[:limit]]


OWNER_ALIASES = {'wynn': 'wynn-encore', 'encore': 'wynn-encore', 'treasure-island': 'ti', 'caesars': 'caesars-towers',
                 'palazzo': 'venetian'}


def owner_block(owner, ids):
    """The queue block an inventory owner names (bellagio, luxorExterior, 'excalibur / excaliburFrontage'), if any."""
    for part in (owner or '').split(' / '):
        k = re.sub(r'(?<!^)(?=[A-Z])', '-', part.strip()).lower()
        k = OWNER_ALIASES.get(re.sub(r'-(exterior|frontage|block|site|podium)$', '', k), k)
        for cand in (k, re.sub(r'-(exterior|frontage|block|site|podium)$', '', k)):
            if cand in ids:
                return cand
    return None


def block_tasks(tools, inventory):
    q = load('tools/resort-blocks/queue.json')
    ids = {b['id']: b['record'] for b in q['blocks']}
    by_record = collections.defaultdict(list)
    for b in inventory:
        ev = b.get('reviewEvidence') or b.get('record') or ''
        if isinstance(ev, str) and ev.startswith('tools/resort-blocks/') and ev.endswith('.json'):
            by_record[ev].append(b)
        elif owner_block(b.get('owner'), ids):
            by_record['tools/resort-blocks/' + ids[owner_block(b.get('owner'), ids)]].append(b)
    tasks, covered = [], set()
    for order, b in enumerate(q['blocks']):
        rec_path = f'tools/resort-blocks/{b["record"]}'
        r = load(rec_path)
        name = b.get('name') or r.get('name') or b['id'].replace('-', ' ').title()
        if all(k in r for k in ('issues', 'gates')):
            items = [i['title'] for i in r['issues'] if i.get('status') != 'resolved']
            if r.get('nextAction'):
                items.append('Next action recorded: ' + r['nextAction'])
            pending = [g['id'] for g in r['gates'] if g.get('status') != 'passed']
            if pending:
                items.append('Completion gates still pending: ' + ', '.join(pending) + ' (tools/resort-blocks/README.md)')
        else:
            items = list(r.get('remaining') or [])
        buildings = by_record.get(rec_path, [])
        covered.update(x['id'] for x in buildings)
        outputs = sorted((r.get('finalBuild') or {}).get('files', {}))
        keys = sorted({Path(o).name.split('-exterior')[0].split('.')[0] for o in outputs if o.endswith('.glb')})
        near = min([(x.get('stripDistanceM') if x.get('stripDistanceM') is not None else 9e9) for x in buildings] or [9e9])
        tall = max([(x.get('heightM') or 0) for x in buildings] or [0])
        prio = 'P1' if order < 12 or (near < 60 and tall > 60) else 'P2' if near < 200 or tall > 35 else 'P3'
        tasks.append({
            'id': f'ext-{b["id"]}',
            'title': f'Refine the exterior of {name}',
            'area': 'exteriors',
            'size': size_of(len(items)),
            'priority': prio,
            'status': 'open' if items else 'review',
            'summary': (r.get('statusNote') or f'Implemented and reviewed in an earlier pass; {len(items)} known gaps are recorded.'),
            'items': items,
            'record': rec_path,
            'buildings': [{'id': x['id'], 'name': bname(x), 'status': x.get('status')} for x in buildings],
            'files': {'reads': [rec_path, 'tools/resort-blocks/README.md'], 'writes': outputs + [rec_path],
                      'builders': builders_for(keys + [b['id'], b['id'].replace('-', '_')], tools)},
            'acceptance': EXTERIOR_ACCEPTANCE,
            'queueOrder': order,
        })
    return tasks, covered


def site_tasks(inventory, covered, tools):
    groups = collections.defaultdict(list)
    for b in inventory:
        if b['id'] in covered or b.get('status') in DONE:
            continue
        groups[b.get('owner') or 'unassigned'].append(b)
    tasks = []
    for owner, rows in sorted(groups.items()):
        names = sorted({bname(x) for x in rows})
        near = min((x.get('stripDistanceM') if x.get('stripDistanceM') is not None else 9e9) for x in rows)
        tall = max((x.get('heightM') or 0) for x in rows)
        items = [f'{bname(x)} ({x["id"]}, {x.get("heightM", "?")} m, status {x.get("status")})'
                 + (f': {x["remaining"]}' if isinstance(x.get('remaining'), str) and 'retained in block record' not in x['remaining'] else '')
                 for x in rows]
        ev = sorted({x.get('reviewEvidence') for x in rows if isinstance(x.get('reviewEvidence'), str)})
        tasks.append({
            'id': f'site-{slug(owner)}',
            'title': f'Review and refine the mapped buildings owned by {owner}',
            'area': 'exteriors',
            'size': size_of(len(rows)),
            'priority': 'P2' if near < 100 or tall > 60 else 'P3',
            'status': 'open',
            'summary': f'{len(rows)} mapped building(s) ({", ".join(names[:4])}{"…" if len(names) > 4 else ""}) passed a first exterior review; refinement is pending and no block record covers them yet. Start one in tools/resort-blocks/ (copy a lightweight record such as akita-plaza.json) and add it to queue.json.',
            'items': items,
            'record': INVENTORY,
            'buildings': [{'id': x['id'], 'name': bname(x), 'status': x.get('status')} for x in rows],
            'files': {'reads': [INVENTORY] + ev, 'writes': ['tools/resort-blocks/'],
                      'builders': builders_for([owner.split(' / ')[0]], tools)},
            'acceptance': EXTERIOR_ACCEPTANCE,
        })
    return tasks


def interior_tasks():
    tasks = []
    for s in INTERIORS:
        name = HOTEL_SETS[s]
        if s in COMPRESSED:
            title = f'Rebuild the public interior of {name} to its floor plan'
            summary = (f'{name} has streamed guest floors (build/hotels/{s}-*.glb) and a compressed, photo-informed arrival, '
                       'reception and casino in the city level (build/public-resorts/DESIGN.md, 2026-10-02), which is not laid out to a plan. '
                       'Rebuild it as a streamed venue to the published resort map, keeping its look. The Venetian, Palazzo, LINQ, Bellagio, '
                       'Paris and Cosmopolitan venues show the pattern (tools/strip-landmarks/build.py, venues.json).')
        else:
            title = f'Author the public interior of {name}'
            summary = (f'{name} has streamed guest floors (lobby, corridors, rooms: build/hotels/{s}-*.glb) but no authored public '
                       'interior on record: no casino floor, main lobby or retail promenade. Check the city level in game before starting. '
                       'The Venetian, Palazzo, LINQ, Bellagio, Paris and Cosmopolitan venues show the pattern (tools/strip-landmarks/build.py, venues.json).')
        tasks.append({
            'id': f'int-{s}',
            'title': title,
            'area': 'interiors',
            'size': 'L',
            'priority': 'P2',
            'status': 'open',
            'summary': summary,
            'items': ['Find the published resort map or floor plan and record its URL in a block record (never commit the image)',
                      'Lay out the casino floor, main lobby, porte-cochère entrance and the routes to the Strip and to the hotel lifts',
                      'Build it as a streamed venue with its own collision, lit through lightInterior()',
                      'Connect it to the existing hotel lobby so guests can walk from the casino to their room'],
            'record': None,
            'buildings': [],
            'files': {'reads': ['tools/strip-landmarks/build.py', 'tools/strip-landmarks/export.py', 'tools/strip-landmarks/guest_sets.py', 'src/work/StripLandmarks.ts'],
                      'writes': ['tools/strip-landmarks/', 'build/strip-landmarks/'], 'builders': ['tools/strip-landmarks/build.py', 'tools/strip-landmarks/export.py']},
            'acceptance': INTERIOR_ACCEPTANCE,
            'needs': ['source pack (tool-source-pack) to rebuild strip-landmark venues'],
        })
    return tasks


def write_board(tasks, stats):
    areas = collections.OrderedDict((a, []) for a in ['release', 'tooling', 'exteriors', 'interiors', 'performance', 'film'])
    for t in tasks:
        areas.setdefault(t['area'], []).append(t)
    lines = ['# Task board', '',
             'Generated by `python3 tools/tasks/build-board.py` from the block records, the building inventory and',
             '`tasks/curated.json`. Do not edit by hand. To pick one up, see [tasks/README.md](README.md); whether a task is',
             'already taken is shown on its GitHub issue (`[task-id]` in the title), not here.', '',
             f'{len(tasks)} tasks: ' + ', '.join(f'{len(v)} {k}' for k, v in areas.items() if v) + '.', '']
    for area, ts in areas.items():
        if not ts:
            continue
        lines += [f'## {area.title()}', '', '| Task | Size | Priority | Items | Title |', '|---|---|---|---|---|']
        for t in sorted(ts, key=lambda t: (t['priority'], t.get('queueOrder', 999), t['id'])):
            lines.append(f'| `{t["id"]}` | {t["size"]} | {t["priority"]} | {len(t["items"])} | {t["title"]} |')
        lines.append('')
    (ROOT / 'tasks/BOARD.md').write_text('\n'.join(lines))


def write_status(tasks, inventory, stats):
    st = collections.Counter(b.get('status') for b in inventory)
    pack = load('tools/release/asset-pack.json') if (ROOT / 'tools/release/asset-pack.json').exists() else None
    ext = [t for t in tasks if t['area'] == 'exteriors']
    open_items = sum(len(t['items']) for t in ext)
    lines = ['# Status: what is built and what is missing', '',
             'Generated by `python3 tools/tasks/build-board.py`. Numbers come from the block records, the building inventory',
             'and the runtime asset list. Open work is in [tasks/BOARD.md](tasks/BOARD.md).', '',
             '## Built', '',
             f'- **Map:** OpenStreetMap footprints, roads and heights for central Las Vegas, plus Clark County pavement surfaces. A box building for every mapped footprint.',
             f'- **Detailed exteriors:** {stats["blocks"]} block records in `tools/resort-blocks/` ({stats["full"]} with the full seven-gate survey). All are installed in the game and visually reviewed.',
             f'- **Mapped buildings reviewed:** {len(inventory)} buildings in the inventory (every mapped building at least 35 m tall and 500 m², plus every footprint within 200 m of Las Vegas Boulevard).',
             f'- **Hotel guest floors:** {len(HOTEL_SETS)} hotel sets with a streamed lobby, corridors, stairs and enterable rooms (`build/hotels/`).',
             f'- **Authored public interiors:** {sum(len(v) for v in AUTHORED_INTERIORS.values())} streamed venues at the Venetian, Palazzo, LINQ, Vanderpump, Fashion Show, the Arena, Park MGM, Treasure Island, Harrah\'s, Polo Towers, the Cosmopolitan, Bellagio and Paris. Compressed, photo-informed lobbies and casinos in the city level for Caesars, Flamingo, Horseshoe, Planet Hollywood, ARIA, Vdara, Waldorf Astoria, Veer and Crystals. The Sphere has an interior and video skin, and the Big Apple Coaster is rideable.',
             (f'- **Runtime assets:** {pack["count"]} files, {pack["bytes"] / 1048576:.0f} MiB in the asset pack (revision {pack["revision"]}).' if pack else ''),
             '', '## Inventory status (mapped buildings)', '', '| Status | Buildings |', '|---|---|']
    lines += [f'| {k} | {v} |' for k, v in st.most_common()]
    lines += ['', '## Missing or unfinished', '',
              f'- **Exterior refinement:** {len(ext)} tasks with {open_items} recorded gaps. No block has passed all seven completion gates; every one is `refinement-deferred` with its gaps listed.',
              f'- **Public interiors:** {len(COMPRESSED)} casino resorts have a compressed, photo-informed lobby and casino that is not laid out to a plan ({", ".join(HOTEL_SETS[s] for s in COMPRESSED)}). {len(INTERIORS) - len(COMPRESSED)} more have no authored public interior on record, only the generic hotel lobby, corridors and rooms ({", ".join(HOTEL_SETS[s] for s in INTERIORS if s not in COMPRESSED)}).',
              ('- **Release tasks:** ' + '; '.join(t['title'] for t in tasks if t['area'] == 'release') + ' (the `release` tasks on the board).'
               if any(t['area'] == 'release' for t in tasks) else None),
              '- **Rebuilding geometry from a clone** needs a source pack that does not exist yet (`tool-source-pack`).',
              '']
    (ROOT / 'STATUS.md').write_text('\n'.join(l for l in lines if l is not None))


def main():
    inventory = load(INVENTORY)['buildings']
    tools = tool_index()
    blocks, covered = block_tasks(tools, inventory)
    sites = site_tasks(inventory, covered, tools)
    curated = load('tasks/curated.json')['tasks']
    for t in curated:
        t.setdefault('status', 'open')
        t.setdefault('record', None)
        t.setdefault('buildings', [])
    tasks = curated + blocks + sites + interior_tasks()
    ids = [t['id'] for t in tasks]
    dup = [i for i, n in collections.Counter(ids).items() if n > 1]
    if dup:
        raise SystemExit(f'duplicate task ids: {dup}')
    stats = {'blocks': len(blocks), 'full': sum(1 for t in blocks if any('Completion gates' in i for i in t['items']))}
    (ROOT / 'tasks/index.json').write_text(json.dumps({
        'about': 'Generated by tools/tasks/build-board.py; do not edit. Claims live on GitHub issues (tasks/README.md).',
        'count': len(tasks), 'tasks': tasks}, indent=1, ensure_ascii=False) + '\n')
    write_board(tasks, stats)
    write_status(tasks, inventory, stats)
    by = collections.Counter(t['area'] for t in tasks)
    print(f'{len(tasks)} tasks ({dict(by)}) -> tasks/index.json, tasks/BOARD.md, STATUS.md')


if __name__ == '__main__':
    main()
