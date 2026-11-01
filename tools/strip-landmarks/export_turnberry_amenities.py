"""Targeted export; retain the existing Turnberry asset through the append installer."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
import bpy, math, json, struct
from mathutils import Matrix
E.colors.update({'tta-seat':'e5ded0','tta-frame-paint':'9da6a5','tta-canopy':'e8dfc8','tta-bark':'86745b','tta-leaf':'547344','tta-grass':'627943','tta-fence-paint':'456566','tta-court-blue':'426f9c'})
bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('turnberryAmenities-exterior')
# Existing redistributable foliage source, never the runtime optimized copy.
before=set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=str(Path('tools/foliage/models/tree-2.glb').resolve()))
added=set(bpy.data.objects)-before;bpy.context.view_layer.update()
proto=[(o.data,o.matrix_world.copy()) for o in added if o.type=='MESH']
coords=[m@v.co for data,m in proto for v in data.vertices];lo=min(v.z for v in coords);hi=max(v.z for v in coords)
for o in added:bpy.data.objects.remove(o,do_unlink=True)
for i,(x,z,h) in enumerate(json.loads(Path('build/city-exteriors/turnberry-amenities-trees.json').read_text())):
 T=Matrix.Translation((x,-z,0.08))@Matrix.Rotation(i*1.3,4,'Z')@Matrix.Scale(h/(hi-lo),4)@Matrix.Translation((0,0,-lo))
 for j,(data,m) in enumerate(proto):
  o=bpy.data.objects.new(f'Turnberry landscape tree {i}/{j}',data);bpy.context.collection.objects.link(o);o.matrix_world=T@m;o['property']='turnberryAmenities';o['source']='turnberry-amenities';o['detail']=0
p=E.OUT/'turnberryAmenities-exterior.glb';bpy.ops.export_scene.gltf(filepath=str(p.resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
print(p)

b=p.read_bytes();jn=struct.unpack_from('<I',b,12)[0];d=json.loads(b[20:20+jn]);rest=b[20+jn:]
for mat in d.get('materials',[]):
 if 'leaves' in mat.get('name','').lower():mat['alphaMode']='MASK';mat['alphaCutoff']=.12;mat['doubleSided']=True
j=json.dumps(d,separators=(',',':')).encode();j+=b' '*((-len(j))%4);p.write_bytes(struct.pack('<III',0x46546c67,2,20+len(j)+len(rest))+struct.pack('<II',len(j),0x4e4f534a)+j+rest)
