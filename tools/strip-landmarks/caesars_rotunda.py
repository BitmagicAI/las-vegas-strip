"""Roadside Caesars drum and fountain, OSM plan + Earth 2022-11-09 elevations.
No photograph-derived texture copied. Vertical dimensions estimated, not surveyed.
"""
from common import *
from forum_shops import arch_panel
ID='way/180831020'
def exterior(B):
 B.source='caesars-roadside-rotunda';B.detail=0
 p=footprint(ID);cx,cz=p.centroid.x,p.centroid.y;r=8.55;roof=8.7
 p=Point(cx,cz).buffer(math.sqrt(p.area/math.pi),resolution=64)
 # Closed drum with ornamental niches, not a fabricated open pavilion/interior.
 B.shell(p,.15,roof-.65,'cp-white',roof=False)
 B.planar('stone',p,.15,True)
 B.planar('cp-flat-roof',Point(cx,cz).buffer(r+.38,resolution=64),roof,True)
 B.lathe('cp-white',(cx,cz),[(.15,r+.2),(.42,r+.2),(.56,r),(.75,r)],128)
 B.lathe('cp-white',(cx,cz),[(7.55,r),(7.7,r+.18),(7.82,r+.18),(8.02,r+.35),(8.32,r+.35),(8.46,r+.52),(8.62,r+.52),(8.7,r+.36)],128)
 # Local shell cylinder is recessed inside mapped outline; surface detail has clear depth.
 for j in range(18):
  a=(j+.5)*math.tau/18;nx,nz=math.cos(a),math.sin(a)
  F=Frame(B,cx+nx*(r+.22),cz+nz*(r+.22),math.atan2(-nx,-nz),y=0)
  arch_panel(F,0,.75,-.04,1.8,5.8,'cp-shadow')
  for side in [-1,1]:
   F.lathe('cp-white',side*1.02,-.20,[(.65,.24),(.85,.24),(1.05,.16),(5.4,.13),(5.55,.22),(5.8,.22)],16)
  F.box('cp-stone',(0,.66,-.15),(2.35,.16,.28))
  # Round frieze medallions visibly alternate with the niches.
  F.path('cp-stone',[(.72*math.cos(t),6.99+.31*math.sin(t),-.1) for t in np.linspace(0,math.tau,25)],.08,6)
 for j in range(144):
  a=j*math.tau/144;F=Frame(B,cx+(r+.27)*math.cos(a),cz+(r+.27)*math.sin(a),-a+math.pi/2,y=0)
  F.box('cp-white',(0,8.12,0),(.17,.2,.25))
 # Three-bay rose-stone fountain front with curved white cornice and basin.
 F=Frame(B,cx+r-.6,cz,-math.pi/2,y=0)
 F.box('cp-stone',(0,.22,-1.5),(8.8,.44,3.8),True)
 for x in [-2.9,0,2.9]:
  F.box('venetian-burgundy',(x,3.1,-.5),(2.65,5.75,.55),True)
  arch_panel(F,x,.7,-.82,1.85,4.8,'cp-shadow')
  for side in [-1,1]:
   F.lathe('cp-white',x+side*1.04,-.95,[(.55,.28),(.85,.28),(1.0,.18),(4.8,.15),(5.0,.26),(5.25,.26)],20)
  F.box('cp-white',(x,5.25,-.7),(2.85,.32,.85))
  F.arch(x,-.8,2.4,6.7,'cp-white',.22,5.25)
 # Basin and coping extend toward the existing roadside walk, not into the road.
 basin=F.poly([(-4.6,-1.2),(4.6,-1.2),(4.6,-3.3),(3.0,-4.2),(-3.0,-4.2),(-4.6,-3.3)])
 B.shell(basin,.15,.75,'cp-stone',roof=False)
 B.planar('cp-white',basin.difference(basin.buffer(-.22)),.75,True)
 B.planar('cp_pool',basin.buffer(-.24),.43)
 B.planar('cp-shadow',basin.buffer(-.24),.18,True)
 F.lathe('cp-white',0,-2.6,[(.45,1.02),(.7,1.02),(.8,.68),(1.1,.45),(1.2,.9),(1.38,.9)],48)
 # Relief sculpture and dioramas require a separate authored asset; not approximated by people primitives.
 return dict(id=ID,center=[cx,cz],roofM=roof,roofHeightSource='Estimated from Earth oblique; OSM5m was generic',remaining=['Detailed fountain sculpture and niche dioramas','Exact decorative profile and medallions','Current2026 survival to be corroborated; Earth reference2022'])
