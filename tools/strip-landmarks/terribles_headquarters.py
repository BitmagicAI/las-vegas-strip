"""Mapped Terrible Herbst headquarters, exterior-only photographic reconstruction."""
from common import *
from forum_shops import facade_frame
from diamond_inn import palm
KEY='terriblesHeadquarters'
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/headquarters';B.detail=0;W=Frame(B,0,0,y=0)
 p=footprint('way/457939132');main=p.intersection(box(60,3720,120,3741));can=p.difference(main)
 B.shell(main,.24,6.8,'thq-white-stucco',roof=False);B.planar('thq-flat-roof-paint',main,6.7,True)
 for a,b in zip(list(main.exterior.coords),list(main.exterior.coords)[1:]):
  G,L,nx,nz=facade_frame(B,a,b,main,.03);G.box('thq-coping',(L/2,6.82,0),(L,.15,.22))
  if nx<-.5 and L>8:
   G.text('TERRIBLE HERBST',(L/2,5.3,-.12),.85,'thq-red-letter')
   for u in np.arange(2,L-1,3):
    G.box('thq-frame',(u,1.8,-.09),(1.8,.9,.1));G.box('thq-glass',(u,1.8,-.16),(1.65,.75,.04))
  elif nz<-.5 or nx>.5:
   for u in np.arange(2,L-1,3.8):
    G.box('thq-frame',(u,2,-.09),(2.1,1.8,.1));G.box('thq-glass',(u,2,-.16),(1.95,1.65,.04))
 # High glazed entrance rises above the flanking single-storey office wings.
 W.box('thq-glass',(88.9,4.55,3741.07),(13.5,8.5,.12),True)
 for x in np.arange(82.2,96,1.5):W.box('thq-frame',(x,4.55,3741.18),(.1,8.5,.15))
 for y in [3.0,5.9,8.7]:W.box('thq-frame',(88.9,y,3741.2),(13.5,.09,.15))
 W.box('thq-roof-paint',(88.9,8.9,3745.0),(17.5,.35,10.2),True)
 W.box('thq-soffit-paint',(88.9,8.69,3745),(17.3,.08,10))
 for x in np.arange(80.7,98,2.1):W.box('thq-frame',(x,8.42,3745),(.15,.45,10))
 for x in [82.1,95.5]:
  W.box('thq-stacked-ashlar',(x,4.42,3747.3),(1.25,8.3,1.3),True)
  W.box('thq-stone-cap',(x,8.6,3747.3),(1.32,.14,1.37))
 # Door remains an exterior endpoint; no invented interior connection.
 W.box('thq-frame',(88.9,1.7,3741.25),(3.2,2.85,.12));W.box('thq-glass',(88.9,1.7,3741.34),(3,2.65,.04))
 W.box('thq-frame',(88.9,1.7,3741.38),(.08,2.7,.04))
 for x in [88.45,89.35]:W.tube('thq-handle',(x,1.1,3741.47),(x,2,3741.47),.025,8)
 site=box(30,3707,184,3770);paving=box(79,3740.9,99,3756).difference(main)
 B.planar('thq-asphalt',site,.16,True);B.planar('thq-paving',paving,.30,True)
 gardens=unary_union([box(55,3720,62,3753),box(63,3741,79,3753),box(99,3741,119,3753)])
 B.planar('thq-gravel',gardens,.32,True)
 for a in parts(gardens):
  for v,w in zip(list(a.exterior.coords),list(a.exterior.coords)[1:]):W.tube('thq-curb',(v[0],.34,v[1]),(w[0],.34,w[1]),.1,8)
 # Layered stone landscape walls observed at the entry, with open central access.
 for x,width in [(72,12),(107,12)]:
  W.box('thq-stacked-ashlar',(x,.9,3748),(width,1.15,.45),True);W.box('thq-stone-cap',(x,1.51,3748),(width+.1,.1,.55))
 for x,z in [(69,3728),(106,3728),(99,3732)]:W.box('thq-service',(x,7.1,z),(2.4,.7,2))
 # Photograph-derived roadside palms and sculptural cactus groupings.
 for x,z,h in [(57,3723,10),(57,3733,9),(57,3744,11),(69,3745,7),(107,3745,7.8),(115,3745,8.5)]:palm(B,x,z,h)
 for x,z,h in [(65,3745,4.8),(76,3745,2.8),(102,3746,3.4),(58,3738,3.7)]:
  W.lathe('thq-cactus-foliage',x,z,[(.32,.23),(h-.3,.24),(h,.12),(h+.1,.01)],20)
  for j in range(10):
   a=j*math.tau/10;W.tube('thq-cactus-rib',(x+.24*math.cos(a),.4,z+.24*math.sin(a)),(x+.24*math.cos(a),h-.3,z+.24*math.sin(a)),.015,5)
  W.path('thq-cactus-foliage',[(x,h*.45,z),(x+.5,h*.45,z),(x+.7,h*.6,z),(x+.7,h*.85,z)],.14,12)
 # Recessed horizontal courses break up the stone piers at pedestrian distance.
 for x in [82.1,95.5]:
  for y in np.arange(.45,8.5,.22):
   for zz in [3746.64,3747.96]:W.box('thq-stone-joint',(x,y,zz),(1.25,.025,.012))
   for xx in [x-.63,x+.63]:W.box('thq-stone-joint',(xx,y,3747.3),(.012,.025,1.3))
 samples=[]
 for x in np.arange(80,98,1):
  for z in np.arange(3742,3756,1):
   if all(math.hypot(x-px,z-3747.3)>1.3 for px in [82.1,95.5]):samples.append([float(x),.3,float(z)])
 Path('build/city-exteriors/terribles-headquarters-samples.json').write_text(json.dumps(samples))
 return dict(key=KEY,name='Terrible Herbst Headquarters',center=[89,0,3738],bounds=[30,3707,184,3770],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
