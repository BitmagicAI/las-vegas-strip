"""NYNY south arrival: mapped stepped pavilion and open Art Deco canopy.
Plan from mapped podium outline; January2025 StreetView establishes open canopy.
Heights are estimates (pavilion20m from map); no interior generation.
"""
from common import *
from forum_shops import facade_frame
KEY='nynyArrival';IDS=['way/115661803']
CANOPY=footprint('way/115661793').intersection(box(-167,1609.7,-136,1643))
def exterior(B):
 B.property=KEY+'-exterior';B.source='nyny-arrival';B.detail=0
 D=.24;p=footprint(IDS[0]);cx,cz=p.centroid.coords[0]
 # Tall fluted central pavilion, with stepped setbacks and cornice returns.
 B.shell(p,8.8,18.1,'nya-stone',roof=False)
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  F,L,_,_=facade_frame(B,a,b,p,.03);F.y=0
  for u in np.linspace(.55,L-.55,9):
   F.box('nya-shadow-paint',(u,13.4,-.055),(.35,8.4,.08))
   F.box('nya-pale-stone',(u+.25,13.4,-.14),(.14,8.6,.24))
  for y,h,dep in [(9,.32,.4),(17.65,.32,.4),(18.1,.45,.65)]:F.box('nya-pale-stone',(L/2,y,-dep/2),(L+.2,h,dep))
 for inset,lo,hi in [(.2,18.3,18.9),(.7,18.9,19.5),(1.2,19.5,20)]:
  q=p.buffer(-inset,join_style=2);B.shell(q,lo,hi,'nya-pale-stone');B.planar('nya-roof-paint',q.buffer(-.18,join_style=2),hi+.025)
 # Clear automobile/foot passage underneath; underside faces downward.
 q=CANOPY;B.shell(q,7.2,8.1,'nya-gold-paint',roof=False)
 B.planar('nya-roof-paint',q,8.1,True)
 for t in triangles(q):B.face('nya-ceiling-paint',[(x,7.2,z)for x,z in list(t.exterior.coords)[:-1]][::-1])
 for a,b in zip(list(q.exterior.coords),list(q.exterior.coords)[1:]):
  F,L,_,_=facade_frame(B,a,b,q,.04);F.y=0
  for y,h,dep,mat in [(7.35,.18,.15,'nya-red-paint'),(7.67,.18,.15,'nya-red-paint'),(8.03,.15,.3,'nya-gold-paint'),(8.3,.36,.12,'nya-pale-stone')]:F.box(mat,(L/2,y,-dep/2),(L+.04,h,dep))
  for u in np.arange(.3,L,.55):F.box('nya-bulb-paint',(u,7.15,-.17),(.07,.07,.08))
 # Mirrored rectangular supports, gold/silver inlaid stylized fan pattern.
 for x,z in [(-163.8,1612.5),(-139.1,1612.5),(-163.8,1626.8),(-139.1,1626.8),(-160.8,1639),(-142.6,1639)]:
   F=Frame(B,x,z,0,y=D);F.box('nya-dark-paint',(0,3.45,0),(1.2,6.9,1.2),True)
   F.box('nya-pale-stone',(0,.55,0),(1.4,1.1,1.4),True)
   for side in [-1,1]:
    for u in [-.46,-.23,0,.23,.46]:F.tube('nya-gold-paint',(0,1.15,side*.615),(u,6.6-abs(u)*2.8,side*.615),.025,6)
    for y in [1.15,6.7]:F.box('nya-gold-paint',(0,y,side*.62),(1.22,.13,.055))
 # Radial soffit stripes, original geometry (not a photograph texture).
 apex=(-151.7,1609.9)
 for i,x in enumerate(np.linspace(-162.4,-140.9,13)):
  B.face('nya-red-paint' if i%2 else 'nya-gold-paint',[(apex[0],7.185,apex[1]),(x,7.185,1642.5),(x+.36,7.185,1642.5)])
 # Frontal sign on narrow southern face. Crown rays sit behind raised letters.
 F=Frame(B,-151.72,1643,0,y=0)
 # Positive local Z is south; text faces south with back=True.
 for i in range(17):
  a=math.pi*i/16;B.tube('nya-gold-paint',(-151.72+3*math.cos(a),9+1.1*math.sin(a),1643.1),(-151.72+7.3*math.cos(a),9+5.4*math.sin(a),1643.1),.09,8)
 for side in [-1,1]:
  F.box('nya-pale-stone',(side*8.9,8.95,-.14),(3.0,1.2,.40))
  F.box('nya-pale-stone',(side*8.6,9.65,-.18),(2.4,.28,.48))
 for yy in [10.15,8.35]:
  F.text('NEW YORK',(0,yy,.31),1.95,'nya-gold-paint',back=True)
  F.text('NEW YORK',(0,yy+.025,.365),1.90,'nya-letter',back=True)
 # Walkable arrival floor follows existing .24m datum. Geometry ownership trim
 # below preserves existing pavement and supplies only absent visual support.
 from local_pavement import local_pavement
 floor=q.buffer(.3,join_style=2);local_pavement(B,floor,D,'nya-floor-concrete')
 samples=[[x,8.35,z]for x in np.arange(q.bounds[0]+.7,q.bounds[2],1)for z in np.arange(1610.5,1642,1)if q.buffer(-.3).contains(Point(x,z))]
 routes=[[[-159,D,1641],[-159,D,1610.5]],[[-144,D,1641],[-144,D,1610.5]],[[-165,D,1618],[-138,D,1618]]]
 Path('build/city-exteriors/nyny-arrival-samples.json').write_text(json.dumps(samples));Path('build/city-exteriors/nyny-arrival-stairs.json').write_text(json.dumps(routes))
 return dict(key=KEY,name='NYNY arrival pavilion and canopy',center=[cx,0,1620],bounds=[-167,1598,-136,1644],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
