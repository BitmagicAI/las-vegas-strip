"""Redistributable original stone/stucco maps; research photographs are not textures."""
import bpy,sys,math
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
E.colors.update({'ht-stucco':'c6bfa8','ht-cream':'e3dcc6','ht-brick':'745645','ht-roof':'9b9990','ht-stucco-rose':'a2765f','ht-green':'3d584c','ht-recess':'272e2c','ht-glass':'536a72','ht-spandrel':'464f4b','ht-metal':'55534a','ht-sill':'d6ccad','ht-joint':'9e9786','ht-red':'b83439','ht-paving':'b7b3a6','ht-stone':'b8ab90','ht-floor':'aaa599','ht-interior':'d7d3c4','ht-ceiling':'d8d4c8','ht-wood':'755038','ht-carpet':'7b6855','ht-upholstery':'a8a69c','ht-blue':'3c505b','ht-screen':'202b2d','ht-magenta':'733449','ht-mustard':'a89a48','ht-light':'e8debc','hampton_pool':'296e79','ht-pool-tile':'8ab3af'})
E.colors.update({'ht-rock':'9f927a','ht-soil':'514839','ht-shrub':'405436','ht-shrub-light':'5c713e','c525-bark':'766650','c525-collision':'766650','c525-palm-stem':'63734c','c525-palm-leaf':'3e6139','c525-palm-light':'587845'})
for part in ['exterior','interior']:
 bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('hampton-tropicana-'+part)
 rng=np.random.default_rng(256);size=512
 for key,m in E.materials.items():
  bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.86
  if key in ['ht-metal','ht-chrome','ht-frame']:bs.inputs['Metallic'].default_value=.55;bs.inputs['Roughness'].default_value=.42
  if key=='ht-glass':bs.inputs['Roughness'].default_value=.22;bs.inputs['Metallic'].default_value=.05;bs.inputs['Alpha'].default_value=1.0;m.surface_render_method='DITHERED'
  m.use_backface_culling=False
  if key=='ht-light':bs.inputs['Emission Color'].default_value=(.95,.92,.8,1);bs.inputs['Emission Strength'].default_value=.35
  if key not in ['ht-stone','ht-brick','ht-wood','ht-floor','ht-carpet','ht-upholstery','ht-rock','c525-bark','ht-soil']:continue
  c=np.array([int(E.colors[key][i:i+2],16)/255 for i in [0,2,4]])
  h=np.full((size,size),.2);shade=np.ones((size,size))
  if key in ['ht-stone','ht-brick']:
   rowheight=16 if key=='ht-stone' else 20
   brickwidth=70 if key=='ht-stone' else 62
   shade[:]=.65;h[:]=.12
   for row,y in enumerate(range(0,size,rowheight)):
    x=-(brickwidth//2 if row%2 else 0)
    while x<size:
     w=int(rng.integers(40,110)) if key=='ht-stone' else brickwidth
     lo=max(x+1,0);hi=min(x+w-1,size)
     h[y+1:min(y+rowheight-1,size),lo:hi]=rng.uniform(.65,.85)
     shade[y+1:min(y+rowheight-1,size),lo:hi]=rng.uniform(.87,1.08);x+=w
  if key in ['ht-wood','ht-floor']:
   yy,xx=np.mgrid[0:size,0:size]
   # Periodic anisotropic noise gives wood fibres without a regular sine-wave stripe.
   fy=np.fft.fftfreq(size)[:,None];fx=np.fft.fftfreq(size)[None,:]
   field=np.fft.ifft2(np.fft.fft2(rng.normal(size=(size,size)))*np.exp(-((fx/.13)**2+(fy/.008)**2))).real
   field/=max(field.std(),.001)
   shade=1+np.clip(field,-2.5,2.5)*.022
   if key=='ht-floor':
    # Eight long boards per two-metre tile, with staggered joints and restrained tones.
    for row in range(8):
     lo=row*64;hi=lo+64;shade[:,lo:hi]*=rng.uniform(.97,1.03)
     shade[:,lo:lo+1]*=.88
     z=int(rng.integers(0,size));shade[z:z+1,lo:hi]*=.88
   h=(shade-1)*.025
  if key in ['ht-rock','c525-bark','ht-soil']:
   yy,xx=np.mgrid[0:size,0:size];field=np.zeros((size,size))
   fy=np.fft.fftfreq(size)[:,None];fx=np.fft.fftfreq(size)[None,:]
   for frequency,weight in [(.012,.6),(.045,.25),(.15,.15)]:
    spectrum=np.exp(-((fx/frequency)**2+(fy/(frequency*(.18 if key=='c525-bark' else 1)))**2))
    octave=np.fft.ifft2(np.fft.fft2(rng.normal(size=(size,size)))*spectrum).real
    field+=octave/max(octave.std(),.001)*weight
   shade=1+np.clip(field,-2,2)*(.13 if key=='c525-bark' else .065)
   h=field*(.22 if key=='c525-bark' else .12)
   if key=='ht-rock':
    # Restrained sediment seams; no regular brick joints on natural stone.
    seams=np.maximum(0,np.cos(yy*math.tau/64+field*.8)-.90)
    shade-=seams*.3;h-=seams*.25
  if key in ['ht-carpet','ht-upholstery']:
   yy,xx=np.mgrid[0:size,0:size]
   weave=((xx%4)<2)*.035+((yy%4)<2)*.035
   shade=.94+weave+(rng.random((size,size))-.5)*.1
   if key=='ht-upholstery':shade*=.91+.09*np.sin((xx+yy*.32)*.25)**2
   h=weave*.2
  h+=rng.random((size,size))*.025
  noise=(rng.random((size,size))-.5)*(.012 if key in ['ht-wood','ht-floor'] else .035)
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
  if o.get('surface')=='c525-collision':
   bpy.data.objects.remove(o,do_unlink=True);continue
  if o.get('surface')=='ht-rock':
   bpy.context.view_layer.objects.active=o
   bevel=o.modifiers.new('Broken sandstone edges','BEVEL');bevel.width=.18;bevel.segments=2;bevel.limit_method='ANGLE'
   bpy.ops.object.modifier_apply(modifier=bevel.name)
   # Broad broken stone planes with small irregularity; seeded by position for reproducibility.
   for v in o.data.vertices:
    q=v.co;v.co.x+=.075*math.sin(q.y*7.1+q.z*4.7);v.co.y+=.065*math.sin(q.x*5.3-q.z*6.1);v.co.z+=.065*math.sin(q.x*6.7+q.y*3.9)
   o.data.update()
  # Only soft seating gets rounded edges; architecture and collision remain untouched.
  if o.get('surface') in ['ht-upholstery','ht-mustard']:
   bpy.context.view_layer.objects.active=o
   bevel=o.modifiers.new('Cushion edge radius','BEVEL');bevel.width=.045;bevel.segments=4;bevel.limit_method='ANGLE'
   bpy.ops.object.modifier_apply(modifier=bevel.name)
   for polygon in o.data.polygons:polygon.use_smooth=True
   normal=o.modifiers.new('Weighted cushion normals','WEIGHTED_NORMAL');normal.keep_sharp=True
   bpy.ops.object.modifier_apply(modifier=normal.name)
  uv=o.data.uv_layers.new(name='Metre finish')
  for p in o.data.polygons:
   axis=max(range(3),key=lambda i:abs(p.normal[i]))
   for li in p.loop_indices:
    q=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(q.y*.5,q.z*.5) if axis==0 else (q.x*.5,q.z*.5) if axis==1 else(q.x*.5,q.y*.5)
 bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/('hampton-tropicana-'+part+'.blend')).resolve()))
 bpy.ops.export_scene.gltf(filepath=str((E.OUT/('hampton-tropicana-'+part+'.glb')).resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
 print('EXPORTED hampton-tropicana-'+part)
