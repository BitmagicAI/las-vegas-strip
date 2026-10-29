"""Original photo-fitted Mi Ranchito exterior/public dining; private kitchen excluded."""
from common import *
KEY='mi-ranchito-sahara';IDS=['way/943068962']
def build(B):
 p=footprint(IDS[0]);B.property=KEY+'-exterior';B.source='retail/'+KEY;B.detail=0
 R=Frame(B,-842.16,-3117.5,-math.pi/2,y=0)
 door=dict(p=R.p(0,.15,0),yaw=-math.pi/2,width=1.9,height=2.5,name='Mi Ranchito public dining',venue=KEY)
 B.shell(p,0,3.4,'mr-ochre',roof=False,openings=[dict(p=R.p(0,.15,0),width=2.1,height=2.65)])
 # Blue hip roof, narrow raised membrane spine; south service pad remains flat.
 x0,x1=-854,-841.7;z0,z1=-3128.9,-3109.1;ix0,ix1=-849.1,-847;iz0,iz1=-3125.6,-3112.3
 low=[(x0,3.45,z0),(x1,3.45,z0),(x1,3.45,z1),(x0,3.45,z1)]
 high=[(ix0,5.0,iz0),(ix1,5.0,iz0),(ix1,5.0,iz1),(ix0,5.0,iz1)]
 for i in range(4):
  j=(i+1)%4;B.upface('mr-blue',[low[i],low[j],high[j],high[i]])
  B.tube('mr-red',low[i],low[j],.09,8)
  # Original low-profile standing seams, interpolated across each roof plane.
  for t in np.arange(.025,.99,.035):
   a=tuple(low[i][k]*(1-t)+low[j][k]*t for k in range(3));b=tuple(high[i][k]*(1-t)+high[j][k]*t for k in range(3));a=(a[0],a[1]+.025,a[2]);b=(b[0],b[1]+.025,b[2]);B.tube('mr-seam',a,b,.015,5)
 B.upface('mr-membrane',high);B.planar('mr-membrane',p.intersection(box(-855,-3109.1,-841,-3105)),3.43)
 # East entrance portico matches owner photograph: stone piers and red-edged gable.
 for u in [-1.65,1.65]:
  R.box('mr-stone',(u,1.6,-.2),(.85,3.2,.45),True)
  for y in np.arange(.2,3.15,.24):
   for j in range(3):R.box('mr-stone'+str((j+int(y*10))%3),(u-.27+j*.27,float(y),-.445),(.25,.21,.025))
 for a,b in [((-2.7,3.45,-.8),(0,4.65,-.8)),((0,4.65,-.8),(2.7,3.45,-.8))]:R.tube('mr-red',a,b,.11,8)
 for u in [-2.7,2.7]:B.upface('mr-blue',[R.p(u,3.45,-.8),R.p(0,4.65,-.8),R.p(0,4.65,1.2),R.p(u,3.45,1.2)])
 B.face('mr-ochre',[R.p(-2.7,3.42,-.7),R.p(2.7,3.42,-.7),R.p(0,4.62,-.7)],True)
 R.box('mr-dark',(0,3.25,-.49),(2.4,.15,.1));R.box('mr-red',(0,4.55,-.87),(4.5,.65,.10));R.text('ENTRANCE',(0,4.32,-.94),.58,'mr-white');R.text('OPEN',(0,4.99,-.94),.83,'mr-red')
 for u in [-1.08,1.08]:R.box('mr-mullion',(u,1.45,-.08),(.09,2.7,.12),True)
 R.box('mr-mullion',(0,2.76,-.08),(2.25,.1,.12))
 R.box('mr-paving',(0,.075,-1.7),(5.5,.15,3.4),True)
 B.upface('mr-paving',[R.p(-1.3,.15,-3.4),R.p(1.3,.15,-3.4),R.p(1.3,0,-5),R.p(-1.3,0,-5)],True)
 for u in [-2.3,2.3]:
  R.lathe('mr-alloy',u,-1.4,[(.15,.4),(.85,.4),(.87,0)],20)
  for y in [.3,.66]:R.lathe('mr-white',u,-1.4,[(y,.41),(y+.025,.41)],20)
  R.lathe('mr-leaf',u,-1.4,[(.8,.16),(1.0,.34),(1.35,.25),(1.65,0)],9)
 # Window group and small red-fenced east patio; service ends simplified.
 for u in [-7,-4,5,8]:
  R.box('mr-dark',(u,1.8,-.24),(1.8,1.65,.07))
  for du in [-.92,.92]:R.box('mr-mullion',(u+du,1.8,-.30),(.07,1.78,.1))
  for y in [.95,2.65]:R.box('mr-mullion',(u,y,-.30),(1.9,.07,.1))
 R.box('mr-paving',(7,.06,-1.6),(5.4,.12,3.2),True)
 for u in np.arange(4.3,9.7,.27):R.box('mr-red',(float(u),.68,-3.2),(.12,1.25,.12))
 for y in [.25,1.15]:R.box('mr-red',(7,y,-3.2),(5.4,.09,.12),True)
 N=Frame(B,-847.7,-3128.61,0,y=0)
 N.box('mr-ochre',(0,4.6,0),(7.8,2.35,.25));N.text('MI RANCHITO',(0,4.93,-.16),.64,'mr-blue');N.text('MEXICAN FOOD',(0,4.3,-.16),.48,'mr-red')
 F=Frame(B,-848,-3107,0,y=0);F.box('mr-service',(0,3.9,0),(2.4,.9,1.6));F.box('mr-alloy',(0,4.4,0),(2.5,.1,1.7))
 for x in [-850,-845]:Frame(B,x,-3105.55,math.pi,y=0).box('mr-service',(0,1.1,-.08),(.65,1,.16))
 # Public interior: measured footprint, inferred room layout, reference-supported finishes.
 B.property=KEY+'-interior';B.source='interior/'+KEY;B.detail=1
 room=R.poly([(-9.6,.3),(7.7,.3),(7.7,10.4),(-9.6,10.4)])
 assert p.buffer(.05).covers(room)
 B.shell(room,.15,3.18,'mr-yellow',roof=False,openings=[dict(p=R.p(0,.15,.3),width=2.1,height=2.6)])
 B.planar('mr-tile',room,.15,True);B.planar('mr-ceiling',room,3.18)
 R.box('mr-inblue',(-9.55,1.67,5.3),(.04,3,10))
 for u in np.arange(-9.5,7.7,.65):R.box('mr-grout',(float(u),.154,5.35),(.014,.004,10.1))
 for v in np.arange(.35,10.4,.65):R.box('mr-grout',(-.95,.154,float(v)),(17.3,.004,.014))
 for u in [-7,-3,1,5]:
  for v in [2.5,6.5]:R.box('mr-lamp',(u,3.15,v),(.65,.025,.65))
 # Rows of colorful wooden high-back chairs; original abstract cactus/sun motifs.
 colors=['mr-green','mr-red','mr-inblue','mr-orange']
 for col,u in enumerate([-7,-4,3.5,6.3]):
  for row,v in enumerate([2.6,5.5]):
   R.box('mr-table',(u,.93,v),(1.65,.09,1.15),True)
   R.box('mr-orange',(u,.981,v),(1.46,.012,.95))
   for dx in [-.65,.65]:R.box('mr-inblue',(u+dx,.99,v),(.045,.006,.86))
   for dz in [-.39,.39]:R.box('mr-green',(u,.99,v+dz),(1.3,.006,.045))
   B.upface('mr-yellow',[R.p(u+.28*math.cos(a),.991,v+.28*math.sin(a)) for a in np.linspace(0,math.tau,17)])
   for du in [-.62,.62]:
    for dv in [-.4,.4]:R.box('mr-dark',(u+du,.55,v+dv),(.07,.75,.07))
   for du,dv,side in [(-.43,-.95,-1),(.43,-.95,-1),(-.43,.95,1),(.43,.95,1)]:
    C=Frame(B,*[R.p(u+du,0,v+dv)[k] for k in [0,2]],-math.pi/2+(math.pi if side<0 else 0),y=0)
    mat=colors[(col+row)%4]
    C.box('mr-seat',(0,.62,0),(.55,.14,.52),True)
    for dx in [-.24,.24]:
     for dz in [-.22,.22]:C.box(mat,(dx,.39,dz),(.065,.48,.065))
     C.box(mat,(dx,.94,.24),(.07,1.12,.08))
    # Smooth scalloped silhouette, separately outlined original painted panel.
    top=[(-.26,1.39),(-.20,1.42),(-.14,1.40),(-.07,1.46),(0,1.48),(.07,1.46),(.14,1.40),(.20,1.42),(.26,1.39)]
    outline=[(-.26,.7),(.26,.7)]+list(reversed(top))
    for face in [.19,.29]:
     B.face(mat,[C.p(x,y,face) for x,y in outline],True)
     C.box('mr-yellow',(0,1.06,face-.012 if face<.2 else face+.012),(.43,.64,.015))
     q=face-.025 if face<.2 else face+.025
     # Stylized cactus with raised arms and original sun, not traced art.
     C.tube('mr-green',(0,.83,q),(0,1.21,q),.026,7)
     for xx,yy in [(-.10,1.02),(.10,1.10)]:
      C.tube('mr-green',(0,yy,q),(xx,yy,q),.022,7);C.tube('mr-green',(xx,yy,q),(xx,yy+.11,q),.022,7)
     B.face('mr-orange',[C.p(.12+.045*math.cos(a),1.28+.045*math.sin(a),q) for a in np.linspace(0,math.tau,13)],True)
   R.box('mr-dark',(u,1.04,v),(.28,.12,.22))
 # Rear public service boundary with arched dark trim and screens; kitchen excluded.
 R.box('mr-service',(-.9,.75,9.65),(16.7,1.2,.65),True)
 for u in [-6,-1,4.5]:
  R.box('mr-dark',(u,2,10.31),(2.1,1.5,.08))
  for a,b in zip(np.linspace(0,math.pi,21),np.linspace(0,math.pi,21)[1:]):R.tube('mr-dark',(u+1.1*math.cos(a),2.3+1.1*math.sin(a)*.65,10.24),(u+1.1*math.cos(b),2.3+1.1*math.sin(b)*.65,10.24),.08,6)
  R.box('mr-dark',(u,2.85,9.95),(2,.75,.1));R.box('mr-screen',(u,2.85,9.88),(1.87,.62,.02))
  for y in [2.65,2.8,2.95]:R.box('mr-white',(u+.3,y,9.86),(.9,.025,.015))
 routes=[dict(name='Entry to dining aisle',points=[R.p(0,y,v) for y,v in [(0,-5.5),(0,-5),(.15,-3),(.15,0),(.15,2),(.15,6),(.15,8.4)]]),dict(name='Public dining cross aisle',points=[R.p(u,.15,8.3) for u in [0,-4,-8]])]
 return dict(key=KEY,name='Mi Ranchito Sahara',center=[-848,0,-3117],bounds=list(p.bounds),structural=True,hotelSources=[],exteriorOnly=False,portals=[door],zones=[dict(origin=R.p(-.95,.15,.25),yaw=-math.pi/2,width=17.4,depth=10.2,height=3.2)],lights=[dict(p=R.p(u,2.8,v),color=0xffedca,power=3,range=7) for u,v in [(-5,3),(4,3),(-5,7),(4,7)]],routes=routes)
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
