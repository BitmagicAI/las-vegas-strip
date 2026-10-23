"""Palazzo deck from official Feb2026 diagram and 2020 aerial.
Registration/elevation estimated on mapped podium; no as-built accuracy claim.
"""
import math
import numpy as np
from shapely.geometry import Point,Polygon,box,LineString
from shapely.ops import unary_union
from common import Frame,footprint,parts

def pools(B):
 B.source='palazzo-pool-deck';B.detail=0;y=14.55
 def w(x,z):return (338+(z-250)*.18,-818-(x-140)*.20)
 def poly(q):return Polygon([w(*a) for a in q])
 def slab(mat,p,lo,hi,solid=True):B.shell(p,lo,hi,mat,roof=False,solid=solid);B.planar(mat,p,hi,solid)
 def oval(x,z,rx,rz):return poly([(x+rx*math.cos(a),z+rz*math.sin(a)) for a in np.linspace(0,math.tau,65)[:-1]])
 def rounded(x,z,xx,zz,r):
  # Trace radius corners in map space; flat sides retained.
  points=[]
  for cx,cz,start in [(xx-r,zz-r,0),(x+r,zz-r,90),(x+r,z+r,180),(xx-r,z+r,270)]:
   for a in np.linspace(start,start+90,9):points.append((cx+r*math.cos(math.radians(a)),cz+r*math.sin(math.radians(a))))
  return poly(points)
 basins=[rounded(797,308,833,332,5),rounded(834,361,861,398,7),rounded(840,405,856,437,7),rounded(822,478,873,554,23),rounded(586,570,709,615,21),rounded(474,508,503,565,13),rounded(247,520,427,543,10)]
 # Paired curved end bays on the largest pool are retained in the water outline.
 deck=poly([(206,505),(240,481),(456,480),(456,461),(763,461),(763,282),(900,282),(932,601),(909,632),(754,650),(679,718),(599,718),(586,674),(456,642),(392,645),(392,617),(243,611),(206,580)])
 site=footprint('way/180584269').buffer(-1)
 tower=footprint('way/30424125').buffer(1.5)
 deck=deck.intersection(site).difference(tower)
 original_areas=[b.area for b in basins]
 basins=[b.intersection(deck.buffer(-1)) for b in basins]
 assert all(b.area > .98*a for b,a in zip(basins,original_areas)), 'Pool registration clips basin; revise placement'
 wet=unary_union(basins)
 slab('marble',deck.difference(wet),13.05,y)
 for b in basins:
  B.planar('water',b,y-.18);B.planar('blue2',b,y-1.12,True);B.shell(b,y-1.12,y-.18,'tile',roof=False)
  slab('ivory',b.buffer(.32).difference(b),y-.1,y+.08)
  # Inlaid border and rings live on the basin floor, under the water.
  B.detail=1
  B.planar('ivory',b.buffer(-.65).difference(b.buffer(-.77)),y-1.10)
  cx,cz=b.centroid.coords[0]
  for r in [1.3,2.1,2.3]:
   ring=Point(cx,cz).buffer(r,quad_segs=24).difference(Point(cx,cz).buffer(r-.10,quad_segs=24)).intersection(b.buffer(-.5))
   B.planar('blue',ring,y-1.095)
  B.detail=0
 # Mapped cabanas. Roof pavilions and furniture share resort material batches.
 reserved=[]
 for px,pz in [(260,493),(284,493),(389,493),(415,493),(477,493),(500,493),(552,490),(576,490),(601,490),(626,490),(682,490),(706,490),(730,490),(754,490),(906,478),(906,514),(906,554),(873,601),(833,601),(791,286),(815,286),(839,286)]:
  x,z=w(px,pz);area=box(x-1.7,z-1.7,x+1.7,z+1.7)
  if not deck.covers(area) or wet.buffer(.6).intersects(area):continue
  reserved.append(area.buffer(.6));T=Frame(B,x,z,y=y)
  T.floor(3.4,3.4,mat='tile',y=.04)
  for sx in [-1,1]:
   for sz in [-1,1]:T.box('ivory',(sx*1.5,1.35,sz*1.5),(.18,2.7,.18),True)
  T.box('white',(0,2.7,0),(3.7,.15,3.7));T.box('white',(0,.4,0),(2,.45,1.7))
  B.detail=1
  for sx in [-1,1]:T.box('white',(sx*1.36,1.5,1.42),(.3,2.4,.08))
  B.detail=0
 # Capri terrace pavilion: shallow curved colonnade oriented to central pool.
 x,z=w(650,679);T=Frame(B,x,z,y=y)
 for a in np.linspace(.1,math.pi-.1,15):
  xx,zz=9*math.cos(a),9*math.sin(a)
  T.lathe('ivory',xx,zz,[(0,.30),(.2,.34),(3.2,.23),(3.5,.34)],12)
 T.path('ivory',[(9*math.cos(a),3.55,9*math.sin(a)) for a in np.linspace(0,math.pi,49)],.23,8)
 B.detail=1
 for a in np.linspace(0,math.pi,42):T.tube('walnut',(7.5*math.cos(a),3.65,7.5*math.sin(a)),(10.3*math.cos(a),3.65,10.3*math.sin(a)),.055,5)
 # Reference garden: domed pavilions and palms in planting islands.
 # Exact species/positions are provisional; exclude water, cabanas and tower.
 from venetian_pool_garden import gardens
 reserved.extend(gardens(B,deck,wet.union(unary_union(reserved)),lambda q:w(*q),y,
  [(270,584),(315,584),(360,584),(400,584),(460,607),(506,590),
   (548,554),(575,635),(726,629),(761,576),(784,496),(787,540),
   (887,464),(899,588),(813,351),(877,365),(877,418),(617,655),(694,670)],crown_clearance=3.5))
 for px,pz,r in [(650,679,3.0),(763,603,2.25)]:
  xx,zz=w(px,pz);site=Point(xx,zz).buffer(r+1)
  if not deck.covers(site) or wet.buffer(.5).intersects(site) or any(a.intersects(site) for a in reserved):continue
  reserved.append(site.buffer(.5));T=Frame(B,xx,zz,y=y);B.detail=0
  T.lathe('ivory',0,0,[(0,r+.4),(.2,r+.4),(.3,r+.2)],32)
  for a in np.linspace(0,math.tau,9)[:-1]:
   T.lathe('ivory',r*.86*math.cos(a),r*.86*math.sin(a),[(.3,.19),(2.8,.16),(3,.23)],12)
  T.lathe('ivory',0,0,[(2.9,r+.3),(3.1,r+.3),(3.2,r)],40)
  T.lathe('sage',0,0,[(3.2+r*.65*math.sin(a),r*math.cos(a)) for a in np.linspace(0,math.pi/2,17)],48)
  B.detail=1
  for a in np.linspace(0,math.tau,25)[:-1]:
   T.path('sage',[(r*math.cos(t)*math.cos(a),3.22+r*.65*math.sin(t),r*math.cos(t)*math.sin(a)) for t in np.linspace(0,math.pi/2,17)],.025,4)
  T.lathe('ivory',0,0,[(3.2+r*.65,.1),(3.5+r*.65,.07),(3.65+r*.65,0)],10)
 B.detail=1
 # Chairs placed in diagram's banks, clear of pools/pavilion footprints.
 for xa,xb,za,zb in [(264,422,552,562),(532,634,515,546),(680,715,513,546),(590,709,623,649),(806,814,477,552)]:
  for px in np.arange(xa,xb,5.5):
   for pz in np.arange(za,zb,13):
    x,z=w(px,pz);area=box(x-1.2,z-1.2,x+1.2,z+1.2)
    if not deck.covers(area) or wet.buffer(.5).intersects(area) or any(a.intersects(area) for a in reserved):continue
    T=Frame(B,x,z,math.pi/2,y=y)
    T.box('white',(0,.4,0),(.72,.1,1.5));B.face('white',[T.p(-.36,.44,-.7),T.p(.36,.44,-.7),T.p(.36,.98,-1.1),T.p(-.36,.98,-1.1)])
    for sx in [-1,1]:T.tube('blackiron',(sx*.3,.06,.6),(sx*.3,.4,.6),.03,5);T.tube('blackiron',(sx*.3,.06,-.6),(sx*.3,.4,-.6),.03,5)
 B.detail=0
 for pp in parts(deck):
  pts=list(pp.exterior.coords)
  for a,b in zip(pts,pts[1:]):B.face('ivory',[(a[0],y,a[1]),(b[0],y,b[1]),(b[0],y+1.1,b[1]),(a[0],y+1.1,a[1])],True)
 return dict(eye=[320,65,-1010],target=[400,15,-930])
