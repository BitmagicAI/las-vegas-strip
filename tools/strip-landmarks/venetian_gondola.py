"""Original metre-scale gondola, based on Venetian's official outdoor ride photos.
Hollow asymmetric clinker-free lacquer hull, ferro, passenger saloon and rowing gear.
No downloaded mesh or texture. Major form stays at distance; fittings are near detail.
"""
import math
import numpy as np
from common import Frame

def gondola(B,x,z,yaw,y=.31):
 old_source,old_detail=B.source,B.detail
 B.source='venetian-gondolas';B.detail=0
 G=Frame(B,x,z,yaw,y=y)
 def face(mat,pts):B.face(mat,[G.p(*p) for p in pts])
 def beam(t):return 1.04*max(.006,1-t*t)**.72*(1+.06*t)
 def sheer(t):return .49+.56*abs(t)**3+.10*max(-t,0)**7
 def center(t):return .09*(1-t*t)
 def hull(t,s,inner=False):
  # s: bottom keel to the gunwale; the two skins join around an open cockpit.
  side=1 if s>=0 else -1;q=abs(s);w=beam(t)*math.sin(q*math.pi/2)
  y=-.29*(1-t*t)+sheer(t)*q**2.25
  if inner:w=max(0,w-.047*math.sin(q*math.pi/2));y+=.055*(1-q)
  return(center(t)+side*w,y,t*5.05)
 ts=np.linspace(-.996,.996,101);ss=np.linspace(-1,1,25)
 for inner in [False,True]:
  for t,tt in zip(ts,ts[1:]):
   for s,st in zip(ss,ss[1:]):
    pts=[hull(t,s,inner),hull(tt,s,inner),hull(tt,st,inner),hull(t,st,inner)]
    face('gondola-lacquer',pts[::-1] if inner else pts)
 for side in [-1,1]:
  G.path('gondola-lacquer',[hull(t,side) for t in ts],.052,10)
  G.path('gondola-brass',[(p[0],p[1]+.038,p[2]) for p in [hull(t,side) for t in ts]],.012,6)
 # Raised foredeck and stern rowing platform; curved outlines, recessed central sole.
 for aa,bb in [(-.99,-.43),(.54,.99)]:
  for t,tt in zip(np.linspace(aa,bb,31),np.linspace(aa,bb,31)[1:]):
   face('gondola-lacquer',[(center(t)-beam(t),sheer(t)-.02,t*5.05),(center(tt)-beam(tt),sheer(tt)-.02,tt*5.05),(center(tt)+beam(tt),sheer(tt)-.02,tt*5.05),(center(t)+beam(t),sheer(t)-.02,t*5.05)])
 for i in range(11):
  xx=(i-5)*.139
  G.box('gondola-wood',(xx,.085,.28),(.128,.05,4.5))
 for zz in [-1.95,2.5]:G.box('gondola-wood',(.06,.20,zz),(1.5,.18,.18))
 # Aft-facing raised scroll-backed red velvet passenger bench, two side seats.
 G.box('gondola-lacquer',(.06,.39,.82),(1.73,.35,.90))
 def cushion(cx,cy,cz,sx,sy,sz):
  B.sphere('gondola-upholstery',G.p(cx,cy,cz),1,24,12,(sx,sy,sz))
 cushion(.06,.63,.8,.77,.15,.43)
 cushion(.06,1.01,1.20,.78,.48,.105)
 for side in [-1,1]:
  G.path('gondola-lacquer',[(side*.78,.54,.35),(side*.80,.82,.38),(side*.78,.92,.80),(side*.74,1.06,1.17)],.07,12)
  G.path('gondola-brass',[(side*.78,.85,.4),(side*.78,.95,.8),(side*.74,1.10,1.16)],.016,8)
  cushion(side*.76,.72,-.70,.15,.19,.56)
  G.box('gondola-lacquer',(side*.79,.42,-.7),(.19,.34,1.16))
 # Crown and scrollwork outline around the seat, not a solid rectangular block.
 G.path('gondola-lacquer',[(-.75,.65,1.27),(-.80,1.05,1.27),(-.68,1.42,1.27),(-.35,1.5,1.27),(0,1.6,1.27),(.43,1.5,1.27),(.78,1.42,1.27),(.88,1.05,1.27),(.83,.65,1.27)],.055,12)
 G.path('gondola-brass',[(-.65,1.4,1.15),(-.3,1.49,1.15),(.06,1.57,1.15),(.4,1.49,1.15),(.76,1.4,1.15)],.015,8)
 # Stainless ferro: curved six-tooth comb plus the Doge's cap, extruded plate.
 # Local plane is longitudinal; the six fingers project ahead of the curved stem.
 profile=[(-5.11,.52),(-5.29,.78),(-5.37,1.22),(-5.35,1.64),(-5.31,1.94),(-5.42,2.22),(-5.11,2.44),(-4.99,2.48),(-5.04,1.94)]
 for j in range(6):
  yy=1.90-j*.17
  profile.extend([(-4.72,yy),(-4.70,yy-.065),(-5.04,yy-.078)])
 profile.extend([(-5.05,.77),(-5.11,.52)])
 from shapely.geometry import Polygon
 from common import triangles
 poly=Polygon(profile).buffer(0)
 for tr in triangles(poly):
  q=list(tr.exterior.coords)[:-1]
  for xx in [-.036,.036]:face('gondola-chrome',[(xx,yy,zz) for zz,yy in (q if xx<0 else q[::-1])])
 for a,b in zip(profile,profile[1:]):face('gondola-chrome',[(-.036,a[1],a[0]),(.036,a[1],a[0]),(.036,b[1],b[0]),(-.036,b[1],b[0])])
 # Slender lifted stern and hand-carved forcola (asymmetric fork rowlock).
 G.path('gondola-chrome',[(0,.85,4.83),(0,1.10,5.02),(0,1.36,5.12),(0,1.55,5.15)],.035,10)
 G.path('gondola-wood',[(.72,.66,3.1),(.70,1.1,3.1),(.80,1.30,3.04),(.88,1.43,2.91)],.06,10)
 G.path('gondola-wood',[(.7,1.08,3.1),(.54,1.28,3.16),(.54,1.42,3.22)],.055,10)
 G.tube('gondola-wood',(.61,1.26,3.14),(1.39,.48,-.87),.032,12)
 # Oar blade tapers rather than ending in a cylinder.
 G.path('gondola-wood',[(1.39,.48,-.87),(1.47,.4,-1.36)],.043,10)
 face('gondola-wood',[(1.43,.42,-1.12),(1.71,.25,-2.08),(1.47,.24,-2.13),(1.29,.42,-1.15)])
 B.detail=1
 # Buttoned upholstery, piping, nailhead edging, gold scrolls and bow ornaments.
 for xx in [-.46,-.2,.06,.32,.58]:
  for yy in [.87,1.12,1.32]:B.sphere('gondola-brass',G.p(xx,yy,1.086),.022,8,6)
 for side in [-1,1]:
  for t in np.linspace(-.86,.88,73):
   p=hull(t,side);B.sphere('gondola-chrome',G.p(p[0],p[1]-.02,p[2]),.011,6,4)
  for zz in [-2.35,1.9]:
   points=[]
   for a in np.linspace(0,math.pi*3.7,49):
    r=.15*(1-a/(math.pi*4.2));points.append((side*(.74+r*math.cos(a)),.69+r*math.sin(a),zz))
   G.path('gondola-brass',points,.014,6)
 for zz in [-3.05,-3.9]:
  for side in [-1,1]:G.path('gondola-brass',[(side*.1,.65,zz-.3),(side*.25,.72,zz),(side*.12,.75,zz+.25)],.021,8)
 # Coiled mooring rope on the stern deck.
 G.path('rope',[(.3+.19*math.cos(a),.66+.012*a/math.tau,3.6+.19*math.sin(a)) for a in np.linspace(0,math.tau*3.5,100)],.017,6)
 G.text('V',(.06,1.19,1.073),.19,'gondola-brass')
 B.source,B.detail=old_source,old_detail
