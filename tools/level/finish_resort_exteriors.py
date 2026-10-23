"""Reference-led local exterior pass. Run after resort_interiors.py.
Uses the immutable pre-pass baseline in build/exteriors; see RESORT-EXTERIORS.md.
"""
import bpy,sys,os,json,math,random
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,'tools/blender-level');sys.path.insert(0,'tools/level')
from bmlevel import *
from bmlevel.core import HullCollider
from geometry_quality import orient_closed_solids
bpy.ops.wm.open_mainfile(filepath=os.path.abspath('build/exteriors/baseline.blend'))
scene.materials.update({m.name:m for m in bpy.data.materials})
data=json.loads(Path('build/exteriors/baseline.mesh-level.json').read_text())
P='Exterior / ';hotel='';serial=0;labels=[];rng=random.Random(92826)
def uid(n):
 global serial
 serial+=1;return P+hotel+f' / {serial:05d} '+n
# Retain the complete public interiors, roads, routes and neighboring landmarks.
def obsolete(n):
 return (n.startswith(('Flamingo hotel /','Horseshoe north wing /','Planet Hollywood resort /','fire-damaged facade','exposed roof rebar')) or n.startswith(('Scene Collection / Flamingo fin','Scene Collection / Flamingo neon','Scene Collection / Horseshoe lettering')))
old=[o for o in bpy.data.objects if obsolete(o.name)];removed=[o.name for o in old]
bpy.data.batch_remove(old);data['colliders']=[c for c in data['colliders'] if not obsolete(c['name'])]
for n,c,metal,rough,em in [
 ('limestone',(.72,.68,.57),.03,.65,0),('chalk',(.81,.79,.70),.02,.53,0),('concrete',(.45,.43,.39),0,.86,0),
 ('steel',(.24,.26,.28),.65,.45,0),('dark',(.025,.031,.041),.35,.54,0),('bronze',(.36,.22,.08),.66,.4,0),
 ('gold',(.86,.51,.08),.64,.32,.2),('pink',(.43,.065,.15),.2,.38,0),('pinkglass',(.22,.095,.15),.65,.23,0),
 ('roseglass',(.36,.17,.21),.65,.28,0),('blueglass',(.07,.13,.20),.67,.25,0),('skyglass',(.21,.34,.45),.62,.23,0),
 ('nightglass',(.022,.047,.066),.6,.29,0),('red',(.38,.018,.033),.15,.53,0),('teal',(.025,.16,.16),.33,.47,0),
 ('pool',(.035,.23,.23),.38,.27,0),('leaf',(.065,.115,.052),0,.91,0),('trunk',(.16,.12,.075),0,.89,0),
 ('pinkneon',(.95,.10,.38),.1,.35,1.7),('warmneon',(1,.60,.19),.1,.4,1),('screen',(.15,.028,.078),.25,.5,.16),
 ('sand',(.39,.32,.23),0,.9,0),('soot',(.03,.032,.036),0,.98,0)]:mat('rx_'+n,c,metal=metal,roughness=rough,glow=em)
# Petals, fronds and barrel-canopy panels are intentionally open sheets.
for n in ['pink','gold','leaf','skyglass']:bpy.data.materials['rx_'+n].use_backface_culling=False
def D(n,p,s,m='limestone',**kw):decor(uid(n),p,s,'rx_'+m,**kw)
def B(n,p,s,m='limestone',**kw):box(uid(n),p,s,'rx_'+m,**kw)
def M(n,vs,fs,m,solid=False,smooth=False):
 name=uid(n);me=bpy.data.meshes.new(name);me.from_pydata([(x,-z,y) for x,y,z in vs],[],fs);me.update();ob=bpy.data.objects.new(name,me);scene.collection.objects.link(ob);me.materials.append(bpy.data.materials['rx_'+m])
 if solid:level.colliders.append(HullCollider(name,[v for p in vs for v in p]))
 if smooth:
  for f in me.polygons:f.use_smooth=True
 return ob
def prism2(n,outline,y0,y1,m='limestone',solid=True):prism(uid(n),outline,y0,y1,'rx_'+m,solid=solid)
def sign(s,p,size=1,yaw=-math.pi/2,m='warmneon',italic=False):
 cr=bpy.data.curves.new(uid(s),'FONT');cr.body=s;cr.align_x='CENTER';cr.size=size;cr.extrude=.027;cr.bevel_depth=.007;cr.shear=0
 if italic:cr.font=bpy.data.fonts.load('/System/Library/Fonts/Supplemental/Brush Script.ttf',check_existing=True)
 ob=bpy.data.objects.new(cr.name,cr);scene.collection.objects.link(ob);ob.location=(p[0],-p[2],p[1]);ob.rotation_euler=(math.pi/2,0,yaw);cr.materials.append(bpy.data.materials['rx_'+m]);labels.append(ob)
 return ob
# Closed tubes, used for ornamental neon, railing and palm stems.
def tube(n,points,r,m='steel',sides=8):
 pts=[Vector(p) for p in points];vs=[]
 for i,p in enumerate(pts):
  t=(pts[min(i+1,len(pts)-1)]-pts[max(i-1,0)]).normalized();u=t.cross(Vector((0,1,0)))
  if u.length<.01:u=t.cross(Vector((1,0,0)))
  u.normalize();v=t.cross(u).normalized()
  for j in range(sides):vs.append(tuple(p+r*(u*math.cos(j*math.tau/sides)+v*math.sin(j*math.tau/sides))))
 fs=[tuple(reversed(range(sides))),tuple(range((len(pts)-1)*sides,len(pts)*sides))]
 fs += [(i*sides+j,i*sides+(j+1)%sides,(i+1)*sides+(j+1)%sides,(i+1)*sides+j) for i in range(len(pts)-1) for j in range(sides)]
 return M(n,vs,fs,m)
def round_rect(x,z,w,d,r=3,steps=6):
 return [(cx+r*math.cos(a+j*math.pi/2/steps),cz+r*math.sin(a+j*math.pi/2/steps)) for cx,cz,a in [(x+w/2-r,z+d/2-r,0),(x-w/2+r,z+d/2-r,math.pi/2),(x-w/2+r,z-d/2+r,math.pi),(x+w/2-r,z-d/2+r,3*math.pi/2)] for j in range(steps+1)]
def roof(n,outline,y):
 prism2(n+' roof',outline,y,y+.35,'concrete',False)
 for a,b in zip(outline,outline[1:]+outline[:1]):facebox(n+' parapet',a,b,.5,y+.65,.85,.24,'chalk',out=0)
def facebox(n,a,b,u,y,w,h,m,depth=.14,out=.10):
 dx=b[0]-a[0];dz=b[1]-a[1];L=math.hypot(dx,dz);tx=dx/L;tz=dz/L
 D(n,(a[0]+dx*u+tz*out,y,a[1]+dz*u-tx*out),(w,h,depth),m,yaw=math.atan2(-tz,tx))
def facade(n,outline,y0,y1,style):
 # Real window openings represented as opaque recessed glazing; enclosing solids
 # remain watertight and are also the coarse long-range shadow silhouettes.
 for a,b in zip(outline,outline[1:]+outline[:1]):
  L=math.dist(a,b)
  if L<.15:continue
  if style=='ph':
   spacing=2.35;cols=max(1,round(L/spacing));rows=max(1,round((y1-y0-7)/2.45));step=(y1-y0-7)/rows
   for i in range(cols):
    u=(i+.5)/cols
    for j in range(rows):
     facebox(n+' paired room glazing',a,b,u,y0+2+j*step,L/cols*.40,step*.74,'nightglass',out=.035,depth=.09)
    facebox(n+' crown lancet',a,b,u,y1-3,L/cols*.50,4.9,'nightglass',out=.05)
   for yy in [y0+.7,y0+(y1-y0)*.35,y1-6.2]:facebox(n+' belt',a,b,.5,yy,L,.35,'chalk',out=.17,depth=.18)
  elif style=='flamingo':
   rows=max(1,round((y1-y0-3)/2.35));step=(y1-y0-3)/rows
   facebox(n+' reflective window wall',a,b,.5,(y0+y1)/2,L,y1-y0-.4,'pinkglass',depth=.11,out=.035)
   for j in range(rows):
    yy=y0+1.4+j*step
    facebox(n+' white floor ribbon',a,b,.5,yy,L,.22,'chalk',out=.20,depth=.22)
    if j%4==1:facebox(n+' rose reflection',a,b,.5,yy+step*.50,L,step*.36,'roseglass',out=.11,depth=.06)
   for i in range(max(1,round(L/2.9))+1):
    u=i/max(1,round(L/2.9));facebox(n+' white vertical mullion',a,b,u,(y0+y1)/2,.15,y1-y0,'chalk',out=.23,depth=.27)
   facebox(n+' roof fascia',a,b,.5,y1-1,L,2.1,'chalk',out=.27,depth=.6)
  else:
   facebox(n+' blue bronze curtain wall',a,b,.5,(y0+y1)/2,L,y1-y0,'blueglass',out=.07)
   rows=max(1,round((y1-y0)/2.65));step=(y1-y0)/rows
   for j in range(rows):
    yy=y0+j*step
    facebox(n+' horizontal spandrel',a,b,.5,yy,L,.66,'steel',out=.22,depth=.28)
    facebox(n+' slab edge',a,b,.5,yy+.36,L,.12,'chalk',out=.25,depth=.35)
   cols=max(1,round(L/2.4))
   for i in range(cols+1):facebox(n+' slender mullion',a,b,i/cols,(y0+y1)/2,.14,y1-y0,'bronze',out=.25,depth=.4)
   facebox(n+' upper setback',a,b,.5,y1-4.1,L,.85,'limestone',out=.8,depth=1.65)
   facebox(n+' blue roof crown',a,b,.5,y1+1.25,L,2.5,'skyglass',out=.0,depth=.18)
   for i in range(cols+1):facebox(n+' crown fin',a,b,i/cols,y1+1.25,.10,2.6,'steel',out=.19,depth=.2)
def wing(n,x,z,w,d,h,style,yaw=0,r=0):
 outline=round_rect(0,0,w,d,r,5) if r else [(-w/2,-d/2),(w/2,-d/2),(w/2,d/2),(-w/2,d/2)]
 # Use clockwise perimeter so outward facade normal is to the right.
 if sum(outline[i][0]*outline[(i+1)%len(outline)][1]-outline[(i+1)%len(outline)][0]*outline[i][1] for i in range(len(outline)))<0:outline.reverse()
 outline=[(x+math.cos(yaw)*xx+math.sin(yaw)*zz,z-math.sin(yaw)*xx+math.cos(yaw)*zz) for xx,zz in outline]
 prism2(n+' closed mass',outline,12.42,h,'chalk' if style=='ph' else 'limestone');facade(n,outline,12.5,h,style);roof(n,outline,h)
 return outline

def plant(x,z,y=12.5,h=6):
 tube('weathered palm trunk',[(x,y,z),(x+.15,y+h*.5,z),(x+.4,y+h,z)],.17,'trunk')
 for i in range(9):
  a=i*math.tau/9;pts=[]
  for j in range(6):
   t=j/5;pts.append((x+.4+math.cos(a)*3.3*t,y+h+1.2*math.sin(t*math.pi)-1.9*t*t,z+math.sin(a)*3.3*t))
  for j in range(5):
   a0=Vector(pts[j]);a1=Vector(pts[j+1]);off=Vector((-math.sin(a),0,math.cos(a)))*(.48*math.sin((j+.7)/6*math.pi))
   M('palm frond',[tuple(a0-off),tuple(a0+off),tuple(a1+off*.7),tuple(a1-off*.7)],[(0,1,2,3)],'leaf')
def roof_equipment(x,z,y):
 D('rooftop mechanical housing',(x,y+1.1,z),(4,2.1,3),'concrete')
 for dz in [-.9,-.3,.3,.9]:D('equipment grille',(x-2.05,y+1.2,z+dz),(.10,1.35,.12),'dark')
 D('duct',(x+3,y+.6,z),(2.5,1.1,1.2),'steel')
def portal(n,x,z,yaw=0,width=10,depth=5):
 # Clear 5 m auto-opening door retained at the original position.
 with context(uid(n),origin=(x,0,z),yaw=yaw):
  B('entrance canopy',(0,5.1,depth/2),(width,.6,depth),'steel')
  for xx in [-width/2+.45,width/2-.45]:B('canopy pier',(xx,2.4,depth-.6),(.6,4.8,.6),'bronze')
  D('canopy light',(0,4.76,depth/2),(width-.8,.08,depth-.7),'warmneon')

# PLANET HOLLYWOOD: broad folded skyline, rounded ends and projecting lower wings.
hotel='Planet Hollywood'
wing('north folded tower',160,199,17,48,98,'ph',yaw=-.20,r=4)
wing('south folded tower',159,242,17,46,98,'ph',yaw=.24,r=4)
wing('central hinge',163,220,20,15,99,'ph',r=3)
wing('north projecting suite wing',139,201,42,13,60,'ph',r=5)
wing('south projecting suite wing',139,250,40,13,63,'ph',r=5)
# Roof lettering follows the two folded faces (not a floating generic signboard).
sign('planet',(145.9,99.7,197),3.7,yaw=-math.pi/2-.20,m='gold')
sign('hollywood',(145.2,99.7,241),3.7,yaw=-math.pi/2+.24,m='gold')
for x,z in [(160,181),(165,211),(164,230),(153,259)]:roof_equipment(x,z,98.5)
# Large paired concert-banner recesses are part of the actual massing. Original,
# faded fictional posters fit the apocalypse without embedding copyrighted ads.
for x,z,angle,title in [(145.2,185,-.20,'AFTERLIGHT'),(147.3,235,.24,'THE LAST SHOW')]:
 a=(x+math.sin(angle)*8,z-8*math.cos(angle));b=(x-math.sin(angle)*8,z+8*math.cos(angle))
 # Ensure face normal toward west.
 a,b=b,a
 facebox('banner shadow surround',a,b,.5,69,16,38,'bronze',depth=.4,out=.6)
 facebox('weathered show banner',a,b,.5,69,15.4,37.4,'screen',depth=.12,out=.85)
 for j in range(7):facebox('faded banner rays',a,b,.5,57+j*3.8,13-j*.9,.17,'pink',out=.94,depth=.03)
 sign(title,(x-1.07*math.cos(angle),69,z-1.07*math.sin(angle)),1.15,yaw=-math.pi/2-angle,m='chalk')
 sign('LIVE',(x-1.07*math.cos(angle),64,z-1.07*math.sin(angle)),2.6,yaw=-math.pi/2-angle,m='warmneon')
# Existing first floor remains intact, articulated outside by its wave-like metal fascia.
for i in range(50):
 z0=173+i*101/50;z1=173+(i+1)*101/50
 x0=64.05-.85*math.sin((z0-173)*math.tau/35);x1=64.05-.85*math.sin((z1-173)*math.tau/35)
 a=(x1,z1);b=(x0,z0);peak=11.9+1.0*math.sin((z0-173)*math.tau/35)
 facebox('undulating metal retail screen',a,b,.5,(peak+5)/2,math.dist(a,b)+.05,peak-5,'steel',depth=.18,out=.02)
 for yy in [5.2,peak-.25]:facebox('wave edge trim',a,b,.5,yy,math.dist(a,b)+.07,.23,'chalk',out=.18,depth=.26)
 # Real perforations implied by inset dark square cells and raised horizontal ribs.
 for row in range(6):
  for col in range(2):facebox('screen perforation',a,b,(col+.5)/2,5.9+row*.85,.48,.30,'dark',depth=.035,out=.14)
 if i%6==0 and abs((z0+z1)/2-218)>5:facebox('street display',a,b,.5,3.05,1.7,3.8,'nightglass',out=.25,depth=.12)
for z in [184,204,237,258]:
 D('retail LED surround',(62.8,8.1,z),(.32,4.7,9),'dark');D('faded retail display',(62.59,8.1,z),(.06,4.2,8.5),'screen')
 sign('MIRACLE MILE',(62.51,8.0,z),.59,m='chalk')
portal('Strip entrance',65,218,yaw=-math.pi/2,width=14,depth=5.5)
sign('planet hollywood',(59.3,5.15,218),.75,m='gold')
portal('Miracle Mile south entrance',174,274,width=14,depth=4)
sign('MIRACLE MILE SHOPS',(174,5.3,278.1),.75,yaw=0,m='warmneon')
# Low rooftop leisure deck, two pools, glass rails and abandoned cabanas.
D('pool terrace',(102,12.62,224),(67,.35,84),'sand')
for z in [202,246]:
 D('pool coping',(96,12.90,z),(22,.28,18),'chalk',bevel=.5);D('stagnant pool',(96,13.06,z),(20.6,.035,16.6),'pool',bevel=.45)
 for dz in [-10,10]:
  for x in [83,90,97,104]:
   D('pool chaise',(x,13.05,z+dz),(1.2,.45,2.5),'chalk');D('chaise cushion',(x,13.31,z+dz),(.95,.12,2.15),'dark')
 for x in [113,122]:
  D('cabana roof',(x,15.5,z+8),(5,.15,5),'chalk')
  for dx in [-2.2,2.2]:
   for dz in [-2.2,2.2]:D('cabana frame',(x+dx,14,z+8+dz),(.12,3,.12),'bronze')
 for x,dz in [(77,-13),(116,-12),(80,13)]:plant(x,z+dz,12.8,5)
for z in range(177,270,4):D('pool terrace baluster',(68,13.5,z),(.08,1.4,.08),'steel')
D('pool terrace toprail',(68,14.2,223),(.15,.12,94),'steel')
# South curb pylon; offsets clear of the existing doors and pavement routes.
B('pylon foundation',(69,1,266),(2,2,2),'concrete');B('pylon mast',(69,11,266),(1.1,21,1.1),'steel')
D('pylon LED',(68.5,20,266),(.65,11,6),'dark');sign('ph',(68.1,21,266),2.4,m='gold');sign('PLANET',(68.1,18.7,266),.7,m='chalk')

# FLAMINGO: connected wings enclose a compressed landscaped roof courtyard.
print('Planet Hollywood geometry built',flush=True)
hotel='Flamingo'
wing('north garden wing',148,-251,96,14,66,'flamingo')
wing('south garden wing',160,-222.3,72,14,64,'flamingo')
wing('east connecting wing',188,-237,16,43,68,'flamingo')
wing('Strip-side lower wing',103,-238,18,37,43,'flamingo')
# Broad cream end piers, central ribs and flush roof crowns are characteristic.
for x,z,w,d,h in [(101,-251,5,15,67),(125,-222.3,5,15,65),(188,-257,17,4,69),(188,-217,17,4,69),(104,-238,19,4,44)]:B('cream end core',(x,(12.4+h)/2,z),(w,h-12.4,d),'chalk')
for x,z in [(122,-259),(147,-259),(170,-259),(143,-214.8),(171,-214.8)]:D('broad facade pier',(x,39.6,z),(1.35,53.5,.65),'chalk')
for x,z,h in [(112,-250,66.5),(143,-250,66.5),(170,-222,64.5)]:roof_equipment(x,z,h)
sign('Flamingo',(97.8,65,-251),1.7,m='pinkneon',italic=True)
sign('Flamingo',(152,65.7,-259.4),2.25,yaw=math.pi,m='pinkneon',italic=True)
sign('Flamingo',(159,63.7,-214.95),2.3,yaw=0,m='pinkneon',italic=True)
# Pink and cream low casino frontage, tiered portico, familiar feather/petal pylon.
for z in list(range(-256,-239,4))+list(range(-232,-215,4)):
 D('pink ground-floor bay',(89.63,4,z),(.20,7.5,3.6),'pink');D('dark street glazing',(89.49,2.7,z),(.06,4.1,3.0),'nightglass')
for yy,w in [(9.0,1.4),(10.8,1.7),(12.3,1.8)]:D('layered casino cornice',(89.5,yy,-237),(w,.45,44.8),'chalk')
portal('Flamingo Strip entrance',90,-237,yaw=-math.pi/2,width=13,depth=5)
sign('Flamingo',(84.5,5.2,-237),1.1,m='pinkneon',italic=True)
portal('Flamingo south lobby',145,-215,width=11,depth=3.8)
# The famous Strip entrance is a sculpted pink/gold lotus marquee, not a balloon.
# Elliptical bulb panels and splayed metal petals rise directly above the canopy.
for i in range(18):
 a0=-math.pi/2+i*math.pi/18;a1=-math.pi/2+(i+1)*math.pi/18;vs=[]
 for j in range(25):
  t=-math.pi/2+j*math.pi/24
  for a in [a0,a1]:vs.append((87-6*math.cos(t)*math.cos(a),13+6.8*math.sin(t),-237+7.5*math.cos(t)*math.sin(a)))
 M('lotus bulb fluted panel',vs,[(2*j,2*j+1,2*j+3,2*j+2) for j in range(24)],'gold' if i%4==0 else 'pink')
 tube('lotus silver seam',[(87-6.035*math.cos(-math.pi/2+j*math.pi/32)*math.cos(a0),13+6.835*math.sin(-math.pi/2+j*math.pi/32),-237+7.54*math.cos(-math.pi/2+j*math.pi/32)*math.sin(a0)) for j in range(33)],.10,'chalk')
for side in [-1,1]:
 for k in range(4):
  # Curved lanceolate petals fan sideways/upward from the foot of the central bulb.
  root=Vector((87,6.8,-237+side*2.5));tip=Vector((87.5,11+k*3.1,-237+side*(14-k*2.6)))
  verts=[];edges=[[],[]]
  for j in range(25):
   t=j/24;c=root.lerp(tip,t)+Vector((-2.6*math.sin(math.pi*t),-1.2*math.sin(math.pi*t),side*2.0*math.sin(math.pi*t)))
   wide=math.sin(math.pi*t)*(2.0 if k<2 else 1.5)
   for side2 in [-1,1]:
    p=c+Vector((0,wide*side2,-side*wide*side2*.4));verts.append(tuple(p));edges[(side2+1)//2].append(tuple(p))
  M('splayed lotus petal',verts,[(2*j,2*j+1,2*j+3,2*j+2) for j in range(24)],'pink' if k%2 else 'gold')
  for edge in edges:tube('petal silver edge',edge,.11,'chalk')
  for j in range(3,23):tube('petal flute',[verts[2*j],verts[2*j+1]],.03,'bronze',6)
# Original bold cursive lettering is converted to geometry in the saved level.
sign('Flamingo',(85.3,21.5,-237),3.6,m='pinkneon',italic=True)
for z in [-242,-237,-232]:tube('marquee sign bracket',[(87,17.8,z),(87,23,z)],.08,'steel')
for z in [-252,-222]:plant(83,z,.1,7.5)
# Recessed northern frontage panels replace the otherwise bare podium wall.
for x in range(102,194,6):
 D('north casino cladding',(x,5.5,-259.32),(5.6,10.6,.15),'limestone')
 D('north recessed glazing',(x,4,-259.43),(4.8,5.5,.10),'nightglass')
for yy in [1,9.1,11.7]:D('north frontage belt',(145,yy,-259.5),(110,.35,.5),'chalk')
# Courtyard greens and irregular pool silhouette above the original sealed casino.
D('courtyard terrace',(150,12.55,-237),(70,.25,15),'sand')
outline=[(127,-242),(141,-243),(151,-240),(170,-242),(177,-237),(166,-234),(147,-235),(136,-231),(126,-233)]
prism2('curving garden pool coping',outline,12.7,12.95,'chalk',False)
prism2('garden pool water',[(150+(x-150)*.94,-237+(z+237)*.83) for x,z in outline],12.97,13.01,'pool',False)
for x,z in [(118,-239),(123,-232),(148,-231),(161,-242),(174,-234),(180,-243)]:plant(x,z,12.8,4.6)
for x in [132,144,156,169]:
 D('garden hedge',(x,13.3,-230.5),(6,1.1,1.6),'leaf',bevel=.3)

# HORSESHOE RESORT TOWER: stepped twin slabs, champagne piers, blue glazing crown.
print('Flamingo geometry built',flush=True)
hotel='Horseshoe'
wing('north Resort Tower slab',109,-131,22,29,76,'horseshoe')
wing('south Resort Tower slab',115,-105,22,28,71,'horseshoe')
# Setback joint and broad solid ends provide the massing; not a wall of identical windows.
for x,z,w,d,h in [(109,-145,23,3.2,79),(112,-117.5,23,3.0,79),(115,-91.6,23,3.1,74)]:
 B('champagne service core',(x,(12.4+h)/2,z),(w,h-12.4,d),'limestone')
for x,z,h in [(97.25,-143,76),(97.25,-131,76),(97.25,-119,76),(103.2,-115,71),(103.2,-103,71),(103.2,-93,71)]:
 D('projecting structural pier',(x,(15+h)/2,z),(1.7,h-15,1.0),'chalk')
 # Flared plinths under the facade match the reference and meet the podium roof.
 vs=[(x-2.7,12.45,z-1),(x+1.2,12.45,z-1),(x+1.2,12.45,z+1),(x-2.7,12.45,z+1),(x-.6,19,z-.5),(x+.6,19,z-.5),(x+.6,19,z+.5),(x-.6,19,z+.5)]
 M('tapered pier base',vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'chalk')
for z in [-140,-130,-121]:D('upper recessed frame',(96.3,72,z),(1.2,5.5,.45),'limestone')
for i,c in enumerate('HORSESHOE'):sign(c,(97.26,75-i*2.6,-145.0),2.25,m='gold')
sign('HORSESHOE',(109,71.8,-146.7),1.4,yaw=math.pi,m='gold')
for x,z,y in [(107,-131,76.6),(115,-104,71.6)]:roof_equipment(x,z,y)
# Wide arched glass porte-cochere opening onto Flamingo Road.
portal('north portico',110,-147,yaw=math.pi,width=15,depth=5.6)
# Barrel roof modeled as a shell with glass panels and visible curved ribs.
for j in range(16):
 t0=j*math.pi/16;t1=(j+1)*math.pi/16
 vs=[]
 for z in [-153.2,-147.2]:
  for t in [t0,t1]:vs.append((110+6.8*math.cos(t),5.3+3.5*math.sin(t),z))
 M('barrel canopy glass',vs,[(0,1,3,2)],'skyglass')
for z in [-153.25,-151.2,-149.2,-147.15]:tube('barrel canopy rib',[(110+6.8*math.cos(i*math.pi/24),5.3+3.5*math.sin(i*math.pi/24),z) for i in range(25)],.09,'bronze')
sign('HORSESHOE',(110,5.3,-153.7),1,yaw=math.pi,m='gold')
# Casino base: limestone pilasters, shallow blue infill and gold fascia; south
# connector to Paris stays completely open inside the existing door envelope.
for z in range(-142,-87,5):
 D('casino limestone pilaster',(91.64,5.5,z),(.4,10.7,.48),'limestone');D('casino blue panel',(91.73,6,z+2),(.12,6.2,3.4),'blueglass')
for yy in [1.0,9.4,11.6]:D('casino facade belt',(91.6,yy,-116),(.7,.35,62),'limestone')
for z in [-134,-109]:sign('HORSESHOE',(91.1,10,z),.65,m='gold')
# Relief horseshoes modeled as open curved metal, visible even when signs are off.
for z in [-132,-108]:
 tube('horseshoe emblem',[(91.15,6.7+1.6*math.sin(math.pi*.78+i*math.pi*1.44/32),z+1.4*math.cos(math.pi*.78+i*math.pi*1.44/32)) for i in range(33)],.15,'gold')

# Bake text once; new objects retain deterministic, editable semantic names.
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
for ob in labels:
 me=bpy.data.meshes.new_from_object(ob.evaluated_get(dg));o=bpy.data.objects.new(ob.name+' glyphs',me);scene.collection.objects.link(o);o.matrix_world=ob.matrix_world.copy()
bpy.data.batch_remove(labels)
# Existing UVs remain unchanged. New concrete/metal shapes get world-planar UVs
# for future surface treatment and correct export tangents.
for ob in bpy.data.objects:
 if ob.type!='MESH' or not ob.name.startswith(P):continue
 uv=ob.data.uv_layers.new(name='ExteriorUV')
 for poly in ob.data.polygons:
  normal=poly.normal;axis=max(range(3),key=lambda i:abs(normal[i]));axes=[i for i in range(3) if i!=axis]
  for li in poly.loop_indices:
   p=ob.matrix_world@ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(p[axes[0]]*.2,p[axes[1]]*.2)
addition=level.mesh_level_json();data['colliders']+=addition['colliders']
Path('build/exteriors/addition.mesh-level.json').write_text(json.dumps(addition,indent=2))
Path('build/exteriors/removed.json').write_text(json.dumps(removed,indent=2))
Path('build/level/vegas.mesh-level.json').write_text(json.dumps(data,indent=2))
orient_closed_solids();bpy.context.scene['resort_exteriors_v1']=True;bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath('build/level/vegas.blend'))
print('EXTERIORS COMPLETE:',len(removed),'old parts replaced;',serial,'new parts;',len(addition['colliders']),'new silhouettes',flush=True)
if '--export' in sys.argv:
 from visibility_export import export_visibility
 export_visibility('build/level/vegas.glb')
