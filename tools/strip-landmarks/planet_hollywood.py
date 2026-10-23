"""Planet Hollywood / Miracle Mile exterior, mapped metres.
Reference: Google Earth 2022 imagery, Caesars exterior photograph, MMS Jan 2026
leasing diagram. Bay/elevation estimates are explicit in the block record.
No interiors, guest cores, roads or gameplay objects are generated here.
"""
from common import *
from forum_shops import facade_frame,arch_panel
KEY='planetHollywood'

def panel(F,x,y,w,h,mat='ph-glass',depth=-.14):
 F.box(mat,(x,y,depth),(w,h,.10))
 for xx in [x-w/2,x+w/2]:F.box('ph-metal',(xx,y,depth-.10),(.085,h+.10,.18))
 for yy in [y-h/2,y+h/2]:F.box('ph-metal',(x,yy,depth-.10),(w+.10,.085,.18))

def screen(F,x,y,w,h,label,mat='ph-led-blue'):
 F.box('ph-black',(x,y,-.42),(w+.40,h+.40,.48))
 F.box(mat,(x,y,-.69),(w,h,.05))
 # Original graphics: lit typography, dark framing; no photographs baked in.
 F.text(label,(x,y-.3,-.76),min(h*.19,w/max(6,len(label))*.95),'ph-letter')
 for yy in np.arange(y-h/2+.12,y+h/2,.48):F.box('ph-led-line',(x,yy,-.727),(w,.018,.012))

def entrance_lightbox(F,w,y=8.8):
 # 2024 designer photographs: a patterned warm lightbox below each display.
 # The motif is authored geometry; no advertising photograph is reused.
 F.box('ph-black',(0,y,-.49),(w,2.8,.30))
 F.box('ph-lightbox-paint',(0,y,-.66),(w-.14,2.6,.04))
 for x in np.arange(-w/2+.6,w/2-.4,1.15):
  for yy in [y-.65,y+.65]:
   pts=[(x,yy+.57),(x+.50,yy),(x,yy-.57),(x-.50,yy),(x,yy+.57)]
   for a,b in zip(pts,pts[1:]):F.tube('ph-metal',(a[0],a[1],-.70),(b[0],b[1],-.70),.025,5)
 F.box('ph-black',(0,y,-.77),(w*.76,1.25,.04))
 F.text('MIRACLE MILE SHOPS',(0,y-.24,-.81),min(.70,w/25),'ph-letter')

def facade_disc(B,F,x,y):
 # Former world-space spheres faced Z even on the west facade, showing only
 # their edges. Build a shallow convex disc in the facade's own frame.
 n=12;r=.38
 center=F.p(x,y,-.36)
 ring=[F.p(x+r*math.cos(j*math.tau/n),y+r*math.sin(j*math.tau/n),-.19) for j in range(n)]
 for j in range(n):B.face('ph-disc',[center,ring[(j+1)%n],ring[j]])

def shop(F,x,w,label,base=.3,height=5.0):
 panel(F,x,base+height/2,w,height)
 for xx in np.arange(x-w/2+.07,x+w/2,2.1):F.box('ph-metal',(xx,base+height/2,-.27),(.085,height,.19))
 F.box('ph-metal',(x,base+2.5,-.28),(w,.10,.19))
 for xx in [x-.65,x+.65]:
  F.box('ph-metal',(xx,base+1.3,-.29),(.04,2.6,.08))
  F.tube('ph-silver',(xx+(.43 if xx<x else -.43),base+1.0,-.40),(xx+(.43 if xx<x else -.43),base+1.75,-.40),.025,8)
 F.box('ph-black',(x,base+height+.58,-.19),(w,1.0,.25))
 F.text(label,(x,base+height+.3,-.36),min(.62,w/max(6,len(label))*.88),'ph-letter')
 F.box('ph-silver',(x,base+height+1.22,-1.1),(w+.3,.18,2.4))

def outdoor_table(F,x,z):
 F.lathe('ph-black',x,z,[(0,.34),(.06,.34),(.07,.04),(.72,.04)],10)
 F.lathe('ph-silver',x,z,[(.72,.65),(.78,.65)],24)
 for dx,dz in [(-.9,0),(.9,0),(0,.9),(0,-.9)]:
  F.box('ph-black',(x+dx,.48,z+dz),(.42,.09,.42))
  for sx in [-.17,.17]:F.box('ph-metal',(x+dx+sx,.22,z+dz),(.035,.44,.32))
  F.box('ph-black',(x+dx,.76,z+dz+.19),(.43,.58,.055))

def exterior(B):
 B.property=KEY+'-exterior';B.detail=0;p=footprint('relation/1606512')
 # West scallops are display housings, not solid 20 m walls all the way down.
 # Their inherited footprint and the old mall roof stay put. This owner supplies
 # glazing, soffits and signage after selective removal of the west render faces.
 ps=list(p.exterior.coords)
 for i,(a,b) in enumerate(zip(ps,ps[1:])):
  L=math.dist(a,b);mx,mz=(a[0]+b[0])/2,(a[1]+b[1])/2
  if L<.12 or mx>59 or not 535<mz<775:continue
  F,L,nx,nz=facade_frame(B,a,b,p,0)
  if nx>-.25:continue
  B.source='mall-west-'+str(int(mz//40))
  # Different architectural zones follow the measured scalloped perimeter.
  north=mz<576;south=mz>725;entry=628<mz<670
  h=20
  F.box('ph-stone',(L/2,.65,.24),(L,1.0,.48))
  if not 646<mz<664:panel(F,L/2,3.8,L-.025,5.15)
  if north or south:
   panel(F,L/2,10.5,L-.04,5.4)
   for y in [6.9,13.5]:F.box('ph-silver',(L/2,y,-.10),(L,.62,.48))
  else:
   F.box('ph-silver',(L/2,12.5,.16),(L,11,.40))
   # Curved metallic discs articulate the original display skin. Limit these
   # close-range details to small batches; no collider for a decorative disc.
   B.detail=1
   for xx in np.arange(.52,L,.98):
    for yy in np.arange(8.2,17.8,1.04):
     facade_disc(B,F,xx,yy)
   B.detail=0
  for y in [6.6,18.3,19.8]:F.box('ph-silver',(L/2,y,-.22),(L,.20,.62))
  # A continuous horizontal soffit closes the bottom of the upper volume.
  F.box('ph-black',(L/2,7.1,.10),(L,.20,1.0))
  F.box('ph-stone',(L/2,19.5,.14),(L,1,.40))
 # North entrance composition: Cabo Wabo two floors, terrace, tall glazing,
 # red recessed entry and silver M / Sephora tower. Dimensions photo-estimated.
 B.source='north-entrance';F=Frame(B,48.95,555,math.pi/2,y=.24)
 # At yaw +pi/2 local -Z is west; local +X points north.
 F.box('ph-silver',(0,10,.05),(29,20,.20))
 for x,w,name in [(8,12,'CABO WABO'),(-6.7,14,'BLUE MARTINI')]:
  shop(F,x,w,name,base=2.7,height=5.0)
  panel(F,x,12.3,w-.4,5.6)
  for xx in np.arange(x-w/2+.4,x+w/2-.1,2.05):F.box('ph-metal',(xx,12.3,-.28),(.11,5.6,.19))
  F.box('ph-metal',(x,12.0,-.29),(w-.4,.1,.19))
  F.text('CANTINA' if x>0 else 'BLUE MARTINI',(x,15.8,-.39),.57,'ph-letter')
 screen(F,0,23.5,29,12,'MIRACLE MILE SHOPS')
 # Patio terrace and a broad stair from the actual sidewalk setback.
 terrace=Frame(B,43,551,math.pi/2,y=.24)
 terrace.box('ph-stone',(0,1.15,0),(22,2.3,8),True)
 terrace.box('ph-paving',(0,2.35,0),(22,.10,8),True)
 T=Frame(B,43,551,math.pi/2,y=2.64)
 T.rail((-10.8,-3.9),(10.8,-3.9),glass=True)
 T.rail((-10.8,-3.9),(-10.8,3.9),glass=True)
 B.detail=1
 for x in [-7,-2,3,8]:
  outdoor_table(T,x,0)
  T.tube('ph-metal',(x,0,0),(x,3.1,0),.045)
  # Fabric parasols have an underside and a supported mast.
  for j in range(8):
   a=j*math.tau/8;b=(j+1)*math.tau/8
   B.face('ph-red',[T.p(x,3.2,0),T.p(x+2*math.cos(a),2.6,2*math.sin(a)),T.p(x+2*math.cos(b),2.6,2*math.sin(b))])
 B.detail=0
 S=Frame(B,37.8,572,math.pi/2,y=.24);S.stairs(0,-4,9,2.4,9)
 # Recessed mall entry north of Sephora; access remains open to the retained hall.
 F=Frame(B,52,585,math.pi/2,y=.24)
 F.box('ph-black',(0,15,1.0),(20,25,1.8))
 shop(F,0,13,'MIRACLE MILE SHOPS',base=2.4,height=4.8)
 display=Frame(B,35,585,math.pi/2,y=.24)
 entrance_lightbox(display,20,10)
 screen(display,0,21,20,18,'MIRACLE MILE')
 S=Frame(B,40,585,math.pi/2,y=.24);S.stairs(0,-2,7,2.4,11)
 # Sephora's black/white stripes, separated silver panel joints above.
 F=Frame(B,41.5,603,math.pi/2,y=.24)
 F.box('ph-silver',(0,5.25,0),(10,10.5,1))
 for yy in np.arange(1.1,9.1,.76):F.box('ph-white' if int(yy/.76)%2 else 'ph-black',(0,yy,-.57),(10,.74,.15))
 panel(F,0,4.5,7.4,7.5,depth=-.70)
 F.text('SEPHORA',(0,9.1,-.72),.65,'ph-letter')
 # Main casino approach: retain the already working arrival hall at x~56–94.
 # Screen and canopy flank, rather than obstruct, the 16 m entry axis.
 B.source='casino-entry';F=Frame(B,38.6,655.15,math.pi/2,y=.24)
 # Single rounded vertical marquee above the entrance, as photographed.
 B.source='ph-hero-screen'
 cx,cz=43.5,642.5
 for j in range(48):
  a=math.pi/2+j*math.pi/48;b=a+math.pi/48
  pts=[(cx+8.0*math.cos(a),8.5,cz+8.0*math.sin(a)),(cx+8.0*math.cos(b),8.5,cz+8.0*math.sin(b)),(cx+8.0*math.cos(b),30,cz+8.0*math.sin(b)),(cx+8.0*math.cos(a),30,cz+8.0*math.sin(a))]
  B.face('ph-led-cylinder',pts)
  for yy in [8.2,30.3]:B.tube('ph-black',(cx+8.15*math.cos(a),yy,cz+8.15*math.sin(a)),(cx+8.15*math.cos(b),yy,cz+8.15*math.sin(b)),.19,8)
 L=Frame(B,cx-8.08,cz,math.pi/2,y=0);L.text('ph',(0,18.5,-.08),5.2,'ph-letter')
 B.source='casino-entry'
 F.box('ph-metal',(0,7.5,4.6),(19,.6,12))
 for x in [-8.5,8.5]:F.box('ph-silver',(x,3.6,-.3),(.55,7.2,.65),True)
 F.text('planet hollywood',(0,7.9,-1.65),.9,'ph-letter')
 B.detail=1
 for x in np.arange(-8.6,8.7,.55):F.box('ph-metal',(x,7.1,4.4),(.035,.14,11.5))
 B.detail=0
 # Southern entrance and Harmon frontage get their own retail rhythm.
 B.source='south-entrance';F=Frame(B,49.2,718,math.pi/2,y=.24)
 shop(F,0,18,'MIRACLE MILE SHOPS',base=.3,height=6)
 display=Frame(B,31,718,math.pi/2,y=.24)
 entrance_lightbox(display,24,8.5)
 screen(display,0,20.4,27,17,'MIRACLE MILE SHOPS')
 B.source='harmon-frontage'
 for x,w,name in [(126,25,'PAMPAS'),(158,31,'GEN KOREAN BBQ'),(192,29,'NACHO DADDY'),(225,24,'MIRACLE MILE'),(248,20,'BUFFALO WILD WINGS')]:
  F=Frame(B,x,858.65,math.pi,y=.24)
  shop(F,0,w,name)
  for yy in [8,11,14,17,19.5]:F.box('ph-silver',(0,yy,-.35),(w,.12,.35))
  for xx in np.arange(-w/2,w/2,3):F.box('ph-joint',(xx,13,-.20),(.03,12,.05))
 # The service facades are articulated with expansion joints, screened plant,
 # loading shutters and roof parapets; no invented guest windows on the mall.
 B.source='mall-service';B.detail=1
 for a,b in zip(ps,ps[1:]):
  L=math.dist(a,b);mx,mz=(a[0]+b[0])/2,(a[1]+b[1])/2
  if L<10 or mx<80:continue
  F,L,nx,nz=facade_frame(B,a,b,p,.03)
  F.box('ph-stone',(L/2,19.95,-.08),(L,.36,.5))
  for xx in np.arange(2,L,8):F.box('ph-joint',(xx,10,-.05),(.035,19,.07))
  if mx>390:
   for xx in np.arange(7,L-4,18):
    panel(F,xx,2.2,5.5,4,'ph-metal')
    for yy in np.arange(.4,4,.22):F.box('ph-joint',(xx,yy,-.31),(5.4,.022,.028))
 B.detail=0
 # PH Live theatre: a faceted raised roof above its mapped auditorium.
 B.source='theatre-roof';theatre=footprint('way/115670770');c=theatre.centroid
 inner=scale(theatre,.83,.83,origin=(c.x,c.y))
 B.shell(theatre,20.02,25,'ph-stone',roof=False,solid=False)
 outer=list(theatre.exterior.coords);inside=list(inner.exterior.coords)
 for j in range(len(outer)-1):
  a,b=outer[j],outer[j+1];aa,bb=inside[j],inside[j+1]
  B.upface('ph-roof',[(a[0],25,a[1]),(b[0],25,b[1]),(bb[0],29,bb[1]),(aa[0],29,aa[1])])
  B.tube('ph-metal',(a[0],25.08,a[1]),(aa[0],29.08,aa[1]),.08,6)
 B.planar('ph-roof',inner,29)
 # Parking structure: continuous dark ventilation slots framed by floor slabs.
 B.source='garage-facades';garage=footprint('way/115670777')
 points=list(garage.exterior.coords)
 for a,b in zip(points,points[1:]):
  if math.dist(a,b)<6:continue
  F,L,nx,nz=facade_frame(B,a,b,garage,.04)
  for yy in np.arange(3.1,29,2.75):
   F.box('ph-black',(L/2,yy,-.10),(L-.2,1.65,.08))
   F.box('ph-stone',(L/2,yy-.93,-.21),(L,.23,.42))
  for xx in np.arange(.5,L,7.5):F.box('ph-stone',(xx,15,-.24),(.42,30,.55))
  F.box('ph-stone',(L/2,30.24,-.14),(L,.48,.7))
 # Roof plant constrained to the mapped mall roof, outside the actual hotel,
 # theatre and pool terraces. No geometry through existing public interiors.
 roof=p.difference(unary_union([footprint(i).buffer(8) for i in ['way/134921373','way/134921371','way/134921379','way/115670770']])).intersection(box(195,535,399,810))
 B.source='mall-roof';B.detail=1
 for x in np.arange(202,390,23):
  for z in np.arange(548,780,28):
   if not roof.contains(box(x-4,z-3,x+4,z+3)):continue
   B.box('ph-metal',(x,21,z),(6,1.8,3.4));B.box('ph-black',(x,21.94,z),(5.6,.08,3))
   for dx in [-1.8,1.8]:B.lathe('ph-metal',(x+dx,z),[(21.95,1),(22.03,1)],20)
 B.detail=0
 return dict(key=KEY,name='Planet Hollywood / Miracle Mile exterior',center=[190,0,675],bounds=list(p.bounds),structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})

def towers(B):
 # Retain the existing guest-tower envelope and physical floor datum. The mapped
 # survey's 122 m tag conflicts with this playable 100 m tower: that discrepancy
 # is recorded, not silently resolved by stretching existing interiors.
 from mapping import point
 def plan(x,z,w,d,r,yaw):
  out=[]
  for cx,cz,a in [(w/2-r,d/2-r,0),(-w/2+r,d/2-r,math.pi/2),(-w/2+r,-d/2+r,math.pi),(w/2-r,-d/2+r,3*math.pi/2)]:
   for j in range(7):
    u,v=cx+r*math.cos(a+j*math.pi/12),cz+r*math.sin(a+j*math.pi/12)
    q=point((x+math.cos(yaw)*u+math.sin(yaw)*v,0,z-math.sin(yaw)*u+math.cos(yaw)*v),'planet-hollywood');out.append((q[0],q[2]))
  return Polygon(out)
 specs=[('north',160,199,17,48,98,4,-.20),('south',159,242,17,46,98,4,.24),('hinge',163,220,20,15,99,3,0),('suite-north',139,201,42,13,60,5,0),('suite-south',139,250,40,13,63,5,0)]
 shapes=[(n,plan(x,z,w,d,r,a),h) for n,x,z,w,d,h,r,a in specs]
 for name,p,h in shapes:
  B.source='guest-ph-'+name;B.detail=0
  B.shell(p,12.42,h,'ph-stucco',roof=False,solid=False)
  B.planar('ph-roof',p,h)
  for poly in parts(p):
   coords=list(poly.exterior.coords)
   for a,b in zip(coords,coords[1:]):
    L=math.dist(a,b)
    if L<.15:continue
    F,L,nx,nz=facade_frame(B,a,b,p,.025)
    mid=Point((a[0]+b[0])/2+nx*.5,(a[1]+b[1])/2+nz*.5)
    # A projecting wing covers only part of a long facade edge. Do not raise
    # the entire edge's window start from one midpoint overlap sample.
    floor=12.5
    crown=h-11.5 if h>90 else h-6.5
    step=L/max(1,round(L/2.9));cols=round(L/step)
    # Continuous recessed blue-charcoal glazing with quiet opaque spandrels;
    # vertical limestone ribs dominate, as in the official elevation photo.
    for j in range(cols):
     xx=(j+.5)*step;ww=step*.43
     if crown>floor:
      F.box('ph-window',(xx,(floor+crown)/2,-.07),(ww,crown-floor,.08))
      for yy in np.arange(floor+.4,crown,2.45):
       F.box('ph-spandrel',(xx,yy,-.13),(ww,.48,.045))
       F.box('ph-mullion',(xx,yy+.29,-.17),(ww,.035,.035))
      F.box('ph-mullion',(xx,(floor+crown)/2,-.14),(.035,crown-floor,.03))
     # True arch silhouette rather than a rectangular black crown panel.
     bottom=max(floor,crown+1.0);height=h-bottom-1.4
     if height>1:
      w=min(ww*1.12,height*.5);r=w/2;spring=bottom+height-r
      pts=[F.p(xx-r,bottom,-.13),F.p(xx+r,bottom,-.13),F.p(xx+r,spring,-.13)]
      pts.extend(F.p(xx+r*math.cos(t),spring+r*math.sin(t),-.13) for t in np.linspace(0,math.pi,15)[1:])
      B.face('ph-window',pts[::-1])
     for side in [-1,1]:F.box('ph-stucco',(xx+side*step*.36,(floor+h)/2,-.12),(.13,h-floor,.30))
    for yy,th,depth in [(crown,.5,.55),(h-.55,.26,.6),(h+.25,.32,.95),(h+.7,.20,1.15)]:
     if yy<floor:continue
     F.box('ph-stone',(L/2,yy,-depth*.3),(L+.05,th,depth))
    if L>12:
     for xx in [1,L-1]:F.box('ph-stone',(xx,(floor+h)/2,-.18),(.36,h-floor,.5))
  # Discreet roof plant, set back behind parapets.
  B.detail=1
  c=p.centroid
  if p.contains(c.buffer(3)):
   B.box('ph-metal',(c.x,h+.75,c.y),(3.5,1.5,2.8))
  B.detail=0
 # Roof letters follow the existing two folded axes.
 for text,old,yaw in [('planet',(145.9,99.7,197),math.pi/2-.20),('hollywood',(145.2,99.7,241),math.pi/2+.24)]:
  q=point(old,'planet-hollywood');F=Frame(B,q[0],q[2],yaw,y=0);B.source='guest-ph-lettering';F.text(text,(0,q[1]+.7,-.2),3.4,'ph-letter')

def harmon_corner(B):
 """June 2026 owner photograph: silver bands, recessed restaurant and terrace.
 LED height is owner's 60 ft; floor elevations remain photo estimates.
 Keep the unrelated Planet Hollywood geometry and mapped structural owner intact.
 """
 B.property=KEY+'-exterior';B.source='harmon-corner';B.detail=0
 p=footprint('way/1255028419');ps=list(p.exterior.coords)
 for a,b in zip(ps,ps[1:]):
  L=math.dist(a,b)
  if L<.3:continue
  F,L,nx,nz=facade_frame(B,a,b,p,.10)
  front=nx<-.18 or nz>.6
  if front:
   # Ground and bridge-level glazing; broad opaque silver panel bands above.
   for y,h in [(1.9,3.5),(6.1,2.65),(10.55,3.1)]:
    panel(F,L/2,y,L-.03,h)
    for xx in np.arange(.3,L,1.5):F.box('ph-silver',(xx,y,-.28),(.07,h,.15))
   for yy,h in [(.18,.3),(4.2,1.0),(8.0,1.0),(12.65,1.25)]:
    F.box('ph-silver',(L/2,yy,-.40),(L,h,.48))
    # Visible panel joints, without coplanar overlay surfaces.
    for xx in np.arange(1.5,L,1.5):F.box('ph-joint',(xx,yy,-.65),(.012,h-.04,.012))
   F.box('ph-black',(L/2,22.2,.15),(L,18.7,.38))
   F.box('ph-led-purple',(L/2,22.2,-.08),(L,18.288,.06))
   for yy in [13.03,31.37]:F.box('ph-metal',(L/2,yy,-.18),(L,.16,.36))
   if L>15:
    F.text('HARMON CORNER',(L/2,22,-.16),min(2.3,L/14),'ph-letter')
    F.text('LAS VEGAS',(L/2,18.4,-.16),1.1,'ph-letter')
    label='SUGAR FACTORY' if nz>.6 else 'RAINFOREST CAFE'
    F.text(label,(L/2,12.3,-.69),min(.82,L/19),'ph-letter')
   if L>6:
    F.box('ph-paving',(L/2,8.55,-1.5),(L,.2,3.2),True)
    # Local guard base at terrace elevation; previous poles ran to the ground.
    q=F.p(0,8.65,0);T=Frame(B,q[0],q[2],F.yaw,y=q[1])
    T.rail((.12,-3),(L-.12,-3),y=1.1,glass=True)
    for xx in np.arange(2,L-1,4):
     q=F.p(xx,8.65,-1.5);T=Frame(B,q[0],q[2],F.yaw,y=q[1])
     B.detail=1;outdoor_table(T,0,0);B.detail=0
   # Storefront doors and projecting canopy at pedestrian scale.
   if L>9:
    for xx in [L*.35,L*.7]:
     for dx in [-.8,0,.8]:F.box('ph-silver',(xx+dx,1.6,-.32),(.06,3.0,.12))
     F.box('ph-metal',(xx,3.15,-.32),(1.65,.10,.12))
     for dx in [-.12,.12]:F.tube('ph-silver',(xx+dx,.9,-.48),(xx+dx,1.6,-.48),.025,8)
  else:
   F.box('ph-silver',(L/2,8,-.1),(L,16,.2))
   for yy in np.arange(1,16,1.5):F.box('ph-joint',(L/2,yy,-.21),(L,.012,.012))
   for xx in np.arange(1.5,L,1.5):F.box('ph-joint',(xx,8,-.21),(.012,15.9,.012))
 B.source='harmon-corner-roof';B.planar('ph-roof',p.buffer(-.3),16.1)
 for x,z in [(75,791),(90,791),(85,815)]:
  B.box('ph-metal',(x,17,z),(6,1.8,3));B.box('ph-black',(x,17.94,z),(5.6,.08,2.7))


def pool_furniture(B):
 from mapping import point
 B.property=KEY+'-exterior';B.source='pool-deck';B.detail=1
 # Existing pool/deck datum is retained. Furniture around both pools is authored
 # in metres after the legacy plan transform, not stretched with the building.
 for oldz in [202,246]:
  for oldx in [80,88,96,104,112]:
   for dz in [-12,12]:
    q=point((oldx,12.82,oldz+dz),'planet-hollywood');F=Frame(B,q[0],q[2],0 if dz<0 else math.pi,y=q[1])
    F.box('ph-awning',(0,.42,0),(.68,.13,1.95))
    F.box('ph-metal',(0,.3,0),(.72,.08,2))
    for xx in [-.28,.28]:F.box('ph-metal',(xx,.14,.1),(.035,.28,1.65))
    # Sloped chaise back, expressed as a closed wedge above its frame.
    B.face('ph-awning',[F.p(-.34,.49,-.3),F.p(.34,.49,-.3),F.p(.34,.95,-.94),F.p(-.34,.95,-.94)])
  for oldx in [76,119]:
   q=point((oldx,12.82,oldz),'planet-hollywood');F=Frame(B,q[0],q[2],0,y=q[1])
   F.box('ph-awning',(0,2.7,0),(4.5,.16,4))
   for xx in [-2.1,2.1]:
    for zz in [-1.8,1.8]:F.box('ph-white',(xx,1.35,zz),(.12,2.7,.12))
   F.box('ph-awning',(0,.55,.5),(3.7,.3,2.1))
 B.detail=0
