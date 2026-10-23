#!/usr/bin/env python3
"""Validate the sequential block records and build a local, source-linked review board.

This is a production record checker, not an architectural or physics test. It never
changes game assets or promotes a block automatically. Python standard library only.
"""
import argparse
import ast
import hashlib
import html
import importlib.util
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = ROOT / 'build/resort-blocks'
GATES = {'survey', 'massing', 'levels', 'facades', 'integration', 'runtime', 'visual'}


def read(path):
    return json.loads(path.read_text())


def local_file(value):
    if not isinstance(value, str) or not value:
        return False
    path = (ROOT / value).resolve()
    return ROOT in path.parents and path.is_file()


FULL = ('sources', 'levels', 'components', 'routes', 'views', 'issues', 'gates')


def is_full(record):
    """The seven-gate block record (Cosmopolitan, Bellagio, ...). The other records are the lightweight city-exterior
    schema: status, free-form sources/components/evidence and a `remaining` list of strings."""
    return all(k in record for k in FULL)


def check_light(record):
    errors = []
    rem = record.get('remaining')
    if rem is not None and not (isinstance(rem, list) and all(isinstance(r, str) for r in rem)):
        errors.append('remaining must be a list of strings (or null)')
    files = (record.get('finalBuild') or {}).get('files', {})
    if not isinstance(files, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in files.items()):
        errors.append('finalBuild.files must map paths to SHA-256 digests')
    return errors


def check_record(record, ready=False):
    if not is_full(record):
        return [f"{record.get('id')}: {e}" for e in check_light(record)] + (
            [f"{record.get('id')}: a complete block needs the full seven-gate record"] if ready else [])
    return [f"{record.get('id')}: {e}" for e in check_full(record, ready)]


def check_full(record, ready=False):
    errors = []
    ids = {}
    for key in ('sources', 'levels', 'components', 'routes', 'views', 'issues', 'gates'):
        values = record.get(key, [])
        ids[key] = {v['id'] for v in values}
        if len(ids[key]) != len(values):
            errors.append(f'{key}: duplicate IDs')
        if not values:
            errors.append(f'{key}: inventory is empty')
    if ids['gates'] != GATES:
        errors.append('The seven required completion gates must all be present')
    for source in record['sources']:
        if not source.get('url') and not local_file(source.get('image')):
            errors.append(f"Source {source['id']} has no usable URL or local image")
    for group in ('levels', 'components', 'routes', 'views'):
        for item in record[group]:
            refs = item.get('sources', item.get('referenceSources', []))
            if not refs or set(refs) - ids['sources']:
                errors.append(f"{group}/{item['id']}: missing or unknown sources")
    for component in record['components']:
        if not component.get('levels') or set(component['levels']) - ids['levels']:
            errors.append(f"Component {component['id']}: unknown or missing levels")
    for route in record['routes']:
        if any(route.get(k) not in ids['levels'] for k in ('fromLevel', 'toLevel')):
            errors.append(f"Route {route['id']}: unknown endpoint level")
        if not route.get('components') or set(route['components']) - ids['components']:
            errors.append(f"Route {route['id']}: unknown or missing components")
    if not ready:
        return errors
    for group in ('gates', 'components', 'routes'):
        for item in record[group]:
            expected = 'passed' if group == 'gates' else 'verified'
            evidence = item.get('evidence', [])
            if item.get('status') != expected or not evidence or not all(local_file(p) for p in evidence):
                errors.append(f"{group}/{item['id']}: requires {expected} status and local evidence")
    for view in record['views']:
        if view.get('status') != 'verified' or not view.get('camera') or not local_file(view.get('gameCapture')):
            errors.append(f"View {view['id']}: installed-game capture and camera record required")
    for level in record['levels']:
        # Guest levels need a physical floor schedule, rather than one elevation.
        if level['id'] == 'guest':
            if not local_file(level.get('schedule')):
                errors.append('Guest levels: physical floor schedule required')
        elif not isinstance(level.get('elevationM'), (int, float)) or not math.isfinite(level['elevationM']):
            errors.append(f"Level {level['id']}: physical elevation required")
    for issue in record['issues']:
        if issue['severity'] == 'blocking' and issue['status'] != 'resolved':
            errors.append(f"Unresolved blocker: {issue['title']}")
    for side in ('baseline', 'after'):
        if not local_file(record.get('performance', {}).get(side)):
            errors.append(f'Performance: {side} route measurement required')
    build = record.get('finalBuild') or {}
    files = build.get('files', {})
    if not files:
        errors.append('Final installed build fingerprint required')
    for path, expected in files.items():
        if not local_file(path) or hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != expected:
            errors.append(f'Final build evidence is stale or missing: {path}')
    return errors


def load_queue():
    queue = read(HERE / 'queue.json')
    blocks = queue['blocks']
    errors = []
    if len({b['id'] for b in blocks}) != len(blocks):
        errors.append('Duplicate block IDs')
    active = [b for b in blocks if b['status'] == 'active']
    if not active and queue.get('active'):
        # every block is refinement-deferred; queue.active names the block the next pass works on
        active = [b for b in blocks if b['id'] == queue['active']]
    if len(active) != 1:
        errors.append('Exactly one block must be active')
    seen_incomplete = False
    records = {}
    for b in blocks:
        if b['status'] not in {'queued', 'active', 'complete', 'refinement-deferred'}:
            errors.append(f"Invalid queue status: {b['id']}")
        if b['status'] == 'active' and seen_incomplete:
            errors.append('An earlier block is unfinished')
        if b['status'] == 'complete' and seen_incomplete:
            errors.append('A later block was completed out of sequence')
        seen_incomplete |= b['status'] not in {'complete', 'refinement-deferred'}
        if b.get('record'):
            path = (HERE / b['record']).resolve()
            if path.parent != HERE or not path.is_file():
                errors.append(f"Missing block record: {b['id']}")
                continue
            record = read(path)
            if record.get('id') != b['id']:
                errors.append(f"Block record ID mismatch: {b['id']}")
            records[b['id']] = record
            # the seven-gate blocks were deferred one by one by the creator; the lightweight city-exterior records are
            # deferred by construction (the 2026-10-12 city-wide pass records what remains instead of a gate)
            if b['status'] == 'refinement-deferred' and is_full(record) and not (
                    b.get('deferral', {}).get('date') and b.get('deferral', {}).get('reason')):
                errors.append(f"{b['id']} requires an explicit dated deferral")
            errors.extend(check_record(record, ready=b['status'] == 'complete'))
        elif b['status'] != 'queued':
            errors.append(f"{b['id']} requires a full block record")
    return queue, records, active[0] if len(active) == 1 else None, errors


def inspect_baseline(record):
    """Read literal legacy tower calls without importing or running Blender code."""
    if record['id'] != 'cosmopolitan':
        return None
    info = record['baseline']
    source = ROOT / info['geometrySource']
    module_path = ROOT / info['mappingSource']
    spec = importlib.util.spec_from_file_location('resort_geographic_mapping', module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    transform = module.recipe('cosmopolitan')
    towers = []
    for node in ast.walk(ast.parse(source.read_text())):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name) or node.func.id != 'tower':
            continue
        name, x, z, width, depth, height, floors = [ast.literal_eval(n) for n in node.args[:7]]
        corners = [module.point([x+dx*width/2, 0, z+dz*depth/2], 'cosmopolitan')
                   for dx, dz in [(-1,-1), (1,-1), (1,1), (-1,1)]]
        towers.append({'name':name, 'heightM':height, 'sourceFloorBands':floors,
                       'polygonXZ':[[p[0],p[2]] for p in corners],
                       'boundsM':[max(p[i] for p in corners)-min(p[i] for p in corners) for i in [0,2]],
                       'sourceLine':node.lineno})
    if len(towers) != 2:
        raise ValueError('Legacy tower recipe changed: inspect and update the baseline reader')
    survey = read(ROOT / info['surveySource'])
    x0, z0, x1, z1 = record['surveyBoundsXZ']
    features = []
    for b in survey['buildings']:
        polys = [[[[p[0],-p[1]] for p in ring] for ring in poly] for poly in b['polygons']]
        points = [p for poly in polys for ring in poly for p in ring]
        bx = [min(p[0] for p in points), min(p[1] for p in points), max(p[0] for p in points), max(p[1] for p in points)]
        if bx[0] <= x1 and bx[2] >= x0 and bx[1] <= z1 and bx[3] >= z0:
            features.append({'id':b['id'],'name':b['name'],'heightM':b['height'],
                             'heightSource':b['kind'],'polygonsXZ':polys,'boundsXZ':bx,
                             'legacyReplacement':b['id'] in transform['osm']})
    return {'note':info['note'], 'transform':transform,'towers':towers,'features':features,
            'sourceHashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                            for p in (source, module_path, ROOT/info['surveySource'])}}


def esc(value):
    return html.escape(str(value), quote=True)


def link(path):
    return path if path.startswith(('https://', 'http://')) else '/'+path


def plan_svg(record, baseline):
    if not baseline:
        return '<p>Block plan survey pending.</p>'
    x0,z0,x1,z1 = record['surveyBoundsXZ']
    width, height = x1-x0, z1-z0
    def points(ring):
        return ' '.join(f'{x-x0:.3f},{z-z0:.3f}' for x,z in ring)
    shapes = ''
    for feature in sorted(baseline['features'], key=lambda f:f['heightM']):
        paths = ' '.join('M '+' L '.join(f'{x-x0:.3f},{z-z0:.3f}' for x,z in ring)+' Z'
                         for poly in feature['polygonsXZ'] for ring in poly)
        color = '#88c3b1' if feature['legacyReplacement'] else '#758989'
        shapes += f'<path class="mapped" d="{paths}" fill="{color}" fill-opacity=".15" stroke="{color}" stroke-width=".6" fill-rule="evenodd"><title>{esc(feature["id"])} · {esc(feature["name"])} · tagged/estimated {feature["heightM"]} m</title></path>'
    for tower in baseline['towers']:
        ps = tower['polygonXZ']
        cx = sum(p[0] for p in ps)/4-x0
        cz = sum(p[1] for p in ps)/4-z0
        shapes += f'<g class="legacy"><polygon points="{points(ps)}" fill="#eaab6e" fill-opacity=".12" stroke="#eaab6e" stroke-width="1" stroke-dasharray="3 2"/><text x="{cx:.2f}" y="{cz:.2f}" text-anchor="middle" fill="#ffd6a8" font-size="5">Old {esc(tower["name"])}</text></g>'
    return f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="North-up diagnostic map: OSM footprints versus the old transformed tower recipes"><defs><pattern id="grid" width="25" height="25" patternUnits="userSpaceOnUse"><path d="M 25 0 L 0 0 0 25" fill="none" stroke="#354648" stroke-width=".3"/></pattern></defs><rect width="100%" height="100%" fill="#17272b"/><rect width="100%" height="100%" fill="url(#grid)"/>{shapes}<path d="M 15 31 V 12 L 12 18 M 15 12 L 18 18" fill="none" stroke="#fff"/><text x="15" y="8" text-anchor="middle" fill="#fff" font-size="5">N</text><path d="M 12 {height-13} h 50" stroke="#fff"/><text x="12" y="{height-17}" fill="#fff" font-size="5">50 m</text></svg>'


def build_report(queue, record, baseline):
    sources = {s['id']:s for s in record['sources']}
    def refs(ids):
        return ' · '.join(f'<a href="#source-{esc(i)}">{esc(sources[i]["title"])}</a>' for i in ids)
    ready_errors = check_record(record, ready=True)
    queue_html = ''.join(f'<div class="queue-item {esc(b["status"])}"><small>{i+1:02} / {esc(b["status"])}</small><strong>{esc(b["name"])}</strong></div>' for i,b in enumerate(queue['blocks']))
    gate_html = ''.join(f'<li><span>{i+1:02}</span><div><strong>{esc(g["name"])}</strong><small>{esc(g["status"])}</small></div></li>' for i,g in enumerate(record['gates']))
    rows = ''.join(f'<tr data-category="{esc(c["category"])}"><td><small>{esc(c["priority"])} / {esc(c["status"])}</small><strong>{esc(c["name"])}</strong></td><td>{esc(", ".join(c["levels"]))}</td><td>{esc(c["scope"])}<details><summary>Reference evidence</summary>{refs(c["sources"])}</details></td></tr>' for c in record['components'])
    level_html = ''.join(f'<article><small>{esc(l["id"])}</small><h3>{esc(l["label"])}</h3><p>{esc(l["features"])}</p><p class="muted">{("Elevation: "+str(l["elevationM"])+" m") if l["elevationM"] is not None else "Physical elevation: survey pending"}</p><div class="refs">{refs(l["sources"])}</div></article>' for l in record['levels'])
    issue_html = ''.join(f'<article class="issue"><small>{esc(i["severity"])} / {esc(i["status"])}</small><h3>{esc(i["title"])}</h3><p>{esc(i["detail"])}</p></article>' for i in record['issues'])
    route_html = ''.join(f'<li><strong>{esc(r["id"].replace("-"," "))}</strong><span>{esc(r["fromLevel"])} → {esc(r["toLevel"])} → return</span><p>{esc(" → ".join(next(c["name"] for c in record["components"] if c["id"]==cid) for cid in r["components"]))}</p><small>{esc(r["status"])} · walk test pending</small></li>' for r in record['routes'])
    view_html = ''.join(f'<li><strong>{esc(v["name"])}</strong><p>{esc(v["purpose"])}</p><small>{"Verified game capture" if v["status"]=="verified" else "Matching reference/game pair pending"}</small></li>' for v in record['views'])
    source_html = ''
    for s in record['sources']:
        uri = s.get('url') or link(s['image'])
        pic = f'<a href="{esc(link(s["image"]))}"><img loading="lazy" src="{esc(link(s["image"]))}" alt="{esc(s["title"])}"></a>' if s.get('image') and s['kind']=='official-map' else ''
        source_html += f'<article id="source-{esc(s["id"])}"><small>{esc(s["kind"])} · checked {esc(s["accessed"])}</small><h3><a href="{esc(uri)}">{esc(s["title"])} ↗</a></h3><p>{esc(s["note"])}</p>{pic}</article>'
    baseline_html = ''
    if baseline:
        baseline_html = '<div class="metrics">'+''.join(f'<div><small>OLD RECIPE / {esc(t["name"])}</small><strong>{t["boundsM"][0]:.1f} × {t["boundsM"][1]:.1f} m</strong><span>Plan envelope · {t["heightM"]} m high</span></div>' for t in baseline['towers'])+'</div>'
    e = record['sources'][0]
    maps = plan_svg(record,baseline)
    css = (HERE/'review.css').read_text()
    options = ''.join(f'<option value="{esc(c)}">{esc(c.title())}</option>' for c in sorted({c['category'] for c in record['components']}))
    doc = f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Afterlight · Complete resort blocks</title><style>{css}</style>
<main><header><div class="eyebrow">VEGAS: AFTERLIGHT / LOCAL PRODUCTION RECORD</div><h1>A resort is more<br>than its towers.</h1><p class="lead">Complete exteriors, from street to skyline.<br>One block at a time, with every public outdoor level connected.</p><nav><a href="#active">Active block</a><a href="#scope">Component checklist</a><a href="#levels">Exterior levels</a><a href="#sources">References</a><a href="/tools/resort-blocks/README.md">Full workflow ↗</a></nav></header>
<div class="queue">{queue_html}</div>
<section class="intro"><div><small>THE REPEATABLE PROCESS</small><h2>Survey. Build. Walk. Compare.</h2><p>Each block has its own component inventory, physical elevation schedule, circulation routes and matching reference views. A visual review and an installed-game walk-through are both required before moving on.</p><p class="note">{esc(record.get('statusNote', 'Work in progress.'))}</p></div><ol class="gates">{gate_html}</ol></section>
<section id="active"><small>01 / ACTIVE · {esc(record['stage'].upper())}</small><h2>{esc(record['name'])}</h2><p>{esc(record['nextAction'])}</p>{baseline_html}<div class="pair"><figure><img src="{esc(link(e['image']))}" alt="{esc(e['title'])}"><figcaption>REFERENCE · {esc(e['title'])}. Image date: {esc(e.get('imageDate') or 'unknown')}.</figcaption></figure><figure>{maps}<figcaption>DIAGNOSTIC PLAN · Green/gray: existing OSM outlines. Dashed amber: old tower recipes after geographic fitting. Names and heights in OSM are not yet reconciled.</figcaption><div class="toggles"><label><input type="checkbox" id="mapped" checked> Map footprints</label><label><input type="checkbox" id="legacy" checked> Old tower recipes</label></div></figure></div><p class="muted">The numbers above are measured from source recipes and the current map transform, not a fresh measurement of the installed GLB. The plan is north-up, at the game’s metre scale.</p></section>
<section><small>FIX FIRST</small><h2>Known discrepancies</h2><div class="cards">{issue_html}</div></section>
<section id="scope"><small>REQUIRED SCOPE / {len(record['components'])} COMPONENTS</small><h2>The whole block</h2><label class="filter">Show <select id="category"><option value="all">All components</option>{options}</select></label><div class="table-wrap"><table><thead><tr><th>Component / priority</th><th>Levels</th><th>Required work</th></tr></thead><tbody>{rows}</tbody></table></div></section>
<section id="levels"><small>FLOOR LABELS ≠ PHYSICAL HEIGHTS</small><h2>Stacked outdoor spaces</h2><div class="cards">{level_html}</div><p class="note">Map labels establish uses and connections. Metric elevations are recorded separately; estimated elevations remain marked as estimates.</p></section>
<section><small>PLAYABLE CONNECTIONS</small><h2>Every destination needs a way back</h2><ul class="routes">{route_html}</ul></section>
<section><small>VISUAL ACCEPTANCE</small><h2>Compare the same views</h2><p>Capture each view from the installed game, alongside its reference. Record the camera, lighting and build version. Passing collision tests alone does not make a resort visually complete.</p><ul class="views">{view_html}</ul></section>
<section id="sources"><small>RESEARCH REGISTER</small><h2>References and their limits</h2><div class="sources">{source_html}</div></section>
<footer><strong>Completion check: {len(ready_errors)} outstanding evidence requirements.</strong><p>These are pending production requirements, not runtime errors. Full completion requires all geometry, routes and review evidence. Creator-approved deferrals retain unfinished work in the queue and issue records. Build this board with <code>python3 tools/resort-blocks/review.py</code>.</p><p>Map footprint data © OpenStreetMap contributors. Official maps © their respective resort operators. Google Earth views include creator-supplied and live browser reference captures. References are for review, not game textures.</p></footer></main>
<script>document.querySelector('#category').addEventListener('change',e=>{{for(const r of document.querySelectorAll('tr[data-category]'))r.hidden=e.target.value!=='all'&&r.dataset.category!==e.target.value}});for(const id of ['mapped','legacy']){{const c=document.getElementById(id);c.addEventListener('change',()=>{{for(const n of document.querySelectorAll('svg .'+id))n.style.display=c.checked?'':'none'}})}}</script></html>'''
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'index.html').write_text(doc)
    (OUT/f"{record['id']}-baseline.json").write_text(json.dumps(baseline,indent=2)+'\n')
    return ready_errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ready', action='store_true', help='Also require completion evidence before advancing')
    args = parser.parse_args()
    queue, records, active, errors = load_queue()
    if errors:
        for error in errors:
            print('ERROR:',error)
        return 1
    record = records[active['id']]
    if not is_full(record):
        status = {}
        for b in queue['blocks']:
            status[b['status']] = status.get(b['status'], 0) + 1
        remaining = sum(len(r.get('remaining') or []) for r in records.values())
        print(f"Records valid: {len(records)} blocks ({', '.join(f'{v} {k}' for k, v in status.items())}); "
              f"{sum(map(is_full, records.values()))} full seven-gate records; {remaining} remaining items.")
        print(f"Active: {active['id']} (lightweight record: no review board). Task board: python3 tools/tasks/build-board.py")
        return 1 if args.ready else 0
    baseline = inspect_baseline(record)
    pending = build_report(queue, record, baseline)
    print(f"Records valid. Active: {record['name']}; {len(record['components'])} components; {len(record['routes'])} routes.")
    print(f'Review: {OUT / "index.html"}')
    print(f'Completion evidence pending: {len(pending)}. No game assets changed.')
    if args.ready and pending:
        for reason in pending:
            print('PENDING:', reason)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
