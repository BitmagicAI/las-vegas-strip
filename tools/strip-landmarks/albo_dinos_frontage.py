"""Albo Pizza and Dino's Lounge street architecture, Jan2026 Street View."""
from common import *
from forum_shops import facade_frame
KEY='alboDinosFrontage'
IDS=['way/1020191190','way/364846573']
def canopy(B,G,L,mat,inside=1.8):
 profile=[(3.2,-.6),(4.35,inside),(4.25,inside),(3.1,-.6)]
 for (y,w),(yy,ww) in zip(profile,profile[1:]+profile[:1]):B.face(mat,[G.p(0,y,w),G.p(L,y,w),G.p(L,yy,ww),G.p(0,yy,ww)])
 for u in [0,L]:B.face(mat,[G.p(u,y,w) for y,w in profile])
 for u in np.arange(.15,L,.4):G.tube('ad-seam-paint',(float(u),3.22,-.61),(float(u),4.37,inside),.018,4)
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/albo-dinos';B.detail=0;W=Frame(B,0,0,y=0)
 p=footprint(IDS[0]);d=footprint(IDS[1]);body=d.intersection(Polygon([(1800,-4200),(1894,-4200),(1894,-4075),(1893,-4065),(1890,-4052),(1800,-4052)]))
 for i,q in enumerate([p,body]):
  B.shell(q,.12,3.55,'ad-dark-brick',roof=False);B.planar('ad-flat-roof-paint',q,3.6)
  for a,b in zip(list(q.exterior.coords),list(q.exterior.coords)[1:]):
   G,L,nx,nz=facade_frame(B,a,b,q,.035)
   G.box('ad-coping-paint',(L/2,3.59,-.07),(L,.14,.16))
   front=nx>.65
   if front:
    if i==0:
     canopy(B,G,L,'ad-charcoal-roof-paint')
     G.box('ad-white-paint',(L*.36,1.94,-.14),(L*.52,1.25,.15));G.box('ad-glass',(L*.36,1.94,-.24),(L*.52-.12,1.1,.04))
     for at in np.arange(L*.1,L*.63,.65):G.box('ad-white-paint',(float(at),1.94,-.28),(.04,1.12,.04))
     G.box('ad-white-paint',(L*.36,1.94,-.28),(L*.52,.04,.04))
     u=L*.79;G.box('ad-white-paint',(u,1.27,-.15),(1.14,2.25,.15));G.box('ad-glass',(u,1.25,-.25),(.99,2.1,.04));G.box('ad-handle-paint',(u+.3,1.2,-.3),(.035,.3,.04))
     G.box('ad-white-paint',(L*.5,3.82,.65),(L*.86,.72,.06));G.text('ALBO PIZZA',(L*.5,3.85,.60),.48,'ad-red-letter');G.text('RESTAURANT',(L*.5,4.6,1.7),.44,'ad-white-letter')
    else:
     G.box('ad-black-paint',(L/2,2.0,-.12),(L-.15,1.7,.10))
     if L>7:
      G.text("Dino's",(L/2,2.54,-.2),.65,'ad-white-letter');G.text('LOUNGE',(L/2,1.88,-.2),.28,'ad-white-letter')
   elif L>5:
    for u in [L*.25,L*.75]:
     G.box('ad-vent-paint',(u,2.65,-.11),(1.0,.45,.09))
     for y in [2.5,2.6,2.7,2.8]:G.box('ad-dark-paint',(u,y,-.17),(.92,.025,.03))
    G.box('ad-service-paint',(L*.6,1.25,-.1),(1.1,2.2,.12))
  x,z=q.centroid.x,q.centroid.y
  for dx,dz in [(-3,-2),(2,2)]:
   W.box('ad-service-paint',(x+dx,4.05,z+dz),(1.5,.9,1.4));W.box('ad-vent-paint',(x+dx,4.52,z+dz),(1.25,.03,1.2))
 # One continuous street roof avoids overlapping fans at concave mapped footprint edges.
 G=Frame(B,1900.78,-4072.58,yaw=-math.atan2(18.93,-5.28),y=0);L=19.65
 canopy(B,G,L,'ad-red-roof-paint',inside=4.0)
 G.text("Dino's",(L*.48,3.65,.28),.72,'ad-white-letter')
 for u in [.2,5,10,15,L-.2]:G.box('ad-black-paint',(u,1.62,-.35),(.08,2.98,.08),True)
 for u in np.arange(.1,17,.17):G.box('ad-black-paint',(float(u),.76,-.38),(.025,1.25,.025))
 for y in [.25,1.37]:G.box('ad-black-paint',(8.5,y,-.38),(17,.045,.045))
 B.face('ad-collision',[G.p(0,.12,-.38),G.p(17,.12,-.38),G.p(17,1.4,-.38),G.p(0,1.4,-.38)],True)
 for x,z in [(1896,-4071),(1895,-4066),(1894,-4060)]:
  W.box('ad-table-wood',(x,.87,z),(1.35,.10,.65));W.box('ad-black-paint',(x,.47,z),(.14,.72,.14),True)
  for dx in [-.62,.62]:W.box('ad-seat-wood',(x+dx,.48,z),(.32,.08,1.3));W.box('ad-black-paint',(x+dx,.28,z),(.09,.4,.9))
 # Two-post roadside pylon; no recreated phone numbers or advertising claims.
 H=Frame(B,1896,-4053,yaw=-math.pi/2,y=0)
 for u in [-.8,.8]:H.box('ad-white-paint',(u,3.65,0),(.20,7.0,.22),True)
 H.box('ad-red-sign-paint',(0,6.25,0),(2.4,1.35,.22));H.text("DINO'S",(0,6.3,-.13),.49,'ad-white-letter');H.text("DINO'S",(0,6.3,.13),.49,'ad-white-letter',back=True)
 H.box('ad-red-sign-paint',(0,4.15,0),(2.5,.85,.2));H.text('LOUNGE',(0,4.17,-.12),.31,'ad-white-letter')
 site=unary_union([p.buffer(1.2,join_style=2),d.buffer(1.3,join_style=2),Polygon([(1880,-4090),(1914,-4090),(1914,-4075),(1905,-4050),(1880,-4050)])]).difference(unary_union([p,body]));B.planar('ad-pavement-concrete',site,.12,True)
 B.groups={k:g for k,g in B.groups.items() if g['material']!='ad-collision'}
 samples=[]
 for x in np.arange(1881,1913,.8):
  for z in np.arange(-4089,-4052,.8):
   point=Point(x,z)
   if site.buffer(-.45).contains(point) and not unary_union([p,body]).buffer(.7).contains(point) and (x<1881.2 or x>1902 or z<-4077 or z>-4055):samples.append([float(x),.12,float(z)])
 Path('build/city-exteriors/albo-dinos-frontage-samples.json').write_text(json.dumps(samples))
 return dict(key=KEY,name="Albo Pizza and Dino's Lounge",center=[1895,0,-4070],bounds=[1879,-4090,1914,-4050],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
