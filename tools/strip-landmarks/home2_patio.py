"""Original grill patio. Photo-informed fixtures; map-picked, estimated placement."""
from common import *
def add_patio(B,F):
 B.property='home2-stadium-exterior';B.source='podium/home2-stadium'
 # Aerial shade-centre pick36.099493,-115.181693 -> local72.14,3.68.
 # Keep the garage (z<=-6 here) and driveway outside the authored terrace.
 patio=F.poly([(68.4,-1.8),(76,-1.8),(76,5.5),(68.4,5.5)])
 landing=F.poly([(67.21,3.05),(71.71,3.05),(71.71,12.55),(67.21,12.55)])
 approach=F.poly([(20,-.5),(70,-.5),(70,-2),(24,-2),(24,-4),(20,-4)])
 new=patio.difference(landing.union(approach))
 B.planar('h2-paving',new,.24,True);B.shell(new,.01,.24,'h2-paving',roof=False)
 # Slatted shade frame, open toward entrance and pool path.
 for x,z in [(68.5,-1.95),(76,-1.95),(76,5.4)]:
  F.box('h2-stone',(x,1.86,z),(.52,3.24,.52),True)
  F.box('h2-counter',(x,3.52,z),(.60,.08,.60))
 for z in [-1.95,5.4]:F.box('h2-charcoal-paint',(72.25,3.43,z),(7.8,.21,.17))
 for x in [68.5,76]:F.box('h2-charcoal-paint',(x,3.43,1.725),(.17,.21,7.55))
 for x in np.arange(68.6,76,.33):F.box('h2-charcoal-paint',(float(x),3.57,1.725),(.095,.14,7.5))
 # Reference grill wall with broad slats above its stone base.
 F.box('h2-stone',(73.1,.71,-1.25),(5.28,.94,.80),True)
 F.box('h2-counter',(73.1,1.21,-1.25),(5.4,.10,.92))
 for x in np.arange(70.5,75.9,.20):F.box('h2-charcoal-paint',(float(x),2.36,-1.61),(.09,2.12,.06))
 F.box('h2-charcoal-paint',(73.15,1.35,-1.61),(5.3,.10,.09))
 for x in [71.75,74.45]:
  F.box('h2-brushed-alloy',(x,1.27,-1.18),(1.12,.20,.70))
  # Curved closed grill hood, actual end caps; no photographic texture.
  pts=[(-1.50,1.37),(-1.50,1.69)]
  pts += [(-1.17-.33*math.cos(a),1.69+.22*math.sin(a)) for a in np.linspace(0,math.pi,13)]
  pts += [(-.84,1.37)]
  for xx in [x-.55,x+.55]:B.face('h2-brushed-alloy',[F.p(xx,y,z) for z,y in pts])
  for (z,y),(zz,yy) in zip(pts,pts[1:]+pts[:1]):B.face('h2-brushed-alloy',[F.p(x-.55,y,z),F.p(x+.55,y,z),F.p(x+.55,yy,zz),F.p(x-.55,yy,zz)])
  F.path('h2-brushed-alloy',[(x-.40,1.55,-.84),(x-.40,1.55,-.71),(x+.40,1.55,-.71),(x+.40,1.55,-.84)],.022,10)
  # Hood temperature dial from the official photograph, no copied branding.
  F.tube('h2-brushed-alloy',(x,1.77,-.86),(x,1.77,-.82),.062,24)
  F.tube('h2-letter',(x,1.77,-.819),(x,1.77,-.815),.049,24)
  F.box('h2-charcoal-paint',(x,1.785,-.811),(.006,.035,.005))
  for dx in [-.34,0,.34]:
   F.tube('h2-charcoal-paint',(x+dx,1.27,-.81),(x+dx,1.27,-.76),.052,16)
   F.box('h2-letter',(x+dx,1.295,-.754),(.009,.035,.009))
  F.box('h2-brushed-alloy',(x,.70,-.833),(.75,.72,.035))
  F.box('h2-charcoal-paint',(x,.70,-.808),(.69,.65,.014))
  F.box('h2-brushed-alloy',(x,.70,-.792),(.65,.61,.012))
  F.path('h2-brushed-alloy',[(x+.22,.81,-.78),(x+.22,.81,-.73),(x+.22,.95,-.73),(x+.22,.95,-.78)],.015,8)
 # Square tables and yellow moulded chairs; broad collision proxies, no leg colliders.
 for x,z in [(73.8,2.6)]:
  F.box('h2-patio-table',(x,1.00,z),(.92,.08,.92))
  F.lathe('h2-metal',x,z,[(.24,.28),(.28,.28),(.29,.045),(.96,.045)],16)
  F.box('h2-patio-proxy',(x,.64,z),(.94,.80,.94),True)
  for dx,dz,yaw in [(-.86,0,-math.pi/2),(.86,0,math.pi/2),(0,.86,0)]:
   G=Frame(B,*F.p(x+dx,0,z+dz)[::2],F.yaw+yaw,y=0)
   G.box('h2-yellow-fabric',(0,.68,0),(.46,.085,.46))
   G.box('h2-yellow-fabric',(0,.96,.20),(.46,.53,.07))
   for u in [-.18,.18]:
    for v in [-.18,.18]:G.tube('h2-yellow-fabric',(u*1.12,.24,v*1.12),(u,.65,v),.018,8)
   G.box('h2-patio-proxy',(0,.72,.03),(.48,.96,.53),True)
 # Compact photo-informed lounge in the covered patio. Arrangement is inferred,
 # not a measured placement; keep the existing entrance/pool route clear.
 x,z=69.95,1.35
 F.lathe('h2-firepit-stone',x,z,[(.24,.48),(.32,.55),(.78,.55),(.83,.72),(.91,.72),(.91,.34),(.80,.34)],48)
 F.lathe('h2-charcoal-paint',x,z,[(.79,.33),(.81,.33)],32)
 F.box('h2-patio-proxy',(x,.55,z),(1.42,.62,1.42),True)
 for angle in [math.pi/2,0,3*math.pi/2]:
  cx=x+math.sin(angle)*1.12;cz=z+math.cos(angle)*1.12
  G=Frame(B,*F.p(cx,0,cz)[::2],F.yaw+angle,y=0)
  G.box('h2-woven',(0,.49,0),(.78,.5,.68))
  G.box('h2-woven',(0,1.17,.29),(.78,1.18,.10))
  G.box('h2-stripe-fabric',(0,.78,-.02),(.69,.16,.59))
  G.box('h2-stripe-fabric',(0,1.04,.20),(.69,.40,.13))
  for u in [-.37,.37]:G.box('h2-woven',(u,.86,0),(.10,.15,.70))
  G.box('h2-patio-proxy',(0,.87,0),(.84,1.26,.74),True)
 # Original unlit lava-stone bed: no new runtime light or static fake flame.
 rng=random.Random(281)
 for i in range(36):
  a=rng.random()*math.tau;r=math.sqrt(rng.random())*.29
  F.lathe('h2-lava',x+math.cos(a)*r,z+math.sin(a)*r,[(.81,.025),(.84,.035),(.86,.012)],6)
 # Low planted pocket beside patio, bounded above the garage edge.
 garden=F.poly([(70.3,-5.0),(75.5,-5.0),(75.5,-2.0),(70.3,-2.0)])
 B.planar('h2-soil',garden,.07)
 rng=random.Random(280)
 for x,z in [(70.7,-4.4),(72.3,-4.5),(74.4,-4.4),(74.8,-2.7),(71.0,-2.7)]:
  for k in range(18):
   a=rng.random()*math.tau;r=rng.uniform(.22,.43);h=rng.uniform(.25,.52)
   p=(x,.08,z);q=(x+math.cos(a)*r,.08+h,z+math.sin(a)*r);w=.018
   B.face('h2-leaf',[F.p(p[0]-w,p[1],p[2]),F.p(p[0]+w,p[1],p[2]),F.p(*q)])
 for key in list(B.groups):
  if B.groups[key]['material']=='h2-patio-proxy':del B.groups[key]
 return [dict(name='Entrance to grill patio and pool path',points=[F.p(x,.24,z) for x,z in [(70.5,7.8),(70.5,4.7),(72,4.7),(72,2.9),(72,.25),(70,.25),(69,-.9),(69,-1.2),(60,-1.2)]]),dict(name='Grill counter approach',points=[F.p(x,.24,z) for x,z in [(71.4,.25),(73,.25),(75,.25)]])]
