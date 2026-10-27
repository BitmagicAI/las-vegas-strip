"""Original facade finish maps, packed into the optimized GLB."""
import bpy,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
E.colors.update({'ps-block':'9b9b93','ps-roof':'7d8079','ps-panel':'b6b3a5','ps-brown':'494043','ps-stone':'a9a18f','ps-green':'4f624a','ps-brick':'62554e','ps-joint':'89857a','ps-sign':'d5d5c6','ps-ink':'343b3c','ps-gold':'b5a456','ps-glass':'344344','ps-metal':'b1b5b2','ps-paper':'d3cdbb','ps-display0':'647e8d','ps-display1':'9d7569','ps-display2':'8a8b64','ps-concrete':'9f9f96','ps-stop':'998b43'})
bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('paradiseShop-exterior')
y,x=np.mgrid[:512,:512];rng=np.random.default_rng(236)
for key,m in E.materials.items():
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.85
 if key=='ps-glass':bs.inputs['Roughness'].default_value=.24;bs.inputs['Metallic'].default_value=.25;continue
 if key not in ['ps-block','ps-stone','ps-stone','ps-brick']:continue
 c=np.array([int(E.colors[key][i:i+2],16)/255 for i in [0,2,4]])
 noise=(rng.random((512,512))-.5)*.08
 if key in ['ps-block','ps-brick']:
  s=np.where((((x+(y//64%2)*64)%128)<3)|((y%64)<3),.68,1)+noise
 else:s=.92+.09*np.sin(y*.24+np.sin(x*.018))+noise
 rgba=np.ones((512,512,4),np.float32);rgba[:,:,:3]=s[:,:,None]*c
 im=bpy.data.images.new('Original '+key,width=512,height=512);im.pixels.foreach_set(rgba.flatten());im.pack()
 node=m.node_tree.nodes.new('ShaderNodeTexImage');node.image=im;m.node_tree.links.new(node.outputs['Color'],bs.inputs['Base Color'])
for key,m in E.materials.items():
 if key.startswith('ps-display'):
  im=bpy.data.images.load(str((E.OUT/('paradiseShop-display'+key[-1]+'-original.png')).resolve()));im.pack()
  t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=im;m.node_tree.links.new(t.outputs['Color'],m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])
for obj in bpy.context.scene.objects:
 if obj.type!='MESH':continue
 uv=obj.data.uv_layers.new(name='Metre finish')
 for p in obj.data.polygons:
  axis=max(range(3),key=lambda i:abs(p.normal[i]))
  for li in p.loop_indices:
   q=obj.data.vertices[obj.data.loops[li].vertex_index].co;uv.data[li].uv=(q.y*.5,q.z*.5) if axis==0 else (q.x*.5,q.z*.5) if axis==1 else(q.x*.5,q.y*.5)
bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/'paradiseShop-exterior.blend').resolve()))
bpy.ops.export_scene.gltf(filepath=str((E.OUT/'paradiseShop-exterior.glb').resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
print('EXPORTED paradiseShop-exterior')
