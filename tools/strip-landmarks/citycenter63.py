"""63 CityCenter: owner 2025 leasing plans + exterior photographs.
Mapped plan, estimated elevations. No commercial photograph/ad is used as texture.
"""
from common import *
from forum_shops import facade_frame
KEY='citycenter63'
MAIN='way/1421481100';WING='way/1422113647'

def slab(B,p,y,mat='ph-silver',thick=.32):
 B.planar(mat,p,y,True);B.shell(p,y-thick,y,mat,roof=False,solid=True)
 B.planar(mat,p,y-thick)

def facade(B,p,lo,hi,glass=True,main=False):
 B.shell(p,lo,hi,'ph-glass' if glass else 'ph-silver',roof=False,solid=True)
 for poly in parts(p):
  coords=list(poly.exterior.coords)
  for a,b in zip(coords,coords[1:]):
   F,L,nx,nz=facade_frame(B,a,b,p,.035)
   clad=main and (nz<-.12 or nx<.1)
   if clad:
    B.face('ph-silver',[F.p(0,lo,-.14),F.p(L,lo,-.14),F.p(L,hi,-.14),F.p(0,hi,-.14)])
    for y in np.arange(lo+.75,hi,.75):F.box('ph-metal',(L/2,y,-.15),(L,.018,.025))
    for u in np.arange(2,L,3.2):F.box('ph-joint',(u,(lo+hi)/2,-.15),(.012,hi-lo,.025))
   elif glass:
    for u in np.linspace(0,L,max(2,math.ceil(L/1.65)+1)):
     F.box('ph-metal',(u,(lo+hi)/2,-.03),(.055,hi-lo,.12))
    for y in np.arange(lo+2.2,hi,.0+2.2):F.box('ph-metal',(L/2,y,-.05),(L,.065,.14))
   else:
    for y in np.arange(lo+.75,hi,.75):F.box('ph-joint',(L/2,y,-.04),(L,.012,.02))
   for y in [lo,hi]:F.box('ph-silver',(L/2,y,-.08),(L,.18,.24))

def guard(B,p,y,omit=None):
 for poly in parts(p):
  pts=list(poly.exterior.coords)
  for a,b in zip(pts,pts[1:]):
   if omit and omit(Point((a[0]+b[0])/2,(a[1]+b[1])/2)):continue
   F,L,_,_=facade_frame(B,a,b,p,0)
   F.box('ph-glass',(L/2,y+.58,0),(L,1.05,.05),True)
   F.box('ph-silver',(L/2,y+1.13,0),(L,.055,.09))
   for u in np.linspace(0,L,max(2,math.ceil(L/1.8)+1)):F.box('ph-metal',(u,y+.55,0),(.035,1.1,.07))

def exterior(B):
 B.property=KEY+'-exterior';B.detail=0;B.source='podium/main'
 p=footprint(MAIN).simplify(.28,preserve_topology=True)
 wing=footprint(WING)
 # Three continuous commercial floor plates; the stepped east edge follows the
 # mapped retail bays. L2 is tied to the existing 6.24 m pedestrian bridge datum.
 base=.24;l2=6.035;l3=12.45;l4=18.65
 for lo,hi in [(base,l2),(l2,l3),(l3,l4)]:
  facade(B,p,lo+.16,hi-.36,main=True)
  slab(B,p,hi)
 # West ARTE wing is distinct from the south roof canopy (different mapped owner).
 B.source='podium/arte-wing';facade(B,wing,base,14.8,False);slab(B,wing,14.8,'forum-flat-roof')
 for a,b in zip(list(wing.exterior.coords),list(wing.exterior.coords)[1:]):
  F,L,nx,nz=facade_frame(B,a,b,wing,.08)
  if nz<-.4:
   F.box('ph-black',(L/2,8,-.04),(min(L-1,24),7,.12));F.text('ARTE MUSEUM',(L/2,8,-.15),1.4,'letter')
 # The upper restaurant occupies only the rounded north end, with a genuine
 # exposed wrap terrace. Stepped ellipse is fitted to mapped rounded corner.
 B.source='podium/ocean-prime'
 cap=scale(Point(-80,798).buffer(1,resolution=48),25,17).intersection(p.buffer(-1))
 inner=cap.buffer(-5.0)
 facade(B,inner,l4+.15,21.8)
 facade(B,inner,21.8,23.5,False)
 slab(B,inner,23.5)
 terrace=cap.difference(inner)
 B.planar('ph-paving',terrace,l4+.025,True);guard(B,cap,l4)
 # Upper curved LED fascia, not a generic solid top storey. Original graphic.
 screen=inner.buffer(-1.0)
 B.shell(screen,24,31,'ph-led-blue',roof=False,solid=True)
 for poly in parts(screen):
  ps=list(poly.exterior.coords)
  for i,(a,b) in enumerate(zip(ps,ps[1:])):
   F,L,nx,nz=facade_frame(B,a,b,screen,.065)
   if i%3==0:F.box('ph-led-line',(L/2,25.5+(i%5)*.65,-.075),(L,.16,.035))
 slab(B,screen,31.1,'forum-flat-roof')
 F=Frame(B,-79,783.6,0,y=0);F.text('OCEAN PRIME',(0,22.65,-.08),.8,'letter')
 # Large corner promotional face set into the silver angled frame. Original
 # typography avoids reusing licensed publicity photography.
 F=Frame(B,-54.5,800,-1.8,y=0)
 F.box('ph-metal',(0,10.75,-.25),(13,13.9,.24))
 F.box('ph-black',(0,10.75,-.40),(11.8,12.8,.10))
 F.text("JASON ALDEAN'S",(0,14.3,-.5),1.0,'letter')
 F.text('KITCHEN + BAR',(0,12.6,-.5),.65,'letter')
 F.text('LAS VEGAS',(0,7.4,-.5),.65,'letter')
 for dx in [-6.5,6.5]:
  F.b.face('ph-silver',[F.p(dx-.4,3.8,-.52),F.p(dx+.4,3.8,-.52),F.p(dx+.7,18.6,-.52),F.p(dx-.4,18.6,-.52)])
 F=Frame(B,-79,786,0,y=0)
 F.text('63 CITYCENTER',(0,28.4,-.15),1.3,'letter')
 F.text('LAS VEGAS',(0,26.7,-.15),.75,'letter')
 # Retail tenant signs follow the shallow east-facing bays rather than crossing
 # the perimeter. Text is sized to clear the structural mullions.
 for x,z,yaw,name,width in [(-56,797,-1.2,"JASON ALDEAN'S",16),(-62,812,-1.25,'ARIAT',10),(-66,825,-1.2,'WELCOME LAS VEGAS',10)]:
  F=Frame(B,x,z,yaw,y=0);F.box('ph-black',(0,10,-.1),(width,1.65,.18));F.text(name,(0,10,-.23),min(.75,width/(len(name)*.65)),'letter')
 # Recessed ground-floor storefronts, glazed doors with tangible reveals.
 B.source='podium/retail'
 for poly in parts(p):
  cs=list(poly.exterior.coords)
  for a,b in zip(cs,cs[1:]):
   F,L,nx,nz=facade_frame(B,a,b,p,.1)
   if nx<.45 or L<3:continue
   F.box('ph-metal',(L/2,3,-.1),(min(2.2,L-.4),4.9,.24))
   F.box('ph-glass',(L/2,3,-.25),(min(1.95,L-.6),4.65,.05))
   for dx in [-.12,.12]:F.tube('ph-silver',(L/2+dx,1.5,-.32),(L/2+dx,2.3,-.32),.025,6)
 # Bridge promenade: share the surveyed deck elevation and do not duplicate its
 # existing deck triangles. Those surveyed bridge spans remain separate owners.
 B.source='podium/bridge-promenade'
 bridge=[]
 for g in json.loads(Path('build/geographic-strip/bridge-only-meshes.json').read_text()):
  if g['material']!='bridge-deck':continue
  verts=g['vertices']
  for face in g['faces']:
   vs=[verts[i] for i in face]
   if all(abs(v[1]-l2)<.005 for v in vs):
    q=Polygon([(v[0],v[2]) for v in vs])
    if q.is_valid and q.area>.001 and q.intersects(box(-130,770,-30,865)):bridge.append(q)
 bridges=unary_union(bridge)
 outer=p.buffer(7.0,resolution=24).intersection(box(-128,772,-37,861)).union(box(-58,848,-47,855))
 promenade=outer.difference(p).difference(bridges.buffer(.015).intersection(box(-300,700,0,819))).intersection(box(-110,770,-30,865))
 def deck_height(z):return l2+.145*max(0,min(1,(z-819)/5))
 for poly in parts(promenade):
  # Split at grade breakpoints so no single triangle spans a change in slope.
  for z0,z1 in [(700,819),(819,824),(824,900)]:
   q=poly.intersection(box(-300,z0,0,z1))
   for region in parts(q):
    for tri in triangles(region):
     pts=list(tri.exterior.coords)[:-1]
     B.upface('ph-paving',[(x,deck_height(z),z) for x,z in pts],True)
     B.face('ph-silver',[(x,deck_height(z)-.28,z) for x,z in pts[::-1]])
  ps=list(poly.exterior.coords)
  for a,b in zip(ps,ps[1:]):
   B.face('ph-silver',[(a[0],deck_height(a[1]),a[1]),(b[0],deck_height(b[1]),b[1]),(b[0],deck_height(b[1])-.28,b[1]),(a[0],deck_height(a[1])-.28,a[1])],True)
 guard(B,outer,l2,lambda pt: p.buffer(.1).contains(pt) or bridges.buffer(1.2).contains(pt) or pt.x<-110)
 for x,z in [(-45,800),(-51,831)]:
  kiosk=scale(Point(x,z).buffer(1,resolution=24),2,3.5)
  if promenade.contains(kiosk):
   facade(B,kiosk,l2,l2+2.8);slab(B,kiosk,l2+3.05)
 # Oval street-level Museum of Illusions pavilion seen in the owner photo.
 # The existing bridge/plaza owns shared top faces; add only uncovered roof area.
 B.source='podium/museum-pavilion'
 pavilion=scale(Point(-48,806).buffer(1,resolution=32),3.6,5.0)
 facade(B,pavilion,base,l2-.45)
 B.shell(pavilion,l2-.45,l2,'ph-silver',roof=False,solid=False)
 B.planar('ph-paving',pavilion.difference(promenade).difference(bridges),l2,True)
 B.planar('ph-paving',pavilion,base,True)
 guard(B,pavilion,l2,lambda pt: bridges.buffer(.45).contains(pt) or promenade.buffer(.45).contains(pt))
 F=Frame(B,-44.28,806,-math.pi/2,y=0)
 F.text('MUSEUM OF',(0,4.8,-.05),.38,'letter')
 F.text('ILLUSIONS',(0,4.25,-.05),.48,'letter')
 for u in [-1.4,0,1.4]:F.box('ph-metal',(u,2.3,-.07),(.075,3.8,.1))
 # Roof service equipment and safe upper dining furniture, kept in near detail.
 B.detail=1;B.source='roof-service'
 exposed=p.difference(cap.buffer(.4))
 for x in np.arange(-111,-70,9):
  for z in np.arange(815,848,10):
   if not exposed.contains(box(x-2,z-1.8,x+2,z+1.8)):continue
   B.box('ph-metal',(x,l4+.6,z),(3.6,1.2,2.8));B.box('ph-black',(x,l4+1.22,z),(3.2,.05,2.4))
 B.source='ocean-prime-terrace'
 for angle in np.linspace(math.pi,math.tau,12):
  x=-80+21*math.cos(angle);z=798+13*math.sin(angle)
  if not terrace.buffer(-.5).contains(Point(x,z)):continue
  F=Frame(B,x,z,0,y=l4+.03)
  F.lathe('ph-metal',0,0,[(0,.36),(.72,.06),(.77,.7)],16)
  for dx in [-.95,.95]:
   F.box('ph-metal',(dx,.4,0),(.5,.08,.55));F.box('ph-metal',(dx,.7,.23),(.5,.6,.06))
  F.tube('ph-silver',(0,0,0),(0,2.5,0),.035,8)
  F.lathe('blue',0,0,[(2.15,1.2),(2.6,.04)],12)
 B.detail=0
 return dict(key=KEY,name='63 CityCenter exterior',center=[-110,0,813],bounds=[-167,778,-48,856],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
