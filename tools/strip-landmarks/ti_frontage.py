"""TI's mapped cove village, retail corner and ship exteriors.
Earth 2022-11-09 establishes forms; owner Nov2025 map establishes tenants.
Elevations are photographic estimates. No interior/road regeneration.
"""
from common import *
IDS=['way/543638190','way/180771078','way/180771079','way/543638206','way/543638185','way/543638212']

def edges(B,p):
 for q in parts(p):
  pts=list(q.exterior.coords)
  for a,b in zip(pts,pts[1:]):
   L=math.dist(a,b)
   if L<.5:continue
   mx,mz=(a[0]+b[0])/2,(a[1]+b[1])/2;nx,nz=-(b[1]-a[1])/L,(b[0]-a[0])/L
   if q.contains(Point(mx+nx*.1,mz+nz*.1)):nx,nz=-nx,-nz
   yield Frame(B,mx,mz,math.atan2(-nx,-nz),y=0),L,nx,nz

def bays(B,p,h,mat,style='village'):
 B.shell(p,.05,h,mat)
 for F,L,nx,nz in edges(B,p):
  F.box('ivory',(0,h-.18,-.18),(L,.36,.4))
  F.box('stone',(0,.45,-.12),(L,.5,.25))
  if L<2.5:continue
  n=max(1,round(L/(4.4 if style=='retail' else 3.7)));step=L/n
  for j in range(n):
   x=-L/2+(j+.5)*step;w=min(2.6,step*.68)
   for y in ([2,6.4,10.8] if style=='retail' else [2.3]):
    F.box('darkglass',(x,y,-.10),(w,3.2,.12))
    for xx in [x-w/2-.1,x+w/2+.1]:F.box('ivory',(xx,y,-.22),(.2,3.5,.3))
    F.box('ivory',(x,y+1.7,-.25),(w+.4,.2,.4))
    F.box('bronze',(x,y,-.19),(.06,3.2,.08));F.box('bronze',(x,y-.4,-.19),(w,.055,.08))
   if style=='village':
    F.arch(x,-.24,w+.2,4.5,mat='stone',thick=.14)
    F.box('shipwood',(x,4.85,-.4),(w+.6,.18,.8))
   if style=='coffee':
    B.face('sage',[F.p(x-w*.65,3.9,-.2),F.p(x+w*.65,3.9,-.2),F.p(x+w*.65,3.5,-1.2),F.p(x-w*.65,3.5,-1.2)])
   B.detail=1
   if style=='village':
    for k in range(int(h/0.65)):
     F.box('stone',(x+step*.45,k*.65+.35,-.08),(.38,.48,.2))
   B.detail=0


def ship(B,ident,bow,stern,width,mat):
 B.source='ti-ship/'+ident;B.detail=0
 cx,cz=(bow[0]+stern[0])/2,(bow[1]+stern[1])/2
 length=math.dist(bow,stern);F=Frame(B,cx,cz,math.atan2(stern[0]-bow[0],stern[1]-bow[1]),y=.25)
 stations=[(-length*.5,.09,2.7),(-length*.38,width*.5,2.5),(-length*.18,width*.85,2.2),(length*.16,width,2.5),(length*.38,width*.8,4.0),(length*.5,width*.55,4.1)]
 for (z,r,t),(zz,rr,tt) in zip(stations,stations[1:]):
  for i in range(16):
   a=math.pi+i*math.pi/16;b=a+math.pi/16
   B.face(mat,[F.p(rad*math.cos(v),top+(top-.05)*math.sin(v),zv) for zv,rad,top,v in [(z,r,t,a),(zz,rr,tt,a),(zz,rr,tt,b),(z,r,t,b)]])
  B.upface('shipwood',[F.p(-r,t,z),F.p(r,t,z),F.p(rr,tt,zz),F.p(-rr,tt,zz)])
  for s in [-1,1]:
   for f in [.38,.65,.86]:F.tube('gold',(s*r*(.65+.35*f),t*f,z),(s*rr*(.65+.35*f),tt*f,zz),.045,6)
   F.tube('shipwood',(s*r,t+.7,z),(s*rr,tt+.7,zz),.075,8)
   for f in np.linspace(.05,.95,4):
    x=s*(r+(rr-r)*f);y=t+(tt-t)*f;v=z+(zz-z)*f
    F.tube('shipwood',(x,y,v),(x,y+.7,v),.045,6)
 for z in [-length*.24,0,length*.29]:
  hh=12.5 if z else 15.5
  F.tube('shipwood',(0,2.3,z),(0,hh,z),.15,12,.06)
  for y,ww in [(hh*.53,width*2.4),(hh*.77,width*2),(hh*.93,width*1.3)]:
   F.tube('shipwood',(-ww/2,y,z),(ww/2,y,z),.085,8)
   F.path('rope',[(-ww/2,y,z),(0,y+.8,z),(ww/2,y,z)],.025,5)
   # Furled canvas rather than imaginary deployed sails in a fixed display ship.
   F.tube('ivory',(-ww*.43,y-.12,z),(ww*.43,y-.12,z),.13,8)
  for s in [-1,1]:
   for dz in [-1.5,0,1.5]:F.tube('rope',(s*width*.8,2.8,z+dz),(0,hh*.78,z),.022,5)
  F.tube('rope',(0,hh,z),(0,3.1,-length*.48),.022,5)
 F.box(mat,(0,3.7,length*.36),(width*1.3,2.4,length*.2))
 for x in [-width*.48,0,width*.48]:F.box('darkglass',(x,4.0,length*.46),(width*.3,.8,.06))
 F.tube('shipwood',(0,2.7,-length*.5),(0,4,-length*.68),.13,10,.05)
 for z in np.arange(-length*.3,length*.31,2.2):
  for s in [-1,1]:F.box('blackiron',(s*width*.91,1.8,z),(.06,.4,.55))


def build(B):
 # Northern retail corner: the old survey encoded a three-storey building as 5m.
 B.source='ti-frontage/way/543638190';p=footprint('way/543638190')
 retail=p.intersection(box(253,-1050,300,-996));village=p.difference(retail)
 bays(B,retail,15.8,'ti-retail-paint','retail');bays(B,village,7.7,'sandstone')
 # Rounded eastern sign face follows the surveyed corner instead of a box.
 for F,L,nx,nz in edges(B,retail):
  if nx>.6:
   F.box('ti-sign-paint',(0,11,-.32),(L+.04,8,.3))
   if L>7:F.text('TI',(0,11,-.51),2.1,'ivory')
  if nz<-.6 and L>9:F.text('CVS pharmacy',(0,3.9,-.42),.7,'red')
 B.source='ti-frontage/way/180771078';p=footprint('way/180771078')
 bays(B,p,9.5,'ti-coral-paint')
 for F,L,nx,nz in edges(B,p):
  if L>5 and nx>.2:
   F.box('ivory',(0,6.1,-.65),(L,.3,1.3));F.rail((-L/2,-1.15),(L/2,-1.15),7.3)
   for j in range(max(1,int(L/3))):
    x=-L/2+(j+.5)*L/max(1,int(L/3));F.box('darkglass',(x,7.7,-.1),(1.65,2.5,.12));F.box('ivory',(x,9.05,-.25),(1.95,.2,.4))
 # Small cove shop is rough pale stone with separate battlement/roof forms.
 B.source='ti-frontage/way/180771079';p=footprint('way/180771079');bays(B,p,7.2,'stone')
 for F,L,nx,nz in edges(B,p):
  for x in np.arange(-L/2+.4,L/2,.95):F.box('stone',(x,7.55,0),(.55,.7,.55))
 # Southern rounded coffee kiosk.
 B.source='ti-frontage/way/543638212';p=footprint('way/543638212');bays(B,p,5.3,'sandstone','coffee')
 for F,L,nx,nz in edges(B,p):
  F.box('ivory',(0,5.55,0),(L,.5,.7))
  if L>9 and nx>.2:F.text('STARBUCKS',(0,4.7,-.45),.55,'sage')
 # Real display hulls replace the two cadastral building prisms.
 ship(B,'way/543638185',(207.1,-943),(217,-921),2.7,'shipwood')
 ship(B,'way/543638206',(233,-970),(251.5,-978),3.0,'ivory')
 # Cove basins follow the gaps between the surveyed village and boulevard.
 # Keep every mapped building and shared bridge landing out of the water mesh.
 B.source='ti-cove-water';main=footprint('way/33959894')
 occupied=unary_union([main,*[footprint(i) for i in IDS if i not in ['way/543638185','way/543638206']]])
 basins=[Polygon([(230,-967),(243,-979),(260,-984),(271,-977),(274,-964),(268,-954),(254,-949),(239,-950)]),Polygon([(203,-945),(216,-946),(230,-938),(239,-926),(236,-913),(218,-895),(208,-900),(199,-915)])]
 for basin in basins:
  p=basin.difference(occupied.buffer(.3))
  B.planar('water',p,.18)
  rim=p.buffer(.4).difference(p)
  B.shell(rim,.12,.48,'stone',roof=False);B.planar('stone',rim,.48,True)
 # Recessed mechanical plant on the otherwise featureless podium roof.
 B.source='ti-roof-equipment';tower=footprint('way/27727145').buffer(4)
 for x in range(25,200,22):
  for z in range(-1020,-880,24):
   q=box(x-2,z-1.5,x+2,z+1.5)
   if main.buffer(-4).covers(q) and not tower.intersects(q):
    B.box('stone',(x,9.8,z),(4,1.4,3));B.box('steel',(x,10.52,z),(4.2,.12,3.2))
    for dx in [-.9,.9]:B.tube('blackiron',(x+dx,10.6,z),(x+dx,10.64,z),.65,16)
 # Gilley's long street face is a low timber-and-glass saloon, not the
 # generic Italian arcade formerly applied across every TI podium edge.
 B.source='ti-gilleys-frontage'
 for F,L,nx,nz in edges(B,main):
  if not (F.x>195 and -918<F.z<-864 and nx>.5):continue
  F.box('ivory',(0,7.4,-.10),(L,3.1,.25))
  F.box('shipwood',(0,5.5,-.25),(L,.85,.5))
  F.box('ivory',(0,6.0,-.35),(L,.18,.75))
  n=max(1,round(L/3.3));step=L/n
  for j in range(n):
   x=-L/2+(j+.5)*step;w=step-.36
   F.box('darkglass',(x,2.65,-.16),(w,4.3,.16))
   for xx in [x-step/2,x+step/2]:F.box('shipwood',(xx,2.7,-.30),(.28,5.4,.46))
   F.box('shipwood',(x,3.5,-.3),(w,.12,.2))
  # Continuous slim canopy along the glass face.
  B.face('roof',[F.p(-L/2,5.2,-.3),F.p(L/2,5.2,-.3),F.p(L/2,4.6,-2),F.p(-L/2,4.6,-2)])
  F.box('ivory',(0,4.55,-2),(L,.18,.15))
  if L>20:F.text("GILLEY'S",(0,7.25,-.27),1.5,'shipwood')
