"""Original Tropicana store and pump architecture; public fixture layout is inferred."""
from common import *
KEY='terribles-tropicana';IDS=['way/1126368783','way/1126368784','way/1126368785']
def build(B):
 B.property=KEY+'-exterior';B.source='podium/'+KEY;B.detail=0
 p=footprint(IDS[0]);F=Frame(B,-1181.907,1729.615,-.02093,y=0);w=16.53;d=16.15
 door=dict(p=F.p(3.8,.32,0),yaw=F.yaw,width=2.2,height=2.7,name='Public shop entrance',venue=KEY);doors=[door]
 B.shell(p,.02,4.35,'th-peach',openings=doors,roof=False);B.planar('th-roof',p,4.18)
 B.shell(p.buffer(.035,join_style=2),.02,.95,'th-brown',openings=doors,roof=False,solid=False)
 B.planar('th-floor',p,.32,True)
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  L=math.dist(a,b);G=Frame(B,*a,math.atan2(-(b[1]-a[1]),b[0]-a[0]),y=0)
  for y,h,dep,mat in [(3.48,.12,.4,'th-white'),(3.98,.87,.38,'th-red'),(4.46,.10,.43,'th-blue'),(3.36,.09,.40,'th-blue')]:G.box(mat,(L/2,y,0),(L,h,dep))
 # North glazed entry frontage: apertures only at the real public entrance.
 for x,ww in [(1.4,2.3),(6.0,2.1)]:
  F.box('th-glass',(x,1.84,-.10),(ww,2.95,.08))
  for xx in [x-ww/2,x+ww/2]:F.box('th-black',(xx,1.84,-.17),(.06,3.0,.10))
 for xx in [2.65,4.95]:F.box('th-black',(xx,1.70,-.17),(.08,2.80,.13))
 F.box('th-black',(3.8,3.06,-.17),(2.35,.08,.13));F.box('th-glass',(3.8,3.26,-.12),(2.25,.3,.06))
 F.text("ATM  ·  BEER  ·  CIGARETTES  ·  ICE",(w/2,3.96,-.23),.80,'th-white')
 F.text("TERRIBLE'S",(3.8,3.03,-.25),.26,'th-white')
 # Photographed exterior ice chest, framed window and corner protectors.
 F.box('th-white',(10.9,1.17,-.54),(1.65,1.70,.90),True)
 for xx in [10.5,11.3]:
  F.box('th-metal',(xx,1.18,-1.01),(.71,1.37,.035));F.box('th-black',(xx,1.18,-1.04),(.02,.18,.025))
 F.text('ICE',(10.9,2.13,-.60),.24,'th-blue')
 F.box('th-white',(13.7,1.77,-.08),(1.55,1.43,.10));F.box('th-glass',(13.7,1.77,-.15),(1.40,1.29,.06))
 for xx in [1.0,7.1]:F.lathe('th-red',xx,-.55,[(.32,.07),(1.3,.07),(1.35,0)],10)
 F.box('th-paving',(w/2,.245,-1.5),(w+.3,.15,3.0),True)
 for x in [2,14]:F.box('th-metal',(x,4.75,1.0),(.55,.48,.25))
 for x,z in [(4,13.5),(11,13.5)]:
  F.box('th-metal',(x,4.65,z),(2.1,.9,1.3));F.box('th-black',(x,5.14,z),(2.15,.08,1.35))
 # Two independent mapped pump roofs. Hip pitch and pump positions estimated from photos.
 fuelroutes=[]
 for ci,ident in enumerate(IDS[1:]):
  roof=footprint(ident);rect=roof.minimum_rotated_rectangle;corners=list(rect.exterior.coords)[:-1];cx,cz=roof.centroid.coords[0]
  B.planar('th-paving',roof,.32,True)
  B.planar('th-soffit',roof,4.35);B.shell(roof,4.35,4.72,'th-blue',roof=False,solid=False)
  for a,b in zip(corners,corners[1:]+corners[:1]):B.face('th-tile',[(a[0],4.75,a[1]),(b[0],4.75,b[1]),(cx,6.0,cz)])
  C=Frame(B,cx,cz,.18 if ci==0 else .26,y=0)
  fuelroutes.append(dict(name='Fuel island '+str(ci+1)+' clear lane',points=[C.p(0,.32,z) for z in [-5,0,5]]))
  for xx in [-3.4,3.4]:
   for zz in [-3.1,3.1]:
    C.box('th-peach',(xx,2.2,zz),(.48,4.4,.48),True)
    C.box('th-brown',(xx,.60,zz),(.70,1.2,.70),True)
    # Island, pump with recessed display, card slot, hoses and protective posts.
    px=xx+.95
    C.box('th-paving',(px,.43,zz),(2.5,.26,1.3),True)
    C.box('th-white',(px,1.18,zz),(.92,1.82,.62),True)
    C.box('th-blue',(px,2.12,zz),(1.04,.18,.72))
    for side in [-1,1]:
     C.box('th-black',(px,1.57,zz+side*.325),(.65,.50,.025))
     C.box('th-display',(px,1.64,zz+side*.343),(.46,.22,.018))
     C.box('th-metal',(px+.23,1.14,zz+side*.343),(.14,.08,.025))
    for side in [-1,1]:
     C.path('th-black',[(px+side*.49,1.93,zz),(px+side*.72,1.55,zz),(px+side*.74,.64,zz),(px+side*.52,.75,zz),(px+side*.49,1.36,zz)],.028,7)
    for dz in [-.54,.54]:C.lathe('th-white',px,zz+dz,[(.27,.06),(1.0,.06),(1.04,0)],8)
  if ci==1:
   C.box('th-peach',(0,5.50,0),(2.05,2.20,2.05))
   for xx in [-.83,.83]:
    for zz in [-.83,.83]:C.box('th-peach',(xx,7.30,zz),(.34,1.6,.34))
   for yaw in [0,math.pi/2,math.pi,3*math.pi/2]:
    G=Frame(B,cx,cz,C.yaw+yaw,y=0);G.arch(0,-.86,1.30,8.07,'th-peach',.13,base=6.53)
   C.box('th-brown',(0,6.53,0),(2.23,.16,2.23));C.box('th-brown',(0,8.12,0),(2.25,.16,2.25))
   roofpts=[(-1.35,-1.35),(1.35,-1.35),(1.35,1.35),(-1.35,1.35)]
   for a,b in zip(roofpts,roofpts[1:]+roofpts[:1]):B.face('th-tile',[C.p(*[a[0],8.22,a[1]]),C.p(b[0],8.22,b[1]),C.p(0,8.85,0)])
 # Public shop: envelope follows footprint; private rear is deliberately inaccessible.
 B.property=KEY+'-interior';B.source='public/'+KEY
 room=F.poly([(.20,.08),(16.3,.08),(16.3,12),(.20,12)])
 B.shell(room,.32,3.55,'th-wall',openings=doors,roof=False);B.planar('th-ceiling',room,3.53)
 for z in np.arange(.4,12,.60):F.box('th-grout',(8.25,.329,z),(16.05,.008,.015))
 for x in np.arange(.4,16.3,.60):F.box('th-grout',(x,.329,6.05),(.015,.008,11.8))
 # Recessed cooler bank: individual bottles/cans behind transparent door glazing.
 for iz,z in enumerate(np.arange(2.4,10.8,1.35)):
  F.box('th-black',(16.08,1.72,z),(.15,2.78,1.30),True)
  for zz in [z-.64,z+.64]:F.box('th-metal',(15.53,1.75,zz),(1.05,2.75,.06))
  for yy in [.36,3.08]:F.box('th-black',(15.53,yy,z),(1.05,.08,1.30))
  F.box('th-glass',(14.97,1.75,z),(.025,2.60,1.20))
  for iy,yy in enumerate([.48,.91,1.34,1.77,2.20,2.63]):
   F.box('th-metal',(15.50,yy,z),(1.02,.035,1.23))
   for i in range(5):
    zz=z-.45+i*.22;mat=['th-red','th-blue','th-green','th-amber'][(iz+iy+i)%4]
    bottle=(iy+iz)%2==0
    F.lathe(mat,15.26,zz,[(yy+.03,.065),(yy+.23,.065),(yy+.28,.035),(yy+.33,.025)] if bottle else [(yy+.03,.061),(yy+.28,.061)],10)
    F.lathe('th-metal',15.26,zz,[(yy+.33 if bottle else yy+.28,0),(yy+.33 if bottle else yy+.28,.027 if bottle else .061)],10)
    F.box('th-label',(15.193,yy+.16,zz),(.018,.10,.09))
    F.box('th-black',(15.182,yy+.16,zz),(.008,.014,.065))
   F.box('th-white',(14.94,yy,z),(.035,.035,1.18))
  F.box('th-metal',(14.91,1.75,z-.61),(.07,2.73,.04))
  F.box('th-metal',(14.91,1.75,z+.61),(.07,2.73,.04))
  F.box('th-metal',(14.83,1.72,z+.47),(.045,.38,.045))
 # Rear L-shaped snack/coffee counter and photographed pale cabinets.
 for x,z,ww,dd in [(4.3,11.32,7.5,.75),(.85,8.1,.9,5.8)]:
  F.box('th-white',(x,.88,z),(ww,1.12,dd),True);F.box('th-black',(x,1.49,z),(ww+.08,.08,dd+.08))
  for xx in np.arange(x-ww/2+.55,x+ww/2,.8):
   F.box('th-metal',(xx,.92,z-dd/2-.035),(.025,.20,.035))
   F.box('th-grout',(xx-.35,.89,z-dd/2-.012),(.012,1.04,.018))
 # Coffee station, chilled pastry display and hot-food roller case.
 for x in [1.8,2.5]:
  F.lathe('th-black',x,11.25,[(1.53,.20),(1.90,.20),(2.06,.15),(2.10,0)],16)
  F.lathe('th-metal',x,11.25,[(1.61,.204),(1.80,.204)],16)
  F.box('th-black',(x,1.63,10.99),(.07,.16,.13))
  F.box('th-metal',(x,1.54,10.98),(.38,.04,.32))
 F.box('th-black',(4.05,1.97,11.28),(1.20,.92,.66))
 F.box('th-glass',(4.05,1.97,10.93),(1.10,.80,.035))
 for yy in [1.60,1.87,2.14]:
  F.box('th-metal',(4.05,yy,10.88),(1.05,.025,.22))
  for x in [3.7,4.05,4.4]:F.box('th-bread',(x,yy+.09,10.85),(.24,.13,.16))
 F.box('th-metal',(6.05,1.61,11.20),(1.35,.20,.63))
 for x in np.arange(5.5,6.7,.12):F.tube('th-metal',(x,1.73,10.96),(x,1.73,11.43),.035,8)
 for x in [5.7,6.15]:F.tube('th-bread',(x,1.79,11.03),(x,1.79,11.32),.042,10)
 for x in [5.43,6.68]:F.box('th-metal',(x,2.02,11.30),(.045,.65,.045))
 F.box('th-glass',(6.05,2.30,11.18),(1.32,.035,.65))
 G=Frame(B,*[F.p(4.3,0,11.94)[i] for i in (0,2)],F.yaw,y=0)
 G.box('th-red',(0,2.95,-.05),(7.6,.74,.08));G.text('HUNGRY?  GOT SNACKS?',(0,2.97,-.11),.43,'th-white')
 # Low gondola racks, with clear circulation loop around them.
 for x in [7.1,10.1]:
  F.box('th-white',(x,1.05,6.6),(1.15,1.4,3.5),True)
  for yy in [.50,.87,1.24,1.61]:
   F.box('th-metal',(x,yy,6.6),(1.26,.045,3.55))
   for z in np.arange(5.05,8.2,.32):
    for side in [-1,1]:
     F.box(['th-red','th-blue','th-green'][int(z*10)%3],(x+side*.49,yy+.14,z),(.20,.23,.23))
     F.box('th-label',(x+side*.598,yy+.16,z),(.012,.08,.14))
     F.box('th-metal',(x+side*.49,yy+.26,z),(.205,.018,.235))
 F.box('th-white',(10.4,.9,1.8),(4.0,1.16,.85),True);F.box('th-black',(10.4,1.52,1.8),(4.1,.08,.94))
 F.box('th-black',(9.2,1.8,1.8),(.48,.48,.30));F.box('th-display',(9.2,1.85,1.62),(.40,.29,.02))
 for z in [2.0,5.4,8.8]:
  for x in [3.8,8,12.4]:F.box('th-light',(x,3.50,z),(2.0,.04,.35))
 F.light(5.0,3.10,5.5,color=0xfff3df,power=22,range=12);F.light(12.2,3.10,7.0,color=0xf0f6ff,power=18,range=10)
 routes=[dict(name='Shop entrance and public circulation',points=[F.p(x,.32,z) for x,z in [(3.8,-2),(3.8,1),(3.8,4),(13.2,4),(13.2,9.4),(3.8,9.4),(3.8,1),(3.8,-2)]]),dict(name='North frontage',points=[F.p(x,.32,-2) for x in [1,8,15]])]
 routes.extend(fuelroutes)
 return dict(key=KEY,name='Terrible Herbst West Tropicana',center=[-1173,0,1730],bounds=[-1186,1697,-1148,1749],structural=True,exteriorOnly=False,portals=doors,zones=[dict(origin=F.p(8.25,.32,.08),yaw=F.yaw,width=16.1,depth=11.92,height=3.23)],lights=B.lights,routes=routes,hotelSources=[])
if __name__=='__main__':
 B=Meshes();meta=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(meta,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
