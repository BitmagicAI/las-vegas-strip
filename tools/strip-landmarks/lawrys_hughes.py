"""Original reference-led Lawry's exterior; fitted heights remain estimates.
The official tour and aerial are linked in lawrys-hughes.json. No borrowed pixels.
"""
from common import *
KEY='lawrys-hughes';ID='way/896655229';YAW=math.pi/2+.058

def build(B):
 F=Frame(B,1202.55,97.80,YAW,y=0)
 p=footprint(ID)
 # The mapped eastern projection is a roof over a driveway, not solid walls.
 main=Polygon([(1152.77,74.473),(1150.612,111.208),(1202.23,114.214),(1202.86,102.525),(1202.23,93.063),(1202.59,86.273),(1197.734,86.05),(1197.977,81.174),(1198.183,77.144)])
 B.property=KEY+'-exterior';B.source='retail/'+KEY;B.detail=0
 door=dict(p=F.p(0,.24,1.95),yaw=YAW,width=2.6,height=2.7,name='Public lounge entrance',venue=KEY)
 B.shell(main,.02,5.1,'lh-stucco',roof=False,openings=[door])
 # Wall base and paired horizontal Art Deco trim follow the actual footprint.
 for a,b in zip(list(main.exterior.coords),list(main.exterior.coords)[1:]):
  R=Frame(B,(a[0]+b[0])/2,(a[1]+b[1])/2,math.atan2(a[1]-b[1],b[0]-a[0]),y=0)
  L=math.dist(a,b)
  R.box('lh-red',(0,.43,0),(L,.82,.13))
  for y in [4.65,4.88]:R.box('lh-cream',(0,y,0),(L+.05,.11,.21))
 # Teal hipped perimeter wings: low roof planes, eaves and raised ridges.
 def hip(x,z,w,d,y,rise):
  lower=[(x-w/2,y,z-d/2),(x+w/2,y,z-d/2),(x+w/2,y,z+d/2),(x-w/2,y,z+d/2)]
  inset=min(w,d)*.35
  upper=[(x-w/2+inset,y+rise,z-d/2+inset),(x+w/2-inset,y+rise,z-d/2+inset),(x+w/2-inset,y+rise,z+d/2-inset),(x-w/2+inset,y+rise,z+d/2-inset)]
  for i in range(4):B.upface('lh-teal',[F.p(*lower[i]),F.p(*lower[(i+1)%4]),F.p(*upper[(i+1)%4]),F.p(*upper[i])])
  B.upface('lh-teal',[F.p(*q) for q in upper])
  for i in range(4):F.tube('lh-seam',lower[i],lower[(i+1)%4],.055,8)
 hip(16,-30,7,33,5.15,1.4);hip(-12,-30,7,33,5.15,1.4)
 hip(13,-5,8,10,5.15,1.1);hip(-11,-4.5,7,9,5.15,1.1)
 # Elongated curved-end central roof, observed in aerial; segmented original surface.
 center=-19;radius=7.5;half=7.5
 outline=[]
 for a in np.linspace(-math.pi/2,math.pi/2,25):outline.append((half+radius*math.cos(a),center+radius*math.sin(a)))
 for a in np.linspace(math.pi/2,3*math.pi/2,25):outline.append((-half+radius*math.cos(a),center+radius*math.sin(a)))
 roof=F.poly(outline);B.planar('lh-roof',main.difference(roof),5.1);B.shell(roof,5.12,6.15,'lh-metal',roof=False,solid=False);B.planar('lh-metal',roof,6.15)
 for a,b in zip(outline,outline[1:]+outline[:1]):F.tube('lh-cream',(a[0],6.18,a[1]),(b[0],6.18,b[1]),.095,8)
 for u in np.arange(-14,15,1):
  cut=roof.intersection(F.poly([(u-.025,-35),(u+.025,-35),(u+.025,-3),(u-.025,-3)]))
  if not cut.is_empty:B.planar('lh-seam',cut,6.165)
 # Cream wall returns and a narrower silver fascia, with an open central portal.
 for u in [-3.5,3.5]:F.box('lh-stucco',(u,2.15,.7),(2.0,4.25,1.4),True)
 for u in [-1.85,1.85]:
  F.box('lh-clear-glass',(u,1.65,1.95),(1.05,2.7,.035),True)
  for x in [u-.52,u+.52]:F.box('lh-metal',(x,1.65,2.0),(.065,2.8,.08))
 for i in range(24):
  a=-math.pi/2+i*math.pi/24;b=a+math.pi/24
  x1=2.65*math.sin(a);x2=2.65*math.sin(b);z1=1.45+.7*math.cos(a);z2=1.45+.7*math.cos(b)
  for yy in [3.15,3.30,3.45,3.60]:F.tube('lh-metal',(x1,yy,z1),(x2,yy,z2),.07,8)
 F.box('lh-metal',(0,2.99,2.0),(4.95,.12,.12))
 # Private apron joins retained grade without replacing municipal road surfaces.
 B.upface('lh-concrete',[F.p(-2.7,.24,1.9),F.p(2.7,.24,1.9),F.p(2.7,.16,6),F.p(-2.7,.16,6)],True)
 # Open porte-cochere: four cream ribbed piers, steel ribs, translucent-looking roof.
 for u in [-4.35,4.35]:
  for v in [3.1,15.2]:
   F.box('lh-cream',(u,2.5,v),(.72,5,.72),True)
   F.box('lh-cream',(u,.3,v),(1.05,.6,1.05),True)
   for dx in [-.24,0,.24]:
    for dz in [-.375,.375]:F.box('lh-rib',(u+dx,2.7,v+dz),(.045,4.1,.025))
   F.box('lh-cream',(u,4.9,v),(1.0,.22,1.0))
 for u in [-4.8,4.8]:F.box('lh-cream',(u,5.12,9.15),(.35,.36,13.4))
 for v in [2.45,15.85]:F.box('lh-cream',(0,5.12,v),(9.95,.36,.35))
 # Hip apex ridge, fitted to mapped canopy footprint; drive clearance >=4.9m.
 corners=[(-4.8,5.3,2.45),(4.8,5.3,2.45),(4.8,5.3,15.85),(-4.8,5.3,15.85)]
 ridge=[(0,7.2,6.4),(0,7.2,11.9)]
 facets=[[corners[0],corners[1],ridge[0]],[corners[1],corners[2],ridge[1],ridge[0]],[corners[2],corners[3],ridge[1]],[corners[3],corners[0],ridge[0],ridge[1]]]
 edges=set()
 for face in facets:
  B.upface('lh-canopy',[F.p(*q) for q in face])
  for a,b in zip(face,face[1:]+face[:1]):
   edge=tuple(sorted((a,b)))
   if edge not in edges:F.tube('lh-frame',a,b,.045,8);edges.add(edge)
 # Roof grid follows planes, including both slopes, rather than a flat overlay.
 for side in [-1,1]:
  for v in np.linspace(2.8,15.5,19):
   rz=max(6.4,min(11.9,v));F.tube('lh-frame',(side*4.8,5.32,float(v)),(0,7.22,float(rz)),.025,8)
  for t in [.25,.5,.75]:
   F.tube('lh-frame',(side*4.8*(1-t),5.32+1.9*t,2.45+3.95*t),(side*4.8*(1-t),5.32+1.9*t,15.85-3.95*t),.025,8)
 # South entry sign pier and lawn-side planting pots; no municipal surfaces altered.
 F.box('lh-red',(-5.8,2.5,1.7),(2.0,5,.7),True)
 F.box('lh-cream',(-5.8,5.08,1.7),(2.18,.16,.85))
 F.text("Lawry's",(-5.8,3.35,2.09),.48,'lh-gold',back=True)
 F.text('THE PRIME RIB',(-5.8,2.75,2.09),.19,'lh-cream',back=True)
 for u in [-6.4,6.4]:
  F.lathe('lh-pot',u,4,[(.04,.4),(.12,.45),(.65,.62),(.8,.65),(.86,.67)],20)
  for dx,dz,h in [(-.2,0,1.15),(.15,.12,1.4),(0,-.14,1.6)]:
   F.tube('lh-wood',(u+dx,.8,4+dz),(u+dx,h+1,4+dz),.035,8)
   for a in np.linspace(0,math.tau,9,endpoint=False):
    tip=(u+dx+.65*math.cos(a),h+.6,4+dz+.65*math.sin(a));mid=(u+dx+.35*math.cos(a+.15),h+1.05,4+dz+.35*math.sin(a+.15))
    B.face('lh-leaf',[F.p(u+dx,h+1,4+dz),F.p(*mid),F.p(*tip)])
 # Service roof equipment on the west flat roof, with visible louvers.
 for u,v in [(-5,-39),(5,-39),(0,-45)]:
  F.box('lh-equipment',(u,5.65,v),(2.6,1.1,2.1))
  for k in range(7):F.box('lh-frame',(u,5.25+k*.11,v+1.06),(2.3,.035,.03))
  F.lathe('lh-frame',u,v,[(6.22,.65),(6.27,.65)],24)
 from lawrys_public import build_public
 public=build_public(B,F,door)
 return dict(key=KEY,name="Lawry's The Prime Rib",center=[p.centroid.x,0,p.centroid.y],bounds=list(p.bounds),structural=True,hotelSources=[],**public)

if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
