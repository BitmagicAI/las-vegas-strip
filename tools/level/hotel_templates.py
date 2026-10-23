"""Small shared Blender assets for streamed Bellagio and Veer guest floors."""
import sys,os,math,json,bpy
from pathlib import Path
sys.path.insert(0,'tools/blender-level')
import bmlevel as b
OUT='build/hotels'

def palette(modern=False):
 b.mat('wall',(.65,.67,.65) if modern else (.76,.69,.55),roughness=.83)
 b.mat('wood',(.16,.19,.20) if modern else (.17,.065,.025),roughness=.54)
 b.mat('trim',(.27,.32,.35) if modern else (.48,.30,.10),metal=.65,roughness=.35)
 b.mat('carpet',(.045,.15,.19) if modern else (.16,.045,.035),roughness=.98)
 b.mat('stone',(.34,.39,.39) if modern else (.64,.57,.42),roughness=.75)
 b.mat('linen',(.79,.80,.73),roughness=.95);b.mat('glass_window',(.30,.53,.65),alpha=.16,roughness=.25)
 b.mat('black',(.014,.023,.028),roughness=.42)
 b.mat('emissive_light',(.9,.74,.43),glow=1.7);b.mat('art',(.13,.35,.40) if modern else (.30,.22,.11))

serial=0
def uid(n):
 global serial
 serial+=1
 return f'{serial:04d} {n}'
def D(n,p,s,m):b.decor(uid(n),p,s,m,bevel=min(.025,min(s)/5))
def B(n,p,s,m):b.box(uid(n),p,s,m)
def lighting(z=0):
 D('light diffuser',(0,3.36,z),(1.1,.06,.55),'emissive_light')
 b.lamp('ceiling light',(0,2.9,z),'#ffe0ac',intensity=17,distance=9)
def start(modern):b.reset();palette(modern)
def finish(name):
 # Match the existing Bellagio material projection (six metres per tile).
 for o in bpy.data.objects:
  if o.type!='MESH' or o.data.uv_layers:continue
  uv=o.data.uv_layers.new(name='ArchitecturalUV')
  for poly in o.data.polygons:
   axis=max(range(3),key=lambda i:abs(poly.normal[i]));axes=[i for i in range(3) if i!=axis]
   for li in poly.loop_indices:
    v=o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co
    uv.data[li].uv=(v[axes[0]]/6,v[axes[1]]/6)
 b.export(OUT,name)
 # Runtime metadata is small, never an enumeration of the building.
 Path('src/work/hotels/'+name+'.json').write_text(Path(OUT+'/'+name+'.mesh-level.json').read_text())

def bellagio_finishes():
 # Reuse the actual packed resort materials, including their textures; no
 # approximate white substitute and no edits to the original city asset.
 names=['b_plaster','b_travertine','b_walnut','b_bronze','b_marble','b_darkmarble','b_shadowstone','b_emissive']
 with bpy.data.libraries.load(str(Path('build/level/vegas.blend').resolve()),link=False) as (src,dst):dst.materials=list(names)
 for name in names:b.scene.materials[name]=bpy.data.materials[name]
 for alias,name in [('wall','b_plaster'),('stone','b_travertine'),('wood','b_walnut'),('trim','b_bronze')]:b.scene.materials[alias]=bpy.data.materials[name]

def entry_arch():
 # A moulded semicircular stone surround above the recessed stair door.
 r=1.21;spring=2.82
 for i in range(24):
  a,c=math.pi*i/24,math.pi*(i+1)/24
  points=[(rr*math.cos(t),spring+rr*math.sin(t),z) for z in [-5.66,-5.38] for rr,t in [(r,a),(r,c),(r+.24,c),(r+.24,a)]]
  me=bpy.data.meshes.new(uid('arched guest portal'));me.from_pydata([(x,-z,y) for x,y,z in points],[],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);me.update()
  ob=bpy.data.objects.new(me.name,me);b.scene.collection.objects.link(ob);me.materials.append(b.scene.materials['stone'])
 # Normals follow the same wound rings used by the existing resort arches.
 import bmesh
 for ob in bpy.data.objects:
  if ob.type=='MESH' and 'arched guest portal' in ob.name:
   bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()

for modern,prefix in [(False,'bellagio'),(True,'veer')]:
 start(modern)
 if not modern:bellagio_finishes()
 # A permanent, hollow podium sleeve hides streamed service storeys and seals
 # the casino ceiling cutout. It has no horizontal cap across the stair route.
 # The inner faces clear the modular shaft; the outer faces overlap the small
 # Boolean clearance in the podium, avoiding cracks and coplanar surfaces.
 recipes=json.loads(Path('src/work/hotels/towers.json').read_text())
 height=next(t['firstGuestFloor'] for t in recipes if t['set']==prefix)*3.6
 for side in [-1,1]:B('podium shaft cladding',(side*3.83,height/2,0),(.24,height,10.65),'wall')
 B('podium shaft rear',(0,height/2,5.23),(7.42,height,.24),'wall')
 for side in [-1,1]:B('podium entry pier',(side*2.305,1.325,-5.23),(2.79,2.65,.24),'wall')
 B('podium entry headwall',(0,(height+2.65)/2,-5.23),(7.42,height-2.65,.24),'wall')
 for x in [-.96,.96]:D('lobby door jamb',(x,1.35,-5.4),(.09,2.7,.09),'trim')
 D('lobby door lintel',(0,2.7,-5.4),(2.01,.10,.09),'trim')
 if not modern:
  # Foundations continue the podium at the perimeter. No platform crosses a
  # stair flight; the foot of the core and its approach remain step-free.
  b.slab('guest core foundation',(0,0),(7.9,10.7),'b_darkmarble',y=-.012,thickness=.25)
  b.slab('guest vestibule marble',(0,-7.2),(11,3.7),'b_marble',y=.018,thickness=.16)
  for x in [-5.32,5.32]:D('vestibule bronze inlay',(x,.031,-7.2),(.045,.012,3.6),'trim')
  D('vestibule threshold border',(0,.031,-8.94),(10.68,.012,.045),'trim')
  for x in [-3.59,3.59]:
   D('engaged travertine pilaster',(x,3.55,-5.49),(.48,7.1,.36),'stone')
   for y,w,h,d in [(.22,.78,.44,.55),(1.13,.59,.13,.42),(6.88,.66,.19,.48),(7.17,.83,.25,.59)]:D('pilaster moulding',(x,y,-5.50),(w,h,d),'stone')
  for y,w,h,d in [(7.40,8.04,.22,.62),(7.63,8.3,.24,.76),(7.79,8.48,.09,.83)]:D('continuous entry cornice',(0,y,-5.45),(w,h,d),'stone')
  D('cornice bronze shadow line',(0,7.26,-5.65),(7.6,.07,.11),'trim')
  for side in [-1,1]:
   x=side*2.3
   D('walnut dado panel',(x,.66,-5.38),(1.8,1.10,.12),'wood')
   for y in [.12,1.23]:D('dado stone rail',(x,y,-5.49),(1.98,.12,.20),'stone')
   for xx in [x-.82,x+.82]:D('panel bronze edge',(xx,.67,-5.46),(.026,.93,.025),'trim')
   D('sconce bronze backplate',(x,3.03,-5.5),(.30,.75,.13),'trim')
   D('sconce alabaster',(x,3.08,-5.66),(.23,.51,.20),'emissive_light')
   b.lamp(uid('guest portal sconce'),(x,3.12,-5.95),'#ffdda8',intensity=16,distance=9)
   for y in [.18,1.12,6.9,7.45]:D('return wall moulding',(side*3.99,y,0),(.18,.16,10.65),'stone')
   for z in [-3.3,0,3.3]:D('return walnut dado',(side*3.975,.66,z),(.09,1.10,2.92),'wood')
  for x in [-1.06,1.06]:D('recessed walnut jamb',(x,1.40,-5.45),(.30,2.80,.25),'wood')
  for x in [-1.36,1.36]:D('portal stone jamb',(x,1.40,-5.52),(.24,2.80,.28),'stone')
  D('portal walnut overdoor',(0,3.12,-5.41),(2.42,.61,.13),'wood')
  entry_arch()
  D('portal keystone',(0,4.06,-5.68),(.32,.46,.25),'stone')
  D('guest wing sign backing',(0,4.7,-5.49),(3.55,.58,.19),'wood')
  for y in [4.4,5.0]:D('guest sign moulding',(0,y,-5.55),(3.69,.10,.22),'stone')
 b.spawn((0,.025,-6));finish(prefix+'-entry')
 start(modern)
 # The landing belongs to the lower end of this storey; the next copy supplies
 # the upper landing. Treads share GPU buffers and use two smooth ramp colliders.
 b.slab('lower landing',(0,-3.65),(6.8,2.4),'stone',thickness=.18)
 b.slab('hallway threshold',(0,-4.975),(1.8,.25),'stone',thickness=.18)
 b.slab('middle landing',(0,3.65),(6.8,2.35),'stone',y=1.8,thickness=.18)
 with b.context('outbound flight',origin=(-1.65,0,-2.5)):
  b.stairs('outbound',(0,0,0),1.8,5,'stone',width=2.8,rail='trim',waist=.22)
 with b.context('return flight',origin=(1.65,1.8,2.5),yaw=math.pi):
  b.stairs('return',(0,0,0),1.8,5,'stone',width=2.8,rail='trim',waist=.22)
 for side in [-1,1]:B('shaft wall',(side*3.55,1.8,0),(.3,3.6,9.9),'wall')
 B('shaft rear',(0,1.8,4.95),(7.4,3.6,.3),'wall')
 for x in [-2.25,2.25]:B('front wall',(x,1.8,-4.95),(2.7,3.6,.3),'wall')
 B('entry lintel',(0,3.14,-4.95),(1.8,.88,.3),'wall')
 for x in [-.96,.96]:D('entry bronze trim',(x,1.4,-5.13),(.08,2.8,.08),'trim')
 lighting(-3.65)
 b.volume('stair lower landing',(0,1.4,-3.65),(1.4,2.8,1.4),tags=['route','unroofed'])
 b.volume('stair middle landing',(0,3.2,3.65),(5.5,2.8,1.5),tags=['route','unroofed'])
 b.spawn((0,.025,-3.65));finish(prefix+'-stair')
 start(modern)
 b.slab('corridor floor',(0,0),(3.8,6),'carpet',thickness=.18)
 B('corridor ceiling',(0,3.5,0),(3.8,.2,6),'wall')
 for side in [-1,1]:
  for z in [-1.825,1.825]:B('door-side wall',(side*1.85,1.75,z),(.2,3.5,2.35),'wall')
  B('door header',(side*1.85,3.05,0),(.2,.9,1.3),'wall')
  for z in [-.71,.71]:D('door casing',(side*1.72,1.35,z),(.1,2.7,.1),'trim')
  D('wall dado',(side*1.72,.7,-1.8),(.08,.06,2.2),'trim')
  D('wall dado',(side*1.72,.7,1.8),(.08,.06,2.2),'trim')
  D('wall panel',(side*1.735,1.6,2),(.04,1.35,1.15),'wood')
  D('framed art',(side*1.69,1.67,2),(.045,.85,.73),'art')
  D('sconce',(side*1.56,2.65,1.06),(.18,.40,.18),'emissive_light')
  D('skirting',(side*1.71,.12,-1.83),(.06,.2,2.3),'wood')
  D('skirting',(side*1.71,.12,1.83),(.06,.2,2.3),'wood')
 # A property-specific inlaid runner keeps repetition intentional.
 for x in [-1.25,1.25]:D('runner border',(x,.007,0),(.045,.012,6),'trim')
 if not modern:
  for z in [-2,0,2]:D('runner medallion',(0,.009,z),(.55,.013,.55),'art')
  for x in [-1.65,1.65]:
   D('crown moulding',(x,3.31,0),(.17,.15,6),'linen')
   D('gilt crown fillet',(x,3.2,0),(.08,.04,6),'trim')
 else:
  for x in [-1.35,1.35]:D('linear ceiling light',(x,3.36,0),(.04,.035,6),'emissive_light')
  for z in [1.5,1.8,2.1,2.4]:
   for side in [-1,1]:D('slatted wall',(side*1.70,1.65,z),(.06,2.55,.07),'wood')
 lighting();b.volume('corridor',(0,1.5,0),(3.2,3,5.6),tags=['indoors','corridor','unroofed'])
 b.spawn((0,.025,0));finish(prefix+'-corridor')
 if not modern:
  sys.path.insert(0,'tools/level')
  from bellagio_corridor import export_corridor_set
  export_corridor_set()
  from bellagio_premier import export_room
  export_room()
  continue
 start(modern)
 b.slab('room floor',(2.7,0),(5.3,5.85),'wood' if modern else 'carpet',thickness=.18)
 B('room ceiling',(2.775,3.5,0),(5.45,.2,6),'wall')
 for z in [-2.9625,2.9625]:B('room party wall',(2.775,1.75,z),(5.45,3.5,.075),'wall')
 # Corridor provides the doorway wall. Exterior-facing window is an actual opening.
 for z in [-2.56,2.56]:B('window pier',(5.44,1.75,z),(.18,3.5,1.0),'wall')
 B('window sill wall',(5.44,.4,0),(.18,.8,4.15),'wall');B('window header',(5.44,3.2,0),(.18,.6,4.15),'wall')
 for y in [.85,2.87]:D('window frame',(5.36,y,0),(.15,.08,4.15),'trim')
 for z in [-2.04,0,2.04]:D('window mullion',(5.36,1.86,z),(.13,2.1,.06),'trim')
 B('window glass',(5.46,1.85,0),(.045,2.02,4.01),'glass_window')
 # Bathroom with an open circulation path from the entrance.
 B('bath partition',(2.05,1.7,-1.97),(.14,3.4,2.15),'wall')
 B('bath return',(.48,1.7,-.88),(.96,3.4,.14),'wall')
 B('bath lintel',(1.47,3.0,-.88),(1,.8,.14),'wall')
 D('bath tiles',(.98,.018,-1.98),(1.95,.035,2.08),'stone')
 B('vanity',(.55,.45,-2.52),(.8,.9,.63),'wood');D('vanity top',(.55,.94,-2.52),(.9,.08,.72),'linen')
 D('mirror',(.56,1.64,-2.94),(.75,.95,.025),'trim')
 B('shower tray',(1.45,.08,-2.5),(.65,.16,.8),'linen')
 D('shower rail',(1.83,1.8,-2.85),(.04,1.2,.05),'trim')
 # Distinct furnishing plans: a low north-facing platform bed in Veer;
 # an upholstered east-facing bed and classical wall treatment in Bellagio.
 if modern:
  B('platform bed',(3.65,.24,-1.70),(1.95,.48,2.3),'wood')
  D('mattress',(3.65,.58,-1.70),(1.90,.22,2.27),'linen')
  D('duvet',(3.65,.72,-1.45),(1.93,.09,1.7),'art')
  for x in [3.16,4.10]:D('pillow',(x,.76,-2.48),(.73,.18,.42),'linen')
  D('headboard',(3.65,.92,-2.92),(2.12,1.3,.12),'wood')
  for x in [2.8,3.2,3.6,4,4.4]:D('headboard slat',(x,1.02,-2.83),(.045,.92,.045),'trim')
 else:
  B('bed base',(3.72,.24,-1.43),(2.3,.48,1.65),'wood')
  D('mattress',(3.72,.59,-1.43),(2.3,.23,1.65),'linen')
  D('bed cover',(3.93,.74,-1.43),(1.79,.07,1.68),'linen')
  D('bed scarf',(4.35,.785,-1.43),(.46,.035,1.7),'art')
  for z in [-1.83,-1.05]:D('pillow',(2.85,.78,z),(.40,.18,.6),'linen')
  D('headboard',(2.5,.99,-1.43),(.13,1.3,1.93),'wood')
  for z in [-2.0,-1.6,-1.2,-.8]:D('upholstery panel',(2.59,1.04,z),(.08,.86,.35),'art')
  for z in [-2.64,2.64]:
   for i in range(6):D('drapery fold',(5.15,1.85,z+(i-2.5)*.065),(.13,2.35,.055),'linen')
  for z in [-2.91,2.91]:D('ceiling cornice',(2.7,3.32,z),(5.3,.17,.18),'linen')
 B('night table',(2.88,.43,-2.64),(.65,.86,.5),'wood');D('bedside lamp',(2.88,1.1,-2.64),(.25,.42,.25),'emissive_light')
 # Opposite side remains a usable lounge/desk area.
 B('console',(4.91,.46,1.34),(.58,.92,1.7),'wood');D('television',(5.0,1.38,1.34),(.06,.82,1.35),'black')
 B('desk',(3.25,.78,2.5),(1.8,.14,.6),'wood')
 for x in [2.5,4]:B('desk leg',(x,.4,2.5),(.08,.8,.4),'trim')
 B('chair seat',(3.2,.47,1.82),(.6,.12,.6),'art')
 B('chair back',(3.2,.77,1.56),(.6,.57,.09),'art')
 for x in [2.98,3.42]:
  for z in [1.61,2.04]:D('chair leg',(x,.22,z),(.045,.44,.045),'trim')
 D('desk lamp',(3.92,1.04,2.5),(.18,.34,.18),'emissive_light')
 if modern:
  B('kitchen cabinets',(.5,.48,1.9),(.8,.96,2),'wood');D('stone counter',(.5,.99,1.9),(.9,.08,2.1),'stone')
  D('induction hob',(.5,1.04,2.36),(.65,.035,.64),'black');D('sink',(.5,1.04,1.26),(.50,.035,.5),'trim')
  B('fridge',(.5,1.03,.78),(.8,2.06,.6),'trim')
  D('cabinet handles',(.94,.85,1.7),(.035,.38,.045),'trim')
  for z in [1.0,1.6,2.2,2.8]:D('cabinet reveals',(.916,.47,z),(.015,.80,.015),'black')
  D('fridge split',(.92,1.39,.78),(.025,.035,.55),'black')
  D('fridge handle',(.94,1.06,.97),(.035,.5,.04),'black')
 else:
  B('chaise base',(1.15,.25,2),(.85,.50,1.7),'wood')
  D('chaise cushion',(1.15,.57,2),(.89,.18,1.73),'art')
  D('chaise back',(.80,.87,2),(.15,.58,1.72),'art')
  D('framed landscape',(2.9,2.3,2.96),(1.6,.8,.06),'trim');D('landscape',(2.9,2.3,2.92),(1.48,.68,.03),'art')
 b.lamp('room warm pool',(2.8,2.9,.35),'#ffe4bd',intensity=24,distance=10)
 b.lamp('window bounce',(4.95,2.3,0),'#adcddd',intensity=12,distance=7)
 b.volume('guest room',(2.7,1.5,0),(5.3,3,5.8),tags=['indoors','hotel-room'])
 b.spawn((.4,.025,0));finish(prefix+'-room')
for modern,prefix in [(False,'bellagio'),(True,'veer')]:
 start(modern)
 B('sealed access panel',(0,1.7,-2.42),(6.8,3.4,.18),'wall')
 D('access stripe',(0,1.55,-2.30),(3,.05,.04),'trim')
 b.text('sealed label','SERVICE / SEALED',(0,1.85,-2.28),'trim',size=.2)
 b.spawn((0,.025,-3.6));finish(prefix+'-cap')
for modern,prefix in [(False,'bellagio'),(True,'veer')]:
 start(modern)
 # Render-only lid at the moving streaming boundary, beyond visible flights.
 # The same thin slab seals the bottom. No collider or walkable-ground index.
 D('shaft streaming closure',(0,-.09,0),(7.4,.18,10.2),'wall')
 b.spawn((0,.025,0));finish(prefix+'-closure')
print('Shared hotel templates complete',flush=True)
