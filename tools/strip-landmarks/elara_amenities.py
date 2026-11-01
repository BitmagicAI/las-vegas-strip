"""Original Elara terrace geometry fitted to linked official photographs; dimensions inferred."""
from common import *
from elara_exterior import tower_shape
from shapely.geometry import shape
KEY='elaraAmenities';Y=.31;UP=3.51

def build(B):
 B.property=KEY+'-exterior';B.source='elara-pool-amenities';B.detail=0
 blocked=unary_union([shape(f['geometry']).buffer(.5) for f in json.load(open('build/geographic-strip/surface-layers.geojson'))['features'] if f['properties']['kind'] in ['road','sidewalk']])
 deck=box(309,815,365,852).difference(blocked).difference(tower_shape())
 pool=Polygon([(323,826),(329,826),(329,823),(341,823),(341,826),(348,826),(348,830),(351,830),(351,839),(348,839),(348,844),(334,844),(334,842),(325,842),(325,838),(322,838),(322,830),(323,830)]).intersection(deck.buffer(-.5))
 B.planar('ela-deck',deck.difference(pool),Y,True)
 B.planar('ela-coping',pool.buffer(.4).difference(pool),Y+.04,True)
 B.planar('elara_pool',pool,.24);B.planar('ela-pool-tile',pool,.02,True)
 B.shell(pool,.02,.31,'ela-pool-tile',roof=False,solid=True)
 # West and south upper galleries with a clear continuous pedestrian strip.
 upper=box(309,819,313.4,852).union(box(309,849,360,852)).intersection(deck)
 B.planar('ela-deck',upper,UP,True);B.planar('ela-soffit',upper,UP-.25)
 B.shell(upper,UP-.25,UP,'ela-soffit',roof=False,solid=False)
 for x,z in [(310,822),(310,833),(310,849),(321,851),(333,851),(345,851),(357,851)]:B.box('ela-post',(x,(Y+UP)/2,z),(.24,UP-Y,.24),True)
 def rail(points,y):
  B.path('ela-post',[(x,y+1.1,z) for x,z in points],.035,6)
  for a,b in zip(points,points[1:]):
   B.face('ela-rail-glass',[(a[0],y+.08,a[1]),(b[0],y+.08,b[1]),(b[0],y+1.05,b[1]),(a[0],y+1.05,a[1])],True)
   for t in np.linspace(0,1,max(2,math.ceil(math.dist(a,b)/2)+1)):
    x=a[0]+(b[0]-a[0])*t;z=a[1]+(b[1]-a[1])*t;B.box('ela-post',(x,y+.55,z),(.045,1.1,.045))
 rail([(313.4,819),(309,819),(309,852),(360,852),(360,849)],UP)
 rail([(313.4,819),(313.4,843.7)],UP);rail([(313.4,847),(313.4,849),(360,849)],UP)
 # Spiral stair: original visible treads, continuous hidden collision surface.
 cx,cz=316,845.4;ri,ro=1.7,3;N=32
 def p(a,r,y):return (cx+r*math.cos(a),y,cz+r*math.sin(a))
 stair=[]
 for i in range(N+1):
  a=-math.pi/2+1.5*math.pi*i/N;y=Y+(UP-Y)*i/N;stair.append(p(a,2.35,y))
 for i in range(N):
  a=-math.pi/2+1.5*math.pi*i/N;b=-math.pi/2+1.5*math.pi*(i+1)/N;lo=Y+(UP-Y)*i/N;hi=Y+(UP-Y)*(i+1)/N
  B.upface('ela-stair',[p(a,ri,lo),p(a,ro,lo),p(b,ro,hi),p(b,ri,hi)],True)
  B.upface('ela-stair',[p(a,ri,hi+.01),p(a,ro,hi+.01),p(b,ro,hi+.01),p(b,ri,hi+.01)])
  B.face('ela-soffit',[p(a,ri,lo),p(a,ro,lo),p(a,ro,hi),p(a,ri,hi)])
 for r in [ri,ro]:
  pts=[p(-math.pi/2+1.5*math.pi*i/N,r,Y+(UP-Y)*i/N+1.05) for i in range(N+1)];B.path('ela-post',pts,.04,6)
  for i in range(0,N+1,2):
   a=-math.pi/2+1.5*math.pi*i/N;y=Y+(UP-Y)*i/N;B.tube('ela-post',p(a,r,y),p(a,r,y+1.05),.035,6)
 B.planar('ela-deck',box(312.5,844.7,313.72,846.1),UP,True)
 def chair(x,z,y,yaw=0):
  F=Frame(B,x,z,yaw,y=y);F.box('ela-cushion',(0,.42,0),(.7,.12,1.8));F.box('ela-post',(0,.2,0),(.55,.4,1.4),True)
  B.face('ela-cushion',[F.p(-.35,.48,-.35),F.p(.35,.48,-.35),F.p(.35,.92,-.9),F.p(-.35,.92,-.9)])
 def palm(x,z,y,i):
  h=5.5+i%3;B.lathe('ela-bark',(x,z),[(y,.2),(y+h,.11)],10);B.box('ela-bark',(x,y+h/2,z),(.3,h,.3),True)
  for j in range(10):
   a=j*math.tau/10+i;ps=[]
   for k in range(7):
    t=k/6;r=2.6*t;yy=y+h+math.sin(t*math.pi)-t;w=.3*math.sin(t*math.pi)
    ps.append([(x+r*math.cos(a)-w*math.sin(a),yy,z+r*math.sin(a)+w*math.cos(a)),(x+r*math.cos(a)+w*math.sin(a),yy,z+r*math.sin(a)-w*math.cos(a))])
   for k,(a,b) in enumerate(zip(ps,ps[1:])):B.face('ela-leaf',[a[0],b[1],b[0]] if k==0 else [a[0],a[1],b[0]] if k==5 else [a[0],a[1],b[1],b[0]])
  B.lathe('ela-planter',(x,z),[(y,.65),(y+.45,.65)],12)
 # Yellow tension sails over south cabanas, open toward the pool.
 for x in [319,325,331,337,343,349,355]:
  for xx in [x-2.3,x+2.3]:
   for z in [849.2,851.7]:B.box('ela-post',(xx,UP+1.35,z),(.08,2.7,.08),True)
  corners=[(x-2.3,UP+2.7,849.2),(x+2.3,UP+2.7,849.2),(x+2.3,UP+2.7,851.7),(x-2.3,UP+2.7,851.7)]
  for a,b in zip(corners,corners[1:]+corners[:1]):B.face('ela-yellow-fabric',[a,b,(x,UP+2.15,850.45)])
  B.box('ela-cushion',(x,UP+.4,851.1),(2.6,.3,.8),True)
 # Lower north cabanas follow the photographed curved gallery in simplified bays.
 for x in [318,325,332,339,346,353]:
  B.box('ela-soffit',(x,2.9,817.3),(5.6,.22,3.6))
  for xx in [x-2.7,x+2.7]:B.box('ela-post',(xx,1.6,819),(.12,2.6,.12),True)
  B.box('ela-curtain',(x,1.6,815.6),(5.5,2.6,.05))
  chair(x-.7,817.3,Y);chair(x+.7,817.3,Y)
 for x in range(326,349,3):chair(x,847,Y,math.pi)
 for z in [827,830,833,836,839]:chair(355,z,Y,-math.pi/2)
 # Southeast circular pavilion, open colonnade.
 cxp,czp=360,844
 for a in np.linspace(0,math.tau,9)[:-1]:
  x=cxp+2.7*math.cos(a);z=czp+2.7*math.sin(a);B.box('ela-post',(x,Y+1.5,z),(.18,3,.18),True)
 B.lathe('ela-soffit',(cxp,czp),[(Y+2.9,3.2),(Y+3.15,3.2),(Y+3.35,.2)],24)
 for i,(x,z) in enumerate([(318,822),(320,839),(353,822),(358,837),(362,849),(310.5,824),(310.5,836)]):palm(x,z,UP if x<313 else Y,i)
 # Spa inset on the lower west gallery; size and location are estimates.
 spa=box(315,830,319,834);B.planar('ela-coping',spa.buffer(.3).difference(spa),.65,True);B.planar('elara_pool',spa,.56);B.planar('ela-pool-tile',spa,Y,True);B.shell(spa,Y,.65,'ela-pool-tile',roof=False,solid=True)
 routes=[dict(name='west-access',points=[[321.2,Y,821],[321.2,Y,842],[316,Y,842],[316,Y,843.05]]),dict(name='south-lower',points=[[321,Y,848.2],[353,Y,848.2]]),dict(name='east-lower',points=[[353,Y,825],[353,Y,844]]),dict(name='north-lower',points=[[321,Y,821],[349,Y,821]]),dict(name='spiral',points=[list(q) for q in stair]+[[311.8,UP,845.4],[311.8,UP,850.1],[314,UP,850.1]]),dict(name='upper-south',points=[[314,UP,850.1],[358,UP,850.1]]),dict(name='upper-west',points=[[311.8,UP,845.4],[311.8,UP,839]])]
 Path('docs/project-records/elara-amenities/routes.json').write_text(json.dumps(routes,indent=2)+'\n')
 return dict(cabanas=13,loungers=25,palms=7,upperDeckM=UP,spiralRiseM=UP-Y,uncertainty='Dimensions/elevations/layout inferred; full 33-cabana program, second spa, exact curved north gallery and street podium remain incomplete.')
if __name__=='__main__':
 B=Meshes();d=build(B);B.save_all();d['triangles']=sum(len(g['faces']) for g in B.groups.values());Path('docs/project-records/elara-amenities/geometry.json').write_text(json.dumps(d,indent=2)+'\n');print(d)
