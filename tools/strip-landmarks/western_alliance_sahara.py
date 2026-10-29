"""Original Western Alliance Sahara exterior; photo-fitted height and massing."""
from common import *
from shapely.geometry.polygon import orient
KEY='western-alliance-sahara';IDS=['way/1414999317','way/1414999318']
def build(B):
 p=footprint(IDS[0]);can=footprint(IDS[1]);R=Frame(B,-464,-3225,math.pi/4,y=0)
 B.property=KEY+'-exterior';B.source='office/'+KEY;B.detail=0
 core=orient(p.intersection(R.poly([(-10,-30),(30,-30),(30,30),(-10,30)])),sign=1.0)
 low=p.difference(core);entry=R.poly([(-28,0),(-10,0),(-10,8),(-28,8)])
 B.shell(core,.02,21.8,'wa-stucco',roof=False);B.planar('wa-membrane',core,21.8)
 B.shell(low.difference(entry),.02,6.2,'wa-stucco',roof=False)
 # Low west roof follows the footprint with a pitched tile surface, leaving the public canopy open.
 def uv(x,z):return ((x+464-(z+3225))/math.sqrt(2),(x+464+(z+3225))/math.sqrt(2))
 def roofy(x,z):
  u,v=uv(x,z);return 6.8+max(0,min(1,(u+25)/15))*4.4
 for q in parts(low):
  for tri in triangles(q):B.upface('wa-tilebase',[(x,roofy(x,z),z) for x,z in list(tri.exterior.coords)[:-1]])
  for a,b in zip(list(q.exterior.coords),list(q.exterior.coords)[1:]):
   B.face('wa-stucco',[(a[0],6.2,a[1]),(b[0],6.2,b[1]),(b[0],roofy(*b),b[1]),(a[0],roofy(*a),a[1])])
 # Individually varied original clay tiles, clipped to the irregular roof.
 for u in np.arange(-27,-9,.36):
  for v in np.arange(-25,26,.46):
   tile=R.poly([(u,v),(u+.35,v),(u+.35,v+.45),(u,v+.45)]).intersection(low)
   if tile.is_empty:continue
   for q in parts(tile):
    for tri in triangles(q):B.upface('wa-tile'+str((int(u*10)+int(v*10))%4),[(x,roofy(x,z)+.035,z) for x,z in list(tri.exterior.coords)[:-1]])
 # Main office glazing rows and projecting piers follow every edge, not a rectangular replacement.
 for a,b in zip(list(core.exterior.coords),list(core.exterior.coords)[1:]):
  dx,dz=b[0]-a[0],b[1]-a[1];L=math.hypot(dx,dz)
  if L<1.3:continue
  F=Frame(B,(a[0]+b[0])/2,(a[1]+b[1])/2,math.atan2(-dz,dx),y=0)
  F.box('wa-cap',(0,21.9,0),(L+.05,.25,.3))
  ua,va=uv(*a);ub,vb=uv(*b)
  if abs(ua+10)<.01 and abs(ub+10)<.01:continue
  if (va+vb)/2>20:
   if L>3:
    F.box('wa-glass',(0,10.4,-.1),(min(1.5,L*.3),18,.08))
    for yy in np.arange(1.5,19.6,1.9):F.box('wa-mullion',(0,float(yy),-.16),(min(1.5,L*.3),.05,.09))
   continue
  count=max(1,int(L/3.1));step=L/count
  for i in range(count):
   u=-L/2+step*(i+.5)
   for floor in range(5):
    y=2.0+floor*3.8
    F.box('wa-glass',(u,y,-.09),(step*.67,2.8,.065))
    for x in [u-step*.335,u+step*.335]:F.box('wa-mullion',(x,y,-.14),(.055,2.92,.09))
    F.box('wa-mullion',(u,y,-.15),(step*.67,.045,.09))
   F.box('wa-stucco',(u-step*.5,10.4,-.15),(.4,20.8,.34))
 # Source-supported dark curved copper crown and gutter above west entry elevation.
 for v in [-13,-9,-5,-1,3,7,11]:
  F=Frame(B,*[R.p(-10,0,v)[i] for i in [0,2]],math.pi/4+math.pi/2,y=0)
  F.box('wa-glass',(0,17.0,-.10),(3.85,3.3,.08))
 # Curved copper cap, with seams following the same quarter-round profile.
 profile=[(-10,19),(-10.5,19.1),(-10.9,19.7),(-11.05,20.7),(-10.95,21.7),(-10.6,22.5),(-10,22.8)]
 for (u,y),(uu,yy) in zip(profile,profile[1:]):
  B.face('wa-copper',[R.p(u,y,-15),R.p(uu,yy,-15),R.p(uu,yy,13),R.p(u,y,13)])
 for v in [-15,13]:
  for i in range(1,len(profile)-1):B.face('wa-copper',[R.p(*[profile[j][0],profile[j][1],v]) for j in [0,i,i+1]])
 for v in np.arange(-15,13,.7):
  for (u,y),(uu,yy) in zip(profile,profile[1:]):R.tube('wa-seam',(u-.025,y,float(v)),(uu-.025,yy,float(v)),.018,6)
 # Low frontage glazing and rounded copper rain gutter below exposed tile edges.
 for q in parts(low):
  q=orient(q,sign=1.0)
  for a,b in zip(list(q.exterior.coords),list(q.exterior.coords)[1:]):
   ua,va=uv(*a);ub,vb=uv(*b);L=math.dist(a,b)
   if max(ua,ub)>-10.1 or L<2:continue
   F=Frame(B,(a[0]+b[0])/2,(a[1]+b[1])/2,math.atan2(-(b[1]-a[1]),b[0]-a[0]),y=0)
   if LineString([a,b]).distance(entry)<.1:continue
   F.box('wa-glass',(0,1.3,-.08),(L-.5,1.8,.06))
   for x in np.arange(-L/2+.25,L/2,1.4):F.box('wa-mullion',(float(x),1.3,-.13),(.05,1.85,.08))
   # The real canopy's copper edge is a curved gutter, not a flat fascia.
   if abs(ua-ub)<.5:
    y=(roofy(*a)+roofy(*b))/2
    for angle in np.linspace(0,math.pi,13)[:-1]:
     aa=float(angle);bb=aa+math.pi/12
     B.face('wa-copper',[F.p(-L/2,y-.55*math.sin(aa),-.55*math.cos(aa)),F.p(L/2,y-.55*math.sin(aa),-.55*math.cos(aa)),F.p(L/2,y-.55*math.sin(bb),-.55*math.cos(bb)),F.p(-L/2,y-.55*math.sin(bb),-.55*math.cos(bb))])
 # Deep public entrance below low roof with column braces and recessed doors.
 for v in [.4,7.6]:
  R.box('wa-stone',(-23,.9,v),(.8,1.8,.8),True)
  R.tube('wa-dark',(-23,1.8,v),(-23,6.0,v),.15,10)
  R.box('wa-dark',(-23,3.9,v),(.23,4.2,.23),True)
  for dv in [-1,1]:R.tube('wa-dark',(-23,4.8,v),(-23,6.2,v+dv),.09,8)
 D=Frame(B,*[R.p(-10.15,0,4)[i] for i in [0,2]],math.pi/4+math.pi/2,y=0)
 D.box('wa-glass',(0,1.6,-.13),(4.6,3.1,.08));D.box('wa-mullion',(0,1.6,-.2),(.07,3.15,.09))
 for u in [-2.3,2.3]:D.box('wa-mullion',(u,1.6,-.2),(.07,3.15,.09))
 D.text('2700',(0,3.55,-.16),.35,'wa-address')
 B.planar('wa-paving',entry.intersection(p).buffer(.15),.08,True)
 # Adjoining mapped roof is kept hollow: drive-through and pedestrian covered circulation.
 B.planar('wa-membrane',can,4.35)
 for a,b in zip(list(can.exterior.coords),list(can.exterior.coords)[1:]):
  dx,dz=b[0]-a[0],b[1]-a[1];L=math.hypot(dx,dz)
  if L<.2:continue
  F=Frame(B,(a[0]+b[0])/2,(a[1]+b[1])/2,math.atan2(-dz,dx),y=0);F.box('wa-cap',(0,4.25,0),(L,.35,.25))
 for u,v in [(39,-7),(39,1),(29,8),(25,-26),(15,-26),(24,18)]:R.box('wa-stucco',(u,2.1,v),(.65,4.2,.65),True)
 # Under-canopy light housings are geometry; no runtime light-set changes.
 for u,v in [(36,-3),(28,10),(20,-24)]:R.box('wa-diffuser',(u,4.2,v),(1.2,.05,.6))
 # Roof equipment and parapets remain separate from windows.
 for u,v in [(0,-5),(7,4),(9,-11)]:
  R.box('wa-service',(u,22.3,v),(2.8,.9,2.0));R.box('wa-alloy',(u,22.79,v),(2.9,.08,2.1))
 # Current WA lettering on the southeast face; dimensions and precise placement fitted.
 S=Frame(B,*[R.p(0,0,26.9)[i] for i in [0,2]],math.pi/4+math.pi,y=0)
 S.text('WA',(0,19.8,-.12),1.1,'wa-logo');S.text('WESTERN ALLIANCE',(0,19.2,-.14),.22,'wa-address')
 # Limited low planting beside public frontage, leaving all road surfaces intact.
 for u,v in [(-25,-3),(-25,11),(-20,18),(-13,25),(-5,29)]:
  pos=R.p(u,0,v)
  for j in range(8):B.sphere('wa-foliage',(pos[0]+.5*math.cos(j*2.4),.7+(j%3)*.12,pos[2]+.5*math.sin(j*2.4)),.6,8,5)
 routes=[dict(name='Covered public entry',points=[R.p(u,.08,4) for u in [-27,-24,-20,-15,-11.2]]),dict(name='Drive-through open clearance',points=[R.p(u,.02,-3) for u in [45,40,35,30,26]])]
 return dict(key=KEY,name='Western Alliance Bank Sahara',center=[-464,0,-3225],bounds=list(p.union(can).bounds),structural=True,hotelSources=[],exteriorOnly=True,portals=[],zones=[],lights=[],routes=routes)
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
