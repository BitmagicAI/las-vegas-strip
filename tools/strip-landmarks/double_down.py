"""Original Double Down Saloon study on its mapped envelope.
East porch corroborated in February 2026 Street View. Public furniture character
follows dated Las Vegas photographs; room placement is an explicit inference.
"""
from common import *
KEY='doubleDown'; ID='way/966155068'; YAW=math.atan2(16.742,-.09)
def frame(B):return Frame(B,2034.052,1174.955,YAW,y=0)

def build(B):
 F=frame(B);p=footprint(ID);B.property=KEY+'-exterior';B.source='podium/double-down-saloon';B.detail=0
 # The door is on the east face, not beneath the west parking-lot sign.
 e=F.p(8.4,.34,12.9);entry=dict(p=e,yaw=YAW+math.pi,width=1.65,height=2.3,name='Double Down entrance',venue=KEY)
 B.portals.append(entry)
 B.shell(p,.16,4.65,'dd-block',openings=[entry],roof=False)
 B.planar('dd-floor',p,.34,True);B.planar('dd-roof',p.buffer(.10),4.68)
 for u in [.12,16.6]:F.box('dd-trim',(u,4.68,6.45),(.24,.24,13.1))
 # West: green rounded fascia, dark brick piers and pointed arch strips.
 F.box('dd-green',(8.35,4.12,-.13),(16.7,.92,.25))
 for i in range(12):
  a=i*math.pi/24;b=(i+1)*math.pi/24
  B.face('dd-green',[F.p(u,4.55+.35*math.sin(t),.22-.35*math.cos(t)) for u,t in [(0,a),(16.7,a),(16.7,b),(0,b)]])
 for u in [.2,5.6,11.1,16.5]:F.box('dd-brick',(u,1.9,-.10),(.35,3.45,.18))
 for u in [2.9,8.35,13.8]:
  for side in [-1,1]:F.path('dd-brick',[(u+side*2.6*(1-t),.3+3.25*math.sin(t*math.pi/2),-.13) for t in np.linspace(0,1,18)],.10,6)
 F.box('dd-sign',(13.8,4.12,-.30),(4.8,.84,.10));F.text('DOUBLE DOWN',(13.8,4.23,-.37),.33,'dd-dark');F.text('SALOON',(13.8,3.88,-.37),.34,'dd-dark')
 # North is blind blockwork with a large sign and planting bed.
 N=Frame(B,*F.p(16.75,0,0)[::2],YAW-math.pi/2,y=0)
 N.box('dd-red',(6.45,3.6,-.10),(10.8,.95,.12));N.box('dd-sign',(6.45,3.6,-.18),(10.56,.75,.06));N.text('DOUBLE DOWN SALOON',(6.45,3.40,-.23),.51,'dd-red')
 N.box('dd-stone',(6.45,.32,-.7),(12.8,.32,1.05),True)
 from courtyard_525 import palm
 for i,x in enumerate([1.3,4.6,7.9,11.2]):palm(B,N,x,-.7,8.7+i*.22)
 # East porch: a modest shingled canopy on posts, not a guessed north doorway.
 F.box('dd-stone',(8.4,.22,13.9),(7.8,.24,2.2),True)
 for u in [4.65,12.15]:F.box('dd-dark',(u,1.57,14.8),(.14,2.5,.14))
 for v0,v1,h0,h1 in [(12.65,14,3.35,3.8),(14,15.15,3.8,3.05)]:
  B.face('dd-shingle',[F.p(4.35,h0,v0),F.p(12.45,h0,v0),F.p(12.45,h1,v1),F.p(4.35,h1,v1)])
 F.box('dd-trim',(8.4,3.03,15.13),(8.2,.16,.13))
 # Threshold access remains continuous, including a shallow apron ramp.
 B.upface('dd-stone',[F.p(7.1,.34,14.9),F.p(9.7,.34,14.9),F.p(9.7,.12,17.1),F.p(7.1,.12,17.1)],True)
 for u in [5.6,11.2]:
  F.box('dd-red',(u,4.15,13.01),(2.3,.75,.12));F.box('dd-sign',(u,4.15,13.09),(2.1,.55,.06))
 E=Frame(B,*F.p(8.4,0,13.15)[::2],YAW+math.pi,y=0)
 E.text('DOUBLE DOWN',(2.8,4.0,0),.25,'dd-red');E.text('SALOON',(-2.8,4.0,0),.35,'dd-red')
 # Service detail and roof equipment, outside the public route.
 for u in [3,13]:
  F.box('dd-metal',(u,4.98,6.5),(2.1,.6,1.7))
  for dv in np.arange(-.65,.7,.16):F.box('dd-dark',(u,5.29,6.5+dv),(1.7,.025,.045))
 F.tube('dd-metal',(15.9,.3,12.98),(15.9,4.55,12.98),.045,8)
 B.property=KEY+'-interior';B.source='public/double-down-saloon'
 B.shell(p.buffer(-.16),.34,3.15,'dd-poster',openings=[entry],roof=False,solid=False)
 B.planar('dd-floor',p.buffer(-.18),.35)
 B.planar('dd-ceiling',p.buffer(-.16),3.18)
 # Clear east entry -> central floor -> bar route; no invented private rooms.
 F.box('dd-dark',(8.0,.85,3.1),(10.5,1.02,1.05),True)
 F.box('dd-wood',(8.0,1.4,3.1),(10.7,.12,1.22))
 F.tube('dd-metal',(2.8,.56,3.85),(13.2,.56,3.85),.04,10)
 for u in np.arange(3.5,13,1.2):
  F.lathe('dd-metal',u,4.2,[(.35,.23),(.42,.23),(.44,.04),(1.04,.04)],12)
  F.lathe('dd-vinyl',u,4.2,[(1.02,.24),(1.12,.25)],20)
 for y in [.85,1.6,2.35]:
  F.box('dd-wood',(8,y,.65),(10.2,.10,.48))
  for j,u in enumerate(np.arange(3.1,13,.23)):
   h=.2+(j%4)*.045
   F.lathe('dd-bottle' if j%3 else 'dd-amber',u,.67,[(y+.05,.045),(y+h,.045),(y+h+.06,.024),(y+h+.14,.024)],8)
 F.box('dd-metal',(14,1.55,.75),(1.15,2.4,.78),True)
 F.box('dd-glass',(14,1.6,1.17),(.93,2.15,.03))
 for y in [.8,1.35,1.9,2.4]:F.box('dd-metal',(14,y,1.2),(.94,.035,.04))
 for u in [4,6.6,9.2]:
  F.box('dd-dark',(u,1.52,3.13),(.7,.18,.46));F.box('dd-screen',(u,1.63,3.1),(.56,.02,.34))
 # Rear live-music corner and cabinets, reference-supported function, inferred placement.
 F.box('dd-wood',(2.3,.5,10.6),(3.6,.3,3.4),True)
 for v in [9.2,12]:
  F.box('dd-dark',(1.2,1.2,v),(.65,1.4,.6))
  for y in [.95,1.5]:F.lathe('dd-metal',1.2,v,[(y,.18),(y+.03,.18)],16)
 F.tube('dd-metal',(3,.65,10.7),(3,2.05,10.7),.02,8)
 F.tube('dd-metal',(3,2.05,10.7),(3.35,2.15,10.7),.025,8)
 # Original collage sheets and hanging paper strips; no photo/artwork copying.
 rng=random.Random(234)
 for j in range(110):
  u=rng.uniform(.6,16);v=rng.uniform(.7,12);y=rng.uniform(2.5,3.1)
  F.box('dd-paper'+str(j%3),(u,y,v),(.16+rng.random()*.16,.018,.12+rng.random()*.16))
 for v in [2.0,6.8,10.8]:
  F.path('dd-dark',[(u,2.9-.25*math.sin(u*math.pi/16),v) for u in np.linspace(.4,16.3,32)],.012,6)
  for j,u in enumerate(np.arange(.6,16,.55)):
   F.lathe('dd-bulb'+str(j%3),u,v,[(2.57,.025),(2.66,.035)],8)
 for u,v,c in [(5,5,0xffbd85),(12,5,0x9cafff),(5,10,0xff779b)]:F.light(u,2.7,v,color=c,power=18,range=9)
 routes=[dict(name='East porch to public bar',points=[F.p(u,y,v) for u,y,v in [(8.4,.12,17),(8.4,.34,14.7),(8.4,.35,11.8),(8.4,.35,6.5),(13.8,.35,6.5)]])]
 return dict(key=KEY,name='Double Down Saloon',center=F.p(8,0,6),bounds=list(p.bounds),structural=True,exteriorOnly=False,portals=[entry],zones=[dict(origin=F.p(8.35,.34,0),yaw=YAW,width=16.7,depth=12.9,height=3.2)],lights=B.lights,routes=routes,hotelSources=[],views={'east':dict(eye=F.p(8,3,27),target=F.p(8,2,12.8)),'north':dict(eye=F.p(27,3,18),target=F.p(16,2,6)),'bar':dict(eye=F.p(10,1.9,10),target=F.p(7,1.6,2))})

if __name__=='__main__':
 B=Meshes();meta=build(B);B.groups={k:g for k,g in B.groups.items() if g['material']!='c525-collision'};B.save_all();(OUT/'doubleDown-metadata.json').write_text(json.dumps(meta,indent=2)+'\n');print('Double Down:',sum(len(g['faces']) for g in B.groups.values()),'triangles')
