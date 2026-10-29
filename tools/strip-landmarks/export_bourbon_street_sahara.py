import bpy,sys,numpy as np,hashlib,json
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
E.colors.update({'bs-stucco': 'c7b99b', 'bs-membrane': 'b9b7ad', 'bs-cornice': 'b1a38a', 'bs-service': '9b9b94', 'bs-dark': '272728', 'bs-wood': '655341', 'bs-brick': '8e6654', 'bs-mortar': 'b3a58b', 'bs-window': '29393c', 'bs-mullion': '4c443c', 'bs-letter': 'e0dfce', 'bs-red': 'a43b34', 'bs-green': '354e40', 'bs-canopy': '979a94', 'bs-alloy': 'a7aaa3', 'bs-paving': '9a8a78', 'bs-inwall': 'b7ab92', 'bs-carpet': '635e55', 'bs-felt': '3d9291', 'bs-ball0': 'eee4c9', 'bs-ball1': 'c2a33b', 'bs-ball2': 'a43d38', 'bs-shade0': 'ba9d44', 'bs-shade1': 'bcae68', 'bs-shade2': '70856a', 'bs-lamp': 'ffe4a3', 'bs-screen': '4c7781', 'bs-art0': '8a443b', 'bs-art1': 'a99b72', 'bs-art2': '536f68', 'bs-board0': '807c6f', 'bs-board1': '8f8b7c', 'bs-board2': '74756c'})
for part in ['exterior','interior']:
 bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('bourbon-street-sahara-'+part)
 for key,m in E.materials.items():
  bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.85
  if key=='bs-carpet':
   rng=np.random.default_rng(45);noise=rng.uniform(-.055,.055,(256,256,1));base=np.array([.38,.35,.30]).reshape(1,1,3)
   pixels=np.concatenate([np.clip(base+noise,0,1),np.ones((256,256,1))],axis=2).astype(np.float32)
   im=bpy.data.images.new('Original woven carpet',width=256,height=256);im.pixels.foreach_set(pixels.ravel());im.pack()
   tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im;m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
  if key in ['bs-alloy']:bs.inputs['Metallic'].default_value=.35;bs.inputs['Roughness'].default_value=.42
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
 bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/('bourbon-street-sahara-'+part+'.blend')).resolve()))
 bpy.ops.export_scene.gltf(filepath=str((E.OUT/('bourbon-street-sahara-'+part+'.glb')).resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
h=hashlib.sha256()
for f in sorted(E.OUT.glob('*.glb')):h.update(f.read_bytes())
for f in sorted(E.OUT.glob('*-collision.json')):h.update(f.read_bytes())
h.update((E.OUT/'venues.json').read_bytes());(E.OUT/'version.json').write_text(json.dumps({'revision':h.hexdigest()[:16]}))
