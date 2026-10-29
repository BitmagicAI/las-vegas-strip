"""Original 365 Hughes retail exterior; fitted heights, preserved tenant uncertainty."""
from common import *
KEY='hughes-retail'
IDS=['way/511850834','way/1421198546','way/1421198547','way/1421198548','way/1421198549','way/1561277593']
def build(B):
 p=footprint(IDS[0]);F=Frame(B,0,0,0,y=0)
 B.property=KEY+'-exterior';B.source='retail/'+KEY;B.detail=0
 # Solid backed storefronts: public interiors are not claimed without room references.
 B.shell(p,.02,6,'hr-stucco',roof=False);B.planar('hr-membrane',p,6)
 for poly in parts(p):
  ring=list(poly.exterior.coords)
  for a,b in zip(ring,ring[1:]):
   F.tube('hr-trim',(a[0],6.04,a[1]),(b[0],6.04,b[1]),.09,6)
 def window(D,w,h=3.9):
  D.box('hr-glass',(0,.35+h/2,.08),(w,h,.05))
  for u in np.linspace(-w/2,w/2,max(2,int(w/1.2)+1)):
   D.box('hr-metal',(float(u),.35+h/2,.14),(.055,h,.11))
  for y in [.35,2.7,h+.35]:D.box('hr-metal',(0,y,.14),(w,.06,.11))
  for u in [-.65,.65]:D.box('hr-black',(u,1.4,.23),(.035,.4,.04))
 # Tall angled Panera end-cap, corroborated by the July2025 entrance photo.
 D=Frame(B,1550.05,127.95,-math.pi/4,y=0)
 tower=D.poly([(-4.1,-7),(4.1,-7),(4.1,0),(-4.1,0)])
 B.shell(tower,.04,10.4,'hr-taupe',roof=False);B.planar('hr-membrane',tower,10.4)
 window(D,5.9,4.8)
 for y in np.arange(5.3,10.4,.65):D.box('hr-joint',(0,float(y),.035),(8.2,.025,.025))
 D.text('Panera',(0,8.6,.12),.72,'hr-letter',back=True);D.text('BREAD',(0,8.02,.12),.29,'hr-letter',back=True)
 D.text('365',(3.3,9.9,.12),.3,'hr-black',back=True);D.text('100',(0,2.85,.22),.18,'hr-letter',back=True)
 B.face('hr-rust',[D.p(-3.25,6.1,.18),D.p(3.25,6.1,.18),D.p(3.25,4.4,1.6),D.p(-3.25,4.4,1.6)])
 for u in [-2.7,-1.35,0,1.35,2.7]:D.tube('hr-black',(u,6.75,.08),(u,6.3,.85),.025,6)
 for u in [-3.7,3.7]:D.box('hr-lamp',(u,2.2,.12),(.18,.45,.08))
 # Round metal-clad Chipotle corner; no duplicate wall skins below the shared roof.
 C=Frame(B,1594.1,128,0,y=0);r=5.0
 circ=Point(1594.1,128).buffer(r,resolution=32)
 openings=[dict(p=C.p(r*math.sin(a),.35,r*math.cos(a)),yaw=a,width=1.48,height=4.3) for a in np.linspace(-1.25,1.25,8)]
 B.shell(circ,.02,10.2,'hr-alloy-paint',roof=False,openings=openings);B.planar('hr-membrane',circ,10.2)
 for y in np.arange(6.1,10.3,.82):
  for a,b in zip(np.linspace(0,math.tau,65),np.linspace(0,math.tau,65)[1:]):
   C.tube('hr-joint',(r*math.sin(a),float(y),r*math.cos(a)),(r*math.sin(b),float(y),r*math.cos(b)),.012,4)
 for a in np.linspace(-1.25,1.25,8):
  P=C.p(r*math.sin(a),0,r*math.cos(a));G=Frame(B,P[0],P[2],a,y=0);window(G,1.5,4.3)
  G.box('hr-metal',(0,3.35,.42),(1.65,.1,.8))
 for a,b in zip(np.linspace(-.58,.58,25),np.linspace(-.58,.58,25)[1:]):
  B.face('hr-red',[C.p((r+.06)*math.sin(t),y,(r+.06)*math.cos(t)) for t,y in [(a,8.3),(b,8.3),(b,9.25),(a,9.25)]])
 for ch,a in zip('CHIPOTLE',np.linspace(-.46,.46,8)):
  q=C.p((r+.13)*math.sin(a),0,(r+.13)*math.cos(a));G=Frame(B,q[0],q[2],a,y=0);G.text(ch,(0,8.65,0),.54,'hr-letter',back=True)
 # Middle bays are retained without unverified current tenant branding.
 for x,w,n in [(1568.5,7.2,'110'),(1576.7,6.5,'120'),(1584.8,6.4,'130')]:
  G=Frame(B,x,129.0,0,y=0);window(G,w,3.9)
  G.box('hr-trim',(0,5.15,.06),(w+.35,1.25,.18));G.text(n,(0,2.95,.22),.19,'hr-letter',back=True)
  G.box('hr-black',(0,4.25,.55),(w+.2,.14,1.15))
 # Parapet caps, restrained service detail and roof plant on the observed flat roof.
 for x in [1558,1568,1578,1588]:
  for z in [110,119]:
   F.box('hr-equipment',(x,6.5,z),(2.1,1,1.8))
   for y in np.arange(6.15,6.85,.13):F.box('hr-black',(x,float(y),z+.91),(1.8,.035,.025))
 for x in [1557,1570,1584,1593]:
  F.box('hr-metal',(x,1.5,106),(1.05,2.7,.1));F.box('hr-black',(x+.36,1.45,105.92),(.04,.3,.05))
 # Individual patio pads, tables, chairs and low rails keep circulation open.
 for x in [1558,1568,1585,1595]:
  z=134.6;F.box('hr-concrete',(x,.25,z),(5.4,.1,3.3),True)
  for side in [-1,1]:
   F.rail((x+side*2.6,z-1.5),(x+side*2.6,z+1.5),1.25)
  for dx in [-1.3,1.3]:
   xx=x+dx;F.box('hr-black',(xx,.67,z),(.1,.74,.1));F.box('hr-wood',(xx,1.06,z),(1.0,.07,.65),True)
   for dz in [-.7,.7]:
    F.box('hr-wood',(xx,.73,z+dz),(.48,.07,.42),True)
    for a in [-.18,.18]:
     for b in [-.15,.15]:F.box('hr-black',(xx+a,.51,z+dz+b),(.035,.43,.035))
    F.box('hr-black',(xx,1.02,z+dz+math.copysign(.18,dz)),(.48,.46,.04))
 routes=[dict(name='South public frontage',points=[[x,.28,138] for x in [1552,1560,1570,1580,1590,1598]])]
 return dict(key=KEY,name='365 Hughes Center retail',center=[1574,0,119],bounds=list(p.bounds),structural=True,hotelSources=[],exteriorOnly=True,portals=[],zones=[],lights=[],routes=routes)
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
