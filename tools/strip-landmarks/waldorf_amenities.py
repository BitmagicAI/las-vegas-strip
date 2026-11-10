"""Original pool-deck study; official Pool_ICE_3 photograph and aerial in research.json.
Fit, levels and furniture counts are estimates; existing tower/interiors remain untouched.
"""
from common import *
from rio_amenities import AmenityMeshes
import waldorf_exterior as W
Y=27.1

def plan():
 tower=footprint(W.TOWER);garage=footprint(W.LOW[2])
 deck=garage.intersection(tower.buffer(30)).difference(tower.buffer(.3)).intersection(box(-210,1040,-100,1140))
 pools=[rotate(box(x-2.65,z-11.5,x+2.65,z+11.5),-20,origin=(x,z)) for x,z in [(-170,1065),(-160,1092)]]
 pools += [Point(-151,1117).buffer(1.6,quad_segs=16),Point(-144,1120).buffer(1.6,quad_segs=16),scale(Point(-134,1126).buffer(2.5,quad_segs=20),1.4,1)]
 assert all(deck.buffer(-.6).covers(p) for p in pools)
 return tower,deck,pools

def build(B):
 B.property='waldorfAmenities-exterior';B.source='waldorf-amenities';B.detail=0
 tower,deck,pools=plan();water=unary_union(pools)
 B.planar('wda-paving',deck.difference(water),Y,True);B.planar('wda_pool',water,Y-.14)
 B.planar('wda-tile',water,Y-1.1,True);B.shell(water,Y-1.1,Y,'wda-tile',roof=False,solid=True)
 B.planar('wda-coping',water.buffer(.3).difference(water),Y+.03,True)
 routes=[]
 for i,p in enumerate(parts(water.buffer(1.1,join_style=2))):
  ring=list(p.exterior.coords);assert deck.covers(LineString(ring).buffer(.42))
  routes.append(dict(name='waldorf-circuit-'+str(i),points=[[x,Y,z] for x,z in ring]))
 corridor=unary_union([LineString([(p[0],p[2]) for p in r['points']]).buffer(.8) for r in routes])
 used=[];counts=dict(cabanas=0,loungers=0,parasols=0);trees=[]
 def reserve(p):
  if not deck.buffer(-.4).contains(p) or water.buffer(2).intersects(p) or corridor.intersects(p) or any(p.intersects(q) for q in used):return False
  used.append(p.buffer(.15));return True
 # Flat white roofs, grey woven side screens and black furnished interiors seen in photo.
 for x,z in [(-170,1065),(-160,1092)]:
  centre=Frame(B,x,z,math.radians(20),y=Y)
  for zz in [-8,0,8]:
   px,_,pz=centre.p(-10.7,0,zz);F=Frame(B,px,pz,math.radians(20),y=Y)
   if not reserve(F.poly([(-2.3,-2.5),(2.3,-2.5),(2.3,2.5),(-2.3,2.5)])):continue
   for dx in [-2,2]:
    for dz in [-2.2,2.2]:F.box('wda-white',(dx,1.5,dz),(.1,3,.1),True)
   F.box('wda-white',(0,3.02,0),(4.35,.16,4.75))
   F.box('wda-screen',(-2.02,1.4,0),(.07,2.8,4.4),True)
   for dz in [-2.22,2.22]:F.box('wda-screen',(0,1.4,dz),(4,.07+2.73,.07),True)
   F.box('wda-dark',(-1.2,.5,0),(1,.4,3.3),True)
   F.box('wda-dark',(-1.55,.85,0),(.3,.6,3.3))
   F.box('wda-white',(.6,.5,0),(.75,.12,1.1),True);counts['cabanas']+=1
 # Double cushion loungers face each basin; narrow unobstructed perimeter paths preserved.
 for x,z in [(-170,1065),(-160,1092)]:
  centre=Frame(B,x,z,math.radians(20),y=Y)
  for side in [-1,1]:
   for zz in np.arange(-10,11,2.7):
    px,_,pz=centre.p(side*6.6,0,zz);F=Frame(B,px,pz,math.radians(20)+side*math.pi/2,y=Y)
    if not reserve(F.poly([(-.55,-1.15),(.55,-1.15),(.55,1.15),(-.55,1.15)])):continue
    F.box('wda-dark',(0,.22,0),(.85,.4,1.95),True);F.box('wda-cushion',(0,.46,.15),(.9,.18,1.7))
    B.face('wda-cushion',[F.p(-.45,.55,-.4),F.p(.45,.55,-.4),F.p(.45,1,-1),F.p(-.45,1,-1)])
    counts['loungers']+=1
 # Glass edge guards only on exposed perimeter, leaving retained tower connections clear.
 for poly in parts(deck):
  pts=list(poly.exterior.coords)
  for a,b in zip(pts,pts[1:]):
   if LineString([a,b]).distance(tower)<.6:continue
   B.face('wda-guard',[(a[0],Y,a[1]),(b[0],Y,b[1]),(b[0],Y+1.1,b[1]),(a[0],Y+1.1,a[1])],True)
   B.tube('wda-metal',(a[0],Y+1.12,a[1]),(b[0],Y+1.12,b[1]),.035,6)
 # Palm placement reservations, imported from existing foliage sources by exporter.
 for x,z in [(-181,1058),(-178,1074),(-175,1086),(-169,1100),(-157,1112),(-121,1130)]:
  p=Point(x,z).buffer(.8,quad_segs=12)
  if reserve(p):
   B.lathe('wda-white',(x,z),[(Y,.65),(Y+.3,.85),(Y+1,.65)],16)
   trees.append(dict(p=[x,Y+.7,z],height=6))
 record=Path('docs/project-records/waldorf-hgv-amenities')
 (record/'waldorf-routes.json').write_text(json.dumps(routes,indent=2)+'\n')
 (record/'waldorf-geometry.json').write_text(json.dumps(dict(**counts,basinAreasM2=[p.area for p in pools],foliagePlacements=trees,limitations=['Approximate basin fit, furniture and elevations; not installed or visually accepted.']),indent=2)+'\n')
 return counts

if __name__=='__main__':
 B=AmenityMeshes();print(build(B));B.save_all()
