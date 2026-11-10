"""Original pool furniture/pergola study from Boyd photos and Google aerial.
Counts and dimensions inferred; preserve existing pool, buildings and arrival routes.
"""
from common import *
RECORD=Path('docs/project-records/west-resort-amenities')
Y=.25

def build(B):
 B.source='gold-coast/pool-furnishings'
 deck=box(-1904,-132,-1852,-106)
 water=box(-1885,-123,-1870,-113).buffer(2,quad_segs=12)
 # North-side shaded structure: open brown rafters on pale square masonry columns.
 shade=box(-1886,-131.3,-1877,-126.5)
 obstacles=[]
 for x in [-1885.65,-1877.35]:
  for z in [-130.95,-126.85]:
   B.box('gca-column',(x,Y+1.5,z),(.48,3,.48),True)
   B.box('gca-column',(x,Y+.18,z),(.7,.36,.7),True)
   B.box('gca-column',(x,Y+2.88,z),(.7,.22,.7))
   obstacles.append(box(x-.36,z-.36,x+.36,z+.36))
 for z in [-131,-126.8]:B.box('gca-wood',(-1881.5,Y+3.13,z),(9.8,.3,.23),True)
 for x in np.arange(-1886.15,-1876.8,.48):B.box('gca-wood',(x,Y+3.38,-128.9),(.12,.26,5.5))
 # White strap chaises on dark tubular frames, without collider-per-strap/leg.
 chairs=[(x,-128.5,0) for x in [-1873.5,-1871.5,-1869.5,-1867.5,-1865.5,-1863.5]]
 chairs += [(-1857.7,z,math.pi/2) for z in [-122,-119.5,-117,-114.5]]
 for x,z,angle in chairs:
  F=Frame(B,x,z,angle,y=Y)
  envelope=rotate(box(-.43,-1.05,.43,1.05),-angle*180/math.pi,origin=(0,0));envelope=translate(envelope,xoff=x,yoff=z)
  assert deck.contains(envelope) and not water.buffer(.6).intersects(envelope)
  obstacles.append(envelope)
  F.box('gca-frame',(0,.27,0),(.77,.12,1.94),True)
  for dx in [-.38,.38]:
   F.tube('gca-frame',(dx,.39,-.42),(dx,.39,.98),.022,6)
   F.tube('gca-frame',(dx,.39,-.42),(dx,.94,-.98),.022,6)
   for dz in [-.65,.65]:F.tube('gca-frame',(dx,.04,dz),(dx,.32,dz),.025,6)
  for dz in np.arange(-.35,.94,.14):F.box('gca-strap',(0,.41,dz),(.72,.025,.09))
  for t in np.arange(.05,.96,.14):
   a=-.42-.56*t;b=a-.05
   B.face('gca-strap',[F.p(-.36,.41+.55*t,a),F.p(.36,.41+.55*t,a),F.p(.36,.46+.55*t,b),F.p(-.36,.46+.55*t,b)])
 # Continuous external deck route avoids water, furniture and pergola supports.
 route=LineString([(-1852.5,-108),(-1896,-108),(-1896,-128.9),(-1889,-128.9),(-1881.5,-128.9)])
 assert deck.covers(route.buffer(.35))
 assert not route.buffer(.35).intersects(water.buffer(.5))
 assert all(not route.buffer(.35).intersects(p) for p in obstacles)
 report={'chairs':len(chairs),'pergolaBounds':list(shade.bounds),'pergolaClearanceM':3,'route':[[x,Y,z] for x,z in route.coords],'scope':'Furniture and pergola only; all counts/dimensions inferred. Existing rounded pool differs from lobed reference. Spa, steps, rock feature, palms and indoor breezeway connection remain unimplemented. No complete-site claim.'}
 RECORD.mkdir(exist_ok=True,parents=True);(RECORD/'gold-amenity-geometry.json').write_text(json.dumps(report,indent=2)+'\n')
 return report
