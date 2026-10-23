"""Westgate reference-based tower, convention podium, garage and station facade.
Official tower 114m; lower elevations/photo details are estimated.
"""
from common import *
from building_surfaces import BuildingSurfaces
from luxor_facades import Access
from forum_shops import facade_frame
KEY='westgateExterior'
def exterior(B):
 B.property=KEY+'-exterior';B.detail=0
 heights={'way/85402000':114,'way/134691921':12,'way/134689730':8,'way/134675467':17,'way/134676135':17}
 rs=[dict(BYID[i],shape=footprint(i),height=h) for i,h in heights.items()]
 pool=unary_union([Point(1984,-2165).buffer(8,resolution=20),Point(1997,-2167).buffer(9,resolution=20),Point(1993,-2155).buffer(7,resolution=20)]).intersection(footprint('way/134691921').buffer(-3))
 surf=BuildingSurfaces(rs);access=Access(next(p for p in json.load(open('build/highrises/plan.json')) if p['key']=='westgate'))
 for r in rs:
  p=r['shape'];h=r['height'];tower=h>100;garage=h==17;station=r['id']=='way/134689730';B.source='tower/westgate' if tower else 'podium/'+r['id']
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
    patch('wg-white' if tower or garage else 'wg-stone',0,0,L,h)
    if tower:
     if L>30:
      count=max(1,round((L-3)/3.1));pitch=(L-3)/count
      for i in range(count):
       x=1.5+i*pitch;w=pitch*.68
       patch('wg-glass',x,4,x+w,h-4,.24)
       patch('wg-frame',x+w/2-.04,4,x+w/2+.04,h-4,.28)
       for y in np.arange(6,h-4,3.45):patch('wg-frame',x,y,x+w,y+.055,.3)
       F.box('wg-white',(x-.18,h/2,0),(.24,h-.4,.65))
     elif L<12:
      patch('wg-glass',.35,4,max(.35,L-.35),h-5,.24)
      for y in np.arange(6,h-4,3.45):patch('wg-frame',.35,y,max(.35,L-.35),y+.055,.3)
      for x in np.arange(0,L,3.1):patch('wg-white',x,0,min(x+.38,L),h,.38)
     for y in [3.7,h-4,h-1]:patch('wg-white',0,y,L,y+.4,.4)
     if L>30:
      for x in np.arange(3,L-3,8):
       F.box('wg-white',(x,h+1,0),(.5,2,.7));F.box('wg-white',(x+2.3,h+2,0),(5,.25,.7))
    elif garage:
     for y in np.arange(3,h,3):patch('wg-shadow',.4,y-1.75,max(.4,L-.4),y-.25,.24)
     for x in np.arange(0,L,6):patch('wg-white',x,0,min(x+.55,L),h,.34)
    else:
     patch('wg-glass',.5,1,max(.5,L-.5),5.6,.24)
     for x in np.arange(0,L,5.4):patch('wg-white',x,0,min(x+.45,L),h,.35)
     for y in [5.8,h-.6]:patch('wg-white',0,y,L,y+.35,.4)
     if not station:
      patch('wg-stone',.3,6.5,max(.3,L-.3),h-.8,.28)
      for x in np.arange(1,L,3):patch('wg-joint',x,6.5,min(x+.08,L),h-.8,.32)
    F.box('wg-white',(L/2,h+.2,0),(L,.4,.65))
   roof=surf.roof(r['id'],poly,h)
   if r['id']=='way/134691921':roof=roof.difference(pool)
   B.planar('wg-blue-roof' if station else 'wg-roof',roof,h+.04,not tower)
   if not tower:
    for a,b in zip(ps,ps[1:]):
     for tri in surf.wall(r['id'],a,b,0,h,access):
      c=B.solids[B.property];n=len(c['vertices'])//3;c['vertices'].extend(float(v) for pt in tri for v in pt);c['indices'].extend([n,n+1,n+2])
   if tower:
    inner=poly.buffer(-3)
    B.planar('wg-roof',inner,h+.4)
    for q in parts(inner):
     for a,b in zip(list(q.exterior.coords),list(q.exterior.coords)[1:]):
      F,L,*_=facade_frame(B,a,b,q,0);F.box('wg-white',(L/2,h+.8,0),(L,1.6,.3))
 B.source='pool-deck'
 B.planar('hgv_pool',pool,11.88)
 B.planar('hgv-cream',pool.buffer(.5).difference(pool),12.10,True)
 B.planar('hgv-pool-tile',pool,10.9,True)
 for q in parts(pool):
  ps=list(q.exterior.coords)
  for a,b in zip(ps,ps[1:]):B.face('hgv-pool-tile',[(a[0],10.9,a[1]),(b[0],10.9,b[1]),(b[0],12.1,b[1]),(a[0],12.1,a[1])],True)
 return dict(key=KEY,name='Westgate exterior and lower buildings',center=[1920,0,-2250],bounds=[1770,-2610,2140,-1985],building='westgate',structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
