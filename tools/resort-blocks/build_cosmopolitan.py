"""Cosmopolitan full-block geometry in geographic metres. No site-wide scaling.
Floor elevations are fitted estimates; official maps establish labels and topology.
The mislabeled third OSM high-rise is used as podium, not another 184m tower.
"""
import sys,json,math
from pathlib import Path
sys.path.insert(0,'tools/strip-landmarks')
from common import *
import common
OUT=Path('build/resort-blocks/cosmo');OUT.mkdir(parents=True,exist_ok=True);common.OUT=OUT
b=Meshes();venues=[];routes=[]
GROUND=.24;LEVELS=[.24,5.84,11.44,17.04,22.64]
site=footprint('way/1212809711')
jockey=[footprint(k) for k in ['way/27897904','way/699020450']]
chelsea=footprint('way/27897905');boulevard=footprint('way/134795273')
# North low-rise condominium blocks retain their own footprint, roofline and owner.
public=site.difference(unary_union(jockey).buffer(.18))
entry_aprons=unary_union([box(-40,697,-31,709),box(-40,634,-31,644),box(-275,726,-265,734),box(-389,702.5,-362,723.5)])
stair_x=[-170,-318];stair_holes=unary_union([box(x-2.05,697.8,x+2.05,712.2) for x in stair_x])
F=lambda x,z,y=GROUND,yaw=0:Frame(b,x,z,yaw,y)
def source(n,detail=0):b.source=n;b.detail=detail

def rail_ring(p,y,openings=None):
 for poly in parts(p):
  for ring in [poly.exterior,*poly.interiors]:
   for a,c in zip(list(ring.coords),list(ring.coords)[1:]):
    line=LineString([a,c]);segments=line.difference(openings) if openings is not None else line
    for edge in [segments] if segments.geom_type=='LineString' else getattr(segments,'geoms',[]):
     if edge.geom_type!='LineString' or edge.length<.08:continue
     a,c=list(edge.coords)[0],list(edge.coords)[-1];F(0,0,y).rail(a,c,glass=True)

def slab(p,y,mat='tile',thick=.32):
 b.extrude(mat,p,y-thick,y,True)
 # Explicit soffit avoids one-sided undersides and sky leaks.
 b.planar(mat,p,y-thick)

def route(name,ps):routes.append(dict(name=name,points=ps))
def table(x,z,y,umbrella=False):
 f=F(x,z,y);f.lathe('steel',0,0,[(0,.3),(.08,.3),(.1,.045),(.73,.045)],12);f.lathe('marble',0,0,[(.73,.62),(.79,.62)],20)
 for dx,dz in [(1,0),(-1,0),(0,1),(0,-1)]:
  f.box('walnut',(dx,.44,dz),(.5,.12,.5));f.box('walnut',(dx,.76,dz+.23),(.5,.58,.055))
  for a in [-.17,.17]:f.box('steel',(dx+a,.2,dz),(.045,.4,.38))
 if umbrella:
  f.tube('steel',(0,0,0),(0,2.65,0),.035)
  for i in range(8):
   a=i*math.tau/8;c=(i+1)*math.tau/8
   b.face('ivory',[f.p(0,2.8,0),f.p(1.75*math.cos(a),2.32,1.75*math.sin(a)),f.p(1.75*math.cos(c),2.32,1.75*math.sin(c))])
def pool(poly,y):
 source(b.source);b.extrude('stone',poly.buffer(.38),y-.3,y+.10,True);b.planar('water',poly,y+.115)
 # Contained shallow basin: people cannot fall through the visual water.
 for p in parts(poly):
  for a,c in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):b.tube('ivory',(a[0],y+.13,a[1]),(c[0],y+.13,c[1]),.09,8)
def cabana(x,z,y):
 f=F(x,z,y);f.floor(4.5,3.5,mat='walnut')
 for xx in [-2,2]:
  for zz in [-1.5,1.5]:f.box('white',(xx,1.4,zz),(.13,2.8,.13))
 f.box('white',(0,2.85,0),(4.4,.14,3.4));f.box('velvet',(0,.48,.2),(3.2,.3,1.7));f.box('ivory',(0,.73,1),(3.2,.6,.3))
 for xx in [-1.85,1.85]:f.box('ivory',(xx,1.38,.5),(.04,2.65,2.1))
def deck_furnish(poly,y,spacing=5):
 source('deck-loungers',1)
 minx,minz,maxx,maxz=poly.bounds
 for x in np.arange(minx+2,maxx-2,spacing):
  for z in np.arange(minz+2,maxz-2,spacing):
   if not poly.covers(Point(x,z).buffer(1.2)):continue
   f=F(x,z,y);f.box('walnut',(0,.30,0),(.8,.10,2));f.box('ivory',(0,.40,-.3),(.73,.13,1.3))
   # Reclining upholstered back, head cushion and separate frame runners.
   for xx in [-.365,.365]:
    b.face('ivory',[f.p(xx,.34,.35),f.p(xx,.44,.32),f.p(xx,.85,.94),f.p(xx,.75,1.0)])
   b.face('ivory',[f.p(-.365,.44,.32),f.p(.365,.44,.32),f.p(.365,.85,.94),f.p(-.365,.85,.94)])
   b.face('ivory',[f.p(-.365,.34,.35),f.p(-.365,.75,1),f.p(.365,.75,1),f.p(.365,.34,.35)])
   f.box('velvet',(0,.78,.82),(.6,.12,.22))
   for xx in [-.4,.4]:f.tube('steel',(xx,.4,-.9),(xx,.4,.32),.025)
   for xx in [-.28,.28]:f.box('steel',(xx,.15,0),(.035,.3,1.7))

def tower(poly,name):
 source('guest-'+name);base=22.64;top=184
 b.shell(poly.buffer(-1.25,join_style=2),base,top,'darkglass',solid=False)
 b.planar('roof',poly,top)
 # Separate recessed glass from projecting balcony noses; metre-scale bands.
 for y in np.arange(base,top-1,3.36):
  b.extrude('silver',poly,y,y+.20,False)
  b.shell(poly.buffer(-.12,join_style=2),y+.32,y+1.3,'darkglass',roof=False,solid=False)
 source('balcony-bays-'+name,1)
 for p in parts(poly):
  for a,c in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
   length=math.dist(a,c)
   if length<2:continue
   dx,dz=(c[0]-a[0])/length,(c[1]-a[1])/length
   for dist in np.arange(1,length,3.15):
    x,z=a[0]+dx*dist,a[1]+dz*dist
    b.box('steel',(x,103,z),(.09,159,.09))
    # Balcony dividers/recess highlights remain cheap batched geometry.
    for y in np.arange(base+1.45,top-2,3.36):b.box('blue3',(x,y,z),(.12,.10,.12))
 source('tower-crown-'+name)
 b.shell(poly.buffer(-.3,join_style=2),181.6,184,'charcoal',roof=False,solid=False)
 for y in [182,182.4,182.8,183.2]:b.shell(poly,y,y+.055,'silver',roof=False,solid=False)

# Permanent envelope; roof decks and all vertical public circulation are real geometry.
b.property='cosmo-exterior';source('podium')
portals=[dict(p=[-36.75,GROUND,703],yaw=-math.pi/2,width=9,height=4.5,name='Las Vegas Boulevard / Chandelier'),dict(p=[-36.6,GROUND,639],yaw=-math.pi/2,width=7,height=4.5,name='The Henry / north Strip'),dict(p=[-364,GROUND,713],yaw=math.pi/2,width=9,height=4.5,name='Chelsea motor court'),dict(p=[-270,GROUND,729.1],yaw=math.pi,width=8,height=4.5,name='Harmon Avenue')]
for y in LEVELS[:4]:
 slab(public.difference(stair_holes.union(Point(-64,700).buffer(10))) if GROUND<y<17 else public.difference(stair_holes) if y>GROUND else public.union(entry_aprons),y,'stone' if y==GROUND else 'tile')
 # Streetfront glass is three storeys, with precisely separate slab bands.
 if y<17:b.shell(public,y,y+5.28,'cosmo-mirror',openings=portals if y==GROUND else [dict(p=[-37,5.84,719],yaw=-math.pi/2,width=8,height=4.6),dict(p=[-49,5.84,734],yaw=math.pi,width=7,height=4.6)] if y==LEVELS[1] else (),roof=False,solid=True)
 # The slab extrusion already owns its edge. A second coplanar fascia here
 # produces a flickering black band when viewed through the street glazing.
# Balustrades around the two open Chandelier galleries.
for y in LEVELS[1:3]:rail_ring(Point(-64,700).buffer(10),y)
# Roof arrangement leaves Jockey Club and both tower plans legible.
chelsea_deck=box(-363,690,-205,727).difference(chelsea)
chelsea_services=box(-363,616,-310,657)
roof14=unary_union([chelsea_deck,chelsea_services,box(-362,650,-310,720),chelsea,boulevard,box(-127,644,-115,719),box(-175,714,-115,719),box(-330,652,-314,676),box(-125,643,-75,652),box(-178,690,-162,719),box(-321,698,-311,719)])
slab(roof14.difference(stair_holes),LEVELS[4],'stone')
# Enclosed transition storey joins the occupied podium to both tower footprints.
# No solid core block: existing guest stairs and roof access retain their openings.
source('tower-podium-stems')
for poly in [chelsea,boulevard]:
 b.shell(poly.buffer(-1.25,join_style=2),17.04,22.64,'cosmo-mirror',roof=False,solid=False)
 for yy in [17.12,19.85,22.45]:b.shell(poly.buffer(-1.19,join_style=2),yy,yy+.16,'silver',roof=False,solid=False)
# Opaque reflective glazing replaces almost-invisible alpha glass. Tall mullions
# and projecting stone piers reproduce the lower-level curtain-wall rhythm.
source('podium-mirror-grid')
for part in parts(public):
 for ring in [part.exterior,*part.interiors]:
  for a,c in zip(list(ring.coords),list(ring.coords)[1:]):
   le=math.dist(a,c)
   if le<2:continue
   dx,dz=(c[0]-a[0])/le,(c[1]-a[1])/le;nx,nz=dz,-dx
   if public.contains(Point((a[0]+c[0])/2+nx,(a[1]+c[1])/2+nz)):nx,nz=-nx,-nz
   for j in range(max(1,round(le/2.8))+1):
    t=j*le/max(1,round(le/2.8));x,z=a[0]+dx*t+nx*.12,a[1]+dz*t+nz*.12
    if any(math.hypot(x-p['p'][0],z-p['p'][2])<p['width']/2+.5 for p in portals):continue
    b.box('silver',(x,8.55,z),(.13,16.6,.13))
    if j%5==0:b.box('ivory',(x+nx*.12,8.55,z+nz*.12),(.55,16.6,.55))
 for yy in [3.0,8.6,14.2]:b.shell(part.buffer(.075,join_style=2),yy,yy+.09,'silver',roof=False,solid=False)
# Tower bases are not colliding solid blocks: guest cores occupy their interiors.
tower(chelsea,'chelsea');tower(boulevard,'boulevard')
source('podium-columns',1)
for z in np.arange(630,734,5.6):b.box('silver',(-36.65,8.5,z),(.3,16.5,.18))
for x in np.arange(-359,-42,8):b.box('charcoal',(x,8.5,731),(.32,16.5,.30))
source('podium-signage',1);F(-36.25,675,GROUND,-math.pi/2).text('THE COSMOPOLITAN',(0,13.6,0),1.1)
F(-98,624,175).text('THE COSMOPOLITAN',(0,3,-.3),1.9)
F(-276,674,177).text('THE COSMOPOLITAN',(0,2,-1),2.3)
# Portal trim and complete sheltered motor court.
for p in portals:
 f=F(p['p'][0],p['p'][2],p['p'][1],p['yaw']);f.portal(w=p['width'],h=p['height'],name=p['name'])
source('chelsea-porte-cochere');f=F(-376,713)
f.box('charcoal',(0,5.9,0),(27,.7,22));f.box('warm',(0,5.49,0),(23,.035,18))
for x in [-11,11]:
 for z in [-8,8]:f.box('silver',(x,2.75,z),(.5,5.5,.5),True)
f.text('THE COSMOPOLITAN',(0,4.65,-10.95),.65)
for z in [-8,8]:f.plant(-8,z);f.plant(8,z)
# Keep both surveyed service-drive centerlines, but correct the inferred bridge
# grade across the ground-level arrival. Endpoints retain the adjacent city grade.
# This is an explicit fitted grade, not a surveyed road elevation.
source('chelsea-drive')
for road in json.load(open('build/geographic-strip/road-network.json'))['roads']:
 if str(road['id']).split('/')[-1] not in ('682151838','682151847'):continue
 pts=road['points']
 for a,c in zip(pts,pts[1:]):
  count=max(1,math.ceil(math.dist(a,c)/1.5))
  for t in range(count):
   p=np.array(a)+(np.array(c)-a)*t/count;q=np.array(a)+(np.array(c)-a)*(t+1)/count
   for v in [p,q]:
    v[1]=.255+(2.681380290917158-.255)*max(0,min(1,(v[2]-718)/(735.5880632127364-718)))
    if road['id']==682151847:v[1]-=.12*max(0,min(1,(690-v[2])/(690-662.6292689468899)))
    else:v[1]+=(.7651878026671267-.255)*max(0,min(1,(715-v[2])/(715-711.1200391367713)))
   dx,dz=q[0]-p[0],q[2]-p[2];length=math.hypot(dx,dz);nx,nz=-dz/length*2.25,dx/length*2.25
   top=[(p[0]+nx,p[1],p[2]+nz),(q[0]+nx,q[1],q[2]+nz),(q[0]-nx,q[1],q[2]-nz),(p[0]-nx,p[1],p[2]-nz)]
   b.face('charcoal',top,True)
   for u,v in zip(top,top[1:]+top[:1]):b.face('charcoal',[u,(u[0],u[1]-.25,u[2]),(v[0],v[1]-.25,v[2]),v])
# Upper bridge thresholds: ramps join the existing 6.24m bridge datum.
source('bridge-landings');F(-37,719,5.84,-math.pi/2).floor(9,12,z=-3)
F(-37,719,5.84,-math.pi/2).stairs(0,-7.5,7,.4,4)
F(-49,733,5.84).floor(7,8)
F(-49,0,5.84).stairs(0,737,4.5,.195,7.25)
for x in [-51.15,-46.85]:b.tube('steel',(x,6.94,737),(x,7.135,744.25),.045)
route('Harmon bridge threshold',[[-49,5.84,727],[-49,5.84,737],[-49,6.035,744.25],[-48.3297,6.035,745.043],[-47.445,6.035,750.977]])
# Two continuous stairs connect all public levels. Upper floor voids persist at every landing.
source('public-stairs')
for x in stair_x:
 for i,y in enumerate(LEVELS[:-1]):
  f=F(x,0,y);f.stairs(0,697.8,3.8,5.6,14.4)
  route(f'public stair {x} / {i+1}',[[x,y,697.5],[x,y,697.8],[x,y+5.6,712.2],[x,y+5.6,716],[x+5,y+5.6,716],[x+5,y+5.6,694],[x,y+5.6,694]])
  # Transparent upper guards leave landings open at both ends.
  for sx in [-2.03,2.03]:f.rail((sx,698),(sx,712),glass=True)
# Reachable roof passage from east stair to the Boulevard guest stair.
source('level14-guest-passage')
rail_ring(box(-175,714,-115,719),22.64,box(-174,709,-164,720).union(box(-127,714,-115,720)))
# Jockey Club: low blocks with actual window rhythm, parapet and roof plant.
for j,poly in enumerate(jockey):
 source('jockey-club-'+str(j));height=[39,36][j];b.shell(poly,GROUND,height,'ivory',solid=True)
 for part in parts(poly):
  for a,c in zip(list(part.exterior.coords),list(part.exterior.coords)[1:]):
   le=math.dist(a,c)
   if le<3:continue
   dx,dz=(c[0]-a[0])/le,(c[1]-a[1])/le
   for t in np.arange(1.7,le-1,3.4):
    for y in np.arange(3.5,height-2,3.1):
     x,z=a[0]+t*dx,a[1]+t*dz;b.box('darkglass',(x,y,z),(1.45,1.6,.15),False,-math.atan2(dz,dx))
 b.shell(poly,height,height+.8,'ivory',roof=False,solid=False)
 source('jockey-roof-plant',1);c=poly.centroid
 for x in [-4,4]:b.box('silver',(c.x+x,height+.8,c.y),(3,1.6,3))
# Slab perimeter guard rails around public roof and recreation level.
source('deck-boundaries');rail_ring(site,17.04);rail_ring(roof14,22.64,box(-128,640,-112,670).union(box(-330,650,-310,679)))
# Ground welcome plaza: furniture never intersects the entry route.
source('street-frontage',1)
for z in [632,649,667,686,722,734]:F(-32,z).plant(0,0,True)
for z in [654,682,728]:F(-32,z).bench(0,0)
# Exterior placeholder for streaming interface; decorated public chunks below.
source('interior-anchor');b.property='cosmo-interior';b.box('charcoal',(-300,-2,710),(.01,.01,.01))
venues.append(dict(key='cosmo',name='Cosmopolitan complete exterior',building='cosmopolitan',bounds=list(site.bounds),portals=portals,zones=[],accessPoints=[[-50,.24,703]],lights=[],views={'entrance':dict(eye=[-20,2,703],target=[-65,5,703]),'aerial':dict(eye=[70,155,530],target=[-200,65,678]),'north':dict(eye=[-185,2,599],target=[-260,110,672]),'frontage':dict(eye=[-18,10,601],target=[-79,19,651]),'arrival-aerial':dict(eye=[-15,42,607],target=[-92,14,661])}))
# Each mapped public level is a streamed furnishing set. Structural floors/stairs
# belong to the permanent envelope; their collision is a single nearby mesh.
for i,(label,y) in enumerate(zip(['1','2','3','4','14'],LEVELS)):
 key='cosmoL'+label;b.property=key+'-exterior';source('level-marker');b.box('charcoal',(-300,-2,710),(.01,.01,.01))
 b.property=key+'-interior';source('level-'+label);f=F(0,0,y)
 if label=='1':
  # Main circulation east/west, registration at Chelsea, LED columns, casino islands.
  for x in [-350,-341,-332]:
   for z in [701,719]:
    f.box('charcoal',(x,2.55,z),(1.4,5.1,1.4),True)
    for dx,dz,w,d in [(0,-.711,1.3,.025),(0,.711,1.3,.025),(-.711,0,.025,1.3),(.711,0,.025,1.3)]:f.box('screen',(x+dx,2.65,z+dz),(w,4.65,d))
  F(-341,726,y).reception(0,0,20,'THE COSMOPOLITAN')
  for x in np.arange(-297,-190,14):
   for z in [676,692,720]:
    for dx in [-2,0,2]:f.slot(x+dx,z)
  for x in [-288,-270,-250,-228,-206]:f.lounge(x,708)
  for x in [-130,-112,-92]:
   for z in [685,715]:f.lounge(x,z)
  for x in np.arange(-348,-55,18):f.box('warm',(x,5.15,707),(8,.04,.1));f.light(x,4.5,707,power=45,range=20)
  for x in [-276,-224]:b.planar('carpet',box(x-24,669,x+24,697),y+.012)
  # The three-storey Chandelier is visible from every gallery via permanent holes.
  for n in range(140):
   a=n*2.399;r=8+1.4*math.sin(n*.23);x=-64+r*math.cos(a);z=700+r*math.sin(a)
   b.tube('silver',(x,y+.7,z),(x,15.8,z),.018,4)
   for yy in np.arange(1+(n%3)*.28,15.8,.7):b.box('ice',(x,yy,z),(.065,.15,.065))
  F(-64,700,y).lathe('blackiron',0,0,[(0,4.2),(.95,4.2),(1.05,4.4)],48)
  for x in [-52,-46]:table(x,645,y)
 elif label=='2':
  for x,z,name in [(-60,650,'EGGSLUT'),(-95,718,'BLOCK 16'),(-217,722,'WICKED SPOON'),(-260,722,'MARQUEE'),(-52,683,'THE CHANDELIER')]:
   g=F(x,z,y);g.reception(0,0,10,name);g.text(name,(0,3.8,1.7),.45)
  for x in [-296,-278,-235,-204,-193,-153,-130,-107]:f.lounge(x,704)
  for x in np.arange(-108,-42,9):table(x,729,y)
 elif label=='3':
  for x,z,name in [(-60,641,'OVERLOOK / POOL ↑'),(-54,674,'MOMOFUKU'),(-100,716,'JALEO'),(-130,721,'SCARPETTA'),(-220,722,'STK'),(-341,675,'THE CHELSEA')]:
   g=F(x,z,y);g.reception(0,0,10,name)
  for x in [-280,-255,-228,-200,-142,-119,-94,-59]:
   for z in [687,719]:table(x,z,y)
  # Strip-facing restaurant terrace with tables, overhead slats and planted edge.
  source('restaurant-patio')
  for z in [662,669,676,683]:table(-43,z,y,True)
  f.box('walnut',(-48,4.1,674),(9,.2,31))
 elif label=='4':
  source('boulevard-pool')
  bp=Polygon([(-63,640),(-43,640),(-42,660),(-45,670),(-60,670),(-64,661)])
  pool(bp,y);deck=box(-68,629,-37,690).difference(bp.buffer(2))
  deck_furnish(deck,y,4.4)
  for z in [674,679,684]:cabana(-61,z,y)
  source('overlook-grill');g=F(-52,720,y);g.reception(0,0,11,'OVERLOOK GRILL')
  for x in [-59,-47]:
   for z in [706,712,727]:table(x,z,y,True)
  for z in [634,675,688,730]:f.plant(-40,z,True)
  # Marquee's lower outdoor terrace sits between the two towers.
  source('marquee-terrace');mp=box(-193,677,-178,688);pool(mp,y)
  for x in [-199,-192,-185,-178,-171,-164]:cabana(x,673,y)
  deck_furnish(box(-202,670,-156,691).difference(mp.buffer(2)),y,5.3)
  F(-198,691,y).reception(0,0,8,'MARQUEE')
 elif label=='14':
  source('chelsea-pool');cp=Polygon([(-346,719),(-337,716),(-285,718),(-275,724),(-339,724)])
  pool(cp,y);deck_furnish(chelsea_deck.difference(cp.buffer(2)),y,5)
  for x in [-354,-345,-336,-327,-318,-309]:f.plant(x,700)
  for x in [-355,-220]:F(x,722,y).reception(0,0,9,'WEST BAR' if x<-300 else 'EAST BAR')
  source('fitness-courts');court=box(-358,620,-329,650);b.planar('sage',court,y+.01)
  for x in [-355,-332]:f.box('white',(x,.025,635),(.07,.02,26))
  for z in [622,635,648]:f.box('white',(-343.5,.025,z),(23,.02,.07))
  f.box('blackiron',(-343.5,.52,635),(23,.95,.025));rail_ring(court,y,box(-344,648,-340,652))
  F(-320,650,y).reception(0,0,10,'SAHRA SPA / FITNESS')
  # Elevated connections to the two existing hotel streaming cores.
  # Guest access floors are unioned into the permanent roof slab.
 for x in stair_x:
  F(x+6,695,y).text('LEVEL '+label+'  /  POOLS · DINING · GUEST ROOMS',(0,2.7,0),.22)
 route('Level '+label+' main gallery',[[-352,y,707],[-326,y,707],[-326,y,694],[-307,y,694],[-307,y,707],[-185,y,707],[-177,y,694],[-159,y,694],[-137,y,694],[-133,y,703],[-78,y,703],[-78,y,714],[-50,y,714],[-43,y,703],[-38,y,703]]) if label!='14' else None
 views={'entrance':dict(eye=[-141,y+1.7,701],target=[-52,y+2.4,703]),'deck':dict(eye=[-46,y+1.7,688],target=[-58,y+1,646])} if label!='14' else {'entrance':dict(eye=[-309,y+1.7,713],target=[-344,y+1,722]),'deck':dict(eye=[-309,y+1.7,713],target=[-344,y+1,722])}
 venues.append(dict(key=key,name='Cosmopolitan · Level '+label,building='cosmopolitan',bounds=list(site.bounds),portals=[],accessPoints=[[x,y,707] for x in np.arange(-350,-35,25)]+[[x,y,650] for x in [-350,-325,-240,-220,-120,-85,-50]],zones=[dict(origin=[-200,y,615],yaw=0,width=335,depth=120,height=5.2)],lights=b.lights[-20:] if label=='1' else [],views={**views,'stairs':dict(eye=[-170,y+1.7,694.5],target=[-170,y+3,714])},outside=True,levelY=y,preloadDistance=45))
route('Boulevard pool deck',[[-170,17.04,716],[-160,17.04,719],[-130,17.04,719],[-90,17.04,708],[-77,17.04,689],[-65,17.04,689],[-46,17.04,688],[-40,17.04,675]])
route('Chelsea pool deck',[[-318,22.64,712.3],[-314,22.64,713],[-304,22.64,713],[-296,22.64,715]])
route('Chelsea court',[[-318,22.64,695],[-319,22.64,674],[-319,22.64,662],[-327,22.64,652],[-342,22.64,652],[-342,22.64,647]])
for name,points in [
 ('Strip entrance',[[-32,.24,703],[-41,.24,703],[-43,.24,714]]),
 ('Henry entrance',[[-32,.24,639],[-46,.24,639]]),
 ('Chelsea arrival',[[-380,.24,713],[-352,.24,713]]),
 ('Harmon entrance',[[-270,.24,733],[-270,.24,722]])]:route(name,points)
import cosmo_frontage
cosmo_frontage.update_builder(b)
b.save_all()
# Empty collision sets are valid and keep the runtime loader uniform.
for v in venues:
 for layer in ['exterior','interior']:
  k=v['key']+'-'+layer;p=OUT/(k+'-collision.json')
  if not p.exists():p.write_text(json.dumps(dict(vertices=[],indices=[])))
(OUT/'venues.json').write_text(json.dumps(venues,indent=2,default=lambda v:float(v)))
(OUT/'routes.json').write_text(json.dumps(routes,indent=2))
ids=['way/1212809711','way/27897905','way/472669744','way/134795273','way/27897904','way/699020450','way/699020451','way/699020452','way/699020453','way/699020449']
(OUT/'replacement-ids.json').write_text(json.dumps(ids))
(OUT/'geometry-report.json').write_text(json.dumps(dict(physicalElevations=LEVELS,labels=['1','2','3','4','14'],estimatedElevations=True,sourceFootprints=ids,triangles=sum(len(g['faces']) for g in b.groups.values()),batches=len(b.groups),routes=len(routes),note='Physical podium elevations fitted from imagery; labels/topology from official maps. Separate two tower footprints; third mapped tower feature treated as lower podium. Pools use safe shallow walkable water surfaces.'),indent=2))
print('Built',len(b.groups),'batches',sum(len(g['faces']) for g in b.groups.values()),'triangles',len(routes),'routes')

# Keep the mapped lift entrance clear after explicit resort regeneration.
if Path("build/strip-landmarks/cosmoPedestrianLift-exterior.glb").exists():
 import runpy
 runpy.run_path("tools/city-exteriors/trim-cosmo-lift-rail.py")
