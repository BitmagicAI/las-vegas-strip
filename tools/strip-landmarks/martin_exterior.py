"""The Martin: stepped blue curtain wall, projecting slab/guard balcony rings.
Mapped157m tower; lower elevations and pool outline fitted approximately to Earth2022.
"""
from common import *
from building_surfaces import BuildingSurfaces
from luxor_facades import Access
from forum_shops import facade_frame
KEY='martinExterior'
TOWER='way/495695274';LOW=['way/495695272','way/495695273','way/495695270','way/495695271']
def exterior(B):
 B.property=KEY+'-exterior';B.detail=0
 heights={TOWER:157,'way/495695272':4.4,'way/495695273':13.3,'way/495695270':6,'way/495695271':3.5}
 records=[dict(BYID[i],shape=footprint(i).simplify(.12,preserve_topology=True),height=heights[i]) for i in [TOWER]+LOW]
 surf=BuildingSurfaces(records);access=Access(next(p for p in json.load(open('build/highrises/plan.json')) if p['key']=='martin'))
 for r in records:
  p=r['shape'];h=r['height'];tower=r['id']==TOWER;garage=r['id']=='way/495695273';B.source='tower/martin' if tower else 'podium/'+r['id']
  for poly in parts(p):
   ps=list(poly.exterior.coords)
   for a,b in zip(ps,ps[1:]):
    F,L,nx,nz=facade_frame(B,a,b,p,.08)
    if L<.1:continue
    line=LineString([a,b]);ux,uz=(b[0]-a[0])/L,(b[1]-a[1])/L
    region=unary_union([Polygon([(line.project(Point(v[0],v[2])),v[1]) for v in t]) for t in surf.wall(r['id'],a,b,0,h,access)])
    def patch(mat,x0,y0,x1,y1,offset=.14):
     if x1<=x0 or y1<=y0:return
     for q in parts(region.intersection(box(x0,y0,x1,y1))):
      for tri in triangles(q):B.face(mat,[(a[0]+ux*x+nx*offset,y,a[1]+uz*x+nz*offset) for x,y in list(tri.exterior.coords)[:-1]])
    patch('ma-glass' if tower else 'ma-white',0,0,L,h)
    if tower:
     for x in np.arange(0,L,1.65):patch('ma-frame',x,4,min(x+.055,L),157,.20)
     for y in np.arange(6,155,3.35):patch('ma-spandrel',0,y,L,y+.8,.17)
     for x in [0,max(0,L-.16)]:patch('ma-white',x,4,min(x+.16,L),157,.21)
     patch('ma-lobby',0,0,L,4.2,.2)
    elif garage:
     for y in [1,4.4,7.8,11.1]:
      patch('ma-shadow',0,y,L,min(y+1.65,13.05),.18)
      for x in np.arange(0,L,5.5):patch('ma-white',x,y,min(x+.5,L),min(y+1.7,13.1),.25)
     F.box('ma-white',(L/2,h+.55,0),(L,1.1,.4))
    else:
     for x in np.arange(.4,L,2.8):patch('ma-lobby',x,.45,min(x+2.2,L-.15),h-.45,.20)
     F.box('ma-white',(L/2,h+.14,0),(L,.28,.4))
    if not tower:
     for t in surf.wall(r['id'],a,b,0,h,access):
      c=B.solids[B.property];n=len(c['vertices'])//3;c['vertices'].extend(v for pt in t for v in pt);c['indices'].extend([n,n+1,n+2])
   roof=surf.roof(r['id'],poly,h);B.planar('pa-parking' if garage else 'ma-roof',roof,h+.025,not tower)
   if garage:
    for z in np.arange(poly.bounds[1]+6,poly.bounds[3]-3,15):
     for x in np.arange(poly.bounds[0]+3,poly.bounds[2]-3,2.7):B.planar('pa-line',box(x,z,x+.08,z+5).intersection(roof.buffer(-1)),h+.05)
  if tower:
   # Continuous ring topology avoids internal seams on the curved and notched ends.
   outer=p.buffer(.85,join_style=1,quad_segs=3);ring=outer.difference(p.buffer(.12))
   for y in np.arange(6,155,3.35):
    B.planar('ma-white',ring,y+.8)
    for poly2 in parts(outer):
     ps2=list(poly2.exterior.coords)
     for a,b in zip(ps2,ps2[1:]):
      B.face('ma-white',[(a[0],y+.58,a[1]),(b[0],y+.58,b[1]),(b[0],y+.8,b[1]),(a[0],y+.8,a[1])])
      B.face('ma-balcony-glass',[(a[0],y+.82,a[1]),(b[0],y+.82,b[1]),(b[0],y+1.75,b[1]),(a[0],y+1.75,a[1])])
      B.face('ma-frame',[(a[0],y+1.75,a[1]),(b[0],y+1.75,b[1]),(b[0],y+1.8,b[1]),(a[0],y+1.8,a[1])])
   B.planar('ma-white',outer.difference(p.buffer(-.4)),157.3)
   for x,z,w,d,h2 in [(-846,836,12,11,2.2),(-823,839,8,10,3),(-808,834,7,5,1.8)]:
    B.box('ma-white',(x,157+h2/2,z),(w,h2,d));B.box('ma-vent',(x,157+h2+.1,z),(w-.4,.2,d-.4))
 # Western pool court, clear of mapped club building and guest approach.
 B.source='pool-court';occupied=unary_union([r['shape'] for r in records])
 deck=box(-909,820,-885,855).difference(occupied.buffer(.25));pool=box(-903,829,-893,849).intersection(deck.buffer(-1.2))
 B.planar('ma-paving',deck.difference(pool),.31,True);B.planar('water',pool,.22);B.planar('ma-white',pool,-1.1,True);B.planar('ma-white',pool.buffer(.4).difference(pool),.34,True)
 for x in [-906,-888]:
  for z in np.arange(824,853,3):
   if deck.difference(pool.buffer(.5)).contains(box(x-.5,z-1,x+.5,z+1)):B.box('ma-white',(x,.55,z),(.75,.16,1.8));B.box('ma-frame',(x,.4,z),(.6,.15,1.6))
 # Solid basin and perimeter fence; leave the tower-side approach open.
 for poly in parts(pool):
  ps=list(poly.exterior.coords)
  for a,b in zip(ps,ps[1:]):B.face('ma-white',[(a[0],-1.1,a[1]),(b[0],-1.1,b[1]),(b[0],.22,b[1]),(a[0],.22,a[1])],True)
 for poly in parts(deck):
  ps=list(poly.exterior.coords)
  for a,b in zip(ps,ps[1:]):
   line=LineString([a,b]);L=line.length
   if L<2 or line.distance(occupied)<.4:continue
   for y in [.55,1.45]:B.tube('ma-frame',(a[0],y,a[1]),(b[0],y,b[1]),.035,6)
   for t in np.linspace(0,1,max(2,math.ceil(L/.16))):
    x,z=a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t
    B.tube('ma-frame',(x,.4,z),(x,1.45,z),.014,4)
   c=B.solids[B.property];n=len(c['vertices'])//3
   c['vertices'].extend([a[0],.32,a[1],b[0],.32,b[1],b[0],1.45,b[1],a[0],1.45,a[1]]);c['indices'].extend([n,n+1,n+2,n,n+2,n+3])
 # Identity on the existing west approach, leaving the guest entrance corridor open.
 Frame(B,-889,805,math.pi/2,y=0).text('THE MARTIN',(0,2.7,0),.55,'ma-letter')
 return dict(key=KEY,name='The Martin tower and lower exterior',center=[-834,0,838],bounds=[-914,802,-754,858],building='martin',structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
