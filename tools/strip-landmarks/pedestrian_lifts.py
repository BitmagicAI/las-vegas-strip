"""Three compact mapped pedestrian lift shafts. References and estimates are in
pedestrian-lifts-research.json. Upper datum follows retained city bridges.
"""
from common import *
from forum_shops import facade_frame
from harmon_east_lift import slab,guard,parts_line
from local_pavement import local_pavement
H=6.035;D=.18
SITES=[
 dict(key='cosmoPedestrianLift',id='way/1421481095',name='Cosmopolitan pedestrian lift',top=9.75,metal=False,ports=[([-51.384,742.045],H),([-51.411,741.633],D)],upper=[(-51.384,742.045),(-48.82,741.86)],lower=[(-51.411,741.633),(-50.2,741.3),(-50.42,738.82)]),
 dict(key='crystalsPedestrianLift',id='way/1421481096',name='Crystals pedestrian lift',top=10.08,metal=True,ports=[([-41.07,846.852],H),([-37.158,847.709],D)],upper=[(-41.07,846.852),(-46.94,846.01)],lower=[(-37.158,847.709),(-34.55,846.28)]),
 dict(key='parkPedestrianLift',id='way/1421481079',name='Park MGM pedestrian lift',top=9.55,metal=True,ports=[([-30.197,1293.61],H),([-30.35,1293.599],D)],upper=[(-30.197,1293.61),(-30.38,1301.06)],lower=[(-30.35,1293.599),(-31.25,1295.21),(-33.82,1295.33)])]

def exterior(B,s):
 key=s['key'];B.property=key+'-exterior';B.source=s['id'];B.detail=0
 p=footprint(s['id']);center=p.centroid;edges=list(zip(list(p.exterior.coords),list(p.exterior.coords)[1:]));ports=[]
 for pos,y in s['ports']:
  a,b=min(edges,key=lambda e:LineString(e).distance(Point(pos)))
  G,L,_,_=facade_frame(B,a,b,p);G.y=0
  # Outward direction of facade_frame's negative local w.
  ports.append(dict(p=pos,direction=[-G.si,-G.co],y=y,label='PEDESTRIAN BRIDGE' if y>1 else 'STREET',width=1.4,height=2.3,metal=s['metal']))
 for a,b in edges:
  line=LineString([a,b]);L=line.length;region=box(0,.03,L,s['top']-.10)
  for o in ports:
   if abs((o['p'][0]-a[0])*(b[1]-a[1])-(o['p'][1]-a[1])*(b[0]-a[0]))/L<.08:
    u=((o['p'][0]-a[0])*(b[0]-a[0])+(o['p'][1]-a[1])*(b[1]-a[1]))/L;region=region.difference(box(u-.74,o['y']-.02,u+.74,o['y']+2.35))
  for poly in parts(region):
   for t in triangles(poly):B.face('pl-dark-stucco' if key=='parkPedestrianLift' else 'hel-panel-paint',[(a[0]+(b[0]-a[0])*u/L,y,a[1]+(b[1]-a[1])*u/L)for u,y in list(t.exterior.coords)[:-1]],True)
  G,L,_,_=facade_frame(B,a,b,p,-.012);G.y=0
  if key!='parkPedestrianLift':
   # Visible panel seams; trim all strips against actual door openings.
   for y in np.arange(.3,s['top']-.1,1.15):
    visible=LineString([G.p(0,0,0)[::2],G.p(L,0,0)[::2]])
    for o in ports:
     if o['y']-.13<y<o['y']+2.45:visible=visible.difference(Point(o['p']).buffer(.85))
    for piece in parts_line(visible):
     aa,bb=list(piece.coords)[0],list(piece.coords)[-1];B.tube('hel-joint-paint',(aa[0],float(y),aa[1]),(bb[0],float(y),bb[1]),.008,4)
   for u in np.arange(1.05,L,1.05):
    pt=G.p(float(u),0,0);segments=[(.1,s['top']-.1)]
    for o in ports:
     if math.dist(pt[::2],o['p'])<.83:segments=[v for aa,bb in segments for v in [(aa,min(bb,o['y']-.12)),(max(aa,o['y']+2.45),bb)]if v[1]>v[0]]
    for aa,bb in segments:G.box('hel-joint-paint',(float(u),(aa+bb)/2,0),(.012,bb-aa,.02))
 slab(B,p,s['top']-.12,s['top'],'hel-cap-paint')
 for y in [D,H]:slab(B,p.buffer(-.015),y-.12,y,'hel-floor')
 for o in ports:
  # G's outward face is negative w; construct in its local plane at the doorway.
  dx,dz=o['direction'];G=Frame(B,*o['p'],math.atan2(-dx,-dz),0);y=o['y']
  for side in [-1,1]:G.box('hel-metal-paint',(side*.77,y+1.18,-.035),(.10,2.46,.15))
  G.box('hel-metal-paint',(0,y+2.4,-.035),(1.64,.15,.15));G.box('hel-metal-paint',(0,y+.01,-.04),(1.64,.02,.24))
  G.box('hel-dark-paint',(0,y+2.64,-.03),(.46,.12,.025))
  if y>1:
   if key=='parkPedestrianLift':G.box('hel-cap-paint',(0,y+2.85,-.55),(2.75,.14,1.25),True)
   else:
    G.box('hel-dark-paint',(0,s['top']-.52,-.025),(1.5,.28,.035))
    for dy in [-.08,0,.08]:G.box('hel-metal-paint',(0,s['top']-.52+dy,-.05),(1.48,.022,.035))
   G.box('hel-sign-paint',(.98,y+2.3,-.38),(.08,.42,.72))
   q=G.p(1.025,0,-.38);S=Frame(B,q[0],q[2],G.yaw-math.pi/2,0);S.text('ELEVATOR',(0,y+2.17,-.045),.12,'hel-letter-paint')
 # Only the missing upper apron is added. Existing bridge top triangles stay owned by city.
 route=LineString(s['upper']);deck=route.buffer(1.45,cap_style=2,join_style=2).difference(p)
 existing=[]
 for g in json.loads(Path('build/geographic-strip/city-meshes.json').read_text()):
  if g['material']!='bridge-deck':continue
  for f in g['faces']:
   v=[g['vertices'][i]for i in f]
   if all(abs(q[1]-H)<.002 for q in v):
    q=Polygon([(q[0],q[2])for q in v])
    if q.intersects(deck):existing.append(q)
 existing=unary_union(existing);slab(B,deck.difference(existing),H-.415,H)
 cuts=unary_union([p.buffer(.15),Point(s['upper'][-1]).buffer(1.65),existing.buffer(.15)])
 for line in parts_line(deck.boundary.difference(cuts)):guard(B,line,H)
 apron=LineString(s['lower']).buffer(1.1,cap_style=2,join_style=2).difference(p)
 local_pavement(B,apron,D,'hel-paving')
 routes=[[[x,D,z]for x,z in list(reversed(s['lower']))]+[[center.x,D,center.y]],[[x,H,z]for x,z in list(reversed(s['upper']))]+[[center.x,H,center.y]]]
 samples=[[center.x,s['top']+.1,center.y],[center.x,D+.1,center.y],[center.x,H+.1,center.y]]
 for x in np.arange(deck.bounds[0],deck.bounds[2],.5):
  for z in np.arange(deck.bounds[1],deck.bounds[3],.5):
   if deck.buffer(-.15).contains(Point(x,z)):samples.append([float(x),H+.1,float(z)])
 access=dict(id=s['id'].replace('/','-'),name=s['name'],bounds=list(p.buffer(3).bounds),height=s['top'],portals=ports,lift=[center.x,center.y],liftButton=[center.x-.65,center.y],meshes=[],collision={'vertices':[],'indices':[]},lights=[],signs=[])
 Path('build/city-exteriors/'+key+'-access.pending.json').write_text(json.dumps(access))
 Path('build/city-exteriors/'+key+'-routes.json').write_text(json.dumps(routes));Path('build/city-exteriors/'+key+'-samples.json').write_text(json.dumps(samples))
 b=p.union(deck).union(apron).bounds
 return dict(key=key,name=s['name'],center=[center.x,0,center.y],bounds=list(b),structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
