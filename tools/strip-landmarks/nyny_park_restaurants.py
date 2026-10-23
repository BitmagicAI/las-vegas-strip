"""Mapped Park restaurant row, replacing the roof-tagged solid placeholder.
Earth 2022-11-09 plus owner property map; heights/tenant bay widths estimated.
"""
from common import *
from forum_shops import facade_frame

def exterior(B):
 B.property='newYorkFrontage-exterior';B.source='park-restaurants';B.detail=0
 p=footprint('way/567194734');h=5.4
 B.shell(p,.24,h,'nyny-brick',roof=False,solid=True)
 B.planar('nyny-membrane-paint',p,h,True)
 for poly in parts(p):
  ps=list(poly.exterior.coords)
  for a,b in zip(ps,ps[1:]):
   F,L,nx,nz=facade_frame(B,a,b,p,.02);F.y=0
   if L<.3:continue
   front=nz<-.25 or nx>.6
   F.box('nyny-metal',(L/2,h-.13,-.12),(L,.26,.38))
   F.box('nyny-concrete',(L/2,.43,-.09),(L,.38,.18))
   if front:
    count=max(1,round(L/5));pitch=L/count
    for i in range(count):
     x=(i+.5)*pitch
     F.box('nyny-window',(x,2.38,-.14),(max(.2,pitch-.65),3.45,.14))
     for dx in [-pitch/2+.29,0,pitch/2-.29]:F.box('nyny-metal',(x+dx,2.4,-.25),(.085,3.55,.12))
     for y in [.68,3.18,4.13]:F.box('nyny-metal',(x,y,-.25),(max(.2,pitch-.52),.085,.12))
     F.box('nyny-metal',(x,4.44,-.65),(max(.2,pitch-.15),.14,1.3))
     for dx in [-pitch/2+.45,pitch/2-.45]:
      F.b.tube('nyny-metal',F.p(x+dx,4.85,-.13),F.p(x+dx,4.42,-1.22),.025,6)
    # Mortar bands remain in solid piers only: no stripes across the glazing.
    for x in np.arange(.1,L,5):F.box('nyny-stone',(x,2.75,-.16),(.15,4.9,.2))
   elif L>7:
    # Back of restaurant row: service doors and louver banks, not shop windows.
    for x in np.arange(3,L-2,12):
     F.box('nyny-metal',(x,1.7,-.10),(1.5,2.9,.12))
     for y in np.arange(.6,2.9,.32):F.box('nyny-shadow',(x,y,-.18),(1.3,.045,.04))
   if front and a[0]>-140 and b[0]>-140 and L>25:
    F.box('nyny-metal',(L/2,4.97,-.2),(min(15,L-2),.7,.16))
    F.text('BEERHAUS',(L/2,4.95,-.31),.62,'nyny-white')
 # Low parapet and sparse surveyed-type mechanical clusters on the stepped roof.
 for x,z in [(-116,1419),(-153,1416),(-188,1428),(-214,1435),(-242,1440)]:
  if p.contains(box(x-1.8,z-1.1,x+1.8,z+1.1)):
   B.box('nyny-metal',(x,h+.45,z),(3.6,.9,2.2))
   for dx in [-.9,.9]:B.lathe('nyny-shadow',(x+dx,z),[(h+.9,.42),(h+.98,.42),(h+.98,.01)],12)
