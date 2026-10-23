"""North arrival fan, fitted to official 2025 lookbook page 2.
64 m upper width / 30 m lower band, 5.3 m clearance, 13.8 m crown are
visual estimates. Existing entrance/collision ownership is unchanged.
"""
from common import *
def arrival(B):
 B.source='arrival/north';B.detail=0
 F=Frame(B,1220,-2541,0,y=0)
 def q(a,r,y):return F.p(r*math.cos(a),y,-.48*r*math.sin(a))
 def crown(a):return 13.8+.32*math.cos(4*a)
 # Closed upper canopy: broad pale fascia, dark recessed soffit, flat membrane.
 for i in range(96):
  a,b=i*math.pi/96,(i+1)*math.pi/96
  pts=[q(a,0,13.7),q(a,32,crown(a)),q(b,32,crown(b))]
  B.upface('fb-flat-roof',pts,True)
  B.face('fb-soffit',list(reversed([q(a,0,13.15),q(a,32,crown(a)-.55),q(b,32,crown(b)-.55)])),True)
  B.face('fb-canopy-white',[q(a,32,crown(a)-.55),q(b,32,crown(b)-.55),q(b,32,crown(b)),q(a,32,crown(a))])
  # Lower branding band follows the fan's smaller ellipse.
  for r in [14.8,15.2]:
   B.face('fb-silver',[q(a,r,5.3),q(b,r,5.3),q(b,r,5.95),q(a,r,5.95)])
  B.upface('fb-silver',[q(a,14.8,5.95),q(b,14.8,5.95),q(b,15.2,5.95),q(a,15.2,5.95)])
 for a,b in [(0,32),(32,0)]:
  angle=0 if a==0 else math.pi
  B.face('fb-canopy-white',[q(angle,0,13.15),q(angle,32,crown(angle)-.55),q(angle,32,crown(angle)),q(angle,0,13.7)])
 # Curved rectangular metal ribs, no solid triangular infill between them.
 # Each is swept through a vertical-to-flared profile; four longitudinal faces.
 for a in np.linspace(.025,math.pi-.025,77):
  def ring(t):
   r=15+17*t*t;y=5.92+(crown(a)-.68-5.92)*t
   tangent=np.array([-math.sin(a),0,-.48*math.cos(a)]);tangent/=np.linalg.norm(tangent)
   radial=np.array([math.cos(a),0,-.48*math.sin(a)]);radial/=np.linalg.norm(radial)
   c=np.array(q(a,r,y))
   return [c+tangent*s*.075+radial*d*.26 for s,d in [(-1,-1),(1,-1),(1,1),(-1,1)]]
  for j in range(20):
   lo,hi=ring(j/20),ring((j+1)/20)
   for k in range(4):B.face('fb-rib-metal',[lo[k],lo[(k+1)%4],hi[(k+1)%4],hi[k]])
 for x in [-26,26]:F.box('fb-canopy-white',(x,6.65,-2),(1.1,13.3,1.1),True)
 title='FONTAINEBLEAU'
 for i,ch in enumerate(title):
  a=math.pi/2-(i-(len(title)-1)/2)*.093
  p=q(a,15.24,5.53);B.text(ch,p,.38,math.pi/2-a,'fb-silver')
