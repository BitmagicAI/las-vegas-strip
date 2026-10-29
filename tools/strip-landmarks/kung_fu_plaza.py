"""Original reference-led restaurant. Dimensions and public room layout are estimates.
January2026 Street View establishes the east front; public photo establishes dining character.
Private service rooms and northern cafe interior remain closed.
"""
from common import *
KEY='kung-fu-plaza';ID='way/1391666928';YAW=math.pi/2+.02411

def build(B):
 p=footprint(ID);F=Frame(B,-1568.186,-1120.5,YAW,y=0)
 B.property=KEY+'-exterior';B.source='podium/'+KEY;B.detail=0
 entry=dict(p=F.p(-2,.16,.12),yaw=YAW,width=1.9,height=2.5,name='Kung Fu dining entrance',venue=KEY)
 B.shell(p,.12,4.5,'kf-stucco',roof=False,openings=[entry]);B.planar('kf-roof',p,4.48)
 B.planar('kf-stone',p,.16,True)
 # Recessed east storefront, masonry panels and round terracotta columns.
 F.box('kf-stone',(-.5,.08,1),(34,.16,2.1),True)
 for u in [-15,-9,4,11,15]:
  F.box('kf-frame',(u,1.65,.19),(3.2,2.4,.13));F.box('kf-glass',(u,1.65,.28),(3.04,2.22,.035))
  for dx in [-.5,.5]:F.box('kf-frame',(u+dx,1.65,.32),(.045,2.3,.045))
 for u in [-17,-6,1,8,17]:
  F.lathe('kf-terra',u,.75,[(.16,.34),(.35,.34),(.48,.25),(3.35,.25),(3.48,.38),(3.64,.38)],24)
 F.box('kf-terra',(-4.5,4.08,.6),(25,1.05,.6))
 F.box('kf-cream',(-4.5,3.49,.7),(25,.15,.85))
 F.box('kf-terra',(12.5,4.42,.6),(9,1.7,.6))
 F.text('KUNG FU',(-9,3.91,.96),.60,'kf-gold',back=True)
 F.text('Thai & Chinese',(-.4,4.27,.96),.35,'kf-gold',back=True)
 F.text('RESTAURANT',(-.4,3.84,.96),.36,'kf-gold',back=True)
 F.text('Since 1973',(-.4,3.58,.97),.18,'kf-gold',back=True)
 F.text('PowerSoul',(12.4,4.6,.97),.46,'kf-burgundy',back=True)
 F.text('Cafe',(12.4,4.02,.97),.4,'kf-burgundy',back=True)
 # Original curved tile courses. Curved eaves rise at both ends, with no copied imagery.
 def roof(u0,u1,y):
  for u in np.arange(u0,u1,.3):
   x=min(float(u)+.3,u1);curve=.58*(max(0,abs((u+ x)/2-(u0+u1)/2)-(u1-u0)/2+2)/2)**2
   for i in range(8):
    v0=-3.8+i*.64;v1=v0+.64
    def yy(v):return y+.8*((v-1.32)/5.12)**2+curve
    B.face('kf-tile',[F.p(u,yy(v0),v0),F.p(x,yy(v0),v0),F.p(x,yy(v1),v1),F.p(u,yy(v1),v1)])
    F.tube('kf-tile-rib',(u,yy(v0)+.025,v0),(u,yy(v1)+.025,v1),.045,6)
  F.path('kf-cream',[(u,y+.58*(max(0,abs(u-(u0+u1)/2)-(u1-u0)/2+2)/2)**2,1.32) for u in np.linspace(u0,u1,55)],.09)
 roof(-17,8,4.68);roof(8,17,5.38)
 # Small raised hip/crest behind the long restaurant eave, visible in January2026.
 for a,b in [((-8,5.35,-3.7),(-4.5,6.25,-2.8)),((-4.5,6.25,-2.8),(-1,5.35,-3.7))]:
  F.path('kf-tile-rib',[a,b],.09,10)
 B.face('kf-terra',[F.p(-8,5.35,-3.7),F.p(-4.5,6.25,-2.8),F.p(-1,5.35,-3.7)])
 for u0,u1,yy in [(-17,8,4.68),(8,17,5.38)]:
  for u in [u0,u1]:
   B.face('kf-tile',[F.p(u,yy+.58,1.32),F.p(u,yy+1.38,-3.8),F.p(u,4.48,-4.4)])
 for u in [8,17]:
  F.path('kf-cream',[(u,5.4,1.3),(u,5.55,1.55),(u,5.9,1.7),(u,6.15,1.62)],.14)
 for u in [-13,5,13]:
  F.box('kf-brick',(u,.43,1.85),(5,.54,.55),True)
  F.box('kf-soil',(u,.72,1.85),(4.8,.035,.39))
  for k in range(11):
   a=u-2.1+k*.42
   F.tube('kf-wood',(a,.72,1.85),(a,1.2,1.85),.025,6)
   for j in range(15):
    ang=j*2.4+k;rr=.12+.1*(j%3);vv=1.85+rr*math.cos(ang);uu=a+rr*math.sin(ang);h=.9+.23*(j%4)/3
    B.face('kf-leaf',[F.p(uu-.13,h,vv),F.p(uu,h+.09,vv-.08),F.p(uu+.13,h+.03,vv),F.p(uu,h-.04,vv+.07)])
 for u in [-10,0,10]:
  F.box('kf-metal',(u,4.85,-9),(1.5,.7,1.25))
  for k in range(7):F.box('kf-frame',(u,5.21,-9.5+k*.16),(1.3,.025,.04))
 # Streamed public dining room. Layout inferred within southern tenant envelope.
 B.property=KEY+'-interior';B.source='public/'+KEY
 F.box('kf-carpet',(-4.5,.17,-5.5),(24,.025,10.7))
 for u in [-16.6,7.5]:F.box('kf-cream',(u,1.8,-5.5),(.2,3.3,10.8),True)
 F.box('kf-cream',(-4.5,1.8,-10.85),(24,3.3,.2),True)
 F.box('kf-ceiling',(-4.5,3.5,-5.5),(24,.15,10.8))
 for u in np.arange(-16,8,1.2):F.box('kf-burgundy',(float(u),3.39,-5.5),(.04,.04,10.7))
 for v in np.arange(-10.5,0,1.2):F.box('kf-burgundy',(-4.5,3.39,float(v)),(24,.04,.04))
 for u in [-12,-4,4]:
  F.box('kf-cream',(u,3.18,-5.5),(.22,.35,10.7))
  for v in [-2,-9.7]:F.box('kf-cream',(u,1.75,v),(.25,3.2,.25),True)

 # Inward-facing street glazing/reveals align with the exterior window groups.
 for u in [-15,-9,4]:
  F.box('kf-frame',(u,1.65,-.12),(3.2,2.4,.10))
  F.box('kf-glass',(u,1.65,-.19),(3.04,2.22,.035))
  for dx in [-.5,.5]:F.box('kf-frame',(u+dx,1.65,-.23),(.045,2.3,.04))
  F.box('kf-cream',(u,.43,-.25),(3.35,.12,.32))
 # Original geometric wall panels stand in for photographed framed decoration.
 for u in [-13,-9,-1,4]:
  F.box('kf-wood',(u,2.1,-10.7),(1.35,1.0,.10))
  F.box('kf-gold',(u,2.1,-10.62),(1.17,.82,.04))
  F.box('kf-burgundy',(u,2.1,-10.58),(1.02,.67,.025))
  F.path('kf-gold',[(u-.35,1.9,-10.55),(u,2.36,-10.55),(u+.35,1.9,-10.55)],.025,8)
 for u in [-16.4,7.35]:F.box('kf-wood',(u,.3,-5.5),(.08,.2,10.5))
 # Booths along the street-side wall leave the entrance and central aisle open.
 for u in [-14,-10,-6,3.5,6]:
  F.box('kf-wood',(u,.42,-.65),(1.85,.55,.8),True)
  F.box('kf-vinyl',(u,.72,-.7),(1.85,.2,.85))
  F.box('kf-vinyl',(u,1.1,-.27),(1.85,1,.16),True)
  F.box('kf-table',(u,.91,-1.8),(1.6,.07,.8),True)
  F.tube('kf-frame',(u,.2,-1.8),(u,.87,-1.8),.07,10)
 def chair(u,v):
  F.box('kf-vinyl',(u,.62,v),(.5,.12,.48),True)
  for x in [-.2,.2]:
   for z in [-.18,.18]:F.box('kf-wood',(u+x,.36,v+z),(.045,.5,.045))
  F.box('kf-wood',(u,1.1,v+.23),(.56,.09,.06))
  for x in [-.2,-.1,0,.1,.2]:F.tube('kf-wood',(u+x,.66,v+.23),(u+x,1.1,v+.23),.018,8)
 for u in [-14,-9,-4,1,5]:
  F.box('kf-table',(u,.91,-6.1),(1.5,.07,1.3),True)
  F.tube('kf-frame',(u,.2,-6.1),(u,.87,-6.1),.07,10)
  for v in [-5.1,-7.1]:chair(u,v)
 # Bar against the rear wall, with a clear approach on its east side.
 F.box('kf-wood',(-5, .72,-9.9),(6,1.12,.9),True)
 F.box('kf-table',(-5,1.32,-9.9),(6.2,.08,1.05))
 for y in [1.8,2.45]:
  F.box('kf-wood',(-5,y,-10.57),(6,.08,.35))
  for u in np.arange(-7.5,-2.4,.38):F.lathe('kf-bottle',float(u),-10.57,[(y+.04,.06),(y+.23,.06),(y+.26,.028),(y+.35,.028)],8)
 for u in [-14,-7,0,5]:
  for v in [-3.6,-8.5]:F.lathe('kf-lamp',u,v,[(3.34,.12),(3.38,.15)],12)
 for u in [-12,-4,4]:F.light(u,3.1,-5,power=65,range=13)
 # Zone points into the building (opposite the exterior frame).
 zone=dict(origin=F.p(-4.5,.16,0),yaw=YAW+math.pi,width=24,depth=10.8,height=3.4)
 return dict(key=KEY,name='Kung Fu Thai & Chinese Restaurant',center=[p.centroid.x,0,p.centroid.y],bounds=[p.bounds[0]-1,p.bounds[1]-1,p.bounds[2]+2.5,p.bounds[3]+1],structural=True,exteriorOnly=False,portals=[entry],zones=[zone],lights=B.lights,routes=[dict(name='Street to dining and bar',points=[F.p(u,.16,v) for u,v in [(-2,2),(-2,-1),(-2,-3.5),(-7,-3.5),(-7,-8.5)]])],hotelSources=[],views={name:dict(eye=F.p(*eye),target=F.p(*target)) for name,eye,target in [('entrance',(-2,1.8,3),(-2,1.8,-3)),('dining',(-2,1.8,-3.5),(-8,1.5,-6)),('booths',(-7,1.8,-4),(-9,1.5,-.5)),('bar',(-4,1.8,-6),(-5,1.5,-10))]})
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
