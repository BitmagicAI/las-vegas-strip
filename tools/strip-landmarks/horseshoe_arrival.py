"""Horseshoe arrival canopy; December2022 Street View + satellite reference.
Mapped plan, estimated canopy heights, retained 6.035m approach bridge datum.
"""
from common import *
KEY='horseshoeArrival';ID='way/115673549'
def exterior(B):
 B.property=KEY+'-exterior';B.source='horseshoe-arrival-canopy';B.detail=0;W=Frame(B,0,0,y=0);p=footprint(ID)
 # Fill only absent ground under this roof; retain every existing road/sidewalk.
 patches=[]
 for g in json.load(open('build/geographic-strip/city-meshes.json')):
  if g['material'] not in ('road','sidewalk','verge','gutter'):continue
  for f in g['faces']:
   vs=[g['vertices'][i]for i in f]
   if max(v[1]for v in vs)>.6 or min(v[1]for v in vs)<-.01:continue
   if max(v[0]for v in vs)<169 or min(v[0]for v in vs)>219 or max(v[2]for v in vs)<175 or min(v[2]for v in vs)>241:continue
   q=Polygon([(v[0],v[2])for v in vs])
   if q.area>.001:patches.append(q)
 missing=p.difference(unary_union(patches));B.planar('ha-ground-asphalt',missing,.135,True)
 # Continuous hidden foundation closes pre-existing collider-only seams.
 B.planar('ha-collision',p,.13,True)
 Path('build/city-exteriors/horseshoe-arrival-ground-fill.json').write_text(json.dumps({'missingAreaM2':missing.area,'scope':'Only unsupported ground within mapped canopy footprint; existing ground surfaces retained'}))
 # Broad flat side wings with inset roof wells, central barrel skylight.
 center=box(168,201,220,215);side=p.difference(center)
 wells=unary_union([box(186,184,207,195),box(184.5,221,205.5,231.5)])
 roof=side.difference(wells)
 B.shell(side,8.65,9.25,'ha-fascia-paint',roof=False)
 B.planar('ha-roof-paint',roof,9.27,True)
 B.planar('ha-roof-paint',wells.intersection(side),8.92,True)
 B.shell(wells.intersection(side),8.92,9.27,'ha-fascia-paint',roof=False)
 for poly in parts(side):
  for tri in triangles(poly):B.face('ha-soffit-paint',[(x,8.65,z)for x,z in list(tri.exterior.coords)[:-1]],True)
 # Deep front fascia, diagonal exposed braces visible from Horseshoe Drive.
 ps=list(p.exterior.coords)
 for a,b in zip(ps,ps[1:]):
  L=math.dist(a,b)
  if L<.1:continue
  for y in [8.65,10.55]:B.tube('ha-steel-paint',(a[0],y,a[1]),(b[0],y,b[1]),.085,8)
  for i in range(max(1,round(L/3.5))):
   n=max(1,round(L/3.5));t0=i/n;t1=(i+1)/n
   aa=(a[0]+(b[0]-a[0])*t0,a[1]+(b[1]-a[1])*t0);bb=(a[0]+(b[0]-a[0])*t1,a[1]+(b[1]-a[1])*t1)
   B.face('ha-panel-glass',[(aa[0],8.72,aa[1]),(bb[0],8.72,bb[1]),(bb[0],10.48,bb[1]),(aa[0],10.48,aa[1])])
   B.tube('ha-steel-paint',(aa[0]-.04,8.7,aa[1]-.04),(bb[0]-.04,10.5,bb[1]-.04),.07,8)
 # Central gently curved green glass roof, solid shell overhead, fine mullions.
 def h(z):return 10.55+1.55*max(0,1-((z-208)/7)**2)
 xs=list(np.linspace(169.5,218,17));zs=list(np.linspace(201,215,13))
 for a,b in zip(xs,xs[1:]):
  for c,d in zip(zs,zs[1:]):
   B.upface('ha-roof-glass',[(a,h(c),c),(b,h(c),c),(b,h(d),d),(a,h(d),d)],True)
 for x in xs:B.path('ha-frame-paint',[(x,h(z)+.035,z)for z in zs],.055,6)
 for z in zs:B.tube('ha-frame-paint',(169.5,h(z)+.035,z),(218,h(z)+.035,z),.035,6)
 # Round metal column clusters; collars and cylindrical collision.
 for x in [179,211]:
  for z in [183,194,222,233]:
   if not p.buffer(-1).contains(Point(x,z)):continue
   for dz in [-.8,.8]:
    W.lathe('ha-steel-paint',x,z+dz,[(.28,.6),(.48,.6),(.55,.49),(8.55,.49),(8.65,.62)],24)
    W.box('ha-collision',(x,4.45,z+dz),(.85,8.3,.85),True)
    for y in [.6,4.5,8.4]:W.lathe('ha-frame-paint',x,z+dz,[(y-.04,.5),(y+.04,.5)],24)
 # Approach bridge enters at6.035m. Keep that datum and provide a continuous deck.
 deck=p.intersection(box(169,203,219,213));B.planar('ha-paving-concrete',deck,6.035,True);B.shell(deck,5.72,6.035,'ha-soffit-paint',roof=False)
 for z in [203.02,212.98]:
  for yy in [6.35,7.1]:B.tube('ha-frame-paint',(170,yy,z),(218,yy,z),.045,8)
  for x in np.arange(170,218,2):W.box('ha-frame-paint',(x,6.59,z),(.065,1.1,.065),True)
  W.box('ha-collision',(194,6.59,z),(48,1.1,.08),True)
 for k in list(B.groups):
  if B.groups[k]['material']=='ha-collision':del B.groups[k]
 return dict(key=KEY,name='Horseshoe arrival canopy',center=[194,0,208],bounds=[169,175,219,241],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
