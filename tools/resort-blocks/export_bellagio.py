"""Export Bellagio plus re-use the previously authored bronze arrival canopy."""
import sys,runpy,json,hashlib,math,argparse
from pathlib import Path
parser=argparse.ArgumentParser()
parser.add_argument('--only',help='Export one exact layer, e.g. bellagioBlock-exterior; preserve all other GLBs')
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
ns=runpy.run_path('tools/strip-landmarks/export.py',run_name='resort_materials');out=Path('build/resort-blocks/bellagio');ns['add'].__globals__['OUT']=out;bpy=ns['bpy']
sys.path.insert(0,'tools/level');import bellagio_arrival as arrival
import numpy as np
ns['colors'].update({'tree-shadow':'304731','tree-leaf':'4f693a','tree-tip':'829458','lake-cream':'eee2c7','lake-ochre':'e3cea1','lake-stone':'eee4cf',
 'lake-roof':'c0afa0','lake-terracotta':'c88a6d','lake-tile-light':'d99d7a',
 'lake-bronze':'465353','lake-glazing':'426770','lake-gold':'c7b36d',
 'lake-rock':'b4ad96','lake-water':'258c99','lake-deep':'174b51',
 'lake-underwater':'30747d','lake-earth':'60624c','lake-leaf':'52663c','lake-paving':'d1b9a2'})
sys.path.insert(0,'tools/resort-blocks');import bellagio_palette
ns['colors'].update(bellagio_palette.COLORS)
ns['colors'].update({'bellagio-flat-roof':'b1a48c','bel-service-trim':'beb5a4','bel-service-joint':'928c7e','bel-service-vent':'555f5e'})
ns['patterns'].update(['lake-cream','lake-ochre','lake-stone','lake-roof',
 'lake-terracotta','lake-tile-light','lake-rock','lake-water','lake-paving'])
original_material=ns['material']
def lake_material(k):
 cached=k in ns['materials'];m=original_material(k)
 if not cached and k.startswith('bel-'):bellagio_palette.finish(k,m.node_tree.nodes.get('Principled BSDF'))
 if cached or not k.startswith('lake-'):return m
 bs=m.node_tree.nodes.get('Principled BSDF')
 if k in ['lake-water','lake-glazing']:
  bs.inputs['Roughness'].default_value=.23 if k=='lake-water' else .16
  bs.inputs['Metallic'].default_value=.2
 if k in ['lake-bronze','lake-gold']:bs.inputs['Metallic'].default_value=.55;bs.inputs['Roughness'].default_value=.35
 if k=='lake-water':
  # Original periodic ripples, baked as a glTF normal map; no aerial image texture.
  n=512;v,u=np.mgrid[0:n,0:n]/n
  wave=.055*np.sin(math.tau*(u*9+v*13))+.03*np.sin(math.tau*(u*23-v*7))+.015*np.cos(math.tau*(u*31+v*27))
  pixels=np.ones((n,n,4),dtype=np.float32);pixels[:,:,:3]=np.array([.145,.55,.60])+wave[:,:,None]*.09
  im=bpy.data.images.new('Original lake ripple color',width=n,height=n);im.pixels.foreach_set(pixels.flatten());im.pack()
  tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im;m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
  dy,dx=np.gradient(wave);normal=np.stack([-dx*1.2,-dy*1.2,np.ones_like(dx)],axis=-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True);pixels[:,:,:3]=normal*.5+.5
  ni=bpy.data.images.new('Original lake ripple normal',width=n,height=n);ni.colorspace_settings.name='Non-Color';ni.pixels.foreach_set(pixels.flatten());ni.pack()
  nt=m.node_tree.nodes.new('ShaderNodeTexImage');nt.image=ni;nn=m.node_tree.nodes.new('ShaderNodeNormalMap');nn.inputs['Strength'].default_value=.45;m.node_tree.links.new(nt.outputs['Color'],nn.inputs['Color']);m.node_tree.links.new(nn.outputs['Normal'],bs.inputs['Normal'])
 return m
ns['add'].__globals__['material']=lake_material

for venue in json.loads((out/'venues.json').read_text()):
 for layer in ['exterior','interior']:
  name=venue['key']+'-'+layer
  if args.only and name!=args.only:continue
  bpy.ops.wm.read_factory_settings(use_empty=True);ns['materials'].clear();ns['add'](name)
  for o in bpy.context.scene.objects:
   if name=='bellagioBlock-exterior' and o.type=='MESH' and o.get('surface') in ['roof','lake-roof']:
    o.data.materials.clear();o.data.materials.append(lake_material('bellagio-flat-roof'));o['surface']='bellagio-flat-roof'
   if o.type=='MESH' and str(o.get('source','')).startswith('arrival-tree/'):
    for polygon in o.data.polygons:polygon.use_smooth=True
   if o.type=='MESH' and o.get('source')=='lakefront-shore-gardens' and o.get('surface') in ['lake-leaf','foliage','sage','bark']:
    for polygon in o.data.polygons:polygon.use_smooth=True
   if o.type=='MESH' and o.get('surface')=='lake-water' and o.data.uv_layers.active:
    for loop in o.data.uv_layers.active.data:loop.uv/=6
  if name=='bellagioBlock-exterior':
   arrival.materials();a=arrival.Builder('Mapped main arrival',(-235,.24,445),(1.3,1,.9),-math.pi/2);
   drive=json.loads((out/'south-arrival-report.json').read_text())['roads']
   def column_clear(p):
    for r in drive:
     for u,v in zip(r['points'],r['points'][1:]):
      dx,dz=v[0]-u[0],v[2]-u[2];t=max(0,min(1,((p[0]-u[0])*dx+(p[2]-u[2])*dz)/max(.001,dx*dx+dz*dz)))
      if math.hypot(p[0]-u[0]-t*dx,p[2]-u[2]-t*dz)<r['width']/2+.9:return False
    return True
   arrival.canopy(a,True,column_filter=column_clear);result=a.finish()
   for o in bpy.context.scene.objects:
    if o.get('bellagioArrival'):o['source']='arrival-canopy';o['detail']=1;o['property']='bellagioBlock'
   # The cached authoring collision remains immutable across repeated exports.
   c=json.loads((out/(name+'-collision.json')).read_text())
   for v in result['colliders']:
    x,y,z=v['position'];w,h,d=[n/2 for n in v['size']];co,si=math.cos(v['yaw']),math.sin(v['yaw']);offset=len(c['vertices'])//3
    for xx,yy,zz in [(-w,-h,-d),(w,-h,-d),(w,h,-d),(-w,h,-d),(-w,-h,d),(w,-h,d),(w,h,d),(-w,h,d)]:c['vertices'].extend([x+xx*co+zz*si,y+yy,z-xx*si+zz*co])
    for face in [(0,3,2,1),(4,5,6,7),(0,4,7,3),(1,2,6,5),(3,7,6,2),(0,1,5,4)]:c['indices'].extend(offset+i for i in [face[0],face[1],face[2],face[0],face[2],face[3]])
   (out/(name+'-runtime-collision.json')).write_text(json.dumps(c,separators=(',',':')))
  bpy.ops.wm.save_as_mainfile(filepath=str((out/(name+'.blend')).resolve()))
  bpy.ops.export_scene.gltf(filepath=str((out/(name+'.glb')).resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
h=hashlib.sha256()
for p in sorted(out.glob('*.glb')):h.update(p.read_bytes())
h.update((out/'venues.json').read_bytes());h.update((out/'bellagioBlock-exterior-runtime-collision.json').read_bytes());(out/'version.json').write_text(json.dumps({'revision':h.hexdigest()[:16]}))
