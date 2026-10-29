"""Original tileable wood grain, plaster and ornamental wallpaper; no photo pixels."""
import bpy,numpy as np

def finishes():
 n=512;y,x=np.mgrid[:n,:n];rng=np.random.default_rng(318);noise=rng.random((n,n))-.5
 for m in bpy.data.materials:
  key=m.name.removeprefix('Strip / ')
  if not key.startswith('hr-'):continue
  bs=m.node_tree.nodes.get('Principled BSDF');base=tuple(12.92*v if v<=.0031308 else 1.055*v**(1/2.4)-.055 for v in bs.inputs['Base Color'].default_value[:3]);shade=np.ones((n,n))
  if key=='hr-wallpaper':
   # Repeating symmetric leaves and diamonds, drawn mathematically rather than copied.
   u=(x%128-64)/64;v=(y%128-64)/64
   leaf=np.abs(u)<(.15+.23*np.sin((v+1)*np.pi)**2)*(1-np.abs(v))
   diamond=np.abs(np.abs(u)+np.abs(v)-.82)<.035
   shade=.78+.34*(leaf|diamond)+noise*.035
  elif key.startswith('hr-plank') or key in ['hr-wood','hr-darkwood']:
   shade=.94+.025*np.sin(y*.11+np.sin(x*.018)*2)+.03*np.sin(y*.53+np.sin(x*.04))+noise*.04
  elif key=='hr-stucco':continue
  else:continue
  rgba=np.ones((n,n,4),np.float32)
  for c,value in enumerate(base):rgba[:,:,c]=np.clip(value*shade,0,1)
  im=bpy.data.images.new('Original Herbs Rye '+key,width=n,height=n);im.pixels.foreach_set(rgba.ravel());im.pack()
  tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im;m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
