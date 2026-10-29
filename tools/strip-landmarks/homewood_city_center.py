"""Original mapped Homewood shell and photo-supported, fitted public reception."""
from common import *
KEY='homewood-city-center'; IDS=['way/494974482']
def build(B):
 p=footprint(IDS[0]);B.property=KEY+'-exterior';B.source='hotel/'+KEY;B.detail=0
 R=Frame(B,-811.15,1106,-math.pi/2,y=0)
 opening=dict(p=R.p(0,.24,0),yaw=R.yaw,width=9,height=3.6)
 door=dict(p=R.p(0,.24,0),yaw=R.yaw,width=2.4,height=2.9,name='Homewood reception',venue=KEY)
 B.shell(p,.02,21.5,'hw-ivory',roof=False,openings=[opening]);B.planar('hw-membrane',p,21.5)
 ring=list(p.exterior.coords)
 for a,b in zip(ring,ring[1:]):
  dx,dz=b[0]-a[0],b[1]-a[1];L=math.hypot(dx,dz);G=Frame(B,(a[0]+b[0])/2,(a[1]+b[1])/2,math.atan2(-dz,dx),y=0)
  G.box('hw-coping',(0,21.5,0),(L,.22,.34));G.box('hw-brown',(0,20.9,0),(L,.6,.14))
  if L<3:continue
  # Both exposed faces use shallow relief; no competing coplanar decals.
  for side in [-1,1]:
   
   x,_,z=G.p(0,2,0)
   if not(x>-815 and x<-808 and 1098<z<1115):G.box('hw-base',(0,2,side*.04),(L,3.95,.08))
   G.box('hw-brown',(0,4.15,side*.08),(L,.32,.18))
  n=max(1,int((L-.8)/3.45));positions=np.linspace(-L/2+1.65,L/2-1.65,n) if n>1 else [0]
  for j,u in enumerate(positions):
   u=float(u)
   for side in [-1,1]:
    # Pale grouped panel piers echo the broad projecting window stacks.
    if j%4 in (1,2):
     G.box('hw-panel',(u,12.5,side*.09),(3.35,16.3,.16))
     for y in np.arange(4.6,20.7,.81):G.box('hw-joint',(u,float(y),side*.18),(3.35,.022,.022))
    for y in [5.6,8.85,12.1,15.35,18.6]:
     d=.25 if j%4 in (1,2) else .10
     G.box('hw-trim',(u,y,side*d),(1.87,2.04,.10))
     G.box('hw-glass',(u,y+.03,side*(d+.07)),(1.68,1.83,.025))
     for off in [-.55,0,.55]:G.box('hw-curtain',(u+off,y+.03,side*(d+.09)),(.035,1.79,.012))
     G.box('hw-trim',(u,y+.03,side*(d+.12)),(.045,1.85,.02))
     G.box('hw-brown',(u,y-1.15,side*(d+.03)),(1.88,.30,.08))
    # Ground windows omitted where the physical lobby opening is cut.
    x,_,z=G.p(u,2,0)
    if not(x>-815 and x<-808 and 1100.8<z<1111.2):
     G.box('hw-trim',(u,2.0,side*.11),(2.0,2.5,.10));G.box('hw-glass',(u,2.0,side*.18),(1.8,2.28,.025))
  for y in [.6,1.5,2.4,3.3]:
   # Base horizontal mortar courses, clear of the entry opening.
   x,_,z=G.p(0,2,0)
   if not(x>-815 and x<-808 and 1098<z<1115):G.box('hw-joint',(0,y,.105),(L,.025,.025))
 # Photo-supported low entrance canopy inside the L, with stone supports.
 for u in [-4.65,4.65]:
  R.box('hw-stone',(u,2,-2.3),(.65,4,.7),True)
  for y in np.arange(.2,4,.18):R.box('hw-joint',(u,float(y),-2.66),(.65,.012,.015))
 R.box('hw-brown',(0,4.05,-1.4),(10.3,.48,4.2));R.box('hw-soffit',(0,3.8,-1.4),(10.0,.03,4.0))
 for u in [-3,0,3]:R.box('hw-lamp',(u,3.77,-2.0),(.18,.03,.18))
 for u in [-2.85,2.85]:R.box('hw-clear',(u,1.86,.03),(3.3,3.22,.035),True)
 for u in [-4.5,-1.2,1.2,4.5]:R.box('hw-trim',(u,1.86,.03),(.08,3.25,.12),True)
 R.box('hw-trim',(0,3.51,.03),(9,.10,.12))
 B.upface('hw-paving',[R.p(-1.5,.01,-5),R.p(1.5,.01,-5),R.p(1.5,.24,.3),R.p(-1.5,.24,.3)],True)
 S=Frame(B,-810.7,1107,math.pi/2,y=0)
 S.text('HOMEWOOD',(0,20.15,.35),.55,'hw-sign',back=True);S.text('SUITES',(0,19.57,.35),.48,'hw-sign',back=True)
 for u in [-6,6]:R.plant(u,-2.5)
 # Original service equipment on the flat roof, fitted to aerial positions.
 for x,z in [(-825,1084),(-806,1085),(-790,1085),(-772,1085),(-825,1110)]:
  Q=Frame(B,x,z,0,y=0);Q.box('hw-equipment',(0,22,0),(2.8,1,1.5));Q.box('hw-vent',(0,22.52,0),(2.4,.03,1.1))
 B.property=KEY+'-interior';B.source='interior/'+KEY;B.detail=1
 room=R.poly([(-4.5,.05),(4.5,.05),(4.5,11),(-4.5,11)])
 B.shell(room,.24,3.7,'hw-wall',roof=False,openings=[{k:v for k,v in opening.items() if k!='yaw'}]);B.planar('hw-floor',room,.24,True);B.planar('hw-soffit',room,3.7)
 for u in np.arange(-4.4,4.5,.26):R.box('hw-joint',(float(u),.244,5.5),(.008,.004,10.8))
 for v in np.arange(.3,11,1.4):
  for u in np.arange(-4.4,4.5,.52):R.box('hw-joint',(float(u),.244,float(v)),(.26,.004,.008))
 # Reception: dark framing, pale timber panels, white solid surface, lowered left desk.
 R.box('hw-darkwood',(-.5,1.0,8.4),(5.5,1.52,.95),True);R.box('hw-lightwood',(-.5,1.02,7.91),(4.9,1.04,.035))
 R.box('hw-counter',(-.5,1.79,8.4),(5.7,.09,1.08))
 R.box('hw-darkwood',(2.8,.76,8.1),(1.05,1.04,1.1),True);R.box('hw-lightwood',(2.8,.79,7.54),(.75,.65,.035));R.box('hw-counter',(2.8,1.32,8.1),(1.15,.08,1.2))
 R.box('hw-darkwood',(-.5,2.0,10.93),(6.7,3.3,.12))
 for u in [1.75,-.5,-2.75]:R.box('hw-lightwood',(u,2.0,10.85),(2.04,2.94,.04))
 for u in [1.2,-2.2]:
  R.box('hw-trim',(u,2.02,8.55),(.62,.38,.08));R.box('hw-trim',(u,1.86,8.55),(.08,.2,.1))
 for u in [1.6,-2.5]:
  R.tube('hw-trim',(u,3.0,8.2),(u,3.68,8.2),.015)
  R.lathe('hw-teal',u,8.2,[(2.83,0),(2.83,.25),(2.95,.23),(3.11,.10),(3.18,.10),(3.18,0)],24)
  R.lathe('hw-lamp',u,8.2,[(2.825,0),(2.825,.21),(2.83,.21)],24)
 # Photo-supported adjacent market fridge; original unbranded packages.
 R.box('hw-trim',(3.85,1.57,10.42),(.9,2.65,.08),True)
 for u in [3.42,4.28]:R.box('hw-trim',(u,1.57,9.9),(.06,2.65,1.1),True)
 for y in [.27,2.87]:R.box('hw-trim',(3.85,y,9.9),(.9,.06,1.1),True)
 R.box('hw-clear',(3.85,1.57,9.33),(.76,2.25,.025))
 for y in [.55,.95,1.35,1.75,2.15,2.55]:
  R.box('hw-trim',(3.85,y,9.85),(.78,.04,.65))
  for u in [4.08,3.86,3.64]:R.box('hw-teal',(u,y+.14,9.50),(.12,.24,.15))
 for u in [-3,0,3]:
  for v in [2,5]:R.box('hw-lamp',(u,3.68,v),(.16,.025,.16))
 routes=[dict(name='Court to reception',points=[R.p(0,.24,v) for v in [-12,-5,-1,1,4,6.5]]),dict(name='East frontage',points=[[-744,.1,z] for z in [1118,1100,1080,1066]])]
 return dict(key=KEY,name='Homewood Suites City Center',center=[-804,0,1104],bounds=list(p.bounds),structural=True,hotelSources=[],exteriorOnly=False,portals=[door],zones=[dict(origin=R.p(0,.24,0),yaw=R.yaw,width=9.2,depth=11.2,height=3.8)],lights=[dict(p=R.p(u,3.3,v),color=0xffefd8,power=4,range=7) for u,v in [(-2,3),(2,3),(-2,8),(2,8)]],routes=routes)
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
