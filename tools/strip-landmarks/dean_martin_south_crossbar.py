"""Original southern courtyard crossbar frontage from December 2022 Street View.
Mapped shell; heights, bay spacing and hidden services are estimates. Interior closed.
"""
from common import *
KEY='dean-martin-south-crossbar'
def build(B):
 B.property=KEY+'-exterior';B.source='podium/'+KEY;B.detail=0
 p=footprint('way/225705140');lo,zn,hi,zs=p.bounds
 B.shell(p,.02,4.65,'dc-stone',roof=False);B.planar('dc-roof',p,4.65)
 F=Frame(B,0,0,y=0)
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  L=math.dist(a,b);G=Frame(B,*a,math.atan2(-(b[1]-a[1]),b[0]-a[0]),y=0)
  out=1 if not p.covers(Point(G.p(L/2,0,.15)[::2])) else -1
  G.box('dc-cap-concrete',(L/2,4.7,0),(L,.14,.22))
  G.box('dc-concrete',(L/2,.16,out*.04),(L,.3,.16))
  for row,y in enumerate(np.arange(.5,4.6,.28)):
   B.face('dc-joint',[G.p(u,float(y)+dy,out*.025) for u,dy in [(0,0),(L,0),(L,.012),(0,.012)]])
   for u in np.arange(.25+(row%2)*.25,L,.5):
    B.face('dc-joint',[G.p(float(u)+dx,float(y)+dy,out*.026) for dx,dy in [(0,.014),(.009,.014),(.009,.28),(0,.28)]])
 # Local +x runs west; local +z points north into the courtyard.
 a=(-854.933,2258.005);b=(-922.027,2257.548);W=math.dist(a,b)
 N=Frame(B,(a[0]+b[0])/2,(a[1]+b[1])/2,math.atan2(-(b[1]-a[1]),b[0]-a[0]),y=0)
 w=W-3.0
 B.upface('dc-metal-paint',[N.p(-w/2,4.75,-.12),N.p(w/2,4.75,-.12),N.p(w/2,3.2,1.35),N.p(-w/2,3.2,1.35)])
 B.upface('dc-trim-paint',[N.p(-w/2,3.17,0),N.p(w/2,3.17,0),N.p(w/2,3.17,1.36),N.p(-w/2,3.17,1.36)])
 for u in np.arange(-w/2,w/2,.3):
  B.upface('dc-rib-paint',[N.p(float(u),4.78,-.10),N.p(min(float(u)+.035,w/2),4.78,-.10),N.p(min(float(u)+.035,w/2),3.23,1.37),N.p(float(u),3.23,1.37)])
 for u in [-w/2,w/2]:B.face('dc-metal-paint',[N.p(u,4.75,-.12),N.p(u,3.17,-.12),N.p(u,3.17,1.36)])
 N.box('dc-trim-paint',(0,3.17,1.35),(w,.15,.16))
 # Reference alternates narrow glazed entrances with opaque vertically ribbed panels.
 N.box('dc-metal-paint',(0,1.63,.07),(w,3.0,.12))
 for u in np.arange(-w/2,w/2,.29):N.box('dc-rib-paint',(float(u),1.63,.15),(.025,2.95,.025))
 bays=[-26,-18,-10,10,18,26]
 for i,u in enumerate(bays):
  ww=4.6 if i%3 else 5.4
  N.box('dc-frame-paint',(u,1.55,.20),(ww,2.85,.13))
  N.box('dc-glass',(u,1.55,.29),(ww-.14,2.69,.03))
  N.box('dc-frame-paint',(u,2.22,.34),(ww,.055,.035))
  for dx in [-ww/2+1.1,ww/2-1.1]:N.box('dc-frame-paint',(u+dx,1.55,.34),(.045,2.75,.04))
  N.box('dc-frame-paint',(u+.35,1.26,.37),(1.05,2.5,.05))
  N.box('dc-glass',(u+.35,1.26,.41),(.94,2.38,.025))
  N.box('dc-metal',(u+.75,1.10,.45),(.025,.3,.04))
  N.box('dc-trim-paint',(u-3.3,1.65,1.25),(.10,3.2,.10))
  # Small unlettered business plaques: names are not sufficiently legible to attribute.
  if i%2==0:N.box('dc-sign',(u,2.66,.38),(2.6,.43,.04))
 # Broad higher blockwork pier divides two tenant frontage runs, as photographed.
 N.box('dc-stone',(0,2.7,.46),(10,5.4,2.2),True)
 N.text('3',(-.2,4.35,1.61),.32,'dc-letter',back=True)
 N.box('dc-sign',(3,4.65,1.59),(2.8,.72,.06))
 N.text('COMPLETE',(3,4.8,1.64),.20,'dc-letter',back=True)
 N.text('ALIGNMENT',(3,4.46,1.64),.20,'dc-letter',back=True)
 N.box('dc-cap-concrete',(0,5.47,.46),(10.15,.14,2.3))
 for row,y in enumerate(np.arange(.3,5.3,.28)):
  N.box('dc-joint',(0,float(y),1.575),(9.95,.012,.015))
  for u in np.arange(-4.8+(row%2)*.25,4.9,.5):
   N.box('dc-joint',(float(u),float(y)+.14,1.575),(.009,.26,.015))
 N.box('dc-concrete',(0,.04,.75),(W,.08,1.5),True)
 for u in [-W/2+.65,W/2-.65]:
  N.box('dc-stone',(u,2.5,.25),(1.3,5,.55))
  N.box('dc-cap-concrete',(u,5.04,.25),(1.4,.12,.65))
 # Modest inferred rear servicing, explicitly not a reconstructed hidden interior.
 R=Frame(B,(lo+hi)/2,2271.252,0,y=0)
 for u in [-25,0,25]:
  R.box('dc-frame-paint',(u,1.25,.15),(1.3,2.5,.13))
  R.box('dc-metal-paint',(u,1.25,.23),(1.15,2.36,.035))
  R.box('dc-vent',(u+3,2.2,.16),(1.5,.7,.09))
 for x in [-912,-889,-866]:
  F.box('dc-metal',(x,4.99,2265),(1.5,.65,1.2))
  for k in range(6):F.box('dc-vent',(x,5.33,2265-.45+k*.18),(1.3,.025,.06))
 return dict(key=KEY,name='5115 southern courtyard crossbar frontage',center=[p.centroid.x,0,p.centroid.y],bounds=[lo-1,zn-2,hi+1,zs+1],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[dict(name='north-courtyard-frontage',points=[[-917,.08,2254.5],[-889,.08,2254.5],[-859,.08,2254.5]])],hotelSources=[])
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
