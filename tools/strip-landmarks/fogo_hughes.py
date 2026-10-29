"""Original Fogo Hughes geometry. Public plan fitted to survey, not measured.
Official tour governs visible architecture; no reference imagery embedded.
"""
from common import *
KEY='fogo-hughes';IDS=['way/511850832']
def build(B):
 p=footprint(IDS[0]);F=Frame(B,1487,106,0,y=0);D=Frame(B,1496.344,123.509,.698,y=0)
 B.property=KEY+'-exterior';B.source='retail/'+KEY;B.detail=0
 door=dict(p=D.p(0,.8,0),yaw=D.yaw,width=2.5,height=3,name='Fogo public entrance',venue=KEY)
 B.shell(p,.02,7.3,'fg-stucco',roof=False,openings=[door]);B.planar('fg-membrane',p,7.3)
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  L=math.dist(a,b);R=Frame(B,(a[0]+b[0])/2,(a[1]+b[1])/2,math.atan2(a[1]-b[1],b[0]-a[0]),y=0)
  R.box('fg-trim',(0,7.27,0),(L+.05,.2,.2));R.box('fg-dark',(0,.35,0),(L,.65,.13))
 # Taller pale south window elevation, three repeated glazed bays.
 S=Frame(B,1481,125.55,-.032,y=0)
 S.box('fg-stucco',(0,4.7,0),(18,9.4,.22),False)
 for u in [-6,0,6]:
  S.box('fg-glass',(u,4.6,.14),(4.1,6.3,.06))
  for du in [-2.08,0,2.08]:S.box('fg-trim',(u+du,4.6,.22),(.09,6.4,.09))
  for y in [1.4,3.8,7.8]:S.box('fg-trim',(u,y,.22),(4.3,.09,.09))
  # Original restrained screen lattice, not copied decorative artwork.
  for xx in np.arange(-1.9,2,.4):
   for yy in np.arange(4.1,7.5,.5):
    S.tube('fg-bronze',(u+float(xx),float(yy),.26),(u+float(xx)+.27,float(yy)+.35,.26),.018,5)
 for u in [-7,0,7]:S.plant(u,1.7,palm=True)
 S.text('FOGO DE CHAO',(0,8.55,.3),.68,'fg-letter',back=True)
 # Stone sign fin and projecting arrival canopy. Dimensional estimates.
 D.box('fg-vein',(-4.8,5.6,.1),(2.3,11.2,2),True)
 for i,c in enumerate('FOGO DE CHAO'):
  if c!=' ':D.text(c,(-4.8,10.6-i*.58,1.13),.53,'fg-letter',back=True)
 D.box('fg-dark',(0,4.8,4.8),(10,.5,10))
 D.box('fg-dark',(4.6,2.35,9.3),(.65,4.7,1.5),True)
 for u in [-2.4,2.4]:
  for v in [2,5,8]:D.lathe('fg-lamp',u,v,[(4.53,.10),(4.57,.10)],12)
 landing=D.poly([(-4,-.5),(3,-.5),(3.5,3.1),(-4,3.1)])
 B.planar('fg-paving',landing,.8,True)
 st=D.p(0,0,6);Frame(B,st[0],st[2],D.yaw+math.pi,y=0).stairs(0,0,3.4,.8,3,y=0)
 # Side ramp, clear collision route and side guarding.
 B.upface('fg-paving',[D.p(-4,.8,2),D.p(-2,.8,2),D.p(-2,.14,10),D.p(-4,.14,10)],True)
 for u in [-4.1,4.1]:
  D.rail((u,.3),(u,9.8),y=1.75)
 for u in [-1.32,1.32]:D.box('fg-trim',(u,2.35,0),(.11,3.1,.2))
 D.box('fg-trim',(0,3.9,0),(2.75,.13,.2))
 # Side windows and rear servicing, all aligned to actual perimeter segments.
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  L=math.dist(a,b)
  if L<6 or (a[1]+b[1])/2>120:continue
  R=Frame(B,(a[0]+b[0])/2,(a[1]+b[1])/2,math.atan2(a[1]-b[1],b[0]-a[0]),y=0)
  q=R.p(0,0,.2);sgn=-1 if p.contains(Point(q[0],q[2])) else 1
  for u in np.arange(-L/2+2,L/2-1,4.5):
   R.box('fg-glass',(float(u),3.2,sgn*.08),(3.3,3.7,.06))
   for du in [-1.7,0,1.7]:R.box('fg-trim',(float(u)+du,3.2,sgn*.13),(.07,3.85,.08))
   for y in [1.28,5.12]:R.box('fg-trim',(float(u),y,sgn*.13),(3.47,.07,.08))
 for u,v in [(-11,-7),(-3,-8),(7,-10),(11,-2)]:
  F.box('fg-equipment',(u,7.95,v),(2.5,1.3,2))
  for yy in np.arange(7.5,8.5,.14):F.box('fg-dark',(u,float(yy),v+1.02),(2.2,.035,.04))
 F.box('fg-membrane',(-2,7.7,-2),(15,.75,12))
 # Fitted public plan: southeast arrival, bar east, market/dining west.
 B.property=KEY+'-interior';B.source='interior/'+KEY;B.detail=1
 room=p.buffer(-.22).intersection(box(1470.9,91,1509.6,126))
 B.shell(room,.8,4.5,'fg-panel',roof=False,openings=[door]);B.planar('fg-carpet',room,.8,True);B.planar('fg-ceiling',room,4.5)
 # Entry corridor to main dining remains clear west of the east bar.
 F.box('fg-wood',(9,1.35,10),(3.3,1.1,1),True);F.box('fg-marble',(9,1.94,10),(3.5,.1,1.15),True)
 # Bar along east side with white top, fluted front and wine display.
 F.box('fg-dark',(16,1.43,0),(1.35,1.26,11),True);F.box('fg-marble',(16,2.1,0),(1.65,.12,11.3),True)
 for v in np.arange(-5.3,5.4,.18):F.box('fg-bronze',(15.28,1.45,float(v)),(.06,1.15,.06))
 F.box('fg-mirror',(20.7,2.8,0),(.06,2.8,10.5))
 for y in [1.7,2.5,3.3,4.1]:
  F.box('fg-bronze',(20.3,y,0),(.65,.06,10.5))
  for v in np.arange(-5,5,.5):F.lathe('fg-bottle',20.3,float(v),[(y+.04,.07),(y+.33,.07),(y+.47,.025)],8)
 for v in np.arange(-4.6,4.7,1.15):
  F.lathe('fg-bronze',14.4,float(v),[(.8,.28),(.86,.28),(.9,.045),(1.6,.045)],12)
  F.box('fg-seat',(14.4,1.68,float(v)),(.53,.15,.52),True)
  F.box('fg-seat',(14.1,1.95,float(v)),(.08,.52,.53))
 # Market island with serving wells, bowls and abstract produce.
 F.box('fg-wood',(-3,1.35,-2),(10,1.1,3.2),True);F.box('fg-marble',(-3,1.94,-2),(10.3,.12,3.5),True)
 for u in np.arange(-7,2,.9):
  for v in [-3,-1]:
   F.lathe('fg-steel',float(u),v,[(2,.25),(2.14,.30)],14)
   F.lathe('fg-food',float(u),v,[(2.14,.22),(2.32,.10)],10)
 for u in [-7,1]:F.tube('fg-bronze',(u,2,-2),(u,2.85,-2),.04,8)
 F.box('fg-clear',(-3,2.8,-2),(8.7,.04,3.0))
 def table(u,v):
  F.box('fg-wood',(u,1.5,v),(1.6,.09,1.6),True)
  for dx in [-.64,.64]:
   for dz in [-.64,.64]:F.box('fg-wood',(u+dx,1.1,v+dz),(.08,.6,.08))
  F.box('fg-cloth',(u,1.56,v),(1.72,.04,1.72))
  for dx in [-.85,.85]:F.box('fg-cloth',(u+dx,1.38,v),(.025,.36,1.72))
  for side in [-1,1]:
   cx=u+side*1.15;F.box('fg-seat',(cx,1.27,v),(.5,.13,.55),True)
   F.box('fg-seat',(cx+side*.23,1.62,v),(.07,.63,.55))
   for dz in [-.21,.21]:
    for dx in [-.19,.19]:F.box('fg-wood',(cx+dx,1.01,v+dz),(.045,.43,.045))
   F.lathe('fg-cloth',u+side*.5,v,[(1.59,.18),(1.61,.18)],18)
   F.lathe('fg-clear',u+side*.48,v+.35,[(1.59,.045),(1.69,.025),(1.8,.065)],12)
 for u in [-12,-7,-2,3]:
  for v in [-11,7,13]:
   if room.covers(F.poly([(u-1.5,v-1.2),(u+1.5,v-1.2),(u+1.5,v+1.2),(u-1.5,v+1.2)])):table(u,v)
 # Slatted curved ceiling fields, ring pendants and paneled walls.
 for u in np.arange(-13,7,.22):
  span=math.sqrt(max(0,1-((u+3)/10)**2))*12
  if span>.2:F.box('fg-wood',(float(u),4.32,-1),(.085,.1,span))
 for u,v,r in [(-8,-10,2.1),(1,-10,2.1),(-7,8,2),(1,8,2),(10,10,1.5)]:
  F.tube('fg-bronze',(u,4.48,v),(u,3.65,v),.035,8)
  for a in np.linspace(0,math.tau,49)[:-1]:
   a2=a+math.tau/48;x=u+r*math.cos(a);z=v+r*math.sin(a)
   F.tube('fg-bronze',(x,3.65,z),(u+r*math.cos(a2),3.65,v+r*math.sin(a2)),.035,6)
   F.lathe('fg-lamp',x,z,[(3.65,.045),(3.85,.045)],8)
  for a in [0,math.pi/2]:F.tube('fg-bronze',(u-r*math.cos(a),3.65,v-r*math.sin(a)),(u+r*math.cos(a),3.65,v+r*math.sin(a)),.03,6)
 for u in [-12,-6,0,6]:
  F.box('fg-wood',(u,2.7,-14.5),(3.5,1.8,.08));F.box('fg-art',(u,2.7,-14.43),(3.3,1.6,.04))
 # Curved slatted bar canopy and arched bottle framing from the tour.
 for v in np.arange(-5.6,5.7,.24):
  pts=[]
  for t in np.linspace(0,math.pi/2,15):pts.append((15+5*math.sin(t),3.0+1.3*(1-math.cos(t)),float(v)))
  F.path('fg-bronze',pts,.028,6)
 for v in [-5.7,0,5.7]:
  F.path('fg-bronze',[(15+5*math.sin(t),3.0+1.3*(1-math.cos(t)),v) for t in np.linspace(0,math.pi/2,24)],.065,8)
 # Low wall panels and regularly framed original abstract artwork.
 for u in np.arange(-14,12,2.2):
  for yy in [1.05,1.8]:F.box('fg-wood',(float(u),yy,-14.47),(2.05,.045,.05))
  for du in [-1,1]:F.box('fg-wood',(float(u)+du,1.43,-14.47),(.045,.8,.05))
 # Host cabinet doors and pulls, rather than an unbroken box.
 for u in [7.7,8.35,9,9.65,10.3]:
  for yy in [1,1.75]:F.box('fg-bronze',(u,yy,10.52),(.6,.025,.025))
  F.box('fg-bronze',(u+.24,1.47,10.55),(.035,.18,.04))
 routes=[dict(name='Arrival ramp and host',points=[D.p(-3,.14,10),D.p(-3,.8,2),D.p(0,.8,2),D.p(0,.8,-1),F.p(6,.8,12),F.p(6,.8,6)]),dict(name='Main dining and market',points=[F.p(u,.8,3) for u in [7,4,-2,-8,-13]]),dict(name='Bar aisle',points=[F.p(12,.8,v) for v in [8,3,-3,-10]])]
 return dict(key=KEY,name='Fogo de Chao Hughes Center',center=[p.centroid.x,0,p.centroid.y],bounds=list(p.bounds),structural=True,hotelSources=[],exteriorOnly=False,portals=[door],zones=[dict(origin=[1490,.8,126],yaw=math.pi,width=42,depth=36,height=5)],lights=[dict(p=F.p(u,3.9,v),color=0xffdfae,power=8,range=12) for u,v in [(-8,-8),(2,-6),(10,10),(16,-1)]],routes=routes)
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
