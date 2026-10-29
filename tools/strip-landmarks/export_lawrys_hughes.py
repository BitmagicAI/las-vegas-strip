import bpy,sys,numpy as np
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
E.colors.update({'lh-stucco':'d2c5a8','lh-roof':'aeaaa0','lh-red':'95504b','lh-cream':'dfd6ba','lh-teal':'36746d','lh-seam':'466d68','lh-metal':'b6b9b3','lh-glass':'344e4b','lh-rib':'b4aa8e','lh-canopy':'b2b88b','lh-frame':'4c5551','lh-gold':'b8a366','lh-pot':'a66549','lh-wood':'67513a','lh-leaf':'426443','lh-equipment':'92958c'})
E.colors.update({'lh-cloth':'d3cbbb','lh-panel':'795039','lh-darkwood':'3b2d24','lh-carpet':'603136','lh-plank':'72513b','lh-ceiling':'ae9975','lh-redseat':'6f2930','lh-tealseat':'2f5354','lh-blueseat':'819ca4','lh-stone':'b0a18a','lh-lamp':'c1b088','lh-mirror':'6f7c77','lh-bottle':'425844','lh-art':'9d896a','lh-clear-glass':'839d96','lh-concrete':'9e988a'})
for part in ['exterior','interior']:
 bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('lawrys-hughes-'+part)
 for key,m in E.materials.items():
  bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.8
  if key in ['lh-metal','lh-teal','lh-frame']:bs.inputs['Metallic'].default_value=.55;bs.inputs['Roughness'].default_value=.38
  if key=='lh-glass':bs.inputs['Roughness'].default_value=.24;bs.inputs['Metallic'].default_value=.3
  if key in ['lh-canopy','lh-clear-glass']:
   bs.inputs['Roughness'].default_value=.35;bs.inputs['Alpha'].default_value=.68 if key=='lh-canopy' else .22;m.surface_render_method='BLENDED'
  if key=='lh-lamp':bs.inputs['Emission Color'].default_value=(1,.8,.5,1);bs.inputs['Emission Strength'].default_value=.18
  if key not in ['lh-stucco','lh-red','lh-roof','lh-pot','lh-panel','lh-plank','lh-carpet','lh-art']:continue
  n=256;rng=np.random.default_rng(348);noise=rng.random((n,n))-.5;rgba=np.ones((n,n,4),np.float32)
  rgb=np.array([int(E.colors[key][i:i+2],16)/255 for i in [0,2,4]])
  yy,xx=np.mgrid[0:n,0:n];shade=1+noise*.07
  if key in ['lh-panel','lh-plank']:
   shade=1+.012*np.sin(xx*1.73+.8*np.sin(yy*.035))+noise*.035
   if key=='lh-plank':shade*=np.where(xx%43<1,.65,1)
  if key=='lh-carpet':
   dx=(xx+32*(yy//64%2))%64-32;dy=yy%64-32
   angle=np.arctan2(dy,dx);radius=np.hypot(dx,dy)
   shade=.9+.18*(np.cos(angle*17+radius*.05)>.88)*(radius<29)+noise*.06
  for c in range(3):rgba[:,:,c]=np.clip(rgb[c]*shade,0,1)
  if key=='lh-art':
   # Original geometric composition, never a copy of a tour photograph.
   rgba[:,:,:3]=[.55,.43,.28]
   rgba[25:230,30:75,:3]=[.27,.38,.37];rgba[60:200,100:225,:3]=[.52,.24,.23]
   circle=(xx-140)**2+(yy-100)**2<42**2;rgba[circle,:3]=[.76,.65,.40]

  im=bpy.data.images.new('Original Lawrys '+key,width=n,height=n);im.pixels.foreach_set(rgba.flatten());im.pack();tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im;m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
 for obj in bpy.context.scene.objects:
  if obj.type!='MESH':continue
  obj.data.validate(verbose=True)
  if obj.name in ['lh-redseat','lh-tealseat','lh-blueseat']:
   bevel=obj.modifiers.new('Soft upholstery edges','BEVEL');bevel.width=.035;bevel.segments=3
   bpy.context.view_layer.objects.active=obj;bpy.ops.object.modifier_apply(modifier=bevel.name)
  uv=obj.data.uv_layers.new(name='Metre finishes')
  for poly in obj.data.polygons:
   axis=max(range(3),key=lambda i:abs(poly.normal[i]))
   for li in poly.loop_indices:
    p=obj.data.vertices[obj.data.loops[li].vertex_index].co;uv.data[li].uv=(p.y/2,p.z/2) if axis==0 else (p.x/2,p.z/2) if axis==1 else (p.x/2,p.y/2)
 bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/('lawrys-hughes-'+part+'.blend')).resolve()))
 bpy.ops.export_scene.gltf(filepath=str((E.OUT/('lawrys-hughes-'+part+'.glb')).resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
