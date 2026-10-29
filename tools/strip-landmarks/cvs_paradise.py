"""Original CVS Paradise shell from mapped footprint and linked facade photographs.
Heights and bay divisions are photo estimates; no unverified interior is represented.
"""
from common import *
KEY='cvs-paradise';IDS=['way/319208750']
def build(B):
 p=footprint(IDS[0]);B.property=KEY+'-exterior';B.source='podium/'+KEY;B.detail=0
 B.shell(p,.03,5.7,'cvs-stucco',roof=False);B.planar('cvs-roof',p,5.7)
 # Plane frames face west and south. Shell backs glass until a researched interior exists.
 frames=[(Frame(B,1958.46,843.935,math.pi/2+.01,y=0),22.61),(Frame(B,1999.035,849.19,math.pi+.01,y=0),34.98)]
 for F,length in frames:
  F.box('cvs-stone',(length/2,3.0,-.09),(length,6.0,.18))
  F.box('cvs-stack',(length/2,1.2,-.21),(length,2.4,.10))
  # Shallow arcing cornice follows the broad storefront fascia, tessellated smoothly.
  pts=[]
  for i in range(41):
   x=length*i/40;h=6.25+.42*math.sin(math.pi*i/40);pts.append((x,h,-.18))
  for j in range(40):
   x=(pts[j][0]+pts[j+1][0])/2;h=(pts[j][1]+pts[j+1][1])/2
   F.box('cvs-stone',(x,(h+6.0)/2,-.09),(length/40,h-6.0,.18))
   # Continuous swept cornice: shared boundaries eliminate stepped box end faces.
   profile=[(-.385,-.245),(-.385,-.155),(-.46,-.125),(-.46,.125),(-.54,.135),(-.54,.225),(.14,.225),(.14,-.245)]
   for q,r in zip(profile,profile[1:]+profile[:1]):
    B.face('cvs-cornice',[F.p(pts[j][0],pts[j][1]+q[1],q[0]),F.p(pts[j+1][0],pts[j+1][1]+q[1],q[0]),F.p(pts[j+1][0],pts[j+1][1]+r[1],r[0]),F.p(pts[j][0],pts[j][1]+r[1],r[0])])
  # Storefront clustered near entrance, blank stone/service bay beyond it.
  start=.3 if length<25 else length-19.2;end=min(length-.3,start+18.9)
  for x in np.linspace(start,end,4):
   F.box('cvs-stucco',(x,3.0,-.38),(.82,4.5,.72),True)
   F.box('cvs-stack',(x,.61,-.45),(.95,1.22,.86))
   F.box('cvs-plaque',(x,3.58,-.81),(.48,.55,.08));F.text('CVS',(x,3.58,-.86),.18,'cvs-cream')
  for a,b in zip(np.linspace(start,end,4)[:-1],np.linspace(start,end,4)[1:]):
   lo=a+.48;hi=b-.48
   F.box('cvs-glass',((lo+hi)/2,2.22,-.25),(hi-lo,2.12,.04))
   n=max(2,round((hi-lo)/1.1))
   for j in range(n+1):F.box('cvs-metal',(lo+(hi-lo)*j/n,2.22,-.30),(.045,2.2,.06))
   for yy in [1.13,1.75,3.30]:F.box('cvs-metal',((lo+hi)/2,yy,-.30),(hi-lo,.045,.07))
   # Generic opaque display panels are original artwork, not photographs/ad reproductions.
   for j in range(n):F.box('cvs-display'+str(j%3),(lo+(hi-lo)*(j+.5)/n,1.45,-.28),((hi-lo)/n-.09,.51,.025))
   F.box('cvs-metal',((lo+hi)/2,3.51,-.48),(hi-lo,.32,.74))
  F.box('cvs-stucco',((start+end)/2,4.55,-.38),(end-start+.8,1.6,.65))
  F.box('cvs-cornice',((start+end)/2,5.42,-.42),(end-start+1.15,.18,.96))
  F.text('CVS/pharmacy',((start+end)/2-.6,4.22,-.74),1.65,'cvs-red')
  badge=start+1.3 if length<25 else end-1.3
  F.box('cvs-red',(badge,4.58,-.77),(.82,.87,.08))
  F.text('24',(badge,4.74,-.83),.43,'cvs-white');F.text('HOURS',(badge,4.36,-.83),.17,'cvs-white')
  if length>25:F.text('Liquor',(5,5.15,-.22),.55,'cvs-red')
 # Southwest chamfer entrance: stone-footed piers, clerestory and tiered deep cap.
 T=Frame(B,1961.25,846.74,3*math.pi/4,y=0)
 T.box('cvs-stucco',(0,5.42,1.15),(8.0,4.85,2.7),True)
 for x in [-3.45,3.45]:
  T.box('cvs-stucco',(x,2.1,-.10),(1.08,4.2,.65),True)
  T.box('cvs-stack',(x,.64,-.17),(1.2,1.28,.78))
 T.box('cvs-glass',(0,1.65,-.08),(5.75,3.3,.08))
 for x in [-2.86,-1.43,0,1.43,2.86]:T.box('cvs-metal',(x,1.65,-.14),(.055,3.3,.08))
 for yy in [.12,2.35,3.28]:T.box('cvs-metal',(0,yy,-.15),(5.8,.055,.08))
 T.box('cvs-red',(0,5.08,-.25),(3.5,2.55,.14))
 T.text('24',(0,5.45,-.34),1.42,'cvs-white');T.text('HOURS',(0,4.43,-.34),.55,'cvs-white')
 T.box('cvs-glass',(0,7.36,-.24),(6.25,.85,.08))
 for x in np.linspace(-3.1,3.1,6):T.box('cvs-metal',(x,7.36,-.30),(.07,.94,.10))
 for yy,w,d,h in [(6.82,8.1,3.0,.18),(7.91,8.6,3.4,.24),(8.12,8.9,3.6,.10)]:T.box('cvs-cornice',(0,yy,1.05),(w,h,d))
 T.box('cvs-metal',(0,8.24,.42),(3.4,.12,.8))
 T.text('CVS',(0,8.30,.35),1.25,'cvs-red')
 # Back and north sides retain restrained service finish, roof parapet and equipment.
 coords=list(p.exterior.coords)
 for a,b in zip(coords,coords[1:]):B.tube('cvs-cornice',(a[0],5.95,a[1]),(b[0],5.95,b[1]),.10,6)
 for xx,zz in [(1972,831),(1983,831),(1991,839)]:
  B.box('cvs-equipment',(xx,6.25,zz),(2.4,1.1,1.8));B.box('cvs-metal',(xx,6.81,zz),(2.1,.04,1.5))
 R=Frame(B,1998.9,834,-math.pi/2)
 for u in [-8,5]:
  R.box('cvs-metal',(u,1.2,-.10),(1.3,2.4,.12));R.box('cvs-cornice',(u,2.5,-.35),(1.65,.16,.65))
  R.box('cvs-metal',(u+.4,1.15,-.19),(.05,.3,.06))
 # Narrow photographed entrance sidewalk, replacing no neighboring parking geometry.
 walk=p.buffer(2.25,join_style=2).difference(p).intersection(unary_union([box(1955,820,1958.5,844),box(1955,843.8,1999.3,852)]))
 B.shell(walk,-.08,.10,'cvs-paving',roof=False);B.planar('cvs-paving',walk,.10,True)
 routes=[dict(name='West frontage',points=[[1956.7,.10,823],[1956.7,.10,834],[1956.7,.10,842]]),dict(name='South approach',points=[[1963,.10,851],[1976,.10,851],[1995,.10,851]])]
 return dict(key=KEY,name='CVS Paradise Esplanade',center=[1979,0,835],bounds=list(p.buffer(3).bounds),structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=routes,hotelSources=[])
if __name__=='__main__':
 B=Meshes();meta=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(meta,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
