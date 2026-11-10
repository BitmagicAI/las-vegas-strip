"""Original Rio pool furniture and landscape study. Official 2025 map/photo links in the record.

Existing basin registration is approximate. This source does not regenerate towers or interiors.
"""
from common import *
import rio_exterior as R

Y=.32
class AmenityMeshes(Meshes):
 def upface(self,mat,pts,solid=False):
  # Polygon triangulation can return a collinear boundary sliver.
  a=np.array(pts,float)
  if np.linalg.norm(np.cross(a[1]-a[0],a[2]-a[0]))<1e-8:return
  super().upface(mat,pts,solid)

def plan():
 occupied=unary_union([r['shape'] for r in R.records()])
 deck=Polygon([(-1298,-141),(-1237,-211),(-1172,-220),(-1137,-197),(-1137,-124),(-1240,-120)]).difference(occupied.buffer(.35))
 outlines=[[(706,285),(729,270),(760,278),(788,275),(826,285),(838,300),(826,318),(828,333),(807,341),(793,337),(785,326),(759,330),(743,324),(736,304),(714,306)],[(630,421),(650,414),(673,428),(676,446),(687,456),(680,474),(685,490),(674,506),(675,521),(659,529),(646,518),(635,519),(626,503),(624,480),(610,468),(618,453)],[(552,380),(573,368),(596,365),(615,373),(622,387),(616,400),(601,406),(595,420),(580,421),(565,409)],[(410,427),(431,422),(446,430),(438,442),(419,449),(410,464),(414,482),(431,491),(432,505),(416,512),(400,503),(389,484),(386,462),(395,442)]]
 pools=[]
 for k,outline in enumerate(outlines):
  p=Polygon([(-1215+(x-640)/3.27+(8 if k==3 else 0),-172.5+(z-400)/3.27-(7 if k==3 else 0)) for x,z in outline]).buffer(.9).buffer(-.9).intersection(deck.buffer(-.6))
  p=p.difference(occupied.buffer(2.5)).simplify(.18,preserve_topology=True)
  pools.append(p)
 water=unary_union(pools)
 deck=deck.union(water.buffer(3)).difference(occupied.buffer(.35))
 return occupied,deck.simplify(.001,preserve_topology=True),pools

def build(B):
 B.property='rioAmenities-exterior';B.source='rio-amenities';B.detail=0
 occupied,deck,pools=plan();water=unary_union(pools);routes=[]
 for i,q in enumerate(parts(water.buffer(1.25,join_style=2))):
  name='connected-circuit-'+str(i)
  for ring in [list(q.exterior.coords)]:
   assert deck.buffer(.01).covers(LineString(ring).buffer(.42))
   routes.append(dict(name='rio-'+name,points=[[x,Y,z] for x,z in ring]))
 route=unary_union([LineString([(p[0],p[2]) for p in r['points']]).buffer(.8) for r in routes])
 B.planar('ra-paving',deck.difference(water),Y,True);B.planar('ra_pool',water,.21)
 B.planar('ra-tile',water,-.55,True);B.shell(water,-.55,Y,'ra-tile',roof=False,solid=True)
 B.planar('ra-coping',water.buffer(.34).difference(water),Y+.035,True)
 available=deck.difference(water.buffer(2.25)).difference(route)
 used=[];counts=dict(cabanas=0,loungers=0,parasols=0,palms=0,shrubs=0)
 def reserve(p):
  if not available.contains(p) or any(p.intersects(v) for v in used):return False
  used.append(p.buffer(.3));return True
 def cabana(x,z,yaw):
  F=Frame(B,x,z,yaw,y=Y)
  for dx in [-2.1,2.1]:
   for dz in [-1.8,1.8]:F.box('ra-white',(dx,1.4,dz),(.12,2.8,.12),True)
  F.box('ra-yellow',(0,1.4,1.85),(4.3,2.8,.1),True)
  for dx in [-2.12,2.12]:F.box('ra-yellow',(dx,1.4,0),(.1,2.8,3.8),True)
  top=[(-2.3,2.8,-2), (2.3,2.8,-2),(2.3,2.8,2),(-2.3,2.8,2)]
  for a,b in zip(top,top[1:]+top[:1]):B.face('ra-yellow',[F.p(*a),F.p(*b),F.p(0,3.6,0)])
  for dx in [-1.8,1.8]:F.box('ra-white',(dx,1.25,-1.83),(.55,2.5,.16))
  # Furnished open cabana, adapted from the official interior photograph.
  F.box('ra-red',(0,.55,1),(3.4,.5,.8),True);F.box('ra-red',(0,.98,1.32),(3.4,.6,.15))
  F.box('ra-teal',(-1.25,.55,-.5),(.75,.55,.8),True)
  F.box('ra-wood',(1.5,.65,.25),(.7,1.3,.7),True)
  F.box('ra-screen',(1.5,1.85,1.77),(1.1,.7,.04))
  F.box('ra-white',(0,.45,-.2),(1.1,.15,.8),True)
  counts['cabanas']+=1
 # Lagoon and Shell only, as the official numbered map shows.
 for p in pools[:2]:
  ring=p.buffer(5).exterior
  for dist in np.arange(1,ring.length,7):
   q=ring.interpolate(dist);x,z=q.x,q.y;near=p.exterior.interpolate(p.exterior.project(q));yaw=math.atan2(near.x-x,near.y-z)+math.pi
   footprint=rotate(box(x-2.4,z-2.2,x+2.4,z+2.2),-math.degrees(yaw),origin=(x,z))
   if reserve(footprint):cabana(x,z,yaw)
 # Loosely concentric rows; exact chair count and orientation remain estimates.
 for x in np.arange(deck.bounds[0]+1,deck.bounds[2],2.6):
  for z in np.arange(deck.bounds[1]+1,deck.bounds[3],3.5):
   if water.distance(Point(x,z))>8 or not reserve(box(x-.6,z-1.2,x+.6,z+1.2)):continue
   F=Frame(B,x,z,0,y=Y);F.box('ra-white',(0,.4,0),(.7,.16,1.9));F.box('ra-wood',(0,.2,0),(.55,.4,1.6),True)
   B.face('ra-white',[F.p(-.35,.48,-.3),F.p(.35,.48,-.3),F.p(.35,.9,-.9),F.p(-.35,.9,-.9)]);counts['loungers']+=1
   if counts['loungers']%5==0:
    B.box('ra-white',(x+.6,Y+1.2,z),(.045,2.4,.045))
    for j in range(12):
     a=j*math.tau/12;b=(j+1)*math.tau/12
     B.face(['ra-yellow','ra-red','ra-blue','ra-white'][j%4],[(x+.6,Y+2.85,z),(x+.6+1.2*math.cos(a),Y+2.35,z+1.2*math.sin(a)),(x+.6+1.2*math.cos(b),Y+2.35,z+1.2*math.sin(b))])
    counts['parasols']+=1
 # Original low-poly palms and planting islands, outside all tested walking loops.
 for x in np.arange(deck.bounds[0]+2,deck.bounds[2]-1,5.5):
  for z in np.arange(deck.bounds[1]+2,deck.bounds[3]-1,5.5):
   q=Point(x,z);patch=q.buffer(1.05,resolution=8)
   if water.distance(q)<4 or not reserve(patch):continue
   B.planar('ra-soil',patch,Y+.03);B.lathe('ra-green',(x,z),[(Y,.7),(Y+.7,1),(Y+1.2,.35)],8);counts['shrubs']+=1
   if counts['shrubs']%2:continue
   h=6+counts['palms']%4;B.lathe('ra-bark',(x,z),[(Y,.25),(Y+h,.12)],10);B.box('ra-bark',(x,Y+h/2,z),(.3,h,.3),True)
   for j in range(10):
    a=j*math.tau/10;points=[]
    for k in range(6):
     t=k/5;rr=2.7*t;yy=Y+h+math.sin(t*math.pi)-t;w=.32*math.sin(t*math.pi)
     points.append([(x+rr*math.cos(a)-w*math.sin(a),yy,z+rr*math.sin(a)+w*math.cos(a)),(x+rr*math.cos(a)+w*math.sin(a),yy,z+rr*math.sin(a)-w*math.cos(a))])
    for k,(a,b) in enumerate(zip(points,points[1:])):B.face('ra-green',[a[0],b[1],b[0]] if k==0 else [a[0],a[1],b[0]] if k==4 else [a[0],a[1],b[1],b[0]])
   counts['palms']+=1
 r=Path('docs/project-records/rio-palms-amenities');(r/'rio-routes.json').write_text(json.dumps(routes,indent=2)+'\n');(r/'rio-geometry.json').write_text(json.dumps(counts,indent=2)+'\n');return counts

if __name__=='__main__':
 B=AmenityMeshes();print(build(B));B.save_all()
