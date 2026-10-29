"""Original Home2 courtyard; aerial-estimated bounds, not a surveyed pool plan."""
from common import *
def add_pool(B,F):
 B.property='home2-stadium-exterior';B.source='podium/home2-stadium'
 # Map-picked centre36.099977,-115.182033 -> local(11.11,-6.96).
 # Keep all new terrace geometry within x1..21,z-14..-.5, before garage x22.2.
 outline=[]
 for a in np.linspace(0,math.tau,97)[:-1]:
  indent=1-.21*math.exp(-((a-math.pi)/.52)**2)
  outline.append((11.1+6.6*math.cos(a)*indent,-7+4.15*math.sin(a)))
 basin=F.poly(outline);deck=F.poly([(1,-.5),(21,-.5),(21,-14),(1,-14)])
 B.planar('h2-paving',deck.difference(basin.buffer(.28)),.24,True)
 B.planar('h2-counter',basin.buffer(.28).difference(basin),.27,True)
 B.shell(deck,.015,.24,'h2-stone',roof=False,solid=True)
 B.shell(basin,.015,.27,'h2-pool-tile',roof=False,solid=True)
 B.planar('h2-pool-tile',basin,.018,True);B.planar('h2_pool',basin,.13)
 # Continuous reachable deck via the existing east-side aisle. No shared road edits.
 approach=F.poly([(20,-.5),(70,-.5),(70,-2),(24,-2),(24,-4),(20,-4)])
 B.planar('h2-paving',approach,.24,True);B.shell(approach,.01,.24,'h2-paving',roof=False)
 def fence(a,b):
  L=math.dist(a,b);G=Frame(B,*F.p(*[a[0],0,a[1]])[::2],F.yaw-math.atan2(b[1]-a[1],b[0]-a[0]),y=0)
  # Visual pickets have actual gaps; a separate thin solid controls collision.
  for y in [.40,1.78]:G.box('h2-charcoal-paint',(L/2,y,0),(L,.085,.09))
  for u in np.arange(.06,L,.19):G.box('h2-charcoal-paint',(float(u),1.08,0),(.09,1.40,.055))
  for u in np.linspace(0,L,max(2,math.ceil(L/2.5)+1)):G.box('h2-charcoal-paint',(float(u),1.03,0),(.075,1.57,.075))
 # Fence collision is exported separately from the visible pickets.
 for a,b in [((1,-.5),(1,-14)),((1,-14),(21,-14)),((21,-14),(21,-4)),((21,-2),(21,-.5))]:
  fence(a,b)
  line=LineString([F.p(a[0],0,a[1])[::2],F.p(b[0],0,b[1])[::2]])
  B.shell(line.buffer(.035,cap_style=2),.24,1.75,'h2-fence-collision',roof=False,solid=True)
 # North shared-drive frontage: stone end piers and continuous high beam visible
 # in March2020 Street View. Dimensions estimated from the adjacent storey.
 for z in [-.5,-14]:
  F.box('h2-stone',(1,1.64,z),(.55,2.8,.55),True)
  F.box('h2-counter',(1,3.08,z),(.63,.08,.63))
 F.box('h2-charcoal-paint',(1,2.98,-7.25),(.19,.22,13.55))
 # Blue-tile waterfall and paired planters on the far edge, as in official photo.
 F.box('h2-pool-tile',(11.1,.90,-11.24),(2.5,1.32,.46),True)
 F.box('h2-counter',(11.1,1.59,-11.24),(2.65,.11,.58))
 for x in [9.25,12.95]:
  F.box('h2-pool-tile',(x,.49,-11.24),(1.15,.50,.73),True);F.box('h2-counter',(x,.77,-11.24),(1.24,.09,.82))
  F.box('h2-soil',(x,.82,-11.24),(.98,.02,.58))
  for dx in [-.3,0,.3]:
   for dz in [-.17,.17]:F.lathe('h2-leaf',x+dx,-11.24+dz,[(.82,.025),(.97,.11),(1.06,.01)],7)
 # Tile grout is real shallow offset trim; no coplanar duplicate planes.
 for x in np.arange(9,13.3,.18):F.box('h2-grout',(float(x),.49,-10.995),(.008,.48,.012))
 for x in np.arange(9.9,12.35,.18):F.box('h2-grout',(float(x),.9,-10.995),(.008,1.28,.012))
 for y in np.arange(.34,1.55,.18):F.box('h2-grout',(11.1,float(y),-10.992),(2.48,.008,.012))
 # Stainless handrails and blue accessibility lift at the shallow west end.
 for z in [-5.7,-6.6]:F.path('h2-metal',[(5.2,.25,z),(5.2,1.05,z),(5.5,1.2,z),(6.1,1.05,z),(6.6,.2,z)],.035,12)
 F.lathe('h2-lift-blue',4,-5.0,[(.24,.27),(.60,.27),(.67,.21)],24)
 F.tube('h2-counter',(4,.6,-5),(4,2.25,-5),.065,12)
 F.tube('h2-counter',(4,2.25,-5),(5,1.35,-5),.055,12)
 F.box('h2-lift-blue',(5,.62,-5),(.5,.09,.48));F.box('h2-lift-blue',(4.78,.92,-5),(.08,.58,.48))
 # Pergola at the north end, clear of the pool coping and circulation.
 for x in [2.2,5.6]:
  for z in [-10.7,-13.1]:F.box('h2-charcoal-paint',(x,1.58,z),(.14,2.68,.14),True)
 for z in [-10.6,-13.2]:F.box('h2-charcoal-paint',(3.9,2.9,z),(3.9,.18,.15))
 for x in np.arange(2,5.9,.30):F.box('h2-charcoal-paint',(float(x),3.03,-11.9),(.095,.16,3.0))
 for x,z in [(3.7,-12),(18.9,-11.8),(18.9,-7)]:
  # Folded canvas umbrella: articulated narrow profile, within table collision.
  F.tube('h2-metal',(x,.24,z),(x,2.85,z),.024,8)
  F.lathe('h2-red-canvas',x,z,[(1.55,.04),(1.75,.16),(2.10,.10),(2.35,.19),(2.63,.11),(2.77,.025)],12)
  F.lathe('h2-charcoal-paint',x,z,[(2.08,.105),(2.13,.105)],12)
  F.box('h2-furniture-collision',(x,.62,z),(.80,.76,.80),True)
  F.lathe('h2-counter',x,z,[(.24,.30),(.28,.30),(.29,.045),(.95,.045),(1,.42)],20)
  for dx in [-.75,.75]:
   F.box('h2-furniture-collision',(x+dx,.72,z),(.46,.96,.48),True)
   F.box('h2-yellow-fabric',(x+dx,.69,z),(.46,.09,.48));F.box('h2-yellow-fabric',(x+dx,1,z+.20),(.46,.55,.06))
   for u in [-.18,.18]:
    for v in [-.18,.18]:F.tube('h2-metal',(x+dx+u,.24,z+v),(x+dx+u,.64,z+v),.023,6)
 for key in list(B.groups):
  if B.groups[key]['material'] in ['h2-fence-collision','h2-furniture-collision']:del B.groups[key]
 # Materials/collision proxies are separated by exporter, no runtime invisible meshes.
 return [dict(name='Pool courtyard approach',points=[F.p(x,.24,z) for x,z in [(70,-1.2),(60,-1.2),(40,-1.2),(23,-1.2),(23,-3),(20.4,-3),(20.4,-5)]]),dict(name='Pool deck circuit',points=[F.p(x,.24,z) for x,z in [(20.4,-5),(20.4,-9),(16,-12.5),(7,-12.5),(1.6,-9),(1.6,-2),(17,-2),(20.4,-3)]])]
