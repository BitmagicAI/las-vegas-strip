"""Gipsy: original 2023 facade/courtyard and photo-supported public-room study.
Dimensions and partition positions are estimates; no private interior is asserted.
"""
from common import *
KEY='gipsy';ID='way/1017043833'
def build(B):
 # The rebuilt rectangular body spans the older mapped shell; courtyard lies east.
 F=Frame(B,1901.7,1133.35,math.pi,y=0);W=25.1;D=18.1
 p=F.poly([(0,0),(W,0),(W,D),(0,D)])
 E=Frame(B,1901.7,1115.25,-math.pi/2,y=0)
 south=dict(p=F.p(12.55,.18,0),yaw=math.pi,width=1.9,height=3.3,name='Gipsy south entrance',venue=KEY)
 east=dict(p=E.p(9.05,.18,0),yaw=-math.pi/2,width=3.5,height=3.5,name='Gipsy courtyard entrance',venue=KEY)
 B.property=KEY+'-exterior';B.source='podium/gipsy';B.detail=0
 B.shell(p,.03,7.35,'gy-stucco',openings=[south,east],roof=False);B.planar('gy-roof',p,7.35);B.planar('gy-floor',p,.18,True)
 # Long Naples facade: five tall bays and arched end bays, layered cornice.
 for y,depth,h in [(6.65,.15,.18),(6.93,.25,.22),(7.19,.38,.18),(7.4,.49,.12)]:
  F.box('gy-cream',(W/2,y,-depth/2),(W+depth,h,depth))
 for u in np.arange(0,W,.96):F.box('gy-joint',(u,3.3,-.008),(.012,6.5,.018))
 for y in np.arange(.3,6.6,.78):F.box('gy-joint',(W/2,y,-.009),(W,.012,.018))
 for u in [4.45,8.5,12.55,16.6,20.65]:
  if u!=12.55:F.box('gy-glass',(u,2.08,-.055),(2.0,3.65,.07))
  for du in [-1.06,1.06]:F.box('gy-bronze',(u+du,2.08,-.12),(.09,3.77,.12))
  for y in [.23,3.95]:F.box('gy-bronze',(u,y,-.12),(2.2,.08,.12))
  if u!=12.55:F.box('gy-bronze',(u,2.05,-.13),(.035,3.6,.05))
  # Four-plane shallow metal hip canopy, not a triangular billboard.
  q=[(u-1.24,4.05,-.08),(u+1.24,4.05,-.08),(u+1.24,4.05,-.95),(u-1.24,4.05,-.95)]
  for i in range(4):B.face('gy-black',[F.p(*q[i]),F.p(*q[(i+1)%4]),F.p(u,4.62,-.16)])
  F.box('gy-black',(u,4.03,-.94),(2.5,.10,.08))
 for u in [1.5,23.6]:
  r=.72;spring=5.45
  pts=[(u-r,.3,-.06),(u+r,.3,-.06)]+[(u+r*math.cos(a),spring+r*math.sin(a),-.06) for a in np.linspace(0,math.pi,25)]
  B.face('gy-glass',[F.p(*v) for v in pts]);F.arch(u,-.13,1.5,6.2,'gy-cream',.07,base=.25)
  F.box('gy-bronze',(u,3.2,-.14),(.045,5.7,.05))
 F.box('gy-stucco',(12.55,6.1,-.75),(20.4,.85,1.5))
 F.box('gy-cream',(12.55,6.58,-.82),(20.8,.14,1.68))
 F.text('GIPSY',(12.55,6.16,-1.52),.82,'gy-gold')
 for a,b in [(3,11.1),(14,22.1)]:
  F.box('gy-stucco',((a+b)/2,.55,-1.85),(b-a,1.1,.25),True)
  F.box('gy-cream',((a+b)/2,1.13,-1.85),(b-a+.08,.10,.35))
 for u in [1.5,23.6]:
  # Original pinnate palm fronds, paired along the photographed Naples front.
  F.lathe('bark',u,-1.0,[(.16,.23),(6.5,.14)],12)
  for j in range(12):
   a=j*math.tau/12
   spine=[]
   for k in range(19):
    t=k/18;r=2.7*t;yy=6.5+1.4*math.sin(t*math.pi)-.8*t
    spine.append((u+r*math.cos(a),yy,-1+r*math.sin(a)))
    if k in [0,18]:continue
    for side in [-1,1]:
     w=.5*math.sin(t*math.pi)
     B.face('foliage',[F.p(u+r*math.cos(a),yy,-1+r*math.sin(a)),F.p(u+(r+.18)*math.cos(a),yy-.04,-1+(r+.18)*math.sin(a)),F.p(u+(r-.15)*math.cos(a)-side*w*math.sin(a),yy-.28,-1+(r-.15)*math.sin(a)+side*w*math.cos(a))])
   F.path('bark',spine,.012,6)
 for u in np.arange(.3,W,.33):F.box('gy-black',(u,7.9,.15),(.022,.88,.025))
 F.box('gy-black',(W/2,8.33,.15),(W,.035,.035))
 # East entrance has tall end piers and a lower central balcony/cornice.
 for a,b in [(0,6.4),(11.7,18.1)]:
  E.box('gy-stucco',((a+b)/2,7.65,.15),(b-a,.60,.30))
  for y,dep in [(7.83,.25),(8.02,.38)]:E.box('gy-cream',((a+b)/2,y,-dep/2),(b-a+.08,.14,dep))
 for y in [5.25,5.48]:E.box('gy-cream',(9.05,y,-.10),(5.3,.12,.22))
 for u in np.arange(6.5,11.7,.22):E.box('gy-bronze',(u,5.9,-.10),(.023,.74,.035))
 E.box('gy-bronze',(9.05,6.28,-.10),(5.3,.04,.05));E.text('GIPSY',(9.05,4.42,-.25),.94,'gy-gold')
 for u in [7.24,10.86]:E.box('gy-bronze',(u,1.95,-.16),(.12,3.7,.15))
 E.box('gy-bronze',(9.05,3.79,-.16),(3.75,.12,.15))
 # Public terrace connects Paradise-side gate to rollup entrance and Naples sidewalk.
 E.box('gy-paving',(9.05,.08,-9.1),(18.1,.16,18.2),True)
 for u in np.arange(.1,18.1,1.2):E.box('gy-pave-joint',(u,.163,-9.1),(.012,.004,18.1))
 for z in np.arange(-18,-.1,1.2):E.box('gy-pave-joint',(9.05,.163,z),(18,.004,.012))
 for u in [0,18.1]:
  E.box('gy-stucco',(u,.55,-9.1),(.25,1.1,18.2),True)
  E.box('gy-cream',(u,1.13,-9.1),(.36,.12,18.25))
 for a,b in [(0,7.65),(10.45,18.1)]:
  E.box('gy-stucco',((a+b)/2,.55,-18.2),(b-a,1.1,.25),True)
  for u in np.arange(a+.1,b,.16):E.box('gy-black',(u,1.45,-18.2),(.022,.7,.025))
  E.box('gy-black',((a+b)/2,1.82,-18.2),(b-a,.03,.04))
 # Potted shrubs and photographed courtyard furniture; walkway down centre stays clear.
 for u in [2.2,15.9]:
  for v in [-3,-10,-15.8]:
   E.lathe('gy-bronze',u,v,[(.16,.46),(.22,.52),(.95,.42)],16)
   rng=random.Random(int(u*100+v))
   for j in range(55):
    a=j*2.399;r=rng.uniform(.05,.4);h=rng.uniform(.4,.9)
    x=u+r*math.cos(a);z=v+r*math.sin(a)
    E.tube('gy-leaf-dark',(x,.92,z),(x+.12*math.cos(a),.92+h,z+.12*math.sin(a)),.009,5)
    for k in range(4):
     yy=1.0+h*k/4;w=.12
     B.face('gy-leaf',[E.p(x,yy,z),E.p(x+w*math.cos(a)-.04*math.sin(a),yy+.1,z+w*math.sin(a)+.04*math.cos(a)),E.p(x+w*math.cos(a)+.04*math.sin(a),yy+.1,z+w*math.sin(a)-.04*math.cos(a))])
 # Two full courtyard trees flank the opening in the completed contractor photo.
 rng=random.Random(250)
 for u in [3.3,14.8]:
  v=-3.3
  E.lathe('gy-stucco',u,v,[(.16,.60),(1.0,.48)],16)
  E.tube('bark',(u,1,v),(u+.12,3.8,v),.09,10,.04)
  for j in range(22):
   a=j*2.399;r=rng.uniform(.5,1.7);yy=rng.uniform(3,5.7)
   xx=u+r*math.cos(a);zz=v+r*math.sin(a)
   E.tube('bark',(u+.08,2.8,v),(xx,yy,zz),.025,6,.006)
   for k in range(24):
    la=rng.random()*math.tau;lr=rng.random()*.62;ly=yy+rng.uniform(-.35,.4)
    x=xx+lr*math.cos(la);z=zz+lr*math.sin(la);w=.075;l=.19
    B.face('gy-leaf' if k%3 else 'gy-leaf-dark',[E.p(x-l*math.cos(la),ly,z-l*math.sin(la)),E.p(x-w*math.sin(la),ly+.04,z+w*math.cos(la)),E.p(x+l*math.cos(la),ly+.02,z+l*math.sin(la)),E.p(x+w*math.sin(la),ly-.02,z-w*math.cos(la))])
 for u in [4.0,14.1]:
  for v in [-6,-12.5]:
   E.box('gy-black',(u,.77,v),(1.25,.09,.75))
   for du in [-.49,.49]:E.box('gy-bronze',(u+du,.4,v),(.045,.75,.5))
   for dv in [-.8,.8]:
    E.box('gy-black',(u,.48,v+dv),(.50,.06,.48));E.box('gy-black',(u,.8,v+dv+(.21 if dv>0 else -.21)),(.5,.55,.035))
    for dx in [-.21,.21]:
     for dz in [-.20,.20]:E.box('gy-bronze',(u+dx,.25,v+dv+dz),(.025,.45,.025))
 F.box('gy-paving',(W/2,.08,-1.1),(W,.16,2.2),True)
 E.box('gy-paving',(9.05,.08,-18.9),(2.8,.16,1.6),True)
 for u,v in [(5,4),(19,4),(8,14),(18,14)]:
  F.box('gy-equipment',(u,7.78,v),(1.8,.75,1.3))
  for z in np.arange(-.5,.51,.15):F.box('gy-black',(u,8.17,v+z),(1.6,.02,.045))
 # Public room: floor-plan inferred from the paired bar/courtyard photographs.
 B.property=KEY+'-interior';B.source='public/gipsy'
 room=F.poly([(.12,.1),(24.98,.1),(24.98,15.7),(.12,15.7)])
 B.shell(room,.18,6.7,'gy-room',openings=[south,east],roof=False);B.planar('gy-ceiling',room,6.71)
 # Long back bar, timber lattice apron and rounded red chair backs.
 F.box('gy-burgundy',(12.5,.69,12.8),(17,1.02,1.25),True);F.box('gy-counter',(12.5,1.25,12.8),(17.2,.12,1.4))
 F.tube('gy-gold',(4, .38,11.9),(21,.38,11.9),.035,10)
 for u in np.arange(4.1,21,.8):
  F.path('gy-gold',[(u,.24,12.15),(u+.25,.6,12.15),(u+.20,1.15,12.15)],.025,6)
  for yy,side in [(.40,-1),(.6,1),(.8,-1)]:
   F.path('gy-gold',[(u+.22,yy,12.15),(u+.22+side*.22,yy+.10,12.15),(u+.22+side*.35,yy+.30,12.15)],.021,6)
 for u in np.arange(4.5,21,1.05):
  F.lathe('gy-red',u,11.65,[(.98,.24),(1.06,.24)],16)
  for dx in [-.18,.18]:
   for dz in [-.18,.18]:F.box('gy-black',(u+dx,.57,11.65+dz),(.035,.8,.035))
  F.path('gy-black',[(u-.23,.97,11.45),(u-.23,1.48,11.45),(u+.23,1.48,11.45),(u+.23,.97,11.45)],.028,8)
  # Elliptical upholstered back, shallow horizontal cylinder in the wall plane.
  ring=[F.p(u+.20*math.cos(a),1.45+.26*math.sin(a),11.42) for a in np.linspace(0,math.tau,25)]
  B.face('gy-red',ring);B.path('gy-black',ring,.027,8)
 for y in [1.45,1.8]:
  F.box('gy-bronze',(12.5,y,15.3),(17,.06,.4))
  for j,u in enumerate(np.arange(4.2,20.9,.27)):F.lathe('gy-bottle' if j%3 else 'gy-amber',u,15.3,[(y+.03,.04),(y+.24,.04),(y+.28,.022),(y+.38,.022)],8)
 F.box('gy-gold',(12.5,4.2,15.55),(12.4,4.4,.08));F.box('gy-screen',(12.5,4.2,15.48),(11.9,3.95,.06));F.text('GIPSY',(12.5,4.15,15.43),1.48,'gy-sign')
 # Photo-supported filigree columns and purple leaf capitals, original motifs.
 for u in [4.6,20.3]:
  for v in [5.2,10.0]:
   F.box('gy-warm',(u,2.4,v),(.43,4.4,.43),True)
   for yy in np.arange(.3,4.5,.38):
    for side in [-1,1]:F.path('gy-bronze',[(u-.23,yy,v+side*.23),(u+.23,yy+.38,v+side*.23),(u-.23,yy+.76,v+side*.23)],.022,6)
   for a in np.linspace(0,math.tau,9,endpoint=False):
    for k in range(3):
     t=k/3;tt=(k+1)/3;r=.12+t*.85;r2=.12+tt*.85
     B.face('gy-purple',[F.p(u+r*math.cos(a)-.14*math.sin(a),4.55+t*.65,v+r*math.sin(a)+.14*math.cos(a)),F.p(u+r*math.cos(a)+.14*math.sin(a),4.55+t*.65,v+r*math.sin(a)-.14*math.cos(a)),F.p(u+r2*math.cos(a),4.55+tt*.65,v+r2*math.sin(a))])
 for yy in [5.8,6.1]:F.path('gy-bronze',[(12.55+4.3*math.cos(a),yy,7.5+4.3*math.sin(a)) for a in np.linspace(0,math.tau,65)],.035,8)
 for a in np.linspace(0,math.tau,24,endpoint=False):
  u=12.55+4.3*math.cos(a);v=7.5+4.3*math.sin(a)
  F.tube('gy-bronze',(u,5.8,v),(u,6.1,v),.024,6)
  F.box('gy-black',(u,5.58,v),(.23,.30,.28))
 for u in np.arange(4.5,21,1.5):
  F.tube('gy-black',(u,6.6,12.1),(u,3.7,12.1),.008,6);F.lathe('gy-warm',u,12.1,[(3.48,.045),(3.7,.045)],10)
 for u in [2.1,22.9]:
  for v in [3.5,7.3,10.5]:
   F.lathe('gy-gold',u,v,[(.18,.26),(.25,.26),(.28,.035),(.72,.035)],12);F.lathe('gy-counter',u,v,[(.72,.48),(.78,.48)],24)
   for dv in [-.85,.85]:F.lathe('gy-red',u,v+dv,[(.18,.29),(.6,.29),(.69,.30)],16)
 for u,v in [(8,6),(17,6),(12,13)]:F.light(u,4.1,v,color=0xe4c1a0,power=24,range=12)
 routes=[dict(name='Courtyard to public room and south entrance',points=[E.p(9.05,.16,-19.5),E.p(9.05,.16,-12),E.p(9.05,.16,-4),E.p(9.05,.18,2),F.p(12.55,.18,7),F.p(12.55,.18,2),F.p(12.55,.16,-1.8)])]
 return dict(key=KEY,name='Gipsy Nightclub',center=F.p(12.55,0,8),bounds=[1876.6,1115.2,1920.0,1133.5],structural=True,exteriorOnly=False,portals=[south,east],zones=[dict(origin=F.p(12.55,.18,.1),yaw=math.pi,width=24.86,depth=15.6,height=6.5)],lights=B.lights,routes=routes,hotelSources=[],views={'room':dict(eye=F.p(12.5,1.8,3),target=F.p(12.5,2,13))})
if __name__=='__main__':
 B=Meshes();meta=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(meta,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
