"""Northern courtyard pool, aerial-estimated dimensions; no surveyed layout claim.
Original geometry. The fenced deck stays beside the east wing, preserving the
parking courtyard rather than replacing the whole court with a garden.
"""
from common import *
def add_pool(B,F):
 B.property='motel6-stadium-exterior';B.source='podium/motel6-stadium'
 # Overhead alignment: east wing inner face x=-797.5, cross wing z=2026.5.
 # Round corners are an interpretation of the low-resolution aerial.
 basin=box(-807.7,2009.3,-801.2,2022.2).buffer(-.65).buffer(.65,quad_segs=8)
 deck=box(-810.7,2006.8,-799.8,2024.5)
 B.planar('m6-deck-concrete',deck.difference(basin.buffer(.24)),.20,True)
 B.planar('m6-white-paint',basin.buffer(.24).difference(basin),.24,True)
 B.shell(deck,.01,.20,'m6-deck-concrete',roof=False)
 B.shell(basin,.015,.24,'m6-pool-tile',roof=False)
 B.planar('m6-pool-tile',basin,.018,True);B.planar('m6_pool',basin,.13)
 # Gate opening at the north end. The simple collision curtain is independent
 # of the thin visual pickets, avoiding dozens of tiny physics bodies.
 for a,b in [((-810.7,2006.8),(-805.8,2006.8)),((-804.3,2006.8),(-799.8,2006.8)),((-799.8,2006.8),(-799.8,2024.5)),((-799.8,2024.5),(-810.7,2024.5)),((-810.7,2024.5),(-810.7,2006.8))]:
  L=math.dist(a,b);G=Frame(B,*a,math.atan2(-(b[1]-a[1]),b[0]-a[0]),y=0)
  for y in [.35,1.48]:G.box('m6-white-paint',(L/2,y,0),(L,.045,.045))
  for x in np.arange(0,L,.18):G.box('m6-white-paint',(float(x),.91,0),(.025,1.16,.025))
  pts=[G.p(0,.20,0),G.p(L,.20,0),G.p(L,1.5,0),G.p(0,1.5,0)]
  c=B.solids[B.property];off=len(c['vertices'])//3;c['vertices'].extend(v for pt in pts for v in pt);c['indices'].extend(off+j for j in [0,1,2,0,2,3])
 # Two understated access rails. Furniture quantity/location remains inferred.
 for x in [-804.9,-804.1]:F.path('m6-metal-paint',[(x,.20,2008.0),(x,1.0,2008.0),(x,1.1,2008.4),(x,.30,2009.8)],.035,12)
 for z in [2012,2016,2020]:
  F.box('m6-white-paint',(-809.3,.48,z),(.65,.09,1.7))
  F.box('m6-white-paint',(-809.3,.72,z+.65),(.65,.5,.08))
  for x in [-809.55,-809.05]:
   for dz in [-.65,.65]:F.tube('m6-metal-paint',(x,.20,z+dz),(x,.44,z+dz),.025,6)
 return [dict(name='Pool gate and west deck',points=[[-805.05,.20,2005.9],[-805.05,.20,2007.4],[-809.2,.20,2007.4],[-810,.20,2010],[-810,.20,2023.5],[-800.4,.20,2023.5]])]
