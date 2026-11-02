"""Original Westin rooftop pool study, linked official photos and aerial trace.
No tower or street geometry regenerated. All metre fits remain estimates.
"""
from common import *
from rio_amenities import AmenityMeshes
RECORD=Path('docs/project-records/westin-platinum-amenities')
Y=7.57

def plan():
 r=json.loads((RECORD/'research.json').read_text())['coordinateFit']['westin']
 lon,lat=r['centreLonLat'];cx=6378137*math.radians(lon+115.173)*math.cos(math.radians(36.116));cz=-6378137*math.radians(lat-36.116)
 def trace(ps):return Polygon([(cx+(x-676)*.1206,cz+(z-360)*.1206) for x,z in ps])
 pool=trace(r['poolPixels']);podium=footprint('way/135020970');tower=footprint('way/543423252')
 deck=trace(r['deckPixels']).intersection(podium.buffer(-.4)).difference(tower.buffer(.3))
 assert deck.buffer(-1.5).covers(pool)
 return deck,pool

def build(B):
 B.property='westinAmenities-exterior';B.source='westin-amenities';B.detail=0
 deck,pool=plan()
 # Old pool aperture gets a roof patch; new basin stays above preserved roof slab.
 B.planar('wpa-deck',box(595.44,97.44,603.56,108.56).difference(pool),7.526,True)
 B.planar('wpa-deck',deck.difference(pool),Y,True)
 B.planar('wpa_pool',pool,Y+.01)
 B.planar('wpa-coping',pool.buffer(.24).difference(pool),Y+.035,True)
 # The retained roof limits basin depth. Do not claim swimming or a surveyed depth.
 ring=list(pool.buffer(1.05,join_style=2).exterior.coords)
 route=LineString(ring);assert deck.covers(route.buffer(.4))
 routes=[dict(name='westin-pool-circuit',points=[[x,Y,z] for x,z in ring])]
 free=deck.buffer(-.5).difference(pool.buffer(2)).difference(route.buffer(.8));used=[]
 counts=dict(loungers=0,daybeds=0,shadeBays=0,parasols=0)
 def reserve(poly):
  if not free.covers(poly) or any(poly.intersects(p) for p in used):return False
  used.append(poly.buffer(.15));return True
 # Flat shade bays and navy daybeds on the north-west apron, inferred placement.
 for x,z in [(589,98),(594,95),(600,96)]:
  F=Frame(B,x,z,math.pi/4,y=Y)
  if not reserve(F.poly([(-1.35,-1.45),(1.35,-1.45),(1.35,1.45),(-1.35,1.45)])):continue
  for dx in [-1.25,1.25]:
   for dz in [-1.35,1.35]:F.box('wpa-dark',(dx,1.35,dz),(.10,2.7,.10),True)
  for i in range(12):F.box('wpa-cream' if i%2 else 'wpa-dark',(-1.32+(i+.5)*2.64/12,2.75,0),(2.64/12,.08,2.85))
  F.box('wpa-navy',(0,.32,.25),(1.9,.64,1.9),True)
  F.box('wpa-navy',(0,.72,1),(1.9,.5,.25))
  counts['daybeds']+=1;counts['shadeBays']+=1
 # Three turquoise parasols visible in the official rooftop photo; fit where clear.
 for x,z in [(603,99),(607,103),(609,107)]:
  if not reserve(Point(x,z).buffer(.55)):continue
  B.box('wpa-dark',(x,Y+1.3,z),(.05,2.6,.05),True)
  for j in range(12):
   a=j*math.tau/12;b=(j+1)*math.tau/12
   B.face('wpa-teal',[(x,Y+2.8,z),(x+1.25*math.cos(a),Y+2.45,z+1.25*math.sin(a)),(x+1.25*math.cos(b),Y+2.45,z+1.25*math.sin(b))])
  counts['parasols']+=1
 # Dark frames and gray fabric, each aligned toward the basin.
 for distance in [3.8,6.8]:
  edge=pool.buffer(distance,join_style=2).exterior
  for t in np.arange(0,edge.length,2.3):
   q=edge.interpolate(t);near=pool.exterior.interpolate(pool.exterior.project(q));yaw=math.atan2(near.x-q.x,near.y-q.y)+math.pi
   F=Frame(B,q.x,q.y,yaw,y=Y)
   if not reserve(F.poly([(-.45,-1.05),(.45,-1.05),(.45,1.05),(-.45,1.05)])):continue
   F.box('wpa-gray',(0,.35,0),(.72,.1,1.85),True)
   for x in [-.34,.34]:
    F.box('wpa-dark',(x,.3,0),(.04,.07,1.95))
    for z in [-.65,.65]:F.box('wpa-dark',(x,.16,z),(.045,.32,.045))
   B.face('wpa-gray',[F.p(-.36,.4,-.3),F.p(.36,.4,-.3),F.p(.36,.85,-.9),F.p(-.36,.85,-.9)])
   counts['loungers']+=1
 # Pale outer guard wall; leave a north access opening as an explicitly unfinished link.
 for a,b in zip(list(deck.exterior.coords),list(deck.exterior.coords)[1:]):
  if max(a[1],b[1])<96:continue
  L=math.dist(a,b)
  if L<.1:continue
  F=Frame(B,(a[0]+b[0])/2,(a[1]+b[1])/2,math.atan2(-(b[1]-a[1]),b[0]-a[0]),y=Y)
  F.box('wpa-cream',(0,.58,0),(L,1.16,.18),True)
 (RECORD/'westin-routes.json').write_text(json.dumps(routes,indent=2)+'\n')
 (RECORD/'westin-geometry.json').write_text(json.dumps(dict(**counts,deckAreaM2=deck.area,poolAreaM2=pool.area,poolBounds=list(pool.bounds),limitations=['Estimated tracing clipped to preserved mapped podium.','Water is a shallow visual surface above retained roof collision; no swimming-depth claim.','Shade/furniture placement inferred. North access link and street-to-deck guest circulation unfinished.','Source study only; export, installed visual/collision checks and performance pending.']),indent=2)+'\n')
 return counts
if __name__=='__main__':
 B=AmenityMeshes();print(build(B));B.save_all()
