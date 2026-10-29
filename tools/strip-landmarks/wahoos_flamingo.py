"""Original Wahoo Flamingo exterior, December2022 street reference.
Mapped footprint is authoritative; facade heights and roof services estimated.
Private interior is closed. No reference pixels are distributed.
"""
from common import *
KEY='wahoos-flamingo';ID='way/1264703198';YAW=math.pi/2+.01599

def build(B):
 p=footprint(ID);F=Frame(B,-1724.6725,98.852,YAW,y=0)
 B.property=KEY+'-exterior';B.source='podium/'+KEY;B.detail=0
 B.shell(p,.12,5.65,'wh-stucco',roof=False);B.planar('wh-roof',p,5.45)
 # Raised narrow central entry parapet, with a recessed center plane.
 F.box('wh-stucco',(-2.2,6.1,-.19),(3.6,1.5,.38),True)
 for a,b,h in [(-14.3,-4,5.65),(-4,-.4,6.85),(-.4,14.3,5.65)]:
  for y,depth,th in [(h-.22,.42,.10),(h-.1,.53,.12),(h,.68,.12)]:
   F.box('wh-cream',((a+b)/2,y,.10),(b-a,th,depth))
 # All perimeter walls have a narrow coping and visible roof-side parapet.
 for a,b in zip(list(p.exterior.coords)[:-1],list(p.exterior.coords)[1:]):
  B.tube('wh-cream',(a[0],5.62,a[1]),(b[0],5.62,b[1]),.08,8)
 # Individually jointed stacked stone at the street base, original deterministic layout.
 for row in range(6):
  for j in range(50):
   u=-14.3+j*.58+(row%2)*.29
   if u+.56>14.3 or -3.5<u<-.9:continue
   F.box('wh-stone-'+str((j*7+row*3)%4),(u+.28,.22+row*.145,.11),(.55,.135,.13))
 # Wide dark storefront windows, including mullions and lower opaque menu panels.
 for u,w in [(-7.9,4.25),(3.2,4.35)]:
  F.box('wh-frame',(u,1.65,.18),(w,2.6,.14))
  F.box('wh-glass',(u,1.83,.27),(w-.16,2.10,.035))
  for dx in [-w/6,w/6]:F.box('wh-frame',(u+dx,1.65,.31),(.055,2.6,.04))
  F.box('wh-frame',(u,1.05,.32),(w,.06,.04))
  for k in [-1,0,1]:
   F.box('wh-menu',(u+k*w/3,.58,.28),(w/3-.10,.48,.035))
  # Hipped blue sheet-metal awning, actual sloping roof geometry.
  pts=[(u-w/2-.45,3.02,1.25),(u+w/2+.45,3.02,1.25),(u+w/2+.45,3.02,-.05),(u-w/2-.45,3.02,-.05)]
  ridge=[(u-w/2+.35,3.84,.12),(u+w/2-.35,3.84,.12)]
  for face in [[pts[0],pts[1],ridge[1],ridge[0]],[pts[1],pts[2],ridge[1]],[pts[2],pts[3],ridge[0],ridge[1]],[pts[3],pts[0],ridge[0]]]:B.face('wh-blue',[F.p(*q) for q in face])
  F.box('wh-cream',(u,3.0,1.25),(w+.95,.09,.11))
  for t in np.linspace(0,1,30):
   lo=(u-w/2-.45+(w+.9)*t,3.035,1.25);hi=(u-w/2+.35+(w-.7)*t,3.855,.12)
   F.tube('wh-seam',lo,hi,.012,5)
 # Central double door, closed because no public interior evidence is available.
 F.box('wh-frame',(-2.2,1.42,.13),(2.05,2.65,.20),True)
 for u in [-2.68,-1.72]:
  F.box('wh-glass',(u,1.58,.25),(.88,2.22,.04))
  F.box('wh-menu',(u,.70,.28),(.84,1.0,.02))
  F.tube('wh-metal',(u-.28,1.15,.35),(u-.28,1.75,.35),.025,10)
 F.box('wh-frame',(-2.2,1.5,.3),(.055,2.4,.04))
 F.text('3891',(-2.2,2.37,.32),.24,'wh-cream',back=True)
 F.box('wh-metal',(-2.2,3.10,.54),(3.3,.12,1.15))
 F.box('wh-cream',(-2.2,3.04,1.10),(3.3,.11,.08))
 for u in [-10.7,-5.2,.2,6.1,11.4]:
  F.box('wh-cream',(u,2.35,.16),(.50,2.35,.13))
  F.box('wh-frame',(u,2.7,.29),(.52,.24,.15))
  F.box('wh-lens',(u,2.56,.30),(.35,.025,.12))
 # Original oval signs, plain typography rather than copied logo artwork.
 def sign(u,y,w,h):
  for material,v,scale in [('wh-blue',.21,1),('wh-red',.25,.94)]:
   q=[F.p(u+math.cos(a)*w/2*scale,y+math.sin(a)*h/2*scale,v) for a in np.linspace(0,math.tau,65)]
   B.face(material,q)
  F.text("Wahoo's",(u,y-.12,.29),h*.40,'wh-cream',back=True)
  F.text('FISH TACO',(u,y-h*.29,.30),h*.12,'wh-cream',back=True)
 sign(-2.2,4.68,2.75,1.0);sign(11.0,4.48,4.65,1.65)
 F.box('wh-blue',(14.52,3.85,.55),(.65,3.2,.3))
 F.box('wh-red',(14.52,3.85,.73),(.53,3.05,.035))
 for i,c in enumerate('WAHOOS'):F.text(c,(14.52,4.99-i*.43,.77),.34,'wh-cream',back=True)
 # Generic original menu board; dated promotional artwork is not reproduced.
 F.box('wh-cream',(8.5,2.3,.15),(2.8,1.8,.12));F.box('wh-menu',(8.5,2.3,.24),(2.66,1.66,.035))
 F.text('BREAKFAST',(8.5,2.65,.28),.29,'wh-red',back=True)
 F.text('ALL DAY',(8.5,2.18,.28),.34,'wh-red',back=True)
 # Narrow public frontage apron; keep parking/roads unchanged.
 F.box('wh-paving',(0,.065,.84),(28.8,.13,1.65),True)
 for u in np.arange(-14,14,1.7):F.box('wh-joint',(float(u),.134,.84),(.012,.005,1.6))
 # Rear equipment inferred from a typical low-rise roof, kept below parapet where possible.
 for u in [-8,3,10]:
  F.box('wh-metal',(u,5.8,-8),(1.5,.65,1.3))
  for v in np.linspace(-8.5,-7.5,8):F.box('wh-frame',(u,6.13,float(v)),(1.3,.02,.04))
 return dict(key=KEY,name="Wahoo's Flamingo",center=[p.centroid.x,0,p.centroid.y],bounds=[p.bounds[0]-1,p.bounds[1]-1,p.bounds[2]+2,p.bounds[3]+1],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],hotelSources=[],routes=[dict(name='East frontage and door approach',points=[F.p(u,.14,v) for u,v in [(-12,1.35),(-2.2,1.35),(12,1.35)]])])
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
