"""Original dated-reference station exterior; unverified shop remains closed."""
from common import *
KEY='standard-tropicana';IDS=['way/431497409','way/431497411']
def build(B):
 B.property=KEY+'-exterior';B.source='podium/'+KEY;B.detail=0
 F=Frame(B,-976.505,1744.499,.00455,y=0);w=14;d=25.69
 p=footprint(IDS[1]);B.shell(p,.02,4.5,'st-stucco',roof=False);B.planar('st-roof',p,4.25);B.shell(p.buffer(.035,join_style=2),.02,.85,'st-base',roof=False,solid=False)
 E=Frame(B,*[F.p(w,0,0)[i] for i in (0,2)],F.yaw-math.pi/2,y=0)
 for G,L in [(F,w),(E,d)]:
  G.box('st-trim',(L/2,4.55,-.06),(L+.2,.18,.26))
  for x in ([3,7,11] if G is F else [3,7,15.5,19.5,23]):
   G.box('st-metal',(x,1.95,-.08),(2.8,2.1,.16));G.box('st-glass',(x,1.95,-.18),(2.66,1.98,.04));G.box('st-metal',(x,1.95,-.22),(.045,2,.05))
  G.box('st-paving',(L/2,.23,-1.5),(L+.3,.18,3),True)
 # East entrance projection and shallow hipped tile crown from 2019 site photograph.
 E.box('st-stucco',(11,3.9,-.35),(5.1,2.3,.7))
 E.box('st-trim',(11,5.1,-.35),(5.4,.15,1))
 roof=[(8.15,-.95),(13.85,-.95),(13.85,3),(8.15,3)]
 for a,b in zip(roof,roof[1:]+roof[:1]):B.face('st-tile',[E.p(a[0],5.2,a[1]),E.p(b[0],5.2,b[1]),E.p(11,6.2,1)])
 E.box('st-metal',(11,1.75,-.12),(2.6,2.85,.24));E.box('st-glass',(11,1.75,-.27),(2.44,2.70,.05))
 for x in [9.72,11,12.28]:E.box('st-metal',(x,1.75,-.32),(.055,2.8,.06))
 for x in [10.8,11.2]:E.tube('st-metal',(x,1.1,-.4),(x,1.65,-.4),.02,8)
 E.box('st-red',(11,4.4,-.74),(4.7,.95,.12));E.text("TERRIBLE'S",(11,4.4,-.83),.60,'st-white');E.text('3201',(11,3.15,-.38),.28,'st-white')
 F.box('st-red',(7,3.85,-.13),(5.0,.85,.16));F.text("TERRIBLE'S",(7,3.85,-.23),.53,'st-white')
 for z in [6,20]:F.box('st-equipment',(6.5,4.9,z),(2.6,1.1,1.8))
 # Mapped fuel canopy: open underside, two longitudinal island rows, no solid box.
 C=Frame(B,-943.457,1737.263,.00437,y=0);cw=11.933;cd=26.784
 canopy=footprint(IDS[0]);B.planar('st-paving',canopy,.32,True);B.planar('st-soffit',canopy,5.15);B.planar('st-roof',canopy,5.8);B.shell(canopy,5.15,5.8,'st-blue',roof=False,solid=False)
 for G,L in [(C,cw),(Frame(B,*[C.p(cw,0,0)[i] for i in (0,2)],C.yaw-math.pi/2,y=0),cd)]:G.text('Standard',(L/2,5.48,-.05),.5,'st-white')
 for x in [2.6,9.3]:
  for iz,z in enumerate([4.5,13.4,22.3]):
   C.box('st-paving',(x,.17,z),(1.8,.34,3.4),True)
   C.box('st-white',(x,2.75,z+.72),(.45,4.8,.45),True)
   C.box('st-base',(x,.9,z+.72),(.64,1.45,.64),True)
   C.box('st-white',(x,1.36,z-.55),(.80,2.1,.7),True);C.box('st-blue',(x,2.48,z-.55),(.96,.27,.85))
   for side in [-1,1]:
    C.box('st-black',(x,1.8,z-.55+side*.36),(.62,.53,.025));C.box('st-display',(x,1.86,z-.55+side*.38),(.43,.22,.015))
    C.box('st-black',(x+.24,1.34,z-.55+side*.37),(.12,.08,.02))
    C.path('st-black',[(x+side*.42,2.22,z-.55),(x+side*.7,1.7,z-.55),(x+side*.65,.65,z-.55),(x+side*.42,.95,z-.55),(x+side*.42,1.5,z-.55)],.028,8)
   for zz in [z-1.5,z+1.5]:C.lathe('st-white',x,zz,[(.2,.065),(1.1,.065),(1.15,0)],10)
   C.box('st-light',(x,5.12,z),(.85,.05,1.1))
 # Slender roadside two-post pylon; price numerals deliberately omitted as time-dependent.
 P=Frame(B,-930,1724,0,y=0)
 for x in [-1.1,1.1]:P.box('st-metal',(x,5.6,0),(.17,11.2,.17),True)
 P.box('st-blue',(0,9.75,0),(2.1,2.5,.26));P.text('Standard',(0,10.45,-.15),.29,'st-white')
 for y,mat in [(10,'st-white'),(9.5,'st-red')]:
  B.face(mat,[P.p(-.75,y+.18,-.15),P.p(0,y-.05,-.15),P.p(.75,y+.18,-.15),P.p(.75,y-.10,-.15),P.p(0,y-.33,-.15),P.p(-.75,y-.10,-.15)])
 routes=[dict(name='Store frontage',points=[E.p(x,.32,-1.8) for x in [1.5,8,14,23]]),dict(name='Canopy centre lane',points=[C.p(6,.32,z) for z in [1.5,9,17,25]])]
 return dict(key=KEY,name='3201 Tropicana station',center=[-950,0,1753],bounds=[-980,1722,-928,1773],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=routes,hotelSources=[])
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
