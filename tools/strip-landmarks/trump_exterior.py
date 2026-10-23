"""Trump International: separate mapped tower from the lower podium outline."""
from common import *
from building_surfaces import BuildingSurfaces
from luxor_facades import Access
from forum_shops import facade_frame
KEY='trumpExterior'
def exterior(B):
 B.property=KEY+'-exterior';B.detail=0
 rs=[dict(BYID[i],shape=footprint(i),height=h) for i,h in [('way/111380664',195),('way/111380666',16)]]
 surf=BuildingSurfaces(rs);access=Access(next(p for p in json.load(open('build/highrises/plan.json')) if p['key']=='trump'))
 pool=box(6,-1485,57,-1474)
 for r in rs:
  p=r['shape'];h=r['height'];tower=h>50;B.source='tower/trump' if tower else 'podium/'+r['id']
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
    patch('tr-glass' if tower or nz>.2 else 'tr-white',0,0,L,h)
    if tower:
     for y in np.arange(17,h-5,3.0):
      patch('tr-spandrel',0,y,L,y+.65,.23)
      patch('tr-frame',0,y,L,y+.095,.28)
     for x in np.arange(0,L,1.55):patch('tr-frame',x,16,min(x+.05,L),h-5,.28)
     patch('tr-white',0,h-5,L,h,.35)
     if L>30:
      F.text('TRUMP',(L/2,h-3.8,-.42),2.7,'tr-letter')
    elif nz<-.2 or abs(nx)>.7:
     for y in np.arange(3,15,3):patch('tr-shadow',.5,y-1.6,max(.5,L-.5),y-.3,.26)
     for x in np.arange(0,L,8):patch('tr-white',x,0,min(x+.65,L),h,.36)
    else:
     for x in np.arange(0,L,5):patch('tr-white',x,0,min(x+.32,L),h,.36)
    F.box('tr-white',(L/2,h+.16,0),(L,.32,.5))
   roof=surf.roof(r['id'],poly,h)
   if not tower:roof=roof.difference(pool)
   B.planar('tr-roof',roof,h+.04,not tower)
   if not tower:
    for a,b in zip(ps,ps[1:]):
     for tri in surf.wall(r['id'],a,b,0,h,access):
      c=B.solids[B.property];n=len(c['vertices'])//3;c['vertices'].extend(float(v) for pt in tri for v in pt);c['indices'].extend([n,n+1,n+2])
 B.source='pool-deck'
 B.planar('hgv_pool',pool,15.83);B.planar('hgv-pool-tile',pool,14.5,True)
 B.planar('tr-white',pool.buffer(.5).difference(pool),16.1,True)
 for a,b in zip(list(pool.exterior.coords),list(pool.exterior.coords)[1:]):B.face('hgv-pool-tile',[(a[0],14.5,a[1]),(b[0],14.5,b[1]),(b[0],16.1,b[1]),(a[0],16.1,a[1])],True)
 # Broad pale arrival roof in front of the south podium; clear drive below.
 B.source='arrival'
 B.box('tr-white',(31,5.8,-1444),(54,.6,12),True)
 for x in [6,56]:B.box('tr-white',(x,2.8,-1440),(.65,5.6,.65),True)
 B.source='roof'
 B.box('tr-white',(32,196,-1512),(63,2,19))
 B.box('tr-roof',(32,197.03,-1512),(61,.06,17))
 return dict(key=KEY,name='Trump International tower podium and pool',center=[32,0,-1510],bounds=[-14,-1558,78,-1437],building='trump',structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
