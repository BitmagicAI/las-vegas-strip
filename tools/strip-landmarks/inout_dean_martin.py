"""Original Dean Martin In-N-Out restaurant exterior. Dimensions are photo estimates."""
from common import *
from inout_site import site
KEY='inout-dean-martin';IDS=['way/257307259']
def build(B):
 p=footprint(IDS[0]);B.property=KEY+'-exterior';B.source='podium/'+KEY;B.detail=0
 doors=[dict(p=[-845.2,.12,1633],yaw=math.pi/2,width=2.4,height=2.5,name='West restaurant entrance',venue=KEY),dict(p=[-829,.12,1640.25],yaw=math.pi,width=2.4,height=2.5,name='South patio entrance',venue=KEY)]
 windows=[]
 for F,L in [(Frame(B,-845.20,1639.9,math.pi/2,y=0),13.1),(Frame(B,-827.3,1640.29,math.pi,y=0),17.7)]:
  for x,w in ([(2.1,3.7),(10.8,3.7)] if L<14 else [(6.1,4.2),(13.0,5.4)]):windows.append(dict(p=F.p(x,1.12,0),yaw=F.yaw,width=w,height=2.14))
 B.shell(p,.04,5.15,'ino-stucco',openings=doors+windows,roof=False);B.planar('ino-roof',p,5.15)
 B.shell(p.buffer(.035,join_style=2),.80,1.10,'ino-red-tile',openings=doors+windows,roof=False,solid=False)
 # Continuous mapped footprint, white molded cap and low red glazed-tile band.
 coords=list(p.exterior.coords)
 for a,b in zip(coords,coords[1:]):
  length=math.dist(a,b)
  if length<.1:continue
  yaw=math.atan2(-(b[1]-a[1]),b[0]-a[0]);F=Frame(B,a[0],a[1],yaw,y=0)
  for y,h,d in [(5.15,.16,.30),(5.32,.12,.44),(5.45,.08,.53)]:F.box('ino-red-tile' if y<1 else 'ino-trim',(length/2,y,0),(length,h,d))
 # Southwest restaurant room has west entrance and south dining windows.
 faces=[(Frame(B,-845.20,1639.9,math.pi/2,y=0),13.1),(Frame(B,-827.3,1640.29,math.pi,y=0),17.7)]
 for F,L in faces:
  for x,w in ([(2.1,3.7),(10.8,3.7)] if L<14 else [(6.1,4.2),(13.0,5.4)]):
   F.box('ino-glass',(x,2.20,-.12),(w,2.35,.06),True)
   for xx in np.linspace(x-w/2,x+w/2,5):F.box('ino-metal',(xx,2.20,-.18),(.045,2.40,.07))
   for yy in [1.02,3.38]:F.box('ino-metal',(x,yy,-.18),(w,.06,.08))
   # Sloping fabric canopy with closed side returns and white valance.
   a=x-w/2-.15;b=x+w/2+.15
   top=[F.p(a,4.25,-.10),F.p(b,4.25,-.10),F.p(b,3.47,-1.30),F.p(a,3.47,-1.30)]
   B.face('ino-red',top);B.face('ino-red',[F.p(a,3.47,-.1),top[0],top[3]]);B.face('ino-red',[F.p(b,3.47,-.1),top[2],top[1]])
   F.box('ino-white',(x,3.32,-1.30),(w+.3,.30,.04))
   for xx in np.arange(a+.2,b,.36):
    F.tube('ino-red',(xx,3.2,-1.33),(xx,3.43,-1.33),.01,5)
    for dx in [-.09,.09]:F.tube('ino-red',(xx,3.43,-1.33),(xx+dx,3.37,-1.33),.012,5)
 # Raised entrance bays at west face and south end; tile hip roofs.
 def entry(F,w=4.1):
  F.box('ino-stucco',(0,4.85,.9),(w,3.5,2.0))
  for x in [-w/2+.27,w/2-.27]:F.box('ino-stucco',(x,1.6,-.08),(.54,3.2,.42),True)
  F.box('ino-glass',(0,2.98,-.12),(w-.65,.60,.06))
  for xx in [-1.45,1.45]:F.box('ino-glass',(xx,1.35,-.12),(.40,2.45,.06))
  for x in [-1.22,1.22]:F.box('ino-metal',(x,1.65,-.18),(.045,3.30,.08))
  for yy in [2.68,3.28]:F.box('ino-metal',(0,yy,-.18),(w-.6,.055,.08))
  # Moving door leaves are supplied by the shared portal system.
  F.text('4888',(0,3.37,-.22),.24,'ino-red')
  for yy,h,d in [(6.56,.20,2.2),(6.73,.12,2.5)]:F.box('ino-trim',(0,yy,.9),(w+.4,h,d))
  base=[(-w/2-.28,-.42),(w/2+.28,-.42),(w/2+.28,2.22),(-w/2-.28,2.22)]
  for a,b in zip(base,base[1:]+base[:1]):B.face('ino-roof-tile',[F.p(a[0],6.80,a[1]),F.p(b[0],6.80,b[1]),F.p(0,7.52,.9)])
  F.text('IN-N-OUT',(0,4.90,-.20),.48,'ino-red')
  # Original dimensional arrow silhouette, traced geometrically rather than a copied logo image.
  arrow=[(-1.30,5.44),(-1.48,6.04),(1.14,5.78),(1.32,5.98),(1.48,5.48),(1.04,5.24),(1.08,5.49),(-1.00,5.72)]
  for tri in triangles(Polygon(arrow)):
   B.face('ino-yellow',[F.p(x,y,-.24) for x,y in list(tri.exterior.coords)[:-1]])
 entry(Frame(B,-845.25,1633.0,math.pi/2,y=0))
 entry(Frame(B,-829.0,1640.30,math.pi,y=0),3.8)
 # Patio circulation on south/west: original concrete top, single owned support layer.
 patio=unary_union([box(-848,1626,-845,1644.5),box(-845,1640.25,-818.5,1644.5)]).difference(p)
 B.shell(patio,-.08,.12,'ino-paving',roof=False);B.planar('ino-paving',patio,.12,True)
 for x,z in [(-843,1643),(-838.4,1643),(-833.8,1643),(-824,1642.4),(-820,1642.4)]:
  F=Frame(B,x,z,0,y=.12)
  F.lathe('ino-table',0,0,[(.76,0),(.76,.74),(.86,.74),(.86,0)],32)
  F.box('ino-table',(0,.79,0),(1.0,.10,1.0),True)
  F.lathe('ino-table',0,0,[(0,.17),(.78,.17)],12)
  for yaw in [0,2*math.pi/3,4*math.pi/3]:
   G=Frame(B,x,z,yaw,y=.12);G.box('ino-table',(0,.46,.93),(1.1,.14,.38),True)
   for xx in [-.35,.35]:G.tube('ino-table',(0,.10,0),(xx,.38,.93),.10,6)
  F.tube('ino-metal',(0,0,0),(0,2.85,0),.035,10)
  for j in range(12):
   a=j*math.tau/12;b=(j+1)*math.tau/12
   B.face('ino-red' if j%2 else 'ino-white',[F.p(0,2.85,0),F.p(1.25*math.cos(a),2.57,1.25*math.sin(a)),F.p(1.25*math.cos(b),2.57,1.25*math.sin(b))])
 # Roof plant and rear/service glazing. Exact rear arrangement remains an estimate.
 for x,z in [(-839,1630),(-830,1630),(-820,1630)]:B.box('ino-equipment',(x,5.60,z),(2.1,.9,1.7))
 G=Frame(B,-813.70,1633,-math.pi/2,y=0)
 G.box('ino-metal',(0,1.75,-.1),(2.4,1.5,.12));G.box('ino-glass',(0,1.75,-.18),(2.24,1.35,.04));G.box('ino-trim',(0,1.04,-.40),(2.5,.1,.7))
 site(B)
 # Photo-supported public dining finishes; dimensions and counter position inferred.
 B.planar('ino-floor',p,.12,True)
 B.property=KEY+'-interior';B.source='public/'+KEY
 room=box(-844.95,1626.9,-827.15,1640.10)
 B.shell(room,.12,4.05,'ino-white',openings=doors+windows,roof=False)
 B.planar('ino-ceiling',room,4.06)
 # Low grey wainscot and sill below the photographed windows.
 for x,z,w,yaw in [(-844.85,1629.1,3.7,math.pi/2),(-844.85,1637.8,3.7,math.pi/2),(-833.4,1639.98,4.2,math.pi),(-840.3,1639.98,5.4,math.pi)]:
  G=Frame(B,x,z,yaw,y=0);G.box('ino-panel',(0,.57,.02),(w,.88,.04))
  G.box('ino-metal',(0,1.02,.04),(w,.055,.10))
  for u in np.arange(-w/2,w/2,.20):G.box('ino-trim',(u,.57,.05),(.012,.88,.016))
 # Square pale laminate tables and rounded spindle-back red chairs from the room photo.
 def chair(x,z,yaw):
  C=Frame(B,x,z,yaw,y=.12)
  C.box('ino-chair',(0,.46,0),(.43,.09,.43),True)
  for dx in [-.17,.17]:
   for dz in [-.17,.17]:C.tube('ino-chair',(dx,0,dz),(dx,.45,dz),.022,8)
  for dx in [-.23,.23]:C.tube('ino-chair',(dx,.46,.20),(dx,.77,.20),.025,8)
  C.path('ino-chair',[(.23*math.cos(a),.77+.29*math.sin(a),.20) for a in np.linspace(0,math.pi,17)],.025,8)
  for dx in [-.16,0,.16]:C.tube('ino-chair',(dx,.46,.20),(dx,.99,.20),.018,6)
 def table(x,z):
  T=Frame(B,x,z,0,y=.12);T.box('ino-table-top',(0,.76,0),(.80,.055,.80),True)
  T.box('ino-metal',(0,.72,0),(.83,.025,.83))
  for dx in [-.30,.30]:T.tube('ino-metal',(dx,0,-.30),(-dx,.73,.30),.028,8)
  chair(x,z-.68,math.pi);chair(x,z+.68,0)
  T.tube('ino-chair',(0,3.94,0),(0,2.65,0),.008,6)
  T.lathe('ino-lamp',0,0,[(2.43,.30),(2.48,.29),(2.68,.06)],24)
  T.lathe('ino-white',0,0,[(2.44,0),(2.44,.27)],24)
 for x in [-843,-841.55,-840.1,-838.65,-837.2,-835.75,-834.3,-832.85]:table(x,1638.65)
 for z in [1628.3,1629.8]:table(-843,z)
 # Public ordering counter only; kitchen and staff rooms remain inaccessible.
 B.box('ino-red-tile',(-835.5,.70,1629.0),(9.0,1.16,.85),True)
 B.box('ino-metal',(-835.5,1.32,1629.0),(9.1,.08,.95))
 for x in [-839,-836,-833]:
  B.box('ino-metal',(x,1.50,1629.0),(.35,.30,.30))
  B.box('ino-menu',(x,2.9,1627.0),(2.3,1.05,.06))
  G=Frame(B,x,1627.04,math.pi,y=0);G.text('BURGERS  /  FRIES',(0,3.05,-.04),.14,'ino-red')
  for yy in [2.8,2.9]:G.box('ino-trim',(0,yy,-.05),(1.8,.015,.02))
 F=Frame(B,-836,1634,0,y=0);F.light(0,3.5,0,color=0xffefd8,power=22,range=14)
 routes=[dict(name='South patio clear aisle',points=[[-843,.12,1641],[-838,.12,1641],[-834,.12,1641],[-830.8,.12,1641]]),dict(name='West entrance sidewalk',points=[[-847,.12,1627],[-847,.12,1633],[-847,.12,1642]])]
 routes.append(dict(name='Public dining entry and cross aisle',points=[[-847,.12,1633],[-843,.12,1633],[-839,.12,1635.8],[-829,.12,1635.8],[-829,.12,1642]]))
 return dict(key=KEY,name='In-N-Out Dean Martin',center=[-830,0,1633],bounds=[-850,1618,-786,1670],structural=True,exteriorOnly=False,portals=doors,zones=[dict(origin=[-836.05,.12,1626.9],yaw=0,width=17.8,depth=13.2,height=4)],lights=B.lights,routes=routes,hotelSources=[])
if __name__=='__main__':
 B=Meshes();meta=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(meta,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
