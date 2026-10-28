import bpy,sys,numpy as np
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
E.colors.update({'ff-siding': '657062', 'ff-membrane': 'a7aaa5', 'ff-trim': '56614f', 'ff-stone': '9b9681', 'ff-tile': '99958b', 'ff-paving': 'b5afa0', 'ff-letter': 'e5dcae', 'ff-glass': '415653', 'ff-cream': 'd2cfb9', 'ff-black': '272c28', 'ff-table': '59715d', 'ff-seat': '657d65', 'ff-equipment': 'a2aaa5', 'ff-panel': '73816d', 'ff-plank': '817966', 'ff-brass': 'a7925d', 'ff-marble': '354e40', 'ff-mirror': '909d8a', 'ff-bottle': '465b33', 'ff-tan': '9c7852', 'ff-pink': 'c79e9b', 'ff-art': '928d74', 'ff-lamp': 'e4cf9b'})
for part in ['exterior','interior']:
 bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('firefly-hughes-'+part)
 for key,m in E.materials.items():
  bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.8
  if key in ['ff-brass']:bs.inputs['Metallic'].default_value=.55;bs.inputs['Roughness'].default_value=.38
  if key in ['ff-membrane','ff-stone']:
   for link in list(bs.inputs['Normal'].links):m.node_tree.links.remove(link)
  if key=='ff-glass':bs.inputs['Roughness'].default_value=.24;bs.inputs['Metallic'].default_value=.3
  if key in ['ff-canopy','ff-clear-glass']:
   bs.inputs['Roughness'].default_value=.35;bs.inputs['Alpha'].default_value=.68 if key=='ff-canopy' else .22;m.surface_render_method='BLENDED'
  if key=='ff-lamp':bs.inputs['Emission Color'].default_value=(1,.8,.5,1);bs.inputs['Emission Strength'].default_value=.18
  if key not in ['ff-siding','ff-membrane','ff-panel','ff-plank','ff-tile','ff-marble','ff-stone']:continue
  n=256;rng=np.random.default_rng(348);noise=rng.random((n,n))-.5;rgba=np.ones((n,n,4),np.float32)
  rgb=np.array([int(E.colors[key][i:i+2],16)/255 for i in [0,2,4]])
  yy,xx=np.mgrid[0:n,0:n];shade=1+noise*.07
  if key in ['ff-panel','ff-plank']:
   shade=1+.012*np.sin(xx*1.73+.8*np.sin(yy*.035))+noise*.035
   if key=='ff-plank':shade*=np.where(xx%43<1,.65,1)
  if key=='ff-stone':
   shade*=np.where(yy%32<3,.58,1)
   shade*=np.where((xx+32*(yy//32%2))%85<2,.66,1)
  if key=='ff-tile':
   shade*=np.where(yy%32<2,.62,1)
   shade*=np.where((xx+16*(yy//32%2))%64<2,.82,1)
  if key=='ff-marble':
   dx=(xx+32*(yy//64%2))%64-32;dy=yy%64-32
   angle=np.arctan2(dy,dx);radius=np.hypot(dx,dy)
   shade=.9+.18*(np.cos(angle*17+radius*.05)>.88)*(radius<29)+noise*.06
  for c in range(3):rgba[:,:,c]=np.clip(rgb[c]*shade,0,1)
  if key=='ff-art':
   # Original geometric composition, never a copy of a tour photograph.
   rgba[:,:,:3]=[.55,.43,.28]
   rgba[25:230,30:75,:3]=[.27,.38,.37];rgba[60:200,100:225,:3]=[.52,.24,.23]
   circle=(xx-140)**2+(yy-100)**2<42**2;rgba[circle,:3]=[.76,.65,.40]

  im=bpy.data.images.new('Original Firefly '+key,width=n,height=n);im.pixels.foreach_set(rgba.flatten());im.pack();tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im;m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
 for obj in bpy.context.scene.objects:
  if obj.type!='MESH':continue
  obj.data.validate(verbose=True)
  if obj.name in ['ff-seat']:
   bevel=obj.modifiers.new('Soft upholstery edges','BEVEL');bevel.width=.035;bevel.segments=3
   bpy.context.view_layer.objects.active=obj;bpy.ops.object.modifier_apply(modifier=bevel.name)
  uv=obj.data.uv_layers.new(name='Metre finishes')
  for poly in obj.data.polygons:
   axis=max(range(3),key=lambda i:abs(poly.normal[i]))
   for li in poly.loop_indices:
    p=obj.data.vertices[obj.data.loops[li].vertex_index].co;uv.data[li].uv=(p.y/2,p.z/2) if axis==0 else (p.x/2,p.z/2) if axis==1 else (p.x/2,p.y/2)
 bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/('firefly-hughes-'+part+'.blend')).resolve()))
 bpy.ops.export_scene.gltf(filepath=str((E.OUT/('firefly-hughes-'+part+'.glb')).resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
