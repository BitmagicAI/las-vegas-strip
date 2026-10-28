import bpy,sys,math,numpy as np
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
E.colors.update({'nl-stucco':'b6b6ae','nl-roof-paint':'999b95','nl-charcoal':'505654','nl-trim-paint':'b9bbb5','nl-panel-dark':'454d46','nl-panel-brown':'625346','nl-block':'c1c1b8','nl-doorframe':'444b48','nl-glass':'344c50','nl-white':'d8d9cc','nl-green':'5f9a4b','nl-metal-paint':'7a807b','nl-lamp':'e0ddbd','nl-planter':'656b65','nl-soil':'37352c','nl-leaf':'3b5b35','nl-umbrella':'c2d4b1'})
for part in ['exterior']:
 bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('nuleaf-twain-'+part)
 for obj in bpy.context.scene.objects:
  if obj.type=='MESH':obj.data.validate(verbose=True)
 for key,m in E.materials.items():
  bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.82
  if key=='nl-glass':
   bs.inputs['Roughness'].default_value=.3
  if key=='nl-metal-paint':bs.inputs['Metallic'].default_value=.45
  if key=='nl-lamp':bs.inputs['Emission Color'].default_value=(.9,.86,.7,1);bs.inputs['Emission Strength'].default_value=.4
  if key not in ['nl-block','nl-stucco','nl-panel-brown']:continue
  n=256;yy,xx=np.mgrid[0:n,0:n];rng=np.random.default_rng(340);noise=rng.random((n,n))-.5;rgba=np.ones((n,n,4),np.float32)
  rgb=[int(E.colors[key][i:i+2],16)/255 for i in [0,2,4]]
  shade=1+noise*(.04 if key=='nl-panel-brown' else .035)
  if key=='nl-panel-brown':shade*=np.where(yy%27<2,.72,1)
  if key=='nl-block':shade=np.where((xx%32<1)|(yy%16<1),.52,1)+noise*.025
  for c in range(3):rgba[:,:,c]=np.clip(rgb[c]*shade,0,1)
  im=bpy.data.images.new('Original NuLeaf Twain '+key,width=n,height=n);im.pixels.foreach_set(rgba.flatten());im.pack();tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im;m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
 for obj in bpy.context.scene.objects:
  if obj.type!='MESH' or obj.data.materials[0].name not in ['Strip / nl-block','Strip / nl-stucco','Strip / nl-stucco','Strip / nl-panel-brown']:continue
  uv=obj.data.uv_layers.new(name='Metre finishes')
  for poly in obj.data.polygons:
   axis=max(range(3),key=lambda i:abs(poly.normal[i]))
   for li in poly.loop_indices:
    p=obj.data.vertices[obj.data.loops[li].vertex_index].co;uv.data[li].uv=(p.y/1.8,p.z/1.8) if axis==0 else (p.x/1.8,p.z/1.8) if axis==1 else (p.x/1.8,p.y/1.8)
 bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/('nuleaf-twain-'+part+'.blend')).resolve()))
 bpy.ops.export_scene.gltf(filepath=str((E.OUT/('nuleaf-twain-'+part+'.glb')).resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
