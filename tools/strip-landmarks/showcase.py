"""Showcase frontage: mapped shells, installer photography and owner site plan.
Advertising is original typographic artwork; dimensions above mapped eaves are
photo-estimated. Retains existing city collision and hotel interiors.
"""
from common import *
from forum_shops import facade_frame
KEY='showcase'

def split_edges(ps):
 # Divide the existing western facade exactly at the atrium ownership boundaries.
 for a,b in zip(ps,ps[1:]):
  ts=[0.,1.]
  if abs(b[1]-a[1])>.001:
   ts += [(z-a[1])/(b[1]-a[1]) for z in (1375,1405) if 0<(z-a[1])/(b[1]-a[1])<1]
  ts.sort()
  for u,v in zip(ts,ts[1:]):
   yield tuple(a[k]+(b[k]-a[k])*u for k in range(2)),tuple(a[k]+(b[k]-a[k])*v for k in range(2))


def exterior(B):
 B.property=KEY+'-exterior';B.detail=0
 for ident,height in [('way/27897909',18),('way/115649937',18),('way/92281772',38)]:
  p=footprint(ident);B.source='podium/'+ident;garage=ident=='way/92281772'
  B.planar('forum-flat-roof',p,height+.07,True)
  # The detailed shell owns structural collision as well as visuals. The former
  # city box has a different height on the middle wing and must not remain inside it.
  collision=Meshes();collision.property=B.property
  collision.shell(p,.24,height,'structure',roof=False)
  dst=B.solids[B.property];src=collision.solids[B.property];offset=len(dst['vertices'])//3
  dst['vertices'].extend(src['vertices']);dst['indices'].extend(i+offset for i in src['indices'])
  for poly in parts(p):
   ps=list(poly.exterior.coords)
   for a,b in split_edges(ps):
    if math.dist(a,b)<.5:continue
    F,L,nx,nz=facade_frame(B,a,b,p,.21)
    if not garage and nx<-.4 and 1375<(a[1]+b[1])/2<1405:continue
    F.box('ph-white',(L/2,height/2,0),(L,height,.06))
    if garage:
     for y in np.arange(2,height-1,3.3):
      F.box('ph-black',(L/2,y+.8,-.08),(L,1.6,.04))
      for x in np.arange(.4,L,6.4):F.box('ph-white',(x,y+.8,-.15),(.38,1.85,.12))
    elif nx<-.4:
     # Real continuous retail glazing, separate floor edges and framed doors.
     for y in [.45,4.75,9.05,13.35]:
      F.box('ph-glass',(L/2,y+1.82,-.08),(L-.15,3.64,.06))
     for x in np.arange(.25,L,2.25):F.box('ph-metal',(x,8.6,-.16),(.075,17.2,.14))
     for y in [4.5,8.8,13.1,17.5]:F.box('ph-silver',(L/2,y,-.22),(L,.3,.35))
    else:
     for y in np.arange(1,height,1.35):F.box('ph-joint',(L/2,y,-.05),(L,.02,.04))
     for x in np.arange(1,L,3):F.box('ph-joint',(x,height/2,-.055),(.018,height,.04))
   B.detail=1
   for x in np.arange(p.bounds[0]+7,p.bounds[2]-4,18):
    for z in np.arange(p.bounds[1]+7,p.bounds[3]-4,21):
     if not p.contains(box(x-2,z-1.5,x+2,z+1.5)):continue
     B.box('ph-metal',(x,height+.65,z),(4,1.1,2.8));B.box('ph-black',(x,height+1.24,z),(3.5,.06,2.4))
   B.detail=0
 # Tenant fronts in north-to-south order from the official site map / Earth.
 for z,w,name,mat in [(1361,12,'OUTBACK','ph-red'),(1416,19,"m&m's",'ph-red'),(1430,23,'adidas','ph-black'),(1463,25,'SKECHERS','ph-led-blue'),(1492,25,'SHOWCASE','ph-black')]:
  B.source='podium/retail';F=Frame(B,39.0,z,math.pi/2,y=.24)
  F.box(mat,(0,11,-.3),(w,3.0,.3));F.text(name,(0,11.05,-.48),min(2.2,w/(len(name)*.75)),'ph-letter')
  F.box('ph-metal',(0,4.5,-1.0),(w,.2,2.0))
  for u in [-w*.32,w*.32]:
   F.box('ph-black',(u,2,-.4),(2.5,4,.1))
   for dx in [-1.28,0,1.28]:F.box('ph-silver',(u+dx,2,-.50),(.075,4,.10))
   F.box('ph-silver',(u,4,-.52),(2.62,.09,.13))
   for dx in [-.18,.18]:F.tube('ph-silver',(u+dx,1.45,-.58),(u+dx,2.25,-.58),.027,8)
 # Tall continuous glazed arch: closed gable, a deep curved fascia and roof ribs.
 B.source='podium/atrium'
 for z0,z1 in zip(np.linspace(1375,1405,31)[:-1],np.linspace(1375,1405,31)[1:]):
  y0=18.25+4.5*math.sin((z0-1375)/30*math.pi);y1=18.25+4.5*math.sin((z1-1375)/30*math.pi)
  B.face('showcase-roof',[(39,y0,z0),(78,y0,z0),(78,y1,z1),(39,y1,z1)])
  B.face('sc-atrium-glass',[(38.7,.25,z0),(38.7,.25,z1),(38.7,y1-.8,z1),(38.7,y0-.8,z0)])
  B.face('sc-rim-paint',[(38.5,y0-.8,z0),(38.5,y1-.8,z1),(38.5,y1+.18,z1),(38.5,y0+.18,z0)])
  B.tube('ph-metal',(39,y0+.025,z0),(78,y0+.025,z0),.035,6)
 for z in np.arange(1375,1405.1,1.5):
  y=18.25+4.5*math.sin((z-1375)/30*math.pi)-.85
  B.box('ph-silver',(38.58,(y+.25)/2,z),(.12,y-.25,.045))
 for y in np.arange(3.1,18.5,3.1):B.box('sc-rim-paint',(38.55,y,1390),(.13,.06,30))
 F=Frame(B,38.3,1390,math.pi/2,y=0)
 F.text('SHOWCASE',(0,16.6,-.1),2.05,'ph-letter')
 for u in [-9,0,9]:
  F.box('sc-rim-paint',(u,2.05,-.25),(3.3,4.1,.18))
  for dx in [-1.6,0,1.6]:F.box('ph-silver',(u+dx,2.05,-.38),(.075,4.1,.09))
 # Tilted yellow sculptural package sign beside the atrium, from owner's photograph.
 F=Frame(B,37.2,1410,math.pi/2,y=0)
 def package(x,y,depth):return F.p(x*.985+y*.174,y*.985-x*.174+7.2,depth)
 # Bowed packet body, side gussets and sealed crimp edges; not a flat billboard.
 def point(u,y,back=False):
  width=3.7-.5*y/12.8
  depth=-.8-(.5*math.sin(math.pi*y/12.8)*(1-u*u)) if not back else -.25
  return package(u*width,y,depth)
 for y0,y1 in zip(np.linspace(0,12.8,17)[:-1],np.linspace(0,12.8,17)[1:]):
  for u0,u1 in zip(np.linspace(-1,1,9)[:-1],np.linspace(-1,1,9)[1:]):
   B.face('sc-yellow-paint',[point(u0,y0),point(u1,y0),point(u1,y1),point(u0,y1)])
   B.face('sc-gold-paint',[point(u0,y0,True),point(u0,y1,True),point(u1,y1,True),point(u1,y0,True)])
  for u in [-1,1]:B.face('sc-gold-paint',[point(u,y0),point(u,y0,True),point(u,y1,True),point(u,y1)])
 for y in [0,12.8]:
  B.face('sc-gold-paint',[point(-1,y),point(1,y),point(1,y,True),point(-1,y,True)])
  for x in np.linspace(-3.0,3.0,29):B.tube('sc-gold-paint',package(x,y+.05,-.88),package(x,y+(.28 if y==0 else -.28),-.88),.025,5)
 F.text("m&m's",(1.25,15.9,-1.45),1.75,'ph-letter')
 F.text('WORLD',(1.1,14.2,-1.45),.9,'ph-letter')
 # Raised confection medallions are original simple sign graphics; mascot sculptures remain deferred.
 for x,y,mat in [(-1,9.6,'ph-red'),(1.0,10.0,'sc-blue-paint'),(2.4,9.2,'sc-gold-paint')]:
  pts=[F.p(x+.65*math.cos(a),y+.46*math.sin(a),-1.45) for a in np.linspace(0,math.tau,25)]
  for i in range(24):B.face(mat,[F.p(x,y,-1.5),pts[i],pts[i+1]])
  F.text('m',(x,y,-1.56),.45,'ph-letter')
 # Coca-Cola's 100-foot glazed entrance tower; segmented glass and clear fins.
 B.source='podium/coca-cola';cx,cz=39.5,1370
 profile=[(.25,3.55),(2,3.9),(4,3.65),(7,3.0),(10,3.1),(14,3.65),(18,3.85),(21,3.1),(24,2.2),(27,1.65),(29.5,1.7),(30.48,1.82)]
 B.lathe('coke-glass',(cx,cz),profile,48)
 for y in np.arange(1,30.4,1.1):
  r=float(np.interp(y,[p[0] for p in profile],[p[1] for p in profile]))+.045
  B.path('ph-silver',[(cx+r*math.cos(a),y,cz+r*math.sin(a)) for a in np.linspace(0,math.tau,49)],.026,6)
 for a in np.linspace(0,math.tau,24,endpoint=False):
  B.path('ph-silver',[(cx+(r+.045)*math.cos(a),y,cz+(r+.045)*math.sin(a)) for y,r in profile],.035,6)
 B.lathe('ph-red',(cx,cz),[(13,3.68),(18,3.91)],48)
 F=Frame(B,cx-3.98,cz,math.pi/2,y=0);F.text('Coca-Cola',(0,15.2,-.08),1.05,'ph-letter')
 F=Frame(B,38.6,1389,math.pi/2,y=.24)
 F.box('ph-led-blue',(0,3.8,-.6),(19,1.6,.4));F.text('Marshalls',(0,3.85,-.85),1.0,'ph-letter')
 # Hard Rock's blue guitar facade and upper picture window; separate Ross front.
 from showcase_fronts import north_front
 north_front(B)
 B.source='podium/site';B.planar('ph-paving',footprint('way/27897909').buffer(4),.05)
 from showcase_iv import build as build_iv
 plan=build_iv(B)
 planpath=Path('build/city-exteriors/showcase-iv-plan.json')
 planpath.parent.mkdir(parents=True,exist_ok=True);planpath.write_text(json.dumps(plan,indent=2))
 return dict(key=KEY,name='Showcase Mall street frontage',center=[70,0,1380],bounds=[32,1205,210,1520],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
