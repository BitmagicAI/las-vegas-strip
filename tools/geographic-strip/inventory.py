import bpy,json,sys,collections
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,'tools/level')
from visibility_export import building
bpy.ops.wm.open_mainfile(filepath=str(Path('build/geographic-strip/before/build/hotels/staged-vegas.blend').resolve()))
out=[]
for o in bpy.data.objects:
 if o.type!='MESH':continue
 p=[o.matrix_world@Vector(v) for v in o.bound_box]
 lo=[min(v[i] for v in p) for i in range(3)];hi=[max(v[i] for v in p) for i in range(3)]
 out.append(dict(name=o.name,owner=o.get('arrivalOwner') or building(o.name),min=[lo[0],lo[2],-hi[1]],max=[hi[0],hi[2],-lo[1]],vertices=len(o.data.vertices),polygons=len(o.data.polygons)))
Path('build/geographic-strip/objects.json').write_text(json.dumps(out))
for k in sorted(set(o['owner'] or 'NONE' for o in out)):
 rows=[o for o in out if (o['owner'] or 'NONE')==k]
 print(k,len(rows),[round(min(o['min'][i] for o in rows),2) for i in range(3)],[round(max(o['max'][i] for o in rows),2) for i in range(3)],sum(o['polygons'] for o in rows))
print('UNOWNED',[(o['name'],o['vertices']) for o in out if not o['owner']][:100])
