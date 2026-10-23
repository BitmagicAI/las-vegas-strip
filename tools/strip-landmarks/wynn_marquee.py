"""Wynn roadside marquee, YESCO135ft total /100x50ft LED face.
Original neutral display artwork; static eraser band, no advertisement or motion claim.
"""
from common import *
KEY='wynnMarquee';IDS=['way/111348710']
def exterior(B):
 B.property=KEY+'-exterior';B.source='wynn-marquee';B.detail=0
 F=Frame(B,432.387,-1164.56,yaw=-.14,y=0);W=15.24;H=41.148;lo=10.668
 # Chamfered bronze pedestal, kept inside mapped footprint.
 p=F.poly([(-4,-2.6),(3,-2.6),(4,-1.8),(4,1.8),(3,2.6),(-4,2.6)])
 B.shell(p,0,lo+.3,'wm-bronze-paint',roof=False);B.planar('wm-roof-paint',p,lo+.3,True)
 for x in [-3.6,-1.8,0,1.8,3.6]:
  for side in [-1,1]:F.box('wm-joint-paint',(x,lo/2,side*2.605),(.035,lo,.018))
 for y in np.arange(2,lo,2):
  for side in [-1,1]:F.box('wm-joint-paint',(0,y,side*2.61),(7.3,.025,.018))
 def depth(u):return .8+1.65*(u/(W/2))**2
 us=np.linspace(-W/2,W/2,49)
 # Two opposed concave faces with a shallow lens-shaped roof and closed ends.
 for side in [-1,1]:
  for u,v in zip(us,us[1:]):
   B.face('wm-led-paint',[F.p(u,lo,side*depth(u)),F.p(v,lo,side*depth(v)),F.p(v,H,side*depth(v)),F.p(u,H,side*depth(u))][::(-1 if side>0 else 1)])
   # Horizontal ribbed moving-eraser housing, held at its photographed low position.
   for y in np.arange(lo,lo+5.4,.22):
    B.face('wm-eraser-paint',[F.p(u,y,side*(depth(u)+.22)),F.p(v,y,side*(depth(v)+.22)),F.p(v,y+.14,side*(depth(v)+.22)),F.p(u,y+.14,side*(depth(u)+.22))][::(-1 if side>0 else 1)])
  for u in [-W/2,W/2]:F.box('wm-metal-paint',(u,(H+lo)/2,side*depth(u)),(.18,H-lo,.18))
  for y in [lo,H]:F.path('wm-metal-paint',[(u,y,side*depth(u))for u in us],.12,6)
  # Name band lettering is a local script-font approximation, kept independent of LED panel.
  F.text('Wynn',(0,lo+1.4,side*(depth(0)+.36)),3.2,'wm-gold-letter',back=side>0)
  F.text('WYNN',(0,28,side*(depth(0)+.06)),1.5,'wm-screen-letter',back=side>0)
  F.text('LAS VEGAS',(0,26,side*(depth(0)+.06)),.65,'wm-screen-letter',back=side>0)
 for u in [-W/2,W/2]:
  B.face('wm-metal-paint',[F.p(u,lo,-depth(u)),F.p(u,lo,depth(u)),F.p(u,H,depth(u)),F.p(u,H,-depth(u))])
 roof=F.poly([(u,-depth(u))for u in us]+[(u,depth(u))for u in us[::-1]])
 B.planar('wm-roof-paint',roof,H,True)
 # Perimeter maintenance surface is local; the public Strip sidewalk stays untouched.
 apron=p.buffer(2.4,join_style=2);B.planar('wm-paving-stone',apron.difference(p),.12,True)
 samples=[]
 for x in np.arange(roof.bounds[0],roof.bounds[2],.8):
  for z in np.arange(roof.bounds[1],roof.bounds[3],.8):
   if roof.buffer(-.15).contains(Point(x,z)):samples.append([float(x),H+.35,float(z)])
 route=[F.p(u,.12,w)for u,w in [(-5,-3.6),(5,-3.6),(5,3.6),(-5,3.6),(-5,-3.6)]]
 Path('build/city-exteriors/wynn-marquee-samples.json').write_text(json.dumps(samples));Path('build/city-exteriors/wynn-marquee-stairs.json').write_text(json.dumps([route]))
 return dict(key=KEY,name='Wynn curved roadside marquee',center=[432,0,-1165],bounds=list(roof.bounds),structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
