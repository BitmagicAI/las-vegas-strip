"""Original permanent former restaurant exterior from dated site photographs."""
from common import *
KEY='former-wendys-tropicana';IDS=['way/431504497']
def build(B):
 B.property=KEY+'-exterior';B.source='podium/'+KEY;B.detail=0
 p=footprint(IDS[0]);F=Frame(B,-1096.476,1723.671,.01004,y=0);w=11.07;d=23.17
 B.shell(p,.02,4.4,'wn-brick',roof=False);B.planar('wn-roof',p,4.12)
 E=Frame(B,*[F.p(w,0,0)[i] for i in (0,2)],F.yaw-math.pi/2,y=0)
 # Curved entrance crown at the north end of the east elevation.
 def top(x):return 5.35+.5*math.sin(math.pi*(x-.3)/10.8)
 for x in np.linspace(.3,11.1,37)[:-1]:
  xx=x+.3
  B.face('wn-red',[E.p(x,3.25,-.18),E.p(xx,3.25,-.18),E.p(xx,top(xx),-.18),E.p(x,top(x),-.18)])
  B.face('wn-coping',[E.p(x,top(x),-.32),E.p(xx,top(xx),-.32),E.p(xx,top(xx),.25),E.p(x,top(x),.25)])
  E.tube('wn-coping',(x,top(x),-.30),(xx,top(xx),-.30),.085,8)
 for x in [.55,10.85]:E.box('wn-stone',(x,2.72,-.22),(1.1,5.4,.52),True)
 for x in np.arange(1.15,10.4,.65):E.box('wn-joint',(x,4.31,-.195),(.014,2.12,.015))
 for y in [3.85,4.5,5.15]:E.box('wn-joint',(5.7,y,-.195),(9.1,.014,.015))
 E.box('wn-metal',(5.7,3.23,-.24),(9.2,.22,.31))
 # Glazed facade with closed door on the southern side; current interior is unknown.
 for x in np.arange(1.7,10.0,1.1):
  E.box('wn-recess',(x,1.73,-.08),(1.08,2.63,.16));E.box('wn-glass',(x,1.73,-.18),(1.01,2.55,.045))
  E.box('wn-metal',(x-.55,1.73,-.23),(.045,2.64,.07))
  E.box('wn-metal',(x,2.78,-.23),(1.1,.04,.07))
 for y in [.42,3.04]:E.box('wn-metal',(5.7,y,-.23),(9.2,.055,.08))
 for x in [8.25,9.34]:E.box('wn-metal',(x,1.70,-.28),(.06,2.64,.08))
 E.tube('wn-chrome',(9.17,1.20,-.35),(9.17,1.65,-.35),.018,8)
 # Service wing has brick walls, panel parapets and two drive-through bays.
 for x in [11.8,14.2,16.6,19,21.4]:
  E.box('wn-panel',(x,3.88,-.045),(2.36,1.03,.09))
  E.box('wn-joint',(x,3.88,-.105),(.018,1.03,.012))
 E.box('wn-coping',(17.1,4.45,-.05),(12.2,.16,.30));E.box('wn-metal',(17.1,3.30,-.09),(12.2,.12,.22))
 for x in [15,21.2]:
  E.box('wn-metal',(x,1.88,-.08),(1.6,1.65,.16));E.box('wn-glass',(x,1.88,-.19),(1.47,1.51,.05))
  E.box('wn-metal',(x,1.88,-.24),(.045,1.55,.06));E.box('wn-sill',(x,1.04,-.36),(1.75,.12,.65))
  for xx in [x-.95,x+.95]:E.box('wn-metal',(xx,2.0,-.10),(.15,.7,.16))
 a=19.6;b=22.8
 B.face('wn-canopy',[E.p(a,2.95,-1.2),E.p(b,2.95,-1.2),E.p(b,3.7,-.04),E.p(a,3.7,-.04)])
 E.box('wn-canopy',((a+b)/2,2.85,-1.2),(b-a,.25,.16))
 for x in np.arange(a,b,.45):E.tube('wn-coping',(x,2.98,-1.2),(x,3.72,-.04),.02,6)
 # North glazing and pale stone corner columns visible from Tropicana.
 for x in [2.1,4.4,6.7,9.0]:
  F.box('wn-metal',(x,1.9,-.07),(2.05,2.45,.14));F.box('wn-glass',(x,1.9,-.17),(1.92,2.32,.04));F.box('wn-metal',(x,1.9,-.21),(.045,2.36,.06))
 F.box('wn-panel',(w/2,3.82,-.07),(w,1.08,.14));F.box('wn-coping',(w/2,4.46,0),(w+.2,.15,.30))
 for x in [.4,w-.4]:F.box('wn-stone',(x,2.25,-.10),(.8,4.5,.3))
 W=Frame(B,*[F.p(0,0,d)[i] for i in (0,2)],F.yaw+math.pi/2,y=0)
 W.box('wn-panel',(d/2,3.88,-.06),(d,1.0,.12));W.box('wn-coping',(d/2,4.46,0),(d,.15,.3))
 S=Frame(B,*[F.p(w,0,d)[i] for i in (0,2)],F.yaw+math.pi,y=0)
 S.box('wn-panel',(w/2,3.88,-.06),(w,1.0,.12));S.box('wn-coping',(w/2,4.46,0),(w,.15,.3))
 S.box('wn-metal',(3,1.50,-.09),(1.25,2.7,.18));S.box('wn-service',(3,1.5,-.20),(1.10,2.55,.05))
 for z in [15,20]:
  F.box('wn-equipment',(5.5,4.8,z),(2.5,1.05,1.8));F.box('wn-metal',(5.5,5.37,z),(2.65,.10,1.95))
  for zz in np.arange(z-.7,z+.7,.16):F.box('wn-joint',(5.5,4.8,zz),(2.53,.04,.03))
 for G,L in [(E,d),(F,w)]:G.box('wn-paving',(L/2,.245,-1.7),(L+.3,.15,3.4),True)
 for x in [.55,10.85]:
  E.box('wn-metal',(x,2.6,-.52),(.25,.38,.12));E.box('wn-light',(x,2.6,-.59),(.17,.24,.025))
 routes=[dict(name='East entrance and service frontage',points=[E.p(x,.32,-2.0) for x in [1.5,8.8,15,21.5]]),dict(name='North frontage',points=[F.p(x,.32,-2) for x in [1,5.5,10]])]
 return dict(key=KEY,name='3333 West Tropicana former restaurant',center=[-1090,0,1735],bounds=[-1099,1719,-1080,1750],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=routes,hotelSources=[])
if __name__=='__main__':
 B=Meshes();meta=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(meta,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
