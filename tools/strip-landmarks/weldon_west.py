"""Weldon Place west homes, January2026 street-reference pass.
Mapped footprints; roof pitch and door placement remain estimates.
"""
from common import *
from forum_shops import facade_frame
from courtyard_525 import palm
KEY='weldonWest';IDS=['way/1236725786', 'way/1236725790', 'way/1236725785', 'way/1236725784', 'way/1236725783']
def window(F,u,y=1.65,w=1.8):
 F.box('rpw-frame-paint',(u,y,-.06),(w+.14,1.3,.12));F.box('rpw-glass',(u,y,-.14),(w,1.16,.04));F.box('rpw-frame-paint',(u,y,-.18),(.04,1.16,.03));F.box('rpw-sill-paint',(u,y-.7,-.14),(w+.25,.09,.27))
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/weldon-west';B.detail=0;ps=[footprint(i) for i in IDS];road=next(r for r in json.loads(Path('build/geographic-strip/road-network.json').read_text())['roads'] if r['name']=='Weldon Place');street=LineString([(v[0],v[2]) for v in road['points']]);roadmask=street.buffer(5.8);allhomes=unary_union(ps);samples=[];routes=[];trees=[];W=Frame(B,0,0,y=0)
 for idx,p in enumerate(ps):
  wall='white'
  B.shell(p,.18,2.95,'rpw-'+wall+'-stucco',roof=False)
  # Constant-pitch hips follow the actual L-shaped boundaries rather than a flat inset cap.
  roof=p.buffer(.32,join_style=2);level=0;outer=roof;slope=.13 if idx in [0,1,3] else .25;roofmat='rpw-membrane-paint' if idx==3 else ('rpw-gray-roof-paint' if idx in [0,1] else 'bt-roof-paint')
  while not outer.is_empty and level<64:
   inner=roof.buffer(-(level+.4),join_style=2)
   for poly in parts(outer.difference(inner)):
    for t in triangles(poly):B.upface(roofmat,[(x,3.0+roof.boundary.distance(Point(x,z))*slope,z)for x,z in list(t.exterior.coords)[:-1]],True)
   outer=inner;level+=.4
  edges=[facade_frame(B,a,b,p,0) for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:])]
  front=[e for e in edges if e[2]>.6];F,L,_,_=max(front,key=lambda e:e[1]);du=L*.53
  for G,ll,nx,nz in edges:
   G.box('hs-red-fascia-paint' if idx in [2,3] else 'rpw-fascia-paint',(ll/2,2.97,-.12),(ll,.17,.46));G.box('rpw-plinth-paint',(ll/2,.31,-.025),(ll,.26,.08))
   if G is F:
    for u in [ll*.22,ll*.79]:
     if False:
      G.box('rpw-frame-paint',(u,2.15,-.07),(min(3.8,ll*.35),.65,.12));G.box('rpw-glass',(u,2.15,-.15),(min(3.6,ll*.33),.49,.04))
     else:
      ww=min(2.1,ll*.24);window(G,u,w=ww)
      for bu in np.arange(u-ww/2+.12,u+ww/2,.22):G.box('rpw-hardware-paint',(float(bu),1.65,-.23),(.022,1.16,.025))
      for by in [1.3,1.95]:G.box('rpw-hardware-paint',(u,by,-.23),(ww,.025,.025))
    G.box('rpw-door-trim-paint',(du,1.25,-.07),(1.04,2.14,.15));G.box('rpw-door-paint',(du,1.25,-.16),(.88,1.99,.04));G.box('rpw-hardware-paint',(du+.31,1.2,-.2),(.04,.14,.04))
    # Thin metal entrance awning and two slender porch columns.
    G.box('rpw-awning-paint',(du,2.61,-.8),(2.1,.10,1.6));
    for u in [du-.95,du+.95]:G.box('rpw-post-paint',(u,1.4,-1.5),(.07,2.44,.07),True)
    G.box('rpw-concrete',(du,.10,-.9),(2.2,.16,1.8),True)
    if idx in [2,6,9]:
     for u in [ll*.22,ll*.79]:
      B.face('rpw-awning-paint',[G.p(u-1.12,2.42,-.05),G.p(u+1.12,2.42,-.05),G.p(u+1.12,2.15,-.7),G.p(u-1.12,2.15,-.7)])
   elif nx>.6 and ll>3.3:
    # A second short east edge at the recessed L serves the garage.
    G.box('rpw-garage-trim-paint',(ll/2,1.35,-.06),(min(4.2,ll-.3),2.35,.12));G.box('rpw-garage-paint',(ll/2,1.35,-.14),(min(4,ll-.5),2.2,.04))
    for y in np.arange(.4,2.4,.35):G.box('rpw-garage-seam-paint',(ll/2,float(y),-.17),(min(4,ll-.5),.018,.025))
   elif ll>4:
    for u in np.arange(2.1,ll-1.2,5.6):window(G,float(u),w=1.2)
  # Continuous entry path in a gravel yard; front fences leave the approach open.
  yard=F.poly([(-.5,0),(L+.5,0),(L+.5,-28),(-.5,-28)]).difference(roadmask).difference(allhomes)
  yard=unary_union([v for v in parts(yard) if v.distance(p)<.51])
  path=F.poly([(du-.7,0),(du+.7,0),(du+.7,-28),(du-.7,-28)]).intersection(yard)
  for G,ll,nx,nz in front:
   if G is not F and ll>3.3:
    drive=G.poly([(.1,0),(ll-.1,0),(ll-.1,-28),(.1,-28)]).difference(roadmask).difference(allhomes)
    drive=unary_union([v for v in parts(drive) if v.distance(p)<.51])
    path=path.union(drive);yard=yard.union(drive)
  B.planar('rpw-concrete' if idx<2 else 'ww-yard-paint',yard.difference(path),.19,True);B.planar('rpw-concrete',path,.18,True)
  if idx>=2:
   depth=max(3,street.distance(Point(F.p(L/2,0,0)[::2]))-6.1)
   for a,b in [(0,du-.9),(du+.9,L)]:
    if b-a<.2:continue
    for u in np.arange(a,b,.24):F.box('ww-fence-paint',(float(u),.95,-depth),(.025,1.5,.025))
    for y in [.3,1.65]:F.box('ww-fence-paint',((a+b)/2,y,-depth),(b-a,.04,.04))
    if idx==2:F.box('ww-green-screen-paint',((a+b)/2,.94,-depth+.025),(b-a,1.35,.015))
  # Short perimeter apron makes visible side doors accessible without terrain holes.
  B.planar('rpw-concrete',p.buffer(.4,join_style=2).difference(p),.18,True)
  startDepth=max(3,street.distance(Point(F.p(du,0,0)[::2]))-6.1)
  routes.append([F.p(du,.18,-startDepth),F.p(du,.18,-2.0),F.p(du,.18,-.55)])
  if idx in [0,2]:
   x,y,z=F.p(L*.12,0,-5.5);trees.append([x,z,6.3,idx*.7])
  if idx==4:palm(B,F,L*.15,-7.5,7.2)
  x,z=p.representative_point().coords[0];yy=3.0+roof.boundary.distance(Point(x,z))*slope
  W.box('rpw-service-paint',(x,yy+.36,z),(1.1,.72,1.1));W.box('rpw-vent-paint',(x,yy+.73,z),(.97,.03,.97))
  B.lathe('rpw-flue-paint',(x+2,z),[(yy-.2,.12),(yy+.65,.12),(yy+.7,.19)],10)
  for x in np.arange(p.bounds[0]+.5,p.bounds[2],1.2):
   for z in np.arange(p.bounds[1]+.5,p.bounds[3],1.2):
    if p.buffer(-.3).contains(Point(x,z)):samples.append([float(x),3.0+roof.boundary.distance(Point(x,z))*slope+.4,float(z)])
 B.groups={k:g for k,g in B.groups.items() if g['material']!='c525-collision'}
 Path('build/city-exteriors/weldon-west-samples.json').write_text(json.dumps(samples));Path('build/city-exteriors/weldon-west-stairs.json').write_text(json.dumps(routes));Path('build/city-exteriors/weldon-west-trees.json').write_text(json.dumps(trees))
 return dict(key=KEY,name='Weldon Place west homes',center=[1890,0,-3730],bounds=list(unary_union(ps).buffer(7).bounds),structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
