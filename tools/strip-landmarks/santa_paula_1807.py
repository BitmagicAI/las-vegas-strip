"""1807/1811 Santa Paula: two-floor galleries, street stairs and mapped roof footprints."""
from common import *
from forum_shops import facade_frame
KEY='santaPaula1807';IDS=['way/1236725810','way/1236725812']
def rail(F,a,b,y):
 L=math.dist(a,b)
 for t in np.linspace(0,1,math.ceil(L/.15)+1):
  u=a[0]+(b[0]-a[0])*t;w=a[1]+(b[1]-a[1])*t;F.box('spf-rail-paint',(u,y+.52,w),(.04,1.04,.04))
 for yy in [.12,1.04]:F.box('spf-rail-paint',((a[0]+b[0])/2,y+yy,(a[1]+b[1])/2),(L if a[1]==b[1] else .055,.06,L if a[0]==b[0] else .055))
 F.b.face('spf-collision',[F.p(a[0],y,a[1]),F.p(b[0],y,b[1]),F.p(b[0],y+1.05,b[1]),F.p(a[0],y+1.05,a[1])],True)
def window(F,u,y,w=1.3,h=1.3):
 F.box('spf-frame-paint',(u,y,-.07),(w,h,.12));F.box('spf-glass',(u,y,-.15),(w-.12,h-.12,.04));F.box('spf-frame-paint',(u,y,-.19),(.04,h-.12,.035));F.box('spf-sill-paint',(u,y-h/2-.04,-.13),(w+.1,.08,.24))
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/santa-paula-1807';B.detail=0;ps=[footprint(i) for i in IDS];samples=[];routes=[];W=Frame(B,0,0,y=0)
 for idx,p in enumerate(ps):
  B.shell(p,.18,6.28,'spf-gray-stucco',roof=False)
  if idx==0:B.planar('spf-membrane-paint',p.buffer(.18,join_style=2),6.3,True)
  else:
   inner=p.buffer(-1.4,join_style=2)
   for q in parts(p.difference(inner)):
    for t in triangles(q):B.upface('spf-roof-paint',[(x,6.28+min(1.4,p.boundary.distance(Point(x,z)))*.36,z) for x,z in list(t.exterior.coords)[:-1]],True)
   B.planar('spf-roof-paint',inner,6.784,True)
  edges=[]
  for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
   G,L,nx,nz=facade_frame(B,a,b,p,0);mid=G.p(L/2,0,0);gallery=(idx==0 and nz<-.8) or(idx==1 and ((nz>.8 and mid[0]<2013 and mid[2]<-3738)or(nx<-.8 and mid[0]>2010)))
   edges.append((G,L,nx,nz,gallery))
   G.box('spf-fascia-paint',(L/2,6.29,-.02),(L,.14,.22));G.box('spf-trim-paint',(L/2,3.12,-.025),(L,.12,.10));G.box('spf-plinth-paint',(L/2,.36,-.035),(L,.36,.08))
   if L>20:
    for u in np.arange(2.1,L-1.4,4.7):
     for y in [.18,3.18]:
      if gallery:
       G.box('spf-frame-paint',(float(u),y+1.08,-.07),(1.0,2.16,.1));G.box('spf-door-paint',(float(u),y+1.08,-.14),(.86,2.02,.05));G.box('spf-hardware-paint',(float(u)+.3,y+1,-.18),(.035,.15,.04))
       window(G,float(u)+1.6,y+1.5,1.2,1.2)
      else:window(G,float(u),y+1.5,1.1,1.18)
   elif L>6:
    for y in [1.7,4.7]:window(G,L/2,y,2.1 if nx<-.8 else 1.4,1.5)
   if gallery:
    G.box('spf-gallery-concrete',(L/2,3.08,-.8),(L,.2,1.6),True);rail(G,(0,-1.6),(L,-1.6),3.18)
    G.box('spf-soffit-paint',(L/2,6.21,-.8),(L,.14,1.7));G.box('spf-membrane-paint',(L/2,6.31,-.8),(L,.06,1.7))
    for u in np.arange(.25,L,4.7):G.box('spf-frame-paint',(float(u),3.2,-1.48),(.10,6.0,.10),True)
  # West stair copied from street reference; exact run and landing lengths estimated.
  F,L,_,_,_=min((e for e in edges if e[2]<-.8),key=lambda e:e[0].x)
  start=.8 if idx==0 else L-1;end=start+(5.8 if idx==0 else -5.8)
  q=F.p(start,0,-.85);S=Frame(B,q[0],q[2],F.yaw+(math.pi/2 if idx==0 else -math.pi/2),y=0)
  S.stairs(0,0,1.6,3,5.8,y=.18)
  lo,hi=(end,L+1.6) if idx==0 else (-1.6,end)
  F.box('spf-gallery-concrete',((lo+hi)/2,3.08,-.85),(hi-lo,.2,1.7),True);rail(F,(lo,-1.7),(hi,-1.7),3.18)
  # Cover over 1807's west landing is visible in the reference.
  if idx==0:F.box('spf-soffit-paint',((lo+hi)/2,6.20,-.85),(hi-lo,.16,1.8))
  turn=L+.8 if idx==0 else -.8
  routes.append([F.p(start,.18,-.85),F.p(end,3.18,-.85),F.p(turn,3.18,-.85),F.p(turn,3.18,2.5),F.p(turn,3.18,9)])
  F.text('1807' if idx==0 else '1811',(L-.8,4.7,-.14),.28,'spf-number-paint')
  # Rooftop HVAC: six units on1807, small vents and low ridges on1811.
  if idx==0:
   for x in [1993,1999,2004,2010,2016,2021]:
    z=-3761.5;W.box('spf-curb-paint',(x,6.41,z),(1.6,.22,1.7));W.box('spf-service-paint',(x,6.85,z),(1.28,.66,1.4));W.box('spf-vent-paint',(x,7.20,z),(1.08,.03,1.1));W.tube('spf-service-paint',(x,6.34,z),(x,6.34,z+1.7),.12,8)
  else:
   for x in [1993,1999,2005,2011,2017]:B.lathe('spf-service-paint',(x,-3745),[(6.8,.10),(7.2,.10),(7.25,.17)],12)
  for x in np.arange(p.bounds[0]+.5,p.bounds[2],1.1):
   for z in np.arange(p.bounds[1]+.5,p.bounds[3],1.1):
    if p.buffer(-.25).contains(Point(x,z)):samples.append([float(x),7.25,float(z)])
 allp=unary_union(ps);site=allp.convex_hull.buffer(2.3,join_style=2);court=ps[1].convex_hull.difference(ps[1]).buffer(-.7)
 B.planar('spf-gravel',site.difference(allp).difference(court),.15,True)
 B.planar('spf-grass',court,.16,True)
 for p in ps:B.planar('spf-concrete',p.buffer(.55,join_style=2).difference(p),.18,True)
 # Ground route below the exposed stair feet and clear west sidewalk.
 B.planar('spf-concrete',box(1986.5,-3770.5,1989.0,-3731),.18,True)
 # Chain-link boundary represented with thin diamond wires, not an opaque wall.
 for z0,z1 in [(-3770,-3769),(-3767,-3756),(-3754,-3752),(-3750,-3731)]:
  length=z1-z0
  for z in np.arange(z0,z1+.1,2.1):W.tube('spf-fence-paint',(1986.7,.18,float(z)),(1986.7,1.42,float(z)),.035,7)
  W.tube('spf-fence-paint',(1986.7,1.39,z0),(1986.7,1.39,z1),.024,6)
  for z in np.arange(z0,z1,.23):
   for dy in [1,-1]:
    zz=min(z1,float(z)+.62);yy=.2 if dy==1 else 1.38;end=.2+(zz-z)*1.9 if dy==1 else 1.38-(zz-z)*1.9
    W.tube('spf-fence-paint',(1986.7,yy,float(z)),(1986.7,end,zz),.007,4)
 B.groups={k:g for k,g in B.groups.items() if g['material']!='spf-collision'}
 Path('build/city-exteriors/santa-paula-1807-samples.json').write_text(json.dumps(samples));Path('build/city-exteriors/santa-paula-1807-stairs.json').write_text(json.dumps(routes))
 return dict(key=KEY,name='1807 and1811 Santa Paula apartments',center=[2006,0,-3750],bounds=list(site.bounds),structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
