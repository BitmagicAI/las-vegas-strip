"""Original site geometry from official pool8532 and satellite; dimensions estimated."""
from common import *

def build_pool(B,F):
 # Local x=0 is west building face. Fence and deck stay east of Dean Martin Drive.
 deck=F.poly([(-22,0),(-1,0),(-1,27),(-20,27),(-22,22)])
 shape=unary_union([scale(Point(-12,12).buffer(1,resolution=32),6.2,8.8),scale(Point(-10,18).buffer(1,resolution=32),5.2,5.7)]).buffer(.2).buffer(-.2)
 deck=unary_union([deck,F.poly([(-12.4,27.2),(30.2,27.2),(30.2,29.2),(-12.4,29.2)]),F.poly([(-13.2,25.9),(-11.4,25.9),(-11.4,28.3),(-13.2,28.3)]),F.poly([(28,24.8),(30,24.8),(30,28.8),(28,28.8)])])
 basin=F.poly(list(shape.exterior.coords));coping=basin.buffer(.34).difference(basin)
 B.planar('ts-paving',deck.difference(basin.buffer(.34)),.24,True)
 B.shell(deck,.02,.24,'ts-paving',roof=False)
 B.planar('ts-counter',coping,.26,True)
 B.planar('ts_pool',basin,.14)
 B.planar('ts-pool-liner',basin,-.6)
 B.shell(basin,-.6,.2,'ts-pool-liner',roof=False)
 # Safety wall on north side, open approach from hotel arrival on south.
 F.box('ts-stone',(-11,1.2,.25),(21,1.95,.35),True)
 def fence(a,b):
  L=math.dist(a,b);n=max(1,math.ceil(L/.14))
  for i in range(n+1):
   x=a[0]+(b[0]-a[0])*i/n;z=a[1]+(b[1]-a[1])*i/n
   F.box('ts-metal',(x,.91,z),(.035,1.34,.035))
  for y in [.4,1.51]:F.tube('ts-metal',(a[0],y,a[1]),(b[0],y,b[1]),.03,6)
  # Invisible individual picket gaps are not collision gaps.
  G=Frame(B,*F.p(a[0],0,a[1])[::2],math.atan2(-(b[1]-a[1]),b[0]-a[0]),y=0)
  G.box('ts-fence-collision',(L/2,.92,0),(L,1.36,.04),True)
  B.groups.pop((B.property,B.source,'ts-fence-collision',B.detail))
 for a,b in [((-21.8,1),(-21.8,22)),((-21.8,22),(-19.8,26.7)),((-19.8,26.7),(-13.2,26.7)),((-11.4,26.7),(-1.2,26.7)),((-1.2,26.7),(-1.2,1))]:fence(a,b)
 # Access gate is visibly held open, with a clear1.8m south entry.
 fence((-13.2,26.7),(-13.2,25.3))
 # Three shallow entry treads at the northern end; pool remains decorative, not a swimming system.
 for i in range(3):
  step=basin.intersection(F.poly([(-18,3+i*.55),(-6,3+i*.55),(-6,3.6+i*.55),(-18,3.6+i*.55)]))
  B.planar('ts-pool-liner',step,.08-i*.12,True)
 for x in [-13.8,-10.8]:F.path('ts-metal',[(x,.24,2.5),(x,1.05,3.5),(x,.75,5.4),(x,-.1,5.4)],.035,8)
 # Low-profile gray sling loungers, not solid seat blocks.
 for x,z,yaw in [(-19,7,-math.pi/2),(-19,12,-math.pi/2),(-19,18,-math.pi/2),(-3,6,math.pi/2),(-3,11,math.pi/2),(-3,17,math.pi/2)]:
  q=F.p(x,0,z);G=Frame(B,q[0],q[2],yaw,y=0)
  for xx in [-.32,.32]:
   G.path('ts-metal',[(xx,.24,-.85),(xx,.58,-.65),(xx,.55,.45),(xx,1.07,1.03)],.025,6)
   G.tube('ts-metal',(xx,.24,.5),(xx,.56,.45),.025,6)
  B.face('ts-sling-paint',[G.p(-.3,.57,-.7),G.p(.3,.57,-.7),G.p(.3,.54,.45),G.p(-.3,.54,.45)],True)
  B.face('ts-sling-paint',[G.p(-.3,.54,.45),G.p(.3,.54,.45),G.p(.3,1.06,1.02),G.p(-.3,1.06,1.02)])
 for x,z in [(-19,4),(-3.5,3.5),(-3.5,21.5)]:
  F.lathe('ts-metal',x,z,[(.24,.25),(.30,.25),(.32,.035),(2.45,.035)],12)
  for i in range(12):
   a=i*math.tau/12;b=(i+1)*math.tau/12
   B.face('ts-sling-paint',[F.p(x,2.62,z),F.p(x+1.65*math.cos(a),2.22,z+1.65*math.sin(a)),F.p(x+1.65*math.cos(b),2.22,z+1.65*math.sin(b))])
 # Accessible lift observed in photo, fixed display geometry only.
 F.box('ts-blue',(-3.5,.68,14.5),(.55,.85,.6),True)
 F.path('ts-metal',[(-3.5,.65,14.5),(-4.2,1.25,14.5),(-5,1.1,14.5),(-5,.52,14.5)],.05,8)
 F.box('ts-blue',(-5,.5,14.5),(.55,.12,.5))
 # Two feather-frond palms observed beside the pool boundary; heights estimated.
 for px,pz,h in [(-19.7,2.3,6.8),(-2.5,1.9,7.7)]:
  F.lathe('ts-palm-bark',px,pz,[(.24,.22),(h*.55,.17),(h,.14)],12)
  F.box('ts-fence-collision',(px,h/2,pz),(.34,h,.34),True)
  B.groups.pop((B.property,B.source,'ts-fence-collision',B.detail))
  for j in range(20):
   a=j*2.39996;co,si=math.cos(a),math.sin(a);length=2.3+(j%4)*.23
   def stem(t):return (px+co*length*t,h+.65*math.sin(math.pi*t)-.6*t,pz+si*length*t)
   F.path('ts-palm-stem',[stem(t) for t in np.linspace(0,1,7)],.018,5)
   for k in range(1,13):
    t=k/14;c=stem(t);v=stem(min(1,t+.15));w=.52*math.sin(math.pi*t)+.08
    for side in [-1,1]:
     tip=(v[0]-si*w*side,v[1]-.16,v[2]+co*w*side)
     B.face('ts-palm-leaf' if j%3 else 'ts-palm-light',[F.p(*c),F.p(*tip),F.p(c[0]+co*.14,c[1]-.025,c[2]+si*.14)])
 return dict(name='Arrival to west pool terrace',points=[F.p(x,.24,z) for x,z in [(29,25.6),(29,28.2),(15,28.2),(0,28.2),(-12.3,28.2),(-12.3,24.6),(-18.8,24.6),(-20.5,20),(-20.5,5)]])
