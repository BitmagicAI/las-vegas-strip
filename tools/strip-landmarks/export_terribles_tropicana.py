"""Redistributable original stone/stucco maps; research photographs are not textures."""
import bpy,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
E.colors.update({'th-label':'d5cbb0','th-amber':'72513c','th-bread':'ad7547','th-peach':'caa486','th-brown':'82665a','th-red':'84332f','th-blue':'29496b','th-white':'dddcd3','th-roof':'a1a298','th-black':'272c2b','th-glass':'344345','th-metal':'a6aba7','th-paving':'999b91','th-display':'8bada9','th-soffit':'bfc0b7','th-tile':'9d6147','th-floor':'bbb7a5','th-wall':'575b59','th-ceiling':'c9c8bd','th-grout':'656b66','th-green':'518369','th-light':'eeeacb'})
for part in ['exterior','interior']:
 bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('terribles-tropicana-'+part)
 rng=np.random.default_rng(256);size=512
 for key,m in E.materials.items():
  bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.86
  if key=='th-glass':bs.inputs['Roughness'].default_value=.22;bs.inputs['Metallic'].default_value=.05;bs.inputs['Alpha'].default_value=.28;m.surface_render_method='DITHERED'
  m.use_backface_culling=False
  if key=='th-light':bs.inputs['Emission Color'].default_value=(.95,.92,.8,1);bs.inputs['Emission Strength'].default_value=.35
  if key not in ['th-peach','th-tile']:continue
  c=np.array([int(E.colors[key][i:i+2],16)/255 for i in [0,2,4]])
  h=np.full((size,size),.2);shade=np.ones((size,size))
  if key=='ino-floor':
   yy,xx=np.mgrid[:size,:size];joints=(xx%64<2)|(yy%64<2);shade=np.where(joints,.32,1.0);h=np.where(joints,.05,.15)
  elif key!='th-peach':
   rowheight=32 if key=='ino-red-tile' else 64
   for y in range(0,size,rowheight):
    x=-int(rng.integers(10,100))
    while x<size:
     w=int(rng.integers(45,145) if key=='ino-red-tile' else rng.integers(65,150));lo=max(x+2,0);hi=min(x+w-2,size)
     h[y+2:min(y+rowheight-2,size),lo:hi]=rng.uniform(.65,.95)
     shade[y+2:min(y+rowheight-2,size),lo:hi]=rng.uniform(.88,1.12);x+=w
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
 bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/('terribles-tropicana-'+part+'.blend')).resolve()))
 bpy.ops.export_scene.gltf(filepath=str((E.OUT/('terribles-tropicana-'+part+'.glb')).resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
 print('EXPORTED terribles-tropicana-exterior')
