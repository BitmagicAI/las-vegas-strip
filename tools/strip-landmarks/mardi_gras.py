"""Original mapped Mardi Gras exterior. Heights/room rhythm inferred; reference links in block record."""
from common import *
KEY='mardi-gras';IDS=['way/33962963','way/33963206','way/1421907606','way/1421907607']
def rail(F,w,y,v=0):
 for h in [.13,1.03]:F.box('mg-iron',(0,y+h,v),(w,.045,.055))
 for u in np.arange(-w/2,w/2+.01,.22):F.box('mg-iron',(float(u),y+.57,v),(.026,1.03,.026))
 for u in np.arange(-w/2+.55,w/2,1.1):
  F.path('mg-iron',[(u,y+.3,v),(u+.12,y+.55,v),(u,y+.8,v),(u-.12,y+.55,v),(u,y+.3,v)],.018,5)
def glazing(F,u,y,v,w,h):
 F.box('mg-glass',(u,y+h/2,v),(w,h,.055))
 for x in [u-w/2,u,u+w/2]:F.box('mg-frame',(x,y+h/2,v+.035),(.055,h+.08,.08))
 for yy in [y,y+h]:F.box('mg-frame',(u,yy,v+.035),(w,.055,.08))
def edge(F,w):
 # Open the top corridor guard only where the pavilion bridge meets it.
 bridgeCuts=[]
 if abs(F.co)>.99 and -1065<F.z<-1044:
  ends=sorted([(1723.7-F.x)/F.co,(1726.2-F.x)/F.co]);bridgeCuts=ends
 for floor in range(3):
  y=.16+floor*3.05
  n=max(1,round(w/4.8));pitch=w/n
  for j in range(n):
   u=-w/2+(j+.5)*pitch
   glazing(F,u+.45,y+.55,-1.96,min(2.35,pitch*.48),1.65)
   F.box('mg-door',(u-pitch*.32,y+1.06,-1.94),(.85,2.12,.06));F.box('mg-brass',(u-pitch*.32+.3,y+1.03,-1.88),(.035,.17,.05))
   if not (floor==2 and bridgeCuts and bridgeCuts[0]-.2<u-pitch/2<bridgeCuts[1]+.2):F.box('mg-stucco',(u-pitch/2,y+1.5,-.02),(.23,3.0,.25),True)
   if floor==2:F.arch(u,0,pitch-.25,y+2.9,'mg-stucco',.15,base=y+2.1)
  if floor:
   if floor==2 and bridgeCuts:
    lo,hi=bridgeCuts
    for a,b in [(-w/2,min(w/2,lo)),(max(-w/2,hi),w/2)]:
     if b>a:
      c=F.p((a+b)/2,0,0);rail(Frame(F.b,c[0],c[2],F.yaw,y=F.y),b-a,y)
   else:rail(F,w,y)
  F.box('mg-trim',(0,y-.08,-.85),(w,.17,2.25),True)

def build(B):
 p=footprint(IDS[0]);q=footprint(IDS[1]);B.property=KEY+'-exterior';B.source='podium/'+KEY;B.detail=0
 # Recess the room shell behind the exterior corridors, retaining mapped overall outline.
 room=p.buffer(-2,join_style=2);B.shell(room,.03,9.3,'mg-stucco',roof=False);B.planar('mg-roof',p.buffer(-4,join_style=2),11.5)
 # Continuous offset roof rings close the corners and avoid overlapping eaves.
 for k in range(12):
  d0=-.3+4.3*k/12;d1=-.3+4.3*(k+1)/12
  ring=p.buffer(-d0,join_style=2).difference(p.buffer(-d1,join_style=2))
  for poly in parts(ring):
   for tri in triangles(poly):
    pts=[]
    for x,z in list(tri.exterior.coords)[:-1]:
     dist=p.boundary.distance(Point(x,z))*(1 if p.covers(Point(x,z)) else -1);t=max(0,min(1,(dist+.3)/4.3));pts.append((x,9.2+2.3*math.sqrt(t),z))
    B.upface('mg-copper',pts)
 for y in [.16,3.21,6.26]:B.planar('mg-deck',p.difference(room),y,True)
 coords=list(p.exterior.coords)
 for a,b in zip(coords,coords[1:]):
  dx,dz=b[0]-a[0],b[1]-a[1];w=math.hypot(dx,dz)
  if w<7:continue
  # Determine outward normal independently of polygon winding.
  nx,nz=-dz/w,dx/w;mid=((a[0]+b[0])/2,(a[1]+b[1])/2)
  if p.contains(Point(mid[0]+nx*.2,mid[1]+nz*.2)):nx,nz=-nx,-nz
  yaw=math.atan2(nx,nz);F=Frame(B,*mid,yaw,y=0);edge(F,w)
 # West motor court and porte cochere; keep drive passage open under the canopy.
 W=Frame(B,1657.75,-1053.8,-math.pi/2,y=0)
 W.box('mg-stucco',(0,4.6,2.45),(15.6,1.1,4.9));W.box('mg-trim',(0,4.01,2.45),(15.8,.12,5.1))
 for u in [-7.2,0,7.2]:
  for v in [1,4.3]:
   W.box('mg-stone',(u,.45,v),(1,.9,1),True);W.tube('mg-iron',(u,.9,v),(u,4.02,v),.09,12)
 for u in [-7,-3.5,3.5,7]:
  W.tube('mg-iron',(u,3.4,5),(u,4,5),.025,8);W.box('mg-lantern',(u,3.22,5),(.26,.38,.26));W.box('mg-iron',(u,3.44,5),(.32,.07,.32))
 rail(Frame(B,*W.p(0,0,4.9)[::2],-math.pi/2,y=0),15.6,5.16)
 W.box('mg-copper',(0,10.1,.35),(20,2.4,.25));W.text('MARDI GRAS HOTEL',(0,10.1,.5),1.13,'mg-trim',back=True)
 W.box('mg-deck',(0,.02,6),(5,.2,13),True)
 glazing(W,0,.16,.18,2.6,2.7)
 for u in [-7,7]:
  W.box('mg-stone',(u,.35,3),(2.4,.7,3),True);W.box('mg-soil',(u,.72,3),(2.2,.06,2.8));W.bench(u,6,'mg-wood')
 # Separate low courtyard pavilion on its mapped outline.
 B.shell(q,.03,6.1,'mg-stucco',roof=False);B.planar('mg-deck',q.difference(box(1724.9,-1050.05,1728.3,-1048.35)),6.26,True)
 for z,yaw in [(-1048.12,0),(-1059.7,math.pi)]:
  C=Frame(B,1709.85,z,yaw,y=0)
  for u in [-12,-8,-4,0,4,8,12]:glazing(C,u,.6,.09,2.7,2)
 P=Frame(B,1725.72,-1054,math.pi/2,y=0)
 for u in [-3.6,0,3.6]:glazing(P,u,.25,.08,3.1,2.45)
 # Exposed two-flight stair and upper terrace: visible in two independent pool views.
 # Placement/rise are fitted estimates; this does not invent an indoor stair core.
 T=Frame(B,1727.3,-1062.4,0,y=.16)
 T.stairs(0,0,1.8,3.05,5.5)
 T.box('mg-deck',(0,3.05-.10,6.2),(1.8,.2,1.4),True)
 T.stairs(0,6.9,1.8,3.05,5.5,y=3.05)
 for side in [-1,1]:
  for lo,hi,y0,y1 in [(0,5.5,0,3.05),(6.9,12.4,3.05,6.1)]:T.tube('mg-iron',(side*.87,y0-.08,lo),(side*.87,y1-.08,hi),.085,4)
  T.tube('mg-iron',(side*.82,4.1,5.5),(side*.82,4.1,6.9),.045)
  for zz in [5.5,6.9]:T.box('mg-iron',(side*.82,1.525,zz),(.12,3.05,.12),True)
 # Terrace connectors land on the top exterior corridors, through matching rail gaps.
 for z0,z1 in [(-1064.0,-1059.7),(-1048.1,-1045.5)]:
  B.box('mg-deck',(1724.95,6.16,(z0+z1)/2),(2.5,.2,z1-z0),True)
  for x in [1723.7,1726.2]:
   G=Frame(B,x,(z0+z1)/2,math.pi/2,y=0);rail(G,z1-z0,6.26)
 B.box('mg-deck',(1726.6,6.16,-1049.2),(3.4,.2,1.7),True)
 for x,y,z in [(1728.2,0,-1048.35),(1728.2,0,-1050.05)]:
  B.box('mg-iron',(x,3.08,z),(.12,6.16,.12),True)
 rail(Frame(B,1726.95,-1048.35,0,y=0),2.5,6.26)
 rail(Frame(B,1728.2,-1049.2,math.pi/2,y=0),1.7,6.26)
 # Pavilion terrace perimeter rails stop at the stair and corridor connectors.
 for z in [-1059.73,-1048.1]:
  rail(Frame(B,1709.0,z,0,y=0),29.4,6.26)
 rail(Frame(B,1694,-1053.9,math.pi/2,y=0),11.5,6.26)
 rail(Frame(B,1725.67,-1055.4,math.pi/2,y=0),8.5,6.26)
 # Eastern pavilion is retained as a building, with a route passing its north side.
 east=footprint(IDS[3]);B.shell(east,.03,3.3,'mg-stucco',roof=False);B.planar('mg-roof',east,3.4)
 E=Frame(B,1785.98,-1055,-math.pi/2,y=0)
 for u in [-3,0,3]:glazing(E,u,.55,.08,2.3,2)
 # Pool deck is an original plan fitted to the aerial, with estimated dimensions.
 pool=box(1732,-1058.3,1750,-1050.1).union(Point(1741,-1054.2).buffer(5.4,resolution=32)).buffer(.35).buffer(-.35)
 spa=Point(1762,-1054.2).buffer(2.2,resolution=32)
 deck=box(1728,-1061.8,1770,-1047.6).difference(pool.union(spa))
 B.planar('mg-deck',deck,.12,True)
 for basin in [pool,spa]:
  B.planar('mg-coping',basin.buffer(.3).difference(basin),.18,True);B.shell(basin,-1.2,.14,'mg-tile',roof=False);B.planar('mg_pool',basin,.04);B.planar('mg-tile',basin,-1.15)
 for x in [1733,1748]:
  for zz in [-1049.5,-1058.9]:
   F=Frame(B,x,zz,0,y=0)
   for u in [-.35,.35]:F.path('mg-frame',[(u,.15,0),(u,.85,0),(u,.95,.3),(u,.8,.65),(u,-.3,.65)],.035,8)
 for x in np.arange(1730,1769,3.1):
  for z in [-1047.95,-1061.3]:
   F=Frame(B,float(x),z,0,y=0);F.box('mg-frame',(0,.32,0),(.65,.09,1.65));F.box('mg-blue',(0,.39,0),(.59,.07,1.55));F.box('mg-blue',(0,.64,-.64),(.59,.55,.09))
 # Ground-level continuous route along the eastern opening and both inner corridors.
 routes=[dict(name='West entrance approach',points=[W.p(2,.12,v) for v in [12,8,3,2]]+[W.p(0,.12,2)]),dict(name='Courtyard east and pool approach',points=[(1802,.12,-1048),(1797,.12,-1048),(1773,.12,-1048),(1773,.12,-1047),(1730,.12,-1047)])]
 routes.append(dict(name='Pavilion exposed stair and upper terrace',points=[(1730,.16,-1062.4),(1727.3,.16,-1062.4),(1727.3,3.21,-1056.9),(1727.3,3.21,-1055.5),(1727.3,6.26,-1050),(1727.3,6.26,-1049.2),(1724.95,6.26,-1049.2),(1724.95,6.26,-1044.8)]))
 return dict(key=KEY,name='Mardi Gras Hotel & Casino',center=[1727,0,-1054],bounds=[1645,-1085,1802,-1021],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],hotelSources=[],routes=routes)
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
