"""Western WhiteCrossMarket wing with north/west tiled mansards and recessed fronts."""
from common import *
from forum_shops import facade_frame
KEY='whiteCrossAnnex'
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/annex';B.detail=0;W=Frame(B,0,0,y=0)
 p=footprint('way/316303725');B.shell(p,.15,5.9,'wca-stucco',roof=False);B.planar('wca-roof-paint',p,5.82,True)
 fronts=[]
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  G,L,nx,nz=facade_frame(B,a,b,p,.035)
  # Shared east wall is retained as an interior boundary; no duplicate decoration over market1700.
  if nx>.7:continue
  G.box('wca-cap-paint',(L/2,5.95,-.03),(L,.12,.2))
  if (nx<-.7 or nz<-.7) and L>10:
   fronts.append((G,L,nx,nz))
   G.box('wca-shadow-paint',(L/2,1.8,-.08),(L,3.3,.12))
   for u in np.arange(1.6,L,3.1):
    G.box('wca-board-paint',(float(u),1.5,-.18),(2.95,2.5,.12))
    for du in [-.75,0,.75]:G.box('wca-board-joint-paint',(float(u)+du,1.5,-.25),(.018,2.5,.025))
   # Cream fascia casts a real canopy shadow; piers stand ahead of the boarded enclosure.
   G.box('wca-stucco',(L/2,3.8,-.85),(L,.95,1.6))
   G.box('wca-soffit-paint',(L/2,3.3,-.85),(L,.08,1.6))
   B.upface('wca-tile-paint',[G.p(0,4.28,-1.65),G.p(L,4.28,-1.65),G.p(L,5.95,.7),G.p(0,5.95,.7)])
   # Tile roll profile follows the slope; detail layer leaves the same solid roof silhouette at distance.
   B.detail=1
   slope=1.67/2.35
   for u in np.arange(.12,L-.1,.24):
    for row in range(6):
     v0=-1.65+row*2.35/6;v1=v0+2.35/6+.025
     for k in range(6):
      a0=k*math.pi/6;a1=(k+1)*math.pi/6
      def pt(a,v):return G.p(float(u)+.105*math.cos(a),4.29+(v+1.65)*slope+.06*math.sin(a),v)
      B.upface('wca-tile-roll-paint',[pt(a0,v0),pt(a1,v0),pt(a1,v1),pt(a0,v1)])
   B.detail=0
   for u in np.linspace(.1,L-.1,6):
    G.box('wca-pier-paint',(float(u),1.8,-1.38),(.28,3.4,.35),True)
    G.box('wca-pier-paint',(float(u),3.91,-.72),(.28,1.15,2.0))
    B.face('wca-pier-paint',[G.p(u-.14,4.3,-1.7),G.p(u+.14,4.3,-1.7),G.p(u+.14,6.1,.75),G.p(u-.14,6.1,.75)])
   G.box('wca-paving',(L/2,.16,-1.45),(L,.08,2.9),True)
   G.box('wca-sign-paint',(L*.52,3.83,-1.69),(9.8,1.5,.1))
   if nx<-.7:G.text('FOR SALE',(L*.52,3.7,-1.77),.7,'wca-green-letter')
   else:
    G.text('WHITE CROSS',(L*.52,4.1,-1.77),.42,'wca-red-letter');G.text('Market',(L*.52,3.38,-1.77),.83,'wca-red-letter')
  elif L>8:
   for u in np.arange(1,L,4):G.box('wca-joint-paint',(float(u),2.85,-.04),(.02,5.4,.03))
   G.box('wca-service-paint',(L*.77,1.5,-.08),(1.1,2.55,.14));G.box('wca-vent',(L*.25,3.5,-.09),(1.4,.7,.16))
 site=Polygon([(1698,-3895),(1774,-3895),(1774,-3838),(1698,-3838)]).difference(p)
 B.planar('wca-asphalt',site,.1,True)
 # Parking bays parallel MainStreet; no alteration of city-road surface geometry.
 for z in np.arange(-3890,-3840,2.8):W.box('wca-line-paint',(1704,.115,float(z)),(4.5,.02,.06))
 for x in np.arange(1707,1769,2.8):W.box('wca-line-paint',(float(x),.115,-3890),(.06,.02,4.5))
 # Closed-site temporary fence set in front of the building, with a broad public parking approach outside.
 for G,L,nx,nz in fronts:
  for u in np.arange(0,L,3.1):
   end=min(L,float(u)+3.1)
   for x in [float(u),end]:G.tube('wca-fence-paint',(x,.12,-3.3),(x,1.95,-3.3),.025,8)
   for y in [.15,1.95]:G.tube('wca-fence-paint',(float(u),y,-3.3),(end,y,-3.3),.025,8)
   for x in np.arange(float(u),end,.28):
    for direction in [-1,1]:
     dest=min(end,max(float(u),float(x)+direction*1.8));height=.15+abs(dest-float(x))
     if abs(dest-float(x))>.01:G.tube('wca-fence-wire',(float(x),.15,-3.3),(dest,height,-3.3),.006,4)
  B.face('wca-collision',[G.p(0,.1,-3.3),G.p(L,.1,-3.3),G.p(L,2,-3.3),G.p(0,2,-3.3)],True)
 B.groups={k:g for k,g in B.groups.items() if g['material']!='wca-collision'}
 for x,z in [(1741,-3874),(1751,-3873),(1765,-3872),(1743,-3864),(1756,-3854)]:
  W.box('wca-service-paint',(x,6.2,z),(1.4,.8,1.2));W.box('wca-vent',(x,6.62,z),(1.2,.04,1))
 # Flat roof seam pattern is geometry at roof scale, not per-pixel noise.
 for x in np.arange(1738,1773,2):
  strip=box(float(x)-.02,-3879,float(x)+.02,-3847).intersection(p)
  B.planar('wca-roof-seam-paint',strip,5.832)
 samples=[]
 for x in np.arange(1700,1772,1.5):
  for z in np.arange(-3893,-3840,1.5):
   pt=Point(x,z)
   if site.buffer(-.7).covers(pt) and not p.buffer(4.7).covers(pt):samples.append([float(x),.1,float(z)])
 Path('build/city-exteriors/white-cross-annex-samples.json').write_text(json.dumps(samples))
 return dict(key=KEY,name='WhiteCrossMarket west wing',center=[1755,0,-3863],bounds=[1697,-3896,1775,-3837],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
