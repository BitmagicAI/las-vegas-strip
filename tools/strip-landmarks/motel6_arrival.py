"""Original arrival planter from December 2022 Street View.
Planter position, palm heights and stone courses are image-based estimates.
No public-road or parking surface is replaced by this local component.
"""
from common import *
def palm(B,F,u,w,h):
 q=F.p(u,0,w);P=Frame(B,q[0],q[2],y=0)
 P.lathe('c525-bark',0,0,[(.15,.28),(h*.55,.20),(h,.15)],12)
 # Trunk collision is contained inside the tapered visual trunk.
 P.box('c525-bark',(0,h/2,0),(.18,h,.18),True)
 for yy in np.arange(.6,h-.4,.25):
  rr=.28-.13*yy/h;P.lathe('c525-bark',0,0,[(float(yy),rr),(float(yy+.07),rr+.025),(float(yy+.13),rr)],10)
 for j in range(38):
  a=j*2.399963;co,si=math.cos(a),math.sin(a);t=(j*.41421356)%1
  tilt=math.radians(70-100*t);r=.45+.2*((j*.414)%1);yy=h+.3*(1-t)
  c=(co*r,yy,si*r);P.path('c525-palm-stem',[(0,h,0),c],.018,5)
  for k in range(12):
   pts=[]
   for n in range(3):
    theta=-1.25+(k+n*.5)*2.5/12;length=1.4*(1 if n==1 else .84)
    radial=math.cos(theta)*length;tang=math.sin(theta)*length
    pts.append(P.p(c[0]+co*radial*math.cos(tilt)-si*tang,c[1]+radial*math.sin(tilt)-.13*(n==1),c[2]+si*radial*math.cos(tilt)+co*tang))
   mat='c525-palm-leaf' if j%3 else 'c525-palm-light'
   B.face(mat,[P.p(*c),pts[0],pts[1]]);B.face(mat,[P.p(*c),pts[1],pts[2]])
 for j in range(14):
  a=j*math.tau/14;co,si=math.cos(a),math.sin(a)
  B.face('c525-bark',[P.p(co*.2,h,si*.2),P.p(co*.5-si*.1,h-1,si*.5+co*.1),P.p(co*.5+si*.1,h-1.2,si*.5-co*.1)])


def add_arrival(B,F):
 B.property='motel6-stadium-exterior';B.source='podium/motel6-stadium'
 # The rounded raised island sits north of the lobby approach.
 island=box(-778.0,1993.3,-770.0,1998.8).buffer(-1.15).buffer(1.15,quad_segs=8)
 inner=island.buffer(-.33)
 B.shell(island,.02,.52,'m6-planter-stone',roof=False)
 B.planar('m6-planter-stone',island.difference(inner),.52,True)
 B.planar('m6-gravel',inner,.43,True)
 # Broken horizontal courses and staggered vertical joints, recessed from coping.
 for yy in [.18,.35]:
  for tri in triangles(island.buffer(.006).difference(island.buffer(-.015))):
   B.upface('m6-stone-joint',[(x,yy,z) for x,z in list(tri.exterior.coords)[:-1]])
 ring=LineString(island.exterior.coords)
 for row in range(3):
  for d in np.arange(row*.30,ring.length,.68):
   a=ring.interpolate(float(d));b=ring.interpolate(float(d)+.015)
   F.tube('m6-stone-joint',(a.x,.04+row*.16,a.y),(b.x,.18+row*.16,b.y),.008,4)
 # Existing original fan-palm kit, batched by its materials.
 for x,z,h in [(-776.9,1994.8,7.8),(-773.6,1994.6,10.4),(-771.5,1997.1,8.9),(-775.2,1997.3,4.9)]:
  palm(B,F,x,z,h)
 rng=random.Random(284)
 for i in range(54):
  x=rng.uniform(-777.5,-770.5);z=rng.uniform(1993.7,1998.3)
  if not inner.covers(Point(x,z)):continue
  r=rng.uniform(.06,.18)
  B.sphere('m6-gravel-rock',(x,.44+r*.3,z),r,6,3,scale=(1.3,.5,.9))
 for x,z,r in [(-777,1997.1,.48),(-772.3,1994.1,.40),(-774.2,1996.4,.32)]:
  B.sphere('m6-planter-stone',(x,.47,z),r,8,5,scale=(1.3,.8,1))
 return [dict(name='Arrival planter bypass',points=[[-768.8,.18,2002.3],[-774,.18,2002.3],[-777,.18,2002.3]])]
