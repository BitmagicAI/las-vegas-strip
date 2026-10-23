"""Mapped east Harmon pedestrian lift and missing bridge connection.
April 2025 Street View establishes panel cladding and door arrangement.
Bridge datum matches installed city decks; upper roof height is estimated.
"""
from common import *
from forum_shops import facade_frame
from local_pavement import local_pavement
KEY='harmonEastLift';ID='way/1421481101';D=.18;H=6.035

def slab(B,p,lo,hi,mat='hel-concrete'):
 B.shell(p,lo,hi,mat,roof=False);B.planar(mat,p,hi,True)
 for q in parts(p):
  for t in triangles(q):B.face(mat,list(reversed([(x,lo,z)for x,z in list(t.exterior.coords)[:-1]])))

def guard(B,line,y):
 coords=list(line.coords)
 for a,b in zip(coords,coords[1:]):
  if math.dist(a,b)<.03:continue
  B.tube('hel-metal-paint',(a[0],y+1.13,a[1]),(b[0],y+1.13,b[1]),.038,8)
  B.face('hel-guard-glass',[(a[0],y+.16,a[1]),(b[0],y+.16,b[1]),(b[0],y+1.07,b[1]),(a[0],y+1.07,a[1])],True)
  for t in np.linspace(0,1,max(2,math.ceil(math.dist(a,b)/1.8)+1)):
   x,z=a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t
   B.box('hel-metal-paint',(x,y+.61,z),(.045,1.14,.045))

def exterior(B):
 B.property=KEY+'-exterior';B.source=ID;B.detail=0
 p=footprint(ID);F=Frame(B,66.982,896.44,-math.atan2(.423,3.336),0)
 # Separate ground and bridge door positions follow the two mapped indoor links.
 ports=[]
 for u,y,label in [(-.43,H,'PEDESTRIAN BRIDGE'),(1.02,D,'STREET')]:
  q=F.p(u,y,-2.005);ports.append(dict(p=[q[0],q[2]],direction=[-F.si,-F.co],y=y,label=label,width=1.18,height=2.3,metal=True))
 openings=[dict(p=[q['p'][0],q['y'],q['p'][1]],width=q['width']+.06,height=q['height'])for q in ports]
 # Shell manually pierced at both elevations; common shell's un-yawed opening
 # path assumes street height, so use yaw to retain the upper-level opening.
 for o in openings:o['yaw']=F.yaw
 # Use the true front plane: a through-shaft clipping mask would also cut the rear.
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  line=LineString([a,b]);L=line.length;region=box(0,.03,L,10.05)
  for o in openings:
   q=Point(o['p'][0],o['p'][2]);u=((q.x-a[0])*(b[0]-a[0])+(q.y-a[1])*(b[1]-a[1]))/L
   distance=abs((q.x-a[0])*(b[1]-a[1])-(q.y-a[1])*(b[0]-a[0]))/L
   if distance<.1:region=region.difference(box(u-o['width']/2,o['p'][1]-.02,u+o['width']/2,o['p'][1]+o['height']+.04))
  for poly in parts(region):
   for t in triangles(poly):B.face('hel-panel-paint',[(a[0]+(b[0]-a[0])*u/L,y,a[1]+(b[1]-a[1])*u/L)for u,y in list(t.exterior.coords)[:-1]],True)
 slab(B,p,9.91,10.08,'hel-cap-paint')
 # Fine panel joints follow each actual wall, avoiding both door cutouts.
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  G,L,_,_=facade_frame(B,a,b,p,-.008);G.y=0
  for y in np.arange(.25,10,1.18):
   segment=LineString([G.p(0,0,0)[::2],G.p(L,0,0)[::2]])
   masks=unary_union([Point(o['p'][0],o['p'][2]).buffer(.72) for o in openings if o['p'][1]-.16<y<o['p'][1]+2.45])
   for piece in parts_line(segment.difference(masks)):
    aa,bb=list(piece.coords)[0],list(piece.coords)[-1];B.tube('hel-joint-paint',(aa[0],float(y),aa[1]),(bb[0],float(y),bb[1]),.008,4)
  for u in np.arange(1.1,L,1.1):
   q=G.p(float(u),0,0)
   for low,high in [(0,10.02)]:
    cuts=[(low,high)]
    for o in openings:
     if math.hypot(q[0]-o['p'][0],q[2]-o['p'][2])<.72:
      cuts=[v for aa,bb in cuts for v in [(aa,min(bb,o['p'][1]-.16)),(max(aa,o['p'][1]+2.45),bb)] if v[1]>v[0]]
    for aa,bb in cuts:G.box('hel-joint-paint',(float(u),(aa+bb)/2,0),(.012,bb-aa,.018))
 # Door surrounds, recessed headers, sills and upper vent.
 for u,y,_ in [(-.43,H,''),(1.02,D,'')]:
  for s in [-1,1]:F.box('hel-metal-paint',(u+s*.66,y+1.18,-2.045),(.10,2.46,.16))
  F.box('hel-metal-paint',(u,y+2.41,-2.045),(1.42,.14,.16))
  F.box('hel-metal-paint',(u,y+.012,-2.06),(1.42,.025,.25))
  F.box('hel-dark-paint',(u,y+2.64,-2.036),(.5,.12,.025))
 F.box('hel-dark-paint',(0,9.35,-2.02),(1.55,.32,.04))
 for y in [9.25,9.33,9.41]:F.box('hel-metal-paint',(0,y,-2.055),(1.53,.025,.04))
 F.box('hel-sign-paint',(-1.7,8.8,-2.38),(.08,.42,.85))
 S=Frame(B,*[F.p(-1.76,0,-2.38)[i]for i in [0,2]],F.yaw+math.pi/2,0)
 S.text('ELEVATOR',(0,8.68,-.05),.13,'hel-letter-paint')
 # Lift cabin floors remain collision-bearing when the near-door controls unload.
 for y in [D,H]:slab(B,p.buffer(-.025),y-.12,y,'hel-floor')
 # Bridge and widened head landing follow mapped way297110936.
 route=LineString([(67.30,890.34),(73.37,846.98),(74.96,835.13)])
 deck=route.buffer(2,cap_style=2,join_style=2).union(Polygon([(60.95,887.94),(69.9,887.8),(69.3,894.74),(65.3,894.5),(60.6,894.4)]))
 flights=[((45.26,893.89),(61.94,891.21),1.75),((43.68,892.21),(62.62,889.02),1.25),((44.86,895.86),(62.14,892.85),1.25)]
 for a,b,w in flights:
  deck=deck.difference(LineString([a,b]).buffer(w/2+.06,cap_style=2))
 existing=[]
 for g in json.loads(Path('build/geographic-strip/city-meshes.json').read_text()):
  if g['material']!='bridge-deck':continue
  for face in g['faces']:
   v=[g['vertices'][i]for i in face]
   if all(abs(q[1]-H)<.002 for q in v)and any(25<q[0]<80 and 770<q[2]<855 for q in v):existing.append(Polygon([(q[0],q[2])for q in v]))
 existing=unary_union(existing)
 slab(B,deck.difference(existing),H-.415,H)
 # Rail openings correspond to lift entrance, stairs and escalators.
 openingsMask=unary_union([p.buffer(.12),LineString([(43.68,892.21),(62.62,889.02)]).buffer(.85),LineString([(44.86,895.86),(62.14,892.85)]).buffer(.85),LineString([(45.26,893.89),(61.94,891.21)]).buffer(1.05),Point(74.96,835.13).buffer(2.4)])
 for line in parts_line(deck.boundary.difference(openingsMask.union(existing.buffer(.15)))):guard(B,line,H)
 # Way179790277 is tagged level=1 rather than bridge=yes; the original importer
 # omitted this short western landing as well as the long east crossing.
 west=LineString([(29.09,778.02),(32.86,778.16),(34.93,778.24),(42.176,781.808)]).buffer(2,cap_style=2,join_style=2)
 slab(B,west.difference(existing),H-.415,H)
 westOpen=unary_union([Point(29.09,778.02).buffer(2.3),Point(42.176,781.808).buffer(2.4),box(31.2,774.5,35.3,782.8),existing.buffer(.15)])
 for line in parts_line(west.boundary.difference(westOpen)):guard(B,line,H)
 # Existing missing flight: central concrete stair, flanked by two escalators.
 stairs=[]
 for j,(a,b,w)in enumerate(flights):
  dx,dz=b[0]-a[0],b[1]-a[1];run=math.hypot(dx,dz);G=Frame(B,a[0],a[1],math.atan2(dx,dz),D)
  count=49 if j==0 else 42;rise=H-D
  B.upface('hel-step', [G.p(-w/2,0,0),G.p(w/2,0,0),G.p(w/2,rise,run),G.p(-w/2,rise,run)],True)
  for k in range(count):
   h=rise/count;d=run/count;G.box('hel-step' if j==0 else 'hel-metal-paint',(0,(k+1)*h-.024,(k+.5)*d),(w,.048,d+.003))
   G.box('hel-step' if j==0 else 'hel-metal-paint',(0,(k+.5)*h,k*d),(w,h,.025))
  for side in [-1,1]:
   x=side*(w/2+.03)
   G.tube('hel-dark-paint' if j else 'hel-metal-paint',(x,1.05,0),(x,rise+1.05,run),.045,8)
   B.face('hel-guard-glass',[G.p(x,.12,0),G.p(x,rise+.12,run),G.p(x,rise+1,run),G.p(x,1,0)],True)
   B.face('hel-metal-paint',[G.p(x,-.3,0),G.p(x,rise-.3,run),G.p(x,rise,run),G.p(x,0,0)])
  stairs.append([[a[0],D,a[1]],[b[0],H,b[1]],[66.4,H,891]])
 # Pier beside the street edge, outside carriageway. No piers on the crossing.
 B.box('hel-concrete',(66.8,2.9,890.8),(1.05,5.8,1.05),True)
 local_pavement(B,box(38,887,86,907).difference(p).union(box(23,740,65,835)),D,'hel-paving')
 samples=[[x,H+.15,z] for x in np.arange(60,77,.75)for z in np.arange(835.5,894,.75)if deck.buffer(-.18).contains(Point(x,z))]
 samples.extend([[q.x,10.2,q.y]for q in [p.centroid]])
 for y in [D,H]:stairs.append([[ports[0 if y==H else 1]['p'][0],y,893.6],[F.x,y,F.z]])
 stairs.append([[67.3,H,890.3],[73.37,H,846.98],[74.96,H,835.13]])
 stairs.append([[26,D,781],[26,D,798],[32,D,798]])
 samples.extend([[x,D+.15,z]for x in [25,28,31,34]for z in [784,788,792,796,800]])
 Path('build/city-exteriors/harmon-east-lift-samples.json').write_text(json.dumps(samples))
 Path('build/city-exteriors/harmon-east-lift-stairs.json').write_text(json.dumps(stairs))
 # Near access data owns only doors/buttons; permanent GLB owns all static collision.
 access=dict(id='way-1421481101',name='East Harmon pedestrian lift',bounds=list(p.buffer(3).bounds),height=10.08,portals=ports,lift=[F.x,F.z],liftButton=[F.p(-1.25,0,0)[0],F.p(-1.25,0,0)[2]],meshes=[],collision={'vertices':[],'indices':[]},lights=[],signs=[])
 Path('build/city-exteriors/harmon-east-lift-access.pending.json').write_text(json.dumps(access))
 return dict(key=KEY,name='Harmon pedestrian bridge connections and east lift',center=[58,0,840],bounds=[23,740,86,907],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})

def parts_line(g):
 if g.is_empty:return []
 if g.geom_type=='LineString':return [g]
 return [l for q in g.geoms for l in parts_line(q)]
