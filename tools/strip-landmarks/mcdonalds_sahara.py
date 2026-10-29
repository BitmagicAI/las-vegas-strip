"""Original exterior/patio; 2019 photograph details explicitly dated, dimensions fitted."""
from common import *
KEY='mcdonalds-sahara';IDS=['way/276426396']
def build(B):
 B.property=KEY+'-exterior';B.source='retail/'+KEY;B.detail=0
 p=footprint(IDS[0]);B.shell(p,.02,6.5,'ms-white',roof=False);B.planar('ms-membrane',p,6.15)
 # White parapet, restrained yellow coping, front/east glazing, service rear.
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  dx,dz=b[0]-a[0],b[1]-a[1];L=math.hypot(dx,dz);F=Frame(B,(a[0]+b[0])/2,(a[1]+b[1])/2,math.atan2(-dz,dx),y=0)
  for y,h,d in [(6.52,.12,.30),(6.30,.07,.17)]:F.box('ms-yellow',(0,y,0),(L,h,d))
  F.box('ms-red',(0,.32,0),(L,.64,.19))
  front=F.z>-3200 or F.x>-377
  if front:
   for u in np.linspace(-L/2+1.8,L/2-1.8,max(1,int(L/3.4))):
    for side in [-1,1]:
     F.box('ms-glass',(float(u),1.98,side*.12),(2.8,2.55,.045))
     for x in [-1.42,0,1.42]:F.box('ms-frame',(float(u+x),1.98,side*.17),(.055,2.65,.055))
     for y in [.67,3.3]:F.box('ms-frame',(float(u),y,side*.17),(2.88,.06,.06))
  else:
   for side in [-1,1]:
    if F.z < -3212:F.box('ms-service',(0,1.4,side*.12),(1.15,2.75,.06))
    for u in [-L*.3,L*.3]:
     F.box('ms-frame',(u,3.4,side*.12),(1.6,.8,.07))
     for y in np.arange(3.05,3.76,.1):F.box('ms-service',(u,float(y),side*.17),(1.5,.025,.025))
 S=Frame(B,-384.5,-3198.55,.0117,y=0)
 # Sloped canvas awning and straight valance, observed over the south frontage.
 B.face('ms-yellow',[S.p(-8,3.8,.15),S.p(8,3.8,.15),S.p(8,3.15,1.75),S.p(-8,3.15,1.75)])
 S.box('ms-yellow',(0,3.08,1.75),(16,.18,.09))
 for u in [-8,8]:B.face('ms-yellow',[S.p(u,3.8,.15),S.p(u,3.15,1.75),S.p(u,3.0,.15)])
 for u in [-6,-2,2,6]:S.tube('ms-frame',(u,3.1,.15),(u,3.1,1.65),.025,6)
 S.box('ms-red',(1.0,5.12,.17),(9.4,1.15,.17));S.text("McDonald's",(1.0,4.8,.28),.76,'ms-letter',back=True)
 # Original tubular arches on a circular red plaque, no copied bitmap.
 S.tube('ms-red',(-5.65,5.15,.12),(-5.65,5.15,.3),.85,32)
 for off in [-.53,0]:
  pts=[(-5.65+off+float(t)*.53,4.75+.9*math.sin(float(t)*math.pi),.34) for t in np.linspace(0,1,17)]
  S.path('ms-gold',pts,.05,8)
 # Closed exterior door; public interior not yet evidenced for this branch.
 S.box('ms-glass',(5.6,1.65,.18),(1.7,2.9,.07))
 for u in [4.72,5.6,6.48]:S.box('ms-frame',(u,1.65,.25),(.06,3,.05))
 for u in [5.42,5.78]:S.box('ms-metal',(u,1.45,.31),(.035,.5,.035))
 # Patio is fitted to the photographed south frontage; central aisle remains open.
 S.box('ms-paving',(0,.08,1.8),(17,.16,3.1),True)
 for u in np.arange(-8,8.1,.5):S.box('ms-grout',(float(u),.163,1.8),(.009,.005,3.1))
 for v in [1,1.5,2,2.5,3]:S.box('ms-grout',(0,.163,v),(17,.005,.009))
 for lo,hi in [(-8.3,-1.2),(1.2,8.3)]:
  for y in [.32,1.25]:S.box('ms-red',((lo+hi)/2,y,3.3),(hi-lo,.055,.055))
  for u in np.arange(lo,hi+.05,.19):S.box('ms-red',(float(u),.78,3.3),(.025,.96,.025))
  for u in [lo,hi]:S.box('ms-red',(u,.75,3.3),(.07,1.18,.07),True)
 for u in [-5,2.7]:
  S.lathe('ms-metal',u,1.65,[(.16,.34),(.24,.34),(.27,.06),(.9,.06)],16)
  S.lathe('ms-table',u,1.65,[(.9,.55),(.96,.55)],24)
  for du in [-.95,.95]:
   for x in [-.22,.22]:
    for z in [-.22,.22]:S.box('ms-metal',(u+du+x,.39,1.65+z),(.035,.46,.035))
   S.box('ms-table',(u+du,.65,1.65),(.5,.08,.5),True)
   S.box('ms-table',(u+du,1.0,1.91),(.5,.62,.06))
 B.upface('ms-paving',[S.p(-1.15,.01,5),S.p(1.15,.01,5),S.p(1.15,.16,3.2),S.p(-1.15,.16,3.2)],True)
 # West pickup frontage and unobtrusive rooftop services.
 W=Frame(B,-393.14,-3206,-math.pi/2,y=0)
 W.box('ms-glass',(0,2,.12),(2.6,1.5,.055))
 for u in [-1.33,0,1.33]:W.box('ms-frame',(u,2,.17),(.055,1.6,.05))
 W.box('ms-white',(0,1.2,.3),(2.8,.12,.5));W.box('ms-red',(0,3,.6),(3.2,.15,1.3))
 Q=Frame(B,0,0,0,y=0)
 for x,z in [(-389,-3204),(-382,-3208),(-389,-3210)]:
  Q.box('ms-equipment',(x,6.58,z),(2.3,.85,1.6))
  for v in np.arange(-.6,.61,.17):Q.box('ms-frame',(x,7.02,z+float(v)),(1.9,.025,.04))
 routes=[dict(name='Patio approach',points=[S.p(0,.2,v) for v in [7,5,3.7,2.6,1.2]]),dict(name='West drive frontage',points=[[-397,.24,z] for z in [-3196,-3205,-3216]])]
 return dict(key=KEY,name='McDonalds West Sahara',center=[-385,0,-3206],bounds=list(p.bounds),structural=True,hotelSources=[],exteriorOnly=True,portals=[],zones=[],lights=[],routes=routes)
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
