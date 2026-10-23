"""Luv-It: August2024 south facade and photographed east walk-up window."""
from common import *
from forum_shops import facade_frame
KEY='luvIt'
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/frontage';B.detail=0;W=Frame(B,0,0,y=0)
 p=footprint('way/364845149');B.shell(p,.18,3.25,'li-blue-paint',roof=False);B.planar('li-roof-paint',p,3.26,True)
 south=None
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  G,L,nx,nz=facade_frame(B,a,b,p,.035)
  for y in np.arange(.4,3.3,.24):G.box('li-blue-shadow-paint',(L/2,float(y),-.018),(L,.018,.025))
  G.box('li-white-paint',(L/2,3.22,-.03),(L,.14,.17))
  if nz>.9:
   south=G
   for u in [L*.18,L*.82]:
    G.box('li-white-paint',(u,1.53,-.09),(1.27,1.9,.14));G.box('li-glass',(u,1.53,-.18),(1.1,1.72,.06))
    for xx in np.linspace(u-.52,u+.52,7):G.box('li-white-paint',(float(xx),1.53,-.24),(.022,1.7,.025))
    G.box('li-white-paint',(u,1.54,-.25),(1.1,.03,.025))
   u=L/2;G.box('li-white-paint',(u,1.5,-.1),(1.5,2.65,.16));G.box('li-door-paint',(u,1.48,-.2),(1.25,2.45,.08));G.text('505',(u,2.35,-.26),.18,'li-dark-letter')
   G.path('li-white-paint',[(u-.9,2.85,-.15),(u,3.22,-.15),(u+.9,2.85,-.15)],.06,8)
   G.box('li-white-paint',(L/2,3.27,-.65),(L+.22,.16,1.3))
   for j in range(4):G.box('li-white-paint',(L*j/3,1.5,-1.2),(.17,2.65,.17),True)
   # Shallow segmental arch fascia; actual open underside, not a solid blocking beam.
   for j in range(3):
    lo=L*j/3;hi=L*(j+1)/3
    for aa,bb in zip(np.linspace(lo,hi,17),np.linspace(lo,hi,17)[1:]):
     ya=2.66+.32*math.sin((aa-lo)/(hi-lo)*math.pi);yb=2.66+.32*math.sin((bb-lo)/(hi-lo)*math.pi)
     for w in [-1.27,-1.13]:B.face('li-white-paint',[G.p(float(aa),ya,w),G.p(float(bb),yb,w),G.p(float(bb),3.33,w),G.p(float(aa),3.33,w)])
     B.face('li-white-paint',[G.p(float(aa),ya,-1.27),G.p(float(aa),ya,-1.13),G.p(float(bb),yb,-1.13),G.p(float(bb),yb,-1.27)])
   G.box('li-white-paint',(L/2,3.8,-.62),(L+.12,.95,1.3))
   for u,w in [(L*.2,L*.36),(L*.8,L*.36)]:
    G.box('li-sign-frame',(u,3.9,-1.34),(w,1.07,.13));G.box('li-white-paint',(u,3.9,-1.42),(w-.12,.95,.04))
   G.text('Luv-it',(L*.8,3.55,-1.46),.92,'li-red-letter');G.text('FROZEN',(L*.2,4.05,-1.46),.45,'li-red-letter');G.text('CUSTARD',(L*.2,3.62,-1.46),.45,'li-red-letter')
   G.box('li-sign-frame',(L/2,3.9,-1.34),(1.1,1.07,.13));G.box('li-white-paint',(L/2,3.9,-1.42),(.96,.93,.04))
   # Original geometric cone icon; does not reuse third-party pixels.
   B.face('li-cone-paint',[G.p(L/2-.24,3.97,-1.46),G.p(L/2+.24,3.97,-1.46),G.p(L/2,3.47,-1.46)])
   for yy,rr in [(4,.24),(4.17,.18),(4.28,.08)]:G.tube('li-cream-paint',(L/2,yy,-1.47),(L/2,yy,-1.51),rr,20)
  elif nx>.9:
   u=L-2.5
   G.box('li-white-paint',(u,3.3,-.62),(4.9,.16,1.3));G.box('li-white-paint',(u,3.83,-1.2),(4.9,.95,.17))
   G.text('Luv-it FROZEN CUSTARD',(u,3.85,-1.32),.34,'li-red-letter')
   for xx in [u-2.4,u+2.4]:G.box('li-white-paint',(xx,1.5,-1.2),(.17,2.65,.17),True)
   G.box('li-white-paint',(u,1.65,-.13),(3.4,1.5,.16));G.box('li-glass',(u,1.65,-.23),(3.2,1.3,.06));G.box('li-white-paint',(u,1.0,-.4),(3.5,.1,.7))
   for xx in [u-.8,u+.8]:G.box('li-white-paint',(xx,1.65,-.28),(.05,1.35,.05))
   G.box('li-white-paint',(u,2.67,-.18),(3.5,.53,.12));G.text('SUNDAES   SHAKES   CONES',(u,2.73,-.27),.18,'li-red-letter');G.text('WALK UP WINDOW',(u,2.52,-.27),.13,'li-dark-letter')
  elif nz<-.9:G.box('li-door-paint',(L*.5,1.38,-.07),(1.1,2.4,.12))
 site=unary_union([p.buffer(1.6,join_style=2),box(1925,-3945,1937,-3939),box(1933,-3950,1937,-3942)]).difference(p);B.planar('li-paving',site,.18,True)
 W.box('li-service',(1929,3.63,-3954),(1.5,.7,1.3))
 samples=[]
 for x in np.arange(1924,1936,.6):
  for z in np.arange(-3961,-3940,.6):
   if site.buffer(-.4).covers(Point(x,z)) and z<-3943.7 and not(x>1932 and z>-3948):samples.append([float(x),.18,float(z)])
 Path('build/city-exteriors/luv-it-samples.json').write_text(json.dumps(samples))
 return dict(key=KEY,name='Luv-It Frozen Custard',center=[1930,0,-3951],bounds=[1923,-3962,1937,-3940],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
