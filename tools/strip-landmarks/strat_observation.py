"""STRAT concrete tripod and glazed pod; reference dimensions in strat.json.
Pod elevations 236–280m, observation264m and mast350m are documented.
Cross-sections and glazing subdivision remain photo estimates.
"""
from common import *
def observation(B):
 B.source='strat-observation';B.detail=0
 cx,cz=footprint('way/135457469').centroid.coords[0]
 def pt(a,r,y):return (cx+r*math.cos(a),y,cz+r*math.sin(a))
 # Hexagonal core and three tapered concrete legs. Open slots at the base and
 # below the pod are real voids, not dark decals on a cylinder.
 core=Polygon([(cx+6.1*math.cos(a),cz+6.1*math.sin(a)) for a in np.linspace(0,math.tau,6,endpoint=False)])
 B.shell(core,.24,239,'st-white',roof=False)
 for a in [math.pi/6,math.pi/6+math.tau/3,math.pi/6+2*math.tau/3]:
  stations=[(.24,23,3.7,3.7),(18,21,3.5,3.7),(73,7.1,3.0,3.4),(165,7.0,2.8,3.2),(213,11,3.0,3.2),(236,18,3.4,3.3)]
  rings=[]
  for y,r,depth,width in stations:
   rings.append([(cx+(r+u)*math.cos(a)-v*math.sin(a),y,cz+(r+u)*math.sin(a)+v*math.cos(a)) for u,v in [(-depth,-width),(depth,-width),(depth,width),(-depth,width)]])
  for lo,hi in zip(rings,rings[1:]):
   for i in range(4):B.face('st-white',[lo[i],lo[(i+1)%4],hi[(i+1)%4],hi[i]],True)
  # Small structural ties at the high opening, leaving the slot legible.
  for y,r in [(221,13.4),(229,15.9)]:B.tube('st-grey',pt(a,6,y),pt(a,r,y),.23,8)
 # Pod profile is an outward splayed enclosure, with distinct restaurant and
 # observation window bands; the earlier closed cone inverted this silhouette.
 profile=[(236,17.8),(241,20.0),(245,23.5),(250,26.2),(256,29.0),(261,31.1),(265.4,32.2),(267,32.2),(268,30.5)]
 for (y,r),(yy,rr) in zip(profile,profile[1:]):
  mat='st-glass' if 245<=y<265.4 else 'st-grey'
  B.lathe(mat,(cx,cz),[(y,r),(yy,rr)],96)
  B.lathe('st-white',(cx,cz),[(y,r+.12),(y+.24,r+.22)],96)
 for a in np.linspace(0,math.tau,96,endpoint=False):
  for (y,r),(yy,rr) in zip(profile[2:7],profile[3:8]):B.tube('st-sill',pt(a,r+.15,y),pt(a,rr+.15,yy),.075,5)
 # Open upper observation ring and tapered equipment roof.
 deck=Point(cx,cz).buffer(30.5,resolution=48)
 B.planar('st-roof',deck,268,True)
 for a in np.linspace(0,math.tau,144,endpoint=False):B.tube('st-sill',pt(a,30.3,268),pt(a,30.3,270.1),.055,5)
 B.lathe('st-sill',(cx,cz),[(269.9,30.3),(270.1,30.3)],144)
 B.lathe('st-white',(cx,cz),[(268.15,24.5),(276,15),(280,10),(280,0)],96)
 for a in np.linspace(0,math.tau,48,endpoint=False):B.tube('st-grey',pt(a,24.55,268.2),pt(a,10.05,280),.065,5)
 # Open lattice Big Shot mast, rather than a solid needle.
 for y in np.arange(280,350,3.5):
  yy=min(350,y+3.5);r=2.7-(y-280)*.028;rr=2.7-(yy-280)*.028
  for a in np.linspace(0,math.tau,4,endpoint=False):
   b=a+math.pi/2
   B.tube('st-white',pt(a,r,y),pt(a,rr,yy),.16,6)
   B.tube('st-red',pt(a,r,y),pt(b,r,y),.085,5)
   B.tube('st-red',pt(a,r,y),pt(b,rr,yy),.065,5)
 # Lower circular arrival enclosure, split into glazing and pale spandrels.
 B.lathe('st-glass',(cx,cz),[(2,25.2),(13,24)],96)
 for y in [2,5.6,9.2,13]:B.lathe('st-white',(cx,cz),[(y,25.6-(y-2)*.1),(y+.35,25.6-(y-2)*.1)],96)
 for a in np.linspace(0,math.tau,64,endpoint=False):B.tube('st-sill',pt(a,25.3,2),pt(a,24.1,13),.07,5)
 B.planar('st-roof',Point(cx,cz).buffer(24,resolution=32).difference(core),13.4,True)

 # Detailed static ride assemblies share this tower owner.
 from strat_thrill_rides import rides
 rides(B,cx,cz)
