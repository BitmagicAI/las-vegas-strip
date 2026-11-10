"""Original Westwood/Highland geometry from dated photos; measured map footprints.
Heights, roof equipment positions and the small customer display plan are inferred.
Reference register: docs/project-records/westwood-2650/references.json.
"""
from common import *
from shapely.geometry.polygon import orient
COLORS={'wc-white-stucco':'deded1','wc-joint':'b5b8b0','wc-cap':'596268','wc-brick':'986950','wc-mortar':'b39b81','wc-glass':'283b42','wc-frame':'7b8485','wc-roof':'b8bbb5','wc-equipment':'959e97','wc-concrete':'ada79a','wc-gravel':'9d9079','wc-leaf':'627144','wc-trunk':'78624c','wc-beige-stucco':'b6ad8a','wc-blue-paint':'667486','hs-cream-stucco':'c6bd91','hs-trim':'a9a27e','hs-sign':'746c61','hs-steel':'4e5758','hs-ornament':'c6c6b5','hs-display':'273c56','hs-floor':'8c8b80','hs-wall':'b7b4a4','hs-ceiling':'b5b4a7','hs-light':'f4e9cf','hs-counter':'898775'}
IDS={'westwood-2650':'way/464694101','highland-steel':'way/464694099','creel-highland':'way/464694100'}

def edges(B,p):
 for poly in parts(p):
  for a,b in zip(list(poly.exterior.coords),list(poly.exterior.coords)[1:]):
   dx,dz=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dz)
   yield Frame(B,(a[0]+b[0])/2,(a[1]+b[1])/2,math.atan2(-dz,dx),y=0),length

def ledges(B,p,h):
 for F,L in edges(B,p):
  F.box('wc-cap',(0,h,0),(L+.035,.18,.28))

def score(F,L,h,mat='wc-joint',step=.8):
 # Thin outward strips, not thousands of hidden box faces; no trim collision.
 for y in np.arange(.4,h,.4):
  F.b.face(mat,[F.p(-L/2,y-.006,-.018),F.p(L/2,y-.006,-.018),F.p(L/2,y+.006,-.018),F.p(-L/2,y+.006,-.018)])
 for x in np.arange(-L/2+step,L/2,step):
  F.b.face(mat,[F.p(x-.005,.03,-.02),F.p(x+.005,.03,-.02),F.p(x+.005,h,-.02),F.p(x-.005,h,-.02)])

def glazing(F,x,y,w,h):
 F.box('wc-frame',(x,y,-.07),(w+.12,h+.12,.10));F.box('wc-glass',(x,y,-.135),(w,h,.035))
 F.box('wc-frame',(x,y,-.17),(.045,h,.035))

def hvac(B,p,h):
 c=p.centroid
 for x,z in [(c.x,c.y),(c.x+5,c.y+6),(c.x-5,c.y-5)]:
  if not p.buffer(-2).contains(Point(x,z)):continue
  B.box('wc-equipment',(x,h+.6,z),(2.0,1.2,1.5))
  for zz in np.arange(z-.6,z+.65,.16):B.box('wc-cap',(x,h+1.22,float(zz)),(1.7,.025,.04))

def bush(F,x,z):
 F.box('wc-gravel',(x,.025,z),(1.5,.05,1.5))
 for j in range(4):
  a=j*2.4;F.b.sphere('wc-leaf',F.p(x+.25*math.cos(a),.47,z+.25*math.sin(a)),.43,8,5)

def metadata(key,p,front,routes,**extra):
 c=p.centroid
 d=dict(key=key,name={'westwood-2650':'2650 Westwood','highland-steel':'Highland Steel customer display','creel-highland':'Creel Highland exterior'}[key],center=[c.x,0,c.y],bounds=list(p.bounds),structural=True,hotelSources=[],exteriorOnly=True,portals=[],zones=[],lights=[],routes=routes,reviewViews=[['front',front.p(0,5.5 if key=='creel-highland' else 3.6,-42 if key=='creel-highland' else -19),front.p(0,5 if key=='creel-highland' else 3,1)],['roof',[c.x+45,65,c.y+40],[c.x,3,c.y]]])
 d.update(extra);return d

def westwood(B):
 key='westwood-2650';p=orient(footprint(IDS[key]),1);B.property=key+'-exterior';B.source='commercial/'+key;B.detail=0
 # The stepped footprint has a visible transverse height break.
 a=np.array([140.187,-2879.768]);b=np.array([167.515,-2866.622]);d=b-a;n=np.array([d[1],-d[0]])
 north=Polygon([a-d*10,b+d*10,b+d*10+n*20,a-d*10+n*20])
 north=p.intersection(north);south=p.difference(north)
 for q,h in [(north,8.8),(south,5.7)]:
  B.shell(q,.02,h,'wc-white-stucco',roof=False);B.planar('wc-roof',q,h);ledges(B,q,h);hvac(B,q,h)
 front=None;routes=[]
 for F,L in edges(B,p):
  # West-facing long elevations observed from Westwood.
  if -F.si<-.65 and L>20:
   h=8.8 if F.z<-2878 else 5.7;score(F,L,h-.12)
   F.box('wc-brick',(0,h/2,-.055),(10.2,h-.12,.07))
   for yy in np.arange(.2,h-.15,.23):F.box('wc-mortar',(0,float(yy),-.10),(10.2,.012,.012))
   for x in [-4,-2.4,-.8,.8,2.4,4]:
    glazing(F,x,1.8,1.05,2.8)
    for y in [.6,1.2,1.8,2.4,3.0]:F.box('wc-frame',(x,y,-.20),(1.1,.035,.04))
   F.box('wc-cap',(0,3.6,-.13),(10.4,.16,.24))
   F.box('wc-concrete',(0,.03,-1.0),(11,.18,2.05),True)
   for x in [-L/2+2,-L/2+4,L/2-3]:bush(F,x,-.8)
   routes.append(dict(name='Frontage approach '+str(len(routes)+1),points=[F.p(-4,.12,-1.1),F.p(4,.12,-1.1)]))
   if front is None:front=F
  elif L>5:score(F,L,5.6,step=1.6)
 return metadata(key,p,front,routes)

def scroll(F,x,y,z,r=.19):
 pts=[(x+r*(1-.65*t)*math.cos(t*math.tau*1.2),y+r*(1-.65*t)*math.sin(t*math.tau*1.2),z) for t in np.linspace(0,1,18)]
 F.path('hs-ornament',pts,.014,6)

def highland(B):
 key='highland-steel';p=orient(footprint(IDS[key]),1);B.property=key+'-exterior';B.source='commercial/'+key;B.detail=0
 F,L=max(edges(B,p),key=lambda e:e[0].x)
 door=dict(p=F.p(.8,.12,0),yaw=F.yaw,width=1.5,height=2.55,name='Customer display entrance',venue=key)
 B.shell(p,.02,4.7,'hs-cream-stucco',roof=False,openings=[door]);B.planar('wc-roof',p,4.7);ledges(B,p,4.7);hvac(B,p,4.7)
 for G,ll in edges(B,p):score(G,ll,4.55,step=.8)
 # Current cream storefront, not the orange finish visible in older detail photos.
 F.box('hs-trim',(0,3.4,-.09),(L,.18,.25))
 F.text('HIGHLAND STEEL',(0,3.85,-.21),.68,'hs-sign')
 F.text('2621',(.8,2.95,-.2),.22,'hs-steel')
 for x in [3.0,5.8]:
  glazing(F,x,1.65,2.0,2.25)
  for xx in np.arange(x-.94,x+.95,.24):
   F.box('hs-steel',(float(xx),1.65,-.25),(.035,2.25,.045))
  for yy in [.65,1.65,2.65]:
   F.box('hs-steel',(x,yy,-.27),(2.0,.035,.045))
  for xx in [x-.6,x,x+.6]:scroll(F,xx,1.6,-.30)
 # Closed warehouse loading door; this is not a second public entrance.
 F.box('hs-steel',(-4.3,1.7,-.075),(4.4,3.4,.08),True)
 for xx in np.arange(-6.4,-2.1,.24):F.box('wc-cap',(float(xx),1.7,-.13),(.025,3.3,.045))
 for x in [.0,1.6]:F.box('wc-frame',(x,1.4,-.09),(.09,2.6,.18),True)
 F.box('wc-cap',(.8,2.8,-.45),(2.0,.13,1.0))
 F.box('wc-concrete',(0,.03,-1),(L,.18,2.1),True)
 # A fitted customer display room, not a surveyed whole-store plan or warehouse tour.
 B.property=key+'-interior';B.source='interior/'+key;B.detail=1
 room=F.poly([(-.05,.04),(7.25,.04),(7.25,7.0),(-.05,7.0)])
 B.shell(room,.12,3.35,'hs-wall',roof=False,openings=[dict(p=F.p(.8,.12,.04),yaw=F.yaw,width=1.5,height=2.55)])
 B.planar('hs-floor',room,.12,True);B.planar('hs-ceiling',room,3.35)
 F.box('hs-counter',(5.3,.65,4.7),(2.8,1.06,.75),True)
 F.box('hs-steel',(5.3,1.21,4.7),(2.95,.08,.85))
 F.box('hs-display',(3.6,1.65,6.93),(6.5,2.8,.07))
 for x in np.arange(.65,6.8,.72):
  F.box('hs-steel',(float(x),1.65,6.86),(.04,2.55,.04))
  for y in [.55,1.15,1.75,2.35]:
   scroll(F,float(x),y,6.8,.23)
   F.path('hs-ornament',[(float(x)-.25,y,6.8),(float(x),y+.27,6.8),(float(x)+.25,y,6.8),(float(x),y-.27,6.8),(float(x)-.25,y,6.8)],.015,6)
 F.text('SERVICE COUNTER',(5.2,2.8,6.78),.22,'hs-ornament')
 for z in [1.7,4.5]:
  F.box('hs-steel',(3.6,3.28,z),(2.2,.07,.23));F.box('hs-light',(3.6,3.22,z),(2.05,.03,.18))
 F.tube('hs-steel',(3.6,3.30,.2),(3.6,3.30,6.8),.018,6)
 routes=[dict(name='Public display entry',points=[F.p(.8,.12,z) for z in [-1.7,0,2,5.6]]),dict(name='Counter approach',points=[F.p(.8,.12,3.4),F.p(5.3,.12,3.4)])]
 return metadata(key,p,F,routes,exteriorOnly=False,portals=[door],zones=[dict(origin=F.p(3.6,.12,.04),yaw=F.yaw,width=7.3,depth=7,height=3.3)],lights=[dict(p=F.p(3.6,3.0,z),color=0xfff0d0,power=3,range=7) for z in [1.7,4.5]])

def creel(B):
 key='creel-highland';p=orient(footprint(IDS[key]),1);B.property=key+'-exterior';B.source='commercial/'+key;B.detail=0
 B.shell(p,.02,11.2,'wc-beige-stucco',roof=False);B.planar('wc-roof',p,11.2);ledges(B,p,11.2);hvac(B,p,11.2)
 front=None;routes=[]
 for F,L in edges(B,p):
  if -F.si>.65 and L>30:
   front=F
   F.box('wc-blue-paint',(0,10.8,-.06),(L,.6,.10))
   for x in np.linspace(-L/2+3,L/2-3,5):
    F.box('wc-blue-paint',(float(x),5.3,-.055),(1.5,10.5,.08))
   F.text('CREEL',(-L/2+6,9.4,-.20),.9,'wc-blue-paint')
   F.box('wc-concrete',(0,.03,-.8),(L,.18,1.65),True)
   routes.append(dict(name='Warehouse public frontage',points=[F.p(-L/2+3,.12,-.8),F.p(L/2-3,.12,-.8)]))
  elif L>18:
   F.box('wc-blue-paint',(0,10.8,-.05),(L,.6,.08))
   for x in [-L/3,0,L/3]:F.box('wc-blue-paint',(x,5.3,-.055),(1.1,10.5,.08))
 if front is None:front=max(edges(B,p),key=lambda e:e[0].x)[0]
 return metadata(key,p,front,routes)

if __name__=='__main__':
 B=Meshes()
 for fn in [westwood,highland,creel]:
  meta=fn(B);(OUT/(meta['key']+'-metadata.json')).write_text(json.dumps(meta,indent=2)+'\n')
 B.save_all();print('Westwood commercial source:',sum(len(g['faces']) for g in B.groups.values()),'faces')
