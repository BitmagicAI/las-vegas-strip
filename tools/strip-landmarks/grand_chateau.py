"""Grand Chateau: branched tower, separate parking podium, green crown."""
from common import *
from building_surfaces import BuildingSurfaces
from luxor_facades import Access
from forum_shops import facade_frame
KEY='grandChateauExterior'
def exterior(B):
 B.property=KEY+'-exterior';B.detail=0
 rs=[dict(BYID[i],shape=footprint(i),height=h) for i,h in [('way/276427203',17),('way/358923855',128)]]
 surf=BuildingSurfaces(rs);access=Access(next(p for p in json.load(open('build/highrises/plan.json')) if p['key']=='grand-chateau'))
 pool=Polygon([(327,979),(335,970),(346,970),(355,980),(347,986),(336,986)])
 for r in rs:
  p=r['shape'];h=r['height'];tower=h>50;B.source='tower/grand-chateau' if tower else 'podium/'+r['id']
  for poly in parts(p):
   ps=list(poly.exterior.coords)
   for a,b in zip(ps,ps[1:]):
    F,L,nx,nz=facade_frame(B,a,b,p,.1);line=LineString([a,b])
    if L<.1:continue
    ux,uz=(b[0]-a[0])/L,(b[1]-a[1])/L
    region=unary_union([Polygon([(line.project(Point(v[0],v[2])),v[1]) for v in t]) for t in surf.wall(r['id'],a,b,0,h,access)])
    def patch(mat,x0,y0,x1,y1,offset=.2):
     if x1<=x0:return
     for q in parts(region.intersection(box(x0,y0,x1,y1))):
      for t in triangles(q):B.face(mat,[(a[0]+ux*x+nx*offset,y,a[1]+uz*x+nz*offset) for x,y in list(t.exterior.coords)[:-1]])
    patch('gc-cream',0,0,L,123 if tower else h)
    if tower:
     bays=max(1,round(L/3.2));pitch=L/bays
     for j in range(bays):
      x=j*pitch
      patch('gc-taupe',x+.38,16,min(x+pitch-.38,L),123,.24)
      for y in np.arange(18,122,3.05):patch('gc-window',x+.7,y,min(x+pitch-.7,L),y+2.03,.28)
      patch('gc-white',x,16,min(x+.32,L),123,.35)
     # Short chamfer/end panels have uninterrupted dark vertical bays.
     if L<22:
      for j in range(bays):
       x=j*pitch;patch('gc-window',x+.7,17,min(x+pitch-.7,L),122,.4)
       for y in np.arange(18,122,3.05):patch('gc-taupe',x+.7,y,min(x+pitch-.7,L),y+.055,.44)
     for y in [16,49,96,122]:
      patch('gc-white',0,y,L,y+.6,.45);F.box('gc-white',(L/2,y,0),(L,.35,.8))
     for x in np.arange(2,L-2,5.5):
      patch('gc-white',x-.85,123,x+.85,125.3,.34);patch('gc-window',x-.5,123,x+.5,124.9,.38)
      # Dormer cheeks return into the sloped roof; dimensions are photo estimates.
      fx=x if F.co*ux-F.si*uz>0 else L-x
      F.box('gc-white',(fx,125.35,.4),(1.8,.2,1.5))
      for side in [-1,1]:F.box('gc-white',(fx+side*.78,124.15,.4),(.14,2.3,1.4))
    else:
     for y in [4,7.5,11,14.5]:patch('gc-shadow',.4,y-1.4,L-.4,y-.2,.28)
     for x in np.arange(0,L,8):patch('gc-taupe',x,0,min(x+.8,L),h,.38)
     for y in [3,6.5,10,13.5,16]:patch('gc-white',0,y,L,y+.2,.35)
     for t in surf.wall(r['id'],a,b,0,h,access):
      c=B.solids[B.property];n=len(c['vertices'])//3;c['vertices'].extend(float(v) for pt in t for v in pt);c['indices'].extend([n,n+1,n+2])
    F.box('gc-white',(L/2,(123 if tower else h)+.2,0),(L,.4,.65))
   roof=surf.roof(r['id'],poly,h)
   if not tower:roof=roof.difference(pool)
   if tower:
    # Original mansard mesh. Keep the existing footprint, maximum height and parent
    # interior/collision ownership; this roof is not a new public walking surface.
    inset=poly.buffer(-2.2,join_style=2)
    for t in triangles(poly.difference(inset)):
     B.upface('gc-green',[(x,123+5*min(1,poly.boundary.distance(Point(x,z))/2.2),z) for x,z in list(t.exterior.coords)[:-1]])
    B.planar('gc-roof',inset,128.04)
   else:B.planar('gc-roof',roof,h+.04,True)
 B.source='pool-deck';B.planar('water',pool,16.84);B.planar('gc-white',pool,15.7,True);B.planar('gc-white',pool.buffer(.5).difference(pool),17.08,True)
 # Light metal frames and dark slings observed in the official fifth-floor photo.
 # Eight inferred placements stay south of the water and north of the verified z=992 walk.
 B.source='pool-furnishings'
 for x in [326,330,334,338,342,346,350,354]:
  F=Frame(B,x,989,y=17.04)
  F.box('gc-shadow',(0,.44,0),(.62,.08,1.25))
  for side in [-1,1]:
   F.tube('gc-white',(side*.35,.40,-.70),(side*.35,.40,.73),.028,6)
   for z in [-.52,.52]:F.tube('gc-white',(side*.35,.06,z),(side*.35,.4,z),.028,6)
  F.b.face('gc-shadow',[F.p(-.31,.44,-.63),F.p(.31,.44,-.63),F.p(.31,.87,-1.14),F.p(-.31,.87,-1.14)])
  for side in [-1,1]:F.tube('gc-white',(side*.35,.44,-.63),(side*.35,.87,-1.14),.028,6)
 B.source='arrival';B.box('gc-white',(341,5.7,900),(24,.7,11),True)
 for x in [330,352]:B.box('gc-cream',(x,2.7,896),(.8,5.4,.8),True)
 return dict(key=KEY,name='Grand Chateau tower podium and arrival exterior',center=[340,0,955],bounds=[285,890,395,1008],building='grand-chateau',structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
