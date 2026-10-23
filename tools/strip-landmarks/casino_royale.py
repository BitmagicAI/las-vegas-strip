"""Casino Royale: mapped plan and operator/Earth2022–2024 facade references.
Fine ornament and roof heights are visual estimates; preserve neighboring Venetian.
"""
from common import *
from forum_shops import facade_frame
KEY='casinoRoyale';IDS=['way/181282568','way/209373381']
def hip(F,x,w,d,y,rise,mat='cr-slate-roof'):
 # A steep four-sided roof with a short ridge, not a flat triangular billboard.
 a=[(x-w/2,y,-.55),(x+w/2,y,-.55),(x+w/2,y,d),(x-w/2,y,d)]
 ridge=[(x-w*.12,y+rise,d*.5),(x+w*.12,y+rise,d*.5)]
 for pts in [[a[0],a[1],ridge[1],ridge[0]],[a[1],a[2],ridge[1]],[a[2],a[3],ridge[0],ridge[1]],[a[3],a[0],ridge[0]]]:F.b.face(mat,[F.p(*q) for q in pts],True)
 for aa,bb in [(a[0],ridge[0]),(a[1],ridge[1]),(a[2],ridge[1]),(a[3],ridge[0]),(ridge[0],ridge[1])]:F.tube('cr-cream',aa,bb,.07,6)
 for j in range(1,9):
  t=j/10
  F.tube('cr-roof-joint',(x-w/2+w*.38*t,y+rise*t,-.55+(d*.5+.55)*t),(x+w/2-w*.38*t,y+rise*t,-.55+(d*.5+.55)*t),.014,4)
def exterior(B):
 B.property=KEY+'-exterior';B.source='casino-royale';B.detail=0
 p=footprint(IDS[0]);F,L,nx,nz=facade_frame(B,(104.108,-566.939),(77.202,-484.696),p,0)
 front=F.poly([(-20,0),(L,0),(L,13),(-20,13)]).intersection(p)
 rear=p.difference(front.buffer(.015))
 B.shell(rear,.24,8.8,'cr-peach-stucco',roof=False);B.planar('cr-flat-roof',rear,8.8,True);B.planar('tile',p,.24,True)
 # Six separately proportioned themed frontages, ordered south to north.
 widths=[14,15,14,13,14,L-70];heights=[10.5,11.5,12,12.4,10.2,11]
 colors=['cr-purple-stucco','cr-blue-stucco','cr-lavender-stucco','cr-blue-stucco','cr-sage-stucco','cr-cream']
 start=0
 for idx,(w,h,mat) in enumerate(zip(widths,heights,colors)):
  x=start+w/2;q=F.poly([(start,0),(start+w,0),(start+w,13),(start,13)]).intersection(p)
  B.shell(q,.24,h,mat,roof=False);B.planar('cr-flat-roof',q,h,True)
  hip(F,x,w-.6,11,h,6 if idx in [1,3] else 4.8)
  for y in [3.6,h-.45,h]:F.box('cr-cream',(x,y,-.23),(w,.24,.55))
  for xx in [start+.18,start+w-.18]:F.box('cr-cream',(xx,h/2,-.15),(.3,h,.32))
  # Recessed shop glazing and two upper-storey bays, with real projecting trim.
  for xx in np.arange(start+1.6,start+w-.5,2.7):
   F.box('darkglass',(xx,1.85,-.085),(2.3,2.8,.12))
   for u in [-1.17,1.17]:F.box('cr-cream',(xx+u,1.85,-.2),(.08,2.85,.13))
   F.box('cr-cream',(xx,.42,-.25),(2.45,.2,.4))
   for y in [5.3,8.3]:
    if y+1.2>h:continue
    F.box('cr-cream',(xx,y,-.14),(1.6,2.15,.22));F.box('darkglass',(xx,y,-.28),(1.31,1.83,.06))
    F.box('cr-cream',(xx,y,-.34),(.06,1.83,.05));F.box('cr-cream',(xx,y,-.34),(1.31,.06,.05))
    F.box('cr-cream',(xx,y-1.16,-.36),(1.85,.18,.6))
  # Small dormers punctuate the steep slate roofs.
  for xx in [x-w*.23,x+w*.23]:
   F.box(mat,(xx,h+1.4,1.4),(2.1,2.8,2.5))
   F.box('darkglass',(xx,h+1.2,.12),(1.2,1.7,.1))
   hip(F,xx,2.5,2.8,h+2.8,1.6)
  # Shaded street-level shop canopy.
  B.face('cr-burgundy',[F.p(start,3.5,-.2),F.p(start+w,3.5,-.2),F.p(start+w,2.95,-1.4),F.p(start,2.95,-1.4)])
  F.box('cr-cream',(x,2.9,-1.4),(w,.12,.08))
  start+=w
 # Tall central sign/gable tower, raised above the contiguous row.
 x=43;F.box('cr-blue-stucco',(x,14,3.5),(5.2,8,7))
 hip(F,x,6.1,7,18,6.5)
 F.box('cr-sign-blue',(x,11.9,-.55),(4.1,11.5,.32))
 for xx in [x-2.15,x+2.15]:F.box('gold',(xx,11.9,-.78),(.12,11.7,.12))
 for j,ch in enumerate('CASINO'):F.text(ch,(x-.98,16-j*1.28,-.8),1.0,'cr-letter')
 for j,ch in enumerate('ROYALE'):F.text(ch,(x+1.02,16-j*1.28,-.8),1.0,'cr-letter')
 # Southern rounded turret and copper-coloured bulb roof.
 tx=-7.8;tz=2.8;c=F.p(tx,0,tz);circle=Point(c[0],c[2]).buffer(3.4,resolution=16)
 B.shell(circle,.24,11.8,'cr-lavender-stucco',roof=False)
 F.lathe('cr-burgundy',tx,tz,[(11.8,3.6),(12.4,3.8),(14,3.1),(15.5,1.8),(16.3,.75),(16.9,.28),(17.4,0)],32)
 for ang in np.linspace(0,math.tau,16,endpoint=False):
  for y in [5.4,8.6]:
   G=Frame(B,c[0]+3.43*math.cos(ang),c[2]+3.43*math.sin(ang),-ang-math.pi/2,y=0)
   G.box('darkglass',(0,y,0),(.95,2.4,.06));G.box('cr-cream',(0,y-1.3,-.12),(1.18,.17,.3))
  F.tube('cr-cream',(tx+3.48*math.cos(ang),.3,tz+3.48*math.sin(ang)),(tx+3.48*math.cos(ang),11.8,tz+3.48*math.sin(ang)),.07,6)
 for y in [3.6,7,11.8]:F.lathe('cr-cream',tx,tz,[(y,3.62),(y+.22,3.62)],32)
 # Finish the irregular southern return, keeping all geometry inside its mapped lot.
 tail=front.difference(F.poly([(0,0),(L,0),(L,13),(0,13)]).buffer(.015)).difference(circle)
 B.shell(tail,.24,9.5,'cr-peach-stucco',roof=False);B.planar('cr-flat-roof',tail,9.5,True)
 # Hotel rear: regularly spaced small windows and warm horizontal floor bands.
 for pp in parts(rear):
  coords=list(pp.exterior.coords)
  for a,b in zip(coords,coords[1:]):
   G,span,nxx,nzz=facade_frame(B,a,b,pp,0)
   if span<2:continue
   for xx in np.arange(1.8,span-1,3.5):
    for y in [2.2,5.2,7.8]:
     G.box('darkglass',(xx,y,-.07),(1.55,1.25,.08));G.box('cr-cream',(xx,y-.75,-.14),(1.8,.14,.3))
   for y in [3.5,6.5,8.7]:G.box('cr-cream',(span/2,y,-.08),(span,.18,.2))
 for xx in np.arange(110,174,14):
  for zz in np.arange(-550,-473,17):
   if rear.contains(box(xx-1,zz-1,xx+1,zz+1)):B.box('lvw-service',(xx,9.3,zz),(2.1,1,1.8))
 # Documented rear pool, small kidney silhouette within the open courtyard.
 court=box(134,-508,177,-488).difference(p.buffer(.05))
 pool=Point(149,-497).buffer(4.5,resolution=24).union(Point(153,-493).buffer(3.4,resolution=24)).difference(Point(154,-499).buffer(2.7,resolution=20))
 pool=pool.intersection(court.buffer(-1.2))
 B.planar('tile',court.difference(pool),.28,True);B.planar('cr_pool',pool,.12)
 B.planar('cr-cream',pool.buffer(.4).difference(pool),.31,True)
 return dict(key=KEY,name='Casino Royale exterior',center=[126,0,-515],bounds=list(p.bounds),structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],views={})
