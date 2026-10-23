"""Rio conference exterior, official ballroom plan and Earth 2022.
Mapped perimeter with individually stepped halls. Heights include roof structure
above the published clear ceilings; exact exterior elevations remain estimates.
"""
from common import *
from forum_shops import facade_frame
KEY='rioConference';IDS=['way/133755242']
def exterior(B):
 B.property=KEY+'-exterior';B.source='rio-conference';B.detail=0
 p=footprint(IDS[0]);base=6.9
 # Registered to the north-up Earth view, with existing resort left untouched.
 halls=[('pavilion',box(-1268,-451,-1203,-354),12.4,'rc-roof'),
        ('amazon',box(-1268,-529,-1171,-469),10.8,'lvw-roof'),
        ('brasilia',box(-1194,-466,-1144,-411),10.2,'rc-roof'),
        ('miranda',box(-1194,-409,-1169,-362),8.6,'rc-roof'),
        ('rotunda',Polygon([(-1248,-355),(-1214,-355),(-1214,-338),(-1222,-330),(-1240,-330),(-1248,-338)]),8.4,'rc-roof'),
        ('south-service',box(-1302,-349,-1255,-305),15.2,'lvw-roof'),
        ('pavilion-service',box(-1255,-464,-1224,-450),13.2,'rc-roof')]
 raised=unary_union([q.intersection(p) for _,q,_,_ in halls])
 B.shell(p,.24,base,'rc-stucco',roof=False);B.planar('rc-roof',p.difference(raised),base,True)
 B.planar('ri-paving',p,.24,True)
 for name,q,h,mat in halls:
  q=q.intersection(p);B.source='rio-conference/'+name
  B.shell(q,base,h,'rc-stucco',roof=False);B.planar(mat,q,h,True)
  B.planar('ri-cream',q.buffer(.16).difference(q.buffer(-.22)),h+.38)
  for pp in parts(q):
   cc=list(pp.exterior.coords)
   for a,b in zip(cc,cc[1:]):
    F,L,_,_=facade_frame(B,a,b,pp,0)
    F.box('ri-cream',(L/2,h+.18,0),(L,.36,.28))
    F.box('ri-cream',(L/2,h-.6,-.07),(L,.16,.16))
  # Roof seam runs and limited plant where aerial evidence shows service equipment.
  x0,z0,x1,z1=q.bounds
  for x in np.arange(x0+8,x1-2,12):B.planar('ri-cream',box(x,z0+1,x+.05,z1-1).intersection(q),h+.015)
  if 'service' in name:
   for x in np.arange(x0+4,x1-3,8):
    for z in np.arange(z0+4,z1-3,9):
     if q.contains(box(x-1.3,z-1.2,x+1.3,z+1.2)):
      B.box('lvw-service',(x,h+.55,z),(2.6,1.1,2.4));B.box('ri-vent',(x,h+1.15,z),(2.2,.1,2))
 B.source='rio-conference/perimeter'
 for pp in parts(p):
  cc=list(pp.exterior.coords)
  for a,b in zip(cc,cc[1:]):
   F,L,nx,nz=facade_frame(B,a,b,pp,0)
   if L<1:continue
   mid=LineString([a,b]).interpolate(.5,normalized=True)
   for y in [.65,base-.55,base+.2]:F.box('ri-cream',(L/2,y,-.14),(L,.25,.3))
   for x in np.arange(1,L-1,7.5):F.box('ri-cream',(x,base/2,-.065),(.08,base-.5,.12))
   east=nx>.7;west=nx<-.7
   # East public patio has spaced glazed doors; service sides use loading shutters.
   if east and -490<mid.y<-341:
    for x in np.arange(4,L-2,11):
     F.box('ri-entryglass',(x,2.25,-.09),(3.2,4,.12))
     for dx in [-1.62,0,1.62]:F.box('ri-bronze',(x+dx,2.25,-.2),(.075,4.05,.06))
     F.box('ri-bronze',(x,4.3,-.2),(3.3,.08,.06))
     F.box('ri-awning',(x,4.6,-1.35),(4.2,.18,2.7))
   elif west and L>16:
    for x in np.arange(6,L-3,18):
     F.box('lvw-loading',(x,2.4,-.12),(3.4,4.25,.18))
     for y in np.arange(.5,4.4,.3):F.box('ri-vent',(x,y,-.23),(3.3,.035,.03))
     for dx in [-1.85,1.85]:F.box('ri-shadow',(x+dx,1,-.3),(.2,1.7,.18))
   elif L>10:
    F.box('ri-entryglass',(L*.5,1.5,-.1),(1.2,2.5,.15))
 # East pavilion and Miranda patios. Registered footprint rather than resort box.
 patio=Polygon([(-1166,-479),(-1129,-479),(-1129,-392),(-1155,-344),(-1204,-324),(-1234,-343),(-1225,-356),(-1166,-356)]).difference(p.buffer(.05))
 B.planar('ri-paving',patio,.25,True)
 for z in np.arange(-472,-343,4):B.planar('ri-cream',box(-1240,z,-1129,z+.06).intersection(patio),.265)
 # Low perimeter planter walls and bench-like masonry edges visible along parking.
 for a,b in [((-1129,-473),(-1129,-423)),((-1152,-353),(-1200,-334))]:
  line=LineString([a,b]);B.shell(line.buffer(.22,cap_style=2),.25,.75,'ri-plinth',roof=False);B.planar('ri-cream',line.buffer(.28,cap_style=2),.75,True)
 return dict(key=KEY,name='Rio Pavilion Conference Center',center=[-1225,0,-420],bounds=list(p.union(patio).bounds),structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],views={})
