import bpy,sys,math,numpy as np
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
E.colors.update({'bf-stucco':'733d3c','bf-roof-paint':'8d918c','bf-coping':'6d5551','bf-plinth':'613e39','bf-stone':'c4af91','bf-floor':'75634f','bf-concrete':'afa99c','bf-cream':'d9d3b8','bf-green':'36573e','bf-glass':'2b4542','bf-door-paint':'323a34','bf-sign-red':'b6423c','bf-planter':'80715d','bf-leaf':'4a6140','bf-rust':'97583a','bf-wood':'503a25','bf-carpet':'56352f','bf-vault':'a98e60','bf-gold':'9f7e3c','bf-art':'95875c','bf-checkcloth':'d9c7a4','bf-menu':'93633e','bf-lamp':'bbb395','bf-back-glass':'2b4542','bf-upholstery':'62352f'})
for part in ['exterior','interior']:
 bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('buca-flamingo-'+part)
 for key,m in E.materials.items():
  bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.84
  if key=='bf-glass':
   bs.inputs['Roughness'].default_value=.2;bs.inputs['Alpha'].default_value=.24
   m.surface_render_method='BLENDED';m.use_backface_culling=True
  if key=='bf-lamp':bs.inputs['Emission Color'].default_value=(1,.8,.4,1);bs.inputs['Emission Strength'].default_value=.12
  if key not in ['bf-stucco','bf-stone','bf-wood','bf-carpet','bf-checkcloth','bf-art','bf-vault']:continue
  n=256;yy,xx=np.mgrid[0:n,0:n];rng=np.random.default_rng(346);noise=rng.random((n,n))-.5;rgba=np.ones((n,n,4),np.float32)
  rgb=np.array([int(E.colors[key][i:i+2],16)/255 for i in [0,2,4]])
  shade=1+noise*.08
  if key=='bf-stone':shade=np.where((yy%19<1)|((xx+(yy//19%2)*24)%48<1),.66,1)+noise*.05
  if key=='bf-wood':shade=1+.06*np.sin(xx*.3)+noise*.03
  if key=='bf-carpet':shade=.8+.2*np.sin(xx*.3)*np.cos(yy*.28)+noise*.08
  if key in ['bf-art','bf-vault']:shade=1+noise*.025
  for c in range(3):rgba[:,:,c]=np.clip(rgb[c]*shade,0,1)
  if key in ['bf-art','bf-vault']:
   # Original abstract prints on paper: varied quiet blocks, no borrowed imagery.
   palette=np.array([[.64,.56,.43],[.43,.36,.27],[.73,.67,.55],[.35,.40,.35],[.56,.36,.27]])
   rgba[:,:,:3]=[.68,.61,.49]
   for row in range(4):
    for col in range(5):
     x=col*51+3+int(rng.integers(0,5));y=row*64+3+int(rng.integers(0,5))
     w=int(rng.integers(32,43));h=int(rng.integers(43,54))
     rgba[y:y+h,x:x+w,:3]=[.81,.76,.65]
     rgba[y+4:y+h-4,x+4:x+w-4,:3]=palette[int(rng.integers(0,len(palette)))]
     rgba[y+h//2:y+h-6,x+7:x+w-7,:3]*=.82
     rgba[y+7:y+13,x+8:x+w-8,:3]*=1.12
  if key=='bf-checkcloth':
   checks=((xx//16+yy//16)%2)==0
   for c,v in enumerate([.58,.16,.13]):rgba[:,:,c]=np.where(checks,v,rgba[:,:,c])
  im=bpy.data.images.new('Original Buca '+key,width=n,height=n);im.pixels.foreach_set(rgba.flatten());im.pack();tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im;m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
 for obj in bpy.context.scene.objects:
  if obj.type!='MESH':continue
  obj.data.validate(verbose=True);uv=obj.data.uv_layers.new(name='Metre finishes')
  for poly in obj.data.polygons:
   axis=max(range(3),key=lambda i:abs(poly.normal[i]))
   for li in poly.loop_indices:
    p=obj.data.vertices[obj.data.loops[li].vertex_index].co;uv.data[li].uv=(p.y/2,p.z/2) if axis==0 else (p.x/2,p.z/2) if axis==1 else (p.x/2,p.y/2)
 bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/('buca-flamingo-'+part+'.blend')).resolve()))
 bpy.ops.export_scene.gltf(filepath=str((E.OUT/('buca-flamingo-'+part+'.glb')).resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
