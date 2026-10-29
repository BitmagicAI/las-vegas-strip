"""Office Bar I, original mapped facade and inferred public room. No private floors."""
from common import *
KEY='officeBar';ID='way/1042462824';YAW=math.pi-math.atan2(.245,14.199)
def build(B):
 p=footprint(ID);F=Frame(B,1983.63,1119.874,YAW,y=0)
 B.property=KEY+'-exterior';B.source='podium/office-bar';B.detail=0
 entry=dict(p=F.p(7.2,.21,0),yaw=YAW,width=1.35,height=2.35,name='Office Bar public entrance',venue=KEY)
 B.shell(p,.08,6.6,'ob-stucco',openings=[entry],roof=False);B.planar('ob-roof',p,6.6);B.planar('ob-floor',p,.21,True)
 for a,b in [(0,6.49),(7.91,14.2)]:F.box('ob-base',((a+b)/2,.23,-.045),(b-a,.32,.09))
 # The doorway interrupts the base trim; separate segments leave the opening clear.
 # Base trim is visual only and kept below the walking threshold.
 for x in [1.35,3.65,5.95,8.25,10.55,12.85]:
  F.box('ob-glass',(x,4.98,-.045),(.92,1.32,.04))
  for dx in [-.49,.49]:F.box('ob-frame',(x+dx,4.98,-.075),(.045,1.40,.055))
  for y in [4.30,5.66]:F.box('ob-frame',(x,y,-.075),(1.02,.045,.055))
 for y in [2.65,4.1,5.85]:F.box('ob-joint',(7.1,y,-.008),(14.2,.012,.012))
 for x in [2.4,11.8]:
  F.box('ob-glass',(x,1.38,-.045),(2.65,2.12,.06))
  for dx in [-1.36,0,1.36]:F.box('ob-black',(x+dx,1.38,-.09),(.065,2.2,.07))
  for y in [.30,2.46]:F.box('ob-black',(x,y,-.09),(2.78,.065,.07))
 for x in [6.17,8.23]:
  F.box('ob-glass',(x,1.41,-.055),(.60,2.35,.07))
  for dx in [-.33,.33]:F.box('ob-black',(x+dx,1.41,-.11),(.06,2.43,.08))
 for x in [6.49,7.91]:F.box('ob-frame',(x,1.41,-.12),(.055,2.44,.08))
 F.box('ob-frame',(7.2,2.64,-.12),(2.78,.07,.08))
 F.text('OFFICE',(7.2,3.75,-.10),.78,'ob-letter');F.text('BAR',(7.2,3.05,-.10),.75,'ob-letter')
 for x,t in [(8.23,'LIQUOR'),(6.17,'STORE')]:
  for j,ch in enumerate(t):F.text(ch,(x,2.30-j*.29,-.104),.22,'ob-letter')
 # Fixtures remain geometry; no additional runtime lights.
 for x in [1.3,2.3,3.3,6.2,7.2,8.2,11.3,12.3]:
  F.path('ob-black',[(x,2.78,-.03),(x,3.0,-.16),(x,3.03,-.38),(x,2.85,-.52)],.025,8)
  F.lathe('ob-black',x,-.52,[(2.73,.19),(2.78,.19),(2.88,.07)],12)
  F.lathe('ob-lamp',x,-.52,[(2.72,.16),(2.73,.16)],12)
 F.path('ob-black',[(5.8,3.3,-.08),(5.9,2.76,-.08),(8.7,2.76,-.08),(8.7,1.8,-.08)],.015,6)
 F.box('ob-concrete',(7.1,.12,-.65),(14.2,.18,1.3),True)
 B.upface('ob-concrete',[F.p(6.3,.21,-1.3),F.p(8.1,.21,-1.3),F.p(8.1,.08,-2.9),F.p(6.3,.08,-2.9)],True)
 for x in [5.65,8.75]:F.box('ob-black',(x,.52,-1.0),(.10,.85,.10),True)
 for x in [1.5,4.0,10.3,12.8]:F.box('ob-stop',(x,.15,-2.1),(1.55,.16,.16),True)
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):B.tube('ob-frame',(a[0],6.64,a[1]),(b[0],6.64,b[1]),.05,6)
 for u,v in [(4,6),(10,13)]:
  F.box('ob-frame',(u,6.95,v),(2.0,.6,1.6))
  for z in np.arange(-.6,.7,.18):F.box('ob-black',(u,7.26,v+z),(1.8,.02,.05))
 # Interior: observed public features, deliberately no copied murals or broadcast images.
 B.property=KEY+'-interior';B.source='public/office-bar'
 room=F.poly([(.25,.15),(13.9,.15),(13.9,17.8),(.25,17.8)])
 B.shell(room,.21,3.15,'ob-wall',openings=[entry],roof=False);B.planar('ob-floor',room,.22);B.planar('ob-ceiling',room,3.16)
 for u in np.arange(.3,14,1.2):F.box('ob-black',(u,3.14,9),(.018,.018,17.6))
 for v in np.arange(.3,17.9,1.2):F.box('ob-black',(7,3.14,v),(13.7,.018,.018))
 # Return counter at the rear, with circulation around the pool area.
 for u,v,w,d in [(7.5,14,9.8,1.15),(2.1,11.3,1.2,6.5)]:
  F.box('ob-wood',(u,.72,v),(w,1.02,d),True);F.box('ob-counter',(u,1.27,v),(w+.13,.12,d+.13))
 for u in np.arange(3.5,12,1.15):
  F.lathe('ob-black',u,12.9,[(.22,.23),(.26,.23),(.3,.04),(.94,.04)],12)
  F.lathe('ob-vinyl',u,12.9,[(.93,.24),(1.02,.24)],16)
  F.box('ob-black',(u,1.38,14),(.65,.18,.70));B.face('ob-screen',[F.p(u-.28,1.40,13.65),F.p(u+.28,1.40,13.65),F.p(u+.28,1.62,14.2),F.p(u-.28,1.62,14.2)])
 for y in [.8,1.5,2.2]:
  F.box('ob-wood',(7.5,y,17.4),(10.6,.08,.35))
  for j,u in enumerate(np.arange(2.5,12.4,.28)):F.lathe('ob-bottle' if j%3 else 'ob-amber',u,17.4,[(y+.04,.04),(y+.25,.04),(y+.30,.02),(y+.39,.02)],8)
 for u,v in [(4.6,6.3),(9.9,8.6)]:
  F.box('ob-wood',(u,.78,v),(2.6,.45,1.45),True);F.box('ob-felt',(u,1.04,v),(2.4,.035,1.25))
  for dx in [-1.05,1.05]:
   for dz in [-.5,.5]:F.box('ob-black',(u+dx,.5,v+dz),(.14,.56,.14))
  for dz in [-.73,.73]:F.box('ob-wood',(u,1.08,v+dz),(2.75,.14,.13))
  for dx in [-1.3,1.3]:F.box('ob-wood',(u+dx,1.08,v),(.13,.14,1.55))
  for dx in [-1.17,0,1.17]:
   for dz in [-.60,.60]:F.lathe('ob-black',u+dx,v+dz,[(1.06,.07),(1.08,.07)],12)
  for j in range(6):B.sphere('ob-ball',F.p(u+j%3*.07,1.09,v+j//3*.07),.027,8,5)
  F.tube('ob-wood',(u-.9,1.17,v-.4),(u+.8,1.17,v+.3),.012,8)
  F.box('ob-black',(u,2.7,v),(1.6,.12,.65));F.box('ob-lamp',(u,2.63,v),(1.45,.02,.53))
  for dx in [-.5,.5]:F.tube('ob-black',(u+dx,2.75,v),(u+dx,3.1,v),.014,6)
 for u in [3,7,11]:F.box('ob-black',(u,2.5,17.68),(1.6,.90,.10));F.box('ob-screen',(u,2.5,17.61),(1.46,.77,.02))
 for u,v,c in [(7,5,0xe7d8b9),(7,13,0xe6c4a0),(11,9,0x9daaff)]:F.light(u,2.8,v,color=c,power=15,range=9)
 routes=[dict(name='Entry and pool circulation',points=[F.p(u,y,v) for u,y,v in [(7.2,.08,-2.7),(7.2,.21,-.5),(7.2,.22,2),(7.2,.22,7),(7.2,.22,11)]])]
 return dict(key=KEY,name='Office Bar I',center=F.p(7,0,9),bounds=list(p.bounds),structural=True,exteriorOnly=False,portals=[entry],zones=[dict(origin=F.p(7.075,.21,.15),yaw=YAW,width=13.65,depth=17.65,height=3)],lights=B.lights,routes=routes,hotelSources=[],views={'bar':dict(eye=F.p(7.2,1.8,3),target=F.p(7,1.4,13))})
if __name__=='__main__':
 B=Meshes();meta=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(meta,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
