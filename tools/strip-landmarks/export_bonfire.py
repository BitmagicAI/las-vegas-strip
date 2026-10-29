"""Original rough stucco and roof finishes; no reference pixels embedded."""
import bpy,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
E.colors.update({'bf-stucco':'c9bd9c','bf-band':'ab997c','bf-base':'8b8271','bf-roof':'928d7f','bf-red':'923a32','bf-gold':'b39a58','bf-sign':'353034','bf-cream':'d4cdb5','bf-metal':'92948a','bf-conduit':'aaa28d','bf-door':'5a554c','bf-awning':'272b2a','bf-bin':'2e302b','bf-concrete':'96978e','bf-black':'292c2b','bf-coping':'928975'})
bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('bonfire-exterior')
rng=np.random.default_rng(242)
for key,m in E.materials.items():
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.94
 if key not in ['bf-stucco','bf-band','bf-base','bf-roof','bf-concrete']:continue
 c=np.array([int(E.colors[key][i:i+2],16)/255 for i in [0,2,4]])
 a=rng.random((512,512));s=.91+.15*a
 rgba=np.ones((512,512,4),np.float32);rgba[:,:,:3]=s[:,:,None]*c
 im=bpy.data.images.new('Original rough '+key,width=512,height=512);im.pixels.foreach_set(rgba.flatten());im.pack()
 tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im;m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])

for obj in list(bpy.context.scene.objects):
 if obj.type=='FONT' and obj.data.body=='BONFIRE':
  fp=Path('/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf')
  if fp.exists():obj.data.font=bpy.data.fonts.load(str(fp),check_existing=True)
  obj.data.size*=1.2;obj.data.extrude=.025;obj.data.bevel_depth=.004;obj.data.resolution_u=6
  outline=obj.copy();outline.data=obj.data.copy();outline.data.offset=.012;outline.data.materials.clear();outline.data.materials.append(E.material('bf-gold'));bpy.context.collection.objects.link(outline)
  from mathutils import Vector
  outline.location-=obj.rotation_euler.to_matrix() @ Vector((0,0,.012))

for obj in bpy.context.scene.objects:
 if obj.type!='MESH':continue
 uv=obj.data.uv_layers.new(name='Metre finish')
 for p in obj.data.polygons:
  axis=max(range(3),key=lambda i:abs(p.normal[i]))
  for li in p.loop_indices:
   q=obj.data.vertices[obj.data.loops[li].vertex_index].co;uv.data[li].uv=(q.y,q.z) if axis==0 else (q.x,q.z) if axis==1 else(q.x,q.y)
bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/'bonfire-exterior.blend').resolve()))
bpy.ops.export_scene.gltf(filepath=str((E.OUT/'bonfire-exterior.glb').resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
print('EXPORTED bonfire-exterior')
