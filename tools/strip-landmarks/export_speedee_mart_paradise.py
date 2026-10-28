import bpy,sys,math,numpy as np
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
E.colors.update({'sm-white':'d6d6ce','sm-plinth':'8e6d57','sm-red':'922a35','sm-yellow':'dfbe4a','sm-metal':'303332','sm-glass':'394b4b','sm-roof':'a6aaa4','sm-floor':'b4b2a5','sm-pipe':'8d9491','sm-cream':'d3c8ac','sm-ceiling':'dbdbce','sm-counter':'d2cbb8','sm-light':'eae6d5','sm-stock-0':'ae4434','sm-stock-1':'d5ae46','sm-stock-2':'3d6b87','sm-stock-3':'547c4a','sm-stock-4':'a58b67'})
for part in ['exterior','interior']:
 bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('speedee-mart-paradise-'+part)
 for obj in bpy.context.scene.objects:
  if obj.type=='MESH':obj.data.validate(verbose=True)
 for key,m in E.materials.items():
  bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.82
  if key=='sm-glass':bs.inputs['Roughness'].default_value=.24
  if key=='sm-metal':bs.inputs['Metallic'].default_value=.45
  if key=='sm-light':bs.inputs['Emission Color'].default_value=(.9,.86,.7,1);bs.inputs['Emission Strength'].default_value=.4
  if key not in ['sm-floor','sm-white','sm-cream']:continue
  n=256;yy,xx=np.mgrid[0:n,0:n];rng=np.random.default_rng(340);noise=rng.random((n,n))-.5;rgba=np.ones((n,n,4),np.float32)
  rgb=[int(E.colors[key][i:i+2],16)/255 for i in [0,2,4]]
  shade=1+noise*.035
  if key=='sm-floor':shade=np.where((xx%64<2)|(yy%64<2),.52,1)+noise*.025
  for c in range(3):rgba[:,:,c]=np.clip(rgb[c]*shade,0,1)
  im=bpy.data.images.new('Original Speedee '+key,width=n,height=n);im.pixels.foreach_set(rgba.flatten());im.pack();tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im;m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
 for obj in bpy.context.scene.objects:
  if obj.type!='MESH' or obj.data.materials[0].name not in ['Strip / sm-floor','Strip / sm-white','Strip / sm-cream']:continue
  uv=obj.data.uv_layers.new(name='Metre finishes')
  for poly in obj.data.polygons:
   axis=max(range(3),key=lambda i:abs(poly.normal[i]))
   for li in poly.loop_indices:
    p=obj.data.vertices[obj.data.loops[li].vertex_index].co;uv.data[li].uv=(p.y/1.8,p.z/1.8) if axis==0 else (p.x/1.8,p.z/1.8) if axis==1 else (p.x/1.8,p.y/1.8)
 bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/('speedee-mart-paradise-'+part+'.blend')).resolve()))
 bpy.ops.export_scene.gltf(filepath=str((E.OUT/('speedee-mart-paradise-'+part+'.glb')).resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
