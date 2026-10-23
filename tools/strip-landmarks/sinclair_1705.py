"""Sinclair 1705: January2026 Street View and overhead plan; estimated elevations."""
from common import *
from forum_shops import facade_frame
KEY='sinclair1705'
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/station';B.detail=0
 p=footprint('way/316303727');B.shell(p,.18,3.65,'sc17-white-paint',roof=False);B.planar('sc17-roof-paint',p,3.5,True)
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  G,L,nx,nz=facade_frame(B,a,b,p,.04)
  G.box('sc17-gray-paint',(L/2,.55,-.05),(L,.74,.14));G.box('sc17-white-paint',(L/2,3.62,-.07),(L,.2,.2))
  if nx<-.7:
   front=G;length=L
   for u in np.arange(5.15,L-4.5,1.45):
    G.box('sc17-glass',(float(u),1.65,-.1),(1.37,2.2,.1))
    for du in [-.71,.71]:G.box('sc17-black-paint',(float(u)+du,1.65,-.18),(.05,2.3,.07))
   for y in [.51,2.78]:G.box('sc17-black-paint',(L/2,y,-.18),(L-8.8,.07,.07))
   # Shallow dark awning, closed fascia and real projecting soffit.
   G.box('sc17-black-paint',(L/2,3.05,-.8),(L-.35,.16,1.6))
   for u in np.arange(.3,L,.42):G.tube('sc17-metal-paint',(float(u),3.14,-.02),(float(u),3.14,-1.6),.012,4)
   G.text('FOOD • DRINKS',(L/2,3.32,-.18),.26,'sc17-dark-letter')
   for u in [L*.5-.45,L*.5+.45]:G.box('sc17-metal-paint',(u,1.45,-.22),(.04,.55,.06))
   G.box('sc17-paving',(L/2,.23,-1),(L,.1,2),True)
  else:
   G.box('sc17-service-paint',(L*.5,1.4,-.08),(1.1,2.4,.12));G.box('sc17-vent',(L*.75,2.7,-.1),(.8,.5,.12))
 G=front;L=length
 # End roofs: dark shallow hips, central flat equipment well remains exposed.
 for lo,hi in [(0,4.6),(L-4.6,L)]:
  for pts in [[(lo-.2,3.7,-.2),(hi+.2,3.7,-.2),(hi-.5,4.45,4.3),(lo+.5,4.45,4.3)],[(lo-.2,3.7,9.3),(lo+.5,4.45,4.3),(hi-.5,4.45,4.3),(hi+.2,3.7,9.3)],[(lo-.2,3.7,-.2),(lo+.5,4.45,4.3),(lo-.2,3.7,9.3)],[(hi+.2,3.7,-.2),(hi+.2,3.7,9.3),(hi-.5,4.45,4.3)]]:B.face('sc17-black-roof-paint',[G.p(*v) for v in pts])
 for u in [7,11,15,18]:
  G.box('sc17-service-paint',(u,3.88,5),(1,.65,1.3));G.box('sc17-vent',(u,4.22,5),(.75,.04,1))
 # Long narrow forecourt canopy. Three bays observed; clear height estimated4.1m.
 cu=L/2;cw=-11.5
 G.box('sc17-white-paint',(cu,4.62,cw),(24,.8,5.5))
 G.box('sc17-green-paint',(cu,4.6,cw-2.78),(23.8,.4,.07));G.box('sc17-roof-paint',(cu,5.035,cw),(23.8,.03,5.3))
 for u in [cu-11.9,cu+11.9]:G.box('sc17-green-paint',(u,4.6,cw),(.08,.4,5.4))
 G.box('sc17-white-paint',(cu-7,4.62,cw-2.84),(7.1,.74,.08));G.text('Sinclair',(cu-7,4.38,cw-2.9),.68,'sc17-red-letter')
 for u in [cu-8,cu,cu+8]:
  G.box('sc17-island',(u,.28,cw),(1.5,.2,3.7),True);G.box('sc17-white-paint',(u,2.24,cw+.7),(.34,4.12,.34),True)
  G.box('sc17-white-paint',(u,1.2,cw-.65),(1.05,1.8,.58),True);G.box('sc17-green-paint',(u,.65,cw-.65),(1.08,.8,.62));G.box('sc17-green-paint',(u,2.18,cw-.65),(1.12,.25,.65))
  for side in [-1,1]:
   G.box('sc17-black-paint',(u,1.55,cw-.65+side*.33),(.89,.75,.05));G.box('sc17-display',(u,1.76,cw-.65+side*.365),(.5,.23,.02))
   for du in [-.26,0,.26]:G.box('sc17-button',(u+du,1.34,cw-.65+side*.37),(.12,.07,.02))
   G.path('sc17-black-paint',[(u+side*.56,2,cw-.65),(u+side*.7,1.7,cw-.65),(u+side*.72,.55,cw-.65),(u+side*.56,.48,cw-.65),(u+side*.5,1,cw-.65)],.028,8)
  for du in [-.65,.65]:G.tube('sc17-green-paint',(u+du,.18,cw-1.6),(u+du,.95,cw-1.6),.055,8)
  G.box('sc17-white-paint',(u,4.2,cw),(1,.04,.45))
 # Local apron stops at pavement and store. Preserve the separate bus shelter/road ownership.
 site=G.poly([(-3,-16),(L+3,-16),(L+3,0),(-3,0)])
 B.planar('sc17-asphalt',site,.18,True)
 for u in np.arange(2,L,3):G.box('sc17-white-paint',(float(u),.193,-3.2),(.08,.014,2.3))
 # Small utility cabinets at south end; pylon separated from pump circulation.
 G.box('sc17-white-paint',(-1,1.1,0),(.9,1.85,.7),True)
 G.box('sc17-white-paint',(L+1.2,3.2,-15),(.24,6,.24),True)
 G.box('sc17-white-paint',(L+1.2,6,-15),(1.8,1.65,.18));G.box('sc17-green-paint',(L+1.2,6,-15.11),(1.65,1.5,.05));G.text('Sinclair',(L+1.2,6.25,-15.17),.3,'sc17-white-letter');G.text('FUEL',(L+1.2,5.62,-15.17),.29,'sc17-white-letter')
 samples=[]
 for u in np.arange(-2,L+2,1.1):
  for w in np.arange(-15,-2,1.1):
   if any(abs(u-v)<1.15 and abs(w-cw)<2.3 for v in [cu-8,cu,cu+8]):continue
   if abs(u-(L+1.2))<.65 and abs(w+15)<.7:continue
   samples.append(list(G.p(float(u),.18,float(w))))
 Path('build/city-exteriors/sinclair-1705-samples.json').write_text(json.dumps(samples))
 Path('build/city-exteriors/sinclair-1705-route.json').write_text(json.dumps([[G.p(u,0,w)[0],G.p(u,0,w)[2]] for u,w in [(1,-5),(L/2,-5),(L-1,-5),(L-1,-14.5)]]))
 return dict(key=KEY,name='Sinclair 1705 exterior',center=[1870,0,-3884],bounds=[1853,-3907,1894,-3861],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
