"""Original exterior from Jan2020 west facade and aerial. Unmeasured heights fitted."""
from common import *
KEY='dennys-sahara';IDS=['way/905241566']
def build(B):
 B.property=KEY+'-exterior';B.source='retail/'+KEY;B.detail=0
 p=footprint(IDS[0]);main=p.intersection(box(-880,-3240,-830,-3203.5));B.shell(main,.02,5.25,'ds-cream',roof=False);B.planar('ds-membrane',main,5.18)
 # Two distinct roof volumes: northern services and southern clerestory dining bay.
 S=Frame(B,-854.5,-3209.0,.025,y=0)
 corners=[(-7.2,5.45,-9.5),(7.2,5.45,-9.5),(7.2,5.45,5.5),(-7.2,5.45,5.5)]
 a,b,c,d=[S.p(*v) for v in corners];ridgeN=S.p(0,7.5,-3.5);ridgeS=S.p(0,7.5,0.5)
 for poly in [[a,b,ridgeN],[b,c,ridgeS,ridgeN],[c,d,ridgeS],[d,a,ridgeN,ridgeS]]:B.upface('ds-metal',poly)
 # Standing seams follow each hip face rather than a generic roof bitmap.
 for u in np.arange(-6.9,7,.65):
  t=1-abs(float(u))/7.2
  for z,run in [(-9.5,6),(5.5,-5)]:
   S.tube('ds-seam',(float(u),5.49,z),(float(u),5.49+2.05*t,z+run*t),.012,5)
 for side in [-1,1]:
  for v in np.arange(-9.2,5.3,.65):
   t=max(0,min(1,(float(v)+9.5)/6,(5.5-float(v))/5))
   S.tube('ds-seam',(side*7.2,5.49,float(v)),(side*7.2*(1-t),5.49+2.05*t,float(v)),.012,5)
 for a,b in zip(corners,corners[1:]+corners[:1]):S.tube('ds-metal',a,b,.10,8)
 ring=list(main.exterior.coords)
 for a,b in zip(ring,ring[1:]):
  dx,dz=b[0]-a[0],b[1]-a[1];L=math.hypot(dx,dz);F=Frame(B,(a[0]+b[0])/2,(a[1]+b[1])/2,math.atan2(-dz,dx),y=0)
  F.box('ds-silver',(0,3.23,0),(L,.32,.65));F.box('ds-metal',(0,3.05,0),(L,.05,.72))
  if F.z<-3219:
   F.box('ds-cream',(0,5.3,0),(L,.3,.2))
   if L>5:
    for side in [-1,1]:F.box('ds-service',(0,1.4,side*.12),(1.2,2.7,.08))
   continue
  if L<3:continue
  # Lower stone courses, upper creamy wall; slim original stone relief.
  for side in [-1,1]:
   F.box('ds-stone',(0,1.5,side*.07),(L,3,.12))
   for row in range(19):
    x=-L/2
    rng=random.Random(row+int(abs(F.x)*13+abs(F.z)))
    while x<L/2-.1:
     w=min(rng.uniform(.25,.75),L/2-x);F.box('ds-stone'+str(rng.randrange(3)),(x+w/2,.1+row*.15,side*.15),(max(.03,w-.015),.13,.06));x+=w
   for u in np.linspace(-L/2+1.1,L/2-1.1,max(1,int(L/3.2))):
    # Both lower dining windows and the upper clerestory are visible architectural layers.
    for y,h in [(1.83,2.05),(4.4,.85)]:
     F.box('ds-glass',(float(u),y,side*.23),(1.75,h,.035))
     for du in [-.9,0,.9]:F.box('ds-alloy',(float(u)+du,y,side*.27),(.045,h+.08,.05))
     for dy in [-h/2,h/2]:F.box('ds-alloy',(float(u),y+dy,side*.27),(1.85,.045,.05))
 # West double entrance below broad silver awning; closed until an interior is evidenced.
 W=Frame(B,-862.2,-3210,-math.pi/2,y=0)
 W.box('ds-silver',(0,3.2,.55),(9.5,.24,1.4))
 for u in [-2,1]:
  W.box('ds-glass',(u,1.48,.40),(2.15,2.85,.045))
  for du in [-1.1,0,1.1]:W.box('ds-alloy',(u+du,1.48,.46),(.055,2.95,.06))
  for y in [.04,2.91]:W.box('ds-alloy',(u,y,.46),(2.25,.06,.06))
  for du in [-.12,.12]:W.box('ds-alloy',(u+du,1.25,.52),(.035,.5,.035))
 # South projecting glazed canopy/rail and red sign panel seen at right of west photo.
 F=Frame(B,-853,-3203.5,.013,y=0)
 F.box('ds-silver',(0,3.15,1.8),(10.5,.28,3.8))
 for u in [-5,5]:F.box('ds-stone',(u,1.5,3.3),(.4,3,.4),True)
 W.box('ds-red',(7.8,3.98,.35),(3.3,1.35,.18));W.text("Denny's",(7.8,3.72,.48),.64,'ds-letter',back=True)
 F.box('ds-paving',(0,.07,1.8),(10,.14,3.8),True)
 for side in [-1,1]:
  lo,hi=(-4.8,-1.3) if side<0 else (1.3,4.8)
  for y in [.22,1.05]:F.box('ds-rail',((lo+hi)/2,y,2.2),(hi-lo,.055,.055))
  for u in np.arange(lo,hi,.17):F.box('ds-rail',(float(u),.63,2.2),(.023,.84,.023))
 B.upface('ds-paving',[F.p(-1.2,.01,4),F.p(1.2,.01,4),F.p(1.2,.14,1.9),F.p(-1.2,.14,1.9)],True)
 # Small northern service units; preserve mapped drives and landscape ownership.
 G=Frame(B,-853,-3224,0,y=0)
 for u,v in [(-2,0),(2,-1),(-1,3)]:
  G.box('ds-equipment',(u,5.8,v),(1.7,1.1,1.4));G.box('ds-metal',(u,6.36,v),(1.5,.025,1.2))
 routes=[dict(name='South canopy approach',points=[F.p(0,.18,v) for v in [8,5,3,1]]),dict(name='West entrance approach',points=[[-869,.22,-3210],[-866,.22,-3210],[-863,.22,-3210]]),dict(name='East frontage',points=[[-842,.22,z] for z in [-3197,-3208,-3220]])]
 return dict(key=KEY,name='Dennys West Sahara',center=[-855,0,-3214],bounds=list(p.bounds),structural=True,hotelSources=[],exteriorOnly=True,portals=[],zones=[],lights=[],routes=routes)
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
