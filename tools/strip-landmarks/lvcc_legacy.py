"""Legacy LVCC halls; mapped plan/Earth2024 roofs and operator2026 arrival.
Heights estimated. Renovation envelope fit is provisional, not surveyed.
"""
from common import *
from forum_shops import facade_frame
KEY='lvccLegacy';IDS=['way/27925846']
def roofy(x,z):
 base=24 if z>-1463 else (14 if z<-1801 else 16)
 return base+11*math.exp(-((z+1695)/52)**2-((x-1850)/45)**2)
def exterior(B):
 B.property=KEY+'-exterior';B.source='lvcc-legacy';B.detail=0
 p=footprint(IDS[0]).simplify(.4);B.planar('lvw-paving',p,.24,True)
 # Divide at actual hall boundaries so roof elevations never stretch across tiers.
 zones=[p.intersection(box(1500,-2100,2450,-1801)),p.intersection(box(1500,-1801,2450,-1463)),p.intersection(box(1500,-1463,2450,-1300))]
 for zone in zones:
  for pp in parts(zone):
   ps=list(pp.exterior.coords)
   for a,b in zip(ps,ps[1:]):
    F,L,nx,nz=facade_frame(B,a,b,pp,0)
    if L<.2:continue
    mid=LineString([a,b]).interpolate(.5,normalized=True)
    shared=p.contains(Point(mid.x+nx*.1,mid.y+nz*.1))
    public=nx<-.45 and not shared
    N=max(1,math.ceil(L/3))
    for j in range(N):
     t0=j/N;t1=(j+1)/N;ax=a[0]+(b[0]-a[0])*t0;az=a[1]+(b[1]-a[1])*t0;bx=a[0]+(b[0]-a[0])*t1;bz=a[1]+(b[1]-a[1])*t1
     # Clamp to this hall's side of elevation boundary.
     ha=roofy(ax-nx*.05,az-nz*.05);hb=roofy(bx-nx*.05,bz-nz*.05)
     lo=roofy(mid.x+nx*.1,mid.y+nz*.1) if shared else .24
     if lo<min(ha,hb)-.55:B.face('lvw-glass' if public else 'lvw-panel',[(ax,lo,az),(bx,lo,bz),(bx,hb-.55,bz),(ax,ha-.55,az)],True)
     if public:
      B.tube('lvw-frame',(ax+nx*.08,.3,az+nz*.08),(ax+nx*.08,ha-.55,az+nz*.08),.055,6)
      for y in np.arange(3,min(ha,hb)-.5,3):B.tube('lvw-frame',(ax+nx*.09,y,az+nz*.09),(bx+nx*.09,y,bz+nz*.09),.045,6)
     elif not shared:B.tube('lvw-joint',(ax+nx*.02,.4,az+nz*.02),(ax+nx*.02,ha-.7,az+nz*.02),.023,4)
     B.face('lvw-white',[(ax,ha-.55,az),(bx,hb-.55,bz),(bx,hb,bz),(ax,ha,az)])
    if public and L>25:
     for x in np.arange(3,L-2,6):
      F.box('lvw-doorframe',(x,1.65,-.15),(2.7,3.2,.12));F.box('lvw-door',(x,1.65,-.23),(2.5,3,.08));F.box('lvw-frame',(x,1.65,-.29),(.055,3,.05))
     if L>75:F.text('LAS VEGAS CONVENTION CENTER',(L/2,8,-.35),1.25,'lvw-letter')
    elif not shared and L>35:
     for x in np.arange(8,L-4,16):
      F.box('lvw-loading',(x,3,-.1),(4.8,5.7,.1));F.box('lvw-frame',(x,6,-.3),(5.3,.2,.6))
      for y in np.arange(.6,5.7,.45):F.box('lvw-joint',(x,y,-.2),(4.6,.045,.04))
   x0,z0,x1,z1=pp.bounds
   for x in np.arange(x0,x1,7):
    for z in np.arange(z0,z1,7):
     for piece in parts(pp.intersection(box(x,z,min(x+7,x1),min(z+7,z1))).difference(box(1844,-1753,1855,-1633))):
      for tri in triangles(piece):
       coords=list(tri.exterior.coords)[:-1]
       # Use an interior point for tier classification at cut boundaries.
       cy=piece.representative_point().y;base=24 if cy>-1463 else(14 if cy<-1801 else 16)
       pts=[(xx,base+11*math.exp(-((zz+1695)/52)**2-((xx-1850)/45)**2),zz) for xx,zz in coords]
       B.upface('lvw-roof',pts,True)
   for x in np.arange(x0+9,x1-5,22):
    for z in np.arange(z0+9,z1-5,25):
     if pp.contains(box(x-2,z-1.5,x+2,z+1.5)) and x>1900:
      y=roofy(x,z);B.box('lvw-service',(x,y+.65,z),(3.4,1.3,2.3));B.box('lvw-white',(x,y+1.4,z),(3.6,.15,2.5))
      B.box('lvw-frame',(x+3,y+.3,z),(2.8,.6,.7))
 # Continuous ribbon canopy: the ribs sit within its soffit rather than
 # projecting unsupported beyond the glass. Segment the curved fascia at 2 m.
 for z in np.arange(-1753,-1633,2):
  za=float(z);zb=za+2;ha=roofy(1855,za);hb=roofy(1855,zb)
  B.upface('lvw-white',[(1844,ha,za),(1855,ha,za),(1855,hb,zb),(1844,hb,zb)],True)
  B.face('lvw-white',[(1844,ha-.65,za),(1844,hb-.65,zb),(1855,hb-.65,zb),(1855,ha-.65,za)])
  B.face('lvw-white',[(1844,ha-.65,za),(1844,ha,za),(1844,hb,zb),(1844,hb-.65,zb)])
 for z in (-1753,-1633):
  h=roofy(1855,z)
  B.face('lvw-white',[(1844,h-.65,z),(1855,h-.65,z),(1855,h,z),(1844,h,z)])
 # Canopy soffit and curved ribs at the central west-facing grand lobby.
 for z in np.arange(-1745,-1640,6):
  h=roofy(1852,z);B.box('lvw-white',(1850,h-.8,z),(7,.3,.22))
  B.tube('lvw-white',(1851,.24,z),(1851,h-.6,z),.17,8)
 return dict(key=KEY,name='LVCC North Central and South halls',center=[1970,0,-1655],bounds=list(p.bounds),structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],views={})
