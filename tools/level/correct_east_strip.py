"""Correct north/south context hotels in the existing incremental Blender level.
Map: official LV Monorail customer-service map (2024). Game north is -Z.
Preserves detailed Paris, gameplay rooms, and authored materials.
"""
import bpy,os,json,ast
from pathlib import Path
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=os.path.abspath('build/level/vegas.blend'))
scene=bpy.context.scene
if scene.get('east_strip_geography_v1'):
 print('East Strip already corrected');raise SystemExit
# label, old center, new center, horizontal scale. Smaller Horseshoe fits the
# compressed parcel between the existing Paris hotel and Flamingo Road.
specs={
 'Flamingo':((133,223),(145,-237),(1,1)),
 'Horseshoe':((162,101),(110,-116),(36/54,62/72)),
 'South Strip skyline':((131,-234),(131,218),(1,1)),
}
def owner(name):
 for key in specs:
  if key in name and 'Road' not in name:return key
 if 'facade rubble 162 ' in name:return 'Horseshoe'
 if 'facade rubble 133 ' in name:return 'Flamingo'
 return None
def transform_point(p,key):
 old,new,scale=specs[key]
 return [new[0]+(p[0]-old[0])*scale[0],p[1],new[1]+(p[2]-old[1])*scale[1]]
counts={k:0 for k in specs}
for ob in list(bpy.data.objects):
 key=owner(ob.name)
 if not key and (ob.name.startswith('fire-damaged facade') or ob.name.startswith('exposed roof rebar')):
  center=sum((ob.matrix_world@Vector(v) for v in ob.bound_box),Vector())/8
  key='Flamingo' if -center.y>170 else 'Horseshoe'
 if not key:continue
 old,new,scale=specs[key]
 # Transform geometry and its origin together (including baked scar vertices).
 from mathutils import Matrix
 matrix=Matrix.Translation((new[0],-new[1],0))@Matrix.Diagonal((scale[0],scale[1],1,1))@Matrix.Translation((-old[0],old[1],0))
 ob.matrix_world=matrix@ob.matrix_world
 if key=='South Strip skyline':ob.name=ob.name.replace(key,'Planet Hollywood resort')
 counts[key]+=1
for col in bpy.data.collections:
 if 'South Strip skyline' in col.name:col.name=col.name.replace('South Strip skyline','Planet Hollywood resort')
# Visible identification for the provisional southern resort massing.
curve=bpy.data.curves.new('Planet Hollywood lettering','FONT');curve.body='PLANET HOLLYWOOD';curve.size=2.4;curve.extrude=.025;curve.align_x='CENTER'
ob=bpy.data.objects.new('Planet Hollywood resort / lettering',curve);scene.collection.objects.link(ob)
import math
ob.location=(94.7,-218,84);ob.rotation_euler=(math.pi/2,0,-math.pi/2);curve.materials.append(bpy.data.materials['emissive_amber'])
bpy.context.view_layer.update();me=bpy.data.meshes.new_from_object(ob.evaluated_get(bpy.context.evaluated_depsgraph_get()));meshob=bpy.data.objects.new(ob.name+' glyphs',me);scene.collection.objects.link(meshob);meshob.matrix_world=ob.matrix_world.copy();bpy.data.objects.remove(ob,do_unlink=True)
p=Path('build/level/vegas.mesh-level.json');data=json.loads(p.read_text())
for field in ['colliders','landmarks','volumes','lights']:
 for record in data[field]:
  key=owner(record['name'])
  if not key:continue
  for prop in ['position','target','foot','top']:
   if prop in record:record[prop]=transform_point(record[prop],key)
  if 'vertices' in record:record['vertices']=[transform_point(v,key) for v in record['vertices']]
  if 'size' in record:
   record['size'][0]*=specs[key][2][0];record['size'][2]*=specs[key][2][1]
  record['name']=record['name'].replace('South Strip skyline','Planet Hollywood resort')
p.write_text(json.dumps(data,indent=2))
scene['east_strip_geography_v1']=True
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath('build/level/vegas.blend'))
source=ast.parse(Path('tools/level/vegas.py').read_text());fn=next(n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=='fast_export');exec(compile(ast.Module(body=[fn],type_ignores=[]),'vegas.py','exec'));fast_export('build/level/vegas.glb')
print('GEOGRAPHY CORRECTED',counts,flush=True)
