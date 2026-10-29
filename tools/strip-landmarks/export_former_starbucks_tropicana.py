"""Redistributable original stone/stucco maps; research photographs are not textures."""
import bpy,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
E.colors.update({'sb-stucco':'c7c7bd','sb-plinth':'92968c','sb-roof':'9e9f95','sb-coping':'b6b8ae','sb-trim':'9b9f95','sb-recess':'202a2c','sb-glass':'3c5050','sb-metal':'353c3d','sb-sill':'a4a69c','sb-chrome':'a8afae','sb-letter':'e3e3d6','sb-canopy':'606861','sb-seam':'7b8079','sb-paving':'a2a499','sb-equipment':'a6a79f','sb-service':'747c78'})
for part in ['exterior']:
 bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('former-starbucks-tropicana-'+part)
 rng=np.random.default_rng(256);size=512
 for key,m in E.materials.items():
  bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.86
  if key=='sb-glass':bs.inputs['Roughness'].default_value=.22;bs.inputs['Metallic'].default_value=.05;bs.inputs['Alpha'].default_value=1.0;m.surface_render_method='DITHERED'
  if key=='sb-canopy':m.use_backface_culling=False
  if key not in ['sb-stucco','sb-plinth']:continue
  c=np.array([int(E.colors[key][i:i+2],16)/255 for i in [0,2,4]])
  h=np.full((size,size),.2);shade=np.ones((size,size))
  h+=rng.random((size,size))*.025
  noise=(rng.random((size,size))-.5)*.065
  rgba=np.ones((size,size,4),np.float32);rgba[:,:,:3]=np.clip((shade+noise)[:,:,None]*c,0,1)
  im=bpy.data.images.new('Original '+key,width=size,height=size);im.pixels.foreach_set(rgba.flatten());im.pack()
  t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=im;m.node_tree.links.new(t.outputs['Color'],bs.inputs['Base Color'])
  dy,dx=np.gradient(h);n=np.dstack((-dx*2,-dy*2,np.ones_like(h)));n/=np.linalg.norm(n,axis=2)[:,:,None]
  rgba[:,:,:3]=n*.5+.5
  im=bpy.data.images.new('Original normal '+key,width=size,height=size);im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(rgba.flatten());im.pack()
  t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=im;normal=m.node_tree.nodes.new('ShaderNodeNormalMap');m.node_tree.links.new(t.outputs['Color'],normal.inputs['Color']);m.node_tree.links.new(normal.outputs['Normal'],bs.inputs['Normal'])
 for o in bpy.context.scene.objects:
  if o.type=='FONT':
   fp=Path('/System/Library/Fonts/Supplemental/Arial Bold.ttf')
   if fp.exists():o.data.font=bpy.data.fonts.load(str(fp),check_existing=True)
  if o.type!='MESH':continue
  uv=o.data.uv_layers.new(name='Metre finish')
  for p in o.data.polygons:
   axis=max(range(3),key=lambda i:abs(p.normal[i]))
   for li in p.loop_indices:
    q=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(q.y*.5,q.z*.5) if axis==0 else (q.x*.5,q.z*.5) if axis==1 else(q.x*.5,q.y*.5)
 bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/('former-starbucks-tropicana-'+part+'.blend')).resolve()))
 bpy.ops.export_scene.gltf(filepath=str((E.OUT/('former-starbucks-tropicana-'+part+'.glb')).resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
 print('EXPORTED former-starbucks-tropicana-exterior')
