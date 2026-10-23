"""Turnberry Towers: mapped curved plans, separate front/rear skins and shared garage.
Earth 2022–2024 views. Floor/crown/podium dimensions are photo estimates.
"""
from common import *
from building_surfaces import BuildingSurfaces
from luxor_facades import Access
from forum_shops import facade_frame
KEY='turnberryTowersExterior'
def exterior(B):
 B.property=KEY+'-exterior';B.detail=0
 ids=['way/134679980','way/134918082','way/134679595']
 rs=[dict(BYID[i],shape=footprint(i),height=18 if i==ids[2] else 138) for i in ids]
 surfaces=BuildingSurfaces(rs);access=Access(next(p for p in json.load(open('build/highrises/plan.json')) if p['key']=='turnberry-towers'))
 for r in rs:
  p=r['shape'];h=r['height'];tower=h>100;B.source='tower/turnberry-towers' if tower else 'podium/'+r['id']
  for poly in parts(p):
   ps=list(poly.exterior.coords)
   for a,b in zip(ps,ps[1:]):
    line=LineString([a,b]);L=line.length
    if L<.1:continue
    F,L,nx,nz=facade_frame(B,a,b,p,.1);ux,uz=(b[0]-a[0])/L,(b[1]-a[1])/L
    region=unary_union([Polygon([(line.project(Point(v[0],v[2])),v[1]) for v in t]) for t in surfaces.wall(r['id'],a,b,0,h,access)])
    def patch(mat,x0,y0,x1,y1,offset=.2):
     for q in parts(region.intersection(box(x0,y0,x1,y1))):
      for t in triangles(q):B.face(mat,[(a[0]+ux*x+nx*offset,y,a[1]+uz*x+nz*offset) for x,y in list(t.exterior.coords)[:-1]])
    if tower:
     rear=nz<-.15;solid=rear and L>7
     patch('tt-white' if solid else 'tt-glass',0,0,L,h)
     if not solid:
      for y in np.arange(4.8,h-3,3.0):
       patch('tt-spandrel',0,y-.65,L,y,.24)
       F.box('tt-white',(L/2,y,0),(L,.22,.65))
       # Balcony bays alternate with glazing; real projecting slabs and guard lines.
       if (rear and L<7) or (not rear and L>7):
        F.box('tt-white',(L/2,y,-.6),(L,.20,1.7))
        F.box('tt-balcony-glass',(L/2,y+.62,-1.35),(L,1.0,.055))
        F.box('tt-frame',(L/2,y+1.14,-1.35),(L,.055,.075))
      for x in np.arange(.4,L,1.6):patch('tt-frame',x,0,min(x+.065,L),h,.3)
     if not rear and L>10:
      for x in [L*.30,L*.66]:patch('tt-white',x,0,min(x+.72,L),h,.48)
     for x in [0,max(0,L-.28)]:patch('tt-white',x,0,min(x+.28,L),h,.4)
     patch('tt-white',0,h-.7,L,h,.3)
    else:
     patch('tt-white',0,0,L,h)
     for y in np.arange(3,h,3):
      patch('tt-shadow',.4,y-1.8,max(.4,L-.4),y-.3,.25)
      patch('tt-white',0,y,L,y+.3,.35)
     for x in np.arange(0,L,6):patch('tt-white',x,0,min(x+.5,L),h,.4)
    F.box('tt-white',(L/2,h+.22,0),(L,.44,.6))
   B.planar('tt-roof',surfaces.roof(r['id'],poly,h),h+.04,not tower)
   if tower:
    # Articulated white rooftop service pavilions follow the individual bent plan.
    inner=poly.buffer(-4)
    x0,z0,x1,z1=inner.bounds
    inner=unary_union([inner.intersection(box(x0+i*(x1-x0)/3+1,z0,x0+(i+1)*(x1-x0)/3-1,z1)) for i in range(3)])
    for q in parts(inner):
     B.shell(q,h,h+3.4,'tt-white',roof=False,solid=False)
     B.planar('tt-roof',q,h+3.4)
   else:
    for a,b in zip(ps,ps[1:]):
     for t in surfaces.wall(r['id'],a,b,0,h,access):B.face('tt-white',t,True)
    # Continuous rooftop parking shade rows visible in the aerial reference.
    for z in [-2856,-2837,-2818]:
     for x in np.arange(1722,1865,7):
      if not poly.contains(box(x-3,z-3,x+3,z+3)):continue
      y=h+2.6
      for dx in [-3,3]:B.box('tt-frame',(x+dx,h+1.3,z),( .09,2.6,.09))
      for s in [-1,1]:B.upface('tt-shade',[(x-3,y,z),(x+3,y,z),(x+3,y-.5,z+s*3),(x-3,y-.5,z+s*3)])
 # South leisure courts are separate from the central arrival drive.
 B.source='leisure-courts'
 for cx,cz in [(1741,-2734),(1854,-2734)]:
  water=unary_union([Point(cx-4,cz).buffer(6,resolution=16),Point(cx+4,cz+1).buffer(7,resolution=16),Point(cx+1,cz-6).buffer(5,resolution=16)])
  deck=water.buffer(5)
  B.planar('hgv-paving',deck.difference(water),.3,True)
  B.planar('hgv-cream',water.buffer(.45).difference(water),.32)
  B.planar('hgv_pool',water,.12)
  B.planar('hgv-pool-tile',water,-1.1,True)
  for q in parts(water):
   ps=list(q.exterior.coords)
   for a,b in zip(ps,ps[1:]):B.face('hgv-pool-tile',[(a[0],-1.1,a[1]),(b[0],-1.1,b[1]),(b[0],.3,b[1]),(a[0],.3,a[1])],True)
 # Two measured-size courts at the west edge; enclosing mesh and planting still pending.
 for z in [-2815,-2742]:
  x=1687
  B.planar('tt-court',box(x-9,z-18,x+9,z+18),.28,True)
  for dx in [-5.49,5.49]:B.box('tt-white',(x+dx,.295,z),(.05,.025,23.77))
  for dz in [-11.885,11.885,-6.4,6.4]:B.box('tt-white',(x,.295,z+dz),(10.98,.025,.05))
  B.box('tt-white',(x,.295,z),(.05,.025,12.8))
 return dict(key=KEY,name='Turnberry Towers exterior and garage',center=[1795,0,-2790],bounds=[1670,-2870,1900,-2680],building='turnberry-towers',structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
