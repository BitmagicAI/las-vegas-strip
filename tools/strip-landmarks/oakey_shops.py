"""Oakey retail row: January 2026 Street View, mapped irregular plan retained."""
from common import *
from forum_shops import facade_frame
KEY='oakeyShops'
def elevation(z):return .55 if z>=-3953 else .18 if z<=-3961 else .18+(z+3961)/8*.37
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/shops';B.detail=0;W=Frame(B,0,0,y=0)
 p=footprint('way/316303731');B.shell(p,.18,3.9,'os-gray-stucco',roof=False);B.planar('os-roof-paint',p,3.72,True)
 fronts=[]
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  G,L,nx,nz=facade_frame(B,a,b,p,.035)
  G.box('os-coping-paint',(L/2,3.92,0),(L,.1,.22))
  if nx>.8 and L>6:
   fronts.append((G,L))
   for u in np.arange(.8,L-.3,1.4):
    u=float(u);z=G.p(u,0,0)[2];floor=elevation(z);mid=(floor+.2+2.95)/2;h=2.95-floor-.2
    G.box('os-glass',(u,mid,-.09),(1.31,h,.1))
    for dx in [-.67,.67]:G.box('os-black-paint',(u+dx,mid,-.17),(.045,h+.1,.07))
    for y in [floor+.17,2.94]:G.box('os-black-paint',(u,y,-.17),(1.4,.055,.07))
   G.box('os-black-paint',(L/2,3.02,-.4),(L,.14,.85))
   # Physical shallow fascia ribs on the north tattoo shop, matched to observed dark corrugated panel.
   for u in np.arange(.12,L,.28):
    u=float(u);z=G.p(u,0,0)[2]
    if -3987<z<-3972:G.box('os-dark-paint',(u,3.5,-.07),(.08,.84,.13))
   # Shared walk follows the surveyed frontage. South restaurant terrace falls to grade in north parking area.
   count=math.ceil(L/1.2)
   for j in range(count):
    u0=L*j/count;u1=L*(j+1)/count;y0=elevation(G.p(u0,0,0)[2]);y1=elevation(G.p(u1,0,0)[2])
    B.upface('os-paving',[G.p(u0,y0,-.02),G.p(u1,y1,-.02),G.p(u1,y1,-4),G.p(u0,y0,-4)],True)
    B.face('os-plinth',[G.p(u0,.12,-4),G.p(u1,.12,-4),G.p(u1,y1,-4),G.p(u0,y0,-4)],True)
    z=(G.p(u0,0,0)[2]+G.p(u1,0,0)[2])/2
    if z>-3959:
     for off in [.52,1.02]:G.tube('os-black-paint',(u0,y0+off,-3.9),(u1,y1+off,-3.9),.025,8)
     G.tube('os-black-paint',(u0,y0,-3.9),(u0,y0+1.02,-3.9),.03,8)
     B.face('os-rail-collision',[G.p(u0,y0,-3.9),G.p(u1,y1,-3.9),G.p(u1,y1+1,-3.9),G.p(u0,y0+1,-3.9)],True)
   # Door handles identify paired entries without punching false interior openings.
   for u in np.arange(3,L-1,7):
    z=G.p(float(u),0,0)[2]
    for dx in [-.2,.2]:G.box('os-metal-paint',(float(u)+dx,elevation(z)+1.2,-.23),(.035,.45,.08))
  elif nz>.7 and L>3 and a[1]<-3980:
   # Glazed return of the projecting northern unit, visible from the Strip.
   for u in np.arange(.7,L-.2,1.3):
    G.box('os-glass',(float(u),1.65,-.09),(1.2,2.5,.1))
    G.box('os-black-paint',(float(u)+.62,1.65,-.17),(.045,2.6,.07))
   G.box('os-black-paint',(L/2,3.02,-.4),(L,.14,.85))
  elif L>8:
   G.box('os-service-paint',(L*.55,1.4,-.06),(1.05,2.4,.12));G.box('os-vent',(L*.25,2.6,-.08),(1.1,.5,.15))
 # Miter the two adjacent angled sidewalk strips; do not leave an open wedge at their joint.
 for i,(A,la) in enumerate(fronts):
  for C,lc in fronts[i+1:]:
   for ua in [0,la]:
    for uc in [0,lc]:
     pa=A.p(ua,0,0);pc=C.p(uc,0,0)
     if math.hypot(pa[0]-pc[0],pa[2]-pc[2])<.2:
      qa=A.p(ua,0,-4);qc=C.p(uc,0,-4)
      join=Polygon([(pa[0],pa[2]),(qa[0],qa[2]),(qc[0],qc[2]),(pc[0],pc[2])]).buffer(0)
      for poly in parts(join):
       for tri in triangles(poly):B.upface('os-paving',[(x,elevation(z),z) for x,z in list(tri.exterior.coords)[:-1]],True)
      B.face('os-plinth',[(qa[0],.12,qa[2]),(qc[0],.12,qc[2]),(qc[0],elevation(qc[2]),qc[2]),(qa[0],elevation(qa[2]),qa[2])],True)
      if pa[2]>-3959:
       for h in [.52,1.02]:B.tube('os-black-paint',(qa[0],elevation(qa[2])+h,qa[2]),(qc[0],elevation(qc[2])+h,qc[2]),.025,8)
 # Locate signs and restaurant canopy on the actual angled east edge rather than a bounding box.
 def at(z):
  for G,L in fronts:
   za=G.p(0,0,0)[2];zb=G.p(L,0,0)[2]
   if min(za,zb)<=z<=max(za,zb):return G,(z-za)/(zb-za)*L
  raise ValueError(z)
 for z,title,size,mat in [(-3937,'AREPAS',.65,'os-red-letter'),(-3951,'ART OF FLAVORS',.35,'os-dark-letter'),(-3966,'X.O SMOKE',.52,'os-red-letter'),(-3979,'TATTOO',.58,'os-red-letter'),(-3997,'CANNABIS',.48,'os-green-letter')]:
  G,u=at(z);G.text(title,(u,3.31,-.17),size,mat)
 G,u=at(-3951);G.text('Gelato & Sweets',(u,3.03,-.47),.31,'os-white-letter')
 G,u=at(-3937);G.text('VIVA LAS',(u,3.74,-.17),.22,'os-dark-letter')
 # Black fabric restaurant awning with real slope and scalloped valance. Patio remains beside through walkway.
 G,u=at(-3937)
 B.face('os-awning-paint',[G.p(u-5.2,2.99,-.1),G.p(u+5.2,2.99,-.1),G.p(u+5.2,2.65,-2.1),G.p(u-5.2,2.65,-2.1)])
 G.box('os-awning-paint',(u,2.56,-2.1),(10.4,.18,.06))
 for xx in np.linspace(u-5.1,u+5.1,44):G.tube('os-awning-paint',(float(xx),2.49,-2.07),(float(xx),2.49,-2.13),.12,8)
 for xx in [u-5.15,u+5.15]:G.box('os-black-paint',(xx,1.59,-2.05),(.07,2.08,.07),True)
 for xx in np.linspace(u-5.1,u+5.1,28):G.tube('os-black-paint',(float(xx),.55,-2.15),(float(xx),1.55,-2.15),.018,6)
 for yy in [.63,1.55]:G.tube('os-black-paint',(u-5.2,yy,-2.15),(u+5.2,yy,-2.15),.03,8)
 B.face('os-rail-collision',[G.p(u-5.2,.55,-2.15),G.p(u+5.2,.55,-2.15),G.p(u+5.2,1.55,-2.15),G.p(u-5.2,1.55,-2.15)],True)
 for xx in [u-3,u,u+3]:
  G.box('os-dark-paint',(xx,1.28,-1.1),(.85,.06,.65));G.tube('os-black-paint',(xx,.55,-1.1),(xx,1.28,-1.1),.035,8)
  for dx in [-.65,.65]:G.box('os-black-paint',(xx+dx,.98,-1.1),(.38,.045,.4));G.box('os-black-paint',(xx+dx,1.22,-.91),(.38,.45,.035))
 # White projecting end fascia and tall dark vertical blade observed on the north tenant.
 G,u=at(-3997);G.box('os-white-paint',(u,3.5,-.48),(12,.9,.55));G.text('CANNABIS',(u,3.3,-.8),.48,'os-green-letter')
 G.box('os-dark-paint',(u-6.1,3.35,-.2),(.3,3.7,.45),True)
 for yy in [3.42]:
  G.box('os-green-paint',(u+4.4,yy,-.8),(.55,.6,.07));G.box('os-green-paint',(u+4.4,yy,-.8),(1.1,.24,.08))
 # Compact service roof volumes; exact service equipment layouts remain unverified.
 for z in [-3937,-3954,-3975,-3997]:
  x=1830+(abs(z)-3930)*.06;W.box('os-service-paint',(x,4.02,z),(1.5,.6,1.8))
 apron=Polygon([(1837,-3930),(1843,-3930),(1850,-3980),(1861,-4008),(1853,-4007),(1840,-3980)]).difference(p)
 B.planar('os-asphalt',apron,.15,True)
 # South ramp joins the raised walk from the public corner.
 # Rails retain collision without adding a solid visual sheet between the bars.
 B.groups={k:g for k,g in B.groups.items() if g['material']!='os-rail-collision'}
 # Sample every facade approach, excluding patio footprint and railing.
 samples=[]
 for G,L in fronts:
  for u in np.arange(.6,L-.3,.9):
   z=G.p(float(u),0,0)[2];x,y,z=G.p(float(u),elevation(z),-3.1);samples.append([x,y,z])
 Path('build/city-exteriors/oakey-shops-samples.json').write_text(json.dumps(samples))
 return dict(key=KEY,name='Oakey mixed storefronts',center=[1840,0,-3969],bounds=[1821,-4009,1862,-3928],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
