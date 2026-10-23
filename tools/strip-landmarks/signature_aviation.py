"""Signature Aviation terminal: mapped shell, photographed public and apron elevations."""
from common import *
from forum_shops import facade_frame
KEY='signatureAviation'
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/terminal';B.detail=0;W=Frame(B,0,0,y=0)
 p=footprint('way/276437574');canopy=footprint('way/276437575')
 B.shell(p,.24,9,'sig-metal-paint',roof=False);B.planar('sig-flat-roof-paint',p,8.9,True)
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  G,L,nx,nz=facade_frame(B,a,b,p,.025)
  G.box('sig-coping',(L/2,9.06,-.03),(L,.12,.24))
  for y in np.arange(.65,9,.36):G.box('sig-panel-joint',(L/2,y,-.055),(L,.018,.018))
  if L<3:continue
  airside=nx>.3 and nz<.2
  bands=[(3.35,5.7)] if airside else [(1.65,2.3),(5.7,1.0)]
  for cy,h in bands:
   G.box('sig-dark',(L/2,cy,-.07),(max(1,L-1.4),h+.12,.1))
   G.box('sig-glass',(L/2,cy,-.14),(max(.8,L-1.6),h,.04))
   for u in np.arange(.8,L-.7,1.45):G.box('sig-frame',(u,cy,-.19),(.055,h,.06))
   for y in np.arange(cy-h/2+.8,cy+h/2,.8):G.box('sig-frame',(L/2,y,-.19),(max(.8,L-1.6),.045,.06))
  if L>22:
   G.text('SIGNATURE',(L*.65,7.45,-.12),1.2,'sig-letter')
   G.text('AVIATION',(L*.65,6.85,-.12),.4,'sig-letter')
   for u in np.arange(1,L,5.8):G.box('sig-pier',(u,1.65,-.22),(.32,2.85,.42))
  if airside and L>13:
   G.box('sig-frame',(L/2,1.65,-.22),(2.6,2.75,.12));G.box('sig-glass',(L/2,1.65,-.3),(2.4,2.55,.04));G.box('sig-frame',(L/2,1.65,-.34),(.05,2.65,.05))
 # Mapped entrance canopy is a roof only: open vehicle clearance below.
 B.planar('sig-canopy-metal-paint',canopy,5.8,True);B.planar('sig-canopy-soffit-paint',canopy,5.45)
 for a,b in zip(list(canopy.exterior.coords),list(canopy.exterior.coords)[1:]):
  G,L,nx,nz=facade_frame(B,a,b,canopy,.01);G.box('sig-canopy-metal-paint',(L/2,5.63,0),(L,.36,.1))
 for x,z in [(150,3983),(155.8,3989.3)]:W.tube('sig-frame',(x,.3,z),(x,5.5,z),.16,16)
 # Public doorway at canopy junction, with transverse mullions and push bars.
 D=Frame(B,157.4,3973.5,math.atan2(.76,-.65),y=0)
 D.box('sig-frame',(0,1.65,-.04),(3.6,2.7,.12));D.box('sig-glass',(0,1.65,-.12),(3.4,2.5,.04));D.box('sig-frame',(0,1.65,-.17),(.05,2.6,.05))
 for x in [-.8,.8]:D.box('sig-frame',(x,1.4,-.22),(.8,.04,.04))
 # Flat roof mechanical plant, kept behind the parapet.
 for x,z in [(178,3980),(185,3987),(175,3975)]:
  W.box('sig-service',(x,9.35,z),(2,.8,2.5));W.box('sig-dark',(x,9.78,z),(1.7,.05,2.1))
 site=p.buffer(4,join_style=2).union(canopy.buffer(2,join_style=2)).difference(p)
 B.planar('sig-paving',site,.30,True)
 arrival=Polygon([(135,3969),(146,3967),(160,3982),(160,3994),(151,3995),(133,3976)])
 B.planar('sig-asphalt',arrival.difference(site),.26,True)
 for x,z in [(147,3975),(148.5,3978),(153,3991),(156,3993)]:W.tube('sig-bollard',(x,.3,z),(x,1.2,z),.11,12)
 # Site ground closes the surveyed terminal plot where the existing city base stops.
 grounds=Polygon([(52,3920),(205,3920),(245,3960),(237,4015),(208,4098),(65,4098),(52,4060)])
 for x in np.arange(52,245,12):
  for z in np.arange(3920,4098,12):B.planar('sig-asphalt',grounds.intersection(box(x,z,x+12,z+12)),.10,True)
 for x,z,w,d in [(75,3965,8,62),(105,3988,8,40),(111,4048,55,5),(70,4062,8,45)]:
  island=box(x-w/2,z-d/2,x+w/2,z+d/2);B.planar('sig-gravel',island,.20,True)
  for a,b in zip(list(island.exterior.coords),list(island.exterior.coords)[1:]):W.tube('sig-curb',(a[0],.22,a[1]),(b[0],.22,b[1]),.09,6)
 for x,z,rows in [(85,3940,13),(115,3972,11),(85,4025,14),(123,4025,14)]:
  for i in range(rows):W.box('sig-line',(x,.125,z+i*2.65),(5,.025,.08))
 samples=[]
 for x in np.arange(130,205,1.2):
  for z in np.arange(3952,4009,1.2):
   if site.buffer(-.6).covers(Point(x,z)) and not canopy.boundary.buffer(.6).covers(Point(x,z)):samples.append([float(x),.3,float(z)])
 Path('build/city-exteriors/signature-aviation-samples.json').write_text(json.dumps(samples))
 return dict(key=KEY,name='Signature Aviation LAS',center=[174,0,3980],bounds=[52,3920,245,4098],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
