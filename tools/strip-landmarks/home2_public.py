"""Original breakfast/reception details informed by Hilton's public-room photographs."""
import math
import numpy as np
def add_details(B,F):
 # Individual drawer fronts, pulls and recessed toe kick, inside existing cabinet envelope.
 for x in np.arange(51.25,59.5,.65):
  for y,h in [(.53,.38),(.96,.34)]:
   F.box('h2-wood',(float(x),y,17.43),(.62,h,.045))
   F.box('h2-metal',(float(x),y+.08,17.39),(.21,.024,.04))
 F.box('h2-charcoal-paint',(55.2,.31,17.46),(8.2,.13,.04))
 F.box('h2-wood',(55.2,2.35,18.85),(8.8,1.75,.08))
 F.text('Inspired table',(56.4,2.8,18.77),.46,'h2-letter')
 # Upper plate cubbies and crockery: separate shelf rims and stacked dishes.
 for x in [51.1,52.2,53.3]:
  F.box('h2-wood',(x,2.45,18.3),(.06,1.55,1.0))
 for y in [1.72,2.22,2.98]:F.box('h2-wood',(52.2,y,18.3),(2.25,.06,1.0))
 for x in [51.65,52.75]:
  for y in np.arange(1.78,2.06,.04):F.lathe('h2-counter',x,18.0,[(float(y),.16),(float(y)+.025,.19)],16)
  F.box('h2-lime-paint',(x,2.56,17.76),(1.02,.35,.06))
 # Existing microwave boxes receive frames, displays, buttons and handles.
 for x in [52.2,54.1,57.3]:
  F.box('h2-frame-paint',(x+.27,1.78,17.53),(.12,.52,.04))
  for y in [1.65,1.77,1.89]:F.box('h2-screen',(x+.27,y,17.50),(.045,.035,.02))
  F.box('h2-metal',(x-.24,1.80,17.51),(.026,.32,.045))
 # Pair of waffle irons with open gridded lids and long insulated handles.
 for x in [55.5,56.25]:
  F.lathe('h2-metal',x,17.65,[(1.4,.19),(1.49,.19)],20)
  F.box('h2-screen',(x,1.51,17.65),(.30,.025,.30))
  F.box('h2-metal',(x,1.72,17.85),(.36,.36,.035))
  for q in [-.12,-.06,0,.06,.12]:
   F.box('h2-screen',(x+q,1.72,17.82),(.012,.30,.02));F.box('h2-screen',(x,1.72+q,17.82),(.30,.012,.02))
  F.tube('h2-metal',(x,1.89,17.85),(x,2.15,17.92),.025,8);F.tube('h2-screen',(x,2.04,17.89),(x,2.2,17.94),.038,8)
 # Cereal and juice dispensers, original generic contents/materials.
 for x in [58.2,58.8]:
  F.lathe('h2-metal',x,17.8,[(1.4,.18),(1.44,.18),(1.45,.045),(1.62,.045)],16)
  F.lathe('h2-ochre-paint',x,17.8,[(1.62,.15),(2.05,.15)],20)
  F.lathe('h2-metal',x,17.8,[(2.05,.17),(2.09,.17)],20)
  F.box('h2-metal',(x,1.58,17.58),(.12,.04,.12))
 # Table top condiments and subtle seams between table sections.
 for x in [54.7,56,57.3]:
  F.lathe('h2-counter',x,13.7,[(1.06,.045),(1.20,.045)],12)
  F.box('h2-panel-joint',(x+.64,1.055,13.7),(.008,.006,1.12))
 # Small potted plants and original multicolour cushions on the long banquette.
 for z in [8.3,10.8,13.3]:
  F.box('h2-yellow-fabric',(47.97,1.0,z),(.24,.43,.55))
  for dz in [-.18,0,.18]:F.box('h2-blue-fabric',(48.11,1.0,z+dz),(.018,.4,.045))
 for x,z in [(50,4.1),(53,4.1),(60.7,5.0)]:
  F.lathe('h2-counter',x,z,[(1.05,.10),(1.25,.13)],16)
  for a in np.linspace(0,math.tau,8,endpoint=False):
   F.tube('h2-green-fabric',(x,1.24,z),(x+.13*math.cos(a),1.48,z+.13*math.sin(a)),.025,5,.006)
 # Vent grilles, ceiling strips and non-emissive fixture lenses. No new runtime lights.
 for x in [49.5,56,62]:
  F.box('h2-frame-paint',(x,3.31,9.5),(.8,.035,.6))
  for u in np.arange(-.3,.35,.10):F.box('h2-panel-joint',(x+float(u),3.285,9.5),(.025,.015,.5))
 for x in [49.5,56,62]:
  for z in [6,15]:F.lathe('h2-counter',x,z,[(3.29,.11),(3.33,.11)],16)
