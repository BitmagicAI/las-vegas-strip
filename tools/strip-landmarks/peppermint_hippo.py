"""1531 Peppermint Hippo exterior: current Street View and listing aerial."""
from common import *
from forum_shops import facade_frame
from diamond_inn import palm
KEY='peppermintHippo'
def archpanel(G,u,base,width,height,mat,depth=-.17):
 frame_mat='ph-black-paint' if mat=='ph-black-paint' else 'ph-window-frame-paint'
 r=width/2;spring=base+height-r
 pts=[(u-r,base,depth),(u+r,base,depth)]+[(u+r*math.cos(a),spring+r*math.sin(a),depth) for a in np.linspace(0,math.pi,17)]
 G.b.face(mat,[G.p(*q) for q in reversed(pts)]);G.path(frame_mat,[(u-r,base,depth-.02),(u-r,spring,depth-.02)],.022,6);G.path(frame_mat,[(u+r,base,depth-.02),(u+r,spring,depth-.02)],.022,6)
 G.path(frame_mat,[(u+r*math.cos(a),spring+r*math.sin(a),depth-.02) for a in np.linspace(0,math.pi,17)],.022,6)
 if mat=='ph-black-paint':return
 for dx in np.arange(-r+.3,r,.35):
  hi=spring+math.sqrt(max(0,r*r-dx*dx));G.tube(frame_mat,(u+float(dx),base,depth-.02),(u+float(dx),hi,depth-.02),.014,6)
 for y in np.arange(base+.3,base+height,.35):
  half=r if y<spring else math.sqrt(max(0,r*r-(y-spring)**2));G.tube(frame_mat,(u-half,float(y),depth-.02),(u+half,float(y),depth-.02),.014,6)
def rail(G,lo,hi,z,base):
 for y in [base+.12,base+.95]:G.tube('ph-red-metal-paint',(lo,y,z),(hi,y,z),.035,8)
 for u in np.arange(lo,hi,.75):
  u=float(u);G.tube('ph-red-metal-paint',(u,base,z),(u,base+1.02,z),.026,8)
  # Interlaced ornamental scroll pattern, shared material and a bounded segment count.
  for yy in [base+.33,base+.72]:
   G.path('ph-red-metal-paint',[(u+.34+.2*math.cos(a),yy+.16*math.sin(a),z) for a in np.linspace(0,math.tau,13)],.014,5)
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/cabaret';B.detail=0;W=Frame(B,0,0,y=0)
 p=footprint('way/364845150');canopy=Polygon([(1951.023,-4055.391),(1957.309,-4054.89),(1955.978,-4038.103),(1949.953,-4041.888)])
 main=p.difference(canopy).buffer(0);B.shell(main,.18,8.35,'ph-white-stucco',roof=False);B.planar('ph-roof-paint',main,8.15,True)
 sign=None
 for a,b in zip(list(main.exterior.coords),list(main.exterior.coords)[1:]):
  G,L,nx,nz=facade_frame(B,a,b,main,.04)
  if L<.3:continue
  G.box('ph-white-paint',(L/2,8.36,-.04),(L,.18,.22))
  if (nx<-.55 and (a[0]+b[0])/2<1940) or (nz<-.7 and (a[0]+b[0])/2<1952):
   G.box('ph-black-paint',(L/2,4.16,-.07),(L,8,.11))
   for y in [4.1,7.85]:G.box('ph-red-paint',(L/2,y,-.17),(L,.72,.13))
   n=max(1,round(L/5.3));step=L/n
   for j in range(n+1):
    G.box('ph-white-paint',(j*step,4.45,-.26),(.55,8.55,.6),True)
    if j<n:
     u=(j+.5)*step;archpanel(G,u,5.1,1.65,2.05,'ph-glass')
     archpanel(G,u,.6,min(step-1,2.9),2.85,'ph-black-paint')
     G.box('ph-light-housing-paint',(u,3.4,-.25),(.2,.13,.18))
   rail(G,.25,L-.25,-.18,8.35)
   if nz>.3 and (a[0]+b[0])/2<1940:sign=(G,L)
  else:
   G.box('ph-red-paint',(L/2,4.1,-.06),(L,.5,.14));G.box('ph-red-paint',(L/2,8,-.06),(L,.35,.14))
   if L>8:
    for u in np.arange(2,L-1,4.5):
     archpanel(G,float(u),5.1,1.4,1.9,'ph-glass');G.box('ph-white-paint',(float(u),1.6,-.08),(1.4,2.5,.12))
    G.box('ph-service-paint',(L*.55,1.45,-.1),(1.2,2.5,.15))
 if sign:
  G,L=sign
  # Recessed balcony reads as a real upper-level porch; its floor and supporting piers stay distinct.
  G.box('ph-white-stucco',(L/2,6.1,-.2),(L-1,3.2,.15));G.box('ph-white-paint',(L/2,4.42,-.8),(L,.24,1.5),True)
  G.box('ph-red-paint',(L/2,8.18,-.8),(L,.65,1.5))
  for u in [1.1,L-1.1]:
   G.tube('ph-white-paint',(u,4.5,-1.3),(u,7.9,-1.3),.12,14)
   archpanel(G,u,5.1,1.4,2.2,'ph-glass',-.31)
  rail(G,.7,L-.7,-1.38,4.55)
  G.text('TOPLESS CABARET',(L/2,3.98,-1.61),.5,'ph-red-letter');G.text('OPEN 24 HRS',(L/2,3.55,-1.61),.34,'ph-red-letter')
  G.text('PEPPERMINT HIPPO',(L/2,7.98,-1.6),.32,'ph-gold-letter')
  # Scalloped crest silhouette observed above the corner bay; detailed hippo emblem remains a separate art task.
  profile=[(-L*.4,8.5),(-L*.4,9.45),(-L*.3,9.55),(-L*.25,9.9),(-L*.12,9.95),(0,10.25),(L*.12,9.95),(L*.25,9.9),(L*.3,9.55),(L*.4,9.45),(L*.4,8.5)]
  poly=Polygon([(x,y) for x,y in profile])
  for tri in triangles(poly):B.face('ph-red-paint',[G.p(L/2+x,y,-.65) for x,y in list(tri.exterior.coords)[:-1]])
  G.path('ph-white-paint',[(L/2+x,y,-.72) for x,y in profile],.08,8);G.text('PH',(L/2,8.75,-.8),1.05,'ph-gold-letter')
 # Northern vehicle canopy is not an extruded solid building.
 B.planar('ph-roof-paint',canopy,4.72);B.planar('ph-white-paint',canopy,4.23,True);B.shell(canopy,4.23,4.72,'ph-black-paint',roof=False,solid=False)
 for x,z in [(1951.7,-4053.5),(1956.5,-4053.1)]:W.box('ph-white-paint',(x,2.2,z),(.65,4.04,.7),True)
 for a,b in zip(list(canopy.exterior.coords),list(canopy.exterior.coords)[1:]):
  G,L,nx,nz=facade_frame(B,a,b,canopy,.04)
  if nx<-.7:G.text('PEPPERMINT HIPPO',(L/2,4.35,-.12),.4,'ph-gold-letter')
 apron=main.buffer(1.1,join_style=2).difference(main).union(canopy).union(Polygon([(1948,-4057),(1960,-4057),(1960,-4037),(1948,-4037)]).difference(main))
 B.planar('ph-paving',apron,.18,True)
 # Southern landscaped corner is bounded off the entrance approach.
 garden=Polygon([(1925,-4017),(1932,-4010),(1948,-4012),(1947,-4017)]).difference(main);B.planar('ph-gravel',garden,.2,True)
 for x,z,h in [(1930,-4015,2.6),(1935,-4014,3.1),(1941,-4014,2.5)]:palm(B,x,z,h,crown_scale=.45)
 for x,z in [(1936,-4029),(1944,-4028),(1966,-4027),(1978,-4025)]:W.box('ph-service-paint',(x,8.55,z),(1.5,.8,2))
 samples=[]
 for x in np.arange(1919,1986,.9):
  for z in np.arange(-4056,-4011,.9):
   q=Point(x,z)
   if apron.buffer(-.3).covers(q) and main.distance(q)>.4 and all(q.distance(Point(a,b))>.7 for a,b in [(1951.7,-4053.5),(1956.5,-4053.1)]):samples.append([float(x),.18,float(z)])
 Path('build/city-exteriors/peppermint-hippo-samples.json').write_text(json.dumps(samples))
 return dict(key=KEY,name='Peppermint Hippo 1531',center=[1953,0,-4032],bounds=[1918,-4058,1987,-4009],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
