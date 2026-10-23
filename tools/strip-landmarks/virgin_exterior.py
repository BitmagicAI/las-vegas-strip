"""Virgin Hotels: three actual towers, not the mapped 182m/50-storey error.
Earth March2024 and official2025map. Opal61m/Ruby48m CVU; Canyon40m estimated.
"""
from common import *
from building_surfaces import BuildingSurfaces
from forum_shops import facade_frame
KEY='virginExterior';IDS=['way/133757428','way/133757429','way/133758151','way/133757427','way/133757908','way/133757524','way/133758066','way/1509415874']
def records():
 parent=footprint(IDS[1]);ruby=parent.intersection(box(1508,737,1643,764));opal=footprint(IDS[2]).intersection(box(1580,570,1674,605))
 return [dict(id=IDS[0],shape=footprint(IDS[0]),height=40,style='canyon'),dict(id='virgin-ruby',shape=ruby,height=48,style='glass'),dict(id='virgin-opal',shape=opal,height=61,style='glass'),dict(id=IDS[1],shape=parent,height=9,style='podium'),dict(id=IDS[2],shape=footprint(IDS[2]),height=9,style='podium')]+[dict(id=i,shape=footprint(i),height=24 if i in IDS[3:5] else 5,style='garage' if i in IDS[3:5] else 'podium') for i in IDS[3:]]
class Access:
 def wall(self,a,b,lo,hi):
  line=LineString([a,b]);L=line.length;region=box(0,lo,L,hi)
  for p in [Point(1752,782),Point(1649,860),Point(1637,726),Point(1682,660)]:
   if line.distance(p)<5:
    x=line.project(p);region=region.difference(box(max(0,x-3),0,min(L,x+3),4.3))
  return [[[line.interpolate(x).x,y,line.interpolate(x).y] for x,y in list(t.exterior.coords)[:-1]] for p in parts(region) for t in triangles(p)]
def exterior(B):
 B.property=KEY+'-exterior';B.detail=0;rs=records();
 for r in rs:r['base']=0
 surf=BuildingSurfaces(rs);access=Access()
 for r in rs:
  p=r['shape'];h=r['height'];style=r['style'];B.source='virgin/'+('tower' if style in ['glass','canyon'] else style)
  for poly in parts(p):
   ps=list(poly.exterior.coords)
   for a,b in zip(ps,ps[1:]):
    line=LineString([a,b]);L=line.length
    if L<.08:continue
    F,_,nx,nz=facade_frame(B,a,b,p,.06);ux,uz=(b[0]-a[0])/L,(b[1]-a[1])/L;tris=surf.wall(r['id'],a,b,0,h,access)
    region=unary_union([Polygon([(line.project(Point(v[0],v[2])),v[1]) for v in t]) for t in tris])
    def patch(mat,x0,y0,x1,y1,off=.15):
     if x1<=x0 or y1<=y0:return
     for q in parts(region.intersection(box(x0,y0,x1,y1))):
      for t in triangles(q):B.face(mat,[(a[0]+ux*x+nx*off,y,a[1]+uz*x+nz*off) for x,y in list(t.exterior.coords)[:-1]])
    patch('vh-blueglass' if style=='glass' else 'vh-white',0,0,L,h)
    if style=='glass':
     for y in np.arange(4,h-1,3.12):
      patch('vh-spandrel',0,y,L,y+.7,.18);patch('vh-metal',0,y+.7,L,y+.82,.25)
      if int(y/3.12)%3==0:patch('vh-white',0,y,L,y+.20,.31)
     for x in np.arange(.1,L,1.45):patch('vh-metal',x,3.5,min(L,x+.045),h-.9,.26)
     patch('vh-white',0,h-1.1,L,h,.36)
     if L<25:patch('vh-white',L*.37,0,L*.63,h,.38)
    elif style=='canyon':
     for y in np.arange(4,h-1,3.08):
      patch('vh-grayglass',.25,y,max(.25,L-.25),min(y+1.9,h-.6),.21)
      patch('vh-white',0,y+1.9,L,min(y+2.5,h),.42)
      for x in np.arange(1,L,2.6):patch('vh-white',x,y,min(x+.3,L),min(y+1.9,h),.4)
     patch('vh-stone',0,0,L,3.2,.31)
    elif style=='garage':
     for y in np.arange(3,h,3.15):patch('vh-shadow',.2,y-1.9,max(.2,L-.2),y-.35,.22);patch('vh-white',0,y,L,y+.26,.33)
     for x in np.arange(0,L,7):patch('vh-white',x,0,min(L,x+.5),h,.38)
     if L>30:patch('vh-white',L*.45,0,L*.55,h,.4)
    else:
     patch('vh-stone',0,0,L,min(3,h),.23)
     for x in np.arange(.5,L-1,4):patch('vh-grayglass',x,.6,min(x+3.3,L-.3),min(h-1,4.8),.31);patch('vh-metal',x,.5,min(x+.1,L),min(h-1,4.9),.4)
     patch('vh-white',0,h-.8,L,h,.36)
    F.box('vh-white',(L/2,h+.12,0),(L,.24,.45))
    for t in tris:
     c=B.solids[B.property];n=len(c['vertices'])//3;c['vertices'].extend(v for pt in t for v in pt);c['indices'].extend([n,n+1,n+2])
   roof=surf.roof(r['id'],poly,h);B.planar('vh-roof',roof,h+.025,True)
   for x in np.arange(poly.bounds[0]+5,poly.bounds[2]-4,29):
    for z in np.arange(poly.bounds[1]+5,poly.bounds[3]-4,29):
     if roof.contains(box(x-1.5,z-1,x+1.5,z+1)):B.box('vh-service',(x,h+.6,z),(3,1.1,2));B.box('vh-shadow',(x,h+1.18,z),(2.7,.05,1.7))
 # Curving courtyard boundaries inferred from the official map and Earth. These
 # are local architectural surfaces; existing road and sidewalk geometry is retained.
 B.source='courtyard';court=Polygon([(1530,715),(1575,605),(1677,611),(1700,650),(1690,697),(1640,732),(1540,732)]).buffer(0)
 court=court.difference(unary_union([r['shape'] for r in rs]));lawn=scale(Point(1660,643).buffer(19,quad_segs=16),1,.85)
 pool=unary_union([scale(Point(1580,696).buffer(16,quad_segs=16),1.15,.72),scale(Point(1599,708).buffer(12,quad_segs=16),1,.8)]).buffer(3).buffer(-3)
 beach=LineString([(1662,710),(1675,701),(1682,689)]).buffer(7,quad_segs=12)
 dish=Point(1598,625).buffer(7,quad_segs=16);water=unary_union([pool,beach,dish]).intersection(court.buffer(-2))
 B.planar('vh-paving',court.difference(water).difference(lawn),.24,True);B.planar('vh-lawn',court.intersection(lawn),.27,True);B.planar('water',water,.1);B.planar('vh-pool-tile',water,-1.2,True);B.planar('vh-white',water.buffer(.5).difference(water),.29,True)
 for p in parts(water):
  ps=list(p.exterior.coords)
  for a,b in zip(ps,ps[1:]):B.face('vh-pool-tile',[(a[0],-1.2,a[1]),(b[0],-1.2,b[1]),(b[0],.1,b[1]),(a[0],.1,a[1])],True)
 for x in np.arange(1550,1690,4):
  for z in np.arange(615,730,4):
   if court.intersection(water.buffer(5)).difference(water.buffer(2)).difference(lawn.buffer(2)).contains(box(x-.5,z-1,x+.5,z+1)):
    B.box('vh-service',(x,.48,z),(.7,.15,1.9));B.box('vh-cushion',(x,.60,z),(.66,.16,1.85))
 # Low glazed pool guards and open-sided shade frames define the deck edges.
 for edge in parts(water.buffer(1.4)):
  ring=LineString(edge.exterior.coords)
  for d in np.arange(0,ring.length,2.0):
   a=ring.interpolate(d);b=ring.interpolate(min(d+1.8,ring.length))
   # Leave access openings on the west side of each pool.
   if a.x<edge.centroid.x and abs(a.y-edge.centroid.y)<2.5:continue
   if court.contains(a.buffer(.3)):
    B.face('vh-grayglass',[(a.x,.35,a.y),(b.x,.35,b.y),(b.x,1.3,b.y),(a.x,1.3,a.y)])
    B.box('vh-metal',(a.x,.82,a.y),(.045,1.15,.045))
 for x,z in [(1560,675),(1563,686),(1628,716),(1620,620),(1640,618)]:
  if court.contains(box(x-2,z-2,x+2,z+2)) and water.buffer(1).disjoint(box(x-2,z-2,x+2,z+2)):
   for xx in [-1.9,1.9]:
    for zz in [-1.9,1.9]:B.box('vh-stone',(x+xx,1.7,z+zz),(.16,2.9,.16))
   for xx in np.arange(-2,2.1,.4):B.box('vh-white',(x+xx,3.2,z),(.18,.18,4.2))
 # Entry porte-cochere, with a clear drive under its raised horizontal roof.
 B.source='arrival';F=Frame(B,1756,800,.5)
 F.box('vh-stone',(0,6.8,0),(22,.5,15),True);F.box('vh-roof',(0,7.08,0),(21.7,.06,14.7))
 for x in [-10,10]:
  for z in [-6.5,6.5]:F.box('vh-metal',(x,3.4,z),(.45,6.8,.45),True)
 return dict(key=KEY,name='Virgin Hotels three towers and casino',center=[1660,0,710],bounds=[1500,510,1825,870],building='virgin',structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
