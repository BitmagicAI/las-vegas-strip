"""Ferraro main frontage and outdoor dining; adjacent A200 tenancy is not replaced."""
from common import *
KEY='ferraros';ID='way/1421206068';YAW=-2.8031839330908013

def build(B):
 p=footprint(ID);F=Frame(B,1914.764,762.171,YAW,y=0)
 B.property=KEY+'-exterior';B.source='podium/ferraros';B.detail=0
 B.shell(p,.04,6.35,'fr-stucco',roof=False);B.planar('fr-roof',p,6.35)
 rng=random.Random(252)
 def stone(u,v,w,h):
  F.box('fr-mortar',(u,h/2,v),(w,h,.34))
  for row in range(math.ceil(h/.19)):
   x=u-w/2+.015
   while x<u+w/2-.03:
    width=min(rng.uniform(.24,.62),u+w/2-x-.015)
    if width<.02:break
    F.box('fr-stone'+str(rng.randrange(3)),(x+width/2,row*.19+.09,v-.19),(width-.018,.163,.06));x+=width
 def cornice(a,b,y,v=0):
  for yy,hh,dd in [(y-.2,.12,.17),(y,.14,.29),(y+.13,.09,.38)]:F.box('fr-trim',((a+b)/2,yy,v-dd/2),(b-a+.10,hh,dd))
 # Main street frontage and tall entry portal, proportions from official front photo.
 cornice(0,22,6.35)
 for u,w in [(1.1,1.7),(21.3,1.3)]:stone(u,-.07,w,6.6);cornice(u-w/2,u+w/2,6.65)
 for u in [4.1,7.15,10.2]:
  F.box('fr-glass',(u,2.65,-.045),(2.05,2.2,.06))
  for dx in [-1.08,1.08]:F.box('fr-metal',(u+dx,2.65,-.10),(.06,2.3,.09))
  F.box('fr-blind',(u,2.15,-.09),(2.02,1.15,.04))
  # Individual original striped fabric awnings, slope and valance.
  for j in range(24):
   x=u-1.22+j*2.44/24;xx=x+2.44/24
   mat='fr-fabric' if j%2 else 'fr-stripe'
   B.face(mat,[F.p(x,4.3,-.08),F.p(xx,4.3,-.08),F.p(xx,3.5,-1.08),F.p(x,3.5,-1.08)])
   F.box(mat,((x+xx)/2,3.40,-1.08),(xx-x,.20,.04))
  for dx in [-1.22,1.22]:F.tube('fr-metal',(u+dx,3.46,-1.06),(u+dx,3.25,-.06),.025,8)
  F.path('fr-metal',[(u,4.6,-.05),(u,4.9,-.30),(u,4.85,-.47)],.02,8)
  F.lathe('fr-metal',u,-.47,[(4.70,.15),(4.84,.06)],12)
 # Entrance projects towards parking; open-sided portico before closed public doors.
 for u in [14.3,19.6]:
  F.box('fr-limestone',(u,2.4,-.8),(.75,4.8,1.6),True)
  for yy in np.arange(.5,4.6,.8):F.box('fr-joint',(u,yy,-1.607),(.74,.012,.014))
 F.box('fr-limestone',(16.95,5.15,-.8),(6.05,1.85,1.6));cornice(13.9,20,6.15,-1.6)
 F.box('fr-stucco',(16.95,6.75,.45),(4.75,1.35,2.5))
 # Upper tower steps, with shallow horizontal stone band and three inset squares.
 F.box('fr-stone1',(16.95,6.95,-.88),(4.7,.65,.10))
 for row in range(4):
  for j in range(9):F.box('fr-stone'+str((row+j)%3),(14.84+j*.52,6.67+row*.16,-.95),(.50,.14,.045));cornice(14.55,19.35,7.35,-.9)
 F.box('fr-limestone',(16.95,8.35,.5),(4.4,1.7,2.8));cornice(14.65,19.25,9.22,-.95)
 for u in [15.65,16.95,18.25]:F.box('fr-inset',(u,8.60,-.92),(.38,.38,.05))
 F.box('fr-glass',(16.95,1.45,-.065),(2.25,2.8,.08))
 for u in [15.79,16.95,18.11]:F.box('fr-metal',(u,1.45,-.12),(.065,2.9,.08))
 for u in [16.78,17.12]:F.tube('fr-metal',(u,.9,-.19),(u,1.4,-.19),.02,10)
 F.text("Ferraro’s",(16.95,5.35,-1.63),.76,'fr-letter');F.text('RISTORANTE',(16.95,4.65,-1.63),.30,'fr-letter')
 for u in [14.3,19.6]:
  B.sphere('fr-metal',F.p(u,3.2,-1.65),.18,16,10)
  F.box('fr-plaque',(u,1.85,-1.65),(.23,.35,.04))
 F.box('fr-paving',(11,.08,-1.3),(22,.16,2.6),True)
 # Terrace occupies the mapped concavity, not a fabricated room inside the restaurant.
 terrace=F.poly([(21.96,-.2),(38.1,-.2),(38.1,10.38),(31.37,10.59),(31.42,8.83),(27.46,7.82),(23.46,4.35)])
 B.planar('fr-patio',terrace,.16,True)
 # Curved facade follows mapped segments. Repeated soffit brackets and glazing stay inside boundary.
 edge=[(21.96,0),(23.46,4.35),(27.46,7.82),(31.42,8.83),(31.37,10.59),(38.08,10.38)]
 for a,b in zip(edge,edge[1:]):
  pa=F.p(a[0],0,a[1]);pb=F.p(b[0],0,b[1]);length=math.dist(pa,pb);yaw=-math.atan2(pb[2]-pa[2],pb[0]-pa[0]);G=Frame(B,pa[0],pa[2],yaw,y=0)
  # On this clockwise perimeter, negative local depth faces the public patio.
  for yy,dd in [(6.0,.25),(6.3,.40)]:G.box('fr-trim',(length/2,yy,-dd/2),(length,.14,dd))
  for x in np.arange(.3,length,.55):G.box('fr-metal',(x,5.65,-.35),(.16,.42,.65))
  G.box('fr-glass',(length/2,2.2,-.065),(max(.3,length-.40),3.6,.08))
  for x in np.arange(.22,length,.95):G.box('fr-metal',(x,2.2,-.13),(.05,3.7,.08))
  G.box('fr-blind',(length/2,4.1,-.16),(length-.3,.65,.07))
 # Three freestanding patio stone piers and horizontal pergola perimeter.
 for u,v in [(24.0,-.15),(33.3,-.15),(38.0,8.8)]:
  F.box('fr-stone1',(u,2.4,v),(.65,4.8,.65),True)
  F.box('fr-trim',(u,4.85,v),(.82,.14,.82));F.box('fr-metal',(u,5.22,v),(.45,.62,.45));F.box('fr-trim',(u,5.57,v),(.70,.10,.70))
 F.box('fr-metal',(30.9,4.55,-.15),(14.4,.30,.32))
 for u in np.arange(24,37.8,.55):F.box('fr-metal',(u,4.45,1.15),(.10,.22,2.6))
 # Low planter edge leaves a generous public opening at the eastern corner.
 F.box('fr-planter',(32.0,.55,-.25),(11.4,1.1,.45),True)
 for u in np.arange(26.5,37.5,.45):
  for j in range(10):
   yy=rng.uniform(.85,2);v=-.25+rng.uniform(-.12,.12);a=rng.uniform(0,math.tau)
   F.tube('fr-leaf',(u,.9,v),(u+.1,yy,v),.008,5)
   B.face('fr-leaf',[F.p(u,yy,v),F.p(u+.18*math.cos(a),yy+.1,v+.18*math.sin(a)),F.p(u+.08*math.cos(a)-.06*math.sin(a),yy+.06,v+.08*math.sin(a)+.06*math.cos(a))])
 # Photographed central round fire table, with surrounding orange lounge chairs.
 F.lathe('fr-metal',29.6,3.4,[(.16,1.05),(.82,1.05)],32)
 F.lathe('fr-counter',29.6,3.4,[(.82,1.15),(.92,1.15)],48);F.lathe('fr-charcoal',29.6,3.4,[(.92,.90),(.93,.90)],40)
 for a in np.linspace(0,math.tau,7,endpoint=False):
  u=29.6+2.15*math.cos(a);v=3.4+2.15*math.sin(a);P=Frame(B,*[F.p(u,0,v)[i] for i in [0,2]],YAW-a+math.pi/2,y=0)
  P.box('fr-cushion',(0,.58,0),(.68,.18,.66));P.box('fr-cushion',(0,.98,.28),(.68,.65,.16))
  for dx in [-.37,.37]:
   P.box('fr-metal',(dx,.42,0),(.045,.52,.72));P.box('fr-metal',(dx,.82,0),(.045,.05,.72))
 for u,v in [(35.5,3.5),(34.8,7.5),(25.5,3.0)]:
  F.box('fr-counter',(u,.92,v),(1.15,.08,.75));F.lathe('fr-metal',u,v,[(.16,.30),(.23,.30),(.25,.04),(.9,.04)],12)
  for du in [-.85,.85]:
   F.box('fr-metal',(u+du,.57,v),(.48,.06,.50));F.box('fr-metal',(u+du,1.0,v+.22),(.48,.8,.04))
   for dx in [-.20,.20]:
    for dz in [-.20,.20]:F.box('fr-metal',(u+du+dx,.36,v+dz),(.035,.4,.035))
 # Roof plant and parapet, main footprint only.
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):B.tube('fr-trim',(a[0],6.38,a[1]),(b[0],6.38,b[1]),.05,6)
 for u,v in [(8,7),(8,17),(19,16),(29,15)]:
  F.box('fr-equipment',(u,6.8,v),(1.7,.8,1.4));F.box('fr-metal',(u,7.21,v),(1.5,.02,1.2))
 routes=[dict(name='Front entrance approach',points=[F.p(16.95,.16,-4),F.p(16.95,.16,-2),F.p(16.95,.16,-.9)]),dict(name='Patio public access',points=[F.p(25.2,.16,-2),F.p(25.2,.16,.8),F.p(26.2,.16,1.8)])]
 F.box('fr-paving',(16.95,.08,-3.1),(2.2,.16,2.2),True);F.box('fr-paving',(25.2,.08,-1.1),(2.8,.16,2.2),True)
 return dict(key=KEY,name='Ferraro’s Ristorante',center=F.p(19,0,10),bounds=list(p.buffer(3).bounds),structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=routes,hotelSources=[])
if __name__=='__main__':
 B=Meshes();meta=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(meta,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
