"""Single continuous Rialto bridge on the mapped axis, with two roof wings.
Plan: OSM 543638181 / 1352089771. Creator aerials establish the broad arch,
central transverse-gabled pavilion and pale barrel-vaulted wings. Heights remain reference estimates;
the upper end preserves the existing 6.24m public portal.
"""
import math
import numpy as np
from shapely.geometry import Polygon,box
from common import Frame,parts,triangles
from palazzo_steps import barrier

START=(174.96,-611.68);END=(225.85,-644.0)
LENGTH=math.dist(START,END)
# Landings at the real street and existing upper doorway, with a shallow crest.
PROFILE=[(0,.24),(3,.24),(24,7.84),(31,7.84),(53,6.24),(LENGTH,6.24)]
def level(s):return float(np.interp(s,*zip(*PROFILE)))
def axis_frame(B):return Frame(B,*START,math.atan2(END[0]-START[0],END[1]-START[1]),y=0)
def route_points():
 R=axis_frame(None)
 return [R.p(0,y+.08,s) for s,y in PROFILE]+[(228,6.32,-644)]

def wall_extrusion(B,R,poly,x0,x1,mat='ivory'):
 for p in parts(poly):
  for tri in triangles(p):
   pts=list(tri.exterior.coords)[:-1]
   for x in [x0,x1]:B.face(mat,[R.p(x,y,s) for s,y in pts],True)
  for ring in [p.exterior,*p.interiors]:
   pts=list(ring.coords)
   for (a,y),(b,yy) in zip(pts,pts[1:]):B.face(mat,[R.p(x0,y,a),R.p(x1,y,a),R.p(x1,yy,b),R.p(x0,yy,b)],True)

def bridge(B):
 R=axis_frame(B);B.source='rialto-bridge';B.detail=0
 half=5.6
 # A single deck owns collision. Visible treads replace, not overlay, the slope.
 for (a,ya),(b,yb) in zip(PROFILE,PROFILE[1:]):
  count=max(1,math.ceil(abs(yb-ya)/.155))
  barrier(B,[R.p(-half,ya,a),R.p(-half,yb,b),R.p(half,yb,b),R.p(half,ya,a)])
  for j in range(count):
   s=a+(b-a)*j/count;t=a+(b-a)*(j+1)/count
   y=ya+(yb-ya)*(j+1)/count
   B.upface('marble',[R.p(-half,y,s),R.p(half,y,s),R.p(half,y,t),R.p(-half,y,t)])
   prev=ya+(yb-ya)*j/count
   if abs(y-prev)>.001:B.face('ivory',[R.p(-half,prev,s),R.p(half,prev,s),R.p(half,y,s),R.p(-half,y,s)])
 # The underside is a full-width arch, not a hanging curved trim line.
 samples=sorted(set([0,3,7,24,31,47,53,LENGTH]+list(np.linspace(7,47,65))))
 def soffit(s):
  if s<=7 or s>=47:return -.05
  return min(level(s)-.65,5.9*math.sqrt(max(0,1-((s-27)/20)**2)))
 body=Polygon([(s,level(s)) for s in samples]+[(s,soffit(s)) for s in reversed(samples)])
 for side in [-1,1]:
  wall_extrusion(B,R,body,side*(half-.25),side*half)
 for a,b in zip(samples,samples[1:]):B.face('plaster',[R.p(-half,soffit(a),a),R.p(half,soffit(a),a),R.p(half,soffit(b),b),R.p(-half,soffit(b),b)],True)
 # Outside balustrades, collision-only infill above the solid plinth.
 from venetian_plaza import rail
 for side in [-1,1]:
  for (a,ya),(b,yb) in zip(PROFILE,PROFILE[1:]):
   # An actual opening where the side stair reaches the bridge, not a rail across it.
   spans=[(a,b)]
   if side==1:spans=[(u,v) for u,v in [(a,min(b,47.0)),(max(a,55.6),b)] if v-u>.05]
   for u,v in spans:
    p=R.p(side*(half-.18),0,u);q=R.p(side*(half-.18),0,v)
    rail(B,(p[0],p[2]),(q[0],q[2]),level(u),level(v))
 # Two joined roof wings; the short raised central pavilion spans both.
 for a,b in [(0,24),(31,LENGTH)]:
  count=max(1,round((b-a)/3.65));step=(b-a)/count
  for side in [-1,1]:
   xx=side*3.85
   for j in range(count):
    lo=a+j*step;hi=a+(j+1)*step;mid=(lo+hi)/2;r=step*.36
    # Each arch stays genuinely open; a single spandrel per bay, no overlaps.
    spring=level(mid)+2.35
    curve=[(mid+r*math.cos(t),spring+r*math.sin(t)) for t in np.linspace(math.pi,0,25)]
    hole=Polygon([(mid-r,level(mid)-1)]+curve+[(mid+r,level(mid)-1)])
    outer=Polygon([(lo,level(lo)),(hi,level(hi)),(hi,level(hi)+4.25),(lo,level(lo)+4.25)])
    wall_extrusion(B,R,outer.difference(hole),xx-.20,xx+.20)
    R.path('marble',[(xx+side*.23,y,s) for s,y in curve],.095,8)
   # Cornice and roof share matching endpoints and the same grade profile.
   stations=sorted(set([a,b]+[s for s,y in PROFILE if a<s<b]))
   R.path('ivory',[(side*4.05,level(s)+4.30,s) for s in stations],.20,8)
  stations=sorted(set([a,b]+[s for s,y in PROFILE if a<s<b]))
  # Shallow circular barrel, visible clearly in the Hisgett street photograph.
  xs=np.linspace(-4.35,4.35,25);radius=(4.35**2+1.0)/2
  def roof_y(x):return 4.46+math.sqrt(radius**2-x*x)-math.sqrt(radius**2-4.35**2)
  for lo,hi in zip(stations,stations[1:]):
   for x,xx in zip(xs,xs[1:]):
    B.face('rialto-roof',[R.p(x,level(lo)+roof_y(x),lo),R.p(xx,level(lo)+roof_y(xx),lo),R.p(xx,level(hi)+roof_y(xx),hi),R.p(x,level(hi)+roof_y(x),hi)])
  B.detail=1
  for s in np.arange(a+.3,b,.85):R.path('silver',[(x,level(s)+roof_y(x)+.025,s) for x in xs],.018,4)
  B.detail=0
 # Pavilion: open axial passage with actual arched gables, enclosed side cheeks.
 for s in [24,31]:
  y=level(s);r=3.2;spring=y+2.25
  cut=Polygon([(-r,y-.2)]+[(r*math.cos(t),spring+r*math.sin(t)) for t in np.linspace(math.pi,0,33)]+[(r,y-.2)])
  outer=box(-4.25,y,4.25,y+5.8)
  for poly in parts(outer.difference(cut)):
   for tri in triangles(poly):B.face('ivory',[R.p(x,yy,s) for x,yy in list(tri.exterior.coords)[:-1]])
  R.path('ivory',[(r*math.cos(t),spring+r*math.sin(t),s-.035) for t in np.linspace(math.pi,0,33)],.18,8)
 for side in [-1,1]:
  xx=side*3.85
  hole=Polygon([(25,7.84),(30,7.84),(30,11.0)]+[(27.5+2.5*math.cos(t),11+2.5*math.sin(t)) for t in np.linspace(0,math.pi,25)]+[(25,7.84)])
  gable=Polygon([(24,7.84),(31,7.84),(31,13.44),(27.5,14.84),(24,13.44)])
  wall_extrusion(B,R,gable.difference(hole),xx-.2,xx+.2)
  for t in [0,.18]:
   R.path('ivory',[(xx+side*.28,13.44-t,23.85),(xx+side*.28,14.92-t,27.5),(xx+side*.28,13.44-t,31.15)],.12,6)
  R.path('marble',[(xx+side*.23,11+2.5*math.sin(t),27.5+2.5*math.cos(t)) for t in np.linspace(0,math.pi,33)],.16,8)
 for lo,hi,yl,yh in [(23.7,27.5,13.52,15.0),(27.5,31.3,15.0,13.52)]:
  B.face('rialto-roof',[R.p(-4.5,yl,lo),R.p(4.5,yl,lo),R.p(4.5,yh,hi),R.p(-4.5,yh,hi)])
 # Stone dentils and layered archivolt follow the span, not an unrelated curve.
 B.detail=1
 for side in [-1,1]:
  for s in np.arange(3,LENGTH-1,.9):R.box('ivory',(side*5.66,level(s)-.35,s),(.16,.32,.28))
  for lift,r in [(.08,.16),(-.20,.12)]:R.path('ivory',[(side*5.68,soffit(s)+lift,s) for s in samples if 7<=s<=47],r,8)
 B.detail=0
 # Align into existing north portal without a diagonal roof crossing its facade.
 landing=Polygon([R.p(-3.5,0,LENGTH) [::2],R.p(3.5,0,LENGTH)[::2],(229,-646.3),(229,-641.7)]) .buffer(0)
 B.planar('marble',landing,6.24,True)
 # Raised landing over the south canal; the old solid stair sides dammed it.
 B.source='rialto-plaza-stair'
 from venetian_waterways import plaza_height
 corners=[]
 for x in [212.9,217.1]:
  z=START[1]+(R.co*(x-START[0])-half)/R.si
  t=R.si*(x-START[0])+R.co*(z-START[1])
  corners.append([(x,plaza_height(x),-664.0),(x,4.5,-658),(x,4.5,-650.5),(x,level(t),z)])
 def mix(p,q,t):return tuple(u+(v-u)*t for u,v in zip(p,q))
 def under(z):
  if not -658<z<-650.5:return .12
  return 1.3+2.65*math.sqrt(max(0,1-((z+654.25)/3.75)**2))
 for seg in range(3):
  a,b=corners[0][seg:seg+2];c,d=corners[1][seg:seg+2]
  count=max(1,math.ceil(max(abs(b[1]-a[1]),abs(d[1]-c[1]))/.155))
  for j in range(count):
   t=j/count;u=(j+1)/count;l0=mix(a,b,t);l1=mix(a,b,u);r0=mix(c,d,t);r1=mix(c,d,u)
   B.upface('marble',[(l0[0],l1[1],l0[2]),(r0[0],r1[1],r0[2]),r1,l1])
   if count>1:B.face('ivory',[l0,r0,(r0[0],r1[1],r0[2]),(l0[0],l1[1],l0[2])])
  barrier(B,[a,c,d,b])
  for low,high in [(a,b),(c,d)]:rail(B,(low[0],low[2]),(high[0],high[2]),low[1],high[1],posts=(-1,1) if seg==0 else (1,))
  for j in range(40):
   u=j/40;v=(j+1)/40;l0=mix(a,b,u);l1=mix(a,b,v);r0=mix(c,d,u);r1=mix(c,d,v)
   for low,high in [(l0,l1),(r0,r1)]:B.face('ivory',[(low[0],under(low[2]),low[2]),(high[0],under(high[2]),high[2]),high,low],True)
   if seg==1:B.face('palazzo-stone',[(l0[0],under(l0[2]),l0[2]),(r0[0],under(r0[2]),r0[2]),(r1[0],under(r1[2]),r1[2]),(l1[0],under(l1[2]),l1[2])],True)
 return {'eye':[146,37,-670],'target':[201,7,-630]}
