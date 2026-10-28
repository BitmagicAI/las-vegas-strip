import bpy,sys,numpy as np
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
E.colors.update({'mf-paving': 'a69d8a', 'mf-stucco': 'c4bba7', 'mf-roof': '99968c', 'mf-trim': 'd5cbb6', 'mf-stone': '635e53', 'mf-wood': '735339', 'mf-black': '242526', 'mf-glass': '3e4b49', 'mf-leaf': '3f5738', 'mf-equipment': '999c95', 'mf-panel': '3c3430', 'mf-plank': '514338', 'mf-ceiling': 'a09986', 'mf-carpet': '665e4e', 'mf-bottle': '3d4d39', 'mf-metal': '848784', 'mf-seat': '433d38', 'mf-cloth': 'd1cbbb', 'mf-lamp': 'c5b38e', 'mf-mirror': '77817a'})
for part in ['exterior','interior']:
 bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('mortons-flamingo-'+part)
 for key,m in E.materials.items():
  bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.8
  if key in ['mf-metal','mf-teal','mf-frame']:bs.inputs['Metallic'].default_value=.55;bs.inputs['Roughness'].default_value=.38
  if key=='mf-roof':
   for link in list(bs.inputs['Normal'].links):m.node_tree.links.remove(link)
  if key=='mf-glass':bs.inputs['Roughness'].default_value=.24;bs.inputs['Metallic'].default_value=.3
  if key in ['mf-canopy','mf-clear-glass']:
   bs.inputs['Roughness'].default_value=.35;bs.inputs['Alpha'].default_value=.68 if key=='mf-canopy' else .22;m.surface_render_method='BLENDED'
  if key=='mf-lamp':bs.inputs['Emission Color'].default_value=(1,.8,.5,1);bs.inputs['Emission Strength'].default_value=.18
  if key not in ['mf-stucco','mf-roof','mf-panel','mf-plank','mf-carpet']:continue
  n=256;rng=np.random.default_rng(348);noise=rng.random((n,n))-.5;rgba=np.ones((n,n,4),np.float32)
  rgb=np.array([int(E.colors[key][i:i+2],16)/255 for i in [0,2,4]])
  yy,xx=np.mgrid[0:n,0:n];shade=1+noise*.07
  if key in ['mf-panel','mf-plank']:
   shade=1+.012*np.sin(xx*1.73+.8*np.sin(yy*.035))+noise*.035
   if key=='mf-plank':shade*=np.where(xx%43<1,.65,1)
  if key=='mf-carpet':
   dx=(xx+32*(yy//64%2))%64-32;dy=yy%64-32
   angle=np.arctan2(dy,dx);radius=np.hypot(dx,dy)
   shade=.9+.18*(np.cos(angle*17+radius*.05)>.88)*(radius<29)+noise*.06
  for c in range(3):rgba[:,:,c]=np.clip(rgb[c]*shade,0,1)
  if key=='mf-art':
   # Original geometric composition, never a copy of a tour photograph.
   rgba[:,:,:3]=[.55,.43,.28]
   rgba[25:230,30:75,:3]=[.27,.38,.37];rgba[60:200,100:225,:3]=[.52,.24,.23]
   circle=(xx-140)**2+(yy-100)**2<42**2;rgba[circle,:3]=[.76,.65,.40]

  im=bpy.data.images.new('Original Mortons '+key,width=n,height=n);im.pixels.foreach_set(rgba.flatten());im.pack();tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im;m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
 for obj in bpy.context.scene.objects:
  if obj.type!='MESH':continue
  obj.data.validate(verbose=True)
  if obj.name in ['mf-seat']:
   bevel=obj.modifiers.new('Soft upholstery edges','BEVEL');bevel.width=.035;bevel.segments=3
   bpy.context.view_layer.objects.active=obj;bpy.ops.object.modifier_apply(modifier=bevel.name)
  uv=obj.data.uv_layers.new(name='Metre finishes')
  for poly in obj.data.polygons:
   axis=max(range(3),key=lambda i:abs(poly.normal[i]))
   for li in poly.loop_indices:
    p=obj.data.vertices[obj.data.loops[li].vertex_index].co;uv.data[li].uv=(p.y/2,p.z/2) if axis==0 else (p.x/2,p.z/2) if axis==1 else (p.x/2,p.y/2)
 bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/('mortons-flamingo-'+part+'.blend')).resolve()))
 bpy.ops.export_scene.gltf(filepath=str((E.OUT/('mortons-flamingo-'+part+'.glb')).resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
