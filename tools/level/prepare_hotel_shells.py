"""Build a staged hotel-shell variant. Never overwrite the current level.
Inputs: build/level/vegas.blend + JSON. Outputs: build/hotels/staged-* only.
"""
import bpy,bmesh,json,math,os,hashlib,sys
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from hotel_shell_policy import preserve_render_shell
OUT=Path('build/hotels');OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=os.path.abspath('build/level/vegas.blend'))
data=json.loads(Path('build/level/vegas.mesh-level.json').read_text());towers=json.loads(Path('src/work/hotels/towers.json').read_text())
FACES=[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)]
def world(t,p):
 x,y,z=p;dx,dz=t.get('lean',[0,0]);x+=dx*y;z+=dz*y;c=math.cos(t['yaw']);s=math.sin(t['yaw']);ox,oy,oz=t['origin']
 return Vector((ox+c*x+s*z,-(oz-s*x+c*z),oy+y))
def local(t,p):
 x=p.x-t['origin'][0];z=-p.y-t['origin'][2];y=p.z-t['origin'][1];c=math.cos(t['yaw']);s=math.sin(t['yaw']);dx,dz=t.get('lean',[0,0])
 return (c*x-s*z-dx*y,y,s*x+c*z-dz*y)
def mesh(n,verts,faces):
 me=bpy.data.meshes.new(n);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(n,me);bpy.context.scene.collection.objects.link(o);return o
cutters=[]
for t in towers:
 for kind,lo,hi in [('stairs',(-3.73,.19,-5.15),(3.73,t['floors']*3.6+.2,5.16)),('guests',(-8.0,t['firstGuestFloor']*3.6-.15,-4.8-t['bays']*6-.25),(8.0,t['floors']*3.6+.2,-4.65))]:
  pts=[world(t,(x,y,z)) for x in [lo[0],hi[0]] for y in [lo[1],hi[1]] for z in [lo[2],hi[2]]]
  ob=mesh('Hotel void '+t['id']+' '+kind,pts,FACES)
  bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();cutters.append((ob,t,lo,hi))
def bbox(o):
 ps=[o.matrix_world@Vector(p) for p in o.bound_box]
 return [min(p[i] for p in ps) for i in range(3)],[max(p[i] for p in ps) for i in range(3)],ps
bpy.context.view_layer.update()
def overlaps(a,b):return all(a[1][i]>b[0][i]+.0001 and b[1][i]>a[0][i]+.0001 for i in range(3))
cb=[bbox(c[0]) for c in cutters]
def relevant(o):
 bb=bbox(o)
 return [c for c,b in zip(cutters,cb) if overlaps(bb,b)]
def diff(o,c,render=False):
 cutter,t,lo,hi=c;ps=[local(t,p) for p in bbox(o)[2]]
 if all(all(lo[i]+1e-5<p[i]<hi[i]-1e-5 for i in range(3)) for p in ps):o.data.clear_geometry();return
 bpy.context.view_layer.objects.active=o;o.select_set(True)
 mod=o.modifiers.new('Hotel circulation void','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
 bpy.ops.object.modifier_apply(modifier=mod.name);o.select_set(False)
 if render and len(o.data.polygons):
  bm=bmesh.new();bm.from_mesh(o.data);gone=[]
  for f in bm.faces:
   pts=[local(t,o.matrix_world@v.co) for v in f.verts]
   if any(all(abs(p[axis]-bound)<.003 for p in pts) for axis in range(3) for bound in [lo[axis],hi[axis]]):gone.append(f)
  bmesh.ops.delete(bm,geom=gone,context='FACES');bm.to_mesh(o.data);bm.free();o.data.update()
original=[o for o in bpy.data.objects if o.type=='MESH' and not o.name.startswith('Hotel void')];changed=[]
original_scene=bpy.context.scene
work_scene=bpy.data.scenes.new('Staged boolean work')
for c in cutters:work_scene.collection.objects.link(c[0])
bpy.context.window.scene=work_scene
for o in original:
 if preserve_render_shell(o):continue
 cs=relevant(o)
 if not cs:continue
 name=o.name
 work_scene.collection.objects.link(o)
 print('CUT',name,flush=True) if len(changed)%100==0 else None
 for c in cs:
  if len(o.data.vertices):diff(o,c,True)
 if not len(o.data.vertices):bpy.data.objects.remove(o,do_unlink=True)
 else:work_scene.collection.objects.unlink(o)
 changed.append(name)
 if len(changed)%100==0:print('Staged render candidates',len(changed),flush=True)
print('Staged render complete',len(changed),flush=True)
def collider_mesh(c):
 if c['shape']=='box':
  x,y,z=c['position'];w,h,d=c['size'];a=c.get('yaw',0);co=math.cos(a);si=math.sin(a)
  vs=[(x+co*xx+si*zz,-(z-si*xx+co*zz),y+yy) for xx in [-w/2,w/2] for yy in [-h/2,h/2] for zz in [-d/2,d/2]]
  return mesh('Collider cut',vs,FACES)
 v=c['vertices'];vs=[(v[i],-v[i+2],v[i+1]) for i in range(0,len(v),3)]
 if c['shape']=='trimesh':
  ix=c['indices'];return mesh('Collider cut',vs,[ix[i:i+3] for i in range(0,len(ix),3)])
 o=mesh('Collider cut',vs,[]);bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.convex_hull(bm,input=list(bm.verts));bm.to_mesh(o.data);bm.free();return o
updated=[];cc=[]
for record in data['colliders']:
 o=collider_mesh(record);bpy.context.view_layer.update();cs=relevant(o)
 if not cs:updated.append(record);bpy.data.objects.remove(o,do_unlink=True);continue
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
 for c in cs:
  if len(o.data.vertices):diff(o,c)
 o.data.calc_loop_triangles()
 if len(o.data.loop_triangles):
  vs=[]
  for v in o.data.vertices:vs.extend([v.co.x,v.co.z,-v.co.y])
  updated.append({'name':record['name'],'shape':'trimesh','vertices':vs,'indices':[i for tri in o.data.loop_triangles for i in tri.vertices]})
 bpy.data.objects.remove(o,do_unlink=True);cc.append(record['name'])
for c in cutters:bpy.data.objects.remove(c[0],do_unlink=True)
bpy.context.window.scene=original_scene
bpy.data.scenes.remove(work_scene)
data['colliders']=updated;data.setdefault('extras',{})['streamedHotels']={'version':1,'towers':[t['id'] for t in towers]}
(OUT/'staged-vegas.mesh-level.json').write_text(json.dumps(data,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str((OUT/'staged-vegas.blend').resolve()))
report={'renderCandidates':changed,'colliderCandidates':cc,'colliders':len(updated),'sourceSHA256':{}}
for name in ['vegas.blend','vegas.mesh-level.json']:
 with open('build/level/'+name,'rb') as f:report['sourceSHA256'][name]=hashlib.file_digest(f,'sha256').hexdigest()
(OUT/'shell-report.json').write_text(json.dumps(report,indent=2));print('STAGED HOTEL SHELLS',len(changed),len(cc),len(updated),flush=True)
import sys
sys.path.insert(0,'tools/level')
from extend_bellagio_room_voids import extend
extend()
