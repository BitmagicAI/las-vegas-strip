"""Bellagio main tower and Spa Tower exteriors, remodelled from the owner's Google Earth view (2026-10-08,
docs/project-records/bellagio-remodel-2026-10-08/owner-reference-google-earth.webp). Each tower has three segments
above its podium:
  lower  - cream: a square window row under two rows of tall windows (the Spa: three square rows), one window per bay
  band   - white
  middle - cream: eight rows of square windows, one per bay
  belt   - white, projecting
  crown  - white: paired square windows, then paired round-arched windows, a frieze and a deep cornice
The outer ends of the wings are lower pavilions with pyramid roofs; the bodies carry low patina hip roofs with a dark
service deck. The main tower's rotunda continues above the roof as a lettered drum, an open arcade and a ribbed dome
to the published 155.8 m tip. One visible window unit spans two floors (four panes), as in the reference.
The tower footprints are the surveyed OSM ways; heights are fitted to the reference's proportions (unit U per row).
"""
import math
import numpy as np
from shapely.geometry import Polygon,Point,LineString,box
from shapely.ops import unary_union
from building_surfaces import parts
from surface_geometry import triangles

ROT_C=(-301.7,321.5);ROT_R=10.3
MAIN=dict(P=12.4,U=6.27)
SPA=dict(P=12.4,U=5.82)

def ccw(p):
 p=p.buffer(0)
 if isinstance(p,Polygon) and not p.exterior.is_ccw:return Polygon(list(p.exterior.coords)[::-1])
 return p

def cross(a,c):return float(a[0]*c[1]-a[1]*c[0])

def simple(p):
 """Drop vertices on straight runs (OSM splits), keep every real corner."""
 cs=list(p.exterior.coords)[:-1];out=[]
 for i,v in enumerate(cs):
  a=np.subtract(v,cs[i-1]);c=np.subtract(cs[(i+1)%len(cs)],v)
  if np.linalg.norm(a)<1e-6:continue
  if abs(cross(a,c))/(np.linalg.norm(a)*np.linalg.norm(c)+1e-9)>.004:out.append(v)
 return Polygon(out)

def halfplane(a,c,toward,size=400):
 """The side of line a-c that contains `toward`."""
 a,c=np.array(a),np.array(c);d=(c-a)/np.linalg.norm(c-a);n=np.array([-d[1],d[0]])
 if np.dot(np.array(toward)-a,n)<0:n=-n
 return Polygon([tuple(a-d*size),tuple(c+d*size),tuple(c+d*size+n*size),tuple(a-d*size+n*size)])

class T:
 """Emit helpers on one Builder."""
 def __init__(s,b):s.b=b
 def quad(s,mat,pts):s.b.face(mat,pts)
 def walls(s,poly,lo,hi,mat,keep=lambda a,c:True):
  for q in parts(poly):
   for ring in [q.exterior,*q.interiors]:
    cs=list(ring.coords)
    for a,c in zip(cs,cs[1:]):
     if math.dist(a,c)<.01 or not keep(a,c):continue
     s.quad(mat,[(a[0],lo,a[1]),(c[0],lo,c[1]),(c[0],hi,c[1]),(a[0],hi,a[1])])
 def cap(s,mat,poly,y,down=False):
  for q in parts(poly):
   for tri in triangles(q):
    pts=[(x,y,z) for x,z in list(tri.exterior.coords)[:-1]];a=np.array(pts)
    if (np.cross(a[1]-a[0],a[2]-a[0])[1]<0)!=down:pts=pts[::-1]
    s.b.face(mat,pts)
 def band(s,outer,base,y0,y1,mat):
  """A projecting course: `outer` minus `base`, walled only where it is not against `base`."""
  ring=outer.difference(base)
  if ring.is_empty:return
  edge=base.boundary
  def keep(a,c):return edge.distance(Point((a[0]+c[0])/2,(a[1]+c[1])/2))>.02
  s.walls(ring,y0,y1,mat,keep);s.cap(mat,ring,y0,True);s.cap(mat,ring,y1)
 def ring(s,mat,c,profile,n=48,phase=0.):
  x,z=c
  for (y,r),(yy,rr) in zip(profile,profile[1:]):
   for i in range(n):
    a=phase+i*math.tau/n;e=phase+(i+1)*math.tau/n
    s.quad(mat,[(x+r*math.cos(a),y,z+r*math.sin(a)),(x+r*math.cos(e),y,z+r*math.sin(e)),(x+rr*math.cos(e),yy,z+rr*math.sin(e)),(x+rr*math.cos(a),yy,z+rr*math.sin(a))])

class Wall:
 """A local frame on a facade: u along the wall, y up, w outward."""
 def __init__(s,t,o,tan,nor,pitch=10.):s.t=t;s.o=o;s.tan=tan;s.nor=nor;s.pitch=pitch
 def p(s,u,y,w):return (s.o[0]+s.tan[0]*u+s.nor[0]*w,y,s.o[1]+s.tan[1]*u+s.nor[1]*w)
 def rect(s,mat,u0,u1,y0,y1,w):s.t.quad(mat,[s.p(u0,y0,w),s.p(u1,y0,w),s.p(u1,y1,w),s.p(u0,y1,w)])
 def slab(s,mat,u0,u1,y0,y1,w0,w1):
  P=s.p;q=s.t.quad
  q(mat,[P(u0,y0,w1),P(u1,y0,w1),P(u1,y1,w1),P(u0,y1,w1)])
  q(mat,[P(u0,y1,w0),P(u0,y1,w1),P(u1,y1,w1),P(u1,y1,w0)]);q(mat,[P(u0,y0,w0),P(u1,y0,w0),P(u1,y0,w1),P(u0,y0,w1)])
  q(mat,[P(u0,y0,w0),P(u0,y0,w1),P(u0,y1,w1),P(u0,y1,w0)]);q(mat,[P(u1,y0,w0),P(u1,y1,w0),P(u1,y1,w1),P(u1,y0,w1)])
 def window(s,uc,y0,w,h,arch=False,deep=1.):
  """Dark glass, a light surround and sill; four- or six-pane glazing bars (near detail)."""
  b=s.t.b;src=b.detail;u0,u1=uc-w/2,uc+w/2;y1=y0+h;f=.20*deep;r=w/2;spring=y1-r if arch else y1
  if arch:
   s.rect('bel-glass',u0,u1,y0,spring,.05);n=10
   for i in range(n):
    a=math.pi*i/n;e=math.pi*(i+1)/n
    s.t.quad('bel-glass',[s.p(uc,spring,.05),s.p(uc+r*math.cos(a),spring+r*math.sin(a),.05),s.p(uc+r*math.cos(e),spring+r*math.sin(e),.05)])
    # Arch moulding: face, soffit and outer edge of each segment.
    ia=(uc+r*math.cos(a),spring+r*math.sin(a));ie=(uc+r*math.cos(e),spring+r*math.sin(e));R=r+.18
    oa=(uc+R*math.cos(a),spring+R*math.sin(a));oe=(uc+R*math.cos(e),spring+R*math.sin(e))
    s.t.quad('bel-frame',[s.p(*ia,f),s.p(*oa,f),s.p(*oe,f),s.p(*ie,f)]);s.t.quad('bel-frame',[s.p(*ia,0),s.p(*ia,f),s.p(*ie,f),s.p(*ie,0)]);s.t.quad('bel-frame',[s.p(*oa,0),s.p(*oe,0),s.p(*oe,f),s.p(*oa,f)])
  else:
   s.rect('bel-glass',u0,u1,y0,y1,.05);s.slab('bel-frame',u0-.18,u1+.18,y1,y1+.2,0,f+.04)
  for x in [u0-.16,u1]:s.slab('bel-frame',x,x+.16,y0,spring,0,f)
  s.slab('bel-frame',u0-.36,u1+.36,y0-.2,y0,0,f+.14)
  b.detail=1
  s.slab('bel-mullion',uc-.045,uc+.045,y0,spring+(r if arch else 0)-.02,.05,.11)
  for k in range(1,max(2,round((spring-y0)/2.4))):yy=y0+(spring-y0)*k/max(2,round((spring-y0)/2.4));s.slab('bel-mullion',u0,u1,yy-.045,yy+.045,.05,.11)
  b.detail=src

def bays(t,union,bay=9.6,margin=1.4,skip=lambda p:False):
 """Bay frames along each straight run of the outline (near-collinear OSM splits merged so a run has even bays)."""
 out=[]
 for q in parts(union):
  cs=list(q.exterior.coords)[:-1];n=len(cs);edges=[(cs[i],cs[(i+1)%n]) for i in range(n)]
  def turn(i):
   a=np.subtract(edges[i-1][1],edges[i-1][0]);c=np.subtract(edges[i][1],edges[i][0])
   return abs(math.atan2(cross(a,c),float(np.dot(a,c))))>math.radians(4)
  starts=[i for i in range(n) if turn(i)] or [0]
  for k,i0 in enumerate(starts):
   i1=starts[(k+1)%len(starts)];run=[];i=i0
   while True:
    run.append(edges[i]);i=(i+1)%n
    if i==i1:break
   L=sum(math.dist(a,c) for a,c in run)
   if L<7:continue
   m=int(max(1,round((L-2*margin)/bay)));p=(L-2*margin)/m
   for j in range(m):
    sj=margin+(j+.5)*p;acc=0
    for a,c in run:
     le=math.dist(a,c)
     if sj<=acc+le or (a,c)==run[-1]:
      d=((c[0]-a[0])/le,(c[1]-a[1])/le);nor=(d[1],-d[0])
      x=a[0]+d[0]*(sj-acc);z=a[1]+d[1]*(sj-acc)
      if q.contains(Point(x+nor[0]*.5,z+nor[1]*.5)):nor=(-nor[0],-nor[1])
      if not skip(Point(x,z)):out.append(Wall(t,(x,z),d,nor,p))
      break
     acc+=le
 return out

def hip(t,poly,y,pitch,slope='bel-patina',deck='bel-deck',target=99.):
 """Hip roof by a mitred inset: one plane per eave, exact until the first edge collapses; a flat deck above."""
 q=ccw(simple(poly));v=np.array(list(q.exterior.coords)[:-1]);n=len(v)
 e=[(v[(i+1)%n]-v[i]) for i in range(n)];e=[d/np.linalg.norm(d) for d in e];inn=[np.array([-d[1],d[0]]) for d in e]
 def inset(dist):
  w=[]
  for i in range(n):
   a,c=i-1,i;pa=v[i]+inn[a]*dist;pc=v[i]+inn[c]*dist;M=np.array([e[a],-e[c]]).T
   try:k=np.linalg.solve(M,pc-pa)
   except np.linalg.LinAlgError:w.append(pa);continue
   w.append(pa+e[a]*k[0])
  return w
 def ok(dist):
  w=inset(dist)
  for i in range(n):
   if np.dot(w[(i+1)%n]-w[i],e[i])<=.05:return False
  return Polygon(w).is_valid
 lo,hi=0.,target
 if not ok(hi):
  for _ in range(40):
   mid=(lo+hi)/2
   if ok(mid):lo=mid
   else:hi=mid
  hi=lo*.985
 D=hi;w=inset(D);top=y+D*math.tan(math.radians(pitch))
 for i in range(n):
  j=(i+1)%n;t.quad(slope,[(v[i][0],y,v[i][1]),(v[j][0],y,v[j][1]),(w[j][0],top,w[j][1]),(w[i][0],top,w[i][1])])
 if Polygon(w).area>.5:t.cap(deck if Polygon(w).area>40 else slope,Polygon(w),top)
 return top

def tower(b,union,body,pavilions,spec,crown,skip=lambda p:False,rotunda=None):
 """Shared Bellagio scheme on a footprint split into a tall body and lower end pavilions."""
 t=T(b);P,U=spec['P'],spec['U'];Y=lambda u:P+u*U
 eave_p=Y(crown['pavilion_eave']);eave=Y(crown['eave'])
 disk=Point(*rotunda).buffer(ROT_R,quad_segs=24) if rotunda else None
 base=union if disk is None else union.union(disk);bbase=body if disk is None else body.union(disk)
 out=lambda p,d:p.buffer(d,join_style=2)
 # Walls by colour zone: the union up to the pavilion eave, the body above it (its pavilion ends are plain white).
 keep_out=(lambda a,c:not Point(rotunda).buffer(ROT_R-.05).contains(Point((a[0]+c[0])/2,(a[1]+c[1])/2))) if rotunda else (lambda a,c:True)
 for lo,hi,mat in [(P,Y(3.6),'bel-cream'),(Y(3.6),Y(4.3),'bel-white'),(Y(4.3),Y(12.3),'bel-cream'),(Y(12.3),eave_p,'bel-white')]:t.walls(union,lo,hi,mat,keep_out)
 t.walls(body,eave_p,eave,'bel-white',keep_out)
 # Courses: base, the white band, the belt cornice, the string under the arches.
 for y0,y1,d in [(P,P+.6,.3),(Y(3.6),Y(3.6)+.5,.35),(Y(4.3)-.5,Y(4.3),.35),(Y(12.3),Y(12.3)+.6,.3),(Y(12.3)+.6,Y(12.3)+1.3,.65),(Y(13.1)-.6,Y(13.1),.25),(Y(crown['string'])-.2,Y(crown['string'])+.25,.3)]:t.band(out(union,d),base,y0,y1,'bel-white')
 # Pavilion cornices and pyramid roofs, cut against the body.
 for pv in pavilions:
  for y0,y1,d in [(eave_p-1.3,eave_p-.7,.35),(eave_p-.7,eave_p,.8)]:t.band(out(pv,d),pv.union(body).union(base),y0,y1,'bel-white')
  hip(t,out(pv,.8),eave_p,33,'bel-patina','bel-patina')
 # Body crown: string over the arches, frieze, stepped cornice, hip roof.
 for y0,y1,d in [(eave-7.0,eave-6.6,.3),(eave-2.2,eave-1.6,.3),(eave-1.6,eave-.8,.7),(eave-.8,eave,1.2)]:t.band(out(body,d),bbase,y0,y1,'bel-white')
 roof=hip(t,out(body,1.2),eave,32,target=11.5)
 # Windows per bay.
 walls=bays(t,union,crown.get('bay',9.6),skip=skip);fat=body.buffer(.01)
 for wl in walls:
  pitch=wl.pitch;one=min(4.6,.48*pitch);two=min(3.3,.34*pitch);gap=.11*pitch
  # Body-only features (the arches, the frieze) test their own position: a bay can straddle a pavilion's edge.
  inbody=lambda u,half=0:all(fat.contains(Point(wl.o[0]+wl.tan[0]*(u+e)-wl.nor[0],wl.o[1]+wl.tan[1]*(u+e)-wl.nor[1])) for e in (-half,half))
  for u0,h in crown['lower']:wl.window(0,Y(u0),one,h*U)
  for k in range(8):wl.window(0,Y(4.3+k+.13),one,.74*U)
  for y0,h in crown['squares']:
   for s in [-1,1]:wl.window(s*(two+gap)/2,Y(y0),two,h*U)
  for y0,h,where in crown['arches']:
   for s in [-1,1]:
    if where=='all' or inbody(s*(two+gap)/2,two/2+.4):wl.window(s*(two+gap)/2,Y(y0),two,h*U,arch=True)
  # Frieze: small square attic lights between the arches and the cornice.
  b.detail=1
  for s in [-1.5,-.5,.5,1.5]:
   if inbody(s*pitch/4,.5):wl.rect('bel-glass',s*pitch/4-.45,s*pitch/4+.45,eave-5.2,eave-4.3,.04)
  b.detail=0
 return t,eave,roof

def main(b,footprint):
 """The main tower: three wings around the lakefront rotunda."""
 q=ccw(footprint);cs=list(q.exterior.coords)[:-1]
 # The rotunda's arc becomes a chord inside the cylinder (the cylinder owns that face).
 cs=[c for c in cs if not (9.5<math.dist(c,ROT_C)<10.7 and c[0]>-299.5)]
 # Its two ends sit just inside the cylinder (one surveyed end is 0.35 m outside it and left a dark slot).
 def snap(c):
  d=math.dist(c,ROT_C)
  return (ROT_C[0]+(c[0]-ROT_C[0])*(ROT_R-.15)/d,ROT_C[1]+(c[1]-ROT_C[1])*(ROT_R-.15)/d) if 9.5<d<10.7 else c
 cs=[snap(c) for c in cs]
 union=Polygon(cs)
 near=lambda p:min(cs,key=lambda c:math.dist(c,p))
 # Pavilion splits are the surveyed vertices at each wing's end (front, back, a point at the end).
 cuts=[((-278.9,238.2),(-304.1,229.9),(-268.5,214.2)),((-279.9,402.2),(-304.0,413.2),(-292.4,439.4)),((-407.4,307.9),(-407.4,335.1),(-428.8,308.0))]
 pavilions=[union.intersection(halfplane(near(a),near(c),near(e))) for a,c,e in cuts]
 body=union.difference(unary_union(pavilions)).buffer(0)
 body=max(parts(body),key=lambda p:p.area)
 crown=dict(lower=[(.17,.68),(1.2,1.05),(2.5,1.05)],squares=[(13.27,.86),(14.47,.86)],string=15.55,pavilion_eave=16.1,
            arches=[(15.65,2.3,'body')],eave=19.4)
 b.source='guest-main';b.detail=0
 t,eave,roof=tower(b,union,body,pavilions,MAIN,crown,skip=lambda p:p.distance(Point(ROT_C))<ROT_R+1,rotunda=ROT_C)
 rotunda(b,t,eave)
 return eave

def rotunda(b,t,eave):
 P,U=MAIN['P'],MAIN['U'];Y=lambda u:P+u*U;cx,cz=ROT_C;R=ROT_R;n=48;ph=-math.pi/n
 b.source='guest-main';b.detail=0
 t.ring('bel-cream',ROT_C,[(P,R),(Y(3.6),R)],n,ph);t.ring('bel-white',ROT_C,[(Y(3.6),R),(Y(4.3),R)],n,ph)
 t.ring('bel-cream',ROT_C,[(Y(4.3),R),(Y(12.3),R)],n,ph);t.ring('bel-white',ROT_C,[(Y(12.3),R),(eave,R)],n,ph)
 for y0,y1,d in [(P,P+.6,.3),(Y(3.6),Y(3.6)+.5,.35),(Y(4.3)-.5,Y(4.3),.35),(Y(12.3),Y(12.3)+.6,.3),(Y(12.3)+.6,Y(12.3)+1.3,.65),(Y(13.1)-.6,Y(13.1),.25),(eave-7.0,eave-6.6,.3),(eave-2.2,eave-1.6,.3),(eave-1.6,eave-.8,.7),(eave-.8,eave,1.2)]:
  t.ring('bel-white',ROT_C,[(y0,R),(y0,R+d),(y1,R+d),(y1,R)],n,ph)
 # Five window columns face the lake (the rest of the cylinder is inside the wings below the roof).
 facet=R*math.cos(math.pi/n)
 for deg in [-60,-30,0,30,60]:
  a=math.radians(deg);nor=(math.cos(a),math.sin(a));tan=(-math.sin(a),math.cos(a))
  wl=Wall(t,(cx+nor[0]*facet,cz+nor[1]*facet),tan,nor,6.)
  for u0,h in [(.17,.68),(1.2,1.05),(2.5,1.05)]:wl.window(0,Y(u0),2.3,h*U)
  for k in range(8):wl.window(0,Y(4.3+k+.15),2.3,.70*U)
  for k in range(3):wl.window(0,Y(13.22+k*.86),2.3,.70*U)
  wl.window(0,Y(15.85),2.3,1.5*U,arch=True)
 # Drum above the roof with the name facing the lake, an open arcade, a ribbed dome and a finial: the 155.8 m tip.
 b.source='cupola';b.detail=0
 top=eave+6.2
 t.ring('bel-white',ROT_C,[(eave,R),(top-.6,R),(top-.6,R+.45),(top,R+.45),(top,R+.8),(top+.5,R+.8),(top+.5,9.65)],n,ph)
 word='BELLAGIO';step=math.radians(11.5)
 for i,ch in enumerate(word):
  a=(3.5-i)*step;x,z=cx+(R+.12)*math.cos(a),cz+(R+.12)*math.sin(a);yaw=math.atan2(-math.cos(a),-math.sin(a))
  b.text(ch,(x,eave+2.0,z),3.0,-yaw,'gold')
 lo=top+.5;hi=lo+5.3
 t.ring('bel-white',ROT_C,[(lo,9.65),(hi,9.65)],n,ph)
 for k in range(12):
  a=k*math.tau/12;nor=(math.cos(a),math.sin(a));tan=(-math.sin(a),math.cos(a))
  wl=Wall(t,(cx+nor[0]*9.6,cz+nor[1]*9.6),tan,nor)
  wl.slab('bel-white',-.65,.65,lo,hi,-.9,.35)
  # Arched opening between this pier and the next.
  a2=a+math.pi/12;nor=(math.cos(a2),math.sin(a2));tan=(-math.sin(a2),math.cos(a2));op=Wall(t,(cx+nor[0]*9.62,cz+nor[1]*9.62),tan,nor)
  op.rect('charcoal',-1.65,1.65,lo,hi-2.1,.04);r=1.65;sp=hi-2.1
  for i in range(8):
   e0=math.pi*i/8;e1=math.pi*(i+1)/8;t.quad('charcoal',[op.p(0,sp,.04),op.p(r*math.cos(e0),sp+r*math.sin(e0),.04),op.p(r*math.cos(e1),sp+r*math.sin(e1),.04)])
 t.ring('bel-white',ROT_C,[(hi,9.65),(hi,10.4),(hi+.6,10.4),(hi+.6,10.9),(hi+1.2,10.9),(hi+1.2,10.1)],n,ph)
 d0=hi+1.2;angles=np.linspace(0,math.radians(82),12)
 t.ring('bel-dome',ROT_C,[(d0+6.2*math.sin(f),10.1*math.cos(f)) for f in angles],n,ph)
 b.detail=1
 for k in range(16):
  a=k*math.tau/16;pts=[(cx+(10.1*math.cos(f)+.12)*math.cos(a),d0+6.2*math.sin(f)+.1,cz+(10.1*math.cos(f)+.12)*math.sin(a)) for f in angles]
  b.path('bel-white',pts,.16,6)
 b.detail=0
 dt=d0+6.2*math.sin(angles[-1])
 t.ring('bel-white',ROT_C,[(dt,1.5),(dt+1.1,1.3),(dt+1.1,1.6),(dt+1.4,1.6),(dt+1.9,.6),(155.8,0)],16)

def spa(b,footprint,center_cut=(523.3,598.4)):
 """The Spa Tower: a long slab with lower pavilions at both ends; its base stands on the ground."""
 union=ccw(footprint);x0,z0,x1,z1=union.bounds
 body=union.intersection(box(x0-5,center_cut[0],x1+5,center_cut[1]))
 pavilions=[p for p in parts(union.difference(body)) if p.area>20]
 crown=dict(lower=[(.25,.72),(1.4,.72),(2.55,.72)],squares=[],string=15.0,pavilion_eave=15.6,
            arches=[(13.25,1.65,'all'),(15.75,2.0,'body')],eave=19.1,bay=9.4)
 b.source='tower/way/114716301';b.detail=0;t=T(b)
 # Base below the tower segments: cream with a white course (neighbouring roofs hide most of it).
 t.walls(union,.24,SPA['P'],'bel-cream');t.band(union.buffer(.3,join_style=2),union,SPA['P']-.8,SPA['P'],'bel-white')
 tower(b,union,body,pavilions,SPA,crown)
