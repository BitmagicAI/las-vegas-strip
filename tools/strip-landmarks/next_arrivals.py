"""Second landmark pass: separately authored resort podiums, arrival halls and Polo.
Executed by build.py with its batched geometry helpers. Metres, surveyed footprints.
The photographs guide finishes and landmark details, not an invented as-built plan.
"""
def ring(F,mat,x,y,z,rx,rz,r=.04,n=80):
 F.path(mat,[(x+rx*math.cos(a),y,z+rz*math.sin(a)) for a in np.linspace(0,math.tau,n+1)],r)
def leafy_planter(F,x,z):
 F.lathe('ivory',x,z,[(0,.90),(.10,.95),(.65,.86),(.70,.92),(.74,.92)],48)
 F.lathe('bark',x,z,[(.68,0),(.68,.84)],40)
 rng=random.Random(78+int(x*11))
 for j in range(42):
  a=rng.random()*math.tau;r=rng.uniform(.15,.74);xx=x+r*math.cos(a);zz=z+r*math.sin(a);hh=rng.uniform(1.05,2.1)
  F.tube('foliage',(xx,.70,zz),(xx+.12*math.cos(a),hh,zz+.12*math.sin(a)),.014,6)
  for k in range(7):
   yy=.82+k*(hh-.82)/7;ang=a+k*2.4;ll=rng.uniform(.16,.32);dx,dz=math.cos(ang),math.sin(ang)
   # Folded lanceolate leaves have a raised midrib and tapered tips.
   p=(xx,yy,zz);tip=(xx+dx*ll*1.6,yy+.10,zz+dz*ll*1.6);mid=(xx+dx*ll*.7,yy+.16,zz+dz*ll*.7)
   left=(mid[0]-dz*ll*.34,yy+.065,mid[2]+dx*ll*.34);right=(mid[0]+dz*ll*.34,yy+.065,mid[2]-dx*ll*.34)
   for tri in [(p,left,mid),(left,tip,mid),(tip,right,mid),(right,p,mid)]:B.face('foliage' if j%3 else 'sage',[F.p(*q) for q in tri])
def flowers(F,x,z,size=1,color='letter'):
 F.lathe('stone',x,z,[(0,.35*size),(.15,.42*size),(.5,.25*size),(.9,.43*size)],28)
 rng=random.Random(65)
 for j in range(65):
  a=rng.random()*math.tau;r=.72*size*math.sqrt(rng.random());y=1.05+.7*size*(1-r/(size*.85));xx=x+r*math.cos(a);zz=z+r*math.sin(a)
  F.tube('foliage',(x,.7,z),(xx,y,zz),.012,5)
  B.sphere(color,F.p(xx,y,zz),.105*size,8,6)
  if j%3==0:B.sphere('foliage',F.p(xx,y-.24,zz),.15*size,8,5,scale=(1,.4,1))
def column(F,x,z,h=7,mat='ivory',r=.38):
 F.lathe(mat,x,z,[(0,r*1.4),(.12,r*1.4),(.22,r*1.2),(.35,r),(h-.65,r*.9),(h-.5,r*1.2),(h-.32,r*1.4),(h,r*1.4)],32)
 for yy in [.13,.27,h-.46,h-.27]:ring(F,'brass',x,yy,z,r*1.26,r*1.26,.025,40)
def framed_wall(F,w,d,h,mat='sage',classic=False):
 for side in [-1,1]:
  for zz in np.arange(3,d-2,4):
   x=side*(w/2-.22)
   F.box(mat,(x,2.6,zz),(.15,4.9,3.75))
   for z in [zz-1.62,zz+1.62]:F.box('ivory',(x-side*.10,2.8,z),(.055,3.9,.075))
   for y in [.85,4.75]:F.box('ivory',(x-side*.10,y,zz),(.055,.075,3.25))
   F.box('brass',(x-side*.23,2.7,zz),(.18,.9,.12));F.box('warm',(x-side*.36,2.8,zz),(.16,.65,.22))
  for yy in [.16,.48,5.5,h-.16]:F.box('ivory',(side*(w/2-.20),yy,d/2),(.18,.18,d))
def coffers(F,w,d,h,mat='sage',step=6):
 for z in np.arange(3,d-1,step):
  for x in np.arange(-w/2+3,w/2-1,6):
   F.box('plaster',(x,h-.02,z),(5.4,.10,step-.7))
   for xx in [x-2.8,x+2.8]:
    F.box(mat,(xx,h-.24,z),(.32,.4,step-.25));F.box('ivory',(xx,h-.46,z),(.43,.07,step-.25));F.box('warm',(xx+(.24 if xx<x else -.24),h-.31,z),(.025,.018,step-.6))
   for zz in [z-step/2+.15,z+step/2-.15]:F.box(mat,(x,h-.24,zz),(5.7,.40,.30))
   if int(round(x+z))%2==0:F.chandelier(x,z,h-1.4)
def console(F,x,z,mat='walnut',brand=None):
 F.box(mat,(x,.58,z),(2.3,1.16,.82),True);F.box('marble',(x,1.18,z),(2.4,.11,.90))
 for xx in np.arange(x-1,x+1.1,.33):F.box('brass',(xx,.65,z-.43),(.018,.78,.02))
 F.box('darkglass',(x,1.48,z+.1),(.6,.38,.055));F.box('steel',(x,1.30,z+.15),(.16,.19,.12))
 if brand:F.text(brand,(x,.70,z-.45),.16,'letter')
def lamps(F,x,z,y=1.3):
 F.lathe('brass',x,z,[(y,.14),(y+.03,.14),(y+.1,.04),(y+.75,.04)],16)
 F.lathe('warm',x,z,[(y+.48,.26),(y+.93,.23)],20)
def gaming(F,w,d,start,mat='carpet'):
 for zz in np.arange(start,d-5,10):
  for side in [-1,1]:
   xx=side*(w/2-7);carpet(F,xx,zz,10,8,mat)
   for dz in [-1.5,1.5]:
    for dx in [-3,-1.8,-.6,.6,1.8,3]:F.slot(xx+dx,zz+dz)
   F.box('charcoal',(xx,3.3,zz),(7,.65,.14));F.text('CASINO',(xx,3.25,zz-.10),.3)
  F.light(0,5.8,zz,0xffe6c8,240,18)
def podium_skin(shape,h,key,holes,gallery_mask,oculus=None):
 # Block ownership stays with this footprint. Detail projects at most 24 cm.
 mat={'park':'sage','palazzo':'ivory','ti':'ochre','harrahs':'sandstone'}[key]
 B.shell(shape,.12,h,mat,holes,roof=False,interior=(gallery_mask,5.45))
 B.planar('harrahs-membrane-paint' if key=='harrahs' else 'roof',shape.difference(oculus) if oculus is not None else shape,h)
 if key=='palazzo':
  from palazzo_street import decorate
  decorate(B,shape,h,holes,gallery_mask)
  return
 B.detail=1
 for pp in parts(shape):
  for a,b in zip(list(pp.exterior.coords),list(pp.exterior.coords)[1:]):
   L=math.dist(a,b)
   if L<4:continue
   dx,dz=(b[0]-a[0])/L,(b[1]-a[1])/L;nx,nz=-dz,dx
   if pp.contains(Point((a[0]+b[0])/2+nx*.1,(a[1]+b[1])/2+nz*.1)):nx,nz=-nx,-nz
   J=Frame(B,a[0]+nx*.10,a[1]+nz*.10,math.atan2(-nx,-nz),y=0)
   if J.co*dx-J.si*dz<0:J=Frame(B,b[0]+nx*.10,b[1]+nz*.10,J.yaw,y=0)
   # Low stone courses stop at doors and internal through-passages.
   mask=unary_union([gallery_mask,*[Frame(B,o['p'][0],o['p'][2],o.get('yaw',0)).poly([(-o['width']/2-1,-3),(o['width']/2+1,-3),(o['width']/2+1,3),(-o['width']/2-1,3)]) for o in holes]])
   for y in [.38,1.2,h-1.1,h-.3]:
    line=LineString([a,b]).difference(mask) if y<5.5 else LineString([a,b])
    for seg in list(line.geoms) if hasattr(line,'geoms') else [line]:
     if seg.geom_type=='LineString' and seg.length>.03:B.tube('ivory',(seg.coords[0][0],y,seg.coords[0][1]),(seg.coords[-1][0],y,seg.coords[-1][1]),.11,4)
   for xx in np.arange(2.6,L,5.2):
    wx,_,wz=J.p(xx,0,0)
    if gallery_mask.distance(Point(wx,wz))<2.5 or any(math.hypot(wx-o['p'][0],wz-o['p'][2])<o['width']/2+3 for o in holes):continue
    J.box(mat,(xx,h/2,-.07),(.45,h,.30))
    if key in ['ti','palazzo']:
     J.box('darkglass',(xx,h-3.8,-.02),(3.9,3.3,.06));J.arch(xx,-.12,4.1,h-1.7,'ivory',.13,h-5.7)
     for x in [xx-1.45,xx,xx+1.45]:J.box('brass',(x,h-3.8,-.10),(.06,3.3,.08))
    else:
     J.box('darkglass',(xx,h-2.2,-.02),(4.6,2.1,.06))
     for x in np.arange(xx-2.1,xx+2.2,.7):J.box('steel',(x,h-2.2,-.10),(.055,2.2,.08))
 B.detail=0

def public_shell(config):
 key=config['key'];enter(key);shape=footprint(config['source']);x,z,yaw=config['frame'];F=Frame(B,x,z,yaw);w,d,h=config['width'],config['depth'],config['height']
 portal=F.portal(w=6.2,h=4.5,name=config['name']+' public entrance');spec=venue(key,config['name'],shape,F,w,d,h,portal);spec['building']=config['building'];spec['connections']=config['connections'];spec['routes']=[]
 spec['views']['skyline']=dict(eye=F.p(110,85,-150),target=F.p(0,28,65))
 replacement.add(config['source']);B.source=key+'-podium'
 # Retain the independently usable existing entrance to every guest core.
 ht=[t for p in json.load(open('build/highrises/plan.json')) if p['key']==config['building'] for t in p['towers']]
 existing=[]
 for t in ht:
  a,b,c,dd=t['linear'];ox,oy,oz=t['origin'];front=t['lobbyFront']
  existing.append(dict(p=[ox+b*front,oy,oz+dd*front],yaw=math.atan2(b,dd),width=5,height=4.8))
 gallery_mask=unary_union([LineString(c['points']).buffer(2.45,cap_style=2,join_style=2) for c in config['connections']])
 oculus=Point(*[F.p(0,0,16)[i] for i in [0,2]]).buffer(8.5,quad_segs=32) if key=='palazzo' else None
 glazed=arrival(F,portal,w-1,h-.5);podium_skin(shape,h+1,key,[glazed,*existing],gallery_mask,oculus)
 spec['accessPoints']=[[c['points'][-1][0],.24,c['points'][-1][1]] for c in config['connections']]
 if key=='harrahs':replacement.update(['way/128632722','way/442763644'])
 enter(key,'interior',key+'-arrival');public=F.poly([(-w/2,.04),(w/2,.04),(w/2,d),(-w/2,d)])
 openings=[glazed];gallery=[]
 for conn in config['connections']:
  line=LineString(conn['points']);gallery.append(line.buffer(2.2,cap_style=2,join_style=2));p=conn['points'][-1];openings.append(dict(p=[p[0],.24,p[1]],yaw=conn['yaw'],width=4.4,height=4.5))
  points=[[xx,.27,zz] for xx,zz in conn['points']];spec['routes'].append(dict(points=[list(F.p(0,.03,3)),*points]))
  for a,b in zip(conn['points'],conn['points'][1:]):
   L=math.dist(a,b);J=Frame(B,a[0],a[1],math.atan2(b[0]-a[0],b[1]-a[1]))
   spec['zones'].append(dict(origin=J.p(0,0,0),yaw=J.yaw,width=4.5,depth=L+.1,height=5.4))
   for zz in np.arange(3,L-1,6):
    J.box('warm',(0,4.52,zz),(2.6,.05,.12));J.light(0,4.2,zz,0xffead2,95,12)
    for side in [-1,1]:J.box('brass',(side*2.13,1.10,zz),(.035,.10,5.8))
   J.text('GUEST ROOMS  /  STAIRS',(0,3.4,max(.5,L-3)),.22,'brass')
 # Union walls remove joints instead of stacking overlapping room boxes.
 union=unary_union([public,*gallery]);B.planar('marble',union,.26,True);B.shell(union,.26,5.1,'plaster',openings,roof=False)
 # Taller main atrium walls meet the lower side galleries under a lintel.
 B.shell(public,5.1,h+.24,'plaster',[],roof=False)
 B.planar('plaster',union.difference(public),5.2)
 ceiling=public.difference(Point(*[F.p(0,0,16)[i] for i in [0,2]]).buffer(8.5,quad_segs=32)) if key=='palazzo' else public
 B.planar('plaster',ceiling,h+.24)
 for ringpoly in parts(union):
  for a,b in zip(list(ringpoly.exterior.coords),list(ringpoly.exterior.coords)[1:]):
   if any(LineString([a,b]).distance(Point(o['p'][0],o['p'][2]))<.4 for o in openings):continue
   B.tube('brass',(a[0],.45,a[1]),(b[0],.45,b[1]),.035,4)
 spec['routes'].append(dict(points=[F.p(0,.03,-3),F.p(0,.03,3),F.p(0,.03,d-3)]))
 return F,spec,shape

for config in json.load(open('build/strip-landmarks/next-plan.json')):
 key=config['key'];F,spec,shape=public_shell(config);w,d,h=config['width'],config['depth'],config['height']
 spec['views']['entrance']=dict(eye=F.p(5,2.7,-39),target=F.p(0,6.5,1))
 if key=='park':
  # Eataly's double-height steel pavilion and pitched glazed roof.
  enter(key,'exterior','eataly-pavilion')
  for x in [-w/2+1,w/2-1]:
   F.box('steel',(x,6,-5),(.48,12,.48));F.box('steel',(x,6,1),(.48,12,.48))
  for z in [-8,-4,0,4]:
   F.path('steel',[(-w/2+1,11.5,z),(0,14.5,z),(w/2-1,11.5,z)],.24)
   F.box('steel',(0,8.7,z),(w-1,.35,.3))
  for x in np.arange(-w/2+2,w/2,2.5):
   yy=14.5-abs(x)/(w/2-1)*3;F.tube('steel',(x,yy,-8),(x,yy,4),.065)
  B.face('glass',[F.p(-w/2+1,11.6,-8),F.p(0,14.6,-8),F.p(0,14.6,4),F.p(-w/2+1,11.6,4)])
  B.face('glass',[F.p(0,14.6,-8),F.p(w/2-1,11.6,-8),F.p(w/2-1,11.6,4),F.p(0,14.6,4)])
  F.text('PARK MGM',(0,10.1,-8.3),1.8);F.text('E A T A L Y',(0,6.5,-4.2),1.05);F.text('ALTI CIBI',(0,5.8,-4.21),.30)
  for x in [-17,17]:F.plant(x,-10,True)
  enter(key,'interior','park-arrival')
  framed_wall(F,w,d,h,'sage');coffers(F,w,d,h,'sage',8)
  # The public approach reads as an Italian food market, then a garden reception.
  for side in [-1,1]:
   for z,label in [(10,'LA PASTA'),(20,'IL MERCATO'),(30,'CAFFE ITALIANO')]:
    x=side*(w/2-6);F.box('walnut',(x,.58,z),(8,1.16,1.55),True);F.box('marble',(x,1.22,z),(8.2,.12,1.65))
    F.box('sage',(x,4.7,z+1.0),(8.3,.8,.35));F.text(label,(x,4.6,z+.79),.40)
    for xx in np.arange(x-3.5,x+3.7,.7):
     F.lathe('copper2',xx,z,[(1.3,.11),(1.6,.11),(1.8,.04)],10)
     F.box('letter',(xx,1.52,z-.12),(.14,.10,.025))
    for zz in [z+1.8,z+2.6]:
     F.box('walnut',(x,2.25,zz),(8,.1,.4))
     for i in range(28):F.lathe('bottle',x-3.7+i*.27,zz,[(2.3,.055),(2.55,.055),(2.65,.02),(2.71,.02)],8)
    for xx in [x-2,x+2]:F.tube('blackiron',(xx,9,z),(xx,3.8,z),.02);F.lathe('brass',xx,z,[(3.5,.42),(3.7,.20),(3.8,.08)],24)
  z=48
  for x in [-14,-7,7,14]:
   F.box('sage',(x,4,z),(1.1,8,1.1));F.box('mirror',(x,4,z-.57),(.90,7.5,.035))
   for xx in [x-.5,x+.5]:F.box('ivory',(xx,4,z-.61),(.055,7.8,.07))
   flowers(F,x,z-3,1.2)
  # Suspended root artwork: tapering, interwoven branches with many fine roots.
  rng=random.Random(31)
  B.sphere('rootwood',F.p(0,8.4,z+1),.8,32,20,scale=(1.7,.5,1))
  def branch(points,r,depth):
   for i,(a,b) in enumerate(zip(points,points[1:])):B.tube('rootwood',F.p(*a),F.p(*b),r*.76**i,12,r*.76**(i+1))
   if depth:
    x,y,zz=points[-1];angle=rng.random()*math.tau
    for side in [-1,1]:
     ang=angle+side*.8;L=2.1 if depth==2 else 1.25
     branch([(x,y,zz),(x+math.cos(ang)*L*.55,y+rng.uniform(-.3,.4),zz+math.sin(ang)*L*.55),(x+math.cos(ang)*L,y+rng.uniform(-.3,.3),zz+math.sin(ang)*L)],r*.51,depth-1)
  for j in range(22):
   a=rng.random()*math.tau;length=rng.uniform(3.0,6.5)
   branch([(rng.uniform(-.65,.65),8.4,z+1),(length*.5*math.cos(a+.2),rng.uniform(7.9,8.7),z+1+length*.35*math.sin(a+.2)),(length*math.cos(a),rng.uniform(8.0,8.7),z+1+length*.65*math.sin(a))],rng.uniform(.10,.20),3)
  for x in [-8,-4,4,8]:console(F,x,58,'sage','PARK MGM');lamps(F,x,58)
  
  for side in [-1,1]:
   F.box('sage',(side*9.1,3.1,62),(11.8,5.6,.35));F.box('brass',(side*9.1,3.7,61.79),(8,3.3,.1));F.box('ivory',(side*9.1,3.7,61.71),(7.7,3,.04))
   # Dimensional botanical relief panels, with individual stems and leaves.
   for j in range(11):
    xx=side*9.1-3.3+j*.65;top=3.9+.8*math.sin(j*1.7)
    F.path('foliage',[(xx,2.35,61.67),(xx+.15,3.25,61.65),(xx-.12,top,61.64)],.013,6)
    for k in range(5):
     yy=2.6+k*.32
     if yy>top:continue
     for s in [-1,1]:B.sphere('sage',F.p(xx+s*.19,yy+.10,61.64),.17,12,8,scale=(1.4,.48,.12))
   leafy_planter(F,side*5,44)
  for r in [6.2,6.5,8.5]:ring(F,'brass',0,.043,49,r,r*.64,.025)
  # Central gate in reception leaves the through-route open.
  # Feature wall itself is decorative, with an opening through its middle.
  F.text('GUEST SERVICES',(0,6.2,59),.56,'brass')
  for x in [-15,15]:F.lounge(x,65);flowers(F,x,70,1.1)
  gaming(F,w,d,77,'parkcarpet')
  spec['views']['lobby']=dict(eye=F.p(0,1.7,37),target=F.p(0,4.4,56))
 elif key=='palazzo':
  enter(key,'exterior','palazzo-mapped-canopy')
  from palazzo_street import canopy
  canopy(B)
  replacement.add('way/180584267')
  enter(key,'interior','palazzo-atrium');framed_wall(F,w,d,h,'champagne',True)
  # Twelve fluted bronze columns frame the circular fountain hall.
  z=16
  for a in np.linspace(math.pi/12,math.tau+math.pi/12,12,endpoint=False):
   x=10.5*math.cos(a);zz=z+10.5*math.sin(a);column(F,x,zz,9.3,'bronze',.37)
   for t in np.linspace(0,math.tau,16,endpoint=False):F.tube('brass',(x+.34*math.cos(t),.5,zz+.34*math.sin(t)),(x+.31*math.cos(t),8.6,zz+.31*math.sin(t)),.018,5)
  for rx,y in [(11.1,9.2),(10.8,9.6),(8.5,11.7)]:ring(F,'champagne',0,y,z,rx,rx,.24)
  for i in range(12):
   a=i*math.tau/12+math.pi/12;b=(i+1)*math.tau/12+math.pi/12;F.path('champagne',[(10.5*math.cos(aa),9.2+1.3*math.sin((aa-a)*6),z+10.5*math.sin(aa)) for aa in np.linspace(a,b,25)],.22)
  # Recessed luminous dome closes the rotunda above the coffered ceiling.
  for a,b in zip(np.linspace(0,math.tau,65),np.linspace(0,math.tau,65)[1:]):
   for q,qq in zip(np.linspace(0,math.pi/2,20),np.linspace(0,math.pi/2,20)[1:]):
    B.face('skyglass',[F.p(8.5*math.cos(aa)*math.sin(bb),12.24+2.6*math.cos(bb),z+8.5*math.sin(aa)*math.sin(bb)) for aa,bb in [(a,q),(b,q),(b,qq),(a,qq)]])
  for a in np.linspace(0,math.tau,24,endpoint=False):F.path('ivory',[(8.5*math.cos(a)*math.sin(q),12.20+2.6*math.cos(q),z+8.5*math.sin(a)*math.sin(q)) for q in np.linspace(0,math.pi/2,24)],.07)
  # An open route skirts the fountain; the center is a sculptural water feature.
  F.lathe('bronze',0,z,[(0,4.7),(.25,4.7),(.4,4.55),(.6,4.55),(.68,4.4)],72)
  F.lathe('water',0,z,[(.58,0),(.58,4.3)],72)
  F.lathe('sandstone',0,z,[(.59,1.8),(.80,1.8),(1.1,1.2),(1.6,1.2)],48)
  # Translucent upright Acqua di Cristallo-inspired figures and water jets.
  for x in [-.83,0,.83]:
   F.lathe('ice',x,z,[(1.6,.34),(1.9,.29),(2.3,.22),(2.6,.22),(2.9,.29),(3.2,.18),(3.5,.25),(3.75,.29),(3.91,.12),(4.04,.10)],36)
   B.sphere('ice',F.p(x,4.25,z),.22,32,20,scale=(.82,1.12,.86))
   B.sphere('ice',F.p(x,4.23,z-.18),.047,16,12,scale=(.5,1.1,1))
   for s in [-1,1]:
    F.path('ice',[(x+s*.23,3.74,z),(x+s*.43,3.38,z-.07),(x+s*.22,3.24,z-.29)],.085,16)
    B.sphere('ice',F.p(x+s*.20,3.24,z-.30),.09,16,10,scale=(.5,1,1))
   F.lathe('ice',x,z-.30,[(3.12,.10),(3.20,.19),(3.44,.21),(3.49,.14)],24)
   for a in np.linspace(0,math.tau,22,endpoint=False):
    F.path('ice',[(x+.335*math.cos(a),1.61,z+.335*math.sin(a)),(x+.25*math.cos(a+.11),2.0,z+.25*math.sin(a+.11)),(x+.20*math.cos(a+.18),2.65,z+.20*math.sin(a+.18))],.013,6)
  for a in np.linspace(0,math.tau,32,endpoint=False):
   F.path('skyglass',[(3.8*math.cos(a)*(1-t*.45),.65+1.8*math.sin(t*math.pi),z+3.8*math.sin(a)*(1-t*.45)) for t in np.linspace(0,1,16)],.018,5)
  for a in np.linspace(0,math.tau,32,endpoint=False):flowers(F,5.4*math.cos(a),z+5.4*math.sin(a),.5,'rose')
  for r in [6.3,8.7,12.0]:ring(F,'brass',0,.041,z,r,r,.035)
  for side in [-1,1]:
   F.reception(side*12,36,9,'THE PALAZZO');lamps(F,side*12,36);F.chandelier(side*12,33,8.8)
   for zz in [42,51]:F.lounge(side*12,zz);flowers(F,side*16,zz,1.2)
  for zz in [34,44,54]:F.chandelier(0,zz,10.2);F.light(0,9,zz,0xffe8cb,450,24)
  gaming(F,w,d,57,'palazzocarpet')
  spec['routes']=[dict(points=[F.p(0,.03,-3),F.p(0,.03,3),F.p(7.2,.03,9),F.p(7.2,.03,23),F.p(0,.03,29),F.p(0,.03,d-3)]),*spec['routes'][:-1]]
  # Redirect guest paths around the central fountain too.
  for route in spec['routes'][1:]:route['points']=[F.p(0,.03,3),F.p(7.2,.03,9),F.p(7.2,.03,23),F.p(0,.03,29),*route['points'][1:]]
  spec['views']['lobby']=dict(eye=F.p(1,1.7,3),target=F.p(0,5.0,17))
 elif key=='ti':
  enter(key,'exterior','treasure-island-arrival')
  for x in [-14,14]:column(F,x,-6,6.7,'ochre',.72)
  F.box('ochre',(0,6.8,-4),(w+2,1.1,10));F.box('ivory',(0,6.15,-4),(w+2,.20,10));F.text('TREASURE ISLAND',(0,7.1,-9.15),.94,'letter')
  for x in np.arange(-14,15,2):F.box('warm',(x,6.03,-6),(.12,.035,.12))
  # Ship sits in its own water basin beside the arrival, clear of the entrance lane.
  S=Frame(B,*[F.p(w/2+20,0,-5)[i] for i in [0,2]],F.yaw+.2)
  lagoon=S.poly([(-9,-20),(9,-20),(12,-12),(12,13),(6,22),(-8,20),(-12,10),(-12,-9)])
  B.extrude('stone',lagoon,-.05,.27,False);B.planar('water',lagoon.buffer(-.5),.31)
  # Watertight curved galleon hull with a high stern and swept pointed bow.
  stations=[(-17,.1,3.8),(-14,3.2,2.9),(-8,4.4,2.5),(2,4.8,2.4),(10,4.0,4.8),(14,3.5,5.4)]
  for (z0,r0,top0),(z1,r1,top1) in zip(stations,stations[1:]):
   for i in range(16):
    a=math.pi+i*math.pi/16;b=math.pi+(i+1)*math.pi/16
    B.face('shipwood',[S.p(r*math.cos(aa),top+(top-.6)*math.sin(aa),zz) for r,top,zz,aa in [(r0,top0,z0,a),(r1,top1,z1,a),(r1,top1,z1,b),(r0,top0,z0,b)]])
   for s in [-1,1]:
    for f in [.2,.45,.68,.85,1.0]:S.tube('gold',(s*r0*(.4+.6*f),.6+(top0-.6)*f,z0),(s*r1*(.4+.6*f),.6+(top1-.6)*f,z1),.05,6)
  for z0,r0,top0 in stations[1:]:
   S.box('shipwood',(0,top0,z0),(r0*2,.16,.8));S.rail((-r0,z0),(r0,z0),top0+1)
  S.box('shipwood',(0,2.5,-2),(8,.22,21));S.box('shipwood',(0,5.3,11),(6.5,.20,6))
  for x in [-3.7,3.7]:
   S.path('brass',[(x,3.4,-13),(x,3.3,6),(x*.83,6.3,14)],.07)
   for z in np.arange(-12,7,1):S.tube('brass',(x,2.5,z),(x,3.4,z),.045)
  for zz,hh in [(-7,18),(2,22),(10,17)]:
   S.tube('shipwood',(0,2.5,zz),(0,hh,zz),.18,14,.065)
   for y,ww in [(hh*.5,10),(hh*.74,8),(hh*.90,5)]:
    S.tube('shipwood',(-ww/2,y,zz),(ww/2,y,zz),.1,10);S.path('rope',[(-ww/2,y,zz),(0,y+2,zz),(ww/2,y,zz)],.027,5)
    for side in [-1,1]:S.tube('rope',(side*ww/2,y,zz),(side*3.6,3.2,zz+4),.018,5)
   S.lathe('shipwood',0,zz,[(hh*.66,1.0),(hh*.67,1.0)],24);ring(S,'brass',0,hh*.66+1,zz,1,1,.05)
   for x in [-3.7,3.7]:
    for dz in [-2,0,2]:S.tube('rope',(x,3.2,zz+dz),(0,hh*.8,zz),.025,5)
   S.tube('rope',(0,hh,zz),(0,4,-20),.022,5)
   S.box('red',(1.1,hh-.6,zz),(2.2,1.1,.05))
  S.tube('shipwood',(0,3.5,-14),(0,7,-24),.16,10,.08)
  for side in [-1,1]:
   for zz in [-9,-5,-1,3,7]:S.box('charcoal',(side*4.1,1.9,zz),(.03,.6,.8));S.tube('blackiron',(side*3.9,1.95,zz),(side*4.8,1.95,zz),.12,12)
  for x in [-6,6]:S.plant(x,23,True)
  spec['views']['ship']=dict(eye=S.p(30,7,-34),target=S.p(0,8,0))
  from ti_facades import exterior as ti_facades
  ti_facades(B)
  enter(key,'interior','ti-reception');framed_wall(F,w,d,h,'ochre',True);coffers(F,w,d,h,'champagne',6)
  carpet(F,0,d/2,w-1,d-1,'ticarpet')
  # Sweeping marble reception with raised panel faces and continuous glowing countertop.
  for i in range(52):
   a=-.8+i*.026;x=-13+7*math.cos(a);zz=22+13*math.sin(a)
   J=Frame(B,*[F.p(x,0,zz)[n] for n in [0,2]],F.yaw-a)
   J.box('champagne',(0,.62,0),(.43,1.24,1.5),True);J.box('marble',(0,1.30,0),(.47,.12,1.65));J.box('warm',(0,1.19,-.8),(.45,.028,.03));J.box('brass',(0,.55,-.77),(.32,.72,.035))
  for a in [-.60,-.28,.04,.36]:
   xx=-13+7*math.cos(a);zz=22+13*math.sin(a)
   F.box('charcoal',(xx,1.62,zz),(.62,.42,.07));F.box('brass',(xx,1.40,zz),(.15,.15,.12));F.box('letter',(xx+.55,1.39,zz-.15),(.30,.018,.40))
  # Hotel arrival details: luggage trolleys, queue stanchions and bell storage.
  for zz in [8,11]:
   xx=-12.2;F.box('walnut',(xx,.18,zz),(1.15,.10,.72))
   for sx in [-.5,.5]:
    for sz in [-.26,.26]:B.sphere('charcoal',F.p(xx+sx,.10,zz+sz),.09,12,8)
    F.path('brass',[(xx+sx,.2,zz-.27),(xx+sx,1.6,zz-.27),(xx+sx,1.84,zz),(xx+sx,1.6,zz+.27),(xx+sx,.2,zz+.27)],.033,10)
   F.tube('brass',(xx-.5,1.84,zz),(xx+.5,1.84,zz),.04,12)
   for j in range(3):
    F.box('velvet',(xx-.35+j*.34,.5,zz),(.29,.55,.42));F.path('brass',[(xx-.41+j*.34,.79,zz),(xx-.41+j*.34,.85,zz),(xx-.26+j*.34,.85,zz),(xx-.26+j*.34,.79,zz)],.012,6)
  for zz in [12,16,20,24]:
   for xx in [-3.7,-1.9]:F.lathe('brass',xx,zz,[(0,.18),(.045,.18),(.10,.035),(.95,.035),(1.03,.08),(1.08,.03)],20)
   if zz<24:F.path('velvet',[(-3.7,1,zz),(-3.7,.88,zz+2),(-3.7,1,zz+4)],.035)
  F.text('BELL DESK',(-10,4.3,28),.5,'brass')
  for z in [8,17,26,35]:
   for x in [-14,14]:column(F,x,z,h,'ochre');F.chandelier(x*.5,z,h-1.5)
  for z in [11,23,34]:F.lounge(11,z);F.plant(14,z)
  # Paneled back reception wall and framed maritime prints.
  for z in np.arange(9,d-2,6):
   F.box('walnut',(-w/2+.5,3,z),(.16,4.0,4.3));F.box('gold',(-w/2+.4,3,z),(.16,3.2,3.6));F.box('nautical',(-w/2+.3,3,z),(.06,3.0,3.4))
  spec['views']['lobby']=dict(eye=F.p(1,1.7,5),target=F.p(-7,3.4,24))
 elif key=='harrahs':
  enter(key,'exterior','harrahs-marquee')
  from harrahs_facades import exterior as harrahs_facades
  harrahs_facades(B)
  enter(key,'interior','harrahs-lobby');framed_wall(F,w,d,h,'champagne');coffers(F,w,d,h,'charcoal',8)
  for side in [-1,1]:
   for i in range(5):
    xx=side*(5.7+i*2.05);console(F,xx,17,'charcoal');F.box('amethyst',(xx,.68,16.56),(1.85,.86,.035));lamps(F,xx,17)
   F.box('plaster',(side*10,3.2,20),(13,6.2,.3))
   # Thousands of individually tilted petals form the flowing, layered reception wall.
   for j in range(64):
    x=side*10-6+j*.19
    for i in range(21):
     yy=1.1+i*.19+.38*math.sin(j*.18)+.18*math.cos(i*.4+j*.11)
     if yy<1.3 or yy>5.8:continue
     zz=19.60-.15*math.sin(j*.19+i*.12);mat=['teal','purple','orchid','rose'][min(3,max(0,int((yy-1.3)/1.13)))]
     B.face(mat,[F.p(x-.13,yy,zz),F.p(x,yy+.17,zz-.10),F.p(x+.14,yy,zz+.02),F.p(x,yy-.14,zz-.07)])
  for z in [27,38,49]:
   for x in [-12,12]:F.lounge(x,z);carpet(F,x,z,7,7,'harrahscarpet');F.chandelier(x,z,6.0)
  for zz in [7,24,40,56]:
   for r in [1,1.45,1.9]:ring(F,'warm',0,6.8,zz,r,r,.04)
  gaming(F,w,d,53,'harrahscarpet')
  spec['views']['lobby']=dict(eye=F.p(-.5,1.7,5),target=F.p(-7,3.0,18))
 # Public lighting is bounded at runtime; the fixture geometry carries the rest.
 for zz in np.arange(6,d-2,9):F.light(0,h-1.2,zz,0xffe9d3,320,22)

# Polo Towers: mapped H-shaped footprint, deeply recessed balconies, purple outline.
enter('polo');shape=footprint('way/27897911');F=Frame(B,149.728,1054.5,math.pi/2);portal=F.portal(w=5.6,h=3.3,name='Polo Towers registration');spec=venue('polo','Hilton Vacation Club Polo Towers',shape,F,18.4,23.022,4.4,portal);spec['building']='polo';replacement.add('way/27897911')
# Fit the reusable rooms across the crossbar, without expanding the map envelope.
t=add_guest('polo','Polo Towers', [220,.24,1054.5],7,15,[0,1,-1,0]);t.update(kind='apartment',lobbyFront=-47.25);spec['hotelSources']=['guest-polo']
B.source='guest-polo';B.shell(shape,.16,5.8,'champagne',[dict(portal,width=18.4,height=4.8)],roof=False);B.shell(shape.buffer(-1.1),5.8,57,'ivory',roof=False);B.planar('roof',shape,57)
for pp in parts(shape):
 for a,b in zip(list(pp.exterior.coords),list(pp.exterior.coords)[1:]):
  L=math.dist(a,b)
  if L<2:continue
  dx,dz=(b[0]-a[0])/L,(b[1]-a[1])/L;nx,nz=-dz,dx
  if pp.contains(Point((a[0]+b[0])/2+nx*.1,(a[1]+b[1])/2+nz*.1)):nx,nz=-nx,-nz
  J=Frame(B,a[0]+nx*.08,a[1]+nz*.08,math.atan2(-nx,-nz),y=0)
  if J.co*dx-J.si*dz<0:J=Frame(B,b[0]+nx*.08,b[1]+nz*.08,J.yaw,y=0)
  cols=max(1,round(L/4.1));cw=L/cols
  # Balconies are inset from the footprint; the slab and balustrade form depth.
  B.detail=1
  for y in np.arange(6.0,54,3.6):
   for j in range(cols):
    x=(j+.5)*cw
    # Alternating recessed balconies and punched windows in cream stucco.
    balcony=j%3!=1 and L>10
    if balcony:
     J.box('darkglass',(x,y+1.55,1.03),(cw-.90,2.5,.055));J.box('champagne',(x,y,.53),(cw,.22,1.4))
     arc=[(x+(cw/2-.22)*math.cos(a),-.02-.22*math.sin(a)) for a in np.linspace(0,math.pi,19)]
     for aa,bb in zip(arc,arc[1:]):
      B.face('champagne',[J.p(aa[0],y+.1,aa[1]),J.p(bb[0],y+.1,bb[1]),J.p(bb[0],y+.54,bb[1]),J.p(aa[0],y+.54,aa[1])])
     J.path('bronze',[(xx,y+.95,zz) for xx,zz in arc],.035,8)
     for xx,zz in arc:J.tube('bronze',(xx,y+.51,zz),(xx,y+.95,zz),.016,6)
     J.box('ivory',(x-cw/2,y+1.6,.42),(.40,3.4,1.56));J.box('silver',(x,y+1.55,1.00),(.05,2.5,.03))
    else:
     J.box('ivory',(x,y+1.7,.43),(cw,3.4,1.25))
     J.box('champagne',(x,y+1.88,-.23),(1.70,1.86,.14));J.box('darkglass',(x,y+1.88,-.31),(1.48,1.66,.04));J.box('silver',(x,y+1.88,-.34),(.035,1.66,.025))
  B.detail=0;J.box('champagne',(L/2,55.5,-.10),(L,2.5,.25));J.box('purple',(L/2,56.9,-.26),(L,.075,.075))
  for xx in [.13,L-.13]:J.box('purple',(xx,30,-.27),(.07,53,.07))
# The actual arrival is a covered motor court with stone-wrapped round piers.
B.source='polo-motor-court';arrival(F,portal,18.4,4.3);F.box('champagne',(0,4.55,-4),(22,.5,10));F.text('POLO TOWERS',(0,5.0,-9.05),.95,'purple');F.text('REGISTRATION  /  VALET',(0,3.7,-9.08),.28,'brass')
for x in [-9,9]:
 F.lathe('champagne',x,-6,[(0,.63),(4.4,.63)],32)
 for row in range(8):
  for a in np.linspace(0,math.tau,20,endpoint=False):
   B.sphere(['stone','ivory','sandstone'][row%3],F.p(x+.62*math.cos(a),.1+row*.14,-6+.62*math.sin(a)),.11,6,4,scale=(1,.55,1))
 F.plant(x,-10)
for xx in np.arange(-7,8,2.5):F.box('warm',(xx,4.25,-5),(.16,.035,.16))
# The tall, blank stucco sign blade is a defining part of the photographed tower.
F.box('champagne',(0,31.0,-.44),(10.3,51.7,.35));F.box('ivory',(0,56.8,-.46),(10.8,.32,.48))
for xx in [-5.1,5.1]:F.box('purple',(xx,31,-.66),(.075,51.5,.07))
F.text('POLO',(0,43.5,-.67),1.6,'purple');F.text('TOWERS',(0,41.6,-.67),1.22,'purple');F.path('purple',[(-2.4,48,-.67),(0,50.6,-.67),(2.4,48,-.67),(0,45.4,-.67),(-2.4,48,-.67)],.10)
# Roof equipment, screened terraces and the small rooftop recreation deck.
B.source='polo-roof'
for x in [-12,12]:
 F.box('champagne',(x,58,23),(7,2,14));F.box('roof',(x,59.2,23),(7.4,.4,14.4))
 for xx in np.arange(x-3,x+3.1,.45):F.box('steel',(xx,58.2,15.85),(.12,1.4,.06))
F.box('ivory',(0,57.15,30),(8,.3,12));F.box('water',(0,57.32,30),(6.7,.035,10.7))
for side in [-1,1]:F.box('ivory',(side*3.9,57.5,30),(.2,.7,12.2))
enter('polo','interior','polo-lobby');atrium(F,18.4,23.022,4.4,front=False,rear=False);rear_portal(F,18.4,4.0,23.022,4.4)
# Elliptical yellow cove, stone light boxes, walnut screens and bronze horses.
for r in [1,1.035]:ring(F,'yellowled',0,4.05,10,6.5*r,4.4*r,.06)
for x in [-6.6,6.6]:
 F.box('walnut',(x,2.0,10),(1.1,4,1.1));F.box('amethyst',(x,2.0,9.41),(.85,3.6,.025));F.box('brass',(x,3.95,10),(1.3,.14,1.3))
# Horse sculpture is an authored three-dimensional bronze silhouette, not a billboard.
def horse(x,z,scale=1):
 def H(dx,y,dz=0):return (x+dx*scale,.24+y*scale,z+dz*scale)
 B.sphere('bronze',F.p(*H(0,1.15)),.52*scale,32,20,scale=(1.5,.88,.59))
 for side in [-1,1]:
  for dx in [-.55,.57]:
   F.path('bronze',[H(dx,1.20,side*.23),H(dx+.12,.60,side*.25),H(dx+.02,.04,side*.27)],.068*scale,12)
   B.sphere('bronze',F.p(*H(dx+.06,.035,side*.27)),.10*scale,20,12,scale=(1.25,.55,1))
 F.tube('bronze',H(.45,1.25),H(.60,1.72),.24*scale,24,.17*scale)
 F.tube('bronze',H(.60,1.72),H(.84,1.95),.17*scale,24,.12*scale)
 B.sphere('bronze',F.p(*H(.95,1.94)),.20*scale,32,20,scale=(1.20,1.05,.68))
 B.sphere('bronze',F.p(*H(1.14,1.78)),.19*scale,32,20,scale=(1.35,.72,.60))
 for side in [-1,1]:F.tube('bronze',H(.85,2.06,side*.1),H(.80,2.25,side*.12),.055*scale,12,.012*scale)
 F.path('bronze',[H(-.65,1.25),H(-.92,1.12,.08),H(-1.0,.63,.1)],.075*scale,12)
 for j in range(9):F.path('bronze',[H(.49+j*.032,1.60+j*.047),H(.41+j*.029,1.58+j*.047),H(.42+j*.03,1.48+j*.047)],.022*scale,8)
F.box('charcoal',(-5.1,.12,8),(4.5,.24,2.1),True);horse(-5.9,8,1);horse(-4.0,8.25,.75)
for x in [-6,6]:
 F.lounge(x,14);F.plant(x,17)
 for zz in [3.5,5.5]:F.box('walnut',(x,2.2,zz),(.10,3.9,.10))
F.reception(5,7.4,6,'POLO TOWERS');lamps(F,5,7.4)
for j in range(46):
 xx=-8.7+j*.385;F.box('purple',(xx,2.5,19.55),(.10,2.4,.025)) if abs(xx)>2.3 else None
spec['routes']=[dict(points=[F.p(0,.03,-3),F.p(0,.03,3),F.p(0,.03,23.1)])]
spec['views']['skyline']=dict(eye=F.p(78,55,-135),target=F.p(0,28,25));spec['views']['lobby']=dict(eye=F.p(0,1.65,3),target=F.p(-2,2.1,11))
