"""Low Santa Paula office: divided-light windows, pale hip roof and fan-palm frontage."""
from common import *
from forum_shops import facade_frame
from oakey_offices import hip
KEY='santaPaulaOffice'
def fan_palm(B,x,z,h,r=1.5):
 F=Frame(B,x,z,y=0);F.box('spo-collision',(0,h/2,0),(.5,h,.5),True);F.lathe('bark',0,0,[(.1,.32),(h*.6,.27),(h,.2)],14)
 for y in np.arange(.3,h,.22):F.lathe('bark',0,0,[(float(y),.26),(float(y)+.06,.33),(float(y)+.15,.28)],12)
 B.detail=0
 for j in range(64):
  a=j*2.399963;co,si=math.cos(a),math.sin(a);tier=(j*.41421356237)%1
  tilt=math.radians(78-158*tier);reach=r*.7*math.cos(tilt);cy=h+r*.7*math.sin(tilt);center=(co*reach,cy,si*reach)
  F.path('spo-palm-stem',[(0,h,0),(co*reach*.55,h+.5,si*reach*.55),center],.023,5)
  # Pleated fan leaves with pointed radial lobes, not broad round canopy blobs.
  for k in range(14):
   angles=[-1.15+k*2.3/14,-1.15+(k+.5)*2.3/14,-1.15+(k+1)*2.3/14]
   points=[]
   for q,t in enumerate(angles):
    length=r*(.86 if q!=1 else 1.0);rad=math.cos(t)*length;tang=math.sin(t)*length
    points.append((center[0]+co*rad*math.cos(tilt)-si*tang,cy+rad*math.sin(tilt)-(.06 if q==1 else 0),center[2]+si*rad*math.cos(tilt)+co*tang))
   mat='spo-palm-leaf' if (j+k)%3 else 'spo-palm-light'
   B.face(mat,[F.p(*center),F.p(*points[0]),F.p(*points[1])]);B.face(mat,[F.p(*center),F.p(*points[1]),F.p(*points[2])])
 # Dried retained frond skirt under mature crowns.
 for j in range(24):
  a=j*math.tau/24;co,si=math.cos(a),math.sin(a)
  B.face('spo-palm-dry',[F.p(co*.27,h,si*.27),F.p(co*.65-si*.13,h-1.8,si*.65+co*.13),F.p(co*.78,h-2.1,si*.78)])
 B.detail=0

def window(G,u):
 G.box('spo-frame-paint',(u,1.6,-.09),(1.35,1.45,.18));G.box('spo-glass',(u,1.6,-.19),(1.19,1.28,.026))
 for du in [-.4,0,.4]:G.box('spo-frame-paint',(u+du,1.6,-.22),(.025,1.3,.03))
 for yy in [1.28,1.6,1.92]:G.box('spo-frame-paint',(u,yy,-.22),(1.2,.025,.03))
 G.box('spo-frame-paint',(u,.85,-.15),(1.5,.11,.3))
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/office';B.detail=0;W=Frame(B,0,0,y=0);p=footprint('way/1236725797')
 B.shell(p,.15,2.8,'spo-siding-paint',roof=False)
 hip(B,p,2.83,1.2)
 for g in B.groups.values():
  if g['material']=='oo-roof-paint':g['material']='spo-roof-paint'
  elif g['material']=='oo-fascia-paint':g['material']='spo-frame-paint'
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  G,L,nx,nz=facade_frame(B,a,b,p,.03)
  G.box('spo-stone-base',(L/2,.45,-.06),(L,.6,.12))
  for u in np.arange(.2,L,.2):G.box('spo-siding-seam-paint',(float(u),1.7,-.042),(.014,2,.025))
  for u in np.arange(.3,L,.55):G.box('spo-frame-paint',(float(u),2.71,-.27),(.07,.15,.56))
  if L>20:
   for u in [L*.12,L*.3,L*.48,L*.72,L*.88]:window(G,u)
   G.box('spo-frame-paint',(L*.6,1.25,-.1),(1.1,2.2,.17));G.box('spo-door-paint',(L*.6,1.22,-.20),(.94,2.08,.03));G.box('spo-glass',(L*.6,1.55,-.23),(.65,1.1,.025));G.box('spo-step',(L*.6,.19,-.64),(1.6,.18,1.25),True)
  else:window(G,L*.35);window(G,L*.72)
 site=box(1938,-3883,1984,-3841).difference(p);B.planar('spo-asphalt',site,.105,True)
 # Gravel strip and the two mature fan palms visible along the south facade.
 B.planar('spo-gravel',box(1940,-3869,1975,-3866),.12,True)
 for x,z,h,r in [(1946,-3867.5,3.3,1.05),(1969.5,-3867.5,3.8,1.45),(1978,-3853,2.3,1.0)]:fan_palm(B,x,z,h,r)
 for x,z in [(1950,-3875),(1964,-3874)]:
  W.lathe('spo-vent',x,z,[(4.0,.08),(4.5,.08),(4.54,.16)],10)
 # Street-side permeable metal fence leaves the existing drive open.
 for za,zb in [(-3865,-3857),(-3848,-3841)]:
  F=Frame(B,1982,za,yaw=-math.pi/2,y=0);L=zb-za
  F.box('spo-boundary-block',(L/2,.4,0),(L,.6,.25),True)
  for u in np.arange(0,L+.01,3):F.box('spo-boundary-block',(float(u),.9,0),(.32,1.6,.32),True)
  for u in np.arange(0,L,.18):F.tube('spo-fence-paint',(float(u),.7,0),(float(u),1.5,0),.018,5)
  for y in [.78,1.34]:F.tube('spo-fence-paint',(0,y,0),(L,y,0),.025,5)
  B.face('spo-collision',[F.p(0,.1,0),F.p(L,.1,0),F.p(L,1.5,0),F.p(0,1.5,0)],True)
 B.groups={k:g for k,g in B.groups.items() if g['material']!='spo-collision'}
 samples=[]
 for x in np.arange(1940,1981,1.3):
  for z in np.arange(-3863,-3843,1.3):
   if math.hypot(x-1978,z+3853)<2:continue
   samples.append([float(x),.105,float(z)])
 Path('build/city-exteriors/santa-paula-office-samples.json').write_text(json.dumps(samples))
 return dict(key=KEY,name='Santa Paula low office',center=[1956,0,-3874],bounds=[1937,-3884,1985,-3840],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
