"""Clark County Fire Station11, mapped footprint; exterior evidence Sep2022/Feb2025."""
from common import *
from forum_shops import facade_frame
KEY='fireStation11'
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/fire';B.detail=0;W=Frame(B,0,0,y=0);p=footprint('way/1125260694');bay=p.intersection(box(-100,3646.6,-60,3661));office=p.difference(bay)
 B.shell(bay,.24,6,'f11-stucco',roof=False);B.planar('f11-flat-roof-paint',bay,6,True)
 B.shell(office,.24,5.2,'f11-stucco',roof=False);B.planar('f11-flat-roof-paint',office,5.2,True)
 # Barrel-vault roof over the central office block, visible above parapet in StreetView.
 for z0,z1 in zip(np.linspace(3626.6,3646.2,25)[:-1],np.linspace(3626.6,3646.2,25)[1:]):
  def height(z):return 5.35+1.45*math.sin(math.pi*(z-3626.6)/19.6)
  B.upface('f11-roof-metal-paint',[(-93,height(z0),z0),(-65,height(z0),z0),(-65,height(z1),z1),(-93,height(z1),z1)])
 for x in np.arange(-93,-64.9,.48):W.path('f11-roof-rib-paint',[(x,5.39+1.45*math.sin(math.pi*t),3626.6+19.6*t) for t in np.linspace(0,1,25)],.025,4)
 for x in [-93,-65]:
  pts=[(x,5.18,3626.6)]+[(x,5.35+1.45*math.sin(math.pi*t),3626.6+19.6*t) for t in np.linspace(0,1,25)]+[(x,5.18,3646.2)]
  B.face('f11-stucco',pts if x==-65 else pts[::-1])
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  G,L,nx,nz=facade_frame(B,a,b,p,.03);height=6 if (a[1]+b[1])/2>3646.6 else 5.2
  G.box('f11-coping',(L/2,height+.05,-.02),(L,.1,.22))
  if nx>.7 and min(a[1],b[1])>3646:
   for z in [3649,3653.5,3658]:
    if min(a[1],b[1])-.1<z<max(a[1],b[1])+.1:
     u=LineString([a,b]).project(Point(-69.6,z));G.box('f11-frame',(u,2.55,-.06),(3.85,4.6,.16));G.box('f11-door',(u,2.55,-.16),(3.6,4.4,.07))
     for y in np.arange(.55,4.7,.42):G.box('f11-door-joint',(u,y,-.21),(3.6,.025,.02))
     for dx in [-1.15,-.38,.38,1.15]:G.box('f11-glass',(u+dx,2.8,-.22),(.63,.4,.025))
  elif L>7:
   for u in np.arange(2,L-1,4.2):
    G.box('f11-frame',(u,2,-.07),(1.8,1.5,.13));G.box('f11-glass',(u,2,-.15),(1.65,1.35,.04))
    G.box('f11-frame',(u,2,-.19),(.045,1.4,.035))
   if L>16:G.box('f11-service',(L*.75,1.4,-.08),(1,2.3,.14))
 # Tall red marker adjacent to east entrance, based on visible exterior photo.
 W.box('f11-red',(-59.3,6.1,3634.5),(1.2,11.7,2.7),True)
 E=Frame(B,-58.65,3634.5,-math.pi/2,y=0)
 E.box('f11-metal',(0,10.55,-.04),(1.9,1.7,.1));E.text('11',(0,10.1,-.12),1.22,'f11-dark')
 W.box('f11-canopy',(-57.5,3.15,3639.5),(7,.16,6),True)
 for z in [3637,3642]:W.tube('f11-metal',(-54.2,.3,z),(-54.2,3.15,z),.065,8)
 D=Frame(B,-59.4,3639.5,-math.pi/2,y=0)
 D.box('f11-frame',(0,1.65,-.02),(1.7,2.7,.1));D.box('f11-glass',(0,1.65,-.09),(1.55,2.55,.04));D.box('f11-metal',(.1,1.45,-.16),(.04,.35,.05))
 D.text('STATION 11',(0,2.9,-.15),.24,'f11-letter')
 F=Frame(B,-69.35,3653.7,-math.pi/2,y=0);F.text('CLARK COUNTY FIRE DEPARTMENT',(0,5.25,-.06),.35,'f11-letter')
 for x,z in [(-87,3650),(-78,3657),(-85,3657),(-78,3650)]:
  W.box('f11-service',(x,6.45,z),(1,.8,1.4));W.box('f11-dark',(x,6.88,z),(.8,.05,1.1))
 # Front gravel garden and separate engine apron; no underlying road regeneration.
 site=box(-105,3608,-23,3671).difference(p.buffer(.1));apron=box(-105,3646,-23,3666).union(box(-105,3608,-60,3620)).union(box(-105,3618,-95,3666))
 for x in range(-105,-23,3):
  for z in range(3608,3671,3):
   cell=site.intersection(box(x,z,x+3,z+3));B.planar('f11-concrete',cell.intersection(apron),.26,True);B.planar('f11-gravel',cell.difference(apron),.26,True)
 B.planar('f11-paving',p.buffer(1.8).difference(p),.32,True)
 B.planar('f11-paving',box(-60,3637,-24,3642).difference(p),.32,True)
 for z in np.arange(3647,3666,4):W.box('f11-joint',(-44,.275,z),(40,.015,.025))
 for x in np.arange(-91,-65,2.8):W.box('f11-line',(x,.28,3614),(.07,.02,4.5))
 for z in np.arange(3610,3645,2.4):
  W.tube('f11-bollard',(-24,.26,z),(-24,1.2,z),.13,10)
  W.tube('f11-white',(-24,.98,z),(-24,1.05,z),.134,10)
 W.tube('f11-metal',(-55,.3,3633),(-55,12.5,3633),.055,10)
 return dict(key=KEY,name='Clark County Fire Station 11',center=[-72,0,3641],bounds=[-106,3607,-22,3672],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
