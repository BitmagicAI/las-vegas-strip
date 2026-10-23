"""Incrementally stage guest voids, connected galleries and wayfinding.

Start from this change's backed-up CURRENT stage, never an old city builder.
Upper render shells remain intact; only collision has full-height guest voids.
"""
import bpy,bmesh,json,math,sys
from pathlib import Path
from mathutils import Vector
OUT=Path('build/hotels');BASE=OUT/'resort-expansion/before'
bpy.ops.wm.open_mainfile(filepath=str((BASE/'staged-vegas.blend').resolve()))
data=json.loads((BASE/'staged-vegas.mesh-level.json').read_text())
towers=[t for t in json.loads(Path('src/work/hotels/towers.json').read_text()) if t['set'] not in ['bellagio','veer']]
FACES=[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)]
def wp(t,p):
 x,y,z=p;c,s=math.cos(t['yaw']),math.sin(t['yaw']);ox,oy,oz=t['origin'];return (ox+c*x+s*z,oy+y,oz-s*x+c*z)
def lp(t,p):
 x=p.x-t['origin'][0];z=-p.y-t['origin'][2];y=p.z-t['origin'][1];c,s=math.cos(t['yaw']),math.sin(t['yaw']);return c*x-s*z,y,s*x+c*z
def mesh(name,vertices,faces,material=None):
 me=bpy.data.meshes.new(name);me.from_pydata([(x,-z,y) for x,y,z in vertices],[],faces);me.update()
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 o=bpy.data.objects.new(name,me);bpy.context.scene.collection.objects.link(o)
 if material:me.materials.append(bpy.data.materials[material])
 return o
def bbox(o):
 pts=[o.matrix_world@Vector(v) for v in o.bound_box];return [min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)],pts
def overlap(a,b):return all(a[1][i]>b[0][i]+.0001 and b[1][i]>a[0][i]+.0001 for i in range(3))
cutters=[]
def cutter(t,lo,hi,render=False,name=''):
 o=mesh('Expansion cut '+name,[wp(t,(x,y,z)) for x in [lo[0],hi[0]] for y in [lo[1],hi[1]] for z in [lo[2],hi[2]]],FACES);cutters.append(dict(o=o,t=t,lo=lo,hi=hi,render=render))
for t in towers:
 height=t['firstGuestFloor']*3.6
 # Exact shaft clearance leaves the permanent sleeve overlapping its edge.
 cutter(t,(-3.73,-.15,-5.15),(3.73,t['floors']*3.6+.2,5.16),False,t['id']+' full shaft')
 cutter(t,(-3.73,-.15,-5.15),(3.73,height+.10,5.16),True,t['id']+' podium')
 d=t['roomDepth']+1.95
 cutter(t,(-d,height-.15,-5.1-t['bays']*6),(d,t['floors']*3.6+.2,-4.65),False,t['id']+' guest rooms')
 cutter(t,(-2.0,-.15,-10.5),(2.0,3.3,-4.8),True,t['id']+' approach')
identity=dict(origin=[0,0,0],yaw=0)
galleries=[('paris',(130,-50),(161,-26)),('caesars',(-205,-240),(-169,-217))]
for key,(x0,z0),(x1,z1) in galleries:cutter(identity,(x0,-.15,z0),(x1,4.35,z1),True,key+' guest gallery')
bpy.context.view_layer.update()
for c in cutters:c['bounds']=bbox(c['o'])
def diff(o,c,render=False):
 lo,hi,t=c['lo'],c['hi'],c['t'];points=[lp(t,p) for p in bbox(o)[2]]
 if all(all(lo[i]+1e-5<p[i]<hi[i]-1e-5 for i in range(3)) for p in points):o.data.clear_geometry();return
 bpy.context.view_layer.objects.active=o;o.select_set(True);mod=o.modifiers.new('Resort circulation clearance','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=c['o'];bpy.ops.object.modifier_apply(modifier=mod.name);o.select_set(False)
 if render and len(o.data.polygons):
  bm=bmesh.new();bm.from_mesh(o.data);gone=[]
  for f in bm.faces:
   ps=[lp(t,o.matrix_world@v.co) for v in f.verts]
   if any(all(abs(p[axis]-bound)<.003 for p in ps) for axis in range(3) for bound in [lo[axis],hi[axis]]):gone.append(f)
  bmesh.ops.delete(bm,geom=gone,context='FACES');bm.to_mesh(o.data);bm.free();o.data.update()
scene=bpy.context.scene;work=bpy.data.scenes.new('Expansion boolean workspace')
for c in cutters:work.collection.objects.link(c['o'])
original=[o for o in scene.objects if o.type=='MESH' and not o.name.startswith('Expansion cut')]
bpy.context.window.scene=work
changed=[]
for o in original:
 bb=bbox(o)
 if bb[1][2]<=.18 and bb[1][2]-bb[0][2]<.6:continue
 cs=[c for c in cutters if c['render'] and overlap(bb,c['bounds'])]
 if not cs:continue
 work.collection.objects.link(o);name=o.name
 for c in cs:
  if len(o.data.vertices):diff(o,c,True)
 if not len(o.data.vertices):bpy.data.objects.remove(o,do_unlink=True)
 else:work.collection.objects.unlink(o)
 changed.append(name)
 if len(changed)%100==0:print('Render clearances',len(changed),flush=True)
def collider_mesh(c):
 if c['shape']=='box':
  t=dict(origin=c['position'],yaw=c.get('yaw',0));w,h,d=[v/2 for v in c['size']];return mesh('Collider cut',[wp(t,(x,y,z)) for x in [-w,w] for y in [-h,h] for z in [-d,d]],FACES)
 vs=list(zip(*[iter(c['vertices'])]*3));ix=c.get('indices',[]);o=mesh('Collider cut',vs,[ix[i:i+3] for i in range(0,len(ix),3)])
 if c['shape']=='convexHull':
  bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.convex_hull(bm,input=list(bm.verts));bm.to_mesh(o.data);bm.free()
 return o
updated=[];collider_changes=[]
for record in data['colliders']:
 o=collider_mesh(record);bpy.context.view_layer.update();bb=bbox(o)
 cs=[] if bb[1][2]<=.18 and bb[1][2]-bb[0][2]<.6 else [c for c in cutters if 'podium' not in c['o'].name and overlap(bb,c['bounds'])]
 if not cs:updated.append(record);bpy.data.objects.remove(o,do_unlink=True);continue
 for c in cs:
  if len(o.data.vertices):diff(o,c)
 o.data.calc_loop_triangles()
 if len(o.data.loop_triangles):updated.append(dict(name=record['name'],shape='trimesh',vertices=[v for p in o.data.vertices for v in (p.co.x,p.co.z,-p.co.y)],indices=[i for tri in o.data.loop_triangles for i in tri.vertices]))
 bpy.data.objects.remove(o,do_unlink=True);collider_changes.append(record['name'])
print('Collision clearances complete',len(collider_changes),flush=True)
data['colliders']=updated
bpy.context.window.scene=scene;bpy.data.scenes.remove(work)
# Architectural connections and signs use existing materials where possible.
def material(n,rgb):
 m=bpy.data.materials.get(n) or bpy.data.materials.new(n);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*rgb,1);m.diffuse_color=(*rgb,1);return n
stone=material('rg_travertine',(.65,.59,.48));wood=material('rg_walnut',(.075,.045,.029));gold=material('rg_brass',(.59,.44,.21));white=material('rg_letters',(.91,.86,.69));floor=material('rg_marble',(.66,.64,.59))
def box(name,p,size,mat,solid=False,yaw=0):
 t=dict(origin=p,yaw=yaw);w,h,d=[v/2 for v in size];o=mesh(name,[wp(t,(x,y,z)) for x in [-w,w] for y in [-h,h] for z in [-d,d]],FACES,mat)
 if solid:data['colliders'].append(dict(name=o.name,shape='box',position=list(p),size=list(size),yaw=yaw))
 return o
def text(name,words,p,yaw,size=.28,width=5):
 cu=bpy.data.curves.new(name,'FONT');cu.body=words;cu.align_x='CENTER';cu.align_y='CENTER';cu.size=size;cu.extrude=.002
 o=bpy.data.objects.new(name,cu);scene.collection.objects.link(o);o.location=(p[0],-p[2],p[1]);o.rotation_euler=(math.pi/2,0,-yaw);cu.materials.append(bpy.data.materials[white]);bpy.context.view_layer.update()
 if o.dimensions.x>width:o.scale.x*=width/o.dimensions.x
 bpy.ops.object.select_all(action='DESELECT');bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o.select_set(False)
for key,(x0,z0),(x1,z1) in galleries:
 n=key+' / Guest gallery / ';x=(x0+x1)/2;z=(z0+z1)/2;w=x1-x0;d=z1-z0
 box(n+'floor',(x,-.025,z),(w,.2,d),floor,True)
 box(n+'ceiling',(x,4.47,z),(w,.24,d),stone,True)
 # Leave the edge adjoining the public casino open. Other walls form an
 # enclosed guest vestibule, with the stair sleeve integrated at its perimeter.
 for zz in [z0,z1]:box(n+'perimeter',(x,2.25,zz),(w,4.35,.24),stone,True)
 edge=x1 if key=='paris' else x0;box(n+'end wall',(edge,2.25,z),(.24,4.35,d),stone,True)
 for zz in [z0+.18,z1-.18]:
  box(n+'dado',(x,.63,zz),(w-.35,1.12,.10),wood)
  box(n+'cornice',(x,4.05,zz),(w-.2,.18,.30),stone)
 for xx in range(int(x0+3),int(x1-1),5):
  for zz in [z0+.25,z1-.25]:box(n+'pilaster',(xx,2.20,zz),(.35,4.15,.38),stone)
 data['volumes'].append(dict(name=key+' Guest gallery',position=[x,2.25,z],size=[w,4.5,d],yaw=0,tags=['indoors','corridor']))
# Clip new gallery walls against shaft voids (floor/ceiling need the same opening).
for o in list(scene.objects):
 if o.type!='MESH' or ' / Guest gallery / ' not in o.name:continue
 for c in cutters:
  if 'podium' in c['o'].name and overlap(bbox(o),c['bounds']):diff(o,c,True)
# Clip the newly introduced gallery colliders with physical full shaft.
final=[]
for rec in data['colliders']:
 if ' / Guest gallery / ' not in rec['name']:final.append(rec);continue
 o=collider_mesh(rec);bpy.context.view_layer.update()
 for c in cutters:
  if 'full shaft' in c['o'].name and overlap(bbox(o),c['bounds']):diff(o,c)
 o.data.calc_loop_triangles()
 if len(o.data.loop_triangles):final.append(dict(name=rec['name'],shape='trimesh',vertices=[v for p in o.data.vertices for v in (p.co.x,p.co.z,-p.co.y)],indices=[i for tri in o.data.loop_triangles for i in tri.vertices]))
 bpy.data.objects.remove(o,do_unlink=True)
data['colliders']=final
print('Connection galleries complete',flush=True)
for t in towers:
 print('Wayfinding',t['id'],flush=True)
 n=t['building']+' / Guest access / ';yaw=t['yaw']+math.pi
 for z in [-7.0,-14]:
  p=wp(t,(0,3.15,z));box(n+'direction board',p,(3.5,.67,.10),wood,yaw=yaw)
  text(n+'guest direction','GUEST ROOMS / STAIRS',wp(t,(0,3.24,z-.061)),yaw,.19,3.25)
  text(n+'guest levels',f"LEVELS {t['firstGuestFloor']+1} - {t['floors']}",wp(t,(0,2.99,z-.061)),yaw,.12,3.25)
 for x in [-1.34,1.34]:box(n+'portal accent',wp(t,(x,1.50,-5.56)),(.12,3.,.12),gold,yaw=t['yaw'])
for c in cutters:bpy.data.objects.remove(c['o'],do_unlink=True)
data['extras']['streamedHotels']['towers']=[t['id'] for t in json.loads(Path('src/work/hotels/towers.json').read_text())]
data['extras']['streamedHotels']['version']=2
(OUT/'staged-vegas.mesh-level.json').write_text(json.dumps(data,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str((OUT/'staged-vegas.blend').resolve()))
(OUT/'resort-expansion/shell-changes.json').write_text(json.dumps(dict(render=changed,colliders=collider_changes),indent=2))
print('EXPANSION STAGED',len(changed),len(collider_changes),flush=True)
