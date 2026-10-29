"""Original Piranha exterior. Metres; mapped footprint, 2025 street and aerial references."""
from common import *
KEY='piranha';ID='way/1017043834'
def build(B):
 p=footprint(ID);B.property=KEY+'-exterior';B.source='podium/piranha';B.detail=0
 B.shell(p,.04,4.35,'ph-mortar',roof=False);B.planar('ph-roof',p,4.35)
 # Current east frontage, north at the right when viewed from Paradise Road.
 E=Frame(B,1920.205,1152.491,-math.pi/2,y=0)
 N=Frame(B,1901.32,1152.157,-.0177,y=0)
 rng=random.Random(248)
 # Original irregular ashlar courses: batched shallow prisms, no per-stone colliders.
 for F,length in [(E,34.18),(N,18.89)]:
  for row in range(15):
   lo=row*.28+.07;u=0
   while u<length-.04:
    w=min(rng.uniform(.42,1.05),length-.025-u)
    if w<.03:break
    F.box('ph-stone'+str(rng.randrange(4)),(u+w/2,lo+.125,-.035),(w-.022,.25,rng.uniform(.045,.07)))
    u+=w
 # Flat roof with narrow tiled pitched skirts, matching aerial rather than a full gable.
 for F,length in [(E,34.18),(N,18.89)]:
  B.face('ph-tile',[F.p(0,4.30,-.20),F.p(length,4.30,-.20),F.p(length,4.74,1.25),F.p(0,4.74,1.25)])
  for u in np.arange(.09,length,.24):
   F.tube('ph-tile-ridge',(u,4.32,-.20),(u,4.76,1.25),.065,8)
  F.box('ph-trim',(length/2,4.22,-.13),(length,.17,.18))
 # East entrance and red barrel canopy; closed leaves until interior layout is verified.
 E.box('ph-dark',(6.3,1.35,-.11),(1.7,2.6,.14))
 for u in [5.45,6.3,7.15]:E.box('ph-metal',(u,1.35,-.21),(.05,2.6,.07))
 for u in [6.13,6.47]:E.tube('ph-metal',(u,1.05,-.28),(u,1.5,-.28),.02,10)
 for i in range(20):
  a=i*math.pi/20;b=(i+1)*math.pi/20
  B.face('ph-canopy',[E.p(6.3+1.7*math.cos(a),2.9+.65*math.sin(a),z) for z in [-.25,-2.4]]+[E.p(6.3+1.7*math.cos(b),2.9+.65*math.sin(b),z) for z in [-2.4,-.25]])
 B.face('ph-canopy',[E.p(6.3+1.7*math.cos(a),2.9+.65*math.sin(a),-2.41) for a in np.linspace(0,math.pi,25)])
 E.text('Piranha',(6.3,3.13,-2.45),.32,'ph-letter')
 for u in np.arange(.65,3.6,.48):
  E.lathe('ph-bollard',u,-1.15,[(.08,.045),(.95,.045)],10)
  E.lathe('ph-letter',u,-1.15,[(.70,.047),(.80,.047)],10)
 for u in [4.6,8.0]:E.tube('ph-metal',(u,.04,-2.35),(u,2.93,-2.35),.035,10)
 E.box('ph-canopy',(6.3,2.83,-2.4),(3.4,.20,.04));E.text('NIGHTCLUB',(6.3,2.60,-.24),.18,'ph-letter')
 # Shuttered windows observed in dated elevations; setback avoids coplanar cladding.
 for F,us in [(E,[11.0]),(N,[5.0,13.0])]:
  for u in us:
   F.box('ph-glass',(u,2.05,-.12),(1.15,1.15,.10))
   for du in [-.82,.82]:
    F.box('ph-wood',(u+du,2.05,-.19),(.42,1.24,.10))
    for y in np.arange(1.49,2.65,.12):F.box('ph-wood-light',(u+du,y,-.25),(.39,.035,.035))
   for du in [-.60,.60]:F.box('ph-trim',(u+du,2.05,-.2),(.06,1.28,.07))
 # North fish-sign silhouette, authored polygons, not copied photograph pixels.
 N.box('ph-purple',(15.7,3.13,-.14),(2.7,1.12,.1));N.text('PIRANHA',(15.7,2.93,-.21),.31,'ph-letter')
 fish=[(-.8,0),(-.35,.35),(.38,.32),(.68,.12),(1,.38),(.87,0),(1,-.38),(.68,-.12),(.38,-.32),(-.35,-.35)]
 B.face('ph-letter',[N.p(15.7+x,3.38+y*.5,-.22) for x,y in fish])
 # Photographed small east notices use original venue wording, no transient event artwork.
 E.box('ph-purple',(2.3,2.0,-.14),(1.1,1.7,.09));E.text('PIRANHA',(2.3,2.42,-.21),.18,'ph-letter')
 E.text('NIGHTCLUB',(2.3,1.48,-.21),.13,'ph-letter')
 E.box('ph-concrete',(8,.06,-3.0),(16,.12,6),True)
 # Separate patio east of south half. Its screens are not another enclosed room.
 patio=Frame(B,1920,1170,-math.pi/2,y=0)
 patio.box('ph-paving',(7.8,.04,-5.4),(15.6,.08,10.8),True)
 for u in np.arange(.3,15.6,2.5):patio.box('ph-metal',(u,1.0,-10.7),(.08,2,.08),True)
 patio.box('ph-screen',(7.8,.95,-10.65),(15.6,1.8,.07),True)
 for u in [0,15.6]:patio.box('ph-screen',(u,.95,-5.35),(.08,1.8,10.7),True)
 # Two low hipped metal shade pavilions visible from road and above.
 for u in [4.0,11.7]:
  for du in [-3.3,3.3]:
   for v in [-9.3,-2.3]:patio.box('ph-metal',(u+du,1.42,v),(.10,2.75,.10),True)
  corners=[(u-3.65,-9.65),(u+3.65,-9.65),(u+3.65,-1.95),(u-3.65,-1.95)]
  for i in range(4):
   a=corners[i];b=corners[(i+1)%4];B.face('ph-shade',[patio.p(a[0],2.85,a[1]),patio.p(b[0],2.85,b[1]),patio.p(u,3.95,-5.8)])
   patio.tube('ph-metal',(a[0],2.87,a[1]),(u,3.97,-5.8),.035,8)
  patio.box('ph-shade',(u,4.04,-5.8),(.9,.16,.9))
 # Neutral roof plant rather than unreferenced facade ornament.
 for x,z,w in [(1909,1160,1.8),(1910,1173,2.2),(1898,1180,1.6)]:
  B.box('ph-equipment',(x,4.8,z),(w,.9,1.5));B.box('ph-dark',(x,5.26,z),(w-.15,.02,1.35))
  for off in np.arange(-.55,.56,.15):B.box('ph-metal',(x,4.8,z+off),(w+.02,.05,.04))
 # West/south parapet, rear service details left explicitly uncertain.
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):B.tube('ph-trim',(a[0],4.39,a[1]),(b[0],4.39,b[1]),.055,6)
 routes=[dict(name='East entrance approach',points=[E.p(6.3,.12,-5.5),E.p(6.3,.12,-3),E.p(6.3,.12,-1)])]
 return dict(key=KEY,name='Piranha Nightclub',center=[1911,0,1170],bounds=[1892,1152,1931,1187],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=routes,hotelSources=[])
if __name__=='__main__':
 B=Meshes();meta=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(meta,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
