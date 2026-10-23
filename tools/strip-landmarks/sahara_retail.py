"""Sahara/Strip retail: Earth2022 reference silhouettes, mapped plans.
Heights and sign dimensions are visual estimates. Existing roads untouched.
"""
from common import *
from forum_shops import facade_frame
KEY='saharaRetail';IDS=['way/'+s for s in ['160585309','276426488','276426487','276427173','276427175']]
def equipment(B,p,h):
 for x in np.arange(p.bounds[0]+4,p.bounds[2]-2,12):
  for z in np.arange(p.bounds[1]+4,p.bounds[3]-2,13):
   if p.contains(box(x-1.2,z-1,x+1.2,z+1)):
    B.box('st-grey',(x,h+.4,z),(2.3,.8,1.8));B.box('silver',(x,h+.84,z),(2.4,.08,1.9))
def glazing(F,x,w,top=3.1):
 F.box('darkglass',(x,(top+.4)/2,-.19),(w,top-.4,.08))
 for u in [-w/2,0,w/2]:F.box('silver',(x+u,(top+.4)/2,-.25),(.06,top-.4,.07))
 for y in [.4,top]:F.box('silver',(x,y,-.25),(w,.06,.07))
def exterior(B):
 B.property=KEY+'-exterior';B.detail=0;ps=[footprint(i) for i in IDS]
 for idx,p in enumerate(ps):
  B.source='retail/'+IDS[idx]
  h=[4.6,11.8,6.6,5.5,4.2][idx];mat=['sr-red-stucco','sr-cream','sr-tan-stucco','sr-brick','sr-cream'][idx]
  B.shell(p,.24,h,mat,roof=False);B.planar('st-roof',p,h,True);B.planar('tile',p,.24,True)
  equipment(B,p,h)
  # Walgreens rounded street edge keeps the mapped curved footprint, not a box.
  for pp in parts(p):
   cc=list(pp.exterior.coords)
   for a,b in zip(cc,cc[1:]):
    F,L,nx,nz=facade_frame(B,a,b,pp,0)
    if L<.2:continue
    front=(nx>.4 or nz>.6) if idx==0 else ((nx<-.3 or nz>.6) if idx==1 else (nx>.3 or (idx==4 and nz>.3)))
    F.box('sr-cream',(L/2,h+.12,-.08),(L,.24,.3))
    if idx==2:
     # Two-level parking shell with horizontal openings and square supports.
     if L>8:
      for y in [1.7,4.7]:
       F.box('st-shadow',(L/2,y,-.16),(L-.6,1.55,.06))
       for x in np.arange(1,L,6):F.box('sr-tan-stucco',(x,y,-.24),(.45,1.7,.2))
     continue
    if front:
     for x in np.arange(1.6,L-1,3.1):glazing(F,x,min(2.7,L-1))
     if idx==0:
      # Pink/red roadside store wraps a triangular parking forecourt.
      F.box('sr-cream',(L/2,3.5,-2),(L,.25,4),True)
      F.box('sr-red-stucco',(L/2,3.76,-4),(L,.46,.13))
      for x in np.arange(1,L,6.5):F.box('sr-yellow',(x,1.75,-3.8),(.13,3.5,.13),True)
      F.box('white',(L/2,5.05,-.18),(L,1.7,.16))
      if L>50:F.text("WORLD'S LARGEST GIFT SHOP",(L/2,4.75,-.30),min(1.7,L/24),'sr-dark')
      elif L>25:F.text('GIFTS  SOUVENIRS',(L/2,4.8,-.30),1.05,'sr-red-stucco')
      elif L>15:F.text('LIQUOR STORE',(L/2,4.8,-.30),.85,'sr-red-stucco')
     elif idx==1:
      F.box('sr-cream',(L/2,4.3,-.2),(L,1.7,.3))
      F.box('sr-billboard',(L/2,8.1,-.27),(L,4.9,.14))
      for y in [5.55,10.6,11.7]:F.box('silver',(L/2,y,-.38),(L,.1,.13))
      if L>16:F.text('Walgreens',(L/2,4.05,-.42),1.35,'sr-red-stucco')
      for x in np.arange(.2,L,4):F.box('silver',(x,8.1,-.36),(.04,4.9,.08))
     elif idx==3:
      # Long low retail arcade; higher north end is authored below.
      F.box('sr-cream',(L/2,3.5,-1.0),(L,.3,2),True)
      for x in np.arange(1,L,7):F.box('sr-tan-stucco',(x,1.8,-1.65),(.42,3.6,.42),True)
      if L>45:
       for x,label in [(L*.23,'SUBWAY')]:F.text(label,(x,4.28,-.24),.64,'white')
     elif idx==4:
      F.box('sr-dark',(L/2,3.6,-.3),(L,.6,.5))
      if L>12:F.text("McDonald's",(L/2,3.32,-.6),.67,'white')
    else:
     for x in np.arange(2,L,6):F.box('sr-joint',(x,h/2,-.04),(.025,h-.3,.04))
     if L>12:F.box('sr-dark',(L/2,1.6,-.1),(1.5,2.8,.1))
  if idx==0:
   # Round sign at the inner elbow; both faces and a physical perimeter ring.
   F=Frame(B,1351,-3147,-3*math.pi/4,y=0)
   pts=[F.p(6.1*math.cos(a),10+6.1*math.sin(a),-.2) for a in np.linspace(0,math.tau,64,endpoint=False)]
   B.face('sr-red-stucco',pts);B.face('sr-red-stucco',[F.p(6.1*math.cos(a),10+6.1*math.sin(a),.15) for a in np.linspace(0,math.tau,64,endpoint=False)][::-1])
   F.path('sr-yellow',[(6.12*math.cos(a),10+6.12*math.sin(a),-.24) for a in np.linspace(0,math.tau,65)],.10,8)
   for text,y,size in [('BONANZA',12.4,1.15),('GIFT',10.7,1.2),('& SOUVENIR',9.2,.72),('SHOPS',7.7,1.1)]:F.text(text,(0,y,-.28),size,'sr-yellow')
   for x in [-3,3]:F.box('sr-dark',(x,5.4,.2),(.18,3,.18))
  if idx==1:
   # Pink end pier at the Sahara corner seen beside the curved billboard band.
   B.box('sr-pink-stucco',(1485,6.8,-3104),(3,13.6,3),True)
   for y in [3,6,9,12]:B.box('darkglass',(1486.55,y,-3104),( .08,1.2,1.3))
  if idx==3:
   north=p.intersection(box(1590,-3235,1630,-3200))
   B.shell(north,h,9,'sr-cream',roof=False);B.planar('st-roof',north,9,True)
   for pp in parts(north):
    cc=list(pp.exterior.coords)
    for a,b in zip(cc,cc[1:]):
     F,L,nx,nz=facade_frame(B,a,b,pp,0)
     if L<3:continue
     for x in np.arange(1.4,L-1,2.7):F.box('darkglass',(x,7.2,-.12),(1.6,1.7,.08))
 return dict(key=KEY,name='Bonanza and Sahara retail exteriors',center=[1470,0,-3150],bounds=list(unary_union(ps).bounds),structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],views={})
