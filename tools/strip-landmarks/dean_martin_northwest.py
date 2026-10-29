"""Original north west courtyard frontage from December 2022 Street View.
Mapped shell; heights, bay spacing and hidden services are estimates. Interior closed.
"""
from common import *
KEY='dean-martin-northwest'
def build(B):
 B.property=KEY+'-exterior';B.source='podium/'+KEY;B.detail=0
 p=footprint('way/225705137');lo,zn,hi,zs=p.bounds
 B.shell(p,.02,4.65,'dw-stone',roof=False);B.planar('dw-roof',p,4.65)
 F=Frame(B,0,0,y=0)
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  L=math.dist(a,b);G=Frame(B,*a,math.atan2(-(b[1]-a[1]),b[0]-a[0]),y=0)
  out=1 if not p.covers(Point(G.p(L/2,0,.15)[::2])) else -1
  G.box('dw-cap-concrete',(L/2,4.7,0),(L,.14,.22))
  G.box('dw-concrete',(L/2,.16,out*.04),(L,.3,.16))
  for row,y in enumerate(np.arange(.5,4.6,.28)):
   B.face('dw-joint',[G.p(u,float(y)+dy,out*.025) for u,dy in [(0,0),(L,0),(L,.012),(0,.012)]])
   for u in np.arange(.25+(row%2)*.25,L,.5):
    B.face('dw-joint',[G.p(float(u)+dx,float(y)+dy,out*.026) for dx,dy in [(0,.014),(.009,.014),(.009,.28),(0,.28)]])
 # Local +x runs north; local +z points east into the courtyard.
 a=(-900.571,2081.352);b=(-901.03,2021.094);W=math.dist(a,b)
 N=Frame(B,(a[0]+b[0])/2,(a[1]+b[1])/2,math.atan2(-(b[1]-a[1]),b[0]-a[0]),y=0)
 w=W-3.0
 B.upface('dw-metal-paint',[N.p(-w/2,4.75,-.12),N.p(w/2,4.75,-.12),N.p(w/2,3.2,1.35),N.p(-w/2,3.2,1.35)])
 B.upface('dw-trim-paint',[N.p(-w/2,3.17,0),N.p(w/2,3.17,0),N.p(w/2,3.17,1.36),N.p(-w/2,3.17,1.36)])
 for u in np.arange(-w/2,w/2,.3):
  B.upface('dw-rib-paint',[N.p(float(u),4.78,-.10),N.p(min(float(u)+.035,w/2),4.78,-.10),N.p(min(float(u)+.035,w/2),3.23,1.37),N.p(float(u),3.23,1.37)])
 for u in [-w/2,w/2]:B.face('dw-metal-paint',[N.p(u,4.75,-.12),N.p(u,3.17,-.12),N.p(u,3.17,1.36)])
 N.box('dw-trim-paint',(0,3.17,1.35),(w,.15,.16))
 # Reference alternates narrow glazed entrances with opaque vertically ribbed panels.
 N.box('dw-metal-paint',(0,1.63,.07),(w,3.0,.12))
 for u in np.arange(-w/2,w/2,.29):N.box('dw-rib-paint',(float(u),1.63,.15),(.025,2.95,.025))
 bays=[-23,-14,-5,4,13,22]
 for i,u in enumerate(bays):
  ww=3.8 if i%3 else 5.0
  N.box('dw-frame-paint',(u,1.55,.20),(ww,2.85,.13))
  N.box('dw-glass',(u,1.55,.29),(ww-.14,2.69,.03))
  N.box('dw-frame-paint',(u,2.22,.34),(ww,.055,.035))
  for dx in [-ww/2+1.1,ww/2-1.1]:N.box('dw-frame-paint',(u+dx,1.55,.34),(.045,2.75,.04))
  N.box('dw-frame-paint',(u+.35,1.26,.37),(1.05,2.5,.05))
  N.box('dw-glass',(u+.35,1.26,.41),(.94,2.38,.025))
  N.box('dw-metal',(u+.75,1.10,.45),(.025,.3,.04))
  N.box('dw-trim-paint',(u-3.3,1.65,1.25),(.10,3.2,.10))
  # Small unlettered business plaques: names are not sufficiently legible to attribute.
  if i%2==0:N.box('dw-sign',(u,2.66,.38),(2.6,.43,.04))
  # Observed security bars remain separated from the glass, avoiding coplanar faces.
  if i in [1,3,4]:
   for dx in np.arange(-ww/2+.16,ww/2-.1,.20):
    N.box('dw-metal',(u+float(dx),1.55,.49),(.018,2.6,.025))
   for y in [.3,1.5,2.8]:N.box('dw-metal',(u,y,.49),(ww-.15,.025,.03))
  if i in [0,3]:
   N.box('dw-metal',(u+2.8,.45,.65),(1.35,.07,.42))
   for dx in [-.52,.52]:N.box('dw-metal',(u+2.8+dx,.22,.65),(.055,.44,.3))
  if i==2:
   N.box('dw-metal-paint',(u+2.9,.43,.4),(.72,.55,.45))
   for y in np.arange(.22,.66,.06):N.box('dw-vent',(u+2.9,float(y),.64),(.63,.02,.02))
 N.box('dw-concrete',(0,.04,.75),(W,.08,1.5),True)
 for u in [-W/2+.65,W/2-.65]:
  N.box('dw-stone',(u,2.5,.25),(1.3,5,.55))
  N.box('dw-cap-concrete',(u,5.04,.25),(1.4,.12,.65))
 # Modest inferred rear servicing, explicitly not a reconstructed hidden interior.
 R=Frame(B,-923.85,(zn+zs)/2,-math.pi/2-.015,y=0)
 for u in [-19,0,19]:
  R.box('dw-frame-paint',(u,1.25,.15),(1.3,2.5,.13))
  R.box('dw-metal-paint',(u,1.25,.23),(1.15,2.36,.035))
  R.box('dw-vent',(u+3,2.2,.16),(1.5,.7,.09))
 for z in [2030,2051,2072]:
  F.box('dw-metal',(-911,4.99,z),(1.5,.65,1.2))
  for k in range(6):F.box('dw-vent',(-911,5.33,z-.45+k*.18),(1.3,.025,.06))
 return dict(key=KEY,name='5115 north west courtyard frontage',center=[p.centroid.x,0,p.centroid.y],bounds=[lo-1,zn-1,hi+2,zs+1],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[dict(name='east-courtyard-frontage',points=[[-897,.08,2025],[-897,.08,2051],[-897,.08,2077]])],hotelSources=[])
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
