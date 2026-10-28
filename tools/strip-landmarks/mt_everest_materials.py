"""Original repeatable finish maps; reference images are never embedded."""
import bpy,numpy as np

def finishes():
 n=512;y,x=np.mgrid[:n,:n];rng=np.random.default_rng(306);noise=rng.random((n,n))-.5
 for key,color in [('me-carpet',(.18,.14,.11)),('me-wood',(.28,.12,.08)),('me-vinyl',(.30,.055,.07)),('me-stucco',(.72,.64,.48))]:
  m=bpy.data.materials.get('Strip / '+key)
  if m is None:continue
  if key=='me-carpet':shade=.9+.08*np.sin(x*.8)*np.sin(y*.8)+.05*np.sin(x*.055+y*.055)+noise*.12
  elif key=='me-wood':shade=.9+.025*np.sin(x*.17+np.sin(y*.025)*2)+noise*.06
  else:shade=.96+noise*.07
  rgba=np.ones((n,n,4),np.float32)
  for c,v in enumerate(color):rgba[:,:,c]=np.clip(v*shade,0,1)
  im=bpy.data.images.new('Original Mt Everest '+key,width=n,height=n);im.pixels.foreach_set(rgba.flatten());im.pack()
  tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im;bs=m.node_tree.nodes.get('Principled BSDF');m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
