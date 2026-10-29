"""Original Speedee Mart, Feb2026 frontage and Jan2023 public shop references.
Mapped footprint retained; elevations and merchandising layout are inferred.
"""
from common import *
KEY='speedee-mart-paradise';ID='way/1017290168';YAW=math.atan2(4.219,-11.124)
def window(F,u,w):
 F.box('sm-glass',(u,1.62,.045),(w,2.15,.045))
 for x in np.linspace(u-w/2,u+w/2,max(2,round(w/1.1)+1)):F.box('sm-metal',(float(x),1.62,.085),(.045,2.25,.09))
 for y in [.52,2.72]:F.box('sm-metal',(u,y,.085),(w,.055,.09))
def frontage(B,F,w,title):
 for y,mat in [(3.72,'sm-red'),(3.58,'sm-yellow')]:F.box(mat,(0,y,.17),(w-.3,.13,.25))
 F.box('sm-metal',(0,3.48,.17),(w-.3,.04,.27))
 F.box('sm-white',(0,2.97,.28),(w,.16,.65))
 for u in np.arange(-w/2+.6,w/2,1.65):F.box('sm-metal',(float(u),3.23,.13),(.48,.16,.2))
 if title=='SPEEDEE MART':
  F.box('sm-white',(0,4.85,-.13),(w-.3,.5,.25))
  F.text('SPEEDEE',(0,4.5,.14),.65,'sm-red',back=True);F.text('MART',(0,3.99,.14),.6,'sm-red',back=True)
 else:F.text(title,(0,4.15,.14),.5,'sm-red',back=True)
 for u in [-w/2,w/2]:
  F.box('sm-white',(u,2.3,.06),(.42,4.6,.48))
  # Rounded swept pier cap, fitted from the visible curved parapet profile.
  for t0,t1 in zip(np.linspace(0,1,17),np.linspace(0,1,17)[1:]):
   y0=4.6+.9*math.sin(t0*math.pi/2);y1=4.6+.9*math.sin(t1*math.pi/2);v0=-.65+.8*t0;v1=-.65+.8*t1
   B.upface('sm-white',[F.p(u-.21,y0,v0),F.p(u+.21,y0,v0),F.p(u+.21,y1,v1),F.p(u-.21,y1,v1)])
   for side in [-1,1]:B.face('sm-white',[F.p(u+side*.21,4.6,v0),F.p(u+side*.21,y0,v0),F.p(u+side*.21,y1,v1),F.p(u+side*.21,4.6,v1)])
def build(B):
 p=footprint(ID);F=Frame(B,1654.935,-833.3325,YAW,y=0)
 B.property=KEY+'-exterior';B.source='podium/'+KEY;B.detail=0
 door=dict(p=F.p(3,.16,0),yaw=YAW,width=1.8,height=2.35,name='Public shop entrance',venue=KEY)
 B.shell(p,.03,4.6,'sm-white',roof=False,openings=[door]);B.shell(p.buffer(.018),.03,.55,'sm-plinth',roof=False,openings=[door],solid=False)
 B.planar('sm-roof',p.buffer(-.15),4.4);B.planar('sm-floor',p,.16,True)
 frontage(B,F,11.9,'SPEEDEE MART');window(F,-1.8,6.2)
 # Angled video-poker storefront on the short adjoining mapped edge.
 A=Frame(B,(1642.844+1649.373)/2,(-832.915-835.442)/2,math.atan2(-2.527,-6.529),y=0)
 frontage(B,A,7.0,'VIDEO POKER');window(A,0,5.9)
 # Street-facing blank wall, branded plate, wall floods and exposed conduits.
 W=Frame(B,(1639.544+1642.844)/2,(-825.345-832.915)/2,math.atan2(7.57,3.3)+math.pi,y=0)
 W.box('sm-metal',(0,3.15,.1),(1.45,1.65,.18));W.box('sm-red',(0,3.32,.21),(1.3,1.1,.035));W.box('sm-yellow',(0,2.7,.21),(1.3,.25,.035))
 W.text('SPEEDEE',(0,3.65,.24),.22,'sm-white',back=True);W.text('MART',(0,3.34,.24),.24,'sm-white',back=True)
 for u in [-2.7,2.7]:W.box('sm-metal',(u,2.6,.17),(.5,.22,.35))
 for u in [1.4,1.7,2.0]:W.path('sm-pipe',[(u,.2,.1),(u,1.1,.1),(u+.2,1.3,.1),(u+.2,1.8,.1)],.025,8)
 W.text('3670',(-2.8,4.2,.08),.28,'sm-metal',back=True)
 # Ice cabinet and water vending kiosk observed beside this wall, clear of door.
 I=Frame(B,1641.7,-834.0,.2,y=.12)
 I.box('sm-white',(0,.95,0),(1.45,1.9,.85),True)
 for u in [-.36,.36]:I.box('sm-metal',(u,1,.44),(.61,1.65,.04));I.box('sm-white',(u,1,.465),(.55,1.58,.025));I.box('sm-metal',(u+.2,1,.5),(.025,.3,.035))
 I.text('ICE',(0,1.65,.5),.27,'sm-red',back=True)
 for u in [2,3]:
  W.box('sm-pipe',(u,.46,.22),(.35,.7,.25),True)
 # Conservative roof equipment; no new ground/road slabs outside the mapped shell.
 for x,z in [(1653,-823),(1658,-825)]:
  B.box('sm-metal',(x,4.7,z),(1.4,.6,1.2));B.box('sm-roof',(x,5.02,z),(1.5,.05,1.3))
 # Shop reference: checkout to left, low aisles and rear cooler wall.
 B.property=KEY+'-interior';B.source='public/'+KEY;inside=p.buffer(-.17)
 B.shell(inside,.16,3.25,'sm-cream',roof=False,openings=[door],solid=False);B.planar('sm-floor',inside,.168)
 for tri in triangles(inside):
  pts=[(x,3.25,z) for x,z in list(tri.exterior.coords)[:-1]];a=np.array(pts);B.face('sm-ceiling',pts if np.cross(a[1]-a[0],a[2]-a[0])[1]<0 else list(reversed(pts)))
 # Fixtures are inferred placements within the photographed public area.
 F.box('sm-white',(-3.8,.76,-2),(1.05,1.2,3.0),True);F.box('sm-counter',(-3.8,1.39,-2),(1.14,.09,3.12))
 F.box('sm-metal',(-3.8,1.62,-1.2),(.45,.4,.12))
 rng=random.Random(340)
 def shelf(u,v,length):
  F.box('sm-white',(u,.82,v),(.9,1.3,length),True)
  for y in [.25,.65,1.05,1.45]:
   F.box('sm-white',(u,y,v),(1.15,.055,length+.08))
   for side in [-1,1]:
    for zz in np.arange(v-length/2+.13,v+length/2-.1,.23):
     F.box('sm-stock-'+str(rng.randrange(5)),(u+side*.44,y+.16,float(zz)),(.2,.27,.17))
 for u in [0,3.2]:shelf(u,-4.7,3.0)
 # Rear merchandise chillers: glass doors with original generic bottle silhouettes.
 C=Frame(B,*[F.p(0,0,-9)[i] for i in [0,2]],YAW,y=0)
 C.box('sm-metal',(0,1.4,-.35),(10.0,2.45,.8),True)
 for u in np.arange(-4.5,5,.9):
  C.box('sm-glass',(float(u),1.4,.08),(.83,2.25,.035))
  for y in [.5,1.0,1.5,2.0]:
   C.box('sm-white',(float(u),y,.11),(.79,.035,.03))
   for dx in [-.26,0,.26]:C.lathe('sm-stock-'+str(rng.randrange(5)),float(u+dx),.13,[(y,.065),(y+.23,.065),(y+.28,.03),(y+.32,.03)],8)
  C.box('sm-metal',(float(u)+.3,1.4,.2),(.025,.65,.05))
 for u in [-2,1.5,4]:
  for v in [-2,-5.7,-8]:F.box('sm-light',(u,3.21,v),(.22,.04,1.45))
 lights=[dict(p=F.p(u,2.9,v),color=0xfff3df,power=24,range=11) for u,v in [(-2,-3),(3,-6)]]
 route=[F.p(3,.16,v) for v in [2.0,.7,-.7,-2.4]]+[F.p(1.6,.16,-2.4),F.p(1.6,.16,-7.1)]
 return dict(key=KEY,name='Speedee Mart Paradise Road',center=[p.centroid.x,0,p.centroid.y],bounds=list(p.bounds),structural=True,exteriorOnly=False,portals=[door],zones=[dict(origin=F.p(0,.16,0),yaw=YAW+math.pi,width=17,depth=11,height=3.1)],lights=lights,hotelSources=[],routes=[dict(name='Public entrance and shop aisle',points=route)])
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
