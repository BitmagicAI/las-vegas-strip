"""Original Fun Hog Ranch reconstruction; room arrangement inferred, not surveyed."""
from common import *
KEY='fun-hog-ranch';ID='way/390003973';YAW=math.pi

def build(B):
 p=footprint(ID);F=Frame(B,1864.7,-550.79,YAW,y=0)
 B.property=KEY+'-exterior';B.source='podium/'+KEY;B.detail=0
 entry=dict(p=F.p(-.5,.16,0),yaw=YAW,width=1.35,height=2.3,name='Public bar entrance',venue=KEY)
 B.shell(p,.04,4.5,'fh-olive',roof=False,openings=[entry]);B.planar('fh-roof',p,4.35);B.planar('fh-foundation',p,.16,True)
 # Board-and-batten front, real doorway kept open, white corner posts and thin cap.
 for u in np.arange(-4.45,4.5,.38):
  if -.5-.8<u<-.5+.8:F.box('fh-batten',(float(u),3.52,.08),(.045,1.85,.08))
  else:F.box('fh-batten',(float(u),2.22,.08),(.045,4.35,.08))
 for h in [.37,2.7,4.5]:F.box('fh-olive',(0,h,.10),(9.28,.10,.08)) if h>2.5 else None
 F.box('fh-white',(0,4.53,.04),(9.38,.10,.14))
 for u in [-4.58,4.58]:F.box('fh-white',(u,2.23,.08),(.13,4.46,.16))
 for u in [-1.22,.22]:F.box('fh-dark',(u,1.35,.12),(.10,2.6,.22))
 F.box('fh-dark',(-.5,2.61,.12),(1.55,.12,.23));F.text('495',(3.30,3.48,.16),.47,'fh-dark',back=True)
 F.box('fh-white',(-.7,3.62,.13),(5.8,.87,.10));F.box('fh-sign',(-.7,3.62,.20),(5.67,.74,.05));F.text('FUN HOG RANCH',(-.7,3.62,.25),.46,'fh-white',back=True)
 for u in [-2.6,1.1]:
  F.path('fh-white',[(u,4.45,.14),(u,4.95,.14),(u,4.95,.65),(u,4.7,.65)],.025,10)
  F.lathe('fh-white',u,.65,[(4.64,.23),(4.72,.13),(4.77,.045)],20);F.lathe('fh-lamp',u,.65,[(4.62,0),(4.62,.07),(4.70,.07),(4.70,0)],16)
 # East-side veranda and timber siding, north apron, estimated roof/rear services.
 for v in np.arange(-.4,-25.7,-.4):F.box('fh-batten',(-4.67,2.2,float(v)),(.08,4.35,.05))
 F.box('fh-roof',(-5.2,3.35,-10.3),(1.3,.13,20.5));F.box('fh-paving',(-5.15,.08,-10.3),(1.3,.16,20.5),True)
 for v in [-.5,-5,-10,-15,-20]:F.box('fh-white',(-5.76,1.7,v),(.13,3.2,.13))
 F.box('fh-paving',(0,.08,.8),(9.5,.16,1.6),True)
 for u,v in [(-1,-7),(1,-18)]:F.box('fh-service',(u,4.75,v),(1.4,.8,1.3));F.box('fh-dark',(u,5.17,v),(1.1,.04,1.0))
 F.box('fh-dark',(0,1.25,-26.17),(1.4,2.3,.08))
 # Compact public timber room; back services deliberately sealed.
 B.property=KEY+'-interior';B.source='public/'+KEY
 F.box('fh-floor',(0,.19,-10.7),(8.6,.06,20.9),True);F.box('fh-ceiling',(0,3.26,-10.7),(8.6,.14,20.9))
 for u in [-4.25,4.25]:F.box('fh-wood',(u,1.74,-10.7),(.14,3.05,20.9),True)
 for a,b in [(-4.25,-1.26),(.26,4.25)]:F.box('fh-wood',((a+b)/2,1.74,-.22),(b-a,3.05,.14),True)
 F.box('fh-wood',(-.5,2.91,-.22),(1.52,.7,.14),True);F.box('fh-wood',(0,1.74,-21.1),(8.5,3.05,.14),True)
 # Horizontal wood courses and ceiling beams reproduce the reference's timber character.
 for h in np.arange(.4,3.2,.23):
  for u in [-4.16,4.16]:F.box('fh-joint',(u,float(h),-10.7),(.025,.012,20.8))
 for v in np.arange(-.5,-21,-.24):F.box('fh-joint',(0,3.18,float(v)),(8.45,.015,.012))
 for v in [-1,-5,-9,-13,-17,-21]:F.box('fh-beam',(0,3.08,v),(8.45,.2,.12))
 # Bar and backbar with a physical service aisle, recessed taps and glass shelving.
 F.box('fh-darkwood',(-2.1,.72,-10.3),(.85,1.02,14),True);F.box('fh-wood',(-2.1,1.28,-10.3),(1.05,.12,14.2))
 F.tube('fh-brass',(-1.45,.42,-3.5),(-1.45,.42,-17.1),.035,12)
 for v in np.arange(-3.6,-17.2,-.55):F.box('fh-beam',(-1.66,.75,float(v)),(.06,.85,.035))
 for v in np.arange(-3.8,-17.2,-1.15):
  F.lathe('fh-metal',-.9,float(v),[(.22,0),(.22,.25),(.27,.25),(.3,.045),(.86,.045),(.88,.28)],20)
  F.lathe('fh-seat',-.9,float(v),[(.88,0),(.88,.28),(.98,.28),(.98,0)],24)
 for h in [.6,1.28,2.1,2.78]:F.box('fh-wood',(-3.86,h,-10.3),(.53,.065,14.1))
 rng=random.Random(332)
 for v in np.arange(-3.65,-17.2,-.32):
  for h in [1.32,2.14]:
   color='fh-bottle-'+str(rng.randrange(3));F.lathe(color,-3.83,float(v),[(h,0),(h,.055),(h+.23,.055),(h+.28,.023),(h+.34,.023),(h+.34,0)],12)
   F.box('fh-label',(-3.765,h+.14,float(v)),(.012,.11,.075))
 for v in [-6,-11,-16]:
  F.box('fh-metal',(-3.8,.8,v),(.5,.8,.75));F.box('fh-dark',(-3.8,1.32,v),(.37,.015,.57));F.path('fh-brass',[(-3.57,1.3,v),(-3.57,1.67,v),(-3.75,1.67,v)],.025,10)
 # Photo-supported booths; placement inferred on opposite wall with a clear longitudinal aisle.
 for v in [-4,-8,-12,-16]:
  F.box('fh-darkwood',(3.55,.44,v),(.95,.44,2.65),True);F.box('fh-seat',(3.45,.71,v),(.92,.14,2.65))
  F.box('fh-seat',(3.94,1.05,v),(.14,.75,2.65))
  for end in [-1,1]:F.box('fh-wood',(3.5,.94,v+end*1.4),(1.25,1.43,.12),True)
  F.box('fh-wood',(2.35,.95,v),(1.05,.09,1.55),True);F.box('fh-metal',(2.35,.57,v),(.09,.7,.09))
  for j in [-.42,.42]:F.lathe('fh-coaster',2.3,v+j,[(1,.095),(1.01,.095),(1.01,0)],16)
 # Original blank screens; no third-party broadcast pixels.
 for v in [-4.5,-10.5,-16.5]:
  F.box('fh-dark',(-2.55,2.65,v),(.12,.88,1.4));F.box('fh-screen',(-2.47,2.65,v),(.025,.76,1.25))
  F.tube('fh-metal',(-2.55,3.2,v),(-2.55,2.9,v),.035,8)
 for v in [-3,-8,-13,-18]:
  F.tube('fh-metal',(0,3.15,v),(0,2.55,v),.014,10);F.lathe('fh-metal',0,v,[(2.42,.15),(2.62,.04)],24);F.lathe('fh-lamp',0,v,[(2.42,0),(2.42,.09),(2.5,.09),(2.5,0)],16)
 for v in [-4,-11,-18]:F.light(.7,2.65,v,power=34,range=10)
 route=[F.p(u,y,v) for u,y,v in [(-.5,.16,2),(-.5,.22,-1),(1,.22,-2),(1,.22,-7),(1,.22,-13),(1,.22,-19)]]
 views={n:dict(eye=F.p(*e),target=F.p(*t)) for n,e,t in [('entrance',(-.5,1.8,-1),(1,1.5,-8)),('booths',(1,1.8,-6),(3.5,1.1,-8)),('bar',(1,1.8,-10),(-3.7,1.5,-11)),('rear',(1,1.8,-19),(0,1.5,-8))]}
 return dict(key=KEY,name='Fun Hog Ranch',center=[p.centroid.x,0,p.centroid.y],bounds=[p.bounds[0]-1,p.bounds[1]-3,p.bounds[2]+2,p.bounds[3]+1],structural=True,exteriorOnly=False,portals=[entry],zones=[dict(origin=F.p(0,.16,-.2),yaw=YAW+math.pi,width=8.6,depth=21,height=3.1)],lights=B.lights,hotelSources=[],routes=[dict(name='Front entrance, public bar aisle and return',points=route)],views=views)
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
