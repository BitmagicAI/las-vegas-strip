"""Original material maps and metre-space UVs for Ferraro’s exterior."""
import bpy,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
E.colors.update({'hd-tan': 'c1ab7b', 'hd-roof': 'b1aea4', 'hd-red': '804143', 'hd-red-joint': '6d383d', 'hd-cap': 'c9bc9c', 'hd-glass': '41575b', 'hd-metal': '363c3a', 'hd-joint': 'ad956d', 'hd-white': 'e4e2d3', 'hd-pink': 'ba3655', 'hd-green': '4d873f', 'hd-orange': 'd78130', 'hd-brown': '5b4638', 'hd-equipment': 'a4a79f', 'hd-service': '8c897d', 'hd-paving': 'aaa797'})
for part in ['exterior']:
 bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('harmon-dining-'+part)
 y,x=np.mgrid[:512,:512];rng=np.random.default_rng(248)
 for key,m in E.materials.items():
  bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.87
  if key in ('fr-fabric','fr-stripe'):m.use_backface_culling=False
  if key=='hd-glass':bs.inputs['Roughness'].default_value=.26;bs.inputs['Metallic'].default_value=.25
  if key=='fr-lamp':bs.inputs['Emission Color'].default_value=bs.inputs['Base Color'].default_value;bs.inputs['Emission Strength'].default_value=.08
  if key not in ['hd-tan','hd-red','hd-paving']:continue
  c=np.array([int(E.colors[key][i:i+2],16)/255 for i in [0,2,4]])
  noise=(rng.random((512,512))-.5)*.10;s=1+noise
  rgba=np.ones((512,512,4),np.float32);rgba[:,:,:3]=np.clip(s[:,:,None]*c,0,1)
  im=bpy.data.images.new('Original '+key,width=512,height=512);im.pixels.foreach_set(rgba.flatten());im.pack()
  t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=im;m.node_tree.links.new(t.outputs['Color'],bs.inputs['Base Color'])
 for o in bpy.context.scene.objects:
  if o.type=='FONT':
   fp=Path('/System/Library/Fonts/Supplemental/Arial Bold Italic.ttf' if o.data.body=='Roberto’s' else '/System/Library/Fonts/Supplemental/Arial Bold.ttf')
   if fp.exists():o.data.font=bpy.data.fonts.load(str(fp),check_existing=True)
  if o.type!='MESH':continue
  uv=o.data.uv_layers.new(name='Metre finish')
  for p in o.data.polygons:
   axis=max(range(3),key=lambda i:abs(p.normal[i]))
   for li in p.loop_indices:
    q=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(q.y*.5,q.z*.5) if axis==0 else (q.x*.5,q.z*.5) if axis==1 else(q.x*.5,q.y*.5)
 bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/('harmon-dining-'+part+'.blend')).resolve()))
 bpy.ops.export_scene.gltf(filepath=str((E.OUT/('harmon-dining-'+part+'.glb')).resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
 print('EXPORTED harmon-dining-'+part)
