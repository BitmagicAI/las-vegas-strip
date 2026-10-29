"""Public-room details inferred from Marriott lobby8513, not a measured plan."""
from common import *
def add_public_details(B,F):
 # Shallow ceiling coffers and wall trim; fixtures borrow the existing light pool.
 for x0,x1,z0,z1 in [(20.1,29,7.1,17.8),(29,43.9,7.1,17.8)]:
  for z in [z0,z1]:F.box('ts-ceiling',((x0+x1)/2,3.31,z),(x1-x0,.30,.28))
  for x in [x0,x1]:F.box('ts-ceiling',(x,3.31,(z0+z1)/2),(.28,.30,z1-z0))
 for x in [22,26,31,36,41]:
  for z in [9,15.2]:
   F.lathe('ts-frame-paint',x,z,[(3.42,.12),(3.46,.12)],12)
   B.planar('ts-letter',F.poly([(x+.09*math.cos(a),z+.09*math.sin(a)) for a in np.linspace(0,math.tau,12,endpoint=False)]),3.414)
 for x in [25,39]:
  F.box('ts-frame-paint',(x,3.43,12),(.70,.055,.54))
  for z in np.arange(11.8,12.22,.055):F.box('ts-panel-seam',(x,3.397,float(z)),(.58,.014,.018))
 for a,b in [((20.1,7.1),(43.9,7.1)),((20.1,7.1),(20.1,17.9)),((43.9,7.1),(43.9,17.9)),((20.1,17.9),(29.6,17.9)),((33,17.9),(43.9,17.9))]:
  F.box('ts-wood',((a[0]+b[0])/2,.34,(a[1]+b[1])/2),(max(.07,abs(a[0]-b[0])),.2,max(.07,abs(a[1]-b[1]))))
 # Dark frame and blue upholstered lobby bench seen beside the timber column.
 for x in [32.55,34.25]:
  for z in [10.78,11.2]:F.tube('ts-chair-frame-paint',(x,.24,z),(x,.57,z),.035,8)
 F.box('ts-wood',(33.4,3.05,10.0),(2.1,.62,1.12))
 # Small business workstation on the column's dining side, with keyboard and chair.
 F.box('ts-wood',(33.45,.99,8.87),(1.75,.09,.70),True)
 for x in [32.7,34.2]:F.box('ts-chair-frame-paint',(x,.63,8.88),(.07,.70,.56))
 F.box('ts-chair-frame-paint',(33.45,1.12,9.04),(.32,.08,.24))
 F.box('ts-chair-frame-paint',(33.45,1.28,9.06),(.05,.3,.05))
 F.box('ts-screen',(33.45,1.54,9.06),(.68,.43,.045))
 F.box('ts-frame-paint',(33.45,1.052,8.76),(.55,.025,.18))
 for i in range(10):
  for j in range(3):F.box('ts-screen',(33.2+i*.05,1.068,8.70+j*.05),(.035,.009,.032))
 F.box('ts-seat',(33.45,.70,8.05),(.62,.13,.6),True)
 F.box('ts-seat',(33.45,1.02,7.78),(.62,.67,.11))
 for x in [33.2,33.7]:
  for z in [7.84,8.25]:F.tube('ts-chair-frame-paint',(x,.24,z),(x,.65,z),.025,6)
 # Lobby lounge occupies the side of the circulation, not the clear reception approach.
 for x in [21.2,23.1]:
  F.box('ts-blue',(x,.58,16.8),(1.1,.42,.87),True)
  F.box('ts-blue',(x,.99,17.17),(1.1,.76,.18))
  for xx in [x-.49,x+.49]:F.box('ts-blue',(xx,.85,16.8),(.13,.45,.9))
  for xx in [x-.39,x+.39]:
   for z in [16.48,17.08]:F.box('ts-chair-frame-paint',(xx,.31,z),(.07,.14,.07))
 F.box('ts-wood',(22.15,.65,15.56),(1.3,.08,.66),True)
 for x in [21.62,22.68]:
  for z in [15.32,15.8]:F.tube('ts-chair-frame-paint',(x,.24,z),(x,.61,z),.025,6)
 # Breakfast cabinet fronts, ceramic cups and trays, original generic shapes.
 for x in [40.3,41.05,41.8,42.55,43.3]:
  F.box('ts-wood',(x,.77,8.312),(.71,.88,.025))
  F.box('ts-metal',(x,1.04,8.34),(.23,.025,.025))
 F.box('ts-counter',(41.7,1.39,8.04),(.65,.045,.38))
 for x in [41.48,41.66,41.84]:
  for z in [7.98,8.16]:F.lathe('ts-letter',x,z,[(1.42,.055),(1.57,.065)],12)
