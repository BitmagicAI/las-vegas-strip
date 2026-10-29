"""Original fitted exterior from site-specific aerial and June 2023 facade evidence."""
from common import *
KEY='chick-fil-a-paradise';IDS=['way/381396713','way/1423939476','way/1423939478']
def build(B):
 B.property=KEY+'-exterior';B.source='retail/'+KEY;B.detail=0
 p=footprint(IDS[0]);B.shell(p,.02,5.35,'cf-plaster',roof=False);B.planar('cf-membrane',p,5.35)
 # Stepped parapets and dark coping follow the mapped shell. Heights are estimates.
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  dx,dz=b[0]-a[0],b[1]-a[1];L=math.hypot(dx,dz)
  if L<.15:continue
  F=Frame(B,(a[0]+b[0])/2,(a[1]+b[1])/2,math.atan2(-dz,dx),y=0)
  top=6.15 if F.z<277 or F.z>294 else 5.65
  F.box('cf-plaster',(0,(top+5.35)/2,0),(L,top-5.35,.26))
  F.box('cf-metal',(0,top+.035,0),(L+.08,.1,.39))
  F.box('cf-stone',(0,.7,0),(L,1.4,.19))
  F.box('cf-sill',(0,1.42,0),(L,.10,.27))
  for side in [-1,1]:
   # Stone coursing in the low base; no copied photographic textures.
   for y in [.26,.55,.84,1.13]:
    F.box('cf-joint',(0,y,side*.102),(L,.015,.015))
    for u in np.arange(-L/2+.3+(y% .3),L/2,.75):F.box('cf-joint',(float(u),y-.14,side*.103),(.012,.26,.015))
  east=F.x>1706;end=F.z<267.4 or F.z>300.4
  if (east or end) and L>3:
   count=max(1,int(L/3.3))
   for u in np.linspace(-L/2+1.5,L/2-1.5,count):
    for side in [-1,1]:
     F.box('cf-glass',(float(u),2.85,side*.15),(2.6,2.7,.055))
     for x in [-1.32,0,1.32]:F.box('cf-metal',(float(u+x),2.85,side*.19),(.065,2.82,.06))
     for y in [1.46,3.25,4.25]:F.box('cf-metal',(float(u),y,side*.19),(2.7,.065,.06))
     F.box('cf-metal',(float(u),4.45,side*.5),(2.95,.15,1.0))
     for x in [-1.1,1.1]:F.tube('cf-metal',(float(u+x),3.9,side*.2),(float(u+x),4.38,side*.85),.025,6)
 # Street-facing raised brand panel, original typesetting rather than logo artwork.
 E=Frame(B,1708.6,280.2,math.pi/2,y=0)
 E.box('cf-red',(0,4.95,.22),(6.4,1.0,.16));E.text('Chick-fil-A',(0,4.65,.33),.66,'cf-letter',back=True)
 # Main entrance glazing/pulls. Closed exterior doors; no invented accessible interior.
 D=Frame(B,1707.4,293.2,math.pi/2,y=0)
 D.box('cf-glass',(0,1.55,.2),(2.25,3.05,.07))
 for u in [-1.16,0,1.16]:D.box('cf-metal',(u,1.55,.26),(.07,3.14,.065))
 for u in [-.2,.2]:D.box('cf-handle',(u,1.35,.34),(.035,.6,.04))
 D.box('cf-metal',(0,3.25,.8),(3.2,.18,1.6))
 # Pickup glazing at the mapped projecting west service bay; size fitted.
 W=Frame(B,1693.68,287.4,-math.pi/2,y=0)
 W.box('cf-glass',(0,2,.08),(2.4,1.5,.07))
 for u in [-1.23,0,1.23]:W.box('cf-metal',(u,2,.14),(.065,1.6,.06))
 for y in [1.2,2.8]:W.box('cf-metal',(0,y,.14),(2.52,.065,.06))
 W.box('cf-sill',(0,1.16,.3),(2.65,.12,.55))
 W.box('cf-red',(0,3.15,.13),(2.5,.4,.06));W.text('PICK UP',(0,3.02,.18),.23,'cf-letter',back=True)
 # Canopies are open below the soffit, with posts outside the drive lanes.
 for idx in IDS[1:]:
  c=footprint(idx);xmin,zmin,xmax,zmax=c.bounds
  B.planar('cf-soffit',c,4.45,True);B.planar('cf-membrane',c,4.75,True)
  B.shell(c,4.45,4.75,'cf-metal',roof=False,solid=True)
  Q=Frame(B,0,0,0,y=0)
  if idx==IDS[1]:posts=[(1685.6,z) for z in [278,287.7,297.7]]
  else:posts=[(x,z) for x in [1646.8,1661.7] for z in [264.3,270.8]]
  for x,z in posts:
   Q.box('cf-stone',(x,.38,z),(.6,.76,.6),True);Q.box('cf-metal',(x,2.6,z),(.22,3.7,.22),True)
  for x in np.arange(xmin+2,xmax-1,4):
   for z in np.arange(zmin+2,zmax-1,5):Q.box('cf-lamp',(float(x),4.42,float(z)),(.65,.035,.22))
 # Original ordering kiosks under the separate canopy, keeping both lanes open.
 Q=Frame(B,0,0,0,y=0)
 for x in [1650,1658]:
  Q.box('cf-metal',(x,1.25,267.4),(.2,2.5,.2),True)
  Q.box('cf-menu',(x,1.65,267.4),(1.3,1.55,.18),True)
  for dz in [-.11,.11]:
   Q.box('cf-red',(x,2.2,267.4+dz),(1.14,.25,.025))
   for y in [1.2,1.45,1.7,1.95]:Q.box('cf-letter',(x,y,267.4+dz),(.85,.035,.025))
 # Rooftop mechanical enclosures and fan grilles, below the stepped parapet skyline.
 for z in [274,283,293]:
  Q.box('cf-equipment',(1701,5.7,z),(3.2,.7,2.3))
  for x in [1700.3,1701.7]:
   Q.lathe('cf-metal',x,z,[(6.06,.43),(6.09,.43)],16)
   for dz in np.arange(-.35,.36,.12):Q.box('cf-equipment',(x,6.105,z+float(dz)),(.8,.025,.025))
 routes=[dict(name='Street frontage',points=[[1713,.24,302],[1713,.24,293.2],[1709.1,.24,293.2]]),dict(name='Covered drive lane',points=[[1689,.24,304],[1689,.24,296],[1689,.24,285],[1689,.24,273]]),dict(name='Order canopy clearance',points=[[1643,.24,269],[1653,.24,269],[1666,.24,269]])]
 return dict(key=KEY,name='Chick-fil-A Flamingo and Paradise',center=[1698,0,284],bounds=list(unary_union([footprint(i) for i in IDS]).bounds),structural=True,hotelSources=[],exteriorOnly=True,portals=[],zones=[],lights=[],routes=routes)
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
