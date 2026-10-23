"""South Central Area Command: public exterior only. Mapped footprint, photoestimated roof heights."""
from common import *
from forum_shops import facade_frame
KEY='southCentralPolice'
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/police';B.detail=0;W=Frame(B,0,0,y=0);p=footprint('way/364846560')
 B.shell(p,.24,3.6,'scp-brick',roof=False);B.shell(p,3.6,5.9,'scp-stucco',roof=False);B.planar('scp-flat-roof',p,5.9,True)
 # Roof rectangles follow the north and south cross wings; intersecting roofs are clipped.
 roofs=[(-90,3474,-61,3494,7.8),(-78,3510,-64,3537,7.7),(-83,3474,-79,3530,8.1),(-74,3497,-68,3507,7.1)]
 claimed=Polygon()
 for x0,z0,x1,z1,peak in roofs:
  area=box(x0,z0,x1,z1).intersection(p).difference(claimed);mid=(z0+z1)/2
  for half in [box(x0,z0,x1,mid),box(x0,mid,x1,z1)]:
   part=area.intersection(half)
   for poly in parts(part):
    for tri in triangles(poly):B.upface('scp-metal-roof',[(x,5.95+(peak-5.95)*(1-abs(z-mid)/((z1-z0)/2)),z) for x,z in list(tri.exterior.coords)[:-1]])
  # Fit gables to the actual tilted footprint edge rather than an axis-aligned box.
  for aa,bb in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
   for side in [x0,x1]:
    if max(abs(aa[0]-side),abs(bb[0]-side))>.8:continue
    lo=max(min(aa[1],bb[1]),z0);hi=min(max(aa[1],bb[1]),z1)
    if hi-lo<1:continue
    def edge(z):
     t=(z-aa[1])/(bb[1]-aa[1]);return aa[0]+t*(bb[0]-aa[0])+(.015 if side==x1 else -.015)
    zs=[lo]+([mid] if lo<mid<hi else [])+[hi]
    for zA,zB in zip(zs,zs[1:]):
     yA=5.95+(peak-5.95)*(1-abs(zA-mid)/((z1-z0)/2));yB=5.95+(peak-5.95)*(1-abs(zB-mid)/((z1-z0)/2))
     pts=[(edge(zA),5.89,zA),(edge(zB),5.89,zB),(edge(zB),yB,zB),(edge(zA),yA,zA)]
     B.face('scp-stucco',pts[::-1] if side==x1 else pts)
  for x in np.arange(x0+.15,x1,.55):
   for zA,zB in [(z0,mid),(mid,z1)]:
    if area.covers(Point(x,(zA+zB)/2)):
     W.tube('scp-roof-seam',(x,5.98+(peak-5.95)*(1-abs(zA-mid)/((z1-z0)/2)),zA),(x,5.98+(peak-5.95)*(1-abs(zB-mid)/((z1-z0)/2)),zB),.025,4)
  claimed=claimed.union(area)
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  G,L,_,_=facade_frame(B,a,b,p,.025)
  G.box('scp-coping',(L/2,5.92,-.04),(L,.12,.15))
  for u in np.arange(.12,L,.22):G.box('scp-brick-rib',(u,1.9,-.035),(.08,3.3,.06))
  G.box('scp-sill',(L/2,3.64,-.045),(L,.1,.1))
  if L>7:
   for center in np.arange(3,L-2,8):
    for d in [-1.2,-.6,0,.6,1.2]:
     u=center+d;G.box('scp-frame',(u,1.98,-.1),(.48,2.6,.14));G.box('scp-glass',(u,1.98,-.18),(.34,2.42,.035))
     for y in [1,1.55,2.1,2.65]:G.box('scp-frame',(u,y,-.21),(.42,.035,.03))
 # Public lobby canopy in recessed east-facing central bay.
 W.box('scp-canopy',(-64,3.5,3502),(9,.28,8),True)
 for z in [3498.5,3505.5]:W.box('scp-brick',(-59.6,1.85,z),(.45,3.2,.45),True)
 E=Frame(B,-67.3,3502,-math.pi/2,y=0)
 for u in [-.52,.52]:
  E.box('scp-frame',(u,1.6,-.02),(1.02,2.7,.14));E.box('scp-glass',(u,1.6,-.11),(.88,2.55,.04));E.box('scp-metal',(u*.25,1.4,-.18),(.04,.4,.05))
 E.text('PUBLIC ENTRANCE',(0,3.05,-.1),.2,'scp-letter')
 E2=Frame(B,-60.95,3484,-math.pi/2,y=0)
 E2.text('LAS VEGAS METROPOLITAN POLICE',(0,4.95,-.1),.42,'scp-letter');E2.text('SOUTH CENTRAL AREA COMMAND',(0,4.35,-.1),.36,'scp-letter')
 site=box(-106,3460,-22,3555).difference(p.buffer(.12))
 for x in range(-106,-22,4):
  for z in range(3460,3555,4):B.planar('scp-asphalt',site.intersection(box(x,z,x+4,z+4)),.26,True)
 B.planar('scp-paving',p.buffer(2.1).difference(p),.32,True)
 # Public front parking rows, with broad clear central approach.
 for z in np.arange(3464,3540,2.8):
  if 3496<z<3509:continue
  W.box('scp-line',(-33,.28,z),(5,.02,.07))
  if z<3492 or z>3513:W.box('scp-line',(-54,.28,z),(4.8,.02,.07))
 for x,z in [(-35,3471),(-35,3488),(-35,3515),(-35,3537)]:
  W.box('scp-gravel',(x,.32,z),(2.2,.14,4.2),True)
  for dz in [-1.1,0,1.1]:B.sphere('scp-shrub',(x,.65,z+dz),.55,12,6,scale=(1,.7,.9))
 # Boundary wall shown in street reference; vehicle entrance deliberately open.
 for x0,x1 in [(-104,-86),(-76,-25)]:
  W.box('scp-brick',((x0+x1)/2,1.3,3550),(x1-x0,2.1,.35),True);W.box('scp-sill',((x0+x1)/2,2.37,3550),(x1-x0,.12,.45))
 for x,z in [(-95,3518),(-86,3497)]:
  W.box('scp-metal',(x,6.4,z),(2.3,.95,1.8));W.box('scp-dark',(x,6.91,z),(1.9,.08,1.4))
 return dict(key=KEY,name='South Central Area Command',center=[-70,0,3507],bounds=[-107,3459,-21,3556],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
