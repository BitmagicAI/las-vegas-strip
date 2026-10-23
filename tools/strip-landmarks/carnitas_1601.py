"""1601 South Las Vegas Boulevard, August2024 StreetView exterior."""
from common import *
from forum_shops import facade_frame
KEY='carnitas1601'
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/frontage';B.detail=0;W=Frame(B,0,0,y=0)
 p=footprint('way/364845147');B.shell(p,.18,4.55,'cg-red-stucco',roof=False);B.planar('cg-flat-roof-paint',p,4.4,True)
 patio=None
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  G,L,nx,nz=facade_frame(B,a,b,p,.035)
  G.box('cg-white',(L/2,3.75,-.03),(L,1.35,.12));G.box('cg-gray',(L/2,2.98,-.09),(L,.25,.08))
  G.box('cg-red-stucco',(L/2,4.43,-.1),(L,.2,.12))
  G.box('cg-coping',(L/2,4.59,0),(L,.13,.2))
  if nx<-.7:
   G.box('cg-white',(L/2,4.03,-.19),(L-.3,.9,.12));G.text('CARNITAS Y TORTAS AHOGADAS GUADALAJARA #2',(L/2,4,-.27),.48,'cg-red-letter')
   for u in [L*.13,L*.46,L*.72,L*.9]:
    G.box('cg-white',(u,1.8,-.1),(1.9,1.5,.12));G.box('cg-glass',(u,1.8,-.18),(1.68,1.28,.05));G.box('cg-metal-paint',(u,1.8,-.23),(.04,1.28,.04))
   u=L*.3;G.box('cg-metal-paint',(u,1.55,-.17),(1.2,2.6,.12));G.box('cg-glass',(u,1.55,-.25),(1.05,2.4,.05));G.tube('cg-metal-paint',(u+.35,1.1,-.32),(u+.35,1.8,-.32),.025,8)
   patio=G.poly([(0,-.15),(L,-.15),(L,-3.05),(0,-3.05)]);B.planar('cg-paving',patio,.18,True)
   G.box('cg-canopy-paint',(L/2,3.05,-1.6),(L,.16,3.2))
   # Gate opening remains traversable; bar geometry has one simple rail collider per span.
   gate=L*.3
   for lo,hi in [(0,gate-.85),(gate+.85,L)]:
    for u in np.arange(lo,hi,.19):G.box('cg-white',(float(u),1.65,-3),(.035,2.9,.035))
    for y in [.35,1.12,3.1]:G.box('cg-white',((lo+hi)/2,y,-3),(hi-lo,.06,.06))
    c=B.solids[B.property];n=len(c['vertices'])//3
    for q in [(lo,.2,-3),(hi,.2,-3),(hi,3.1,-3),(lo,3.1,-3)]:c['vertices'].extend(G.p(*q))
    c['indices'].extend([n,n+1,n+2,n,n+2,n+3])
   for u in [0,L*.5,L]:G.box('cg-white',(u,1.65,-3),(.12,2.9,.12),True)
   for u in [L*.11,L*.55,L*.83]:
    G.box('cg-table',(u,.96,-1.8),(1.35,.1,.7));G.box('cg-metal-paint',(u,.56,-1.8),(.13,.7,.13))
    for w in [-1.1,-2.5]:
     G.box('cg-table',(u,.65,w),(1.35,.09,.32));G.box('cg-metal-paint',(u,.4,w),(.12,.5,.12))
  elif nz<-.7:
   G.box('cg-white',(L*.5,1.8,-.12),(2.1,1.5,.12));G.box('cg-glass',(L*.5,1.8,-.2),(1.88,1.28,.05));G.text('TAQUERIA',(L*.5,3.65,-.15),.55,'cg-red-letter')
  elif nx>.7:
   G.box('cg-metal-paint',(L*.7,1.5,-.08),(1.05,2.45,.1));G.box('cg-gray',(L*.3,2.2,-.07),(1.4,.8,.12))
   for u in [2,L-2]:G.tube('cg-gray',(u,.4,-.15),(u,4.5,-.15),.045,8)
 site=box(1914,-4004,1933,-3979).difference(p)
 B.planar('cg-paving',site.difference(patio),.18,True)
 for x,z in [(1925,-3994),(1926,-3986)]:W.box('cg-service',(x,4.9,z),(1.5,.8,1.3))
 samples=[]
 for x in np.arange(1915,1932,.7):
  for z in np.arange(-4003,-3980,.7):
   if site.buffer(-.5).covers(Point(x,z)) and not (1917<x<1921 and -4001<z<-3980):samples.append([float(x),.18,float(z)])
 Path('build/city-exteriors/carnitas-1601-samples.json').write_text(json.dumps(samples))
 return dict(key=KEY,name='Carnitas y Tortas Ahogadas Guadalajara 2',center=[1925,0,-3991],bounds=[1913,-4005,1934,-3978],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
