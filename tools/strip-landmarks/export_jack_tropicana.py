"""Redistributable original stone/stucco maps; research photographs are not textures."""
import bpy,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
E.colors.update({'jk-brick':'626463','jk-stone':'99978c','jk-roof':'94958c','jk-red':'9c3542','jk-rib':'b44853','jk-metal':'626b70','jk-frame':'9a9d9c','jk-glass':'354c53','jk-chrome':'b5b8b4','jk-fascia':'8b9291','jk-stucco':'8d8d83','jk-timber':'7c6c56','jk-service':'515954','jk-equipment':'949b98','jk-paving':'a0a098','jk-light':'dbd6bd','jk-letter':'e5e5dd'})
for part in ['exterior']:
 bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('jack-tropicana-'+part)
 rng=np.random.default_rng(256);size=512
 for key,m in E.materials.items():
  bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.86
  if key in ['jk-metal','jk-chrome','jk-frame']:bs.inputs['Metallic'].default_value=.55;bs.inputs['Roughness'].default_value=.42
  if key=='jk-glass':bs.inputs['Roughness'].default_value=.22;bs.inputs['Metallic'].default_value=.05;bs.inputs['Alpha'].default_value=1.0;m.surface_render_method='DITHERED'
  m.use_backface_culling=False
  if key=='jk-light':bs.inputs['Emission Color'].default_value=(.95,.92,.8,1);bs.inputs['Emission Strength'].default_value=.35
  if key not in ['jk-stone','jk-brick']:continue
  c=np.array([int(E.colors[key][i:i+2],16)/255 for i in [0,2,4]])
  h=np.full((size,size),.2);shade=np.ones((size,size))
  if key!='jk-unused':
   rowheight=16 if key=='jk-stone' else 20
   brickwidth=70 if key=='jk-stone' else 62
   shade[:]=.65;h[:]=.12
   for row,y in enumerate(range(0,size,rowheight)):
    x=-(brickwidth//2 if row%2 else 0)
    while x<size:
     w=int(rng.integers(40,110)) if key=='jk-stone' else brickwidth
     lo=max(x+1,0);hi=min(x+w-1,size)
     h[y+1:min(y+rowheight-1,size),lo:hi]=rng.uniform(.65,.85)
     shade[y+1:min(y+rowheight-1,size),lo:hi]=rng.uniform(.87,1.08);x+=w
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
 bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/('jack-tropicana-'+part+'.blend')).resolve()))
 bpy.ops.export_scene.gltf(filepath=str((E.OUT/('jack-tropicana-'+part+'.glb')).resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
 print('EXPORTED jack-tropicana-'+part)
