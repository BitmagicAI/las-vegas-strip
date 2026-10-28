import bpy,sys,math,numpy as np
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
E.colors.update({'se-stucco':'adafa8','se-white':'d0d0c5','se-membrane-paint':'979b96','se-soffit':'454a48','se-orange':'c6552c','se-red':'a72d37','se-green':'266354','se-steel-paint':'222b2b','se-glass':'33484a','se-letter':'dbd8c3','se-metal-paint':'858b85','se-screen':'28383a','se-rubber':'232525','se-yellow':'cba743','se-concrete':'9d9c91','se-cream':'bbb8a7','se-floor':'9e9e90','se-ceiling':'c9c7b9','se-cabinet':'4c514e','se-counter':'a29e8f','se-stock':'a88c5b','se-light':'d1d0bd'})
E.colors.update({'se-pack-red':'a73e37','se-pack-blue':'365c89','se-pack-gold':'b59a4b','se-pack-green':'496c45'})
for part in ['exterior','interior']:
 bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('seven-eleven-paradise-'+part)
 for obj in bpy.context.scene.objects:
  if obj.type=='MESH':obj.data.validate(verbose=True)
 for key,m in E.materials.items():
  bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.82
  if key=='se-glass':
   bs.inputs['Roughness'].default_value=.18;bs.inputs['Alpha'].default_value=.22
   m.surface_render_method='BLENDED';m.use_backface_culling=True
  if key=='se-metal-paint':bs.inputs['Metallic'].default_value=.45
  if key=='se-light':bs.inputs['Emission Color'].default_value=(.9,.86,.7,1);bs.inputs['Emission Strength'].default_value=.4
  if key not in ['se-floor','se-stucco','se-cream','se-counter']:continue
  n=256;yy,xx=np.mgrid[0:n,0:n];rng=np.random.default_rng(340);noise=rng.random((n,n))-.5;rgba=np.ones((n,n,4),np.float32)
  rgb=[int(E.colors[key][i:i+2],16)/255 for i in [0,2,4]]
  shade=1+noise*(.5 if key=='se-counter' else .035)
  if key=='se-floor':shade=np.where((xx%64<2)|(yy%64<2),.52,1)+noise*.025
  for c in range(3):rgba[:,:,c]=np.clip(rgb[c]*shade,0,1)
  im=bpy.data.images.new('Original Paradise 7Eleven '+key,width=n,height=n);im.pixels.foreach_set(rgba.flatten());im.pack();tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im;m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
 for obj in bpy.context.scene.objects:
  if obj.type!='MESH' or obj.data.materials[0].name not in ['Strip / se-floor','Strip / se-stucco','Strip / se-cream','Strip / se-counter']:continue
  uv=obj.data.uv_layers.new(name='Metre finishes')
  for poly in obj.data.polygons:
   axis=max(range(3),key=lambda i:abs(poly.normal[i]))
   for li in poly.loop_indices:
    p=obj.data.vertices[obj.data.loops[li].vertex_index].co;uv.data[li].uv=(p.y/1.8,p.z/1.8) if axis==0 else (p.x/1.8,p.z/1.8) if axis==1 else (p.x/1.8,p.y/1.8)
 bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/('seven-eleven-paradise-'+part+'.blend')).resolve()))
 bpy.ops.export_scene.gltf(filepath=str((E.OUT/('seven-eleven-paradise-'+part+'.glb')).resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
