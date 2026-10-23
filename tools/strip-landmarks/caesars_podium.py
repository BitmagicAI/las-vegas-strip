"""Mapped low-rise casino envelope and OMNIA roof/frontage.
Earth 2022 topdown/east oblique and Caesars2024 property map. Roof heights and
architectural sections estimated. Retain original interiors, doors and guest core.
"""
from common import *
from forum_shops import facade_frame
from caesars_colosseum import CX,CZ,R

def exterior(B,ids,low):
 B.source='caesars-podium';B.detail=0
 original=footprint('way/115672893')
 towers=unary_union([footprint(i) for i in ids]);owned=unary_union([footprint(i) for i in low]+[Point(CX,CZ).buffer(R+.1,resolution=64)])
 p=original.difference(owned).buffer(0)
 # The occupied legacy casino/gallery remain independent and untouched. Exterior
 # shell apertures retain their currently used approach, pending full real-plan
 # interior reconstruction. They are access compromises, not surveyed door data.
 portals=[dict(p=[-119,0,-17],yaw=-math.pi/2,width=66,height=9.1),dict(p=[-106,0,-81],yaw=-math.pi/2,width=18,height=8.5),dict(p=[-77,0,-127],yaw=-math.pi/2,width=12,height=6.8),dict(p=[-129,0,72],yaw=-math.pi/2,width=9,height=5.5)]
 old=unary_union([box(-355,-135,-162,-6),box(-419,-75,-342,-2)])
 # Lower base roof and stepped nightclub block. Do not cap occupied tower rooms.
 omnia=p.intersection(box(-154,-175,-76,-96));arrival=p.intersection(box(-155,-45,-108,43));rest=p.difference(omnia.union(arrival))
 core=box(-285.25,-85.8,-274.75,-78.2)
 regions=[(rest,12.4),(omnia,14.4),(arrival,8.2)]
 for k,(region,h) in enumerate(regions):
  B.source='caesars-podium-roof-'+str(k)
  roof=region.difference(towers.buffer(.05)).difference(core).difference(footprint('way/1168129083'))
  B.planar('cp-flat-roof',roof,h,True)
  # Elevated roof tier closures only, above public walking clearance.
  if k in (1,2):
   lo,hi=(12.4,14.4) if k==1 else (8.2,12.4)
   # Only internal tier edges get this closure; external edges have their own
   # facade below. Closing the entire region made a floating arrival fascia.
   for edge in parts(region.boundary.difference(p.boundary.buffer(.05)),'LineString'):
    for a,b in zip(list(edge.coords),list(edge.coords)[1:]):
     B.face('cp-white',[(a[0],lo,a[1]),(b[0],lo,b[1]),(b[0],hi,b[1]),(a[0],hi,a[1])],True)
  B.detail=1
  for x in np.arange(region.bounds[0]+6,region.bounds[2]-4,14):
   for z in np.arange(region.bounds[1]+6,region.bounds[3]-4,16):
    if roof.buffer(-4).contains(Point(x,z)) and not (-150<x<-80 and -150<z<-55):
     B.box('cp-service',(x,h+.6,z),(3.1,1.2,2.2));B.box('cp-shadow',(x,h+1.21,z),(2.85,.045,2))
  B.detail=0
 # Only the actual external perimeter gets facade walls, never internal tier cuts.
 for poly in parts(original):
  ps=list(poly.exterior.coords)
  for a,b in zip(ps,ps[1:]):
   line=LineString([a,b]);L=line.length
   if L<.3 or line.intersection(owned.buffer(.15)).length>L*.5:continue
   mid=line.interpolate(.5,normalized=True)
   if towers.buffer(.2).contains(mid):continue
   h=14.4 if omnia.buffer(.1).contains(mid) else 8.2 if arrival.buffer(.1).contains(mid) else 12.4
   F,_,nx,nz=facade_frame(B,a,b,original,.04)
   # Cut public openings and preserved interior intersections geometrically.
   wall=box(0,.05,L,h)
   masks=[old]+[Frame(B,o['p'][0],o['p'][2],o['yaw']).poly([(-o['width']/2,-5),(o['width']/2,-5),(o['width']/2,5),(-o['width']/2,5)]) for o in portals]
   heights=[9.5]+[o['height'] for o in portals]
   for mask,head in zip(masks,heights):
    for seg in parts(line.intersection(mask),'LineString'):
     ds=[line.project(Point(q)) for q in seg.coords];wall=wall.difference(box(min(ds)-.02,0,max(ds)+.02,head))
   ux,uz=(b[0]-a[0])/L,(b[1]-a[1])/L
   for part in parts(wall):
    for t in triangles(part):B.face('cp-white',[(a[0]+ux*x,y,a[1]+uz*x) for x,y in list(t.exterior.coords)[:-1]],True)
   # Upper entablature is continuous; no low trim through doorways.
   for yy,hh,dep in [(h-.7,.55,.5),(h-.25,.25,.75),(h+.15,.24,.95)]:F.box('cp-white',(L/2,yy,-dep/2),(L,hh,dep))
   # Blind Roman bays on street faces, restrained service piers elsewhere.
   count=max(1,round(L/5.8));step=L/count
   for j in range(count):
    x=(j+.5)*step;pt=line.interpolate(x)
    if any(mask.buffer(.6).contains(pt) for mask in masks):continue
    if L<3:continue
    width=min(step-1.25,4.5)
    if width<1:continue
    F.box('cp-colosseum-recess',(x,h*.43,-.11),(width,h*.56,.16))
    F.box('cp-white',(x,h*.43,-.22),(width-.30,h*.56-.30,.10))
    for xx in [x-step/2+.2,x+step/2-.2]:
     F.box('cp-white',(xx,h*.46,-.28),(.4,h*.9,.6));F.box('cp-white',(xx,h*.9,-.34),(.72,.30,.8))
    for yy in [.7,h*.72]:F.box('cp-white',(x,yy,-.28),(width+.4,.3,.6))
 # Mapped crescent porte-cochere: the survey's building=roof must not be
 # extruded down to ground. 8.2 m roof/7.65 m soffit is an estimated clearance.
 B.source='caesars-arrival-canopy';canopy=footprint('way/1168129083')
 B.planar('cp-flat-roof',canopy,8.2,True)
 for part in parts(canopy):
  for t in triangles(part):B.face('cp-white',[(x,7.65,z) for x,z in reversed(list(t.exterior.coords)[:-1])])
 B.shell(canopy,7.65,8.2,'cp-white',roof=False,solid=True)
 # Fluted columns on the two ends of the crescent keep the middle drive clear.
 for x,z in [(-130,-39),(-139,-39),(-140,3),(-130,3)]:
  from caesars_poolcourt import column
  column(B,x,z,0,7.65,.6)
 # OMNIA circular drum and ribbed dome, fitted to the rooftop in Earth topdown.
 B.source='caesars-omnia';x,z,r=-108,-134,11.5;base=14.4
 B.lathe('cp-white',(x,z),[(base,r),(base+3.4,r),(base+3.7,r+.25)],96)
 B.lathe('cp-white',(x,z),[(base+3.7+4.6*math.sin(t),r*math.cos(t)) for t in np.linspace(0,math.pi/2,25)],96)
 for a in np.linspace(0,math.tau,24,endpoint=False):
  B.path('cp-colosseum-recess',[(x+(r+.04)*math.cos(t)*math.cos(a),base+3.74+4.6*math.sin(t),z+(r+.04)*math.cos(t)*math.sin(a)) for t in np.linspace(0,math.pi/2,18)],.025,6)
 F=Frame(B,-76.58,-127,-math.pi/2,y=0)
 for side in [-1,1]:F.box('cp-white',(side*7,7.2,0),(1.6,14.4,1.2),True)
 F.box('cp-white',(0,12.1,0),(15.6,4.6,1.0));F.box('cp-shadow',(0,11.9,-.58),(8.6,3.3,.14));F.text('OMNIA',(0,11.9,-.72),1.15,'cp-white')
 # Red-roof pavilion adjacent to arrival: hip planes, not an extruded flat box.
 F=Frame(B,-121,-78,math.radians(-19),y=12.4);w,d=33,20
 for coords in [[(-w/2,0,-d/2),(w/2,0,-d/2),(w/2-4,4,0),(-w/2+4,4,0)],[(w/2,0,-d/2),(w/2,0,d/2),(w/2-4,4,0)],[(w/2,0,d/2),(-w/2,0,d/2),(-w/2+4,4,0),(w/2-4,4,0)],[(-w/2,0,d/2),(-w/2,0,-d/2),(-w/2+4,4,0)]]:B.face('cp-tile',[F.p(*q) for q in coords])
 for zz in [-d/2,d/2]:F.box('cp-white',(0,.03,zz),(w+.5,.36,.55))
 # Pad only the new exterior envelope; preserve every original interior floor.
 B.source='caesars-podium-floor';B.planar('cp-deck',p.difference(old).difference(towers),.025,True)
 report={'footprint':'way/115672893','roofEstimatesM':[12.4,14.4,8.2],'omniaDomeCenter':[x,z],'omniaDomeRadiusM':r,'newAccessApertures':portals,'remaining':['Public interior plan not reconstructed: legacy interior preserved','Main arrival canopy elevation estimated; glazing and onward public hall still incomplete','Full roof-to-pool circulation unverified','OMNIA 2026 dayclub not included; this envelope follows 2022 imagery']}
 (Path('build/city-exteriors')/'caesars-podium-plan.json').write_text(json.dumps(report,indent=2))
