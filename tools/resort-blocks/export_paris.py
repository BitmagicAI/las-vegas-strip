"""Export authored Paris surfaces; original material textures and baked spatial cells."""
import runpy,json,hashlib,math,sys
from pathlib import Path
import numpy as np
ns=runpy.run_path('tools/strip-landmarks/export.py',run_name='resort_materials');out=Path('build/resort-blocks/paris');ns['add'].__globals__['OUT']=out;bpy=ns['bpy']
ns['colors'].update({'paris-stone':'d5c6ad','paris-cream':'e7ddc9','paris-slate':'263d4d','paris-iron':'243e36','paris-leaf':'4e693c','paris-rattan':'bfa77e','paris-paving':'cdbda6','paris-red':'932a31','paris-yellow':'d7ab66','paris-copper':'608579','paris-canopy':'73988e','paris-gold':'c0a25c','paris-blue':'205585'})
ns['colors'].update({'paris-window':'526368','paris-canopy-frame':'a3b7b3','paris-asphalt':'646367','paris-opera-roof':'bd987d','paris-relief':'bfb09b','paris-joint':'ada18d','paris-display':'111923','paris-script':'c62238'})
ns['colors'].update({'paris-ashlar':'c8c4ba','paris-ivory':'e0d6c5','paris-rose':'cbbdaf','paris-shutter':'617b7c','paris-chimney':'976957'})
ns['colors'].update({'paris-eiffel':'918b83','paris-eiffel-edge':'a39e97','paris-eiffel-shadow':'554e48','paris-eiffel-glass':'283434','paris-pool-paving':'e4dbc9','paris-pool-band':'b7ab96','paris-pool-tile':'7bc4d5','paris-water':'259fc5','paris-pool-frame':'3d4240','paris-pool-cushion':'e4e3df','paris-pool-leaf':'526446','paris-pool-hedge':'344d32','paris-pool-soil':'645e4b'})
ns['patterns'].update(['paris-stone','paris-slate','paris-paving','paris-rattan','paris-water'])
ns['colors'].update({'paris-membrane-paint':'969b96','paris-service-metal':'848b88','paris-service-joint':'777d77'})
original=ns['material']
def material(k):
 cached=k in ns['materials'];m=original(k)
 if cached or not k.startswith('paris-'):return m
 bs=m.node_tree.nodes.get('Principled BSDF')
 if k in ['paris-copper','paris-gold','paris-iron']:bs.inputs['Metallic'].default_value=.45;bs.inputs['Roughness'].default_value=.38
 if k=='paris-canopy':bs.inputs['Metallic'].default_value=.05;bs.inputs['Roughness'].default_value=.35;bs.inputs['Alpha'].default_value=.54;m.surface_render_method='DITHERED'
 if k.startswith('paris-eiffel'):bs.inputs['Metallic'].default_value=.16;bs.inputs['Roughness'].default_value=.7
 if k=='paris-water':bs.inputs['Metallic'].default_value=.13;bs.inputs['Roughness'].default_value=.22
 if k=='paris-window':bs.inputs['Metallic'].default_value=.18;bs.inputs['Roughness'].default_value=.32
 if k=='paris-display':bs.inputs['Roughness'].default_value=.45
 if k in ['paris-stone','paris-slate','paris-paving','paris-rattan','paris-water']:
  n=512;v,u=np.mgrid[0:n,0:n]/n;rgb=np.array([int(ns['colors'][k][i:i+2],16)/255 for i in (0,2,4)]);noise=np.random.default_rng(17).random((n,n))-.5;variation=noise*.028
  if k=='paris-stone':variation-=((v%(.25)<.005)|((u+np.floor(v*4)*.5)%1<.006))*.055
  if k=='paris-slate':variation-=((v%(.125)<.008)|((u*4+np.floor(v*8)*.5)%1<.025))*.09
  if k=='paris-paving':variation-=((v%(.5)<.003)|(u%(.5)<.003))*.08
  if k=='paris-rattan':variation+=.05*np.sin(u*120)*np.sin(v*120)
  if k=='paris-water':
   wave=np.sin(u*51+np.cos(v*27)*1.6)*np.sin(v*61+np.cos(u*39)*1.5)
   variation+=np.maximum(0,wave-.4)*.075+np.sin(u*113+v*77)*.007
  pix=np.ones((n,n,4),dtype=np.float32);pix[:,:,:3]=np.clip(rgb+variation[:,:,None],0,1)
  im=bpy.data.images.new('Paris original '+k,width=n,height=n);im.pixels.foreach_set(pix.flatten());im.pack();tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im;m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
 return m
ns['add'].__globals__['material']=material
for v in json.loads((out/'venues.json').read_text()):
 for layer in ['exterior','interior']:
  name=v['key']+'-'+layer
  if '--only' in sys.argv and name!=sys.argv[sys.argv.index('--only')+1]:continue
  bpy.ops.wm.read_factory_settings(use_empty=True);ns['materials'].clear();ns['add'](name)
  for o in bpy.context.scene.objects:
   source=str(o.get('source',''));o['spatialCell']=source.rsplit('@',1)[-1] if '@' in source else f'{math.floor(o.location.x/64)}_{math.floor(-o.location.y/64)}'
   if o.type=='MESH' and o.get('surface') in ['paris-leaf','bark','paris-blue']:
    for p in o.data.polygons:p.use_smooth=True
  for o in list(bpy.context.scene.objects):
   if o.type=='FONT' and o.data.body=='Paris':
    o.data.font=bpy.data.fonts.load('/System/Library/Fonts/Supplemental/Apple Chancery.ttf');o.data.extrude=.055
    outline=o.copy();outline.data=o.data.copy();outline.data.offset=.11;outline.data.extrude=.025;outline.data.materials.clear();outline.data.materials.append(material('paris-cream'));bpy.context.collection.objects.link(outline)
    from mathutils import Vector
    o.location+=o.rotation_euler.to_matrix() @ Vector((0,0,.12))
  bpy.ops.wm.save_as_mainfile(filepath=str((out/(name+'.blend')).resolve()))
  bpy.ops.export_scene.gltf(filepath=str((out/(name+'.glb')).resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
h=hashlib.sha256()
for p in sorted(out.glob('*.glb')):h.update(p.read_bytes())
h.update((out/'venues.json').read_bytes());(out/'version.json').write_text(json.dumps({'revision':h.hexdigest()[:16]}))
