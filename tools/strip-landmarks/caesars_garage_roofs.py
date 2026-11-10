"""Two mapped parking decks; original markings/details from aerial observations.
Existing23m datum retained; stall pitch and equipment placement are inferred.
"""
from common import *
IDS=['way/134949710','way/134949713']
Y=23.
def roofs(B):
 B.property='caesarsGarageRoofs-exterior';B.detail=0
 counts=[]
 for index,ident in enumerate(IDS):
  B.source='garage-roof/'+ident;p=footprint(ident);safe=p.buffer(-1.2)
  B.planar('cgr-west-concrete' if index==0 else 'cgr-east-concrete',p,Y)
  houses=[(-529,-194,15,13),(-488,-151,20,5)]if index==0 else [(-304,-193,13,11)]
  plant=box(-603,-207,-574,-173)if index==0 else Polygon()
  blocked=unary_union([plant.buffer(2),*[box(x-w/2-1,z-d/2-1,x+w/2+1,z+d/2+1)for x,z,w,d in houses]])
  parking=safe.difference(blocked);stripes=0
  def line(a,b,width=.12):
   nonlocal stripes
   q=LineString([a,b]).buffer(width/2,cap_style=2).intersection(parking)
   if not q.is_empty:B.planar('cgr-line-paint',q,Y+.025);stripes+=1
  left,right=p.bounds[0]+4,p.bounds[2]-4
  if index==0:left=-562
  for center in [-230,-212,-194,-176,-158]:
   for side in [-1,1]:
    for xx in np.arange(left,right,2.8):line((xx,center),(xx+side*2.2,center+side*5.2))
   line((left,center),(right,center))
  # Roof housings preserve inferred footprint, without inventing accessible stairs.
  for x,z,w,d in houses:
   q=box(x-w/2,z-d/2,x+w/2,z+d/2)
   if not safe.covers(q):continue
   B.box('cgr-service-paint',(x,Y+1.7,z),(w,3.4,d),True)
   B.box('cgr-cap-paint',(x,Y+3.45,z),(w+.3,.16,d+.3))
   for xx in np.arange(x-w/2+.7,x+w/2-.5,1.5):
    B.box('cgr-vent-paint',(xx,Y+2,z-d/2-.025),(1.1,1.3,.05))
    for yy in np.arange(Y+1.45,Y+2.6,.18):B.box('cgr-metal-paint',(xx,yy,z-d/2-.065),(1.15,.035,.06))
  # Western mechanical bank observed aerially; only original simplified volumes.
  if index==0:
   for x in [-596,-582]:
    for z in [-200,-185]:
     B.box('cgr-metal-paint',(x,Y+.28,z),(9,.56,11),True)
     B.box('cgr-service-paint',(x,Y+1.55,z),(8,2.1,9),True)
     for zz in [z-2.4,z+2.4]:
      B.lathe('cgr-vent-paint',(x,zz),[(Y+2.62,1.7),(Y+2.68,1.7)],16)
      B.planar('cgr-vent-paint',Point(x,zz).buffer(1.65,resolution=8),Y+2.69)
      for a in np.linspace(0,math.tau,8,endpoint=False):B.tube('cgr-metal-paint',(x,Y+2.7,zz),(x+1.55*math.cos(a),Y+2.7,zz+1.55*math.sin(a)),.04,4)
  # Static fixtures only; no runtime light or shader changes.
  poles=[(-553,-220),(-472,-220),(-553,-166),(-440,-182)]if index==0 else [(-395,-220),(-324,-220),(-395,-164),(-324,-164)]
  for x,z in poles:
   if not safe.covers(Point(x,z)):continue
   B.box('cgr-cap-paint',(x,Y+.2,z),(.7,.4,.7),True)
   B.box('cgr-metal-paint',(x,Y+3.5,z),(.14,7,.14),True)
   B.box('cgr-metal-paint',(x,Y+7,z),(1.5,.14,.16))
   for dx in [-.55,.55]:B.box('cgr-fixture-paint',(x+dx,Y+6.92,z),(.45,.18,.6))
  counts.append({'id':ident,'stripeSegments':stripes,'roofM':Y})
 return {'decks':counts,'inferred':'2.8m stall pitch,5.2m depth,diagonal orientation,row spacing,roof housings and mechanical details estimated from aerial. Existing23m datum retained. No ground-to-roof route claim.'}
if __name__=='__main__':
 B=Meshes();meta=roofs(B);B.save_all();Path('build/city-exteriors/caesars-garage-geometry.json').write_text(json.dumps(meta,indent=2));print(sum(len(g['faces'])for g in B.groups.values()),'triangles')
