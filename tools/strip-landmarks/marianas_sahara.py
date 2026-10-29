"""Original Mariana's Sahara exterior. Jan2025 public frontage reference.
Dimensions beyond mapped outline estimated; private/public interior remains closed.
"""
from common import *
KEY='marianas-sahara';ID='way/764088498';YAW=math.pi+.037

def build(B):
 p=footprint(ID);F=Frame(B,-1512,-3073,YAW,y=0)
 B.property=KEY+'-exterior';B.source='podium/'+KEY;B.detail=0
 # Remove projecting arcade volumes from the solid shell; their openings are real.
 core=p.difference(F.poly([(-40,.05),(40,.05),(40,8),(-40,8)]))
 B.shell(core,.10,6.2,'ms-stucco',roof=False);B.planar('ms-roof',p,6.12)
 def trim(u,w,v,h):
  for yy,dd,hh in [(h-.30,.38,.14),(h-.16,.52,.12),(h,.73,.18)]:F.box('ms-brown',(u,yy,v+.12),(w+.20,hh,dd))
 # Deep arched structures: extruded wall with actual holes, not painted black arches.
 def arcade(a,b,front):
  centres=[a+(b-a)*.25,a+(b-a)*.75];r=1.43;spring=2.65;h=6.35
  region=box(a,0,b,h)
  for u in centres:
   pts=[(u-r,0),(u+r,0),(u+r,spring)]+[(u+r*math.cos(t),spring+r*math.sin(t)) for t in np.linspace(0,math.pi,33)]+[(u-r,0)]
   region=region.difference(Polygon(pts))
  for q in parts(region):
   for tr in triangles(q):
    xy=list(tr.exterior.coords)[:-1]
    for v in [.15,front]:B.face('ms-stucco',[F.p(x,y,v) for x,y in xy],True)
   for ring in [q.exterior,*q.interiors]:
    for (x,y),(xx,yy) in zip(list(ring.coords),list(ring.coords)[1:]):B.face('ms-stucco',[F.p(x,y,.15),F.p(xx,yy,.15),F.p(xx,yy,front),F.p(x,y,front)],True)
  trim((a+b)/2,b-a,front,h)
  for u in [a+.5,(a+b)/2,b-.5]:
   for y,dep in [(2.55,.28),(2.66,.40),(2.76,.31)]:F.box('ms-brown',(u,y,front+.1),(1.03,.08,dep))
   # Horizontal rustication below the spring line.
   for y in [.48,.98,1.48,1.98]:F.box('ms-joint',(u,y,front+.012),(.95,.014,.014))
   F.box('ms-metal',(u,2.28,front+.19),(.16,.22,.18));F.box('ms-lamp',(u,2.25,front+.29),(.11,.14,.08))
  for u in centres:
   # Actual tapered keystone above each crown.
   q=[(u-.18,4.03),(u+.18,4.03),(u+.26,4.61),(u-.26,4.61)]
   B.face('ms-brown',[F.p(x,y,front+.07) for x,y in q])
   for a0,a1 in zip(np.linspace(0,math.pi,13)[:-1],np.linspace(0,math.pi,13)[1:]):
    x=u+1.65*math.cos(a0);y=spring+1.65*math.sin(a0)
    F.tube('ms-joint',(u+r*math.cos(a0),spring+r*math.sin(a0),front+.012),(x,y,front+.012),.008,5)
   F.box('ms-frame',(u,1.38,.10),(2.62,2.65,.12));F.box('ms-glass',(u,1.38,.18),(2.46,2.49,.025))
   F.box('ms-frame',(u,1.38,.22),(.055,2.5,.035))
  return centres
 arcade(-12.55,-2.7,3.65);arcade(3.2,13.2,3.65)
 for u,w,v,h,t in [(-7.62,9.85,3.65,6.35,'CARNICERIA'),(8.2,10,3.65,6.35,'PANADERIA'),(-20.3,14.9,0,5.8,'FRUTERIA'),(21,15.5,0,5.8,'CARNES')]:
  if v==0:trim(u,w,v,h)
  F.box('ms-brown',(u,h-.85,v+.14),(w-.65,.9,.12));F.box('ms-cream',(u,h-.85,v+.22),(w-.83,.72,.04))
  F.text(t,(u,h-1.07,v+.26),.55,'ms-green',back=True)
 # Center recessed entrance and low tiled canopy between the projecting wings.
 trim(.25,5.9,.0,6.15)
 F.box('ms-frame',(.25,1.58,.15),(3.7,2.85,.12),True)
 for u in [-.63,1.13]:
  F.box('ms-glass',(u,1.60,.24),(1.68,2.66,.03))
  F.tube('ms-metal',(u-.45,1.0,.30),(u-.45,1.8,.30),.025,10)
 F.text('3631',(.25,3.15,.18),.30,'ms-brown',back=True)
 F.box('ms-stucco',(.25,3.75,1.4),(5.9,.7,2.8),True)
 for row in range(4):
  v=.18+row*.67;y=4.85-row*.16
  for u in np.arange(-2.6,3.1,.26):
   # Curved individual clay tile barrels aligned down the slope.
   F.tube('ms-tile-'+str((int(u*10)+row)%3),(float(u),y,v),(float(u),y-.18,v+.73),.135,10)
 F.text("MARIANA'S",(-3.2,6.48,.24),.63,'ms-green',back=True)
 F.text('SUPERMARKETS',(3.2,6.48,.24),.60,'ms-red',back=True)
 F.box('ms-stucco',(.2,6.65,-.10),(30,1.1,.3),True);trim(.2,30,-.1,7.3)
 # Visible end walls, recessed commercial glazing and restrained generic service detail.
 for u in [-26,-22,-18,-15,15.5,19,22.5,26]:
  F.box('ms-frame',(u,1.5,.16),(2.8,2.7,.12));F.box('ms-glass',(u,1.5,.24),(2.65,2.55,.025))
 for u in [-1.4,.25,1.9]:F.lathe('ms-yellow',u,2.6,[(.12,.065),(1.26,.065),(1.32,.04)],12)
 for u in [-2.2,2.7]:
  F.lathe('ms-metal',u,1.25,[(.12,.26),(.85,.28),(.95,.26)],16)
 # Local arcade apron only; existing parking and roads are preserved.
 F.box('ms-paving',(.25,.06,1.85),(29,.12,3.7),True)
 for u in np.arange(-13,15,1.5):F.box('ms-joint',(float(u),.124,1.85),(.012,.004,3.6))
 for a,b in zip(list(p.exterior.coords)[:-1],list(p.exterior.coords)[1:]):B.tube('ms-brown',(a[0],6.24,a[1]),(b[0],6.24,b[1]),.065,8)
 for u,v in [(-21,-12),(-12,-18),(0,-12),(11,-20),(20,-11),(-8,-35),(8,-36)]:
  F.box('ms-metal',(u,6.7,v),(2.8,.9,2.0))
  for z in np.linspace(v-.8,v+.8,12):F.box('ms-frame',(u,7.16,float(z)),(2.5,.025,.035))
 return dict(key=KEY,name="Mariana's Sahara",center=[p.centroid.x,0,p.centroid.y],bounds=[p.bounds[0]-1,p.bounds[1]-1,p.bounds[2]+1,p.bounds[3]+1],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],hotelSources=[],routes=[dict(name='Front approach to recessed entrance',points=[F.p(u,.13,v) for u,v in [(-10,4.9),(1.1,4.9),(1.1,3.4),(1.1,.8)]])])
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
