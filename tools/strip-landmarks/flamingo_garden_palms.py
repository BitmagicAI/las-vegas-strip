"""Original pinnate palms; inferred forms and heights, not surveyed specimens.
Replace selected existing tree positions, retaining their ground collision and all
other vegetation. No image textures or third-party palm geometry are used.
"""
import math
PALM_INDICES=frozenset([11,12,14,15,17,22,24,32,36,38,44,50])

def add_palm(B,x,z,index,yaw,ground=.4):
 height=8.4+(index%4)*.8
 B.lathe('fgp-bark',(x,z),[(ground,.12),(ground+.5,.12),(ground+height-.4,.10),(ground+height,.16)],10)
 # Narrow ring scars and a compact crown; keep trunk within existing collider.
 for k in range(1,int(height/.32)):
  y=ground+k*.32
  B.lathe('fgp-bark',(x,z),[(y-.015,.105),(y,.12),(y+.02,.105)],10)
 for tier in range(2):
  for j in range(12):
   a=yaw+j*math.tau/12+tier*.31
   reach=3.2 if tier==0 else 2.55
   def point(t,side=0):
    r=reach*t
    return (x+r*math.cos(a)-side*math.sin(a),ground+height+1.1*math.sin(t*math.pi)-(1.4 if tier==0 else .15)*t,z+r*math.sin(a)+side*math.cos(a))
   B.path('fgp-leaf',[point(k/8)for k in range(9)],.018,4)
   for k in range(1,13):
    t=k/14;length=.95*math.sin(math.pi*t)**.7
    for side in [-1,1]:
     root=point(t);tip=point(min(.99,t+.12),side*length)
     tip=(tip[0],tip[1]-.18,tip[2])
     a0=point(t-.055,side*.06);a1=point(t+.055,side*.06)
     ridge=((root[0]+tip[0])*.5,(root[1]+tip[1])*.5+.045,(root[2]+tip[2])*.5)
     for tri in [(a0,ridge,tip),(ridge,a1,tip)]:
      B.face('fgp-leaf',tri);B.face('fgp-leaf',list(reversed(tri)))
