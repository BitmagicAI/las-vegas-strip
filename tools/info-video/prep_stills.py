"""Stills for the info video: references, evidence and game shots copied (resized, JPEG) into .bitmagic/info-video/stills/,
with an index the story page reads (build/info-video/page/data/stills.json). Third-party images (Google Earth captures, public
photos, official floor plans) are marked third: true so the page can show them small and soft, or not at all (?refs=off).
python3 tools/info-video/prep_stills.py"""
import glob, json, os
from PIL import Image, ImageOps
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, '.bitmagic/info-video/stills'); os.makedirs(OUT, exist_ok=True)
R = lambda *p: os.path.join(ROOT, *p)
index = {}


def put(name, src, size=(1920, 1080), crop=None, third=False, note='', fit='contain'):
    im = Image.open(src).convert('RGB')
    if crop: im = im.crop(crop)
    if fit == 'cover': im = ImageOps.fit(im, size, Image.LANCZOS)
    else: im.thumbnail(size, Image.LANCZOS)
    p = os.path.join(OUT, name + '.jpg'); im.save(p, quality=92)
    index[name] = dict(src=os.path.relpath(src, ROOT), w=im.width, h=im.height, third=third, note=note)


BR = 'docs/project-records/bellagio-remodel-2026-10-08/'
VE = 'docs/project-records/venetian-exterior-2026-10-09/'
put('cesium', R('build/strip-survey/cesium-textured-strip.jpg'), third=True, note='Google Photorealistic 3D Tiles via Cesium Sandcastle (coverage check, 2026-10-03)')
put('ge-bellagio', R(BR + 'owner-reference-google-earth.webp'), third=True, note='Google Earth view supplied by the owner')
put('game-before-bellagio', R(BR + 'owner-game-before.webp'), note='game before the remodel (owner screenshot)')
put('ge-venetian', R(VE + 'user-google-earth-comparison.png'), third=True, note='Google Earth view supplied by the owner')
put('venetian-rejected', R(VE + 'user-rejected-game.png'), note='game before the Venetian revision (owner screenshot)')
put('venetian-after', R(VE + 'revision-final-game.png'), crop=(250, 60, 1280, 640), note='after the revision (game)')
put('venetian-blender', R(VE + 'venetian-palace-plaza-review.png'), note='offline Blender review render')
put('plan-venetian', R(VE + 'official-resort-map-1.png'), third=True, note='official Venetian resort map, level 1')
put('plan-bellagio', R('tools/resort-blocks/references/bellagio/property-map.png'), third=True, note='official Bellagio property map')
put('blender-bellagio', R('build/resort-blocks/bellagio-tower-preview/reference.png'), note='Blender Cycles render of bellagio_towers.py output')
put('eiffel-rejected', R('tools/resort-blocks/references/paris-eiffel-rejected-2026-10-06.png'), size=(1920, 1080), fit='cover', note='game view the owner rejected (2026-10-06)')
put('eiffel-after', R('build/resort-blocks/paris/game-eiffel-retry.jpg'), size=(1920, 1080), fit='cover', note='rebuilt with measured leg sections (game)')
put('headboard', R('build/info-video/rooms/headboard2/headboard-bellagio-b.png'), size=(1920, 1080), fit='cover', note='Bellagio guest room, headboard wall (game)')
put('blender-rotunda', R('build/resort-blocks/bellagio-tower-preview/rotunda.png'), note='Blender Cycles render')

# Public photo research board (small tiles), exterior / hallway / room candidates.
refs = sorted(f for f in glob.glob(R('build/highrises/references/*.jpg')) if 'contact' not in f)
tiles = []
for i, f in enumerate(refs[:96]):
    im = ImageOps.fit(Image.open(f).convert('RGB'), (300, 200), Image.LANCZOS); n = f'ref-{i:02d}'
    im.save(os.path.join(OUT, n + '.jpg'), quality=85); tiles.append(n)
index['refTiles'] = dict(list=tiles, third=True, note='public photos gathered for research (build/highrises/references)')

# Rooms and corridors (game stills, HUD hidden); rooms whose capture faced the corridor are left out.
sets = json.load(open(R('build/info-video/rooms/sets.json'))); redo = set(json.load(open(R('build/info-video/rooms/redo.json'))) + ['luxor'])
rooms, cors = [], []
for s in sets:
    for kind, lst in (('room', rooms), ('corridor', cors)):
        f = R(f"build/info-video/rooms/shots/{kind}-{s['set']}.png")
        if not os.path.exists(f) or (kind == 'room' and s['set'] in redo): continue
        n = f"{kind}-{s['set']}"; im = ImageOps.fit(Image.open(f).convert('RGB'), (960, 540), Image.LANCZOS); im.save(os.path.join(OUT, n + '.jpg'), quality=90)
        lst.append(dict(n=n, set=s['set'], name=s['name']))
index['rooms'] = rooms; index['corridors'] = cors

# Before/after evidence pairs from the city-wide exterior pass (same camera, same file name).
pairs = []
for b in sorted(glob.glob(R('build/city-exteriors/*-before'))):
    a = b[:-len('-before')] + '-after'
    if not os.path.isdir(a): continue
    for f in sorted(os.listdir(b)):
        if f.endswith('.png') and os.path.exists(os.path.join(a, f)):
            key = os.path.basename(b)[:-7] + '-' + f[:-4]
            for side, d in (('b', b), ('a', a)):
                im = ImageOps.fit(Image.open(os.path.join(d, f)).convert('RGB'), (800, 450), Image.LANCZOS); im.save(os.path.join(OUT, f'pair-{key}-{side}.jpg'), quality=88)
            pairs.append(key); break
index['pairs'] = pairs
os.makedirs(R('build/info-video/page/data'), exist_ok=True)
json.dump(index, open(R('build/info-video/page/data/stills.json'), 'w'), indent=1)
print(len(index), 'entries;', len(tiles), 'ref tiles;', len(rooms), 'rooms;', len(cors), 'corridors;', len(pairs), 'before/after pairs')
