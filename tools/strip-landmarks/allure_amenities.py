"""Original Allure arrival and residential amenity court, photo-fitted, not surveyed."""
from common import *
KEY='allureAmenities'
DECK=17.5
POOL=box(1241,-3184,1261,-3160)
SPA=box(1263,-3182,1268,-3177)
COURT=box(1211,-3194,1293,-3146)
def build(B):
 B.property=KEY+'-exterior';B.source='allure-amenities';B.detail=0
 # The absent north parking podium is inferred from architect gallery and aerial.
 # Keep neighboring Ahern and the installed tower entirely intact.
 for y in [0.18,3.5,7,10.5,14,DECK-.25]:
  for z in [-3194,-3146]:B.box('aa-stone',(1252,y,z),(82,.45,.5),True)
  for x in [1211,1293]:B.box('aa-stone',(x,y,-3170),(.5,.45,48),True)
 for x in np.arange(1211,1294,8.2):
  for z in [-3194,-3146]:B.box('aa-stone',(x,DECK/2,z),(.65,DECK,.65),True)
 for z in np.arange(-3186,-3146,8):
  for x in [1211,1293]:B.box('aa-stone',(x,DECK/2,z),(.65,DECK,.65),True)
 for z in [-3193.7,-3146.3]:B.box('aa-shadow',(1252,8.5,z),(80,16,.08))
 for x in [1211.3,1292.7]:B.box('aa-shadow',(x,8.5,-3170),(.08,16,47))
 B.planar('aa-deck',COURT.difference(POOL.buffer(.5,join_style=2)).difference(SPA.buffer(.4,join_style=2)),DECK,True)
 for basin in [POOL,SPA]:
  B.planar('aa-coping',basin.buffer(.5,join_style=2).difference(basin),DECK,True)
  B.planar('aa-pool-tile',basin,DECK-1.25,True)
  B.planar('allure_pool',basin,DECK-.18)
  B.shell(basin,DECK-1.25,DECK,'aa-pool-tile',roof=False,solid=True)
 # Perimeter parapet and slim balustrade keep elevated circulation bounded.
 for a,b in [((1211,-3194),(1293,-3194)),((1211,-3194),(1211,-3146)),((1293,-3194),(1293,-3146))]:
  line=LineString([a,b]);B.extrude('aa-stone',line.buffer(.18,cap_style=2),DECK,DECK+.4,True)
  B.tube('aa-metal',(a[0],DECK+1.15,a[1]),(b[0],DECK+1.15,b[1]),.04)
  for t in np.linspace(0,1,int(line.length/1.6)+1):
   p=line.interpolate(t,normalized=True);B.box('aa-metal',(p.x,DECK+.77,p.y),(.045,.75,.045))
  B.extrude('allure-rail',line.buffer(.025,cap_style=2),DECK+.4,DECK+1.15,True)
 # Low tiled-roof amenity wings flank the court in the reference. Closed shells,
 # because the private internal plan and lift connection have not been established.
 for x in [1218,1286]:
  p=box(x-5,-3189,x+5,-3153);B.shell(p,DECK,DECK+3,'aa-stone',roof=False)
  for side in [-1,1]:
   B.face('aa-roof',[(x,DECK+4.25,-3189.5),(x+side*5.5,DECK+3,-3189.5),(x+side*5.5,DECK+3,-3152.5),(x,DECK+4.25,-3152.5)])
  for z in np.arange(-3188,-3154,2.6):
   B.box('aa-glass',(x+(5.02 if x<1250 else -5.02),DECK+1.55,z),(.045,2.3,1.8))
 # Sparse original furnishing, lower count than the photographed deck.
 for x in [1235,1274]:
  for z in [-3187,-3181,-3175,-3169,-3163]:
   F=Frame(B,x,z,math.pi/2 if x<1250 else -math.pi/2,y=DECK)
   F.box('aa-fabric',(0,.48,0),(.72,.08,1.7))
   F.box('aa-fabric',(0,.76,-.78),(.72,.65,.08))
   for xx in [-.3,.3]:
    F.tube('aa-metal',(xx,.1,.7),(xx,.5,.7),.025,6);F.tube('aa-metal',(xx,.1,-.7),(xx,.5,-.7),.025,6)
 for x,z in [(1230,-3189),(1274,-3189),(1230,-3154),(1274,-3154)]:
  B.box('aa-stone',(x,DECK+.48,z),(1.65,.96,1.65),True)
  B.box('aa-soil',(x,DECK+.98,z),(1.48,.04,1.48))
 # Pool handrails: visible, with no manufactured decorative brand assets.
 for x in [1243,1245]:
  B.path('aa-metal',[(x,DECK-.8,-3182),(x,DECK+.7,-3183),(x,DECK+.8,-3184.7),(x,DECK,-3185.1)],.045,8)
 # Silver arrival canopy: rounded west edge, flat east connection to tower.
 canopy=box(1210,-3144,1222,-3123).union(Point(1210,-3133.5).buffer(8,resolution=24).intersection(box(1202,-3144,1210,-3123)))
 B.extrude('aa-silver',canopy,5.0,5.75,True);B.planar('aa-soffit',canopy,4.99)
 for x,z in [(1205,-3139),(1205,-3128),(1217,-3139)]:
  B.tube('aa-silver',(x,.2,z),(x,5,z),.55,16)
  B.box('aa-silver',(x,2.6,z),(1.0,4.8,1.0),True)
 # Small guard booth is closed and outside the clear arrival lane.
 B.box('aa-stone',(1205,1.25,-3124),(3.3,2.5,2.5),True)
 for z in [-3125.27,-3122.73]:B.box('aa-glass',(1205,1.8,z),(2.8,.95,.025))
 B.box('aa-roof',(1205,2.6,-3124),(3.7,.2,2.9))
 # Freestanding south-front sign, original lettering approximation.
 B.box('aa-blue',(1243,.65,-3104),(14,1.0,.55),True)
 B.text('ALLURE',(1243,1.2,-3103.65),2.0,math.pi,'aa-silver')
 B.text('LAS VEGAS',(1243,.42,-3103.64),.36,math.pi,'aa-silver')
 return {'deckY':DECK,'poolBounds':list(POOL.bounds),'courtBounds':list(COURT.bounds),'inferred':'Podium 17.5m, pool20x24m, spa5x5m, canopy5m clearance; photo/aerial fitted, not surveyed.','remaining':'Private amenity interiors and continuous lift access not modeled. Tower crown/balconies remain approximate.'}
if __name__=='__main__':
 B=Meshes();meta=build(B);B.save_all();Path('docs/project-records/allure-amenities/geometry.json').write_text(json.dumps(meta,indent=2)+'\n');print(sum(len(g['faces'])for g in B.groups.values()),'triangles')
