"""Luxor roadside obelisk: mapped plan, referenced tapered shaft and open base.
Height42.672m follows published140ft; ornament is authored approximation.
"""
from common import *
KEY='luxorObelisk';IDS=['way/399368723'];CX=-28.4755;CZ=2283.836

def exterior(B):
 B.property=KEY+'-exterior';B.source='luxor-obelisk';B.detail=0
 F=Frame(B,CX,CZ,y=0);p=footprint(IDS[0])
 B.planar('lob-paving',p.buffer(1.7,join_style=2),.24,True)
 # Keep a continuous north/south passage under the plinth, not a solid box.
 for x in [-3.45,3.45]:F.box('lob-stone-paint',(x,1.65,0),(2.75,2.82,11.36),True)
 F.box('lob-stone-paint',(0,3.12,0),(9.67,.4,11.36),True)
 F.box('lob-stone-paint',(0,3.45,0),(9.4,.30,11.1),True)
 def loft(y0,y1,w0,d0,w1,d1,mat,solid=False):
  a=[(-w0/2,y0,-d0/2),(w0/2,y0,-d0/2),(w0/2,y0,d0/2),(-w0/2,y0,d0/2)]
  b=[(-w1/2,y1,-d1/2),(w1/2,y1,-d1/2),(w1/2,y1,d1/2),(-w1/2,y1,d1/2)]
  for i in range(4):B.face(mat,[F.p(*a[i]),F.p(*a[(i+1)%4]),F.p(*b[(i+1)%4]),F.p(*b[i])],solid)
  B.upface(mat,[F.p(*q)for q in b],solid)
 loft(3.6,6.4,8.9,10.6,7.3,8.6,'lob-stone-paint',True)
 F.box('lob-stone-paint',(0,6.5,0),(7.55,.22,8.85),True)
 loft(6.61,39.35,6.7,6.7,3.55,3.55,'lob-glyph-paint',True)
 loft(39.35,42.672,3.55,3.55,.015,.015,'lob-stone-paint',True)
 # North/south channel letters project from the tapered faces.
 for side in [-1,1]:
  for j,ch in enumerate('LUXOR'):
   y=35.4-j*2.2;d=(6.7+(3.55-6.7)*(y-6.61)/(39.35-6.61))/2
   F.text(ch,(0,y,side*(d+.11)),1.95,'lob-blue-letter',back=side>0)
 # Flanking pedestal relief figures, segmented sculpted silhouettes, batched.
 # Fine facial/robe carving remains an approximation, never scan-quality.
 def sculpt(x,z,y,yaw):
  S=Frame(B,CX+x,CZ+z,yaw=yaw,y=y)
  for sx in [-.22,.22]:
   S.box('lob-sculpt-stone',(sx,.16,-.1),(.38,.24,.6))
   S.tube('lob-sculpt-stone',(sx,.25,0),(sx,.98,0),.16,12,.22)
  S.lathe('lob-sculpt-stone',0,0,[(.9,.45),(1.35,.43),(1.75,.52),(2.05,.36)],20)
  S.lathe('lob-sculpt-stone',0,-.01,[(1.95,.2),(2.1,.31),(2.45,.30),(2.6,.12)],20)
  S.box('lob-sculpt-stone',(0,2.26,-.29),(.10,.18,.10))
  for side in [-1,1]:
   S.path('lob-sculpt-stone',[(side*.45,1.8,0),(side*.63,1.32,-.08),(side*.3,1.25,-.34)],.13,10)
  # Stone headdress side lappets and incised kilt folds.
  for side in [-1,1]:S.path('lob-sculpt-stone',[(side*.23,2.5,.02),(side*.37,2.15,.04),(side*.32,1.88,-.03)],.11,8)
  for x0 in [-.27,-.13,0,.13,.27]:S.path('lob-carve-paint',[(x0,.93,-.43),(x0,1.28,-.43)],.015,4)
 for side in [-1,1]:
  for x in [-2.8,-1.4,0,1.4,2.8]:sculpt(x,side*5.35,3.65,0 if side<0 else math.pi)
 # Service lights are fixtures only; do not alter the runtime light set.
 for side in [-1,1]:
  for x in [-2.6,2.6]:F.box('lob-metal-paint',(x,3.65,side*5.2),(.3,.16,.25))
 samples=[[CX+x,.8,CZ+z]for x in [-1.4,0,1.4]for z in np.arange(-6.5,6.6,.5)]
 routes=[[[CX,.24,CZ-6.5],[CX,.24,CZ+6.5]],[[CX-5.9,.24,CZ-5.8],[CX-5.9,.24,CZ+5.8]]]
 Path('build/city-exteriors/luxor-obelisk-samples.json').write_text(json.dumps(samples));Path('build/city-exteriors/luxor-obelisk-stairs.json').write_text(json.dumps(routes))
 return dict(key=KEY,name='Luxor obelisk',center=[CX,0,CZ],bounds=list(p.buffer(2).bounds),structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
