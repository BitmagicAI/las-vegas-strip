"""Original facade finish maps, packed into the optimized GLB."""
import bpy,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
E.colors.update({'q-panel':'b6b3a5','q-brown':'493e3e','q-cream':'b6b3a5','q-green':'4f624a','q-roof':'7d817c','q-stone':'a9a18f','q-brick':'605450','q-joint':'827e73','q-sign':'d6d7ca','q-ink':'363b4d','q-red':'98494c','q-glass':'243030','q-metal':'999d9b','q-paper':'9b947e','q-dark':'262728','q-concrete':'9f9f96','q-stop':'998b43','q-floor':'403d3a','q-wall':'5e4b41','q-ceiling':'27282a','q-counter':'564b40','q-wood':'504232','q-vinyl':'30343c','q-screen':'45547c','q-bottle':'37594c','q-amber':'7b5e38','q-felt':'325c58','q-ball':'d8cb9a','q-lamp':'b9b3c0'})
for part in ['exterior','interior']:
 bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('quadz-'+part)
 y,x=np.mgrid[:512,:512];rng=np.random.default_rng(236)
 for key,m in E.materials.items():
  bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.85
  if key in ['q-screen','q-lamp']:
   bs.inputs['Emission Color'].default_value=bs.inputs['Base Color'].default_value;bs.inputs['Emission Strength'].default_value=.7
  if key=='q-glass':bs.inputs['Roughness'].default_value=.24;bs.inputs['Metallic'].default_value=.25;continue
  if key not in ['q-cream','q-wood','q-brick','q-wall','q-counter']:continue
  c=np.array([int(E.colors[key][i:i+2],16)/255 for i in [0,2,4]])
  noise=(rng.random((512,512))-.5)*.08
  if key in ['q-cream','q-brick']:
   s=np.where((((x+(y//64%2)*64)%128)<3)|((y%64)<3),.68,1)+noise
  elif key=='q-wood':s=.96+.035*np.sin(y*.24+np.sin(x*.018))+noise*.4
  else:s=1+noise*.35
  rgba=np.ones((512,512,4),np.float32);rgba[:,:,:3]=s[:,:,None]*c
  im=bpy.data.images.new('Original '+key,width=512,height=512);im.pixels.foreach_set(rgba.flatten());im.pack()
  node=m.node_tree.nodes.new('ShaderNodeTexImage');node.image=im;m.node_tree.links.new(node.outputs['Color'],bs.inputs['Base Color'])
 # Original abstract screen program; no copied broadcast or gaming artwork.
 m=E.materials.get('q-screen')
 if m:
  rgba=np.ones((512,512,4),np.float32);rgba[:,:,:3]=[.06,.10,.22]
  for j in range(4):
   for k in range(3):
    yy=35+j*110;xx=30+k*160
    rgba[yy:yy+80,xx:xx+135,:3]=[.34+.08*(k%2),.45,.57]
    rgba[yy+12:yy+64,xx+12:xx+120,:3]=[.12,.22+.04*j,.33]
    rgba[yy+69:yy+75,xx+20:xx+110,:3]=[.62,.52,.22]
  im=bpy.data.images.new('Original abstract video display',width=512,height=512);im.pixels.foreach_set(rgba.flatten());im.pack()
  bs=m.node_tree.nodes.get('Principled BSDF');t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=im;m.node_tree.links.new(t.outputs['Color'],bs.inputs['Base Color']);m.node_tree.links.new(t.outputs['Color'],bs.inputs['Emission Color'])
 for o in bpy.context.scene.objects:
  if o.type=='FONT' and o.data.body=='QUADZ':
   fp=Path('/System/Library/Fonts/Supplemental/Arial Bold.ttf')
   if fp.exists():o.data.font=bpy.data.fonts.load(str(fp),check_existing=True)
 for obj in bpy.context.scene.objects:
  if obj.type!='MESH':continue
  uv=obj.data.uv_layers.new(name='Metre finish')
  for p in obj.data.polygons:
   axis=max(range(3),key=lambda i:abs(p.normal[i]))
   for li in p.loop_indices:
    q=obj.data.vertices[obj.data.loops[li].vertex_index].co;uv.data[li].uv=(q.y*.5,q.z*.5) if axis==0 else (q.x*.5,q.z*.5) if axis==1 else(q.x*.5,q.y*.5)
 bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/('quadz-'+part+'.blend')).resolve()))
 bpy.ops.export_scene.gltf(filepath=str((E.OUT/('quadz-'+part+'.glb')).resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
 print('EXPORTED quadz-'+part)
