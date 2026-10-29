"""Original Herbs & Rye architecture. Public arrangement inferred from attributed photos."""
from common import *
KEY='herbs-rye'; ID='way/764345678'; YAW=math.pi

def build(B):
 p=footprint(ID);F=Frame(B,-1685.46,-3121.69,YAW,y=0)
 B.property=KEY+'-exterior';B.source='podium/'+KEY;B.detail=0
 entry=dict(p=F.p(5.1,.16,0),yaw=YAW,width=1.65,height=2.55,name='Public dining entrance',venue=KEY)
 B.shell(p,.05,4.8,'hr-stucco',roof=False,openings=[entry]);B.planar('hr-roof',p,4.6);B.planar('hr-foundation',p,.16,True)
 for u in [-10,-5.5,2.7,10]:F.box('hr-trim',(u,2.45,.10),(.23,4.75,.19),True)
 F.box('hr-trim',(-2.885,.28,.08),(14.23,.42,.16));F.box('hr-trim',(7.985,.28,.08),(4.03,.42,.16))
 F.box('hr-stucco',(0,4.79,.04),(20.2,.16,.25))
 # Continuous paved apron, above grade, with an unobstructed doorway.
 F.box('hr-paving',(0,.08,.8),(20.6,.16,1.7),True)
 for u in np.arange(-10,10,.45):F.box('hr-joint',(float(u),.165,.8),(.012,.005,1.6))
 for v in [.2,.65,1.1,1.55]:F.box('hr-joint',(0,.165,v),(20.5,.005,.012))
 # Sloped black fabric canopy with closed end triangles; open below.
 for a,b in [(3.0,10.0)]:
  B.face('hr-awning',[F.p(a,3.55,.12),F.p(b,3.55,.12),F.p(b,2.95,1.4),F.p(a,2.95,1.4)])
  for u in [a,b]:B.face('hr-awning',[F.p(u,3.55,.12),F.p(u,2.95,1.4),F.p(u,2.95,.12)])
  F.box('hr-awning',((a+b)/2,2.91,1.4),(b-a,.13,.045))
  for u in [3.05,6.5,9.95]:F.tube('hr-metal',(u,2.97,.1),(u,2.97,1.35),.025,8)
 for u in [4.23,5.97]:F.box('hr-metal',(u,1.44,.13),(.10,2.65,.18))
 F.box('hr-metal',(5.1,2.78,.13),(1.85,.12,.18))
 F.text('Herbs & Rye',(-1.6,3.8,.22),.72,'hr-sign',back=True)
 F.box('hr-metal',(-7.8,2.95,.18),(3.8,1.13,.12));F.box('hr-board',(-7.8,2.95,.255),(3.64,.98,.025))
 for h in [2.65,2.85,3.05,3.25]:F.box('hr-trim',(-7.8,h,.28),(3.60,.012,.015))
 F.text('COCKTAILS',(-7.8,3.17,.29),.18,'hr-metal',back=True);F.text('STEAKS & SPIRITS',(-7.8,2.85,.29),.17,'hr-metal',back=True)
 F.box('hr-metal',(3.8,1.9,.20),(.3,.23,.06));F.box('hr-metal',(8.5,.57,.65),(.5,.96,.48),True);F.box('hr-board',(8.5,.7,.905),(.36,.49,.015))
 for u in [-9.8,9.8]:F.box('hr-metal',(u,4.6,.15),(.24,.19,.30))
 for u,v in [(-6,-20),(3,-19),(6,-22)]:
  F.box('hr-metal',(u,4.92,v),(1.8,.64,1.4));F.box('hr-roof',(u,5.28,v),(1.9,.08,1.5))
 # Public rooms only. Rear kitchen and private rooms remain a closed envelope.
 B.property=KEY+'-interior';B.source='public/'+KEY
 F.box('hr-floor',(0,.18,-8),(19.4,.03,15.8));F.box('hr-ceiling',(0,3.35,-8),(19.4,.15,16))
 for u in [-9.7,9.7]:
  F.box('hr-wallpaper',(u,1.77,-8),(.16,3.14,16),True)
  F.box('hr-wood',(u,.76,-8),(.20,1.15,15.9));F.box('hr-wood',(u,1.37,-8),(.25,.08,15.9))
 F.box('hr-wallpaper',(0,1.77,-15.95),(19.4,3.14,.15),True);F.box('hr-wood',(0,.76,-15.82),(19.3,1.15,.12));F.box('hr-wood',(0,1.37,-15.75),(19.3,.08,.16))
 for a,b in [(-9.7,4.22),(5.98,9.7)]:
  F.box('hr-wallpaper',((a+b)/2,1.77,-.12),(b-a,3.14,.12));F.box('hr-wood',((a+b)/2,.76,-.22),(b-a,1.15,.12))
 F.box('hr-wood',(5.1,3.02,-.16),(1.76,.60,.18))
 # Recessed wainscot panels, not coplanar overlays.
 for side in [-1,1]:
  for v in np.arange(-1,-15,-1.25):
   F.box('hr-darkwood',(side*9.57,.77,float(v)),(.04,.88,1.08))
 # Plank joints and slight alternating tint provide physical scale.
 for k,u in enumerate(np.arange(-9.55,9.65,.23)):
  for j in range(6):
   v=-.2-j*2.65-(k%3)*.35;lo=max(-15.85,v-2.61);hi=min(-.1,v)
   if hi>lo:F.box('hr-plank-'+str((k+j)%4),(float(u),.201,(lo+hi)/2),(.222,.006,hi-lo))
 def chair(u,v,yaw=0):
  C=Frame(B,*[F.p(u,0,v)[i] for i in [0,2]],YAW+yaw,y=0)
  C.lathe('hr-wood',0,0,[(.59,.26),(.66,.26)],20)
  for dx in [-.19,.19]:
   for dz in [-.19,.19]:C.tube('hr-wood',(dx,.2,dz),(dx,.61,dz),.032,8)
  C.path('hr-wood',[(-.23,.62,.20),(-.25,1.12,.25),(-.20,1.23,.26),(.20,1.23,.26),(.25,1.12,.25),(.23,.62,.20)],.035,10)
  for dx in [-.14,-.07,0,.07,.14]:C.tube('hr-wood',(dx,.7,.22),(dx*1.3,1.19,.25),.014,8)
 def table(u,v):
  F.box('hr-wood',(u,.92,v),(1.45,.07,.92),True)
  for dx in [-.59,.59]:
   for dz in [-.34,.34]:F.box('hr-darkwood',(u+dx,.53,v+dz),(.065,.73,.065))
  for dx in [-.4,.4]:
   F.lathe('hr-plate',u+dx,v+.1,[(.96,.15),(.98,.17),(.985,.15),(.975,.1)],24)
   F.box('hr-napkin',(u+dx,.999,v+.12),(.2,.025,.10))
   F.lathe('hr-glass',u+dx,v-.25,[(.96,.055),(.97,.055),(.98,.01),(1.07,.01),(1.09,.04),(1.20,.055)],20)
  chair(u,v-.9,math.pi);chair(u,v+.9)
 for u in [-1.7,2.0,7.5]:
  for v in [-4,-7.5,-11]:table(u,v)
 # Photo-supported wood and bottles; placement inferred, clear public aisle along its front.
 F.box('hr-darkwood',(-7, .72,-7.3),(1.1,1.08,10.5),True);F.box('hr-metal',(-7,1.30,-7.3),(1.30,.09,10.7))
 F.tube('hr-brass',(-6.25,.40,-2.1),(-6.25,.40,-12.5),.04,12)
 for v in np.arange(-2.4,-12.4,-1.5):
  F.lathe('hr-wood',-5.75,float(v),[(.20,.30),(.27,.30),(.29,.05),(.84,.05),(.88,.25),(.96,.25)],16)
 for h in [.5,1.45,2.15,2.85]:F.box('hr-wood',(-9.25,h,-7.3),(.62,.08,10.5))
 for v in np.arange(-2.4,-12.4,-.42):
  for h in [1.50,2.20]:
   F.lathe('hr-bottle-'+str(int(abs(v)*10)%3),-9.24,float(v),[(h,.065),(h+.24,.065),(h+.29,.027),(h+.38,.027)],10)
   F.box('hr-label',(-9.17,h+.13,float(v)),(.012,.12,.085))
 # Small chandelier fixtures, wall sconces and original framed geometric panels.
 for u in [-1.7,4.8]:
  for v in [-4,-10]:
   F.tube('hr-brass',(u,3.30,v),(u,2.65,v),.023,10)
   F.path('hr-brass',[(u+.42*math.cos(a),2.63,v+.42*math.sin(a)) for a in np.linspace(0,math.tau,25)],.025,8)
   for a in np.linspace(0,math.tau,6,endpoint=False):
    x=u+.42*math.cos(a);z=v+.42*math.sin(a);F.lathe('hr-lamp',x,z,[(2.65,.045),(2.82,.045),(2.85,.015)],10)
    F.lathe('hr-glass',x,z,[(2.45,0),(2.51,.035),(2.58,0)],10)
 for u in [-5,0,5]:
  F.box('hr-brass',(u,2.25,-15.68),(1.4,.95,.07));F.box('hr-art',(u,2.25,-15.63),(1.27,.82,.025))
  for radius in [.12,.24,.36]:
   F.path('hr-brass',[(u+radius*math.cos(a),2.25+radius*math.sin(a),-15.60) for a in np.linspace(0,math.tau,5)],.012,6)
  F.box('hr-brass',(u+1.0,2.12,-15.56),(.12,.38,.15));F.lathe('hr-lamp',u+1,-15.42,[(2.12,.06),(2.32,.12),(2.38,.06)],12)
 for v in [-4,-11]:F.light(1,2.8,v,power=90,range=14)
 F.light(-7.6,2.8,-7,power=60,range=10)
 route=[F.p(u,.20,v) for u,v in [(5.1,2),(5.1,-1),(5.1,-5),(4,-8.5),(0,-8.5),(-4,-8.5)]]
 views={n:dict(eye=F.p(*e),target=F.p(*t)) for n,e,t in [('entrance',(5.1,1.8,3),(5.1,1.4,-5)),('dining',(5.1,1.8,-2),(2,1.5,-11)),('bar',(-3.6,1.8,-8),(-8,1.4,-7)),('rear',(4,1.8,-12),(0,1.8,-15.8))]}
 return dict(key=KEY,name='Herbs & Rye',center=[p.centroid.x,0,p.centroid.y],bounds=[p.bounds[0]-1,p.bounds[1]-2,p.bounds[2]+1,p.bounds[3]+1],structural=True,exteriorOnly=False,portals=[entry],zones=[dict(origin=F.p(0,.16,0),yaw=YAW+math.pi,width=19.4,depth=16,height=3.1)],lights=B.lights,hotelSources=[],routes=[dict(name='Entrance, dining and bar',points=route)],views=views)
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
