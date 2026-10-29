"""Original small repeat textile maps, not copied reference-image pixels."""
import bpy,numpy as np,math
def meeting_finishes():
 n=512;yy,xx=np.mgrid[0:n,0:n];rng=np.random.default_rng(338)
 noise=rng.random((n,n))-.5
 for key in ['mg-carpet','mg-table-cloth','mg-seat']:
  m=bpy.data.materials.get('Strip / '+key)
  if m is None:continue
  bs=m.node_tree.nodes.get('Principled BSDF');rgba=np.ones((n,n,4),np.float32)
  if key=='mg-carpet':
   # Restrained gold looping motif over a dense brown woven ground; approximate.
   u=xx/n*math.tau;v=yy/n*math.tau
   loops=np.minimum(abs(np.sin(u+1.1*np.sin(v))),abs(np.sin(v+1.1*np.sin(u))))
   motif=np.clip((.07-loops)*9,0,.5)
   for c,base in enumerate([.31,.255,.17]):rgba[:,:,c]=base+motif*[.16,.13,.065][c]+noise*.045
  else:
   weave=np.sin(xx*math.pi/2)*np.cos(yy*math.pi/2)*.012+noise*.02
   for c,base in enumerate([.31,.37,.25] if key=='mg-table-cloth' else [.14,.135,.115]):rgba[:,:,c]=base+weave
  im=bpy.data.images.new('Original Mardi Gras '+key,width=n,height=n);im.pixels.foreach_set(rgba.flatten());im.pack()
  tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im;m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color']);bs.inputs['Roughness'].default_value=.94
 for obj in bpy.context.scene.objects:
  if obj.type!='MESH' or obj.data.materials[0].name not in ['Strip / mg-carpet','Strip / mg-table-cloth','Strip / mg-seat']:continue
  uv=obj.data.uv_layers.new(name='Textile metres')
  for poly in obj.data.polygons:
   axis=max(range(3),key=lambda i:abs(poly.normal[i]))
   for li in poly.loop_indices:
    p=obj.data.vertices[obj.data.loops[li].vertex_index].co
    uv.data[li].uv=(p.y,p.z) if axis==0 else (p.x,p.z) if axis==1 else (p.x,p.y)

  if obj.data.materials[0].name=='Strip / mg-carpet':
   for item in uv.data:item.uv*=4
