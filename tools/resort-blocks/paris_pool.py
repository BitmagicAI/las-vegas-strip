"""Exterior pool terrace: photo-fitted radial layout, original authored furniture.
All furnishings are static exterior batches; nothing waits for an interior load.
"""
import math,random
import numpy as np
from shapely.geometry import Polygon,Point,LineString
from shapely.ops import unary_union
from common import Frame, parts

def build(c,area):
 b,F,source,P,slab,rail=[c[k] for k in ['b','F','source','P','slab','rail']]
 cx,cz=135,387;R=21.8
 vertices=[(cx+R*math.cos(a),cz+R*math.sin(a)) for a in np.arange(8)*math.pi/4+math.pi/8]
 outline=Polygon(vertices)
 # Small inset corners and stone islands distinguish this pool from a plain disc.
 pool=outline.difference(unary_union([Point(x,z).buffer(1.65,quad_segs=6) for x,z in vertices]))
 source('podium-pool-deck');slab(area.difference(pool.buffer(.6)),P,'paris-pool-paving')
 # Continuous actual basin floor and walls, water sits below rounded coping.
 b.planar('paris-pool-tile',pool,P-1.2,True);b.shell(pool,P-1.2,P-.12,'paris-pool-tile',roof=False,solid=True)
 b.planar('paris-water',pool,P-.15)
 coping=pool.buffer(.65,join_style=2).difference(pool)
 b.shell(coping,P-.12,P+.08,'paris-cream',roof=False,solid=False);b.planar('paris-cream',coping,P+.08)
 # Radial limestone fans and contrasting fine joint bands are flush overlays.
 for j in range(8):
  a=(j+.5)*math.pi/4
  sector=Polygon([(cx,cz),(cx+100*math.cos(a-.028),cz+100*math.sin(a-.028)),(cx+100*math.cos(a+.028),cz+100*math.sin(a+.028))])
  b.planar('paris-pool-band',sector.intersection(area).difference(pool.buffer(.72)),P+.006)
 for r in [26.2,31.5,37.1]:
  outer=Polygon([(cx+r*math.cos(a),cz+r*math.sin(a)) for a in np.arange(8)*math.pi/4+math.pi/8])
  b.planar('paris-pool-band',outer.buffer(.08,join_style=2).difference(outer.buffer(-.08,join_style=2)).intersection(area),P+.008)
 # Inset pedestal urns along the octagon. A low plinth fits within the corner cut.
 source('podium-pool-urns')
 for x,z in vertices:
  f=F(x,z,P);f.box('paris-cream',(0,.16,0),(1.6,.32,1.6));f.box('paris-ivory',(0,.63,0),(1.05,.75,1.05))
  f.lathe('paris-cream',0,0,[(1,.47),(1.13,.55),(1.2,.36),(1.38,.32),(1.9,.65),(2.05,.72),(2.15,.67)],24)
  b.sphere('paris-pool-leaf',(x,P+2.19,z),.56,12,7,scale=(1,.35,1))
 # Walk routes reserve physical clearance through both furniture and greenery.
 paths=[[(68,412.5),(112,412.5),(120,419),(158,419),(158,349),(112,349),(112,414),(120,414)]]
 clearance=unary_union([LineString(p).buffer(1.3) for p in paths])
 usable=area.buffer(-1.1).difference(pool.buffer(1.3)).difference(clearance)
 def fits(f,w,d):return usable.covers(f.poly([(-w/2,-d/2),(w/2,-d/2),(w/2,d/2),(-w/2,d/2)]))
 def lounger(f):
  # Four-leg dark frame, curved slatted chaise, pale cushion and folded towel.
  for x in [-.38,.38]:
   f.path('paris-pool-frame',[(x,.08,-.85),(x,.39,-.7),(x,.39,.48),(x,.88,1.03)],.035,6)
   for z in [-.7,.5]:f.tube('paris-pool-frame',(x,.1,z),(x,.43,z),.03,6)
  f.box('paris-pool-cushion',(0,.44,-.1),(.75,.13,1.4))
  b.face('paris-pool-cushion',[f.p(-.375,.48,.57),f.p(.375,.48,.57),f.p(.375,.95,1.08),f.p(-.375,.95,1.08)])
  f.box('paris-blue',(0,.53,-.47),(.78,.035,.30))
  for z in [-.7,.2]:f.tube('paris-pool-frame',(-.4,.39,z),(.4,.39,z),.025,5)
 count=0;source('pool-loungers',1)
 # Each side of the octagon gets two staggered runs, oriented to the water.
 for j in range(8):
  a=j*math.pi/4
  normal=(math.cos(a),math.sin(a));tangent=(-normal[1],normal[0])
  for distance in [24.4,28.0]:
   for offset in np.arange(-7.2,8,1.15):
    x,z=cx+distance*normal[0]+offset*tangent[0],cz+distance*normal[1]+offset*tangent[1]
    f=F(x,z,P,math.pi/2-a)
    if fits(f,.95,2.3):lounger(f);count+=1
 # White tensile cabanas with scalloped valances and tied-back curtains.
 cabanas=0
 for a in np.arange(0,math.tau,math.pi/8):
  x,z=cx+35.6*math.cos(a),cz+35.6*math.sin(a);f=F(x,z,P,math.pi/2-a)
  if not fits(f,4.5,3.6):continue
  cabanas+=1;source('podium-pool-cabanas')
  for xx in [-2,2]:
   for zz in [-1.5,1.5]:
    f.box('paris-pool-frame',(xx,1.42,zz),(.075,2.84,.075))
    f.box('paris-pool-cushion',(xx,1.35,zz),(.24,2.65,.28))
  roof=[(-2.25,2.9,-1.75),(2.25,2.9,-1.75),(2.25,2.9,1.75),(-2.25,2.9,1.75)]
  for i in range(4):b.face('paris-pool-cushion',[f.p(*roof[i]),f.p(*roof[(i+1)%4]),f.p(0,3.65,0)])
  for zz in [-1.75,1.75]:f.box('paris-pool-cushion',(0,2.82,zz),(4.5,.24,.05))
  for xx in [-2.25,2.25]:f.box('paris-pool-cushion',(xx,2.82,0),(.05,.24,3.5))
  source('pool-cabana-furnishings',1)
  f.box('paris-pool-frame',(0,.26,.3),(3.4,.52,1.9));f.box('paris-pool-cushion',(0,.6,.3),(3.38,.18,1.88))
  for xx in [-1,.0,1]:f.box('paris-pool-cushion',(xx,.86,1.0),(.84,.52,.24))
  f.box('paris-pool-frame',(0,.23,-1.05),(.85,.46,.6))
 # Perimeter planted beds, mature branched trees and layered dark shrubs.
 rng=random.Random(2410);source('podium-pool-gardens')
 beds=[]
 for a in np.arange(0,math.tau,math.pi/12):
  x,z=cx+40.2*math.cos(a),cz+40.2*math.sin(a)
  bed=Point(x,z).buffer(3.1,quad_segs=4).intersection(usable)
  if bed.area<13:continue
  beds.append(bed);slab(bed,P+.13,'paris-pool-soil',False)
  f=F(x,z,P);f.lathe('bark',0,0,[(.1,.23),(2.7,.17),(5,.09)],9)
  for j in range(6):
   t=j*2.4;dx=math.cos(t)*(1.2+j*.15);dz=math.sin(t)*(1.2+j*.15)
   f.tube('bark',(0,2.2+j*.22,0),(dx,4.2+j*.25,dz),.085,6)
   for k in range(3):
    q=f.p(dx+rng.uniform(-.6,.6),4.4+j*.23+rng.uniform(-.4,.5),dz+rng.uniform(-.6,.6))
    b.sphere('paris-pool-leaf' if (j+k)%3 else 'paris-leaf',q,1.25+rng.random()*.5,9,6,scale=(1,.75,1))
  for j in range(9):
   a=j*math.tau/9;xx=x+2.1*math.cos(a);zz=z+2.1*math.sin(a)
   if bed.contains(Point(xx,zz)):b.sphere('paris-pool-hedge',(xx,P+.6,zz),.75,9,5,scale=(1,.65,1))
 # Formal low hedges divide cabana bays without individual collision bodies.
 source('pool-garden-detail',1)
 for bed in beds:
  for poly in parts(bed):
   for x,z in list(poly.exterior.coords)[::2]:b.sphere('paris-pool-hedge',(x,P+.45,z),.48,8,5)
 source('podium-pool-boundary')
 for a,z in [((93,342),(182,342)),((182,342),(182,437)),((93,437),(93,415)),((93,410),(93,342))]:rail(a,z,P,True)
 return pool,dict(center=[cx,P,cz],waterHeight=P-.15,basinDepth=1.2,loungers=count,cabanas=cabanas,plantedBeds=len(beds),outdoorResidency='permanent exterior / spatial LOD; no indoor proximity gate',layoutConfidence='photo fitted; intermediate dimensions and furniture arrangement estimated')
