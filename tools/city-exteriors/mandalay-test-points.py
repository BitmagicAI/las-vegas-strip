import sys
sys.path.insert(0,'tools/strip-landmarks')
from mandalay_pool_detail import *
water=unary_union([p for r,p in plans() if r['deckY']<1]);buildings=unary_union([structure(i) for i in IDS]+[structure(i) for i in ['way/116660358','way/502624676','way/116660354']]);deck=water.buffer(12,quad_segs=12).buffer(5).buffer(-5).difference(buildings.buffer(.2)).difference(water.buffer(.65));points=[]
for x in np.arange(deck.bounds[0],deck.bounds[2],3):
 for z in np.arange(deck.bounds[1],deck.bounds[3],3):
  if deck.buffer(-.5).contains(Point(x,z)):points.append(dict(x=x,z=z,y=.64,id='deck'))
Path('build/city-exteriors/mandalay-deck-test-points.json').write_text(json.dumps(points));print('deck',len(points))
points=[]
for r,p in plans():
 for x in np.arange(p.bounds[0]+.8,p.bounds[2],4):
  for z in np.arange(p.bounds[1]+.8,p.bounds[3],4):
   if p.buffer(-.5).contains(Point(x,z)):points.append(dict(x=x,z=z,y=r['deckY']-.4,id=r['id']))
Path('build/city-exteriors/mandalay-pool-test-points.json').write_text(json.dumps(points));print('pool',len(points))
