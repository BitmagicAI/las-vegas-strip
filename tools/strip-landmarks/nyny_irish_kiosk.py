"""Mapped green Nine Fine Irishmen outdoor kiosk. April2025 StreetView.
3m height from map, .24m world datum retained; photograph's broad terrace steps
belong to the existing frontage and remain a separate grade reconciliation task.
"""
from common import *
from forum_shops import facade_frame
KEY='nynyIrishKiosk';IDS=['way/399323162']
def exterior(B):
 B.property=KEY+'-exterior';B.source='nyny-irish-kiosk';B.detail=0
 p=footprint(IDS[0]);D=.28;B.shell(p,D,D+2.92,'nik-green-paint',roof=False)
 B.planar('nik-roof-paint',p.buffer(.13,join_style=2),D+3.0,True)
 B.planar('nik-floor-concrete',p,D,True)
 # Framed green panels, dark upper sign boxes and projecting counters.
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  F,L,nx,nz=facade_frame(B,a,b,p,.04);F.y=D
  for y,h,dep in [(.10,.20,.07),(.82,.13,.10),(2.08,.12,.12),(2.82,.13,.17),(3.03,.13,.24)]:F.box('nik-edge-paint',(L/2,y,-dep/2),(L+.12,h,dep))
  for u in [.11,L-.11]:
   F.box('nik-edge-paint',(u,1.47,-.10),(.22,2.9,.23))
   F.box('nik-base-paint',(u,.47,-.15),(.31,.78,.30))
   for k in [-.09,0,.09]:F.box('nik-edge-paint',(u+k,.47,-.31),(.032,.66,.04))
  bays=max(2,round((L-.44)/.82));bw=(L-.44)/bays
  for j in range(bays):
   u=.22+(j+.5)*bw
   F.box('nik-panel-paint',(u,.48,-.045),(bw-.08,.60,.035))
   F.box('nik-panel-paint',(u,1.47,-.045),(bw-.08,1.03,.035))
   for yy in [.97,1.97]:F.box('nik-edge-paint',(u,yy,-.075),(bw-.045,.035,.035))
   for du in [-bw/2+.035,bw/2-.035]:F.box('nik-edge-paint',(u+du,1.47,-.075),(.035,1.03,.035))
   # Framed paper menu panels visible in the photographed closed serving shutters.
   F.box('nik-menu-frame-paint',(u,1.55,-.085),(.30,.40,.035))
   F.box('nik-paper-paint',(u,1.55,-.109),(.265,.36,.008))
   for yy in np.arange(1.43,1.69,.045):F.box('nik-ink-paint',(u,yy,-.116),(.19,.008,.008))
  F.box('nik-sign-paint',(L/2,2.51,-.075),(L-.55,.43,.10))
  F.text('PINTS · FOOD · SPIRITS',(L/2,2.49,-.135),.13,'nik-gold-letter')
  F.box('nik-counter-paint',(L/2,.91,-.28),(L-.43,.10,.62),True)
  # Roofline raised square end plaques and small cap balls.
  for u in [.30,L-.30]:
   F.box('nik-edge-paint',(u,2.52,-.13),(.27,.47,.18))
   F.lathe('nik-edge-paint',u,-.05,[(3.08,.07),(3.15,.09),(3.24,.035),(3.3,0)],10)
 # Roof seam and discreet service door on west side.
 a,b=list(p.exterior.coords)[:2];F,L,_,_=facade_frame(B,a,b,p,.04);F.y=D
 F.box('nik-dark-paint',(L/2,1.03,-.13),(.79,1.93,.08))
 F.box('nik-edge-paint',(L/2,1.03,-.19),(.69,1.83,.04))
 F.box('nik-handle-paint',(L/2+.23,1,-.23),(.04,.18,.045))
 # Local pavement only where the current city has no supporting surface.
 apron=box(-52.5,1549,-34,1573);covered=[p.buffer(.015)]
 for g in json.loads(Path('build/geographic-strip/city-meshes.json').read_text()):
  if not g['faces']:continue
  q=np.asarray(g['vertices'])[np.asarray(g['faces'])];xs=q[:,:,0];zs=q[:,:,2];ys=q[:,:,1];a=apron.bounds
  mask=(xs.max(1)>a[0])&(xs.min(1)<a[2])&(zs.max(1)>a[1])&(zs.min(1)<a[3])&(ys.max(1)<.6)&(ys.min(1)>-.1)
  for t in q[mask]:
   poly=Polygon(t[:,[0,2]])
   if poly.area>.001:covered.append(poly.intersection(apron).buffer(.015))
 paving=apron.difference(unary_union(covered));B.planar('nik-floor-concrete',paving,D,True)
 # Some retained city pavement is visual-only. Supply its missing collision,
 # subtracting any actual existing near-ground collider triangles first.
 physical=[]
 for c in json.loads(Path('build/geographic-strip/city-colliders.json').read_text()):
  if not c['indices']:continue
  q=np.asarray(c['vertices']).reshape(-1,3)[np.asarray(c['indices']).reshape(-1,3)];xs=q[:,:,0];zs=q[:,:,2];ys=q[:,:,1];a=apron.bounds
  mask=(xs.max(1)>a[0])&(xs.min(1)<a[2])&(zs.max(1)>a[1])&(zs.min(1)<a[3])&(ys.max(1)<.6)&(ys.min(1)>-.1)
  for t in q[mask]:
   poly=Polygon(t[:,[0,2]])
   if poly.area>.001:physical.append(poly.intersection(apron))
 missing=apron.difference(p.buffer(.015)).difference(paving).difference(unary_union(physical))
 B.planar('nik-collision-only',missing,D,True)
 for k in list(B.groups):
  if B.groups[k]['material']=='nik-collision-only':del B.groups[k]
 samples=[[x,3.55,z]for x in np.arange(p.bounds[0],p.bounds[2],.35)for z in np.arange(p.bounds[1],p.bounds[3],.35)if p.buffer(-.1).contains(Point(x,z))]
 routes=[]
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  F,L,_,_=facade_frame(B,a,b,p,.04);F.y=D
  routes.append([F.p(.3,0,-1.05),F.p(L-.3,0,-1.05)])
 Path('build/city-exteriors/nyny-irish-kiosk-samples.json').write_text(json.dumps(samples));Path('build/city-exteriors/nyny-irish-kiosk-stairs.json').write_text(json.dumps(routes))
 return dict(key=KEY,name='NYNY Irish outdoor kiosk',center=[p.centroid.x,0,p.centroid.y],bounds=[-52.5,1549,-34,1573],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
