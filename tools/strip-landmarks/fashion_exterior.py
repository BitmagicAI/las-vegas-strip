"""Fashion Show exterior: mapped perimeter, official anchor plan, Earth2022 roofs.
Elevations are photographic estimates. Existing galleria/portal remains authoritative.
"""
from common import *
from forum_shops import facade_frame
from sahara_retail import equipment

def glass(F,u,lo,hi,w):
 F.box('fs-glass',(u,(lo+hi)/2,-.23),(w,hi-lo,.10))
 for x in np.arange(u-w/2,u+w/2+.01,1.5):F.box('fs-metal',(x,(lo+hi)/2,-.32),(.065,hi-lo,.10))
 for y in np.arange(lo,hi+.1,2.8):F.box('fs-metal',(u,y,-.34),(w,.065,.1))

def exterior(B,p,F,glazed):
 interior=(F.poly([(-21.9,.3),(21.9,.3),(21.9,108),(-21.9,108)]),16.4)
 # Each anchor has its own height/finish; clipped to the mapped mall footprint.
 specs=[('DILLARD’S',box(-220,-1420,-66,-1236),21,'fs-taupe'),('NORDSTROM',box(-45,-1420,44,-1305),23,'fs-sand'),('MACY’S MEN',box(65,-1400,168,-1317),17.5,'fs-white'),('',box(219,-1400,287,-1315),17,'fs-white'),('DICK’S',box(-76,-1236,-10,-1170),12.5,'fs-sand'),('SOUTH RETAIL',box(7,-1216,101,-1130),16,'fs-stone'),('MACY’S',box(103,-1228,230,-1130),18,'fs-white'),('NEIMAN MARCUS',box(219,-1162,319,-1080),18.5,'fs-stone')]
 areas=[];used=Polygon()
 for name,mask,h,mat in specs:
  q=p.intersection(mask).difference(used);used=unary_union([used,q]);areas.append((name,q,h,mat))
 areas.append(('GALLERIA',p.difference(used),16.5,'fs-white'))
 for name,q,h,mat in areas:
  B.source='mall/'+name
  B.shell(q,.15,h,mat,[glazed],roof=False,interior=interior)
  B.planar('fs-flat-roof',q,h,True)
  # Parapets and joints only on visible exterior boundary, not clipping seams.
  for pp in parts(q):
   cs=list(pp.exterior.coords)
   for a,b in zip(cs,cs[1:]):
    line=LineString([a,b]);mid=line.interpolate(.5,normalized=True)
    if p.boundary.distance(mid)>.15:continue
    J,L,nx,nz=facade_frame(B,a,b,p,.02)
    if L<.4:continue
    if Point(F.x,F.z).distance(line)<18:continue # existing open entry assembly
    east=mid.x>320 and nx>.25 and -1325<mid.y<-1160
    J.box('fs-stone',(L/2,h+.3,-.02),(L,.6,.3))
    J.box('fs-joint',(L/2,.65,-.10),(L,.12,.06))
    if east:
     glass(J,L/2,.8,h-.4,max(.2,L-.2))
     for y in [6.8,12.4]:J.box('fs-metal',(L/2,y,-.42),(L,.45,.8))
    else:
     for y in np.arange(2.4,h,2.4):J.box('fs-joint',(L/2,y,-.035),(L,.022,.045))
     for u in np.arange(1.2,L,2.4):J.box('fs-joint',(u,h/2,-.035),(.022,h,.045))
     if name=='NORDSTROM':
      for u in np.arange(2,L,5.5):J.box('fs-sand-light',(u,h/2,-.16),(.65,h,.26))
      J.box('fs-stone',(L/2,5.5,-.22),(L,.6,.5))
     if name=='NEIMAN MARCUS':
      for u in np.arange(1.4,L,2.8):J.box('fs-sand-light',(u,h/2,-.09),(.15,h,.14))
      if L>15:glass(J,L/2,1,6.3,L-3)
     entry_side=(nz<-.6 if name in ['NORDSTROM','MACY’S MEN',''] else nx<-.6 if name=='DILLARD’S' else (nx>.6 or nz>.6) if name=='NEIMAN MARCUS' else nz>.6)
     if L>24 and name!='GALLERIA' and entry_side:
      # Architectural closed entry treatment; no invented public interior.
      glass(J,L/2,.25,4.8,9)
      for u in [-3,-1,1,3]:
       J.box('fs-metal',(L/2+u,2.4,-.4),(.06,4.5,.12))
       J.tube('fs-metal',(L/2+u+.3,1,-.5),(L/2+u+.3,2,-.5),.025,6)
      label=name if name!='SOUTH RETAIL' else ''
      if label:J.text(label,(L/2,min(h-2,10),-.3),min(1.6,(L-3)/max(8,len(label))),'fs-sign')
      if name=='NORDSTROM':
       canopy=Point(*J.p(L/2,0,-4)[::2]).buffer(1,32)
       canopy=scale(canopy,11,5,origin='centroid');B.extrude('fs-stone',canopy,5.4,5.75,True)
       for u in [L/2-8,L/2+8]:J.box('fs-sand',(u,2.7,-5),(.7,5.4,.7),True)
      elif name in ['MACY’S MEN','MACY’S','DICK’S']:
       J.box('fs-metal',(L/2,4.9,-1.7),(12,.22,3.4),True)
     if L>35 and name=='GALLERIA':
      for u in np.arange(9,L-4,15):
       J.box('fs-service',(u,2.5,-.1),(4.6,4.7,.12))
       for y in np.arange(.4,4.7,.23):J.box('fs-joint',(u,y,-.19),(4.5,.035,.07))
  # Sparse mechanical clusters; avoid the previous uniform carpet of boxes.
  for ix,x in enumerate(np.arange(q.bounds[0]+8,q.bounds[2],27)):
   for iz,z in enumerate(np.arange(q.bounds[1]+8,q.bounds[3],31)):
    if (ix+iz*2)%3==0 and q.contains(box(x-2,z-1.5,x+2,z+1.5)):
     B.box('fs-service',(x,h+.65,z),(4,1.3,3));B.box('fs-metal',(x,h+1.34,z),(4.1,.08,3.1))
     for dx in [-.85,.85]:B.lathe('fs-joint',(x+dx,z),[(h+1.39,.62),(h+1.45,.62)],12)
  # Irregular groups of rooftop mechanical housings, not a continuous flat slab.
  for x in np.arange(q.bounds[0]+13,q.bounds[2],34):
   for z in np.arange(q.bounds[1]+11,q.bounds[3],39):
    if (int(x/34)+int(z/39))%4==0 and q.contains(box(x-4,z-3,x+4,z+3)):
     B.box('fs-service',(x,h+1.3,z),(8,2.6,6));B.box('fs-metal',(x,h+2.65,z),(8.2,.12,6.2))
 # Solar-topped capsule over the western central concourse, established in Earth.
 B.source='galleria-skylight'
 capsule=LineString([(-68,-1275),(136,-1275)]).buffer(17,32).intersection(p)
 B.shell(capsule,16.5,20,'fs-glass',roof=False,solid=False);B.planar('fs-white',capsule,20.05)
 for x in np.arange(-80,152,20):
  for z in [-1283,-1267]:
   panel=box(x-9,z-6,x+9,z+6).intersection(capsule.buffer(-1.2))
   if not panel.is_empty:
    B.planar('fs-solar',panel,20.12)
    for xx in np.arange(x-8,x+9,1.5):
     stripe=box(xx-.025,z-6,xx+.025,z+6).intersection(panel)
     if not stripe.is_empty:B.planar('fs-metal',stripe,20.14)
 # Larger Cloud columns and open truss crowns from landlord photograph.
 B.source='cloud-supports'
 for x,z in [(347,-1195),(389,-1261)]:
  B.extrude('fs-metal',Point(x,z).buffer(3.65,12),.15,36.8,True)
  B.lathe('fs-metal',(x,z),[(.2,4.2),(1,4.6),(1.5,3.8),(37,3.8)],48)
  for lo,hi in [(7,21)]:
   for j in range(48):
    a=j*math.tau/48;b=(j+1)*math.tau/48
    B.face('fs-screen',[(x+3.87*math.cos(a),lo,z+3.87*math.sin(a)),(x+3.87*math.cos(b),lo,z+3.87*math.sin(b)),(x+3.87*math.cos(b),hi,z+3.87*math.sin(b)),(x+3.87*math.cos(a),hi,z+3.87*math.sin(a))])
  for y in np.arange(22,37,1.8):B.lathe('fs-joint',(x,z),[(y,3.84),(y+.08,3.84)],48)
  for j in range(12):
   a=j*math.tau/12;b=(j+1)*math.tau/12
   B.tube('fs-metal',(x+3.8*math.cos(a),37,z+3.8*math.sin(a)),(x+3.8*math.cos(a),42,z+3.8*math.sin(a)),.11,8)
   B.tube('fs-metal',(x+3.8*math.cos(a),37,z+3.8*math.sin(a)),(x+3.8*math.cos(b),42,z+3.8*math.sin(b)),.085,8)
  for y in [37,39.5,42]:B.path('fs-metal',[(x+3.8*math.cos(a),y,z+3.8*math.sin(a)) for a in np.linspace(0,math.tau,49)],.14)
  J=Frame(B,x+3.95,z,math.pi/2,y=0);J.text('FASHION SHOW',(0,41.1,0),.65,'fs-white')
 # Upper Plaza terrace under the curved retail facade. Main ground portal stays clear.
 B.source='strip-plaza'
 F.box('fs-stone',(0,6.45,-3),(64,.36,5.8),True)
 for u in [-29,-19,19,29]:F.box('fs-metal',(u,3.135,-5.1),(.35,6.27,.35),True)
 upper=Frame(B,F.x,F.z,F.yaw,y=6.87)
 for lo,hi in [(-32,-26.8),(-23.2,23.2),(26.8,32)]:upper.rail((lo,-5.82),(hi,-5.82),1.15,True)
 for x in [-25,25]:F.stairs(x,-18,3.3,6.63,12.2)
 for x in [-12,12]:upper.bench(x,-3)
 # Names are architectural labels, not downloaded advertising artwork.
 F.text('THE CAPITAL GRILLE',(14,13.3,-.5),.56,'fs-white')
 F.text('MAGGIANO’S',(-14,8.7,-.5),.7,'fs-white')
 return areas
