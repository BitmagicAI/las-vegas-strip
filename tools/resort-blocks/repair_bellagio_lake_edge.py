"""Selective cached lake-edge repair. No road, tower, tree or interior rebuild.

python3 tools/resort-blocks/repair_bellagio_lake_edge.py
blender -b --python tools/resort-blocks/export_bellagio.py -- --only bellagioBlock-exterior
Then optimize/install this GLB alone. See BELLAGIO-BUILD.md.
"""
import sys,json,hashlib
from pathlib import Path
sys.path.insert(0,'tools/strip-landmarks')
from common import Meshes
from bellagio_edge_ownership import reconcile,close_roadside,support_roadside_verge
OUT=Path('build/resort-blocks/bellagio')
p=OUT/'bellagioBlock-exterior.json';doc=json.loads(p.read_text());b=Meshes()
b.groups={i:g for i,g in enumerate(doc['meshes'])}
b.solids['bellagioBlock-exterior']=json.loads((OUT/'bellagioBlock-exterior-collision.json').read_text())
def sha(g):return hashlib.sha256(json.dumps(g,separators=(',',':')).encode()).hexdigest()
before={i:sha(g) for i,g in b.groups.items()}
old_collision=json.loads((OUT/'bellagioBlock-exterior-collision.json').read_text())
city=json.loads(Path('build/geographic-strip/city-meshes.json').read_text())
report={}
for g in b.groups.values():
    if g['source']=='lakefront-fountain-array':
        delta=min(0,-1.6-max(v[1] for v in g['vertices']))
        for v in g['vertices']:v[1]+=delta
        report['hardwareLoweredM']=-delta
if not any(g['source']=='lakefront-roadside-closures' for g in b.groups.values()):
    report['roadsideClosureM2']=close_roadside(b,city)
report['vergeSupportTrianglesAdded']=support_roadside_verge(b,city)
report['ownership']=reconcile(b)
report['changedExistingGroups']=[{'source':b.groups[i]['source'],'material':b.groups[i]['material']} for i,h in before.items() if sha(b.groups[i])!=h]
allowed={'lakefront-strip-promenade','lakefront-lake','south-arrival-landscape','lakefront-fountain-array','lakefront-roadside-closures'}
assert all(g['source'] in allowed for g in report['changedExistingGroups'])
report['unchangedExistingGroups']=len(before)-len(report['changedExistingGroups'])
# Keep the appended canopy colliders, while replacing only the author's prefix.
runtime_path=OUT/'bellagioBlock-exterior-runtime-collision.json'
if runtime_path.exists():
 runtime=json.loads(runtime_path.read_text());nv=len(old_collision['vertices']);ni=len(old_collision['indices'])
 assert runtime['vertices'][:nv]==old_collision['vertices'] and runtime['indices'][:ni]==old_collision['indices'], 'Runtime collision has other edits; do not overwrite'
 new=b.solids['bellagioBlock-exterior'];shift=(len(new['vertices'])-nv)//3
 runtime['vertices']=new['vertices']+runtime['vertices'][nv:]
 runtime['indices']=new['indices']+[i+shift if i>=nv//3 else i for i in runtime['indices'][ni:]]
# Validate the runtime prefix before changing either authoring file.
doc['meshes']=list(b.groups.values());p.write_text(json.dumps(doc,separators=(',',':')))
(OUT/'bellagioBlock-exterior-collision.json').write_text(json.dumps(b.solids['bellagioBlock-exterior'],separators=(',',':')))
(OUT/'lake-edge-ownership.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if runtime_path.exists():
 runtime_path.write_text(json.dumps(runtime,separators=(',',':')))
 h=hashlib.sha256()
 for f in sorted(OUT.glob('*.glb')):h.update(f.read_bytes())
 h.update((OUT/'venues.json').read_bytes());h.update(runtime_path.read_bytes())
 (OUT/'version.json').write_text(json.dumps({'revision':h.hexdigest()[:16]}))
