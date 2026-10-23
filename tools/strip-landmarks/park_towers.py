"""Park Towers at Hughes Center: mapped asymmetric plans and rounded green-glass bays."""
from common import *
from forum_shops import facade_frame
KEY='parkTowers';IDS=['way/182464616','way/182464631']
def exterior(B):
 B.property=KEY+'-exterior';B.source='park-towers';B.detail=0
 allp=[]
 for ident,caps in [(IDS[0],[(1224,-18,5.8),(1228,18,5.6)]),(IDS[1],[(1253,-54,5.2),(1289,-60,5.5)])]:
  p=footprint(ident);allp.append(p);B.shell(p,0,62,'pk-white',roof=False)
  ps=list(p.exterior.coords)
  for a,b in zip(ps,ps[1:]):
   F,L,_,_=facade_frame(B,a,b,p,0)
   if L<.2:continue
   mx,mz=(a[0]+b[0])/2,(a[1]+b[1])/2
   curved=any(math.hypot(mx-x,mz-z)<r+1.3 for x,z,r in caps)
   if curved:
    F.box('pk-glass',(L/2,31.3,-.12),(L-.02,59.4,.045))
    for y in np.arange(3,62,3.05):F.box('pk-white',(L/2,y,-.24),(L,.22,.25))
    F.box('pk-frame',(0,31.3,-.22),(.065,59.4,.065))
   elif L>=3:
    count=max(1,round(L/3));w=L/count
    balcony=7<L<17
    for k in range(count):
     x=(k+.5)*w
     for y in np.arange(4.4,61,3.05):
      F.box('pk-glass',(x,y,-.12),(w*.70,2.36,.045))
      F.box('pk-frame',(x,y,-.17),(.045,2.36,.06))
      if balcony:
       F.box('pk-white',(x,y-1.28,-.72),(w*.94,.18,1.45),True)
       F.box('pk-rail',(x,y-.43,-1.37),(w*.91,.08,.08))
       for xx in np.linspace(x-w*.44,x+w*.44,5):F.box('pk-rail',(xx,y-.83,-1.37),(.045,.75,.045))
       for xx in [x-w*.44,x+w*.44]:F.box('pk-white',(xx,y-.78,-.72),(.14,.95,1.4))
      else:F.box('pk-sill',(x,y-1.24,-.23),(w*.75,.12,.18))
   # Pale cornice follows every original corner and curved bay.
   F.box('pk-white',(L/2,61.9,-.12),(L,.4,.45))
  B.planar('pk-roof',p,62.025,True)
  for x,z,r in caps:
   B.lathe('pk-patina',(x,z),[(62.1,r+.25),(62.6,r+.25),(63.25,r*.94),(64,r*.63),(64.3,.05)],32)
  cx,cz=p.centroid.coords[0];core=box(cx-5,cz-4,cx+5,cz+4)
  # Open roof-service screen rather than a solid extruded roof box.
  for a,b in zip(list(core.exterior.coords),list(core.exterior.coords)[1:]):
   F,L,*_=facade_frame(B,a,b,core,0);F.box('pk-white',(L/2,63.8,0),(L,3.6,.45))
  for x,z in [(cx-2,cz-1),(cx+2,cz+1)]:B.box('pk-service',(x,63,z),(2.2,1.8,2.6))
 bounds=unary_union(allp).bounds
 return dict(key=KEY,name='Park Towers at Hughes Center',center=[1250,0,-25],bounds=list(bounds),structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],views={})
