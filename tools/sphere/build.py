"""Reference-led Sphere architecture. Metres, +Y up, north=-Z.
Blender exports material batches; collision excludes seats and decorative trims.
"""
import json,math
from pathlib import Path
from collections import defaultdict
import numpy as np
import mapbox_earcut as earcut
from shapely.geometry import Point,Polygon,box as polygon_box
from shapely.ops import unary_union
OUT=Path('build/sphere');OUT.mkdir(exist_ok=True)
CENTER=[983.04,0,-583.71]
R=516*.3048/2;TOP=366*.3048;CY=TOP-R;MAIN=6.085
M={
 'liner':('#080b10',0,1,0),'shell':('#ffffff',0,1,0),'screen':('#ffffff',0,1,0),
 'black':('#11171c',.35,.5,0),'terrazzo':('#161e26',.25,.26,0),'white':('#bbc7ce',.25,.38,0),
 'metal':('#555f68',.75,.3,0),'dark-metal':('#1c2830',.55,.4,0),'glass':('#729baa',.2,.2,0),
 'concrete':('#777c80',.05,.85,0),'tread':('#3b424a',.45,.55,0),'seat':('#222c3e',0,.8,0),
 'blue-light':('#54bfdd',0,.3,1.2),'warm-light':('#ffe9b5',0,.3,1.5),'white-light':('#cceeff',0,.3,1.7),
 'wood':('#6a4831',0,.5,0),'plaza':('#94948d',0,.8,0),'yellow':('#d9b962',.1,.5,0),
}
parts={'exterior':defaultdict(lambda:dict(vertices=[],faces=[],uv=[])),'interior':defaultdict(lambda:dict(vertices=[],faces=[],uv=[]))}
coll={k:dict(vertices=[],indices=[]) for k in parts};signs=[];seats=[];routes=[];lights=[]
section='exterior'
def mesh(mat,v,f,solid=False,uv=None):
 g=parts[section][mat];n=len(g['vertices']);g['vertices']+=v;g['faces'] += [[n+i for i in t] for t in f];g['uv']+=uv or [[p[0]/3,p[2]/3] for p in v]
 if solid:
  c=coll[section];n=len(c['vertices'])//3;c['vertices'] += [q for p in v for q in p];c['indices'] += [n+i for t in f for i in t]
def quad(mat,p,solid=False):mesh(mat,p,[[0,1,2],[0,2,3]],solid)
def poly(poly,y,depth,mat,solid=False):
 if poly.is_empty:return
 if poly.geom_type!='Polygon':
  for p in poly.geoms:poly_(p,y,depth,mat,solid)
  return
 rings=[list(poly.exterior.coords)[:-1],*[list(r.coords)[:-1] for r in poly.interiors]]
 arr=np.array([p for ring in rings for p in ring],dtype=np.float64);ends=np.cumsum([len(r) for r in rings],dtype=np.uint32)
 inds=earcut.triangulate_float64(arr,ends).reshape(-1,3)
 v=[[float(x),y,float(z)] for x,z in arr]
 faces=[]
 for a,b,c in inds:
  # Ensure all top normals point upward.
  pa,pb,pc=arr[a],arr[b],arr[c];area=(pb[0]-pa[0])*(pc[1]-pa[1])-(pb[1]-pa[1])*(pc[0]-pa[0])
  faces.append([int(a),int(c),int(b)] if area>0 else [int(a),int(b),int(c)])
 mesh(mat,v,faces,solid)
 mesh(mat,[[x,y-depth,z] for x,_,z in v],[f[::-1] for f in faces],solid)
 for ring in rings:
  for (x,z),(xx,zz) in zip(ring,ring[1:]+ring[:1]):quad(mat,[[x,y,z],[xx,y,zz],[xx,y-depth,zz],[x,y-depth,z]],solid)
poly_=poly

def box(name,p,size,mat,solid=False,yaw=0):
 x,y,z=p;w,h,d=[v/2 for v in size];c,s=math.cos(yaw),math.sin(yaw)
 v=[[x+xx*c+zz*s,y+yy,z-xx*s+zz*c] for xx,yy,zz in [(-w,-h,-d),(w,-h,-d),(w,h,-d),(-w,h,-d),(-w,-h,d),(w,-h,d),(w,h,d),(-w,h,d)]]
 mesh(mat,v,[[0,2,1],[0,3,2],[4,5,6],[4,6,7],[0,4,7],[0,7,3],[1,2,6],[1,6,5],[3,7,6],[3,6,2],[0,1,5],[0,5,4]],solid)
def beam(a,b,width,depth,mat,solid=False):
 a,b=np.array(a,float),np.array(b,float);d=b-a;d/=np.linalg.norm(d);side=np.cross(d,[0,1,0])
 if np.linalg.norm(side)<.01:side=np.array([1.,0,0])
 side/=np.linalg.norm(side);up=np.cross(side,d)
 v=[(p+side*s*width/2+up*t*depth/2).tolist() for p in [a,b] for s,t in [(-1,-1),(1,-1),(1,1),(-1,1)]]
 mesh(mat,v,[[0,2,1],[0,3,2],[4,5,6],[4,6,7],[0,4,7],[0,7,3],[1,2,6],[1,6,5],[3,7,6],[3,6,2],[0,1,5],[0,5,4]],solid)
def cylinder(x,z,y0,y1,r0,r1,mat,solid=False,n=24):
 v=[[x+r*math.sin(i*2*math.pi/n),y,z+r*math.cos(i*2*math.pi/n)] for y,r in [(y0,r0),(y1,r1)] for i in range(n)]
 f=[]
 for i in range(n):j=(i+1)%n;f.extend([[i,j,n+j],[i,n+j,n+i]])
 for i in range(1,n-1):f.extend([[0,i+1,i],[n,n+i,n+i+1]])
 mesh(mat,v,f,solid)
def arc_poly(r0,r1,a0,a1,cx=0,cz=0,n=64):
 return Polygon([(cx+r*math.sin(a),cz-r*math.cos(a)) for r,ang in [(r1,np.linspace(a0,a1,n)),(r0,np.linspace(a1,a0,n))] for a in ang])
def arc(r,y0,y1,a0,a1,mat,cx=0,cz=0,solid=False,n=96):
 for a,b in zip(np.linspace(a0,a1,n+1)[:-1],np.linspace(a0,a1,n+1)[1:]):
  quad(mat,[[cx+r*math.sin(a),y0,cz-r*math.cos(a)],[cx+r*math.sin(b),y0,cz-r*math.cos(b)],[cx+r*math.sin(b),y1,cz-r*math.cos(b)],[cx+r*math.sin(a),y1,cz-r*math.cos(a)]],solid)
def railing(r,y,a0,a1,cx=0,cz=0,glass=True):
 arc(r,y+.10,y+1.14,a0,a1,'glass' if glass else 'dark-metal',cx,cz,True,n=32)
 for hh in [.10,1.15]:poly(arc_poly(r-.035,r+.035,a0,a1,cx,cz),y+hh,.06,'metal')
 for a in np.linspace(a0,a1,max(2,int((a1-a0)*r/2.4))):cylinder(cx+r*math.sin(a),cz-r*math.cos(a),y,y+1.2,.035,.035,'metal',False,6)
def torus(p,r,thick,mat,orient='horizontal',n=64,m=6):
 v=[]
 for i in range(n+1):
  a=i*2*math.pi/n
  for j in range(m):
   b=j*2*math.pi/m;rr=r+thick*math.cos(b)
   x,y,z=rr*math.sin(a),thick*math.sin(b),rr*math.cos(a)
   if orient=='vertical':y,z=z,y
   v.append([p[0]+x,p[1]+y,p[2]+z])
 f=[]
 for i in range(n):
  for j in range(m):a=i*m+j;b=i*m+(j+1)%m;c=b+m;d=a+m;f.extend([[a,b,c],[a,c,d]])
 mesh(mat,v,f)
def sign(text,p,yaw,width=5,height=.7):signs.append(dict(text=text,p=list(p),yaw=yaw,width=width,height=height,section=section))
def route(name,points):routes.append(dict(name=name,points=points))
def escalator(name,a,b,width=2.3):
 # Detailed stair surface; one smooth, closed wedge collider per flight.
 ax,ay,az=a;bx,by,bz=b;dx,dz=bx-ax,bz-az;length=math.hypot(dx,dz);nx,nz=dz/length,-dx/length;n=math.ceil((by-ay)/.16)
 yawr=math.atan2(nx,nz)
 v=[[x+side*nx*width/2,y-.15,z+side*nz*width/2] for x,y,z in [a,b] for side in [-1,1]]
 quad('tread',[v[0],v[2],v[3],v[1]],True)
 for k in range(n):
  t=(k+.5)/n;yy=ay+(by-ay)*(k+1)/n
  box(name,[ax+dx*t,yy-.075,az+dz*t],[width,.15,length/n+.012],'tread',False,math.atan2(dx,dz))
  beam([ax+dx*(k+1)/n-nx*width/2,yy+.009,az+dz*(k+1)/n-nz*width/2],[ax+dx*(k+1)/n+nx*width/2,yy+.009,az+dz*(k+1)/n+nz*width/2],.035,.018,'yellow')
 for side in [-1,1]:
  aa=[ax+nx*side*(width/2+.09),ay+.03,az+nz*side*(width/2+.09)];bb=[bx+nx*side*(width/2+.09),by+.03,bz+nz*side*(width/2+.09)]
  quad('glass',[aa,bb,[bb[0],bb[1]+1,bb[2]],[aa[0],aa[1]+1,aa[2]]],True)
  beam([aa[0],aa[1]+1.05,aa[2]],[bb[0],bb[1]+1.05,bb[2]],.12,.10,'black')
  beam([aa[0],aa[1]+.12,aa[2]],[bb[0],bb[1]+.12,bb[2]],.09,.055,'blue-light')
 route(name,[a,b])

# EXTERIOR: independent LED skin and a dark ribbed base with real openings.
phiN,thetaN=192,80;thetaMax=math.acos((12-CY)/R)
v=[];uv=[]
for j in range(thetaN+1):
 theta=j/thetaN*thetaMax
 for i in range(phiN+1):
  phi=-math.pi+i/phiN*2*math.pi
  v.append([R*math.sin(theta)*math.sin(phi),CY+R*math.cos(theta),R*math.sin(theta)*math.cos(phi)])
  uv.append([i/phiN,1-theta/math.pi])
f=[]
for j in range(thetaN):
 for i in range(phiN):a=j*(phiN+1)+i;b=a+1;c=b+phiN+1;d=a+phiN+1;f.extend([[a,d,c],[a,c,b]])
mesh('shell',v,f,False,uv)
section='interior'
mesh('liner',[[x*.996,CY+(y-CY)*.996,z*.996] for x,y,z in v],[t[::-1] for t in f],False,uv)
section='exterior'
# Convex base walls, with entrance bays subtracted by segment rather than hidden doors.
entranceAngles=[(-1.08,6.085),(math.pi/2,.18),(-.55,.18)]
for i in range(192):
 a=-math.pi+i/192*2*math.pi;b=a+2*math.pi/192;mid=(a+b)/2
 hole=next((y for ang,y in entranceAngles if abs(mid-ang)<.08),None)
 if hole is None:arc(75.4,.18,12,a,b,'dark-metal',solid=True,n=1)
 else:
  if hole>.2:arc(75.4,.18,hole,a,b,'dark-metal',solid=True,n=1)
  arc(75.4,hole+3.8,12,a,b,'dark-metal',solid=True,n=1)
 if hole is None:beam([75.6*math.sin(mid),.2,-75.6*math.cos(mid)],[75.6*math.sin(mid),11.95,-75.6*math.cos(mid)],.075,.075,'metal')
poly(Point(0,0).buffer(76,96),.18,.4,'concrete',True)
poly(arc_poly(73,76,-math.pi,math.pi),12,.3,'dark-metal',True)
# Local plaza respects the surrounding surveyed roads (inside the source building footprint).
poly(Point(0,0).buffer(86,96).difference(Point(0,0).buffer(76,96)),.18,.25,'plaza',True)
# Bridge vestibule: exact surveyed endpoint, direction retained.
BP=[905.7057821369358-CENTER[0],6.085,-624.5134752991656-CENTER[2]]
D=[.8834336052311916,.468556362829723];N=[D[1],-D[0]]
end=[BP[0]+D[0]*20,MAIN,BP[2]+D[1]*20]
for y in [MAIN,MAIN+4]:
 q=[[p[0]+N[0]*s*3.7,y,p[2]+N[1]*s*3.7] for p,s in [(BP,-1),(end,-1),(end,1),(BP,1)]]
 poly(Polygon([(p[0],p[2]) for p in q]),y,.18,'terrazzo' if y==MAIN else 'metal',True)
for side in [-1,1]:
 a=[BP[0]+N[0]*side*3.7,MAIN,BP[2]+N[1]*side*3.7];b=[end[0]+N[0]*side*3.7,MAIN,end[2]+N[1]*side*3.7]
 quad('glass',[a,b,[b[0],MAIN+4,b[2]],[a[0],MAIN+4,a[2]]],True)
 for k in range(6):beam([a[0]+(b[0]-a[0])*k/5,MAIN,a[2]+(b[2]-a[2])*k/5],[a[0]+(b[0]-a[0])*k/5,MAIN+4,a[2]+(b[2]-a[2])*k/5],.10,.10,'metal')
sign('SPHERE  /  VENETIAN BRIDGE',[BP[0],MAIN+3.4,BP[2]],math.atan2(-D[0],-D[1]),6,.5)
route('Bridge threshold to atrium',[BP,end,[-45,MAIN,-42],[-29,MAIN,-42],[-20,MAIN,-51]])
portals=[dict(name='Venetian bridge',p=BP,direction=D,width=5.5,height=3.5)]
# East plaza: glazed, multi-bay entrance with a deep metal canopy.
for z in [-12,-6,0,6,12]:
 box('glazed plaza bay',[76,2.7,z],[.12,5,5.6],'glass',abs(z)>4)
 box('plaza mullion',[76,3,z+2.9],[.20,6,.16],'metal')
box('plaza canopy',[79,6.1,0],[13,.4,33],'metal',True)
for z in [-14,14]:cylinder(82,z,.2,6,.16,.16,'metal',True)
for z in range(-14,15,2):box('canopy linear light',[79,5.87,z],[10,.04,.035],'white-light')
sign('sphere',[82.1,4.4,0],math.pi/2,10,1.4)
portals.append(dict(name='Plaza Entry',p=[76,.18,0],direction=[-1,0],width=5.5,height=3.5))
# West ground entry and a short direct ascent to the main atrium.
west=[75.4*math.sin(-.55),.18,-75.4*math.cos(-.55)]
portals.append(dict(name='West Entry',p=west,direction=[math.sin(.55),math.cos(.55)],width=5.5,height=3.5))
sign('WEST ENTRY',[west[0],4.4,west[2]],-.55+math.pi,6,.65)

section='interior'
# Main floor has voids for the two ground-to-main escalator banks.
holes=unary_union([polygon_box(51,-7,74,7),polygon_box(-42,-65,-34,-46)])
main=Point(0,0).buffer(73.4,96).difference(holes)
poly(main,MAIN,.4,'terrazzo',True)
for z in [-2.1,2.1]:escalator('Plaza escalator',[73,.18,z],[52,MAIN,z],2.5)
box('plaza landing',[50,MAIN-.2,0],[5,.4,14],'terrazzo',True)
route('Plaza doors to atrium',[[80,.18,0],[75,.18,2.1],[73,.18,2.1],[52,MAIN,2.1],[47,MAIN,5],[58,MAIN,-20],[42,MAIN,-45],[20,MAIN,-51]])
for x in [-40,-36]:escalator('West entry escalator',[x,.18,-64],[x,MAIN,-47],2.5)
box('west landing',[-38,MAIN-.2,-44],[10,.4,6],'terrazzo',True)
route('West entry approach',[west,[-40,.18,-64]])
# Ribbed auditorium wall at the inner edge of the atrium; portals open to both side aisles.
for a0,a1 in [(-1.04,-.91),(-.83,-.46),(-.38,-.05),(.05,.38),(.46,.83),(.91,1.04)]:
 arc(47,MAIN,19,a0,a1,'black',0,28,True,n=20)
 for a in np.arange(a0,a1,.012):beam([47*math.sin(a),MAIN,28-47*math.cos(a)],[47*math.sin(a),19,28-47*math.cos(a)],.04,.06,'metal')
# Monumental columns, flared capitals and glowing collars.
for x,z in [(-50,-40),(-34,-57),(-18,-64),(18,-64),(34,-57),(50,-40)]:
 cylinder(x,z,MAIN,28,.85,.68,'white',True)
 cylinder(x,z,28,31.1,.68,2.0,'white')
 torus([x,28.1,z],.75,.11,'white-light')
 cylinder(x,z,MAIN,MAIN+.26,.94,.94,'dark-metal')
 lights.append([x,13,z])
# Sweeping balcony bands; front edges vary smoothly, as in the photographs.
for level,y in enumerate([15,24]):
 balcony=arc_poly(62,73.3,-1.13,1.13)
 # Four central flights emerge onto open landings (not through a solid slab).
 if level==0:balcony=balcony.difference(polygon_box(-16,-68,16,-43))
 poly(balcony,y,.55,'white',True)
 poly(balcony.buffer(-.035),y+.035,.025,'terrazzo')
 
 for aa,bb in [(-1.13,-.22),(.22,.72),(.82,1.13)]:railing(62,y,aa,bb)
 arc(62,y-.3,y-.12,-1.13,1.13,'blue-light')
 arc(72.9,y+.25,y+4.4,-1.13,1.13,'black',solid=True)
 for a in np.linspace(-1.1,1.1,32):
  x,z=69*math.sin(a),-69*math.cos(a);cylinder(x,z,y-.64,y-.58,.075,.075,'white-light',False,8)
# Four central escalators: two to terrace, two onward to upper gallery.
for x in [-5.5,-9.0]:escalator('Atrium to Terrace',[x,MAIN,-43],[x,15,-68],2.6)
for x in [5.5,9.0]:escalator('Terrace to Gallery',[x,15,-68],[x,24,-43],2.6)
box('terrace escalator landing',[0,14.725,-69.7],[30,.55,3.6],'white',True)
box('gallery arrival',[7.2,23.73,-40.3],[9,.55,6],'white',True)
box('gallery crosswalk',[24,23.73,-41.5],[40,.55,4],'white',True)
# A side gallery route to the terrace; no unexplained stair termination.
box('gallery connector',[43,23.73,-49.5],[4,.55,19],'white',True)
route('Upper gallery connector',[[9,24,-43],[9,24,-41.5],[43,24,-41.5],[43,24,-53]])
# Sealed dark ceiling above the main atrium, with curved soffit rims.
poly(arc_poly(52,74,-1.28,1.28),31,.38,'black',True)
for r in [55,62,72]:arc(r,30.7,31,-1.2,1.2,'white')
# Suspended ring installation and fine suspension cables.
for k in range(26):
 t=k/25;x=-40+80*t;z=-48+7*math.sin(t*math.pi*2);y=18+5*math.sin(t*math.pi*2+.3)
 torus([x,y,z],1.15+.25*math.sin(k),.13,'metal','vertical',32)
 torus([x,y,z-.07],1.12+.25*math.sin(k),.035,'blue-light','vertical',32)
 beam([x,y+1.4,z],[x,30.5,z],.018,.018,'dark-metal')
# Concession fronts: curved wall, framed menus, counters, shelves, warm uplighting.
for k,a in enumerate([-.78,-.46,0,.46,.78]):
 x,z=69*math.sin(a),-69*math.cos(a);yaw=-a
 box('bar back',[x,MAIN+2.5,z],[9,5,.7],'black',True,yaw)
 for j in [-2.6,0,2.6]:
  xx=x+j*math.cos(a);zz=z+j*math.sin(a)
  box('menu',[xx,MAIN+3.1,zz+.4],[2.0,1.25,.06],'warm-light',False,yaw)
  for hh in [.7,1.35,2.0]:box('display shelves',[xx,MAIN+hh,zz+.2],[2.3,.05,.5],'wood',False,yaw)
 box('concession counter',[x,MAIN+.62,z+1.3],[9,1.24,1.4],'dark-metal',True,yaw)
 box('countertop',[x,MAIN+1.27,z+1.3],[9.2,.10,1.6],'metal',False,yaw)
 sign(['CANTINA','REFRESHMENTS','ATRIUM KITCHEN + BAR','TAPROOM','SPHERE MARKET'][k],[x,MAIN+4.35,z+.5],math.pi-a,8,.48)
# Expo pods with glowing displays and curved seat benches.
for x in [-26,26]:
 cylinder(x,-44,MAIN,MAIN+.24,2.0,2.0,'metal')
 cylinder(x,-44,MAIN+.24,MAIN+1.1,.65,.52,'black')
 cylinder(x,-44,MAIN+1.1,MAIN+1.15,.95,.95,'blue-light')
 sign('IMMERSIVE EXPERIENCE',[x,MAIN+1.6,-44],math.pi,2.6,.35)
for x in [-62,62]:
 box('recessed service frontage',[x,MAIN+1.7,-24],[4,3.4,.4],'black',True)
 sign('SECTIONS 100  /  AUDITORIUM',[x,MAIN+3.3,-26],math.pi,7,.55)
# The bowl is an enclosed volume, with its tier undersides hidden from the
# public atrium. Broad portals at either side open into the main seating aisles.
arc(61,MAIN,9.6,-.85,.85,'black',0,28,True)
arc(61,9.6,31.6,-1.075,1.075,'black',0,28,True)
for yy in [10.0,24.4,31.4]:arc(61.05,yy,yy+.05,-1.075,1.075,'blue-light',0,28)
for a in np.linspace(-.82,.82,43):
 cylinder(61.10*math.sin(a),28-61.10*math.cos(a),MAIN,31.5,.045,.045,'dark-metal',False,6)
for a in [-.96,.96]:sign('AUDITORIUM  /  SECTIONS 100—200',[61.2*math.sin(a),10.7,28-61.2*math.cos(a)],math.pi-a,7,.58)
route('Atrium to auditorium east aisle',[[20,MAIN,-51],[43,MAIN,-45],[56,MAIN,-30],[56,MAIN,-16],[42,MAIN,5],[20,MAIN,25],[0,MAIN,25]])
route('Atrium to auditorium west aisle',[[-20,MAIN,-51],[-29,MAIN,-42],[-43,MAIN,-42],[-56,MAIN,-30],[-56,MAIN,-16],[-42,MAIN,5],[-20,MAIN,25],[0,MAIN,25]])
# Auditorium tiers. Seats are shared runtime instances, never individual bodies.
TIERS=[(18,24,.92,MAIN,.45),(43,18,.88,18.7,.64),(62,12,.82,32.8,.75),(75,12,.75,44.4,.75)]
AISLES=[-1.035,-.70,-.35,0,.35,.70,1.035]
lastR,lastY=16,MAIN
for ti,(r0,n,run,y0,rise) in enumerate(TIERS):
 if ti:
  # Every aisle has a stepped connector across the gap between tiers.
  for a in AISLES:
   aa=[lastR*math.sin(a),lastY,28-lastR*math.cos(a)];bb=[r0*math.sin(a),y0,28-r0*math.cos(a)]
   escalator(f'Tier {ti} connecting aisle',aa,bb,1.6)
 for row in range(n):
  r=r0+row*run;y=y0+row*rise
  poly(arc_poly(r,r+run,-1.075,1.075,0,28,80),y,rise+.2,'black',True)
  # Aisle stairs split each row rise into comfortable 15–19 cm risers.
  if row<n-1:
   for a in AISLES:
    w=.9/r;steps=math.ceil(rise/.18)
    for k in range(steps):poly(arc_poly(r+run*k/steps,r+run*(k+1)/steps,a-w,a+w,0,28,2),y+rise*k/steps,.18,'tread',False)
    quad('tread',[[rr*math.sin(ang),yy-.02,28-rr*math.cos(ang)] for rr,yy,ang in [(r,y,a-w),(r+run,y+rise,a-w),(r+run,y+rise,a+w),(r,y,a+w)]],True)
  count=int(2.15*r/.59)
  for i in range(count):
   a=-1.075+(i+.5)*2.15/count
   if min(abs(a-aa)*r for aa in AISLES)<1.15:continue
   seats.append([r*math.sin(a),y,28-r*math.cos(a),-a,ti])
  if row in [0,n-1]:
   poly(arc_poly(r,r+.028,-1.075,1.075,0,28,80),y+.015,.015,'blue-light')
 lastR=r0+(n-1)*run;lastY=y0+(n-1)*rise
 poly(arc_poly(lastR,lastR+2.1,-1.075,1.075,0,28,80),lastY,.3,'black',True)
 # Suite fascia follows the fan, above the two middle tiers.
 if ti in [1,2]:
  arc(lastR+1.5,lastY+.5,lastY+3.0,-1.07,1.07,'glass',0,28)
  for a in np.linspace(-1.05,1.05,25):cylinder((lastR+1.5)*math.sin(a),28-(lastR+1.5)*math.cos(a),lastY,lastY+3.2,.045,.045,'metal')
 for a in AISLES:
  route(f'Tier {ti+1} aisle {a}',[[rr*math.sin(a),yy,28-rr*math.cos(a)] for rr,yy in [(r0+j*run,y0+j*rise) for j in range(n)]])
  sign(str((ti+1)*100+round((a+1.075)*10)),[(lastR+1.2)*math.sin(a),lastY+1.8,28-(lastR+1.2)*math.cos(a)],-a,1.4,.5)
# Stage and show floor; black perimeter keeps screen edges from revealing the city.
poly(Point(0,27).buffer(17.5,64),MAIN+.04,.25,'black',True)
poly(Point(0,35).buffer(10,64),MAIN+.22,.22,'dark-metal',True)
torus([0,MAIN+.24,35],10,.025,'blue-light')
route('Front floor to central seating',[[0,MAIN,25],[0,MAIN,10]])
# Giant curved display rises to the documented ~73 m apex; front and overhead.
v=[];uv=[];NX,NY=144,64
for j in range(NY+1):
 lat=j/NY*math.pi/2
 for i in range(NX+1):
  ang=-math.pi*.60+i/NX*math.pi*1.2
  v.append([66*math.cos(lat)*math.sin(ang),MAIN+66*math.sin(lat),-5+66*math.cos(lat)*math.cos(ang)])
  uv.append([i/NX,j/NY])
f=[]
for j in range(NY):
 for i in range(NX):a=j*(NX+1)+i;b=a+1;c=b+NX+1;d=a+NX+1;f.extend([[a,b,c],[a,c,d]])
mesh('screen',v,f,False,uv)
# Auditorium overhead acoustic shell, independent of the animated media plane.
poly(Point(0,0).buffer(63,96),78,.4,'black',True)

for sec in parts:
 data=dict(meshes=[dict(material=k,**v) for k,v in parts[sec].items()],collision=coll[sec])
 (OUT/(sec+'-collision.json')).write_text(json.dumps(coll[sec],separators=(',',':')))
 (OUT/(sec+'.json')).write_text(json.dumps(data,separators=(',',':')))
meta=dict(center=CENTER,radius=R,height=TOP,mainLevel=MAIN,portals=portals,signs=signs,seats=seats,lights=lights,routes=routes,materials=M,views={
 'exterior':dict(p=[-139,1.85,-149],target=[0,55,0]),'plaza':dict(p=[97,1.9,-9],target=[74,3,0]),
 'bridge':dict(p=[BP[0]-7*D[0],MAIN+1.7,BP[2]-7*D[1]],target=[BP[0]+12*D[0],MAIN+2,BP[2]+12*D[1]]),
 'bridge-door':dict(p=[BP[0]-1.7*D[0],MAIN+1.7,BP[2]-1.7*D[1]],target=[BP[0]+3*D[0],MAIN+1.9,BP[2]+3*D[1]]),
 'atrium':dict(p=[-30,MAIN+1.7,-42],target=[13,18,-58]),
 'escalators':dict(p=[-15,MAIN+1.7,-39],target=[0,18,-64]),
 'bowl':dict(p=[0,31.28,-29.96],target=[0,42,36]),
 'upper':dict(p=[0,54.35,-55.25],target=[0,26,30])})
(OUT/'sphere.json').write_text(json.dumps(meta,separators=(',',':')))
print(json.dumps(dict(center=CENTER,seats=len(seats),parts={s:{'triangles':sum(len(g['faces']) for g in parts[s].values()),'colliderTriangles':len(coll[s]['indices'])//3,'batches':len(parts[s])} for s in parts},routes=len(routes)),indent=2))
