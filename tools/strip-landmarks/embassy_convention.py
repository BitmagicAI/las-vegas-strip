"""Embassy Suites Convention Center; mapped plan, Hilton and Earth facade evidence."""
from common import *
from building_surfaces import BuildingSurfaces
from forum_shops import facade_frame
KEY='embassyConvention';IDS=['way/331337786','way/1426502732']
class Closed:
 def wall(self,a,b,lo,hi):return [[(a[0],lo,a[1]),(b[0],lo,b[1]),(b[0],hi,b[1])],[(a[0],lo,a[1]),(b[0],hi,b[1]),(a[0],hi,a[1])]]
def exterior(B):
 B.property=KEY+'-exterior';B.source='embassy-convention';B.detail=0
 p=footprint(IDS[0]);cz=-886.65
 # Capsule atrium follows the long building axis; dimensions are photo estimates.
 atr=LineString([(1692,cz),(1753,cz)]).buffer(5.3,resolution=12)
 rs=[]
 def add(id,p,h,kind):
  if not p.is_empty:rs.append(dict(id=id,shape=p,base=0,height=h,kind=kind))
 add('atrium',atr,36,'glass')
 for n,(x0,x1,h) in enumerate([(1691,1699,24),(1699,1705,27),(1705,1711,30),(1711,1760,32)]):
  add('wing'+str(n),p.intersection(box(x0,-920,x1,-855)).difference(atr),h,'wing')
 entry=footprint(IDS[1]);add('entry',entry,7.2,'glass')
 surf=BuildingSurfaces(rs)
 for r in rs:
  h=r['height'];kind=r['kind']
  for pp in parts(r['shape']):
   ps=list(pp.exterior.coords)
   for a,b in zip(ps,ps[1:]):
    L=math.dist(a,b)
    if L<.02:continue
    F,_,nx,nz=facade_frame(B,a,b,pp,0);line=LineString([a,b]);ux,uz=(b[0]-a[0])/L,(b[1]-a[1])/L
    ts=surf.wall(r['id'],a,b,0,h,Closed());region=unary_union([Polygon([(line.project(Point(v[0],v[2])),v[1]) for v in t]) for t in ts])
    def patch(mat,x0,y0,x1,y1,off=.06):
     if x1<=x0 or y1<=y0:return
     for q in parts(region.intersection(box(x0,y0,x1,y1))):
      for t in triangles(q):B.face(mat,[(a[0]+ux*x+nx*off,y,a[1]+uz*x+nz*off) for x,y in list(t.exterior.coords)[:-1]])
    gray=kind=='wing' and (a[0]+b[0])/2<1711 and abs((a[1]+b[1])/2-cz)<11
    patch('es-glass' if kind=='glass' else 'es-gray' if gray else 'es-stone',0,0,L,h)
    if kind=='glass':
     for y in np.arange(.2,h,1.5):patch('es-bronze',0,y,L,min(h,y+.055),.13)
     for x in np.arange(0,L,1.45):patch('es-bronze',x,0,min(x+.055,L),h,.14)
     for y in np.arange(3,h,3):patch('es-bronze',0,y,L,min(y+.19,h),.2)
     patch('es-copper',0,h-.25,L,h,.24)
    else:
     for y in np.arange(6,h-1,3):
      if gray:
       if L>3:patch('es-glass',L*.5-.35,y,L*.5+.35,y+.7,.12)
      else:
       n=max(1,round(L/3.5));w=L/n
       for k in range(n):
        x=k*w+.55;patch('es-glass',x,y,min(x+w-1.1,L),y+1.65,.12)
        patch('es-sill',x-.07,y-.1,min(x+w-1.03,L),y,.17)
        # Balcony stacks on the long hotel wings, kept above the public ground.
        if (L>30 and k%4==2) or (nx<-.8 and L>6 and k==n//2):
         c=line.interpolate((k+.5)*w);cx,cz2=c.x+nx*.7,c.y+nz*.7
         w2=w-.5
         pts=[(cx+ux*u+nx*v,y-.09,cz2+uz*u+nz*v) for u,v in [(-w2/2,-.75),(w2/2,-.75),(w2/2,.75),(-w2/2,.75)]]
         balcony=Polygon([(q[0],q[2]) for q in pts])
         if any(other['id']!=r['id'] and other['height']>y-.2 and balcony.intersection(other['shape']).area>.05 for other in rs):continue
         B.upface('es-salmon',pts,True)
         for yy in [y+.1,y+.4,y+.7,y+1]:B.tube('es-bronze',(cx-ux*w2/2+nx*.68,yy,cz2-uz*w2/2+nz*.68),(cx+ux*w2/2+nx*.68,yy,cz2+uz*w2/2+nz*.68),.022,6)
         for u in [-w2/2,w2/2]:B.tube('es-bronze',(cx+ux*u+nx*.68,y-.09,cz2+uz*u+nz*.68),(cx+ux*u+nx*.68,y+1,cz2+uz*u+nz*.68),.026,6)
     patch('es-salmon',0,h-.35,L,h,.17)
     patch('es-gray',0,0,L,min(h,4.7),.1)
     if L>10:
      for x in np.arange(.7,L-1,2.8):patch('es-glass',x,.5,min(L,x+2.2),3.7,.16)
    for t in ts:B.face('es-shadow',t,True)
   roof=surf.roof(r['id'],pp,h);B.planar('es-roof',roof,h+.025,True)
   if kind=='glass':
    for a,b in zip(ps,ps[1:]):
     F,L,_,_=facade_frame(B,a,b,pp,0);F.box('es-copper',(L/2,h+.18,0),(L,.35,.22))
 # Roof plant follows the two roof levels.
 for x in np.arange(1714,1748,7):B.box('es-service',(x,32.6,-873),(3.2,1.2,3.8))
 for x in np.arange(1702,1748,8):B.box('es-service',(x,36.45,-886.65),(2.5,.85,2.7))
 F=Frame(B,1723,-892.25,0,y=0);F.text('EMBASSY SUITES',(0,37.1,0),1.5,'es-letter')
 F=Frame(B,1669,cz,math.pi/2,y=0);F.text('EMBASSY SUITES',(0,6.25,-.1),.6,'es-letter')
 return dict(key=KEY,name='Embassy Suites · Convention Center',center=[1720,0,-887],bounds=[1664,-916,1762,-861],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],views={})
