"""1512 Casino Center: mapped cottage and rear gabled building; Jan2026 reference."""
from common import *
from forum_shops import facade_frame
from rexford_place_west import window
KEY='casinoCenter1512';IDS=['way/1235856400','way/1235856401']
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/casino-center-1512';B.detail=0;ps=[footprint(i)for i in IDS];whole=unary_union(ps);W=Frame(B,0,0,y=0);samples=[];routes=[]
 site=box(1770,-4107,1810,-4092).difference(whole);B.planar('rpw-concrete',site,.18,True)
 for idx,p in enumerate(ps):
  B.shell(p,.18,2.95,'rpw-white-stucco',roof=False)
  es=[facade_frame(B,a,b,p,0)for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:])];F,L,_,_=max([e for e in es if e[2]>.7],key=lambda e:e[1]);depth=max((z-F.z)*F.co+(x-F.x)*F.si for x,z in p.exterior.coords)
  for side in [-1,1]:
   u=-.25 if side<0 else L+.25
   B.upface('rpw-gray-roof-paint',[F.p(u,3.05,-.3),F.p(u,3.05,depth+.3),F.p(L/2,4.5,depth+.3),F.p(L/2,4.5,-.3)],True)
  for w in [0,depth]:B.face('rpw-white-stucco',[F.p(0,2.95,w),F.p(L,2.95,w),F.p(L/2,4.47,w)])
  for G,ll,nx,nz in es:
   G.box('rpw-fascia-paint',(ll/2,2.97,-.10),(ll,.13,.25))
   if G is F:
    du=L*.72;window(G,L*.28,w=2.45)
    G.box('rpw-door-trim-paint',(du,1.25,-.07),(1.04,2.14,.15));G.box('rpw-door-paint',(du,1.25,-.16),(.88,1.99,.04));G.box('rpw-hardware-paint',(du+.31,1.2,-.2),(.04,.14,.04))
    G.box('rpw-awning-paint',(du,2.6,-.6),(1.4,.08,1.2))
    routes.append([G.p(du,.18,-6.0 if idx==1 else -3.5),G.p(du,.18,-1.5),G.p(du,.18,-.55)])
   elif ll>5:window(G,ll*.45,w=1.15)
  for x in np.arange(p.bounds[0]+.5,p.bounds[2],.65):
   for z in np.arange(p.bounds[1]+.5,p.bounds[3],.65):
    if not p.buffer(-.3).contains(Point(x,z)):continue
    u=(x-F.x)*F.co-(z-F.z)*F.si;y=3.05+1.45*(1-abs(u-L/2)/(L/2+.25));samples.append([float(x),y+.4,float(z)])
  if idx==1:
   for a,b in [(0,L*.72-.9),(L*.72+.9,L)]:
    for u in np.arange(a,b,.16):F.box('spad-white-letter',(float(u),1,-5.2),(.025,1.65,.025))
    for y in [.3,1.8]:F.box('spad-white-letter',((a+b)/2,y,-5.2),(b-a,.04,.04))
   lawn=F.poly([(0,-1),(L*.45,-1),(L*.45,-4.9),(0,-4.9)]);B.planar('ww-yard-paint',lawn,.20,True)
   for side in [0,L]:F.box('rpw-fence-paint',(side,1,-2.6),(.035,1.6,5.1))
 Path('build/city-exteriors/casino-center-1512-samples.json').write_text(json.dumps(samples));Path('build/city-exteriors/casino-center-1512-stairs.json').write_text(json.dumps(routes))
 return dict(key=KEY,name='Casino Center 1512 cottage and rear building',center=[1790,0,-4100],bounds=[1770,-4108,1811,-4091],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
