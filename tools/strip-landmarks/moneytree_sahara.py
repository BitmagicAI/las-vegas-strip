"""Original Moneytree Sahara exterior and public lobby; photograph-fitted dimensions."""
from common import *
KEY='moneytree-sahara';IDS=['way/900523799']
def build(B):
 p=footprint(IDS[0]);B.property=KEY+'-exterior';B.source='retail/'+KEY;B.detail=0
 R=Frame(B,-722.45,-3206.2,-math.pi/2,y=0)
 door=dict(p=R.p(-2.3,.18,0),yaw=-math.pi/2,width=1.6,height=2.6,name='Moneytree public lobby',venue=KEY)
 B.shell(p,.02,3.7,'mt-stucco',roof=False,openings=[dict(p=R.p(0,.18,0),width=7.8,height=2.95)])
 B.planar('mt-membrane',p.intersection(box(-740,-3225,-720,-3211)),3.72)
 # South portion is a blue gabled roof, ridge east-west; north service roof remains flat.
 x0,x1=-738.2,-722.3;z0,z1=-3211.1,-3200.8;zm=(z0+z1)/2
 for za in [z0,z1]:
  B.upface('mt-blue',[ (x0,3.8,za),(x1,3.8,za),(x1,6.0,zm),(x0,6.0,zm)])
  for x in np.arange(x0,x1,.32):B.tube('mt-seam',(float(x),3.83,za),(float(x),6.03,zm),.017,6)
 for x in [x0+.2,x1-.2]:
  B.face('mt-stucco',[(x,3.68,z0),(x,3.68,z1),(x,5.95,zm)],True)
  for za in [z0,z1]:B.tube('mt-blue',(x,3.78,za),(x,6.0,zm),.11,8)
 # East gable louver and current lettering.
 R.box('mt-stucco',(0,3.25,.04),(8.05,.55,.16),True)
 R.box('mt-letter',(0,3.39,-.12),(6.2,.7,.08));R.box('mt-dark',(0,3.39,-.18),(6,.62,.04))
 R.text('MONEYTREE',(0,3.16,-.23),.59,'mt-yellow')
 for a,b in zip(np.linspace(0,math.tau,33),np.linspace(0,math.tau,33)[1:]):
  B.face('mt-dark',[R.p(0,4.74,-.12),R.p(.42*math.cos(a),4.74+.42*math.sin(a),-.12),R.p(.42*math.cos(b),4.74+.42*math.sin(b),-.12)])
 for y in np.arange(4.4,5.11,.09):
  w=2*math.sqrt(max(0,.42**2-(y-4.74)**2));R.box('mt-blue',(0,float(y),-.15),(w,.035,.035))
 # Public entrance clear opening and window panes, no duplicate transparent box faces.
 for u,w in [(.85,4.5),(-3.62,.35)]:
  B.face('mt-clear',[R.p(u-w/2,.2,0),R.p(u+w/2,.2,0),R.p(u+w/2,2.92,0),R.p(u-w/2,2.92,0)],True)
 for u in [-3.9,-3.1,-1.5,-.4,1.2,3.2,3.9]:R.box('mt-mullion',(u,1.55,-.04),(.075,2.8,.12),True)
 R.box('mt-blue',(0,2.98,-.08),(8,.14,.15));R.box('mt-blue',(0,.18,-.08),(8,.12,.15))
 for u in [-.4,1.2,3.2]:R.box('mt-blue',(u,1,-.06),(.07,1.7,.13))
 R.box('mt-blue',(.85,.55,-.07),(4.5,.06,.14))
 # A south-facing sign and dark glazing corroborated by official storefront photograph.
 S=Frame(B,-730.3,-3201.12,math.pi,y=0)
 S.box('mt-dark',(0,3.65,-.5),(8.8,.85,.1));S.text('MONEYTREE',(0,3.36,-.57),.70,'mt-yellow')
 S.box('mt-glass',(0,1.7,-.12),(8.4,2.3,.06))
 for u in [-4.2,-2.1,0,2.1,4.2]:S.box('mt-blue',(u,1.7,-.18),(.08,2.45,.12))
 for y in [.5,2.9]:S.box('mt-blue',(0,y,-.18),(8.55,.08,.12))
 for x,z in [(-728,-3217),(-732,-3219)]:
  F=Frame(B,x,z,0,y=0);F.box('mt-service',(0,4.1,0),(1.6,.7,1.3));F.box('mt-alloy',(0,4.47,0),(1.7,.06,1.4))
 R.box('mt-paving',(0,.09,-1.0),(8.8,.18,2.0),True)
 B.upface('mt-paving',[R.p(-3.2,.18,-2),R.p(-1.4,.18,-2),R.p(-1.4,0,-4),R.p(-3.2,0,-4)],True)
 for lo,hi in [(-4.4,-3.25),(-1.35,4.4)]:
  for u in np.arange(lo,hi+.01,.35):R.tube('mt-dark',(float(u),.18,-1.92),(float(u),1.15,-1.92),.018,6)
  R.tube('mt-dark',(lo,1.15,-1.92),(hi,1.15,-1.92),.03,8)
 # Public lobby inferred from July2025 photo, confined to footprint; service area excluded.
 B.property=KEY+'-interior';B.source='interior/'+KEY;B.detail=1
 room=R.poly([(-3.8,.08),(3.8,.08),(3.8,10),(-3.8,10)])
 assert p.buffer(.3).covers(room), 'Public room must fit mapped footprint'
 B.shell(room,.18,3.15,'mt-wall',roof=False,openings=[dict(p=R.p(0,.18,.08),width=7.6,height=2.72)])
 B.planar('mt-tile',room,.18,True);B.planar('mt-ceiling',room,3.15)
 B.planar('mt-carpet',R.poly([(-3.6,.2),(3.6,.2),(3.6,7.8),(-3.6,7.8)]),.195)
 # Low-contrast carpet weave and square tile joints remain original geometry.
 for u in np.arange(-3.5,3.6,.22):R.box('mt-carpetweave',(float(u),.198,4),(.025,.003,7.5))
 for u in np.arange(-3.8,3.81,.6):R.box('mt-grout',(float(u),.183,8.9),(.012,.003,2.2))
 for v in np.arange(8,10.01,.6):R.box('mt-grout',(0,.183,float(v)),(7.6,.003,.012))
 for u in np.arange(-3.8,3.81,.6):R.box('mt-grid',(float(u),3.13,5),(.022,.02,9.9))
 for v in np.arange(.1,10.01,.6):R.box('mt-grid',(0,3.13,float(v)),(7.6,.02,.022))
 for u in [-2,2]:
  for v in [2,5.6,8.6]:R.box('mt-lamp',(u,3.115,v),(.55,.022,1.15))
 # Writing islands with blue tops, lightwood cabinets and slim gray legs.
 for u,v in [(1.6,3.7),(-1.65,5.9)]:
  R.box('mt-wood',(u,.75,v),(1.65,1,.65),True);R.box('mt-blue',(u,1.28,v),(2.4,.08,1.15),True)
  for x in [-1.0,1.0]:
   for z in [-.43,.43]:R.tube('mt-alloy',(u+x,.2,v+z),(u+x,1.23,v+z),.045,8)
  R.box('mt-blue',(u,1.38,v),(.08,.2,1.1))
  for x in [-.6,.6]:R.box('mt-paper',(u+x,1.33,v+.12),(.25,.012,.3))
 # Plain service boundary; no invented operational/private layout.
 R.box('mt-wood',(0,.75,9.4),(6.8,1.1,.7),True);R.box('mt-blue',(0,1.34,9.4),(7,.08,.85),True)
 for u in [-2.4,0,2.4]:
  R.box('mt-dark',(u,1.43,9.35),(.45,.04,.25))
 # Original abstract poster designs, not copied advertisements.
 for v in [2.3,4,5.7]:
  R.box('mt-alloy',(3.73,2.05,v),(.06,.95,.7));R.box('mt-paper',(3.69,2.05,v),(.025,.86,.61));R.box('mt-blue',(3.67,2.25,v),(.025,.22,.56));R.box('mt-yellow',(3.65,1.9,v),(.025,.12,.42))
 routes=[dict(name='Public entry and lobby',points=[R.p(-2.3,y,v) for y,v in [(0,-5),(0,-4),(.18,-2),(.18,0),(.18,2),(.18,3.8)]]),dict(name='Lobby to service boundary',points=[R.p(0,.18,v) for v in [1,3,6,8.5]])]
 return dict(key=KEY,name='Moneytree West Sahara',center=[-730,0,-3212],bounds=list(p.bounds),structural=True,hotelSources=[],exteriorOnly=False,portals=[door],zones=[dict(origin=R.p(0,.18,0),yaw=-math.pi/2,width=7.8,depth=10.1,height=3.2)],lights=[dict(p=R.p(u,2.8,v),color=0xffefd1,power=3,range=6) for u,v in [(-2,2),(2,2),(-2,7),(2,7)]],routes=routes)
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
