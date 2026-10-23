"""Rio's red/blue curved glazing, stepped crown and mapped lower resort.
Earth2022 and official2023 photo; CVU128.9m versus131m fitted crown.
Two-metre allowance preserves the existing129.6m guest ceiling; no interior regeneration.
"""
from common import *
from building_surfaces import BuildingSurfaces
from luxor_facades import Access
from forum_shops import facade_frame
KEY='rioExterior'
HEIGHTS={'way/27998220':74,'way/27998223':123,'way/134938477':130,'way/134938479':131,'way/134938481':126,'way/116876230':13,'way/27523550':14,'way/111394031':14,'way/135296660':14,'way/135297226':12,'way/133755241':5,'way/133755243':5,'way/133755251':6,'way/133755258':9,'way/133755305':5,'way/1442763264':9,'way/1442763265':9}
TOWERS=list(HEIGHTS)[:5];LOW=list(HEIGHTS)[5:];GARAGES=['way/27523550','way/111394031','way/135296660']
def records():return [dict(BYID[i],shape=footprint(i).simplify(.08,preserve_topology=True),height=h) for i,h in HEIGHTS.items()]
def exterior(B):
 B.property=KEY+'-exterior';B.detail=0
 rs=records();surf=BuildingSurfaces(rs);access=Access(next(p for p in json.load(open('build/highrises/plan.json')) if p['key']=='rio'))
 for r in rs:
  p=r['shape'];h=r['height'];ident=r['id'];tower=ident in TOWERS;ipanema=ident==TOWERS[0];garage=ident in GARAGES
  B.source='tower/rio' if tower else 'podium/'+ident
  for poly in parts(p):
   for ring in [poly.exterior,*poly.interiors]:
    ps=list(ring.coords)
    for a,b in zip(ps,ps[1:]):
     F,L,nx,nz=facade_frame(B,a,b,p,.08)
     if L<.05:continue
     ux,uz=(b[0]-a[0])/L,(b[1]-a[1])/L;line=LineString([a,b]);tris=surf.wall(ident,a,b,0,h,access)
     region=unary_union([Polygon([(line.project(Point(v[0],v[2])),v[1]) for v in t]) for t in tris])
     def patch(mat,x0,y0,x1,y1,offset=.13):
      if x1<=x0 or y1<=y0:return
      for q in parts(region.intersection(box(x0,y0,x1,y1))):
       for tri in triangles(q):B.face(mat,[(a[0]+ux*x+nx*offset,y,a[1]+uz*x+nz*offset) for x,y in list(tri.exterior.coords)[:-1]])
     patch('ri-blueglass' if tower else 'ri-sand',0,0,L,h)
     if tower:
      # Fields are cut to a curved boundary in elevation, not arbitrary colored bays.
      steps=max(1,math.ceil(L/1.5));dx=L/steps
      for j in range(steps):
       x0=j*dx;x1=(j+1)*dx;wx=a[0]+ux*(x0+x1)/2;wz=a[1]+uz*(x0+x1)/2
       if ipanema:
        distance=min(100,math.hypot(wx+1357,wz+164));threshold=74*(1-(min(1,distance/112))**1.7)
       else:
        distance=abs(wx+1219);threshold=123*(1-(min(1,distance/70))**1.8)
       patch('ri-redglass',x0,threshold,x1,h,.15)
       patch('ri-blueframe',x0,0,min(x0+.045,L),min(threshold,h),.23)
       patch('ri-redframe',x0,threshold,min(x0+.045,L),h,.23)
       for y in np.arange(7,h,3.15 if not ipanema else 3.4):
        patch('ri-redframe' if y>threshold else 'ri-blueframe',x0,y,x1,y+.09,.24)
      if ipanema and L<24:
       patch('ri-white',0,6,L,h,.30)
       patch('ri-white',0,h-.6,L,h,.34)
       if L>15:F.text('RIO',(L/2,h-6,-.42),4.2,'ri-letter')
      F.box('ri-white',(L/2,h+.15,0),(L,.3,.5))
     elif garage:
      for y in np.arange(1,h-1,3.2):patch('ri-shadow',0,y,L,min(y+1.7,h-.5),.2)
      for x in np.arange(0,L,7):patch('ri-white',x,0,min(x+.7,L),h,.3)
      F.box('ri-white',(L/2,h+.5,0),(L,1,.45))
     else:
      patch('ri-plinth',0,0,L,.7,.18)
      for y in [h-.7,6.4]:patch('ri-cream',0,y,L,min(y+.35,h),.25)
      for x in np.arange(.7,L-1,4.8):
       patch('ri-entryglass',x,.75,min(x+3.5,L-.25),min(5.7,h-.8),.20)
       for edge in [x,min(x+3.5,L-.25)]:patch('ri-bronze',edge,.7,min(edge+.07,L),min(5.8,h-.7),.28)
       if h>8:F.box('ri-awning',(x+1.7,5.85,1),(3.5,.18,2.2))
      for x in np.arange(0,L,9.6):patch('ri-cream',x,0,min(x+.55,L),h,.30)
      F.box('ri-cream',(L/2,h+.2,0),(L,.4,.5))
     if not tower:
      for t in tris:
       c=B.solids[B.property];n=len(c['vertices'])//3;c['vertices'].extend(v for pt in t for v in pt);c['indices'].extend([n,n+1,n+2])
   roof=surf.roof(ident,poly,h);B.planar('pa-parking' if garage else 'ri-roof',roof,h+.025,not tower)
   if garage:
    for z in np.arange(poly.bounds[1]+7,poly.bounds[3]-3,16):
     for x in np.arange(poly.bounds[0]+3,poly.bounds[2]-3,2.7):B.planar('pa-line',box(x,z,x+.08,z+5).intersection(roof.buffer(-1)),h+.05)
   else:
    # Small shared roof service modules stay fully inside each uncovered roof.
    B.detail=1
    for x in np.arange(poly.bounds[0]+10,poly.bounds[2]-7,24):
     for z in np.arange(poly.bounds[1]+10,poly.bounds[3]-7,24):
      if roof.contains(box(x-2,z-1.5,x+2,z+1.5)):
       B.box('ri-white',(x,h+.7,z),(4,1.35,3));B.box('ri-vent',(x,h+1.4,z),(3.5,.1,2.5))
    B.detail=0
 # Four curved basins fitted to the Earth2022 plan within the mapped courtyard notch.
 # Approximate registration: photo image640,400 at world-1215,-172.5;3.27px/m.
 B.source='pool-courtyard'
 occupied=unary_union([r['shape'] for r in rs])
 deck=Polygon([(-1298,-141),(-1237,-211),(-1172,-220),(-1137,-197),(-1137,-124),(-1240,-120)]).difference(occupied.buffer(.35))
 outlines=[[(706,285),(729,270),(760,278),(788,275),(826,285),(838,300),(826,318),(828,333),(807,341),(793,337),(785,326),(759,330),(743,324),(736,304),(714,306)],[(630,421),(650,414),(673,428),(676,446),(687,456),(680,474),(685,490),(674,506),(675,521),(659,529),(646,518),(635,519),(626,503),(624,480),(610,468),(618,453)],[(552,380),(573,368),(596,365),(615,373),(622,387),(616,400),(601,406),(595,420),(580,421),(565,409)],[(410,427),(431,422),(446,430),(438,442),(419,449),(410,464),(414,482),(431,491),(432,505),(416,512),(400,503),(389,484),(386,462),(395,442)]]
 pools=[]
 for k,outline in enumerate(outlines):
  pool=Polygon([(-1215+(x-640)/3.27+(8 if k==3 else 0),-172.5+(z-400)/3.27-(7 if k==3 else 0)) for x,z in outline]).buffer(.9).buffer(-.9).intersection(deck.buffer(-.6));pools.append(pool)
 water=unary_union(pools)
 B.planar('ri-paving',deck.difference(water),.32,True);B.planar('water',water,.19);B.planar('ri-cream',water,-1.0,True);B.planar('ri-cream',water.buffer(.4).difference(water),.36,True)
 for poly in parts(water):
  pts=list(poly.exterior.coords)
  for a,b in zip(pts,pts[1:]):B.face('ri-cream',[(a[0],-1,a[1]),(b[0],-1,b[1]),(b[0],.19,b[1]),(a[0],.19,a[1])],True)
 for x in np.arange(-1285,-1145,3.0):
  for z in np.arange(-210,-125,7):
   if 2.5<water.distance(Point(x,z))<7 and deck.difference(water.buffer(2)).contains(box(x-.5,z-1,x+.5,z+1)):
    B.box('ri-white',(x,.55,z),(.7,.15,1.9));B.box('ri-bronze',(x,.37,z),(.6,.18,1.6))
 return dict(key=KEY,name='Rio towers and lower resort exterior',center=[-1320,0,-141],bounds=[-1653,-331,-1004,39],building='rio',structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
