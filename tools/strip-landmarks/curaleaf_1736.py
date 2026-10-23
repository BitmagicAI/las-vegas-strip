"""1736 Curaleaf street frontage, January2026 boarded east panels."""
from common import *
from forum_shops import facade_frame
KEY='curaleaf1736'
def yucca(B,x,z,seed):
 rng=random.Random(seed);F=Frame(B,x,z,y=.22)
 for k in range(38):
  a=k*2.39996;lean=rng.uniform(.35,.9);h=rng.uniform(.45,1.05);w=rng.uniform(.025,.045);co,si=math.cos(a),math.sin(a)
  pts=[(0,0,0),(co*lean*.35,h*.67,si*lean*.35),(co*lean,h,si*lean)]
  for i in range(2):
   a0,b0=pts[i],pts[i+1];wa=w if i==0 else w*.65;wb=w*.65 if i==0 else 0
   vs=[F.p(a0[0]-si*wa,a0[1],a0[2]+co*wa),F.p(a0[0]+si*wa,a0[1]+.015,a0[2]-co*wa),F.p(b0[0]+si*wb,b0[1],b0[2]-co*wb),F.p(b0[0]-si*wb,b0[1],b0[2]+co*wb)]
   mat='cu-leaf-light' if k%4==0 else 'cu-leaf';B.face(mat,vs);B.face(mat,list(reversed(vs)))
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/retail';B.detail=0
 p=footprint('way/364846569');B.shell(p,.15,4.25,'cu-gray-stucco',roof=False);B.planar('cu-roof-paint',p,4.18,True)
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  G,L,nx,nz=facade_frame(B,a,b,p,.025)
  G.box('cu-base-paint',(L/2,.65,-.04),(L,.9,.1));G.box('cu-fascia-paint',(L/2,4.1,-.04),(L,.3,.16))
  G.box('cu-cap-metal-paint',(L/2,4.32,-.1),(L+.08,.08,.38))
  if L>5 and (nx>.7 or abs(nz)>.7):
   count=max(2,round(L/2.7));step=L/count
   for i in range(count):
    u=(i+.5)*step
    G.box('cu-board'+str(i%3),(u,2.55,-.1),(step-.42,2.8,.14))
    for du in [-step*.23,0,step*.23]:G.box('cu-board-joint',(u+du,2.55,-.18),(.012,2.7,.018))
    G.box('cu-stacked-ashlar',(i*step+.12,2.55,-.12),(.25,2.85,.22))
   G.box('cu-stacked-ashlar',(L-.12,2.55,-.12),(.25,2.85,.22))
  elif L>2:
   G.box('cu-service-paint',(L/2,1.55,-.08),(1,2.4,.14))
  if nx>.7 and L>5:
   G.text('1736',(L-.6,4,-.22),.3,'cu-dark-letter')
   # Projecting horizontal sunshade strips and brackets visible above east front.
   for y in [4.45,4.55]:G.box('cu-cap-metal-paint',(L/2,y,-.42),(L,.06,.8))
   for u in np.arange(.3,L,.9):G.box('cu-frame-paint',(float(u),4.4,-.35),(.035,.22,.85))
 W=Frame(B,0,0,y=0)
 # Southeast corner sign tower, gray-blue panel skin with staggered vertical strips.
 T=Frame(B,1762.5,-3813.3,yaw=-math.pi/2+.025,y=0)
 T.box('cu-tower-paint',(0,4.8,0),(2.4,9.3,1.35),True)
 for side in [-1,1]:
  for u in np.arange(-1.15,1.16,.16):
   for i in range(10):
    y=.8+i*.8+(int((u+1.2)*10)%2)*.2
    T.box('cu-tile-light' if int((u+1.2)*100)%3 else 'cu-tile-dark',(float(u),y,side*.69),(.12,.7,.025))
 T.text('Curaleaf',(0,7.45,-.73),.4,'cu-white-letter');T.text('DISPENSARY',(0,7.05,-.73),.17,'cu-white-letter')
 # Leaf mark as a thin curved outline; exact vector brand artwork remains a refinement.
 path=[(0+.65*math.cos(a),8.35+.42*math.sin(a),-.74) for a in np.linspace(.3,5.8,32)]
 T.path('cu-white-letter',path,.022,6);T.path('cu-white-letter',[(-.65,7.95,-.74),(.25,8.6,-.74)],.022,6)
 for dx in [-1.5,1.5]:T.tube('cu-yellow-paint',(dx,.18,-.4),(dx,1.3,-.4),.055,8)
 # Narrow apron, north entrance approach and site circulation, avoiding neighboring footprints.
 site=Polygon([(1705,-3835),(1768,-3835),(1772,-3829),(1767,-3808),(1730,-3807),(1705,-3810)]).difference(p)
 garden=Polygon([(1766,-3832),(1770,-3829),(1766,-3810),(1761,-3810),(1765,-3820)]).difference(p.buffer(.8))
 B.planar('cu-asphalt',site.difference(garden),.14,True);B.planar('cu-gravel',garden,.19,True)
 apron=p.buffer(.9).difference(p);B.planar('cu-paving',apron,.2,True)
 for x in np.arange(1733,1765,2.7):W.box('cu-line-paint',(float(x),.155,-3831),(.06,.02,3.8))
 # North entry vestibule kept opaque pending an interior pass.
 G=Frame(B,1747.5,-3825.63,yaw=0,y=0)
 G.box('cu-glass',(0,1.7,-.12),(2.3,2.8,.12))
 for x in [-1.15,0,1.15]:G.box('cu-frame-paint',(x,1.7,-.2),(.06,2.9,.08))
 G.box('cu-cap-metal-paint',(0,3.45,-.65),(3,.15,1.6));G.box('cu-paving',(0,.2,-2.2),(3.5,.1,4.4),True)
 for x,z in [(1738,-3820),(1742,-3817),(1756,-3818),(1752,-3820)]:
  W.box('cu-service-paint',(x,4.55,z),(1.2,.7,1));W.box('cu-vent',(x,4.92,z),(1,.04,.8))
 for i,(x,z) in enumerate([(1767,-3829),(1767,-3825),(1766.5,-3822),(1765.5,-3815),(1764,-3811)]):yucca(B,x,z,300+i)
 # Detached western utility enclosure shown in overhead imagery.
 W.box('cu-wood',(1712,1.55,-3818),(5,2.8,3),True)
 for x in np.arange(1709.6,1714.5,.17):W.box('cu-wood-joint',(float(x),1.55,-3816.48),(.025,2.75,.03))
 samples=[]
 for x in np.arange(1707,1769,1.1):
  for z in np.arange(-3834,-3809,1.1):
   pt=Point(x,z)
   if site.buffer(-.7).covers(pt) and not p.buffer(2).covers(pt) and not box(1708,-3821,1716,-3815).covers(pt) and pt.distance(Point(1762.5,-3813.3))>2:samples.append([float(x),.14,float(z)])
 Path('build/city-exteriors/curaleaf-1736-samples.json').write_text(json.dumps(samples))
 return dict(key=KEY,name='Curaleaf1736 exterior',center=[1748,0,-3818],bounds=[1704,-3836,1773,-3806],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
