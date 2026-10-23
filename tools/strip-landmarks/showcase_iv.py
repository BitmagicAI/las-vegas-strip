"""Showcase IV and neighboring Walgreens: mapped plans, Nadel/Gindi/Earth refs.
Vertical divisions and rooftop furniture placement remain photo estimates.
No commercial reference photography is used as a game texture.
"""
from common import *
from forum_shops import facade_frame
IDS=['way/115649938','way/95224290']
ROOF=22.86

def curtain(F,L,lo,hi,metal='ph-metal'):
 F.box('ph-glass',(L/2,(lo+hi)/2,-.07),(L-.12,hi-lo,.08))
 for x in np.arange(.15,L,1.65):F.box(metal,(x,(lo+hi)/2,-.17),(.065,hi-lo,.13))
 for y in np.arange(lo+2.2,hi,2.2):F.box('ph-silver',(L/2,y,-.16),(L,.045,.10))
 for y in [lo,hi]:F.box(metal,(L/2,y,-.26),(L,.28,.44))

def picnic(B,x,z,y,angle=0):
 F=Frame(B,x,z,angle,y=y)
 F.box('walnut',(0,.76,0),(2.0,.09,.85))
 for side in [-1,1]:
  F.box('walnut',(0,.45,side*.7),(2.0,.08,.32))
  for xx in [-.65,.65]:
   F.tube('steel',(xx,.06,side*.83),(xx,.72,side*.26),.035,6)
 F.tube('steel',(-.65,.3,0),(.65,.3,0),.035,6)

def build(B):
 p=footprint(IDS[0]);B.source='showcase-iv-shell';B.detail=0
 # The old generic12m mapped box is wholly replaced, not hidden behind a taller facade.
 B.shell(p,.18,ROOF,'ph-stone',roof=False,solid=True)
 B.planar('ph-stone',p,.18,True)
 terrace=p.intersection(box(37.4,1242.5,67.5,1273.6))
 B.planar('forum-flat-roof',p.difference(terrace),ROOF,True)
 for poly in parts(p):
  ps=list(poly.exterior.coords)
  for a,b in zip(ps,ps[1:]):
   if math.dist(a,b)<.4:continue
   F,L,nx,nz=facade_frame(B,a,b,p,.10)
   west=nx<-.7 and max(a[0],b[0])<40
   north=nz<-.7
   if west:
    for lo,hi in [(.35,5.65),(6.0,13.55),(13.9,22.2)]:curtain(F,L,lo,hi)
   elif north and min(a[0],b[0])<60:
    # Glazing wraps the northwest corner, then changes to the service wall.
    for lo,hi in [(6,13.55),(13.9,22.2)]:curtain(F,min(L,21),lo,hi)
   else:
    for yy in [5.8,13.7,22.3]:F.box('ph-white',(L/2,yy,-.12),(L,.24,.28))
    B.detail=1
    for xx in np.arange(.3,L,3.2):F.box('ph-joint',(xx,11.3,-.045),(.02,22.3,.025))
    for yy in np.arange(1.2,22,1.2):F.box('ph-joint',(L/2,yy,-.04),(L,.015,.025))
    B.detail=0
   F.box('ph-white',(L/2,22.55,-.16),(L,.62,.38))
 # Set-back ground entry glazing and doors; interiors remain outside this pass.
 B.source='showcase-iv-street'
 F=Frame(B,36.53,1260.5,math.pi/2,y=0)
 for u in [-11,-3,7,13]:
  F.box('ph-black',(u,2.25,-.2),(2.8,4.1,.08))
  for dx in [-1.44,0,1.44]:F.box('ph-silver',(u+dx,2.25,-.28),(.07,4.15,.10))
  F.box('ph-silver',(u,4.33,-.28),(2.94,.08,.12))
  for dx in [-.15,.15]:F.tube('ph-silver',(u+dx,1.3,-.36),(u+dx,2.1,-.36),.024,6)
 F.box('ph-metal',(2,5.8,-.85),(27,.30,1.8))
 # North Target panel and upper Olive Garden panel retain the actual sign volumes.
 F.box('ph-red',(7.6,9.6,-.42),(12.3,6.4,.45))
 for r,w in [(1.65,.29),(.64,.64)]:
  if r==.64:
   pts=[F.p(10+.64*math.cos(t),10+.64*math.sin(t),-.70) for t in np.linspace(0,math.tau,65)[:-1]];B.face('ph-white',list(reversed(pts)))
  else:
   for a,b in zip(np.linspace(0,math.tau,97)[:-1],np.linspace(0,math.tau,97)[1:]):
    B.face('ph-white',list(reversed([F.p(10+(r-w/2)*math.cos(a),10+(r-w/2)*math.sin(a),-.70),F.p(10+(r+w/2)*math.cos(a),10+(r+w/2)*math.sin(a),-.70),F.p(10+(r+w/2)*math.cos(b),10+(r+w/2)*math.sin(b),-.70),F.p(10+(r-w/2)*math.cos(b),10+(r-w/2)*math.sin(b),-.70)])))
 F.text('target',(5.4,8.0,-.73),1.02,'ph-white')
 F.box('cr-sage-stucco',(7.6,19.0,-.39),(12.3,5.7,.35))
 F.text('Olive Garden',(7.6,19.3,-.60),1.05,'ph-white')
 F.text('ITALIAN KITCHEN',(7.6,17.7,-.61),.38,'ph-white')
 # A projecting south sign fin is19.51m high per the structural engineer.
 F.box('ph-red',(-12.8,12.255,-.85),(3.7,19.51,1.0))
 F.box('ph-glass',(-12.8,12.25,-1.37),(3.1,17.4,.06))
 for i,ch in enumerate('BURLINGTON'):F.text(ch,(-12.8,20.2-i*1.6,-1.43),.9,'ph-white')
 for u,w,label,mat in [(-7.5,5.3,'CHEVYS','cr-sage-stucco'),(-1.8,5.3,'PARADOX','ph-black')]:
  F.box(mat,(u,9.5,-.40),(w,7.0,.28));F.text(label,(u,9.5,-.58),.70,'ph-white')
 # Roof terrace: front30m of parcel, enclosed bar to its east and south service strip.
 B.source='showcase-iv-rooftop'
 terrace=p.intersection(box(37.4,1242.5,67.5,1273.6))
 B.planar('tile',terrace,ROOF,True)
 club=p.intersection(box(67.5,1243.0,84.4,1266.3))
 B.shell(club,ROOF,ROOF+4.3,'ph-white',roof=False,solid=True)
 B.planar('forum-flat-roof',club,ROOF+4.3,True)
 C=Frame(B,67.35,1266.2,math.pi/2,y=ROOF)
 curtain(C,23,.12,3.75)
 # Slender glazed guards on terrace edges; solid skirt and handrail preserve safety.
 for poly in parts(terrace):
  ps=list(poly.exterior.coords)
  for a,b in zip(ps,ps[1:]):
   if abs(a[0]-67.5)<.1 and abs(b[0]-67.5)<.1:continue
   G,L,_,_=facade_frame(B,a,b,terrace,0)
   G.box('ph-metal',(L/2,ROOF+.10,0),(L,.2,.22),True)
   G.box('ph-glass',(L/2,ROOF+.68,0),(L,1.08,.065),True)
   G.box('ph-silver',(L/2,ROOF+1.23,0),(L,.055,.08))
   for u in np.arange(0,L,1.8):G.box('ph-metal',(u,ROOF+.67,0),(.06,1.15,.10))
 # West canopy/sign frame, documented in2022Earth and current venue photos.
 C=Frame(B,48.5,1254,math.pi/2,y=ROOF)
 for xx in [-7.2,7.2]:
  for zz in [-6.0,6.0]:C.box('steel',(xx,3.4,zz),(.20,6.8,.20),True)
 for yy in [3.9,6.7]:
  for zz in [-6.0,6.0]:C.box('steel',(0,yy,zz),(14.6,.22,.22))
  for xx in [-7.2,7.2]:C.box('steel',(xx,yy,0),(.22,.22,12.0))
 for xx in [-7.2,0,7.2]:
  C.tube('steel',(xx,3.9,-6),(xx,6.7,0),.075,6);C.tube('steel',(xx,6.7,0),(xx,3.9,6),.075,6)
 C.box('ph-led-blue',(0,2.7,-6.08),(14.6,2.05,.12))
 C.text('BREWDOG',(0,2.8,-6.18),1.45,'ph-white')
 # Pale tensioned central shade with faceted rising center, tucked inside frame.
 corners=[(-6,-4.8),(6,-4.8),(6,4.8),(-6,4.8)]
 for a,b in zip(corners,corners[1:]+corners[:1]):
  B.upface('cp-fabric',[C.p(a[0],5.35,a[1]),C.p(b[0],5.35,b[1]),C.p(0,6.5,0)])
 # Secondary flat shade and furnishings; repeated tables are material-batched.
 B.box('ph-white',(61.8,ROOF+3.35,1255),(9.5,.20,13.0))
 for x in [57.2,66.4]:
  for z in [1249,1261]:B.box('steel',(x,ROOF+1.65,z),(.12,3.3,.12),True)
 B.detail=1
 for x in [41.3,45.2,49.1,53.0,56.9,61.0]:picnic(B,x,1244.2,ROOF+.06,math.pi/2)
 for x in [42,48,54,60]:
  for z in [1266.2,1270.1]:picnic(B,x,z,ROOF+.06)
 for z in [1250,1255,1260]:picnic(B,62,z,ROOF+.06,math.pi/2)
 # Rooftop service equipment stays behind bar, following the observed east plant zone.
 for x,z,w,d in [(91,1247,4,3),(94,1254,4,3),(99,1262,5,3),(105,1262,5,3),(115,1256,10,9),(91,1271,5,3),(112,1271,6,3)]:
  if not p.contains(box(x-w/2,z-d/2,x+w/2,z+d/2)):continue
  B.box('ph-metal',(x,ROOF+1,z),(w,2,d));B.box('ph-black',(x,ROOF+2.05,z),(w-.3,.08,d-.3))
  for dx in [-w*.25,w*.25]:B.lathe('ph-silver',(x+dx,z),[(ROOF+2.1,.65),(ROOF+2.17,.65)],16)
 B.detail=0
 walgreens(B)
 return {'ids':IDS,'roofM':ROOF,'heightSource':'Estimated75ft roof; storeydivisions photo fitted','terraceBounds':list(terrace.bounds),'remaining':['Public vertical access/retail interiors','Exact promotional artwork and Target Bullseye dog sculpture','Roof furniture and signage panel layout approximate']}

def walgreens(B):
 p=footprint(IDS[1]);B.source='walgreens-showcase';h=6.45
 B.shell(p,.12,h,'ph-stone',roof=False,solid=True);B.planar('forum-flat-roof',p,h,True)
 for poly in parts(p):
  ps=list(poly.exterior.coords)
  for a,b in zip(ps,ps[1:]):
   if math.dist(a,b)<.2:continue
   F,L,nx,nz=facade_frame(B,a,b,p,.12)
   for y in [.3,4.8,6.1]:F.box('ph-white',(L/2,y,-.12),(L,.18,.28))
   if nx<-.5:
    curtain(F,L,.4,4.6)
    F.box('ph-white',(L/2,5.35,-.25),(L,1.2,.45))
    if L>12:F.text('Walgreens',(L/2,5.25,-.51),1.1,'ph-red')
    F.box('ph-metal',(L/2,4.62,-.72),(L,.15,1.45))
   else:
    for x in np.arange(.5,L,4):F.box('ph-joint',(x,3,-.04),(.02,6,.025))
 for x,z in [(51,1219),(69,1217),(82,1224),(95,1218)]:
  if not p.contains(box(x-1.5,z-1,x+1.5,z+1)):continue
  B.box('ph-metal',(x,h+.55,z),(3,1.1,2));B.box('ph-black',(x,h+1.14,z),(2.8,.06,1.8))
