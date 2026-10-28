import bpy,sys,numpy as np
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
E.colors.update({'lh-stucco':'d2c5a8','lh-roof':'aeaaa0','lh-red':'95504b','lh-cream':'dfd6ba','lh-teal':'36746d','lh-seam':'466d68','lh-metal':'b6b9b3','lh-glass':'344e4b','lh-rib':'b4aa8e','lh-canopy':'b2b88b','lh-frame':'4c5551','lh-gold':'b8a366','lh-pot':'a66549','lh-wood':'67513a','lh-leaf':'426443','lh-equipment':'92958c'})
bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('lawrys-hughes-exterior')
for key,m in E.materials.items():
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.8
 if key in ['lh-metal','lh-teal','lh-frame']:bs.inputs['Metallic'].default_value=.55;bs.inputs['Roughness'].default_value=.38
 if key=='lh-glass':bs.inputs['Roughness'].default_value=.24;bs.inputs['Metallic'].default_value=.3
 if key=='lh-canopy':bs.inputs['Roughness'].default_value=.42
 if key not in ['lh-stucco','lh-red','lh-roof','lh-pot']:continue
 n=256;rng=np.random.default_rng(348);noise=rng.random((n,n))-.5;rgba=np.ones((n,n,4),np.float32)
 rgb=np.array([int(E.colors[key][i:i+2],16)/255 for i in [0,2,4]])
 for c in range(3):rgba[:,:,c]=np.clip(rgb[c]*(1+noise*.07),0,1)
 im=bpy.data.images.new('Original Lawrys '+key,width=n,height=n);im.pixels.foreach_set(rgba.flatten());im.pack();tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im;m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
for obj in bpy.context.scene.objects:
 if obj.type!='MESH':continue
 obj.data.validate(verbose=True);uv=obj.data.uv_layers.new(name='Metre finishes')
 for poly in obj.data.polygons:
  axis=max(range(3),key=lambda i:abs(poly.normal[i]))
  for li in poly.loop_indices:
   p=obj.data.vertices[obj.data.loops[li].vertex_index].co;uv.data[li].uv=(p.y/2,p.z/2) if axis==0 else (p.x/2,p.z/2) if axis==1 else (p.x/2,p.y/2)
bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/'lawrys-hughes-exterior.blend').resolve()))
bpy.ops.export_scene.gltf(filepath=str((E.OUT/'lawrys-hughes-exterior.glb').resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
