"""OYO towers and casino: mapped footprints, official gallery and Earth reference."""
from common import *
from building_surfaces import BuildingSurfaces
from forum_shops import facade_frame
from platinum import Closed
KEY='oyoExterior';IDS=['way/118361200','way/118376294','way/118376296','way/27858541','way/118354226','way/118353929']
def exterior(B):
 B.property=KEY+'-exterior';B.source='oyo';B.detail=0
 rs=[dict(id=i,shape=footprint(i),base=0,height=h) for i,h in zip(IDS,[6,32,59,20,5])];surf=BuildingSurfaces(rs)
 for r in rs:
  p,h=r['shape'],r['height'];tower=h in [32,59];garage=h==20
  for poly in parts(p):
   ps=list(poly.exterior.coords)
   if garage:
    # Open decks, independent floor slabs and piers: no opaque garage box.
    for y in np.arange(.2,20.1,3.3):B.shell(poly,y-.22,y,'oy-white',roof=False);B.planar('oy-roof',poly,y,True)
   for a,b in zip(ps,ps[1:]):
    line=LineString([a,b]);L=line.length
    if L<.15:continue
    F,_,nx,nz=facade_frame(B,a,b,poly,0);ux,uz=(b[0]-a[0])/L,(b[1]-a[1])/L
    ts=surf.wall(r['id'],a,b,0,h,Closed());region=unary_union([Polygon([(line.project(Point(v[0],v[2])),v[1]) for v in t]) for t in ts])
    def patch(mat,x0,y0,x1,y1,off=.08):
     if x1<=x0 or y1<=y0:return
     for q in parts(region.intersection(box(x0,y0,x1,y1))):
      for t in triangles(q):B.face(mat,[(a[0]+ux*x+nx*off,y,a[1]+uz*x+nz*off) for x,y in list(t.exterior.coords)[:-1]])
    if not garage:
     for t in ts:B.face('oy-white',t,True)
    if tower:
     if L>28:
      n=round(L/3.8);w=L/n
      for k in range(n):
       x=(k+.5)*w
       patch('oy-blue',x-w*.41,6,x+w*.41,h-3,.1)
       for y in np.arange(7,h-3,2.85):
        patch('oy-glass',x-w*.30,y,x+w*.30,y+2.05,.17)
        patch('oy-frame',x-.04,y,x+.04,y+2.05,.23)
        patch('oy-sill',x-w*.32,y-.12,x+w*.32,y,.23)
      for y in [6,h-3]:patch('oy-sill',0,y,L,y+.25,.26)
      if h==59:F.text('OYO',(L/2,h+1.5,-1.3),2.8,'oy-red')
     elif L>12:
      # Architectural palm silhouette mural on the otherwise opaque tower ends.
      x=L*.5;lo=max(6,h*.23);top=h-6;off=.13
      def mural(points):
       B.face('oy-mural',[(a[0]+ux*xx+nx*off,yy,a[1]+uz*xx+nz*off) for xx,yy in points])
      mural([(x-.55,lo),(x+.45,lo),(x+.75,top),(x+.20,top)])
      for side in [-1,1]:
       for k in range(6):
        reach=L*(.22+.025*k);drop=1.0+k*.95
        upper=[];lower=[]
        for t in np.linspace(0,1,12):
         xx=x+side*reach*t;yy=top+(2.9-k*.3)*math.sin(t*math.pi)-drop*t*t;width=.42*math.sin(t*math.pi)
         upper.append((xx,yy+width));lower.append((xx,yy-width))
        for j in range(11):mural([upper[j],upper[j+1],lower[j+1],lower[j]])
      for y in np.arange(8,h-5,6):patch('oy-glass',1,y,1.5,y+1.1,.2)
     F.box('oy-sill',(L/2,h-2,-.38),(L,.18,.6))
    elif garage:
     for x in np.arange(.4,L,6):F.box('oy-white',(x,10,-.1),(.55,20,.65),True)
     for y in np.arange(.2,20,3.3):F.box('oy-white',(L/2,y+.6,-.08),(L,1.15,.3),True)
     if L>50:
      F.box('oy-blue',(L*.53,11,-.45),(19,9,.15));F.text('OYO',(L*.53,12,-.58),3.2,'oy-letter');F.text('HOTEL & CASINO',(L*.53,9,-.58),.65,'oy-letter')
    else:
     for x in np.arange(.6,L-1,2.5):
      patch('oy-glass',x,.5,min(x+2,L),4.7,.16)
      patch('oy-frame',x+.95,.5,min(x+1.02,L),4.7,.23)
     patch('oy-blue',0,4.9,L,5.45,.19)
     for x in np.arange(.1,L,7):F.box('oy-white',(x,2.6,-.3),(.4,5.2,.6))
    if not tower:F.box('oy-sill',(L/2,h+.2,0),(L,.4,.5))
   if not garage:B.planar('oy-roof',surf.roof(r['id'],poly,h),h+.025,True)
   if tower:
    # Continuous offset rings close every corner of the mansard.
    for d0,d1,y0,y1 in [(-.4,.1,h-2,h-1.4),(.1,1.05,h-1.4,h+1.5),(1.05,1.6,h+1.5,h+2)]:
     outer=poly.buffer(-d0,join_style=2);inner=poly.buffer(-d1,join_style=2)
     for q0 in parts(outer.difference(inner)):
      for tri in triangles(q0):
       pts=[]
       for xx,zz in list(tri.exterior.coords)[:-1]:
        pt=Point(xx,zz);t=pt.distance(outer.boundary)/(pt.distance(outer.boundary)+pt.distance(inner.boundary)+1e-9)
        pts.append((xx,y0+t*(y1-y0),zz))
       B.upface('oy-mansard',pts,True)
    q=poly.buffer(-2)
    B.planar('oy-roof',q,h+1.55,True)
    for pp in parts(q):
     pt=pp.representative_point();B.box('oy-service',(pt.x,h+2,pt.y),(4,1.5,4))
   if h==6:
    for x in np.arange(465,521,11):
     for z in np.arange(1753,1807,13):
      if poly.contains(box(x-1.8,z-1.8,x+1.8,z+1.8)):B.box('oy-service',(x,6.8,z),(3,1.5,3))
 # Mapped arrival canopy replaces its old solid box with a clear underside.
 canopy=footprint(IDS[5]);B.shell(canopy,4.6,5.05,'oy-blue',roof=False);B.planar('oy-roof',canopy,5.05,True)
 for x,z in [(466.3,1713.2),(484.7,1713.2),(466.3,1737.8),(484.7,1737.8)]:B.box('oy-white',(x,2.3,z),(.65,4.6,.65),True)
 F=Frame(B,475.5,1712,y=0);F.text('OYO HOTEL & CASINO',(0,5.2,-.2),.62,'oy-letter')
 F=Frame(B,510,1745.6,y=0);F.text('HOOTERS',(0,5.25,-.4),1.05,'oy-orange')
 # Pool enclosed by the L-shaped hotel; size is estimated from aerial view.
 pool=scale(Point(496,1861).buffer(1,28),11,15,origin=(496,1861));deck=pool.buffer(3)
 B.planar('oy-paving',deck.difference(pool),.24,True);B.planar('oy-sill',pool.buffer(.4).difference(pool),.34,True);B.planar('oyo_pool',pool,.17);B.planar('oy-blue',pool,-1.1,True)
 ps=list(pool.exterior.coords)
 for a,b in zip(ps,ps[1:]):B.face('oy-blue',[(a[0],-1.1,a[1]),(b[0],-1.1,b[1]),(b[0],.34,b[1]),(a[0],.34,a[1])],True)
 return dict(key=KEY,name='OYO Hotel and Casino exterior',center=[480,0,1810],bounds=[420,1730,542,1894],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],views={})
