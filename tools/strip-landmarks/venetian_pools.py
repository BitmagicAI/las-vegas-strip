"""Main Venetian roof deck from official February 2026 pool map.
Map pixels fitted to inherited podium; position/elevation are estimates, not survey.
Independent exterior geometry only; no interior doors or lights are generated.
"""
import math
import numpy as np
from shapely.geometry import Polygon,box,Point
from shapely.ops import unary_union
from common import Frame,footprint

def main_deck(B):
 B.source='venetian-main-pool';B.detail=0
 def slab(mat,shape,lo,hi,solid=True):
  # Constrained triangulation preserves concave boundaries and basin holes.
  B.shell(shape,lo,hi,mat,roof=False,solid=solid)
  B.planar(mat,shape,hi,solid)
 # 2026 official map pixel-to-world registration. North is provisional; site fit
 # is constrained to existing north podium, with 2m tower clearance.
 def world(p):return (262+(p[0]-160)*.22,-793+(p[1]-330)*.22)
 def poly(points):return Polygon([world(p) for p in points])
 outlines=[[(228,373),(375,373),(375,389),(398,389),(398,416),(228,416)],[(245,503),(373,503),(373,514),(398,514),(398,560),(278,560),(278,539),(245,539)],[(580,400),(665,400),(665,503),(580,503)],[(713,390),(745,390),(745,475),(757,475),(757,536),(734,536),(734,509),(713,509)]]
 pools=[poly(q) for q in outlines];wet=unary_union(pools)
 deck=poly([(160,420),(209,420),(209,330),(479,330),(479,300),(534,300),(534,360),(682,360),(682,340),(805,340),(805,440),(880,440),(880,497),(650,716),(612,740),(570,716),(160,716)])
 site=footprint('relation/7770314').buffer(-1.5)
 towers=unary_union([footprint('way/30618090'),footprint('way/111322067')]).buffer(2)
 deck=deck.intersection(site).difference(towers)
 y=18.55
 slab('marble',deck.difference(wet.buffer(.50)),17.04,y,True)
 for pool in pools:
  pool=pool.intersection(deck)
  B.planar('water',pool,y-.17)
  B.planar('blue',pool,y-1.25,True)
  slab('ivory',pool.buffer(.5).difference(pool),y-.2,y+.03,True)
  # Real below-water walls preserve a recessed basin instead of a blue decal.
  B.shell(pool,y-1.25,y-.17,'tile',roof=False)
  a,b,c,d=pool.bounds
  for k in range(4):slab('ivory',box(a+.7,b+.7,a+4.4,b+1.3+k*.5),y-.35-k*.25,y-.10-k*.25,True)
 # Main #2 pool's four raised daybeds in its center.
 x,z=world((622,453));F=Frame(B,x,z,y=y)
 for a in [-1.35,1.35]:
  for b in [-1.8,1.8]:F.box('ivory',(a,.10,b),(2.5,.3,3.4),True);F.box('white',(a,.34,b),(2.3,.16,3.2))
 from venetian_pool_garden import gardens
 reserved=gardens(B,deck,wet,world,y)
 # Dense rows from mapped chair banks; preserve at least 1.4m circulation.
 B.detail=1
 def chair(px,py,yaw=0):
  x,z=world((px,py))
  if not deck.buffer(-1).contains(Point(x,z)) or wet.buffer(1.3).contains(Point(x,z)) or any(q.intersects(box(x-.55,z-1.2,x+.55,z+1.2)) for q in reserved):return
  T=Frame(B,x,z,yaw,y=y+.04)
  T.box('white',(0,.44,.25),(.72,.09,1.45))
  B.face('white',[T.p(-.36,.48,-.48),T.p(.36,.48,-.48),T.p(.36,1.05,-1.04),T.p(-.36,1.05,-1.04)])
  for s in [-1,1]:
   T.tube('charcoal',(s*.34,.15,.9),(s*.34,.47,.9),.035,5);T.tube('charcoal',(s*.34,.15,-.6),(s*.34,.48,-.6),.035,5)
   T.tube('charcoal',(s*.36,.45,.95),(s*.36,.46,-.48),.025,5);T.tube('charcoal',(s*.36,.46,-.48),(s*.36,1.07,-1.06),.025,5)
  T.box('blue',(0,.50,.38),(.38,.025,.28))
 for xa,xb,ya,yb in [(238,389,432,487),(280,393,570,611),(551,562,390,521),(587,663,381,389),(676,688,400,520),(773,804,452,527),(704,753,551,572)]:
  for xx in np.arange(xa,xb,5.4):
   for zz in np.arange(ya,yb,12):chair(xx,zz)
 B.detail=0
 # Six shallow cabana rooms at the north edge, open toward the pools.
 for px in [238,264,289,315,341,367]:
  x,z=world((px,349));T=Frame(B,x,z,y=y)
  T.box('plaster',(0,1.75,-1.25),(5.1,3.5,.25),True)
  for s in [-1,1]:T.box('ivory',(s*2.45,1.75,0),(.25,3.5,2.7),True)
  T.box('ivory',(0,3.65,0),(5.35,.30,3.1));T.arch(0,1.5,3.5,3.5,'ivory',.15)
  T.box('darkglass',(0,1.45,-1.08),(4.6,2.8,.05))
  B.detail=1
  for k in range(16):
   xx=-1.9+k*.24
   B.face('ivory' if k%2 else 'charcoal',[T.p(xx,3.15,1.5),T.p(xx+.24,3.15,1.5),T.p(xx+.24,2.6,2.65),T.p(xx,2.6,2.65)])
  B.detail=0
 # Spritz outdoor pavilion: estimated envelope from official plan.
 x,z=world((340,674));T=Frame(B,x,z,y=y);T.floor(34,12,0,'tile')
 for xx in [-16,-8,0,8,16]:
  for zz in [-5.6,5.6]:T.box('ivory',(xx,2.1,zz),(.45,4.2,.45),True)
 for side in [-1,1]:B.face('terracotta',[T.p(-17,4.1,side*6.5),T.p(17,4.1,side*6.5),T.p(17,5.4,0),T.p(-17,5.4,0)])
 B.detail=1
 for xx in [-12,-6,0,6,12]:
  for zz in [-3,3]:
   T.lathe('ivory',xx,zz,[(0,.12),(.7,.12),(.75,.65),(.82,.65)],12)
 B.detail=0
 # Physical perimeter parapet keeps the roof edge safe; fine copings are batched.
 for ring in [q.exterior for q in ([deck] if deck.geom_type=='Polygon' else deck.geoms)]:
  pts=list(ring.coords)
  for a,b in zip(pts,pts[1:]):
   B.face('ivory',[(a[0],y,a[1]),(b[0],y,b[1]),(b[0],y+1.08,b[1]),(a[0],y+1.08,a[1])],True)
   B.tube('ivory',(a[0],y+1.1,a[1]),(b[0],y+1.1,b[1]),.10,6)
 return dict(eye=[280,21,-750],target=[390,20,-752])
