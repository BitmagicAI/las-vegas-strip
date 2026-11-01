"""Export only the obelisk; retain its original procedural stone maps."""
import sys,hashlib,json
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
import bpy
E.colors['lob-gold-letter']='b39a64'
bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('luxorObelisk-exterior')
font=Path('/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf')
for obj in bpy.context.scene.objects:
 if obj.type=='FONT' and obj.data.materials and obj.data.materials[0].name in ['Strip / lob-blue-letter','Strip / lob-gold-letter']:
  if font.exists():obj.data.font=bpy.data.fonts.load(str(font),check_existing=True)
  obj.data.extrude=.045;obj.data.bevel_depth=.008
bpy.ops.export_scene.gltf(filepath=str((E.OUT/'luxorObelisk-exterior.glb').resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
(E.OUT/'version.json').write_text(json.dumps({'revision':hashlib.sha256((E.OUT/'luxorObelisk-exterior.glb').read_bytes()+(E.OUT/'venues.json').read_bytes()).hexdigest()[:16]}))
