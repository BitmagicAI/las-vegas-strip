"""Oasis / Sweethearts: mapped courtyard plan, photo-estimated elevations.
Reference photographs are research only; all surfaces are authored geometry.
"""
from common import *
from forum_shops import facade_frame
KEY='oasisMotel'
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/motel';B.detail=0
 F=Frame(B,1799.532,-3798.11,math.atan2(10.809,5.674),y=0)
 p=footprint('way/364845142');cut=F.poly([(.45,-3),(6.9,-3),(6.9,8),(.45,8)])
 body=p.difference(cut)
 B.shell(body,.02,3.8,'om-stucco',roof=False);B.planar('om-roof',body,3.8,True)
 # Ground reaches through the real courtyard, with no building box across entry.
 B.planar('om-paving',F.poly([(-16,-3),(17,-3),(17,93),(-16,93)]),-.08,True)
 B.planar('om-paving',F.poly([(-7.4,5), (7.4,5),(7.4,88),(-7.4,88)]),.04,True)
 # Chapel upper floor on southern front wing.
 chapel=p.intersection(F.poly([(-16,-2),(.3,-2),(.3,17),(-16,17)]))
 B.shell(chapel,3.8,6.6,'om-ochre',roof=False);B.planar('om-roof',chapel,6.6)
 # Recessed motel bays and window/door frames on courtyard walls.
 for poly in parts(body):
  ps=list(poly.exterior.coords)
  for a,b in zip(ps,ps[1:]):
   if math.dist(a,b)<2:continue
   G,L,nx,nz=facade_frame(B,a,b,p,.06)
   G.box('om-trim',(L/2,3.78,-.02),(L,.22,.38))
   if L<12:continue
   for u in np.arange(2.7,L-2,5.3):
    G.box('om-reveal',(u,1.8,-.04),(2.2,1.65,.08))
    G.box('om-glass',(u,1.8,-.1),(2,1.45,.08))
    for dx in [-1,0,1]:G.box('om-frame',(u+dx,1.8,-.17),(.055,1.55,.06))
    G.box('om-trim',(u,1,-.22),(2.3,.12,.35))
    G.box('om-door',(u+1.95,1.25,-.08),(.9,2.4,.1))
    G.box('om-frame',(u+2.23,1.2,-.17),(.04,.2,.06))
    G.box('om-ac',(u,.45,-.2),(1.15,.6,.4))
    for h in np.arange(.23,.7,.09):G.box('om-reveal',(u,h,-.42),(1,.025,.025))
 # Wide shallow entrance arch: closed solid lintel above a real clear passage.
 cx=3.675;half=3.225;top=6.1
 def underside(x):return 3.9+.8*max(0,1-((x-cx)/half)**2)
 for x0,x1 in zip(np.linspace(.45,6.9,33)[:-1],np.linspace(.45,6.9,33)[1:]):
  h0,h1=underside(x0),underside(x1)
  for z in [-.25,6.3]:B.face('om-stucco',[F.p(x0,h0,z),F.p(x1,h1,z),F.p(x1,top,z),F.p(x0,top,z)],True)
  B.face('om-stucco',[F.p(x0,h0,-.25),F.p(x0,h0,6.3),F.p(x1,h1,6.3),F.p(x1,h1,-.25)],True)
 F.box('om-trim',(cx,6.18,3),(7.3,.16,6.7))
 for x in [.05,7.3]:
  F.box('om-stucco',(x,2,0),(.8,4,1),True)
  F.lathe('om-gray',x,-.62,[(.05,.55),(.3,.55),(.45,.4),(3.6,.32),(3.75,.5),(3.95,.55)],20)
 # Street shops and chapel window wall, read from front photo.
 for x,w,label in [(11.65,8.5,'SMOKE SHOP'),(-7.7,14.7,'SWEETHEARTS CHAPEL')]:
  fz=-1.4 if x<0 else -.36
  F.box('om-stucco',(x,3.28,fz),(w,.95,.42))
  F.text(label,(x,3.3,fz-.24),.48 if x<0 else .45,'om-red')
  F.box('om-glass',(x,1.5,fz+.1),(w-.7,2.45,.1))
  for xx in np.arange(x-w/2+.35,x+w/2,.9):F.box('om-frame',(xx,1.5,fz),(.055,2.5,.06))
  F.box('om-trim',(x,.2,fz),(w,.3,.3))
 # Upper chapel shallow blind arches, inset grille and cornice.
 for x in [-11.8,-5]:
  F.box('om-reveal',(x,5,-1.13),(4.9,1.9,.09));F.box('om-ochre',(x,4.95,-1.23),(4.5,1.55,.1))
  F.path('om-trim',[(x+2.5*math.cos(a),5.35+.6*math.sin(a),-1.28) for a in np.linspace(0,math.pi,25)],.08)
  F.box('om-glass',(x,4.48,-1.31),(2.4,.6,.1))
  for xx in np.linspace(x-1.2,x+1.2,7):F.box('om-ochre',(xx,4.48,-1.4),(.055,.6,.05))
 F.box('om-trim',(-7.6,6.65,-1.08),(15.8,.23,.5))
 # Freestanding motel sign: main historic identity; no guessed live prices.
 F.box('om-trim',(10,7.5,1.2),(.45,7,.5),True)
 for yaw in [F.yaw,F.yaw+math.pi]:
  q=F.p(10,0,1.2);G=Frame(B,q[0],q[2],yaw,y=0)
  G.box('om-stucco',(0,9.2,-.24),(4.5,2.65,.3));G.box('om-red',(0,6.9,-.24),(4.5,1.75,.3))
  G.text('OASIS',(0,9.7,-.43),.8,'om-teal');G.text('MOTEL',(0,8.7,-.43),.8,'om-teal');G.text('MOTEL',(0,6.9,-.43),.65,'om-letter')
  for y in [5.95,7.85,10.65]:G.box('om-trim',(0,y,-.3),(4.8,.16,.45))
 B.detail=1
 # Courtyard planting strips and rear service equipment. No invented pool.
 for z in np.arange(27,85,12):
  F.box('om-soil',(-5.4,.08,z),(2,.15,5))
  for dz in [-1.6,0,1.6]:B.sphere('om-leaf',F.p(-5.4,.5,z+dz),.7,10,6,scale=(1,.65,1))
 for x,z in [(-11,30),(-11,55),(-11,77),(12,25),(12,44)]:
  F.box('om-ac',(x,4.1,z),(1.5,.6,1.2));F.box('om-reveal',(x,4.42,z),(1.2,.04,.9))
 B.detail=0
 return dict(key=KEY,name='Oasis Motel and Sweethearts Chapel',center=[1832,0,-3779],bounds=[1785,-3818,1894,-3735],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
