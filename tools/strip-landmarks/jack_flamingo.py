"""Original restaurant reconstruction; photographed dining character, inferred room plan."""
from common import *
KEY='jack-flamingo';IDS=['way/445000146']
def build(B):
 p=footprint(IDS[0]);B.property=KEY+'-exterior';B.source='retail/'+KEY;B.detail=0
 R=Frame(B,2352.8,110.8,-math.pi/2,y=0)
 door=dict(p=R.p(0,.28,0),yaw=R.yaw,width=1.9,height=2.9,name='Jack public dining room',venue=KEY)
 opening=dict(p=R.p(0,.28,0),yaw=R.yaw,width=7.2,height=3.5)
 B.shell(p,.02,4.8,'jf-stucco',roof=False,openings=[opening]);B.planar('jf-membrane',p,4.8)
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  dx,dz=b[0]-a[0],b[1]-a[1];L=math.hypot(dx,dz);F=Frame(B,(a[0]+b[0])/2,(a[1]+b[1])/2,math.atan2(-dz,dx),y=0)
  F.box('jf-trim',(0,4.82,0),(L+.08,.18,.35));F.box('jf-dark',(0,4.47,0),(L,.22,.19))
  if F.x>2351:continue
  F.box('jf-dark',(0,.43,0),(L,.86,.17))
  for y in [1.0,3.7]:F.box('jf-trim',(0,y,0),(L,.10,.18))
  if L>10:
   for u in np.linspace(-L/2+2,L/2-2,max(2,int(L/3.5))):
    for side in [-1,1]:
     F.box('jf-glass',(float(u),2.3,side*.13),(2.6,2.6,.05))
     for x in [-1.34,0,1.34]:F.box('jf-frame',(float(u+x),2.3,side*.18),(.065,2.74,.05))
     for y in [.95,3.65]:F.box('jf-frame',(float(u),y,side*.18),(2.73,.06,.05))
 # East entry architectural tower; exact bay positions fitted to mapped facade.
 for u in [-1.65,1.65]:R.box('jf-dark',(u,1.85,-.28),(.65,3.7,.45),True)
 R.box('jf-red',(0,4.85,-.28),(4.0,2.3,.45));R.box('jf-trim',(0,6.03,-.28),(4.3,.16,.65))
 R.box('jf-red',(0,4.9,-.56),(1.45,1.45,.08));R.text('Jack',(0,4.86,-.62),.58,'jf-letter');R.text('in the box',(0,4.47,-.62),.22,'jf-letter')
 R.box('jf-frame',(0,3.4,-.9),(2.35,.15,1.7));
 for u in [-1,1]:R.tube('jf-frame',(u,3.4,-1.65),(u,3.8,-.3),.025,6)
 for u in [-2.3,2.3]:R.box('jf-clear',(u,1.95,0),(2.6,3.25,.04),True)
 for u in [-3.6,-.95,.95,3.6]:R.box('jf-frame',(u,1.95,0),(.075,3.35,.12),True)
 R.box('jf-frame',(0,3.65,0),(7.2,.09,.12))
 # Open central doorway; threshold connects to existing ground by a gentle ramp.
 B.upface('jf-paving',[R.p(-1.15,.01,-3),R.p(1.15,.01,-3),R.p(1.15,.28,.2),R.p(-1.15,.28,.2)],True)
 # South drive-through pickup bay and awning, supported by aerial projection.
 S=Frame(B,2341.5,116.0,0,y=0)
 S.box('jf-dark',(0,1.7,.05),(3.5,3.4,.22));S.box('jf-glass',(0,2,.19),(2.4,1.5,.06))
 for u in [-1.2,0,1.2]:S.box('jf-frame',(u,2,.24),(.06,1.55,.055))
 S.box('jf-trim',(0,1.2,.4),(2.7,.15,.6));S.box('jf-frame',(0,3.2,.5),(3.6,.16,1.0))
 Q=Frame(B,0,0,0,y=0)
 for x in [2334,2341,2348]:
  Q.box('jf-equipment',(x,5.12,111),(2.4,.65,1.7))
  for z in np.arange(110.4,111.61,.17):Q.box('jf-frame',(x,5.46,float(z)),(2.0,.025,.05))
 # Public dining room: no unsupported service-counter or private kitchen layout.
 B.property=KEY+'-interior';B.source='interior/'+KEY;B.detail=1
 room=R.poly([(-3.6,.08),(3.6,.08),(3.6,10.7),(-3.6,10.7)])
 B.shell(room,.28,3.4,'jf-wall',roof=False,openings=[opening]);B.planar('jf-floor',room,.28,True);B.planar('jf-ceiling',room,3.4)
 for u in np.arange(-3.6,3.61,.6):R.box('jf-grout',(float(u),.284,5.4),(.014,.008,10.6));R.box('jf-grid',(float(u),3.385,5.4),(.022,.02,10.6))
 for v in np.arange(.1,10.71,.6):R.box('jf-grout',(0,.284,float(v)),(7.2,.008,.014));R.box('jf-grid',(0,3.385,float(v)),(7.2,.02,.022))
 # Window-height dining ledge from the April2026 frame; furniture is original.
 R.box('jf-table',(-2.4,1.12,.5),(2.25,.08,.55))
 def chair(u,v,reverse=False):
  for x in [-.22,.22]:
   for z in [-.23,.23]:R.box('jf-alloy',(u+x,.51,v+z),(.035,.46,.035))
  R.box('jf-alloy',(u,.76,v),(.51,.07,.51))
  z=v+(.24 if reverse else -.24)
  for x in [-.24,.24]:R.box('jf-alloy',(u+x,1.02,z),(.04,.52,.04))
  R.box('jf-alloy',(u,1.27,z),(.52,.045,.045))
  for x in [-.12,0,.12]:R.box('jf-alloy',(u+x,1.02,z),(.025,.43,.035))
 def table(u,v):
  R.box('jf-frame',(u,.33,v),(.65,.1,.65));R.box('jf-alloy',(u,.68,v),(.08,.65,.08))
  # Round-corner red tabletop authored as a beveled footprint.
  shape=box(u-.58,v-.4,u+.58,v+.4).buffer(.10,quad_segs=4)
  top=R.poly(list(shape.exterior.coords));B.planar('jf-table',top,1.05,True);B.shell(top,.99,1.05,'jf-alloy',roof=False,solid=False)
  chair(u,v-.8);chair(u,v+.8,True)
 for u,v in [(-2.35,3.2),(2.35,3.2),(-2.35,6.0),(2.35,6.0),(-2.35,8.8),(2.35,8.8)]:table(u,v)
 for u in [-2.8,0,2.8]:
  R.tube('jf-frame',(u,3.4,1.05),(u,2.52,1.05),.013,6)
  R.lathe('jf-pendant',u,1.05,[(2.23,.08),(2.28,.12),(2.48,.09),(2.56,.04)],16)
 for u in [-2,2]:
  for v in [4.8,8.4]:R.box('jf-lamp',(u,3.38,v),(.45,.025,.45))
 routes=[dict(name='Public dining entry and return',points=[R.p(0,.28,v) for v in [-6,-3,-1,1,4.5,7.5,9.8]]),dict(name='South pickup frontage',points=[[2327,.24,120],[2341,.24,120],[2356,.24,120]])]
 return dict(key=KEY,name='Jack in the Box East Flamingo',center=[2341,0,111],bounds=list(p.bounds),structural=True,hotelSources=[],exteriorOnly=False,portals=[door],zones=[dict(origin=R.p(0,.28,0),yaw=R.yaw,width=7.3,depth=10.9,height=3.5)],lights=[dict(p=R.p(u,3.05,v),color=0xffe4b8,power=3,range=6) for u,v in [(-2,2),(2,2),(-2,8),(2,8)]],routes=routes)
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
