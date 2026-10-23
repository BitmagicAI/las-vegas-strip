"""Six distinct Santa Paula apartment exteriors; side access dimensions estimated."""
from common import *
from forum_shops import facade_frame
KEY='santaPaulaNorth';IDS=['way/12367258'+v for v in ['04','03','06','02','05','01']]
def rail(F,a,b,y):
 L=math.dist(a,b)
 for t in np.linspace(0,1,math.ceil(L/.18)+1):
  u=a[0]+(b[0]-a[0])*t;w=a[1]+(b[1]-a[1])*t;F.box('spn-rail-paint',(u,y+.5,w),(.035,1,.035))
 F.tube('spn-rail-paint',(a[0],y+1,a[1]),(b[0],y+1,b[1]),.035,7)
 F.b.face('spn-collision',[F.p(a[0],y,a[1]),F.p(b[0],y,b[1]),F.p(b[0],y+1,b[1]),F.p(a[0],y+1,a[1])],True)
def window(F,u,y,w=1.05,h=1.35):
 F.box('spn-frame-paint',(u,y,-.07),(w+.14,h+.14,.14));F.box('spn-glass',(u,y,-.16),(w,h,.035));F.box('spn-frame-paint',(u,y,-.19),(.035,h,.03));F.box('spn-frame-paint',(u,y,-.19),(w,.04,.03));F.box('spn-sill-paint',(u,y-h/2-.10,-.15),(w+.26,.09,.28))
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/santa-paula-north';B.detail=0;W=Frame(B,0,0,y=0);samples=[];routes=[];ps=[footprint(i) for i in IDS]
 for idx,p in enumerate(ps):
  lower=['olive','cream','gray','pale','charcoal','white'][idx];upper=['olive','blue','slate','pale','charcoal','purple'][idx]
  B.shell(p,.18,3.15,'spn-'+lower+'-stucco',roof=False);B.shell(p,3.15,6.13,'spn-'+upper+'-paint',roof=False)
  edges=[facade_frame(B,a,b,p,0) for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:])];F,L,nx,nz=min((e for e in edges if e[2]<-.8),key=lambda e:e[0].x)
  # Gables on1703/1715/1721, shallow hipped roofs on the other three.
  roofmat='spn-brown-roof-paint' if idx in [0,1,3] else 'spn-gray-roof-paint'
  if idx in [0,3,4]:
   def hh(x,z):
    u=(x-F.x)*F.co-(z-F.z)*F.si
    return 6.15+max(0,1-abs(u-L/2)/(L/2))*1.65
   for t in triangles(p):
    # Split at ridge in world coordinates before triangulation.
    for lo,hi in [(-100,L/2),(L/2,100)]:
     clip=Polygon([(F.p(u,0,w)[0],F.p(u,0,w)[2]) for u,w in [(lo,-100),(hi,-100),(hi,100),(lo,100)]])
     for q in parts(t.intersection(clip)):
      for tt in triangles(q):B.upface(roofmat,[(x,hh(x,z),z) for x,z in list(tt.exterior.coords)[:-1]],True)
   for G,ll,nnx,nnz in edges:
    a=G.p(0,6.13,0);b=G.p(ll,6.13,0);m=G.p(ll/2,0,0)
    if abs(nnx)>.8:B.face('spn-'+upper+'-paint',[a,b,(m[0],hh(m[0],m[2]),m[2])],True)
  else:
   inner=p.buffer(-2.5,join_style=2)
   for q in parts(p.difference(inner)):
    for t in triangles(q):B.upface(roofmat,[(x,6.15+min(2.5,p.boundary.distance(Point(x,z)))*.38,z) for x,z in list(t.exterior.coords)[:-1]],True)
   B.planar(roofmat,inner,7.1,True)
  gallery=max((e for e in edges if e[3]>.8),key=lambda e:e[1])
  for G,ll,nnx,nnz in edges:
   G.box('spn-fascia-paint',(ll/2,6.13,-.07),(ll,.15,.26));G.box('spn-trim-paint',(ll/2,3.14,-.04),(ll,.10,.12));G.box('spn-plinth-paint',(ll/2,.33,-.035),(ll,.3,.10))
   if G is F:
    us=[ll*.28,ll*.72] if idx!=2 else [ll/2]
    for u in us:
     for y in [1.65,4.62]:window(G,u,y)
    G.text(str([1703,1707,1711,1715,1721,1725][idx]),(ll*.82,2.45,-.15),.2,'spn-number-paint')
    if idx==5:
     for u in [ll*.12,ll*.4,ll*.62,ll*.90]:
      for y in [3.5,4.1,4.7,5.3,5.85]:B.face('spn-accent-paint',[G.p(u+.18*math.cos(a),y+.18*math.sin(a),-.09) for a in np.linspace(0,2*math.pi,12,endpoint=False)])
   elif G is gallery[0]:
    for u in np.arange(2.4,ll-1,4.6):
     for y in [.18,3.18]:
      G.box('spn-frame-paint',(float(u),y+1.07,-.07),(1.0,2.14,.12));G.box('spn-door-paint',(float(u),y+1.07,-.15),(.85,2.0,.05));window(G,float(u)+1.5,y+1.48,1.1,1.1)
   elif ll>5:
    for u in np.arange(2.0,ll-1,4.2):
     for y in [1.65,4.62]:window(G,float(u),y,.9,1.2)
   if idx in [1,2,5]:
    for y in np.arange(3.35,6.1,.23):G.box('spn-siding-shadow-paint',(ll/2,float(y),-.021),(ll,.018,.025))
  G,ll,_,_=gallery
  G.box('spn-gallery-concrete',((6.3+ll)/2,3.08,-.8),(ll-6.3,.2,1.6),True);rail(G,(6.6,-1.6),(ll,-1.6),3.18)
  G.box('spn-soffit-paint',(ll/2,6.08,-.8),(ll,.13,1.7))
  for u in np.arange(7,ll,4.5):G.box('spn-frame-paint',(float(u),3.2,-1.49),(.10,6,.10),True)
  q=G.p(.5,0,-.8);S=Frame(B,q[0],q[2],G.yaw+math.pi/2,y=0);S.stairs(0,0,1.4,3,5.8,y=.18)
  routes.append([G.p(.35,.18,-.8),G.p(6.5,3.18,-.8),G.p(ll-1,3.18,-.8)])
  for x,z in [p.representative_point().coords[0]]:
   W.box('spn-service-paint',(x,7.55,z),(1.3,.85,1.5));W.box('spn-vent-paint',(x,8,z),(1.13,.03,1.3))
  B.planar('spn-concrete',p.buffer(1.85,join_style=2).difference(p),.18,True)
  yard=box(1992,p.bounds[1],p.bounds[0],p.bounds[3]);B.planar('spn-gravel',yard,.17,True)
  # Sparse metal perimeter fence, with a pedestrian gap beside the gallery.
  for z in np.arange(p.bounds[1],p.bounds[3]-.8,.22):W.box('spn-fence-paint',(1992, .8,float(z)),(.03,1.25,.03))
  W.box('spn-fence-paint',(1992,1.33,(p.bounds[1]+p.bounds[3]-.8)/2),(.04,.045,p.bounds[3]-p.bounds[1]-.8))
  for x in np.arange(p.bounds[0]+.5,p.bounds[2],1.2):
   for z in np.arange(p.bounds[1]+.5,p.bounds[3],1.2):
    if p.buffer(-.25).contains(Point(x,z)):samples.append([float(x),hh(x,z)+.3 if idx in [0,3,4] else 7.35,float(z)])
 B.groups={k:g for k,g in B.groups.items() if g['material']!='spn-collision'}
 Path('build/city-exteriors/santa-paula-north-samples.json').write_text(json.dumps(samples));Path('build/city-exteriors/santa-paula-north-stairs.json').write_text(json.dumps(routes))
 return dict(key=KEY,name='Santa Paula north apartment row',center=[2010,0,-3846],bounds=list(unary_union(ps).bounds),structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
