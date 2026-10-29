"""Photo-supported public rooms; measured plan unavailable, partitions inferred.
All geometry stays inside the claimed main building, excluding the A200 annex.
"""
from common import *
def build_public(B,F,entry):
 B.property='ferraros-interior';B.source='public/ferraros';B.detail=0
 room=F.poly([(.2,.12),(21.7,.12),(21.7,20.2),(.2,20.2)])
 B.shell(room,.16,4.25,'fr-room',openings=[entry],roof=False)
 B.planar('fr-ceiling',room,4.27)
 # Separate flooring follows the photographed bar / carpeted dining contrast.
 B.planar('fr-woodfloor',F.poly([(.21,.13),(21.69,.13),(21.69,9),(.21,9)]),.16,True)
 B.planar('fr-carpet',F.poly([(.21,9),(21.69,9),(21.69,20.19),(.21,20.19)]),.16,True)
 for u in [.24,21.66]:F.box('fr-trim',(u,.27,10.1),(.06,.2,20))
 F.box('fr-trim',(11,.27,20.15),(21.5,.2,.08))
 def chair(u,v,turn=0,high=False):
  p=F.p(u,0,v);G=Frame(B,p[0],p[2],F.yaw+turn,y=0);seat=.9 if high else .63
  G.box('fr-leather',(0,seat,0),(.48,.10,.48))
  for x in [-.19,.19]:
   for z in [-.19,.19]:G.box('fr-walnut',(x,(seat+.16)/2,z),(.04,seat-.16,.04))
  # Curved wooden back, tapered side rails; not a single thick box.
  for x in [-.24,.24]:G.tube('fr-walnut',(x,seat-.1,.19),(x*.88,seat+.65,.28),.025,8)
  for k in range(8):
   a=-.5+k/8;b=-.5+(k+1)/8
   G.b.face('fr-walnut',[G.p(a*.44,seat+.18,.22+.12*a*a),G.p(b*.44,seat+.18,.22+.12*b*b),G.p(b*.48,seat+.61,.26+.12*b*b),G.p(a*.48,seat+.61,.26+.12*a*a)])
 def setting(u,v,y):
  F.lathe('fr-porcelain',u,v,[(y,.12),(y+.012,.13),(y+.025,.115)],20)
  F.box('fr-napkin',(u+.22,y+.014,v),(.11,.025,.20))
  F.lathe('fr-drink',u-.13,v+.19,[(y,.04),(y+.11,.042)],12)
  F.tube('fr-cutlery',(u+.13,y+.02,v-.07),(u+.13,y+.02,v+.08),.006,6)
 def table(u,v,w=1.25,d=.85):
  F.box('fr-table',(u,.94,v),(w,.07,d),True)
  for du in [-w*.32,w*.32]:
   F.lathe('fr-metal',u+du,v,[(.16,.22),(.20,.22),(.22,.035),(.90,.035)],12)
  for dv in [-d/2-.38,d/2+.38]:chair(u,v+dv,0 if dv>0 else math.pi)
  for dv in [-.23,.23]:setting(u,v+dv,.982)
  F.lathe('fr-bottle',u+.35,v,[(.98,.035),(1.17,.035),(1.21,.017),(1.29,.017)],10)
 # Long L bar and open circulation around its right end.
 F.box('fr-walnut',(7.2,.66,2.45),(11.2,1.0,.88),True)
 F.box('fr-table',(7.2,1.21,2.45),(11.45,.10,1.05))
 F.box('fr-walnut',(1.85,.66,4),(.65,1.0,2.6),True)
 F.box('fr-table',(1.85,1.21,4),(.85,.10,2.75))
 F.tube('fr-cutlery',(1.8,.4,3.06),(12.7,.4,3.06),.024,10)
 for u in np.arange(2.6,12.7,.9):
  chair(u,3.65,math.pi,True)
  F.box('fr-trim',(u,.66,2.905),(.62,.69,.025))
  F.box('fr-walnut',(u,.66,2.928),(.56,.63,.022))
 # Cabinet system and bottles, observed above the bar and at the far side.
 def bottles(u,v,w,base,rows=3,face=-1):
  F.box('fr-walnut',(u,base+rows*.41/2,v),(w,rows*.41,.30))
  for row in range(rows):
   yy=base+.07+row*.41
   F.box('fr-shelfback',(u,yy+.15,v+face*.17),(w-.08,.32,.025))
   for j,x in enumerate(np.arange(u-w/2+.12,u+w/2-.07,.20)):
    mat='fr-bottle' if j%3 else 'fr-amber'
    F.lathe(mat,x,v+face*.23,[(yy,.036),(yy+.20,.036),(yy+.23,.018),(yy+.30,.018)],8)
    F.lathe('fr-label',x,v+face*.23,[(yy+.07,.037),(yy+.13,.037)],8)
  for x in np.arange(u-w/2,u+w/2+.1,1):F.box('fr-walnut',(x,base+rows*.41/2,v+face*.29),(.05,rows*.41,.06))
 bottles(7.3,.55,11.6,2.6,3,1)
 # Three inner window recesses match the exterior awning bays.
 for u in [4.1,7.15,10.2]:
  F.box('fr-glass',(u,1.95,.25),(2.0,1.2,.05))
  F.box('fr-blind',(u,2.5,.29),(2,.25,.04))
  for du in [-1.03,1.03]:F.box('fr-walnut',(u+du,2.02,.32),(.06,1.5,.08))
 for u,v in [(5,6.1),(9,6.1),(19,5.2)]:table(u,v)
 # Broad arched divisions between the wood-floored bar and carpeted dining.
 for u in [1,10.6,21]:F.box('fr-room',(u,2.18,9),(.55,4.04,.30),True)
 for a,b in [(1.28,10.32),(10.88,20.72)]:
  center=(a+b)/2;half=(b-a)/2
  for k in range(32):
   x=a+(b-a)*k/32;xx=a+(b-a)*(k+1)/32
   y=2.75+.80*math.sqrt(max(0,1-((x-center)/half)**2));yy=2.75+.80*math.sqrt(max(0,1-((xx-center)/half)**2))
   B.face('fr-room',[F.p(x,y,8.84),F.p(xx,yy,8.84),F.p(xx,4.25,8.84),F.p(x,4.25,8.84)])
   B.face('fr-room',[F.p(xx,yy,9.16),F.p(x,y,9.16),F.p(x,4.25,9.16),F.p(xx,4.25,9.16)])
   F.tube('fr-trim',(x,y,8.81),(xx,yy,8.81),.04,8)
 for u in [3.1,7.2,18.5]:
  for v in [11.7,15.4,18.4]:table(u,v,1.4,.9)
 # Wine-wall banquette feature, entirely inside the claimed main room.
 bottles(11.9,19.85,5.0,.7,7)
 F.box('fr-leather',(11.9,.60,18.9),(4.8,.32,.70),True)
 F.box('fr-leather',(11.9,1.05,19.22),(4.8,.70,.17))
 for x in np.arange(9.7,14.3,.28):
  for y in [.89,1.13]:B.sphere('fr-button',F.p(x,y,19.11),.025,8,5)
 # Photo-supported dark-framed wall mirrors and sconces. Reflections are
 # represented by muted backing, not expensive per-room render targets.
 for v in [11.8,16.6]:
  F.box('fr-walnut',(21.59,2.3,v),(.10,2.05,1.55))
  F.box('fr-shelfback',(21.52,2.3,v),(.025,1.84,1.34))
  for dv in [-1.4,1.4]:
   F.box('fr-cutlery',(21.55,2.35,v+dv),(.12,.42,.18))
   F.box('fr-lamp',(21.46,2.4,v+dv),(.10,.30,.13))
 for u in [2.5,5.7,17.5,20]:
  F.box('fr-walnut',(u,2.4,20.09),(1.45,2.15,.09))
  F.box('fr-blind',(u,2.4,20.03),(1.27,1.97,.05))
 for u,v in [(11.5,11.8),(10.8,14.5)]:table(u,v,1.6,.9)
 F.box('fr-walnut',(19.7,.69,1.9),(1.2,1.06,.65),True)
 F.box('fr-table',(19.7,1.25,1.9),(1.27,.07,.72))
 # Ceiling cross beams and ring chandelier reproduced as original geometry.
 for u,v in [(6,14.5),(17.2,14.5)]:
  F.box('fr-walnut',(u,4.07,v),(6.6,.12,1.0));F.box('fr-walnut',(u,4.07,v),(1.0,.12,7))
  for yy,r in [(4.05,1.7),(3.2,1.1)]:F.path('fr-cutlery',[(u+r*math.cos(a),yy,v+r*math.sin(a)) for a in np.linspace(0,math.tau,49)],.03,8)
  for a in np.linspace(0,math.tau,12,endpoint=False):
   x=u+1.1*math.cos(a);z=v+1.1*math.sin(a)
   F.tube('fr-cutlery',(x,3.2,z),(u+.35*math.cos(a),4.15,v+.35*math.sin(a)),.009,6)
   F.lathe('fr-lamp',x,z,[(3.2,.022),(3.49,.022)],8)
 for u in [3,8,13,18]:
  for v in [4.5,8,12,17]:F.lathe('fr-lamp',u,v,[(4.2,.07),(4.22,.07)],12)
 for u,v in [(7,5.8),(16,5),(6,14),(17,14)]:F.light(u,3.7,v,color=0xffe7ce,power=9,range=11)
 return room
