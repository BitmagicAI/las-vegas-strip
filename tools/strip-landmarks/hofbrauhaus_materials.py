"""Original repeatable finish maps; no third-party reference pixels."""
import bpy, numpy as np, math

def finishes():
 n=512;yy,xx=np.mgrid[0:n,0:n];rng=np.random.default_rng(232)
 noise=rng.random((n,n))-.5
 for name in ['hb-floor','hb-oak','hb-darkwood']:
  mat=bpy.data.materials.get('Strip / '+name)
  if mat is None:continue
  bs=mat.node_tree.nodes.get('Principled BSDF');base=np.ones((n,n,4),np.float32)
  if name=='hb-floor':
   row=yy//64;u=(xx+(row%2)*64)%128;v=yy%64
   grout=(u<3)|(v<3);tile=.83+.15*np.sin((xx//128+row*7)*3.7)
   shade=np.where(grout,.55,tile)+noise*.045
   color=[.42,.31,.23]
  else:
   wave=np.sin(xx*.11+np.sin(yy*.015)*2+np.sin(xx*.025))
   shade=.9+wave*.055+noise*.04
   color=[.54,.33,.15] if name=='hb-oak' else [.24,.17,.105]
  for c,value in enumerate(color):base[:,:,c]=np.clip(value*shade,0,1)
  im=bpy.data.images.new('Original Hofbrauhaus '+name,width=n,height=n);im.pixels.foreach_set(base.flatten());im.pack()
  tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im;mat.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color']);bs.inputs['Roughness'].default_value=.84
 for obj in bpy.context.scene.objects:
  if obj.type!='MESH':continue
  material=obj.data.materials[0].name
  if material not in ['Strip / hb-floor','Strip / hb-oak','Strip / hb-darkwood']:continue
  uv=obj.data.uv_layers.new(name='Metre finish')
  for poly in obj.data.polygons:
   axis=max(range(3),key=lambda i:abs(poly.normal[i]))
   for li in poly.loop_indices:
    p=obj.data.vertices[obj.data.loops[li].vertex_index].co
    uv.data[li].uv=(p.y,p.z) if axis==0 else (p.x,p.z) if axis==1 else (p.x,p.y)
  if material=='Strip / hb-floor':
   for item in uv.data:item.uv*=.5
 for obj in bpy.context.scene.objects:
  if obj.type=='MESH' and obj.data.materials[0].name=='Strip / hb-vault':
   for poly in obj.data.polygons:poly.use_smooth=True

def trees(interior=False):
 from mathutils import Matrix
 yaw=1.7868214428245313;co=math.cos(yaw);si=math.sin(yaw)
 sites=[(u,v,5.2) for u in [5,13,23] for v in [3,21]] if interior else [(u,-1.1,3.4) for u in [3,11,33,48,57]]
 for lod in ([1] if interior else [0,1,2]):
  before=set(bpy.data.objects)
  # The existing tree-1 reduction collapses most leaf/trunk area; use the intact source.
  bpy.ops.import_scene.gltf(filepath=str(__import__('pathlib').Path('public/foliage/tree-2.glb' if lod==2 else 'public/foliage/tree-0.glb').resolve()))
  added=set(bpy.data.objects)-before;bpy.context.view_layer.update();proto=[(o.data,o.matrix_world.copy()) for o in added if o.type=='MESH']
  coords=[m@v.co for d,m in proto for v in d.vertices];lo=min(v.z for v in coords);hi=max(v.z for v in coords)
  for o in added:bpy.data.objects.remove(o,do_unlink=True)
  for i,(u,v,h) in enumerate(sites):
   x=1922.741+co*u+si*v;z=969.671-si*u+co*v
   T=Matrix.Translation((x,-z,.19))@Matrix.Rotation(i*2.4,4,'Z')@Matrix.Scale(h/(hi-lo),4)@Matrix.Translation((0,0,-lo))
   for j,(data,m) in enumerate(proto):
    o=bpy.data.objects.new(f'Hofbrauhaus tree {i}/{lod}/{j}',data);bpy.context.collection.objects.link(o);o.matrix_world=T@m
    o['property']='hofbrauhaus';o['source']='public/garden-tree' if interior else f'arrival-tree/{math.floor(x/40)},{math.floor(z/40)}/{lod}';o['detail']=0
    for mat in data.materials:
     if mat:mat['sourceLicense']='CC0 Poly Haven tree_small_02 (existing project asset)'
