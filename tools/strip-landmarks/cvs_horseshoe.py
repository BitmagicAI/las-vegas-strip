"""CVS Strip frontage, satellite and September2022 STEP BY STEP3D photo.
Western part of mapped parking podium543422869. Heights/retail depth estimated.
"""
from common import *
from forum_shops import facade_frame
from local_pavement import local_pavement
KEY='cvsHorseshoe'
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/cvs-frontage';B.detail=0
 p=footprint('way/543422869').intersection(box(0,260,68,320))
 B.shell(p,.15,8.2,'cv-white-paint',roof=False);B.planar('cv-roof-paint',p,8.21,True)
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  F,L,nx,nz=facade_frame(B,a,b,p,.025)
  if nx>.8:continue
  F.box('cv-dark-paint',(L/2,1.65,-.07),(L,3,.1))
  for u in np.arange(.4,L-.4,1.6):
   F.box('cv-glass',(u,1.7,-.14),(1.48,2.75,.04));F.box('cv-frame-paint',(u+.77,1.7,-.19),(.05,2.95,.09))
  F.box('cv-white-paint',(L/2,3.4,-.2),(L,.65,.5))
  if nx<-.8:
   # Offset horizontal metal screen panels; real thickness and open joints.
   for k in range(6):F.box('cv-screen-paint',(L/2,4.13+k*.67,-.55),(L+.4,.62,.18))
   F.text('CVS',(L/2,4.05,-.67),5.0,'cv-white-letter')
   F.text('CVS pharmacy',(L/2,3.42,-.49),.49,'cv-red-letter')
   for u in [L*.36,L*.64]:
    F.box('cv-door-frame-paint',(u,1.6,-.23),(2.2,2.8,.09));F.box('cv-glass',(u,1.6,-.3),(2.05,2.65,.03))
    F.box('cv-frame-paint',(u,1.6,-.34),(.05,2.65,.04))
  else:
   F.box('cv-screen-paint',(L/2,5.85,-.2),(L,4.75,.16))
   if nx<-.1:
    F.box('cv-red-paint',(L/2,5.85,-.3),(max(.5,L-.5),4.45,.1));F.text('CVS',(L/2,5.9,-.37),min(1.7,L*.28),'cv-white-letter')
   for y in np.arange(3.9,8.2,.67):F.box('cv-joint-paint',(L/2,y,-.3),(L,.025,.025))
 W=Frame(B,0,0,y=0)
 for x,z in [(57,280),(57,288),(57,296),(57,304)]:
  W.box('cv-service-paint',(x,8.65,z),(2.3,.85,1.6));W.box('cv-vent-paint',(x,9.09,z),(2,.025,1.3))
 # Satellite-supported service apron, not the importer's five-metre parking box.
 B.source='podium/cvs-east-service-apron';local_pavement(B,box(68,309.9,169,318.5),.18,'cv-concrete-paint');apron=footprint('way/543422869').intersection(box(68,260,180,320))
 B.planar('cv-service-asphalt',apron,.18,True);B.shell(apron,0,.18,'cv-concrete-paint',roof=False)
 # Drain channels at the rear of the shop; metal slats remain below walking clearance.
 for z in [280,288,296,304]:
  B.box('cv-vent-paint',(70,.19,z),(.35,.02,2.2))
  for zz in np.arange(z-1,z+1,.16):B.box('cv-frame-paint',(70,.205,float(zz)),(.31,.015,.025))
 # Closed service door and loading shutter on the shop's rear facade; dimensions estimated.
 W.box('cv-service-paint',(68.04,1.65,286),(.08,3.0,3.2))
 for yy in np.arange(.3,3.2,.22):W.box('cv-joint-paint',(68.09,float(yy),286),(.025,.025,3.1))
 W.box('cv-door-frame-paint',(68.05,1.3,300),(.09,2.3,1.15));W.box('cv-frame-paint',(68.11,1.2,300.38),(.05,.12,.12))
 samples=[[float(x),.18,float(z)]for x in np.arange(69,168,2)for z in np.arange(274,309,2)if apron.buffer(-.3).contains(Point(x,z))]
 Path('build/city-exteriors/cvs-east-apron-samples.json').write_text(json.dumps(samples))
 Path('build/city-exteriors/cvs-east-apron-routes.json').write_text(json.dumps([[[118,.18,315],[118,.18,305]],[[75,.18,315],[75,.18,278]],[[75,.18,278],[75,.18,307]],[[75,.18,305],[163,.18,305]],[[95,.18,274],[150,.18,274]]]))
 return dict(key=KEY,name='CVS Horseshoe Strip frontage',center=[100,0,291],bounds=[34,272,169,319],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
