"""515 East St Louis: brick office, western arcade and red-roof entry tower."""
from common import *
from forum_shops import facade_frame
from st_louis_square_frontage import roof
KEY='stLouisOffice515';YAW=math.atan2(19.302,10.36)
def frame(B):return Frame(B,1764.029,-3582.295,yaw=YAW,y=0)
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/office515';B.detail=0;F=frame(B);p=footprint('way/364845139');body=p.intersection(F.poly([(-1,2),(23,2),(23,22),(-1,22)]))
 B.shell(body,.12,4.3,'o515-brick',roof=False)
 for a,b in zip(list(body.exterior.coords),list(body.exterior.coords)[1:]):
  G,L,nx,nz=facade_frame(B,a,b,body,.035)
  for y,h,d in [(3.48,.18,.15),(3.9,.6,.13),(4.27,.15,.3)]:G.box('o515-white-paint',(L/2,y,-d/2),(L,h,d))
  count=max(1,round(L/4.2))
  for j in range(count):
   u=L*(j+.5)/count
   for du in [-1.45,1.45]:G.box('o515-white-paint',(u+du,2.55,-.13),(.10,1.8,.10))
   G.path('o515-white-paint',[(u+1.45*math.cos(t),3.35+.24*math.sin(t),-.15) for t in np.linspace(0,math.pi,18)],.055,6)
   if nx<-.65:
    G.box('o515-frame-paint',(u,2.0,-.15),(2.1,2.45,.16));G.box('o515-glass',(u,2.0,-.25),(1.96,2.3,.04))
    for dx in [-.65,0,.65]:G.box('o515-frame-paint',(u+dx,2.0,-.30),(.035,2.3,.035))
    G.box('o515-frame-paint',(u,2.0,-.30),(1.96,.035,.035))
   elif nx>.65:
    if j in [1,count-2]:
     G.box('o515-frame-paint',(u,1.75,-.15),(1.25,2.3,.15));G.box('o515-door-paint',(u,1.75,-.26),(1.1,2.15,.04));G.text('515',(u,2.62,-.31),.23,'o515-dark-letter')
     G.box('o515-step-concrete',(u,.5,-.35),(1.65,.2,.7),True)
     q=G.p(u,0,-2.1);S=Frame(B,q[0],q[2],yaw=G.yaw,y=0);S.stairs(0,0,1.4,.48,1.4,y=.12)
    elif j==2:
     G.box('o515-service-paint',(u,1.7,-.22),(.9,1.4,.35))
     for dx in [-.3,0,.3]:G.tube('o515-conduit-paint',(u+dx,.2,-.15),(u+dx,3.5,-.15),.027,6)
 # Continuous dark mansard around the white flat central roof.
 outer=[(-.15,-.15),(22.05,-.15),(22.05,21.02),(-.15,21.02)];inner=[(.65,.65),(21.25,.65),(21.25,20.22),(.65,20.22)]
 for i in range(4):
  a,b=outer[i],outer[(i+1)%4];c,d=inner[(i+1)%4],inner[i]
  B.upface('o515-mansard-paint',[F.p(a[0],4.4,a[1]),F.p(b[0],4.4,b[1]),F.p(c[0],5.1,c[1]),F.p(d[0],5.1,d[1])])
 B.planar('o515-roof-paint',F.poly(inner),5.1)
 # Colonnaded front terrace sits above the parking level.
 F.box('o515-terrace-concrete',(11,.48,.5),(22,.24,3.0),True)
 for u in [0,3.67,7.34,14.66,18.33,22]:
  F.box('o515-white-paint',(u,2.1,-.8),(.25,3.0,.25),True);F.box('o515-white-paint',(u,.8,-.8),(.42,.4,.42),True);F.box('o515-white-paint',(u,3.45,-.8),(.5,.18,.5))
 F.box('o515-white-paint',(11,3.85,.4),(22,.7,2.8))
 for a,b in [(0,3.67),(3.67,7.34),(7.34,9),(13,14.66),(14.66,18.33),(18.33,22)]:F.path('o515-white-paint',[((a+b)/2+(b-a)/2*math.cos(t),3.5+.28*math.sin(t),-1.0) for t in np.linspace(0,math.pi,18)],.075,6)
 F.box('o515-white-paint',(11,5.05,1),(3.8,2.4,3.5),True)
 for u in [10.15,11.85]:
  F.box('o515-glass',(u,5.18,-.78),(.62,1.35,.04));F.arch(u,-.82,.72,6.02,mat='o515-frame-paint',thick=.045,base=4.52)
 roof(B,F,8.9,13.1,-.95,2.95,y=6.32,rise=1.0)
 F.text('515',(11,4.12,-1.04),.28,'o515-dark-letter');F.text('BUILDING C',(4.7,3.92,-1.04),.3,'o515-dark-letter')
 # Entry behind the small tower, with an explicit sloped approach from the west apron.
 F.box('o515-frame-paint',(11,1.82,1.86),(1.85,2.4,.16));F.box('o515-glass',(11,1.82,1.76),(1.68,2.24,.04))
 B.upface('o515-ramp-concrete',[F.p(5,.12,-3.0),F.p(11,.6,-3.0),F.p(11,.6,-1.5),F.p(5,.12,-1.5)],True)
 F.box('o515-terrace-concrete',(12,.48,-1.7),(2,.24,2.6),True)
 for w in [-3,-1.5]:F.tube('o515-rail-paint',(5,1.15,w),(11,1.63,w),.035,8)
 for u,y in [(5,.12),(8,.36),(11,.6)]:
  for w in [-3,-1.5]:F.tube('o515-rail-paint',(u,y,w),(u,y+1.03,w),.03,8)
 # Single exterior paving owner; retain existing roads and parking beyond the apron.
 site=p.buffer(2.5,join_style=2).union(F.poly([(3,-4),(14,-4),(14,0),(3,0)])).difference(p)
 B.planar('o515-apron-concrete',site,.12,True)
 for u,w in [(5,6),(16,6),(5,16),(16,16)]:F.box('o515-service-paint',(u,5.55,w),(1.35,.9,1.25));F.box('o515-vent-paint',(u,6.02,w),(1.12,.035,1.03))
 for g in B.groups.values():
  if g['material']=='stone':g['material']='o515-step-concrete'
  if g['material']=='steel':g['material']='o515-rail-paint'
 samples=[]
 for u in np.arange(.7,21.3,1):
  for w in [-2,22.0]:
   if w<0 and 4<u<14:continue
   samples.append(F.p(float(u),.12,w))
 Path('build/city-exteriors/st-louis-office-515-samples.json').write_text(json.dumps(samples))
 return dict(key=KEY,name='515 East St Louis office',center=[1778,0,-3587],bounds=[1759,-3605,1797,-3568],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
