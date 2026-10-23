"""Oasis exterior: Earth 2022 plan + current official pool photograph/map.
Plan fitted to surveyed pavilion anchors; pool boundaries and .64m deck estimated.
No existing bridge, interiors, city road geometry or terrain are regenerated.
"""
from common import *
Y=.64
def plans():
 north=Polygon([(-417,2200),(-391,2200),(-391,2210),(-384,2210),(-384,2220),(-403,2220),(-403,2211),(-417,2211)])
 main=unary_union([box(-429,2251,-411,2309),box(-431,2263,-384,2299),box(-402,2254,-385,2310),Point(-379,2250).buffer(12,quad_segs=24),box(-398,2250,-379,2275)])
 return north,main

def exterior(B):
 B.property='luxorExterior-exterior';B.source='luxor-oasis-deck';B.detail=0
 north,main=plans();water=unary_union([north,main]);pavilion=footprint('way/118344871')
 ground=box(-441,2189,-354,2319).difference(pavilion)
 # Keep existing approach pavilion collision and deck. Pools extend beneath its bridge.
 pools=water.difference(pavilion.buffer(.4));deck=ground.difference(pools.buffer(.65))
 B.planar('luxor-pool-paving',deck,Y,True)
 B.shell(ground,.24,Y,'luxor-stone',roof=False,solid=False)
 B.planar('luxor-pool-tile',pools,.27)
 B.planar('luxor_pool',pools,.43)
 B.planar('luxor-stone',pools.buffer(.65).difference(pools),Y+.025,True)
 B.shell(pools,.27,Y,'luxor-pool-tile',roof=False)
 # Low boundary wall and a gateway toward the documented north pool entrance.
 for a,b in [((-440,2190),(-440,2318)),((-440,2318),(-367,2318)),((-440,2190),(-364,2190))]:
  L=math.dist(a,b);B.box('luxor-stone',((a[0]+b[0])/2,1.15,(a[1]+b[1])/2),(L if a[1]==b[1] else .35,1.0,L if a[0]==b[0] else .35),True)
 B.source='luxor-oasis-colonnade'
 for z in np.arange(2197,2225,4):
  B.lathe('luxor-stone',(-433,z),[(Y,.9),(Y+.3,.9),(Y+.5,.59),(6.5,.56),(6.8,.76),(7.2,1.08),(7.65,1.18),(7.9,1.18)],24)
  B.box('luxor-band',(-433,8.03,z),(2.5,.3,2.5))
  for yy in [6.5,6.7,6.9]:B.lathe('luxor-band',(-433,z),[(yy,.8),(yy+.07,.8)],24)
  for a in np.linspace(0,math.tau,12,endpoint=False):
   B.tube('luxor-band',(-433+.6*math.cos(a),6.8,z+.6*math.sin(a)),(-433+1.1*math.cos(a),7.7,z+1.1*math.sin(a)),.045,5)
  B.box('luxor-stone',(-433,4,z),(1,6.7,1),True)
 B.box('luxor-stone',(-433,8.35,2210),(3.2,.4,30))
 B.source='luxor-oasis-furniture'
 # Repeated furniture shares four materials and is batched with the resort.
 for z in np.arange(2194,2315,3.1):
  for x in [-436,-425,-420,-411,-406,-397,-392,-383,-378,-361]:
   pad=box(x-.55,z-1.2,x+.55,z+1.2)
   if not deck.buffer(-1.5).contains(pad) or abs(z-2287)<5 or (x<-429 and z<2227):continue
   F=Frame(B,x,z,0,Y)
   F.box('luxor-chair-frame-paint',(0,.28,0),(.8,.12,2.1));F.box('luxor-chair-cushion',(0,.39,-.28),(.73,.1,1.4))
   B.face('luxor-chair-cushion',[F.p(-.36,.44,.4),F.p(.36,.44,.4),F.p(.36,.95,1),F.p(-.36,.95,1)])
   for xx in [-.33,.33]:F.box('luxor-chair-frame-paint',(xx,.15,0),(.06,.3,1.6))
 for z in [2196,2203,2210,2217,2235,2242,2307]:
  x=-358
  for xx in [-1.7,1.7]:
   for zz in [-1.7,1.7]:B.box('luxor-chair-frame-paint',(x+xx,Y+1.5,z+zz),(.1,3,.1))
  B.box('luxor-cabana-fabric',(x,Y+2.9,z),(3.8,.15,3.8))
  B.box('luxor-cabana-fabric',(x+1.7,Y+1.5,z),(.05,2.8,3.3))
  B.box('luxor-chair-cushion',(x,Y+.45,z+.9),(2.6,.4,1.2))
 # Separate small bar building on the surveyed plan is retained, now articulated.
 p=footprint('way/1126368992');B.source='luxor-oasis-bar'
 B.shell(p,.24,3.9,'luxor-stone',roof=False);B.planar('luxor-membrane-paint',p,3.9)
 for x in np.arange(p.bounds[0]+1.5,p.bounds[2]-1,3):
  B.box('luxor-glass',(x,2.1,p.bounds[1]-.08),(2.2,1.8,.12))
  B.box('luxor-band',(x,1.2,p.bounds[1]-.3),(2.4,.15,.7))
 return ['way/1126368992']
