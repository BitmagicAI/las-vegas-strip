"""Triangle and mesh counts of every runtime GLB (tools/optimize/runtime-glbs.json), read from each GLB's JSON chunk only.
Drawn triangles count every node that references a mesh (instanced meshes counted per node; EXT_mesh_gpu_instancing
counted per instance). Writes build/info-video/glb-stats.json.
python3 tools/info-video/glb_stats.py"""
import json, struct, os, collections
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
inv = json.load(open(os.path.join(ROOT, 'tools/optimize/runtime-glbs.json')))

def glb_json(path):
    with open(path, 'rb') as f:
        magic, ver, length = struct.unpack('<III', f.read(12))
        clen, ctype = struct.unpack('<II', f.read(8))
        return json.loads(f.read(clen))

def tris_of(j):
    acc = j.get('accessors', [])
    mesh_tris = []
    for m in j.get('meshes', []):
        t = 0
        for p in m.get('primitives', []):
            mode = p.get('mode', 4)
            if mode != 4: continue
            if 'indices' in p: t += acc[p['indices']]['count'] // 3
            else: t += acc[p['attributes']['POSITION']]['count'] // 3
        mesh_tris.append(t)
    drawn = 0; nodes = 0; inst = 0
    for n in j.get('nodes', []):
        if 'mesh' in n:
            k = 1
            ext = n.get('extensions', {}).get('EXT_mesh_gpu_instancing')
            if ext:
                a = ext.get('attributes', {})
                if a: k = acc[list(a.values())[0]]['count']; inst += k
            drawn += mesh_tris[n['mesh']] * k; nodes += 1
    return dict(meshes=len(mesh_tris), unique=sum(mesh_tris), drawn=drawn, meshNodes=nodes, instances=inst,
                materials=len(j.get('materials', [])), textures=len(j.get('textures', [])), images=len(j.get('images', [])))

out = []
for e in inv['files']:
    p = os.path.join(ROOT, e['rel'])
    if not os.path.exists(p): continue
    try: s = tris_of(glb_json(p))
    except Exception as ex: s = dict(error=str(ex))
    out.append(dict(rel=e['rel'], loader=e.get('loader'), when=e.get('when'), bytes=e.get('bytes'), **s))
json.dump(out, open(os.path.join(ROOT, 'build/info-video/glb-stats.json'), 'w'), indent=1)
groups = collections.defaultdict(lambda: collections.Counter())
for r in out:
    rel = r['rel']; g = '/'.join(rel.split('/')[:2]) if not rel.startswith('build/resort-blocks') else '/'.join(rel.split('/')[:3])
    for k in ('drawn', 'unique', 'meshes', 'materials', 'images', 'bytes'): groups[g][k] += r.get(k, 0) or 0
    groups[g]['files'] += 1
tot = collections.Counter()
for g, c in sorted(groups.items(), key=lambda x: -x[1]['drawn']):
    print(f"{g:45s} files {c['files']:4d}  drawn {c['drawn']:>12,}  unique {c['unique']:>12,}  materials {c['materials']:6d}  images {c['images']:5d}  {c['bytes']/1e6:9.1f} MB")
    tot.update(c)
print('TOTAL', {k: f'{v:,}' for k, v in tot.items()})
print('errors', [r['rel'] for r in out if 'error' in r][:5])
