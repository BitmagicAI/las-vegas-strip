"""Original procedural finishes; no third-party photographs embedded."""
import bpy,sys,math
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
E.colors.update({'h2-white-stucco': 'dadbd4', 'h2-ochre-paint': 'a17b4e', 'h2-charcoal-paint': '555653', 'h2-gray-paint': '676966', 'h2-lime-paint': 'a7bd4e', 'h2-aqua-paint': 'a7c7c5', 'h2-roof': 'b9bbb4', 'h2-roof-metal': '7d9293', 'h2-frame-paint': 'c3d0cb', 'h2-metal': '707b7c', 'h2-panel-joint': '777972', 'h2-glass': '4f888c', 'h2-transom-glass': '314c50', 'h2-sill-paint': 'c3c8bc', 'h2-letter': 'f1eee4', 'h2-stone': 'aaa9a2', 'h2-paving': 'aaa99e', 'h2-floor': 'aca69a', 'h2-interior': 'd3cec2', 'h2-ceiling': 'e0ded5', 'h2-counter': 'd6d4c8', 'h2-screen': '20292d', 'h2-wood': 'aa8c60', 'h2-seat-fabric': '79756a', 'h2-green-fabric': '7e924e', 'h2-yellow-fabric': 'b5a14a', 'h2-blue-fabric': '527e87', 'h2-gold': 'b29b58', 'h2-soffit': 'bbb39e', 'h2-vent': '535a57'})
E.colors.update({'h2-patio-table':'969d9a','h2-brushed-alloy':'b6bdbb','h2-red-canvas':'9e3033','h2-chair-wood':'bda270','h2-pool-tile':'466e87','h2_pool':'529baf','h2-grout':'a8bfc2','h2-lift-blue':'4773a4','h2-soil':'484035','h2-leaf':'6d8249'})
for part in ([sys.argv[sys.argv.index('--part')+1]] if '--part' in sys.argv else ['exterior','interior']):
 bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('home2-stadium-'+part)
 rng=np.random.default_rng(278);n=512;yy,xx=np.mgrid[:n,:n]
 for key,m in E.materials.items():
  bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.86;m.use_backface_culling=False
  if key in ['h2-metal','h2-roof-metal','h2-brushed-alloy']:bs.inputs['Metallic'].default_value=.5;bs.inputs['Roughness'].default_value=.44
  if key=='h2-brushed-alloy':bs.inputs['Metallic'].default_value=.85;bs.inputs['Roughness'].default_value=.32
  if key=='h2-glass':bs.inputs['Metallic'].default_value=.03;bs.inputs['Roughness'].default_value=.36
  if key not in ['h2-wood','h2-floor','h2-stone','h2-seat-fabric','h2-patio-table']:continue
  c=np.array([int(E.colors[key][i:i+2],16)/255 for i in [0,2,4]])
  fy=np.fft.fftfreq(n)[:,None];fx=np.fft.fftfreq(n)[None,:]
  field=np.fft.ifft2(np.fft.fft2(rng.normal(size=(n,n)))*np.exp(-((fx/.12)**2+(fy/.008)**2))).real;field/=max(field.std(),.001)
  shade=1+field*(.014 if part=='interior' else .035);height=field*.008
  if key=='h2-floor':
   for i in range(8):shade[:,i*64:i*64+64]*=rng.uniform(.95,1.04);shade[:,i*64:i*64+1]*=.85
  if key=='h2-stone':
   shade=np.ones((n,n));height=np.zeros((n,n))
   for row,y in enumerate(range(0,n,20)):
    for x in range(-64 if row%2 else 0,n,128):
     lo=max(0,x+1);hi=min(n,x+126);shade[y+1:y+19,lo:hi]=rng.uniform(.83,1.12);height[y+1:y+19,lo:hi]=.55
  if key=='h2-stone' and part=='exterior':
   # Original stacked-stone relief: varying lengths, recessed joints and fractured faces.
   shade=np.full((n,n),.73);height=np.zeros((n,n))
   for row,y in enumerate(range(0,n,20)):
    x=-int(rng.integers(12,90))
    while x<n:
     width=int(rng.integers(34,108));lo=max(0,x+1);hi=min(n,x+width-1)
     if hi>lo:
      h=min(18,n-y-1);sy,sx=np.mgrid[:h,:hi-lo]
      grain=rng.normal(0,.028,(h,hi-lo));fracture=.045*np.sin(sx*.19+sy*.37+rng.random()*6)
      shade[y+1:y+1+h,lo:hi]=rng.uniform(.82,1.12)+grain+fracture
      edge=np.minimum(np.minimum(sx+1,hi-lo-sx),np.minimum(sy+1,h-sy))
      height[y+1:y+1+h,lo:hi]=np.minimum(edge/3,1)*(rng.uniform(.15,.40)+fracture)
     x+=width
  if key=='h2-patio-table':
   shade=1+field*.025; height=field*.002
  if key=='h2-seat-fabric':shade=1+((xx%4<2)*.035+(yy%4<2)*.035);height=shade*.1
  rgba=np.ones((n,n,4),np.float32);rgba[:,:,:3]=np.clip(c[None,None,:]*(shade+rng.normal(0,.01,(n,n)))[:,:,None],0,1)
  im=bpy.data.images.new('Original '+key,width=n,height=n);im.pixels.foreach_set(rgba.flatten());im.pack();t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=im;m.node_tree.links.new(t.outputs['Color'],bs.inputs['Base Color'])
  dy,dx=np.gradient(height);normal=np.dstack((-dx*2,-dy*2,np.ones_like(height)));normal/=np.linalg.norm(normal,axis=2)[:,:,None];rgba[:,:,:3]=normal*.5+.5
  im=bpy.data.images.new('Original normal '+key,width=n,height=n);im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(rgba.flatten());im.pack();t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=im;node=m.node_tree.nodes.new('ShaderNodeNormalMap');m.node_tree.links.new(t.outputs['Color'],node.inputs['Color']);m.node_tree.links.new(node.outputs['Normal'],bs.inputs['Normal'])
 for o in bpy.context.scene.objects:
  if o.type=='FONT':o.data.font=bpy.data.fonts.load('/System/Library/Fonts/Supplemental/Arial.ttf',check_existing=True)
  if o.type!='MESH':continue
  if o.get('surface') in ['h2-green-fabric','h2-seat-fabric','h2-chair-wood'] or (part=='exterior' and o.get('surface')=='h2-yellow-fabric'):
   bpy.context.view_layer.objects.active=o;b=o.modifiers.new('Soft seat edges','BEVEL');b.width=.025;b.segments=3;b.limit_method='ANGLE';bpy.ops.object.modifier_apply(modifier=b.name)
  uv=o.data.uv_layers.new(name='Metre finish')
  for p in o.data.polygons:
   axis=max(range(3),key=lambda i:abs(p.normal[i]))
   axes=[i for i in range(3) if i!=axis]
   bounds=[(min(o.data.vertices[o.data.loops[j].vertex_index].co[k] for j in p.loop_indices),max(o.data.vertices[o.data.loops[j].vertex_index].co[k] for j in p.loop_indices)) for k in axes]
   for li in p.loop_indices:
    q=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(q.y*.5,q.z*.5) if axis==0 else (q.x*.5,q.z*.5) if axis==1 else (q.x*.5,q.y*.5)
    if o.get('surface')=='h2-glass':uv.data[li].uv=tuple((q[k]-lo)/max(.0001,hi-lo) for k,(lo,hi) in zip(axes,bounds))
    if part=='interior' and o.get('surface')=='h2-wood':u,v=uv.data[li].uv;uv.data[li].uv=(v,u)
 bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/('home2-stadium-'+part+'.blend')).resolve()))
 bpy.ops.export_scene.gltf(filepath=str((E.OUT/('home2-stadium-'+part+'.glb')).resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
 print('EXPORTED home2-stadium-'+part)
