"""Original Platinum indoor/outdoor pool study from official gallery and aerial.
Dimensions, furniture positions and enclosed plan are inferred, not surveyed.
"""
from common import *
from rio_amenities import AmenityMeshes
RECORD=Path('docs/project-records/westin-platinum-amenities');Y=12.47

def plan():
 r=json.loads((RECORD/'research.json').read_text())['coordinateFit']['platinum'];lon,lat=r['centreLonLat']
 cx=6378137*math.radians(lon+115.173)*math.cos(math.radians(36.116));cz=-6378137*math.radians(lat-36.116)
 def trace(ps):return Polygon([(cx+(x-676)*.1206,cz+(z-360)*.1206) for x,z in ps])
 pool=trace(r['outdoorPoolPixels']);inside=trace(r['indoorEnclosurePixels'])
 tower=footprint('way/543423254');parent=footprint('way/135298867')
 garage=parent.intersection(box(860,242,900.5,295)).difference(tower)
 deck=garage.buffer(-.4).intersection(box(871,247.8,893,280))
 # Rounded indoor pool and narrow swim-through match the photo; exact fit inferred.
 indoor=box(875,271,884.5,277.4).buffer(-.7).buffer(.7,resolution=8)
 channel=box(882,265.9,884,273)
 water=unary_union([pool,indoor,channel]);assert deck.covers(water)
 return deck,pool,inside,water

def build(B):
 B.property='platinumAmenities-exterior';B.source='platinum-amenities';B.detail=0
 deck,pool,inside,water=plan()
 B.planar('ppa-deck',box(875.54,252.54,884.46,268.46).difference(water),12.426,True)
 B.planar('ppa-deck',deck.difference(water),Y,True)
 B.planar('ppa_pool',water,Y+.01)
 B.planar('ppa-coping',water.buffer(.2).difference(water),Y+.025,True)
 # Open dry doorway west of water channel, no collision across the water opening.
 # Separate interior source for required interior-light treatment at integration.
 B.source='platinum-pool-interior';B.property='platinum-interior'
 x0,z0,x1,z1=inside.bounds;H=3.4
 B.shell(inside,Y,Y+H,'ppa-interior-wall',roof=False,openings=[dict(p=[877,Y,z0],width=2.4,height=2.8),dict(p=[883,Y,z0],width=2.1,height=2.7),dict(p=[880,Y+.55,z0],width=2.1,height=2.15),dict(p=[886.5,Y+.55,z0],width=2.4,height=2.15),dict(p=[889.5,Y+.55,z0],width=2.4,height=2.15)])
 B.planar('ppa-interior-ceiling',inside,Y+H)
 # Four north-facing glazed bays: visual frames above pool, clear doorway retained.
 for x in [880,886.5,889.5]:
  B.box('ppa-frame',(x,Y+1.65,z0-.02),(.07,3.1,.10))
 B.box('ppa-frame',((x0+x1)/2,Y+3.12,z0-.02),(x1-x0,.10,.10))
 # Interior table/chairs visible beside the north wall, outside walking line.
 for x,z in [(888.5,271.6),(888.5,275.8)]:
  B.box('ppa-frame',(x,Y+.38,z),(.12,.76,.12),True)
  B.box('ppa-dark',(x,Y+.8,z),(1.2,.08,1.2),True)
  for dz in [-.95,.95]:
   B.box('ppa-dark',(x,Y+.45,z+dz),(.55,.12,.55),True)
   B.box('ppa-frame',(x,Y+.2,z+dz),(.40,.40,.40))
 B.source='platinum-amenities';B.property='platinumAmenities-exterior'
 # Exterior backs retain enclosure silhouette while the public interior streams.
 B.box('ppa-gray',((x0+x1)/2,Y+H/2,z1+.04),(x1-x0,H,.08),True)
 for x in [x0-.04,x1+.04]:B.box('ppa-gray',(x,Y+H/2,(z0+z1)/2),(.08,H,z1-z0),True)
 B.planar('ppa-roof',inside,Y+H+.1,True)
 # Gray perimeter wall punctured with rectangular skyline openings and lime awnings.
 for a,b in [((873,249),(891.5,249)),((873,249),(873,266.5))]:
  L=math.dist(a,b);F=Frame(B,a[0],a[1],math.atan2(-(b[1]-a[1]),b[0]-a[0]),y=Y)
  F.box('ppa-gray',(L/2,.45,0),(L,.9,.2),True);F.box('ppa-gray',(L/2,2.6,0),(L,.35,.2),True)
  n=max(1,round(L/3.6));w=L/n
  for i in range(n+1):F.box('ppa-gray',(i*w,1.4,0),(.28,2.8,.25),True)
  for i in range(n):F.box('ppa-lime',((i+.5)*w,2.47,.25),(w-.35,.09,.65))
 # Dry circuit around outdoor pool; southern leg leads through the open indoor door.
 routes=[dict(name='platinum-outdoor',points=[[877,Y,267.4],[874,Y,267.4],[874,Y,255.5],[888.2,Y,255.5],[888.2,Y,267.1]]),dict(name='platinum-indoor-link',points=[[877,Y,267.4],[877,Y,269.5],[874,Y,269.5],[874,Y,278.4],[885.7,Y,278.4],[885.7,Y,271]])]
 corridor=unary_union([LineString([(p[0],p[2])for p in r['points']]).buffer(.65)for r in routes])
 free=deck.difference(inside).difference(water.buffer(1)).difference(corridor);used=[];count=0
 for z in [251,253,264]:
  for x in np.arange(874.6,891,1.6):
   F=Frame(B,x,z,0,y=Y);q=F.poly([(-.45,-1.05),(.45,-1.05),(.45,1.05),(-.45,1.05)])
   if not free.covers(q) or any(q.intersects(p)for p in used):continue
   used.append(q);F.box('ppa-dark',(0,.37,0),(.7,.10,1.9),True)
   for dx in [-.34,.34]:
    F.box('ppa-frame',(dx,.3,0),(.04,.08,1.95))
    for dz in [-.7,.7]:F.box('ppa-frame',(dx,.16,dz),(.04,.32,.04))
   B.face('ppa-dark',[F.p(-.35,.42,-.3),F.p(.35,.42,-.3),F.p(.35,.86,-.9),F.p(-.35,.86,-.9)]);count+=1
 (RECORD/'platinum-routes.json').write_text(json.dumps(routes,indent=2)+'\n')
 (RECORD/'platinum-geometry.json').write_text(json.dumps(dict(loungers=count,deckAreaM2=deck.area,waterAreaM2=water.area,indoorBounds=list(inside.bounds),limitations=['Inferred enclosure dimensions/ceiling and channel registration.','Shallow water above retained structural roof; no swimming-depth claim.','Separate platinum-interior asset uses existing streamed venue interior lighting; metadata integration pending.','Exact planting, festoon fixtures, guest lift access and street-to-pool route remain unfinished.']),indent=2)+'\n')
 return count
if __name__=='__main__':
 B=AmenityMeshes();print('loungers',build(B));B.save_all()
