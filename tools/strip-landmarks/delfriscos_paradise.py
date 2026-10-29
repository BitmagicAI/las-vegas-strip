"""Original reference-led restaurant exterior; dimensions fitted, not surveyed."""
from common import *
KEY='delfriscos-paradise';IDS=['way/205741855']
def build(B):
 p=footprint(IDS[0]);B.property=KEY+'-exterior';B.source='restaurant/'+KEY;B.detail=0
 # Main building excludes the mapped open western porte-cochere.
 main=p.intersection(box(1564.3,-260,1610,-190));B.shell(main,.02,5.5,'df-stucco',roof=False);B.planar('df-membrane',main,5.5)
 F=Frame(B,1580.4,-226,.032,y=0)
 def hip(F,w,d,eave,rise):
  a,b=w/2,d/2;r=max(0,a-b)
  pts=[(-a,eave,-b),(a,eave,-b),(a,eave,b),(-a,eave,b)]
  ridge=[(-r,eave+rise,0),(r,eave+rise,0)]
  for q in [[pts[0],pts[1],ridge[1],ridge[0]],[pts[1],pts[2],ridge[1]],[pts[2],pts[3],ridge[0],ridge[1]],[pts[3],pts[0],ridge[0]]]:B.face('df-slate',[F.p(*v) for v in q])
  for i in range(4):F.tube('df-trim',pts[i],pts[(i+1)%4],.09)
 # Pitched central roof and service wings in aerial; exact pitches inferred.
 hip(F,32,17,5.6,2.3)
 for x,z,w,d in [(1580,-241,24,8),(1580,-209,30,7)]:
  Q=Frame(B,x,z,.032,y=0)
  for u,v in [(-w/2,0),(w/2,0)]:Q.box('df-stucco',(u,5.8,v),(.3,.6,d))
  for v in [-d/2,d/2]:Q.box('df-stucco',(0,5.8,v),(w,.6,.3))
  for u in [-7,0,7]:
   Q.box('df-equipment',(u,5.9,0),(2.1,.8,1.5));Q.box('df-trim',(u,6.32,0),(1.8,.05,1.25))
   for off in np.arange(-.5,.6,.18):Q.box('df-equipment',(u,6.36,float(off)),(1.7,.035,.035))
 # West arrival faces the parking lot, not Paradise Road.
 E=Frame(B,1555.9,-227.2,-math.pi/2+.032,y=0)
 # Open drive-through clearance under gable, columns and panelled bases.
 E.box('df-ceiling',(0,4.55,0),(12,.28,20),True)
 for u in [-5.3,5.3]:
  for v in [-8,0,8]:
   E.box('df-trim',(u,.45,v),(1.04,.9,1.04),True);E.box('df-stucco',(u,2.6,v),(.78,3.4,.78),True)
   for side in [-1,1]:
    E.box('df-panel',(u+side*.4,2.6,v),(.025,2.8,.53));E.box('df-panel',(u,2.6,v+side*.4),(.53,2.8,.025))
   for y,w in [(4.23,.98),(4.36,1.12),(.91,1.1)]:E.box('df-trim',(u,y,v),(w,.12,w))
 for v in [-10,10]:
  B.face('df-stucco',[E.p(-6,4.7,v),E.p(6,4.7,v),E.p(0,6.65,v)])
  for side in [-1,1]:E.tube('df-trim',(side*6,4.7,v),(0,6.65,v),.12)
 for side in [-1,1]:B.face('df-slate',[E.p(side*6,4.73,-10),E.p(0,6.68,-10),E.p(0,6.68,10),E.p(side*6,4.73,10)])
 for u in [-6,6]:E.box('df-trim',(u,4.65,0),(.22,.28,20.3))
 for u in [-3,3]:
  for v in [-6,0,6]:
   for a in [-2.4,2.4]:E.box('df-trim',(u+a,4.385,v),(.08,.04,4.8))
   for a in [-2.4,2.4]:E.box('df-trim',(u,4.385,v+a),(4.8,.04,.08))
   E.tube('df-brass',(u,4.4,v),(u,3.85,v),.025);E.box('df-lamp',(u,3.7,v),(.22,.36,.22))
 E.text("Del Frisco's",(0,5.35,10.15),.62,'df-trim',back=True)
 E.text('DOUBLE EAGLE STEAKHOUSE',(0,4.9,10.15),.22,'df-trim',back=True)
 # West entrance at inner end, opaque doorway pending measured public-room layout.
 W=Frame(B,1564.1,-227.5,-math.pi/2+.032,y=0)
 W.box('df-door',(0,1.6,.15),(3.6,3.2,.12),True)
 for u in [-1.7,0,1.7]:W.box('df-brass',(u,1.6,.23),(.065,3.2,.04))
 for u in [-.85,.85]:
  for y in [.8,2.2]:W.box('df-panel',(u,y,.23),(1.4,1.1,.035))
 for u in [-3.4,3.4]:W.box('df-red',(u,2.05,.2),(1.1,3.6,.13))
 # Repeated shuttered wall bays, cornice and lower plinth, fitted to outer faces.
 for a,b in zip(list(main.exterior.coords),list(main.exterior.coords)[1:]):
  dx,dz=b[0]-a[0],b[1]-a[1];L=math.hypot(dx,dz)
  if L<3:continue
  G=Frame(B,(a[0]+b[0])/2,(a[1]+b[1])/2,math.atan2(-dz,dx),y=0)
  for y,h,depth in [(.3,.6,.2),(4.5,.12,.18),(5.35,.25,.34)]:G.box('df-trim' if y==4.5 else 'df-stucco',(0,y,0),(L,h,depth))
  if a[0]<1566 and b[0]<1566:continue
  for u in np.linspace(-L/2+2,L/2-2,max(1,int(L/4.5))):
   G.box('df-glass',(float(u),2.5,0),(1.6,2.2,.2))
   for side in [-1,1]:
    G.box('df-trim',(float(u),3.65,side*.13),(1.9,.14,.08))
    for t in np.arange(-.72,.73,.18):G.box('df-trim',(float(u+t),2.5,side*.13),(.09,2.1,.035))
 for u in [-7.1,7.1]:E.plant(u,7,palm=True)
 routes=[dict(name='West arrival',points=[[1538,.28,-227],[1546,.28,-227],[1553,.28,-227],[1561,.28,-227]]),dict(name='Paradise frontage',points=[[1601,.28,z] for z in [-250,-238,-225,-212,-199]])]
 return dict(key=KEY,name='Del Friscos Paradise',center=[1576,0,-226],bounds=list(p.bounds),structural=True,hotelSources=[],exteriorOnly=True,portals=[],zones=[],lights=[],routes=routes)
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
