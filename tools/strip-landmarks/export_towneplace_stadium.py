"""Original procedural finishes; no third-party photographs embedded."""
import bpy,sys,math
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
E.colors.update({'ts-chair-frame-paint':'35332e','ts-white-stucco':'d4d2c8','ts-ochre-paint':'907039','ts-charcoal-paint':'444240','ts-wood':'9a7954','ts-roof':'999991','ts-roof-metal':'464f58','ts-frame-paint':'c7c9bd','ts-metal':'424b50','ts-panel-seam':'4c4b47','ts-glass':'465452','ts-sill-paint':'bbbdb3','ts-letter':'efeee1','ts-stone':'aaa491','ts-paving':'aaa596','ts-floor':'b29a79','ts-interior':'d4cbb6','ts-ceiling':'dedbd0','ts-counter':'d5d1c4','ts-red-paint':'a7472c','ts-screen':'1b2226','ts-market-paint':'6e8146','ts-blue':'366b7a','ts-seat':'454037','ts-red-fabric':'9b4c3d'})
for part in ([sys.argv[sys.argv.index('--part')+1]] if '--part' in sys.argv else ['exterior','interior']):
 bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('towneplace-stadium-'+part)
 rng=np.random.default_rng(278);n=512;yy,xx=np.mgrid[:n,:n]
 for key,m in E.materials.items():
  bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.86;m.use_backface_culling=False
  if key in ['ts-metal','ts-roof-metal']:bs.inputs['Metallic'].default_value=.5;bs.inputs['Roughness'].default_value=.44
  if key=='ts-glass':bs.inputs['Metallic'].default_value=.03;bs.inputs['Roughness'].default_value=.36
  if key=='ts-glass':
   # Original curtain impression behind reflective glazing, not a copied photograph.
   u=xx/(n-1);v=yy/(n-1)
   folds=.74+.11*np.cos(u*math.tau*19)+.04*np.cos(u*math.tau*41)
   curtain=(u>.07)&(u<.93)&(v>.08)&(v<.94)
   shade=folds*(.80+.20*v)
   rgba=np.ones((n,n,4),np.float32)
   rgba[:,:,:3]=np.array([.15,.20,.22])[None,None,:]
   fabric=shade[:,:,None]*np.array([.48,.49,.46])[None,None,:]
   rgba[:,:,:3]=np.where(curtain[:,:,None],fabric,rgba[:,:,:3])
   # Dark gap where the two curtains meet, with a narrow blue glazing tint.
   rgba[:,n//2-4:n//2+4,:3]*=.48
   im=bpy.data.images.new('Original glazed curtain folds',width=n,height=n);im.pixels.foreach_set(rgba.flatten());im.pack()
   t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=im;m.node_tree.links.new(t.outputs['Color'],bs.inputs['Base Color'])
  if key not in ['ts-wood','ts-floor','ts-stone','ts-red-fabric']:continue
  c=np.array([int(E.colors[key][i:i+2],16)/255 for i in [0,2,4]])
  fy=np.fft.fftfreq(n)[:,None];fx=np.fft.fftfreq(n)[None,:]
  field=np.fft.ifft2(np.fft.fft2(rng.normal(size=(n,n)))*np.exp(-((fx/.12)**2+(fy/.008)**2))).real;field/=max(field.std(),.001)
  shade=1+field*(.014 if part=='interior' else .035);height=field*.008
  if key=='ts-floor':
   for i in range(8):shade[:,i*64:i*64+64]*=rng.uniform(.95,1.04);shade[:,i*64:i*64+1]*=.85
  if key=='ts-stone':
   shade=np.ones((n,n));height=np.zeros((n,n))
   for row,y in enumerate(range(0,n,20)):
    for x in range(-64 if row%2 else 0,n,128):
     lo=max(0,x+1);hi=min(n,x+126);shade[y+1:y+19,lo:hi]=rng.uniform(.83,1.12);height[y+1:y+19,lo:hi]=.55
  if key=='ts-red-fabric':shade=1+((xx%4<2)*.035+(yy%4<2)*.035);height=shade*.1
  rgba=np.ones((n,n,4),np.float32);rgba[:,:,:3]=np.clip(c[None,None,:]*(shade+rng.normal(0,.01,(n,n)))[:,:,None],0,1)
  im=bpy.data.images.new('Original '+key,width=n,height=n);im.pixels.foreach_set(rgba.flatten());im.pack();t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=im;m.node_tree.links.new(t.outputs['Color'],bs.inputs['Base Color'])
  dy,dx=np.gradient(height);normal=np.dstack((-dx*2,-dy*2,np.ones_like(height)));normal/=np.linalg.norm(normal,axis=2)[:,:,None];rgba[:,:,:3]=normal*.5+.5
  im=bpy.data.images.new('Original normal '+key,width=n,height=n);im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(rgba.flatten());im.pack();t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=im;node=m.node_tree.nodes.new('ShaderNodeNormalMap');m.node_tree.links.new(t.outputs['Color'],node.inputs['Color']);m.node_tree.links.new(node.outputs['Normal'],bs.inputs['Normal'])
 for o in bpy.context.scene.objects:
  if o.type=='FONT':o.data.font=bpy.data.fonts.load('/System/Library/Fonts/Supplemental/Arial.ttf',check_existing=True)
  if o.type!='MESH':continue
  if o.get('surface') in ['ts-seat','ts-red-fabric']:
   bpy.context.view_layer.objects.active=o;b=o.modifiers.new('Soft seat edges','BEVEL');b.width=.025;b.segments=3;b.limit_method='ANGLE';bpy.ops.object.modifier_apply(modifier=b.name)
  uv=o.data.uv_layers.new(name='Metre finish')
  for p in o.data.polygons:
   axis=max(range(3),key=lambda i:abs(p.normal[i]))
   axes=[i for i in range(3) if i!=axis]
   bounds=[(min(o.data.vertices[o.data.loops[j].vertex_index].co[k] for j in p.loop_indices),max(o.data.vertices[o.data.loops[j].vertex_index].co[k] for j in p.loop_indices)) for k in axes]
   for li in p.loop_indices:
    q=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(q.y*.5,q.z*.5) if axis==0 else (q.x*.5,q.z*.5) if axis==1 else (q.x*.5,q.y*.5)
    if o.get('surface')=='ts-glass':uv.data[li].uv=tuple((q[k]-lo)/max(.0001,hi-lo) for k,(lo,hi) in zip(axes,bounds))
    if part=='interior' and o.get('surface')=='ts-wood':u,v=uv.data[li].uv;uv.data[li].uv=(v,u)
 bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/('towneplace-stadium-'+part+'.blend')).resolve()))
 bpy.ops.export_scene.gltf(filepath=str((E.OUT/('towneplace-stadium-'+part+'.glb')).resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
 print('EXPORTED towneplace-stadium-'+part)
