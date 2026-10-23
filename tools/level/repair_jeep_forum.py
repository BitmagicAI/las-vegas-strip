"""Idempotent repair of the current local level; retains all CityCenter edits.
Run on the final Blender source after a baseline regeneration, before export.
"""
import bpy,json,os,shutil,sys,math
from pathlib import Path
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=os.path.abspath('build/level/vegas.blend'))
for suffix in ['blend','mesh-level.json']:
 p=Path('build/level/vegas.'+suffix);backup=Path('build/repairs/pre-jeep-forum.'+suffix)
 if not backup.exists():shutil.copy2(p,backup)
data=json.loads(Path('build/level/vegas.mesh-level.json').read_text())
report={'shopfronts':[],'ground':[]}
def bounds(ob):
 pts=[ob.matrix_world@Vector(p) for p in ob.bound_box]
 return [min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]
def resize_x(ob,lo,hi):
 a,b=bounds(ob);ob.scale.x*=(hi-lo)/(b[0]-a[0]);ob.location.x+=(lo+hi-a[0]-b[0])/2
 bpy.context.view_layer.update()
# Jambs occupy x=centre +/- [2.00,2.24]. Window/base ends must stop outside
# the jamb, including their depth returns; shared end planes caused the stripes.
shops=[(-162,'FORUM ARCADE -162','FORUM GIFTS'),(-144,'FORUM ARCADE -144','GALLERIA'),(-126,'FORUM ARCADE -126','BOUTIQUE'),(-122,'FORUM UPPER BOUTIQUE','UPPER BOUTIQUE')]
for x,key,title in shops:
 fascia=next(o for o in bpy.data.objects if key in o.name and o.name.endswith(' fascia'))
 a,b=bounds(fascia);width=b[0]-a[0];inner=2.28;outer=width/2-.15
 for ob in list(bpy.data.objects):
  if key not in ob.name:continue
  if ob.name.endswith(' window') or ob.name.endswith(' display window base'):
   lo,hi=bounds(ob);side=1 if (lo[0]+hi[0])/2>x else -1
   resize_x(ob,x+inner if side==1 else x-outer,x+outer if side==1 else x-inner)
   collider=next((c for c in data['colliders'] if c['name']==ob.name),None)
   if collider:
    collider['position'][0]=(x+side*(inner+outer)/2);collider['size'][0]=outer-inner
  elif ob.name.endswith(' glyphs'):
   # Regenerate text in its existing plane, then fit actual measured glyph bounds.
   matrix=ob.matrix_world.copy();name=ob.name;materials=list(ob.data.materials)
   curve=bpy.data.curves.new(name+' fitted','FONT');curve.body=title;curve.align_x='CENTER';curve.size=.43;curve.extrude=.009;curve.resolution_u=4
   temp=bpy.data.objects.new(name+' source',curve);bpy.context.scene.collection.objects.link(temp);temp.matrix_world=matrix
   for mat in materials:curve.materials.append(mat)
   bpy.context.view_layer.update();lo,hi=bounds(temp)
   factor=min(1,3.5/(hi[0]-lo[0]),.36/(hi[2]-lo[2]));curve.size*=factor
   bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();me=bpy.data.meshes.new_from_object(temp.evaluated_get(dg));ob.data=me;ob['label']=title
   bpy.data.objects.remove(temp,do_unlink=True)
 bpy.context.view_layer.update()
 label=next(o for o in bpy.data.objects if key in o.name and o.name.endswith(' glyphs'));lo,hi=bounds(label)
 assert lo[0]>=x-1.8 and hi[0]<=x+1.8,(key,'label crosses jamb')
 # No window/base side face is coplanar with a jamb, even when viewed obliquely.
 for ob in bpy.data.objects:
  if key in ob.name and (ob.name.endswith(' window') or ob.name.endswith(' display window base')):
   a,b=bounds(ob);near=min(abs(a[0]-x),abs(b[0]-x));assert near>2.26
 report['shopfronts'].append({'shop':key,'label':title,'labelWidth':hi[0]-lo[0],'jambClearance':.04})
# Raised paving was visual only: give tires the same surface the player sees.
# One continuous forecourt collider bridges narrow grout joints for stable wheels.
pavers=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('Sanctuary / paver ')]
a=[min(bounds(o)[0][i] for o in pavers) for i in range(3)];b=[max(bounds(o)[1][i] for o in pavers) for i in range(3)]
surfaces=[('Repairs / sanctuary paving',a,b)]
for name in ['District ground / boulevard','District ground / Flamingo Road']:
 ob=bpy.data.objects.get(name)
 if ob:surfaces.append(('Repairs / '+name,*bounds(ob)))
for name,a,b in surfaces:
 record={'name':name,'shape':'box','position':[(a[0]+b[0])/2,(a[2]+b[2])/2,-(a[1]+b[1])/2],'size':[b[0]-a[0],b[2]-a[2],b[1]-a[1]],'yaw':0}
 data['colliders']=[c for c in data['colliders'] if c['name']!=name];data['colliders'].append(record)
 report['ground'].append(record)
Path('build/level/vegas.mesh-level.json').write_text(json.dumps(data,indent=2))
Path('src/work/vegas.mesh-level.json').write_text(json.dumps(data,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath('build/level/vegas.blend'))
Path('build/repairs/forum-ground-report.json').write_text(json.dumps(report,indent=2))
print('FORUM / GROUND REPAIRS PASS',json.dumps(report),flush=True)
