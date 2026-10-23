#!/usr/bin/env python3
"""The runtime asset pack: every file under the ignored build/ folder that the game loads, so a fresh clone can run.

build/ holds ~29 GB of Blender sources, reports and intermediates; the game loads about 1.1 GB of it. This tool lists
exactly that set, by the same rules the runtime code uses (the loaders named beside each rule), and packs it:

  python3 tools/release/asset-pack.py list     # write tools/release/asset-pack.json (path, bytes, sha256 per file)
  python3 tools/release/asset-pack.py build    # list, then write .bitmagic/release/las-vegas-strip-assets-<rev>.tar.gz
  python3 tools/release/asset-pack.py check    # what a loader rule names but build/ lacks (exit 1 if any)
  python3 tools/release/asset-pack.py stage    # list, then mirror the set into runtime-assets/ (tracked with Git LFS)

Each runtime GLB ships as its meshopt-optimized copy (build/optimized/, installed by tools/optimize) stored at the
ORIGINAL path: glbUrl() (src/work/OptimizedGlb.ts) returns the original URL when there is no optimized manifest, which a
clone does not have, so the compressed bytes load from the path the game asks for. A GLB whose source changed after it
was optimized ships as the current original (the runtime would load the original too).

Contributors fetch the pack with `node tools/release/fetch-assets.mjs` (docs/ASSETS.md). The pack is a gzipped tar
(meshopt output is made to be gzipped; the collision JSON shrinks most). Members are sorted, timestamped at the revision
date and the gzip header carries no time, so the same inputs give the same file."""
import gzip
import hashlib
import io
import json
import os
import shutil
import sys
import tarfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUILD = ROOT / 'build'
OUT_LIST = ROOT / 'tools/release/asset-pack.json'
OUT_DIR = ROOT / '.bitmagic/release'
# The runtime set in the repository (2026-10-23, the owner: "upload the files as LFS ... otherwise it will be very
# difficult to update the project"). The same bytes as the pack, at the same paths minus the leading build/. A clone
# copies it into its ignored build/ (tools/release/fetch-assets.mjs); every checkout builds into build/ and refreshes
# this mirror with `stage`, then commits it.
RUNTIME = ROOT / 'runtime-assets'


def rel(p):
    return str(Path(p).relative_to(ROOT)) if Path(p).is_absolute() else str(p)


def load_json(path):
    with open(ROOT / path) as f:
        return json.load(f)


def runtime_files():
    """(path, reason) for every runtime file the loaders ask for, GLBs included."""
    want = {}

    def add(path, why):
        want.setdefault(path, why)

    # GLBs: every runtime GLB the optimizer enumerated (tools/optimize/optimize-runtime-glbs.mjs walks the same loaders)
    # (public/ GLBs such as foliage/tree-0.glb are committed and load as their originals in a clone)
    for path in load_json('build/optimized/manifest.json')['files']:
        if path.startswith('build/'):
            add(path, 'runtime GLB (build/optimized/manifest.json)')
    # world.json assets served from build/ (doors in worldProfileData.doors)
    for a in load_json('src/work/world.json').get('assets', []):
        url = (a.get('url') or '').split('?')[0]
        if url.startswith('/build/'):
            add(url[1:], f'world.json asset {a.get("id")}')
    g = 'build/geographic-strip/'
    # GeographicCity.ts, Game.ts, SanctuaryJeep.ts, film/SceneCrowd.ts, GeographicPassages.ts
    for f in ['city-version.json', 'city-colliders.json', 'road-network.json', 'access/manifest.json', 'city.glb', 'detailed.glb']:
        add(g + f, 'GeographicCity / Game / SanctuaryJeep')
    access = load_json(g + 'access/manifest.json')
    for e in access.get('entries', access) if isinstance(access, dict) else access:
        add(f'{g}access/{e["id"]}.json', 'GeographicPassages bridge concourse')
    # HighriseCity.ts: version.json, exteriors.glb, <key>-collision.json
    add('build/highrises/version.json', 'HighriseCity')
    add('build/highrises/exteriors.glb', 'HighriseCity')
    for p in sorted((BUILD / 'highrises').glob('*-collision.json')):
        add(rel(p), 'HighriseCity collision')
    # StripLandmarks.ts (also ResortBlocks.ts for cosmo, bellagio, paris): venues.json, version.json, per venue
    # <key>-exterior.glb + its collision, and unless exteriorOnly <key>-interior.glb + <key>-interior-collision.json
    for base in ['build/strip-landmarks/', 'build/resort-blocks/cosmo/', 'build/resort-blocks/bellagio/', 'build/resort-blocks/paris/']:
        add(base + 'venues.json', 'StripLandmarks')
        add(base + 'version.json', 'StripLandmarks')
        for m in load_json(base + 'venues.json'):
            k = m['key']
            add(f'{base}{k}-exterior.glb', 'StripLandmarks exterior')
            add(base + (m.get('exteriorCollision') or f'{k}-exterior-collision.json'), 'StripLandmarks exterior collision')
            if not m.get('exteriorOnly'):
                for f in [f'{k}-interior.glb', f'{k}-interior-collision.json']:
                    if (ROOT / base / f).exists():
                        add(base + f, 'StripLandmarks interior (streamed)')
    add('build/resort-blocks/bellagio/south-arrival-report.json', 'SanctuaryJeep / SceneCrowd arrival roads')
    # BigAppleCoaster.ts
    for f in ['version.json', 'route.json', 'coaster-collision.json', 'coaster.glb', 'train.glb']:
        add('build/south-strip/' + f, 'BigAppleCoaster')
    # PbrDetail.ts
    for f in ['sets.json', 'albedo.webp', 'normal.webp', 'arm.webp']:
        add('build/pbr/strips/' + f, 'PbrDetail')
    # SphereVenue.ts: sphere.json, version.json, media.json and the media it names
    for f in ['sphere.json', 'version.json', 'media.json', 'exterior.glb', 'interior.glb', 'exterior-collision.json', 'interior-collision.json']:
        add('build/sphere/' + f, 'SphereVenue')
    media = load_json('build/sphere/media.json')
    for k in ['exterior', 'exteriorPoster', 'interior', 'interiorPoster']:
        add('build/sphere/' + media[k], 'SphereVenue media')
    # HotelTemplates.ts: /build/hotels/<module>.glb and /build/hotels/<module>.mesh-level.json
    # (only real modules: the optimizer's list already applies HotelLayout's set and part names, so staged-vegas.glb,
    # which no module name can request, stays out)
    for path in load_json('build/optimized/manifest.json')['files']:
        if path.startswith('build/hotels/') and path.endswith('.glb'):
            add(path[:-4] + '.mesh-level.json', 'HotelTemplates module levels')
    add('build/vehicles/afterlight-jeep.glb', 'SanctuaryJeep')
    return want


def source_for(path, manifest):
    """The bytes to ship for a runtime path: the optimized copy while it matches its source, else the original."""
    e = manifest.get(path)
    src = ROOT / path
    if e and src.exists():
        st = src.stat()
        opt = ROOT / e['optimized']
        if opt.exists() and st.st_size == e['size'] and int(st.st_mtime) == int(e['modified'] / 1000):
            return opt, 'optimized'
        return src, 'original (changed since optimized)'
    return src, 'original'


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def listing():
    manifest = load_json('build/optimized/manifest.json')['files']
    want = runtime_files()
    files, missing = [], []
    for path in sorted(want):
        src, kind = source_for(path, manifest)
        if not src.exists():
            missing.append((path, want[path]))
            continue
        files.append({'path': path, 'bytes': src.stat().st_size, 'sha256': sha256(src), 'from': rel(src), 'kind': kind})
    return files, missing


def write_list(files):
    old = json.loads(OUT_LIST.read_text()) if OUT_LIST.exists() else {}
    revision = time.strftime('%Y-%m-%d')
    doc = {
        'about': 'Runtime files the game loads from the ignored build/ folder. Made by tools/release/asset-pack.py; '
                 'fetched by tools/release/fetch-assets.mjs. See docs/ASSETS.md.',
        'revision': revision,
        'pack': {'name': f'las-vegas-strip-assets-{revision}.tar.gz', 'url': old.get('pack', {}).get('url', ''),
                 'bytes': old.get('pack', {}).get('bytes', 0), 'sha256': old.get('pack', {}).get('sha256', '')},
        'count': len(files),
        'bytes': sum(f['bytes'] for f in files),
        'files': [{k: f[k] for k in ('path', 'bytes', 'sha256', 'kind')} for f in files],
    }
    OUT_LIST.write_text(json.dumps(doc, indent=1) + '\n')
    return doc


def build(files, doc):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / doc['pack']['name']
    mtime = int(time.mktime(time.strptime(doc['revision'], '%Y-%m-%d')))
    with open(out, 'wb') as raw, gzip.GzipFile(filename='', mode='wb', fileobj=raw, mtime=0, compresslevel=6) as gz, \
            tarfile.open(fileobj=gz, mode='w', format=tarfile.PAX_FORMAT) as tar:
        for f in files:
            info = tarfile.TarInfo(f['path'])
            info.size = f['bytes']
            info.mtime = mtime
            info.mode = 0o644
            info.uname = info.gname = ''
            with open(ROOT / f['from'], 'rb') as src:
                tar.addfile(info, src)
    digest = sha256(out)
    doc['pack'].update(bytes=out.stat().st_size, sha256=digest)
    OUT_LIST.write_text(json.dumps(doc, indent=1) + '\n')
    print(f'wrote {rel(out)}: {out.stat().st_size / 1048576:.1f} MiB, sha256 {digest}')
    print('Upload it (a GitHub release asset, max 2 GiB) and put its URL in tools/release/asset-pack.json pack.url.')


def stage(files):
    """Mirror the runtime set into runtime-assets/: copy what is new or changed, delete what left the set."""
    keep, copied, same = set(), 0, 0
    for f in files:
        assert f['path'].startswith('build/'), f['path']
        dest = RUNTIME / f['path'][len('build/'):]
        keep.add(dest)
        if dest.exists() and dest.stat().st_size == f['bytes'] and sha256(dest) == f['sha256']:
            same += 1
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / f['from'], dest)
        copied += 1
    removed = 0
    for p in sorted(RUNTIME.rglob('*'), reverse=True):
        if p.is_file() and p not in keep:
            p.unlink()
            removed += 1
        elif p.is_dir() and not any(p.iterdir()):
            p.rmdir()
    print(f'runtime-assets/: {copied} copied, {same} unchanged, {removed} removed. Commit it: '
          'git add -A runtime-assets tools/release/asset-pack.json')


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'list'
    files, missing = listing()
    for path, why in missing:
        print(f'missing {path}  ({why})')
    if cmd == 'check':
        print(f'{len(files)} present, {len(missing)} missing')
        sys.exit(1 if missing else 0)
    doc = write_list(files)
    by = {}
    for f in files:
        by[f['kind']] = by.get(f['kind'], 0) + f['bytes']
    print(f'{len(files)} files, {doc["bytes"] / 1048576:.1f} MiB -> {rel(OUT_LIST)}')
    for k, b in sorted(by.items()):
        print(f'  {k}: {b / 1048576:.1f} MiB')
    if cmd == 'build':
        build(files, doc)
    if cmd == 'stage':
        stage(files)


if __name__ == '__main__':
    main()
