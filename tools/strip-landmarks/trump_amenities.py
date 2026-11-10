"""Trump pool length correction and original photo-fitted deck amenities."""
from common import *
KEY='trumpAmenities'
Y=16.04
POOL=box(31.5-16.764,-1485,31.5+16.764,-1474)
OLD=box(6,-1485,57,-1474)
def build(B):
 B.property=KEY+'-exterior';B.source='trump-pool-amenities';B.detail=0
 def lounger(x,z,yaw):
  F=Frame(B,x,z,yaw,y=Y)
  F.box('wga-blue-fabric',(0,.42,0),(.75,.12,1.8));F.box('wga-white-paint',(0,.2,0),(.55,.4,1.5),True)
  B.face('wga-blue-fabric',[F.p(-.375,.48,-.4),F.p(.375,.48,-.4),F.p(.375,.95,-.95),F.p(-.375,.95,-.95)])
  for xx in [-.36,.36]:F.path('wga-white-paint',[(xx,.46,.85),(xx,.46,-.4),(xx,.95,-.95)],.025,6)
 def palm(x,z,i):
  h=6+i%3
  B.lathe('wga-bark',(x,z),[(Y,.23),(Y+h,.11)],12);B.box('wga-bark',(x,Y+h/2,z),(.3,h,.3),True)
  for j in range(12):
   a=j*math.tau/12+i*.4;ps=[]
   for k in range(7):
    t=k/6;r=3*t;yy=Y+h+1.2*math.sin(t*math.pi)-t;w=.32*math.sin(t*math.pi)
    ps.append([(x+r*math.cos(a)-w*math.sin(a),yy,z+r*math.sin(a)+w*math.cos(a)),(x+r*math.cos(a)+w*math.sin(a),yy,z+r*math.sin(a)-w*math.cos(a))])
   for k,(a,b) in enumerate(zip(ps,ps[1:])):
    B.face('wga-leaf',[a[0],b[1],b[0]] if k==0 else [a[0],a[1],b[0]] if k==5 else [a[0],a[1],b[1],b[0]])
  B.lathe('wga-planter',(x,z),[(Y,.8),(Y+.5,.8)],16)

 # Fill the old overlong pool ends without touching the surrounding podium.
 B.planar('wga-deck',OLD.difference(POOL.buffer(.5)),Y,True)
 B.planar('wga-white-paint',POOL.buffer(.5).difference(POOL),16.1,True)
 B.planar('trump_pool',POOL,15.83)
 B.planar('wga-pool-tile',POOL,14.5,True)
 B.shell(POOL,14.5,16.1,'wga-pool-tile',roof=False,solid=True)
 # Navy awning follows the photographed tower-side terrace, open underneath.
 for x in range(4,61,8):
  B.face('wga-blue-fabric',[(x,20,-1496),(x+8,20,-1496),(x+8,18.7,-1492.5),(x,18.7,-1492.5)])
  B.box('wga-blue-fabric',(x+4,18.55,-1492.5),(8,.3,.06))
  B.tube('wga-white-paint',(x,Y,-1495.8),(x,20,-1495.8),.055,8)
 for x in range(12,54,3):lounger(x,-1490,0)
 for x in [8,11,54,57]:
  for z in [-1476,-1480,-1484]:lounger(x,z,math.pi/2 if x<20 else -math.pi/2)
 # Reduced planted south border leaves the east/west end passages clear.
 B.box('wga-planter',(31.5,Y+.45,-1469.2),(43,.9,1.8),True)
 B.box('wga-soil',(31.5,Y+.91,-1469.2),(42.7,.04,1.5))
 for i,x in enumerate([13,19,25,31,37,43,49]):palm(x,-1469.2,i)
 for x in range(12,52,3):
  B.lathe('wga-leaf',(x,-1469.2),[(Y+.93,.55),(Y+1.55,.7),(Y+1.9,.25)],10)
 # End-entry handrails and closed navy parasols as in the reference.
 for x in [15.2,47.8]:
  for z in [-1477.5,-1481.5]:B.path('wga-white-paint',[(x,14.6,z),(x,17,z),(x+(1.6 if x>30 else -1.6),17,z),(x+(1.6 if x>30 else -1.6),Y,z)],.045,8)
 for x in [15,24,33,42,51]:
  B.tube('wga-white-paint',(x,Y,-1491.7),(x,Y+2.6,-1491.7),.035,8)
  B.lathe('wga-blue-fabric',(x,-1491.7),[(Y+.8,.3),(Y+2.4,.1),(Y+2.7,.02)],12)
 # Boundary rail behind the south planting; no invented doorway connection.
 for x in range(0,65,2):B.box('wga-white-paint',(x,Y+.6,-1465),(.07,1.2,.07),True)
 B.tube('wga-white-paint',(0,Y+1.2,-1465),(64,Y+1.2,-1465),.045,8)
 routes=[{'name':'north-deck','points':[[10,Y,-1487.3],[54,Y,-1487.3]]},{'name':'south-deck','points':[[10,Y,-1472],[54,Y,-1472]]},{'name':'west-pool-end','points':[[13,Y,-1487],[13,Y,-1472]]},{'name':'east-pool-end','points':[[50,Y,-1487],[50,Y,-1472]]}]
 Path('docs/project-records/trump-amenities/routes.json').write_text(json.dumps(routes,indent=2)+'\n')
 return dict(poolLength=33.528,poolWidth=11,loungers=26,palms=7,uncertainty='Official110ft length; width/elevation retained, furniture density and awning dimensions inferred. Arrival and cabana interiors deferred.')
if __name__=='__main__':
 B=Meshes();d=build(B);B.save_all();d['triangles']=sum(len(g['faces']) for g in B.groups.values());Path('docs/project-records/trump-amenities/geometry.json').write_text(json.dumps(d,indent=2)+'\n');print(d)
