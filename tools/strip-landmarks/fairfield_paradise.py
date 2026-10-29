"""Original Fairfield exterior and photo-supported fitted public lobby."""
from common import *
KEY='fairfield-paradise';IDS=['way/565876914']
def build(B):
 p=footprint(IDS[0]);B.property=KEY+'-exterior';B.source='hotel/'+KEY;B.detail=0
 R=Frame(B,1659.37,-408.1,math.pi/2,y=0)
 door=dict(p=R.p(0,.28,0),yaw=R.yaw,width=2.6,height=2.8,name='Fairfield public lobby',venue=KEY)
 opening=dict(p=R.p(0,.28,0),yaw=R.yaw,width=11.6,height=3.65)
 B.shell(p,.02,14.6,'ff-stucco',roof=False,openings=[opening]);B.planar('ff-membrane',p,14.6)
 # Every wing follows the actual dogleg outline; frame bands and recessed windows.
 ring=list(p.exterior.coords)
 for a,b in zip(ring,ring[1:]):
  dx,dz=b[0]-a[0],b[1]-a[1];L=math.hypot(dx,dz);G=Frame(B,(a[0]+b[0])/2,(a[1]+b[1])/2,math.atan2(-dz,dx),y=0)
  for y,h in [(.35,.7),(14.2,1.05)]:G.box('ff-border',(0,y,0),(L,h,.26))
  for u in [-L/2+.23,L/2-.23]:G.box('ff-border',(u,7.3,0),(.46,14.6,.32))
  if L<7:continue
  n=max(1,int((L-3)/3.4));positions=np.linspace(-L/2+2,L/2-2,n)
  for u in positions:
   for y in [2.25,5.65,9.05,12.45]:
    wpos=G.p(float(u),y,0)
    if y<4 and wpos[0]<1660 and abs(wpos[2]+408.1)<6.6:continue
    for side in [-1,1]:
     G.box('ff-trim',(float(u),y,side*.055),(1.65,1.85,.16))
     G.box('ff-glass',(float(u),y+.08,side*.15),(1.39,1.39,.035))
     G.box('ff-alloy',(float(u),y+.08,side*.18),(.055,1.39,.025))
     G.box('ff-vent',(float(u),y-.65,side*.18),(1.38,.23,.03))
     for q in [-.07,0,.07]:G.box('ff-trim',(float(u),y-.65+q,side*.20),(1.3,.02,.012))
 W=Frame(B,1659.25,-408.1,-math.pi/2,y=0)
 # Tall blank brand pier from official photograph, independent of window rhythm.
 W.box('ff-stucco',(-6.2,7.3,.24),(3.2,14.6,.18))
 W.text('Fairfield',(-5.8,12.8,.36),.67,'ff-letter',back=True);W.text('BY MARRIOTT',(-5.8,12.18,.36),.23,'ff-letter',back=True)
 # Curved broad canopy, smoothly rising on one side, supported by stone and metal.
 def cy(u):return 4.7+1.2*(.5+.5*math.cos((u+2)*math.pi/14))
 us=np.linspace(-7,7,29)
 for a,b in zip(us,us[1:]):
  for yoff,mat in [(0,'ff-ceiling'),(.32,'ff-border')]:B.face(mat,[W.p(float(a),cy(a)+yoff,1),W.p(float(b),cy(b)+yoff,1),W.p(float(b),cy(b)+yoff,16),W.p(float(a),cy(a)+yoff,16)],True)
  for v in [1,16]:B.face('ff-border',[W.p(float(a),cy(a),v),W.p(float(b),cy(b),v),W.p(float(b),cy(b)+.32,v),W.p(float(a),cy(a)+.32,v)])
 for u in [-7,7]:W.box('ff-border',(u,cy(u)+.16,8.5),(.14,.32,15))
 for u,v in [(5.2,13.8),(-5.4,2.4)]:
  h=cy(u)+.8;W.box('ff-stone',(u,h/2,v),(1.7,h,1.7),True)
  for y in np.arange(.3,h,.22):
   W.box('ff-joint',(u,float(y),v+.86),(1.68,.015,.018));W.box('ff-joint',(u+.86,float(y),v),(.018,.015,1.68))
 for u in [-4.8,-4.35]:W.tube('ff-alloy',(u,.28,12),(u,cy(u),12),.075)
 for u in [-4,0,4]:
  for v in [4,9,14]:W.box('ff-lamp',(u,cy(u)-.025,v),(.17,.04,.17))
 # Glazed entrance panels surround a genuinely open central doorway.
 for u in [-3.65,3.65]:
  R.box('ff-clear',(u,1.95,.10),(4.6,3.25,.045),True)
 for u in [-5.8,-1.3,1.3,5.8]:R.box('ff-trim',(u,1.94,.10),(.09,3.3,.12),True)
 R.box('ff-trim',(0,3.62,.10),(11.6,.12,.14))
 B.upface('ff-paving',[R.p(-1.5,.01,-4),R.p(1.5,.01,-4),R.p(1.5,.28,.3),R.p(-1.5,.28,.3)],True)
 for x,z in [(1672,-410),(1682,-410),(1700,-417),(1714,-417),(1726,-417)]:
  Q=Frame(B,x,z,0,y=0);Q.box('ff-equipment',(0,15.05,0),(2.5,.9,1.8));Q.box('ff-vent',(0,15.52,0),(2.2,.045,1.5))
 for u in [-8.2,8.2]:W.plant(u,13)
 # Public lobby only: inferred arrangement of official photographed furniture/finishes.
 B.property=KEY+'-interior';B.source='interior/'+KEY;B.detail=1
 room=R.poly([(-5.8,.05),(5.8,.05),(5.8,12),(-5.8,12)])
 B.shell(room,.28,3.9,'ff-wall',roof=False,openings=[opening]);B.planar('ff-floor',room,.28,True);B.planar('ff-ceiling',room,3.9)
 for u in np.arange(-5.6,5.8,.24):R.box('ff-joint',(float(u),.284,6.03),(.009,.006,11.9))
 for v in np.arange(.4,12,1.6):
  for u in np.arange(-5.6,5.8,.48):R.box('ff-joint',(float(u),.284,float(v+(.3 if int(u*10)%2 else 0))),(.24,.006,.009))
 for u in [-3.7,3.7]:
  R.box('ff-wall',(u,2.1,5.6),(.6,3.65,.6),True);R.box('ff-trim',(u,.4,5.6),(.67,.25,.67))
 R.box('ff-green',(0,2.1,11.93),(11.4,3.5,.04))
 # Original circular relief; no copied wall artwork.
 for i in range(24):
  a=i*math.tau/24;R.box('ff-letter',(1.6*math.cos(a),2.35+1.1*math.sin(a),11.88),(.13,.13,.04))
 R.box('ff-stone',(2.5,.89,9.6),(5,1.22,1.15),True);R.box('ff-counter',(2.5,1.55,9.6),(5.15,.11,1.3))
 for u in [.05,1.28,2.5,3.72,4.95]:R.box('ff-joint',(u,.91,9.018),(.008,1.10,.012))
 R.box('ff-trim',(2.5,.34,9.01),(4.9,.10,.03))
 for u in [1,3.7]:R.box('ff-trim',(u,1.79,9.85),(.6,.38,.08));R.box('ff-trim',(u,1.62,9.84),(.08,.2,.1))
 # Lounge with spindle chairs, upholstered cushions, sofa, tables and low divider.
 R.box('ff-wood',(-3.5,.88,6.7),(4,1.2,.2),True)
 def chair(u,v):
  for a in [-.36,.36]:
   for b in [-.32,.32]:R.box('ff-wood',(u+a,.53,v+b),(.065,.5,.065))
   R.box('ff-wood',(u+a,.94,v),(.07,.08,.8))
  R.box('ff-green',(u,.8,v),(.72,.18,.7),True);R.box('ff-green',(u,1.16,v+.35),(.72,.62,.14),True)
  for a in np.linspace(-.34,.34,6):R.box('ff-wood',(u+float(a),1.13,v+.45),(.025,.65,.03))
 for u,v in [(-4.4,3),(-2.2,3),(-4.4,5.1)]:chair(u,v)
 R.box('ff-sofa',(-2.7,.78,5.5),(2.25,.8,.8),True);R.box('ff-sofa',(-2.7,1.12,5.84),(2.25,.75,.16),True)
 for u in [-3.8,-1.6]:R.box('ff-sofa',(u,1.02,5.5),(.18,.5,.8))
 R.lathe('ff-trim',-3.3,4.2,[(.28,.33),(.34,.33),(.36,.05),(.77,.05)],20);R.lathe('ff-counter',-3.3,4.2,[(.77,.58),(.83,.58)],32)
 for u in [-3,1.5,4]:
  for v in [2,6,10]:R.box('ff-lamp',(u,3.87,v),(.22,.025,.22))
 routes=[dict(name='Arrival and lobby',points=[R.p(0,.28,v) for v in [-16,-8,-4,-1,1,4,7,8]]),dict(name='South hotel walk',points=[[x,.28,-393] for x in [1642,1655,1670,1686,1700,1715,1738]])]
 return dict(key=KEY,name='Fairfield Inn Paradise',center=[1695,0,-411],bounds=list(p.bounds),structural=True,hotelSources=[],exteriorOnly=False,portals=[door],zones=[dict(origin=R.p(0,.28,0),yaw=R.yaw,width=11.8,depth=12.2,height=4)],lights=[dict(p=R.p(u,3.4,v),color=0xffefd4,power=4,range=8) for u,v in [(-3,3),(3,3),(-3,9),(3,9)]],routes=routes)
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
