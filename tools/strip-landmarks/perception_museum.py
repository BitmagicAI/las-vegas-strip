"""Perception museum: Jan2025 facade and mapped plan; elevations estimated."""
from common import *
from forum_shops import facade_frame
from courtyard_525 import palm
KEY='perceptionMuseum';YAW=-math.atan2(9.417,17.176)
def frame(B):return Frame(B,1032.772,-2492.61,YAW,y=0)
def wall(B,G,L,graphic):
 region=box(0,.18,L,7.2)
 if graphic:
  # Original vector reconstruction of the photographed angular optical wall graphic.
  strips=[]
  xs=[0,L*.25,L*.5,L*.72,L];bases=[4.5,1.2,5.5,2,4.4];widths=[1,.65,.9,.55,1.2]
  for k in range(-18,19):
   lower=[(x,base+k*spacing) for x,base,spacing in zip(xs,bases,widths)]
   upper=[(x,base+(k+.5)*spacing) for x,base,spacing in zip(xs,bases,widths)]
   strips.append(region.intersection(Polygon(lower+list(reversed(upper)))))
  black=unary_union(strips);white=region.difference(black)
  for mat,area in [('perception-black-paint',black),('perception-white-paint',white)]:
   for poly in parts(area):
    for t in triangles(poly):B.face(mat,[G.p(u,y,0) for u,y in list(t.exterior.coords)[:-1]],True)
 else:
  B.face('perception-white-paint',[G.p(0,.18,0),G.p(L,.18,0),G.p(L,7.2,0),G.p(0,7.2,0)],True)
 G.box('perception-coping-paint',(L/2,7.23,0),(L,.12,.22))
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/perception';B.detail=0;F=frame(B);p=footprint('way/364843228')
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  G,L,nx,nz=facade_frame(B,a,b,p,0);graphic=nx>.6 or nz>.6
  wall(B,G,L,graphic)
  if nx<-.6:
   G.box('perception-yellow-paint',(L/2,3.3,-.045),(L-.2,6.2,.06));G.text('PERCEPTION',(L/2,3.25,-.1),1.2,'perception-black-letter')
   for u in [L*.25,L*.75]:G.box('perception-door-frame-paint',(u,1.6,-.12),(1.8,2.8,.14));G.box('perception-glass',(u,1.6,-.21),(1.64,2.64,.035))
  elif nz>.6:
   G.box('perception-yellow-paint',(L*.28,1.2,-.035),(L*.56,2,.05));G.text('PERCEPTION',(L*.28,1.1,-.08),.67,'perception-black-letter')
  if not graphic:
   for u in [L*.15,L*.85]:G.box('perception-vent-paint',(u,4.2,-.08),(1.3,.7,.14))
 plant=F.poly([(5.7,11),(13.5,11),(13.5,24),(5.7,24)])
 B.planar('perception-roof-paint',p.difference(plant),7.2,True);B.planar('perception-roof-paint',plant,6.25,True);B.shell(plant,6.25,7.2,'perception-servicewall-paint',roof=False)
 for u,w in [(7,13),(11,13),(7,18),(11,20),(8.5,22.7)]:
  F.box('perception-service-paint',(u,6.65,w),(1.55,.8,1.7));F.box('perception-vent-paint',(u,7.08,w),(1.3,.05,1.4))
 # Pedestrian gravel forecourt follows the building's street edge, separate from retained road.
 court=F.poly([(19.6,-1),(30.5,-1),(30.5,36.5),(19.6,36.5)]).difference(p)
 path=F.poly([(19.6,-1),(21.8,-1),(21.8,36.5),(19.6,36.5)]).difference(p)
 B.planar('perception-gravel',court.difference(path),.2,True);B.planar('perception-paving-concrete',path,.18,True)
 B.planar('perception-paving-concrete',p.buffer(1.2,join_style=2).difference(p).difference(court),.18,True)
 for w in [3,10,17,24,31]:palm(B,F,25.4,w,10.5 if w%2 else 9.3)
 for w in np.arange(-.5,36,1.65):
  F.lathe('perception-bollard-paint',30,float(w),[(.18,.16),(1.32,.16)],12)
  for y in [1.01,1.15]:F.lathe('perception-white-paint',30,float(w),[(y,.165),(y+.045,.165)],12)
  F.box('perception-hidden-collision',(30,.75,float(w)),(.32,1.14,.32),True)
 for w in [7,20,33]:
  F.box('perception-utility-paint',(27.8,.55,w),(.62,.7,.55),True)
 # Low gravel garden plants: narrow leaves in modest clumps, not grass or dense meshes.
 for u,w in [(24,7),(27,13),(23.5,27),(27,30)]:
  for k in range(24):
   a=k*2.39996;r=.22+.15*((k*.414)%1);h=.22+.21*((k*.618)%1)
   B.face('perception-leaf',[F.p(u+math.cos(a)*.04,.2,w+math.sin(a)*.04),F.p(u+math.cos(a)*r,.2+h,w+math.sin(a)*r),F.p(u+math.cos(a+.3)*.05,.2,w+math.sin(a+.3)*.05)])
 B.groups={k:g for k,g in B.groups.items() if g['material'] not in ['perception-hidden-collision','c525-collision']}
 samples=[]
 for x in np.arange(p.bounds[0]+.5,p.bounds[2],1.3):
  for z in np.arange(p.bounds[1]+.5,p.bounds[3],1.3):
   if p.buffer(-.3).contains(Point(x,z)):samples.append([float(x),6.8 if plant.contains(Point(x,z)) else 7.7,float(z)])
 Path('build/city-exteriors/perception-museum-samples.json').write_text(json.dumps(samples))
 return dict(key=KEY,name='Perception museum exterior',center=[1033,0,-2473],bounds=[1010,-2498,1068,-2434],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
