"""Original private courtyard study from official pool photo and linked aerial.

Metre estimates, not a surveyed plan. Hotel, arrival and GO Pool are separate owners.
"""
from common import *
from rio_amenities import AmenityMeshes
import hgv_flamingo_exterior as H

Y=.27

def plan():
 occupied=unary_union([r['shape'] for r in H.records()])
 deck=box(314,-135,354,-99).difference(occupied.buffer(.35))
 # Zoom20 aerial fit: long north/south basin, west bulge and east shallow step.
 pool=box(323.5,-123,329,-110).union(Point(323.8,-116.5).buffer(2.4,quad_segs=12)).union(box(328,-119,330,-114))
 pool=pool.buffer(.3,join_style=1).buffer(-.3,join_style=1)
 spa=Point(336,-116.7).buffer(1.65,quad_segs=20)
 terrace=box(340,-133,352,-101).intersection(deck)
 return occupied,deck,pool,spa,terrace

def build(B):
 B.property='hgvFlamingoAmenities-exterior';B.source='hgv-flamingo-amenities';B.detail=0
 occupied,deck,pool,spa,terrace=plan();water=pool.union(spa)
 stair=box(337,-105,340,-101)
 B.planar('ha-paving',deck.difference(water).difference(terrace).difference(stair),Y,True)
 B.planar('ha_pool',water,Y-.12)
 B.planar('ha-tile',water,Y-1.05,True);B.shell(water,Y-1.05,Y,'ha-tile',roof=False,solid=True)
 B.planar('ha-coping',water.buffer(.28).difference(water),Y+.035,True)
 # Raised east terrace: photographic riser count supports an estimated .85 m rise.
 upper=Y+.85
 B.planar('ha-paving',terrace,upper,True)
 B.shell(terrace,Y,upper,'ha-stone',openings=[dict(p=[340,Y,-103],width=4.1,height=1.2)],roof=False,solid=True)
 Frame(B,337,-103,math.pi/2,y=Y).stairs(0,0,4,.85,3)
 counts=dict(pavilions=0,loungers=0,parasols=0)
 reserved=[]
 for x,z in [(346,-128),(346,-119),(346,-109)]:
  F=Frame(B,x,z,0,y=upper);reserved.append(box(x-2.9,z-2.9,x+2.9,z+2.9))
  for dx in [-2.05,2.05]:
   for dz in [-2.05,2.05]:
    F.box('ha-stone',(dx,.3,dz),(.55,.6,.55),True)
    F.box('ha-white',(dx,1.65,dz),(.36,2.7,.36),True)
  for dx in [-2.25,2.25]:F.box('ha-white',(dx,3.05,0),(.25,.22,4.65))
  for dz in [-2.25,2.25]:F.box('ha-white',(0,3.05,dz),(4.65,.22,.25))
  corners=[(-2.55,3.15,-2.55),(2.55,3.15,-2.55),(2.55,3.15,2.55),(-2.55,3.15,2.55)]
  for a,b in zip(corners,corners[1:]+corners[:1]):B.face('ha-roof',[F.p(*a),F.p(*b),F.p(0,4.15,0)])
  F.box('ha-wood',(0,.72,0),(1.2,.12,1.2),True)
  for dx in [-1.1,1.1]:F.box('ha-wood',(dx,.46,0),(.55,.12,.6),True)
  counts['pavilions']+=1
 routes=[]
 for name,p in [('pool',pool),('spa',spa)]:
  ring=list(p.buffer(1.05,join_style=1).simplify(.15).exterior.coords)
  assert deck.difference(terrace).covers(LineString(ring).buffer(.42))
  routes.append(dict(name='hgv-'+name,points=[[x,Y,z] for x,z in ring]))
 routes.append(dict(name='hgv-terrace-stair',points=[[334,Y,-103],[337,Y,-103],[340,upper,-103],[341,upper,-103],[341,upper,-131]]))
 corridor=unary_union([LineString([(p[0],p[2]) for p in r['points']]).buffer(.8) for r in routes])
 available=deck.difference(water.buffer(2)).difference(terrace).difference(stair).difference(corridor)
 def lounger(x,z,yaw=0):
  F=Frame(B,x,z,yaw,y=Y)
  for dx in [-.34,.34]:F.box('ha-frame',(dx,.35,0),(.035,.08,1.95))
  for dx in [-.28,.28]:
   for dz in [-.65,.6]:F.box('ha-frame',(dx,.18,dz),(.045,.36,.045),True)
  for zz in np.arange(-.25,.95,.15):F.box('ha-wood',(0,.4,zz),(.67,.035,.1))
  for t in np.arange(0,1,.16):
   zz=-.3-t*.65;yy=.42+t*.55
   F.box('ha-wood',(0,yy,zz),(.67,.06,.1))
  counts['loungers']+=1
 for x in [317.5,320,332.5,335.5]:
  for z in np.arange(-131,-101,3):
   p=box(x-.6,z-1.2,x+.6,z+1.2)
   if not available.contains(p):continue
   lounger(x,z);reserved.append(p)
   if counts['loungers']%4==0:
    xx=x+.8;B.box('ha-frame',(xx,Y+1.15,z),(.045,2.3,.045))
    for j in range(10):
     a=j*math.tau/10;b=(j+1)*math.tau/10
     B.face('ha-lime',[(xx,Y+2.75,z),(xx+1.05*math.cos(a),Y+2.3,z+1.05*math.sin(a)),(xx+1.05*math.cos(b),Y+2.3,z+1.05*math.sin(b))])
    counts['parasols']+=1
 # Blue handrails seen in the official photo, kept outside perimeter walk centreline.
 for z in [-121,-112]:
  for x in [324.4,325.2]:B.path('ha-blue',[(x,Y+.05,z-1),(x,Y+.8,z-.8),(x,Y+.85,z),(x,Y-.3,z+.5)],.035,8)
 # Pebble beds reserve positions for existing foliage-source imports at export time.
 trees=[]
 for x,z,h in [(315.5,-131,7),(315.7,-124,8),(315.4,-115,6),(315.8,-106,8),(350,-133,6),(351,-115,7)]:
  p=Point(x,z).buffer(.85,quad_segs=12)
  if not deck.contains(p) or corridor.intersects(p) or any(p.intersects(q) for q in reserved):continue
  yy=upper if terrace.contains(p) else Y
  B.planar('ha-pebbles',p,yy+.025);trees.append(dict(p=[x,yy,z],height=h))
 record=Path('docs/project-records/waldorf-hgv-amenities')
 (record/'hgv-routes.json').write_text(json.dumps(routes,indent=2)+'\n')
 (record/'hgv-geometry.json').write_text(json.dumps(dict(**counts,poolAreaM2=pool.area,spaAreaM2=spa.area,terraceRiseM=.85,foliagePlacements=trees,limitations=['Aerial fit and terrace elevation estimated; foliage imports pending; not installed or walked.']),indent=2)+'\n')
 return counts

if __name__=='__main__':
 B=AmenityMeshes();print(build(B));B.save_all()
