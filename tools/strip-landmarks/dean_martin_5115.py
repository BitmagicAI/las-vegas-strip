"""Original 5115 Dean Martin east-front building, February 2025 reference.
Mapped perimeter; heights and tenant bay divisions are estimated. Closed interior.
"""
from common import *
KEY='dean-martin-5115'
def build(B):
 B.property=KEY+'-exterior';B.source='podium/'+KEY;B.detail=0
 p=footprint('way/225705143');lo,zn,hi,zs=p.bounds
 B.shell(p,.02,5.65,'dm-stone',roof=False);B.planar('dm-roof',p,5.65)
 F=Frame(B,0,0,y=0)
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  L=math.dist(a,b);G=Frame(B,*a,math.atan2(-(b[1]-a[1]),b[0]-a[0]),y=0)
  out=1 if not p.covers(Point(G.p(L/2,0,.15)[::2])) else -1
  G.box('dm-cap-concrete',(L/2,5.68,0),(L,.14,.22))
  G.box('dm-concrete',(L/2,.16,out*.04),(L,.3,.16))
  for row,y in enumerate(np.arange(.5,5.5,.28)):
   B.face('dm-joint',[G.p(u,float(y)+dy,out*.025) for u,dy in [(0,0),(L,0),(L,.012),(0,.012)]])
   for u in np.arange(.25+(row%2)*.25,L,.5):
    B.face('dm-joint',[G.p(float(u)+dx,float(y)+dy,out*.026) for dx,dy in [(0,.014),(.009,.014),(.009,.28),(0,.28)]])
 # Courtyard frontage is north-facing; the road end turns east at its north half.
 N=Frame(B,(lo+hi)/2,zn,math.pi,y=0);W=hi-lo
 E=Frame(B,hi,zn+5.63,math.pi/2,y=0)
 def mansard(G,width):
  B.upface('dm-metal-paint',[G.p(-width/2,5.75,-.12),G.p(width/2,5.75,-.12),G.p(width/2,3.65,1.15),G.p(-width/2,3.65,1.15)])
  for u in np.arange(-width/2,width/2,.28):
   B.upface('dm-rib-paint',[G.p(float(u),5.78,-.1),G.p(float(u)+.035,5.78,-.1),G.p(float(u)+.035,3.68,1.17),G.p(float(u),3.68,1.17)])
  G.box('dm-trim-paint',(0,3.61,1.15),(width,.16,.18))
 mansard(N,W);mansard(E,11.26)
 B.upface('dm-metal-paint',[(hi,5.75,zn+.12),(hi+1.15,3.65,zn),(hi,3.65,zn-1.15),(hi-.12,5.75,zn)])
 # Glazed courtyard bays and opaque backing preserve unverified interiors.
 for u in np.arange(-W/2+5,W/2-2,8):
  N.box('dm-frame-paint',(float(u),1.85,.07),(5.7,2.65,.18))
  N.box('dm-glass',(float(u),1.85,.18),(5.5,2.45,.035))
  for dx in [-1.8,0,1.8]:N.box('dm-frame-paint',(float(u)+dx,1.85,.22),(.045,2.5,.04))
  N.box('dm-frame-paint',(float(u)+1.8,1.3,.25),(1.1,2.5,.05))
  N.box('dm-glass',(float(u)+1.8,1.3,.29),(.98,2.38,.025))
  N.box('dm-metal',(float(u)+1.5,1.1,.33),(.025,.3,.04))
 N.box('dm-concrete',(0,.04,.65),(W,.08,1.3),True)
 # Original lettering and simple panels only; no copied promotional artwork.
 E.box('dm-sign',(0,4.62,1.22),(10.7,1.55,.12))
 E.text('HOLLYWOOD CARS MUSEUM',(0,5.07,1.3),.44,'dm-letter',back=True)
 E.text('HERE',(0,3.98,1.3),1.20,'dm-red',back=True)
 E.text('5155',(-5.0,3.1,.17),.43,'dm-letter',back=True)
 S=Frame(B,-770.09,2166,math.pi/2,y=0)
 S.box('dm-yellow',(0,4.44,.1),(12.6,1.15,.09))
 S.text('HOLLYWOOD', (0,4.65,.17),.62,'dm-letter',back=True)
 S.text('CARS MUSEUM', (0,4.18,.17),.43,'dm-letter',back=True)
 # Restrained inferred roof plant and service openings on the rear wall.
 for x,z in [(-827,2158),(-808,2158),(-785,2162)]:
  F.box('dm-metal',(x,6,z),(1.7,.65,1.2))
  for k in range(6):F.box('dm-vent',(x,6.34,z-.45+k*.18),(1.45,.025,.06))
 return dict(key=KEY,name='5115 Dean Martin commercial frontage',center=[p.centroid.x,0,p.centroid.y],bounds=[lo-1,zn-2,hi+2,zs+1],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[dict(name='north-courtyard-frontage',points=[[-772,.08,2145.7],[-805,.08,2145.7],[-837,.08,2145.7]])],hotelSources=[])
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
