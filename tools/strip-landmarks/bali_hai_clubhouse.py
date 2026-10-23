"""Bali Hai clubhouse exterior: mapped plan and inspected satellite/lakeside photo."""
from common import *
from forum_shops import facade_frame
KEY='baliHaiClubhouse'
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/clubhouse';B.detail=0
 W=Frame(B,-219,3671,-math.radians(40),y=0);p=footprint('way/133903810')
 local=rotate(translate(p,219,-3671),-40,origin=(0,0))
 def world(q):return translate(rotate(q,40,origin=(0,0)),-219,3671)
 porte=world(box(-9,-56,4,-36.2));service=world(box(17,3,29,16));body=p.difference(porte).buffer(-2.8,join_style=2)
 B.shell(body,.24,5.2,'bhc-ochre-stucco',roof=False)
 terrace=p.difference(body);B.planar('bhc-terrace-stone',terrace,.32,True)
 B.planar('bhc-flat-roof',service,5.18,True)
 # The roof is one continuous tessellation, with no coincident overlapping hip planes.
 hips=[(-23.5,-28,20.5,2,5.3),(-30.6,0,33.6,27,5.1),(-17,24,9.4,35.3,5.1),(-9.3,-55.7,4.3,-25,5.1)]
 def roofheight(u,v):
  return 5.1+min(local.boundary.distance(Point(u,v)),14)*.52
 roof=local.difference(box(17,3,29,16))
 for u in np.arange(-31,34,1.1):
  for v in np.arange(-56,36,1.1):
   for part in parts(roof.intersection(box(u,v,u+1.1,v+1.1))):
    for tri in triangles(part):
     pts=[W.p(x,roofheight(x,z),z) for x,z in list(tri.exterior.coords)[:-1]];B.upface('bhc-roof-paint',pts)
 # Eaves follow the mapped perimeter; covered terrace stone columns stand at measured bays.
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  G,L,nx,nz=facade_frame(B,a,b,p,.02)
  G.box('bhc-dark-timber',(L/2,5.06,-.04),(L,.22,.25))
  for u in np.linspace(.55,L-.55,max(2,round(L/4.5)+1)) if L>2 else []:
   G.box('bhc-stacked-ashlar',(u,1.25,.42),(.68,1.86,.68),True)
   G.box('bhc-dark-timber',(u,3.6,.42),(.30,2.85,.30),True)
   G.box('bhc-stone-cap',(u,2.21,.42),(.8,.14,.8))
 # Glazed restaurant and pro-shop bays beneath the overhang, not opaque blank walls.
 for a,b in zip(list(body.exterior.coords),list(body.exterior.coords)[1:]):
  G,L,nx,nz=facade_frame(B,a,b,body,.025)
  if L<2:continue
  for u in np.linspace(1,L-1,max(1,round(L/2.7))):
   G.box('bhc-dark-timber',(u,2.65,-.05),(2.15,3.55,.15))
   G.box('bhc-glass',(u,2.65,-.14),(1.93,3.33,.03))
   for dx in [-.49,0,.49]:G.box('bhc-dark-timber',(u+dx,2.65,-.18),(.045,3.35,.05))
   G.box('bhc-dark-timber',(u,2.7,-.18),(1.95,.06,.05))
   G.box('bhc-sage-shade',(u,4.08,-.22),(2.16,.43,.12))
 # Central layered cupola, observed in the lakeside photo and satellite.
 def hip(cx,cz,w,d,y,rise,mat):
  corners=[(cx-w/2,cz-d/2),(cx+w/2,cz-d/2),(cx+w/2,cz+d/2),(cx-w/2,cz+d/2)]
  for a,b in zip(corners,corners[1:]+corners[:1]):B.upface(mat,[W.p(a[0],y,a[1]),W.p(b[0],y,b[1]),W.p(cx,y+rise,cz)])
 W.box('bhc-dark-timber',(-2,13.3,-6),(3.8,1.6,3.8))
 for yaw in [0,math.pi/2,math.pi,3*math.pi/2]:
  G=Frame(B,*[W.p(-2,0,-6)[i] for i in [0,2]],W.yaw+yaw,y=0)
  for x in np.arange(-1.6,1.7,.4):G.box('bhc-sage-shade',(x,13.4,-1.94),(.24,.9,.05))
 hip(-2,-6,6.3,6.3,13.9,2.1,'bhc-roof-paint');W.box('bhc-dark-timber',(-2,16.15,-6),(1.5,.7,1.5));hip(-2,-6,3.1,3.1,16.5,1.3,'bhc-roof-paint');W.tube('bhc-bronze',(-2,17.8,-6),(-2,18.6,-6),.09,10,0)
 # Exposed service-roof recess and modest HVAC equipment from the aerial.
 for u,v in [(20,6),(25,6),(20,12),(25,12)]:
  W.box('bhc-service',(u,5.8,v),(2.1,1.2,2.7));W.box('bhc-dark-timber',(u,6.43,v),(1.8,.05,2.35))
 # Arrival loop remains within its own site, leaving the public road untouched.
 approach=world(box(-13,-69,18,-35)).difference(p)
 B.planar('bhc-paving',approach,.26,True)
 garden=world(Point(9,-53).buffer(7.5,32));B.planar('bhc-garden',garden,.29,True)
 # Shore terrace edge: stone plinth with metal rail, keeping door approaches open.
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  G,L,nx,nz=facade_frame(B,a,b,p,.02)
  if (a[1]+b[1])/2<3665 or L<3:continue
  G.box('bhc-stacked-ashlar',(L/2,.6,-.12),(L,.55,.4),True)
  G.box('bhc-stone-cap',(L/2,.91,-.12),(L,.08,.47))
  G.tube('bhc-rail',(0,1.45,-.12),(L,1.45,-.12),.035,8)
  for u in np.arange(.25,L,.6):G.tube('bhc-rail',(u,.94,-.12),(u,1.45,-.12),.025,6)
 samples=[]
 for x in np.arange(p.bounds[0],p.bounds[2],1.2):
  for z in np.arange(p.bounds[1],p.bounds[3],1.2):
   if terrace.buffer(-.8).covers(Point(x,z)):samples.append([float(x),.32,float(z)])
 Path('build/city-exteriors/bali-hai-clubhouse-samples.json').write_text(json.dumps(samples))
 return dict(key=KEY,name='Bali Hai Golf Clubhouse',center=[-219,0,3671],bounds=[-266,3607,-169,3719],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
