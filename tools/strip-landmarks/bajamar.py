"""Bajamar1615: mapped angled plan, August2024 Street View facade."""
from common import *
from forum_shops import facade_frame
KEY='bajamar'
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/frontage';B.detail=0;W=Frame(B,0,0,y=0)
 p=footprint('way/364845146');B.shell(p,.18,3.65,'bj-teal-paint',roof=False);B.planar('bj-roof-paint',p,3.58,True)
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  G,L,nx,nz=facade_frame(B,a,b,p,.035)
  G.box('bj-teal-paint',(L/2,3.65,-.04),(L,.18,.19))
  glazed=(nz<-.7 or (nx<-.7 and L<9))
  if glazed:
   G.box('bj-blue-paint',(L/2,.55,-.08),(L,.7,.12))
   G.box('bj-glass',(L/2,1.92,-.11),(L-.16,2.02,.09))
   # Continuous silver framing; fixed opaque backing retains exterior-only ownership.
   count=max(3,round(L/1.5))
   for j in range(count+1):G.box('bj-aluminum-paint',(L*j/count,1.65,-.18),(.05,2.9,.07))
   for y in [.22,.9,2.94]:G.box('bj-aluminum-paint',(L/2,y,-.18),(L,.055,.07))
   # Quarter-round fabric awning, with underside and closed ends.
   profile=[(3.08,-.72)]+[(3.08+.51*math.sin(t),-.21-.51*math.cos(t)) for t in np.linspace(0,math.pi/2,13)]+[(3.59,.02),(3.05,.02)]
   for (y,w),(yy,ww) in zip(profile,profile[1:]+profile[:1]):B.face('bj-awning-paint',[G.p(0,y,w),G.p(L,y,w),G.p(L,yy,ww),G.p(0,yy,ww)])
   for u in [0,L]:B.face('bj-awning-paint',[G.p(u,y,w) for y,w in profile])
   G.box('bj-aluminum-paint',(L/2,3.05,-.72),(L,.06,.055))
   if L<9:
    G.text('BAJAMAR',(L/2,3.27,-.755),.53,'bj-white-letter')
   else:
    u=L*.53;G.box('bj-aluminum-paint',(u,1.58,-.25),(1.17,2.72,.07));G.box('bj-glass',(u,1.53,-.3),(1.02,2.43,.04));G.tube('bj-aluminum-paint',(u-.35,1.1,-.34),(u-.35,1.68,-.34),.023,8);G.text('1615',(u,2.81,-.34),.21,'bj-white-letter')
    # Sign pole and rounded triangular roadside sign, based on observed silhouette.
    G.lathe('bj-blue-paint',L*.52,-3.0,[(.18,.48),(1.25,.48)],24);G.tube('bj-teal-paint',(L*.52,1.25,-3),(L*.52,6.45,-3),.13,16)
    px,py,pz=G.p(L*.52,0,-3);H=Frame(B,px,pz,yaw=G.yaw+math.pi/2,y=0)
    def signpoint(x,y,w):return H.p(x-L*.52,y,w+3)
    sign=[(-.75,6.3),(-1,6.65),(-.95,7.1),(-.55,7.9),(0,8.45),(.55,7.9),(.95,7.1),(1,6.65),(.75,6.3)]
    for w in [-3.12,-2.88]:B.face('bj-sign-blue',[signpoint(L*.52+x,y,w) for x,y in sign])
    for i in range(len(sign)):
     x,y=sign[i];xx,yy=sign[(i+1)%len(sign)];B.face('bj-teal-paint',[signpoint(L*.52+x,y,-3.12),signpoint(L*.52+xx,yy,-3.12),signpoint(L*.52+xx,yy,-2.88),signpoint(L*.52+x,y,-2.88)])
    H.path('bj-white-letter',[(x*.91,7.25+(y-7.25)*.91,-.14) for x,y in sign+sign[:1]],.035,8);H.text('BAJAMAR',(0,7.1,-.16),.31,'bj-white-letter');H.text('SEAFOOD',(0,6.68,-.16),.16,'bj-white-letter')
  else:
   G.box('bj-teal-paint',(L/2,.45,-.08),(L,.5,.12))
   if L>10:
    G.box('bj-aluminum-paint',(L*.72,1.35,-.12),(1.05,2.3,.09));G.box('bj-vent',(L*.25,2.3,-.1),(1.4,.6,.15))
 for x,z in [(1907,-3978),(1900,-3981)]:W.box('bj-service',(x,3.98,z),(1.2,.6,1.0))
 S=Frame(B,1899,-3981,yaw=math.atan2(2.86,5.778),y=0)
 S.box('bj-white-paint',(0,4.17,0),(2.7,.82,1.3));S.text('BAJAMAR',(0,4.18,-.67),.39,'bj-sign-blue');S.text('BAJAMAR',(0,4.18,.67),.39,'bj-sign-blue',back=True)
 site=p.buffer(1.3,join_style=2).difference(p);B.planar('bj-paving',site,.18,True)
 samples=[]
 for x in np.arange(1894,1916,.55):
  for z in np.arange(-3987,-3969,.55):
   if site.buffer(-.36).covers(Point(x,z)):samples.append([float(x),.18,float(z)])
 Path('build/city-exteriors/bajamar-samples.json').write_text(json.dumps(samples))
 return dict(key=KEY,name='Bajamar Seafood and Tacos',center=[1905,0,-3978],bounds=[1893,-3989,1917,-3969],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
