"""Original site signage, positioned from aerial/photo estimates (not a survey)."""
from common import *
def site(B):
 def prism(F,mat,profile,depth):
  p=Polygon(profile)
  for t in triangles(p):
   points=list(t.exterior.coords)[:-1]
   B.face(mat,[F.p(x,y,-depth/2) for x,y in points])
   B.face(mat,[F.p(x,y,depth/2) for x,y in reversed(points)])
  for a,b in zip(profile,profile[1:]+profile[:1]):B.face(mat,[F.p(a[0],a[1],-depth/2),F.p(b[0],b[1],-depth/2),F.p(b[0],b[1],depth/2),F.p(a[0],a[1],depth/2)])
 def sign(x,z,yaw,tall):
  F=Frame(B,x,z,yaw,y=0);bottom=10.4 if tall else 4.5;w=5.6 if tall else 4.8;h=2.55 if tall else 2.1
  F.box('ino-concrete',(0,.18,0),(1.4,.36,1.4),True)
  F.box('ino-metal',(0,bottom/2,0),(.43,bottom,.43),True)
  if tall:
   for y in np.arange(2.4,bottom,.38):F.lathe('ino-trim',0,0,[(y,.23),(y+.07,.48),(y+.16,.48),(y+.19,.23)],24)
  panel=[(-w/2+.12,bottom),(w/2-.12,bottom),(w/2,bottom+.12),(w/2,bottom+h-.12),(w/2-.12,bottom+h),(-w/2+.12,bottom+h),(-w/2,bottom+h-.12),(-w/2,bottom+.12)]
  prism(F,'ino-sign-red',panel,.55 if tall else .25)
  for side in [-1,1]:
   G=Frame(B,x,z,yaw+(math.pi if side==1 else 0),y=0)
   for yy in [bottom+.10,bottom+h-.10]:G.box('ino-metal',(0,yy,-(.30 if tall else .15)),(w-.2,.045,.045))
   G.text('IN-N-OUT',(0,bottom+h*.55,-(.32 if tall else .17)),1.60 if tall else 1.36,'ino-sign-white')
   G.text('BURGER',(0,bottom+.23,-(.32 if tall else .17)),1.72 if tall else 1.46,'ino-sign-white')
  # Arrow cap is a continuous thick original silhouette, with an open triangular centre.
  y=bottom+h
  arrow=[(-w*.48,y-.5),(-w*.66,y+1.8),(w*.48,y+.45),(w*.50,y+.78),(w*.72,y+.05),(w*.38,y-.38),(w*.42,y+.02),(-w*.40,y+1.03),(-w*.27,y-.5)]
  arrow=[(-x,y) for x,y in arrow]
  prism(F,'ino-yellow',arrow,.72 if tall else .30)
 sign(-790.5,1623.5,math.pi/2,True)
 sign(-837,1667.5,math.pi,False)
 # Short photographed southern boundary segment; retain existing road surfaces and entrances.
 F=Frame(B,-837,1668,math.pi,y=0)
 F.box('ino-concrete',(0,.43,0),(18,.86,.38),True)
 F.box('ino-trim',(0,.89,0),(18.14,.10,.46))
 for y in [.20,.43,.66]:F.box('ino-joint',(0,y,-.195),(18,.012,.012))
 for row,y in enumerate([.10,.32,.55,.78]):
  for x in np.arange(-8.6+(row%2)*.45,9,.9):F.box('ino-joint',(x,y,-.20),(.012,.19,.012))
 for x in np.arange(-8.85,9,.24):F.box('ino-fence',(x,1.52,0),(.025,1.2,.025))
 for y in [1.01,1.98]:F.box('ino-fence',(0,y,0),(18,.045,.05))
 for x in np.arange(-9,9.1,3):F.box('ino-fence',(x,1.5,0),(.065,1.24,.065))
