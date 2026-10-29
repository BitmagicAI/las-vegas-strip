"""Original, reference-informed print shop. Public layout is fitted, not measured."""
from common import *
KEY='fedex-hughes';IDS=['way/159969363'];YAW=.2467

def build(B):
 original=footprint(IDS[0]);F=Frame(B,1632.055,-.318,YAW,y=0)
 arc=[(-7.7+4.5*math.cos(a),-12.3+4.5*math.sin(a)) for a in np.linspace(math.pi,1.5*math.pi,17)]
 p=F.poly(arc+[(12.2,-16.8),(12.2,16.8),(-12.2,16.8)])
 c=F.p(-7.7-4.5/math.sqrt(2),.2,-12.3-4.5/math.sqrt(2))
 D=Frame(B,c[0],c[2],YAW-3*math.pi/4,y=0)
 B.property=KEY+'-exterior';B.source='retail/'+KEY;B.detail=0
 door=dict(p=D.p(0,.2,0),yaw=D.yaw,width=2.4,height=2.65,name='FedEx Office public entry',venue=KEY)
 glass=dict(p=D.p(0,.2,0),yaw=D.yaw,width=9,height=3.35)
 B.shell(p,.02,6,'fx-stucco',roof=False,openings=[glass]);B.planar('fx-membrane',p,6)
 # Original curved tiled entry wall, matching the visible northwest corner.
 tile_arc=[(-7.7+(u+7.7)*1.014,-12.3+(v+12.3)*1.014) for u,v in arc]
 for (a,b) in zip(tile_arc,tile_arc[1:]):
  B.face('fx-tile',[F.p(*[a[0],3.65,a[1]]),F.p(b[0],3.65,b[1]),F.p(b[0],8,b[1]),F.p(a[0],8,a[1])])
  for y in [7.9,8.08]:F.tube('fx-trim',(a[0],y,a[1]),(b[0],y,b[1]),.09,8)
 for u in [-1.26,1.26]:D.box('fx-black',(u,1.65,.04),(.09,2.9,.15))
 for a,b in [(-4.3,-1.3),(1.3,4.3)]:
  D.box('fx-clear',((a+b)/2,1.9,-.22),(b-a,3.3,.035),True)
  for u in np.arange(a,b,.9):D.box('fx-black',(float(u),1.9,-.17),(.055,3.3,.08))
 D.box('fx-clear',(0,3.15,-.22),(2.4,.55,.035),True)
 D.box('fx-black',(0,2.9,-.15),(8.6,.08,.1))
 D.box('fx-black',(0,3.5,.65),(9.4,.22,1.6))
 for u in [-3.5,3.5]:D.tube('fx-black',(u,3.63,1.35),(u,5.15,-.05),.025,8)
 D.text('FedEx Office',(0,6.1,.18),.7,'fx-letter',back=True)
 for u in [-4.8,4.8]:
  D.box('fx-black',(u,2.3,0),(.25,.65,.12));D.box('fx-lamp',(u,2.3,.07),(.17,.5,.05))
 landing=D.poly([(-4.5,-1),(4.5,-1),(4.5,1.8),(-4.5,1.8)])
 B.planar('fx-concrete',landing,.2,True)
 B.upface('fx-concrete',[D.p(-1.2,.2,1.8),D.p(1.2,.2,1.8),D.p(1.2,.29,3.8),D.p(-1.2,.29,3.8)],True)
 for u in [-12.2,12.2]:
  F.box('fx-trim',(u,5.86,2),(.16,.24,29))
  for v in [-7,1,9]:
   F.box('fx-panel',(u,2.6,v),(.11,4.3,3.5))
 for v in [-9,-3,3,9]:
  F.box('fx-steel',(-8,6.55,v),(2.5,1.05,2.3))
  for yy in np.arange(6.15,6.95,.12):F.box('fx-black',(-8,float(yy),v+1.16),(2.2,.035,.025))
 F.box('fx-steel',(3,1.6,16.85),(1.8,3,.08),True)
 F.box('fx-black',(3.65,1.5,16.93),(.05,.25,.05))
 # Public area: exact layout unmeasured; retain a clear entry, counter and copier aisle.
 B.property=KEY+'-interior';B.source='interior/'+KEY;B.detail=1
 room=p.buffer(-.2).intersection(F.poly([(-12,-17),(12,-17),(12,6),(-12,6)]))
 B.shell(room,.2,3.9,'fx-wall',roof=False,openings=[glass]);B.planar('fx-carpet',room,.2,True);B.planar('fx-ceiling',room,3.9)
 F.box('fx-purple',(0,2.05,5.79),(23.4,3.7,.06))
 # Suspended tile grid and restrained light panels; existing venue light pool only.
 for u in np.arange(-10,12,1.2):F.box('fx-grid',(float(u),3.86,-4.5),(.018,.02,20))
 for v in np.arange(-14,6,1.2):F.box('fx-grid',(0,3.86,float(v)),(23,.02,.018))
 for u in [-7,0,7]:
  for v in [-11,-5,1]:F.box('fx-lamp',(u,3.84,v),(1.1,.025,.55))
 def counter(u,v,w,d):
  F.box('fx-cabinet',(u,.75,v),(w,1.1,d),True);F.box('fx-top',(u,1.34,v),(w+.12,.08,d+.12),True)
  for x in np.arange(u-w/2+.35,u+w/2,.7):
   F.box('fx-edge',(float(x),.8,v+d/2+.02),(.015,.95,.02))
   F.box('fx-steel',(float(x)+.22,.95,v+d/2+.04),(.025,.16,.04))
 counter(2,-2,8,1.3);counter(2,2.7,8,2.1)
 # Registers, keyboards and shallow shelving facing the customer aisle.
 for u in [-.6,4.6]:
  F.box('fx-black',(u,1.5,-2),(.08,.28,.1));F.box('fx-black',(u,1.8,-2),(.7,.43,.09));F.box('fx-screen',(u,1.8,-2.05),(.62,.35,.015))
  F.box('fx-black',(u,1.41,-2.4),(.52,.035,.19))
  for x in np.arange(-.2,.24,.05):
   for z in [-2.44,-2.38]:F.box('fx-key',(u+float(x),1.43,z),(.035,.009,.035))
 for y in [.45,.75,1.05]:
  F.box('fx-top',(2,y,-2.72),(7.8,.04,.22))
  for u in np.arange(-1.7,6,.3):F.box('fx-package',(float(u),y+.1,-2.73),(.22,.16,.12))
 def copier(u,v):
  cp=F.p(u,0,v);C=Frame(B,cp[0],cp[2],YAW-math.pi/2,y=0)
  def box(mat,pos,size,solid=False):C.box(mat,(pos[0]-u,pos[1],pos[2]-v),size,solid)
  box('fx-cabinet',(u,.8,v),(1.1,1.2,.9),True)
  for y in [.38,.63,.88]:
   box('fx-panel',(u,y,v-.46),(.97,.2,.035));box('fx-black',(u,y+.04,v-.49),(.35,.035,.025))
  box('fx-black',(u,1.43,v),(1.12,.06,.93));box('fx-cabinet',(u,1.55,v),(.92,.16,.77))
  box('fx-paper',(u,1.65,v),(.65,.025,.45));box('fx-black',(u+.6,1.3,v),(.25,.08,.35))
  box('fx-screen',(u+.6,1.35,v),(.21,.025,.28))
  box('fx-black',(u-.65,1.12,v),(.3,.04,.45));box('fx-paper',(u-.65,1.16,v),(.27,.025,.4))
 for v in [-5,-1,3]:copier(-9,v)
 # Packing supplies and paper shelves, original generic cartons without copied labels.
 for u in [8.4,10.5]:
  F.box('fx-cabinet',(u,1.15,1),(1.5,1.9,.6),True)
  for y in [.35,.8,1.25,1.7]:
   F.box('fx-top',(u,y,.63),(1.45,.04,.45))
   for dx in [-.45,0,.45]:
    F.box('fx-carton',(u+dx,y+.18,.6),(.37,.32,.3));F.box('fx-paper',(u+dx,y+.18,.44),(.21,.09,.012))
 for u,t in [(-8,'SELF SERVICE'),(1,'PRINT & SHIP'),(9,'PACKING')]:F.text(t,(u,2.8,5.72),.23,'fx-letter',back=False)
 # Workstations and central cutting/packing table detail.
 for u in [-1,2,5]:
  F.box('fx-paper',(u,1.4,2.7),(1.3,.025,.8));F.box('fx-steel',(u,1.47,2.7),(.025,.06,.8))
 entry=D.p(0,.2,-1.5)
 routes=[dict(name='Entrance and service counter',points=[D.p(0,.28,3.6),D.p(0,.2,1.2),entry,F.p(-6,.2,-9),F.p(-6,.2,-5),F.p(2,.2,-5)]),dict(name='Self-service copiers',points=[F.p(-6,.2,v) for v in [-9,-5,-1,3]]),dict(name='Packing aisle',points=[F.p(u,.2,-5) for u in [2,6,9]])]
 return dict(key=KEY,name='FedEx Office Hughes Center',center=[p.centroid.x,0,p.centroid.y],bounds=list(p.bounds),structural=True,hotelSources=[],exteriorOnly=False,portals=[door],zones=[dict(origin=F.p(0,.2,-17),yaw=YAW,width=25,depth=24,height=5)],lights=[dict(p=F.p(u,3.5,v),color=0xf1f2ee,power=5,range=11) for u,v in [(-6,-10),(5,-10),(-6,0),(5,0)]],routes=routes)
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
