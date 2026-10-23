"""Gold Coast: mapped footprint, Earth2022 roof/site and2024 south arcade.
Casino9m/garage15m/pool dimensions are estimated; hotel mapped35m retained.
"""
from common import *
from building_surfaces import BuildingSurfaces
from forum_shops import facade_frame,arch_panel
KEY='goldCoastExterior';IDS=['way/27523549','way/135296658','way/27523550','way/27523551']
class Access:
 def wall(self,a,b,lo,hi):
  L=LineString([a,b]);region=box(0,lo,L.length,hi)
  for p in [Point(-1780,-25.6),Point(-1650,-81),Point(-1860,-106)]:
   if L.distance(p)<4:
    t=L.project(p);region=region.difference(box(t-2.5,0,t+2.5,4))
  return [[[L.interpolate(x).x,y,L.interpolate(x).y] for x,y in list(t.exterior.coords)[:-1]] for p in parts(region) for t in triangles(p)]
def exterior(B):
 B.property=KEY+'-exterior';B.detail=0;rs=[dict(BYID[i],shape=footprint(i),height=h) for i,h in zip(IDS[:3],[9,35,15])];surf=BuildingSurfaces(rs)
 for r in rs:
  p=r['shape'];h=r['height'];tower=h==35;garage=h==15;B.source='gold-coast/'+('hotel' if tower else 'garage' if garage else 'casino')
  for poly in parts(p):
   ps=list(poly.exterior.coords)
   for a,b in zip(ps,ps[1:]):
    L=math.dist(a,b)
    if L<.1:continue
    F,_,nx,nz=facade_frame(B,a,b,p,.12);ux,uz=(b[0]-a[0])/L,(b[1]-a[1])/L;line=LineString([a,b]);tris=surf.wall(r['id'],a,b,0,h,Access())
    region=unary_union([Polygon([(line.project(Point(v[0],v[2])),v[1]) for v in t]) for t in tris])
    def patch(mat,x0,y0,x1,y1,off=.16):
     if x1<=x0 or y1<=y0:return
     for q in parts(region.intersection(box(x0,y0,x1,y1))):
      for t in triangles(q):B.face(mat,[(a[0]+ux*x+nx*off,y,a[1]+uz*x+nz*off) for x,y in list(t.exterior.coords)[:-1]])
    patch('gco-white',0,0,L,h)
    if tower:
     for x in np.arange(1.5,L-1,3.8):
      for y in np.arange(4,33,3):
       patch('gco-reveal',x-.12,y-.12,min(x+1.82,L),y+1.8,.20);patch('gco-window',x,y,min(x+1.7,L),y+1.65,.22)
       patch('gco-frame',x+.82,y,min(x+.88,L),y+1.65,.27);patch('gco-stone',x-.2,y-.22,min(x+1.9,L),y-.10,.38)
     patch('gco-stone',0,0,L,3,.24)
     # Sloped terracotta perimeter, enclosing a flat white roof.
     B.face('gco-tile',[F.p(0,h,0),F.p(L,h,0),F.p(L,h+1.1,2),F.p(0,h+1.1,2)])
    elif garage:
     for y in np.arange(3,15,3):patch('gco-reveal',.2,y-1.8,max(.2,L-.2),y-.3,.24)
     for x in np.arange(.5,L,7):patch('gco-white',x,0,min(x+.6,L),h,.4)
    else:
     patch('gco-stone',0,0,L,1.1,.24)
     # South and east public elevations: arcaded walkway and red tiled roof.
     public=nz>.5 or nx>.5
     if public and L>7:
      for x in np.arange(2.7,L-2,5.4):
       arch_panel(F,x,0,-.28,4.0,4.5,'gco-window');F.arch(x,-.45,4.2,4.65,'gco-white',.12)
       F.box('gco-stone',(x-2.5,1.9,-.1),(.5,3.8,.75))
       F.box('gco-frame',(x,2,-.4),(.08,3.5,.08))
       F.box('gco-window',(x,6.8,-.4),(3.8,1,.08));F.box('gco-stone',(x,6.1,-.1),(4,.25,.35))
      B.face('gco-tile',[F.p(0,h-.5,-.8),F.p(L,h-.5,-.8),F.p(L,h+1.0,2.2),F.p(0,h+1.0,2.2)])
      F.box('gco-white',(L/2,h-.6,-.8),(L,.22,.4))
     else:
      for x in np.arange(2,L-2,6):patch('gco-service',x,1,min(x+3,L-.4),3.7,.25)
    F.box('gco-white',(L/2,h+.1,0),(L,.2,.4))
    for t in tris:
     c=B.solids[B.property];n=len(c['vertices'])//3;c['vertices'].extend(v for pt in t for v in pt);c['indices'].extend([n,n+1,n+2])
   roof=surf.roof(r['id'],poly,h);B.planar('gco-roof',roof,h+.02,True)
   for x in np.arange(poly.bounds[0]+7,poly.bounds[2]-5,24):
    for z in np.arange(poly.bounds[1]+7,poly.bounds[3]-5,24):
     if roof.contains(box(x-2,z-1.5,x+2,z+1.5)):B.box('gco-service',(x,h+.65,z),(4,1.2,3));B.box('gco-reveal',(x,h+1.28,z),(3.6,.05,2.6))
 # Street entrance pediments and projecting piers, respecting existing door gap.
 B.source='gold-coast/arrival'
 for x in [-1898,-1857,-1780,-1725]:
  F=Frame(B,x,-24.8,math.pi,y=0);F.box('gco-white',(0,10.4,1),(8,3,4));F.box('gco-window',(0,10.4,-1.05),(3,1.8,.08))
  B.face('gco-tile',[F.p(-4.6,11.9,-1.5),F.p(0,13.7,-1.5),F.p(0,13.7,3.4),F.p(-4.6,11.9,3.4)])
  B.face('gco-tile',[F.p(0,13.7,-1.5),F.p(4.6,11.9,-1.5),F.p(4.6,11.9,3.4),F.p(0,13.7,3.4)])
  B.face('gco-white',[F.p(-4.6,11.9,-1.52),F.p(4.6,11.9,-1.52),F.p(0,13.7,-1.52)])
 # Covered south motor court uses its mapped outline, open beneath the roof.
 B.source='gold-coast/motor-court';canopy=footprint(IDS[3]);B.planar('gco-roof',canopy,5.3,True)
 for poly in parts(canopy):
  ps=list(poly.exterior.coords)
  for a,b in zip(ps,ps[1:]):
   if math.dist(a,b)<.1:continue
   F,L,_,_=facade_frame(B,a,b,poly,.02);F.box('gco-white',(L/2,5.2,0),(L,.35,.4))
   for x in np.arange(1,L,8):F.box('gco-stone',(x,2.55,0),(.4,5.1,.4),True)
 # Pool west of hotel, separate from the casino roof.
 B.source='gold-coast/pool';pool=box(-1885,-123,-1870,-113).buffer(2,quad_segs=12);deck=box(-1904,-132,-1852,-106).difference(unary_union([r['shape'] for r in rs]))
 water=pool.intersection(deck.buffer(-1));B.planar('gco-paving',deck.difference(water),.25,True);B.planar('water',water,.1);B.planar('gco-stone',water.buffer(.5).difference(water),.3,True)
 for p in parts(water):
  ps=list(p.exterior.coords)
  for a,b in zip(ps,ps[1:]):B.face('gco-pooltile',[(a[0],-1.2,a[1]),(b[0],-1.2,b[1]),(b[0],.1,b[1]),(a[0],.1,a[1])],True)
 B.planar('gco-pooltile',water,-1.2,True)
 return dict(key=KEY,name='Gold Coast hotel and Spanish casino exterior',center=[-1770,0,-90],bounds=[-1940,-250,-1550,0],building='gold-coast',structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
