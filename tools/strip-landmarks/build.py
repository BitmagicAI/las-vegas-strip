"""Five individually authored Strip landmarks. Photos inform detail; OSM owns siting."""
from common import *
B=Meshes();venues=[];replacement=set();towers=[]
def enter(key,layer='exterior',source=''):
 B.property=key+'-'+layer;B.source=source;B.detail=0
def rect(x,z,w,d):return box(x-w/2,z-d/2,x+w/2,z+d/2)
def entry_on(poly,near,min_length=13):
 # Choose the outer facade, not a tower/courtyard hole; stay clear of corners.
 candidates=[]
 for a,b in zip(list(poly.exterior.coords),list(poly.exterior.coords)[1:]):
  edge=LineString([a,b])
  if edge.length<min_length:continue
  margin=6 if min_length>=13 else min(6,edge.length*.24);q=edge.interpolate(max(margin,min(edge.length-margin,edge.project(Point(*near)))))
  candidates.append((q.distance(Point(*near)),edge,q))
 _,edge,p=min(candidates,key=lambda v:v[0]);a,b=edge.coords
 dx,dz=b[0]-a[0],b[1]-a[1];L=edge.length;nx,nz=-dz/L,dx/L
 if not poly.contains(Point(p.x+nx*.25,p.y+nz*.25)):nx,nz=-nx,-nz
 return Frame(B,p.x,p.y,math.atan2(nx,nz))
def venue(key,name,shape,frame,width,depth,height,portal):
 center=shape.centroid
 spec=dict(key=key,name=name,center=[center.x,0,center.y],bounds=list(shape.bounds),portals=[portal],lights=[],zones=[],views={},hotelSources=[])
 spec['zones'].append(dict(origin=frame.p(0,0,0),yaw=frame.yaw,width=width,depth=depth,height=height))
 spec['views']['entrance']=dict(eye=frame.p(3,2,-23),target=frame.p(0,5,6))
 spec['views']['lobby']=dict(eye=frame.p(1,1.7,5),target=frame.p(0,2.5,min(depth-4,27)))
 venues.append(spec);return spec
def arrival(F,p,w,h,floor=True):
 # Full glazed entrance wall, inset bronze/steel door surrounds and side lights.
 for side in [-1,1]:
  ww=(w-p['width'])/2
  F.box('glass',(side*(p['width']/2+ww/2),h/2,-.035),(ww,h,.075),True)
  for x in np.arange(p['width']/2+.08,w/2,.95):F.box('steel',(side*x,h/2,-.13),(.065,h,.15))
 F.box('glass',(0,(h+p['height'])/2,-.035),(p['width'],h-p['height'],.08))
 for yy in [0,p['height'],h]:F.box('steel',(0,yy,-.13),(w,.10,.15))
 if floor:F.floor(w+5,8,-4,'tile')
 for xx in [-w/2-1.2,w/2+1.2]:
  F.plant(xx,-4);F.tube('silver',(xx,0,-7),(xx,.95,-7),.08,12)
 for side in [-1,1]:
  F.box('walnut',(side*(w/2+.7),h/2,-.22),(1.0,h+.4,.65));F.box('warm',(side*(w/2+.1),h/2,-.6),(.06,h-.3,.04))
 for x in np.arange(-w/2+1,w/2,2.5):F.box('warm',(x,h+.03,-2.0),(.6,.035,.6))
 return {**p,'width':w,'height':h}
def carpet(F,x,z,w,d,color='carpet'):
 F.box(color,(x,.027,z),(w,.022,d))
 for xx in [x-w/2,x+w/2]:F.box('brass',(xx,.04,z),(.06,.012,d))
def lightbox(F,x,y,z,w,h,text):
 F.box('charcoal',(x,y,z),(w+.12,h+.12,.10));F.box('screen',(x,y,z-.07),(w,h,.03));F.text(text,(x,y-.15,z-.1),min(.45,w/(len(text)*.7)),'letter')
def cornice(poly,y,mat='stone',thick=.2):
 for p in parts(poly):
  for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
   B.tube(mat,(a[0],y,a[1]),(b[0],y,b[1]),thick,4)
def facade(poly,lo,hi,style='linq',opening=(),roof=True):
 wall={'linq':'white','vanderpump':'sandstone','venetian':'pinkstone','fashion':'ivory'}[style]
 B.shell(poly,lo,hi,wall,opening,roof)
 B.detail=1
 for p in parts(poly):
  for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
   L=math.dist(a,b)
   if L<1:continue
   ux,uz=(b[0]-a[0])/L,(b[1]-a[1])/L;nx,nz=-uz,ux
   if p.contains(Point((a[0]+b[0])/2+nx*.1,(a[1]+b[1])/2+nz*.1)):nx,nz=-nx,-nz
   F=Frame(B,a[0]+nx*.12,a[1]+nz*.12,math.atan2(-nx,-nz),y=0)
   # Local +X follows the outward-facing facade. Reverse edge origin if needed.
   if F.co*ux-F.si*uz<0:F=Frame(B,b[0]+nx*.12,b[1]+nz*.12,F.yaw,y=0)
   cols=max(1,round(L/(2.7 if style=='linq' else 3.3)));cw=L/cols
   for j in range(cols):
    x=(j+.5)*cw
    for row,y in enumerate(np.arange(lo+.8,hi-2,3.2)):
     if style=='linq':
      color=['blue','blue2','blue3','white','blue2','white','white','red'][((j*7+row*11)%17)%8]
      F.box(color,(x,y+1.0,0),(cw-.08,3.10,.12));F.box('darkglass',(x,y+.92,-.095),(cw*.74,1.57,.05));F.box('silver',(x,y+.09,-.14),(cw*.79,.08,.08))
     elif style=='vanderpump':
      F.box('charcoal',(x,y+1,-.03),(cw*.76,2.6,.10));F.box('darkglass',(x,y+1,-.11),(cw*.65,2.33,.03))
      for xx in [x-cw*.36,x+cw*.36]:F.box('bronze',(xx,y+1,-.16),(.10,2.65,.12))
      F.box('sandstone',(x,y+2.38,-.10),(cw*.9,.22,.3));F.box('bronze',(x,y+.20,-.4),(cw*.85,.09,.55))
      for yy in [y+.25,y+.95]:F.box('blackiron',(x,yy,-.62),(cw*.84,.045,.045))
      for xx in np.arange(x-cw*.39,x+cw*.4,.21):F.box('blackiron',(xx,y+.59,-.62),(.025,.7,.035))
     elif style=='venetian':
      F.box('darkglass',(x,y+.9,-.02),(cw*.68,1.9,.08));F.arch(x,-.15,cw*.77,y+2.3,'ivory',.10,y-.1)
     else:
      F.box('darkglass',(x,y+1,-.02),(cw-.24,2.7,.08));F.box('silver',(x-cw/2,y+1,-.09),(.12,3.2,.12))
   for y in np.arange(lo,hi,3.2):F.box('ivory' if style=='vanderpump' else 'silver',(L/2,y,-.01),(L,.12,.18))
 B.detail=0
 cornice(poly,hi-.3,'stone' if style=='vanderpump' else 'silver',.20)
def atrium(F,w,d,h,style='modern',front=True,rear=True,wall_opening=None):
 F.floor(w,d,d/2,'marble' if style=='classic' else 'tile')
 F.box('plaster',(0,h+.12,d/2),(w,.24,d))
 for s in [-1,1]:
  mat='panel' if style=='classic' else 'plaster'
  if wall_opening is None:F.box(mat,(s*w/2,h/2,d/2),(.3,h,d),True)
  else:
   wall=F.poly([(s*w/2-.15,0),(s*w/2+.15,0),(s*w/2+.15,d),(s*w/2-.15,d)]).difference(wall_opening)
   F.b.extrude(mat,wall,F.y,F.y+h,True)
 if rear:F.box('panel',(0,h/2,d),(w,h,.3),True)
 if front:
  for s in [-1,1]:F.box('glass',(s*(w/4+1.6),2.3,0),(w/2-3.2,4.6,.10),True)
  F.box('stone',(0,(h+4.7)/2,0),(w,h-4.7,.22),True)
 for z in np.arange(3,d,6):
  F.box('warm',(0,h-.10,z),(w-2,.05,.07));F.light(0,h-.5,z,0xffe7cc,260,14)
  for x in [-w/2+.6,w/2-.6]:F.box('brass',(x,h-.2,z),(.16,.28,5.5))
  if style=='classic':
   F.chandelier(0,z,h-1.2)
   for x in [-w/2+2,w/2-2]:F.lathe('ivory',x,z,[(0,.38),(.15,.46),(.3,.31),(h-.6,.31),(h-.3,.47),(h,.47)],24)
 for x in np.arange(-w/2+1,w/2,1.5):F.box('grout',(x,.012,d/2),(.018,.015,d-.1))
 for z in np.arange(.5,d,1.5):F.box('grout',(0,.014,z),(w-.1,.014,.018))
 for x in [-w/2+.8,w/2-.8]:F.box('brass',(x,.025,d/2),(.06,.015,d-.1))
def shop(F,x,z,label,width=8,classic=False):
 F.box('shopglass',(x,2.6,z),(width,5,.10));F.box('charcoal' if not classic else 'walnut',(x,5.2,z),(width+.2,.85,.30));F.text(label,(x,5.13,z-.19),min(.48,(width-.7)/(len(label)*.6)))
 for xx in [x-width/2,x+width/2]:F.box('ivory',(xx,2.6,z),(.2,5.2,.3))
 F.box('warm',(x,4.5,z-.07),(width-.4,.055,.05))
 # Window displays have actual shelving and pedestals behind tinted glazing.
 for dx in [-width*.27,0,width*.27]:
  F.box('stone',(x+dx,.6,z+.5),(1,1.2,.8));F.box('bronze',(x+dx,1.45,z+.5),(.35,.50,.25))
def rear_portal(F,width,opening,depth,height):
 for side in [-1,1]:F.box('panel',(side*(width+opening)/4,height/2,depth),((width-opening)/2,height,.3),True)
 F.box('panel',(0,(height+4.5)/2,depth),(opening,height-4.5,.3),True)
def add_guest(key,name,origin,bays,floors,linear):
 t=dict(id=key+'-1',name=name,building=key,origin=origin,yaw=math.atan2(linear[1],linear[0]),linear=linear,floors=floors,firstGuestFloor=2,bays=bays,kind='room',set=key,roomDepth=7.6,lazy=True,source='guest-'+key,lobbyFront=-5.25-6*bays,windowWidth=19.2)
 towers.append(t);return t

# LINQ: surveyed three-wing tower, blue/white room grid, hexagonal Strip skin,
# a curved Vortex crown, and an uninterrupted promenade to the observation wheel.
enter('linq');pod=footprint('way/115771295');tower=footprint('way/115773426');F=entry_on(pod,(36,-250));portal=F.portal(w=6,h=4.6,name='The LINQ casino entrance');spec=venue('linq','The LINQ + High Roller',pod,F,34,79,8,portal)
B.source='linq-podium';glazed=arrival(F,portal,29,6.6);B.shell(pod,.15,17,'white',[glazed],interior=(F.poly([(-16.9,.3),(16.9,.3),(16.9,78),(-16.9,78)]),8.6));B.source='guest-linq'
from linq_facades import tower as linq_tower,street as linq_street
linq_tower(B,tower);spec['hotelSources']=['guest-linq']
linq_street(B,pod,F)
spec['views'].update({'strip':{'eye':[-16,2,-274],'target':[40,17,-251]},'facade-aerial':{'eye':[-142,108,-420],'target':[154,29,-260]}})
B.source='linq-promenade'
replacement.update(['way/115771295','way/115773426','way/115772002','way/402543935','way/402543936','way/402543937','way/1424252908'])
# Promenade follows its mapped, gently turning pedestrian corridor.
promenade=LineString([(36,-160),(109,-161),(140,-171),(235,-174),(319,-177),(400,-183)])
B.extrude('tile',promenade.buffer(6.2,cap_style=2,join_style=2),.02,.23,True)
for ident in ['way/402543935','way/402543936']:
 p=footprint(ident);B.shell(p,.24,8.8,'ivory')
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  line=LineString([a,b]);mid=line.interpolate(.5,normalized=True)
  if line.length<6 or promenade.distance(mid)>13:continue
  dx,dz=b[0]-a[0],b[1]-a[1];nx,nz=-dz/line.length,dx/line.length
  if p.contains(Point(mid.x+nx*.1,mid.y+nz*.1)):nx,nz=-nx,-nz
  J=Frame(B,mid.x+nx*.15,mid.y+nz*.15,math.atan2(-nx,-nz))
  count=max(1,int(line.length/13));labels=['THE LINQ PROMENADE','CHAYO','BROOKLYN BOWL','YARD HOUSE','GORDON RAMSAY FISH & CHIPS','WELCOME TO LAS VEGAS']
  for j in range(count):shop(J,(j-(count-1)/2)*12,0,labels[j%len(labels)],10)
for i in range(14):
 p=promenade.interpolate((i+.4)/14,normalized=True);J=Frame(B,p.x,p.y)
 J.plant(-5,0,True);J.bench(5,0)
for x,z in [(80,-159),(142,-171),(220,-174),(300,-177),(367,-180)]:
 J=Frame(B,x,z)
 for s in [-1,1]:J.tube('steel',(0,0,s*5.5),(0,7.4,s*5.5),.09)
 J.path('blackiron',[(0,7.3-.8*math.sin(a*math.pi),-5.5+11*a) for a in np.linspace(0,1,30)],.018)
 for a in np.linspace(0,1,20):J.box('warm',(0,7.1-.8*math.sin(a*math.pi),-5.5+11*a),(.085,.12,.085))
# Keep dedicated roof/service and upper storefront details in future LINQ rebuilds.
for g in B.groups.values():
 if g['property']!='linq-exterior':continue
 if g['source'] in ['linq-podium','linq-promenade','guest-linq'] and g['material']=='roof':g['material']='linq-membrane-paint'
 if g['source']=='linq-promenade' and g['material']=='shopglass':g['material']='linq-glass'
from linq_podium_detail import exterior as linq_podium_detail
linq_podium_detail(B)
enter('linq','interior');atrium(F,34,78,8,front=False,rear=False)
F.reception(-10,18,8,'THE LINQ');F.lounge(10,12);F.lounge(10,22)
for j in range(34):
 xx=-14.8+j*.29;F.box('walnut',(xx,3.8,20.05),(.12,7.2,.35))
for x in [-12.1,-8.0]:lightbox(F,x,3.9,19.75,3.5,2.0,'THE LINQ')
for row in range(5):
 for i in range(32):F.box('white' if (row*7+i*3)%5 else 'silver',(-13.8+i*.245,.24+row*.19,17.404),(.234,.18,.025))
for xx in [-13.5,-8.5]:
 for zz in [12,15]:F.lathe('steel',xx,zz,[(0,.17),(.07,.17),(.1,.035),(1.0,.035),(1.04,.07)],12)
F.path('blackiron',[(-13.5,1,12),(-13.5,1,15),(-8.5,1,15),(-8.5,1,12)],.026)
for x in [4.6,6.1,7.6]:
 F.box('blue',(x,.9,9),(.75,1.8,.55),True);F.box('screen',(x,1.43,8.69),(.60,.64,.03));F.text('CHECK IN',(x,.65,8.65),.12)
F.text('EXPRESS SERVICES',(6.1,3.2,9),.35,'blue')
# Blue-lit portal and a lower lounge ceiling give arrival a distinct composition.
for x in [-5.7,5.7]:F.box('blue',(x,2.65,4),(.65,5.3,1.0));F.box('screen',(x,2.65,3.47),(.47,5.0,.03))
F.box('blue',(0,5.5,4),(12,1,1));F.box('screen',(0,5.46,3.47),(11.5,.78,.03))
for z in np.arange(7,25,.62):F.box('walnut',(-9,6.8,z),(15,.25,.16))
# Catalyst bar: rounded island, back bar bottles, stools and globe pendants.
F.box('walnut',(10,.66,26),(11,1.32,1.45),True);F.box('charcoal',(10,1.38,26),(11.4,.16,1.7));F.text('CATALYST',(10,4.1,28),.55,'magenta')
for x in np.arange(5.4,15,1.15):
 F.lathe('steel',x,24.7,[(0,.28),(.06,.28),(.1,.045),(.78,.045)],14);F.box('velvet',(x,.81,24.7),(.58,.12,.50));F.tube('steel',(x,6.5,26),(x,4.7,26),.018);B.sphere('warm',F.p(x,4.5,26),.23,16,10)
for z in [32,41,50,59,68]:
 for side in [-1,1]:
  carpet(F,side*10,z,10,7.8)
  for x in [side*4.3,side*6.1]:F.slot(x,z)
  for x in [side*14.9]:F.lathe('silver',x,z,[(0,.45),(6.7,.45),(7.3,.75)],24)
  lightbox(F,side*10,3.2,z,3.6,.8,'PLAY   THE LINQ')

for z in [32,38,44,50,56]:
 for x in [-12,-10,-8,8,10,12]:F.slot(x,z)
for z in [10,26,47,68]:F.plant(15,z);F.box('blue',(0,7.55,z),(30,.3,.30))
F.text('CASINO   /   HOTEL CHECK-IN',(0,5.3,11),.7,'blue');F.text('GUEST ROOMS  →',(0,4.4,73),.55,'blue')
# The vestibule and stair core share the casino axis; floors meet edge-to-edge.
rear_portal(F,34,8.7,78,8)
q=F.p(0,0,78);J=Frame(B,q[0],q[2],F.yaw);atrium(J,9,14.75,6,front=False,rear=False)
add_guest('linq','The LINQ',list(F.p(0,0,110)),2,17,[.8*F.co,F.si,-.8*F.si,F.co])
F.floor(2.5,2.1,105.0,'tile')
spec['zones'].append(dict(origin=J.p(0,0,0),yaw=J.yaw,width=9,depth=14.75,height=6))
spec['views']['skyline']=dict(eye=[-70,30,-165],target=[220,40,-252])

# High Roller: 158.5 m wheel, 28 upright spherical cabins, cable spokes and
# four inclined legs; separate moving batches allow the rim to turn slowly.
enter('linq');cx,cz=437.1,-182.0;cy=85.1;r=79.25;B.source='wheel-fixed';axis=.08
W=Frame(B,cx,cz,axis,y=0)
for sx in [-1,1]:
 for sz in [-1,1]:W.tube('white',(sx*23,0,sz*21),(sx*3,cy,sz*2.5),1.0,16)
W.tube('steel',(0,cy,-8),(0,cy,8),1.3,24)
for s in [-1,1]:W.tube('white',(0,cy,s*7),(0,cy,s*3),2.8,28)
B.source='wheel-rim';B.detail=0
for dz in [-1.4,1.4]:
 pts=[W.p(r*math.cos(a),cy+r*math.sin(a),dz) for a in np.linspace(0,math.tau,337)];B.path('white',pts,.63,10)
for i in range(112):
 a=i*math.tau/112;aa=a+math.tau/112
 W.tube('steel',(r*math.cos(a),cy+r*math.sin(a),-1.4),(r*math.cos(aa),cy+r*math.sin(aa),1.4),.11,6)
for i in range(56):
 a=i*math.tau/56
 for s in [-1,1]:W.tube('steel',(3.1*math.cos(a+.12*s),cy+3.1*math.sin(a+.12*s),s*5.2),(r*math.cos(a),cy+r*math.sin(a),s*1.4),.043,5)
spec['wheel']=dict(center=[cx,cy,cz],radius=r,yaw=axis,cabins=28)
for i in range(28):
 a=i*math.tau/28;x,y=r*math.cos(a),cy+r*math.sin(a);B.source='wheel-cabin-'+str(i)
 B.sphere('cabinglass',W.p(x,y,0),3.05,24,16,(1,1,1.20))
 for dz in [-1.9,1.9]:W.path('white',[(x+2.72*math.cos(t),y+2.72*math.sin(t),dz) for t in np.linspace(0,math.tau,49)],.11)
 for zz in [-2.7,0,2.7]:W.path('steel',[(x+2.9*math.cos(t),y+2.9*math.sin(t),zz*.6) for t in np.linspace(0,math.tau,41)],.065)
 W.box('silver',(x,y-1.85,0),(4.0,.24,4.2));W.box('blue',(x,y-1.4,1.4),(2.7,.42,.65))
B.source='wheel-station';station=Frame(B,423,-162,0);station.floor(22,28,0);station.box('white',(0,5,0),(24,.5,28));station.text('HIGH ROLLER',(0,5.6,-14.4),1.0,'blue')
for x in [-10,10]:
 for z in [-11,11]:station.tube('silver',(x,0,z),(x,5,z),.18,12)
spec['views']['wheel']=dict(eye=[345,2,-174],target=[437,79,-182])

# Cromwell / Vanderpump: the retained boutique-hotel envelope, dark French
# balcony rails, warm stone piers, cornices, rooftop garden and Giada corner.
enter('vanderpump');p=footprint('way/61239326');F=entry_on(p,(35,101));portal=F.portal(w=5,h=4.5,name='The Vanderpump Hotel entrance');spec=venue('vanderpump','The Vanderpump Hotel',p,F,29,46,6.4,portal)
# (podium 7.0 m, under the guest tower's level-3 floor at 7.44: at 8.0 its roof sliced through that floor's rooms and
# corridor, and hiding it from inside made it pop back in as a film camera left through a window, 2026-10-08)
B.source='vanderpump-podium';glazed=arrival(F,portal,16,5.8);B.shell(p,.15,7.0,'sandstone',[glazed]);upper=p.intersection(box(35,77,135,128));B.source='guest-vanderpump';facade(upper,7.14,34,'vanderpump');spec['hotelSources']=['guest-vanderpump']
for y in [7.3,32.7,34.3,35.0]:cornice(upper,y,'ivory',.27)
F.box('bronze',(0,4.9,-2.3),(19,.45,5.2));F.text('THE VANDERPUMP HOTEL',(0,6,-4.95),.76,'letter')
for x in [-8,8]:F.lathe('sandstone',x,-3,[(0,.38),(.2,.46),(4.5,.32),(4.8,.5)],24);F.plant(x,-5)
for x in np.arange(-13,14,2.6):F.arch(x,-.22,2.25,7.6,'ivory',.13,5)
# Rooftop pergola, pool, framed cabanas and clipped planting.
R=Frame(B,80,102,0,y=35.2);R.floor(79,37,0,'tile');R.box('water',(0,.05,0),(28,.1,10))
for x in np.arange(-33,35,9):
 for z in [-14,14]:
  R.plant(x,z,True);R.box('velvet',(x,.7,z*.72),(2,.18,2.2));R.box('ivory',(x,3.4,z*.72),(3.2,.16,3.2))
  for s in [-1,1]:R.box('bronze',(x+s*1.5,1.7,z*.72),( .06,3.4,.06))
R.rail((-38,-18),(38,-18),1.2,True);R.rail((-38,18),(38,18),1.2,True)
G=Frame(B,53,126,math.pi,y=0);G.text('GIADA',(0,7.8,0),1.2,'letter')
G.box('bronze',(0,23,-.42),(17.5,20,.2));G.box('panel',(0,23,-.58),(16.5,19,.14))
for x in [-7.8,7.8]:G.box('gold',(x,23,-.69),(.10,18,.07));G.box('warm',(x,23,-.73),(.03,17.6,.03))
for y in [14.2,31.8]:G.box('gold',(0,y,-.69),(15.6,.10,.07))
G.text('THE',(0,25.5,-.73),.8,'letter');G.text('VANDERPUMP',(0,23.4,-.73),1.05,'letter');G.text('HOTEL',(0,22,-.73),.65,'letter')
for x in np.arange(-13,14,2):
 G.box('darkglass',(x,5.3,-.36),(1.88,3.0,.08));G.box('bronze',(x-.96,5.3,-.46),(.10,3.3,.12));G.box('warm',(x-.81,5.3,-.49),(.022,2.6,.03))
G.box('ivory',(0,7.5,-.55),(29,.55,1.4));G.text('GIADA',(0,8.2,-.95),1.15,'letter')
for x in np.arange(-11,12,2):G.plant(x,-1.3)

replacement.add('way/61239326')
enter('vanderpump','interior');atrium(F,29,46,6.4,'classic',front=False,rear=False)
F.reception(-7,17,9,'THE VANDERPUMP');F.lounge(8,11);F.lounge(8,21)
for z in [8,20,33,42]:F.plant(-12,z);F.plant(12,z)
for z in [31,37]:
 for x in [-9,-7,-5,5,7,9]:F.slot(x,z)
for side in [-1,1]:
 for z in np.arange(3,43,4):
  F.box('bronze',(side*14.27,2.8,z),(.12,4.5,2.8));F.box('panel',(side*14.17,2.8,z),(.10,4.24,2.52))
F.text('GUEST ROOMS',(0,4.6,44),.55,'letter')
for z in [11,21,32,40]:
 for side in [-1,1]:
  carpet(F,side*8,z,10.5,7.5,'floralcarpet')
  F.lathe('bronze',side*4,z,[(0,.31),(.2,.39),(4.2,.22),(4.5,.35)],24)
  F.chandelier(side*8,z,5.5)
for side in [-1,1]:
 for z in [4,12,23,35,42]:
  F.box('gold',(side*14.05,2.8,z),(.12,3.1,2.2));F.box('darkglass',(side*13.96,2.8,z),(.07,2.85,1.96))
  F.box('warm',(side*13.84,2.8,z),(.06,.67,.14))
# Botanical metal tracery and a rose-colored lounge, echoing the current refurbishment.
for x in np.arange(-12.5,-5.5,.44):
 F.path('brass',[(x+.25*math.sin(y*3),y,20.3) for y in np.linspace(1.8,5.8,32)],.012)
 for y in [2.5,3.3,4.1,4.9]:B.sphere('gold',F.p(x,y,20.3),.09,10,6,(1,.5,.3))

rear_portal(F,29,4.7,46,6.4)
q=F.p(0,0,46);J=Frame(B,q[0],q[2],F.yaw);atrium(J,5,2.25,6.4,front=False,rear=False)
add_guest('vanderpump','The Vanderpump Hotel',list(F.p(0,0,71.5)),3,9,[.86*F.co,F.si,-.86*F.si,F.co])
F.floor(2.5,2.1,66.5,'marble')
spec['views']['skyline']=dict(eye=[-35,14,177],target=[89,20,101])

# Fashion Show: mapped anchors and articulated east front; the actual mapped
# Cloud outline defines its long lenticular roof, lifted to the photographed height.
enter('fashion');p=footprint('way/180584255');F=entry_on(p,(366,-1207));portal=F.portal(w=6,h=5.2,name='Fashion Show Strip entrance');spec=venue('fashion','Fashion Show',p,F,44,108,16,portal)
B.source='mall-shell';glazed=arrival(F,portal,34,14.8);B.shell(p,.15,16.5,'ivory',[glazed],interior=(F.poly([(-21.9,.3),(21.9,.3),(21.9,108),(-21.9,108)]),16.4));replacement.update(['way/180584255','way/1421449927','relation/19447588'])
cloud=footprint('relation/19447588');c=cloud.centroid;B.source='cloud';coords=list(cloud.exterior.coords)[:-1]
for side in [-1,1]:
 for j in range(12):
  t=j/12;tt=(j+1)/12
  for a,b in zip(coords,coords[1:]+coords[:1]):
   pts=[]
   for q,v in [(t,a),(t,b),(tt,b),(tt,a)]:
    xx=c.x+(v[0]-c.x)*q;zz=c.y+(v[1]-c.y)*q;yy=33.2+(zz-c.y)*.06+side*3.2*math.sqrt(max(0,1-q*q));pts.append((xx,yy,zz))
   B.face('silver' if side>0 else 'cloudskin',pts)
for i,(x,z) in enumerate([(347,-1195),(389,-1261)]):
 B.lathe('silver',(x,z),[(.24,1.3),(29,1.1),(34,1)],24)
 for j in range(16):
  a=j*math.tau/16;bb=(j+1)*math.tau/16
  B.face('ledblue',[(x+1.34*math.cos(a),6,z+1.34*math.sin(a)),(x+1.34*math.cos(bb),6,z+1.34*math.sin(bb)),(x+1.34*math.cos(bb),25,z+1.34*math.sin(bb)),(x+1.34*math.cos(a),25,z+1.34*math.sin(a))])
 L=Frame(B,x+1.5,z,math.pi/2);L.text('FASHION',(0,19,0),.45,'letter');L.text('SHOW',(0,18.2,0),.6,'letter')
F.box('silver',(0,6,-2.5),(35,.45,6));F.text('FASHION SHOW',(0,7.2,-5.6),1.3,'letter')
for x in [-17,-10,10,17]:F.box('glass',(x,7.5,-.10),(6.5,14,.12));F.box('silver',(x-3.3,7.5,-.22),(.16,14,.17))
for x in [-21,21]:F.plant(x,-5,True)
for side in [-1,1]:
 for i in range(6):
  J=Frame(B,*[F.p(side*25,0,i*11)[k] for k in [0,2]],F.yaw)
  J.plant(0,0,True)
spec['views']['skyline']=dict(eye=[535,22,-1110],target=[328,24,-1235])
enter('fashion','interior');atrium(F,44,108,16,front=False)
# Two-storey galleria: open central void, real balconies and paired escalators.
for s in [-1,1]:
 slab=box(s*14.5-7.5,6,s*14.5+7.5,108).difference(box(s*13-1.5,10,s*13+1.5,26))
 B.extrude('tile',F.poly(list(slab.exterior.coords)) if not slab.interiors else Polygon([(F.p(x,0,z)[0],F.p(x,0,z)[2]) for x,z in slab.exterior.coords],[[(F.p(x,0,z)[0],F.p(x,0,z)[2]) for x,z in ring.coords] for ring in slab.interiors]),6.65,7.04,True)
 for z in np.arange(12,104,12):
  for y in [0,6.8]:
   p=F.p(s*21.6,y,z);J=Frame(B,p[0],p[2],F.yaw+s*math.pi/2,y=p[1]);shop(J,0,0,['NORDSTROM','ZARA','SAKS FIFTH AVENUE','MACY’S','DILLARD’S','NEIMAN MARCUS','FASHION SHOW'][int(z/12)%7],10)
  F.lathe('white',s*8,z,[(0,.44),(6.6,.44),(6.8,.5),(15.6,.5)],20)
 R=Frame(B,F.x,F.z,F.yaw,y=7.04);R.rail((s*7.1,8),(s*7.1,106),1.2,True)
for x in [-13,13]:
 F.stairs(x,11,2.5,6.8,14)
 F.box('tile',(x,6.66,25.5),(2.5,.28,1.0),True)
 for side in [-1,1]:F.tube('blackiron',(x+side*1.35,1.1,11),(x+side*1.35,7.9,25),.12)
 # Guard the upper-level stair opening on both sides; leave its exit clear.
 U=Frame(B,F.x,F.z,F.yaw,y=7.04)
 for side in [-1,1]:U.rail((x+side*1.5,10),(x+side*1.5,26),1.15,True)
 U.rail((x-1.5,10),(x+1.5,10),1.15,True)
for z in [33,56,79,99]:F.lounge(-3,z);F.plant(4,z);F.box('white',(0,15.7,z),(42,.5,.6))
F.box('charcoal',(0,.4,68),(5,.8,17),True);F.text('FASHION SHOW',(0,4.5,83),.85,'blue')
F.text('LEVEL 2   /   DEPARTMENT STORES',(0,6.0,7),.6,'blue')
for z in np.arange(13,100,18):
 for x in [-5,5]:
  F.box('screen',(x,12.5,z),(.08,3.2,1.8));F.tube('steel',(x,16,z),(x,14.1,z),.012)
  F.box('ivory',(x,14.2,z),(.16,.10,1.9))
 for s in [-1,1]:
  F.box('brass',(s*7,6.7,z),( .13,.35,17.7));F.box('warm',(s*7,6.4,z),(.035,.035,17.6))
  for yy in [1.3,2.5,3.7]:F.box('walnut',(s*21.3,yy,z),(.30,.10,7))
 for x in [-3,3]:F.bench(x,z+4)
# Broad high-level luminous skylight grid, separated from the opaque roof above.
for z in np.arange(6,103,8):
 F.box('skyglass',(0,15.86,z),(12,.03,6.5));F.box('silver',(0,15.72,z),( .13,.15,6.7))
 for dz in [-3.4,3.4]:F.box('silver',(0,15.74,z+dz),(12.4,.14,.13))
# Suspended theatrical trusses and round retail kiosks flank the runway.
for z in [47,58,71,84]:
 for y in [10.7,11.2]:F.tube('charcoal',(-6,y,z),(6,y,z),.055)
 for x in np.arange(-6,6,1):
  F.tube('charcoal',(x,10.7,z),(x+.5,11.2,z),.028);F.tube('charcoal',(x+.5,11.2,z),(x+1,10.7,z),.028)
  F.box('charcoal',(x+.5,10.5,z),(.28,.32,.44));F.box('warm',(x+.5,10.32,z-.15),(.16,.02,.16))
 for x in [-5.8,5.8]:F.tube('blackiron',(x,11.2,z),(x,15.7,z),.012)
for x,z in [(-4.2,38),(4.2,48),(-4.2,91),(4.2,99)]:
 F.lathe('walnut',x,z,[(0,1.65),(.12,1.75),(1.0,1.75),(1.12,1.85)],40)
 F.lathe('glass',x,z,[(1.13,1.67),(1.85,1.67)],40)
 F.lathe('silver',x,z,[(1.85,1.75),(1.94,1.75)],40)
 for side in [-1,1]:F.tube('silver',(x+side*1.25,1.1,z),(x+side*1.25,3.7,z),.07)
 F.lathe('white',x,z,[(3.6,2.2),(3.78,2.2)],40)
 F.text('ACCESSORIES',(x,3.35,z-1.85),.28,'blue')
 for dx in [-.8,0,.8]:F.box('gold',(x+dx,1.38,z-.6),(.3,.42,.22))

spec['routes']=[dict(points=[F.p(0,0,-5),F.p(0,0,5),F.p(0,0,55)]),dict(points=[F.p(-13,.08,11),F.p(-13,6.88,25),F.p(-13,6.88,26),F.p(-13,6.88,50)])]

# Venetian: exact Campanile footprint, loggias, patterned Doge's Palace wall,
# blue-green canal, mooring poles, bridge and a fresco-inspired entrance gallery.
enter('venetian');p=footprint('relation/7770314');F=entry_on(p,(223,-689));portal=F.portal(w=6,h=5.5,name='Venetian Grand Colonnade');spec=venue('venetian','The Venetian frontage',p,F,37,65,12,portal)
Q=Frame(B,225.85,-644,math.pi/2,y=6.24);upperPortal=Q.portal(w=4.6,h=3.3,name='Rialto / Grand Canal gallery');spec['portals'].append(upperPortal)
# Grand Canal Shoppes east entrance (2026-10-08, the owner: "fly through the shoppes to the casino ... and through the lobby"):
# an upper-level door from a terrace on the east face, toward the Sphere. S: local z west along the street, x across it.
S=Frame(B,438.6,-734,-math.pi/2,y=7.24);eastPortal=S.portal(w=7,h=5,name='Grand Canal Shoppes east terrace');spec['portals'].append(eastPortal)
galleryMask=unary_union([F.poly([(-18.4,.3),(18.4,.3),(18.4,65),(-18.4,65)]),box(225.85,-648,251,-640),box(244.8,-672,249.2,-644)])
guestPortals=[dict(p=[t['origin'][0]+t['lobbyFront'],.24,t['origin'][2]],width=4.2,height=4.7) for t in json.load(open('src/work/hotels/highrise-towers.json')) if t['building']=='venetian']
# Each frontage has one owner: remove the legacy podium under the three palazzi.
frontageFootprints=unary_union([footprint(i).buffer(.08,join_style=2) for i in ['way/33996627','way/543728945','way/115776190']])
podium=p.difference(frontageFootprints)
B.source='venetian-podium';glazed=arrival(F,portal,11,6.2,floor=False)
# the hotel arrivals doors (2026-10-23) from the forecourt into the lobby's vestibule (the portal belongs to the interior)
arrivalsOpening=dict(p=[232.0,.24,-630.75],yaw=math.pi,width=6.0,height=4.5)
B.shell(podium,.15,17,'pinkstone',[glazed,upperPortal,eastPortal,arrivalsOpening,*guestPortals],roof=False,interior=(galleryMask,12.6));B.planar('ivory',podium,17)
from venetian_plaza import DECK
palaceFloor=Frame(B,225.15,-690.7,math.pi/2).poly([(-33,-3.5),(33,-3.5),(33,3.5),(-33,3.5)])
B.planar('tile',F.poly([(-8,-8),(8,-8),(8,0),(-8,0)]).difference(DECK.union(palaceFloor)),.24,True)
# the terrace: a stone balcony on brackets, balustrades, two lanterns
T2=Frame(B,438.6,-734,math.pi/2,y=7.24);T2.box('marble',(0,-.18,4.2),(16,.36,8.4),True)
for x in [-7.6,7.6]:T2.box('ivory',(x,.55,4.2),(.3,1.1,8.4),True)
T2.box('ivory',(0,.55,8.3),(15.5,1.1,.3),True)
for x in np.arange(-6,6.1,3):T2.box('ivory',(x,-1.1,.6),(.5,1.6,1.2))
for x in [-5,5]:T2.tube('blackiron',(x,0,6.5),(x,3.2,6.5),.06);T2.box('warm',(x,3.35,6.5),(.34,.42,.34))
T2.text('GRAND CANAL SHOPPES',(0,5.65,.15),.62,'gold',True);replacement.update(['relation/7770314','way/43875964','way/33996627','way/543728945','way/115776190'])
from venetian_frontage import campanile, palazzi
campanile(B)
palazzi(B)
# Photo-guided replacement of the palace arcade, tracery and upper facade.
from venetian_palace import palace
palace(B)
from venetian_north_frontage import frontage as north_frontage
north_frontage(B)
from venetian_towers import towers
towers(B)
from venetian_canal import canal as mapped_canal
spec['views']['site-correction']=mapped_canal(B)
spec['views']['gondola-bank']=dict(eye=[185,2,-728],target=[199,1,-726])
spec['views']['gondola-detail']=dict(eye=[191,7,-735],target=[199,1,-726])
spec['views']['venetian-street']=dict(eye=[90,2,-592],target=[140,7,-580])
from venetian_plaza import plaza
spec['views']['palace-plaza']=plaza(B)
from venetian_waterways import side_bridge,water_review
side_bridge(B)
spec['views']['canal-bridge-clearance']=dict(eye=[193,1.6,-711],target=[195,2.3,-688])
spec['views']['canal-north-throat']=dict(eye=[218,1.8,-729],target=[239,2.3,-725.6])
spec['views']['canal-water-aerial']=dict(eye=[144,44,-761],target=[222,5,-705])
Path('build/strip-landmarks/venetian-water-routes.json').write_text(json.dumps(water_review(),indent=2))
spec['views']['frontage-correction']=dict(eye=[110,145,-900],target=[265,55,-655])
from venetian_yard import yard
yard(B)
from venetian_rialto import bridge,route_points
spec['views']['rialto-overview']=bridge(B)
spec['views']['rialto-stairs']=dict(eye=[163,4,-618],target=[195,10,-624])
spec['views']['rialto-underpass']=dict(eye=[192,2,-654],target=[201,5,-628])
spec['views']['rialto-plaza-ground']=dict(eye=[212,2.8,-676],target=[199,9,-630])
spec['views']['palace-ground']=dict(eye=[190,2.8,-692],target=[223,17,-690])
spec['views']['rialto-landing']=dict(eye=[215,10,-659],target=[222,10,-641])
F.text('THE VENETIAN',(0,7.3,-.7),1.1,'gold');F.arch(0,-.5,8,10.5,'ivory',.25)
spec['views']['skyline']=dict(eye=[38,14,-707],target=[219,42,-663])
spec['views']['canal']=dict(eye=[163,2,-741],target=[171,34,-626])
spec['views']['rialto']=dict(eye=[153,9,-654],target=[195,8,-626])
from venetian_pools import main_deck
spec['views']['pool']=main_deck(B)
from palazzo_tower import tower as palazzo_tower
palazzo_tower(B)
from venezia_courtyard import courtyard
spec['views']['pool-garden']=courtyard(B)
from palazzo_pools import pools as palazzo_pools
spec['views']['palazzo-pools']=palazzo_pools(B)
from palazzo_retail import frontage as palazzo_retail
spec['views']['palazzo-retail']=palazzo_retail(B)
spec['views']['palazzo-tower']=dict(eye=[230,3,-1080],target=[465,108,-895])
enter('venetian','interior');B.source='venetian-interiors'
# ── The Venetian's public interiors (2026-10-23; the owner on the previous ones: "What happened? This looks exactly like
#    before, very low detail, blocky." They chose a rebuild to the official resort map at full detail). Three streamed
#    venues: the lobby (this venue's interior: Great Hall, Scenic Overlook, Rialto landing, arrivals, colonnade, rotunda,
#    front desk), the casino ('venetianCasino') and the Grand Canal Shoppes on Level 2 ('grandCanal'). Layout:
#    venetian_interior_plan.py; kit: venetian_kit.py; materials: venetian_materials.py. Build them alone (and faster) with
#    build_venetian_interior.py. The previous interior's code is in git history and build/venetian-interiors/.
from venetian_lobby import build as venetian_lobby
from venetian_casino import build as venetian_casino
from venetian_shoppes import build as venetian_shoppes
from build_venetian_interior import lobby_routes
_lobby=venetian_lobby(B)[0]
spec['portals']=[p_ for p_ in spec['portals'] if p_['name']=='Venetian Grand Colonnade']+_lobby['portals']
for f_ in ['zones','accessPoints']:spec[f_]=_lobby[f_]
spec['routes']=lobby_routes(_lobby)
spec['views'].update(_lobby['views'])
for _sub in venetian_casino(B)+venetian_shoppes(B):
 enter(_sub['key'],'exterior','anchor');B.box('vi-iron',_sub.pop('anchor'),(.01,.01,.01),True);venues.append(_sub)

# T-Mobile Arena: the asymmetrical mapped envelope, rust-colored shingle shell,
# northeast curtain wall, broad balconies, magenta LED ribbon and open plaza.
enter('arena');p=footprint('way/364489406');F=entry_on(p,(-388,1404),1);portal=F.portal(w=7,h=5.0,name='T-Mobile Arena main doors');spec=venue('arena','T-Mobile Arena',p,F,54,35,26,portal)
main=footprint('way/364489402');center=main.centroid;B.source='arena-shell'
glazed=arrival(F,portal,38,6.3);B.shell(p,.15,7,'darkglass',[glazed],False)
for a,b in zip(list(main.exterior.coords),list(main.exterior.coords)[1:]):
 L=math.dist(a,b);mid=((a[0]+b[0])/2,(a[1]+b[1])/2);glass=mid[0]>-453 and mid[1]<1480
 B.face('glass' if glass else 'copperpanel',[(a[0],7,a[1]),(b[0],7,b[1]),(b[0],34,b[1]),(a[0],34,a[1])],not glass)
 if glass:
  # The long curtain wall is transparent, with high-level public balconies.
  for u in np.linspace(0,1,max(2,int(L/2.8))):
   x,z=a[0]+(b[0]-a[0])*u,a[1]+(b[1]-a[1])*u;B.tube('steel',(x,7,z),(x,34,z),.09)
  for y in [12,19,26,33]:B.tube('silver',(a[0],y,a[1]),(b[0],y,b[1]),.13)
  for y in [17,24]:
   outward=np.array(mid)-np.array(center.coords[0]);outward/=np.linalg.norm(outward)
   B.face('silver',[(a[0],y,a[1]),(b[0],y,b[1]),(b[0]+outward[0]*2,y,b[1]+outward[1]*2),(a[0]+outward[0]*2,y,a[1]+outward[1]*2)])
  if mid[1]<1465:
   B.face('magenta',[(a[0]+.08,19,a[1]-.08),(b[0]+.08,19,b[1]-.08),(b[0]+.08,27,b[1]-.08),(a[0]+.08,27,a[1]-.08)])
 else:
  B.detail=1;ux,uz=(b[0]-a[0])/L,(b[1]-a[1])/L;nx,nz=-uz,ux
  if main.contains(Point(mid[0]+nx*.2,mid[1]+nz*.2)):nx,nz=-nx,-nz
  for row,y in enumerate(np.arange(7.2,33,1.12)):
   for x in np.arange(0,L,2.0):
    a0=max(0,x+(row%2)*.8);a1=min(L,a0+1.94)
    if a1<=a0:continue
    B.face(['copperpanel','copper2','copper3'][(row+int(x)*3)%3],[(a[0]+ux*a0+nx*.06,y,a[1]+uz*a0+nz*.06),(a[0]+ux*a1+nx*.06,y,a[1]+uz*a1+nz*.06),(a[0]+ux*a1+nx*.13,y+1.06,a[1]+uz*a1+nz*.13),(a[0]+ux*a0+nx*.13,y+1.06,a[1]+uz*a0+nz*.13)])
  B.detail=0
B.planar('roof',p,35.5)
F.box('silver',(0,5.9,-4.0),(43,.5,9));F.text('T-Mobile ARENA',(0,35,-.9),2.2,'magenta');F.text('WELCOME TO LAS VEGAS',(0,23.7,-1.0),1.0,'letter')
for x in [-20,-13,13,20]:F.box('glass',(x,2.6,-.1),(6,5.2,.09),True);F.box('steel',(x-3,2.6,-.25),(.1,5.2,.12))
F.floor(65,24,-12,'tile');F.text('PLAZA',(18,1.6,-22),1.7,'magenta')
for x in [-26,26]:
 for z in [-6,-19,-34]:F.plant(x,z);F.bench(x+3,z)
for x,z in [(-34,-13),(34,-13)]:
 F.tube('steel',(x,0,z),(x,12,z),.16,12)
 for a in np.linspace(0,math.tau,12,endpoint=False):F.tube('bronze',(x,8,z),(x+4.5*math.cos(a),11,z+4.5*math.sin(a)),.07)
replacement.update(['way/'+str(i) for i in range(364489398,364489407)])
spec['views']['skyline']=dict(eye=[-286,20,1334],target=[-455,22,1448])
enter('arena','interior')
# Floor and circulation ring are clipped to the surveyed envelope.
B.planar('tile',p,.24,True);B.planar('charcoal',p,35.1)
F.light(0,12,14,0xdbeaff,1600,55);F.light(-20,12,20,0xe7edff,1600,55)
for x in [-20,20]:F.box('charcoal',(x,1.2,13),(8,2.4,1.2),True);F.text('TICKETS  /  GUEST SERVICES',(x,3,13-.8),.34,'letter')
ax,az=-471,1470;rx,rz=60,65
def gate_angle(a):return abs((a-math.pi/12+math.pi/6)%(math.pi/3)-math.pi/6)<.045
# Stepped seating tiers, access aisles and the rink. Instanced chairs are added
# by the runtime, one draw per seat part instead of individual objects.
A=Frame(B,ax,az,0)
A.box('ice',(0,.025,0),(59.5,.05,27.5),True)
for side in [-1,1]:A.box('red',(side*20,.065,0),(.13,.012,27));A.box('blue',(side*8,.065,0),(.2,.012,27))
A.box('red',(0,.065,0),(.13,.012,27))
for x in [-20,20]:
 for z in [-7,7]:A.path('red',[(x+4*math.cos(a),.065,z+4*math.sin(a)) for a in np.linspace(0,math.tau,49)],.065)
for ring,(rows,r0,r1,y0,y1) in enumerate([(19,.52,.79,.7,11.4),(19,.84,1.0,14.4,25.4)]):
 for row in range(rows):
  t=row/(rows-1);r0i=r0+(r1-r0)*t;rnext=r0i+(r1-r0)/(rows-1);y=y0+(y1-y0)*t
  for j in range(160):
   a=j*math.tau/160;aa=(j+1)*math.tau/160
   if ring==0 and r0i<.615 and gate_angle((a+aa)/2):continue
   pts=[A.p(rx*r*math.cos(ang),y,rz*r*math.sin(ang)) for r,ang in [(r0i,a),(r0i,aa),(rnext,aa),(rnext,a)]];B.face('concrete',pts)
   # Close each riser instead of leaving gaps beneath the rows.
   previous=y-(y1-y0)/(rows-1)
   B.face('charcoal',[A.p(rx*r0i*math.cos(ang),yy,rz*r0i*math.sin(ang)) for ang,yy in [(a,previous),(aa,previous),(aa,y),(a,y)]])
  count=int(math.tau*math.sqrt(((rx*r0i)**2+(rz*r0i)**2)/2)/.62)
  for j in range(count):
   a=j*math.tau/count
   if abs((a+math.pi/12)%(math.pi/6)-math.pi/12)<.020:continue
   if ring==0 and r0i<.615 and gate_angle(a):continue
   spec.setdefault('seats',[]).append([ax+rx*r0i*math.cos(a),y+.38,az+rz*r0i*math.sin(a),-a-math.pi/2])
 # Broad collision terraces carry guests between radial access stairs.
 outer=scale(Point(ax,az).buffer(1,resolution=96),rx*(r1+.025),rz*(r1+.025));inner=scale(Point(ax,az).buffer(1,resolution=96),rx*(r1-.04),rz*(r1-.04))
 aisles=unary_union([LineString([(ax+rx*.5*math.cos(a),az+rz*.5*math.sin(a)),(ax+rx*r1*math.cos(a),az+rz*r1*math.sin(a))]).buffer(1.1,cap_style=2) for a in np.arange(12)*math.tau/12])
 B.planar('concrete',outer.difference(inner).difference(aisles),y1+.24,True)
for i in range(12):
 a=i*math.tau/12;radius=math.hypot(rx*math.cos(a),rz*math.sin(a));dx,dz=rx*math.cos(a)/radius,rz*math.sin(a)/radius
 J=Frame(B,ax+radius*.5*dx,az+radius*.5*dz,math.atan2(dx,dz),y=.24)
 J.stairs(0,0,1.6,11.4,radius*.29);J.stairs(0,radius*.29,1.6,3.0,radius*.05,y=11.4);J.stairs(0,radius*.34,1.6,11.0,radius*.16,y=14.4)
# Enclosed concourse around the bowl, with six passageways beneath the seats.
# This hides the underside of the stands from the public entrance.
for j in range(240):
 a=j*math.tau/240;aa=(j+1)*math.tau/240;opening=gate_angle((a+aa)/2)
 for y0,y1 in [(3.5 if opening else 0,14.0),(14.0,25.9)]:
  B.face('charcoal',[A.p(rx*1.025*math.cos(ang),yy,rz*1.025*math.sin(ang)) for ang,yy in [(a,y0),(aa,y0),(aa,y1),(a,y1)]],True)
 B.face('magenta',[A.p(rx*1.026*math.cos(ang),yy,rz*1.026*math.sin(ang)) for ang,yy in [(a,4.0),(aa,4.0),(aa,4.25),(a,4.25)]])
for i in range(6):
 a=math.pi/12+i*math.pi/3;dx,dz=rx*math.cos(a),rz*math.sin(a);r=math.hypot(dx,dz);dx/=r;dz/=r
 G=Frame(B,ax+dx*r*1.025,az+dz*r*1.025,math.atan2(-dx,-dz))
 G.box('blackiron',(0,4.75,-.8),(6.2,.95,.12))
 G.text('ARENA  /  '+str(101+i),(0,4.55,-.89),.48,'letter')
 # Tunnel walls and roof stop before the open arena floor.
 for side in [-1,1]:G.box('concrete',(side*2.5,1.75,r*.2575),(.2,3.5,r*.515))
 G.box('charcoal',(0,3.55,r*.2575),(5,.18,r*.515))
 G.light(0,3.2,r*.16,0xe4efff,240,15)
 # Counters sit outside the bowl wall and leave the entrance passages clear.
 for side in [-1,1]:
  px,_,pz=G.p(side*9,0,-2.8)
  if not p.buffer(-3.5).contains(Point(px,pz)):continue
  G.box('blackiron',(side*9,2.45,-.75),(6,4.9,.35))
  G.box('copperpanel',(side*9,.62,-2.7),(6,1.24,1.3),True)
  G.box('charcoal',(side*9,1.29,-2.7),(6.2,.13,1.5))
  G.box('magenta',(side*9,4.35,-1.1),(6,.35,.6))
  G.text('CONCESSIONS' if side<0 else 'REFRESHMENTS',(side*9,3.82,-1.16),.34,'letter')
  for column in [-1.8,0,1.8]:
   G.box('screen',(side*9+column,2.65,-1.0),(1.5,1.45,.08))
   G.text('MENU',(side*9+column,2.99,-1.08),.18,'letter')
   for line in range(4):G.box('letter',(side*9+column,2.7-line*.2,-1.09),(1.05,.026,.01))
  for register in [-2,2]:
   G.box('steel',(side*9+register,1.55,-2.8),(.5,.4,.35))
   G.box('screen',(side*9+register,1.63,-3.0),(.43,.26,.035))
  G.light(side*9,5.1,-3.0,0xffead0,180,12)
  G.bench(side*16,-3.0)
concourse=p.difference(scale(Point(ax,az).buffer(1,resolution=96),rx*1.026,rz*1.026))
B.planar('plaster',concourse,6.6)
F.text('ARENA CONCOURSE',(0,4.2,20),.65,'letter')
A.box('charcoal',(0,25,0),(15,7,10));
for side in [-1,1]:
 A.box('screen',(0,25,side*5.1),(14.5,6.5,.05));A.box('screen',(side*7.6,25,0),(.05,6.5,9.5))
A.text('VEGAS',(0,25,-5.2),1.5,'letter');A.text('GOLDEN KNIGHTS',(0,22.7,-5.2),.55,'letter')
for x in [-45,0,45]:
 for z in [-43,0,43]:A.light(x,32,z,0xe3ebff,1400,60)
spec['zones'].append(dict(origin=[ax,.24,az-rz],yaw=0,width=rx*2,depth=rz*2,height=35))
spec['routes']=[dict(points=[F.p(0,0,-5),F.p(0,0,4),F.p(0,0,16)])]
spec['views']['bowl']=dict(eye=[ax+3,14,az-57],target=[ax,4,az+10])

exec(compile(Path('tools/strip-landmarks/next_arrivals.py').read_text(),'next_arrivals.py','exec'))

from forum_shops import exterior as forum_shops_exterior
venues.append(forum_shops_exterior(B))

# Every venue's entrance is a tested route, and all metadata remains local.
for s in venues:
 s['lights']=[l for l in B.lights if l['venue']==s['key']]
 if 'routes' not in s:
  zone=s['zones'][0];F=Frame(B,zone['origin'][0],zone['origin'][2],zone['yaw'],zone['origin'][1]);s['routes']=[dict(points=[F.p(0,0,-3),F.p(0,0,3),F.p(0,0,min(12,zone['depth']-1))])]
(OUT/'venues.json').write_text(json.dumps(venues,separators=(',',':')))
(OUT/'replacement-ids.json').write_text(json.dumps(sorted(replacement)))
(OUT/'guest-towers.json').write_text(json.dumps(towers,indent=2))
from venetian_surface_ownership import reconcile
reconcile(B)
B.save_all()
print('LANDMARKS',len(venues),'batches',len(B.groups),'triangles',sum(len(g['faces']) for g in B.groups.values()),'replacement features',len(replacement),flush=True)
