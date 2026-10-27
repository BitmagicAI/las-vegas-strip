"""Original mapped Cane's exterior; public dining arrangement inferred from partial photos."""
from common import *
KEY='canes-tropicana';IDS=['way/1126368782']
def build(B):
 B.property=KEY+'-exterior';B.source='podium/'+KEY;B.detail=0
 p=footprint(IDS[0]);F=Frame(B,-1252.904,1708.287,.01056,y=0);w=12.69;d=24.74
 doors=[dict(p=F.p(3,.32,0),yaw=F.yaw,width=1.9,height=2.7,name='Public dining entrance',venue=KEY)]
 B.shell(p,.02,4.9,'can-stucco',openings=doors,roof=False);B.planar('can-roof',p,4.63);B.planar('can-floor',p,.32,True)
 B.shell(p.buffer(.05,join_style=2),.02,1.05,'can-stone',openings=doors,roof=False,solid=False)
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  L=math.dist(a,b);G=Frame(B,*a,math.atan2(-(b[1]-a[1]),b[0]-a[0]),y=0)
  for y,h,dep,mat in [(4.95,.12,.25,'can-metal'),(4.48,.06,.10,'can-joint'),(1.12,.12,.23,'can-sill')]:G.box(mat,(L/2,y,0),(L,h,dep))
 # Raised north entrance tower. Door aperture remains real through both shells.
 for x,ww in [(1.48,1.14),(4.52,1.14)]:F.box('can-cream',(x,2.95,-.18),(ww,5.9,.34),True)
 F.box('can-cream',(3,4.53,-.18),(4.2,3.0,.34));F.box('can-metal',(3,6.08,-.19),(4.42,.14,.52))
 F.box('can-red',(1.75,2.9,-.39),(.35,5.8,.06))
 F.box('can-metal',(3,3.34,-.86),(2.9,.22,1.62))
 for xx in [2,4]:F.tube('can-metal',(xx,4.10,-.25),(xx,3.43,-1.58),.025,8)
 for xx in [1.99,4.01]:F.box('can-silver',(xx,1.78,-.41),(.075,2.94,.10))
 F.box('can-silver',(3,3.22,-.41),(2.09,.07,.10));F.box('can-glass',(3,3.04,-.37),(1.94,.24,.035))
 F.box('can-red',(3,4.90,-.38),(2.95,1.0,.08));F.text("Cane's",(3,5.02,-.45),.70,'can-letter');F.text('CHICKEN FINGERS',(3,4.55,-.45),.18,'can-letter')
 # North dining bays and long west facade, including standing-seam metal awnings.
 def glazing(G,L,centers):
  for x in centers:
   G.box('can-recess',(x,2.22,-.08),(2.05,2.02,.12));G.box('can-glass',(x,2.22,-.16),(1.91,1.87,.035))
   for xx in [x-.99,x,x+.99]:G.box('can-silver',(xx,2.22,-.21),(.045,2.02,.07))
   for yy in [1.23,3.21]:G.box('can-silver',(x,yy,-.21),(2.04,.05,.07))
  a=.3;b=L-.3
  B.face('can-metal',[G.p(a,3.35,-1.2),G.p(b,3.35,-1.2),G.p(b,4.15,-.05),G.p(a,4.15,-.05)])
  G.box('can-metal',((a+b)/2,3.30,-1.21),(b-a,.12,.12))
  for x in np.arange(a,b,.24):G.tube('can-rib',(x,3.37,-1.21),(x,4.17,-.05),.018,5)
  for x in [a,b]:B.face('can-metal',[G.p(x,3.30,-.02),G.p(x,4.15,-.02),G.p(x,3.35,-1.22)])
 N=Frame(B,*[F.p(5.2,0,0)[i] for i in (0,2)],F.yaw,y=0);glazing(N,7.4,[1.3,3.7,6.1])
 W=Frame(B,*[F.p(0,0,14)[i] for i in (0,2)],F.yaw+math.pi/2,y=0);glazing(W,14,[1.7,4.3,6.9,9.5,12.1])
 for G,L in [(F,w),(W,14)]:G.box('can-paving',(L/2,.245,-1.7),(L+.3,.15,3.4),True)
 # Rear service elevation, closed delivery door and drive-through window.
 E=Frame(B,*[F.p(w,0,0)[i] for i in (0,2)],F.yaw-math.pi/2,y=0)
 E.box('can-silver',(9,2.0,-.1),(2.05,1.7,.15));E.box('can-glass',(9,2,-.2),(1.87,1.52,.04));E.box('can-silver',(9,2,-.25),(.055,1.6,.08));E.box('can-sill',(9,1.17,-.40),(2.15,.13,.65));E.box('can-metal',(9,3.05,-.75),(2.7,.20,1.50))
 for z in [17,21]:
  F.box('can-equipment',(4,5.13,z),(2.1,1.0,1.5));F.box('can-metal',(4,5.68,z),(2.2,.10,1.6))
  for dz in np.arange(-.65,.7,.18):F.box('can-joint',(4,5.15,z+dz),(2.13,.04,.04))
 for x in [1,w-1]:F.tube('can-metal',(x,.3,.12),(x,4.6,.12),.045,8)
 # Public dining volume. The private kitchen boundary is inferred, not surveyed.
 B.property=KEY+'-interior';B.source='public/'+KEY
 room=F.poly([(.2,.12),(w-.2,.12),(w-.2,13.5),(.2,13.5)])
 B.shell(room,.32,3.65,'can-interior',openings=doors,roof=False);B.planar('can-ceiling',room,3.63)
 F.box('can-brick',(w-.27,1.98,7.0),(.08,3.30,12.8));F.box('can-red',(6.3,1.98,13.42),(12.2,3.30,.08))
 for x in np.arange(.3,w-.3,.6):F.box('can-grout',(x,.328,6.8),(.014,.008,13.3))
 for z in np.arange(.3,13.5,.6):F.box('can-grout',(6.35,.328,z),(12.3,.008,.014))
 # Black upholstered booths with stitched padded backs and wood tables.
 for z in [3.3,6.4,9.5]:
  for zz in [z-.88,z+.88]:
   F.box('can-black',(10.7,.77,zz),(2.15,.40,.63),True)
   F.box('can-black',(10.7,1.22,zz+(.30 if zz>z else -.30)),(2.17,1.02,.18),True)
   for x in [10.0,10.7,11.4]:F.box('can-seam',(x,1.28,zz+(.19 if zz>z else -.19)),(.012,.70,.012))
  F.box('can-wood',(10.7,1.10,z),(1.9,.07,1.0),True);F.tube('can-metal',(10.7,.34,z),(10.7,1.07,z),.07,12);F.box('can-metal',(10.7,.37,z),(.72,.06,.65))
  F.lathe('can-red',10.95,z,[(1.14,.045),(1.28,.06)],12)
  F.lathe('can-letter',10.95,z,[(1.28,.062),(1.30,.062)],12)
 # Open table seating along west windows, generous central route.
 for z in [4.0,8.4]:
  F.box('can-wood',(2.2,1.10,z),(1.5,.07,1.0),True)
  for zz in [z-.9,z+.9]:
   for x in [1.8,2.6]:
    F.box('can-black',(x,.78,zz),(.50,.10,.50),True);F.box('can-black',(x,1.10,zz+(.22 if zz>z else -.22)),(.50,.62,.08))
    for dx in [-.20,.20]:F.tube('can-metal',(x+dx,.33,zz),(x+dx,.73,zz),.025,8)
  F.tube('can-metal',(2.2,.33,z),(2.2,1.07,z),.07,12)
 # Order counter seals off private rooms; no invented kitchen circulation.
 F.box('can-wood',(4.1,.91,11.8),(6.8,1.18,.85),True);F.box('can-metal',(4.1,1.53,11.8),(6.95,.08,.95))
 for x in [2.0,5.5]:
  F.box('can-metal',(x,1.59,11.8),(.32,.05,.26));F.box('can-metal',(x,1.75,11.8),(.07,.30,.07))
  F.box('can-black',(x,1.94,11.79),(.46,.32,.075));F.box('can-screen',(x,1.94,11.745),(.40,.26,.018))
  for yy in [1.89,1.95]:F.box('can-letter',(x,yy,11.73),(.25,.012,.008))
 # Small wall sconces and original geometric framed panels; no borrowed photo artwork.
 for z in [3.4,7.6,11.6]:
  F.box('can-black',(.26,2.45,z),(.08,1.05,.8))
  F.box('can-wood',(.31,2.45,z),(.035,.94,.69))
  for yy,dz in [(2.25,-.17),(2.5,.13),(2.70,-.1)]:F.box('can-letter',(.335,yy,z+dz),(.012,.12,.25))
 for x in [6.3,10.5]:
  F.box('can-metal',(x,4.15,-.13),(.13,.30,.20));F.box('can-letter',(x,3.99,-.17),(.11,.025,.14))
 for x in [2,4.3,6.6]:
  F.box('can-black',(x,2.79,13.30),(2.0,.95,.09));F.box('can-menu',(x,2.79,13.24),(1.87,.82,.025))
  F.text('CHICKEN FINGERS',(x,3.03,13.20),.14,'can-letter')
  for yy in [2.80,2.61]:F.box('can-letter',(x,yy,13.19),(1.35,.025,.012))
 # Original lettering rather than copying the wall mural/art photographs.
 F.text("Cane's",(9.7,2.80,13.32),.68,'can-letter')
 for z in [3.3,6.4,9.5]:
  F.tube('can-metal',(10.7,3.63,z),(10.7,2.60,z),.012,6)
  F.lathe('can-letter',10.7,z,[(2.43,.24),(2.77,.08)],16)
 for x,z in [(4.0,4.0),(7.5,8.0)]:F.light(x,3.25,z,color=0xffefd8,power=20,range=11)
 routes=[dict(name='Entry and dining circulation',points=[F.p(x,.32,z) for x,z in [(3,-2),(3,1.2),(5,2),(5,9.9),(8.5,9.9),(8.5,2),(3,1.2),(3,-2)]]),dict(name='North frontage',points=[F.p(x,.32,-2.2) for x in [1,6.3,11.7]]),dict(name='West frontage',points=[W.p(x,.32,-2.2) for x in [1,7,13]])]
 return dict(key=KEY,name='Raising Canes West Tropicana',center=[-1246,0,1720],bounds=[-1257,1704,-1237,1736],structural=True,exteriorOnly=False,portals=doors,zones=[dict(origin=F.p(w/2,.32,.12),yaw=F.yaw,width=w-.4,depth=13.38,height=3.33)],lights=B.lights,routes=routes,hotelSources=[])
if __name__=='__main__':
 B=Meshes();meta=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(meta,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
