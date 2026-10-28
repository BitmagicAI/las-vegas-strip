"""Original 3716 Paradise shop/canopy; Jan2026 exterior, Feb2025 counter refs.
Footprints mapped; elevations, fixture positions and concealed layout are estimates.
"""
from common import *
KEY='seven-eleven-paradise';IDS=['way/390004000','way/1423935197']
def build(B):
 p,c=map(footprint,IDS);F=Frame(B,1659.736,-636.842,-math.pi/2,y=0)
 B.property=KEY+'-exterior';B.source='retail/'+KEY;B.detail=0
 door=dict(p=F.p(3,.15,0),yaw=-math.pi/2,width=1.8,height=2.45,name='Shop entrance',venue=KEY)
 B.upface('se-concrete',[F.p(2.12,.168,-.8),F.p(3.88,.168,-.8),F.p(3.88,.34,.8),F.p(2.12,.34,.8)],True)
 windows=[]
 for u in [-7.2,-5.4,-3.6,-1.8,0,1.47,4.8,6.6,8.0]:
  w=1.1 if u==1.47 else 1.65 if u<7.8 else 1.05
  for base,top in [(.35,3.65),(3.775,4.625)]:
   windows.append(dict(p=F.p(u,base+.15,0),yaw=-math.pi/2,width=w,height=top-base-.25))
 B.shell(p,0,5.35,'se-stucco',openings=[door,*windows],roof=False);B.planar('se-membrane-paint',p,5.35)
 # Shop's high dark metal storefront behind the west canopy; transom above main lights.
 for u in [-7.2,-5.4,-3.6,-1.8,0,1.47,4.8,6.6,8.0]:
  width=1.1 if u==1.47 else 1.65 if u<7.8 else 1.05
  F.box('se-glass',(u,2.0,.025),(width,3.3,.04),True)
  F.box('se-glass',(u,4.2,.025),(width,.85,.04),True)
  F.box('se-steel-paint',(u-width/2,2.4,.07),(.06,4.6,.1))
 for y in [3.65,4.7]:F.box('se-steel-paint',(0,y,.07),(17.9,.08,.1))
 for lo,hi in [(-8.95,2.1),(3.9,8.95)]:F.box('se-steel-paint',((lo+hi)/2,.35,.07),(hi-lo,.08,.1))
 F.text('3716',(-5,4.0,.1),.6,'se-letter',back=True)
 # Canopy remains an open structure: fascia/soffit only, no walls through pump lanes.
 B.shell(c,4.95,6.0,'se-white',roof=False,solid=False);B.planar('se-membrane-paint',c,6.0)
 for tri in triangles(c):
  pts=[(x,4.95,z) for x,z in list(tri.exterior.coords)[:-1]];a=np.array(pts);B.face('se-soffit',pts if np.cross(a[1]-a[0],a[2]-a[0])[1]<0 else list(reversed(pts)))
 for a,b in zip(list(c.exterior.coords),list(c.exterior.coords)[1:]):
  if LineString([a,b]).distance(p.boundary)<.02 and p.buffer(.03).covers(LineString([a,b])):continue
  dx,dz=b[0]-a[0],b[1]-a[1];w=math.hypot(dx,dz);R=Frame(B,(a[0]+b[0])/2,(a[1]+b[1])/2,math.atan2(-dz,dx),y=0)
  # Jan2026 photograph shows rounded segmented coping above the fascia.
  # Radius/seam spacing are estimates; retain the concealed flat membrane.
  profile=[(-.38*math.cos(t),6.015+.30*math.sin(t)) for t in np.linspace(0,math.pi,13)]
  for (v0,y0),(v1,y1) in zip(profile,profile[1:]):
   B.upface('se-white',[R.p(-w/2,y0,v0),R.p(w/2,y0,v0),R.p(w/2,y1,v1),R.p(-w/2,y1,v1)])
  for u in np.linspace(-w/2+.06,w/2-.06,max(2,math.ceil(w/1.5)+1)):
   R.path('se-metal-paint',[(float(u),y+.012,v) for v,y in profile],.012,6)
  # Thin outward belts wrap each edge; no duplicated coplanar panels.
  for y,h,m in [(5.79,.16,'se-orange'),(5.47,.34,'se-green'),(5.12,.17,'se-red')]:R.box(m,(0,y,0),(w,h,.055))
 # Slender black columns, beams and lit soffit panels: fixed materials, no runtime lights.
 columns=[(1646,-631),(1646,-624),(1657,-617),(1664,-613),(1666,-625)]
 for x,z in columns:B.box('se-steel-paint',(x,2.48,z),(.3,4.96,.3),True);B.box('se-steel-paint',(x,.1,z),(.48,.2,.48),True)
 for z,x0,x1 in [(-631,1646,1659.7),(-624,1646,1668.5),(-617,1657,1668.5)]:B.box('se-steel-paint',((x0+x1)/2,4.83,z),(x1-x0,.26,.17))
 for x,z in [(1650,-630),(1650,-623),(1661,-618),(1664,-625)]:B.box('se-light',(x,4.91,z),(.65,.045,1.15))
 # Original branding shapes, all geometry and lettering authored here.
 for x,z,yaw in [(1643.98,-628,-math.pi/2),(1663,-609.42,0)]:
  R=Frame(B,x,z,yaw,y=0);R.box('se-white',(0,5.45,.04),(1.5,1.4,.12));R.text('7',(0,5.29,.12),.85,'se-red',back=True);R.text('ELEVEN',(0,4.97,.12),.2,'se-green',back=True)
 # Fuel islands follow photographed pump positions; dimensions are inferred.
 for x,z,yaw in [(1648.3,-629.5,0),(1657.4,-618.5,.55),(1664.3,-619.8,0)]:
  R=Frame(B,x,z,yaw,y=.04);R.box('se-concrete',(0,.08,0),(1.25,.16,3.2),True)
  R.box('se-white',(0,.68,0),(.84,1.2,.65),True);R.box('se-steel-paint',(0,1.65,0),(.9,.75,.7),True)
  R.box('se-white',(0,2.1,0),(.95,.12,.75));R.box('se-green',(0,.7,.337),(.78,.32,.025));R.text('7',(0,.56,.36),.42,'se-red',back=True)
  for side in [-1,1]:
   R.box('se-screen',(0,1.75,side*.36),(.47,.24,.02));R.box('se-metal-paint',(.28,1.45,side*.36),(.15,.2,.03))
   R.path('se-rubber',[(side*.44,1.9,0),(side*.58,1.5,0),(side*.61,.55,0),(side*.48,.42,0),(side*.42,1.3,0)],.035,8)
  for v in [-1.2,1.2]:R.tube('se-yellow',(0,.15,v),(0,.9,v),.075,12)
 for x,z in [(1662,-642),(1673,-640),(1672,-631)]:
  B.box('se-metal-paint',(x,5.6,z),(1.1,.5,1.1));B.box('se-soffit',(x,5.87,z),(1.2,.04,1.2))
 # Public room: counter details supported by the Feb2025 photo; arrangement inferred.
 B.property=KEY+'-interior';B.source='public/'+KEY
 B.planar('se-floor',p.buffer(-.15),.15,True);B.shell(p.buffer(-.16),.15,4.75,'se-cream',openings=[door,*windows],roof=False,solid=False)
 inside=p.buffer(-.16)
 for tri in triangles(inside):
  pts=[(x,4.65,z) for x,z in list(tri.exterior.coords)[:-1]];a=np.array(pts);B.face('se-ceiling',pts if np.cross(a[1]-a[0],a[2]-a[0])[1]<0 else list(reversed(pts)))
 # Exposed T-grid: reference establishes a tiled ceiling, spacing is estimated.
 for x in np.arange(1660.0,1677.5,.6):
  B.box('se-white',(float(x),4.625,-636.84),(.022,.035,17.5))
 for z in np.arange(-645.5,-628.0,1.2):
  B.box('se-white',(1668.7,4.625,float(z)),(17.5,.035,.022))
 R=Frame(B,1665,-640,0,y=.15)
 R.box('se-cabinet',(0,.58,0),(5,1.16,1.1),True);R.box('se-counter',(0,1.19,0),(5.12,.08,1.2))
 for u in np.arange(-2.2,2.4,.62):
  R.box('se-cabinet',(float(u),.58,.566),(.56,1.02,.035))
  for y in np.arange(.35,.9,.1):R.box('se-metal-paint',(float(u),float(y),.593),(.34,.025,.025))
  R.box('se-metal-paint',(float(u)+.2,1.02,.61),(.1,.035,.05))
 # Wire racks, cup stacks, condiment dispensers, trays and original packaging.
 for y in [1.35,1.7,2.05]:
  R.box('se-steel-paint',(0,y,-.25),(4.8,.045,.48))
  for u in np.arange(-2.4,2.5,.12):R.tube('se-steel-paint',(float(u),y,-.48),(float(u),y,.02),.009,6)
  for j,u in enumerate(np.arange(-2.1,2.2,.42)):
   u=float(u);m=['se-pack-red','se-pack-blue','se-pack-gold','se-pack-green'][(j+int(y*10))%4]
   # Original generic snack bags, not copied product labels.
   R.box(m,(u,y+.14,-.22),(.24,.26,.16))
   R.box('se-white',(u,y+.15,-.132),(.17,.08,.008))
   R.box('se-metal-paint',(u,y+.272,-.22),(.23,.012,.16))
   for dy,w in [(0,.12),(.025,.08)]:R.box('se-steel-paint',(u,y+.14+dy,-.125),(w,.008,.004))
 for u in [-1.6,-.7,.2,1.1]:
  for y in [1.26,1.34,1.42]:R.lathe('se-white',u,.3,[(y,.08),(y+.18,.11)],16)
 for x,z in [(1673,-634),(1673,-639)]:B.box('se-cabinet',(x,1.1,z),(1.0,1.9,3.0),True)
 for x in [1663,1667,1671,1675]:
  for z in [-631,-636,-641]:B.box('se-light',(x,4.62,z),(.6,.035,1.2))
 lights=[dict(p=[1665,4.2,-633],color=0xfff4e0,power=22,range=12),dict(p=[1672,4.2,-640],color=0xfff4e0,power=22,range=12)]
 route=[F.p(3,.34 if v==1 else .15,v) for v in [4,1,-1,-3]]+[(1665,.15,-633),(1669,.15,-633)]
 return dict(key=KEY,name='7-Eleven Paradise Road',center=[p.centroid.x,0,p.centroid.y],bounds=list(p.union(c).bounds),structural=True,exteriorOnly=False,portals=[door],zones=[dict(origin=[1659.7,.15,-636.84],yaw=math.pi/2,width=18,depth=18,height=4.6)],lights=lights,hotelSources=[],routes=[dict(name='Canopy to shop and counter',points=route)])
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
