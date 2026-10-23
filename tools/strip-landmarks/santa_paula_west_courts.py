"""Seven mapped single-storey duplex/courtyard buildings; January2026 reference.
Doors and roof pitch are estimates, not a surveyed interior plan.
"""
from common import *
from forum_shops import facade_frame
from rexford_place_west import window
from courtyard_525 import palm
KEY='santaPaulaWestCourts'
IDS=['way/'+str(v) for v in [1236725793,1236725792,1236725794,1236725778,1236725782,1236725776,1236725775]]
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/santa-paula-west-courts';B.detail=0
 ps=[footprint(i)for i in IDS];whole=unary_union(ps);samples=[];routes=[];trees=[];W=Frame(B,0,0,y=0)
 yard=unary_union([box(1958,-3748,1975,-3692),box(1936,-3692,1973,-3610),box(1910,-3644,1936,-3610)]).difference(whole)
 B.planar('rpw-concrete',yard,.18,True)
 for idx,p in enumerate(ps):
  B.shell(p,.18,2.95,'rpw-'+('white' if idx==0 else 'tan')+'-stucco',roof=False)
  roof=p.buffer(.28,join_style=2);outer=roof;level=0;slope=.22
  mat='bt-roof-paint' if idx==0 else ('terracotta' if idx==1 else 'rpw-gray-roof-paint')
  while not outer.is_empty and level<64:
   inner=roof.buffer(-(level+.4),join_style=2)
   for poly in parts(outer.difference(inner)):
    for t in triangles(poly):B.upface(mat,[(x,3+roof.boundary.distance(Point(x,z))*slope,z)for x,z in list(t.exterior.coords)[:-1]],True)
   outer=inner;level+=.4
  edges=[facade_frame(B,a,b,p,0)for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:])]
  front=[e for e in edges if (e[3]>.6 if idx==2 else e[2]>.6)]
  F,L,_,_=max(front,key=lambda e:e[1]);n=max(1,int(L/8));bay=L/n
  for G,ll,nx,nz in edges:
   G.box('hs-red-fascia-paint',(ll/2,2.98,-.11),(ll,.16,.42));G.box('rpw-plinth-paint',(ll/2,.31,-.025),(ll,.26,.08))
   if G is F:
    for j in range(n):
     u=(j+.52)*bay;wu=(j+.22)*bay
     G.box('rpw-door-trim-paint',(u,1.25,-.07),(1.04,2.14,.15));G.box('rpw-door-paint',(u,1.25,-.16),(.88,1.99,.04));G.box('rpw-hardware-paint',(u+.31,1.2,-.2),(.04,.14,.04))
     window(G,wu,w=min(2.2,bay*.3))
     G.box('rpw-awning-paint',(u,2.61,-.85),(2.2,.09,1.7))
     for v in [u-1,u+1]:G.box('rpw-post-paint',(v,1.4,-1.55),(.07,2.44,.07),True)
     approach=G.poly([(u-.7,0),(u+.7,0),(u+.7,-3),(u-.7,-3)]).difference(whole)
     B.planar('rpw-concrete',approach,.18,True)
     routes.append([G.p(u,.18,-2.8),G.p(u,.18,-1.8),G.p(u,.18,-.55)])
   elif ll>4:
    for u in np.arange(2,ll-1,5):window(G,float(u),w=1.3)
  B.planar('rpw-concrete',p.buffer(.4,join_style=2).difference(p),.18,True)
  for x in np.arange(p.bounds[0]+.5,p.bounds[2],1.2):
   for z in np.arange(p.bounds[1]+.5,p.bounds[3],1.2):
    if p.buffer(-.3).contains(Point(x,z)):samples.append([float(x),3+roof.boundary.distance(Point(x,z))*slope+.4,float(z)])
  for k in range(max(1,int(p.area/120))):
   x=p.bounds[0]+(k+1)*(p.bounds[2]-p.bounds[0])/(max(1,int(p.area/120))+1);z=p.centroid.y
   if not p.buffer(-1).contains(Point(x,z)):continue
   y=3+roof.boundary.distance(Point(x,z))*slope
   W.box('rpw-service-paint',(x,y+.35,z),(1,.7,1));W.box('rpw-vent-paint',(x,y+.71,z),(.9,.025,.9))
 # Marked concrete parking court, clear paths around its perimeter.
 for z in np.arange(-3688,-3648,2.8):W.box('rpw-frame-paint',(1968,.195,float(z)),(4.4,.015,.08))
 for x,z,h in [(1966,-3728,5.4),(1953,-3658,6.5),(1916,-3624,4.8)]:trees.append([x,z,h,.7])
 palm(B,W,1969,-3739,2.8)
 B.groups={k:g for k,g in B.groups.items()if g['material']!='c525-collision'}
 Path('build/city-exteriors/santa-paula-west-courts-samples.json').write_text(json.dumps(samples));Path('build/city-exteriors/santa-paula-west-courts-stairs.json').write_text(json.dumps(routes));Path('build/city-exteriors/santa-paula-west-courts-trees.json').write_text(json.dumps(trees))
 return dict(key=KEY,name='Santa Paula west courtyard homes',center=[1948,0,-3680],bounds=list(whole.union(yard).buffer(2).bounds),structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
