import bpy,sys,numpy as np
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
E.colors.update({'fg-stucco': 'deded4', 'fg-membrane': 'a7aaa5', 'fg-trim': 'aeb6b1', 'fg-dark': '454743', 'fg-vein': 'd8d8d1', 'fg-paving': '96988f', 'fg-letter': '282d29', 'fg-glass': '425450', 'fg-bronze': 'a99561', 'fg-equipment': '9caaa5', 'fg-panel': '9a9889', 'fg-carpet': '817c6e', 'fg-ceiling': 'c3c0aa', 'fg-wood': '9e815a', 'fg-marble': 'd5d1bc', 'fg-mirror': 'a0ada6', 'fg-bottle': '4d5d35', 'fg-seat': '4a5144', 'fg-art': '8b8074', 'fg-lamp': 'e4cf9b', 'fg-clear': 'c9ded9', 'fg-steel': '8c9390', 'fg-food': '73814c', 'fg-cloth': 'dedbca'})
for part in ['exterior','interior']:
 bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('fogo-hughes-'+part)
 for key,m in E.materials.items():
  bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.8
  if key in ['fg-bronze']:bs.inputs['Metallic'].default_value=.55;bs.inputs['Roughness'].default_value=.38
  if key in ['fg-membrane','fg-vein']:
   for link in list(bs.inputs['Normal'].links):m.node_tree.links.remove(link)
  if key=='fg-glass':bs.inputs['Roughness'].default_value=.24;bs.inputs['Metallic'].default_value=.3
  if key in ['fg-canopy','fg-clear']:
   bs.inputs['Roughness'].default_value=.35;bs.inputs['Alpha'].default_value=.68 if key=='fg-canopy' else .22;m.surface_render_method='BLENDED'
  if key=='fg-lamp':bs.inputs['Emission Color'].default_value=(1,.8,.5,1);bs.inputs['Emission Strength'].default_value=.18
  if key not in ['fg-stucco','fg-membrane','fg-panel','fg-carpet','fg-tile','fg-marble','fg-vein','fg-art']:continue
  n=256;rng=np.random.default_rng(348);noise=rng.random((n,n))-.5;rgba=np.ones((n,n,4),np.float32)
  rgb=np.array([int(E.colors[key][i:i+2],16)/255 for i in [0,2,4]])
  yy,xx=np.mgrid[0:n,0:n];shade=1+noise*.07
  if key in ['fg-panel','fg-carpet']:
   shade=1+.012*np.sin(xx*1.73+.8*np.sin(yy*.035))+noise*.035
   if key=='fg-carpet':shade=1+noise*.12+.018*np.sin(xx*.19)*np.sin(yy*.21)
  if key=='fg-vein':
   shade=1+noise*.035-.14*np.exp(-((xx-yy*.65-20*np.sin(yy*.023))%103-51)**2/5)
  if key=='fg-tile':
   shade*=np.where(yy%32<2,.62,1)
   shade*=np.where((xx+16*(yy//32%2))%64<2,.82,1)
  if key=='fg-marble':
   dx=(xx+32*(yy//64%2))%64-32;dy=yy%64-32
   angle=np.arctan2(dy,dx);radius=np.hypot(dx,dy)
   shade=.9+.18*(np.cos(angle*17+radius*.05)>.88)*(radius<29)+noise*.06
  for c in range(3):rgba[:,:,c]=np.clip(rgb[c]*shade,0,1)
  if key=='fg-art':
   # Original geometric composition, never a copy of a tour photograph.
   rgba[:,:,:3]=[.55,.43,.28]
   rgba[25:230,30:75,:3]=[.27,.38,.37];rgba[60:200,100:225,:3]=[.52,.24,.23]
   circle=(xx-140)**2+(yy-100)**2<42**2;rgba[circle,:3]=[.76,.65,.40]

  im=bpy.data.images.new('Original Fogo '+key,width=n,height=n);im.pixels.foreach_set(rgba.flatten());im.pack();tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im;m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
 for obj in bpy.context.scene.objects:
  if obj.type!='MESH':continue
  obj.data.validate(verbose=True)
  if obj.name in ['fg-seat']:
   bevel=obj.modifiers.new('Soft upholstery edges','BEVEL');bevel.width=.035;bevel.segments=3
   bpy.context.view_layer.objects.active=obj;bpy.ops.object.modifier_apply(modifier=bevel.name)
  uv=obj.data.uv_layers.new(name='Metre finishes')
  for poly in obj.data.polygons:
   axis=max(range(3),key=lambda i:abs(poly.normal[i]))
   for li in poly.loop_indices:
    p=obj.data.vertices[obj.data.loops[li].vertex_index].co;uv.data[li].uv=(p.y/2,p.z/2) if axis==0 else (p.x/2,p.z/2) if axis==1 else (p.x/2,p.y/2)
 bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/('fogo-hughes-'+part+'.blend')).resolve()))
 bpy.ops.export_scene.gltf(filepath=str((E.OUT/('fogo-hughes-'+part+'.glb')).resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
