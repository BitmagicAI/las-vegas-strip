"""St Louis Square: mapped shop footprints, January2026 street and satellite references."""
from common import *
from forum_shops import facade_frame
KEY='stLouisSquareFrontage'
IDS=['way/364845137','way/364845138','way/364845136']
def frame(B):return Frame(B,1717.26,-3616.08,yaw=math.atan2(33.80,17.22),y=0)
def roof(B,F,u0,u1,w0,w1,y=4.3,rise=1.6):
 d=min((w1-w0)/2,(u1-u0)/2);a=(u0+d,y+rise,(w0+w1)/2);b=(u1-d,y+rise,(w0+w1)/2)
 for face in [[(u0,y,w0),(u1,y,w0),b,a],[(u1,y,w0),(u1,y,w1),b],[(u1,y,w1),(u0,y,w1),a,b],[(u0,y,w1),(u0,y,w0),a]]:B.upface('sls-red-roof-paint',[F.p(*p) for p in face])
 # Raised standing seams clipped to each hip plane, not a tile texture.
 for u in np.arange(u0+.25,u1,.55):
  u=float(u);h=rise*min(1,(u-u0)/max(d,.01),(u1-u)/max(d,.01));inset=h/rise*(w1-w0)/2
  for wa,wb in [(w0,w0+inset),(w1,w1-inset)]:F.tube('sls-roof-seam-paint',(u,y+.018,wa),(u,y+h+.018,wb),.016,4)
 for w in [w0,w1]:F.box('sls-white-paint',((u0+u1)/2,y-.08,w),(u1-u0,.19,.15))
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/st-louis-square';B.detail=0;F=frame(B);ps=[footprint(i) for i in IDS];allp=unary_union(ps)
 for index,p in enumerate(ps):
  B.shell(p,.12,4.22,'sls-brick' if index==1 else 'sls-ivory-stucco',roof=False)
  B.planar('sls-flat-roof-paint',p,4.24)
  for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
   G,L,nx,nz=facade_frame(B,a,b,p,.035)
   G.box('sls-brick',(L/2,.7,-.025),(L,1.15,.08))
   for yy,h,dep in [(3.78,.22,.16),(4.08,.16,.29),(4.22,.10,.37)]:G.box('sls-white-paint',(L/2,yy,-dep/2),(L,h,dep))
   if L<3:continue
   count=max(1,round(L/(6.5 if index==1 else 3.6)));bay=L/count
   for j in range(count):
    u=bay*(j+.5);width=min(4.3 if index==1 else 2.7,bay-.75)
    G.box('sls-white-paint',(u,2.08,-.12),(width+.18,2.65,.17))
    G.box('sls-glass',(u,2.08,-.23),(width,2.45,.04))
    for dx in [-width/2,0,width/2]:G.box('sls-frame-paint',(u+dx,2.08,-.27),(.045,2.45,.04))
    for yy in [1.5,2.7]:G.box('sls-frame-paint',(u,yy,-.27),(width,.045,.04))
    # Fine diamond security grille seen on the western windows.
    if nx<-.5 or nz>.5:
     for q in np.arange(-2.45,width,.36):
      q=float(q);xa=max(0,q);xb=min(width,q+2.45)
      if xb>xa:G.tube('sls-grille-paint',(u-width/2+xa,.86+xa-q,-.30),(u-width/2+xb,.86+xb-q,-.30),.009,4)
     for q in np.arange(0,width+2.45,.36):
      q=float(q);xa=max(0,q-2.45);xb=min(width,q)
      if xb>xa:G.tube('sls-grille-paint',(u-width/2+xa,.86+q-xa,-.31),(u-width/2+xb,.86+q-xb,-.31),.009,4)
    if index==1:
     # Shallow arched transom atop the wider brick pavilion windows.
     arc=[(u+width/2*math.cos(t),3.31+.43*math.sin(t),-.25) for t in np.linspace(0,math.pi,25)]
     B.face('sls-glass',[G.p(*q) for q in arc])
     for aa,bb in zip(arc,arc[1:]):G.tube('sls-white-paint',aa,bb,.045,6)
     G.box('sls-white-paint',(u,3.31,-.29),(width,.07,.08))
    if j==count//2 and index!=1:
     G.box('sls-frame-paint',(u,1.27,-.32),(1.06,2.28,.05));G.box('sls-glass',(u,1.28,-.36),(.94,2.12,.025));G.box('sls-handle-paint',(u+.32,1.25,-.40),(.035,.35,.04))
    if (nx<-.5 or nz>.6) and index==0:
     B.upface('sls-awning-fabric',[G.p(u-width/2-.12,3.5,-.35),G.p(u+width/2+.12,3.5,-.35),G.p(u+width/2+.12,3.07,-1.05),G.p(u-width/2-.12,3.07,-1.05)])
     G.box('sls-awning-fabric',(u,2.99,-1.05),(width+.24,.17,.04))
     for dx in np.arange(-width/2,width/2,.25):G.tube('sls-awning-stripe-paint',(u+float(dx),3.51,-.35),(u+float(dx),3.08,-1.05),.012,4)
   if nx<-.5 and L>10 and index==0:
    mid=L/2;B.face('sls-white-paint',[G.p(mid-2.5,4.24,-.22),G.p(mid+2.5,4.24,-.22),G.p(mid,5.2,-.22)])
    for aa,bb in [((mid-2.55,4.23,-.3),(mid,5.25,-.3)),((mid,5.25,-.3),(mid+2.55,4.23,-.3))]:G.tube('sls-cornice-paint',aa,bb,.09,4)
 # Distinct roof zones follow the satellite plan; no bounding rectangle over the whole parcel.
 roof(B,F,22.5,38.2,-.25,15.05)
 roof(B,F,-.25,7.5,-.25,6.0,rise=1.2)
 roof(B,F,-10.5,-3.1,9.55,20.0,rise=1.35)
 roof(B,F,-3.1,1.3,14.5,20.0,rise=.9)
 roof(B,F,9.35,15,25.15,32.95,rise=1.05)
 # Roof equipment confined to the white flat sections.
 for u,w in [(14,6),(18,8),(-5,27),(25,27),(33,26)]:
  F.box('sls-service-paint',(u,4.62,w),(1.4,.7,1.1));F.box('sls-vent-paint',(u,4.98,w),(1.2,.03,.9))
 # Plaza in the gaps; slab extends to the street-side walkway, not over existing roads.
 site=F.poly([(-11,8),(-1,-2),(39,-2),(39,34),(-11,34)])
 plaza=site.difference(allp);B.planar('sls-plaza-concrete',plaza,.12,True)
 # Permeable pergola roofs bridge the two retail wings; high enough for real pedestrian clearance.
 for u0,u1,w0,w1 in [(7.8,22.0,15.4,19.7),(5.7,9.1,20.2,31.8)]:
  for u in [u0,u1]:
   for w in [w0,w1]:F.box('sls-white-paint',(u,1.95,w),(.24,3.66,.24),True);F.box('sls-white-paint',(u,.35,w),(.4,.46,.4),True)
  for w in [w0,w1]:F.box('sls-white-paint',((u0+u1)/2,3.86,w),(u1-u0+.5,.26,.2))
  for u in np.arange(u0-.12,u1+.2,.45):F.box('sls-white-paint',(float(u),3.99,(w0+w1)/2),(.09,.18,w1-w0+.65))
 samples=[]
 for u in np.arange(-9,38,1.2):
  for w in np.arange(-1,33,1.2):
   q=F.p(float(u),.12,float(w))
   if plaza.buffer(-.4).contains(Point(q[0],q[2])) and not allp.buffer(1.2).contains(Point(q[0],q[2])) and all(math.hypot(u-a,w-b)>.65 for a,b in [(7.8,15.4),(22,15.4),(7.8,19.7),(22,19.7),(5.7,20.2),(9.1,20.2),(5.7,31.8),(9.1,31.8)]):samples.append(q)
 Path('build/city-exteriors/st-louis-square-frontage-samples.json').write_text(json.dumps(samples))
 return dict(key=KEY,name='St Louis Square frontage',center=[1740,0,-3620],bounds=[1713,-3654,1767,-3588],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
