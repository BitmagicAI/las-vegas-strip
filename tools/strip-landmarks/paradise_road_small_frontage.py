"""Paradise small commercial frontage. February 2026 street-reference pass.
Plans from mapped footprints; roof/equipment dimensions are estimates.
"""
from common import *
from forum_shops import facade_frame
KEY='paradiseSmallFrontage'
IDS=['way/'+str(i) for i in [986507542,986507541,986507532,969288406,969288402,969288399,969288398,969288397]]
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/paradise-road-small-frontage';B.detail=0
 ps=[footprint(i)for i in IDS];whole=unary_union(ps);roads=json.loads(Path('build/geographic-strip/road-network.json').read_text())['roads'];street=unary_union([LineString([(p[0],p[2])for p in r['points']])for r in roads if r['name']=='Paradise Road']);roadmask=street.buffer(10.3);samples=[];routes=[];W=Frame(B,0,0,y=0)
 for idx,p in enumerate(ps):
  mat=['pr-white-stucco','pr-white-stucco','pr-dark-stone','pr-pale-stone','pr-red-paint','pr-tan-stucco','pr-cream-stucco','pr-cream-stucco'][idx];height=3.1 if idx!=3 else 3.7
  B.shell(p,.18,height,mat,roof=False)
  roof=p.buffer(.32,join_style=2);slope=.16 if idx not in [2,3,6,7] else .045;roofmat='bt-roof-paint' if slope>.1 else 'pr-membrane-paint';level=0;outer=roof
  while not outer.is_empty and level<64:
   inner=roof.buffer(-(level+.35),join_style=2)
   for poly in parts(outer.difference(inner)):
    for t in triangles(poly):B.upface(roofmat,[(x,height+.08+roof.boundary.distance(Point(x,z))*slope,z)for x,z in list(t.exterior.coords)[:-1]],True)
   outer=inner;level+=.35
  edges=[facade_frame(B,a,b,p,0)for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:])];front=[e for e in edges if e[2]<-.65];F,L,_,_=max(front,key=lambda e:e[1]);du=L*.79
  for G,ll,nx,nz in edges:
   G.box('pr-white-trim-paint' if idx in [2,3] else 'pr-brown-trim-paint',(ll/2,height-.03,-.15),(ll,.17,.48))
   G.box('pr-plinth-paint',(ll/2,.28,-.035),(ll,.18,.1))
   if idx==3:G.box('pr-pale-stone',(ll/2,height+.26,0),(ll,.52,.24),True)
   if G is F:
    # An opaque wall behind the doors preserves the exterior-only scope.
    if idx==1:G.box('pr-red-brick',(ll/2,.64,-.06),(ll,.90,.14))
    if idx in [0,1,4,5,6,7]:
     for u,ww in [(ll*.24,min(2.4,ll*.34)),(ll*.53,min(1.8,ll*.23))]:
      G.box('pr-window-frame-paint',(u,1.75,-.08),(ww+.16,1.42,.16));G.box('pr-glass',(u,1.75,-.18),(ww,1.26,.045))
      G.box('pr-window-frame-paint',(u,1.75,-.22),(.045,1.26,.04));G.box('pr-white-trim-paint',(u,1.0,-.16),(ww+.22,.10,.30))
      if idx>=4:
       for bu in np.arange(u-ww/2+.08,u+ww/2,.20):G.box('pr-bar-paint',(float(bu),1.75,-.29),(.025,1.3,.03))
       for by in [1.2,2.3]:G.box('pr-bar-paint',(u,by,-.29),(ww,.025,.03))
    if idx==2:
     for u in [ll*.21,ll*.48]:G.box('pr-black-paint',(u,1.5,-.09),(min(2.7,ll*.25),2.5,.12))
    G.box('pr-window-frame-paint',(du,1.34,-.08),(1.13,2.32,.16));G.box('pr-door-paint',(du,1.34,-.18),(.97,2.16,.04));G.box('pr-glass',(du,1.67,-.21),(.72,1.35,.025));G.box('pr-handle-paint',(du-.34,1.2,-.25),(.045,.32,.05))
    # Projecting door canopy, thin folded drip edge, and wall lights.
    G.box('pr-awning-paint',(du,2.78,-.84),(1.9,.08,1.68));G.box('pr-brown-trim-paint',(du,2.69,-1.65),(1.9,.16,.05))
    for u in [du-.83,du+.83]:G.tube('pr-bar-paint',(u,2.30,-.1),(u,2.75,-1.48),.018,6)
    G.box('pr-light-paint',(du-1,2.40,-.17),(.18,.27,.25))
    if idx in [1,2,5,7]:
     text={1:'DESIGNER RESALE',2:'CHAPEL EXPRESS',5:'TAX',7:'MASSAGE'}[idx];sw=min(ll*.68,6.2);G.box('pr-sign-paint',(ll*.37,2.65,-.13),(sw,.55,.14));G.text(text,(ll*.37,2.46,-.22),min(.32,sw/(len(text)*.7)),'pr-sign-letter')
   elif ll>4:
    G.box('pr-window-frame-paint',(ll*.66,1.6,-.07),(1.15,1.05,.14));G.box('pr-glass',(ll*.66,1.6,-.16),(1.0,.90,.04))
    # Downpipe and service grille, kept off the principal arrival route.
    G.box('pr-drain-paint',(ll-.25,1.6,-.12),(.075,2.85,.09));G.box('pr-service-paint',(ll*.28,1.1,-.10),(.85,.7,.15))
    for y in np.arange(.82,1.4,.075):G.box('pr-vent-paint',(ll*.28,float(y),-.20),(.72,.025,.025))
  # Forecourt reaches the existing street edge without spilling into the road.
  apron=F.poly([(-.4,0),(L+.4,0),(L+.4,-36),(-.4,-36)]).difference(roadmask).difference(whole)
  apron=unary_union([a for a in parts(apron)if a.distance(p)<.51]);B.planar('pr-asphalt',apron,.18,True)
  path=F.poly([(du-.8,0),(du+.8,0),(du+.8,-36),(du-.8,-36)]).intersection(apron);B.planar('pr-concrete',path,.20,True)
  B.planar('pr-concrete',p.buffer(.35,join_style=2).difference(p),.19,True)
  start=max(2.8,street.distance(Point(F.p(du,0,0)[::2]))-10.7);routes.append([F.p(du,.20,-start),F.p(du,.20,-2.2),F.p(du,.20,-.6)])
  if idx in [0,1,4,5,7]:
   for u in np.arange(.8,max(.9,L-2.8),2.6):
    stripe=F.poly([(float(u),-3),(float(u)+.08,-3),(float(u)+.08,-7),(float(u),-7)]).intersection(apron)
    B.planar('pr-line-paint',stripe,.195)
  # Separate rooftop mechanical units and exhausts, not duplicated full roof planes.
  x,z=p.representative_point().coords[0];yy=height+.08+roof.boundary.distance(Point(x,z))*slope
  for dx in [-1.6,1.6]:
   if not p.buffer(-1).contains(Point(x+dx,z)):continue
   W.box('pr-service-paint',(x+dx,yy+.48,z),(1.15,.85,1.25));W.box('pr-vent-paint',(x+dx,yy+.92,z),(1.03,.04,1.13))
   for zz in np.arange(z-.5,z+.6,.12):W.box('pr-service-paint',(x+dx,yy+.95,float(zz)),(1.06,.025,.035))
  B.lathe('pr-drain-paint',(x,z+2),[(yy-.2,.12),(yy+.7,.12),(yy+.74,.20)],10)
  for x in np.arange(p.bounds[0]+.5,p.bounds[2],1):
   for z in np.arange(p.bounds[1]+.5,p.bounds[3],1):
    if p.buffer(-.35).contains(Point(x,z)):samples.append([float(x),height+.08+roof.boundary.distance(Point(x,z))*slope+.4,float(z)])
 Path('build/city-exteriors/paradise-road-small-frontage-samples.json').write_text(json.dumps(samples));Path('build/city-exteriors/paradise-road-small-frontage-stairs.json').write_text(json.dumps(routes))
 return dict(key=KEY,name='Paradise Road small commercial frontage',center=[1738,0,-3255],bounds=list(whole.buffer(28).bounds),structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
