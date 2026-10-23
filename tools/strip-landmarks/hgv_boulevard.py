"""Hilton Boulevard: separately fitted wings, central pavilion and garage.
Earth 2022-11-09; CTBUH identifies 90m/123m towers. Pavilion 14m estimated.
"""
from common import *
from luxor_facades import Access
from forum_shops import facade_frame
KEY='hgvExterior'
def exterior(B):
 B.property=KEY+'-exterior';B.detail=0
 plan=next(p for p in json.load(open('build/highrises/plan.json')) if p['key']=='hgv-boulevard');access=Access(plan)
 records=[]
 for p in parts(footprint('relation/6138877')):
  h=14 if p.area<800 else (90 if p.bounds[3]-p.bounds[1]>p.bounds[2]-p.bounds[0] else 123)
  records.append((p,h,False))
 records.append((footprint('way/568597559'),24,True))
 for p,h,garage in records:
  B.source='podium/way/568597559' if garage else 'tower/hgv-boulevard'
  for poly in parts(p):
   ps=list(poly.exterior.coords)
   for a,b in zip(ps,ps[1:]):
    line=LineString([a,b]);L=line.length
    if L<.1:continue
    F,L,nx,nz=facade_frame(B,a,b,p,.08);ux,uz=(b[0]-a[0])/L,(b[1]-a[1])/L
    region=unary_union([Polygon([(line.project(Point(v[0],v[2])),v[1]) for v in tri]) for tri in access.wall(a,b,0,h)])
    def patch(mat,x0,y0,x1,y1,offset=.12):
     for q in parts(region.intersection(box(x0,y0,x1,y1))):
      for tri in triangles(q):B.face(mat,[(a[0]+ux*x+nx*offset,y,a[1]+uz*x+nz*offset) for x,y in list(tri.exterior.coords)[:-1]])
    patch('hgv-sand',0,0,L,h)
    if garage:
     for y in np.arange(2,h-1,3.2):patch('hgv-shadow',.4,y,L-.4,y+1.65,.2)
     for x in np.arange(0,L,7):patch('hgv-cream',x,0,min(x+.45,L),h,.3)
    elif h>20:
     if L>25:
      pitch=3.15;count=max(1,int((L-6)/pitch));spacing=(L-6)/count
      for x in [3+i*spacing for i in range(count)]:
       for y in np.arange(5,h-3,3.08):
        patch('hgv-window',x,y,x+spacing*.60,min(y+2.15,h-2),.18)
        patch('hgv-sill',x-.08,y-.15,x+spacing*.60+.08,y,.28)
       patch('hgv-cream',x+spacing*.76,4,x+spacing*.86,h-1,.3)
     else:
      for x in np.arange(1.1,L-1,2.2):patch('hgv-cream',x,5,min(x+.27,L),h,.28)
     for y in [3.7,h-1.7,h-.5]:patch('hgv-cream',0,y,L,y+.3,.36)
     # Raised ribbed shoulder crowns at both ends of each long elevation.
     if L>25:
      for x in [0,L-5]:
       F.box('hgv-sand',(x+2.5,h+.75,0),(5,1.5,1.1))
       for dx in [.6,1.8,3,4.2]:F.box('hgv-cream',(x+dx,h+1.15,-.55),(.22,2.3,.38))
    else:
     for x in np.arange(.7,L-1,3.2):patch('hgv-window',x,1,min(x+2.3,L-.3),8,.2)
     for y in [3.5,8.4,12.4]:patch('hgv-cream',0,y,L,y+.4,.38)
    F.box('hgv-cream',(L/2,h+.1,0),(L,.2,.5))
   B.planar('hgv-roof',poly,h+.03)
   if h>20 and not garage:
    inner=poly.buffer(-2.2)
    for q in parts(inner):
     for a,b in zip(list(q.exterior.coords),list(q.exterior.coords)[1:]):
      F,L,*_=facade_frame(B,a,b,q,0);F.box('hgv-roof',(L/2,h+.75,0),(L,1.5,.22))
 # Rear pool court: dimensions fitted to the top-down 2022 Earth view.
 B.source='pool-court'
 court=Polygon([(993,-2672),(1042,-2663),(1067,-2584),(1034,-2602),(1000,-2625)])
 lap=unary_union([box(998,-2665,1030,-2659),box(998,-2665,1005,-2644)])
 leisure=unary_union([Point(1031,-2633).buffer(5),Point(1041,-2627).buffer(5),Point(1034,-2618).buffer(5),Point(1049,-2610).buffer(5),LineString([(1031,-2633),(1041,-2627),(1034,-2618),(1049,-2610)]).buffer(3)])
 pools=unary_union([lap,leisure]).intersection(court.buffer(-1.5))
 B.planar('hgv-paving',court.difference(pools),.3,True)
 B.planar('hgv_pool',pools,.12)
 B.planar('hgv-cream',pools.buffer(.5).difference(pools),.32)
 for pool in parts(pools):
  B.planar('hgv-pool-tile',pool,-1.1,True)
  for a,b in zip(list(pool.exterior.coords),list(pool.exterior.coords)[1:]):B.face('hgv-pool-tile',[(a[0],-1.1,a[1]),(b[0],-1.1,b[1]),(b[0],.3,b[1]),(a[0],.3,a[1])],True)
 for x,z in [(1012,-2654),(1018,-2653),(1024,-2652),(1029,-2650),(1011,-2640),(1017,-2637),(1021,-2629),(1052,-2603)]:
  F=Frame(B,x,z,.32,y=.3)
  F.box('ph-awning',(0,.42,0),(.68,.13,1.95));F.box('ph-metal',(0,.3,0),(.72,.08,2))
  for xx in [-.28,.28]:F.box('ph-metal',(xx,.14,.1),(.035,.28,1.65))
  B.face('ph-awning',[F.p(-.34,.49,-.3),F.p(.34,.49,-.3),F.p(.34,.95,-.94),F.p(-.34,.95,-.94)])
 return dict(key=KEY,name='Hilton Grand Vacations Boulevard exterior',center=[1100,0,-2660],bounds=[985,-2800,1170,-2560],building='hgv-boulevard',structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
