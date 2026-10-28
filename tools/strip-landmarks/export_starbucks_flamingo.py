import bpy,sys,numpy as np
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
E.colors.update({'sb-stucco': 'ccc9c0', 'sb-fascia': '5a5e5a', 'sb-stone': '464c48', 'sb-membrane': 'aaa8a1', 'sb-clear': 'b7ccc8', 'sb-metal': 'b1b6b0', 'sb-letter': 'eee5ca', 'sb-black': '202721', 'sb-green': '176744', 'sb-paving': 'b4b2a5', 'sb-equipment': 'a0aaa4', 'sb-wall': 'c6bca4', 'sb-floor': '9b998f', 'sb-ceiling': '767d76', 'sb-wood': 'b08c57', 'sb-tile': 'd4ddd7', 'sb-paper': 'e2dbc6', 'sb-ink': '655e4d', 'sb-steel': '999f9a', 'sb-bread': 'b8904b', 'sb-lamp': 'eee1b4'})
for part in ['exterior','interior']:
 bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('starbucks-flamingo-'+part)
 for key,m in E.materials.items():
  bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.8
  if key in ['sb-bronze']:bs.inputs['Metallic'].default_value=.55;bs.inputs['Roughness'].default_value=.38
  if key in ['sb-membrane','sb-vein']:
   for link in list(bs.inputs['Normal'].links):m.node_tree.links.remove(link)
  if key=='sb-glass':bs.inputs['Roughness'].default_value=.24;bs.inputs['Metallic'].default_value=.3
  if key in ['sb-canopy','sb-clear']:
   bs.inputs['Roughness'].default_value=.35;bs.inputs['Alpha'].default_value=.68 if key=='sb-canopy' else .22;m.surface_render_method='BLENDED'
  if key=='sb-lamp':bs.inputs['Emission Color'].default_value=(1,.8,.5,1);bs.inputs['Emission Strength'].default_value=.18
  if key not in ['sb-wood','sb-floor','sb-stone','sb-tile']:continue
  n=256;rng=np.random.default_rng(348);noise=rng.random((n,n))-.5;rgba=np.ones((n,n,4),np.float32)
  rgb=np.array([int(E.colors[key][i:i+2],16)/255 for i in [0,2,4]])
  yy,xx=np.mgrid[0:n,0:n];shade=1+noise*.07
  if key in ['sb-wood']:
   shade=1+.012*np.sin(xx*1.73+.8*np.sin(yy*.035))+noise*.035
   if key=='sb-carpet':shade=1+noise*.12+.018*np.sin(xx*.19)*np.sin(yy*.21)
  if key=='sb-vein':
   shade=1+noise*.035-.14*np.exp(-((xx-yy*.65-20*np.sin(yy*.023))%103-51)**2/5)
  if key=='sb-tile':
   shade*=np.where(yy%64<1,.7,1)
   shade*=np.where(xx%16<1,.7,1)
  if key=='sb-marble':
   dx=(xx+32*(yy//64%2))%64-32;dy=yy%64-32
   angle=np.arctan2(dy,dx);radius=np.hypot(dx,dy)
   shade=.9+.18*(np.cos(angle*17+radius*.05)>.88)*(radius<29)+noise*.06
  for c in range(3):rgba[:,:,c]=np.clip(rgb[c]*shade,0,1)
  if key=='sb-art':
   # Original geometric composition, never a copy of a tour photograph.
   rgba[:,:,:3]=[.55,.43,.28]
   rgba[25:230,30:75,:3]=[.27,.38,.37];rgba[60:200,100:225,:3]=[.52,.24,.23]
   circle=(xx-140)**2+(yy-100)**2<42**2;rgba[circle,:3]=[.76,.65,.40]

  im=bpy.data.images.new('Original Starbucks '+key,width=n,height=n);im.pixels.foreach_set(rgba.flatten());im.pack();tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im;m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
 for obj in bpy.context.scene.objects:
  if obj.type!='MESH':continue
  obj.data.validate(verbose=True)
  if obj.name in ['sb-seat']:
   bevel=obj.modifiers.new('Soft upholstery edges','BEVEL');bevel.width=.035;bevel.segments=3
   bpy.context.view_layer.objects.active=obj;bpy.ops.object.modifier_apply(modifier=bevel.name)
  uv=obj.data.uv_layers.new(name='Metre finishes')
  for poly in obj.data.polygons:
   axis=max(range(3),key=lambda i:abs(poly.normal[i]))
   for li in poly.loop_indices:
    p=obj.data.vertices[obj.data.loops[li].vertex_index].co;uv.data[li].uv=(p.y/2,p.z/2) if axis==0 else (p.x/2,p.z/2) if axis==1 else (p.x/2,p.y/2)
 bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/('starbucks-flamingo-'+part+'.blend')).resolve()))
 bpy.ops.export_scene.gltf(filepath=str((E.OUT/('starbucks-flamingo-'+part+'.glb')).resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
import hashlib
h=hashlib.sha256()
for f in sorted(E.OUT.glob('*.glb')):h.update(f.read_bytes())
for f in sorted(E.OUT.glob('*-collision.json')):h.update(f.read_bytes())
h.update((E.OUT/'venues.json').read_bytes())
(E.OUT/'version.json').write_text(__import__('json').dumps({'revision':h.hexdigest()[:16]}))
