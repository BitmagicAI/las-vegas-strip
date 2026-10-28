"""Original surveyed shell and reference-supported frontage; public interior closed."""
from common import *
KEY='chick-fil-a-flamingo';ID='way/1264703200'
def build(B):
 p=footprint(ID);B.property=KEY+'-exterior';B.source='podium/'+KEY;B.detail=0
 B.shell(p,.08,6.25,'cf-stucco',roof=False);B.planar('cf-roof',p,6.06);B.planar('cf-foundation',p,.14,True)
 F=Frame(B,-1633.8,117.28,0,y=0)
 # Parapet cap follows the mapped shell; upper fascia remains continuous cream stucco.
 for poly in parts(p):
  for a,b in zip(list(poly.exterior.coords),list(poly.exterior.coords)[1:]):
   L=math.dist(a,b);yaw=-math.atan2(b[1]-a[1],b[0]-a[0]);cx=(a[0]+b[0])/2;cz=(a[1]+b[1])/2
   B.box('cf-cap',(cx,6.27,cz),(L,.18,.27),False,yaw)
 # Brick faces with recessed mortar. Original deterministic color variation.
 rng=random.Random(322)
 def bricks(G,a,b,lo,hi,z,holes=()):
  region=box(a,lo,b,hi)
  for h in holes:region=region.difference(box(*h))
  for row,y in enumerate(np.arange(lo,hi,.09)):
   for x in np.arange(a-.26,b,.26):
    x=float(x)+(row%2)*.13;q=box(x+.006,float(y)+.006,x+.254,min(float(y)+.084,hi)).intersection(region)
    for poly in parts(q):
     for t in triangles(poly):B.face('cf-brick-'+str(rng.randrange(5)),[G.p(u,v,z) for u,v in list(t.exterior.coords)[:-1]])
 def window(G,u,z,w,h=2.55,base=.55):
  G.box('cf-glass',(u,base+h/2,z),(w,h,.075))
  for x in np.linspace(u-w/2,u+w/2,max(2,round(w/1.0)+1)):G.box('cf-frame',(float(x),base+h/2,z+.07),(.065,h+.12,.12))
  for y in [base,base+h*.68,base+h]:G.box('cf-frame',(u,y,z+.07),(w+.1,.075,.12))
  G.box('cf-sill',(u,base-.1,z+.06),(w+.18,.16,.25))
 def canopy(G,u,z,w,h=3.23):
  G.box('cf-cap',(u,h,z+.48),(w,.14,1.15))
  for x in [u-w*.4,u+w*.4]:G.tube('cf-frame',(x,h+.1,z+.98),(x,h+.7,z+.03),.018,8)
 # South end: brick panels framing a tall cream entrance bay.
 for a,b in [(-5.9,-1.55),(1.55,5.85)]:
  F.box('cf-mortar',((a+b)/2,2.45,.045),(b-a,4.55,.12))
  holes=[(2.2,.55,4.75,3.1)] if a>0 else []
  bricks(F,a,b,.23,4.7,.12,holes)
 window(F,3.475,.19,2.55);canopy(F,3.475,.2,2.85)
 window(F,0,.17,2.25,2.7,.18);canopy(F,0,.17,2.85,3.05)
 for u in [-.5,.5]:F.tube('cf-metal',(u,1.05,.34),(u,1.55,.34),.018,8)
 F.text('3841',(0,2.97,.30),.20,'cf-letter',back=True)
 F.box('cf-sign',(0,4.55,.16),(1.48,1.62,.18))
 # Original wordmark treatment, no copied brand pixels.
 F.text('Chick-fil-A',(0,4.55,.28),.19,'cf-letter',back=True)
 for u in [-1.1,1.1]:
  F.box('cf-frame',(u,3.88,.15),(.09,.12,.16));F.tube('cf-frame',(u,3.85,.17),(u,3.72,.43),.025,8)
 # West-side covered dining glazing; frame normal points west.
 W=Frame(B,-1641.22,110.3,-math.pi/2,y=0)
 holes=[(-12.5,.6,-8.7,3.13),(-7.8,.6,-4.0,3.13),(-3.1,.6,.7,3.13),(1.6,.6,5.4,3.13)]
 W.box('cf-mortar',(-3.55,2.45,-.6),(20.2,4.55,1.44),True)
 bricks(W,-13.65,6.55,.23,4.7,.14,holes)
 for a,lo,b,hi in holes:window(W,(a+b)/2,.22,b-a,hi-lo,lo)
 W.box('cf-cap',(-3.55,3.48,.85),(20.3,.16,1.8))
 for u in [-13.5,-8.8,-4.1,.6,6.4]:W.box('cf-frame',(u,1.81,1.48),(.10,3.34,.10),True)
 # North/east service treatment is inferred; keep the route/drive-through footprint free.
 E=Frame(B,-1627.75,101.3,math.pi/2,y=0)
 E.box('cf-mortar',(0,1.0,.05),(29,.9,.12));bricks(E,-14.4,14.4,.23,1.4,.12)
 window(E,-5.2,.14,1.2,1.15,1.2);canopy(E,-5.2,.14,1.6,2.7)
 E.box('cf-service',(7.4,1.2,.17),(1.05,2.15,.1),True);E.box('cf-frame',(7.1,1.15,.25),(.05,.18,.04))
 F.box('cf-paving',(0,.07,1.12),(11.7,.14,2.25),True)
 # Planters are within the immediate entrance apron, not over existing streets.
 for u in [-4.8,4.9]:
  F.box('cf-planter',(u,.36,.93),(.65,.6,.65),True)
  for k in range(7):
   x=u+rng.uniform(-.2,.2);z=.93+rng.uniform(-.2,.2)
   F.lathe('cf-shrub',x,z,[(.62,0),(.78,.18),(.98,.12),(1.06,0)],7)
 for u,v in [(-2,-8),(2,-17),(-2,-25)]:
  F.box('cf-metal',(u,6.46,v),(1.8,.62,1.4));F.box('cf-cap',(u,6.82,v),(1.9,.09,1.5))
  for k in range(8):F.box('cf-frame',(u-.75+k*.21,6.88,v),(.035,.015,1.2))
 route=[F.p(u,.14,v) for u,v in [(0,2),(0,1.2),(0,.75)]]
 return dict(key=KEY,name='Chick-fil-A Flamingo',center=[p.centroid.x,0,p.centroid.y],bounds=[p.bounds[0]-2,p.bounds[1]-1,p.bounds[2]+1,p.bounds[3]+3],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],hotelSources=[],routes=[dict(name='Front entrance approach',points=route)])
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
