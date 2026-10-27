"""Original Harmon Square east dining pad; western mislabeled retail is retained."""
from common import *
KEY='harmon-dining';IDS=['way/1183057878','way/1382446130']
def build(B):
 p=unary_union([footprint(i) for i in IDS]);F=Frame(B,1847.877,986.235,-.00414,y=0)
 B.property=KEY+'-exterior';B.source='podium/harmon-dining';B.detail=0
 B.shell(p,.04,4.8,'hd-tan',roof=False);B.planar('hd-roof',p,4.8)
 # Separate heights and recessed shopfronts preserve the photographed three-tenant rhythm.
 for lo,hi,height in [(0,9.7,7.2),(9.7,16.5,4.95),(16.5,26.5,6.25)]:
  F.box('hd-red',((lo+hi)/2,2.15,-.075),(hi-lo,4.3,.15))
  # Fine horizontal siding, shared batched material.
  for yy in np.arange(.25,4.2,.15):F.box('hd-red-joint',((lo+hi)/2,yy,-.16),(hi-lo,.016,.012))
  F.box('hd-tan' if lo!=9.7 else 'hd-red',((lo+hi)/2,(height+3.35)/2,-.12),(hi-lo,height-3.35,.45))
  F.box('hd-cap',((lo+hi)/2,height+.055,-.12),(hi-lo+.10,.11,.58))
  F.box('hd-tan',((lo+hi)/2,4.9,15.9),(hi-lo,.30,.30))
  for x in [lo+.2,hi-.2]:F.box('hd-tan',(x,1.7,-.35),(.40,3.4,.50),True)
  # Each public front gets a recessed glazed door and continuous mullioned windows.
  a,b=lo+.6,hi-.6
  for j in range(max(2,int((b-a)/1.0))):
   n=max(2,int((b-a)/1.0));x=a+(b-a)*(j+.5)/n;w=(b-a)/n
   F.box('hd-glass',(x,1.7,-.19),(w-.055,2.72,.035))
   F.box('hd-metal',(x-w/2,1.7,-.23),(.05,2.86,.075))
   F.box('hd-metal',(x,2.70,-.24),(w,.045,.07))
  for yy in [.33,3.08]:F.box('hd-metal',((a+b)/2,yy,-.24),(b-a,.055,.075))
  dx=(a+b)/2
  for xx in [dx-.48,dx+.48]:
   F.box('hd-metal',(xx,1.65,-.27),(.055,2.66,.08))
   F.tube('hd-metal',(xx+.10,1.05,-.35),(xx+.10,1.6,-.35),.018,8)
  F.text(str(130 if lo==0 else 120 if lo==9.7 else 110),(dx,2.88,-.29),.16,'hd-white')
 # Roberto's tall angular trim and diagonal inset joints, geometric, not copied imagery.
 for a,b in [((0,7.1),(4,3.4)),((4,3.4),(9.7,7.1)),((0,5.6),(9.7,4.1))]:
  F.tube('hd-joint',(a[0],a[1],-.355),(b[0],b[1],-.355),.012,5)
 F.text("Roberto’s",(4.85,5.63,-.38),1.0,'hd-pink')
 F.text('TACO SHOP',(4.85,5.03,-.38),.21,'hd-green');F.text('OPEN 24 HRS',(4.85,4.42,-.38),.32,'hd-white')
 F.box('hd-tan',(13.1,3.55,-.65),(7.0,.24,1.3))
 F.text('SUBWAY',(13.1,4.25,-.38),.78,'hd-green')
 F.text('DUNKIN’',(23.8,5.30,-.38),.80,'hd-orange');F.text('DONUTS',(23.8,4.48,-.38),.80,'hd-pink')
 F.text('DRIVE THRU',(23.8,3.81,-.38),.26,'hd-white')
 # Oversized takeaway-cup entrance landmark, dimensions estimated from facade photograph.
 # Closed cylinder intersects the opaque facade only; it is not a public entrance.
 F.lathe('hd-brown',18.65,-.68,[(.15,.95),(3.45,1.25)],64)
 F.lathe('hd-white',18.65,-.68,[(3.45,1.25),(6.37,1.53),(6.45,1.56)],64)
 F.lathe('hd-white',18.65,-.68,[(6.45,1.61),(6.60,1.61),(6.65,1.45),(6.88,1.45),(7.15,1.14),(7.27,.75),(7.3,.08)],64)
 for yy in [6.45,6.62]:F.lathe('hd-cap',18.65,-.68,[(yy,1.62),(yy+.045,1.62)],64)
 F.text('DUNKIN’',(18.65,5.23,-2.235),.37,'hd-orange');F.text('DONUTS',(18.65,4.77,-2.235),.37,'hd-pink')
 F.text('COFFEE',(18.65,4.37,-2.235),.16,'hd-brown')
 # Frame the drive-through without filling its 7.9 m mapped gap or changing the road.
 F.box('hd-red',(-4.05,4.7,1.0),(8.10,.75,1.0),True)
 F.text('DRIVE THRU',(-4.05,4.67,.46),.42,'hd-white')
 for x in [-7.85,-.25]:
  F.box('hd-tan',(x,2.15,1.0),(.35,4.3,.65),True)
  F.lathe('hd-red',x,0,[(0,.09),(1.15,.09)],12)
 # Roof perimeter and equipment are separate from the front fascia.
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):B.tube('hd-cap',(a[0],4.95,a[1]),(b[0],4.95,b[1]),.08,6)
 for u,v in [(4,9),(12,10),(21,8)]:
  F.box('hd-equipment',(u,5.3,v),(1.6,.8,1.4));F.box('hd-metal',(u,5.71,v),(1.4,.035,1.2))
  for j in range(10):F.box('hd-metal',(u-.65+j*.145,5.3,v-.715),(.04,.55,.02))
 # East drive-through service window and rear door panels.
 G=Frame(B,*[F.p(26.52,0,10)[i] for i in [0,2]],-math.pi/2-.00414,y=0)
 G.box('hd-metal',(0,1.7,-.07),(2.15,1.55,.10));G.box('hd-glass',(0,1.7,-.13),(2.02,1.40,.04))
 G.box('hd-cap',(0,1.03,-.32),(2.25,.10,.55))
 for u in [5,13,23]:F.box('hd-service',(u,1.2,16.15),(1.1,2.4,.10))
 F.box('hd-paving',(13.2,.06,-1.65),(26.8,.12,3.3),True)
 routes=[dict(name='North storefront sidewalk',points=[F.p(1,.12,-2.8),F.p(10,.12,-2.8),F.p(16,.12,-2.8),F.p(24,.12,-2.8)]),dict(name='Drive through passage',points=[F.p(-4,0,-4),F.p(-4,0,5),F.p(-4,0,15),F.p(-4,0,19)])]
 return dict(key=KEY,name='Harmon Square dining frontage',center=F.p(13,0,8),bounds=list(p.buffer(4).bounds),structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=routes,hotelSources=[])
if __name__=='__main__':
 B=Meshes();meta=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(meta,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
