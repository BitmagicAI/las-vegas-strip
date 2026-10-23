"""BLVD: mapped building parts, owner three-level plan and built 2026 photo.
Elevations are photograph estimates; source lease dates do not imply tenant opening.
"""
from common import *
from forum_shops import facade_frame
from showcase_iv import curtain,picnic
KEY='blvdRetail'
IDS=['way/1424222049','way/1505714402','way/1505714403','way/1424222051','way/1424222048','way/1505714401','way/1424222047']
DECK=14.0

def trim(B,p,lo,hi):
 for poly in parts(p):
  ps=list(poly.exterior.coords)
  for a,b in zip(ps,ps[1:]):
   if math.dist(a,b)<.25:continue
   F,L,nx,nz=facade_frame(B,a,b,p,.06)
   for y in [lo+.12,hi-.12]:F.box('blvd-painted-metal',(L/2,y,-.1),(L,.24,.23))
   if nx>.5:
    for y in np.arange(lo+1.2,hi,1.2):F.box('ph-joint',(L/2,y,-.02),(L,.02,.025))
    for u in np.arange(.3,L,3):F.box('ph-joint',(u,(lo+hi)/2,-.02),(.02,hi-lo,.025))

def storefront(B,z0,z1,label,mat='ph-white',x=38.5,style='glass'):
 F=Frame(B,x,z1,math.pi/2,y=0);L=z1-z0
 B.source='blvd-front/'+label
 F.box('ph-black',(L/2,6.8,-.10),(L-.12,13.2,.18))
 curtain(F,L,.25,13.25,metal='blvd-painted-metal')
 # Different tenant fascia volumes, rather than a repeated texture on one wall.
 if style=='screen':
  F.box('blvd-painted-metal',(L/2,9.8,-.34),(L-.3,6.0,.45))
  F.box(mat,(L/2,9.8,-.60),(L-.6,5.7,.05))
  F.text(label,(L/2,10,-.65),min(1.7,L/max(4,len(label)*.7)),'ph-white')
 elif style=='stone':
  F.box(mat,(L/2,9.6,-.30),(L-.3,6.6,.42));F.text(label,(L/2,10,-.54),min(1.5,L/max(4,len(label)*.7)),'ph-black')
 else:F.text(label,(L/2,10.1,-.38),min(1.65,L/max(4,len(label)*.7)),'ph-white')
 for u in [L*.5-1.5,L*.5+1.5]:
  F.box('ph-glass',(u,2,-.25),(2.85,3.7,.06))
  for dx in [-1.44,0,1.44]:F.box('ph-silver',(u+dx,2,-.32),(.055,3.8,.08))
  for dx in [-.12,.12]:F.tube('ph-silver',(u+dx,1.2,-.39),(u+dx,2,-.39),.024,6)
 F.box('blvd-painted-metal',(L/2,4.1,-.6),(L,.18,1.2))
 # Store-front blade signs establish depth at walking distance.
 F.box('ph-black',(.25,8.5,-.68),(.3,7.8,1.2))

def shade_tree(B,x,z,r=3.0):
 # Built rooftop's green steel funnel shade: open lattice, not foliage or opaque disk.
 B.source='blvd-roof-shades';y=DECK
 for a in np.linspace(0,math.tau,12,endpoint=False):
  B.tube('blvd-painted-metal',(x+.48*math.cos(a),y+.1,z+.48*math.sin(a)),(x+r*math.cos(a+.25),y+4.8,z+r*math.sin(a+.25)),.038,6)
 for yy,rr in [(1.2,.7),(2.7,1.35),(4.1,2.4),(4.8,r),(4.98,r*1.07)]:
  B.path('blvd-green-paint',[(x+rr*math.cos(a),y+yy,z+rr*math.sin(a)) for a in np.linspace(0,math.tau,33)],.05,6)
 B.lathe('blvd-painted-metal',(x,z),[(y,.55),(y+.12,.55)],16)

def exterior(B):
 B.property=KEY+'-exterior';B.detail=0
 north=unary_union([footprint(IDS[0]),footprint(IDS[1])]);south=unary_union([footprint(IDS[4]),footprint(IDS[5]),footprint(IDS[6])]);connector=footprint(IDS[2]);floor=unary_union([north,south,connector])
 bars=unary_union([footprint(IDS[0]),footprint(IDS[4]),footprint(IDS[6])])
 # Owner's terrace plan uses these upper parts, not the generic map's tiny 3m rise.
 B.source='blvd-street-apron'
 # Close private storefront-to-sidewalk gaps; retain the existing public walk and curb.
 apron=box(27,1011,42,1201).difference(unary_union([north,south,box(36,1086,108,1115)]))
 B.planar('ph-paving',apron,.075,True)
 B.source='blvd-shell'
 for p in [north,south]:
  B.shell(p,.15,DECK,'ph-stone',roof=False,solid=True);B.planar('ph-paving',p,.15,True)
  trim(B,p,.15,DECK)
 stair_opening=box(59.9,1091.8,82.0,1095.4)
 B.planar('tile',floor.difference(stair_opening),DECK,True)
 # Rear bridge connects roof wings; central street-to-rear passage stays open below.
 B.planar('blvd-painted-metal',connector.difference(stair_opening),DECK-.35)
 B.shell(connector.difference(stair_opening),DECK-.35,DECK,'blvd-painted-metal',roof=False,solid=True)
 for x,z in [(102,1089),(102,1098)]:B.box('blvd-painted-metal',(x,DECK/2,z),(.55,DECK,.55),True)
 B.source='blvd-roof-retail'
 B.shell(bars,DECK,DECK+4.6,'ph-stone',roof=False,solid=True)
 B.planar('forum-flat-roof',bars,DECK+4.6,True)
 for poly in parts(bars):
  ps=list(poly.exterior.coords)
  for a,b in zip(ps,ps[1:]):
   if math.dist(a,b)<.4:continue
   F,L,nx,nz=facade_frame(B,a,b,bars,.10)
   if nx<.7:curtain(F,L,DECK+.2,DECK+4.15,metal='blvd-painted-metal')
   F.box('blvd-painted-metal',(L/2,DECK+4.5,-.1),(L,.30,.35))
 # Continuous orange fascia and black steel/glass safety guards along exposed deck.
 B.source='blvd-terrace-edge'
 for poly in parts(floor):
  ps=list(poly.exterior.coords)
  for a,b in zip(ps,ps[1:]):
   if math.dist(a,b)<.4:continue
   F,L,nx,nz=facade_frame(B,a,b,floor,.02)
   if nx<-.3:
    F.box('blvd-copper',(L/2,DECK-.65,-.12),(L,1.2,.16))
    for u in np.arange(.12,L,1.5):F.box('blvd-painted-metal',(u,DECK-.65,-.23),(.065,1.3,.08))
   # Leave no railing inside a roof bar wall.
   if bars.buffer(.12).covers(LineString([a,b])):continue
   F.box('glass',(L/2,DECK+.58,0),(L,1.15,.07),True)
   F.box('blvd-painted-metal',(L/2,DECK+1.18,0),(L,.07,.12))
   for u in np.arange(0,L,1.6):F.box('blvd-painted-metal',(u,DECK+.60,0),(.07,1.2,.12))
 # Street fronts fitted to separate north/south mapped wings; tenant lettering is original.
 for z0,z1,label,mat,sty in [(1013,1031,'BOOT BARN','ph-stone','stone'),(1031,1043,'ABC STORES','ph-white','stone'),(1043,1058,'JD SPORTS','ph-black','screen'),(1058,1073,'H&M','ph-white','stone'),(1073,1086,'BLVD','ph-stone','stone'),(1115,1128,'adidas','ph-red','screen'),(1128,1142,'lululemon','ph-white','stone'),(1142,1155,'Abercrombie','walnut','stone'),(1155,1161,'SUNGLASS HUT','ph-black','glass'),(1161,1168,'LE VEIL','ph-stone','stone'),(1168,1184,'OPENING 2027','ph-red','screen'),(1184,1198,'PUMA','ph-glass','glass')]:
  section=(north if z0<1100 else south).intersection(box(0,z0,150,z1))
  frontx=section.bounds[0]-.18
  storefront(B,z0,z1,label,mat,x=frontx,style=sty)
 # South corner's diagonal steel/glass structure and large pylon frame.
 B.source='blvd-puma-corner';F=Frame(B,south.intersection(box(0,1184,150,1198)).bounds[0]-.18,1198,math.pi/2,y=0)
 for u in [0,4.5,9,13.5]:
  F.tube('ph-white',(u,.3,-.40),(min(14,u+4.5),6.7,-.40),.09,6)
  F.tube('ph-white',(min(14,u+4.5),6.7,-.40),(u,13.25,-.40),.09,6)
 F.box('blvd-painted-metal',(0,27,-.40),(10.5,29,1.7),True)
 F.box('ph-led-blue',(0,28,-1.30),(9.9,25,.08))
 F.text('PUMA',(0,29,-1.37),1.65,'ph-white');F.text('LAS VEGAS',(0,26.8,-1.37),.65,'ph-white');F.text('BLVD',(0,18,-1.37),1.2,'ph-white')
 # Public stairs in the documented central hub, with smooth collision and landings.
 B.source='blvd-hub-paving'
 # Private central access court: close the exposed terrain gap without rebuilding roads.
 court=box(36,1086,108,1115).difference(unary_union([north,south]))
 B.planar('ph-paving',court,.08,True)
 B.source='blvd-hub-stairs';S=Frame(B,41,1093.6,math.pi/2,y=0)
 S.stairs(0,0,3.4,6.9,18,y=.2);S.box('ph-paving',(0,6.96,19.5),(3.4,.28,3),True)
 S.stairs(0,21,3.4,6.9,18,y=7.1)
 S.box('ph-paving',(0,13.86,40.5),(3.4,.28,3),True)
 # Collision panels below sloped handrails prevent falling out sideways.
 for side in [-1,1]:
  u=side*1.65
  for z0,z1,y0,y1 in [(0,18,.2,7.1),(21,39,7.1,14)]:
   B.face('glass',[S.p(u,y0,z0),S.p(u,y1,z1),S.p(u,y1+1.05,z1),S.p(u,y0+1.05,z0)],True)
 # Guards around the deck opening leave the east landing unobstructed.
 for z in [1091.77,1095.43]:
  B.box('glass',(71,DECK+.55,z),(22,1.1,.06),True)
  B.box('blvd-painted-metal',(71,DECK+1.12,z),(22,.06,.1))
 # The landing joins connector at x82, beyond the head-clearance opening.
 B.source='blvd-hub-sign';H=Frame(B,37.5,1092.8,math.pi/2,y=0)
 for u in [-2.2,2.2]:H.box('blvd-painted-metal',(u,8.4,0),(.25,16.8,.3),True)
 H.box('ph-black',(0,13.0,0),(6.3,5.6,.45));H.text('BLVD',(0,15,-.25),1.05,'ph-white');H.text('Hilton',(0,13.4,-.25),.85,'ph-white');H.text('POLO TOWERS',(0,11.2,-.25),.40,'ph-white')
 # Sparse service units are placed only on occupied roofs, never over public terrace.
 B.source='blvd-roof-plant';B.detail=1
 for x in [96,101]:
  for z in np.arange(1024,1193,17):
   if not bars.contains(box(x-1.4,z-1,x+1.4,z+1)):continue
   B.box('blvd-painted-metal',(x,DECK+5.1,z),(2.8,1,2));B.box('ph-black',(x,DECK+5.65,z),(2.6,.1,1.8))
 terrace=floor.difference(bars)
 for x,z in [(72,1040),(72,1053),(73,1068),(68,1128),(68,1141),(68,1155)]:
  if terrace.contains(Point(x,z).buffer(3.3)):shade_tree(B,x,z)
 for x in [69,75]:
  for z in [1035,1048,1061,1074,1125,1138,1151]:
   if terrace.contains(Point(x,z).buffer(1.5)):picnic(B,x,z,DECK)
 B.detail=0
 (OUT/'blvd-retail-plan.json').write_text(json.dumps({'deckM':DECK,'roofM':DECK+4.6,'estimatedElevations':True,'floorAreaM2':floor.area,'terraceAreaM2':terrace.area,'ids':IDS},indent=2))
 return dict(key=KEY,name='BLVD retail and rooftop',center=[75,0,1106],bounds=[30,1008,130,1204],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
