"""Clip the existing source and staged doorway trim without rebuilding the city.
Preserves surface UVs, shared materials, collider data and the restored tower.
"""
import bpy,bmesh,json,sys,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
sys.path.insert(0,str(Path(__file__).resolve().parent))
from bellagio_podium import wall_moulding_spans

OUT=Path('build/hotels/bellagio-door-repair');OUT.mkdir(exist_ok=True)
report_path=Path('build/hotels/shell-report.json')
report=json.loads(report_path.read_text())
for name,digest in report['sourceSHA256'].items():
    with open('build/level/'+name,'rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==digest,'Source changed since staging'
counts={}
for path in [Path('build/level/vegas.blend'),Path('build/hotels/staged-vegas.blend')]:
    bpy.ops.wm.open_mainfile(filepath=str(path.resolve()));bpy.context.view_layer.update()
    remove=[];repaired=[]
    for ob in list(bpy.data.objects):
        if ob.type!='MESH' or not ob.name.startswith('Bellagio ') or not ob.name.endswith('wall moulding'):continue
        pts=[ob.matrix_world@Vector(p) for p in ob.bound_box]
        x=sum(p.x for p in pts)/8;height=sum(p.z for p in pts)/8
        lo,hi=min(-p.y for p in pts),max(-p.y for p in pts)
        spans=wall_moulding_spans(x,height,lo,hi)
        if spans==[(lo,hi)]:continue
        for i,(start,end) in enumerate(spans):
            bm=bmesh.new();bm.from_mesh(ob.data);bm.transform(ob.matrix_world)
            for z,sign in [(start,-1),(end,1)]:
                bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),
                    dist=.00001,plane_co=(0,-z,0),plane_no=(0,sign,0),clear_inner=True)
                boundary=[e for e in bm.edges if e.is_boundary]
                if boundary:bmesh.ops.holes_fill(bm,edges=boundary,sides=0)
            bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
            assert all(e.is_manifold for e in bm.edges),'Trim end must be capped'
            me=bpy.data.meshes.new(ob.name+' segment');bm.to_mesh(me);bm.free();me.update()
            for mat in ob.data.materials:me.materials.append(mat)
            part=ob.copy();part.data=me;part.matrix_world=Matrix.Identity(4);part.name=ob.name+f' / portal span {i+1}'
            for collection in ob.users_collection:collection.objects.link(part)
        repaired.append({'name':ob.name,'spans':spans});remove.append(ob)
    bpy.data.batch_remove(remove)
    bpy.ops.wm.save_as_mainfile(filepath=str(path.resolve()))
    counts[str(path)]=repaired
    print('DOOR TRIM',str(path),len(repaired),'mouldings split',flush=True)
# This repair changed the same four decorative objects in both source and stage;
# update the provenance guard only after both saves completed successfully.
with open('build/level/vegas.blend','rb') as f:report['sourceSHA256']['vegas.blend']=hashlib.file_digest(f,'sha256').hexdigest()
report.setdefault('repairs',[]).append('bellagio-door-trim')
report_path.write_text(json.dumps(report,indent=2))
(OUT/'report.json').write_text(json.dumps(counts,indent=2))
