"""Original BMO Sahara exterior from August2025 photograph and aerial; fitted dimensions."""
from common import *
KEY='bmo-sahara';IDS=['way/900523798']
def build(B):
 p=footprint(IDS[0]);B.property=KEY+'-exterior';B.source='retail/'+KEY;B.detail=0
 B.shell(p,.02,5.5,'bs-stucco',roof=False);B.planar('bs-membrane',p,5.5)
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  dx,dz=b[0]-a[0],b[1]-a[1];L=math.hypot(dx,dz);F=Frame(B,(a[0]+b[0])/2,(a[1]+b[1])/2,math.atan2(-dz,dx),y=0)
  F.box('bs-cap',(0,5.53,0),(L+.08,.12,.25));F.box('bs-base',(0,.18,0),(L,.35,.12))
  for u in np.arange(-L/2+.6,L/2,1.25):F.box('bs-joint',(float(u),2.75,-.012),(.012,5.1,.012))
 # East entry, facing the parking court. Portal floats forward of the true wall.
 R=Frame(B,-776.65,-3191.3,-math.pi/2,y=0)
 for u in [-3.0,2.0]:R.box('bs-stucco',(u,2.05,-.27),(.65,4.1,.65),True)
 R.box('bs-stucco',(-.5,3.92,-.27),(5.65,.85,.65),True)
 R.box('bs-glass',(-.5,1.77,-.20),(4.35,3.5,.07))
 for u in [-2.67,-1.7,-.5,.7,1.67]:R.box('bs-mullion',(u,1.77,-.26),(.065,3.55,.08))
 for y in [.04,.9,2.68,3.53]:R.box('bs-mullion',(-.5,y,-.27),(4.42,.065,.09))
 for u in [-.65,-.35]:R.tube('bs-alloy',(u,1.1,-.34),(u,1.65,-.34),.022,8)
 for u in [-1.1,.1]:R.box('bs-blue',(u,1.91,-.30),(1.0,.2,.02))
 R.text('2980',(-.5,4.05,-.62),.28,'bs-address')
 R.text('BMO',(.5,4.91,-.14),.61,'bs-letter')
 # Original roundel and abstract M geometry; no downloaded logos/textures.
 center=R.p(-1.4,4.99,-.16);ring=[R.p(-1.4+.48*math.cos(a),4.99+.48*math.sin(a),-.18) for a in np.linspace(0,math.tau,33)]
 for a,b in zip(ring,ring[1:]):B.face('bs-red',[center,a,b])
 shape=[(-.27,-.1),(-.27,.11),(-.12,.25),(0,.13),(.12,.25),(.27,.11),(.27,-.1),(.12,.03),(0,-.08),(-.12,.03)]
 # Faceted white monogram kept geometric and modest.
 for a,b in zip(shape,shape[1:]+shape[:1]):B.face('bs-letter',[R.p(-1.4,4.99,-.20),R.p(-1.4+a[0],4.99+a[1],-.20),R.p(-1.4+b[0],4.99+b[1],-.20)])
 R.box('bs-letter',(-1.4,4.72,-.20),(.55,.075,.02))
 def bay(F,u,width=1.45,height=2.7,base=.55):
  mid=base+height/2;top=base+height
  F.box('bs-glass',(u,mid,-.12),(width,height,.065))
  for x in [u-width/2,u,u+width/2]:F.box('bs-mullion',(x,mid,-.17),(.055,height+.1,.07))
  for y in [base-.03,top+.03]:F.box('bs-mullion',(u,y,-.17),(width+.1,.055,.07))
  q=[F.p(u-width/2-.12,top+.05,-.15),F.p(u+width/2+.12,top+.05,-.15),F.p(u+width/2+.12,top-.37,-1.0),F.p(u-width/2-.12,top-.37,-1.0)]
  B.face('bs-blue',q);B.face('bs-blue',[q[0],q[3],F.p(u-width/2-.12,top-.37,-.15)]);B.face('bs-blue',[q[1],F.p(u+width/2+.12,top-.37,-.15),q[2]])
  F.box('bs-blue',(u,top-.42,-1),(width+.24,.12,.035))
 for u in [3.45,5.55]:bay(R,u,1.35)
 # Northern east wing, same established facade language; placement fitted.
 N=Frame(B,-774.28,-3202,-math.pi/2,y=0)
 for u in [-2.5,0,2.5]:bay(N,u,1.55)
 # Richfield side corroborated by January2026 Street View.
 W=Frame(B,-791.86,-3191.5,math.pi/2,y=0)
 for u in [-2.0,1.8]:bay(W,u,1.5,1.6,1.1)
 W.text('BMO',(-.2,4.9,-.15),.54,'bs-letter')
 ring=[W.p(-1.8+.4*math.cos(a),4.98+.4*math.sin(a),-.17) for a in np.linspace(0,math.tau,25)]
 for a,b in zip(ring,ring[1:]):B.face('bs-red',[W.p(-1.8,4.98,-.17),a,b])
 for a,b in zip(shape,shape[1:]+shape[:1]):B.face('bs-letter',[W.p(-1.8,4.98,-.20),W.p(-1.8+a[0],4.98+a[1],-.20),W.p(-1.8+b[0],4.98+b[1],-.20)])
 W.box('bs-letter',(-1.8,4.71,-.20),(.55,.075,.02))
 # Angled northwest return has additional narrow glazing, fitted on mapped edges.
 a=(-791.949,-3199.879);b=(-787.281,-3204.799);dx,dz=b[0]-a[0],b[1]-a[1]
 F=Frame(B,(a[0]+b[0])/2,(a[1]+b[1])/2,math.atan2(-dz,dx),y=0)
 for u in [-1.5,1.5]:bay(F,u,1.15,1.6,1.1)
 # Low clipped shrubs and scattered red desert rocks, constrained to west frontage.
 for i,(x,z) in enumerate([(-793.7,-3189),(-794,-3192.2),(-793.8,-3195.3),(-791,-3200.3)]):
  for j in range(7):
   a=j*2.399;B.sphere('bs-foliage',(x+.34*math.cos(a),.6+(j%3)*.11,z+.34*math.sin(a)),.4,8,5)
  B.sphere('bs-rock',(x-.65,.18,z+.7),.27,7,4)
 # Front wall sconces, physically separate from the stucco surface.
 for u in [-3,2]:
  R.lathe('bs-alloy',u,-.66,[(2.65,0),(2.65,.10),(3.2,.10),(3.2,0)],12)
 # Teal pyramid above the south roof; original roof panels and standing seams.
 C=Frame(B,-784,-3188.9,0,y=0);corners=[(-4,-4),(4,-4),(4,4),(-4,4)]
 for i,a in enumerate(corners):
  b=corners[(i+1)%4];B.face('bs-patina',[C.p(a[0],5.55,a[1]),C.p(b[0],5.55,b[1]),C.p(0,8.15,0)])
  C.tube('bs-seam',(a[0],5.57,a[1]),(0,8.17,0),.025,8)
  for t in np.arange(.12,.96,.12):
   x=a[0]*(1-t)+b[0]*t;z=a[1]*(1-t)+b[1]*t
   C.tube('bs-seam',(float(x),5.57,float(z)),(0,8.17,0),.012,6)
 for x,z in [(-780,-3201),(-786,-3197)]:
  F=Frame(B,x,z,0,y=0);F.box('bs-service',(0,5.9,0),(1.5,.8,1.5));F.box('bs-alloy',(0,6.33,0),(1.6,.08,1.6))
 # Minimal adjacent entry walk; preserve all mapped parking and street surfaces.
 R.box('bs-paving',(-.5,.10,-1),(6,.2,2),True)
 B.upface('bs-paving',[R.p(-3.5,.2,-2),R.p(2.5,.2,-2),R.p(2.5,0,-3.5),R.p(-3.5,0,-3.5)],True)
 routes=[dict(name='East entry approach',points=[R.p(-.5,0,-6),R.p(-.5,0,-3.5),R.p(-.5,.2,-2),R.p(-.5,.2,-.9)]),dict(name='East public frontage',points=[[-771,.05,-3208],[-771,.05,-3200],[-771,.05,-3192],[-771,.05,-3180]])]
 return dict(key=KEY,name='BMO West Sahara',center=[-783,0,-3194],bounds=list(p.bounds),structural=True,hotelSources=[],exteriorOnly=True,portals=[],zones=[],lights=[],routes=routes)
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
