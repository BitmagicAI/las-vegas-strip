"""Single-storey Rexford Place east homes: mapped plans, shallow hips and recessed arrivals.
Street photographs span2015–2020; doors and mechanical dimensions are estimates.
"""
from common import *
from forum_shops import facade_frame
KEY='rexfordPlaceEast';IDS=['way/1236746614', 'way/1236746613', 'way/1236746612', 'way/1236746611', 'way/1236621178', 'way/1236621177', 'way/1236621179', 'way/1236621176', 'way/1236621175', 'way/1236621174', 'way/1236621173']
def window(F,u,y=1.65,w=1.8):
 F.box('rpw-frame-paint',(u,y,-.06),(w+.14,1.3,.12));F.box('rpw-glass',(u,y,-.14),(w,1.16,.04));F.box('rpw-frame-paint',(u,y,-.18),(.04,1.16,.03));F.box('rpw-sill-paint',(u,y-.7,-.14),(w+.25,.09,.27))
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/rexford-place-east';B.detail=0;ps=[footprint(i) for i in IDS];samples=[];routes=[];trees=[];W=Frame(B,0,0,y=0)
 for idx,p in enumerate(ps):
  wall=['white','rose','cream','white','cream','tan','white','white','tan','cream','white'][idx]
  B.shell(p,.18,2.95,'rpw-'+wall+'-stucco',roof=False)
  # Constant-pitch hips follow the actual L-shaped boundaries rather than a flat inset cap.
  roof=p.buffer(.32,join_style=2);level=0;outer=roof;slope=.10 if idx in [0,2,3,4,6,10] else .25;roofmat='rpw-membrane-paint' if idx in [0,2,3,4,6,10] else ('rpw-gray-roof-paint' if idx==7 else 'bt-roof-paint')
  while not outer.is_empty and level<8:
   inner=roof.buffer(-(level+.4),join_style=2)
   for poly in parts(outer.difference(inner)):
    for t in triangles(poly):B.upface(roofmat,[(x,3.0+roof.boundary.distance(Point(x,z))*slope,z)for x,z in list(t.exterior.coords)[:-1]],True)
   outer=inner;level+=.4
  edges=[facade_frame(B,a,b,p,0) for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:])]
  front=[e for e in edges if e[2]<-.6];F,L,_,_=max(front,key=lambda e:e[1]);du=L*.53
  for G,ll,nx,nz in edges:
   G.box('rpw-fascia-paint',(ll/2,2.97,-.12),(ll,.17,.46));G.box('rpw-plinth-paint',(ll/2,.31,-.025),(ll,.26,.08))
   if G is F:
    for u in [ll*.22,ll*.79]:window(G,u,w=min(2.1,ll*.24))
    G.box('rpw-door-trim-paint',(du,1.25,-.07),(1.04,2.14,.15));G.box('rpw-door-paint',(du,1.25,-.16),(.88,1.99,.04));G.box('rpw-hardware-paint',(du+.31,1.2,-.2),(.04,.14,.04))
    # Thin metal entrance awning and two slender porch columns.
    G.box('rpw-awning-paint',(du,2.61,-.8),(2.1,.10,1.6));
    for u in [du-.95,du+.95]:G.box('rpw-post-paint',(u,1.4,-1.5),(.07,2.44,.07),True)
    G.box('rpw-concrete',(du,.10,-.9),(2.2,.16,1.8),True)
    if idx in [2,6,9]:
     for u in [ll*.22,ll*.79]:
      B.face('rpw-awning-paint',[G.p(u-1.12,2.42,-.05),G.p(u+1.12,2.42,-.05),G.p(u+1.12,2.15,-.7),G.p(u-1.12,2.15,-.7)])
   elif nx<-.6 and ll>3.3:
    # A second short east edge at the recessed L serves the garage.
    G.box('rpw-garage-trim-paint',(ll/2,1.35,-.06),(min(4.2,ll-.3),2.35,.12));G.box('rpw-garage-paint',(ll/2,1.35,-.14),(min(4,ll-.5),2.2,.04))
    for y in np.arange(.4,2.4,.35):G.box('rpw-garage-seam-paint',(ll/2,float(y),-.17),(min(4,ll-.5),.018,.025))
   elif ll>4:
    for u in np.arange(2.1,ll-1.2,5.6):window(G,float(u),w=1.2)
  # Continuous entry path in a gravel yard; front fences leave the approach open.
  yard=F.poly([(0,0),(L,0),(L,-8),(0,-8)]).difference(p)
  path=F.poly([(du-.7,0),(du+.7,0),(du+.7,-8),(du-.7,-8)])
  B.planar('rpw-yard-paint',yard.difference(path),.17,True);B.planar('rpw-concrete',path,.18,True)
  for a,b in [(0,du-1),(du+1,L)]:
   if b-a<.2:continue
   if idx%3==0:
    F.box('rpw-block-stucco',((a+b)/2,.67,-5.9),(b-a,1.0,.18),True);F.box('rpw-fence-cap-paint',((a+b)/2,1.2,-5.9),(b-a,.10,.23))
   elif idx%3==1:
    for u in np.arange(a,b,.20):F.box('rpw-fence-paint',(float(u),.74,-5.9),(.03,1.12,.03))
    F.box('rpw-fence-paint',((a+b)/2,1.3,-5.9),(b-a,.04,.04))
  # Short perimeter apron makes visible side doors accessible without terrain holes.
  B.planar('rpw-concrete',p.buffer(.4,join_style=2).difference(p),.18,True)
  routes.append([F.p(du,.18,-5.5),F.p(du,.18,-2.0),F.p(du,.18,-.55)])
  if idx in [0,3,6,9]:
   x,y,z=F.p(L*.18,0,-3.4);trees.append([x,z,5.5+idx*.15,idx*.7])
  x,z=p.representative_point().coords[0];yy=3.0+roof.boundary.distance(Point(x,z))*slope
  W.box('rpw-service-paint',(x,yy+.36,z),(1.1,.72,1.1));W.box('rpw-vent-paint',(x,yy+.73,z),(.97,.03,.97))
  B.lathe('rpw-flue-paint',(x+2,z),[(yy-.2,.12),(yy+.65,.12),(yy+.7,.19)],10)
  for x in np.arange(p.bounds[0]+.5,p.bounds[2],1.2):
   for z in np.arange(p.bounds[1]+.5,p.bounds[3],1.2):
    if p.buffer(-.3).contains(Point(x,z)):samples.append([float(x),3.0+roof.boundary.distance(Point(x,z))*slope+.4,float(z)])
 Path('build/city-exteriors/rexford-place-east-samples.json').write_text(json.dumps(samples));Path('build/city-exteriors/rexford-place-east-stairs.json').write_text(json.dumps(routes));Path('build/city-exteriors/rexford-place-east-trees.json').write_text(json.dumps(trees))
 return dict(key=KEY,name='Rexford Place east homes',center=[2088,0,-4045],bounds=list(unary_union(ps).buffer(7).bounds),structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
