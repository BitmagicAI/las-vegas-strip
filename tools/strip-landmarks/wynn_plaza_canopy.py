"""Wynn Plaza curved motor court canopy from April2025 StreetView.
Mapped curving narrow footprint; eaves/roof elevations estimated from photo.
"""
from common import *
from forum_shops import facade_frame
KEY='wynnPlazaCanopy';IDS=['way/1419057384']
def exterior(B):
 B.property=KEY+'-exterior';B.source='wynn-plaza-canopy';B.detail=0;p=footprint(IDS[0]);W=Frame(B,0,0,y=0)
 B.planar('wpc-roof-paint',p,7.5,True);B.shell(p,4.9,7.5,'wpc-travertine-stone',roof=False)
 for tri in triangles(p):
  vs=[(x,4.9,z)for x,z in list(tri.exterior.coords)[:-1]]
  if np.cross(np.array(vs[1])-vs[0],np.array(vs[2])-vs[0])[1]>0:vs.reverse()
  B.face('wpc-soffit-paint',vs,True)
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  F,L,nx,nz=facade_frame(B,a,b,p,0)
  for y,h,d in [(4.98,.16,.20),(7.34,.18,.24),(7.55,.12,.38)]:F.box('wpc-cream-stucco',(L/2,y,0),(L+.03,h,d))
  # Narrow upper screen following the east edge of the curved canopy.
  if nx>.6:
   F.box('wpc-cream-stucco',(L/2,8.05,.20),(L+.02,1.0,.18),True)
   F.box('wpc-cream-stucco',(L/2,8.59,.20),(L+.03,.12,.30))
 # White square end piers, leaving the curving vehicle lane fully open.
 for x,z in [(595.5,-1259.3),(598.2,-1276.5)]:
  W.box('wpc-cream-stucco',(x,2.55,z),(.55,4.7,.55),True);W.box('wpc-cream-stucco',(x,.35,z),(.8,.5,.8),True)
 # Suspended tapered lanterns and sparse underside beams, no new scene lights.
 for x,z in [(595.5,-1263),(595.5,-1268),(596.0,-1273)]:
  B.tube('wpc-bronze-paint',(x,4.9,z),(x,4.5,z),.018,6)
  B.lathe('wpc-lantern-glass',(x,z),[(4.05,.07),(4.4,.16),(4.5,.12)],6)
  B.lathe('wpc-bronze-paint',(x,z),[(4.4,.18),(4.46,.18)],6)
 B.planar('wpc-paving-stone',p.union(LineString([(590,-1266),(595,-1266)]).buffer(1.2,cap_style=2)),.20,True)
 samples=[]
 for x in np.arange(p.bounds[0],p.bounds[2],.5):
  for z in np.arange(p.bounds[1],p.bounds[3],.5):
   if p.buffer(-.2).contains(Point(x,z)):samples.append([float(x),7.85,float(z)])
 routes=[[(595,.20,-1261),(595,.20,-1265),(595,.20,-1270),(596,.20,-1275)],[(590,.20,-1266),(593,.20,-1266),(595,.20,-1266)]]
 Path('build/city-exteriors/wynn-plaza-canopy-samples.json').write_text(json.dumps(samples));Path('build/city-exteriors/wynn-plaza-canopy-stairs.json').write_text(json.dumps(routes))
 return dict(key=KEY,name='Wynn Plaza curved canopy',center=[596,0,-1270],bounds=list(p.bounds),structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
