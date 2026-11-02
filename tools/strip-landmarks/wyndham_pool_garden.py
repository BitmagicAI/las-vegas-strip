"""Original pool-court study from operator photos23/24 and Google aerial.
Ground registration uses the mapped datum; dimensions and counts remain inferred.
"""
from common import *
from shapely.geometry import shape
RECORD=Path('docs/project-records/west-resort-amenities')
Y=.32

def plan():
 # Google north-up aerial at 36.12205,-115.18415,zoom20,1280x720.
 # Map pane begins atx72: geographic centre(676,360), approximate0.1206m/pixel.
 cx=6378137*math.radians(-115.18415+115.173)*math.cos(math.radians(36.116))
 cz=-6378137*math.radians(36.12205-36.116)
 def p(x,y):return(cx+(x-676)*.1206,cz+(y-360)*.1206)
 outlines=[[(399,296),(485,275),(530,456),(452,477)],[(272,426),(356,519),(298,571),(217,478)]]
 pools=[Polygon([p(*v) for v in ps]) for ps in outlines]
 spas=[Polygon([p(*v) for v in ps]) for ps in [[(461,481),(506,471),(520,523),(475,534)],[(218,536),(249,568),(226,590),(196,557)]]]
 deck=Polygon([p(*v) for v in [(146,265),(355,158),(523,233),(588,520),(542,677),(438,700),(170,586),(105,450)]])
 occupied=unary_union([footprint(i) for i in ['way/1459325605','way/1459325606','way/1459325607','way/1459325608']])
 deck=deck.difference(occupied.buffer(.6))
 surfaces=json.loads(Path("build/geographic-strip/surface-layers.geojson").read_text())["features"]
 circulation=unary_union([shape(f["geometry"]) for f in surfaces if f["properties"]["kind"] in ["road","sidewalk"]])
 deck=deck.difference(circulation.buffer(.2))
 assert deck.intersection(circulation).area<1e-6
 assert all(deck.buffer(-.5).covers(w) for w in pools+spas)
 assert not deck.intersects(occupied)
 return p,deck,pools,spas

def build(B):
 B.source='wyndham-desert-blue/pool-garden';p,deck,pools,spas=plan();water=unary_union(pools+spas)
 # Shallow raised basins preserve existing ground and do not claim swimming depth.
 B.planar('wpa-deck',deck.difference(water.buffer(.35,join_style=2)),Y,True)
 for basin in pools+spas:
  B.planar('wpa-tile',basin,.28,True);B.shell(basin,.28,.61,'wpa-tile',roof=False,solid=True)
  B.planar('wpa-coping',basin.buffer(.35,join_style=2).difference(basin),.61,True);B.planar('wpa_pool',basin,.46)
 # Furnishing rows near the rectangular pools, inferred count rather than exact inventory.
 furniture=[]
 for px,py,angle in [(555,y,0) for y in [310,345,380,415]]+[(x,235,math.pi) for x in [350,385,420,455]]+[(175,y,-.65) for y in [400,435,470,505]]:
  x,z=p(px,py);F=Frame(B,x,z,angle,y=Y)
  bound=translate(rotate(box(-.44,-1.05,.44,1.05),-angle*180/math.pi,origin=(0,0)),xoff=x,yoff=z)
  if not deck.buffer(-.25).covers(bound) or water.buffer(.8).intersects(bound):continue
  furniture.append(bound);F.box('wpa-frame',(0,.26,0),(.79,.12,1.96),True)
  for dx in [-.38,.38]:
   F.box('wpa-frame',(dx,.35,.1),(.04,.05,1.76))
   for dz in [-.7,.7]:F.box('wpa-frame',(dx,.14,dz),(.045,.28,.045))
  F.box('wpa-mesh',(0,.36,.25),(.71,.025,1.35))
  B.face('wpa-mesh',[F.p(-.355,.37,-.425),F.p(.355,.37,-.425),F.p(.355,.91,-.96),F.p(-.355,.91,-.96)])
 # Blue parasols are static shade, not runtime lights or leaf-card substitutes.
 parasols=0
 for px,py in [(580,360),(395,220),(155,455)]:
  x,z=p(px,py)
  if not deck.buffer(-.3).contains(Point(x,z)):continue
  B.tube('wpa-frame',(x,Y,z),(x,2.8,z),.035,8)
  for j in range(12):
   a=j*math.tau/12;b=(j+1)*math.tau/12
   B.face('wpa-blue',[(x,2.8,z),(x+1.1*math.cos(a),2.25,z+1.1*math.sin(a)),(x+1.1*math.cos(b),2.25,z+1.1*math.sin(b))])
  parasols+=1
 report={'deckBounds':list(deck.bounds),'deckAreaM2':deck.area,'poolAreasM2':[w.area for w in pools],'spaAreasM2':[w.area for w in spas],'loungers':len(furniture),'parasols':parasols,'registration':'Approximate0.1206m/px north-up Google aerial, centre676,360. Ground datum preserved; survey precision not claimed.','remaining':['Palms/cabanas/splash-pad landscaping not yet modeled.','No indoor entrance or swimming simulation.','Exact pool shape, depth and ground registration need installed comparison.']}
 RECORD.mkdir(exist_ok=True,parents=True);(RECORD/'wyndham-geometry.json').write_text(json.dumps(report,indent=2)+'\n');return report
