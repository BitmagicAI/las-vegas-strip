"""Elara curved curtain wall and distinct low Harmon canopy, Earth Nov 2022."""
from common import *
from luxor_facades import Access
from forum_shops import facade_frame
KEY='elaraExterior'
def tower_shape():return footprint('relation/5342155').intersection(box(290,770,480,814))
def exterior(B):
 B.property=KEY+'-exterior';B.detail=0;B.source='tower/elara'
 p=tower_shape();access=Access(next(q for q in json.load(open('build/highrises/plan.json')) if q['key']=='elara'))
 for poly in parts(p):
  ps=list(poly.exterior.coords)
  for a,b in zip(ps,ps[1:]):
   F,L,nx,nz=facade_frame(B,a,b,p,.08)
   if L<.1:continue
   line=LineString([a,b]);ux,uz=(b[0]-a[0])/L,(b[1]-a[1])/L
   region=unary_union([Polygon([(line.project(Point(v[0],v[2])),v[1]) for v in t]) for t in access.wall(a,b,0,183)])
   def patch(mat,x0,y0,x1,y1,offset=.15):
    for q in parts(region.intersection(box(x0,y0,x1,y1))):
     for t in triangles(q):B.face(mat,[(a[0]+ux*x+nx*offset,y,a[1]+uz*x+nz*offset) for x,y in list(t.exterior.coords)[:-1]])
   patch('el-glass',0,0,L,183)
   for y in np.arange(10,182,3.5):
    patch('el-spandrel',0,y,L,y+.7,.18);patch('el-frame',0,y,L,y+.06,.22)
   for x in np.arange(0,L,1.55):patch('el-frame',x,8,min(x+.055,L),183,.22)
   # Narrow red vertical accent belongs to the east end, not every facade.
   if nx>.8 and L>12:patch('el-red',L*.3,28,L*.3+2.2,183,.24)
   if nz>.6 and L>60:F.text('Hilton Grand Vacations',(L/2,177,-.35),2,'el-white')
   F.box('el-roof',(L/2,183.2,0),(L,.4,.35))
  B.planar('el-roof',poly,183.1)
 # The south face is segmented; keep one continuous identity rather than per-edge labels.
 Frame(B,340,813,0,y=0).text('Hilton Grand Vacations',(0,177,-.5),1.7,'el-white')
 B.source='roof'
 for x,w,d,h in [(330,33,13,2.5),(385,44,8,3),(442,13,15,5)]:
  B.box('el-white',(x,183+h/2,792),(w,h,d));B.box('el-vent',(x,183+h+.1,792),(w-1,.2,d-1))
 # Low white sweeping canopy follows mapped south curves; it is not tower height.
 B.source='arrival'
 canopy=footprint('relation/5342155').difference(p).union(box(340,805,465,813))
 B.planar('el-white',canopy,8.5,True);B.planar('el-white',canopy,7.9)
 for poly in parts(canopy):
  ps=list(poly.exterior.coords)
  for a,b in zip(ps,ps[1:]):B.face('el-white',[(a[0],7.9,a[1]),(b[0],7.9,b[1]),(b[0],8.5,b[1]),(a[0],8.5,a[1])],True)
 for x,z in [(425,835),(463,835),(355,809),(391,809)]:B.box('el-metal',(x,4,z),(.55,8,.55),True)
 B.box('el-vent',(442,8.65,825),(17,.3,10))
 # Recessed service/entrance glazing beneath east canopy, leave drive open.
 B.box('el-glass',(467,3.7,823),(.3,7.4,22),True)
 for z in np.arange(813,835,2):B.box('el-frame',(466.8,3.7,z),(.12,7.4,.06))
 # Southwest pool terrace, estimated footprint from the overhead reference.
 from shapely.geometry import shape
 layers=json.load(open('build/geographic-strip/surface-layers.geojson'))['features']
 blocked=unary_union([shape(f['geometry']).buffer(.5) for f in layers if f['properties']['kind'] in ['road','sidewalk']])
 B.source='pool-deck'
 deck=box(309,815,365,852).difference(blocked).difference(p)
 pool=Polygon([(325,824),(339,822),(348,825),(351,832),(350,844),(340,846),(330,844),(322,838)]).buffer(2).buffer(-2).intersection(deck.buffer(-2))
 B.planar('el-roof',deck.difference(pool),.31,True)
 B.planar('water',pool,.24);B.planar('el-white',pool,.02,True)
 B.planar('el-white',pool.buffer(.5).difference(pool),.34,True)
 for z in [820,847]:
  for x in range(314,360,4):
   if deck.contains(Point(x,z)):
    B.box('el-white',(x,.6,z),(.72,.16,1.9))
    B.box('el-metal',(x,.46,z),(.55,.12,1.5))
 return dict(key=KEY,name='Elara glass tower and arrival exterior',center=[390,0,812],bounds=[290,770,480,855],building='elara',structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
