"""Turnberry Place's four terrace towers and Stirling Club, Earth reference fit."""
from common import *
from building_surfaces import BuildingSurfaces
from luxor_facades import Access
from forum_shops import facade_frame
KEY='turnberryPlaceExterior'
def exterior(B):
 B.property=KEY+'-exterior';B.detail=0
 ids=['way/134677416','way/134677417','way/134677425','way/134677429','way/134678078','way/134678384','way/1265036420']
 rs=[dict(BYID[i],shape=footprint(i),height=145 if i in ids[:4] else 8) for i in ids]
 surf=BuildingSurfaces(rs);access=Access(next(p for p in json.load(open('build/highrises/plan.json')) if p['key']=='turnberry-place'))
 for r in rs:
  p=r['shape'];h=r['height'];tower=h>100;B.source='tower/turnberry-place' if tower else 'podium/'+r['id']
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
    patch('tp-white' if tower else 'tp-stone',0,0,L,h)
    if tower:patch('tp-glass',.7,0,max(.7,L-.7),h-1,.23)
    if tower:
     for y in np.arange(4.7,h-4,3.55):
      patch('tp-spandrel',0,y-.45,L,y,.24)
      patch('tp-white',0,y,L,y+.15,.3)
      # Broad corner terraces, with curved outside edges and distinct white soffits.
      bays=[(0,min(7,L/3)),(max(L-7,L*2/3),L)] if L>15 else [(0,L)]
      for x0,x1 in bays:
       pts=[(x0,y,-.2),(x1,y,-.2)]+[(x0+(x1-x0)*t,y,-1.3-.65*math.sin(math.pi*t)) for t in np.linspace(1,0,9)]
       B.upface('tp-white',[F.p(*v) for v in pts])
       for aa,bb in zip(pts[2:],pts[3:]):
        F.box('tp-white',((aa[0]+bb[0])/2,y-.1,(aa[2]+bb[2])/2),(max(.1,abs(aa[0]-bb[0])),.2,.13))
        B.face('tp-balcony-glass',[F.p(aa[0],y+.1,aa[2]),F.p(bb[0],y+.1,bb[2]),F.p(bb[0],y+1.1,bb[2]),F.p(aa[0],y+1.1,aa[2])])
        F.tube('tp-frame',(aa[0],y+1.14,aa[2]),(bb[0],y+1.14,bb[2]),.035,4)
     for x in np.arange(.9,L,1.75):patch('tp-frame',x,0,min(x+.055,L),h,.28)
     for x in [0,L*.25,L*.75,max(0,L-1.5)]:patch('tp-white',x,0,min(x+1.5,L),h,.45)
     if L<28:patch('tp-white',L*.36,0,L*.64,h,.48)
     patch('tp-white',0,h-1,L,h,.35)
    else:
     for x in np.arange(1,L-1,4.4):
      patch('tp-glass',x,.5,min(x+2.8,L-.3),5.5,.26)
      for xx in [x,x+2.8]:patch('tp-stone',xx-.16,0,min(xx+.16,L),6,.34)
     patch('tp-white',0,6,L,6.3,.34)
   B.planar('tp-roof',surf.roof(r['id'],poly,h),h+.04)
   if tower:
    # A shallow barrel crown follows the long diagonal tower axis.
    rect=list(poly.minimum_rotated_rectangle.exterior.coords);a,b=max(zip(rect,rect[1:]),key=lambda ab:LineString(ab).length)
    ux,uz=(b[0]-a[0]),(b[1]-a[1]);length=math.hypot(ux,uz);ux/=length;uz/=length
    nx,nz=-uz,ux;c=poly.centroid;depth=poly.area/length
    def pt(s,t):return (c.x+ux*s+nx*t,h+3.2*math.sqrt(max(0,1-(t/(depth/2))**2)),c.y+uz*s+nz*t)
    for t,tt in zip(np.linspace(-depth/2,depth/2,21),np.linspace(-depth/2,depth/2,21)[1:]):
     for lo,hi in [(-length/2,-7),(7,length/2)]:B.upface('tp-patina',[pt(lo,t),pt(hi,t),pt(hi,tt),pt(lo,tt)])
    B.upface('tp-white',[pt(-7,-depth/2),pt(7,-depth/2),pt(7,depth/2),pt(-7,depth/2)])
    for side in [-1,1]:
     for t,tt in zip(np.linspace(-depth/2,depth/2,21),np.linspace(-depth/2,depth/2,21)[1:]):
      v=pt(side*length/2,t);w=pt(side*length/2,tt);B.face('tp-white',[(v[0],h,v[2]),(w[0],h,w[2]),w,v])
   else:
    # Clubhouse hipped tile roof retains mapped irregular footprint.
    inner=poly.buffer(-3)
    for a,b in zip(ps,ps[1:]):
     aa=inner.exterior.interpolate(inner.exterior.project(Point(a))) if inner.geom_type=='Polygon' else poly.centroid
     bb=inner.exterior.interpolate(inner.exterior.project(Point(b))) if inner.geom_type=='Polygon' else poly.centroid
     B.upface('tp-tile',[(a[0],h,a[1]),(b[0],h,b[1]),(bb.x,h+2.6,bb.y),(aa.x,h+2.6,aa.y)])
    B.planar('tp-tile',inner,h+2.6)
 return dict(key=KEY,name='Turnberry Place towers and clubhouse',center=[1515,0,-2395],bounds=[1420,-2520,1610,-2270],building='turnberry-place',structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
