"""Export original saloon geometry and repeatable finish maps; no reference pixels."""
import bpy,sys,math
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
E.colors.update({'dd-block':'a2a09a','dd-floor':'49413c','dd-roof':'787978','dd-trim':'939590','dd-green':'526c47','dd-brick':'62534d','dd-sign':'d3d1b3','dd-dark':'292a2b','dd-red':'8d3635','dd-stone':'a5a39b','dd-shingle':'555252','dd-metal':'666b6c','dd-poster':'767064','dd-ceiling':'514d49','dd-wood':'574335','dd-vinyl':'422a2b','dd-bottle':'355344','dd-amber':'84613d','dd-glass':'526f70','dd-screen':'508a87','dd-paper0':'b9b2a0','dd-paper1':'8a8880','dd-paper2':'b6a89d','dd-bulb0':'edb66c','dd-bulb1':'6592d4','dd-bulb2':'b65c69'})

def finishes():
 n=512;y,x=np.mgrid[:n,:n];rng=np.random.default_rng(234)
 for key in ['dd-block','dd-floor','dd-shingle','dd-poster','dd-ceiling','dd-wood']:
  m=E.materials.get(key)
  if not m:continue
  rgba=np.ones((n,n,4),np.float32);noise=rng.random((n,n))-.5
  c=np.array([int(E.colors[key][i:i+2],16)/255 for i in [0,2,4]])
  if key=='dd-block':
   grout=(((x+(y//64%2)*64)%128)<3)|((y%64)<3);s=np.where(grout,.7,1)+noise*.06
  elif key=='dd-shingle':s=.8+.18*np.sin((x//64+(y//40)*3)*7.1)+noise*.09;s[(y%40)<3]=.45
  elif key in ['dd-poster','dd-ceiling']:
   # A repeatable original paper-collage atlas, all marks generated here.
   s=np.ones((n,n));rgba[:,:,:3]=c
   for j in range(140):
    xx=int(rng.integers(0,490));yy=int(rng.integers(0,490));w=int(rng.integers(18,80));h=int(rng.integers(14,65));col=np.array([.65,.60,.49])*rng.uniform(.55,1.2) if j%5 else np.array([.40,.24,.20])
    rgba[yy:yy+h,xx:xx+w,:3]=col
    for r in range(4,h-3,6):rgba[yy+r:yy+r+2,xx+3:xx+w-3,:3]=col*.38
   rgba[:,:,:3]*=(1+noise*.09)[:,:,None]
  elif key=='dd-wood':s=.92+np.sin(x*.23+np.sin(y*.018))* .06+noise*.04
  else:s=.85+noise*.09;s[(x%128<2)|(y%128<2)]=.55
  if key not in ['dd-poster','dd-ceiling']:rgba[:,:,:3]=s[:,:,None]*c
  im=bpy.data.images.new('Original saloon '+key,width=n,height=n);im.pixels.foreach_set(rgba.flatten());im.pack()
  bs=m.node_tree.nodes.get('Principled BSDF');t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=im;m.node_tree.links.new(t.outputs['Color'],bs.inputs['Base Color']);bs.inputs['Roughness'].default_value=.86
 for key,m in E.materials.items():
  bs=m.node_tree.nodes.get('Principled BSDF')
  if key.startswith('dd-bulb') or key=='dd-screen':bs.inputs['Emission Color'].default_value=bs.inputs['Base Color'].default_value;bs.inputs['Emission Strength'].default_value=1.5
 for obj in bpy.context.scene.objects:
  if obj.type!='MESH':continue
  uv=obj.data.uv_layers.new(name='Metre finish')
  for p in obj.data.polygons:
   axis=max(range(3),key=lambda i:abs(p.normal[i]))
   for li in p.loop_indices:
    q=obj.data.vertices[obj.data.loops[li].vertex_index].co;uv.data[li].uv=(q.y,q.z) if axis==0 else (q.x,q.z) if axis==1 else(q.x,q.y)
  for v in uv.data:v.uv*=.5

for part in ['exterior','interior']:
 bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('doubleDown-'+part);finishes()
 bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/('doubleDown-'+part+'.blend')).resolve()))
 bpy.ops.export_scene.gltf(filepath=str((E.OUT/('doubleDown-'+part+'.glb')).resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
 print('EXPORTED doubleDown-'+part)
