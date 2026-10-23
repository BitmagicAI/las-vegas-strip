"""Export chapel with existing CC0 Poly Haven tree asset, shared mesh data."""
import sys,math,json,hashlib,struct
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
import bpy
from mathutils import Matrix,Vector
name='rexfordEllenCourtyard-exterior';bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add(name)
for mat in bpy.data.materials:
 if mat.name=='Strip / cf-grass':
  bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=1;bs.inputs['Specular IOR Level'].default_value=0
for lod in range(3):
 if lod!=1:
  before=set(bpy.data.objects)
  asset='tree-2.glb'
  bpy.ops.import_scene.gltf(filepath=str((Path('public/foliage')/asset).resolve()))
  added=set(bpy.data.objects)-before;bpy.context.view_layer.update();proto=[(o.data,o.matrix_world.copy()) for o in added if o.type=='MESH']
  coords=[m@v.co for data,m in proto for v in data.vertices];lo=min(v.z for v in coords);hi=max(v.z for v in coords);print('TREE_HEIGHT',lod,hi-lo)
  for data,m in proto:
   for mat in data.materials:
    if mat:mat['sourceLicense']='CC0 Poly Haven tree_small_02 (existing project asset)'
  for o in added:bpy.data.objects.remove(o,do_unlink=True)
 for i,(x,z,h,yaw) in enumerate([(2085,-3852,4.5,.4),(2083.5,-3837,4.8,1.9),(2082,-3804,4.2,2.8)]):
  s=h/(hi-lo);T=Matrix.Translation((x,-z,.08))@Matrix.Rotation(yaw,4,'Z')@Matrix.Scale(s,4)@Matrix.Translation((0,0,-lo))
  for j,(data,m) in enumerate(proto):
   o=bpy.data.objects.new(f'Rexford street tree {i}/{lod}/{j}',data);bpy.context.collection.objects.link(o);o.matrix_world=T@m;o['property']='rexfordEllenCourtyard';o['source']=f'arrival-tree/{math.floor(x/40)},{math.floor(z/40)}/{lod}';o['detail']=0
bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/(name+'.blend')).resolve()))
p=E.OUT/(name+'.glb');bpy.ops.export_scene.gltf(filepath=str(p.resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
# Leaf silhouettes are cutouts, not layers of blended transparency.
b=p.read_bytes();jn=struct.unpack_from('<I',b,12)[0];d=json.loads(b[20:20+jn]);rest=b[20+jn:]
for mat in d.get('materials',[]):
 if 'leaves' in mat.get('name','').lower():mat['alphaMode']='MASK';mat['alphaCutoff']=.12;mat['doubleSided']=True
j=json.dumps(d,separators=(',',':')).encode();j+=b' '*((-len(j))%4);p.write_bytes(struct.pack('<III',0x46546c67,2,20+len(j)+len(rest))+struct.pack('<II',len(j),0x4e4f534a)+j+rest)
h=hashlib.sha256()
for f in sorted(E.OUT.glob('*.glb')):h.update(f.read_bytes())
for f in sorted(E.OUT.glob('*-collision.json')):h.update(f.read_bytes())
h.update((E.OUT/'venues.json').read_bytes());(E.OUT/'version.json').write_text(json.dumps({'revision':h.hexdigest()[:16]}));print('EXPORTED',name)
