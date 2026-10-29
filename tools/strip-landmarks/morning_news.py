"""Original Morning News facade and photographed dining finishes; fitted public plan."""
from common import *
KEY='morning-news';IDS=['way/905241567']
def build(B):
 p=footprint(IDS[0]);B.property=KEY+'-exterior';B.source='retail/'+KEY;B.detail=0
 R=Frame(B,-997,-3198.6,0,y=0)
 opening=dict(p=R.p(0,.22,0),yaw=0,width=9,height=3.25)
 door=dict(p=R.p(0,.22,0),yaw=0,width=2.4,height=2.8,name='Morning News public dining',venue=KEY)
 B.shell(p,.02,5.65,'mn-stucco',roof=False,openings=[opening]);B.planar('mn-membrane',p,5.65)
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  dx,dz=b[0]-a[0],b[1]-a[1];L=math.hypot(dx,dz);F=Frame(B,(a[0]+b[0])/2,(a[1]+b[1])/2,math.atan2(-dz,dx),y=0)
  F.box('mn-dark',(0,5.66,0),(L+.1,.18,.35));F.box('mn-dark',(0,4.18,0),(L,.16,.3))
  if F.z> -3197.8:
   F.box('mn-stone',(0,.63,0),(L,1.25,.19))
   F.box('mn-dark',(0,1.3,0),(L,.10,.25))
 # Northern entry bays: continuous clear storefront with genuinely open central portal.
 for u,w in [(-2.85,3.15),(2.85,3.15)]:
  B.face('mn-clear',[R.p(u-w/2,.225,0),R.p(u+w/2,.225,0),R.p(u+w/2,3.175,0),R.p(u-w/2,3.175,0)],True)
 for u in [-4.5,-1.2,1.2,4.5]:R.box('mn-frame',(u,1.72,-.03),(.085,3,.14),True)
 R.box('mn-frame',(0,3.22,-.03),(9.1,.08,.14))
 for u in [-5.1,5.1,-10.8]:
  R.box('mn-stone',(u,.76,-.13),(.85,1.1,.4),True);R.box('mn-dark',(u,1.35,-.16),(1,.10,.46))
  # Individually staggered sandstone pieces, original geometry and muted variation.
  for row in range(6):
   for col in range(3):
    x=u-.39+col*.27+(row%2)*.025
    R.box('mn-stone'+str((row*7+col*3)%4),(x,.32+row*.17,-.345),(.25,.155,.035))
 def awning(u,w):
  for a,b in zip(np.linspace(0,math.pi/2,13),np.linspace(0,math.pi/2,13)[1:]):
   pts=[R.p(u-w/2,3.26+.78*math.cos(a),-.12-.95*math.sin(a)),R.p(u+w/2,3.26+.78*math.cos(a),-.12-.95*math.sin(a)),R.p(u+w/2,3.26+.78*math.cos(b),-.12-.95*math.sin(b)),R.p(u-w/2,3.26+.78*math.cos(b),-.12-.95*math.sin(b))]
   B.face('mn-canvas',pts)
  R.box('mn-canvas',(u,3.18,-1.07),(w,.16,.035))
  for x in [u-w/2+.1,u+w/2-.1]:R.tube('mn-frame',(x,2.8,-.1),(x,3.24,-1.05),.025,8)
 for u,w in [(-2.85,3.1),(0,2.3),(2.85,3.1),(-8,3.2)]:awning(u,w)
 R.box('mn-glass',(-8,1.95,-.10),(3,2.35,.055))
 for u in [-9.52,-8,-6.48]:R.box('mn-frame',(u,1.95,-.15),(.065,2.47,.08))
 for y in [.73,3.17]:R.box('mn-frame',(-8,y,-.15),(3.1,.065,.08))
 R.text('Morning News',(0,4.92,-.13),.67,'mn-blue');R.text('3154',(0,3.04,-.14),.17,'mn-letter')
 R.box('mn-paving',(0,.11,-.8),(10,.22,1.6),True)
 B.upface('mn-paving',[R.p(-1.4,.01,-3),R.p(1.4,.01,-3),R.p(1.4,.22,-1.5),R.p(-1.4,.22,-1.5)],True)
 for lo,hi in [(-5,-1.5),(1.5,5)]:
  for u in np.linspace(lo,hi,7):R.tube('mn-frame',(float(u),.22,-1.5),(float(u),1.18,-1.5),.023,6)
  R.tube('mn-frame',(lo,1.18,-1.5),(hi,1.18,-1.5),.035,8)
 for u in [-8,-3,2]:
  R.box('mn-equipment',(u,6,4.5),(1.6,.7,1.3))
  for v in np.arange(4,5.05,.17):R.box('mn-frame',(u,6.36,float(v)),(1.3,.025,.04))
 # Fitted public room; private kitchen and unreferenced back-of-house deliberately excluded.
 B.property=KEY+'-interior';B.source='interior/'+KEY;B.detail=1
 room=R.poly([(-4.5,.06),(4.5,.06),(4.5,8.5),(-4.5,8.5)])
 B.shell(room,.22,3.42,'mn-wall',roof=False,openings=[dict(p=R.p(0,.22,.06),width=9,height=3.0)])
 B.planar('mn-wood',room,.22,True);B.planar('mn-ceiling',room,3.42)
 # Herringbone is authored in world metres and clipped to the dining footprint.
 for i in range(-12,13):
  for j in range(-40,41):
   x=i*.8-j*.2;z=i*.8+j*.2
   for flip in [0,1]:
    q=box(x+.007,z+.007,x+.793,z+.193) if not flip else box(x+.807,z+.007,x+.993,z+.793)
    q=translate(rotate(q,45,origin=(0,0)),xoff=-997,yoff=-3194.4).intersection(room)
    if not q.is_empty:B.planar('mn-wood'+str((i*3+j+flip)%4),q,.23)
 for u in np.arange(-4.45,4.46,.12):R.box('mn-flute',(float(u),.91,8.44),(.065,1.35,.055))
 for v in np.arange(.15,8.46,.12):R.box('mn-flute',(4.44,.91,float(v)),(.055,1.35,.065))
 for v in np.arange(.2,8.5,.2):R.box('mn-wood',(4.43,2.77,float(v)),(.06,.85,.07))
 for u in np.arange(-4.4,4.5,.2):R.box('mn-wood',(float(u),2.77,8.43),(.07,.85,.06))
 R.box('mn-yellow',(3.93,.62,4.7),(.94,.34,6.8),True);R.box('mn-yellow',(4.29,1.05,4.7),(.18,.82,6.8))
 R.box('mn-yellow',(0,.62,7.99),(7.8,.34,.9),True);R.box('mn-yellow',(0,1.05,8.34),(7.8,.82,.18))
 def chair(u,v,back=1,yaw=0):
  c=R.p(u,0,v);F=Frame(B,c[0],c[2],yaw,y=0);u=v=0
  for x in [-.22,.22]:
   for z in [-.22,.22]:F.tube('mn-brown',(u+x,.23,v+z),(u+x*.85,.7,v+z*.85),.025,8)
  F.box('mn-woven',(u,.72,v),(.5,.08,.47))
  for x in [-.23,.23]:F.tube('mn-brown',(u+x,.68,v+back*.21),(u+x,1.24,v+back*.24),.025,8)
  F.tube('mn-brown',(u-.23,1.24,v+back*.24),(u+.23,1.24,v+back*.24),.028,8)
  for y in np.arange(.85,1.22,.07):F.box('mn-woven',(u,float(y),v+back*.23),(.44,.035,.03))
  for x in np.arange(-.20,.21,.05):F.box('mn-woven',(float(x),1.02,back*.245),(.018,.38,.018))
 def table(u,v):
  R.box('mn-frame',(u,.27,v),(.55,.1,.55));R.box('mn-frame',(u,.64,v),(.08,.74,.08))
  R.box('mn-table',(u,1.02,v),(1.15,.065,.78),True)
 for v in [2.3,4.7,7]:
  table(2.85,v);chair(1.88,v,yaw=-math.pi/2)
 for v in [2.6,5.2]:
  table(-2.7,v);chair(-2.7,v-.8,1);chair(-2.7,v+.8,-1)
 # Small welcome counter and original nonrepresentational artwork.
 R.box('mn-counter',(-3.4,.77,.8),(1.7,1.1,.65),True);R.box('mn-table',(-3.4,1.34,.8),(1.8,.06,.75))
 for u in [-2,0,2]:
  R.box('mn-brown',(u,2.18,8.39),(1.1,.85,.05));R.box('mn-art',(u,2.18,8.35),(.98,.73,.025))
  R.box('mn-blue',(u-.2,2.22,8.33),(.12,.4,.015));R.box('mn-yellow',(u+.12,2.08,8.32),(.35,.12,.015))
 for u in np.arange(-4.5,4.51,.6):R.box('mn-grid',(float(u),3.4,4.25),(.025,.02,8.4))
 for v in np.arange(.1,8.51,.6):R.box('mn-grid',(0,3.4,float(v)),(9,.02,.025))
 for u in [-2,2]:
  for v in [2,6.7]:R.lathe('mn-lamp',u,v,[(3.38,0),(3.38,.15),(3.40,.15),(3.40,0)],16)
 for v in [3,6]:
  R.tube('mn-ceiling',(0,3.4,v),(0,3.03,v),.035,8)
  R.lathe('mn-ceiling',0,v,[(2.98,0),(2.98,.14),(3.1,.14),(3.1,0)],16)
  for a in [0,math.tau/3,2*math.tau/3]:
   F=Frame(B,*[R.p(0,0,v)[i] for i in [0,2]],a,y=0);F.box('mn-ceiling',(.35,3.06,0),(.7,.035,.15))
 routes=[dict(name='Public dining entry and return',points=[R.p(0,.22,v) for v in [-4,-2,0,2,4,6.8]]),dict(name='North frontage',points=[[-1011,.24,-3203],[-1004,.24,-3203],[-997,.24,-3203],[-989,.24,-3203]])]
 return dict(key=KEY,name='Morning News Sahara',center=[-999,0,-3193],bounds=list(p.bounds),structural=True,hotelSources=[],exteriorOnly=False,portals=[door],zones=[dict(origin=R.p(0,.22,0),yaw=0,width=9.1,depth=8.6,height=3.5)],lights=[dict(p=R.p(u,3.05,v),color=0xffefcf,power=3,range=6) for u,v in [(-2,2),(2,2),(-2,6.7),(2,6.7)]],routes=routes)
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
