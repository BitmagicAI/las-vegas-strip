"""Bellagio first mapped exterior pass. Coordinates are geographic metres.
Published architectural tip 155.8 m; other section heights are fitted estimates.
Legacy playable casino/guest cores are retained, not silently replaced by boxes.
"""
import sys,json,math
from pathlib import Path
sys.path.insert(0,'tools/strip-landmarks')
from common import *
import common
import bellagio_lakefront as lakefront
import bellagio_south_arrival as south_arrival
import bellagio_garage as garage
OUT=Path('build/resort-blocks/bellagio');OUT.mkdir(parents=True,exist_ok=True);common.OUT=OUT
b=Meshes();venues=[];routes=[];G=.24
site=footprint('relation/1599958');tower=footprint('way/25723909');court=Polygon(max(site.interiors,key=lambda r:Polygon(r).area))
# Existing custom casino, service rooms and two guest stairs retain one geometry owner.
legacy=box(-369,247,-257,397)
access=json.load(open('build/geographic-strip/access/bellagio-via-plan.json'))
via=unary_union([Polygon(p) for p in access['upper']]+[LineString(p).buffer(4.2) for p in access['lower']]+[LineString(p).buffer(3.5) for p in access['stairs']]).buffer(.15)
F=lambda x,z,y=G,yaw=0:Frame(b,x,z,yaw,y)
def source(s,detail=0):b.source=s;b.detail=detail

def slab(p,y,mat='marble',solid=True):
 # Constrained triangulation preserves non-convex outlines and courtyard holes.
 b.shell(p,y-.28,y,mat,roof=False,solid=solid);b.planar(mat,p,y,solid);b.planar(mat,p,y-.28)
def route(name,points):routes.append(dict(name=name,points=points))
def column(x,z,y=G,h=6,r=.45):
 f=F(x,z,y);f.lathe('ivory',0,0,[(0,r*1.45),(.2,r*1.45),(.32,r),(h-.4,r*.84),(h-.3,r*1.3),(h,r*1.3)],16)
def rail(a,c,y=G):F(0,0,y).rail(a,c,glass=True)
def patio_table(x,z,y=G):
 f=F(x,z,y);f.lathe('brass',0,0,[(0,.35),(.06,.35),(.1,.05),(.74,.05)],10);f.lathe('marble',0,0,[(.74,.62),(.81,.62)],16)
 for dx,dz in [(1,0),(-1,0),(0,1),(0,-1)]:
  f.box('ivory',(dx,.47,dz),(.53,.1,.54));f.box('ivory',(dx,.78,dz+.24),(.53,.58,.08))
  for xx in [-.21,.21]:f.box('bronze',(dx+xx,.24,dz),(.04,.48,.44))
def pergola(x,z,w,d,y=G):
 f=F(x,z,y)
 for xx in [-w/2,w/2]:
  for zz in [-d/2,d/2]:column(x+xx,z+zz,y,3,.17)
 for xx in [-w/2,w/2]:f.box('ivory',(xx,3.14,0),(.22,.22,d+.5))
 for zz in np.arange(-d/2,d/2+.1,.5):f.box('ivory',(0,3.28,zz),(w+.5,.13,.12))
def hedge(poly,y=G):
 b.shell(poly,y,y+.8,'sage',roof=False,solid=True);b.planar('sage',poly,y+.8,True)
def pool(poly):
 slab(poly.buffer(.45),G+.06,'ivory');b.planar('water',poly,G+.075)
 # Original modeled mosaic, not a photograph used as a texture.
 for ratio in [.3,.6,.86]:b.shell(scale(poly,xfact=ratio,yfact=ratio,origin='centroid'),G+.076,G+.079,'blue',roof=False,solid=False)
 c=poly.centroid
 for dx,dz in [(1,0),(-1,0),(0,1),(0,-1)]:
  if poly.covers(Point(c.x+dx*2,c.y+dz*2)):b.planar('blue2',Point(c.x+dx*2,c.y+dz*2).buffer(.42,quad_segs=8),G+.08)
def lounge(x,z,y=G):
 f=F(x,z,y);f.box('ivory',(0,.35,0),(.78,.16,1.9));f.box('ivory',(0,.61,.72),(.78,.48,.18))
 for xx in [-.31,.31]:f.box('bronze',(xx,.15,0),(.045,.3,1.7))
def circle_fountain(x,z,r,y=G):
 f=F(x,z,y);f.lathe('stone',0,0,[(0,r),(.3,r),(.42,r-.12),(.42,r-.4),(.26,r-.4)],40);b.planar('water',Point(x,z).buffer(r-.4,quad_segs=24),y+.28)
 f.lathe('ivory',0,0,[(.2,.7),(1.2,.3),(1.3,1.6),(1.5,1.6),(1.5,.2),(2.5,.15),(2.6,.75),(2.8,.75)],24)

# Permanent structural shell.
b.property='bellagioBlock-exterior';source('podium')
# Preserved bridge interiors carve their own openings through the north shell.
portals=[dict(p=[-229.0,G,445],yaw=-math.pi/2,width=8,height=4.5,name='BELLAGIO MAIN ENTRANCE'),dict(p=[-366.25,G,445],yaw=-math.pi/2,width=6,height=4.5,name='POOL COURTYARD'),dict(p=[-370,G,480],yaw=math.pi,width=6,height=4.5,name='POOL GARDENS')]
# Public restaurant frontages follow actual polygon edges, with a connected
# lakeside terrace rather than an arbitrary rooftop restaurant.
restaurants=[('SPAGO',(-169,263),16),('CARBONE RIVIERA',(-171,300),18),('PRIME',(-186,334),20),('LAGO',(-190,355),16),('JASMINE',(-163,375),17)]
for name,(x,z),w in restaurants:
 edge=site.exterior.interpolate(site.exterior.project(Point(x,z)));x,z=edge.x,edge.y
 portals.append(dict(p=[x,G,z],yaw=-math.pi/2,width=5,height=4.5,name=name))
# Existing lower gallery exit is connected to the new casino promenade.
link=LineString([(-190,225),(-201,237),(-233,237),(-270,238)]).buffer(2.5,cap_style=2)
slab(link.difference(via.union(site)),G)
# Full mapped roof and exterior walls; retained casino owns its own floor/ceiling.
slab(site.difference(legacy.union(via)),G)
b.shell(site,G,12.1,'sandstone',openings=portals,roof=False,solid=True,interior=(via.union(link).union(lakefront.NORTH),26))
conservatory=box(-338,429,-302,463)
slab(site.difference(conservatory).difference(tower).difference(lakefront.NORTH),12.4,'roof',False)
# Source tower footprint is already exact in world metres. No whole-site transform.
# Main tower and Spa Tower after the owner's Google Earth reference: three segments, white crowns with arched
# windows, patina hip roofs, lower end pavilions, the rotunda's drum/arcade/dome (bellagio_towers.py, 2026-10-08).
# The Spa is drawn here (source tower/way/114716301, hidden from its own guest rooms); its collision stays with the
# high-rise pass (HighriseCity drops only that tower's visuals).
import bellagio_towers
bellagio_towers.main(b,tower)
bellagio_towers.spa(b,footprint('way/25723910'))
# Low-rise cornices and facade rhythm; opening-aware trims never cross doorways.
source('podium-cornice')
for y in [9.8,11.8,12.5]:b.shell(site.buffer(.16,join_style=2),y,y+.22,'ivory',roof=False,solid=False,interior=(lakefront.NORTH,26))
# Lake and pool frontage pilasters, arches, opaque glazing, lamps. Roof/service
# sides receive measured repetition without glass falsely exposing an empty void.
source('podium-facade',1)
for ring in [site.exterior,*site.interiors]:
 for a,c in zip(list(ring.coords),list(ring.coords)[1:]):
  le=math.dist(a,c)
  if le<7:continue
  dx,dz=(c[0]-a[0])/le,(c[1]-a[1])/le;nx,nz=dz,-dx
  if site.contains(Point((a[0]+c[0])/2+nx,(a[1]+c[1])/2+nz)):nx,nz=-nx,-nz
  yaw=-math.atan2(dz,dx)
  for d in np.arange(3.3,le-2,6.6):
   x,z=a[0]+dx*d+nx*.16,a[1]+dz*d+nz*.16
   if lakefront.NORTH.covers(Point(x,z)) or via.buffer(.5).contains(Point(x,z)) or any(math.hypot(x-p['p'][0],z-p['p'][2])<p['width']/2+2 for p in portals):continue
   f=F(x,z,G,yaw);f.box('ivory',(0,4.5,0),(.6,9,.32))
   if x>-240 or court.buffer(2).contains(Point(x,z)):
    f.box('darkglass',(2.2,3.3,-.02),(3.3,4.9,.1));f.arch(2.2,.14,3.6,6.6,'ivory',.18)
    f.box('brass',(0,3.2,.35),(.18,.7,.2));f.box('warm',(0,3.2,.50),(.14,.48,.16))
# Conservative service roof treatment; no invented public rooftop decks.
source('service-roof',1)
for x in np.arange(-570,-450,30):
 for z in np.arange(260,620,35):
  if site.contains(Point(x,z).buffer(4)):b.box('roof',(x,13.5,z),(7,2,4));b.box('silver',(x,14.55,z),(7.2,.1,4.2))
# New lawn courtyard and five pools, independently furnished nearby.
source('pool-deck');slab(court.difference(legacy),G,'tile');pools=[box(-370,382,-351,414),Point(-391,394).buffer(11,quad_segs=2),Point(-427,394).buffer(11,quad_segs=2),box(-443,432,-387,463).buffer(5,join_style=1),Point(-432,519).buffer(12,quad_segs=12)]
for p in pools:pool(p.intersection(court.buffer(-1)))
source('pool-courtyard-colonnade')
for x in np.arange(-445,-380,5.5):
 column(x,361,h=5);F(x,361).arch(2.75,0,4.65,5.2,'ivory',.18)
b.box('ivory',(-412,5.7,361),(72,.42,.65))
for z in np.arange(372,478,7):column(-449,z,h=4.8)
b.box('ivory',(-449,5.3,424),(.65,.42,110))
# Legible main entrance. The existing bronze/glass canopy is re-authored at this
# mapped arrival during Blender export, at full-scale component dimensions.
source('arrival-threshold');slab(box(-232,436,-198,454).difference(site),G,'marble')
f=F(-228.75,445,G,-math.pi/2);f.arch(0,0,10.4,8.8,'ivory',.3)
f.text('BELLAGIO',(0,6.1,-.2),.72)
for xx in [-5.3,5.3]:f.box('ivory',(xx,2.7,0),(.9,5.4,.7))
for p in portals:F(p['p'][0],p['p'][2],p['p'][1],p['yaw']).portal(w=p['width'],h=p['height'],name=p['name'])
# Conservatory roof: framed glass hip lantern over a planted public court.
source('conservatory-roof')
for side in [-1,1]:
 b.face('glass',[(-320+side*18,12.4,429),(-320+side*18,12.4,463),(-320,19,463),(-320,19,429)])
 for z in np.arange(429,464,2):b.tube('copper',(-320+side*18,12.5,z),(-320,19.1,z),.09)
for z in [429,463]:b.face('glass',[(-338,12.4,z),(-302,12.4,z),(-320,19,z)]);b.tube('copper',(-338,12.5,z),(-302,12.5,z),.11)
# Sidewalk-to-lobby route and connections to retained casino.
for name,points in [('Main arrival',[[-199,G,445],[-230,G,445],[-252,G,445],[-264,G,445],[-268,G,450],[-280,G,450],[-306,G,450]]),('Casino connection',[[-246,G,445],[-246,G,386],[-263,.075,386],[-289,.075,386]]),('North casino',[[-195,.18,208],[-195,.18,215],[-193,.18,221],[-190,.18,225],[-201,G,237],[-233,G,237],[-270,G,238],[-290,.075,249]]),('Courtyard',[[-320,G,450],[-350,G,450],[-361,G,450],[-366.25,G,445],[-378,G,445],[-378,G,423],[-371,G,423],[-380,G,423],[-410,G,423],[-444,G,423],[-444,G,476],[-433,G,493]])]:route(name,points)
# Small anchor interior gates the permanent entrance doors; main furnishings
# stream by spatial region rather than as a 600m-wide casino.
b.property='bellagioBlock-interior';source('anchor');b.box('roof',(-250,-3,445),(.01,.01,.01))
venues.append(dict(key='bellagioBlock',name='Bellagio · exterior and arrival',building='bellagio',structural=True,exteriorCollision='bellagioBlock-exterior-runtime-collision.json',bounds=list(site.bounds),portals=portals,zones=[],accessPoints=[[-229,G,445],[-366.25,G,445],[-370,G,480]],lights=[],views={'entrance':dict(eye=[-198,2,445],target=[-241,4,445]),'aerial':dict(eye=[60,235,115],target=[-310,60,365]),'deck':dict(eye=[-375,2,422],target=[-409,2,395])}))
# Lakeside restaurant terrace pieces follow the edge and clear the lake basin.
for p in portals[3:]:
 x,_,z=p['p'];name=p['name'];b.property='bellagioBlock-exterior';source('patio-'+name)
 deck=box(x-3,z-7,x+10,z+7);slab(deck.difference(site),G,'tile');rail((x+10,z-7),(x+10,z+7));rail((x,z-7),(x+10,z-7));rail((x,z+7),(x+10,z+7))
 # Stately shade pergolas, planting and a two-metre clear entrance aisle.
 pergola(x+5,z,8,13)
 for zz in [z-4.5,z+4.5]:patio_table(x+5,zz);F(x+9,zz).plant(0,0)
 F(x-.2,z,2,-math.pi/2).text(name,(0,3,0),min(.48,5/(len(name)*.6)))
 route(name+' terrace',[[x-6,G,z],[x-1,G,z],[x+5,G,z],[x+8,G,z]])
# Streaming interior zones are explicitly modest and connected.
chunks=[('bellagioLobby',(-275,405,-222,488)),('bellagioGarden',(-455,355,-341,552)),('bellagioConservatory',(-340,421,-295,479)),('bellagioPromenade',(-256,229,-189,424))]
for key,bounds in chunks:
 b.property=key+'-exterior';source('anchor');b.box('roof',(-250,-3,445),(.01,.01,.01));b.property=key+'-interior';source(key,1);x0,z0,x1,z1=bounds
 if key=='bellagioLobby':
  f=F(0,0);f.reception(-255,470,25,'BELLAGIO');circle_fountain(-272,445,3)
  for x in [-264,-238]:
   for z in [416,432,457,478]:column(x,z,h=8.4);F(x,z).chandelier(0,0,7.2)
  for x in [-267,-234]:
   for z in [425,462]:F(x,z).lounge(0,0)
  # Colored glass-flower ceiling, original polygon petals in Bellagio's palette.
  for x in np.arange(-260,-234,1.8):
   for z in np.arange(436,454,1.8):
    y=7.1+.4*math.sin(x+z);mat=['blue2','ochre','rose','red','gold'][int(abs(x*7+z*3))%5]
    for k in range(8):
     a=k*math.tau/8;c=(k+1)*math.tau/8;b.face(mat,[(x,y,z),(x+.9*math.cos(a),y+.23,z+.9*math.sin(a)),(x+.9*math.cos(c),y+.23,z+.9*math.sin(c))])
  slab(box(-276,405,-222,488),9.1,'ivory',False)
 elif key=='bellagioGarden':
  dry=court.buffer(-3).difference(unary_union(pools).buffer(2)).difference(legacy.buffer(1));clear=unary_union([LineString([(p[0],p[2]) for p in r['points']]).buffer(1.7) for r in routes])
  for x in np.arange(-446,-348,3.2):
   for z in np.arange(372,543,6):
    if dry.difference(clear).covers(Point(x,z).buffer(1.2)):lounge(x,z)
  for x,z in [(-440,374),(-412,374),(-380,375),(-441,418),(-416,417),(-386,417),(-443,476),(-383,473),(-446,493),(-416,493),(-446,539),(-416,539)]:F(x,z).plant(0,0,True)
  for x,z,w,d in [(-425,369,14,6),(-400,479,14,5),(-437,487,14,5)]:pergola(x,z,w,d);patio_table(x,z)
  # Mediterranean pine/topiary canopies and garden borders, beside clear routes.
  for x,z in [(-442,375),(-412,375),(-379,375),(-442,420),(-415,421),(-383,420),(-444,473),(-381,473),(-446,500),(-415,540),(-444,538)]:
   f=F(x,z);f.lathe('bark',0,0,[(0,.22),(3.8,.14)],10)
   for dx,dz,yy,rr in [(0,0,4.5,2.5),(-1,0,4.8,1.9),(1,0,5,2),(0,1,5.3,1.8)]:b.sphere('foliage',(x+dx,yy,z+dz),rr,12,7,scale=(1,.6,1))
  for z in [370,426,476,544]:
   p=box(-447,z,-417,z+1.2).intersection(dry).difference(clear);hedge(p)
 elif key=='bellagioConservatory':
  for x in [-329,-312]:
   for z in [435,455]:
    hedge(box(x-4,z-4,x+4,z+4));F(x,z).plant(0,0,True)
    for a in np.linspace(0,math.tau,24,endpoint=False):b.sphere(['rose','orchid','gold'][int(a*10)%3],(x+3*math.cos(a),1.2,z+3*math.sin(a)),.32,8,5)
  circle_fountain(-320,445,2.5)
 else:
  for x in [-233,-208]:
   for z in np.arange(260,410,17):
    if site.covers(Point(x,z).buffer(3)):F(x,z).lounge(0,0);column(x,z+6,h=8.7)
  for z in np.arange(248,416,15):F(-242,z).chandelier(0,0,7.5)
  for x in [-252,-232]:
   for z in [272,302,338]:
    for dx in [-1.5,0,1.5]:F(x+dx,z).slot(0,0)
 for x,z in [((x0+x1)/2,z0+10),((x0+x1)/2,z1-10)]:F(x,z).light(0,6,0,power=120,range=23)
 views={'entrance':dict(eye=[-230,1.94,445],target=[-269,5,445]),'deck':dict(eye=[-379,1.94,423],target=[-409,2,395])} if key=='bellagioLobby' else {'entrance':dict(eye=[(x0+x1)/2,1.94,z1-4],target=[(x0+x1)/2,2,z0+4]),'deck':dict(eye=[-379,1.94,423],target=[-409,2,395])}
 venues.append(dict(key=key,name=key.replace('bellagio','Bellagio · '),building='bellagio',bounds=list(bounds),portals=[],outside=key in ['bellagioGarden','bellagioConservatory'],levelY=G,preloadDistance=50,zones=[dict(origin=[(x0+x1)/2,G,z0],yaw=0,width=x1-x0,depth=z1-z0,height=8.5)],accessPoints=[[x,G,z] for x in np.arange(x0+8,x1,25) for z in np.arange(z0+8,z1,25)],lights=b.lights[-2:],views=views))
lakefront_report=lakefront.build(b,site,via,slab,routes,portals)
(OUT/'lakefront-report.json').write_text(json.dumps(lakefront_report,indent=2))
venues[0]['bounds']=list(site.union(lakefront.LAKE.buffer(6)).bounds)
venues[0]['views']['lakefront']=dict(eye=[-3,47,283],target=[-102,8,222])
venues[0]['views']['shore']=dict(eye=[-18,1.94,274],target=[-101,12,222])
venues[0]['views']['bridge']=dict(eye=[-68.44,7.825,172.1],target=[-68.17,7.825,205.91])
venues[0]['views']['bridge-stairs']=dict(eye=[-48.526,7.825,204.909],target=[-29.526,1.92,215.909])
south_arrival.build(b,site,lakefront.LAKE,routes)
garage_report=garage.build(b,routes)
(OUT/'garage-report.json').write_text(json.dumps(garage_report,indent=2))
venues[0]["views"]["arrival-aerial"]=dict(eye=[45,110,667],target=[-135,12,504])
venues[0]["views"]["arrival"]=dict(eye=[-44,2,553],target=[-143,6,530])
venues[0]['views']['garage']=dict(eye=[-285,27,606],target=[-285,4,530])
venues[0]['views']['garage-entry']=dict(eye=[-258,5.4,574],target=[-258,5.4,545])
venues[0]['views']['sign-stairs']=dict(eye=[-61,1.895,584.5],target=[-46,5,584.5])
from ramp_barriers import finish_barriers
finish_barriers(b)
(OUT/'ramp-barriers.json').write_text(json.dumps(b.ramp_barriers,indent=2))
from bellagio_edge_ownership import reconcile,close_roadside,support_roadside_verge
edge_report={'roadsideClosureM2':close_roadside(b,json.loads(Path('build/geographic-strip/city-meshes.json').read_text())),'ownership':reconcile(b)}
edge_report['vergeSupportTrianglesAdded']=support_roadside_verge(b,json.loads(Path('build/geographic-strip/city-meshes.json').read_text()))
(OUT/'lake-edge-ownership.json').write_text(json.dumps(edge_report,indent=2))
import bellagio_service
bellagio_service.build(b)
b.save_all()
for v in venues:
 for layer in ['exterior','interior']:
  p=OUT/(v['key']+'-'+layer+'-collision.json')
  if not p.exists():p.write_text(json.dumps(dict(vertices=[],indices=[])))
(OUT/'venues.json').write_text(json.dumps(venues,indent=2,default=float));(OUT/'routes.json').write_text(json.dumps(routes,indent=2,default=float))
# Explicit replacement ownership, never a bounding-box delete of all neighbors.
ids=['way/25718288','relation/1599958','way/25723909','way/114703388','way/114716305','way/114716306','way/114717628','way/114717630','way/114718351']+lakefront.ROOF_IDS
(OUT/'replacement-ids.json').write_text(json.dumps(ids))
(OUT/'geometry-report.json').write_text(json.dumps(dict(triangles=sum(len(g['faces']) for g in b.groups.values()),batches=len(b.groups),architecturalTipM=155.8,mainFootprint=list(tower.bounds),siteFootprint=list(site.bounds),poolCount=len(pools),newRoutes=len(routes),retainedOwners=['Bellagio custom casino/interior','Bellagio custom guest templates','Bellagio Spa Tower collision (visuals: bellagio_towers.py)','Via Bellagio bridge passage','south covered walkway','parking and theatre'],estimates=['Roof wing heights','Pool and patio physical elevations','Pool dimensions and garden furniture placement'],limits=['Legacy casino retains prototype position','Detailed service facade and restaurant-specific fit-out need further comparison','All new interiors require runtime walk verification']),indent=2))
print('Bellagio:',len(b.groups),'batches,',sum(len(g['faces']) for g in b.groups.values()),'triangles')
