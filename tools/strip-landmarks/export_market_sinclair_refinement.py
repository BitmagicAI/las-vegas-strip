"""Export only the two market and Sinclair frontages; installation and shared bake are separate."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path("tools/strip-landmarks").resolve()))
import export as E
import bpy
for key in ["market1700","sinclair1705"]:
 bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add(key+"-exterior")
 # Match the heavy market fascia lettering without changing other exporters.
 if key=='market1700':
  import json
  labels=json.loads((E.OUT/(key+'-exterior.json')).read_text())['labels']
  for label in labels:
   if 'fitWidth' not in label:continue
   obj=bpy.data.objects.get(label['text']);font=Path('/System/Library/Fonts/Supplemental/Arial Bold.ttf')
   if font.exists():obj.data.font=bpy.data.fonts.load(str(font),check_existing=True)
   bpy.context.view_layer.update()
   width=max(v[0] for v in obj.bound_box)-min(v[0] for v in obj.bound_box)
   if width>0:obj.scale.x=label['fitWidth']/width
  bpy.context.view_layer.update()
 bpy.ops.export_scene.gltf(filepath=str((E.OUT/(key+"-exterior.glb")).resolve()),export_format="GLB",export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
