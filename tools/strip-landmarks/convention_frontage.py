"""Convention Center frontage: Earth2022-24 + ground photographs, metres.
Mapped restaurant address stale: corner is El Gordo3041, El Pastor3049 in south row.
Heights other than mapped Royal8levels are photo estimates. No new public interiors.
"""
from common import *
from forum_shops import facade_frame
from sahara_retail import equipment
from venetian_pool_garden import gardens
KEY='conventionFrontage';IDS=['way/'+s for s in ['320330805','1419057375','276427198','331347691']]
def window(F,u,y,w,h):
 F.box('cf-glass',(u,y,-.12),(w,h,.1))
 for dx in [-w/2,0,w/2]:F.box('cf-frame',(u+dx,y,-.2),(.055,h+.1,.08))
 for yy in [y-h/2,y+h/2]:F.box('cf-frame',(u,yy,-.2),(w,.065,.08))
def patio_chair(B,x,z,mat):
 B.box(mat,(x,.72,z),(.45,.06,.46));B.box(mat,(x,1.02,z+.23),(.45,.55,.05))
 for dx in [-.18,.18]:
  for dz in [-.18,.18]:B.tube(mat,(x+dx,.23,z+dz),(x+dx,.7,z+dz),.024,4)
def exterior(B):
 B.property=KEY+'-exterior';B.detail=0
 royal,liq,taco,shops=[footprint(i) for i in IDS];allp=unary_union([royal,liq,taco,shops])
 # Royal: eight storeys, recessed repeated balcony cells on both long elevations.
 B.source='royal-resort';h=25.4;B.shell(royal,.24,h,'cf-white',roof=False);B.planar('cf-flat-roof',royal,h,True)
 for pp in parts(royal):
  cc=list(pp.exterior.coords)
  for a,b in zip(cc,cc[1:]):
   F,L,nx,nz=facade_frame(B,a,b,pp,.02)
   F.box('cf-white',(L/2,h+.22,-.05),(L,.44,.42),True)
   if abs(nz)>.7:
    n=max(1,round(L/3.9));w=L/n
    for floor in range(1,8):
     y=.24+floor*3.12
     F.box('cf-white',(L/2,y,-1),(L,.17,2.1),True)
     for i in range(n):
      u=(i+.5)*w;window(F,u,y+1.3,w-.5,2.4)
      F.box('cf-white',(i*w,y+1.5,-1),(.17,3,2.1),True)
      F.box('cf-blue',(u,y+1,-2.02),(w-.18,.055,.06),True)
      for q in np.arange(i*w+.22,(i+1)*w-.12,.2):F.box('cf-blue',(q,y+.54,-2.02),(.025,.92,.035))
    F.box('cf-white',(L/2,25,-1),(L,.18,2.1),True)
    for u in np.arange(2,L-1,4):window(F,u,1.7,3.1,2.55)
   else:
    for y in np.arange(3.2,h,3.12):F.box('cf-joint',(L/2,y,-.03),(L,.035,.03))
    for u in np.arange(1,L,3.7):F.box('cf-joint',(u,h/2,-.035),(.035,h,.04))
 equipment(B,royal,h)
 # Front porte cochere: open drive-through, doubled blue horizontal trim.
 canopy=box(921,-1800,936,-1783);B.planar('cf-flat-roof',canopy,4.65,True)
 B.planar('cf-asphalt',box(919,-1801,938,-1782).difference(royal),.06,True)
 for z in [-1800,-1783]:
  B.box('cf-white',(928.5,4.55,z),(15,.85,.45),True)
  for y in [4.32,4.76]:B.box('cf-blue',(928.5,y,z-.24),(15,.08,.05))
 for x in [921.4,935.6]:
  for z in [-1798.8,-1784]:B.box('cf-white',(x,2.2,z),(.55,4.4,.55),True)
 F=Frame(B,928.5,-1800,0,y=0);F.text('ENTRANCE',(0,4.42,-.26),.37,'cf-blue')
 # Clearly framed closed lobby entrance below the canopy.
 for x in [927.7,929.0]:
  B.box('cf-frame',(x,1.63,-1782.83),(1.3,2.82,.12))
  B.box('cf-glass',(x,1.66,-1782.91),(1.16,2.61,.06))
  B.tube('cf-frame',(x+.43,1,-1782.96),(x+.43,1.8,-1782.96),.025,6)
 # The sign spine stands beside the canopy, not on top of the guest tower.
 B.box('cf-white',(936.2,7.4,-1797),(3.5,14.8,1.05),True)
 for x in [935.3,936.2,937.1]:B.box('cf-blue',(x,7.3,-1797.56),(.12,13.8,.06))
 B.box('cf-blue',(936.2,10.2,-1797.7),(6.2,4.15,.32))
 B.box('cf-screen',(936.2,10.2,-1797.9),(5.8,3.75,.08))
 F=Frame(B,936.2,-1797.96,0,y=0);F.text('ROYAL RESORT',(0,14.45,0),.52,'cf-blue');F.text('ROYAL',(0,10.3,0),.7,'cf-white')
 # Arrival walks kept inside the forecourt, with an open vehicle lane.
 B.planar('cf-paving',box(890,-1804,967,-1785).difference(box(919,-1805,938,-1782)),.18,True)
 for x in [893,902,912,947,956,964]:
  B.planar('cf-gravel',Point(x,-1801).buffer(1.45),.19)
 gardens(B,box(890,-1805,967,-1784),royal,lambda q:q,.18,points=[(x,-1801) for x in [893,902,912,947,956,964]],crown_clearance=0)
 B.detail=0
 # Back pool terrace visible on Earth. Basin is dry in the available aerial reference.
 basin=box(947,-1760,962,-1751).buffer(1.5,resolution=8)
 B.planar('cf-paving',basin.buffer(3),.2,True);B.planar('cf-pool-dry',basin,.21,True)
 # Two connected white retail wings; one-storey storefronts beneath tall sign fascia.
 for name,p in [('liquor',liq),('shops',shops)]:
  B.source=name;hh=6.5
  B.shell(p,.24,hh,'cf-white',roof=False);B.planar('cf-flat-roof',p,hh,True)
  for pp in parts(p):
   cc=list(pp.exterior.coords)
   for a,b in zip(cc,cc[1:]):
    F,L,nx,nz=facade_frame(B,a,b,pp,.04)
    front=(name=='liquor' and nx<-.7) or (name=='shops' and (nz<-.7 or nx<-.7))
    if L<1:continue
    F.box('cf-white',(L/2,hh,-.12),(L,.22,.35))
    if front and L>4:
     for y in np.arange(3.5,hh,.55):F.box('cf-joint',(L/2,y,-.12),(L,.025,.035))
     for u in np.arange(1.8,L-1,3.4):window(F,u,1.75,3.12,2.65)
     F.box('cf-frame',(L/2,3.25,-.72),(L,.14,1.4))
     for u in np.arange(5,L-1,10.2):
      for dx in [-.7,.7]:
       F.box('cf-frame',(u+dx,1.52,-.25),(1.38,2.74,.08))
       F.box('cf-glass',(u+dx,1.55,-.3),(1.24,2.52,.06))
       F.tube('cf-frame',(u+dx+.43,1,-.35),(u+dx+.43,1.7,-.35),.022,5)
     for u in np.arange(1,L,3):F.tube('cf-frame',(u,4,-.15),(u,3.3,-1.3),.024,4)
     if name=='liquor':F.text('LIQUOR',(L*.5,4.5,-.22),1.2,'cf-red')
     elif nx<-.7 and L>10:
      if F.x<750:F.text('Tacos el Pastor',(L/2,4.6,-.22),.85,'cf-red')
      elif F.x>820:F.text('KIMCHI',(L/2,4.6,-.22),.9,'cf-red')
     elif nz<-.7 and L>35:
      F.text('TACOS EL PASTOR',(L*.15,4.6,-.22),.75,'cf-red')
      # Unverified tenants get storefront geometry without invented business names.
    elif L>7:
     F.box('cf-service',(L/2,1.7,-.15),(1.4,2.9,.1))
     for u in np.arange(2,L,5):F.box('cf-joint',(u,hh/2,-.1),(.025,hh-.3,.04))
  equipment(B,p,hh)
 # Small colorful patio on the northern storefront edge, safely outside road.
 pad=box(739,-1746,755,-1742);B.planar('cf-paving',pad,.24,True)
 for x in [742,747,752]:
  B.box('cf-frame',(x,1,-1744),(1,.07,1));B.tube('cf-frame',(x,.24,-1744),(x,.97,-1744),.06,6)
  patio_chair(B,x-.8,-1744,'cf-red');patio_chair(B,x+.8,-1744,'cf-blue')
 # Corner El Gordo: tan fascia, red tiled piers and pitched red metal edge roofs.
 B.source='tacos-el-gordo';hh=5.8
 B.shell(taco,.24,hh,'cf-tan',roof=False);B.planar('cf-flat-roof',taco,hh,True)
 for pp in parts(taco):
  cc=list(pp.exterior.coords)
  for a,b in zip(cc,cc[1:]):
   F,L,nx,nz=facade_frame(B,a,b,pp,.04)
   if L<3:continue
   front=nx<-.35 or nz<-.35
   if front:
    for u in np.arange(1.8,L-1,3.5):
     window(F,u,1.8,3.1,2.8)
     F.box('cf-red-tile',(u-1.65,1.8,-.25),(.25,3.3,.45),True)
    F.box('cf-red',(L/2,3.45,-.3),(L,.23,.55))
    F.text('TACOS EL GORDO',(L/2,4.4,-.3),min(.95,L/17),'cf-red')
    F.b.upface('cf-metal-roof',[F.p(0,5.7,-.6),F.p(L,5.7,-.6),F.p(L,7.1,1.2),F.p(0,7.1,1.2)],True)
    for u in np.arange(.25,L,.45):F.tube('cf-roof-seam',(u,5.72,-.6),(u,7.12,1.2),.022,4)
    for u in [0,L]:
     F.box('cf-red-tile',(u,2.95,-.35),(.5,5.9,.6),True)
   else:
    F.box('cf-service',(L/2,1.7,-.16),(1.5,2.9,.15))
 # Distinct west corner entrance gable.
 F=Frame(B,747.7,-1779.7,math.pi/2,y=0)
 F.b.face('cf-red',[F.p(-2.6,5.2,0),F.p(2.6,5.2,0),F.p(2.6,7.5,0),F.p(0,9.1,0),F.p(-2.6,7.5,0)])
 F.path('cf-tan',[(-2.65,5.2,-.05),(-2.65,7.55,-.05),(0,9.17,-.05),(2.65,7.55,-.05),(2.65,5.2,-.05)],.08,6)
 F.text('TACOS',(0,6.35,-.06),.72,'cf-white');F.text('3041',(0,5.6,-.06),.35,'cf-white')
 equipment(B,taco,hh)
 return dict(key=KEY,name='Convention Center Drive frontage',center=[850,0,-1764],bounds=list(allp.buffer(5).bounds),structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],views={})
