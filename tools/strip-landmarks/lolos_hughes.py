"""Original Hughes retail exterior. Dimensions fitted to mapped footprint and photo."""
from common import *
KEY='lolos-hughes';IDS=['way/1001560963','way/1423439018']
def build(B):
 p=unary_union([footprint(i) for i in IDS]);W=Frame(B,0,0,0,y=0)
 B.property=KEY+'-exterior';B.source='retail/'+KEY;B.detail=0
 # Taller southern restaurant volume; the named OSM outline is its covered patio.
 main=footprint(IDS[0]);south=main.intersection(Polygon([(1270,96),(1315,96),(1315,125),(1270,125)]));north=main.difference(south)
 R=Frame(B,1300.71,76,-math.pi/2+.0356,y=0)
 door=dict(p=R.p(0,.28,0),yaw=R.yaw,width=2.0,height=2.65,name='SIXT public rental office',venue=KEY)
 opening=dict(p=R.p(0,.28,0),yaw=R.yaw,width=8.1,height=3.9)
 B.shell(north,.02,5.8,'lh-stucco',roof=False,openings=[opening]);B.planar('lh-membrane',north,5.8)
 B.shell(south,.02,9.4,'lh-stone',roof=False);B.planar('lh-membrane',south,9.4)
 def glazing(F,w,h,base=.28):
  F.box('lh-glass',(0,base+h/2,.065),(w,h,.045))
  for u in np.linspace(-w/2,w/2,max(2,int(w/1.35)+1)):
   F.box('lh-alloy',(float(u),base+h/2,.12),(.055,h,.1))
  for y in [base,2.65,base+h]:F.box('lh-alloy',(0,y,.12),(w,.055,.1))
 # East entrance photo: high clerestory and deep charcoal portal backed by veined stone.
 E=Frame(B,1300.57,107.2,math.pi/2+.0356,y=0)
 glazing(E,16.8,8.7)
 for u in [-6.55,6.55]:E.box('lh-stone',(u,4.0,.38),(3.7,8,.68),True)
 for y in np.arange(.6,8,.55):
  for u in [-6.55,6.55]:E.box('lh-joint',(u,float(y),.735),(3.68,.016,.015))
 E.box('lh-charcoal',(0,6.05,1.0),(12.8,2.05,1.9),True)
 E.box('lh-charcoal',(5.7,2.55,1.0),(1.4,5.1,1.9),True)
 for u in [-2.7,2.7]:E.box('lh-stone',(u,2.5,.9),(.7,5,1.7),True)
 E.box('lh-alloy',(0,3.05,1.15),(4.8,.14,2.5))
 E.text("Lo-Lo's",(0,6.3,1.99),.82,'lh-gold',back=True)
 E.text('Chicken & Waffles',(0,5.62,1.99),.34,'lh-letter',back=True)
 for u in [-.62,.62]:E.box('lh-charcoal',(u,1.4,.24),(.04,.5,.05))
 E.box('lh-alloy',(0,9.35,.75),(21.5,.24,2.8))
 # South glazing and covered patio shown in aerial; full depth is kept open underneath.
 S=Frame(B,1288.5,115.25,.0356,y=0)
 glazing(S,17.0,8.4)
 S.box('lh-alloy',(0,9.35,.4),(20.7,.24,1.6))
 patio=footprint(IDS[1]);B.planar('lh-paving',patio,.25,True)
 B.planar('lh-membrane',patio,3.6);B.planar('lh-canopy',patio,3.42)
 for u in [-8.4,0,8.4]:
  for v in [1,6.6]:S.box('lh-charcoal',(u,1.83,v),(.14,3.18,.14),True)
 S.box('lh-canopy',(0,3.5,6.7),(17.2,.22,.18))
 for u in [-6,-2.7,2.7,6]:
  S.box('lh-charcoal',(u,.66,3.9),(.1,.8,.1));S.box('lh-wood',(u,1.1,3.9),(1.35,.08,.72),True)
  for dv in [-.75,.75]:
   S.box('lh-charcoal',(u,.7,3.9+dv),(.5,.07,.45),True)
   for a in [-.2,.2]:
    for b in [-.17,.17]:S.box('lh-charcoal',(u+a,.47,3.9+dv+b),(.04,.46,.04))
   S.box('lh-charcoal',(u,1.0,3.9+dv+math.copysign(.2,dv)),(.5,.5,.04))
 # Existing northern retail remains lower. Suite markings avoid unverified tenant names.
 for z,n in [(89,'120'),(76,'140'),(65,'150')]:
  x=1301.0 if z<81 else 1300.6;D=Frame(B,x,z,math.pi/2+.0356,y=0)
  if n!='140':glazing(D,8.1,3.9)
  else:
   for a,b in [(-4.05,-1.06),(1.06,4.05)]:
    D.box('lh-clear',((a+b)/2,2.23,-.1),(b-a,3.9,.035),True)
    for u in np.arange(a,b,1.2):D.box('lh-alloy',(float(u),2.23,-.06),(.055,3.9,.1))
   for u in [-1.04,1.04]:D.box('lh-alloy',(u,1.6,-.06),(.08,2.65,.1))
   D.box('lh-clear',(0,3.6,-.1),(2.0,1.04,.035),True)
   D.box('lh-stucco',(0,5.45,.16),(5.7,2.1,.3))
   D.text('SIXT',(0,5.42,.34),.56,'lh-letter',back=True)
   D.box('lh-orange',(0,5.04,.36),(2.9,.085,.05))
  D.box('lh-canopy',(0,4.22,.7),(8.7,.15,1.5))
  D.text(n,(0,3.05,.21),.22,'lh-letter',back=True)
  for u in [-4.5,4.5]:
   D.box('lh-stucco',(u,2.7,.17),(.65,5.4,.3));D.box('lh-stone',(u,.72,.2),(.68,.9,.34))
   D.box('lh-lamp',(u,2.65,.36),(.12,.35,.09))
 # Northern angled end bay follows mapped footprint; glazing rhythm inferred.
 for x,z,ang,w in [(1305.7,56.8,2.47,8.5),(1295.7,50.1,2.47,8.0)]:
  N=Frame(B,x,z,ang,y=0);glazing(N,w,3.9);N.box('lh-canopy',(0,4.25,.65),(w+.5,.14,1.4));N.text('160',(0,3.05,.22),.22,'lh-letter',back=True)
 # Roof equipment and service doors; no changes to adjoining streets or lots.
 for x,z,h in [(1288,104,9.4),(1294,100,9.4),(1286,87,5.8),(1292,78,5.8),(1294,63,5.8)]:
  W.box('lh-equipment',(x,h+.48,z),(2.2,.95,1.6))
  for y in np.arange(h+.15,h+.85,.14):W.box('lh-charcoal',(x,float(y),z+.81),(1.95,.035,.025))
 for z in [100,82,65]:
  D=Frame(B,1278.4+(100-z)*.0356,z,-math.pi/2+.0356,y=0)
  D.box('lh-charcoal',(0,1.55,.09),(1.15,2.8,.12));D.box('lh-alloy',(.4,1.4,.18),(.04,.3,.04))
 for poly in parts(main):
  ring=list(poly.exterior.coords)
  for a,b in zip(ring,ring[1:]):
   y=9.5 if min(a[1],b[1])>=96 else 5.9;W.tube('lh-alloy',(a[0],y,a[1]),(b[0],y,b[1]),.085,6)
 # Gentle entrance transition from existing lower forecourt to raised public floor.
 B.upface('lh-paving',[R.p(-1.3,.01,-3.6),R.p(1.3,.01,-3.6),R.p(1.3,.28,.25),R.p(-1.3,.28,.25)],True)
 # Small public rental office supported by February2026 business photograph.
 B.property=KEY+'-interior';B.source='interior/'+KEY;B.detail=1
 room=R.poly([(-4.1,.12),(4.1,.12),(4.1,10.1),(-4.1,10.1)])
 B.shell(room,.28,3.55,'lh-wall',roof=False,openings=[opening]);B.planar('lh-floor',room,.28,True);B.planar('lh-ceiling',room,3.55)
 for u in np.arange(-3.6,4,.6):R.box('lh-joint',(float(u),.286,5.1),(.014,.006,9.9))
 for v in np.arange(.3,10,.6):R.box('lh-joint',(0,.286,float(v)),(8.1,.006,.014))
 for u in np.arange(-3.6,4,1.2):R.box('lh-grid',(float(u),3.52,5.1),(.018,.02,9.9))
 for v in np.arange(.5,10,1.2):R.box('lh-grid',(0,3.52,float(v)),(8.1,.02,.018))
 for u in [-2.4,1.8]:
  for v in [2,5,8]:R.box('lh-lamp',(u,3.5,v),(.58,.025,1.12))
 R.box('lh-orange',(0,1.9,10.04),(8.05,3.15,.04))
 # Original plain wall graphic replaces copyrighted photo mural.
 R.box('lh-charcoal',(-4.04,1.9,5.1),(.04,3.15,9.7))
 for v in [3.5,6]:
  R.box('lh-orange',(-3.25,.52,v),(.55,.48,.55),True)
  R.box('lh-orange',(1.9,.83,v),(1.9,1.1,1.35),True);R.box('lh-charcoal',(1.9,1.42,v),(2.02,.08,1.47),True)
  R.box('lh-charcoal',(1.9,1.65,v),(.08,.4,.1));R.box('lh-charcoal',(1.9,1.96,v),(.7,.44,.09));R.box('lh-screen',(1.9,1.96,v-.05),(.64,.38,.012))
  R.box('lh-charcoal',(1.9,1.48,v-.45),(.5,.035,.18))
  for a in range(9):
   for b in range(3):R.box('lh-grid',(1.68+a*.05,1.505,v-.5+b*.05),(.035,.009,.035))
 for u in [-2.8,-1.4]:
  R.box('lh-chair',(u,.75,8.3),(.62,.12,.6),True);R.box('lh-chair',(u,1.13,8.56),(.62,.68,.12),True)
  for a in [-.23,.23]:
   for b in [-.23,.23]:R.box('lh-alloy',(u+a,.49,8.3+b),(.04,.42,.04))
 R.text('SIXT',(0,2.7,9.99),.5,'lh-charcoal',back=False)
 R.box('lh-charcoal',(0,.29,1), (1.9,.02,1.3))
 routes=[dict(name='East retail walk',points=[[1314,.28,z] for z in [124,110,96,82,68,56]]),dict(name='Southern patio approach',points=[[1313,.28,126],[1305,.28,126],[1296,.28,126],[1286,.28,126]])]
 routes.append(dict(name='SIXT public office',points=[R.p(0,.28,v) for v in [-4,-1,1,3,6,8]]))
 return dict(key=KEY,name='325 Hughes Center retail / Lo-Los',center=[1293,0,88],bounds=list(p.bounds),structural=True,hotelSources=[],exteriorOnly=False,portals=[door],zones=[dict(origin=R.p(0,.28,0),yaw=R.yaw,width=8.3,depth=10.3,height=3.6)],lights=[dict(p=R.p(u,3.1,v),color=0xf3f0e8,power=4,range=7) for u,v in [(-2,3),(2,3),(-2,8),(2,8)]],routes=routes)
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
