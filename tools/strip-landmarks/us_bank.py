"""US Bank Center: mapped12/8/5/2-storey stepped volumes, Earth2022 reference."""
from common import *
from building_surfaces import BuildingSurfaces
from forum_shops import facade_frame
KEY='usBankCenter';IDS=['way/1459305985','way/1459305986','way/1459305987','way/1459305988','way/802738240','way/276426324','way/802738239']
class Access:
 def wall(self,a,b,lo,hi):return [[(a[0],lo,a[1]),(b[0],lo,b[1]),(b[0],hi,b[1])],[(a[0],lo,a[1]),(b[0],hi,b[1]),(a[0],hi,a[1])]]
def exterior(B):
 B.property=KEY+'-exterior';B.detail=0;B.source='us-bank-center'
 rs=[dict(id=i,shape=footprint(i),base=0,height=9 if i==IDS[5] else BYID[i]['height'],part=i in IDS[:4]) for i in IDS];surf=BuildingSurfaces(rs)
 for r in rs:
  p=r['shape'];h=r['height'];garage=r['id']==IDS[5];shade=r['id']==IDS[6]
  if shade:
   B.planar('ub-roof',p,3.5)
   for x,z in list(p.exterior.coords)[:-1]:B.box('ub-stone',(x,1.7,z),(.28,3.4,.28),True)
   continue
  ps=list(p.exterior.coords)
  for a,b in zip(ps,ps[1:]):
   line=LineString([a,b]);L=line.length
   if L<.05:continue
   F,_,nx,nz=facade_frame(B,a,b,p,.03);ux,uz=(b[0]-a[0])/L,(b[1]-a[1])/L;tris=surf.wall(r['id'],a,b,0,h,Access())
   region=unary_union([Polygon([(line.project(Point(v[0],v[2])),v[1]) for v in t]) for t in tris])
   def patch(mat,x0,y0,x1,y1,off=.16):
    if x1<=x0 or y1<=y0:return
    for q in parts(region.intersection(box(x0,y0,x1,y1))):
     for t in triangles(q):B.face(mat,[(a[0]+ux*x+nx*off,y,a[1]+uz*x+nz*off) for x,y in list(t.exterior.coords)[:-1]])
   patch('ub-stone',0,0,L,h)
   for y in np.arange(1.0,h-1,3.08):
    patch('ub-shadow' if garage else 'ub-glass',0,y,L,min(h,y+1.8),.21)
    patch('ub-trim',0,y+1.8,L,min(h,y+1.95),.32)
    if not garage:
     for x in np.arange(1,L,1.55):patch('ub-frame',x,y,min(L,x+.035),min(h,y+1.8),.25)
   patch('ub-trim',0,h-.3,L,h,.32)
   if garage:
    for x in np.arange(.3,L,7):patch('ub-stone',x,0,min(L,x+.6),h,.4)
   for t in tris:
    c=B.solids[B.property];n=len(c['vertices'])//3;c['vertices'].extend(v for pt in t for v in pt);c['indices'].extend([n,n+1,n+2])
   if r['id']==IDS[0] and nx>.9 and L>12:F.text('us bank',(L*.5,h-1,-.5),.85,'ub-letter')
  roof=surf.roof(r['id'],p,h);B.planar('ub-roof',roof,h+.03,True)
  # Low parapets only on visible roof boundaries, with no buried duplicate walls.
  for rr in parts(roof):
   ps=list(rr.exterior.coords)
   for a,b in zip(ps,ps[1:]):
    F,L,_,_=facade_frame(B,a,b,rr,.02);F.box('ub-stone',(L/2,h+.3,0),(L,.6,.22),True)
  if r['id']==IDS[0]:
   core=p.buffer(-9,join_style=2);B.shell(core,h+.03,h+3,'ub-stone')
   for x,z in list(core.exterior.coords)[:-1]:B.box('ub-service',(x,h+3.4,z),(1.8,.7,1.8))
 return dict(key=KEY,name='US Bank Center',center=[-90,0,-3240],bounds=[-192,-3330,-43,-3183],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],views={})
