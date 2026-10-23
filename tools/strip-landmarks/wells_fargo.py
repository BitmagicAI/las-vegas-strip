"""3800 Howard Hughes: folded glass elevations and stepped stone crown."""
from common import *
from forum_shops import facade_frame
KEY='wellsFargoTower';IDS=['way/156624462']
def exterior(B):
 B.property=KEY+'-exterior';B.source='wells-fargo-tower';B.detail=0
 p=footprint(IDS[0]);B.shell(p,0,50,'wf-stone',roof=False)
 B.planar('wf-roof',p,50,True)
 ps=list(p.exterior.coords)
 for a,b in zip(ps,ps[1:]):
  F,L,_,_=facade_frame(B,a,b,p,0)
  if L<.5:continue
  def panel(mat,x,y,w,h,d=.14):F.box(mat,(x,y,-d),(w,h,.055))
  if L>12:
   center=L/2;glassW=min(9.3,L*.36);lo=center-glassW/2;hi=center+glassW/2
   # Projected glass is folded, rather than a painted stripe on the stone wall.
   for k in range(5):
    x0=lo+glassW*k/5;xm=x0+glassW/10;x1=x0+glassW/5
    for aa,bb,da,db in [(x0,xm,-.12,-.8),(xm,x1,-.8,-.12)]:
     B.face('wf-glass',[F.p(aa,2.4,da),F.p(bb,2.4,db),F.p(bb,49.9,db),F.p(aa,49.9,da)])
     for y in np.arange(3.4,49.9,2.85):F.path('wf-metal',[(aa,y,da-.02),(bb,y,db-.02)],.025)
    F.box('wf-stone',(xm,26,-.85),(.13,47.2,.16))
   for left,right in [(.7,lo-.65),(hi+.65,L-.7)]:
    n=max(1,round((right-left)/2.25));pitch=(right-left)/n
    for k in range(n):
     x=left+(k+.5)*pitch
     for y in np.arange(5.15,49,2.85):
      panel('wf-glass',x,y,pitch*.7,1.95)
      panel('wf-sill',x,y-1.05,pitch*.77,.12,.2)
   # Stepped stone shoulder extends above the main room grid.
   for x in [lo-.45,hi+.45]:F.box('wf-stone',(x,51.25,0),(.8,2.5,.65))
   F.box('wf-stone',(center,51.9,0),(glassW+1.7,.9,.8))
  else:
   n=max(1,round(L/2.1))
   for k in range(n):
    for y in np.arange(5.15,49,2.85):panel('wf-glass',(k+.5)*L/n,y,L/n*.65,1.95)
  # Lobby glazing and actual sill/frame depth around the base.
  for x in np.arange(.6,L-.7,1.7):
   panel('wf-glass',x+.6,1.7,1.2,2.9)
   panel('wf-metal',x+.6,1.7,.04,2.9,.2)
  panel('wf-plinth',L/2,.25,L,.5,.24)
 crown=p.buffer(-1.4,join_style=2);B.shell(crown,50,56,'wf-stone',roof=False)
 for pp in parts(crown):
  for a,b in zip(list(pp.exterior.coords),list(pp.exterior.coords)[1:]):
   F,L,_,_=facade_frame(B,a,b,pp,0)
   if L>12:
    for x in np.arange(1.5,L-1,2):F.box('wf-glass',(x,52,-.1),(1.3,2.1,.05))
    F.text('WELLS FARGO',(L/2,55,-.12),.68,'wf-gold')
   F.box('wf-cornice',(L/2,56,0),(L,.25,.5))
  # Inset metal hip roof; ridge follows the octagonal plan and has no flat cap.
  cx,cz=pp.centroid.coords[0];roof=pp.buffer(-.45,join_style=2)
  for a,b in zip(list(roof.exterior.coords),list(roof.exterior.coords)[1:]):
   B.upface('wf-roof-metal',[(a[0],56.2,a[1]),(b[0],56.2,b[1]),(cx,60,cz)],True)
   B.path('wf-roof-rib',[(a[0],56.24,a[1]),(cx,60.04,cz)],.045)
 # Narrow raised granite footing follows the existing footprint, not the roads.
 B.planar('wf-paving',p.buffer(.6).difference(p),.06,True)
 return dict(key=KEY,name='Wells Fargo Tower',center=[1480,0,-332],bounds=list(p.bounds),structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],views={})
