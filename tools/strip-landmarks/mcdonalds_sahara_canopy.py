"""Mapped Sahara McDonald's corner canopy, February2026 street-reference pass."""
from common import *
from forum_shops import facade_frame
KEY='mcdonaldsSaharaCanopy';IDS=['way/1414999331']
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/mcdonalds-sahara-canopy';B.detail=0;p=footprint(IDS[0]);main=footprint('way/276427175');edges=[facade_frame(B,a,b,p,0)for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:])];F,L,_,_=max([e for e in edges if e[3]>.6],key=lambda e:e[1]);depth=max((z-F.z)*F.co+(x-F.x)*F.si for x,z in p.exterior.coords)
 # Solid top and downward soffit are separate faces of a single canopy slab.
 B.planar('mc-canopy-roof-paint',p,4.65,True)
 for tri in triangles(p):
  vs=[(x,3.95,z)for x,z in list(tri.exterior.coords)[:-1]]
  if np.cross(np.array(vs[1])-vs[0],np.array(vs[2])-vs[0])[1]>0:vs=vs[::-1]
  B.face('mc-soffit-paint',vs,True)
 for G,ll,nx,nz in edges:
  mid=Point(G.p(ll/2,0,0)[::2])
  if main.distance(mid)<.08:continue
  B.face('mc-fascia-paint',[G.p(0,4.65,0),G.p(ll,4.65,0),G.p(ll,3.95,.42),G.p(0,3.95,.42)],True)
  for y in [4.53,4.64]:G.box('mc-coping-paint',(ll/2,y,-.035),(ll,.045,.09))
  if ll>18:G.text("McDonald's",(ll/2,4.12,-.10),.55,'mc-white-letter')
 # Pale angled canopy supports, positioned away from the central approach.
 for u in [1.5,L-1.5]:
  for w in [2.4,depth-2.7]:
   for lean in [-.38,.38]:F.tube('mc-post-paint',(u,.18,w),(u+lean,3.95,w+.25),.10,12)
   F.box('mc-base-paint',(u,.22,w),(.5,.08,.6),True)
 # Two tall yellow side arches; low ends at opposite ends of the canopy.
 for u in [.55,L-.55]:
  points=[(u,.65+8.1*math.sin(math.pi*t),-.15+(depth+.3)*t)for t in np.linspace(0,1,65)]
  for a,b in zip(points,points[1:]):
   # Rectangular section avoids a round pipe silhouette.
   aa=np.array(a);bb=np.array(b);dv=bb-aa;normal=np.array([0,-dv[2],dv[1]]);normal=normal/np.linalg.norm(normal)*.32
   for side in [-1,1]:B.face('mc-yellow-paint',[F.p(*(aa+normal+[side*.16,0,0])),F.p(*(bb+normal+[side*.16,0,0])),F.p(*(bb-normal+[side*.16,0,0])),F.p(*(aa-normal+[side*.16,0,0]))])
   for sign in [-1,1]:B.face('mc-yellow-paint',[F.p(*(aa+sign*normal+[-.16,0,0])),F.p(*(bb+sign*normal+[-.16,0,0])),F.p(*(bb+sign*normal+[.16,0,0])),F.p(*(aa+sign*normal+[.16,0,0]))])
 # Roof equipment curb and shallow louvres, not another floating floor.
 cu=L*.51;cw=depth*.56
 F.box('mc-roof-curb-paint',(cu,4.94,cw),(4.1,.58,4.1));F.box('mc-vent-paint',(cu,5.24,cw),(3.6,.04,3.6))
 for u in np.arange(cu-1.5,cu+1.6,.26):F.box('mc-service-paint',(float(u),5.32,cw),(.06,.10,3.2))
 B.planar('mc-concrete',p,.18,True)
 for u in [L*.25,L*.5,L*.75]:
  F.box('mc-light-paint',(u,3.92,depth*.35),(.32,.05,.55))
 samples=[]
 for x in np.arange(p.bounds[0]+.5,p.bounds[2],1.2):
  for z in np.arange(p.bounds[1]+.5,p.bounds[3],1.2):
   if p.buffer(-.35).contains(Point(x,z)):samples.append([float(x),5.03,float(z)])
 routes=[[F.p(u,.18,.6),F.p(u,.18,depth*.55),F.p(u,.18,depth-1.6)]for u in [L*.25,L*.5,L*.75]]
 Path('build/city-exteriors/mcdonalds-sahara-canopy-samples.json').write_text(json.dumps(samples));Path('build/city-exteriors/mcdonalds-sahara-canopy-stairs.json').write_text(json.dumps(routes))
 return dict(key=KEY,name='McDonalds Sahara corner canopy',center=[1612,0,-3114],bounds=list(p.bounds),structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
