"""Original Naked City Paradise exterior from mapped plan and public facade references."""
from common import *
KEY='nakedCity';ID='way/1042462823';YAW=math.atan2(18.479,-4.703)
def build(B):
 p=footprint(ID);F=Frame(B,1962.488,1119.529,YAW,y=0)
 B.property=KEY+'-exterior';B.source='podium/naked-city-paradise';B.detail=0
 B.shell(p,.08,6.6,'nc-stucco',roof=False);B.planar('nc-roof',p,6.6)
 # South return belongs to this mapped tenancy, adjoining the Office Bar frontage.
 # February2023 southern Street View shows a small shop opening and upper windows here.
 S=Frame(B,1969.431,1119.629,math.pi-math.atan2(.10,6.943),y=0)
 for u in [1.7,5.2]:
  S.box('nc-glass',(u,4.98,-.045),(.92,1.32,.05))
  for dx in [-.49,.49]:S.box('nc-frame',(u+dx,4.98,-.08),(.045,1.40,.055))
 for lo,hi in [(1.1,3.55),(3.65,5.3)]:
  mid=(lo+hi)/2;S.box('nc-glass',(mid,1.4,-.055),(hi-lo,2.20,.07))
  for u in [lo,hi]:S.box('nc-dark',(u,1.4,-.12),(.055,2.30,.08))
  for y in [.27,2.53]:S.box('nc-dark',(mid,y,-.12),(hi-lo,.055,.08))
 S.box('nc-concrete',(3.47,.08,-.65),(6.94,.16,1.3),True)
 # Four photographed upper openings along the oblique western elevation.
 for u in [2.1,6.3,12.7,17.0]:
  F.box('nc-glass',(u,4.6,-.045),(1.05,1.35,.05))
  for dx in [-.55,.55]:F.box('nc-frame',(u+dx,4.6,-.075),(.045,1.43,.055))
  for y in [3.90,5.30]:F.box('nc-frame',(u,y,-.075),(1.14,.045,.06))
 for y in [3.05,3.65,5.65]:F.box('nc-joint',(9.53,y,-.012),(19.06,.015,.018))
 F.text('naked city',(10,6.08,-.10),.40,'nc-red');F.text('PIZZA',(10,5.48,-.12),.74,'nc-red')
 # Closed glazed entry; no fictional room or open portal behind it.
 for u in [9.2,10.8]:
  F.box('nc-glass',(u,1.34,-.065),(1.48,2.26,.065))
  for du in [-.76,.76]:F.box('nc-dark',(u+du,1.34,-.12),(.055,2.37,.08))
  for y in [.17,2.51]:F.box('nc-dark',(u,y,-.12),(1.56,.055,.08))
  F.tube('nc-steel',(u+.55,.95,-.19),(u+.55,1.48,-.19),.018,10)
 # Rounded fabric canopy: quarter-cylinder roof over a straight valance.
 for i in range(16):
  a=i*math.pi/32;b=(i+1)*math.pi/32
  q=[(7.9,2.75+.65*math.sin(a),-.1-.95*math.cos(a)),(12.1,2.75+.65*math.sin(a),-.1-.95*math.cos(a)),(12.1,2.75+.65*math.sin(b),-.1-.95*math.cos(b)),(7.9,2.75+.65*math.sin(b),-.1-.95*math.cos(b))]
  B.face('nc-fabric',[F.p(*v) for v in q])
 F.box('nc-fabric',(10,2.60,-1.05),(4.2,.30,.055));F.text('4608',(10,2.57,-1.09),.28,'nc-letter')
 for u in [7.9,12.1]:
  B.face('nc-fabric',[F.p(u,2.45,-.1),F.p(u,2.45,-1.05)]+[F.p(u,2.75+.65*math.sin(a),-.1-.95*math.cos(a)) for a in np.linspace(0,math.pi/2,17)])
 # Long weathered side awnings and groundfloor glazing.
 for lo,hi in [(.7,7.5),(12.5,18.5)]:
  mid=(lo+hi)/2;w=hi-lo
  F.box('nc-glass',(mid,1.2,-.055),(w-.3,1.95,.07))
  for u in np.arange(lo,hi+.01,1.0):F.box('nc-dark',(u,1.2,-.12),(.06,2.05,.08))
  for y in [.2,2.23]:F.box('nc-dark',(mid,y,-.12),(w,.07,.08))
  B.face('nc-awning',[F.p(lo,2.85,-.04),F.p(hi,2.85,-.04),F.p(hi,2.05,-1.15),F.p(lo,2.05,-1.15)])
  for u in np.arange(lo,hi+.01,1.1):F.tube('nc-metal',(u,2.83,-.05),(u,2.03,-1.15),.018,8)
  F.tube('nc-metal',(lo,2.03,-1.15),(hi,2.03,-1.15),.025,8)
  for u in [lo,hi]:F.box('nc-dark',(u,1.1,-1.1),(.07,2.0,.07))
 # Timber patio screen at the northern bay, with open entry route.
 for u in [14.1,16.3,18.5]:F.box('nc-wood',(u,.95,-1.5),(.12,1.7,.12),True)
 for y in np.arange(.25,1.72,.20):F.box('nc-wood',(16.3,y,-1.5),(4.5,.16,.09),True)
 # Diagonal lattice in two groundfloor panels, behind awning edge.
 for lo,hi in [(1.0,3.3),(16.0,18.2)]:
  for direction in [-1,1]:
   for start in np.arange(lo-2,hi,.25):
    line=LineString([(start,0),(start+direction*2,2)])
    cut=line.intersection(box(lo,.25,hi,1.95))
    if cut.geom_type=='LineString' and not cut.is_empty:
     a,b=list(cut.coords)[0],list(cut.coords)[-1];F.tube('nc-wood',(a[0],a[1],-.16),(b[0],b[1],-.16),.018,4)
 # String-light cable and lamp lenses (geometry only, preserve fixed light pool).
 for lo,hi,z in [(.8,7.4,-1.17),(8,12,-1.09),(12.5,18.5,-1.17)]:
  pts=[(u,2.08-.12*math.sin((u-lo)/(hi-lo)*math.pi),z) for u in np.linspace(lo,hi,20)]
  F.path('nc-dark',pts,.009,6)
  for u in np.arange(lo,hi,.65):
   y=2.08-.12*math.sin((u-lo)/(hi-lo)*math.pi);F.tube('nc-dark',(u,y,z),(u,y-.09,z),.009,6);B.sphere('nc-bulb',F.p(u,y-.12,z),.025,8,5)
 for u in [2,6,14,18]:
  F.path('nc-steel',[(u,2.86,-.04),(u,3.35,-.04),(u,3.35,-.18)],.017,8)
  for du in [-.09,.09]:F.box('nc-lamp',(u+du,3.38,-.22),(.16,.12,.18))
 # Continuous paved approach matches the existing grade; no roadside regeneration.
 F.box('nc-concrete',(9.53,.08,-.85),(19.06,.16,1.7),True)
 for u in [8.15,11.85]:F.lathe('nc-metal',u,-1.35,[(.16,.055),(1,.055)],10)
 for u in [6.9,12.7]:
  F.lathe('nc-wood',u,-.65,[(.16,.28),(.22,.32),(.65,.35),(.76,.32)],16)
  for y in [.25,.62]:F.lathe('nc-metal',u,-.65,[(y,.35),(y+.035,.35)],16)
  F.lathe('nc-soil',u,-.65,[(.73,.29),(.75,.29)],16)
  # Low upright leaves, original geometric planting, kept within planter.
  for a in np.linspace(0,math.tau,12,endpoint=False):
   B.face('nc-leaf',[F.p(u,.74,-.65),F.p(u+.16*math.cos(a+.2),.79,-.65+.16*math.sin(a+.2)),F.p(u+.22*math.cos(a),1.16,-.65+.22*math.sin(a))])
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):B.tube('nc-frame',(a[0],6.63,a[1]),(b[0],6.63,b[1]),.04,6)
 B.box('nc-metal',(1965,6.9,1108),(1.6,.6,1.3));B.box('nc-dark',(1965,7.21,1108),(1.4,.02,1.1))
 routes=[dict(name='West entrance approach',points=[F.p(10,.08,-3),F.p(10,.16,-1.5),F.p(10,.16,-.5)])]
 return dict(key=KEY,name='Naked City Pizza Paradise',center=[1964,0,1110],bounds=list(p.bounds),structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=routes,hotelSources=[])
if __name__=='__main__':
 B=Meshes();meta=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(meta,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
