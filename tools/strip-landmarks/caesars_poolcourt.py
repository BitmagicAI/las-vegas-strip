"""Garden of the Gods: plan from Earth 2022 and Caesars August2024 map.
Horizontal dimensions are image-fit estimates. Deck10.2m is a documented
compatibility datum above retained legacy casino/gallery (roof8.5m), NOT a
surveyed real-world elevation. Do not label public hotel access verified.
"""
from common import *
Y=10.2
CX,CZ=-349.5,-3.5

def rounded(x,z,w,d,r=2):
 return box(x-w/2+r,z-d/2+r,x+w/2-r,z+d/2-r).buffer(r,quad_segs=8)

def plans():
 temple=Point(CX,CZ).buffer(18.2,quad_segs=32)
 venus=rounded(-397,-44,36,8,3.8)
 jupiter=scale(Point(-454,-48).buffer(1,quad_segs=24),5,10,origin=(-454,-48))
 apollo=rounded(-453,35,17,11,3)
 neptune=rounded(-397,-4,30,13,1.5)
 fortuna=scale(Point(-435,-4).buffer(1,quad_segs=24),11,9,origin=(-435,-4)).difference(box(-450,-9,-434,1))
 bacchusA=rounded(-461,-13,10,6,1);bacchusB=rounded(-461,7,10,6,1)
 return [('temple',temple),('venus',venus),('jupiter',jupiter),('apollo',apollo),('neptune',neptune),('fortuna',fortuna),('bacchus-north',bacchusA),('bacchus-south',bacchusB)]

def column(B,x,z,base,h,r=.45):
 B.box('cp-white',(x,base+.2,z),(r*3,.4,r*3),True)
 B.lathe('cp-white',(x,z),[(base+.4,r*1.4),(base+.55,r*1.4),(base+.68,r),(base+h-.9,r*.82),(base+h-.75,r*1.35),(base+h-.45,r*1.48),(base+h-.25,r*1.55)],24)
 B.box('cp-white',(x,base+h-.12,z),(r*3.3,.24,r*3.3))
 for a in np.linspace(0,math.tau,16,endpoint=False):
  B.tube('cp-flute',(x+r*.985*math.cos(a),base+.75,z+r*.985*math.sin(a)),(x+r*.82*math.cos(a),base+h-.95,z+r*.82*math.sin(a)),.028,4)
 # Main shaft collision uses a simple octagonal cylinder, not individual flutes.
 ps=list(Point(x,z).buffer(r*.81,quad_segs=2).exterior.coords);solid=B.solids[B.property]
 for a,b in zip(ps,ps[1:]):
  n=len(solid['vertices'])//3;solid['vertices'].extend([a[0],base+.4,a[1],b[0],base+.4,b[1],b[0],base+h-.25,b[1],a[0],base+h-.25,a[1]]);solid['indices'].extend([n,n+1,n+2,n,n+2,n+3])

def lounger(B,x,z,yaw=0):
 F=Frame(B,x,z,yaw,Y)
 F.box('cp-chair-frame',(0,.34,0),(.8,.14,2.05))
 F.box('cp-cushion',(0,.46,-.24),(.74,.12,1.45))
 for s in [-1,1]:F.box('cp-chair-frame',(s*.33,.17,0),(.07,.34,1.6))
 # Backrest is an actual inclined shell, not a standing block.
 a=F.p(-.37,.51,.46);b=F.p(.37,.51,.46);c=F.p(.37,.96,1);d=F.p(-.37,.96,1)
 B.face('cp-cushion',[a,b,c,d]);B.face('cp-cushion',[d,c,b,a])

def cabana(B,x,z):
 F=Frame(B,x,z,0,Y)
 F.box('cp-deck',(0,.12,0),(4.1,.24,4.1),True)
 for xx in [-1.85,1.85]:
  for zz in [-1.85,1.85]:F.box('cp-chair-frame',(xx,1.7,zz),(.13,3.4,.13))
 F.box('cp-fabric',(0,3.33,0),(4.2,.16,4.2))
 for xx in [-1.86,1.86]:F.box('cp-fabric',(xx,1.7,1.12),(.065,3.2,1.6))
 F.box('cp-fabric',(0,1.7,1.86),(3.7,3.2,.065))
 F.box('cp-cushion',(0,.45,1.1),(2.7,.4,1.1));F.box('cp-chair-frame',(0,.3,-.7),(1.2,.6,.7))

def exterior(B):
 B.source='caesars-poolcourt';B.detail=0
 from caesars_exterior import IDS
 court=box(-473,-64,-307,52).difference(footprint('way/115672893').buffer(.1)).difference(unary_union([footprint(i).buffer(.5) for i in IDS]))
 pools=plans();water=unary_union([p for _,p in pools]);deck=court.difference(water)
 B.planar('cp-deck',deck,Y,True)
 B.shell(court,Y-.5,Y,'cp-stone',roof=False,solid=True)
 for name,p in pools:
  B.planar('cp-basin',p,Y-1.45,True)
  B.shell(p,Y-1.45,Y,'cp-basin',roof=False,solid=True)
  B.planar('cp_pool',p,Y-.28)
  B.planar('cp-white',p.buffer(.65).difference(p),Y+.025)
  # Dark blue tile edging and inset pool-bottom motif, under animated water.
  B.planar('cp-pool-tile',p.buffer(-.4).difference(p.buffer(-.65)),Y-1.42)
  B.planar('cp-pool-tile',p.buffer(-1.5).difference(p.buffer(-1.65)),Y-1.419)
 # Temple's radiating inlaid pool bottom.
 for a in np.linspace(0,math.tau,24,endpoint=False):
  tip=(CX+17.3*math.cos(a),CZ+17.3*math.sin(a));u=(CX+5.8*math.cos(a-.07),CZ+5.8*math.sin(a-.07));v=(CX+5.8*math.cos(a+.07),CZ+5.8*math.sin(a+.07))
  B.planar('cp-pool-tile',Polygon([tip,u,v]),Y-1.418)
 # Circular central temple: continuous entablature, ribbed patinated dome.
 island=Point(CX,CZ).buffer(5.8,quad_segs=24)
 B.shell(island,Y-1.45,Y+.12,'cp-white',solid=True)
 for a in np.linspace(0,math.tau,8,endpoint=False):column(B,CX+4.9*math.cos(a),CZ+4.9*math.sin(a),Y+.12,7.2,.46)
 B.lathe('cp-white',(CX,CZ),[(Y+7.25,5.2),(Y+7.45,5.6),(Y+8.2,5.6),(Y+8.38,5.85),(Y+8.55,5.85)],64)
 dome=[(Y+8.55+4.65*math.sin(a),5.5*math.cos(a)) for a in np.linspace(0,math.pi/2,18)]
 B.lathe('cp-patina',(CX,CZ),dome,64)
 for a in np.linspace(0,math.tau,24,endpoint=False):
  B.path('cp-patina-seam',[(CX+(r+.03)*math.cos(a),y+.015,CZ+(r+.03)*math.sin(a)) for y,r in dome],.035,4)
 for y,r in dome[3:-1:3]:B.lathe('cp-patina-seam',(CX,CZ),[(y,r+.035),(y+.04,r+.035)],64)
 B.lathe('cp-white',(CX,CZ),[(Y+13.2,.35),(Y+13.65,.35),(Y+13.65,0)],24)
 # Four bowl fountains, geometry only; spray animation and central sculpture pending.
 for a in [0,math.pi/2,math.pi,math.pi*1.5]:
  x,z=CX+5.85*math.cos(a),CZ+5.85*math.sin(a)
  B.lathe('cp-white',(x,z),[(Y-.6,.6),(Y+.3,.65),(Y+.9,1.2),(Y+1.05,1.3),(Y+1.05,.2)],32)
 for a in np.linspace(0,math.tau,8,endpoint=False):column(B,CX+20.8*math.cos(a),CZ+20.8*math.sin(a),Y,7.7,.42)
 # Colonnades flanking Neptune, doors/paths remain between columns.
 for z in [-14,6]:
  for x in [-411,-404,-397,-390,-383]:column(B,x,z,Y,4.6,.28)
  B.box('cp-white',(-397,Y+4.65,z),(31,.45,1.05))
 # Pale inset walking patterns use non-overlapping geometric rings.
 for r in [22,27]:B.planar('cp-inlay',Point(CX,CZ).buffer(r,quad_segs=48).difference(Point(CX,CZ).buffer(r-.18,quad_segs=48)).intersection(deck),Y+.016)
 for x in [-467,-426,-376,-310]:B.planar('cp-inlay',box(x,-63,x+.22,51).intersection(deck),Y+.017)
 # Rows of actual cabanas and low orange loungers, all batched by material.
 B.detail=1
 for x in np.arange(-419,-376,6):
  for z in [-57,-30]:
   if court.contains(box(x-2.2,z-2.2,x+2.2,z+2.2)):cabana(B,x,z)
 for x in np.arange(-418,-375,2.15):
  for z in [-50,-37]:lounger(B,x,z,math.pi if z==-37 else 0)
 for a in np.linspace(0,math.tau,40,endpoint=False):
  x,z=CX+24.2*math.cos(a),CZ+24.2*math.sin(a)
  if court.contains(Point(x,z).buffer(1.5)) and not water.buffer(1.6).contains(Point(x,z)):lounger(B,x,z,math.pi/2-a)
 for z in np.arange(-58,44,2.8):
  for x in [-469,-442]:
   if court.contains(Point(x,z).buffer(1.5)) and not water.buffer(1.8).contains(Point(x,z)):lounger(B,x,z,math.pi/2)
 B.detail=0
 # Pool court guard at exposed boundaries. Public-access opening is not invented.
 for poly in parts(court):
  ps=list(poly.exterior.coords)
  for a,b in zip(ps,ps[1:]):
   if math.dist(a,b)<1:continue
   F,L,_,_=__import__('forum_shops').facade_frame(B,a,b,court,0)
   F.box('cp-white',(L/2,Y+.62,0),(L,1.24,.24),True)
   F.box('cp-white',(L/2,Y+1.29,0),(L,.10,.38))
 report={'deckDatumM':Y,'datumReason':'Preserves legacy casino roof8.5m; estimated compatibility datum, not surveyed pool elevation.','court':list(court.exterior.coords) if court.geom_type=='Polygon' else [],'pools':[{'name':n,'bounds':list(p.bounds),'area':p.area} for n,p in pools],'remaining':['Statue sculpture, fountain spray, mature landscape and connected public hotel access.','Actual pool-court elevation needs reconciliation with retained interiors.']}
 Path('build/city-exteriors/caesars-pool-plan.json').write_text(json.dumps(report,indent=2))
