"""Allure and adjacent red-panel low-rise blocks; Google Earth 2022 reference."""
from common import *
from luxor_facades import Access
from building_surfaces import BuildingSurfaces
from forum_shops import facade_frame
KEY='allureExterior'
def exterior(B):
 B.property=KEY+'-exterior';B.detail=0
 ids=['way/134935559','way/977762385','way/977762386'];rs=[dict(BYID[i],shape=footprint(i)) for i in ids]
 surface=BuildingSurfaces(rs);access=Access(next(p for p in json.load(open('build/highrises/plan.json')) if p['key']=='allure'))
 for r in rs:
  p=r['shape'];h=r['height'];tower=r['id']==ids[0];B.source='tower/allure' if tower else 'podium/'+r['id']
  for poly in parts(p):
   ps=list(poly.exterior.coords)
   for a,b in zip(ps,ps[1:]):
    line=LineString([a,b]);L=line.length
    if L<.1:continue
    F,L,nx,nz=facade_frame(B,a,b,p,.15);ux,uz=(b[0]-a[0])/L,(b[1]-a[1])/L
    region=unary_union([Polygon([(line.project(Point(v[0],v[2])),v[1]) for v in t]) for t in surface.wall(r['id'],a,b,0,h,access)])
    def patch(mat,x0,y0,x1,y1,offset=.2):
     for q in parts(region.intersection(box(x0,y0,x1,y1))):
      for t in triangles(q):B.face(mat,[(a[0]+ux*x+nx*offset,y,a[1]+uz*x+nz*offset) for x,y in list(t.exterior.coords)[:-1]])
    patch('allure-glass' if tower else 'allure-red',0,0,L,h)
    if tower:
     endwall=line.interpolate(.5,normalized=True).x<1227 or line.interpolate(.5,normalized=True).x>1277
     pier=L<2.8 or (abs(nx)>.8 and L<10) or endwall
     if pier:
      patch('allure-white',0,0,L,h,.26)
      if endwall and L>3:
       for y in np.arange(5,h-4,3.35):
        for x in np.arange(.8,L-1,2.8):patch('allure-glass',x,y+.5,min(x+1.5,L-.5),y+2.65,.3)
     for y in np.arange(5,h-4,3.35):
      patch('allure-white',0,y,L,y+.24,.35)
      if not pier:
       patch('allure-spandrel',0,y+.28,L,y+.77,.25)
       if nz<-.2 or L>15:
        F.box('allure-white',(L/2,y,0),(L,.22,1.35))
        F.box('allure-rail',(L/2,y+.63,-.78),(L,1.04,.05))
        F.box('allure-white',(L/2,y+1.16,-.78),(L,.055,.08))
     if not pier:
      for x in np.arange(0,L,1.7):patch('allure-frame',x,4,min(x+.05,L),h-1,.29)
     for x in [0,max(0,L-.3)]:patch('allure-white',x,0,min(x+.3,L),h,.4)
     patch('allure-white',0,h-.9,L,h,.36)
    else:
     for y in np.arange(2,h-1,3):patch('allure-joint',0,y,L,y+.12,.25)
     for x in np.arange(0,L,8):patch('allure-white',x,0,min(x+.38,L),h,.32)
     patch('allure-white',0,h-.5,L,h,.4)
     if L>20:
      for x in np.arange(1,L-2,4.8):patch('allure-glass',x,.65,min(x+3.4,L-.4),3,.28)
    F.box('allure-white',(L/2,h+.18,0),(L,.36,.6))
   roof=surface.roof(r['id'],poly,h);B.planar('allure-roof',roof,h+.04)
   if tower:
    for x,z,w,d in [(1233,-3126,8,10),(1253,-3124,11,9),(1273,-3125,7,8)]:
     B.box('allure-white',(x,h+1.8,z),(w,3.6,d))
     B.box('allure-roof',(x,h+3.64,z),(w-.4,.08,d-.4))
 return dict(key=KEY,name='Allure and neighboring lower exteriors',center=[1220,0,-3130],bounds=[1100,-3210,1300,-3090],building='allure',structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
