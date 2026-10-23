"""Wyndham Desert Blue: mapped crescent and raised arrival canopies, Earth reference."""
from common import *
from forum_shops import facade_frame
KEY='wyndhamDesertBlue';IDS=['way/568622622','way/1459325605','way/1459325606','way/1459325607','way/1459325608']
def exterior(B):
 B.property=KEY+'-exterior';B.source='wyndham-desert-blue';B.detail=0
 p=footprint(IDS[1]);ps=list(p.exterior.coords)
 B.shell(p,0,53,'wd-white',roof=False)
 for a,b in zip(ps,ps[1:]):
  L=math.dist(a,b)
  if L<.1:continue
  F,_,nx,nz=facade_frame(B,a,b,p,0)
  def panel(mat,x,y,w,h,d=.08):F.box(mat,(x,y,d*-1),(w,h,.045))
  panel('wd-pink',L/2,7.5,L,15,.1)
  long=L>8
  if not long:continue
  # Each segment follows the source crescent; keep bay sizes in metres.
  n=max(1,round(L/2.6));w=L/n
  for k in range(n):
   x=(k+.5)*w
   for y in np.arange(16.2,43,2.85):
    panel('wd-glass',x,y,w*.69,1.85,.16)
    panel('wd-frame',x,y,w*.72,.065,.22)
    panel('wd-frame',x,y,.04,1.85,.23)
    panel('wd-sill',x,y-1,w*.74,.11,.27)
   for y in [2.5,5.4,8.3,11.2,14.1]:panel('wd-glass',x,y,w*.84,1.8,.16)
   panel('wd-glass',x,47.4,w-.08,9.1,.16)
   panel('wd-frame',x,47.4,.04,9.1,.23)
  for y in [15.2,43,45.9,48.8,51.7]:panel('wd-sill',L/2,y,L,.2,.27)
  # Blue upper glazing continues around both broad faces; end caps stay stone.
  if L>17:
   for y in [44.4,47.3,50.2]:panel('wd-frame',L/2,y,L,.04,.24)
  panel('wd-cornice',L/2,52.8,L,.4,.35)
 B.planar('wd-roof',p,53.025,True)
 for a,b in zip(ps,ps[1:]):
  F,L,_,_=facade_frame(B,a,b,p,0);F.box('wd-white',(L/2,53.45,0),(L,.85,.35),True)
 # Mapped canopies are explicitly elevated (4m clear); retain open drive beneath.
 for ident in IDS[2:]:
  pp=footprint(ident)
  if ident==IDS[-1]:
   B.shell(pp,0,5,'wd-pink',roof=False)
  else:
   B.shell(pp,4,5,'wd-pink',roof=False)
   B.planar('wd-soffit',pp,4)
   for x,z in list(pp.exterior.coords)[::2]:
    if p.distance(Point(x,z))<.5:continue
    B.box('wd-pink',(x,2,z),(.45,4,.45),True)
  B.planar('wd-roof',pp,5,True)
  for poly in parts(pp):
   qs=list(poly.exterior.coords)
   for a,b in zip(qs,qs[1:]):
    F,L,_,_=facade_frame(B,a,b,poly,0);F.box('wd-white',(L/2,5.05,0),(L,.15,.25))
 # Rooftop plant sits on a raised curved service screen with actual depth.
 screen=p.buffer(-5,join_style=2)
 B.shell(screen,53.05,55.4,'wd-service',roof=False)
 B.planar('wd-roof',screen,55.4,True)
 for pp in parts(screen):
  for x,z in list(pp.exterior.coords)[::2]:B.box('wd-plant',(x,56,z),(2.6,1.2,2.6))
 # Tower branding on both broad faces, aligned with the nearest surveyed segment.
 for target in [(-966,-690),(-966,-719)]:
  a,b=min(zip(ps,ps[1:]),key=lambda ab:LineString(ab).distance(Point(*target)))
  F,L,_,_=facade_frame(B,a,b,p,0);F.text('WYNDHAM',(L/2,52.7,-.6),1.15,'wd-letter')
 # Entry canopy fascia, at the source's south-west outward edge.
 pp=footprint(IDS[2]);qs=list(pp.exterior.coords);a,b=min(zip(qs,qs[1:]),key=lambda ab:LineString(ab).distance(Point(-974,-674)))
 F,L,_,_=facade_frame(B,a,b,pp,0);F.text('WYNDHAM',(L/2,4.45,-.25),.5,'wd-letter')
 return dict(key=KEY,name='Wyndham Desert Blue',center=[-968,0,-700],bounds=list(footprint(IDS[0]).bounds),structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],views={})
