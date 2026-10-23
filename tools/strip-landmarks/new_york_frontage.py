"""Streetwall and garage facades; existing hotel skyline, coaster and interiors retained."""
from common import *
from forum_shops import facade_frame
from building_surfaces import BuildingSurfaces
from luxor_facades import Access
KEY='newYorkFrontage'
def exterior(B):
 B.property=KEY+'-exterior';B.detail=0
 ids=['way/115661793','way/115661794','way/29709970']
 records=[dict(BYID[i],shape=footprint(i)) for i in ids]
 # Main arrival is an open canopy, not an enclosed continuation of the podium.
 for r in records:
  if r['id']=='way/115661793':r['shape']=r['shape'].difference(unary_union([box(-52.5,1549,-34,1573),box(-167,1609.7,-136,1643.1)]))
 # Include towers as occluders so the streetwall does not paint their enclosed faces.
 plan=next(p for p in json.load(open('build/highrises/plan.json')) if p['key']=='new-york')
 towers=[dict(f,shape=footprint(f['id'])) for f in plan['features'] if f['id'] not in ids]
 surface=BuildingSurfaces(records+towers);access=Access(plan)
 public=LineString([(-29,1464),(-69,1464),(-95,1479),(-103,1485)]).buffer(4.5,cap_style=2)
 for r in records:
  p=r['shape'];ident=r['id'];h=r['height'];garage=ident=='way/29709970';shack=ident=='way/115661794'
  if shack:continue  # Dedicated reference-led skin below owns this restaurant.
  B.source='podium/'+ident
  for poly in parts(p):
   ps=list(poly.exterior.coords)
   for a,b in zip(ps,ps[1:]):
    F,L,nx,nz=facade_frame(B,a,b,p,.16)
    if L<.2:continue
    line=LineString([a,b]);ux,uz=(b[0]-a[0])/L,(b[1]-a[1])/L;mid=line.interpolate(.5,normalized=True)
    vis=surface.wall(ident,a,b,0,h,access)
    region=unary_union([Polygon([(line.project(Point(v[0],v[2])),v[1]) for v in tri]) for tri in vis])
    if ident=='way/115661793':
     for seg in parts(line.intersection(public),'LineString'):
      ds=[line.project(Point(q)) for q in seg.coords];region=region.difference(box(min(ds)-.05,0,max(ds)+.05,4.7))
    if ident=='way/115661793':
     # Remove old generic hotel skin exactly where the restaurant frontage sits.
     cut=line.intersection(footprint('way/115661794').buffer(.04))
     for seg in parts(cut,'LineString'):
      ds=[line.project(Point(q)) for q in seg.coords]
      region=region.difference(box(min(ds),0,max(ds),9.3))
    if region.is_empty:continue
    def patch(mat,x0,y0,x1,y1,offset=.20):
     for q in parts(region.intersection(box(x0,y0,x1,y1))):
      for tri in triangles(q):B.face(mat,[(a[0]+ux*x+nx*offset,y,a[1]+uz*x+nz*offset) for x,y in list(tri.exterior.coords)[:-1]])
    patch('nyny-concrete' if garage else 'nyny-stone',0,0,L,h)
    if garage:
     for y in np.arange(1.0,h-1,3.15):
      patch('nyny-shadow',.3,y,L-.3,y+1.85,.23)
      patch('nyny-white',0,y+1.9,L,y+2.28,.28)
     for x in np.arange(0,L,7.2):patch('nyny-concrete',x,0,min(x+.55,L),h,.34)
    else:
     east=nx>.25;front=east or (nz<-.2 and mid.y<1480)
     count=max(1,math.ceil(L/(10 if front else 7)));step=L/count
     for j in range(count):
      x=j*step;style=int((mid.y+j*step)/13)%3
      mat=['nyny-stone','nyny-white','nyny-brick'][style] if front and not shack else 'nyny-stone'
      patch(mat,x+.02,.3,x+step-.02,h-.1,.22)
      patch('nyny-window',x+.55,.65,x+step-.55,min(4.1,h-.7),.29)
      for u in np.arange(x+.55,x+step-.45,1.5):patch('nyny-metal',u,.65,u+.065,min(4.1,h-.7),.33)
      patch('nyny-shadow',x+.2,4.25,x+step-.2,min(4.9,h-.2),.32)
      for u in [x+.05,x+step-.32]:patch('nyny-white',u,.1,u+.24,h,.38)
      if h>7:
       for u in np.arange(x+.9,x+step-.8,2.5):
        patch('nyny-shadow',u,5.35,u+1.5,h-1.0,.28)
        patch('nyny-white',u-.08,5.2,u+1.58,5.35,.36)
      if front and step>5:
       F.box('nyny-white',(x+step/2,h-.3,-.30),(step-.15,.45,.6))
       if not shack:F.box('nyny-metal',(x+step/2,4.35,-.90),(step-.8,.18,1.5))
     if shack and L>15 and (east or nz<-.5):F.text('SHAKE SHACK',(L/2,5,-.32),.62,'nyny-green')
    F.box('nyny-white',(L/2,h+.1,-.15),(L+.12,.25,.5))
   roof=surface.roof(ident,poly,h);B.planar('ph-roof',roof,h+.06)
   if not garage:
    for x in np.arange(p.bounds[0]+4,p.bounds[2]-4,19):
     for z in np.arange(p.bounds[1]+4,p.bounds[3]-4,23):
      if roof.contains(box(x-1.5,z-1,x+1.5,z+1)):B.box('ph-metal',(x,h+.5,z),(3,.8,2))
 # Upgrade the retained miniature street row in place. The measured footprint and
 # circulation remain legacy-owned; this skin adds real depth around its openings.
 B.source='streetwall-detail';B.detail=0
 for i,z in enumerate(np.arange(1507,1630,12)):
  if any(abs(z-q)<.01 for q in [1555,1567]):continue  # Mapped Irish kiosk owns this open terrace bay.
  h=[14,18,15,21,17][i%5];F=Frame(B,-37.22,z,-math.pi/2,y=0)
  mat='nyny-brick' if i in [2,7] else ('nyny-white' if i%3 else 'nyny-stone')
  # Front points toward +X (negative local Z). Separations avoid coplanar overlays.
  F.box(mat,(0,h/2,-.04),(11.4,h,.12))
  for y,depth,thick in [(1,.22,.18),(6.8,.36,.28),(8.05,.23,.35),(h-.55,.4,.28),(h+.02,.55,.35)]:
   F.box('nyny-white',(0,y,-depth/2-.12),(11.65,thick,depth))
  for u in [-5.42,5.42]:
   F.box('nyny-white',(u,h/2,-.2),(.45,h,.32))
   for y in np.arange(.8,h-.7,.65):F.box('nyny-stone',(u,y,-.39),(.64,.18,.11))
  for u in [-3,0,3]:
   F.box('nyny-window',(u,3.25,-.15),(2.64,4.35,.08))
   for dx in [-1.36,1.36]:F.box('nyny-metal',(u+dx,3.25,-.23),(.1,4.65,.17))
   for y in [1.02,3.95,5.48]:F.box('nyny-metal',(u,y,-.24),(2.8,.1,.16))
   F.box('nyny-metal',(u,2.5,-.25),(.07,2.8,.13))
   for y in np.arange(9,h-1,3):
    F.box('nyny-window',(u,y,-.15),(1.3,1.7,.08))
    for dx in [-.75,.75]:F.box('nyny-white',(u+dx,y,-.22),(.15,1.95,.24))
    for dy in [-.93,.93]:F.box('nyny-white',(u,y+dy,-.28),(1.68,.17,.36))
    F.box('nyny-metal',(u,y,-.22),(.055,1.7,.08))
    F.box('nyny-metal',(u,y+.05,-.23),(1.3,.06,.08))
    F.box('nyny-stone',(u,y+1.12,-.2),(1.8,.13,.23))
  # Fine cornice dentils and masonry string courses replace blank upper walls.
  for u in np.arange(-5.15,5.2,.5):F.box('nyny-white',(u,h-.26,-.38),(.17,.22,.26))
  for y in np.arange(8.3,h-.8,3):F.box('nyny-stone',(0,y,-.14),(10.6,.1,.12))
  # Cover old generic district-name labels with an unbranded recessed fascia.
  F.box('nyny-metal',(0,7.6,-.2),(10.2,.72,.25))
 from shake_shack_frontage import exterior as shack_frontage
 shack_frontage(B)
 from nyny_park_restaurants import exterior as restaurants
 restaurants(B)
 return dict(key=KEY,name='New York New York streetwall',center=[-160,0,1520],bounds=[-365,1425,-38,1656],building='new-york',structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
