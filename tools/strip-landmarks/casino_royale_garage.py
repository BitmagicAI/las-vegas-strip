"""Casino Royale parking: mapped five-storey plan, December2022 south elevation.
Storey heights, north/west detailing and interior circulation inferred.
"""
from common import *
KEY='casinoRoyaleGarage';ID='way/313625620'
def exterior(B):
 B.property=KEY+'-exterior';B.source='casino-royale-parking';B.detail=0
 p=footprint(ID);F=Frame(B,201.764,-491.77,math.atan2(1.394,51.853),y=.24)
 ramp=F.poly([(7,-19),(13,-19),(13,19),(7,19)])
 for i in range(6):
  y=.24+3.2*i;floor=p if i==0 else p.difference(ramp)
  B.planar('rg-deck-concrete',floor,y,True);B.shell(floor,y-.24,y,'rg-edge-paint',roof=False)
  for poly in parts(floor):
   for t in triangles(poly):B.face('rg-soffit-paint',[(x,y-.24,z)for x,z in list(t.exterior.coords)[:-1]])
  if i<5:
   # Stacked same-direction ramps keep a constant3.2m separation.
   q=[F.p(7,3.2*i,-19),F.p(13,3.2*i,-19),F.p(13,3.2*(i+1),19),F.p(7,3.2*(i+1),19)]
   B.upface('rg-ramp-concrete',q,True)
   for u in [7,13]:
    F.tube('rg-rail-paint',(u,3.2*i+1.05,-19),(u,3.2*(i+1)+1.05,19),.045,8)
    # Continuous ramp curb/safety face with collision; preserves car clearance.
    B.face('rg-curb-concrete',[F.p(u,3.2*i,-19),F.p(u,3.2*(i+1),19),F.p(u,3.2*(i+1)+.35,19),F.p(u,3.2*i+.35,-19)],True)
   # Interior columns stay away from main turning/drive lanes.
   for u in [-12,-3]:
    for v in [-15,-5,5,15]:F.box('rg-tan-stucco',(u,3.2*i+1.6,v),(.65,3.2,.65),True)
  # Parked bay lines around the west half, two generous circulation lanes.
  for v in np.arange(-19,20,2.7):
   F.box('rg-line-paint',(-14,3.2*i+.012,v),(5.6,.018,.075))
   F.box('rg-line-paint',(3.5,3.2*i+.012,v),(3.8,.018,.075))
  # Outer metal guards: floor edges, thin horizontal rails, pickets.
  edges=[((-17.4,-25.6),(-17.4,25.6)),((17.4,-25.6),(17.4,25.6)),((-17.4,-25.6),(17.4,-25.6)),((-17.4,25.6),(17.4,25.6))]
  for a,b in edges:
   L=math.dist(a,b)
   for t0,t1 in zip(np.linspace(0,1,math.ceil(L/.23)+1),np.linspace(0,1,math.ceil(L/.23)+1)[1:]):
    t=(t0+t1)/2;u=a[0]+(b[0]-a[0])*t;v=a[1]+(b[1]-a[1])*t
    if i==0 and abs(u+17.4)<.1 and abs(v)<3.5:continue
    F.box('rg-rail-paint',(u,3.2*i+.55,v),(.035,1.1,.035))
   # Split the west entry at ground; all upper edge rails continuous.
   cuts=[(a,b)]
   if i==0 and a[0]==b[0]==-17.4:cuts=[(a,(-17.4,-3.5)),((-17.4,3.5),b)]
   for aa,bb in cuts:
    for yy in [.12,1.1]:F.tube('rg-rail-paint',(aa[0],3.2*i+yy,aa[1]),(bb[0],3.2*i+yy,bb[1]),.04,8)
    B.face('rg-collision',[F.p(aa[0],3.2*i,aa[1]),F.p(bb[0],3.2*i,bb[1]),F.p(bb[0],3.2*i+1.1,bb[1]),F.p(aa[0],3.2*i+1.1,aa[1])],True)
 # Broad tan end piers reproduce the photographed two open bays.
 for v in [-25.6,25.6]:
  for u,w in [(-14.7,5.8),(0,6.2),(14.5,6.2)]:
   F.box('rg-tan-stucco',(u,8.65,v),(w,17.3,.55),True)
   F.box('rg-coping-paint',(u,17.34,v),(w+.12,.12,.72))
 for u in [-17.4,17.4]:
  for v in [-19,-10,10,19]:F.box('rg-tan-stucco',(u,8.1,v),(.48,16.2,1.0),True)
 # A parapeted central roof divider and restrained roof utility equipment.
 F.box('rg-tan-stucco',(0,16.85,0),(.45,1.2,38),True)
 for v in [-22,22]:
  F.box('rg-service-paint',(-3,16.9,v),(2.2,1.3,1.8));F.box('rg-shadow-paint',(-3,17.57,v),(1.8,.025,1.4))
 # South sign; no new lights are allocated.
 G=Frame(B,*F.poly([(0,26),(0.01,26),(0.01,26.01)]).centroid.coords[0],yaw=F.yaw+math.pi,y=0)
 G.box('rg-red-paint',(0,7.15,0),(3.2,2,.16));G.text('Best Western',(0,7.65,-.1),.28,'rg-white-letter');G.text('PLUS',(0,7.17,-.1),.25,'rg-white-letter');G.text('CASINO ROYALE',(0,6.55,-.1),.30,'rg-white-letter')
 # Local approach apron, stopping before the retained service drive.
 B.planar('rg-paving-concrete',p.buffer(.8,join_style=2).difference(p),.24,True)
 for k in list(B.groups):
  if B.groups[k]['material']=='rg-collision':del B.groups[k]
 return dict(key=KEY,name='Casino Royale parking garage',center=[202,0,-492],bounds=[182,-520,222,-464],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
