"""Move only decorative Flamingo Road markings to the corrected Caesars edge."""
import bpy,os,ast
from pathlib import Path
bpy.ops.wm.open_mainfile(filepath=os.path.abspath('build/level/vegas.blend'))
if not bpy.context.scene.get('caesars_road_aligned'):
 for ob in bpy.data.objects:
  if 'Flamingo Road' in ob.name or ' / crosswalk ' in ob.name:ob.location.y=-ob.location.y
 bpy.context.scene['caesars_road_aligned']=True
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath('build/level/vegas.blend'))
source=ast.parse(Path('tools/level/vegas.py').read_text());fn=next(n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=='fast_export');exec(compile(ast.Module(body=[fn],type_ignores=[]),'vegas.py','exec'));fast_export('build/level/vegas.glb')
