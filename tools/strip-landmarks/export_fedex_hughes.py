import bpy,sys,numpy as np,hashlib,json
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
E.colors.update({'fx-stucco':'b7b0a1','fx-membrane':'a4a7a3','fx-tile':'75635e','fx-trim':'aea297','fx-black':'222829','fx-clear':'aec9c7','fx-letter':'e4e2d8','fx-lamp':'e8ebdf','fx-concrete':'a3a29b','fx-panel':'a8aba5','fx-steel':'858e91','fx-wall':'b8b9b2','fx-carpet':'555654','fx-ceiling':'c2c5bf','fx-purple':'463b68','fx-grid':'7c817f','fx-cabinet':'b8ad92','fx-top':'999c94','fx-edge':'777669','fx-screen':'425b65','fx-key':'777f80','fx-package':'627461','fx-paper':'d4d6cf','fx-carton':'a88e65'})
for part in ['exterior','interior']:
 bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('fedex-hughes-'+part)
 for key,m in E.materials.items():
  bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.85
  if key in ['fx-steel','fx-black']:bs.inputs['Metallic'].default_value=.35;bs.inputs['Roughness'].default_value=.42
  if key=='fx-clear':bs.inputs['Alpha'].default_value=.18;bs.inputs['Roughness'].default_value=.3;m.surface_render_method='BLENDED'
  if key=='fx-lamp':bs.inputs['Emission Color'].default_value=(.9,.95,1,1);bs.inputs['Emission Strength'].default_value=.15
  if key not in ['fx-tile','fx-carpet','fx-ceiling']:continue
  n=256;yy,xx=np.mgrid[:n,:n];rng=np.random.default_rng(359);shade=1+(rng.random((n,n))-.5)*(.13 if key=='fx-carpet' else .045)
  if key=='fx-tile':
   shade*=np.where((xx%64<1)|(yy%64<1),.62,1)
   shade*=1+.045*np.sin((xx//64)*17+(yy//64)*5)
  rgba=np.ones((n,n,4),np.float32);rgb=[int(E.colors[key][i:i+2],16)/255 for i in [0,2,4]]
  for c in range(3):rgba[:,:,c]=np.clip(rgb[c]*shade,0,1)
  im=bpy.data.images.new('Original FedEx '+key,width=n,height=n);im.pixels.foreach_set(rgba.flatten());im.pack();tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im;m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
 for obj in bpy.context.scene.objects:
  if obj.type!='MESH':continue
  obj.data.validate();uv=obj.data.uv_layers.new(name='Metre finishes')
  for poly in obj.data.polygons:
   axis=max(range(3),key=lambda i:abs(poly.normal[i]))
   for li in poly.loop_indices:
    p=obj.data.vertices[obj.data.loops[li].vertex_index].co;uv.data[li].uv=(p.y/2,p.z/2) if axis==0 else (p.x/2,p.z/2) if axis==1 else (p.x/2,p.y/2)
 bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/('fedex-hughes-'+part+'.blend')).resolve()))
 bpy.ops.export_scene.gltf(filepath=str((E.OUT/('fedex-hughes-'+part+'.glb')).resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
h=hashlib.sha256()
for f in sorted(E.OUT.glob('*.glb')):h.update(f.read_bytes())
for f in sorted(E.OUT.glob('*-collision.json')):h.update(f.read_bytes())
h.update((E.OUT/'venues.json').read_bytes());(E.OUT/'version.json').write_text(json.dumps({'revision':h.hexdigest()[:16]}))
