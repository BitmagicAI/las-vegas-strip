"""Original Palms pool cabanas, based on official photographs; dimensions inferred.

Existing towers, guest interiors and Place roof remain untouched by this source.
"""
from common import *
import palms_exterior as P
from rio_amenities import AmenityMeshes
REC=Path('docs/project-records/rio-palms-amenities')
Y=.335

def build(B):
 B.property='palmsAmenities-exterior';B.source='palms-amenities';B.detail=0
 parent=footprint(P.PARENT);pools=[]
 for p in parts(parent):
  for r in p.interiors:
   if Polygon(r).area>100:pools.append(Polygon(r))
 pools.sort(key=lambda p:p.centroid.x)
 # West pool's round dry island is visible in aerial photography.
 pools[0]=pools[0].difference(Point(pools[0].centroid.x,pools[0].centroid.y).buffer(3.2,resolution=24))
 water=unary_union(pools);deck=P.courtyard().union(water.buffer(3)).difference(unary_union([r['shape'] for r in P.records() if r['height']>30]).buffer(.5))
 routes=[]
 for i,p in enumerate(pools):
  ring=list(p.buffer(1.2).exterior.coords);line=LineString(ring)
  assert deck.buffer(.01).covers(line.buffer(.42))
  routes.append(dict(name='palms-pool-'+str(i),points=[[x,Y,z] for x,z in ring]))
 paths=unary_union([LineString([(x,z) for x,y,z in r['points']]).buffer(.85) for r in routes])
 B.planar('pa-paving',deck.difference(water),Y,True);B.planar('pa_pool',water,.19);B.planar('pa-tile',water,-.8,True);B.shell(water,-.8,Y,'pa-tile',roof=False,solid=True)
 B.planar('pa-white',water.buffer(.3).difference(water),Y+.025,True)
 available=deck.difference(water.buffer(2.3)).difference(paths);used=[];counts=dict(cabanas=0,loungers=0)
 def reserve(p):
  if not available.contains(p) or any(p.intersects(q) for q in used):return False
  used.append(p.buffer(.3));return True
 # Two-level white cabana galleries with timber pergolas and small upper pools.
 for x in np.arange(-1873,-1789,6.5):
  z=143
  if not reserve(box(x-2.8,z-2.5,x+2.8,z+2.5)):continue
  F=Frame(B,x,z,math.pi,y=Y)
  for dx in [-2.6,2.6]:
   F.box('pa-white',(dx,3,0),(.18,6,4.8),True)
  F.box('pa-white',(0,1.5,2.35),(5.4,3,.15),True)
  F.box('pa-white',(0,3,0),(5.5,.2,4.9),True)
  F.box('pa-navy',(0,.55,1.5),(3.7,.5,.8),True)
  F.box('pa-navy',(0,1,1.8),(3.7,.6,.15))
  F.box('pa-white',(0,.5,0),(1.2,.12,.8),True)
  for dx in [-2.25,2.25]:F.box('pa-navy',(dx,1.4,-2.2),(.4,2.8,.13))
  for dx in np.arange(-2.6,2.7,.45):F.box('pa-wood',(dx,6,0),(.13,.18,5))
  pool=F.poly([(-2,-1.9),(2,-1.9),(2,-.3),(-2,-.3)])
  B.shell(pool,3.42,4.05,'pa-tile',solid=True,roof=False);B.planar('pa_pool',pool,Y+3.65)
  F.box('pa-navy',(0,3.55,1.4),(3.5,.45,.85),True)
  # Solid upper edge guards; access is deferred pending reference-supported stairs.
  for side in [-1,1]:F.box('pa-white',(side*2.6,3.55,0),(.12,1.1,4.8),True)
  F.box('pa-white',(0,3.55,-2.4),(5.2,1.1,.12),True)
  counts['cabanas']+=1
 for x in np.arange(deck.bounds[0]+1,deck.bounds[2]-1,2.3):
  for z in np.arange(deck.bounds[1]+1,deck.bounds[3]-1,3.2):
   if water.distance(Point(x,z))>5 or not reserve(box(x-.55,z-1.05,x+.55,z+1.05)):continue
   F=Frame(B,x,z,0,y=Y);F.box('pa-white',(0,.25,0),(.65,.5,1.8),True);F.box('pa-navy',(0,.54,0),(.7,.12,1.85));counts['loungers']+=1
 (REC/'palms-routes.json').write_text(json.dumps(routes,indent=2)+'\n');(REC/'palms-geometry.json').write_text(json.dumps(counts,indent=2)+'\n');return counts
if __name__=='__main__':
 B=AmenityMeshes();print(build(B));B.save_all()
