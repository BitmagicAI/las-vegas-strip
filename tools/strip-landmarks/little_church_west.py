"""Cedar chapel and separate office wing. Current satellite placement, historic
42x19ft chapel dimensions; height estimates from owner's exterior photograph."""
from common import *
from forum_shops import facade_frame
KEY='littleChurchWest'
def lancet(F,x,z,base,w,h):
 pts=[(x-w/2,base,z),(x+w/2,base,z),(x+w/2,base+h-w*.65,z),(x,base+h,z),(x-w/2,base+h-w*.65,z)]
 F.b.face('cw-glass',[F.p(*q) for q in pts[:3]])
 for i in range(2,len(pts)-1):F.b.face('cw-glass',[F.p(*pts[0]),F.p(*pts[i]),F.p(*pts[i+1])])
 F.path('cw-trim',pts+[pts[0]],.045,6)
 F.tube('cw-trim',(x,base,z-.025),(x,base+h-.12,z-.025),.025,6)
 for y in np.arange(base+.3,base+h-.2,.3):F.tube('cw-trim',(x-w*.35,y,z-.03),(x+w*.35,y,z-.03),.016,5)
def roof(F,w,d,base,rise,z=0):
 for side in [-1,1]:
  pts=[F.p(side*w/2,base,z),F.p(0,base+rise,z),F.p(0,base+rise,z+d),F.p(side*w/2,base,z+d)]
  F.b.face('cw-shingles',pts,False)
 for zz in [z,z+d]:
  F.b.face('cw-cedar',[F.p(-w/2,base,zz),F.p(w/2,base,zz),F.p(0,base+rise,zz)])
  F.path('cw-trim',[(-w/2,base,zz),(0,base+rise,zz),(w/2,base,zz)],.09,8)
 for y in np.arange(.12,rise,.22):
  x=w/2*(1-y/rise)
  for side in [-1,1]:F.path('cw-roof-edge',[(side*x,base+y+.015,z),(side*x,base+y+.015,z+d)],.016,5)
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/chapel';B.detail=0
 shapes=sorted(parts(footprint('relation/6138883')),key=lambda p:p.area);office=shapes[-1]
 F=Frame(B,56.9,3333.8,2.098,y=.14)
 # 19x42ft historic envelope, northeast alignment follows mapped small chapel.
 F.box('cw-cedar',(0,1.65,6.4),(5.79,3.3,12.8),True)
 roof(F,6.2,13.15,3.3,2.5,-.18)
 for x in np.arange(-2.85,2.9,.22):
  h=3.3+2.5*(1-abs(x)/3.1)
  F.box('cw-batten',(x,h/2,-.045),(.035,h,.07))
 for side in [-1,1]:
  for z in np.arange(.1,12.8,.24):F.box('cw-batten',(side*2.93,1.65,z),(.06,3.3,.035))
  # Five historic side windows each side, 30x48in.
  for z in np.linspace(1.5,11.3,5):
   G=Frame(B,*[F.p(side*2.96,0,z)[i] for i in [0,2]],F.yaw-side*math.pi/2,y=.14)
   lancet(G,0,-.025,1.12,.76,1.22)
 F.box('cw-door',(0,1.02,-.09),(1.22,2.04,.12))
 for x in [-.65,0,.65]:F.box('cw-trim',(x,1.06,-.17),(.07,2.12,.12))
 for x,h in [(-.52,1.28),(0,1.83),(.52,1.28)]:lancet(F,x,-.14,3.02,.42,h)
 roof(F,2.15,.95,2.26,.17,-.95)
 for x in [-.95,.95]:F.tube('cw-trim',(x,2.3,-.88),(x,1.66,-.1),.065,8)
 # Offset octagonal tower with open belfry and tapered shingled spire.
 tx=2.8;tz=.65
 F.lathe('cw-cedar',tx,tz,[(0,.91),(3.2,.91),(3.9,.62),(4.2,.62)],8)
 for x in [-.36,.36]:lancet(F,tx+x,-.24,2.5,.3,1.08)
 F.lathe('cw-shingles',tx,tz,[(4.15,.86),(4.5,.65)],8)
 for j in range(8):
  a=j*math.tau/8;F.tube('cw-trim',(tx+.58*math.cos(a),4.45,tz+.58*math.sin(a)),(tx+.58*math.cos(a),5.75,tz+.58*math.sin(a)),.075,8)
 F.lathe('cw-shingles',tx,tz,[(5.72,.85),(5.87,.85),(8.9,.04)],8)
 for y in np.arange(6,8.8,.22):
  r=.85*(8.9-y)/3.03;F.lathe('cw-roof-edge',tx,tz,[(y,r+.018),(y+.025,r+.018)],8)
 F.tube('cw-metal',(tx,8.85,tz),(tx,9.45,tz),.025,6)
 # Entry walk with a smooth shallow approach; office remains a separate building.
 B.source='podium/office';B.shell(office,.04,3.4,'cw-office',roof=False);B.planar('cw-office-roof',office,3.4,True)
 for a,b in zip(list(office.exterior.coords),list(office.exterior.coords)[1:]):
  G,L,_,_=facade_frame(B,a,b,office,.06);G.box('cw-trim',(L/2,3.42,-.04),(L,.18,.18))
  if L>10:
   for u in np.arange(2,L-1,4):
    G.box('cw-office-glass',(u,1.7,-.05),(1.5,1.5,.08))
    for dx in [-.8,.8]:G.box('cw-office',(u+dx,1.7,-.12),(.08,1.65,.1))
 for x,z in [(90,3324),(111,3324),(124,3335)]:B.box('cw-metal',(x,3.7,z),(1.6,.6,1.2))
 B.source='podium/garden';W=Frame(B,0,0,y=0)
 site=box(39,3314,132,3364);chapel=F.poly([(-3.8,-1.1),(3.8,-1.1),(3.8,13.2),(-3.8,13.2)])
 garden=box(40,3315,119,3341).difference(office).difference(chapel)
 walk=LineString([(40,3338),(50,3338),(56.9,3333.8)]).buffer(1.1).union(LineString([(57,3337),(79,3337),(84,3331)]).buffer(1.15))
 for x in range(39,132,4):
  for z in range(3314,3364,4):
   cell=box(x,z,x+4,z+4).intersection(site).difference(office).difference(chapel)
   B.planar('cw-asphalt',cell.difference(garden),.02,True)
   B.planar('cw-grass',cell.intersection(garden).difference(walk),.08,True)
   B.planar('cw-paving',cell.intersection(walk),.1,True)
 B.planar('cw-paving',chapel,.12,True)
 for x in np.arange(48,126,2.8):W.box('cw-line',(x,.15,3358),(.07,.025,4.6))
 # Roadside shaped sign and small timber hitching-post sign.
 S=Frame(B,43,3325,math.pi/2,y=0)
 S.box('cw-cedar',(0,2.8,0),(.55,5.6,.5),True)
 outline=[(-1.45,3.7),(-1.4,6.25),(-.7,6.3),(0,6.5),(.7,6.3),(1.4,6.25),(1.45,3.7),(0,3.35)]
 for i in range(1,len(outline)-1):B.face('cw-sign',[S.p(outline[j][0],outline[j][1],-.3) for j in [0,i,i+1]])
 S.path('cw-gold',[(x,y,-.32) for x,y in outline+[outline[0]]],.07,8)
 for text,y,size in [('LITTLE',5.98,.39),('CHURCH',5.55,.4),('OF THE',5.18,.26),('WEST',4.8,.42),('WEDDING',4.26,.36),('CHAPEL',3.87,.39)]:S.text(text,(0,y,-.35),size,'cw-trim')
 H=Frame(B,53,3339,2.098,y=0)
 for x in [-1.1,1.1]:H.tube('cw-batten',(x,0,0),(x,1.2,0),.08,8)
 H.tube('cw-batten',(-1.2,1.15,0),(1.2,1.15,0),.09,8);H.box('cw-sign',(0,.65,0),(1.8,.65,.1));H.text('WEDDING CHAPEL',(0,.65,-.065),.18,'cw-trim')
 B.detail=0
 return dict(key=KEY,name='Little Church of the West exterior',center=[85,0,3337],bounds=[38,3313,133,3365],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
