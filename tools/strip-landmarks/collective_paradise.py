"""Original shared retail shell and photographed Tacos patio; unmeasured details fitted."""
from common import *
KEY='collective-paradise';IDS=['way/565876924']
def build(B):
 p=footprint(IDS[0]);B.property=KEY+'-exterior';B.source='retail/'+KEY;B.detail=0
 # Mapped southwest projection is an open dining canopy, not an enclosed box.
 patio=box(1635.4,-354.4,1647.6,-346.7);main=p.difference(patio)
 B.shell(main,.02,5.1,'cp-stone',roof=False);B.planar('cp-membrane',main,5.1)
 for a,b in zip(list(main.exterior.coords),list(main.exterior.coords)[1:]):
  dx,dz=b[0]-a[0],b[1]-a[1];L=math.hypot(dx,dz)
  if L<1:continue
  G=Frame(B,(a[0]+b[0])/2,(a[1]+b[1])/2,math.atan2(-dz,dx),y=0)
  for y,h,d in [(.22,.44,.18),(4.65,.7,.25),(5.13,.12,.36)]:G.box('cp-fascia' if y==4.65 else 'cp-stone',(0,y,0),(L,h,d))
  # Street and courtyard-facing storefront rhythms; unseen rear remains service wall.
  front=(a[1]>-355 and b[1]>-355) or (a[0]<1636.2 and b[0]<1636.2)
  if front and L>4:
   for u in np.linspace(-L/2+1.7,L/2-1.7,max(1,int(L/3.4))):
    G.box('cp-glass',(float(u),2.25,0),(2.7,3.35,.18))
    for side in [-1,1]:
     for t in [-1.4,0,1.4]:G.box('cp-metal',(float(u+t),2.25,side*.13),(.065,3.5,.05))
     for y in [.5,3.3,4.0]:G.box('cp-metal',(float(u),y,side*.13),(2.85,.065,.05))
  elif L>12:
   for u in np.arange(-L/2+5,L/2-2,12):
    for side in [-1,1]:
     G.box('cp-service',(float(u),1.3,side*.12),(1.1,2.55,.05));G.box('cp-metal',(float(u+.35),1.2,side*.17),(.06,.26,.03))
 # Aerial central multi-pitched roof; preserve surrounding flat service roofs.
 outer=[(1675.8,-362),(1684,-371),(1697,-371),(1708.8,-361),(1708.8,-350),(1697,-338.2),(1683,-338.2),(1675.8,-347)]
 cx,cz=1692,-355
 inner=[(cx+(x-cx)*.42,cz+(z-cz)*.42) for x,z in outer]
 for i in range(len(outer)):
  j=(i+1)%len(outer);a,b=outer[i],outer[j];c,d=inner[j],inner[i]
  B.face('cp-slate',[(a[0],5.2,a[1]),(b[0],5.2,b[1]),(c[0],8.1,c[1]),(d[0],8.1,d[1])])
  B.tube('cp-metal',(a[0],5.23,a[1]),(d[0],8.13,d[1]),.045)
 B.planar('cp-membrane',Polygon(inner),8.1)
 for x,z,w,d in [(1642,-364,2,1.6),(1653,-365,2.5,2),(1665,-365,3,2),(1716,-361,2.2,2),(1685,-321,3,2),(1686,-301,2,1.5),(1692,-356,2,2)]:
  Q=Frame(B,x,z,0,y=0);y=8.1 if x==1692 else 5.1
  Q.box('cp-equipment',(0,y+.5,0),(w,1,d));Q.box('cp-metal',(0,y+1.02,0),(w*.8,.04,d*.8))
  for v in np.arange(-d*.35,d*.36,.18):Q.box('cp-equipment',(0,y+1.06,float(v)),(w*.8,.03,.03))
 # Broker photograph: white framed Cleaver sign tower, ribbed pale infill,
 # blue lettering, wood accent, screened bays and a modest upper pavilion.
 # Location/height fitted to the aerial courtyard chamfer; no interior claimed.
 C=Frame(B,1671.15,-341.82,-1.12,y=0)
 for u in [-2.7,2.7]:C.box('cp-white',(u,3.4,-2.0),(.45,6.8,5.5),True)
 C.box('cp-white',(0,6.7,.35),(5.8,.35,.8))
 C.box('cp-infill',(0,4.9,.53),(5.0,3.1,.15))
 for u in np.arange(-2.4,2.41,.15):C.box('cp-rib',(float(u),4.9,.64),(.035,3.1,.04))
 C.text('CLEAVER',(0,5.25,.74),.76,'cp-blue',back=True)
 C.text('Butchered Meats',(0,4.5,.74),.32,'cp-blue',back=True)
 C.text('Seafood & Cocktails',(0,4.05,.74),.28,'cp-blue',back=True)
 C.box('cp-glass',(0,1.65,-.12),(3.9,3.1,.06))
 for u in [-1.9,0,1.9]:C.box('cp-metal',(u,1.65,-.07),(.07,3.1,.05))
 C.box('cp-wood',(-3.8,2.3,.31),(1.5,4.6,.12))
 for u in [-5.3,-6.6,-7.9]:
  C.box('cp-white',(u,1.9,.3),(1.15,2.6,.09))
  for y in np.arange(.7,3.16,.09):C.box('cp-rib',(u,float(y),.36),(1.08,.035,.025))
 C.box('cp-white',(-.8,6.15,-3),(5.0,2.1,3.2))
 C.box('cp-glass',(-.8,6.12,-1.37),(3.6,1.6,.045))
 C.box('cp-metal',(-.8,6.12,-1.33),(.08,1.6,.03))
 for u in [-5.7,4.8]:
  C.box('cp-planter',(u,.57,3.4),(2.4,1.05,.8),True)
  C.box('cp-leaf',(u,1.2,3.4),(2.2,.5,.65))
 # Tacos patio matches its southwest mapped canopy: dark fascia, braced steel posts,
 # timber soffit, string lights, planter hedges and black rails.
 T=Frame(B,1641.5,-350.3,0,y=0)
 T.box('cp-paving',(0,.15,0),(12,.3,7.2),True)
 T.box('cp-wood',(0,4.08,0),(12.4,.18,7.4),True)
 for v in [-3.7,3.7]:T.box('cp-fascia',(0,4.48,v),(12.5,.8,.16))
 for u in [-6.2,6.2]:T.box('cp-fascia',(u,4.48,0),(.16,.8,7.4))
 for u in [-5.6,0,5.6]:
  for v in [-3.1,3.1]:
   if u==0 and v>0:continue
   T.box('cp-metal',(u,2.1,v),(.2,3.9,.2),True)
   for sign in [-1,1]:T.tube('cp-metal',(u,3.1,v),(u+sign*.8,4.03,v),.07,n=4)
 for u in np.arange(-5.8,6,.22):T.box('cp-wood',(float(u),3.973,0),(.025,.025,7.0))
 # Simple original lettering rather than a copied logo bitmap.
 T.box('cp-metal',(0,5.4,3.8),(7,.75,.12))
 for u in [-2.8,2.8]:T.box('cp-metal',(u,4.98,3.8),(.09,.5,.09))
 T.text('TACOS & BEER',(0,5.17,3.89),.53,'cp-letter',back=True)
 T.text('TACOS & BEER',(0,5.17,3.71),.53,'cp-letter')
 for v in [-2,0,2]:
  pts=[]
  for u in np.linspace(-5.5,5.5,25):pts.append((float(u),3.8-.45*(1-(u/5.5)**2),v))
  T.path('cp-metal',pts,.012,4)
  for u,y,z in pts[::3]:
   T.tube('cp-metal',(u,y,z),(u,y-.12,z),.015,4)
   T.lathe('cp-lamp',u,z,[(y-.22,.04),(y-.19,.065),(y-.13,.035)],8)
 # Front planter sections leave a central entry gap; patio stays publicly walkable.
 for u in [-3.8,3.8]:
  T.box('cp-planter',(u,.52,3.15),(3.6,.75,.7),True)
  T.box('cp-leaf',(u,1.15,3.15),(3.5,.65,.62))
  T.box('cp-metal',(u,1.25,3.57),(3.6,.06,.06))
  for x in np.arange(u-1.75,u+1.76,.18):T.box('cp-metal',(float(x),.78,3.57),(.025,.9,.025))
 for u in [-4.3,4.3]:
  T.lathe('cp-metal',u,-.5,[(.3,.32),(.36,.32),(.4,.06),(1.04,.06)],12)
  T.lathe('cp-wood',u,-.5,[(1.04,.63),(1.10,.63)],24)
  for v in [-1.7,.7]:
   T.box('cp-metal',(u,.55,v),(.48,.5,.48),True);T.box('cp-wood',(u,.84,v),(.55,.08,.55))
   T.box('cp-wood',(u,1.13,v+(.24 if v>0 else -.24)),(.55,.55,.05))
 # Gentle center approach from existing forecourt, no changes to roads.
 B.upface('cp-paving',[T.p(-1.1,.01,6),T.p(1.1,.01,6),T.p(1.1,.3,3.5),T.p(-1.1,.3,3.5)],True)
 routes=[dict(name='Tacos patio',points=[[1628,.28,-343],[1638,.28,-343],[1638,.28,-344.3],T.p(0,.24,6),T.p(0,.3,3.5),T.p(0,.3,1),T.p(0,.3,-1.6)]),dict(name='Retail courtyard',points=[[1667,.28,-333],[1670,.28,-324],[1670,.28,-310],[1670,.28,-294]])]
 return dict(key=KEY,name='The Collective Paradise retail',center=[1678,0,-339],bounds=list(p.bounds),structural=True,hotelSources=[],exteriorOnly=True,portals=[],zones=[],lights=[],routes=routes)
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
