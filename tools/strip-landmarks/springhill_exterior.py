"""SpringHill Suites Convention Center; Earth reference exterior in mapped metres."""
from common import *
from building_surfaces import BuildingSurfaces
from luxor_facades import Access
from forum_shops import facade_frame
KEY='springhillExterior'
def exterior(B):
 B.property=KEY+'-exterior';B.detail=0
 rs=[dict(BYID[i],shape=footprint(i),height=h) for i,h in [('way/543640999',74),('way/313762434',19)]]
 surf=BuildingSurfaces(rs);access=Access(next(p for p in json.load(open('build/highrises/plan.json')) if p['key']=='springhill'))
 pool=box(1543,-2138,1551,-2133)
 for r in rs:
  p=r['shape'];h=r['height'];tower=h>50;B.source='tower/springhill' if tower else 'podium/'+r['id']
  for poly in parts(p):
   ps=list(poly.exterior.coords)
   for a,b in zip(ps,ps[1:]):
    line=LineString([a,b]);L=line.length
    if L<.1:continue
    F,L,nx,nz=facade_frame(B,a,b,p,.1);ux,uz=(b[0]-a[0])/L,(b[1]-a[1])/L
    region=unary_union([Polygon([(line.project(Point(v[0],v[2])),v[1]) for v in t]) for t in surf.wall(r['id'],a,b,0,h,access)])
    def patch(mat,x0,y0,x1,y1,offset=.2):
     for q in parts(region.intersection(box(x0,y0,x1,y1))):
      for t in triangles(q):B.face(mat,[(a[0]+ux*x+nx*offset,y,a[1]+uz*x+nz*offset) for x,y in list(t.exterior.coords)[:-1]])
    patch('sh-white',0,0,L,h)
    if tower:
     xs=[1.3,L-2.6] if L<25 else [2,8,14,16.6,23,25.6,33,39,46,52]
     for x in xs:
      if x<0 or x+1.25>L:continue
      for y in np.arange(4,h-3,3.08):
       patch('sh-window',x,y,x+1.25,y+1.65,.24)
       patch('sh-frame',x+.60,y,x+.65,y+1.65,.29)
       patch('sh-sill',x-.06,y-.12,x+1.31,y,.31)
     for x in np.arange(4,L,10):patch('sh-joint',x,2,min(x+.055,L),h-1,.26)
     for y in [2.5,h-.7]:patch('sh-sill',0,y,L,y+.22,.34)
    else:
     for y in np.arange(3,18,2.9):patch('sh-shadow',.4,y-1.7,max(.4,L-.4),y-.2,.24)
     for x in np.arange(0,L,7):patch('sh-white',x,0,min(x+.5,L),h,.36)
     patch('sh-white',0,17,L,h,.35)
    F.box('sh-white',(L/2,h+.2,0),(L,.4,.5))
   roof=surf.roof(r['id'],poly,h)
   if tower:roof=roof.difference(pool)
   B.planar('sh-roof',roof,h+.04,True)
   if not tower:
    for a,b in zip(ps,ps[1:]):
     for tri in surf.wall(r['id'],a,b,0,h,access):
      c=B.solids[B.property];n=len(c['vertices'])//3;c['vertices'].extend(float(v) for pt in tri for v in pt);c['indices'].extend([n,n+1,n+2])
 B.source='roof-deck'
 for poly in parts(footprint('way/543640999').buffer(-.4)):
  ps=list(poly.exterior.coords)
  for a,b in zip(ps,ps[1:]):
   B.tube('sh-frame',(a[0],75.15,a[1]),(b[0],75.15,b[1]),.04,6)
   for t in np.linspace(0,1,max(2,math.ceil(math.dist(a,b)/.14))):
    x,z=a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1]);B.tube('sh-frame',(x,74.25,z),(x,75.15,z),.015,4)
   c=B.solids[B.property];n=len(c['vertices'])//3
   for pt in [(a[0],74.1,a[1]),(b[0],74.1,b[1]),(b[0],75.2,b[1]),(a[0],75.2,a[1])]:c['vertices'].extend(pt)
   c['indices'].extend([n,n+1,n+2,n,n+2,n+3])

 B.planar('hgv_pool',pool,73.82);B.planar('hgv-pool-tile',pool,72.8,True)
 B.planar('sh-sill',pool.buffer(.45).difference(pool),74.08,True)
 ps=list(pool.exterior.coords)
 for a,b in zip(ps,ps[1:]):B.face('hgv-pool-tile',[(a[0],72.8,a[1]),(b[0],72.8,b[1]),(b[0],74.1,b[1]),(a[0],74.1,a[1])],True)
 B.box('sh-white',(1570,75.8,-2134.5),(14,3.6,12),True)
 B.box('sh-roof',(1570,77.65,-2134.5),(13.4,.1,11.4))
 return dict(key=KEY,name='SpringHill Suites exterior and garage',center=[1570,0,-2130],bounds=[1535,-2150,1608,-2105],building='springhill',structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
