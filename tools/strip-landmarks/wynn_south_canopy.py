"""Wynn South Gate porte-cochere: satellite plan, January 2025 driveway view."""
from common import *
from forum_shops import facade_frame
KEY='wynnSouthCanopy'
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/way/886592895';B.detail=0;p=footprint('way/886592895');h=7.1
 # Deep cream entablature, elliptical arches and substantial square piers.
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  F,L,nx,nz=facade_frame(B,a,b,p,0)
  if L<3:continue
  n=max(1,round(L/8));step=L/n;region=box(0,.20,L,h)
  for j in range(n):
   c=(j+.5)*step;r=(step-1.4)/2
   if r<.5:continue
   arch=[(c-r,.1),(c+r,.1),(c+r,4.35)]+[(c+r*math.cos(t),4.35+1.35*math.sin(t)) for t in np.linspace(0,math.pi,32)]+[(c-r,.1)]
   region=region.difference(Polygon(arch))
   # Recessed arched soffit, trim and a true open aperture through the fascia.
   pts=[F.p(c+r*math.cos(t),4.35+1.35*math.sin(t),-.04) for t in np.linspace(0,math.pi,33)]
   for aa,bb in zip(pts,pts[1:]):B.tube('wsc-trim-stone',aa,bb,.105,8)
   for t,u in zip(np.linspace(0,math.pi,33),np.linspace(0,math.pi,33)[1:]):
    B.face('wsc-soffit-paint',[F.p(c+r*math.cos(t),4.35+1.35*math.sin(t),0),F.p(c+r*math.cos(u),4.35+1.35*math.sin(u),0),F.p(c+r*math.cos(u),4.35+1.35*math.sin(u),.7),F.p(c+r*math.cos(t),4.35+1.35*math.sin(t),.7)])
  for q in parts(region):
   for tri in triangles(q):
    vs=list(tri.exterior.coords)[:-1]
    B.face('wsc-cream-stucco',[F.p(x,y,0) for x,y in vs],True)
    B.face('wsc-cream-stucco',[F.p(x,y,.7) for x,y in reversed(vs)],True)
  for y,dy,depth in [(6.45,.16,.18),(6.83,.22,.30),(7.08,.18,.44)]:F.box('wsc-trim-stone',(L/2,y,.15),(L+.05,dy,depth+.7))
  # Subtle terracotta relief panels on square piers.
  for j in range(n+1):
   u=min(L-.45,max(.45,j*step))
   F.box('wsc-plinth-stone',(u,.4,.35),(.95,.4,.9))
   F.box('wsc-relief-paint',(u,2.85,-.025),(.22,1.85,.05))
 # Continuous roof slab; underside wound down, with no wall across the driveway.
 B.planar('wsc-roof-paint',p,7.2,True)
 for q in parts(p):
  for tri in triangles(q):
   vs=[(x,6.65,z) for x,z in list(tri.exterior.coords)[:-1]]
   if np.cross(np.array(vs[1])-vs[0],np.array(vs[2])-vs[0])[1]>0:vs.reverse()
   B.face('wsc-soffit-paint',vs,True)
 inner=p.buffer(-2.8,join_style=2)
 # Mitered standing-seam hip perimeter around the low tan central roof.
 for q in parts(p.difference(inner)):
  for tri in triangles(q):
   B.upface('wsc-hip-metal-paint',[(x,7.23+min(2.8,p.boundary.distance(Point(x,z)))*.52,z) for x,z in list(tri.exterior.coords)[:-1]],True)
 B.planar('wsc-roof-paint',inner,8.70,True)
 # Roof border coping and drainage are geometry, without extra live lights.
 for a,b in zip(list(inner.exterior.coords),list(inner.exterior.coords)[1:]):B.tube('wsc-trim-stone',(a[0],8.73,a[1]),(b[0],8.73,b[1]),.10,8)
 samples=[]
 for x in np.arange(p.bounds[0]+.5,p.bounds[2],1.2):
  for z in np.arange(p.bounds[1]+.5,p.bounds[3],1.2):
   pt=Point(x,z)
   if p.buffer(-.3).contains(pt):samples.append([float(x),9.3,float(z)])
 Path('build/city-exteriors/wynn-south-canopy-samples.json').write_text(json.dumps(samples))
 return dict(key=KEY,name='Wynn South Gate porte-cochere',center=[589,0,-1080],bounds=list(p.buffer(2).bounds),structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
