"""Original north 5115 frontage from February 2025 Street View.
Mapped perimeter; roof heights, glazing divisions and rear plant estimated.
No reproduced photographs or invented accessible interior.
"""
from common import *
KEY='dean-martin-north'
def build(B):
 B.property=KEY+'-exterior';B.source='podium/'+KEY;B.detail=0
 p=footprint('way/225705144');lo,zn,hi,zs=p.bounds
 B.shell(p,.02,5.45,'dn-stone',roof=False);B.planar('dn-roof',p,5.45)
 F=Frame(B,0,0,y=0)
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  L=math.dist(a,b);G=Frame(B,*a,math.atan2(-(b[1]-a[1]),b[0]-a[0]),y=0)
  out=1 if not p.covers(Point(G.p(L/2,0,.15)[::2])) else -1
  G.box('dn-cap-concrete',(L/2,5.5,0),(L,.14,.22))
  G.box('dn-concrete',(L/2,.16,out*.04),(L,.3,.16))
  for row,y in enumerate(np.arange(.5,5.4,.28)):
   B.face('dn-joint',[G.p(u,float(y)+dy,out*.025) for u,dy in [(0,0),(L,0),(L,.012),(0,.012)]])
   for u in np.arange(.25+(row%2)*.25,L,.5):
    B.face('dn-joint',[G.p(float(u)+dx,float(y)+dy,out*.026) for dx,dy in [(0,.014),(.009,.014),(.009,.28),(0,.28)]])
 # Follow the surveyed 0.49m slope along the south edge, rather than an axis-aligned facade.
 a=(-842.182,2122.529);b=(-770.879,2122.039);W=math.dist(a,b)
 N=Frame(B,(a[0]+b[0])/2,(a[1]+b[1])/2,math.atan2(-(b[1]-a[1]),b[0]-a[0]),y=0)
 E=Frame(B,hi-.04,2114.5,math.pi/2+.007,y=0)
 def mansard(G,width,top=5.55):
  B.upface('dn-metal-paint',[G.p(-width/2,top,-.12),G.p(width/2,top,-.12),G.p(width/2,3.55,1.15),G.p(-width/2,3.55,1.15)])
  for u in np.arange(-width/2,width/2,.28):
   B.upface('dn-rib-paint',[G.p(float(u),top+.025,-.10),G.p(min(float(u)+.035,width/2),top+.025,-.10),G.p(min(float(u)+.035,width/2),3.575,1.17),G.p(float(u),3.575,1.17)])
  G.box('dn-trim-paint',(0,3.5,1.15),(width,.16,.18))
 lowCenter=N.p(-7.55,0,0);highCenter=N.p(W/2-7.55,0,0)
 yaw=math.atan2(-(b[1]-a[1]),b[0]-a[0])
 L=Frame(B,lowCenter[0],lowCenter[2],yaw,y=0)
 H=Frame(B,highCenter[0],highCenter[2],yaw,y=0)
 mansard(L,W-15.1);mansard(H,15.1,6.65)
 H.box('dn-metal-paint',(0,6.04,-.13),(15.1,1.22,.22))
 B.face('dn-metal-paint',[H.p(-7.55,6.65,-.12),H.p(-7.55,5.55,-.12),H.p(-7.55,3.55,1.15)])
 mansard(E,15.1,6.65)
 # Raised street-end cap and explicit canopy corner closure.
 E.box('dn-metal-paint',(0,6.04,-.13),(15.1,1.22,.22))
 B.upface('dn-metal-paint',[(hi-.16,6.65,2122.02),(hi+1.1,3.55,2122.03),(hi,3.55,2123.2),(hi-.16,6.65,2121.92)])
 # Closed, recessed courtyard storefronts; exact tenant partitions are inferred.
 for u in np.arange(-W/2+5,W/2-2,8):
  N.box('dn-frame-paint',(float(u),1.72,.07),(6.2,2.75,.18))
  N.box('dn-glass',(float(u),1.72,.18),(6,2.55,.035))
  for dx in [-2,0,2]:N.box('dn-frame-paint',(float(u)+dx,1.72,.22),(.055,2.6,.05))
  N.box('dn-frame-paint',(float(u)+2,1.3,.25),(1.1,2.5,.05))
  N.box('dn-glass',(float(u)+2,1.3,.29),(.98,2.38,.025))
  N.box('dn-metal',(float(u)+1.7,1.1,.33),(.025,.3,.04))
  N.box('dn-trim-paint',(float(u)-3.8,1.76,1.04),(.1,3.45,.1))
 N.box('dn-concrete',(0,.04,.65),(W,.08,1.3),True)
 for u in [-5,-2.5,0,2.5,5]:
  E.box('dn-frame-paint',(u,1.72,.07),(2.4,2.7,.16))
  E.box('dn-glass',(u,1.72,.17),(2.26,2.5,.035))
  E.box('dn-sign',(u,1.8,.22),(1.65,.65,.03))
 E.box('dn-sign',(0,4.97,1.23),(14.6,2.05,.1))
 E.text('BENZ TEK PROFORMANCE',(0,5.42,1.30),.59,'dn-letter',back=True)
 E.text('LAS VEGAS EXOTIC',(0,4.79,1.30),.46,'dn-letter',back=True)
 E.text('COLLISION & REPAIR',(0,4.25,1.30),.46,'dn-letter',back=True)
 N.box('dn-dark-sign',(W/2-8,5.0,1.23),(12.8,1.15,.08))
 N.text('TATTOO',(W/2-8,4.58,1.30),.95,'dn-white',back=True)
 Q=Frame(B,-771.03,2097.9,math.pi/2+.007,y=0)
 Q.box('dn-yellow',(0,3.1,.16),(11.8,1.6,.09))
 Q.text('HOLLYWOOD',(0,3.30,.23),.62,'dn-letter',back=True)
 Q.text('CARS MUSEUM',(0,2.69,.23),.53,'dn-letter',back=True)
 for x,z in [(-831,2105),(-810,2104),(-789,2101)]:
  F.box('dn-metal',(x,5.83,z),(1.6,.65,1.2))
  for k in range(6):F.box('dn-vent',(x,6.17,z-.45+k*.18),(1.4,.025,.06))
 return dict(key=KEY,name='5115 north entrance / Benz Tek frontage',center=[p.centroid.x,0,p.centroid.y],bounds=[lo-1,zn-1,hi+2,zs+2],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[dict(name='south-courtyard-frontage',points=[[-774,.08,2125],[-805,.08,2125],[-837,.08,2125]])],hotelSources=[])
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
