"""Residence Inn Hughes Center, mapped U-shaped plan with cream piers and blue hip roofs."""
from common import *
from forum_shops import facade_frame
KEY='residenceInnHughes';IDS=['way/205497576','way/1460748280']
def hip(B,F,x,z,w,d,y,rise):
 c=[(x-w/2,y,z-d/2),(x+w/2,y,z-d/2),(x+w/2,y,z+d/2),(x-w/2,y,z+d/2)]
 ridge=[(x-w*.2,y+rise,z),(x+w*.2,y+rise,z)]
 for poly in [[c[0],c[1],ridge[1],ridge[0]],[c[1],c[2],ridge[1]],[c[2],c[3],ridge[0],ridge[1]],[c[3],c[0],ridge[0]]]:B.upface('rh-blue-roof',[F.p(*v) for v in poly],True)
 # Raised standing seams on the sloping metal roof, well separated from roof faces.
 for xx in np.arange(x-w*.2,x+w*.2,.55):
  for side in [-1,1]:B.tube('rh-roof-seam',F.p(xx,y+.035,z+side*d/2),F.p(xx,y+rise+.035,z),.018,4)
def exterior(B):
 B.property=KEY+'-exterior';B.source='residence-inn-hughes';B.detail=0
 p=footprint(IDS[0]);B.shell(p,0,36,'rh-cream',roof=False);B.planar('rh-roof',p,36.025,True)
 ps=list(p.exterior.coords)
 for a,b in zip(ps,ps[1:]):
  F,L,_,_=facade_frame(B,a,b,p,0)
  if L<.1:continue
  F.box('rh-stone',(L/2,.9,-.12),(L,1.8,.25))
  for y in [3,33.1,35.7]:F.box('rh-trim',(L/2,y,-.15),(L,.24,.32))
  if L>12:
   n=max(1,round(L/3.25));w=L/n
   for k in range(n):
    x=(k+.5)*w
    for y in np.arange(4.45,34,3.05):
     F.box('rh-glass',(x,y,-.13),(1.4,1.62,.045))
     F.box('rh-frame',(x,y,-.19),(.055,1.63,.055))
     F.box('rh-frame',(x,y-.26,-.19),(1.4,.055,.055))
     F.box('rh-trim',(x,y-.86,-.24),(1.58,.12,.25))
     F.box('rh-reveal',(x,y+.84,-.18),(1.47,.065,.12))
    F.box('rh-glass',(x,1.9,-.2),(1.5,1.5,.045))
  if 9<L<12:F.text('Residence Inn',(L/2,34,-.23),.46,'rh-sign')
 # Roof center: blue pitched metal cap observed between the two wings.
 F=Frame(B,1550,22,math.radians(42.5),0);hip(B,F,0,0,17,13,36.1,2.8)
 for x,z in [(1522,34),(1548,2)]:
  B.box('rh-cream',(x,37.1,z),(4,2.2,4),True);B.box('rh-roof',(x,38.23,z),(4.4,.16,4.4))
 # Drive-through porte-cochere on the east arrival face. No filled solid beneath roof.
 a=(1547.459,40.921);b=(1557.674,29.756);F,L,_,_=facade_frame(B,a,b,p,0);x=L*.5
 F.box('rh-trim',(x,4.85,-5.5),(14,.3,11.5),True);hip(B,F,x,-5.5,14.6,12.1,5.03,2.25)
 for xx in [x-6,x+6]:F.box('rh-stone',(xx,2.35,-10),(.65,4.7,.65),True)
 F.text('RESIDENCE INN',(x,4.65,-11.35),.40,'rh-sign')
 return dict(key=KEY,name='Residence Inn Hughes Center exterior',center=[1540,0,22],bounds=list(p.buffer(12).bounds),structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],views={})
