"""Original exterior/patio from October2026 northfront, April2022 envelope and aerial.
Heights, canopy profile and support dimensions are fitted; interior excluded.
"""
from common import *
from shapely.geometry.polygon import orient
KEY='chick-fil-a-sahara';IDS=['way/587100024']
def build(B):
 B.property=KEY+'-exterior';B.source='retail/'+KEY;B.detail=0
 p=orient(footprint(IDS[0]),sign=1);F=Frame(B,33.85,-3204.59,-.01316,y=0)
 B.shell(p,0,5.5,'cs-plaster',roof=False);B.planar('cs-membrane',p,5.5)
 # Tall northwestern pier and charcoal west/service faces, not a generic chain prototype.
 tower=box(17.7,-3204.9,24.1,-3200.1).intersection(p.buffer(.06));B.shell(tower,0,7.2,'cs-tan',roof=False);B.planar('cs-membrane',tower,7.2)
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  w=math.dist(a,b);R=Frame(B,(a[0]+b[0])/2,(a[1]+b[1])/2,math.atan2(a[1]-b[1],b[0]-a[0]),y=0)
  R.box('cs-coping',(0,5.55,0),(w+.04,.12,.3))
  if R.x<24 and R.z>-3200:B.upface('cs-gray',[R.p(-w/2,.1,-.04),R.p(w/2,.1,-.04),R.p(w/2,5.3,-.04),R.p(-w/2,5.3,-.04)])
 # Large north sloping roof overhang; double surface gives a visible ribbed soffit.
 for yoff,mat in [(0,'cs-dark'),(-.13,'cs-soffit')]:
  pts=[F.p(-9,7.4+yoff,-.6),F.p(16.3,7.4+yoff,-.6),F.p(16.3,5.65+yoff,5.2),F.p(-9,5.65+yoff,5.2)]
  if yoff<0:B.face(mat,list(reversed(pts)))
  else:B.upface(mat,pts)
 for u in np.arange(-9,16.4,.22):F.tube('cs-rib',(float(u),7.25,-.6),(float(u),5.5,5.2),.012,6)
 F.box('cs-dark',(3.65,7.38,-.6),(25.6,.18,.16))
 for u in [-9,16]:F.box('cs-dark',(u,3.65,-.1),(.28,7.3,.3),True)
 # Opaque exterior glazing; public interiors await location-specific evidence.
 def window(R,u,y,w,h):
  R.box('cs-glass',(u,y,-.09),(w,h,.055))
  for x in [-w/2,0,w/2]:R.box('cs-dark',(u+x,y,-.14),(.055,h+.1,.06))
  for yy in [y-h/2,y+h/2]:R.box('cs-dark',(u,yy,-.14),(w+.1,.06,.06))
 def awning(R,u,w,y=4.55):
  B.upface('cs-dark',[R.p(u-w/2,y,0),R.p(u+w/2,y,0),R.p(u+w/2,y-.65,-1.15),R.p(u-w/2,y-.65,-1.15)])
  R.box('cs-dark',(u,y-.68,-1.15),(w,.12,.08))
  for dx in [-w/2+.15,w/2-.15]:R.tube('cs-dark',(u+dx,y-.8,0),(u+dx,y-.65,-1.1),.03,8)
 for u in [-1.5,3.1,7.7,12.3]:window(F,u,2.35,4.05,2.85);awning(F,u,4.35)
 window(F,-7,1.55,1.7,2.8);awning(F,-7,2.4,3.7)
 for du in [-.14,.14]:F.tube('cs-alloy',(-7+du,1.05,-.2),(-7+du,1.55,-.2),.025,8)
 # Panel joints limited to solid tan pier.
 T=Frame(B,20.9,-3204.96,-.01316,y=0)
 for yy in [2.7,4.5,6.2]:T.box('cs-joint',(0,yy,0),(6.2,.018,.025))
 T.text('Chick-fil-A',(0,5.05,-.16),.67,'cs-red')
 W=Frame(B,17.6,-3202.3,math.pi/2,y=0);window(W,0,1.9,2.2,1.45);awning(W,0,2.5,3.2)
 W.text('Chick-fil-A',(0,5.0,-.22),.48,'cs-red')
 F.box('cs-red',(-4.4,2.3,-.13),(1.0,1.0,.1));F.text('MOBILE',(-4.4,2.4,-.2),.17,'cs-white');F.text('PICKUP',(-4.4,2.1,-.2),.17,'cs-white')
 # East service window, fitted to queue-side wall from aerial.
 E=Frame(B,50.03,-3198.5,-math.pi/2,y=0);window(E,0,1.8,2,1.5);awning(E,0,2.4,3.25)
 for x,z in [(31,-3198),(40,-3195),(43,-3200)]:
  B.box('cs-equipment',(x,5.9,z),(2.8,.8,1.6))
  for dx in [-.65,.65]:
   B.lathe('cs-dark',(x+dx,z),[(6.31,.42),(6.34,.42)],16)
   for zz in np.arange(-.3,.31,.1):B.box('cs-alloy',(x+dx,6.36,z+float(zz)),(.65,.02,.02))
 # North patio slab/ramp and separated rail openings.
 F.box('cs-paving',(2.8,.1,-3.5),(29,.2,6.6),True)
 B.upface('cs-paving',[F.p(-8,0,-8),F.p(-6,0,-8),F.p(-6,.2,-6.7),F.p(-8,.2,-6.7)],True)
 for lo,hi in [(-11.5,-8.2),(-5.8,17.2)]:
  F.tube('cs-dark',(lo,1.25,-6.7),(hi,1.25,-6.7),.03,8)
  for u in np.arange(lo,hi,.18):F.tube('cs-dark',(float(u),.2,-6.7),(float(u),1.25,-6.7),.017,6)
 # Original metal furniture and red octagonal umbrellas from frontage photos.
 for u in [-2.5,2.5,7.5,12.5]:
  v=-3.0;F.lathe('cs-dark',u,v,[(.21,.35),(.25,.35),(.28,.06),(.95,.06)],12)
  F.box('cs-dark',(u,.99,v),(1.3,.07,.8),True)
  for xx in np.arange(-.58,.6,.08):F.box('cs-rib',(u+float(xx),1.031,v),(.025,.008,.74))
  for dv in [-.95,.95]:
   F.box('cs-dark',(u,.65,v+dv),(.5,.08,.5),True)
   for dx in [-.21,.21]:
    F.tube('cs-dark',(u+dx,.2,v+dv-.2),(u+dx,.64,v+dv-.2),.025,8);F.tube('cs-dark',(u+dx,.2,v+dv+.2),(u+dx,1.25,v+dv+.2),.025,8)
   for yy in [.85,1.02,1.2]:F.box('cs-dark',(u,yy,v+dv+.2),(.48,.035,.04))
  F.tube('cs-alloy',(u,.2,v),(u,3.65,v),.025,10)
  for j in range(8):
   a=j*math.tau/8;b=(j+1)*math.tau/8
   pts=[F.p(u,3.5,v),F.p(u+1.75*math.cos(a),3.1,v+1.75*math.sin(a)),F.p(u+1.75*math.cos(b),3.1,v+1.75*math.sin(b))]
   B.upface('cs-red',pts);B.face('cs-red',list(reversed(pts)))
   F.tube('cs-alloy',(u,3.47,v),(u+1.75*math.cos(a),3.07,v+1.75*math.sin(a)),.012,6)
 # West curved tensile canopy over drive lane. Profile and supports are estimates.
 center=(20,-3195);ang=np.linspace(math.pi*.63,math.pi*1.15,17)
 def cp(t,r,y):return(center[0]+math.cos(t)*r,y,center[1]+math.sin(t)*r)
 # World Z south: this arc sits west/northwest alongside the mapped wall.
 for i,(a,b) in enumerate(zip(ang,ang[1:])):
  y0=4.2+.4*math.sin(i*math.pi/4);y1=4.2+.4*math.sin((i+1)*math.pi/4)
  pts=[cp(a,7.0,y0),cp(a,13.8,4.7),cp(b,13.8,4.7),cp(b,7.0,y1)]
  B.upface('cs-fabric',pts);B.face('cs-fabric',list(reversed(pts)))
 for i in range(0,17,4):
  a=ang[i];B.tube('cs-dark',cp(a,13.8,0),cp(a,13.8,4.7),.09,12);B.tube('cs-dark',cp(a,7,4.2),cp(a,13.8,4.7),.06,8)
 # Local planting strips; mapped roads/colliders stay untouched.
 Q=Frame(B,0,0,0,y=0)
 for x,z in [(12,-3211),(16,-3211),(21,-3213),(27,-3213),(34,-3213),(42,-3213),(50,-3211)]:
  Q.lathe('cs-gravel',x,z,[(.02,.85),(.04,.85)],12)
  for j in range(8):
   a=j*math.tau/8;dx=.48*math.cos(a);dz=.48*math.sin(a)
   B.upface('cs-leaf',[(x,.04,z),(x+dx,1.1,z+dz),(x+dx+.07,.12,z+dz)])
   Q.tube('cs-stem',(x+dx*.2,.1,z+dz*.2),(x+dx*.45,1.25,z+dz*.45),.014,6)
   Q.lathe('cs-flower',x+dx*.45,z+dz*.45,[(1.1,.04),(1.3,.025),(1.4,0)],6)
 routes=[dict(name='Patio entrance and frontage',points=[F.p(-7,0,-9),F.p(-7,0,-8),F.p(-7,.2,-6.4),F.p(-7,.2,-4.9),F.p(0,.2,-4.9),F.p(8,.2,-4.9),F.p(15,.2,-4.9)]),dict(name='West drive canopy clearance',points=[[7,0,-3204],[7,0,-3198],[8,0,-3192],[12,0,-3187]])]
 return dict(key=KEY,name='Chick-fil-A Sahara at I-15',center=[35,0,-3196],bounds=[3,-3215,52,-3180],structural=True,hotelSources=[],exteriorOnly=True,portals=[],zones=[],lights=[],routes=routes)
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces'])for g in B.groups.values()),'triangles')
