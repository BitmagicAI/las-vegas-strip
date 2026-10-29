import bpy,sys,numpy as np,hashlib,json
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
E.colors.update({'mr-ochre': 'c98e34', 'mr-blue': '153b7f', 'mr-red': 'ae302f', 'mr-seam': '25498a', 'mr-membrane': 'b8b9af', 'mr-dark': '272c2b', 'mr-white': 'dfdfcf', 'mr-stone': '7e7265', 'mr-stone0': '948878', 'mr-stone1': '6b6862', 'mr-stone2': 'a09280', 'mr-mullion': 'a0abaa', 'mr-paving': '888a87', 'mr-alloy': '929fa4', 'mr-leaf': '3c5829', 'mr-service': '74736c', 'mr-yellow': 'd2ab36', 'mr-inblue': '286486', 'mr-tile': '50483e', 'mr-grout': '4c4942', 'mr-ceiling': 'd7d5c9', 'mr-lamp': 'faf3d9', 'mr-table': '644831', 'mr-orange': 'c88525', 'mr-green': '366444', 'mr-seat': '853e3d', 'mr-screen': '385c8a'})
for part in ['exterior','interior']:
 bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('mi-ranchito-sahara-'+part)
 for key,m in E.materials.items():
  bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.85
  if key in ['mr-alloy','mr-mullion']:bs.inputs['Metallic'].default_value=.35;bs.inputs['Roughness'].default_value=.42
  if key=='unused-glass':bs.inputs['Alpha'].default_value=1;bs.inputs['Roughness'].default_value=.3;m.surface_render_method='BLENDED'
 for obj in bpy.context.scene.objects:
  if obj.type=='FONT':
   obj.data.resolution_u=3;obj.data.bevel_depth=0
   font=Path('/System/Library/Fonts/Supplemental/Arial Bold.ttf')
   if font.exists():obj.data.font=bpy.data.fonts.load(str(font),check_existing=True)
  if obj.type!='MESH':continue
  obj.data.validate();uv=obj.data.uv_layers.new(name='Metre finishes')
  for poly in obj.data.polygons:
   axis=max(range(3),key=lambda i:abs(poly.normal[i]))
   for li in poly.loop_indices:
    p=obj.data.vertices[obj.data.loops[li].vertex_index].co;uv.data[li].uv=(p.y/2,p.z/2) if axis==0 else (p.x/2,p.z/2) if axis==1 else (p.x/2,p.y/2)
 bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/('mi-ranchito-sahara-'+part+'.blend')).resolve()))
 bpy.ops.export_scene.gltf(filepath=str((E.OUT/('mi-ranchito-sahara-'+part+'.glb')).resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
h=hashlib.sha256()
for f in sorted(E.OUT.glob('*.glb')):h.update(f.read_bytes())
for f in sorted(E.OUT.glob('*-collision.json')):h.update(f.read_bytes())
h.update((E.OUT/'venues.json').read_bytes());(E.OUT/'version.json').write_text(json.dumps({'revision':h.hexdigest()[:16]}))
