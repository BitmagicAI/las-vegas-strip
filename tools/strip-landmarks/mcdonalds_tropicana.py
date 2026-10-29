"""Original mapped restaurant exterior. Height and bay spacing are photo estimates."""
from common import *
KEY='mcdonalds-tropicana';IDS=['way/190828100']
def build(B):
 p=footprint(IDS[0]);B.property=KEY+'-exterior';B.source='podium/'+KEY;B.detail=0
 F=Frame(B,-1200.426,1707.062,.03185,y=0);w=16.06;d=29.55
 B.shell(p,.02,4.65,'mcd-stucco',roof=False);B.planar('mcd-roof',p,4.39)
 B.shell(p.buffer(-.20,join_style=2),4.39,4.65,'mcd-metal',roof=False,solid=False)
 B.planar('mcd-metal',p.difference(p.buffer(-.22,join_style=2)),4.69)
 # Street-facing north elevation and customer entrance on the west return.
 fronts=[Frame(B,*[F.p(-w/2,0,0)[i] for i in (0,2)],F.yaw,y=0),Frame(B,*[F.p(-w/2,0,d)[i] for i in (0,2)],F.yaw+math.pi/2,y=0)]
 routes=[]
 for j,G in enumerate(fronts):
  L=w if j==0 else d
  end=L if j==0 else 24.5
  # Textured stone skirt and top sill sit off the structural backing.
  G.box('mcd-stone',(end/2,.63,-.085),(end,1.15,.17))
  G.box('mcd-metal',(end/2,1.24,-.16),(end,.10,.24))
  for x in np.arange(1.7,end-1,2.45):
   G.box('mcd-recess',(x,2.23,-.08),(2.27,1.9,.13))
   G.box('mcd-glass',(x,2.23,-.17),(2.18,1.78,.035))
   for xx in [x-1.14,x+1.14]:G.box('mcd-metal',(xx,2.23,-.22),(.065,1.96,.09))
   for yy in [1.27,3.19]:G.box('mcd-metal',(x,yy,-.22),(2.34,.065,.09))
  G.box('mcd-soffit',(end/2,3.48,-.86),(end,.14,1.8))
  G.box('mcd-yellow' if j==0 else 'mcd-metal',(end/2,3.64,-1.75),(end,.32,.12))
  for x in np.arange(1,end,3.4):
   G.tube('mcd-metal',(x,4.18,-.04),(x,3.60,-1.70),.035,8)
   G.box('mcd-soffit',(x,3.38,-1),(.28,.03,.28))
  # Metallic corrugations are finite-depth ribs, no overlapping coplanar faces.
  for yy in np.arange(4.05,4.78,.105):G.box('mcd-metal',(end/2,yy,-.10),(end,.055,.14))
  G.box('mcd-paving',(L/2,.245,-1.55),(L,.15,3.05),True)
  routes.append(dict(name=('North' if j==0 else 'West')+' frontage',points=[G.p(t,.32,-2.2) for t in [1,L/2,L-1]]))
 # Crown ribbon: real curved elevation, tapered at both ends, not a flat block.
 G=fronts[0]
 for a,b in zip(np.linspace(0,w,49),np.linspace(0,w,49)[1:]):
  def h(x):return 4.72+.55*math.sin(math.pi*x/w)
  pts=[G.p(a,h(a),-.25),G.p(b,h(b),-.25),G.p(b,h(b)+.24,-.25),G.p(a,h(a)+.24,-.25)]
  B.face('mcd-yellow',pts)
  B.face('mcd-yellow',[G.p(a,h(a)+.24,-.25),G.p(b,h(b)+.24,-.25),G.p(b,h(b)+.24,.05),G.p(a,h(a)+.24,.05)])
 G.text("McDonald's",(w*.5,4.12,-.27),.85,'mcd-letter')
 # West entrance portal, supported by close-up photograph showing address3451.
 G=fronts[1];x=6.2
 G.box('mcd-white',(x,2.33,-.25),(3.8,4.66,.36))
 G.box('mcd-recess',(x,1.53,-.46),(2.18,2.93,.05));G.box('mcd-glass',(x,1.53,-.50),(2.06,2.82,.03))
 for xx in [x-1.09,x,x+1.09]:G.box('mcd-metal',(xx,1.53,-.56),(.065,2.95,.09))
 for yy in [.08,.92,2.39,3.01]:G.box('mcd-metal',(x,yy,-.56),(2.21,.065,.09))
 for xx in [x-.13,x+.13]:G.tube('mcd-metal',(xx,1.05,-.65),(xx,1.42,-.65),.024,8)
 G.box('mcd-yellow',(x,3.32,-1.05),(3.85,.36,1.9));G.text('3451',(x+.52,2.60,-.58),.27,'mcd-letter');G.text('Welcome',(x,3.81,-.46),.40,'mcd-metal')
 # Original arched M silhouettes on the entrance and north-east corner.
 def arches(G,x,y,z,s):
  for side in [-1,1]:
   pts=[]
   for t in np.linspace(0,math.pi,21):pts.append(G.p(x+side*s*.42+s*.42*math.cos(t),y+s*math.sin(t),z))
   B.path('mcd-yellow',pts,s*.07,8)
 arches(G,x,4.03,-.46,.55)
 # White corner pier carrying the second wall emblem, visible in the oblique reference.
 N=fronts[0]
 N.box('mcd-white',(1.05,2.23,-.22),(2.10,4.46,.40))
 arches(N,1.05,3.40,-.46,.76)
 fronts[1].box('mcd-white',(d-1.0,2.23,-.22),(2.0,4.46,.40))
 # Blue safety posts flank the closed entrance without blocking the public route.
 for xx in [x-1.65,x+1.65]:G.lathe('mcd-blue',xx,-.95,[(.32,.10),(1.30,.10),(1.36,0)],12)
 # Rear/east service details, closed service window, joints and louvres.
 H=Frame(B,*[F.p(w/2,0,0)[i] for i in (0,2)],F.yaw-math.pi/2,y=0)
 for t in np.arange(1,d,3):H.box('mcd-joint',(t,2.2,-.035),(.024,4.3,.035))
 for x in [12,19]:
  H.box('mcd-metal',(x,1.82,-.10),(1.8,1.45,.15));H.box('mcd-glass',(x,1.82,-.20),(1.65,1.28,.04))
  H.box('mcd-metal',(x,1.13,-.39),(2.0,.12,.65));H.box('mcd-yellow',(x,2.71,-.60),(2.5,.19,1.25))
  H.box('mcd-metal',(x,1.82,-.25),(.05,1.35,.06))
 for z in [12,22]:
  F.box('mcd-equipment',(1.5,4.88,z),(2.8,.9,1.9));F.box('mcd-metal',(1.5,5.37,z),(2.95,.08,2.05))
  for zz in np.arange(z-.7,z+.8,.17):F.box('mcd-joint',(1.5,4.9,zz),(2.84,.04,.06))
 return dict(key=KEY,name='McDonalds West Tropicana',center=[-1200,0,1722],bounds=[-1214,1703,-1187,1741],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=routes,hotelSources=[])
if __name__=='__main__':
 B=Meshes();meta=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(meta,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
