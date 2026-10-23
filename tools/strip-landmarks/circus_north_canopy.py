"""North canopy: January2025 Google Street View, mapped footprint.
Estimated 5.8m roof/5.35m clear soffit; parent casino envelope retained.
"""
from common import *
from forum_shops import facade_frame
KEY='circusNorthCanopy';IDS=['way/1431436415']
def exterior(B):
 B.property=KEY+'-exterior';B.source='circus-north-canopy';B.detail=0;p=footprint(IDS[0]);W=Frame(B,0,0,y=0)
 B.planar('cc-flat-roof',p,5.8,True);B.shell(p,5.35,5.8,'cc-white',roof=False)
 for t in triangles(p):B.face('cc-shadow',[(x,5.35,z)for x,z in list(t.exterior.coords)[:-1]][::-1],True)
 # Long northern fascia, trimmed to the real source outline.
 a,b=(902.918,-2365.55),(916.218,-2358.437);F,L,_,_=facade_frame(B,a,b,p,0)
 for y,h,d,mat in [(5.34,.18,.26,'cc-pink'),(5.61,.18,.30,'cc-white'),(5.83,.12,.32,'cc-sill')]:F.box(mat,(L/2,y,0),(L,h,d))
 # Structural concrete posts with chamfered octagonal cross sections.
 for u in [1.2,L-1.2]:
  x,y,z=F.p(u,0,.45);q=Point(x,z).buffer(.42,resolution=2)
  B.shell(q,.20,5.35,'cc-white',roof=False);B.planar('cc-white',q,5.35,True)
 # Visible under-canopy beams, cross ties and shallow conduit runs.
 for u in np.arange(.5,L,.95):F.box('cc-metal',(float(u),5.15,1.65),(.075,.27,3.05))
 for w in [.6,2.6]:F.box('cc-metal',(L/2,5.05,w),(L,.14,.10))
 for u in [2.2,7,12.2]:
  F.box('cc-shadow',(u,4.98,1.5),(.36,.08,.36))
  F.tube('cc-metal',(u,5.05,.5),(u,5.05,2.7),.018,6)
 # Individual unlit marquee bulbs; no extra runtime lights.
 for u in np.arange(.25,L,.23):
  x,y,z=F.p(float(u),5.64,-.18);B.lathe('cc-gold',(x,z),[(y-.025,.025),(y+.025,.025)],6)
 B.planar('cc-sill',p,.20,True)
 samples=[]
 for x in np.arange(p.bounds[0],p.bounds[2],.5):
  for z in np.arange(p.bounds[1],p.bounds[3],.5):
   if p.buffer(-.1).contains(Point(x,z)):samples.append([float(x),6.15,float(z)])
 routes=[[list(F.p(u,.20,1.6))for u in [2,5,8,11,13]], [list(F.p(7,.20,w))for w in [-1,0,1,2.5]]]
 Path('build/city-exteriors/circus-north-canopy-samples.json').write_text(json.dumps(samples));Path('build/city-exteriors/circus-north-canopy-stairs.json').write_text(json.dumps(routes))
 return dict(key=KEY,name='Circus Circus north roadside canopy',center=[909,0,-2360],bounds=list(p.bounds),structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
