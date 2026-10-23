"""Grand Bazaar street retail. Mapped footprints; Ole Red current built references.
Unknown tenant placements are deliberately not given invented brand signs.
"""
from common import *
from forum_shops import facade_frame
RETAIL=['way/1254249180','way/983892276','way/1254249181','way/839503453','way/839503455','way/1254249185','way/1254249184','way/839503452','way/1254249190','way/1254249183','way/839470825','way/1254249182']
def frontage(B):
 B.source='horseshoe/bazaar-frontage'
 for ident in RETAIL:
  p=footprint(ident);ole=ident=='way/839503453';h=17 if ole else BYID[ident]['height'];roof=BYID[ident]['tags'].get('building')=='roof'
  if ole:
   # Four levels, estimated4.2m spacing. The mapped9m height predates this venue.
   x0,z0,x1,z1=p.bounds;front=x0+2.6
   for level in range(4):
    y=.24+level*4.2
    B.box('baz-deck',((x0+x1)/2,y-.12,(z0+z1)/2),(x1-x0,.24,z1-z0),True)
    # Recessed west glazing leaves real projecting balconies inside the footprint.
    if level<3:
     B.box('baz-glass',(front,y+2,z0+(z1-z0)/2),(.12,3.8,z1-z0-1.3))
     for z in np.arange(z0+.7,z1,5):
      B.box('baz-brick',(front-.15,y+2.1,z),(.65,4.2,.65),True)
      B.box('baz-metal',(front-.27,y+2,z+2.3),(.12,3.8,.08))
     for yy in [y+.4,y+3.7]:B.box('baz-metal',(front-.27,yy,(z0+z1)/2),(.15,.15,z1-z0))
    if level:
     for a,b in [((x0,z0),(x0,z1)),((x0,z0),(front,z0)),((x0,z1),(front,z1))]:
      F=Frame(B,0,0,y=y);F.rail(a,b,1.12,True)
    if level<3:
     for z in [z0,z1]:
      B.box('baz-brick',((front+x1)/2,y+2.1,z),(x1-front,4.2,.25),True)
      for x in np.arange(front+2,x1-1,4.7):B.box('baz-glass',(x,y+2,z+(-.16 if z==z0 else .16)),(3.4,3.0,.06))
     B.box('baz-brick',(x1,y+2.1,(z0+z1)/2),(.25,4.2,z1-z0),True)
   # Roof shade frame and inset brick service core.
   B.box('baz-brick',(x1-3,14.65,(z0+z1)/2),(6,4.2,8),True)
   for z in np.arange(z0+1,z1,5):
    for x in [x0+.5,x0+7]:B.box('baz-metal',(x,14.4,z),(.15,3.4,.15))
    B.box('baz-metal',(x0+3.8,16.1,z),(7.6,.16,.16))
   B.box('baz-shade',(x0+3.8,16.16,(z0+z1)/2),(7.6,.1,z1-z0))
   for level in [1,2,3]:B.box('baz-red',(x0-.03,.24+level*4.2-.18,(z0+z1)/2),(.12,.14,z1-z0))
   F=Frame(B,x0-.1,(z0+z1)/2,math.pi/2,y=0);F.text('OLE RED',(0,4.25,0),1.2,'baz-letter')
   continue
  if roof:
   B.planar('baz-shade',p,h)
   for x,z in list(p.exterior.coords)[:-1]:B.box('baz-metal',(x,h/2,z),(.12,h,.12),True)
   continue
  B.shell(p,0,h,'baz-stucco',roof=False)
  B.planar('baz-roof',p,h,True)
  ps=list(p.exterior.coords)
  for a,b in zip(ps,ps[1:]):
   F,L,_,_=facade_frame(B,a,b,p,.08)
   if L<2:continue
   F.box('baz-metal',(L/2,h-.45,-.12),(L,.55,.15))
   for x in np.arange(2,L-1,4.2):
    F.box('baz-glass',(x,2,-.15),(3.5,3.7,.06));F.box('baz-metal',(x,2,-.22),(.08,3.7,.1))
    for y in [.25,3.85]:F.box('baz-metal',(x,y,-.22),(3.6,.12,.1))
    F.box('baz-awning',(x,4.2,-.85),(3.7,.15,1.6))
   if ident=='way/983892276' and L>15:F.text("GIORDANO'S",(L/2,h-.9,-.4),.75,'baz-letter')
   F.box('baz-stucco',(L/2,h+.14,0),(L,.28,.3))
  c=p.representative_point();B.box('baz-service',(c.x,h+.45,c.y),(2,.9,1.5))
