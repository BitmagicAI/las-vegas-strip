"""4207 Las Vegas Blvd: mapped store/canopy, April2023 front reference."""
from common import *
from forum_shops import facade_frame
KEY='southShell'
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/store';B.detail=0
 p=footprint('way/457939126');c=footprint('way/457939125');F=Frame(B,0,0,y=.3)
 B.shell(p,.04,4.5,'ss-tan',roof=False);B.planar('ss-roof',p,4.5,True)
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  G,L,_,_=facade_frame(B,a,b,p,.04)
  for y in [.8,1.85,2.9]:G.box('ss-cream',(L/2,y,-.035),(L,.12,.06))
  G.box('ss-yellow',(L/2,4.2,-.035),(L,.55,.1));G.box('ss-red',(L/2,3.88,-.09),(L,.09,.08))
  # Glazed curved northwest entrance front, matching mapped canted segments.
  if a[0]<117 and b[0]<117:
   n=max(1,int(L/1.4));width=L/n
   for i in range(n):
    u=(i+.5)*width
    if L>6 and a[0]<108 and b[0]<108 and u>2.8:continue
    G.box('ss-glass',(u,1.9,-.07),(width-.09,2.9,.1))
    for dx in [-width/2,width/2]:G.box('ss-black',(u+dx,1.9,-.14),(.06,3,.07))
    G.box('ss-black',(u,1.7,-.14),(width,.04,.07))
   for y in [.4,3.4]:G.box('ss-black',(L/2,y,-.14),(L,.06,.07))
   if L>6 and a[0]<108 and b[0]<108:G.text('WINE  SLOTS',(L/2,3.65,-.17),.48,'ss-red')
  if a[1]<2938 and b[1]<2938:G.text('MINI MART',(L/2,3.4,-.17),.65,'ss-red')
 # Canopy is a suspended roof, never a solid mapped building.
 B.source='podium/canopy';B.shell(c,4.5,5.05,'ss-yellow',roof=True);B.planar('ss-cream',c,4.5,True)
 for a,b in zip(list(c.exterior.coords),list(c.exterior.coords)[1:]):
  G,L,_,_=facade_frame(B,a,b,c,0)
  G.box('ss-red',(L/2,4.57,-.05),(L,.12,.13));G.box('ss-white',(L/2,5.04,-.02),(L,.12,.12))
 for x in [76.2,82.7]:
  for z in [2943.5,2953.2]:
   F.box('ss-white',(x,2.32,z),(.32,4.4,.38),True)
   F.box('ss-cream',(x,.17,z),(1.35,.3,2.4),True)
   # Fuel dispenser casing, display,keypad,nozzle recesses and hanging hoses.
   F.box('ss-white',(x,1.25,z+.52),(.75,1.85,.5),True)
   F.box('ss-yellow',(x,2.16,z+.5),(1,.28,.68))
   for side in [-1,1]:
    G=Frame(B,x+side*.39,z+.52,side*math.pi/2,y=0)
    G.box('ss-black',(0,1.55,-.015),(.32,.47,.03));G.box('ss-screen',(0,1.63,-.04),(.25,.15,.02))
    for u in [-.07,0,.07]:
     for y in [1.37,1.42,1.47]:G.box('ss-metal',(u,y,-.04),(.035,.025,.02))
    G.path('ss-black',[(.22,1.75,-.08),(.4,1.68,-.09),(.5,.6,-.1),(.25,.4,-.12),(.18,1.1,-.14)],.025,6)
    G.box('ss-black',(.18,1.14,-.15),(.07,.22,.08))
 for x in [75,79.4,83.8]:
  for z in [2942,2948,2954]:F.box('ss-light',(x,4.17,z),(.55,.05,.55))
 # Storefront apron, flat forecourt and north access; preserve adjacent streets.
 B.source='podium/forecourt';site=box(41,2927,129,2962).difference(p)
 apron=p.buffer(1.3).difference(p)
 for x in range(41,129,4):
  for z in range(2927,2962,4):
   cell=site.intersection(box(x,z,x+4,z+4));B.planar('ss-asphalt',cell.difference(apron),.32,True);B.planar('ss-paving',cell.intersection(apron),.42,True)
 for x,z in [(113,2941),(120,2946)]:F.box('ss-metal',(x,4.54,z),(1.6,.68,1.3))
 for z in [2942,2945,2948,2951]:F.tube('ss-yellow',(105.4,.12,z),(105.4,1,z),.075,10)
 # Pump island protective posts.
 for x in [76.2,82.7]:
  for z in [2942.1,2945.1,2951.8,2954.8]:F.tube('ss-white',(x,.2,z),(x,.85,z),.07,10)
 G=Frame(B,72.8,2948,math.pi/2,y=0);G.box('ss-white',(0,5.1,0),(1.5,1.4,.14));
 # Raised red/yellow scallop emblem on the fascia sign.
 for mat,r,dep in [('ss-red',.58,-.1),('ss-yellow',.48,-.12)]:
  pts=[G.p(0,4.75,dep)]+[G.p(r*math.cos(a),5.05+r*math.sin(a),dep) for a in np.linspace(0,math.pi,13)]
  for i in range(1,len(pts)-1):B.face(mat,[pts[0],pts[i],pts[i+1]])
 for a in np.linspace(.18,math.pi-.18,7):G.path('ss-red',[(0,4.83,-.14),(.47*math.cos(a),5.05+.47*math.sin(a),-.14)],.018,5)
 B.detail=0
 return dict(key=KEY,name='Four Seasons Drive Shell and grocery exterior',center=[87,0,2945],bounds=[40,2926,130,2963],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
