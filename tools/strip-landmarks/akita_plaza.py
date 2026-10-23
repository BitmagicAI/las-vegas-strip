"""Akita Plaza: mapped T-plan; street photograph establishes bay hierarchy.
Heights and tenant boundaries are estimates. No interior or adjoining parcel claim.
"""
from common import *
from forum_shops import facade_frame
KEY='akitaPlaza'
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/retail';B.detail=0
 p=footprint('way/180250509');B.shell(p,.05,5.45,'ap-stucco',roof=False);B.planar('ap-roof',p,5.45,True)
 F=Frame(B,60.45,2905.06,math.pi/2,y=.32)
 # Front runs north to south in local X (positive X goes north).
 # Long soffit, projecting square piers and recessed shopfronts.
 for start,end,title,mat in [(0,16,"McDonald's",'ap-burgundy'),(16,28,'LIQUOR OUTLET','ap-stucco'),(28,40,'SAYULITAS','ap-stucco'),(40,51,'JF BAKERY','ap-stucco'),(51,72,'PANDA EXPRESS','ap-stucco')]:
  mid=(start+end)/2;L=end-start
  F.box(mat,(mid,4.65,-.1),(L,1.5,.22));F.box('ap-cream',(mid,3.82,-.4),(L,.18,.9))
  for i in range(int(L/1.5)):
   u=start+(i+.5)*L/int(L/1.5);w=L/int(L/1.5)
   F.box('ap-glass',(u,1.85,-.08),(w-.07,3.25,.1))
   F.box('ap-frame',(u-w/2,1.85,-.17),(.065,3.3,.08))
   for y in [.25,1.05,3.45]:F.box('ap-frame',(u,y,-.17),(w,.055,.08))
  # Double entrance with pull handles; glazed panels remain closed exterior doors.
  for d in [-.45,.45]:
   F.box('ap-frame',(mid+d,1.5,-.2),(.05,2.6,.07));F.tube('ap-metal',(mid+d*.3,1.2,-.27),(mid+d*.3,1.65,-.27),.018,7)
  for u in [start+.2,end-.2]:
   F.box('ap-cream',(u,1.95,-.56),(.42,3.9,.68),True);F.box('ap-gray',(u,.27,-.56),(.52,.54,.78),True)
  F.text(title,(mid,4.35,-.29),.82 if L<15 else .8,'ap-white' if start==0 else ('ap-red' if start==51 else ('ap-blue' if start==28 else 'ap-ink')))
  if start in [0,28,51]:
   for d in [-L*.28,L*.28]:
    F.box('ap-white',(mid+d,1.8,-.21),(1.05,1.45,.025))
    F.box('ap-red',(mid+d,2.35,-.23),(1.0,.25,.025))
    F.text('OPEN' if start==28 else 'WELCOME',(mid+d,2.27,-.25),.14,'ap-white')
    F.text('FRESH DAILY',(mid+d,1.8,-.25),.11,'ap-ink')
  if start==28:
   F.box('ap-blue',(mid,3.7,-.94),(L-.8,.1,.1));F.text('MEXICAN FOOD',(mid,3.57,-.96),.25,'ap-red')
  if start==0:
   F.box('ap-yellow',(mid,3.58,-.82),(L,.14,1.35))
   F.box('ap-gray',(mid,5.35,-.24),(L,.7,.18))
   for y in np.arange(5.06,5.67,.09):F.box('ap-metal',(mid,y,-.36),(L,.035,.07))
 # Northern raised hip-roof bay, and central gable over the former Clubwear shop.
 for u,w in [(63,9)]:
  F.box('ap-stucco',(u,5.66,4),(w,1.0,8))
  for a,b in [((-w/2,-.5),(w/2,-.5)),((w/2,-.5),(w/2,8.5)),((w/2,8.5),(-w/2,8.5)),((-w/2,8.5),(-w/2,-.5))]:
   B.face('ap-roof-metal',[F.p(u+a[0],6.22,a[1]),F.p(u+b[0],6.22,b[1]),F.p(u,8,4)])
  F.box('ap-cream',(u,6.2,4),(w+.3,.18,9.3))
 u=35
 B.face('ap-stucco',[F.p(u-6,5.4,-.3),F.p(u+6,5.4,-.3),F.p(u,7.1,-.3)])
 for s in [-1,1]:F.path('ap-cream',[(u+s*6,5.4,-.38),(u,7.1,-.38)],.13,6)
 # South drive-through face: burgundy upper wall, gray ledge and suspended canopy.
 S=Frame(B,72.45,2905.08,math.pi,y=.32)
 S.box('ap-burgundy',(0,3.1,-.08),(24,6.15,.18))
 S.box('ap-metal',(0,3.25,-.62),(24,.18,1.3))
 for u in [-9,-5,-1,3,7,11]:S.tube('ap-metal',(u,4.55,-.15),(u,3.4,-1.23),.025,7)
 S.box('ap-glass',(3,1.9,-.23),(2.1,1.3,.12));S.box('ap-white',(3,2.65,-.23),(2.5,.18,.15));S.text('PAY HERE',(3,2.91,-.26),.18,'ap-white')
 S.text("McDonald's",(0,5.5,-.24),.9,'ap-white')
 # Remaining perimeter: expansion joints, cornice, service doors and drain pipes.
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  G,L,_,_=facade_frame(B,a,b,p,0)
  if a[0]<61 and b[0]<61 or a[1]>2904 and b[1]>2904:continue
  G.box('ap-cream',(L/2,5.4,-.035),(L,.23,.17));G.box('ap-gray',(L/2,.43,-.035),(L,.8,.1))
  for u in np.arange(3,L,5):G.box('ap-joint',(u,2.9,-.06),(.025,4.6,.02))
  if L>10:
   G.box('ap-service',(L*.65,1.35,-.1),(1.1,2.5,.13));G.box('ap-metal',(L*.65,2.7,-.3),(1.4,.1,.6));G.tube('ap-metal',(L-.4,.3,-.12),(L-.4,5.2,-.12),.055,8)
 # Rooftop packaged units, screened service extension.
 W=Frame(B,0,0,y=0)
 for x,z in [(74,2843),(74,2857),(75,2875),(75,2894),(95,2869)]:
  W.box('ap-metal',(x,5.8,z),(2.5,.7,1.8))
  for k in range(9):W.box('ap-ink',(x-1.15+k*.28,6.16,z),(.09,.025,1.6))
 # Exact public site excludes separate eastern building and south road.
 site=box(40,2827,110,2913).difference(p);apron=p.buffer(2.5).difference(p)
 for x in range(40,110,4):
  for z in range(2827,2913,4):
   cell=site.intersection(box(x,z,x+4,z+4));B.planar('ap-asphalt',cell.difference(apron),.32,True);B.planar('ap-paving',cell.intersection(apron),.44,True)
 # Short perpendicular parking row, line paint on the asphalt.
 for z in np.arange(2834,2891,2.8):W.box('ap-line',(50,.333,z),(5.1,.014,.09))
 for z in np.arange(2835.4,2889,2.8):W.box('ap-gray',(55,.49,z),(.15,.27,1.8),True)
 # Tenant pylon based on 2025 Street View; sign heights are estimates.
 P=Frame(B,43,2894,math.pi/2,y=.32)
 P.box('ap-white',(0,5,0),(.9,10,.85),True)
 for y,h,txt,mat,ink in [(10.7,2.5,"McDonald's",'ap-burgundy','ap-yellow'),(8.9,.9,'PANDA EXPRESS','ap-red','ap-white'),(7.3,2.1,'LIQUOR OUTLET','ap-white','ap-ink'),(5.55,1.1,'SAYULITAS','ap-white','ap-blue'),(4.55,.75,'JF BAKERY','ap-white','ap-ink')]:
  P.box(mat,(0,y,0),(4.8,h,.45),True)
  for back in [False,True]:P.text(txt,(0,y-.17,.26 if back else -.26),.35,ink,back=back)
 B.detail=0
 return dict(key=KEY,name='Akita Plaza retail exterior',center=[75,0,2870],bounds=[39,2826,111,2914],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
