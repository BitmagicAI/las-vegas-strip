"""Mirage-era lagoon footprint estimated from 2022 overhead Earth imagery.
Keep county street/sidewalk masks authoritative; these are not survey dimensions.
"""
from common import *
from shapely.geometry import shape

def lagoon(B):
 B.source='podium/way/1468774558'
 layers=json.load(open('build/geographic-strip/surface-layers.geojson'))['features']
 blocked=unary_union([shape(f['geometry']).buffer(.8) for f in layers if f['properties']['kind'] in ['road','sidewalk']])
 # Long north/south water garden between the bowed arrival drive and boulevard.
 outline=Polygon([(-5,-693),(43,-690),(37,-665),(28,-632),(18,-601),(13,-574),(4,-546),(-5,-512),(-13,-490),(-30,-494),(-38,-518),(-32,-547),(-42,-564),(-48,-587),(-36,-613),(-25,-638),(-20,-668)]).buffer(3).buffer(-3)
 # Arrival carriageway is an authored site surface, separate from city streets.
 knots=[(-12,-486),(-38,-522),(-47,-555),(-43,-587),(-39,-616),(-20,-653),(30,-695)]
 pts=np.array([knots[0],*knots,knots[-1]],float);samples=[]
 for i in range(1,len(pts)-2):
  a,b,c,d=pts[i-1:i+3]
  for t in np.linspace(0,1,30):samples.append(.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t))
 drive=LineString(samples).buffer(5.5)
 B.planar('mi-drive',drive.difference(blocked),.08,True)
 garden=outline.difference(blocked.union(drive.buffer(1)))
 water=garden.buffer(-2).difference(Point(-16,-635).buffer(22)).difference(Point(-20,-517).buffer(10))
 B.planar('mi-garden',garden,.12,True)
 B.planar('water',water,.23)
 B.planar('mi-rock',water.buffer(1.2).difference(water),.27,True)
 # Rough elliptical crater with open bowl; no solid cone in the water.
 cx,cz=-7,-591
 rings=[(14,.3),(13,2),(11,5),(8,8),(6.8,8.4),(5.6,6.2),(4,5.7)]
 rng=random.Random(241)
 noise=[[rng.uniform(-1.4,1.4) for _ in range(48)] for _ in rings]
 for k,((r,y),(rr,yy)) in enumerate(zip(rings,rings[1:])):
  for j in range(48):
   a,b=j*math.tau/48,(j+1)*math.tau/48
   def pt(t,i,rad,h,level):
    n=noise[level][i%48];return(cx+(rad+n)*math.cos(t),h+n*.42,cz+(rad+n)*math.sin(t))
   B.face('mi-rock' if rng.random()<.75 else 'mi-rock-light',[pt(a,j,r,y,k),pt(b,j+1,r,y,k),pt(b,j+1,rr,yy,k+1),pt(a,j,rr,yy,k+1)],True)
 B.planar('mi-rock',Point(cx,cz).buffer(4),5.7,True)
