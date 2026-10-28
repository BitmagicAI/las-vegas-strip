"""Original 5155 Dean Martin exterior. February2025 frontage reference.
Mapped footprint is authoritative for plan; heights, bay divisions and hidden
service details are estimates. No operating range or interior layout is claimed.
"""
from common import *
KEY='shooting-center'
def build(B):
 B.property=KEY+'-exterior';B.source='podium/'+KEY;B.detail=0
 p=footprint('way/1126368790');lo,zn,hi,zs=p.bounds
 F=Frame(B,0,0,y=0)
 B.shell(p,.02,5.1,'sc-masonry',roof=False)
 B.planar('sc-roof-paint',p,5.1)
 coords=list(p.exterior.coords)
 for a,b in zip(coords,coords[1:]):
  L=math.dist(a,b);G=Frame(B,*a,math.atan2(-(b[1]-a[1]),b[0]-a[0]),y=0)
  out=1 if not p.covers(Point(G.p(L/2,0,.15)[::2])) else -1
  G.box('sc-cap-concrete',(L/2,5.12,out*.04),(L+.04,.18,.22))
  G.box('sc-concrete',(L/2,.22,out*.04),(L,.42,.16))
  # Coarse split-face block courses, subtle original joints in metre units.
  for row,y in enumerate(np.arange(.52,5,.24)):
   G.box('sc-joint',(L/2,float(y),out*.012),(L,.009,.025))
   for u in np.arange(.2+(row%2)*.2,L,.4):
    B.face('sc-joint',[G.p(float(u)+dx,float(y)+dy,out*.026) for dx,dy in [(-.004,.005),(.004,.005),(.004,.235),(-.004,.235)]])
  for u in np.arange(.2,L,6):G.box('sc-masonry',(float(u),2.57,out*.065),(.22,4.7,.14))
 # East road frontage: raised sign parapet and tiled sloping canopy.
 z0,z1=2215.759,2248.899;mid=(z0+z1)/2;W=z1-z0
 S=Frame(B,hi,mid,math.pi/2,y=0)
 S.box('sc-masonry',(0,5.55,-.10),(W,1.1,.25))
 S.box('sc-cap-concrete',(0,6.16,-.10),(W+.12,.18,.38))
 # Raised tiled mansard visible in the February 2025 frontage. Each tile
 # has a shallow curved section; openings sit above the continuous lower eave.
 for u in np.arange(-W/2,W/2,.24):
  for v in np.arange(0,2.4,.34):
   x0=float(u);x1=min(W/2,x0+.235);v0=float(v);v1=min(2.4,v0+.33)
   h=lambda z:5.22-.55*z
   for k in range(3):
    a=k/3;b=(k+1)/3
    xa=x0+(x1-x0)*a;xb=x0+(x1-x0)*b
    ha=.035*math.sin(a*math.pi);hb=.035*math.sin(b*math.pi)
    B.upface('sc-roof-tile',[S.p(xa,h(v0)+ha,v0),S.p(xb,h(v0)+hb,v0),S.p(xb,h(v1)+hb,v1),S.p(xa,h(v1)+ha,v1)])
 for u in [-12,-6,0,6,12]:
  S.box('sc-window-frame-paint',(u,4.81,1.54),(2.28,.96,.15))
  S.box('sc-glass',(u,4.81,1.63),(2.12,.80,.04))
  S.box('sc-window-frame-paint',(u,4.81,1.66),(.045,.80,.04))
 S.box('sc-trim-paint',(0,3.88,2.4),(W+.08,.18,.20))
 for u in [-W/2+.2,-9.5,0,9.5,W/2-.2]:
  S.box('sc-post-paint',(u,1.9,2.25),(.12,3.8,.12),True)
 # Inferred tenant bay widths. Dark glazing has an opaque backing in this exterior pass.
 for u in [-12,-4,4,12]:
  S.box('sc-window-frame-paint',(u,2.0,.05),(4.8,1.45,.16))
  S.box('sc-glass',(u,2.0,.15),(4.64,1.29,.035))
  for t in [-1.5,0,1.5]:S.box('sc-window-frame-paint',(u+t,2.0,.18),(.045,1.32,.05))
  S.box('sc-concrete',(u,1.22,.16),(4.96,.12,.30))
 for u in [-8,8]:
  S.box('sc-window-frame-paint',(u,1.2,.08),(1.65,2.4,.16))
  S.box('sc-glass',(u,1.2,.18),(1.49,2.24,.025))
  S.box('sc-window-frame-paint',(u,1.2,.22),(.045,2.24,.04))
  for dx in [-.15,.15]:S.box('sc-metal',(u+dx,1.1,.25),(.03,.35,.04))
 S.box('sc-sign-paint',(-2.8,5.64,.08),(4.5,.85,.12))
 S.text('Las Vegas',(-2.8,5.83,.17),.24,'sc-letter',back=True)
 S.text('SHOOTING CENTER',(-2.8,5.48,.17),.32,'sc-letter',back=True)
 S.box('sc-sign-paint',(2.2,5.64,.08),(5,.85,.12))
 S.text('J&S DIESEL',(2.2,5.64,.17),.54,'sc-letter',back=True)
 S.text('5155',(15,5.68,.16),.60,'sc-sign-paint',back=True)
 # Continuous entry apron; keep public road geometry untouched.
 S.box('sc-concrete',(0,.04,1.34),(W+.4,.08,2.7),True)
 # Roof mechanical blocks are restrained inferred service detail.
 for x,z in [(-805,2210),(-803,2227),(-786,2238),(-796,2261)]:
  F.box('sc-metal',(x,5.46,z),(1.6,.66,1.2))
  for j in range(6):F.box('sc-vent',(x,5.81,z-.45+j*.18),(1.4,.035,.055))
 return dict(key=KEY,name='5155 Dean Martin — Shooting Center',center=[p.centroid.x,0,p.centroid.y],bounds=[lo-1,zn-1,hi+4,zs+1],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[dict(name='covered-frontage',points=[[-770.4,.08,2247],[-770.4,.08,2217]]),dict(name='south-door-approach',points=[[-767,.08,2240.329],[-770.5,.08,2240.329]]),dict(name='north-door-approach',points=[[-767,.08,2224.329],[-770.5,.08,2224.329]])],hotelSources=[])
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
