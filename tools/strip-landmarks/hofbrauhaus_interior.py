"""Reference-supported public room character; connecting layout is explicitly inferred.

Official hall/garden photographs establish finishes and furniture, not a measured
floorplan. Fit both rooms within the mapped envelope; do not invent private rooms.
"""
from common import *
from hofbrauhaus import KEY,YAW,ID,window

def interior(B,meta):
 B.property=KEY+'-interior';B.source='public/hofbrauhaus';B.detail=0
 F=Frame(B,1922.741,969.671,YAW,y=0)
 p=footprint(ID).buffer(-.16)
 # Inward wall faces, retained inside opaque exterior glazing.
 B.shell(p,.18,10.7,'hb-cream',openings=meta['portals'],roof=False,solid=False)
 B.planar('hb-floor',p,.19)
 # Southern indoor garden; northern vaulted beer hall. Connection is an
 # interpretation, not a claim of surveyed public circulation.
 for lo,hi in [(.2,4.4),(10,27.5)]:F.box('hb-cream',(29,4.1,(lo+hi)/2),(.24,7.8,hi-lo),True)
 P=Frame(B,*F.p(29,0,7.2)[::2],YAW+math.pi/2,y=0)
 P.arch(0,0,5.6,5.5,'hb-stone',.16,.18)
 # Interior window reveals mirror the street elevations, rather than blank walls.
 G=Frame(B,1922.741,969.671,YAW,y=0)
 for u in [34,41,48]:
  # Window helper faces outward; positive inset places its backing indoors.
  window(G,u,.7,4,5.6,True,depth=.22)
 for u in [4,9,14,24,57]:window(G,u,.4,2.65,3.65,True,depth=.22)
 for u in [7,15,23,34,42,50,57]:
  # Original framed Bavarian colour panels, no copied murals.
  F.box('hb-darkwood',(u,3.2,26), (1.65,1.35,.08))
  F.box('hb-blue',(u,3.2,25.95), (1.4,1.1,.04))
  F.text('HB',(u,3.25,25.90),.5,'hb-stone')
 # Three shallow barrel vaults across hall width, with real intrados faces.
 for v0 in [1,10,19]:
  for u0 in [31,38,45,52]:
   for j in range(20):
    a=j*math.pi/20;b=(j+1)*math.pi/20
    vs=[v0+4.5-4.5*math.cos(t) for t in [a,b]]
    ys=[7.2+2.9*math.sin(t) for t in [a,b]]
    B.face('hb-vault',[F.p(u0,ys[0],vs[0]),F.p(u0+7,ys[0],vs[0]),F.p(u0+7,ys[1],vs[1]),F.p(u0,ys[1],vs[1])])
   F.path('hb-stone',[(u0,7.15+2.9*math.sin(a),v0+4.5-4.5*math.cos(a)) for a in np.linspace(0,math.pi,25)],.09)
 for u in [31,38,45,52,59]:
  for v in [10,19]:
   F.box('hb-cream',(u,3.7,v),(.55,7,.55),True)
   F.box('hb-oak',(u,1.15,v),(.67,1.9,.67))
   F.box('hb-stone',(u,7.15,v),(.95,.25,.95))
 # A continuous clear aisle at v=7.2 links the entrance and both rooms.
 def table(u,v,length=4.4,garden=False):
  mat='hb-darkwood' if garden else 'hb-oak'
  for k in range(5):F.box(mat,(u,.97,v+(k-2)*.17),(length,.07,.16))
  for du in [-length*.35,length*.35]:
   F.box('hb-iron',(u+du,.56,v),(.10,.76,.65))
   F.box('hb-iron',(u+du,.22,v),(.14,.08,.95))
  # One coarse seating collider per bench, no chair-leg bodies.
  for side in [-1,1]:
   F.box(mat,(u,.57,v+side*.9),(length,.10,.36),True)
   F.box(mat,(u,1.03,v+side*1.08),(length,.42,.07))
   for du in [-length*.35,length*.35]:F.box('hb-iron',(u+du,.37,v+side*.9),(.09,.4,.3))
  for du in [-1,1]:
   F.lathe('hb-cream',u+du,v,[(1.01,.05),(1.22,.045)],8)
 for u in [34.5,41.5,48.5,55.5]:
  for v in [3.4,13.5,23]:table(u,v)
 # Oak bar and shelves at the rear, outside the dining circulation.
 F.box('hb-oak',(44,1,29),(20,1.6,.85),True)
 F.box('hb-darkwood',(44,1.85,29),(20.3,.14,1.15))
 for y in [1,1.9,2.8,3.7]:F.box('hb-oak',(44,y,31),(19,.10,.48))
 for u in np.arange(35,54,.45):
  F.lathe('hb-bottle',u,31,[(2,.055),(2.25,.055),(2.32,.026),(2.42,.026)],8)
 # Indoor garden sky ceiling, fountain and original chestnut-like leaf clusters.
 B.planar('hb-sky',F.poly([(1,1),(28,1),(28,25),(1,25)]),7.6)
 for u in [6,13,23]:
  for v in [11.5,17]:
   if u==13 and v==17:continue
   table(u,v,3.0,True)
 F.lathe('hb-stone',14,20,[(.2,1.6),(.45,1.6),(.6,1.4)],32)
 F.lathe('hb-stone',14,20,[(.45,.34),(2.6,.25),(2.8,.65),(2.95,.2)],20)
 B.planar('hb_pool',Point(F.p(14,0,20)[::2]).buffer(1.35),.52)
 # Suspended iron lanterns, not point lights per fixture.
 for u in [8,20,34,43,53]:
  for v in [7,17]:
   F.tube('hb-iron',(u,7.5,v),(u,5.7,v),.022,6)
   F.box('hb-lamp',(u,5.4,v),(.34,.5,.34))
   for du in [-.19,.19]:
    for dv in [-.19,.19]:F.box('hb-iron',(u+du,5.4,v+dv),(.025,.6,.025))
   F.box('hb-iron',(u,5.72,v),(.5,.08,.5))
 for u,v in [(13,12),(23,20),(40,10),(53,22)]:F.light(u,5.2,v,power=220,range=21)
 meta['lights']=B.lights
 meta['routes']=[dict(name='Street to garden and hall',points=[F.p(u,.2,v) for u,v in [(19,-1.5),(19,2),(19,7.2),(29,7.2),(54,7.2)]])]
 meta['views']={'entrance':dict(eye=F.p(19,2,-5),target=F.p(19,2,8)), 'hall':dict(eye=F.p(32,2,7.2),target=F.p(54,4,15)), 'garden':dict(eye=F.p(20,2,5),target=F.p(12,3,19))}
 return meta
