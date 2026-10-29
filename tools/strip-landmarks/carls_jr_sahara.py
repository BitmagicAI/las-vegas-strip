"""Original Sahara restaurant exterior; dimensions/services inferred where hidden."""
from common import *
KEY='carls-jr-sahara';ID='way/926281500'
def build(B):
 p=footprint(ID);B.property=KEY+'-exterior';B.source='podium/'+KEY;B.detail=0
 F=Frame(B,-1784.3,-3194.1,0,y=0)
 B.shell(p,.08,4.35,'cj-stucco',roof=False);B.planar('cj-roof',p,4.35);B.planar('cj-paving',p,.14,True)
 # Cream sill and dark-framed south windows beneath the red wraparound canopy.
 def window(G,u,z,w,h=1.65,base=1.0):
  G.box('cj-frame',(u,base+h/2,z),(w,h,.12));G.box('cj-glass',(u,base+h/2,z+.075),(w-.12,h-.14,.04))
  for x in np.linspace(u-w/2,u+w/2,max(2,round(w/.95)+1)):G.box('cj-frame',(float(x),base+h/2,z+.12),(.055,h,.07))
  G.box('cj-sill',(u,base-.12,z+.1),(w+.2,.24,.22))
 def canopy(G,u,z,w):
  G.box('cj-red',(u,3.13,z+.1),(w,.38,.75));G.box('cj-red-dark',(u,2.91,z+.1),(w,.07,.8))
  G.box('cj-trim',(u,3.39,z+.1),(w,.08,.8))
 window(F,2,.18,8.8);canopy(F,2,.2,9.5)
 # Southwest setback entrance, seen left of the front window row.
 W=Frame(B,-1788.9,-3195.80,0,y=0)
 window(W,0,.10,2.5,2.35,.18);W.box('cj-frame',(0,1.32,.27),(.075,2.35,.09))
 W.box('cj-handle',(.24,1.24,.34),(.05,.45,.06));canopy(W,0,.15,3.3)
 W.text('3866',(0,2.65,.3),.26,'cj-letter',back=True)
 # Broad red tile mansard with a raised flat cream roof center.
 outer=[(-7.55,-.3),(7.5,-.3),(7.5,-24.2),(-7.55,-24.2)]
 inner=[(-5.4,-2.8),(5.4,-2.8),(5.4,-21.7),(-5.4,-21.7)]
 for i in range(4):
  j=(i+1)%4
  B.upface('cj-tile',[F.p(*q) for q in [(outer[i][0],4.25,outer[i][1]),(outer[j][0],4.25,outer[j][1]),(inner[j][0],5.8,inner[j][1]),(inner[i][0],5.8,inner[i][1])]])
  a,b=outer[i],outer[j];c,d=inner[i],inner[j];n=math.ceil(math.dist(a,b)/.22)
  for k in range(n+1):
   t=k/n;u=a[0]+(b[0]-a[0])*t;v=a[1]+(b[1]-a[1])*t;u2=c[0]+(d[0]-c[0])*t;v2=c[1]+(d[1]-c[1])*t
   F.tube('cj-tile-'+str(k%3),(u,4.3,v),(u2,5.85,v2),.045,7)
 F.box('cj-trim',(0,5.84,-12.25),(11.1,.17,19.2));F.box('cj-roof',(0,5.87,-12.25),(10.8,.08,18.9))
 # East entrance tower: gable roof and red fabric canopy visible in location-specific panorama.
 E=Frame(B,-1776.75,-3201.5,math.pi/2,y=0)
 E.box('cj-stucco',(0,3.45,-.4),(4.3,6.9,2.1),True)
 B.face('cj-stucco',[E.p(*q) for q in [(-2.15,6.9,.66),(2.15,6.9,.66),(0,8.1,.66)]])
 for sign in [-1,1]:
  B.upface('cj-tile',[E.p(0,8.16,.95),E.p(sign*2.4,6.95,.95),E.p(sign*2.4,6.95,-2),E.p(0,8.16,-2)])
  E.tube('cj-trim',(0,8.12,.98),(sign*2.4,6.9,.98),.07,10)
 window(E,0,.72,2.35,2.4,.18);E.box('cj-frame',(0,1.4,.90),(.06,2.4,.1));E.box('cj-handle',(.23,1.2,.99),(.05,.45,.07))
 # Sloped red canopy, solid sides and raised lettering; original simplified identity.
 B.face('cj-red',[E.p(*q) for q in [(-1.7,3.5,1.6),(1.7,3.5,1.6),(1.7,4.25,.68),(-1.7,4.25,.68)]])
 E.box('cj-red',(0,3.40,1.6),(3.4,.2,.10));E.text("Carl's Jr.",(0,6.15,.72),.62,'cj-red',back=True)
 for u,z,w in [(-5.2,.12,5.0),(5.4,.12,4.7)]:window(E,u,z,w);canopy(E,u,z,w+.4)
 # West drive-through window in mapped recess; services are approximate.
 D=Frame(B,-1792.1,-3209.7,-math.pi/2,y=0);window(D,0,.18,1.7,1.35,1.15);canopy(D,0,.25,2.5)
 D.box('cj-metal',(0,1.08,.45),(2.1,.14,.7));D.box('cj-red',(3.1,2,.3),(1.1,2,.15));D.text('PICK UP',(0,3.65,.2),.30,'cj-red',back=True)
 for u,v in [(-2,-11),(2,-16)]:
  F.box('cj-metal',(u,6.25,v),(1.8,.75,1.35));F.box('cj-dark',(u,6.65,v),(1.9,.08,1.45))
 F.box('cj-paving',(-4.6,.07,.9),(7.6,.14,2.1),True)
 F.box('cj-gravel',(2,.13,.85),(8.2,.1,1.1))
 for u in np.arange(-1.7,6,.7):F.lathe('cj-leaf',float(u),.8,[(.18,0),(.25,.31),(.68,.34),(.9,.18),(.95,0)],11)
 # Low street monument sign; footprint inferred, outside the public approach.
 F.box('cj-dark',(-8.5,.6,3.4),(3.2,1.2,.65),True);F.box('cj-red',(-8.5,1.65,3.4),(3.4,.9,.6))
 F.text("Carl's Jr.",(-8.5,1.67,3.73),.49,'cj-letter',back=True);F.text('3866',(-8.5,.6,3.74),.36,'cj-letter',back=True)
 route=[W.p(u,.14,v) for u,v in [(0,2.2),(0,1.2),(0,.6)]]
 return dict(key=KEY,name="Carl's Jr. Sahara",center=[p.centroid.x,0,p.centroid.y],bounds=[p.bounds[0]-3,p.bounds[1]-1,p.bounds[2]+3,p.bounds[3]+5],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],hotelSources=[],routes=[dict(name='Restaurant approach',points=route)])
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
