"""Waldorf Astoria: KPF angular glass/metal tower and separate podium.
CVU164.3m; Earth Nov2022; parking/pool deck27m and sky lobby79m estimated.
"""
from common import *
from building_surfaces import BuildingSurfaces
from forum_shops import facade_frame
LOBBY=box(-143.6855,1050.871,-73.903,1125.782)
KEY='waldorfExterior';LOW=['way/52194829','way/52134170','way/52186615'];TOWER=LOW[0]
class Access:
 def wall(self,a,b,lo,hi):
  line=LineString([a,b]);L=line.length;region=box(0,lo,L,hi)
  for seg in parts(line.intersection(LOBBY),'LineString'):
   ds=[line.project(Point(q)) for q in seg.coords];region=region.difference(box(min(ds),0,max(ds),12.1))
  for door in [Point(-134,1058),Point(-68,1096)]:
   if line.distance(door)<5:
    x=line.project(door);region=region.difference(box(max(0,x-2),0,min(L,x+2),5))
  return [[[line.interpolate(x).x,y,line.interpolate(x).y] for x,y in list(t.exterior.coords)[:-1]] for p in parts(region) for t in triangles(p)]
def records():return [dict(BYID[i],shape=footprint(i).simplify(.08,preserve_topology=True),height=h,base=12.1 if i==TOWER else 0) for i,h in zip(LOW,[164.3,12,27])]
def exterior(B):
 B.property=KEY+'-exterior';B.detail=0;rs=records();surf=BuildingSurfaces(rs);access=Access();tower=footprint(TOWER)
 # Pool terrace occupies the garage roof alongside the tower's inner bend.
 garage=footprint(LOW[2]);deck=garage.intersection(tower.buffer(30)).difference(tower.buffer(.3)).intersection(box(-210,1040,-100,1140))
 pools=unary_union([rotate(box(-173,1080,-165,1102),-20,origin=(-169,1091)),rotate(box(-148,1118,-126,1124),20,origin=(-137,1121))]).intersection(deck.buffer(-2))
 for r in rs:
  p=r['shape'];h=r['height'];ident=r['id'];istower=ident==TOWER;isgarage=ident==LOW[2];B.source='guest-waldorf' if istower else 'podium/'+ident
  for poly in parts(p):
   for ring in [poly.exterior,*poly.interiors]:
    ps=list(ring.coords)
    for a,b in zip(ps,ps[1:]):
     line=LineString([a,b]);L=line.length
     if L<.08:continue
     F,_,nx,nz=facade_frame(B,a,b,p,.06);ux,uz=(b[0]-a[0])/L,(b[1]-a[1])/L;tris=surf.wall(ident,a,b,r['base'],h,access)
     region=unary_union([Polygon([(line.project(Point(v[0],v[2])),v[1]) for v in t]) for t in tris])
     def patch(mat,x0,y0,x1,y1,off=.12):
      if x1<=x0 or y1<=y0:return
      for q in parts(region.intersection(box(x0,y0,x1,y1))):
       for t in triangles(q):B.face(mat,[(a[0]+ux*x+nx*off,y,a[1]+uz*x+nz*off) for x,y in list(t.exterior.coords)[:-1]])
     patch('wa-glass' if istower else 'wa-shadow' if isgarage else 'wa-metal',0,0,L,h)
     if istower:
      # Window-scale alternating metal / vision glass / fritted spandrel bays.
      count=max(1,round(L/3.15));w=L/count
      for j in range(count):
       x=j*w;pw=.40*w
       patch('wa-metal-light' if j%3==0 else 'wa-metal',x,6,min(x+pw,L),h,.27)
       for y in np.arange(6,160,3.35):
        patch('wa-spandrel',x+pw,y,min(x+w,L),min(y+1.1,h),.17)
        patch('wa-frame',x+pw,y+1.1,min(x+w,L),y+1.15,.21)
       patch('wa-frame',x+w-.05,6,x+w,h,.25)
      # Sky lobby read as a broad recessed dark slot, without emissive fill.
      if L>18:
       patch('wa-skyglass',0,77,L,81,.34)
       patch('wa-metal',0,76.75,L,77,.4);patch('wa-metal',0,81,L,81.25,.4)
      for x in np.arange(0,L,3):patch('wa-frame',x,0,min(x+.08,L),6,.25)
      patch('wa-metal',0,160.8,L,164.3,.3)
     elif isgarage:
      # Folded panels create actual shallow facade relief, sharing one batch.
      for x in np.arange(0,L,1.0):
       width=min(1,L-x);pts=[(x,.20),(x+width*.5,.65),(x+width,.20)]
       for (u0,o0),(u1,o1) in zip(pts,pts[1:]):
        # Clip geometry to exterior ownership so buried garage walls never return.
        for q in parts(region.intersection(box(u0,0,u1,h))):
         for t in triangles(q):B.face('wa-metal' if o0<o1 else 'wa-metal-dark',[(a[0]+ux*u+nx*(o0+(o1-o0)*(u-u0)/max(.001,u1-u0)),y,a[1]+uz*u+nz*(o0+(o1-o0)*(u-u0)/max(.001,u1-u0))) for u,y in list(t.exterior.coords)[:-1]])
      for y in np.arange(2,h,3.4):patch('wa-shadow',0,y,L,y+.12,.69)
     else:
      for x in np.arange(.4,L-1,2.5):
       patch('wa-glass',x,.6,min(x+2.2,L-.2),min(h-1,9),.21)
       patch('wa-frame',x,.6,min(x+.07,L),min(h-1,9),.25)
      patch('wa-stone',0,0,L,.6,.25);patch('wa-metal-light',0,h-.5,L,h,.3)
     F.box('wa-metal',(L/2,h+.1,0),(L,.2,.4))
     for t in tris:
      c=B.solids[B.property];n=len(c['vertices'])//3;c['vertices'].extend(v for pt in t for v in pt);c['indices'].extend([n,n+1,n+2])
   roof=surf.roof(ident,poly,h)
   if isgarage:roof=roof.difference(deck)
   if abs(h-12)<.01:roof=roof.difference(LOBBY)
   B.planar('wa-roof',roof,h+.025,True)
   B.detail=1
   for x in np.arange(poly.bounds[0]+7,poly.bounds[2]-5,23):
    for z in np.arange(poly.bounds[1]+7,poly.bounds[3]-5,23):
     cell=box(x-1.7,z-1.2,x+1.7,z+1.2)
     if roof.contains(cell) and (not isgarage or deck.distance(cell)>3):B.box('wa-metal-light',(x,h+.7,z),(3.4,1.3,2.4));B.box('wa-vent',(x,h+1.38,z),(3,.08,2))
   B.detail=0
 # West pool terrace: slabs, basin walls, coping and perimeter glass guards.
 B.source='pool-deck';B.planar('wa-paving',deck.difference(pools),27.08,True);B.planar('water',pools,26.92);B.planar('wa-stone',pools,25.6,True);B.planar('wa-stone',pools.buffer(.35).difference(pools),27.11,True)
 for p in parts(pools):
  ps=list(p.exterior.coords)
  for a,b in zip(ps,ps[1:]):B.face('wa-stone',[(a[0],25.6,a[1]),(b[0],25.6,b[1]),(b[0],26.92,b[1]),(a[0],26.92,a[1])],True)
 for p in parts(deck):
  ps=list(p.exterior.coords)
  for a,b in zip(ps,ps[1:]):
   if LineString([a,b]).distance(tower)<.5:continue
   B.face('wa-guard',[(a[0],27.1,a[1]),(b[0],27.1,b[1]),(b[0],28.2,b[1]),(a[0],28.2,a[1])],True);B.tube('wa-frame',(a[0],28.22,a[1]),(b[0],28.22,b[1]),.035,6)
 for x in np.arange(-195,-115,3.0):
  for z in np.arange(1050,1138,4.5):
   if deck.intersection(pools.buffer(6)).difference(pools.buffer(1.8)).contains(box(x-.45,z-1,x+.45,z+1)):
    B.box('wa-cushion',(x,27.45,z),(.7,.18,1.9));B.box('wa-frame',(x,27.25,z),(.6,.18,1.6))
 # Glazed arrival canopy follows the north tower edge, above clear vehicle space.
 B.source='arrival';F=Frame(B,-140,1055,-.36)
 F.box('wa-guard',(0,5.3,0),(24,.12,4.5),True)
 for x in np.arange(-12,13,3):F.box('wa-frame',(x,5.18,0),(.10,.16,4.5))
 return dict(key=KEY,name='Waldorf Astoria tower and podium',center=[-125,0,1095],bounds=[-225,1010,-40,1190],building='waldorf',structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
