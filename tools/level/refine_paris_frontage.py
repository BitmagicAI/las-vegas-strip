"""Keep the Louvre wall behind its recessed window trim; mirror the authoring fix without rebuilding the district."""
import bpy,json,ast,os
from pathlib import Path
bpy.ops.wm.open_mainfile(filepath='build/level/vegas.blend')
objects=[o for o in bpy.data.objects if 'Louvre street upper facade' in o.name]
assert len(objects)==1
objects[0].location.x=70.6
bpy.context.view_layer.update()
p=Path('build/level/vegas.mesh-level.json');data=json.loads(p.read_text())
hits=[c for c in data['colliders'] if 'Louvre street upper facade' in c.get('id','') or 'Louvre street upper facade' in c.get('name','')]
assert len(hits)==1,hits
hits[0]['position'][0]=70.6
p.write_text(json.dumps(data,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath('build/level/vegas.blend'))
source=ast.parse(Path('tools/level/vegas.py').read_text())
fn=next(n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=='fast_export')
exec(compile(ast.Module(body=[fn],type_ignores=[]),'vegas.py','exec'))
fast_export('build/level/vegas.glb')
print('Louvre wall corrected in blend, GLB and collision metadata',flush=True)
