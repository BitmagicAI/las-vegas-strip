"""3965 Desert Oasis: mapped courtyard building and detached south wing.
May2025 photographed architecture; roof heights inferred, not measured.
"""
from common import *
from forum_shops import facade_frame
KEY='desertOasis';IDS=['way/364846547','way/364846546','way/1424222041']
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/apartments';B.detail=0
 main=footprint(IDS[0]);south=footprint(IDS[1]);canopy=footprint(IDS[2]);F=Frame(B,53.45,2744.38,math.pi/2,y=.32)
 # Recessed entrance is a genuine open pedestrian passage through west wing.
 passage=box(52.8,2735.2,63.0,2739.4)
 B.shell(main.difference(passage),.32,6.05,'do-stucco',roof=False)
 B.shell(main.intersection(passage),3.15,6.05,'do-stucco',roof=False)
 B.planar('do-roof',main,6.05,True);B.planar('do-ceiling',main.intersection(passage),3.15,True)
 B.shell(south,.32,5.7,'do-stucco',roof=False);B.planar('do-roof',south,5.7,True)
 # Photo-visible frontage: squared tiled wings and three open red lattice panels.
 for lo,hi in [(0,3.0),(11.5,14.8)]:
  F.box('do-tile',((lo+hi)/2,3.2,-.10),(hi-lo,6.4,.24),True)
  for u in np.arange(lo+.4,hi,.4):F.box('do-joint',(u,3.2,-.235),(.014,6.38,.016))
  for y in np.arange(.4,6.4,.4):F.box('do-joint',((lo+hi)/2,y,-.235),(hi-lo,.013,.016))
 for u in [3.2,5.95,8.7,11.45]:F.box('do-tile',(u,3.15,-.42),(.32,6.3,.6),True)
 for u in [4.57,7.32,10.07]:
  panel=box(-1.18,2.75,1.18,6.2)
  holes=[Point(x,y).buffer(.095,resolution=5) for x in np.arange(-1.06,1.14,.25) for y in np.arange(2.9,6.15,.25)]
  panel=panel.difference(unary_union(holes))
  for t in triangles(panel):B.face('do-red',[F.p(u+x,y,-.52) for x,y in list(t.exterior.coords)[:-1]])
 F.text('Desert Oasis',(1.5,5.8,-.27),.32,'do-red');F.text('3965',(1.5,4.7,-.27),.26,'do-ink')
 # Entrance threshold and recessed steel gate are offset clear of through-route.
 F.box('do-gold',(9.8,1.3,-.28),(1.1,2.6,.16));F.box('do-glass',(9.8,1.6,-.38),(.85,1.6,.07))
 F.text('OFFICE',(9.8,2.78,-.4),.16,'do-ink')
 # Small side windows, downpipes and outdoor room doors along the courtyard.
 for poly,h in [(main,6.05),(south,5.7)]:
  for a,b in zip(list(poly.exterior.coords),list(poly.exterior.coords)[1:]):
   G,L,_,_=facade_frame(B,a,b,poly,.32)
   if a[0]<54 and b[0]<54 and poly==main:continue
   G.box('do-eave',(L/2,h-.32,-.15),(L,.18,.4))
   if L<4:continue
   for u in np.arange(2,L-1,3.8):
    for y in [1.45,4.25]:
     G.box('do-frame',(u,y,-.06),(.85,1.05,.12));G.box('do-glass',(u,y,-.135),(.66,.89,.04))
     G.box('do-frame',(u,y,-.18),(.04,.89,.035));G.box('do-sill',(u,y-.57,-.22),(1,.1,.4))
    G.box('do-joint',(u+1.6,2.65,-.04),(.025,5.1,.03))
   for u in [1,L-1]:G.tube('do-eave',(u,.3,-.22),(u,h-.4,-.22),.04,8)
 # Courtyard doors, balconies, accessible stairs at the east end.
 W=Frame(B,0,0,y=0)
 for x in np.arange(64,85,3.8):
  for y in [.32,3.1]:
   G=Frame(B,x,2737.49,math.pi,y=y)
   G.box('do-door',(0,1.15,-.09),(.85,2.3,.12));G.box('do-metal',(.28,1.1,-.18),(.04,.15,.04))
 W.box('do-walkway',(74,3.04,2738.25),(26,.15,1.5),True)
 for x in np.arange(61.5,87,.85):W.tube('do-rail',(x,3.1,2739.01),(x,4.1,2739.01),.023,7)
 W.tube('do-rail',(61.5,4.1,2739.01),(87,4.1,2739.01),.033,8)
 for i in range(17):W.box('do-walkway',(85.9,.32+(i+1)*2.78/17/2,2743.2-i*.25),(1.2,(i+1)*2.78/17,.25),True)
 for x in [85.25,86.55]:W.tube('do-rail',(x,1.2,2743.4),(x,4.1,2739),.035,8)
 # Existing mapped canopy is a roof on posts, not a wall across the access.
 B.shell(canopy,2.9,3.07,'do-eave',roof=True)
 for x,z in [(88.8,2747.9),(93,2747.9)]:W.box('do-metal',(x,1.62,z),(.14,2.6,.14),True)
 # Pylon with blank weathered lower cabinet, as photographed.
 P=Frame(B,43,2737,math.pi/2,y=.32)
 for u in [-1.2,1.2]:P.box('do-red',(u,3.1,0),(.28,6.2,.35),True)
 P.box('do-gold',(0,6.1,0),(4.7,2.5,.32),True);P.box('do-sign-paint',(0,6.35,-.19),(4.5,1.9,.05));P.box('do-red',(0,5.4,-.19),(4.5,.65,.05))
 P.text('MOTEL',(0,6,-.24),.74,'do-ink');P.text('APARTMENTS',(0,5.15,-.24),.4,'do-white')
 P.box('do-red',(0,3.5,0),(3.2,1.7,.37),True)
 for i in range(8):P.box('do-worn',(-1.35+i*.39,3.5,-.22),(.35,1.55,.06))
 # Complete walking and parking support, courtyard pool retained below deck.
 site=box(39,2728,119,2764).difference(main.union(south));pool=box(68,2740,75,2743.3)
 for x in range(39,119,3):
  for z in range(2728,2764,3):
   c=site.intersection(box(x,z,x+3,z+3)).difference(pool)
   B.planar('do-asphalt' if x<51 or x>96 or z>2760 else 'do-paving',c,.34,True)
 B.planar('do-paving',passage,.34,True)
 B.planar('do-pool',pool,.15);B.planar('do-paving',pool,-.8,True);B.shell(pool,-.8,.34,'do-tile',roof=False)
 for z in np.arange(2730,2759,2.8):W.box('do-line',(47,.35,z),(4.8,.015,.08))
 for x,z in [(69,2732),(81,2732),(98,2734),(110,2734),(68,2755),(86,2755)]:W.box('do-metal',(x,6.3 if z<2745 else 5.95,z),(1.3,.5,1.15))
 B.detail=0
 return dict(key=KEY,name='Desert Oasis apartments exterior',center=[79,0,2746],bounds=[38,2727,120,2765],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
