"""Original TownePlace geometry, official photo-supported elevations and public rooms."""
from common import *
KEY='towneplace-stadium';IDS=['way/431504486']
def build(B):
 B.property=KEY+'-exterior';B.source='podium/'+KEY;B.detail=0
 F=Frame(B,-853,1736,y=0);p=footprint(IDS[0])
 entry=(31.2725,.24,22.23)
 doors=[dict(p=F.p(*entry),yaw=0,width=3.1,height=2.85,name='TownePlace public lobby',venue=KEY)]
 B.shell(p,.02,17.8,'ts-white-stucco',openings=doors,roof=False);B.planar('ts-roof',p,17.75)
 coords=list(p.exterior.coords)
 for a,b in zip(coords,coords[1:]):
  L=math.dist(a,b)
  if L<1:continue
  G=Frame(B,*a,math.atan2(-(b[1]-a[1]),b[0]-a[0]),y=0)
  q=G.p(L/2,0,-.12);sgn=-1 if not p.covers(Point(q[0],q[2])) else 1
  mx=(a[0]+b[0])/2+853;mz=(a[1]+b[1])/2
  south=mz>1747
  west_end=max(a[0],b[0])<-852
  mat='ts-ochre-paint' if south else 'ts-white-stucco'
  if 5<mx<15 or 20<mx<29 or 34<mx<50 or 55<mx<64:mat='ts-charcoal-paint'
  if 24<mx<30 and south:mat='ts-wood'
  north_front=not south and abs(a[0]-b[0])>L*.9
  central_strip=north_front and 28<mx<33.5
  if central_strip:mat='ts-charcoal-paint'
  if west_end:mat='ts-ochre-paint'
  # Original stepped footprint provides facade projections rather than coplanar skins.
  G.box(mat,(L/2,10.65,sgn*.04),(L,14.0,.06))
  if west_end:G.box('ts-white-stucco',(L*5/6,10.65,sgn*.085),(L/3,14.0,.03))
  G.box('ts-stone',(L/2,1.75,sgn*.05),(L,3.4,.08)) if min(math.dist(G.p(L/2,0,0)[::2],doors[0]['p'][::2]),L)>4 else None
  G.box('ts-white-stucco',(L/2,17.8,0),(L+.08,.22,.34))
  if north_front and not central_strip:G.box('ts-white-stucco',(L/2,16.35,sgn*.13),(L,.65,.22))
  G.box('ts-sill-paint',(L/2,3.6,sgn*.10),(L,.14,.24))
  if L<2.7:continue
  bays=max(1,round(L/4.4));pitch=L/bays
  for i in range(bays):
   u=(i+.5)*pitch;w=min(2.12,pitch-.65)
   for floor in range(4):
    y=5.2+floor*3.05
    G.box('ts-frame-paint',(u,y,sgn*.12),(w+.14,1.92,.13))
    G.box('ts-glass',(u,y,sgn*.21),(w,1.78,.05))
    G.box('ts-frame-paint',(u-.28,y,sgn*.25),(.045,1.8,.045))
    G.box('ts-sill-paint',(u,y-.99,sgn*.22),(w+.22,.09,.25))
    if mat=='ts-charcoal-paint' and not central_strip:
     for du in np.arange(-pitch/2+.25,pitch/2,.25):G.box('ts-panel-seam',(u+float(du),y,sgn*.082),(.012,3.0,.016))
   q=G.p(u,0,0)
   if math.dist(q[::2],doors[0]['p'][::2])>3:
    G.box('ts-frame-paint',(u,1.8,sgn*.14),(w+.14,2.2,.14));G.box('ts-glass',(u,1.8,sgn*.24),(w,2.06,.045))
  if central_strip:
   for yy in np.arange(3.8,17.6,.24):G.box('ts-panel-seam',(L/2,float(yy),sgn*.085),(L,.013,.018))
  for yy in [6.8,9.85,12.9,15.95]:G.box('ts-panel-seam',(L/2,yy,sgn*.085),(L,.018,.018))
 # Three shallow sloping crowns with projecting metal fascias, estimated from both official views.
 for x,w,base in [(10,18,18.1),(37,28,18.65),(62,19,18.35)]:
  z0=-.7;z1=20.1
  pts=[F.p(x-w/2,base,z0),F.p(x+w/2,base+.85,z0),F.p(x+w/2,base+.85,z1),F.p(x-w/2,base,z1)]
  B.face('ts-roof-metal',pts)
  # Enclose the shallow roof crown; the overhang is not an open floating plane.
  for a,b in zip(pts,pts[1:]+pts[:1]):
   # Recess the fascia below a thin metal edge; north-facing backing is charcoal.
   B.face('ts-charcoal-paint' if a[2]==pts[0][2] and b[2]==pts[0][2] else 'ts-white-stucco',[a,b,(b[0],17.78,b[2]),(a[0],17.78,a[2])])
  B.face('ts-white-stucco',[(q[0],17.78,q[2]) for q in pts])
  for a,b in zip(pts,pts[1:]+pts[:1]):B.face('ts-frame-paint',[a,b,(b[0],b[1]-.10,b[2]),(a[0],a[1]-.10,a[2])])
 F.box('ts-charcoal-paint',(30.78,18.25,-.88),(5.1,1.05,.18))
 F.box('ts-white-stucco',(30.78,19.43,-.88),(5.1,1.3,.18))
 F.text('TOWNEPLACE SUITES',(42,18.4,20.18),.85,'ts-charcoal-paint',back=True)
 F.text('MARRIOTT',(42,17.96,20.18),.32,'ts-red-paint',back=True)
 F.text('TownePlace Suites',(41,18.35,-.79),.85,'ts-letter')
 F.text('MARRIOTT',(44,17.94,-.79),.3,'ts-red-paint')
 # South arrival canopy and pergola; independently supported, no solid placeholder.
 F.box('ts-frame-paint',(31.3,3.65,24.6),(13.8,.35,5.5))
 for x in [25.0,37.6]:F.box('ts-frame-paint',(x,1.9,26.5),(.24,3.6,.24),True)
 for i in range(25):
  x=24.3+i*.58;F.tube('ts-metal',(x,3.88,21.8),(x,4.35,24.6),.018,5);F.tube('ts-metal',(x,4.35,24.6),(x,3.88,27.4),.018,5)
 B.face('ts-roof-metal',[F.p(24.3,3.85,21.8),F.p(38.3,3.85,21.8),F.p(38.3,4.32,24.6),F.p(24.3,4.32,24.6)])
 B.face('ts-roof-metal',[F.p(24.3,4.32,24.6),F.p(38.3,4.32,24.6),F.p(38.3,3.85,27.4),F.p(24.3,3.85,27.4)])
 for x in [40,44,48,52]:
  F.box('ts-metal',(x,3.45,21.8),(.10,.16,7.1));F.box('ts-metal',(x,1.8,25.3),(.10,3.4,.10),True)
 for z in np.arange(18.3,25.4,.38):F.box('ts-metal',(46,3.55,float(z)),(12.2,.06,.05))
 F.box('ts-paving',(31.3,.12,24.6),(12,.24,6),True)
 for x in [29.68,32.86]:F.box('ts-frame-paint',(x,1.7,22.3),(.08,2.95,.18))
 F.box('ts-frame-paint',(31.27,3.2,22.3),(3.26,.10,.18))
 from towneplace_pool import build_pool
 pool_route=build_pool(B,F)
 # Public room is inset into the surveyed perimeter with a supported vestibule.
 room=F.poly([(20,7),(44,7),(44,18),(32.85,18),(32.85,22.3),(29.7,22.3),(29.7,18),(20,18)])
 B.planar('ts-floor',room,.24,True)
 B.property=KEY+'-interior';B.source='public/'+KEY
 B.shell(room,.24,3.5,'ts-interior',openings=doors,roof=False);B.planar('ts-ceiling',room,3.48)
 # Reception's high counter and curved accessible end from official desk8521.
 F.box('ts-wood',(23.3,.84,10.0),(4.3,1.2,.72),True);F.box('ts-counter',(23.3,1.48,10),(4.5,.12,.90))
 F.lathe('ts-wood',25.9,10,[(.24,.5),(.98,.5)],24);F.lathe('ts-counter',25.9,10,[(.98,.55),(1.08,.55)],24)
 B.planar('ts-counter',F.poly([(25.9+.55*math.cos(a),10+.55*math.sin(a)) for a in np.linspace(0,math.tau,32,endpoint=False)]),1.08)
 F.box('ts-red-paint',(24.5,1.21,10.40),(.8,.32,.035));F.text('hello.',(24.5,1.21,10.43),.19,'ts-letter',back=True)
 for x in [22.4,24.3]:F.box('ts-screen',(x,1.65,9.9),(.60,.38,.05))
 F.box('ts-wood',(23.3,1.84,7.1),(6.0,3.2,.1))
 for x,t in [(21.8,'Stay'),(23.3,'Work'),(24.8,'Play')]:F.box('ts-red-paint',(x,2.5,7.2),(.9,.65,.06));F.text(t,(x,2.5,7.25),.19,'ts-letter',back=True)
 # Market shelves and glazed refrigerator next to reception.
 F.box('ts-frame-paint',(20.55,1.35,9.0),(.8,2.2,1.1),True)
 for yy in [.5,.95,1.4,1.85]:
  F.box('ts-counter',(20.65,yy,9.0),(.7,.06,.95))
  for z in [8.7,9,9.3]:F.box('ts-market-paint',(20.8,yy+.16,z),(.22,.26,.15))
 F.box('ts-glass',(21.01,1.35,9.0),(.025,2.05,.96))
 # TV column separates dining from arrival; preserve clear route to reception.
 F.box('ts-wood',(33.4,1.85,10),(1.4,3.22,.75),True);F.box('ts-screen',(33.4,2.1,10.4),(1.15,.70,.035))
 F.box('ts-blue',(33.4,.65,11.0),(2.0,.18,.65),True)
 for x,z in [(37.4,11),(41,11),(38,15.7)]:
  F.box('ts-wood',(x,1.0,z),(1.8,.10,.9),True)
  F.lathe('ts-chair-frame-paint',x,z,[(.24,.36),(.31,.36),(.32,.06),(.96,.06)],16)
  for zz in [z-.9,z+.9]:
   F.box('ts-seat',(x,.70,zz),(.56,.14,.55),True)
   F.box('ts-red-fabric',(x,1.02,zz+(.23 if zz>z else -.23)),(.57,.70,.09))
   for xx in [x-.23,x+.23]:
    for dz in [-.22,.22]:F.tube('ts-chair-frame-paint',(xx,.24,zz+dz),(xx,.65,zz+dz),.025,6)
 # Beverage counter and breakfast alcove visible beside dining in official lobby image.
 F.box('ts-wood',(41.8,.76,7.8),(3.5,1.04,1.0),True);F.box('ts-counter',(41.8,1.32,7.8),(3.65,.09,1.1))
 for x in [40.8,42.6]:F.box('ts-frame-paint',(x,1.85,7.8),(.7,1.0,.65));F.box('ts-screen',(x,1.95,8.14),(.55,.6,.04))
 for x in [27,37]:F.light(x,3.15,13,power=23,range=14)
 routes=[dict(name='Public arrival to reception',points=[F.p(x,.24,z) for x,z in [(31.27,27),(31.27,20),(31.27,14),(27,12),(23.5,12)]]),dict(name='Dining circulation',points=[F.p(x,.24,z) for x,z in [(31.27,16),(34.5,16),(35.4,13),(39.1,13),(42.7,13),(42.7,16.8)]])]
 routes.append(pool_route)
 return dict(key=KEY,name='TownePlace Suites Stadium District',center=[-818.6,0,1747.1],bounds=[-876,1733,-778,1766],structural=True,exteriorOnly=False,portals=doors,zones=[dict(origin=F.p(20,.24,7),yaw=0,width=24,depth=15.3,height=3.24)],lights=B.lights,routes=routes,hotelSources=[])
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
