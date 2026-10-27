"""QUADZ mapped exterior and inferred public room, original redistributable geometry.
Frontage: Google Street View February 2023. Public features: Las Vegas photo set.
No surveyed interior plan; western retail is a separate closed tenancy.
"""
from common import *
KEY='quadz';ID='way/1382446128';YAW=-math.atan2(1.358,31.061)
def build(B):
 p=footprint(ID);F=Frame(B,1969.332,1173.452,YAW,y=0)
 B.property=KEY+'-exterior';B.source='podium/quadz';B.detail=0
 entry=dict(p=F.p(20,.21,0),yaw=YAW,width=1.45,height=2.25,name='QUADZ public entrance',venue=KEY)
 B.shell(p,.08,1.05,'q-brown',openings=[entry],roof=False)
 B.shell(p,1.05,3.45,'q-cream',openings=[entry],roof=False)
 B.shell(p,3.45,4.55,'q-green',roof=False)
 B.planar('q-roof',p,4.55);B.planar('q-floor',p,.21,True)
 # Continuous shallow canopy with curved cap, distinct from structural wall.
 F.box('q-green',(15.55,3.98,-.20),(31.1,1.08,.40))
 for i in range(12):
  a=i*math.pi/24;b=(i+1)*math.pi/24
  B.face('q-green',[F.p(x,4.5+.27*math.sin(t),.12-.34*math.cos(t)) for x,t in [(0,a),(31.1,a),(31.1,b),(0,b)]])
 F.box('q-stone',(15.55,3.32,-.12),(31.1,.40,.18))
 for x in [0.2,11.5,18.5,30.9]:F.box('q-brick',(x,1.65,-.10),(.30,3.15,.20))
 # Pale vertical siding at the front; blockwork is limited to side elevations.
 for a,b in [(10.8,16.95),(18.25,19.23),(20.77,31.0)]:F.box('q-panel',((a+b)/2,2.03,-.018),(b-a,1.95,.024))
 # Vertical panel joints, not thousands of masonry boxes.
 for x in [x for x in np.arange(.5,30.8,.31) if not 19.2<x<20.8 and not 2<x<10.8]:F.box('q-joint',(x,1.94,-.039),(.012,1.75,.012))
 for x,w,text in [(5.6,8.9,'GET BOOKED'),(20.0,9.5,'QUADZ'),(28.4,4.6,'VIDEO BAR')]:
  F.box('q-sign',(x,3.97,-.43),(w,.88,.055));F.text(text,(x,3.78,-.47),.68 if text=='QUADZ' else .42,'q-ink')
 for x,y,t in [(28.4,3.57,'COCKTAILS  GAMING'),(20,2.77,'QUADZ')]:F.text(t,(x,y,-.16),.19 if x>25 else .32,'q-red')
 # West retail storefront, glazed bays and double doors; private in this pass.
 for x in [3.1,5.3,7.5,9.7]:
  F.box('q-glass',(x,1.56,-.09),(2.03,2.22,.07))
  for dx in [-1.05,1.05]:F.box('q-metal',(x+dx,1.56,-.15),(.055,2.3,.07))
  for y in [.42,2.68]:F.box('q-metal',(x,y,-.15),(2.14,.05,.07))
  F.box('q-paper',(x,1.6,-.14),(.63,.85,.025));F.text('SHOP',(x,1.5,-.17),.16,'q-ink')
 for x in [5.9,6.7]:F.tube('q-metal',(x,1.0,-.20),(x,1.5,-.20),.022,8)
 # QUADZ has paired separate doors; keep one functioning clear public opening.
 F.box('q-dark',(17.6,1.36,-.10),(1.2,2.25,.08))
 for x in [16.96,18.24,19.23,20.77]:F.box('q-metal',(x,1.35,-.16),(.07,2.35,.09))
 for x in [17.6,20]:F.box('q-metal',(x,2.54,-.16),(1.4,.07,.09))
 F.text('EXIT',(17.6,1.95,-.17),.13,'q-sign')
 F.box('q-red',(21.7,1.95,-.08),(.7,.6,.07));F.text('WELCOME',(21.7,1.89,-.13),.11,'q-sign')
 F.box('q-dark',(25.8,2.83,-.12),(1.35,.53,.10));F.text('VIDEO BAR',(25.8,2.74,-.19),.15,'q-red')
 F.box('q-concrete',(15.55,.12,-.55),(31.1,.18,1.06),True)
 # Apron slope blends public threshold to existing parking ground.
 B.upface('q-concrete',[F.p(19,.21,-1.0),F.p(21,.21,-1.0),F.p(21,.10,-2.5),F.p(19,.10,-2.5)],True)
 for x in [2,8,14,25,29]:F.box('q-stop',(x,.15,-2.25),(1.55,.15,.16),True)
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):B.tube('q-metal',(a[0],4.58,a[1]),(b[0],4.58,b[1]),.055,6)
 for x,z in [(1980,1181),(1993,1183)]:
  B.box('q-metal',(x,4.92,z),(2.0,.7,1.6))
  for dz in np.arange(-.6,.7,.16):B.box('q-dark',(x,5.28,z+dz),(1.7,.02,.055))
 # Service side intentionally subdued; equipment positions are estimates.
 for x in [1978,1998]:B.tube('q-metal',(x,.15,1189.3),(x,4.5,1189.3),.045,8)
 B.property=KEY+'-interior';B.source='public/quadz'
 room=F.poly([(12,.15),(30.7,.15),(30.7,12.7),(12,12.7)])
 B.shell(room,.21,3.12,'q-wall',openings=[entry],roof=False)
 B.planar('q-floor',room,.22);B.planar('q-ceiling',room,3.15)
 # Long return bar along rear; circulation corridor is clear from front entry.
 F.box('q-dark',(22,.7,9.6),(12,1.0,1.0),True);F.box('q-counter',(22,1.24,9.6),(12.15,.13,1.16))
 F.box('q-dark',(28,.7,8.3),(1,1,3.5),True);F.box('q-counter',(28,1.24,8.3),(1.14,.13,3.6))
 F.tube('q-metal',(16,.39,8.9),(27.2,.39,8.9),.035,10)
 for u in np.arange(16.5,27.1,1.15):
  F.lathe('q-metal',u,8.45,[(.22,.23),(.27,.23),(.3,.045),(.93,.045)],12)
  F.lathe('q-vinyl',u,8.45,[(.91,.24),(1.02,.24)],20)
  # Angled video poker housing, original abstract screen graphics.
  for v0,v1,h0,h1 in [(9.2,9.8,1.32,1.58)]:B.face('q-screen',[F.p(u-.30,h0,v0),F.p(u+.30,h0,v0),F.p(u+.30,h1,v1),F.p(u-.30,h1,v1)])
  F.box('q-dark',(u,1.32,9.52),(.68,.13,.66))
 for y in [.8,1.45,2.1]:
  F.box('q-wood',(23,y,12.1),(12,.08,.45))
  for j,u in enumerate(np.arange(17.3,28.8,.28)):F.lathe('q-bottle' if j%3 else 'q-amber',u,12.1,[(y+.04,.04),(y+.27,.04),(y+.31,.02),(y+.40,.02)],8)
 # Tables, pockets, rails, balls and cue rack. Placement inferred from photos.
 for u,v in [(14,3.0),(14,6.7),(23.8,3.0)]:
  F.box('q-wood',(u,.69,v),(1.55,.75,2.75),True)
  F.box('q-felt',(u,1.10,v),(1.38,.04,2.55))
  for dx in [-.78,.78]:F.box('q-wood',(u+dx,1.14,v),(.14,.16,2.9))
  for dz in [-1.4,1.4]:F.box('q-wood',(u,1.14,v+dz),(1.65,.16,.14))
  for dx in [-.64,.64]:
   for dz in [-1.23,0,1.23]:F.lathe('q-dark',u+dx,v+dz,[(1.11,.075),(1.13,.075)],12)
  for j in range(6):B.sphere('q-ball',F.p(u+(j%3-.8)*.10,1.15,v+(j//3)*.09),.028,8,5)
  F.tube('q-wood',(u-.4,1.21,v-.9),(u+.3,1.21,v+.9),.013,8)
  F.box('q-dark',(u,2.75,v),(1.2,.15,2.1));F.box('q-lamp',(u,2.66,v),(1.1,.02,1.9))
 for u in [18,26]:
  F.lathe('q-metal',u,5.7,[(.22,.32),(.26,.32),(.3,.05),(1.22,.05)],12)
  F.lathe('q-wood',u,5.7,[(1.22,.55),(1.29,.55)],24)
 for u in [15,21,27]:
  F.box('q-dark',(u,2.3,12.42),(1.55,.95,.12));F.box('q-screen',(u,2.3,12.34),(1.42,.81,.02))
 for v in [2,6,10]:
  F.tube('q-dark',(12.5,2.98,v),(30,2.98,v),.035,6)
  for u in [16,20,24,28]:F.box('q-lamp',(u,2.9,v),(.10,.12,.10))
 for u,v,c in [(19,5,0xc8b9ff),(24,10,0xffc691),(14,6,0x8295ff)]:F.light(u,2.7,v,color=c,power=15,range=9)
 routes=[dict(name='Entrance and bar circulation',points=[F.p(u,y,v) for u,y,v in [(20,.10,-2.5),(20,.21,-.5),(20,.22,2),(20,.22,7),(26,.22,7)]])]
 return dict(key=KEY,name='QUADZ Las Vegas',center=F.p(20,0,6),bounds=list(p.bounds),structural=True,exteriorOnly=False,portals=[entry],zones=[dict(origin=F.p(21.35,.21,.15),yaw=YAW,width=18.7,depth=12.55,height=3)],lights=B.lights,routes=routes,hotelSources=[],views={'bar':dict(eye=F.p(20,1.8,3.5),target=F.p(23,1.4,10))})
if __name__=='__main__':
 B=Meshes();meta=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(meta,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
