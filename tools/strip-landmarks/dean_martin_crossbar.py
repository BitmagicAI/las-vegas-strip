"""Original northern courtyard crossbar frontage from December 2022 Street View.
Mapped shell; heights, bay spacing and hidden services are estimates. Interior closed.
"""
from common import *
KEY='dean-martin-crossbar'
def build(B):
 B.property=KEY+'-exterior';B.source='podium/'+KEY;B.detail=0
 p=footprint('way/225705136');lo,zn,hi,zs=p.bounds
 B.shell(p,.02,4.65,'dx-stone',roof=False);B.planar('dx-roof',p,4.65)
 F=Frame(B,0,0,y=0)
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  L=math.dist(a,b);G=Frame(B,*a,math.atan2(-(b[1]-a[1]),b[0]-a[0]),y=0)
  out=1 if not p.covers(Point(G.p(L/2,0,.15)[::2])) else -1
  G.box('dx-cap-concrete',(L/2,4.7,0),(L,.14,.22))
  G.box('dx-concrete',(L/2,.16,out*.04),(L,.3,.16))
  for row,y in enumerate(np.arange(.5,4.6,.28)):
   B.face('dx-joint',[G.p(u,float(y)+dy,out*.025) for u,dy in [(0,0),(L,0),(L,.012),(0,.012)]])
   for u in np.arange(.25+(row%2)*.25,L,.5):
    B.face('dx-joint',[G.p(float(u)+dx,float(y)+dy,out*.026) for dx,dy in [(0,.014),(.009,.014),(.009,.28),(0,.28)]])
 # Local +x runs east; local +z points south into the courtyard.
 a=(-926.128,2002.37);b=(-852.658,2001.914);W=math.dist(a,b)
 N=Frame(B,(a[0]+b[0])/2,(a[1]+b[1])/2,math.atan2(-(b[1]-a[1]),b[0]-a[0]),y=0)
 w=W-3.0
 B.upface('dx-metal-paint',[N.p(-w/2,4.75,-.12),N.p(w/2,4.75,-.12),N.p(w/2,3.2,1.35),N.p(-w/2,3.2,1.35)])
 B.upface('dx-trim-paint',[N.p(-w/2,3.17,0),N.p(w/2,3.17,0),N.p(w/2,3.17,1.36),N.p(-w/2,3.17,1.36)])
 for u in np.arange(-w/2,w/2,.3):
  B.upface('dx-rib-paint',[N.p(float(u),4.78,-.10),N.p(min(float(u)+.035,w/2),4.78,-.10),N.p(min(float(u)+.035,w/2),3.23,1.37),N.p(float(u),3.23,1.37)])
 for u in [-w/2,w/2]:B.face('dx-metal-paint',[N.p(u,4.75,-.12),N.p(u,3.17,-.12),N.p(u,3.17,1.36)])
 N.box('dx-trim-paint',(0,3.17,1.35),(w,.15,.16))
 # Reference alternates narrow glazed entrances with opaque vertically ribbed panels.
 N.box('dx-metal-paint',(0,1.63,.07),(w,3.0,.12))
 for u in np.arange(-w/2,w/2,.29):N.box('dx-rib-paint',(float(u),1.63,.15),(.025,2.95,.025))
 bays=[-30,-22,-2,7,16,25,32]
 for i,u in enumerate(bays):
  ww=4.6 if i%3 else 5.4
  N.box('dx-frame-paint',(u,1.55,.20),(ww,2.85,.13))
  N.box('dx-glass',(u,1.55,.29),(ww-.14,2.69,.03))
  N.box('dx-frame-paint',(u,2.22,.34),(ww,.055,.035))
  for dx in [-ww/2+1.1,ww/2-1.1]:N.box('dx-frame-paint',(u+dx,1.55,.34),(.045,2.75,.04))
  N.box('dx-frame-paint',(u+.35,1.26,.37),(1.05,2.5,.05))
  N.box('dx-glass',(u+.35,1.26,.41),(.94,2.38,.025))
  N.box('dx-metal',(u+.75,1.10,.45),(.025,.3,.04))
  N.box('dx-trim-paint',(u-3.3,1.65,1.25),(.10,3.2,.10))
  # Small unlettered business plaques: names are not sufficiently legible to attribute.
  if i%2==0:N.box('dx-sign',(u,2.66,.38),(2.6,.43,.04))
 # Broad higher blockwork pier divides two tenant frontage runs, as photographed.
 N.box('dx-stone',(-12.5,2.7,.46),(10,5.4,2.2))
 N.text('7',(-16.7,4.35,1.61),.32,'dx-letter')
 N.box('dx-cap-concrete',(-12.5,5.47,.46),(10.15,.14,2.3))
 for row,y in enumerate(np.arange(.3,5.3,.28)):
  N.box('dx-joint',(-12.5,float(y),1.575),(9.95,.012,.015))
  for u in np.arange(-17.3+(row%2)*.25,-7.6,.5):
   N.box('dx-joint',(float(u),float(y)+.14,1.575),(.009,.26,.015))
 N.box('dx-concrete',(0,.04,.75),(W,.08,1.5),True)
 for u in [-W/2+.65,W/2-.65]:
  N.box('dx-stone',(u,2.5,.25),(1.3,5,.55))
  N.box('dx-cap-concrete',(u,5.04,.25),(1.4,.12,.65))
 # Modest inferred rear servicing, explicitly not a reconstructed hidden interior.
 R=Frame(B,(lo+hi)/2,1988.9,math.pi+.0185,y=0)
 for u in [-25,0,25]:
  R.box('dx-frame-paint',(u,1.25,.15),(1.3,2.5,.13))
  R.box('dx-metal-paint',(u,1.25,.23),(1.15,2.36,.035))
  R.box('dx-vent',(u+3,2.2,.16),(1.5,.7,.09))
 for x in [-913,-890,-866]:
  F.box('dx-metal',(x,4.99,1995),(1.5,.65,1.2))
  for k in range(6):F.box('dx-vent',(x,5.33,1995-.45+k*.18),(1.3,.025,.06))
 return dict(key=KEY,name='5115 northern courtyard crossbar frontage',center=[p.centroid.x,0,p.centroid.y],bounds=[lo-1,zn-1,hi+2,zs+1],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[dict(name='south-courtyard-frontage',points=[[-922,.08,2005.5],[-890,.08,2005.5],[-857,.08,2005.5]])],hotelSources=[])
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
