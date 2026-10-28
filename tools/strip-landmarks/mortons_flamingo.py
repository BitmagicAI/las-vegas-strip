"""Original Morton's geometry, fitted to OSM and linked official 2014 tour.
Room coordinates/heights are estimates, not a surveyed plan. No reference pixels.
"""
from common import *
KEY='mortons-flamingo';ID='way/390004030';YAW=-math.pi/2+.108

def build(B):
 F=Frame(B,1758.9,130.8,YAW,y=0);p=footprint(ID)
 B.property=KEY+'-exterior';B.source='retail/'+KEY;B.detail=0
 door=dict(p=F.p(0,.24,0),yaw=YAW,width=2.6,height=2.75,name='Public restaurant entrance',venue=KEY)
 B.shell(p,.02,5.2,'mf-stucco',roof=False,openings=[door]);B.planar('mf-roof',p,5.2)
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  R=Frame(B,(a[0]+b[0])/2,(a[1]+b[1])/2,math.atan2(a[1]-b[1],b[0]-a[0]),y=0);L=math.dist(a,b)
  R.box('mf-stone',(0,.48,0),(L,.92,.13));R.box('mf-stucco',(0,5.45,0),(L,.5,.28),True)
  for y in [5.16,5.7]:R.box('mf-trim',(0,y,0),(L+.1,.15,.4))
 # Raised stepped entrance parapet and original dimensional lettering.
 for u,w,y,h in [(0,9,5.55,1.8),(-7,5,5.1,.9),(7,5,5.1,.9)]:
  F.box('mf-stucco',(u,y,-.15),(w,h,.45));F.box('mf-trim',(u,y+h/2,-.12),(w+.18,.16,.6))
 F.text("MORTON'S",(0,5.9,.15),.7,'mf-black',back=True);F.text('THE STEAKHOUSE',(0,5.32,.16),.24,'mf-black',back=True)
 # Curved laminated wood canopy; four round columns. Heights fitted from photograph.
 for u in [-3.6,3.6]:
  for v in [1,6]:
   F.lathe('mf-stucco',u,v,[(.12,.39),(.3,.39),(.35,.30),(3.6,.30),(3.72,.38)],24)
   F.box('mf-trim',(u,3.78,v),(.85,.18,.85))
 def cy(u):return 3.9+.85*(1-(u/4.25)**2)
 for i in range(40):
  a=-4.25+i*8.5/40;b=a+8.5/40
  B.upface('mf-wood',[F.p(a,cy(a),.1),F.p(b,cy(b),.1),F.p(b,cy(b),6.8),F.p(a,cy(a),6.8)])
 for v in [.1,.35,6.55,6.8]:
  for i in range(40):
   a=-4.25+i*8.5/40;b=a+8.5/40
   for dy in [0,-.15]:F.tube('mf-wood',(a,cy(a)+dy,v),(b,cy(b)+dy,v),.065,8)
 for u in np.linspace(-4,4,17):F.tube('mf-wood',(float(u),cy(u)-.08,.1),(float(u),cy(u)-.08,6.8),.035,8)
 B.upface('mf-paving',[F.p(-3,.24,0),F.p(3,.24,0),F.p(3,.16,7.1),F.p(-3,.16,7.1)],True)
 # Dark glazed sidelights and recessed side awnings, stone sill and metal frames.
 for u in [-2.4,2.4,-7.2,7.2]:
  F.box('mf-glass',(u,1.8,.04),(1.6,2.6,.04),True)
  for x in [u-.8,u,u+.8]:F.box('mf-black',(x,1.8,.09),(.055,2.7,.07))
  if abs(u)>3:
   B.upface('mf-black',[F.p(u-1.1,3.25,0),F.p(u+1.1,3.25,0),F.p(u+1.1,2.95,1),F.p(u-1.1,2.95,1)])
   F.box('mf-black',(u,2.85,1),(2.2,.2,.08))
 for u,v in [(-6,2),(6,2),(-10,1),(10,1)]:
  F.box('mf-stone',(u,.35,v),(2,.5,1.2),True);F.box('mf-leaf',(u,.75,v),(1.8,.45,1))
 for u,v in [(-7,-9),(4,-10),(-6,-23),(5,-28),(0,-35)]:
  F.box('mf-equipment',(u,5.75,v),(2.3,1.1,1.7))
  for y in np.arange(5.35,6.18,.12):F.box('mf-black',(u,float(y),v+.86),(2,.025,.025))
 # Raised roof rectangles visible in aerial; height and offsets fitted.
 for u,v,w,h in [(-8,-8,5,8),(7,-8,4,8),(-7,-33,6,8),(7,-31,4,7)]:
  rp=F.poly([(u-w/2,v-h/2),(u+w/2,v-h/2),(u+w/2,v+h/2),(u-w/2,v+h/2)]).intersection(p)
  B.shell(rp,5.21,5.7,'mf-stucco',roof=False,solid=False);B.planar('mf-roof',rp,5.7)
 # Public footprint: entrance and bar west; main dining east, supported by linked tour.
 B.property=KEY+'-interior';B.source='interior/'+KEY;B.detail=1
 room=F.poly([(-9,-.05),(8,-.05),(8,-32),(-9,-32)])
 B.shell(room,.24,3.55,'mf-panel',roof=False,openings=[door])
 B.planar('mf-plank',room,.24,True);B.planar('mf-ceiling',room,3.55)
 dining=F.poly([(-9,-11),(8,-11),(8,-32),(-9,-32)]);B.planar('mf-carpet',dining,.246)
 # Entrance wine cabinets and host counter, with clear central aisle.
 for u in [-5.8,5.7]:
  # Open frames and shelves, not a solid cabinet hidden behind opaque glass.
  v=-9.0
  F.box('mf-black',(u,1.6,v),(1.1,2.7,.12),True)
  for x in [u-.52,u+.52]:F.box('mf-black',(x,1.6,v+1.15),(.09,2.7,2.4),True)
  for y in [.35,.95,1.55,2.15,2.8]:F.box('mf-black',(u,y,v+1.15),(1.15,.07,2.4))
  for vv in [-8.8,-8.35,-7.9,-7.45,-7.0]:
   for y in [.4,1.0,1.6,2.2]:F.lathe('mf-bottle',u,float(vv),[(y,.08),(y+.3,.08),(y+.38,.028)],10)
 # Rounded host desk, convex front matching the reference silhouette.
 desk=F.poly([(2.5+.95*math.cos(t),-3+1.5*math.sin(t)) for t in np.linspace(0,math.tau,40,endpoint=False)])
 B.shell(desk,.24,1.43,'mf-black',roof=False);B.planar('mf-stone',desk.buffer(.06),1.46,True)
 # Bar on north side (left on entry), tall tables and stools.
 F.box('mf-panel',(-7.2,.83,-6),(1.3,1.16,7.5),True);F.box('mf-black',(-7.2,1.45,-6),(1.65,.1,7.7))
 for v in [-3.5,-5.2,-6.9,-8.6]:
  F.lathe('mf-metal',-5.6,v,[(.24,.26),(.3,.26),(.32,.04),(1.0,.04)],16)
  F.box('mf-seat',(-5.6,1.06,v),(.5,.12,.5),True)
 # Dining tables, booths, mirrored pilasters and layered round ceiling shades.
 for v in [-13.5,-18,-22.5,-27]:
  for u in [-5,0,5]:
   F.box('mf-wood',(u,.63,v),(.15,.78,.15),True)
   F.box('mf-cloth',(u,1.04,v),(1.7,.07,1.45),True)
   # Hanging cloth panels leave visible leg space; original restrained pleats.
   for side in [-1,1]:
    F.box('mf-cloth',(u+side*.84,.87,v),(.025,.32,1.45))
    F.box('mf-cloth',(u,.87,v+side*.72),(1.7,.32,.025))
   for side in [-1,1]:
    F.box('mf-seat',(u+side*1.15,.65,v),(.5,.16,.54),True)
    F.box('mf-seat',(u+side*1.38,1.05,v),(.09,.85,.54),True)
    for dz in [-.2,.2]:
     for dx in [-.19,.19]:F.box('mf-black',(u+side*1.15+dx,.4,v+dz),(.06,.32,.06))
    F.lathe('mf-cloth',u+side*.5,v,[(1.08,.19),(1.10,.19)],20)
   F.lathe('mf-lamp',u,v,[(3.12,.6),(3.24,.6),(3.25,.75),(3.37,.75)],32)
  for u in [-8.6,7.6]:
   F.box('mf-black',(u,1.85,v),(.22,3.15,.5));F.box('mf-mirror',(u+(.13 if u<0 else -.13),1.9,v),(.03,2.9,.38))
 # Perimeter upholstered booths and a paneled rear wall.
 for v in [-14,-19,-24,-29]:
  F.box('mf-seat',(6.8,.65,v),(.85,.22,3.4),True)
  F.box('mf-seat',(7.25,1.04,v),(.2,.95,3.4),True)
  for vv in [v-1.65,v+1.65]:F.box('mf-panel',(6.6,1.0,vv),(1.5,1.5,.14),True)
 for u in [-7,-3,1,5]:
  F.box('mf-trim',(u,2.1,-31.9),(1.3,1.6,.06))
  F.box('mf-panel',(u,2.1,-31.85),(1.13,1.43,.04))
 for v in [-7,-17,-27]:F.box('mf-black',(-.5,3.44,v),(17,.18,.18))
 for u in [-8.8,7.8]:F.box('mf-black',(u,1.0,-17),(.12,.12,29))
 return dict(key=KEY,name="Morton's The Steakhouse",center=[p.centroid.x,0,p.centroid.y],bounds=list(p.bounds),structural=True,hotelSources=[],exteriorOnly=False,portals=[door],zones=[dict(origin=F.p(-.5,.24,0),yaw=F.yaw+math.pi,width=17.2,depth=32.2,height=3.8)],lights=[dict(p=F.p(0,3.1,v),color=0xffe1be,power=8,range=10) for v in [-3,-12,-21,-29]],routes=[dict(name='Entry to public dining',points=[F.p(0,.24,v) for v in [8,2,-1,-8,-11]]+[F.p(2.5,.24,v) for v in [-13,-19,-25,-30]])])

if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
