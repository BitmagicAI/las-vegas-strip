"""Original south spa/deck study from Hilton gallery and Google aerial.
Registration/dimensions are estimates; preserve the existing hotel and ground.
"""
from common import *
from rio_amenities import AmenityMeshes
RECORD=Path('docs/project-records/convention-area-refinement')
Y=.32

def build(B):
 B.property='embassySpaRefinement-exterior';B.source='embassy-spa-refinement';B.detail=0
 deck=box(1712.6,-865.7,1732.38,-857.99)
 spa=box(1724.42,-864.02,1730.81,-861.01)
 hotel=footprint('way/331337786')
 assert not deck.intersects(hotel)
 # Shallow raised basin avoids cutting or overwriting the existing city ground.
 B.planar('ess-deck',deck.difference(spa.buffer(.3,join_style=2)),Y,True)
 B.planar('ess-tile',spa,.285,True)
 B.shell(spa,.28,.65,'ess-tile',roof=False,solid=True)
 B.planar('ess-coping',spa.buffer(.3,join_style=2).difference(spa),.65,True)
 B.planar('ess_pool',spa,.49)
 walls=[(box(1712.6,-858.19,1732.38,-857.99)),box(1732.18,-865.7,1732.38,-857.99),box(1712.6,-865.7,1712.8,-862.2),box(1712.6,-860.7,1712.8,-857.99)]
 for p in walls:
  B.shell(p,Y,2.3,'ess-wall',roof=False,solid=True);B.planar('ess-coping',p,2.3,True)
  for y in [1.4,1.95]:B.shell(p.buffer(.012,join_style=2),y,y+.13,'ess-band',roof=False,solid=False)
 # Open pedestrian gate bay remains 1.5m wide; no invented access through hotel glass.
 for z in [-862.2,-860.7]:B.tube('ess-metal',(1712.7,Y,z),(1712.7,2.25,z),.035,8)
 B.path('ess-metal',[(1712.7,2.25,-862.2),(1712.7,2.55,-861.95),(1712.7,2.65,-861.45),(1712.7,2.55,-860.95),(1712.7,2.25,-860.7)],.035,8)
 chairs=[]
 for x in [1714.1,1715.6,1717.1,1718.6,1720.1,1721.6]:
  z=-859.55;F=Frame(B,x,z,math.pi,y=Y);chairs.append(box(x-.43,z-1.03,x+.43,z+1.03))
  F.box('ess-frame',(0,.29,0),(.78,.12,1.95),True)
  for dx in [-.38,.38]:
   F.box('ess-frame',(dx,.37,0),(.045,.06,1.95))
   for dz in [-.7,.7]:F.box('ess-frame',(dx,.15,dz),(.05,.3,.05))
  F.box('ess-mesh',(0,.37,.25),(.7,.03,1.35))
  B.face('ess-mesh',[F.p(-.35,.385,-.425),F.p(.35,.385,-.425),F.p(.35,.85,-.95),F.p(-.35,.85,-.95)])
  F.tube('ess-towel',(-.28,.82,-.83),(.28,.82,-.83),.065,8)
 for x in [1715.6,1719.5]:
  z=-864.25;B.tube('ess-frame',(x,Y,z),(x,2.85,z),.035,8)
  for j in range(12):
   a=j*math.tau/12;b=(j+1)*math.tau/12
   B.face('ess-parasol',[(x,2.85,z),(x+1.1*math.cos(a),2.35,z+1.1*math.sin(a)),(x+1.1*math.cos(b),2.35,z+1.1*math.sin(b))])
 # West spa edge handrail, similar to the official photo; dimensions inferred.
 for z in [-863.3,-862.65]:
  B.path('ess-metal',[(1723.98,Y,z),(1723.98,1.4,z),(1724.35,1.5,z),(1724.8,1.3,z),(1724.8,.45,z)],.035,8)
 # Static pool lift silhouette. This is not a simulated accessibility mechanism.
 B.box('ess-metal',(1731.55,.48,-862),( .45,.3,.6),True)
 B.tube('ess-metal',(1731.55,.5,-862),(1731.55,1.5,-862),.06,8)
 B.tube('ess-metal',(1731.55,1.5,-862),(1730.7,1.25,-862),.05,8)
 B.box('ess-blue',(1730.6,.9,-862),(.4,.08,.5))
 B.box('ess-blue',(1730.82,1.12,-862),(.08,.44,.5))
 route=LineString([(1711.7,-861.45),(1713.4,-861.45),(1713.4,-862.3),(1722.8,-862.3)])
 for p in chairs+walls+[spa.buffer(.3,join_style=2)]:assert not route.buffer(.32).intersects(p)
 assert all(deck.covers(p) for p in chairs)
 report={'deckBounds':list(deck.bounds),'spaBounds':list(spa.bounds),'deckAreaM2':deck.area,'spaAreaM2':spa.area,'loungers':6,'parasols':2,'gateClearanceM':1.5,'limitations':['Dimensions and furniture count inferred from official image and aerial, not surveyed.','Raised shallow basin preserves pre-existing ground; no depth/swimming claim.','Pool lift is static, not interactive.','Palms deferred: supplied broadleaf source models are not appropriate substitutes.','Hotel glass and interiors preserved; route enters from external west gate only.','Source only, not installed or visually accepted.']}
 (RECORD/'embassy-geometry.json').write_text(json.dumps(report,indent=2)+'\n')
 (RECORD/'embassy-routes.json').write_text(json.dumps([{'name':'embassy-deck-access','points':[[x,Y,z] for x,z in route.coords]}],indent=2)+'\n')
 return report
if __name__=='__main__':
 B=AmenityMeshes();print(build(B));B.save_all()
