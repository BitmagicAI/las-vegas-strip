"""Original motel materials, metre-scaled UVs, local optimized export."""
import bpy,sys
import numpy as np
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
E.colors.update({'m6-grout':'958e7d','m6-dark-tile':'777064','m6-mat':'303a3b','m6-light-trim':'e4e0c6','m6-white-stucco':'d2d0c5','m6-membrane-paint':'a8aaa4','m6-shingle':'74796c','m6-white-paint':'d7ddd6','m6-frame-paint':'d7ddd6','m6-blue-paint':'3162a1','m6-metal-paint':'8e9692','m6-number':'cecab6','m6-glass':'263c3e','m6-ac':'b8b9ae','m6-vent':'535b59','m6-deck-concrete':'a1a298','m6-letter':'f1f0e9','m6-lobby-tile':'c4bca9','m6-interior':'d4cfc1','m6-ceiling':'d8d6ca','m6-coffee-wood':'494541','m6-counter':'b8b3a6','m6-screen':'252b2d','m6-chair':'414b49','m6-appliance':'d8d9d2','m6-control':'747d7c','m6-vending':'34465a','stone':'b4b7ad','steel':'cbd3cd'})
E.colors.update({'m6-pool-tile':'61969e','m6_pool':'4c8e9c'})
E.colors.update({'m6-planter-stone':'9d8e78','m6-stone-joint':'625c50','m6-gravel':'b1a08a','m6-gravel-rock':'a79985','c525-bark':'80705a','c525-collision':'80705a','c525-palm-stem':'706a38','c525-palm-leaf':'4c6335','c525-palm-light':'6d783c'})
for part in ['exterior','interior']:
 bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('motel6-stadium-'+part)
 for key,m in E.materials.items():
  m.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.86
  if key in ['m6-metal-paint']:m.node_tree.nodes.get('Principled BSDF').inputs['Metallic'].default_value=.5
 # Original small-scale shingle colour variation; no reference photograph used.
 if 'm6-shingle' in E.materials:
  m=E.materials['m6-shingle'];bs=m.node_tree.nodes.get('Principled BSDF');rng=np.random.default_rng(284);n=256
  data=np.ones((n,n,4),np.float32);base=np.array([.455,.475,.424]);shade=np.ones((n,n),np.float32)
  for row,yy in enumerate(range(0,n,32)):
   for xx in range(-32 if row%2 else 0,n,64):
    lo=max(0,xx);hi=min(n,xx+64);shade[yy:yy+32,lo:hi]=rng.uniform(.90,1.06);shade[yy:yy+2,lo:hi]*=.65;shade[yy:yy+32,lo:lo+1]*=.8
  shade+=rng.normal(0,.018,(n,n));data[:,:,:3]=np.clip(shade[:,:,None]*base,0,1)
  im=bpy.data.images.new('Original motel shingle courses',width=n,height=n);im.pixels.foreach_set(data.ravel());im.pack()
  node=m.node_tree.nodes.new('ShaderNodeTexImage');node.image=im;m.node_tree.links.new(node.outputs['Color'],bs.inputs['Base Color'])
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  uv=o.data.uv_layers.new(name='Metre finish')
  for p in o.data.polygons:
   axis=max(range(3),key=lambda i:abs(p.normal[i]));axes=[i for i in range(3) if i!=axis]
   for li in p.loop_indices:
    q=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(q[axes[0]],q[axes[1]])
 bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/('motel6-stadium-'+part+'.blend')).resolve()))
 bpy.ops.export_scene.gltf(filepath=str((E.OUT/('motel6-stadium-'+part+'.glb')).resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
 print('EXPORTED motel6-stadium-'+part)
