"""HGV Flamingo, mapped plan and Earth 2022-11-09 facade/roof reference.
Stepped elevations are visual estimates within the mapped 51m envelope.
"""
from common import *
from building_surfaces import BuildingSurfaces
from forum_shops import facade_frame
KEY='hgvFlamingoExterior'
IDS=['way/115768623','way/115768620','way/115769438','way/115768621','way/115768622','way/115768624']
def records():
 rs=[]
 for i,(z0,z1,h) in enumerate([(-139,-123,40),(-123,-87,47),(-87,-63,51),(-63,-27,47),(-27,-11,40)]):
  rs.append(dict(id='hgv-flamingo-'+str(i),shape=footprint(IDS[0]).intersection(box(350,z0,385,z1)),height=h,base=0))
 for ident in IDS[1:]:rs.append(dict(BYID[ident],shape=footprint(ident),height=BYID[ident]['height'],base=0))
 return rs
class Access:
 def wall(self,a,b,lo,hi):
  line=LineString([a,b]);L=line.length;region=box(0,lo,L,hi)
  for p in [Point(380,-75),Point(339,-75),Point(359,-74)]:
   if line.distance(p)<1.5:
    x=line.project(p);region=region.difference(box(max(0,x-1.7),0,min(L,x+1.7),3.3))
  return [[[line.interpolate(x).x,y,line.interpolate(x).y] for x,y in list(t.exterior.coords)[:-1]] for p in parts(region) for t in triangles(p)]
def exterior(B):
 B.property=KEY+'-exterior';B.detail=0;rs=records();surf=BuildingSurfaces(rs);access=Access()
 for r in rs:
  p=r['shape'];h=r['height'];tall=h>30;B.source='hgv-flamingo/hotel'
  for poly in parts(p):
   ps=list(poly.exterior.coords)
   for a,b in zip(ps,ps[1:]):
    line=LineString([a,b]);L=line.length
    if L<.05:continue
    F,_,nx,nz=facade_frame(B,a,b,p,.08);ux,uz=(b[0]-a[0])/L,(b[1]-a[1])/L;tris=surf.wall(r['id'],a,b,0,h,access)
    region=unary_union([Polygon([(line.project(Point(v[0],v[2])),v[1]) for v in t]) for t in tris])
    def patch(mat,x0,y0,x1,y1,off=.18):
     if x1<=x0 or y1<=y0:return
     for q in parts(region.intersection(box(x0,y0,x1,y1))):
      for t in triangles(q):B.face(mat,[(a[0]+ux*x+nx*off,y,a[1]+uz*x+nz*off) for x,y in list(t.exterior.coords)[:-1]])
    patch('hf-white',0,0,L,h)
    if tall:
     n=max(1,round(L/3.2));w=L/n
     for j in range(n):
      x=j*w;midz=a[1]+uz*(x+w/2)
      accent=r['id'].startswith('hgv-flamingo') and (abs(midz+75)<14 or midz<-123 or midz>-27)
      if accent:patch('hf-burgundy',x,3.5,x+w,h-.5,.20)
      for y in np.arange(4,h-2,3.05):
       ww=min(1.25,w*.55);xx=x+(w-ww)/2
       patch('hf-reveal',xx-.08,y-.08,xx+ww+.08,y+1.65,.24)
       patch('hf-glass',xx,y,xx+ww,y+1.55,.27)
       patch('hf-frame',xx+ww*.49,y,xx+ww*.51+.025,y+1.55,.3)
       patch('hf-frame',xx,y+.7,xx+ww,y+.75,.3)
       patch('hf-white',xx-.12,y-.16,xx+ww+.12,y-.08,.38)
     # Continuous recessed glazing bays are a defining feature of the long slab.
     if abs(uz)>.8 and r['id'].startswith('hgv-flamingo'):
      for z0 in [-117,-77,-38]:
       d0=(z0-a[1])/uz;d1=(z0+4-a[1])/uz;x0,x1=sorted([d0,d1]);x0=max(0,x0);x1=min(L,x1)
       if x1>x0:
        patch('hf-glass',x0,3.3,x1,h-1,.42)
        for x in np.arange(x0,x1,.65):patch('hf-frame',x,3.3,x+.045,h-1,.48)
        for y in np.arange(4,h-1,1.5):patch('hf-frame',x0,y,x1,y+.045,.48)
        patch('hf-white',x0-.35,0,x0,h,.65);patch('hf-white',x1,0,x1+.35,h,.65)
    else:
     for x in np.arange(.5,L-1,2.7):patch('hf-glass',x,.5,min(x+2.35,L-.4),min(h-.7,4),.23);patch('hf-frame',x,.5,min(x+.08,L),min(h-.7,4),.32)
    patch('hf-cornice',0,h-.6,L,h,.45);patch('hf-stone',0,0,L,.45,.35)
    F.box('hf-white',(L/2,h+.12,0),(L,.24,.5))
    for t in tris:
     c=B.solids[B.property];n=len(c['vertices'])//3;c['vertices'].extend(v for pt in t for v in pt);c['indices'].extend([n,n+1,n+2])
   roof=surf.roof(r['id'],poly,h);B.planar('hf-roof',roof,h+.025,True)
   for x in np.arange(poly.bounds[0]+3,poly.bounds[2]-2,10):
    for z in np.arange(poly.bounds[1]+3,poly.bounds[3]-2,10):
     if roof.contains(box(x-1,z-1,x+1,z+1)):B.box('hf-service',(x,h+.65,z),(2,1.2,2));B.box('hf-vent',(x,h+1.27,z),(1.8,.05,1.8))
 # Private north courtyard pool (not the large Flamingo GO pool).
 B.source='courtyard';pool=box(326,-129,337,-112).buffer(2,quad_segs=8);spa=Point(343,-116).buffer(2.3,quad_segs=16)
 water=pool.union(spa);deck=box(314,-135,354,-99).difference(unary_union([r['shape'] for r in rs]));B.planar('hf-paving',deck.difference(water),.25,True);B.planar('water',water,.10);B.planar('hf-pool-tile',water,-1.1,True);B.planar('hf-stone',water.buffer(.45).difference(water),.29,True)
 for poly in parts(water):
  ps=list(poly.exterior.coords)
  for a,b in zip(ps,ps[1:]):B.face('hf-pool-tile',[(a[0],-1.1,a[1]),(b[0],-1.1,b[1]),(b[0],.1,b[1]),(a[0],.1,a[1])],True)
 for z in np.arange(-130,-106,3):
  for x in [319,348]:
   if deck.difference(water.buffer(1.5)).contains(box(x-1,z-.5,x+1,z+.5)):
    B.box('hf-frame',(x,.49,z),(1.9,.12,.7));B.box('hf-cushion',(x,.60,z),(1.85,.14,.66));B.box('hf-cushion',(x+.7,.86,z),(.45,.4,.66))
 # East entry canopy: open below, no obstruction across the mapped road.
 B.source='arrival';B.box('hf-cornice',(381.3,3.8,-75),(4.2,.22,6),True)
 for z in [-77.8,-72.2]:B.box('hf-white',(382.9,1.9,z),(.24,3.8,.24),True)
 return dict(key=KEY,name='HGV Flamingo exterior and private court',center=[355,0,-75],bounds=[310,-154,387,-1],building='hgv-flamingo',structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
