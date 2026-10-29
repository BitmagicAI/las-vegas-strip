"""Original exterior/public dining. Photo-supported finishes; layout inferred."""
from common import *
KEY='mt-everest-sahara';ID='way/764147974';YAW=math.pi+.033

def build(B):
 p=footprint(ID);F=Frame(B,-1517.67,-3125.39,YAW,y=0)
 B.property=KEY+'-exterior';B.source='podium/'+KEY;B.detail=0
 entry=dict(p=F.p(1.3,.16,.05),yaw=YAW,width=1.55,height=2.65,name='Public dining entrance',venue=KEY)
 B.shell(p,.1,3.6,'me-brick',roof=False,openings=[entry]);B.planar('me-roof',p,3.55);B.planar('me-floor',p,.16,True)
 # Red painted brick courses retain small mortar joints without coincident faces.
 for row in range(10):
  for i in range(43):
   u=-6.4+i*.30+(row%2)*.15
   if u>6.35 or .48<u<2.12:continue
   F.box('me-brick-'+str((i+row)%3),(u,.17+row*.09,.08),(.285,.078,.06))
 for a,b in [(-6.35,.45),(2.15,6.35)]:
  for u in np.arange(a+.65,b-.2,1.3):
   F.box('me-frame',(float(u),2.02,.13),(1.29,2.25,.13));F.box('me-glass',(float(u),2.02,.22),(1.15,2.10,.025))
   # Original geometric mountain motif, no reference pixels copied.
   F.box('me-blue',(float(u),1.42,.24),(1.12,.82,.025))
   for dx,hh in [(-.28,.55),(.13,.74),(.38,.42)]:
    B.face('me-snow',[F.p(u+dx-.25,1.03,.26),F.p(u+dx,1.03+hh,.26),F.p(u+dx+.28,1.03,.26)])
 for u in [-6.5,.45,2.15,6.5]:F.box('me-red',(u,1.82,.20),(.18,3.4,.28),True)
 F.box('me-red',(0,3.39,.24),(13.5,.40,.46));F.text('3641',(1.3,2.99,.5),.39,'me-cream',back=True)
 F.text('MT. EVEREST',(-2.0,3.38,1.01),.30,'me-cream',back=True)
 F.text("INDIA'S CUISINE",(-2.0,3.03,.51),.22,'me-cream',back=True)
 F.box('me-concrete',(0,.07,.8),(13.5,.14,1.6),True)
 # Hipped tiled eave on north and side faces; central flat service roof is inferred.
 for u in np.arange(-6.9,6.91,.24):
  for j in range(7):
   v=.8-j*.55; y=3.70+min(j*.15,max(0,6.9-abs(float(u)))*.35)
   F.tube('me-tile-'+str((j+int(u*10))%3),(float(u),y,v),(float(u),y+.16,v-.58),.125,10)
 for side in [-1,1]:
  for v in np.arange(-3.1,-22,-.24):
   for j in range(5):
    u=side*(6.85-j*.52);y=3.70+j*.18
    F.tube('me-tile-'+str(j%3),(u,y,float(v)),(u-side*.55,y+.19,float(v)),.125,10)
 F.box('me-red',(0,3.5,.9),(13.8,.32,.19))
 # Close the inner eave returns above the flat service roof.
 for u in [-4.5,4.5]:F.box('me-red',(u,4.05,-12.4),(.12,1.0,18.6))
 F.box('me-red',(0,4.07,-3.1),(9.1,1.04,.12))
 for side in [-1,1]:
  for v in [-2.8,-5.7,-8.6,-11.5]:
   F.box('me-frame',(side*6.55,2.0,v),(.16,1.7,2.75))
   F.box('me-glass',(side*6.65,2.0,v),(.025,1.55,2.59))
   F.box('me-frame',(side*6.68,2.0,v),(.04,1.60,.055))
 for u in [-3,3]:F.box('me-metal',(u,3.95,-17),(1.4,.7,1.4))
 # Public dining envelope; rear private kitchen remains closed.
 B.property=KEY+'-interior';B.source='public/'+KEY
 F.box('me-carpet',(0,.18,-7),(12.3,.025,13.8));F.box('me-ceiling',(0,3.05,-7),(12.3,.12,14))
 for u in [-6.15,6.15]:
  F.box('me-orange',(u,1.65,-7),(.12,2.85,14),True);F.box('me-wood',(u,.68,-7),(.15,1.0,13.9))
 for side in [-1,1]:
  for v in [-2.8,-5.7,-8.6,-11.5]:
   F.box('me-frame',(side*6.04,2.0,v),(.05,1.63,2.7))
   F.box('me-glass',(side*6.0,2.0,v),(.025,1.52,2.55))
   for h in np.arange(1.25,2.78,.075):F.box('me-blind',(side*5.97,float(h),v),(.045,.045,2.60))
 F.box('me-orange',(0,1.65,-13.9),(12.3,2.85,.15),True);F.box('me-wood',(0,.68,-13.79),(12.2,1.0,.08))
 for a,b in [(-6.1,.42),(2.18,6.1)]:
  F.box('me-wood',((a+b)/2,.70,-.13),(b-a,1.08,.10))
  F.box('me-orange',((a+b)/2,2.87,-.13),(b-a,.30,.10))
  for u in np.arange(a+.6,b-.4,1.2):
   F.box('me-frame',(float(u),1.98,-.16),(1.15,1.72,.10));F.box('me-glass',(float(u),1.98,-.22),(1.07,1.64,.025))
   for h in np.arange(1.20,2.77,.075):F.box('me-blind',(float(u),float(h),-.26),(1.09,.045,.045))
 for u in np.arange(-6,6.1,.6):F.box('me-grid',(float(u),2.98,-7),(.018,.025,13.8))
 for v in np.arange(-13.8,0,.6):F.box('me-grid',(0,2.98,float(v)),(12.2,.025,.018))
 def table(u,v,w=1.3,d=.8):
  F.box('me-table',(u,.91,v),(w,.065,d),True);F.box('me-frame',(u,.25,v),(.65,.06,.55));F.tube('me-frame',(u,.25,v),(u,.87,v),.065,12)
  for dx in [-.35,.35]:
   F.lathe('me-glassware',u+dx,v,[(.95,.065),(.96,.065),(.97,.012),(1.04,.012),(1.06,.052),(1.15,.06),(1.15,.052),(1.07,.045)],20)
   F.lathe('me-cream',u+dx,v+.24,[(.95,.13),(.97,.15),(.985,.15),(.975,.11)],24)
 def chair(u,v):
  F.box('me-vinyl',(u,.63,v),(.48,.09,.46),True)
  for dx in [-.2,.2]:
   for dz in [-.18,.18]:F.box('me-table',(u+dx,.39,v+dz),(.04,.48,.04))
   F.box('me-table',(u+dx,.98,v+.21),(.04,.74,.045))
  for h in [.83,1.03,1.21]:F.box('me-table',(u,h,v+.21),(.45,.065,.04))
 # Perimeter booths with padded seams; central circulation remains open.
 for u in [-4.8,-2.7,4.6]:
  F.box('me-wood',(u,.41,-.7),(1.8,.5,.78),True);F.box('me-vinyl',(u,.70,-.72),(1.8,.16,.80));F.box('me-vinyl',(u,1.13,-.3),(1.8,.95,.20),True)
  F.box('me-red',(u,1.13,-.415),(1.74,.016,.012));table(u,-1.65);chair(u,-2.45)
 for u in [-4.7,4.7]:
  for v in [-5,-8.2,-11.4]:
   table(u,v,1.25,1.1)
   for dz in [-.95,.95]:chair(u,v+dz)
 # Inferred compact buffet against closed rear wall; stainless trays are photo-supported.
 F.box('me-wood',(0,.67,-12.95),(4.3,1.0,1.0),True);F.box('me-metal',(0,1.2,-12.95),(4.5,.10,1.12))
 for u in [-1.6,-.8,0,.8,1.6]:
  F.box('me-metal',(u,1.24,-12.95),(.68,.025,.82))
  for dx in [-.32,.32]:F.box('me-metal',(u+dx,1.29,-12.95),(.035,.12,.82))
  for dz in [-.39,.39]:F.box('me-metal',(u,1.29,-12.95+dz),(.68,.12,.035))
  F.box('me-food-'+str(int((u+2)*5)%3),(u,1.27,-12.95),(.56,.018,.68))
 for u in [-1.6,-.8,0,.8,1.6]:
  F.tube('me-metal',(u,1.30,-13.02),(u+.20,1.40,-12.45),.012,8)
  F.lathe('me-metal',u,-13.02,[(1.28,.04),(1.30,.055),(1.31,.048)],12)
 for u in [-2.1,2.1]:F.tube('me-metal',(u,1.2,-13.2),(u,1.85,-13.2),.025,10)
 F.box('me-metal',(0,1.85,-13.2),(4.3,.05,.32))
 for u in [-4,0,4]:
  for v in [-3.5,-9.5]:
   F.lathe('me-lamp',u,v,[(2.94,.08),(2.98,.11)],16)
 for u in [-3.4,3.4]:
  F.tube('me-frame',(u,2.98,-6.5),(u,2.58,-6.5),.028,10);F.lathe('me-frame',u,-6.5,[(2.48,.14),(2.58,.2),(2.64,.14)],20)
  for ang in np.linspace(0,math.tau,5)[:-1]:
   pts=[(u+math.cos(ang)*r-math.sin(ang)*w,2.57,-6.5+math.sin(ang)*r+math.cos(ang)*w) for r,w in [(.15,-.08),(.76,-.13),(.83,.08),(.15,.08)]]
   B.upface('me-table',[F.p(*q) for q in pts])
 for u in [-4.8,-2.7,4.6]:
  F.tube('me-frame',(u,2.98,-1.5),(u,2.52,-1.5),.012,6);F.lathe('me-lamp',u,-1.5,[(2.38,.045),(2.48,.075),(2.53,.03)],12)
 for v in [-3,-10]:F.light(0,2.75,v,power=55,range=12)
 route=[F.p(u,.16,v) for u,v in [(1.3,2),(1.3,-1),(1.3,-4),(0,-4),(0,-10.6)]]
 views={n:dict(eye=F.p(*e),target=F.p(*t)) for n,e,t in [('entrance',(1.3,1.8,3),(1.3,1.6,-4)),('dining',(1.3,1.8,-4),(-4,1.4,-7)),('booths',(0,1.8,-3.5),(-3.8,1.2,-.5)),('buffet',(0,1.8,-9),(0,1.2,-13))]}
 return dict(key=KEY,name="Mt. Everest India's Cuisine",center=[p.centroid.x,0,p.centroid.y],bounds=[p.bounds[0]-1,p.bounds[1]-2,p.bounds[2]+1,p.bounds[3]+1],structural=True,exteriorOnly=False,portals=[entry],zones=[dict(origin=F.p(0,.16,0),yaw=YAW+math.pi,width=12.3,depth=14,height=2.9)],lights=B.lights,hotelSources=[],routes=[dict(name='Entrance to dining and buffet',points=route)],views=views)
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
