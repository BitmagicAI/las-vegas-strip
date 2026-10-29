"""Original address-referenced shop; fitted public layout, no copied packaging."""
from common import *
KEY='vape-pirates-sahara';IDS=['way/943068961']
def build(B):
 p=footprint(IDS[0]);B.property=KEY+'-exterior';B.source='retail/'+KEY;B.detail=0
 R=Frame(B,-886.4,-3118.66,0,y=0)
 door=dict(p=R.p(1,.14,0),yaw=0,width=1.6,height=2.6,name='Vape Pirates public shop',venue=KEY)
 banks=[(-5.9,2),(-3.55,2),(-1.25,1.9),(3.45,2.05),(5.8,1.95)]
 B.shell(p,0,4.1,'vp-stucco',roof=False,openings=[dict(p=R.p(u,.14,0),width=w,height=2.55) for u,w in banks+[(1,1.6)]])
 B.planar('vp-membrane',p,4.12)
 # Tall ribbed parapet at the front; returned coping on all mapped roof edges.
 R.box('vp-parapet',(0,4.6,.06),(14.5,1.2,.24),True)
 for u in np.arange(-7.2,7.21,.18):R.box('vp-rib',(float(u),4.6,-.08),(.035,1.2,.045))
 R.box('vp-coping',(0,5.23,.03),(14.6,.08,.31))
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):B.tube('vp-coping',(a[0],4.18,a[1]),(b[0],4.18,b[1]),.075,6)
 R.text('VAPE PIRATES',(0,3.15,-.18),.95,'vp-dark')
 # Glazed frontage with horizontal security bars; doorway stays clear.
 for u,w in banks:
  B.face('vp-clear',[R.p(u-w/2,.18,-.02),R.p(u+w/2,.18,-.02),R.p(u+w/2,2.83,-.02),R.p(u-w/2,2.83,-.02)],True)
  for du in [-w/2,w/2]:R.box('vp-alloy',(u+du,1.5,-.12),(.07,2.7,.14),True)
  for y in np.arange(.3,2.8,.19):R.box('vp-bars',(u,float(y),-.22),(w,.045,.055))
  for y in [.17,2.85]:R.box('vp-alloy',(u,y,-.12),(w+.08,.08,.14))
 for u in [-7,-4.74,-2.4,-.15,2.2,4.62,6.94]:R.box('vp-stucco',(u,1.48,.03),(.28,2.96,.18),True)
 R.box('vp-coping',(-3.5,.1,-.07),(7.0,.2,.18),True);R.box('vp-coping',(4.6,.1,-.07),(5.5,.2,.18),True)
 # Remove sill at entry by using side pieces instead of crossing door.
 # Explicit approach deck and ramp stand above existing terrain without altering roads.
 R.box('vp-paving',(1,.07,-.8),(2.2,.14,1.6),True)
 B.upface('vp-paving',[R.p(.05,.14,-1.6),R.p(1.95,.14,-1.6),R.p(1.95,0,-3.2),R.p(.05,0,-3.2)],True)
 for u in [-6,-3,4.5,7]:R.box('vp-concrete',(u,.24,-2.1),(.45,.48,.5),True)
 for u in [-4.5,0,4.5]:
  R.box('vp-dark',(u,3.97,-.23),(.48,.18,.3));R.box('vp-lamp',(u,3.88,-.29),(.38,.025,.24))
 for u in [-6.1,6]:R.box('vp-dark',(u,3.4,-.17),(1.5,.38,.07));R.text('SHOP',(u,3.29,-.22),.18,'vp-white')
 for x,z in [(-890,-3106),(-882,-3102)]:
  F=Frame(B,x,z,0,y=0);F.box('vp-service',(0,4.65,0),(2,1,1.6));F.box('vp-coping',(0,5.18,0),(2.1,.08,1.7))
  for y in np.arange(4.3,5.1,.12):F.box('vp-bars',(0,float(y),-.81),(1.7,.04,.04))
 E=Frame(B,-876.91,-3105,-math.pi/2,y=0)
 E.box('vp-service',(0,1.4,-.1),(1.1,2.6,.08));E.box('vp-dark',(0,2.8,-.14),(1.2,.08,.15))
 for u in [-3,3]:E.box('vp-service',(u,1.5,-.12),(.65,.9,.18))
 # Public room; original pale tile and black cabinets based on dated photographs.
 B.property=KEY+'-interior';B.source='interior/'+KEY;B.detail=1
 room=R.poly([(-6.65,.25),(6.65,.25),(6.65,14.6),(-6.65,14.6)])
 assert p.buffer(.03).covers(room)
 B.shell(room,.14,3.18,'vp-wall',roof=False,openings=[dict(p=R.p(u,.14,.25),width=w,height=2.55)for u,w in banks+[(1,1.6)]])
 B.planar('vp-tile',room,.14,True);B.planar('vp-ceiling',room,3.18)
 for u in np.arange(-6.6,6.7,.7):R.box('vp-grout',(float(u),.143,7.4),(.013,.004,14.3))
 for v in np.arange(.3,14.7,.7):R.box('vp-grout',(0,.143,float(v)),(13.3,.004,.013))
 for u in [-4,0,4]:
  for v in [2,6,10,13]:R.lathe('vp-lamp',u,v,[(3.14,0),(3.14,.12),(3.16,.12),(3.16,0)],12)
 for u in [-3.5,3.5]:
  R.box('vp-white',(u,3.14,7),(1.1,.05,1.1))
  for dv in np.arange(-.4,.41,.12):R.box('vp-bars',(u,3.10,7+float(dv)),(.8,.02,.035))
 colors=['vp-packred','vp-packblue','vp-packgreen','vp-packgold','vp-white']
 def rack(F,w):
  F.box('vp-dark',(0,1.43,0),(w,2.55,.4),True)
  for y in [.35,.78,1.21,1.64,2.07,2.5]:
   F.box('vp-rack',(0,y,-.26),(w,.045,.6))
   for j,u in enumerate(np.arange(-w/2+.16,w/2-.1,.23)):
    h=.21+.06*(j%3);F.box(colors[(j+int(y*10))%5],(float(u),y+h/2+.03,-.28),(.16,h,.19))
    F.box('vp-white',(float(u),y+h*.55,-.381),(.11,.035,.012))
 rack(Frame(B,*[R.p(0,0,14.2)[k]for k in [0,2]],0,y=.14),12.5)
 for u,yaw in [(-6.3,-math.pi/2),(6.3,math.pi/2)]:
  rack(Frame(B,*[R.p(u,0,8)[k]for k in [0,2]],yaw,y=.14),10.5)
 def counter(u,v,w,d):
  R.box('vp-dark',(u,.55,v),(w,.82,d),True)
  for z in [-d/2,d/2]:R.box('vp-alloy',(u,1.39,v+z),(w,.045,.045))
  # Single glass faces avoid overlapping transparent box surfaces.
  for z in [-d/2,d/2]:B.face('vp-clear',[R.p(u-w/2,.95,v+z),R.p(u+w/2,.95,v+z),R.p(u+w/2,1.35,v+z),R.p(u-w/2,1.35,v+z)],True)
  B.upface('vp-clear',[R.p(u-w/2,1.42,v-d/2),R.p(u+w/2,1.42,v-d/2),R.p(u+w/2,1.42,v+d/2),R.p(u-w/2,1.42,v+d/2)])
  R.box('vp-lamp',(u,1.29,v),(w-.1,.025,.06))
  for x in [-w/2+.05,w/2-.05]:
   for z in [-d/2,d/2]:R.box('vp-alloy',(u+x,1.18,v+z),(.035,.48,.035))
   R.box('vp-alloy',(u+x,1.39,v),(.035,.045,d))
   B.face('vp-clear',[R.p(u+x,.95,v-d/2),R.p(u+x,.95,v+d/2),R.p(u+x,1.35,v+d/2),R.p(u+x,1.35,v-d/2)],True)
  for j,x in enumerate(np.arange(-w/2+.16,w/2-.12,.3)):
   R.box(colors[j%5],(u+float(x),1.1,v),(.2,.24,min(.25,d*.6)))
 counter(-2.5,7,2.4,5);counter(5.1,7,1.2,9);counter(-5.1,7,1.2,9);counter(0,13,10.8,.8)
 R.box('vp-dark',(-2.5,1.6,7),(1.4,.4,.32));R.box('vp-screen',(-2.5,1.63,6.82),(1.2,.25,.03))
 routes=[dict(name='Entry and central public aisle',points=[R.p(1,y,v)for y,v in [(0,-4),(0,-3.2),(.14,-1),(.14,0),(.14,3),(.14,7),(.14,11.7)]]),dict(name='Cross aisle to display',points=[R.p(u,.14,11.8)for u in [1,-2,-4]])]
 return dict(key=KEY,name='Vape Pirates Sahara',center=[-885,0,-3109],bounds=list(p.bounds),structural=True,hotelSources=[],exteriorOnly=False,portals=[door],zones=[dict(origin=R.p(0,.14,.2),yaw=0,width=13.4,depth=14.5,height=3.2)],lights=[dict(p=R.p(u,2.8,v),color=0xf2f3eb,power=3,range=8)for u,v in [(-3,3),(3,3),(-3,10),(3,10)]],routes=routes)
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces'])for g in B.groups.values()),'triangles')
