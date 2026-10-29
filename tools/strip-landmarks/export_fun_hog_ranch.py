"""Original timber and paint palette; no reference photograph pixels."""
import bpy,sys,numpy as np
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
palette={'olive':'666d50','batten':'555e48','roof':'777b70','foundation':'85837b','white':'dddcc9','sign':'434c3a','dark':'202323','paving':'959080','service':'8b9292','floor':'423b32','ceiling':'503a28','wood':'765138','joint':'332b22','beam':'493326','darkwood':'402e24','metal':'777a75','seat':'362e26','brass':'a08c53','label':'c6b893','coaster':'999381','screen':'202b2c','lamp':'f0ddb0','bottle-0':'354b36','bottle-1':'69502e','bottle-2':'563c2f'}
E.colors.update({'fh-'+k:v for k,v in palette.items()})
def finishes():
 y,x=np.mgrid[:512,:512];noise=np.random.default_rng(332).random((512,512))-.5
 for key,m in E.materials.items():
  bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.78
  if key in ['fh-metal','fh-brass']:bs.inputs['Metallic'].default_value=.7;bs.inputs['Roughness'].default_value=.3
  if 'bottle' in key or key=='fh-seat':bs.inputs['Roughness'].default_value=.34
  if key=='fh-lamp':bs.inputs['Emission Color'].default_value=(1,.72,.4,1);bs.inputs['Emission Strength'].default_value=.65
  if key not in ['fh-wood','fh-ceiling','fh-darkwood','fh-beam','fh-olive','fh-batten']:continue
  base=[12.92*v if v<=.0031308 else 1.055*v**(1/2.4)-.055 for v in bs.inputs['Base Color'].default_value[:3]]
  shade=.94+.035*np.sin(y*.17+np.sin(x*.025)*2)+.025*np.sin(y*.73+np.sin(x*.04))+noise*.06
  if key in ['fh-olive','fh-batten']:shade=1+noise*.035
  rgba=np.ones((512,512,4),np.float32)
  for c,v in enumerate(base):rgba[:,:,c]=np.clip(v*shade,0,1)
  im=bpy.data.images.new('Original Fun Hog '+key,width=512,height=512);im.pixels.foreach_set(rgba.ravel());im.pack();tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im;m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
for part in ['exterior','interior']:
 bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('fun-hog-ranch-'+part)
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  uv=o.data.uv_layers.new(name='Metres')
  for p in o.data.polygons:
   axis=max(range(3),key=lambda i:abs(p.normal[i]));axes=[i for i in range(3) if i!=axis]
   for li in p.loop_indices:
    q=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(q[axes[0]],q[axes[1]])
 finishes()
 bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/('fun-hog-ranch-'+part+'.blend')).resolve()))
 bpy.ops.export_scene.gltf(filepath=str((E.OUT/('fun-hog-ranch-'+part+'.glb')).resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
 print('EXPORTED fun-hog-ranch-'+part)
