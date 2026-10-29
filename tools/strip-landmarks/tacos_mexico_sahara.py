"""Original folded-roof restaurant; photo-supported public finishes, inferred layout."""
from common import *
KEY='tacos-mexico-sahara';ID='way/907577008'
def build(B):
 p=footprint(ID);F=Frame(B,-1683,-3189.4,0,y=0)
 B.property=KEY+'-exterior';B.source='podium/'+KEY;B.detail=0
 entry=dict(p=F.p(0,.16,.05),yaw=0,width=1.65,height=2.65,name='Public dining entrance',venue=KEY)
 B.shell(p,.1,3.35,'tm-wall',roof=False,openings=[entry]);B.planar('tm-floor',p,.16,True)
 # February2025 south Street View: four folded planes, not a flat parapet.
 folds=[(-10.1,5.05),(-5.1,3.45),(0,4.95),(5.0,3.45),(10.0,5.05)]
 for (a,ha),(b,hb) in zip(folds,folds[1:]):
  B.upface('tm-roof',[F.p(a,ha,.7),F.p(b,hb,.7),F.p(b,hb,-13.0),F.p(a,ha,-13.0)])
  B.face('tm-roof-under',[F.p(a,ha-.12,-13),F.p(b,hb-.12,-13),F.p(b,hb-.12,.7),F.p(a,ha-.12,.7)])
  B.face('tm-red',[F.p(a,ha,.72),F.p(a,ha-.22,.72),F.p(b,hb-.22,.72),F.p(b,hb,.72)])
  # Back wall closes folded roof voids without altering neighboring shells.
  B.face('tm-wall',[F.p(a,3.3,-12.0),F.p(b,3.3,-12.0),F.p(b,hb,-12.0),F.p(a,ha,-12.0)])
  for u in np.arange(a+.18,b,.42):
   h=ha+(hb-ha)*(float(u)-a)/(b-a)
   F.tube('tm-seam',(float(u),h+.015,.66),(float(u),h+.015,-12.95),.009,6)
 # Close upper shell along the surveyed footprint up to each folded plane.
 def roofh(x):
  u=x+1683
  for (a,ha),(b,hb) in zip(folds,folds[1:]):
   if a<=u<=b:return ha+(hb-ha)*(u-a)/(b-a)-.12
  return 4.9
 for poly in parts(p):
  for a,b in zip(list(poly.exterior.coords),list(poly.exterior.coords)[1:]):
   cuts=[0,1]
   if abs(b[0]-a[0])>.001:
    cuts += [(u-1683-a[0])/(b[0]-a[0]) for u,h in folds if 0<(u-1683-a[0])/(b[0]-a[0])<1]
   cuts.sort()
   for t0,t1 in zip(cuts,cuts[1:]):
    x0,z0=[a[i]+(b[i]-a[i])*t0 for i in range(2)];x1,z1=[a[i]+(b[i]-a[i])*t1 for i in range(2)]
    B.face('tm-wall',[(x0,3.3,z0),(x1,3.3,z1),(x1,roofh(x1),z1),(x0,roofh(x0),z0)])
 for u in [-9.5,9.4]:F.box('tm-red',(u,1.76,.1),(.17,3.25,.17),True)
 # Central peaked entrance: stone piers, low glazing and original small signs.
 for a,b in [(-3,-.86),(.86,3)]:
  F.box('tm-stone',((a+b)/2,1.82,.08),(b-a,3.35,.25),True)
  for j in range(7):
   u=a+.22+(j%3)*(b-a-.44)/2;y=.45+j*.43
   B.face('tm-red',[F.p(u-.15,y,.22),F.p(u+.19,y+.05,.22),F.p(u+.23,y+.24,.22),F.p(u-.09,y+.31,.22)])
 for a,b in [(-8.8,-3.1),(3.1,8.8)]:
  F.box('tm-panel',((a+b)/2,.7,.07),(b-a,1.0,.16))
  F.box('tm-glass',((a+b)/2,2.25,.11),(b-a,1.9,.08))
  for u in np.arange(a,b+.01,1.15):F.box('tm-metal',(float(u),2.25,.18),(.045,1.98,.08))
  for y in [1.28,2.65,3.22]:F.box('tm-metal',((a+b)/2,y,.18),(b-a,.05,.09))
 for u in [-.85,.85]:F.box('tm-metal',(u,1.53,.20),(.07,2.78,.10))
 F.box('tm-metal',(0,2.91,.20),(1.8,.08,.10))
 F.box('tm-red',(0,3.34,.24),(3.1,.68,.15));F.text('OPEN 24 HOURS',(0,3.37,.34),.25,'tm-letter',back=True)
 F.box('tm-paving',(0,.07,1.0),(19.5,.14,2.0),True)
 # Modest current pylon, estimated dimensions; no copied graphics.
 F.box('tm-red',(9.6,3.9,1.1),(.23,7.6,.23),True)
 F.box('tm-red',(9.6,6.5,1.1),(.24,2.6,1.8));F.box('tm-letter',(9.74,6.5,1.1),(.04,2.35,1.6))
 for u in [-5,5]:F.box('tm-service',(u,1.1,-11.8),(1,2,.1),True)
 F.box('tm-metal',(0,5.28,-7),(1.6,.65,1.3))
 B.property=KEY+'-interior';B.source='public/'+KEY
 # Room rectangle deliberately conservative inside mapped footprint; rear kitchen sealed.
 F.box('tm-grout',(0,.18,-4.1),(13.0,.025,8.0));F.box('tm-wall',(0,3.16,-4.1),(13.0,.12,8.0))
 for i,u in enumerate(np.arange(-6.5,6.4,.3)):
  for j,v in enumerate(np.arange(-8.1,-.1,.3)):
   F.box('tm-tile-red' if (i+j)%2 else 'tm-tile-cream',(float(u)+.15,.20,float(v)+.15),(.292,.018,.292))
 for u in [-6.5,6.5]:
  F.box('tm-wall',(u,1.7,-4.1),(.15,2.9,8),True);F.box('tm-tile-cream',(u, .82,-4.1),(.18,1.22,8));F.box('tm-red',(u,1.47,-4.1),(.19,.17,8))
  for v in np.arange(-8,0,.22):F.box('tm-grout',(u- .10 if u>0 else u+.10,.82,float(v)),(.015,1.2,.009))
  for y in np.arange(.24,1.43,.22):F.box('tm-grout',(u-.10 if u>0 else u+.10,float(y),-4.1),(.015,.009,8))
 F.box('tm-wall',(0,1.7,-8.2),(13.0,2.9,.15),True)
 # Dining booths along side walls; aisle and entrance remain clear.
 for side in [-1,1]:
  for v in [-2.4,-4.7,-7.0]:
   u=side*5.0
   F.box('tm-table',(u,.93,v),(2.2,.065,.85),True)
   for dx in [-.8,.8]:F.tube('tm-frame',(u+dx,.24,v),(u+dx,.90,v),.04,10)
   for dz in [-.78,.78]:
    F.box('tm-seat',(u,.64,v+dz),(2.25,.15,.49),True)
    F.box('tm-seat',(u,.93,v+dz+(.23 if dz>0 else -.23)),(2.25,.88,.10),True)
    F.box('tm-red',(u,.33,v+dz),(2.1,.46,.43),True)
 # Photo-supported stainless counter with diamond embossing, original menu typography.
 F.box('tm-metal',(0,.71,-7.5),(7.5,1.02,.9),True);F.box('tm-metal',(0,1.24,-7.4),(7.7,.08,1.15))
 for x in np.arange(-3.6,3.5,.35):
  for y in [.42,.77,1.1]:
   F.tube('tm-bright',(float(x)-.16,y,-7.035),(float(x),y+.16,-7.035),.006,5)
   F.tube('tm-bright',(float(x),y+.16,-7.035),(float(x)+.16,y,-7.035),.006,5)
   F.tube('tm-bright',(float(x)-.16,y,-7.035),(float(x),y-.16,-7.035),.006,5)
   F.tube('tm-bright',(float(x),y-.16,-7.035),(float(x)+.16,y,-7.035),.006,5)
 for u,word in [(-2.7,'TACOS'),(-.9,'BURRITOS'),(.9,'TORTAS'),(2.7,'QUESADILLAS')]:
  F.box('tm-red',(u,2.52,-8.04),(1.72,.85,.10));F.text(word,(u,2.73,-7.97),.14,'tm-letter',back=True)
  for j in range(4):F.box('tm-letter',(u,2.52-j*.10,-7.97),(1.3-j*.15,.025,.015))
 F.box('tm-frame',(0,1.7,-8.04),(1.7,.56,.1))
 for u in [-5,0,5]:
  for v in [-2.2,-5.8]:F.box('tm-lamp',(u,3.08,v),(1.05,.045,.18))
 for v in [-2.4,-6.3]:F.light(0,2.85,v,power=24,range=11)
 route=[F.p(u,.16,v) for u,v in [(0,2.4),(0,-1),(0,-4.5),(-3.3,-4.5),(-3.3,-1),(0,-1),(0,-6.5)]]
 views={n:dict(eye=F.p(*e),target=F.p(*t)) for n,e,t in [('entrance',(0,1.8,2),(0,1.4,-5)),('booths',(0,1.8,-3),(5.0,1,-4)),('counter',(0,1.8,-4.7),(0,1.5,-7.5)),('return',(-2,1.8,-5),(0,1.5,0))]}
 return dict(key=KEY,name='Tacos Mexico Sahara',center=[p.centroid.x,0,p.centroid.y],bounds=[p.bounds[0]-2,p.bounds[1]-2,p.bounds[2]+2,p.bounds[3]+3],structural=True,exteriorOnly=False,portals=[entry],zones=[dict(origin=F.p(0,.16,-.1),yaw=math.pi,width=13.0,depth=8,height=3)],lights=B.lights,hotelSources=[],routes=[dict(name='Dining and counter',points=route)],views=views)
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
