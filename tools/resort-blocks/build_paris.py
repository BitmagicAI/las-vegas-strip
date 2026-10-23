"""Paris whole-block exterior, geographic metres; source/confidence in paris.json.
Shared materials and 64m static cells. Furniture is visual, structural routes collide.
Replaces Eiffel geometry while retaining its ride and custom casino/guest modules.
"""
import sys,json,math
from pathlib import Path
sys.path.insert(0,'tools/strip-landmarks')
from common import *
import common
from paris_eiffel import build as build_eiffel
from paris_pool import build as build_pool
from paris_arrival import arrival_void, sector, build as build_arrival
OUT=Path('build/resort-blocks/paris');OUT.mkdir(parents=True,exist_ok=True);common.OUT=OUT
b=Meshes();G=.24;D=6.64;P=10.74;routes=[];venues=[]
site=footprint('way/33974140');tower=footprint('way/27831697')
# Preserved casino has its own ground, walls and ceiling; never add coplanar floors.
legacy=box(79.8,385.5,177.7,478.5)
F=lambda x,z,y=G,yaw=0:Frame(b,x,z,yaw,y)
def source(s,detail=0):b.source=s;b.detail=detail

def slab(p,y,mat='tile',solid=True):
 b.shell(p,y-.30,y,mat,roof=False,solid=solid);b.planar(mat,p,y,solid);b.planar(mat,p,y-.30)
def route(name,points):routes.append(dict(name=name,points=points))
def col(f,x,z,h=5,r=.24):
 f.lathe('paris-stone',x,z,[(0,r*1.4),(.2,r*1.4),(.3,r),(h-.4,r*.82),(h-.3,r*1.45),(h,r*1.45)],12)
 # Capitals with curled ends, all in same stone batch.
 for dx in [-r,r]:f.lathe('paris-stone',x+dx,z,[(h-.28,r*.5),(h-.1,r*.65),(h,r*.3)],8)
def rail(a,c,y=G,stone=False):
 f=F(0,0,y);L=math.dist(a,c)
 f.tube('paris-iron' if not stone else 'paris-stone',(a[0],1.1,a[1]),(c[0],1.1,c[1]),.06 if not stone else .15)
 f.tube('paris-iron',(a[0],.16,a[1]),(c[0],.16,c[1]),.035)
 for t in np.linspace(0,1,max(2,math.ceil(L/.45)+1)):
  x,z=a[0]+(c[0]-a[0])*t,a[1]+(c[1]-a[1])*t
  if stone:f.lathe('paris-stone',x,z,[(.1,.10),(.22,.13),(.38,.07),(.65,.13),(.9,.08),(1.05,.12)],8)
  else:
   f.tube('paris-iron',(x,.15,z),(x,1.08,z),.021)
   f.b.sphere('brass',(x,y+1.11,z),.055,6,4)
 # One invisible collision strip instead of one collider per spindle.
 before={k:(len(g['vertices']),len(g['faces'])) for k,g in b.groups.items()}
 dx,dz=c[0]-a[0],c[1]-a[1];b.box('paris-iron',((a[0]+c[0])/2,y+.53,(a[1]+c[1])/2),(L,1.06,.05),True,-math.atan2(dz,dx))
 for k,g in list(b.groups.items()):
  if k not in before:del b.groups[k]
  else:
   nv,nf=before[k];del g['vertices'][nv:];del g['faces'][nf:]
def tree(x,z,y=G,r=2.3):
 f=F(x,z,y);f.lathe('paris-stone',0,0,[(0,.7),(.15,.8),(.75,.72)],16);f.lathe('bark',0,0,[(.5,.17),(3.7,.11)],8)
 for dx,dz,dy,rr in [(0,0,4,r),(-.8,0,4.5,r*.8),(.9,.4,4.2,r*.8),(0,.7,5,r*.65)]:b.sphere('paris-leaf',(x+dx,y+dy,z+dz),rr,12,7,scale=(1,.85,1))
def table(x,z,y=G,umbrella=None,picnic=False):
 f=F(x,z,y)
 if picnic:
  for dz in [-.24,0,.24]:f.box('walnut',(0,.78,dz),(2.2,.09,.22))
  for dz in [-.76,.76]:
   f.box('walnut',(0,.45,dz),(2.2,.09,.32))
   for xx in [-.78,.78]:f.tube('paris-iron',(xx,0,dz*.5),(xx,.72,0),.045)
 else:
  f.lathe('paris-iron',0,0,[(0,.35),(.05,.35),(.08,.05),(.72,.05)],10);f.lathe('marble',0,0,[(.72,.58),(.80,.58)],16)
  for dx,dz in [(-.85,0),(.85,0),(0,-.85),(0,.85)]:
   f.box('paris-rattan',(dx,.46,dz),(.45,.06,.45));f.box('paris-rattan',(dx,.77,dz+.2),(.45,.56,.06))
   for xx in [-.19,.19]:f.tube('paris-iron',(dx+xx,0,dz+.15),(dx+xx,.93,dz+.15),.025);f.tube('paris-iron',(dx+xx,0,dz-.17),(dx+xx,.46,dz-.17),.025)
  for dx in [-.25,.25]:f.lathe('white',dx,0,[(.802,.15),(.82,.15)],12);f.lathe('glass',dx,.2,[(.8,.04),(1,.055)],8)
 if umbrella:
  f.tube('walnut',(0,0,0),(0,3.12,0),.04)
  for i in range(10):
   a=i*math.tau/10;c=(i+1)*math.tau/10;r=1.9
   f.b.face(umbrella,[f.p(0,3.1,0),f.p(r*math.cos(a),2.62,r*math.sin(a)),f.p(r*math.cos(c),2.62,r*math.sin(c))]);f.tube('paris-iron',(0,3.08,0),(r*math.cos(a),2.60,r*math.sin(a)),.012)
   f.b.face(umbrella,[f.p(r*math.cos(a),2.62,r*math.sin(a)),f.p(r*math.cos(c),2.62,r*math.sin(c)),f.p(r*math.cos(c),2.48,r*math.sin(c)),f.p(r*math.cos(a),2.48,r*math.sin(a))])
def mansard(poly,y,rise=4,inset=2):
 q=poly.buffer(-inset,join_style=2)
 # Four-sided pieces only here; tower has a separate ring using corresponding vertices.
 a=list(poly.exterior.coords)[:-1];c=list(q.exterior.coords)[:-1]
 if len(a)==len(c):
  for i in range(len(a)):
   j=(i+1)%len(a);b.face('paris-slate',[(a[i][0],y,a[i][1]),(a[j][0],y,a[j][1]),(c[j][0],y+rise,c[j][1]),(c[i][0],y+rise,c[i][1])])
 else:b.shell(poly,y,y+rise,'paris-slate',roof=False,solid=False)
 b.planar('roof',q,y+rise)
def archbay(f,x,z,w=3.7,h=6.8,base=.5):
 # Arched dark glazing, not a rectangular black decal above an arch.
 r=w/2;spring=h-r;pts=[f.p(x-r,base,z),f.p(x+r,base,z)]+[f.p(x+r*math.cos(a),spring+r*math.sin(a),z) for a in np.linspace(0,math.pi,18)]
 b.face('darkglass',pts);f.arch(x,z+.10,w,h,'paris-stone',.15,base)
 for xx in [-w*.25,0,w*.25]:f.box('paris-iron',(x+xx,(base+spring)/2,z+.16),(.055,spring-base,.06))
 f.box('paris-iron',(x,spring-.45,z+.16),(w,.07,.06));f.box('paris-stone',(x,h+.15,z+.20),(.45,.6,.45))
def ornate_front(x,z0,z1,h=12,upper=True):
 f=F(x,z0,G,math.pi/2);length=z1-z0;n=max(1,round(length/5.3));pitch=length/n
 for i in range(n):
  xx=-(i+.5)*pitch
  isdoor=abs(z0-xx-354)<3 and abs(x-44.15)<1
  if not isdoor:archbay(f,xx,0,pitch*.65,6.2)
  for dx in [-pitch*.46,pitch*.46]:
   col(f,xx+dx,.28,h=6.8,r=.22)
   if upper:f.box('paris-stone',(xx+dx,9.3,.1),(.34,3.7,.35))
  if upper:
   archbay(f,xx,0,pitch*.57,10.8,7.7)
   f.box('paris-stone',(xx,7.45,.48),(pitch*.78,.22,1));rail((x-.55,z0+(i+.18)*pitch),(x-.55,z0+(i+.82)*pitch),G+7.5)
   # Raised wreath/scrollwork, original geometry rather than photo texture.
   f.path('paris-stone',[(xx+math.cos(a)*.52,11.6+math.sin(a)*.35,.20) for a in np.linspace(0,math.tau,17)],.08)
 for yy,depth in [(6.8,.5),(7.1,.65),(h-.7,.45),(h-.35,.7),(h,.85)]:f.box('paris-stone',(-length/2,yy,depth/2),(length,.18,depth))
 for xx in np.arange(-length+.3,0,.65):f.box('paris-stone',(xx,h-.53,.55),(.25,.24,.35))

b.property='parisBlock-exterior';source('podium-structure')
# Remove duplicated masses explicitly; the retained interior occupies the middle.
north=box(44.3,333,77,374);south=footprint('way/114722037').union(box(47.5,420,86,457.4))
ground=unary_union([site,north,south,box(33.5,417,51.8,458)]).difference(legacy)
slab(ground,G,'paris-paving')
pool_area=box(92,341,183,438).intersection(site).difference(tower).difference(arrival_void().buffer(9))
# Public roof, separated from north/south ornamental pavilions and tall tower.
arrival=arrival_void()
roofcut=unary_union([pool_area,box(30,326,86,480),tower,arrival,sector(46,56)])
b.shell(site,G,10.35,'paris-stone',roof=False,interior=(unary_union([legacy.buffer(.2),north.buffer(.2),south.buffer(.2),arrival]),14))
slab(site.difference(roofcut),10.65,'roof',False)
# Single authoritative X tower. Fitted OSM plan rather than a stretched group.
source('guest-bordeaux');b.shell(tower,10.7,101,'paris-stone',solid=False)
mansard(tower.buffer(.7,join_style=2),101,9,2.6)
for y,h in [(13,.8),(29,.3),(96.8,.35),(100.6,.7)]:b.shell(tower.buffer(.3,join_style=2),y,y+h,'paris-cream',roof=False,solid=False)
for a,c in zip(list(tower.exterior.coords),list(tower.exterior.coords)[1:]):
 L=math.dist(a,c);dx,dz=(c[0]-a[0])/L,(c[1]-a[1])/L;nx,nz=dz,-dx
 if tower.contains(Point((a[0]+c[0])/2+nx,(a[1]+c[1])/2+nz)):nx,nz=-nx,-nz
 yaw=-math.atan2(dz,dx);count=max(1,round(L/3.0));pitch=L/count
 for i in range(count):
  x,z=a[0]+dx*(i+.5)*pitch+nx*.14,a[1]+dz*(i+.5)*pitch+nz*.14;f=F(x,z,0,yaw)
  for yy in np.arange(16,98,3.05):
   f.box('darkglass',(0,yy,0),(min(1.5,pitch*.53),1.95,.12));f.box('paris-cream',(0,yy-1.05,0),(min(1.8,pitch*.65),.16,.28));f.box('paris-cream',(0,yy+1.07,0),(min(1.85,pitch*.68),.18,.24))
  f.box('paris-cream',(-pitch*.44,56,.03),(.25,84,.3))
  # Tall curved dormers crossing the blue roof, with pediment and finial.
  f.box('paris-stone',(0,102.9,.0),(1.85,3.7,1.2));archbay(f,0,.68,1.1,105.1,101.6)
  f.path('paris-cream',[(-1,105,.7),(0,106.1,.7),(1,105,.7)],.15)
  f.lathe('paris-cream',0,.15,[(106,.16),(106.8,.13),(107.2,.03)],8)
# Corner pavilion crowns articulate the ends of the X rather than a flat roof.
for x,z in [(174.8,340),(280,340),(176,447),(280,447)]:
 source('guest-bordeaux');f=F(x,z,0);f.lathe('paris-cream',0,0,[(109,.55),(110,.55),(112,.06)],12)
# Permanent outdoor tower and pool geometry; authored at world scale.
eiffel_report=build_eiffel(globals())
pool,pool_report=build_pool(globals(),pool_area)
# Two front pavilions at actual surveyed position. North = Mon Ami Gabi,
# south = Alexxa's and Beer Park, with the Eiffel's separate owner between them.
north=box(44.3,333,77,374);south=footprint('way/114722037').union(box(47.5,420,86,457.4))
source('podium-north-pavilion');b.shell(north,G,13,'paris-stone',roof=False,solid=True,openings=[dict(p=[44.3,G,354],yaw=math.pi/2,width=4,height=3.8)])
slab(north,13,'roof',False);mansard(north.buffer(.4,join_style=2),13,4,3)
ornate_front(44.15,333,374,13)
# North central raised pediment; visible from lake and footpath.
f=F(43.7,353.5,G,math.pi/2)
f.b.face('paris-stone',[f.p(-8,13,0),f.p(0,18.2,0),f.p(8,13,0)])
f.path('paris-cream',[(-8,13.2,.3),(0,18.4,.3),(8,13.2,.3)],.22)
f.lathe('paris-cream',0,0,[(18,.22),(19.5,.14),(20.2,.03)],12)
# Awnings below the stone arcade, dark green framing and crimson scalloped valance.
source('north-patio',1)
slab(box(32.8,333,44,374),G+.08,'paris-paving')
for z in np.arange(336,373,5.5):
 b.face('paris-red',[(44,4.2,z-2.7),(39.5,3.4,z-2.7),(39.5,3.4,z+2.7),(44,4.2,z+2.7)])
 b.box('paris-red',(39.5,3.22,z),(.05,.36,5.4));F(39.35,z,G,math.pi/2).text('MON AMI GABI' if 350<z<360 else 'BISTRO',(0,3.18,0),.24,'letter')
 for zz in [z-1.1,z+1.1]:table(36.5,zz,G+.08,'paris-red' if zz==z-1.1 else None)
for a,c in [((32.8,333),(32.8,351)),((32.8,357),(32.8,374)),((32.8,333),(44,333)),((32.8,374),(44,374))]:rail(a,c,G+.08)
# French street facade wraps corner: glazed doors and recessed entrance arcade.
source('podium-south-pavilion');portals=[dict(p=[47.5,G,428],yaw=math.pi/2,width=5,height=3.8,name="ALEXXA'S / CASINO"),dict(p=[44.3,G,354],yaw=math.pi/2,width=4,height=3.8,name='MON AMI GABI')]
b.shell(south,G,D-.3,'paris-stone',roof=False,solid=True,openings=portals,interior=(legacy.buffer(.2),11))
# Existing entrance is x80.35/z428.06; this gap joins to it without replacement.
b.shell(south,D,13,'paris-stone',roof=False,solid=False,interior=(unary_union([box(0,419,64,458),box(64,412,68,433)]),14))
ornate_front(53.2,435,454,12,False)
# Restaurant glazing at ground level; doorway bay stays genuinely open.
for z in np.arange(421.7,456,4.8):
 if abs(z-428)<4:continue
 f=F(47.35,z,G,math.pi/2);archbay(f,0,0,3.9,4.8,.15)
 for xx in [-1.95,1.95]:f.box('paris-iron',(xx,2.4,.1),(.1,4.8,.15))
 b.face('paris-yellow',[(47.3,3.5,z-2.35),(39,3.1,z-2.35),(39,3.1,z+2.35),(47.3,3.5,z+2.35)])
 b.box('paris-yellow',(39,2.9,z),(.08,.4,4.7))
 F(38.9,z,G,math.pi/2).text("ALEXXA'S",(0,2.87,0),.28,'paris-iron')
# Street patio and upper deck: furniture, shade, fence, bar, screens, festoon lights.
staircut=box(65,438.45,71,455.2)
terrace=unary_union([south,box(36,417,53,457.5),box(69,417,79.7,438.5)]).difference(staircut)
slab(terrace,D,'paris-paving')
for a,c in [((36,417),(36,457.5)),((36,417),(69,417)),((36,457.5),(86,457.5))]:rail(a,c,D)
F(68,455,G,math.pi).stairs(0,0,4,D-G,16.5)
# Upper stair landing has a clear 3m path, then a second stair to the pool level.
F(66,432,D,math.pi).stairs(0,0,3.4,P-D,18)
slab(box(64,411,92,414),P,'paris-paving')
for a,c in [((64,411),(92,411)),((64,411),(64,414)),((68,414),(92,414))]:rail(a,c,P)
source('upper-patio-detail',1)
for x in [41,48,57,64]:
 for z in np.arange(422,454,5):
  if x==64 and z<439:continue
  table(x,z,D,'paris-red' if x in [41,57] else None,True)
for z in np.arange(421,455,7):
 tree(36.8,z,D,1.3)
 for x in [37,64]:b.tube('paris-iron',(x,D,z),(x,D+4,z),.05)
 b.path('paris-iron',[(37+i*27/12,D+4-.6*math.sin(i*math.pi/12),z) for i in range(13)],.016)
 for i in range(1,12):b.sphere('warm',(37+i*27/12,D+3.96-.6*math.sin(i*math.pi/12),z),.07,6,4)
f=F(62,425,D);f.box('brick',(0,.65,0),(3,1.3,9));f.box('walnut',(0,1.35,0),(3.3,.13,9.3))
for z in [422,427,432]:F(63.8,z,D,math.pi/2).box('screen',(0,2.4,0),(2.6,1.5,.13))
F(35.8,441,D,math.pi/2).text('BEER PARK',(0,1.6,0),.72,'paris-red')
for x,z in [(36,419),(48,419),(64,454)]:tree(x,z,G,1.4)
F(47.2,428,G,math.pi/2).text('ALEXXA’S · CASINO · ROOFTOP',(0,4.5,0),.35,'paris-cream')
for x,z,y,text in [(72,455,G,'BEER PARK / ROOFTOP'),(63.5,434,D,'POOL TERRACE')]:
 f=F(x,z,y,math.pi);f.box('paris-iron',(0,1.8,0),(2.5,.65,.09));f.box('paris-iron',(0,.85,0),(.07,1.7,.07));f.text(text,(0,1.8,.055),.16,'paris-cream')
# Arrival architecture owns the facade, canopy, Opera pavilion, Arc and balloon.
portals.append(build_arrival(globals()))
# A connected terrace route, with continuous slabs and structural stair ramps.
route('Alexxa street entrance',[[31,G,428],[44,G,428],[52,G,428],[64,G,428],[64,G,423],[78,G,423],[78,G,428],[87,G,428]])
route('Beer Park ascent',[[60,G,455],[68,G,455],[68,D,438.5],[68,D,437.8],[67,D,437.8],[60,D,438.5],[52,D,438.5],[40,D,438.5]])
route('Pool ascent',[[67,D,437.8],[66,D,432],[66,P,414],[66,P,412.5],[95,P,412.5],[110,P,412.5],[135,P,418]])
route('Pool circuit',[[135,P,418],[158,P,418],[158,P,349],[112,P,349],[112,P,414],[120,P,414]])
# New observation geometry must retain the full cabin-to-gallery circuit.
from paris_eiffel import CENTER
ef=Frame(b,*CENTER,math.pi/4,0)
route('Eiffel observation circuit',[ef.p(x,140,z) for x,z in [(-.4,0),(-4.5,0),(-4.5,-4.5),(4.5,-4.5),(4.5,4.5),(-4.5,4.5),(-4.5,0),(-.4,0)]])
route('Eiffel ground cabin',[ef.p(x,.24,0) for x in [-4,-2.5,-.4]])
route('Mon Ami Gabi entrance',[[30,G+.08,354],[40,G+.08,354],[47,G,354],[63,G,354]])
route('Main arrival into casino',[[126.8,G-.10,458],[126.8,G-.10,448],[126.8,G,441],[126.8,G,436],[126.8,G,426],[126.8,G,421]])
route('Arc main vault',[[107,G+.05,490.7],[127.3,G+.05,490.7],[147,G+.05,490.7]])
# Interior anchors and independent, nearby public furniture sets.
views={'entrance':dict(eye=[30,1.94,428],target=[59,3.2,428]),'aerial':dict(eye=[-135,125,468],target=[159,45,391]),'deck':dict(eye=[111,P+1.7,425],target=[137,P+2,388]),'stairs':dict(eye=[68,G+1.7,456],target=[68,D+1.5,438.5]),'pool-stairs':dict(eye=[66,D+1.7,433],target=[66,P+1.4,413]),'pool-bridge':dict(eye=[66,P+1.7,412.5],target=[110,P+1.7,412.5]),'frontage':dict(eye=[20,2,343],target=[46,6,367]),'arrival':dict(eye=[127,2,457],target=[127,8,435]),'arrival-inside':dict(eye=[126.8,1.94,423],target=[126.8,2.5,454]),'arrival-aerial':dict(eye=[4,130,607],target=[113,13,462]),'facades':dict(eye=[130,14,465],target=[128,14,435]),'facades-aerial':dict(eye=[87,49,497],target=[137,12,448])}
venues.append(dict(key='parisBlock',name='Paris · mapped resort exterior',building='paris',structural=True,bounds=list(site.bounds),portals=portals,zones=[],accessPoints=[[47.5,G,428],[44.3,G,354],[68,G,455],[126.8,G,436]],lights=[],views=views))
b.property='parisBlock-interior';source('anchor');b.box('roof',(75,-3,450),(.01,.01,.01))
# Ground restaurant furnishings stay out of the two entry aisles.
for name,bounds,y in [('parisDining',[44.4,333,79.7,458],G),('parisPool',[92,341,183,438],P)]:
 b.property=name+'-exterior';source('anchor');b.box('roof',(75,-3,450),(.01,.01,.01));b.property=name+'-interior';source(name,1)
 if name=='parisDining':
  for x in [52,59,67]:
   for z in [338,344,364,370,421,435,448]:table(x,z,y)
  for z in [337,369,451]:F(74,z).reception(0,0,5,'PARIS')
 else:
  source('anchor');b.box('roof',(75,-3,450),(.01,.01,.01))
 venues.append(dict(key=name,name='Paris · '+('restaurant interiors' if y==G else 'Pool à Paris'),building='paris',bounds=bounds,portals=[],outside=True,levelY=y,preloadDistance=30,zones=[dict(origin=[(bounds[0]+bounds[2])/2,y,bounds[1]],yaw=0,width=bounds[2]-bounds[0],depth=bounds[3]-bounds[1],height=4)],accessPoints=[[x,y,z] for x in range(int(bounds[0])+5,int(bounds[2]),20) for z in range(int(bounds[1])+5,int(bounds[3]),25)],lights=[],views=views))
views.update({'tower-pool':dict(eye=[-112,115,530],target=[110,75,400]),'pool-aerial':dict(eye=[82,59,439],target=[137,P,386]),'tower-base':dict(eye=[12,43,447],target=[74.5,31,400.5]),'lift-cabin':dict(eye=[74.20096,1.95,400.79904],target=[69,1.95,406]),'observation':dict(eye=[71.1,141.7,403.9],target=[15,137,414])})
(OUT/'tower-pool-measurements.json').write_text(json.dumps(dict(eiffel=eiffel_report,pool=pool_report),indent=2))
# Split all triangles spatially at author time. No runtime per-prop traversal.
old=b.groups;b.groups={}
for g in old.values():
 for ids in g['faces']:
  pts=[g['vertices'][i] for i in ids];x=sum(p[0] for p in pts)/3;z=sum(p[2] for p in pts)/3
  cell='tower' if g['source'].startswith('guest-') else f'{math.floor(x/64)}_{math.floor(z/64)}'
  k=(g['property'],g['source']+'@'+cell,g['material'],g['detail']);out=b.groups.setdefault(k,dict(property=g['property'],source=k[1],material=g['material'],detail=g['detail'],vertices=[],faces=[]));n=len(out['vertices']);out['vertices'].extend(pts);out['faces'].append([n,n+1,n+2])
b.save_all()
for v in venues:
 for layer in ['exterior','interior']:
  p=OUT/(v['key']+'-'+layer+'-collision.json')
  if not p.exists():p.write_text(json.dumps(dict(vertices=[],indices=[])))
(OUT/'venues.json').write_text(json.dumps(venues,indent=2));(OUT/'routes.json').write_text(json.dumps(routes,indent=2))
ids=['way/33974140','way/27831697','way/114697072','way/114697073','way/114697074','way/114722037','way/364846544','way/472669747','way/1424222076','way/1424222077','way/1424222078','way/1424222079','way/1436542141']
(OUT/'replacement-ids.json').write_text(json.dumps(ids))
(OUT/'geometry-report.json').write_text(json.dumps(dict(triangles=sum(len(g['faces']) for g in b.groups.values()),batches=len(b.groups),towerBounds=list(tower.bounds),levels={'ground':G,'restaurants':D,'pool':P,'towerCrown':112},retained=['Eiffel observation lift interaction','custom casino / guest rooms','Versailles tower, Horseshoe and neighboring buildings'],estimated=['Facade bay spacing','Ornament','Public level elevations','Furniture placement'],cellSizeM=64),indent=2))
print('Paris:',len(b.groups),'material/cell batches',sum(len(g['faces']) for g in b.groups.values()),'triangles')

# Retain ownership boundary with the separately authored mapped rooftop pavilion.
import runpy
runpy.run_path('tools/resort-blocks/trim-paris-rooftop-bar.py')
