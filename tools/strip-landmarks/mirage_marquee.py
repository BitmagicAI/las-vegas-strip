"""Mirage-era double pylon and pedestrian shelter from mapped plan and historical views.
60m overall height remains an explicit visual estimate; displays use original neutral art.
"""
from common import *
KEY='mirageMarquee';IDS=['way/180766593','way/851629120']
def exterior(B):
 B.property=KEY+'-exterior';B.source='mirage-marquee';B.detail=0
 F=Frame(B,-.252,-427.01,yaw=-.0244,y=0)
 # Tall separated legs leave a real open lower gap instead of a solid building block.
 for u in [-10.65,10.65]:
  F.box('mm-white-stone',(u,27,0),(2.4,54,3.7),True)
  for side in [-1,1]:
   F.box('mm-metal-paint',(u,27,side*1.86),(.62,52,.045))
   for y in np.arange(2,53,2.2):F.box('mm-joint-paint',(u,y,side*1.89),(.64,.025,.025))
  F.box('mm-white-stone',(u,.5,0),(3.2,1,4.3),True)
 # Upper primary display cabinet and a lower secondary cabinet between the piers.
 for lo,hi,w in [(28,53.5,21.6),(7,26,18.7)]:
  F.box('mm-dark-metal-paint',(0,(lo+hi)/2,0),(w,hi-lo,3.2))
  for side in [-1,1]:
   F.box('mm-display-paint',(0,(lo+hi)/2,side*1.63),(w-.5,hi-lo-.5,.035))
   for u in [-w/2,w/2]:F.box('mm-white-stone',(u,(lo+hi)/2,side*1.7),(.28,hi-lo+.25,.24))
   for y in [lo,hi]:F.box('mm-white-stone',(0,y,side*1.7),(w+.5,.3,.3))
 # Stepped entablature, black channel letters and narrow gold accent.
 for y,h,w,d in [(54,.65,25.3,4.3),(56.7,4.7,24.3,3.8),(59.25,.45,25.5,4.4),(59.75,.35,25.8,4.7)]:
  F.box('mm-white-stone',(0,y,0),(w,h,d),True)
 for side in [-1,1]:
  F.text('THE MIRAGE',(0,56.1,side*1.96),2.7,'mm-dark-letter',back=side>0)
  F.text('CASINO & RESORT',(0,54.8,side*2.18),.8,'mm-dark-letter',back=side>0)
  F.text('THE MIRAGE',(0,40.5,side*1.69),1.85,'mm-gold-letter',back=side>0)
  F.text('LAS VEGAS',(0,38.4,side*1.69),.8,'mm-gold-letter',back=side>0)
  F.text('ENTERTAINMENT',(0,17.4,side*1.69),.92,'mm-white-letter',back=side>0)
  F.text('DINING  /  CASINO',(0,15.7,side*1.69),.6,'mm-white-letter',back=side>0)
  for y in [30,51.5]:F.box('mm-gold-paint',(0,y,side*1.68),(18,.045,.025))
 # Adjacent mapped covered pedestrian shelter, with a lit soffit and open sides.
 p=footprint(IDS[1]);x,z=p.centroid.x,p.centroid.y;S=Frame(B,x,z,yaw=-.021,y=0)
 S.box('mm-bronze-paint',(0,3.10,0),(6.9,.48,3.9),True)
 S.box('mm-white-paint',(0,2.84,0),(6.5,.06,3.5))
 for u in [-2.95,2.95]:
  for w in [-1.45,1.45]:
   S.box('mm-white-stone',(u,.55,w),(.48,1.1,.48),True)
   S.box('mm-bronze-paint',(u,1.98,w),(.32,1.76,.32),True)
 for side in [-1,1]:S.text('Mirage',(0,2.94,side*1.96),.38,'mm-white-letter',back=side>0)
 for u in [-2,-1,0,1,2]:
  for w in [-1,0,1]:S.box('mm-lamp',(u,2.79,w),(.07,.015,.07))
 apron=p.buffer(1.3,join_style=2);B.planar('mm-paving-stone',apron,.11,True)
 # Maintenance pad only under sign piers; retain nearby street surfaces.
 sign=footprint(IDS[0]);B.planar('mm-paving-stone',sign.buffer(.8,join_style=2),.10,True)
 samples=[]
 for poly,y in [(F.poly([(-12.9,-2.35),(12.9,-2.35),(12.9,2.35),(-12.9,2.35)]),59.925),(S.poly([(-3.45,-1.95),(3.45,-1.95),(3.45,1.95),(-3.45,1.95)]),3.34)]:
  for xx in np.arange(poly.bounds[0],poly.bounds[2],.8):
   for zz in np.arange(poly.bounds[1],poly.bounds[3],.8):
    if poly.buffer(-.18).contains(Point(xx,zz)):samples.append([float(xx),y+.35,float(zz)])
 routes=[[S.p(-2.2,.11,-2.3),S.p(-2.2,.11,2.3)],[S.p(2.2,.11,-2.3),S.p(2.2,.11,2.3)]]
 Path('build/city-exteriors/mirage-marquee-samples.json').write_text(json.dumps(samples));Path('build/city-exteriors/mirage-marquee-stairs.json').write_text(json.dumps(routes))
 return dict(key=KEY,name='Mirage historic marquee and sidewalk shelter',center=[0,0,-427],bounds=[-14,-432,14,-417],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
