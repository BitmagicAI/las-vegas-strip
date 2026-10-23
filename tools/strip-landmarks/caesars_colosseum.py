"""Colosseum exterior in geographic metres; no inherited resort nonuniform scale.
Sceno Plus: 256ft diameter,120ft height. Centre fitted to surveyed podium arc;
facade register dimensions estimated from Earth Nov2022 and designer photograph.
"""
from common import *
from forum_shops import facade_frame
CX,CZ=-170.54651611,-211.10638017
R,H=256*.3048/2,120*.3048

def exterior(B):
 B.source='caesars-colosseum';B.detail=0
 p=Point(CX,CZ).buffer(R,resolution=64)
 # Theatre remains an opaque exterior volume. Public casino interiors are retained.
 B.shell(p,.05,H-.65,'cp-colosseum-sand',roof=False,solid=True)
 B.planar('cp-flat-roof',p.buffer(-.65),H-1.1,True)
 B.shell(p,H-.65,H,'cp-colosseum-sand',roof=False,solid=False)
 for y,r,h,mat in [(1.0,R+.18,.5,'cp-white'),(10.8,R+.34,.65,'cp-white'),(12.0,R+.24,.25,'cp-white'),(21.0,R+.35,.65,'cp-white'),(22.1,R+.25,.28,'cp-white'),(31.0,R+.36,.65,'cp-white'),(32.0,R+.52,.35,'cp-white'),(H-.1,R+.55,.20,'cp-white')]:
  ring=Point(CX,CZ).buffer(r,resolution=64).difference(Point(CX,CZ).buffer(R-.04,resolution=64));B.planar(mat,ring,y+h/2);B.shell(Point(CX,CZ).buffer(r,resolution=64),y-h/2,y+h/2,mat,roof=False,solid=False)
 # Blind arches/panels, not dark hotel windows. Flat facets are tangent at their
 # centre; inward edges terminate at the curved wall rather than crossing it.
 bays=36;step=math.tau/bays
 for j in range(bays):
  a=j*step;F=Frame(B,CX+R*math.cos(a),CZ+R*math.sin(a),-a-math.pi/2,y=0)
  for base,height,w in [(1.55,7.2,3.65),(13.0,6.8,3.8),(23.1,6.8,3.8)]:
   r=w/2;spring=base+height-r
   pts=[(-r,base),(r,base),(r,spring)]+[(r*math.cos(t),spring+r*math.sin(t)) for t in np.linspace(0,math.pi,21)[1:]]
   B.face('cp-colosseum-recess',[F.p(x,y,-.13) for x,y in pts[::-1]])
   # Thin stone archivolt with planar front and substantial reveal.
   for t0,t1 in zip(np.linspace(0,math.pi,21),np.linspace(0,math.pi,21)[1:]):
    B.face('cp-white',[F.p(rr*math.cos(t),spring+rr*math.sin(t),-.30) for rr,t in [(r,t0),(r,t1),(r+.20,t1),(r+.20,t0)]])
   for s in [-1,1]:F.box('cp-white',(s*(r+.10),(base+spring)/2,-.24),(.20,spring-base,.28))
   F.box('cp-white',(0,base-.12,-.25),(w+.65,.24,.48))
   if base>12:
    F.box('cp-colosseum-sand',(0,base+height/2-.2,-.18),(w-.32,height-1.8,.05))
    F.box('cp-white',(0,base+height+.20,-.3),(w+.75,.24,.6))
  # Engaged piers between bays: shadow-casting capitals and bases.
  b=a+step/2;G=Frame(B,CX+R*math.cos(b),CZ+R*math.sin(b),-b-math.pi/2,y=0)
  for lo,hi in [(1.3,10.4),(12.5,20.7),(22.5,30.7)]:
   G.box('cp-white',(0,(lo+hi)/2,-.24),(.60,hi-lo,.62))
   for yy,ww,hh,dep in [(lo+.15,1.05,.30,.95),(hi-.18,1.10,.36,1.0)]:G.box('cp-white',(0,yy,-.3),(ww,hh,dep))
  for yy in [33.0,35.3]:G.box('cp-colosseum-joint',(0,yy,-.13),(6.3,.025,.04))
  G.box('cp-white',(0,34.05,-.14),(.14,2.2,.18))
 # Roof service spine and two end houses are visible in Earth; dimensions inferred.
 F=Frame(B,CX,CZ,math.radians(-39),y=H-1.1)
 F.box('cp-white',(0,.8,0),(3,1.6,65))
 for z in [-29,29]:
  F.box('cp-white',(0,1.45,z),(22,2.9,10));F.box('cp-flat-roof',(0,2.92,z),(22.3,.12,10.3))
 for x in [-18,18]:
  for z in [-17,-5,8,19]:
   F.lathe('cp-service',x,z,[(0,.8),(.3,.8),(.5,.48),(1.2,.48),(1.2,.9),(1.35,.9)],16)
 B.detail=0
 return {'center':[CX,CZ],'diameterM':R*2,'heightM':H,'footprintArcFitRadiusM':37.76164,'planDifferenceM':R-37.76164,'facadeBaysEstimated':bays,'interior':'not generated; casino preserved','roof':'service housings estimated from Earth'}
