"""Wiseguys former Main Street location, January2026 facade; murals pending."""
from common import *
from forum_shops import facade_frame
KEY='mainStreet1511'
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/frontage';B.detail=0;W=Frame(B,0,0,y=0)
 p=footprint('way/689003951');B.shell(p,.18,4.65,'ms-white-brick-paint',roof=False);B.planar('ms-flat-roof-paint',p,4.48,True)
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  G,L,nx,nz=facade_frame(B,a,b,p,.025);G.box('ms-coping',(L/2,4.67,0),(L,.13,.16))
  if nx<-.7:
   # Street frontage: one centered red entry, silver fluted canopy and stone strips.
   for u in [L*.08,L*.38,L*.65,L*.96]:
    G.box('ms-gray-stone',(u,2.42,-.05),(.55,4.45,.13))
    for y in np.arange(.45,4.5,.32):G.box('ms-stone-joint',(u,y,-.13),(.53,.018,.02))
   G.box('ms-black',(L*.52,1.53,-.13),(1.15,2.7,.08));G.box('ms-red',(L*.52,1.54,-.19),(.98,2.5,.05))
   G.text('LIVE COMEDY',(L*.52,1.72,-.23),.11,'ms-letter')
   G.tube('ms-metal',(L*.52+.36,1.05,-.27),(L*.52+.36,1.85,-.27),.025,8)
   G.box('ms-black',(L*.68,2,-.16),(.6,1.1,.05))
   G.box('ms-canopy-metal',(L/2,3.3,-.5),(L,.35,1))
   for u in np.arange(.1,L,.12):G.box('ms-metal',(u,3.3,-1.02),(.045,.35,.035))
   G.box('ms-black',(L/2,4.06,-.14),(6.5,.97,.03));G.text('Wiseguys',(L/2,4.16,-.19),.65,'ms-letter');G.text('LIVE COMEDY',(L/2,3.81,-.19),.18,'ms-letter')
  elif nz>.7:
   # South parking entry has a deep rounded fabric hood.
   u=L*.22;G.box('ms-black',(u,1.55,-.11),(1.8,2.7,.09));G.box('ms-red',(u,1.55,-.18),(1.6,2.5,.05))
   for t0,t1 in zip(np.linspace(0,math.pi,19),np.linspace(0,math.pi,19)[1:]):
    B.face('ms-black',[G.p(u+1.4*math.cos(t0),2.7+1.4*math.sin(t0),-.05),G.p(u+1.4*math.cos(t1),2.7+1.4*math.sin(t1),-.05),G.p(u+1.4*math.cos(t1),2.7+1.4*math.sin(t1),-1.5),G.p(u+1.4*math.cos(t0),2.7+1.4*math.sin(t0),-1.5)])
   for u2 in [2,L/2,L-2]:G.box('ms-black',(u2,4.35,-.18),(.35,.22,.24))
 # Parking retained inside the lot, off the Main Street sidewalk.
 yard=box(1723,-4112,1760,-4099).difference(p);B.planar('ms-asphalt',yard,.18,True)
 B.planar('ms-paving',p.buffer(1,join_style=2).difference(p).difference(yard),.18,True)
 for x in np.arange(1725,1758,3):W.box('ms-line',(float(x),.191,-4109),(.07,.012,5.5))
 for x,z in [(1732,-4120),(1742,-4120)]:W.box('ms-service',(x,4.95,z),(2,.9,1.6));W.box('ms-black',(x,5.42,z),(1.6,.03,1.2))
 samples=[]
 for x in np.arange(1724,1758,1):
  for z in np.arange(-4110,-4100,1):
   if yard.buffer(-.5).covers(Point(x,z)):samples.append([float(x),.18,float(z)])
 Path('build/city-exteriors/main-street-1511-samples.json').write_text(json.dumps(samples))
 return dict(key=KEY,name='1511 South Main Street',center=[1736,0,-4121],bounds=[1721,-4130,1761,-4098],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
