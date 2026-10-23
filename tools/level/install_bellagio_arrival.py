"""Update the arrival architecture in both editable scenes; retain hotel voids."""
import bpy,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from bellagio_arrival import build_arrival,PREFIX

out=Path('build/bellagio-arrival');out.mkdir(exist_ok=True)
report_path=Path('build/hotels/shell-report.json');report=json.loads(report_path.read_text())
for n,d in report['sourceSHA256'].items():
    with open('build/level/'+n,'rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==d,'Source changed since staging: '+n
changes={}
for path in [Path('build/level/vegas.blend'),Path('build/hotels/staged-vegas.blend')]:
    bpy.ops.wm.open_mainfile(filepath=str(path.resolve()));bpy.context.view_layer.update()
    remove=[]
    for ob in list(bpy.data.objects):
        if not ob.name.startswith('Bellagio'):continue
        if ob.name.startswith(PREFIX):remove.append(ob)
        elif 'broken frontage rail' in ob.name:
            pts=[ob.matrix_world@Vector(v) for v in ob.bound_box];z=-sum(v.y for v in pts)/8
            if 18<z<51:remove.append(ob)
    removed=[ob.name for ob in remove];bpy.data.batch_remove(remove)
    additions=build_arrival();bpy.context.view_layer.update()
    bpy.ops.wm.save_as_mainfile(filepath=str(path.resolve()))
    data_path=path.with_suffix('.mesh-level.json');data=json.loads(data_path.read_text())
    data['colliders']=[c for c in data['colliders'] if not c['name'].startswith(PREFIX)]+additions['colliders']
    data['lights']=[c for c in data['lights'] if not c['name'].startswith(PREFIX)]+additions['lights']
    data_path.write_text(json.dumps(data,indent=2)+'\n')
    changes[str(path)]={'removed':removed,'newColliderCount':len(additions['colliders']),'totalColliders':len(data['colliders'])}
for n in report['sourceSHA256']:
    with open('build/level/'+n,'rb') as f:report['sourceSHA256'][n]=hashlib.file_digest(f,'sha256').hexdigest()
report['repairs']=list(dict.fromkeys(report.get('repairs',[])+['bellagio-glass-porte-cochere']));report_path.write_text(json.dumps(report,indent=2))
(out/'installation.json').write_text(json.dumps(changes,indent=2))
print('Arrival architecture updated in source and stage',flush=True)
