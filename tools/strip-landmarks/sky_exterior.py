"""Sky Las Vegas: blue glass, projecting white bands and distinct low podium.
Lochsa Engineering 500ft/45 storeys; Earth2022. Podium16m photo-estimated.
"""
from common import *
from building_surfaces import BuildingSurfaces
from luxor_facades import Access
from forum_shops import facade_frame
KEY='skyExterior'
def records():
 return [dict(BYID['way/134068316'],shape=footprint('way/134068316'),height=152.4),dict(BYID['way/543641002'],shape=footprint('way/543641002'),height=16)]
def exterior(B):
 B.property=KEY+'-exterior';B.detail=0
 rs=records();surfaces=BuildingSurfaces(rs);access=Access(next(p for p in json.load(open('build/highrises/plan.json')) if p['key']=='sky'))
 for r in rs:
  p=r['shape'];h=r['height'];tower=h>100;B.source='tower/sky' if tower else 'podium/'+r['id']
  for poly in parts(p):
   ps=list(poly.exterior.coords)
   for a,b in zip(ps,ps[1:]):
    line=LineString([a,b]);L=line.length
    if L<.1:continue
    F,L,nx,nz=facade_frame(B,a,b,p,.1);ux,uz=(b[0]-a[0])/L,(b[1]-a[1])/L
    region=unary_union([Polygon([(line.project(Point(v[0],v[2])),v[1]) for v in tri]) for tri in surfaces.wall(r['id'],a,b,0,h,access)])
    def patch(mat,x0,y0,x1,y1,offset=.2):
     for q in parts(region.intersection(box(x0,y0,x1,y1))):
      for tri in triangles(q):B.face(mat,[(a[0]+ux*x+nx*offset,y,a[1]+uz*x+nz*offset) for x,y in list(tri.exterior.coords)[:-1]])
    patch('sky-glass' if tower else 'sky-white',0,0,L,h)
    if tower:
     for y in [3.8,7.2,10.6,14]:patch('sky-white',0,y,L,y+.28,.3)
     for x in np.arange(0,L,4):patch('sky-white',x,0,min(x+.2,L),16,.31)
     for y in np.arange(17,h-5,3.15):
      patch('sky-spandrel',0,y-.8,L,y,.24)
      # Floor edge projects from the glazing. Corners stay open rather than solid boxes.
      F.box('sky-white',(L/2,y,0),(L,.24,1.2))
      for x0,x1 in [(0,min(11,L/2)),(max(L-11,L/2),L)]:
       F.box('sky-balcony',( (x0+x1)/2,y+.66,-.85),(x1-x0,1.08,.055))
       F.box('sky-white',((x0+x1)/2,y+1.24,-.85),(x1-x0,.055,.09))
     for x in np.arange(0,L,1.9):patch('sky-mullion',x,16,min(x+.055,L),h-1,.29)
     if L>40:
      for x in [L*.35,L*.46,L*.57,L*.68]:patch('sky-white',x,16,x+.55,h-2,.38)
     patch('sky-white',0,h-1,L,h,.32)
     # Crown frames articulate the penthouse rather than a uniform flat roof.
     for x in np.arange(2,L-2,5.7):
      F.box('sky-white',(x,h+1.3,0),(.28,2.6,.65));F.box('sky-white',(x+2.3,h+2.6,0),(4.6,.25,.65))
    else:
     for y in [3.8,7.2,10.6,14]:
      patch('sky-shadow',.4,y-2.2,L-.4,y-.4,.24)
      patch('sky-white',0,y,L,y+.3,.35)
     for x in np.arange(0,L,6):patch('sky-white',x,0,min(x+.55,L),h,.35)
   roof=surfaces.roof(r['id'],poly,h);B.planar('sky-roof',roof,h+.04)
 return dict(key=KEY,name='Sky Las Vegas exterior',center=[1055,0,-2535],bounds=[995,-2580,1100,-2490],building='sky',structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
