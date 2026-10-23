"""Russell Road service building; north wall and roof referenced, concealed sides inferred."""
from common import *
from forum_shops import facade_frame
KEY='russellService';ID='way/1378308607'
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/'+ID;B.detail=0;p=footprint(ID);F=Frame(B,-152.057,3342.601,math.atan2(.178,15.431),y=0)
 B.shell(p,.18,5.8,'rsv-tan-stucco',roof=False);B.planar('rsv-membrane-paint',p.buffer(-.12),5.58,True)
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  G,L,nx,nz=facade_frame(B,a,b,p,.01)
  G.box('rsv-coping-paint',(L/2,5.79,-.04),(L,.18,.28))
  G.box('rsv-plinth-paint',(L/2,.4,-.04),(L,.42,.10))
  if abs(nx)>.8:
   # Service doors and grille positions are estimates: no public interior inferred.
   for u in [L*.2,L*.75]:
    G.box('rsv-frame-paint',(u,1.5,-.06),(1.26,2.64,.12));G.box('rsv-door-paint',(u,1.5,-.14),(1.08,2.46,.06));G.tube('rsv-hardware-paint',(u+.35,1.25,-.20),(u+.35,1.54,-.20),.018,6)
    G.box('rsv-fixture-paint',(u,3.15,-.12),(.38,.20,.28))
   for u in [L*.42,L*.55]:
    G.box('rsv-vent-paint',(u,3.2,-.07),(1.1,.7,.12))
    for y in np.arange(2.9,3.51,.10):G.box('rsv-frame-paint',(u,float(y),-.15),(1.04,.035,.04))
   for u in [1,L-1]:G.tube('rsv-drain-paint',(u,.18,-.15),(u,5.62,-.15),.045,8)
   for u in [L*.32,L*.64]:G.box('rsv-joint-paint',(u,2.9,-.015),(.018,5.35,.025))
  if nz>.8:
   G.box('rsv-frame-paint',(L*.5,1.7,-.08),(3,3,.12));G.box('rsv-door-paint',(L*.5,1.7,-.16),(2.8,2.8,.06))
   G.box('rsv-frame-paint',(L*.5,3.45,-.85),(4.1,.12,1.6))
 # Six roof equipment groups at aerial positions and smaller pipe terminals.
 for j,(u,w) in enumerate([(2.2,3),(2.3,8),(3.8,12),(11.4,12),(3.8,24),(11.4,24)]):
  F.box('rsv-curb-paint',(u,5.7,w),(1.6,.22,1.7));F.box('rsv-service-paint',(u,6.06,w),(1.3,.6,1.4))
  F.lathe('rsv-vent-paint',u,w,[(6.37,.4),(6.42,.4)],20)
  for ang in np.linspace(0,math.tau,8,endpoint=False):F.tube('rsv-grille-paint',(u,6.44,w),(u+.38*math.cos(ang),6.44,w+.38*math.sin(ang)),.014,5)
  F.box('rsv-vent-paint',(u+.66,6.04,w),(.025,.4,1.1))
 for u,w in [(2,10),(2.7,18),(11,13.4)]:F.lathe('rsv-drain-paint',u,w,[(5.58,.12),(5.9,.12),(5.94,.20)],12)
 for w in np.arange(1.2,30,2.4):F.box('rsv-roof-seam-paint',(7.7,5.59,float(w)),(14.8,.014,.016))
 # Only local ground apron; retain the public road and larger parking surfaces.
 B.planar('rsv-concrete',p.buffer(.7,join_style=2).difference(p),.18,True)
 B.planar('rsv-asphalt',p.buffer(2.8,join_style=2).difference(p.buffer(.7,join_style=2)),.08,True)
 samples=[]
 for x in np.arange(p.bounds[0]+.3,p.bounds[2],1.1):
  for z in np.arange(p.bounds[1]+.3,p.bounds[3],1.1):
   if p.buffer(-.25).contains(Point(x,z)):samples.append([float(x),6.2,float(z)])
 Path('build/city-exteriors/russell-service-samples.json').write_text(json.dumps(samples))
 return dict(key=KEY,name='Russell Road service building',center=[-144,0,3358],bounds=list(p.buffer(3).bounds),structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
