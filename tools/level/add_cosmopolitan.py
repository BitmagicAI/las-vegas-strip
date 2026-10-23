"""Idempotently replace the old skyline block in the current editable level."""
import sys,os,json,ast
from pathlib import Path
sys.path.insert(0,'tools/level');sys.path.insert(0,'tools/blender-level')
from bmlevel import level,scene
import bpy
from cosmopolitan import build_cosmopolitan
from geometry_quality import orient_closed_solids
bpy.ops.wm.open_mainfile(filepath=os.path.abspath('build/level/vegas.blend'))
old=[o for o in bpy.data.objects if o.name.startswith('Cosmopolitan')]
print('Replacing',len(old),'old Cosmopolitan objects',flush=True)
bpy.data.batch_remove(old)
print('Cleanup complete',flush=True)
for m in list(bpy.data.materials):
    if m.name.startswith('co_'):bpy.data.materials.remove(m)
meta=build_cosmopolitan()
addition=level.mesh_level_json()
path=Path('build/level/vegas.mesh-level.json');data=json.loads(path.read_text())
for k in ['colliders','volumes','landmarks','lights']:
    data[k]=[r for r in data[k] if not r['name'].startswith('Cosmopolitan')]+addition[k]
data['extras']['links']=[r for r in data['extras']['links'] if not r['from'].startswith('Cosmopolitan')]+addition['extras']['links']
data['extras']['doors']=[r for r in data['extras']['doors'] if not r.startswith('Cosmopolitan')]+addition['extras']['doors']
path.write_text(json.dumps(data,indent=2))
dp=Path('build/level/vegas.doors.json');doors=json.loads(dp.read_text());doors=[d for d in doors if not d['id'].startswith('Cosmopolitan')]+level.doors_json();dp.write_text(json.dumps(doors,indent=2))
# Local audit includes all foundation/collision context; full level stays authoritative.
Path('build/cosmopolitan/addition.mesh-level.json').write_text(json.dumps(addition,indent=2))
orient_closed_solids();bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath('build/level/vegas.blend'))
source=ast.parse(Path('tools/level/vegas.py').read_text());fn=next(n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=='fast_export');exec(compile(ast.Module(body=[fn],type_ignores=[]),'vegas.py','exec'));fast_export('build/level/vegas.glb')
p=Path('src/work/vegas-missions.json');missions=json.loads(p.read_text());missions['cosmopolitan']=meta;p.write_text(json.dumps(missions,indent=2))
print('COSMOPOLITAN COMPLETE',len(addition['colliders']),'colliders;',len(data['colliders']),'total',flush=True)
