"""Original procedural finish maps; source photos are references only."""
import bpy,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
E.colors.update({'gy-leaf':'536749','gy-leaf-dark':'344b35','gy-stucco':'bda381','gy-cream':'d4c7ae','gy-roof':'adafa6','gy-floor':'575651','gy-joint':'ac9477','gy-glass':'354449','gy-bronze':'62533c','gy-black':'252624','gy-gold':'a39154','gy-paving':'a59076','gy-pave-joint':'8c7a65','gy-equipment':'a6a99f','gy-room':'64454d','gy-ceiling':'3e303b','gy-burgundy':'4f2532','gy-counter':'49443f','gy-red':'803c4d','gy-bottle':'4d684d','gy-amber':'8c6431','gy-screen':'262e38','gy-sign':'c6ba80','gy-warm':'b9a270','gy-purple':'7b548c'})
for part in ['exterior','interior']:
 bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('gipsy-'+part)
 y,x=np.mgrid[:512,:512];rng=np.random.default_rng(250)
 for key,m in E.materials.items():
  bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.83
  if key in ['gy-warm','gy-sign']:
   bs.inputs['Emission Color'].default_value=bs.inputs['Base Color'].default_value;bs.inputs['Emission Strength'].default_value=.45
  if key=='gy-glass':bs.inputs['Roughness'].default_value=.23;bs.inputs['Metallic'].default_value=.25
  if key in ['gy-gold','gy-bronze']:bs.inputs['Metallic'].default_value=.5;bs.inputs['Roughness'].default_value=.48
  if key not in ['gy-stucco','gy-floor','gy-room','gy-counter','gy-paving']:continue
  c=np.array([int(E.colors[key][i:i+2],16)/255 for i in [0,2,4]])
  s=1+(rng.random((512,512))-.5)*.07
  if key=='gy-room':
   # Original botanical-like mottling, not a reproduction of the photographer's wallpaper.
   s+=.1*np.sin(x*.13+np.sin(y*.09))*np.cos(y*.15+np.sin(x*.05))
  if key=='gy-floor':
   s+=.045*np.sin(x*.03+np.sin(y*.045));s=np.where((x%256<2)|(y%128<2),s*.88,s)
   bs.inputs['Roughness'].default_value=.52
  rgba=np.ones((512,512,4),np.float32);rgba[:,:,:3]=np.clip(s[:,:,None]*c,0,1)
  im=bpy.data.images.new('Original '+key,width=512,height=512);im.pixels.foreach_set(rgba.flatten());im.pack()
  t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=im;m.node_tree.links.new(t.outputs['Color'],bs.inputs['Base Color'])
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
 bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/('gipsy-'+part+'.blend')).resolve()))
 bpy.ops.export_scene.gltf(filepath=str((E.OUT/('gipsy-'+part+'.glb')).resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
 print('EXPORTED gipsy-'+part)
