"""STRAT Level8 Swim & Social: traced aerial plan and official August2023 photo.
Absolute elevation26.25m and roof/awning dimensions remain estimates.
"""
from common import *
from forum_shops import facade_frame
KEY='stratPoolDeck';IDS=['way/89469749'];Y=26.25
# Satellite screen registration at 1280x720, Maps zoom20. Centre36.14693,-115.15755.
def xy(x,z):return (1390.0+(x-640)*.1215,-3443.3+(z-360)*.1215)
def poly(points):return Polygon([xy(*q)for q in points])
def chair(B,x,z,yaw=0):
 F=Frame(B,x,z,yaw,y=Y);F.box('spool-cushion-paint',(0,.45,.1),(.69,.10,1.30));
 for side in [-1,1]:
  F.tube('spool-white-frame-paint',(side*.37,.17,-.95),(side*.37,.46,.88),.025,8)
  for w in [-.65,.65]:F.tube('spool-white-frame-paint',(side*.32,.03,w),(side*.32,.44,w-.15),.025,8)
 B.face('spool-cushion-paint',[F.p(-.345,.49,-.55),F.p(.345,.49,-.55),F.p(.345,.99,-1.08),F.p(-.345,.99,-1.08)])
 for side in [-1,1]:F.tube('spool-white-frame-paint',(side*.36,.49,-.55),(side*.36,1.01,-1.09),.025,8)
def umbrella(B,x,z):
 F=Frame(B,x,z,y=Y);F.lathe('spool-white-frame-paint',0,0,[(0,.03),(2.55,.03)],10)
 for i in range(8):
  a=i*math.tau/8;b=(i+1)*math.tau/8;B.face('spool-blue-fabric-paint',[F.p(0,2.65,0),F.p(1.5*math.cos(a),2.24,1.5*math.sin(a)),F.p(1.5*math.cos(b),2.24,1.5*math.sin(b))]);F.tube('spool-white-frame-paint',(0,2.56,0),(1.48*math.cos(a),2.23,1.48*math.sin(a)),.013,6)
def exterior(B):
 B.property=KEY+'-exterior';B.source='strat-pool-deck';B.detail=0;platform=footprint('way/89469753');hut=footprint(IDS[0]);site=platform.union(hut.buffer(.7)).buffer(2,join_style=2).buffer(-2,join_style=2).difference(footprint('way/543641711').buffer(.20));W=Frame(B,0,0,y=0)
 raw=poly([(657,429),(680,410),(711,385),(747,373),(773,354),(806,356),(832,369),(841,391),(838,411),(826,432),(831,455),(850,480),(878,484),(899,472),(918,450),(940,433),(973,439),(1005,457),(1003,488),(987,513),(958,518),(943,527),(924,524),(912,535),(895,547),(889,571),(865,582),(834,579),(814,567),(800,547),(778,535),(758,534),(733,543),(711,553),(691,550),(677,529),(660,501),(652,472),(661,451)])
 basin=raw.buffer(1.1,join_style=1).buffer(-1.1,join_style=1).intersection(platform.buffer(-1));assert basin.area>500,basin.area
 deck=site.difference(basin.buffer(.24));B.planar('spool-deck-concrete',deck,Y,True)
 # Recessed basin: no collidable water sheet or old roof at the water level.
 B.planar('spool_pool',basin,Y-.18);B.planar('spool-basin-paint',basin,Y-1.25,True);B.shell(basin,Y-1.25,Y-.18,'spool-blue-tile',roof=False)
 B.planar('spool-coping-concrete',basin.buffer(.24).difference(basin),Y+.035,True)
 B.shell(basin,Y-.26,Y-.08,'spool-blue-tile',roof=False)
 # Pavilion sits on the pool level, not beneath the casino podium.
 B.shell(hut,Y,Y+3.1,'spool-white-stucco',roof=False);B.planar('spool-roof-paint',hut,Y+3.1,True);B.planar('spool-deck-concrete',hut,Y,True)
 for a,b in zip(list(hut.exterior.coords),list(hut.exterior.coords)[1:]):
  F,L,nx,nz=facade_frame(B,a,b,hut,.08);F.y=Y
  F.box('spool-white-frame-paint',(L/2,3.12,-.07),(L,.16,.25))
  if nz>.5 and L>5:
   for u in np.arange(.9,L-.6,1.6):
    F.box('spool-window-frame-paint',(float(u),1.55,-.06),(1.46,2.55,.12));F.box('spool-glass',(float(u),1.55,-.14),(1.32,2.41,.04))
   F.text('SWIM & SOCIAL',(L/2,2.78,-.20),.28,'spool-blue-letter')
  elif L>4:F.box('spool-service-paint',(L*.6,1.2,-.1),(.95,1.5,.13))
 # Three tensile shades extend over the pool edges, with black metal frames.
 for points in [[(635,372),(681,380),(653,438),(617,411)],[(634,484),(704,560),(663,576),(615,530)],[(944,414),(1018,438),(1014,468),(933,438)]]:
  q=[xy(*v)for v in points];pts=[(x,Y+(3.0 if i%2 else 4.0),z)for i,(x,z)in enumerate(q)]
  for (x,z),top in zip(q,pts):B.tube('spool-dark-frame-paint',(x,Y,z),top,.055,10)
  B.face('spool-yellow-fabric-paint',pts);B.path('spool-dark-frame-paint',pts+[pts[0]],.055,8)
 # Low cabana range along the southern edge. Alternating fabric strips are disjoint.
 cabanas=[]
 for px,pz in [(675,625),(719,629),(842,647),(881,651),(939,655),(977,658),(1110,310),(1152,316)]:
  x,z=xy(px,pz);cab=box(x-2,z-2.3,x+2,z+2.3)
  if not site.buffer(-.6).covers(cab) or cab.intersects(basin.buffer(1)):continue
  F=Frame(B,x,z,y=Y);cabanas.append(cab.buffer(.8));F.box('spool-white-stucco',(0,1.55,2.1),(4.0,3.1,.18),True)
  for u in [-1.92,1.92]:F.box('spool-white-frame-paint',(u,1.4,-2.0),(.09,2.8,.09),True)
  for j in range(20):
   a=-2+j*.2;b=a+.2;mat='spool-yellow-fabric-paint' if j%2 else 'spool-white-fabric-paint'
   B.face(mat,[F.p(a,3.05,2.2),F.p(b,3.05,2.2),F.p(b,2.65,-2.2),F.p(a,2.65,-2.2)])
   B.face(mat,[F.p(a,2.65,-2.2),F.p(b,2.65,-2.2),F.p(b,2.45,-2.2),F.p(a,2.45,-2.2)])
  F.box('spool-cushion-paint',(0,.5,.8),(3.1,.35,1.2));F.box('spool-cushion-paint',(0,.94,1.3),(3.1,.55,.18))
 # Round daybeds and blue umbrellas along the southeast pool edge.
 B.detail=1
 for px,pz in [(770,570),(912,572),(945,551),(981,555),(1009,537),(845,450),(885,458)]:
  x,z=xy(px,pz)
  if not deck.buffer(-1.1).contains(Point(x,z)):continue
  B.lathe('spool-white-frame-paint',(x,z),[(Y,.95),(Y+.32,.95)],24);B.lathe('spool-blue-fabric-paint',(x,z),[(Y+.32,.93),(Y+.55,.93)],24);umbrella(B,x,z)
 reserved=unary_union(cabanas).union(basin.buffer(1.2)).union(hut.buffer(1.5))
 # Separate lounge groups reproduce the eastern and western rows without perimeter over-density.
 for pxs,pzs in [(range(1060,1250,25),range(420,591,30)),(range(515,597,27),range(390,557,31))]:
  for px in pxs:
   for pz in pzs:
    x,z=xy(px,pz)
    if site.buffer(-1.3).contains(Point(x,z))and not reserved.buffer(1.3).contains(Point(x,z)):chair(B,x,z,.08)
 B.detail=0
 # Solid parapets on exposed edges; north joints meeting garage/hotel stay open.
 for a,b in zip(list(platform.exterior.coords),list(platform.exterior.coords)[1:]):
  F,L,nx,nz=facade_frame(B,a,b,platform,0);F.y=Y
  if nz<-.4:continue
  F.box('spool-white-stucco',(L/2,.65,0),(L,1.3,.22),True);F.box('spool-coping-concrete',(L/2,1.33,0),(L,.08,.30))
 samples=[]
 for x in np.arange(site.bounds[0]+1,site.bounds[2],3):
  for z in np.arange(site.bounds[1]+1,site.bounds[3],3):
   q=Point(x,z)
   if not site.buffer(-.4).contains(q):continue
   expected=Y+3.1 if hut.contains(q) else (Y-1.25 if basin.buffer(-.4).contains(q) else Y)
   if basin.boundary.distance(q)<.5:continue
   samples.append([float(x),expected+.35,float(z)])
 routes=[[(1376,Y,-3438),(1376,Y,-3428),(1376,Y,-3415)],[(1438,Y,-3434),(1448,Y,-3434),(1455,Y,-3421)],[(1384,Y,-3438),(1388,Y,-3438),(1392,Y,-3438)]]
 Path('build/city-exteriors/strat-pool-deck-samples.json').write_text(json.dumps(samples));Path('build/city-exteriors/strat-pool-deck-stairs.json').write_text(json.dumps(routes))
 return dict(key=KEY,name='STRAT Swim and Social pool deck',center=[1408,Y,-3427],bounds=list(site.bounds),structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
