"""Circus frontage details, Earth 2022–24. Heights remain mapped estimates.
Existing city cores retained; this module replaces earlier decorative facades.
"""
from common import *
from forum_shops import facade_frame
from sahara_retail import equipment

def glass(F,u,y,w,h):
 F.box('cc-window',(u,y,-.29),(w,h,.08))
 for x in [u-w/2,u,u+w/2]:F.box('cc-metal',(x,y,-.36),(.055,h,.08))
 for yy in [y-h/2,y+h/2]:F.box('cc-metal',(u,yy,-.36),(w,.055,.08))

def frontage(B,ident,p,h):
 motel=ident=='way/364843230';slots=ident=='way/180250495';food=ident=='way/180250447'
 for pp in parts(p):
  cc=list(pp.exterior.coords)
  for edge,(a,b) in enumerate(zip(cc,cc[1:])):
   F,L,nx,nz=facade_frame(B,a,b,pp,.02)
   if L<1:continue
   if motel:
    court=edge in [5,6,7,8]
    F.box('cc-blue' if court else 'cc-white',(L/2,h/2,-.16),(L,h,.12))
    F.box('cc-white',(L/2,h-.05,-.35),(L,.25,.6))
    for y in [.24,3.15]:
     for u in np.arange(2,L-1,4.4):
      if court:
       F.box('cc-door',(u-1,y+1.2,-.27),(.9,2.4,.1))
       for x in [u-1.5,u-.5]:F.box('cc-white',(x,y+1.25,-.32),(.08,2.5,.14))
       F.box('cc-white',(u-1,y+2.46,-.32),(1.08,.08,.14))
       F.tube('cc-metal',(u-.7,y+1,-.35),(u-.7,y+1.35,-.35),.025,6)
       glass(F,u+.72,y+1.5,1.55,1.35)
       F.box('cc-sill',(u+.72,y+.55,-.5),(1.5,.45,.4))
       for x in np.arange(u+.1,u+1.4,.14):F.box('cc-shadow',(x,y+.55,-.71),(.035,.32,.02))
      else:glass(F,u,y+1.9,.62,.5)
    if court:
     F.box('cc-white',(L/2,3.03,-.95),(L,.24,1.9),True)
     F.box('cc-white',(L/2,.13,-.95),(L,.22,1.9),True)
     runs=[(0,2.1),(3.9,L)] if L>35 else [(0,L)]
     for lo,hi in runs:
      for y in [3.28,4.25]:F.box('cc-blue',((lo+hi)/2,y,-1.88),(hi-lo,.075,.07),True)
      for u in np.arange(lo+.1,hi,.18):F.box('cc-blue',(u,3.78,-1.88),(.035,.97,.045))
     for u in np.arange(.3,L,4.4):F.box('cc-blue',(u,1.6,-1.75),(.1,3.1,.1),True)
     if L>35:
      F.stairs(3,-7.7,1.6,3.15,5.8,y=0)
      for side in [2.18,3.82]:
       F.tube('cc-blue',(side,1,-7.7),(side,4.15,-1.9),.045,6)
     # Overhanging upper eave, the gallery below remains open.
     F.box('cc-white',(L/2,5.98,-.95),(L,.12,1.9))
   else:
    front=nx>.7;side=abs(nz)>.7
    F.box('cc-white',(L/2,h/2,-.16),(L,h,.12))
    if slots:
     for y,depth in [(3.8,.75),(4.3,.42),(5.3,.3),(5.85,.45)]:F.box('cc-sill',(L/2,y,-depth/2-.24),(L,.18,depth))
     if front or side:
      for u in np.arange(2,L-1,3.7):glass(F,u,1.8,3.25,3)
      F.box('cc-shadow',(L/2,3.35,-.4),(L,.45,.12))
      for u in np.arange(5,L-2,10):F.text('PLAY   WIN',(u,3.35,-.48),.31,'cc-yellow')
      for u in np.arange(1,L,4.2):
       F.box('cc-white',(u,2,-1.5),(.35,4,.35),True)
       F.box('cc-sill',(u,3.8,-1.5),(.7,.22,.65))
      F.box('cc-flat-roof',(L/2,4.08,-.9),(L,.14,1.8),True)
     if front and L>15:
      F.text('SLOTS A FUN',(L/2,4.8,-.55),1.05,'cc-gold')
      F.box('cc-shadow',(L/2,6.85,-.2),(10,1.7,.24))
      F.text('SLOTS A FUN',(L/2,6.85,-.35),.9,'cc-yellow')
    elif food:
     F.box('cc-brown',(L/2,1,-.21),(L,2,.12))
     if front or side:
      for u in np.arange(2,L-1,2.8):glass(F,u,2.25,2.48,3.4)
      F.box('cc-yellow',(L/2,5.55,-.55),(L,.4,1.2))
     if front:
      F.box('cc-shadow',(L/2,4.8,-.29),(min(L-.3,12),1.1,.18))
      F.text("McDonald's",(L/2,4.8,-.4),min(.95,L/12),'cc-yellow')
      F.box('cc-yellow',(L/2,6.12,-.6),(L,.18,1.6))
    if (front or side) and L>8:
     for dx in [-.65,.65]:
      glass(F,L/2+dx,1.48,1.22,2.64)
      F.tube('cc-metal',(L/2+dx+.4,1,-.42),(L/2+dx+.4,1.9,-.42),.025,6)
 B.planar('cc-flat-roof',p,h+.065)
 equipment(B,p,h+.065)
 if food:
  # Yellow pitched roof occupies the eastern dining volume; service roof stays flat.
  F,L,_,_=facade_frame(B,(882.136,-2163.216),(891.938,-2181.851),p,0)
  for sign in [-1,1]:
   B.upface('cc-yellow',[F.p(L/2+sign*L/2,6.05,-.6),F.p(L/2+sign*L/2,6.05,15),F.p(L/2,7.2,15),F.p(L/2,7.2,-.6)])
 if motel:
  court=Polygon([(846,-2419),(860,-2445),(906,-2444),(917,-2396),(969,-2368),(972,-2350),(950,-2359),(851,-2410)])
  B.planar('cc-asphalt',court.difference(p.buffer(.4)),.06,True)
  pool=box(873,-2423,886,-2414)
  B.planar('cc-white',pool.buffer(1.4),.15,True)
  B.planar('circus_pool',pool,.19)
  for a,b in [((871.4,-2424.4),(887.4,-2424.4)),((887.4,-2424.4),(887.4,-2412.6)),((887.4,-2412.6),(871.4,-2412.6))]:
   length=math.dist(a,b)
   for t in np.linspace(0,1,max(2,int(length/.17))):
    x=a[0]+(b[0]-a[0])*t;z=a[1]+(b[1]-a[1])*t;B.tube('cc-blue',(x,.2,z),(x,1.35,z),.025,4)
   B.tube('cc-blue',(a[0],1.35,a[1]),(b[0],1.35,b[1]),.04,6)
