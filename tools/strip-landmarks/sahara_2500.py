"""Original 2500 West Sahara office exterior; unseen bays and dimensions inferred."""
from common import *
from shapely.geometry.polygon import orient
KEY='sahara-2500'
def build(B):
 B.property=KEY+'-exterior';B.source='office/'+KEY;B.detail=0
 p=orient(footprint('way/1018431817'),sign=1)
 S=Frame(B,-256.8,-3279.2,math.pi-.008,y=0);W=Frame(B,-271.9,-3299,math.pi/2-.008,y=0);N=Frame(B,-256.6,-3318.5,-.008,y=0);E=Frame(B,-241.5,-3298.7,-math.pi/2-.008,y=0)
 bays=[];cuts=[]
 for side,R in enumerate([S,W,N,E]):
  us=[-10,-5,1,7,12]if side in [0,2]else[-15,-9,-3,3,9,15]
  for u in us:
   for y,h in [(.55,2.9),(5.1,2.05)]:
    door=side==0 and u==-5 and y<1;yy=0 if door else y;hh=3.3 if door else h;w=2.5 if side in[0,2]else 2.2
    cuts.append(dict(p=R.p(u,yy,0),yaw=R.yaw,width=w,height=hh));bays.append((R,u,yy,w,hh,door))
 B.shell(p,0,8.7,'s25-stucco',openings=cuts,roof=False);B.planar('s25-membrane',p,8.55)
 for R,u,y,w,h,door in bays:
  R.box('s25-glass',(u,y+h/2,.2),(w,h,.035),True)
  for du in [-w/2,0,w/2]:R.box('s25-green',(u+du,y+h/2,.13),(.055,h+.05,.08))
  for yy in [y,y+h*.45,y+h]:R.box('s25-green',(u,yy,.13),(w,.055,.08))
  for du in [-w/2,w/2]:R.box('s25-reveal',(u+du,y+h/2,.04),(.1,h+.3,.5))
  for yy in [y-.12,y+h+.1]:R.box('s25-reveal',(u,yy,.04),(w+.1,.12,.5))
  if not door:
   for yy in np.arange(y+.12,y+h-.1,.14):R.box('s25-blind',(u,float(yy),.24),(w-.1,.045,.025))
  else:
   for du in [-.12,.12]:R.tube('s25-alloy',(u+du,1.1,.05),(u+du,1.6,.05),.025,8)
 # Horizontal panel joints on solid piers and the band above the ground-floor glass.
 for side,R in enumerate([S,W,N,E]):
  length=30.3 if side in[0,2]else 39.2
  for yy in [3.7,4.1,4.5]:R.box('s25-joint',(0,yy,-.035),(length,.012,.025))
  us=[-12.5,-7.5,-2,4,9.5,14]if side in[0,2]else[-17.5,-12,-6,0,6,12,17.5]
  for u in us:
   for yy in [.5,1.1,1.7,2.3,2.9,3.5]:R.box('s25-joint',(u,yy,-.035),(1.5,.012,.025))
  for yy in [4.65,8.73]:R.box('s25-coping',(0,yy,-.03),(length+.08,.1,.22))
 # Taller western part of the stepped front parapet, as in Street View.
 S.box('s25-stucco',(4.8,9,-.03),(20.7,.6,.24));S.box('s25-coping',(4.8,9.34,-.03),(20.85,.12,.35))
 S.text('2500',(-9,7.4,-.2),.95,'s25-green')
 # Square-column southeast portico with open side access and protected door.
 S.box('s25-stucco',(-9,4.2,-1.65),(12,.9,3.3),True);S.box('s25-coping',(-9,4.7,-1.65),(12.2,.12,3.5))
 for u in [-14.4,-8.6,-3.6]:
  S.box('s25-column',(u,1.9,-3),(.65,3.8,.65),True)
  for yy in [.6,1.2,1.8,2.4,3]:S.box('s25-joint',(u,yy,-3.335),(.65,.012,.02))
 for yy in [3.85,4.12,4.4]:S.box('s25-joint',(-9,yy,-3.315),(12,.012,.02))
 S.box('s25-paving',(-9,.075,-1.6),(12.5,.15,3.4),True)
 B.upface('s25-paving',[S.p(-6.4,0,-4.5),S.p(-3.6,0,-4.5),S.p(-3.6,.15,-2.7),S.p(-6.4,.15,-2.7)],True)
 # Discrete surface fixtures and local beds, not changes to city pavement.
 for u in [-12,-2]:
  S.box('s25-lampbox',(u,3.2,-.18),(.18,.38,.26));S.box('s25-lamp',(u,3.18,-.32),(.12,.22,.025))
 for u in [0,5,10,14]:
  S.box('s25-gravel',(u,.025,-1.3),(2.8,.05,2.4))
  for j in range(5):B.sphere('s25-leaf',S.p(u+.3*math.cos(j*2),.45,-1.3+.3*math.sin(j*2)),.35,10,6)
 # Utility/HVAC array follows roof aerial; exact equipment models remain approximate.
 for x,z in [(-263,-3288),(-250,-3288),(-263,-3303),(-250,-3303),(-257,-3311)]:
  B.box('s25-curb',(x,8.75,z),(2.3,.35,1.8));B.box('s25-equipment',(x,9.25,z),(2,.7,1.5))
  for dx in [-.5,.5]:B.lathe('s25-dark',(x+dx,z),[(9.61,.36),(9.65,.36)],16)
  for dz in np.arange(-.6,.61,.15):B.box('s25-alloy',(x+1.02,9.25,z+float(dz)),(.025,.4,.04))
 W.box('s25-service',(-15,1.2,.03),(1.1,2.4,.09),True);W.box('s25-alloy',(-14.6,1.1,-.04),(.13,.04,.06))
 routes=[dict(name='Corner entrance approach',points=[S.p(-5,y,v)for v,y in [(-7,0),(-4.5,0),(-2.7,.15),(-1.5,.15),(-.7,.15)]]),dict(name='West public approach',points=[[x,0,-3294]for x in [-285,-281,-277,-274]])]
 return dict(key=KEY,name='2500 West Sahara offices',center=[-256,0,-3299],bounds=list(p.buffer(8).bounds),structural=True,hotelSources=[],exteriorOnly=True,portals=[],zones=[],lights=[],routes=routes)
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces'])for g in B.groups.values()),'triangles')
