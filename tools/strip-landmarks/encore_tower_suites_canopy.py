"""Encore Tower Suites fabric arrival canopy; January2025 StreetView.
5.3m eaves/7.2m crown estimated. Static exterior; original interiors retained.
"""
from common import *
from forum_shops import facade_frame
KEY='encoreSuitesCanopy';IDS=['way/182524943']
def exterior(B):
 B.property=KEY+'-exterior';B.source='encore-suites-canopy';B.detail=0;p=footprint(IDS[0]);c=p.centroid;F=Frame(B,c.x,c.y,.68,y=0)
 # Curved hip in shallow concentric bands; stripe polygons are disjoint surfaces.
 from shapely import affinity
 local=affinity.rotate(affinity.translate(p,-c.x,-c.y),math.degrees(.68),origin=(0,0))
 def world(x,z):return F.p(x,0,z)
 def height(x,z):
  d=min(2.9,local.boundary.distance(Point(x,z)));return 5.3+1.9*(d/2.9)**1.7
 for d in np.arange(0,3,.15):
  ring=local.buffer(-float(d),join_style=2).difference(local.buffer(-float(d)-.15,join_style=2))
  for x in np.arange(local.bounds[0]-.4,local.bounds[2],.32):
   mat='etsc-black-fabric-paint' if int(round((x-local.bounds[0]+.4)/.32))%2 else 'etsc-white-fabric-paint'
   for q in parts(ring.intersection(box(float(x),local.bounds[1]-1,float(x)+.32,local.bounds[3]+1))):
    for tri in triangles(q):
     vs=[F.p(u,height(u,v),v)for u,v in list(tri.exterior.coords)[:-1]];B.upface(mat,vs,True)
 top=local.buffer(-3,join_style=2)
 for x in np.arange(local.bounds[0]-.4,local.bounds[2],.32):
  mat='etsc-black-fabric-paint' if int(round((x-local.bounds[0]+.4)/.32))%2 else 'etsc-white-fabric-paint'
  for q in parts(top.intersection(box(float(x),local.bounds[1]-1,float(x)+.32,local.bounds[3]+1))):
   for tri in triangles(q):B.upface(mat,[F.p(u,7.2,v)for u,v in list(tri.exterior.coords)[:-1]],True)
 # Glazed, closed entrance at the actual short connection to the tower footprint.
 E,L,_,_=facade_frame(B,(713.236,-1531.489),(710.682,-1534.272),footprint('way/27910891'),.42)
 E.box('etsc-white-frame-paint',(L/2,2.6,0),(L+.25,5.2,.18))
 for u in [L*.25,L*.75]:
  E.box('etsc-glass',(u,2.25,-.12),(L*.5-.18,3.9,.05))
  E.tube('etsc-white-frame-paint',(u+.42,1.3,-.19),(u+.42,2.3,-.19),.024,8)
 E.text('TOWER SUITES',(L/2,4.55,-.14),.26,'etsc-black-fabric-paint')
 # Scalloped alternating valance, perimeter rails and white piers clear of driveway.
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  G,L,nx,nz=facade_frame(B,a,b,p,0)
  G.box('etsc-white-frame-paint',(L/2,5.17,0),(L,.12,.12))
  for j in range(max(1,math.ceil(L/.32))):
   lo=j*.32;hi=min(L,lo+.32);mat='etsc-black-fabric-paint'if j%2 else'etsc-white-fabric-paint'
   B.face(mat,[G.p(lo,5.3,0),G.p(hi,5.3,0),G.p(hi,4.87,0),G.p((lo+hi)/2,4.82,0),G.p(lo,4.87,0)])
 # Pillars at the three exposed corners; western edge attaches to existing entry.
 for x,z in [(719,-1547.3),(724.6,-1539.8),(714,-1532.8)]:
  C=Frame(B,x,z,.68,y=0);C.box('etsc-white-frame-paint',(0,2.6,0),(.38,5.2,.38),True);C.box('etsc-white-frame-paint',(0,.35,0),(.57,.7,.57),True);C.box('etsc-white-frame-paint',(0,4.97,0),(.63,.3,.63))
 # Underside cross-bracing and muted lamps, without adding live lights.
 for u in [-3,0,3]:
  pts=[]
  for v in np.arange(local.bounds[1],local.bounds[3],.25):
   if local.contains(Point(u,v)):pts.append(F.p(u,5.02,float(v)))
  if len(pts)>1:B.tube('etsc-white-frame-paint',pts[0],pts[-1],.035,8)
 B.planar('etsc-paving-stone',p,.20,True)
 samples=[]
 for u in np.arange(local.bounds[0]+.3,local.bounds[2],.7):
  for v in np.arange(local.bounds[1]+.3,local.bounds[3],.7):
   if local.buffer(-.15).contains(Point(u,v)):samples.append(list(F.p(float(u),height(u,v)+.35,float(v))))
 routes=[[(723,.20,-1539),(720,.20,-1542),(717,.20,-1544)],[(714,.20,-1534),(716,.20,-1537),(719,.20,-1540)]]
 Path('build/city-exteriors/encore-tower-suites-canopy-samples.json').write_text(json.dumps(samples));Path('build/city-exteriors/encore-tower-suites-canopy-stairs.json').write_text(json.dumps(routes))
 return dict(key=KEY,name='Encore Tower Suites striped canopy',center=[718,0,-1540],bounds=list(p.bounds),structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
