import bpy,sys,numpy as np,hashlib,json
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
E.colors.update({'aj-stucco': 'd5d2c9', 'aj-tile': '35383b', 'aj-tilecap': '414448', 'aj-dark': '252729', 'aj-membrane': 'aaa9a0', 'aj-joint': '333537', 'aj-stone0': 'c9caca', 'aj-stone1': 'deddd6', 'aj-stone2': 'b4b8b8', 'aj-letter': 'e0c28c', 'aj-window': '283e44', 'aj-mullion': '494d50', 'aj-service': 'a4a49a', 'aj-alloy': '8f999a', 'aj-paving': '9b9387', 'aj-red': '984b43', 'aj-inwall': '373331', 'aj-floor': '8c7460', 'aj-weave': '9a784d', 'aj-straw': 'b59767', 'aj-leaf': '647447', 'aj-pendant': '927044', 'aj-lamp': 'ffe6a5', 'aj-leather': 'a76736', 'aj-wood': '8e5934', 'aj-woven': '242b2b', 'aj-pot': '99704c', 'aj-brick': 'a77b62', 'aj-brick0':'a5785b','aj-brick1':'ab8167','aj-brick2':'987257', 'aj-mortar': '6e6154', 'aj-counter': 'b9a48b', 'aj-bottle': '698977', 'aj-screen': '45585e'})
for part in ['exterior','interior']:
 bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('los-amores-julia-sahara-'+part)
 for key,m in E.materials.items():
  bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.85
  if key in ['aj-alloy']:bs.inputs['Metallic'].default_value=.35;bs.inputs['Roughness'].default_value=.42
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
 bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/('los-amores-julia-sahara-'+part+'.blend')).resolve()))
 bpy.ops.export_scene.gltf(filepath=str((E.OUT/('los-amores-julia-sahara-'+part+'.glb')).resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
h=hashlib.sha256()
for f in sorted(E.OUT.glob('*.glb')):h.update(f.read_bytes())
for f in sorted(E.OUT.glob('*-collision.json')):h.update(f.read_bytes())
h.update((E.OUT/'venues.json').read_bytes());(E.OUT/'version.json').write_text(json.dumps({'revision':h.hexdigest()[:16]}))
