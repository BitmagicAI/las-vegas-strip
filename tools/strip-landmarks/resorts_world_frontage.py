"""Strip frontage fitted to Earth 2022-11-09 and Giroux built-work account.
Facade zones use mapped outline; elevations and stair rise are photo estimates.
No claim of completed interior connection at the raised retail entrance.
"""
from common import *
SURVEY_ROADS=json.load(open("build/strip-survey/survey.json"))["roads"]
def facade(B,F,L,nx,nz,mid,ident,h,patch):
 public=nx>.25 or nz>.65
 corner=ident=='way/972129019' and mid.x>655 and -1857<mid.y<-1815
 zouk=ident=='way/972129019' and mid.x>555 and mid.y>-1812
 patch('rw-stone',0,0,L,h)
 if corner:
  patch('rw-bronze',0,3.2,L,17.6,.30)
  for y in [3.1,7.1,11.1,15.1,17.65]:patch('rw-metal',0,y,L,y+.13,.39)
  for x in np.arange(.1,L,1.5):patch('rw-metal',x,3.2,min(x+.08,L),17.6,.39)
  patch('rw-white',0,18,L,h,.42)
 elif zouk:
  patch('rw-blue-panel',0,.5,L,19.5,.3)
  # Wrap-around screen on the separate southern block; original neutral artwork.
  patch('rw-shadow',.4,6.8,max(.5,L-.4),11.3,.36)
  for y in np.arange(1,19.5,3.1):patch('rw-joint',0,y,L,y+.045,.38)
 elif public:
  for x in np.arange(.7,L-1,6):
   patch('rw-bronze',x,.5,min(x+4.8,L-.3),6.7,.3)
   patch('rw-metal',x,.5,x+.12,6.7,.38)
  patch('rw-white',0,7.6,L,8.3,.39)
  B.detail=1
  # Projecting tapered upper fins; the old flat strips had no silhouette or shadow.
  for i,x in enumerate(np.arange(.8,L-.5,2.6)):
   bottom=10+(i%4)*1.0;top=h-.5
   B.face('rw-fin',[F.p(x,bottom,-.36),F.p(x+.14,bottom,-.36),F.p(x+.14,top,-.65),F.p(x,top,-.65)])
   B.face('rw-shadow',[F.p(x,bottom,-.1),F.p(x,bottom,-.36),F.p(x,top,-.65),F.p(x,top,-.1)])
  B.detail=0
  if ident=='way/972129019' and L>45 and mid.x>680:
   for x in np.arange(7,L-6,18):
    F.box('rw-red',(x,6.6,-.9),(7.4,.38,1.8))
    F.box('rw-white',(x,7.6,-.15),(8.1,1.8,.42))
 else:
  for y in np.arange(1.2,h,2):patch('rw-joint',0,y,L,y+.02,.25)
 patch('rw-white',0,h-.3,L,h,.4)
def entry(B):
 B.source='rw-street-entry';B.detail=0
 # North-facing local frame has its outward direction toward the Strip (east).
 F=Frame(B,685.1,-1901.9,math.atan2(-49.46,-27.563),y=0)
 for x in [-5.9,5.9]:F.box('rw-red',(x,10.0,-1.1),(1.1,20,2.3),True)
 F.box('rw-red',(0,19.45,-1.1),(12.9,1.1,2.3),True)
 # Existing opaque podium is the backing; glazing and portal remain exterior only.
 F.box('rw-bronze',(0,11.4,-.33),(10.7,15.2,.14))
 for y in [4.0,7.8,11.6,15.4,18.9]:F.box('rw-metal',(0,y,-.44),(10.7,.10,.12))
 for x in [-4.3,-2.15,0,2.15,4.3]:F.box('rw-metal',(x,11.4,-.44),(.085,15.2,.12))
 F.text('RESORTS WORLD',(0,6.1,-.55),.44,'rw-white')
 # Walkable approach, visual treads over one continuous collision ramp.
 F.box('rw-paving',(0,3.1,-3),(10,.4,4.6),True)
 F.box('rw-paving',(0,-.1,-41.25),(9,.2,1.0),True)
 F.stairs(0,-41,9,3.3,36,y=0)
 # Only north-side planter: south-side counterpart encroached on mapped service lane.
 for side in [-1]:
  F.box('rw-planter',(side*7.4,1.0,-4),(2.8,2,4.4),True)
  F.box('rw-soil',(side*7.4,2.015,-4),(2.55,.03,4.1))
 # Rounded pavilion's red ground portal; stays within its mapped eastern facade.
 P=Frame(B,688,-1837,-math.pi/2,y=0)
 for x in [-3,3]:P.box('rw-red',(x,3,-.5),(.75,6,1))
 P.box('rw-red',(0,5.65,-.5),(6.75,.7,1))
 # Tall slit accents on the pale side panel north of the bronze corner.
 S=Frame(B,679,-1860,-math.pi/2,y=0)
 for x in [-8,-5,-2,1]:S.box('rw-shadow',(x,12,-.3),(.5,8-(x+8)*.25,.12))

 # Forecourt islands follow the photographed triangular lawns / oval plaza.
 # Dimensions inferred from mapped pedestrian edges, clipped away from circulation.
 B.source='rw-street-gardens'
 roads=unary_union([LineString([(x,-z) for x,z in r['points']]).buffer(9 if r['class']=='primary' else 4.8 if r['class']=='service' else 2.3) for r in SURVEY_ROADS if r['class'] in ['primary','service','footway']])
 site=footprint('way/972129019').buffer(2)
 for outline in [[(695,-1905),(739,-1887),(758,-1939)],[(751,-2018),(806,-2016),(777,-1968)]]:
  q=Polygon(outline).difference(site).difference(roads)
  B.planar('rw-paving',q,.10,True)
  for z in np.arange(q.bounds[1]+2,q.bounds[3],10):
   lawn=q.buffer(-1.4).intersection(box(660,z,830,z+4.2))
   B.shell(lawn,.10,.23,'rw-planter',roof=False)
   B.planar('rw-garden',lawn,.23,True)
 plaza=scale(Point(746,-1959).buffer(1,resolution=48),22,15).difference(site).difference(roads)
 B.planar('rw-paving',plaza,.12,True)
