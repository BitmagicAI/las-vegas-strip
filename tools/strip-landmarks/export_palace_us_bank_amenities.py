"""Original amenity meshes plus existing redistributable broadleaf foliage sources."""
import sys,json,struct
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
import bpy
from mathutils import Matrix
E.colors.update({'psa-paving':'d2c7b7','psa_pool':'4698b4','psa-tile':'78a2ac','psa-coping':'e3ded3','psa-white':'f0ece3','psa-dark':'343538','psa-navy':'27374b','psa-yellow':'d9bd45','uba-gravel':'b3a38b','uba-path':'d3d1c7','uba-paving':'b7a99b','uba-soil':'756a51','uba-stone':'b5a89c','uba-hedge':'465d34'})
for key in ['palaceStationAmenities','usBankAmenities']:
 bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add(key+'-exterior')
 if key=='usBankAmenities':
  before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(Path('tools/foliage/models/tree-1.glb').resolve()));added=set(bpy.data.objects)-before;bpy.context.view_layer.update();proto=[(o.data,o.matrix_world.copy()) for o in added if o.type=='MESH'];coords=[m@v.co for data,m in proto for v in data.vertices];lo=min(v.z for v in coords);hi=max(v.z for v in coords)
  # tree-1 is the solid-geometry LOD. Match foliage-trees.mjs's textureless
  # treatment: its inherited tree-0 alpha maps otherwise erase the canopy.
  for data,m in proto:
   for mat in data.materials:
    if not mat or not mat.use_nodes:continue
    for node in list(mat.node_tree.nodes):
     if node.type=='TEX_IMAGE':mat.node_tree.nodes.remove(node)
    for node in mat.node_tree.nodes:
     if node.type=='BSDF_PRINCIPLED':
      node.inputs['Base Color'].default_value=(.13,.22,.07,1) if 'leaves' in mat.name.lower() else (.18,.12,.065,1)
      node.inputs['Alpha'].default_value=1
      node.inputs['Roughness'].default_value=.9
  for o in added:bpy.data.objects.remove(o,do_unlink=True)
  placements=json.loads(Path('docs/project-records/palace-us-bank-amenities/us-bank-geometry.json').read_text())['treePlacements']
  for i,(x,z,h) in enumerate(placements):
   T=Matrix.Translation((x,-z,.74))@Matrix.Rotation(i*1.3,4,'Z')@Matrix.Scale(h/(hi-lo),4)@Matrix.Translation((0,0,-lo))
   for j,(data,m) in enumerate(proto):
    o=bpy.data.objects.new(f'US Bank garden tree {i}/{j}',data);bpy.context.collection.objects.link(o);o.matrix_world=T@m;o['property']=key;o['source']='us-bank-amenities';o['detail']=0
 p=E.OUT/(key+'-exterior.glb');bpy.ops.export_scene.gltf(filepath=str(p.resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
 b=p.read_bytes();jn=struct.unpack_from('<I',b,12)[0];d=json.loads(b[20:20+jn]);rest=b[20+jn:]
 for mat in d.get('materials',[]):
  if 'leaves' in mat.get('name','').lower():mat['alphaMode']='OPAQUE';mat.pop('alphaCutoff',None);mat['doubleSided']=True
 j=json.dumps(d,separators=(',',':')).encode();j+=b' '*((-len(j))%4);p.write_bytes(struct.pack('<III',0x46546c67,2,20+len(j)+len(rest))+struct.pack('<II',len(j),0x4e4f534a)+j+rest)
