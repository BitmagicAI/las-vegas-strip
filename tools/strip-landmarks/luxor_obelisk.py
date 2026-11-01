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
 # Raised blue letters with a narrow warm metal backing, referenced north/south.
 for side in [-1,1]:
  for j,ch in enumerate('LUXOR'):
   y=34.7-j*2.8;d=(6.7+(3.55-6.7)*(y-6.61)/(39.35-6.61))/2
   F.text(ch,(0,y,side*(d+.10)),3.85,'lob-gold-letter',back=side>0)
   F.text(ch,(0,y+.02,side*(d+.19)),3.7,'lob-blue-letter',back=side>0)
 # Four original relief figures on each face (October2024 Street View).
 # Profile rings give continuous carved silhouettes, not downloaded sculpture.
 def sculpt(x,z,y,yaw):
  S=Frame(B,CX+x,CZ+z,yaw=yaw,y=y)
  def form(profile,mat='lob-sculpt-stone',cx=0,n=16):
   rings=[[(cx+w*math.cos(a),yy,zz+depth*math.sin(a)) for a in np.linspace(0,math.tau,n,endpoint=False)] for yy,w,depth,zz in profile]
   for lo,hi in zip(rings,rings[1:]):
    for i in range(n):B.face(mat,[S.p(*lo[i]),S.p(*hi[i]),S.p(*hi[(i+1)%n]),S.p(*lo[(i+1)%n])])
   B.face(mat,[S.p(*q)for q in rings[0]])
   B.upface(mat,[S.p(*q)for q in rings[-1]])
  for side in [-1,1]:
   cx=side*.23
   form([(.05,.19,.36,-.18),(.18,.2,.37,-.18),(.27,.16,.23,-.05)],cx=cx)
   form([(.22,.12,.14,0),(.50,.14,.16,0),(.78,.19,.19,0),(1.13,.21,.22,0)],cx=cx)
  form([(1.02,.45,.24,0),(1.18,.46,.25,0),(1.45,.37,.24,0),(1.72,.50,.25,0),(1.90,.53,.23,.01),(2.02,.34,.20,.02)])
  form([(1.99,.16,.16,0),(2.12,.17,.16,0)])
  form([(2.08,.17,.17,-.03),(2.17,.24,.23,-.03),(2.40,.25,.23,-.02),(2.52,.19,.19,0)])
  # Broad headdress crown and hanging lappets, collar and carved brow/eyes.
  form([(2.35,.31,.25,.035),(2.54,.32,.24,.04),(2.62,.22,.18,.05)])
  for side in [-1,1]:
   form([(1.91,.105,.17,.04),(2.12,.14,.20,.045),(2.37,.13,.22,.05),(2.49,.10,.20,.05)],cx=side*.31,n=12)
   S.path('lob-carve-paint',[(side*.08,2.30,-.251),(side*.19,2.30,-.21)],.012,6)
   S.path('lob-sculpt-stone',[(side*.06,2.34,-.26),(side*.19,2.34,-.225)],.025,8)
   S.path('lob-sculpt-stone',[(side*.48,1.89,0),(side*.57,1.63,-.01),(side*.53,1.26,-.10)],.12,12)
   form([(1.12,.10,.11,-.11),(1.32,.115,.12,-.10)],cx=side*.53,n=12)
   for yy in [1.98,2.08,2.18,2.28,2.38]:S.path('lob-carve-paint',[(side*.23,yy,-.15),(side*.40,yy,-.12)],.009,4)
  S.box('lob-sculpt-stone',(0,2.25,-.285),(.085,.17,.10))
  S.path('lob-carve-paint',[(-.10,2.15,-.24),(0,2.14,-.27),(.10,2.15,-.24)],.009,6)
  S.path('lob-carve-paint',[(-.32,1.96,-.15),(-.20,1.84,-.23),(0,1.79,-.25),(.20,1.84,-.23),(.32,1.96,-.15)],.014,6)
  for x0 in [-.30,-.15,0,.15,.30]:S.path('lob-carve-paint',[(x0,1.07,-.25),(x0,1.37,-.235)],.01,4)
 for side in [-1,1]:
  for x in [-2.85,-.95,.95,2.85]:sculpt(x,side*5.35,3.65,0 if side<0 else math.pi)
 # Service lights are fixtures only; do not alter the runtime light set.
 for side in [-1,1]:
  for x in [-2.6,2.6]:F.box('lob-metal-paint',(x,3.65,side*5.2),(.3,.16,.25))
 samples=[[CX+x,.8,CZ+z]for x in [-1.4,0,1.4]for z in np.arange(-6.5,6.6,.5)]
 routes=[[[CX,.24,CZ-6.5],[CX,.24,CZ+6.5]],[[CX-5.9,.24,CZ-5.8],[CX-5.9,.24,CZ+5.8]]]
 Path('build/city-exteriors/luxor-obelisk-samples.json').write_text(json.dumps(samples));Path('build/city-exteriors/luxor-obelisk-stairs.json').write_text(json.dumps(routes))
 return dict(key=KEY,name='Luxor obelisk',center=[CX,0,CZ],bounds=list(p.buffer(2).bounds),structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
