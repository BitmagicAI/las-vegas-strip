"""Static rooftop machinery from cited photographs; dimensions/orientation estimated.
Not a playable ride. Keeps the existing observation pod/mast geometry owner.
"""
from common import *
def rides(B,cx,cz):
 B.source='strat-rooftop-rides';B.detail=0;F=Frame(B,cx,cz,y=0)
 # Big Shot central pressure cylinder and guide rails within the existing lattice.
 F.lathe('st-red',0,0,[(280,1.05),(333,1.05),(334,.85)],24)
 for a in np.linspace(0,math.tau,4,endpoint=False):
  x,z=2.1*math.cos(a),2.1*math.sin(a)
  F.tube('st-sill',(x,280,z),(x,332,z),.07,8)
 # Octagonal loading apron above the tapered machinery roof; sides are enclosed.
 apron=Point(cx,cz).buffer(9.7,resolution=2)
 B.shell(apron,280,280.5,'st-grey',roof=False);B.planar('st-roof',apron,280.5,True)
 for a in np.linspace(0,math.tau,64,endpoint=False):
  x,z=9.35*math.cos(a),9.35*math.sin(a)
  F.tube('st-sill',(x,280.5,z),(x,281.65,z),.035,6)
 F.lathe('st-blue',0,0,[(281.60,9.35),(281.68,9.35)],64)
 # Four banks of four outward-facing seats, parked at loading height.
 for k in range(4):
  a=k*math.pi/2;C=Frame(B,cx+4*math.sin(a),cz+4*math.cos(a),a,y=281)
  C.box('st-grey',(0,.25,0),(4.4,.45,1.5))
  for u in [-1.5,-.5,.5,1.5]:
   C.box('st-red',(u,.55,0),(.8,.18,.85));C.box('st-red',(u,1.15,-.35),(.8,1.1,.22))
   for dx in [-.27,.27]:
    C.tube('st-shadow',(u+dx,1.58,-.18),(u+dx,.85,.35),.07,8)
   C.tube('st-shadow',(u-.27,.85,.35),(u+.27,.85,.35),.07,8)
 # X-Scream: southwest-facing pivot/rails, carriage in the parked position.
 # Its tip projects beyond the observation ring; no invented ground-level building.
 R=Frame(B,cx-22,cz+10,math.pi/2+.20,y=268)
 for x in [-1.05,1.05]:
  R.box('st-white',(x,1.6,0),(.55,3.2,1.0),True)
  R.tube('st-grey',(x,0,3.5),(x,3.3,0),.18,10)
  R.tube('st-shadow',(x,3.45,-9),(x,3.45,10),.20,12)
  R.tube('st-shadow',(x,2.85,-9),(x,2.85,10),.16,10)
 for w in np.arange(-9,10,.8):
  R.tube('st-grey',(-1.05,3.35,float(w)),(1.05,3.35,float(w)),.09,8)
  for x in [-1.05,1.05]:R.tube('st-shadow',(x,2.85,float(w)),(x,3.45,float(w)+.8),.065,6)
 R.tube('st-sill',(-1.55,3.2,0),(1.55,3.2,0),.40,16)
 # Narrow platform and safety rails at the loading end, outside the central roof.
 R.box('st-roof',(0,.13,-5.5),(5,.26,7),True)
 for x in [-2.3,2.3]:
  for w in np.arange(-8.8,-1.9,.35):R.tube('st-sill',(x,.25,float(w)),(x,1.5,float(w)),.025,6)
  R.tube('st-sill',(x,1.5,-8.8),(x,1.5,-2),.055,8)
 R.box('st-ride-green-paint',(0,3.85,-4.2),(2.35,.55,5.6))
 for w in [-6.1,-4.8,-3.5,-2.2]:
  for x in [-.55,.55]:
   R.box('st-shadow',(x,4.2,w),(.85,.16,.9));R.box('st-shadow',(x,4.7,w-.35),(.85,1.05,.20))
   for dx in [-.28,.28]:R.tube('st-sill',(x+dx,5.05,w-.2),(x+dx,4.35,w+.38),.06,8)
   R.tube('st-sill',(x-.28,4.35,w+.38),(x+.28,4.35,w+.38),.06,8)
 # Blue handrail visible in reference, mounted on existing outer deck rail.
 F.lathe('st-blue',0,0,[(269.98,30.36),(270.18,30.36)],144)
 # Low equipment cabinets on upper machinery terrace.
 for x,z in [(-7,0),(7,0),(0,-7)]:
  F.box('st-grey',(x,281.2,z),(1.5,1.4,1.0),True)
