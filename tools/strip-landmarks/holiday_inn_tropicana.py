"""Original Holiday Inn Express facade and photo-supported public communal room."""
from common import *
from shapely.geometry import box as clipbox
KEY='holiday-inn-tropicana';IDS=['way/118363803']
def build(B):
 p=footprint(IDS[0]);tower=p.intersection(clipbox(680,1813.8,730,1900));R=Frame(B,704,1813.8,0,y=0)
 B.property=KEY+'-exterior';B.source='hotel/'+KEY;B.detail=0
 op=dict(p=R.p(0,.22,0),yaw=0,width=6,height=3.5)
 B.shell(tower,.02,21.5,'hi-gray',roof=False,openings=[op]);B.planar('hi-membrane',tower,21.5)
 ring=list(tower.exterior.coords)
 for a,b in zip(ring,ring[1:]):
  dx,dz=b[0]-a[0],b[1]-a[1];L=math.hypot(dx,dz);F=Frame(B,(a[0]+b[0])/2,(a[1]+b[1])/2,math.atan2(-dz,dx),y=0)
  F.box('hi-white',(0,21.15,0),(L,.7,.24))
  if L<4:continue
  for side in [-1,1]:
   if L>35:
    for u in [-L*.38,L*.05]:
     F.box('hi-orange',(u,12.8,side*.2),(2,17.4,.18))
    F.box('hi-navy',(L*.05-5,12.3,side*.07),(7.8,17.9,.12))
    F.box('hi-white',(-L/2+1,12.4,side*.26),(1.8,18.2,.5));F.box('hi-white',(L/2-1,12.4,side*.26),(1.8,18.2,.5))
   else:
    F.box('hi-orange',(-L*.25,12.8,side*.06),(L*.48,17.4,.1))
    F.box('hi-white',(L/2-.7,12.3,side*.24),(1.3,18.2,.48));F.box('hi-white',(-L/2+.7,12.3,side*.24),(1.3,18.2,.48))
   for y in [4.6,7.85,11.1,14.35,17.6,20.7]:F.box('hi-joint',(0,y,side*.10),(L,.018,.02))
  n=max(1,int((L-2.5)/3.5))
  for u in np.linspace(-L/2+2,L/2-2,n):
   for y in [5.65,8.9,12.15,15.4,18.65]:
    for side in [-1,1]:
     F.box('hi-frame',(float(u),y,side*.34),(1.85,2.0,.08));F.box('hi-glass',(float(u),y+.08,side*.40),(1.68,1.75,.02))
     F.box('hi-frame',(float(u),y+.08,side*.43),(.045,1.75,.02));F.box('hi-vent',(float(u),y-1.10,side*.36),(1.85,.32,.08))
 # North canopy is open, not a six-storey extrusion of the mapped roof projection.
 R.box('hi-dark',(0,4.25,-6.3),(13.5,.32,12.8));R.box('hi-wood',(0,4.07,-6.3),(13.1,.035,12.4))
 for u in [-5.7,5.7]:
  for v in [-11,-2]:
   R.box('hi-stone',(u,1.25,v),(.72,2.5,.72),True);R.box('hi-dark',(u,3.25,v),(.24,1.5,.24),True)
 for u in [-4,0,4]:
  for v in [-10,-5]:R.box('hi-lamp',(u,4.04,v),(.15,.025,.15))
 for u in [-2.1,2.1]:R.box('hi-clear',(u,1.92,.02),(1.8,3.4,.035),True)
 for u in [-3,-1.2,1.2,3]:R.box('hi-frame',(u,1.92,.02),(.08,3.4,.12),True)
 R.box('hi-frame',(0,3.62,.02),(6,.08,.12))
 B.upface('hi-paving',[R.p(-1.5,.01,-4),R.p(1.5,.01,-4),R.p(1.5,.22,.3),R.p(-1.5,.22,.3)],True)
 R.box('hi-orange',(0,20.2,-.58),(8.0,1.7,.12));R.text('Holiday Inn',(0,20.35,-.68),.63,'hi-sign');R.text('EXPRESS & SUITES',(0,19.76,-.68),.38,'hi-sign');R.text('175',(6.2,20.9,-.52),.38,'hi-dark')
 for z in [1826,1844,1864]:
  F=Frame(B,706,z,0,y=0);F.box('hi-equipment',(0,22.0,0),(2.5,1,2));F.box('hi-vent',(0,22.51,0),(2.1,.03,1.6))
 for u in [-7,7]:R.plant(u,-2)
 B.property=KEY+'-interior';B.source='interior/'+KEY;B.detail=1
 room=R.poly([(-5,.05),(5,.05),(5,15),(-5,15)])
 B.shell(room,.22,3.8,'hi-wall',roof=False,openings=[{k:v for k,v in op.items() if k!='yaw'}]);B.planar('hi-floor',room,.22,True);B.planar('hi-ceiling',room,3.8)
 for u in np.arange(-4.9,5,.32):R.box('hi-joint',(float(u),.223,7.5),(.006,.004,14.8))
 for u in [-3.7,3.7]:
  R.box('hi-wood',(u,3.66,7.5),(2.6,.15,14.8))
  for v in [4,9,13]:
   R.box('hi-white',(u,1.9,v),(.3,3.4,.3),True)
   R.box('hi-blue',(u,1.95,v-.17),(.22,2.9,.035))
   for y in [.6,3.2]:
    for du in [-.07,.07]:R.box('hi-steel',(u+du,y,v-.194),(.025,.025,.01))
 # Communal high tables and wood chairs, matched to reference types and colors.
 for u in [-2.0,2.0]:
  for v in [5,10]:
   R.box('hi-counter',(u,1.2,v),(1.45,.10,2.65))
   for du in [-.55,.55]:
    for dv in [-1.1,1.1]:R.box('hi-wood',(u+du,.7,v+dv),(.15,.96,.15),True)
   for side in [-1,1]:
    for dv in [-.8,.8]:
     x=u+side*1.05;z=v+dv
     R.box('hi-leather',(x,.84,z),(.5,.12,.5));R.box('hi-leather',(x+side*.23,1.22,z),(.08,.62,.5))
     for dx in [-.2,.2]:
      for dz in [-.2,.2]:R.box('hi-wood',(x+dx,.51,z+dz),(.045,.58,.045))
     R.box('hi-wood',(x,.45,z),(.5,.05,.05))
   R.box('hi-copper',(u,1.55,v),(.05,.65,.05));R.box('hi-copper',(u,1.88,v),(.45,.12,.25))
 # Far-wall banquette and display, visible in official communal lobby view.
 R.box('hi-blue',(0,.61,14.3),(7,.45,.9),True);R.box('hi-seatback',(0,1.15,14.71),(7,.95,.2))
 for u in np.arange(-3.4,3.5,.15):R.box('hi-wood',(float(u),1.15,14.59),(.022,.9,.025))
 R.box('hi-dark',(0,2.45,14.94),(1.7,.95,.035))
 for u in [-3,0,3]:
  for v in [2,7,12]:R.box('hi-lamp',(u,3.78,v),(.16,.025,.16))
 door=dict(p=R.p(0,.22,0),yaw=0,width=2.4,height=3.4,name='Holiday Inn public lobby',venue=KEY)
 return dict(key=KEY,name='Holiday Inn Express East Tropicana',center=[705,0,1835],bounds=list(p.bounds),structural=True,hotelSources=[],exteriorOnly=False,portals=[door],zones=[dict(origin=R.p(0,.22,0),yaw=0,width=10.2,depth=15.2,height=3.9)],lights=[dict(p=R.p(u,3.4,v),color=0xffefd8,power=4,range=8) for u,v in [(-2,3),(2,3),(-2,11),(2,11)]],routes=[dict(name='Canopy to communal lobby',points=[R.p(0,.22,v) for v in [-15,-5,-1,1,4,8,12.5]])])
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
