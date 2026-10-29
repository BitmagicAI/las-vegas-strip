"""Original NuLeaf Twain facade, fitted to mapped shell and public photographs.
No photo pixels or concealed interior plan are reproduced. Dimensions estimated.
"""
from common import *
KEY='nuleaf-twain';IDS=['way/331347657']
def build(B):
 p=footprint(IDS[0]);F=Frame(B,1721.21,-606.80,0,y=0)
 B.property=KEY+'-exterior';B.source='retail/'+KEY;B.detail=0
 B.shell(p,0,5.7,'nl-stucco',roof=False);B.planar('nl-roof-paint',p,5.7)
 # Tall charcoal fascia and pale perimeter coping.
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  dx,dz=b[0]-a[0],b[1]-a[1];w=math.hypot(dx,dz);R=Frame(B,(a[0]+b[0])/2,(a[1]+b[1])/2,math.atan2(-dz,dx),y=0)
  R.box('nl-charcoal',(0,4.9,0),(w,1.6,.14));R.box('nl-trim-paint',(0,5.75,0),(w+.08,.12,.22));R.box('nl-trim-paint',(0,4.08,0),(w,.14,.2))
 # Two recessed horizontal panel bays to west, white narrow block piers.
 for lo,hi in [(-10.8,-5.6),(-4.9,-.6)]:
  F.box('nl-panel-dark',((lo+hi)/2,2.03,.09),(hi-lo,4.0,.12))
  # Continuous skins prevent bright subpixel cracks between individual boards.
  F.box('nl-panel-brown',((lo+hi)/2,1.02,.20),(hi-lo,1.68,.10))
  F.box('nl-panel-dark',((lo+hi)/2,2.93,.20),(hi-lo,2.14,.10))
  # Horizontal joints are filtered into the finish map, avoiding thin-mesh aliasing.
 for u in [-10.98,-5.25,-.25,3.2,7.2,10.98]:F.box('nl-block',(u,2.05,.16),(.48,4.1,.35))
 # Closed entrance: no guessed public interior or walk-through portal.
 F.box('nl-doorframe',(1.0,1.38,.18),(1.46,2.76,.3),True)
 F.box('nl-glass',(1.0,1.39,.35),(1.18,2.44,.04));F.box('nl-trim-paint',(1.55,1.2,.4),(.04,.52,.06))
 F.box('nl-charcoal',(1.0,2.85,.3),(1.75,.22,.48))
 for lo,hi in [(0,2.8),(3.5,6.9),(7.5,10.6)]:
  for u in np.linspace(lo+.25,hi-.25,4):
   F.box('nl-glass',(float(u),3.55,.13),((hi-lo)/4-.08,.65,.04))
  F.box('nl-trim-paint',((lo+hi)/2,3.15,.19),(hi-lo,.08,.12))
  F.box('nl-trim-paint',((lo+hi)/2,3.94,.19),(hi-lo,.08,.12))
 # Raised signage and restrained wall-mounted fixture hardware.
 F.text('430',(-8.7,4.88,.18),.65,'nl-white',back=True)
 F.text('NuLeaf',(-.3,4.55,.18),1.03,'nl-green',back=True)
 F.box('nl-green',(-4.6,5.0,.22),(1.05,.33,.22));F.box('nl-green',(-4.6,5.0,.22),(.33,1.05,.22))
 for u in [-9,-4,3,9]:
  F.tube('nl-metal-paint',(u,5.4,.1),(u,5.3,.55),.035,8);F.box('nl-metal-paint',(u,5.27,.55),(.18,.13,.21));F.box('nl-lamp',(u,5.2,.55),(.15,.02,.18))
 # Freestanding photographed sign; fitted position and dimensions, no price data.
 S=Frame(B,1731,-601.5,0,y=0)
 S.box('nl-charcoal',(0,2.9,0),(1.35,5.8,.58),True)
 S.box('nl-green',(0,6.25,0),(3.3,1.8,.62));S.box('nl-white',(0,6.25,.33),(3.15,1.65,.04))
 S.text('NuLeaf',(0,6.15,.37),.6,'nl-green',back=True);S.text('MARIJUANA DISPENSARY',(0,5.75,.37),.17,'nl-charcoal',back=True)
 # Low wall planters and shade umbrellas seen in the November2024 frontage.
 for u in [-9.7,-4.2,3.7,9.4]:
  F.box('nl-planter',(u,.35,.62),(.48,.7,.48),True);F.box('nl-soil',(u,.71,.62),(.4,.02,.4))
  for k in range(7):
   a=k*math.tau/7;center=F.p(u,.72,.62);tip=F.p(u+.32*math.cos(a),1.15,.62+.32*math.sin(a))
   B.face('nl-leaf',[center,F.p(u+.08*math.cos(a+.9),.91,.62+.08*math.sin(a+.9)),tip]);B.face('nl-leaf',[center,tip,F.p(u+.08*math.cos(a-.9),.91,.62+.08*math.sin(a-.9))])
 for u in [5.2,8.0]:
  F.tube('nl-metal-paint',(u,.05,1.0),(u,2.8,1.0),.028,10)
  for k in range(8):
   a=k*math.tau/8;b=(k+1)*math.tau/8
   B.upface('nl-umbrella',[F.p(u,2.9,1),F.p(u+1.15*math.cos(a),2.6,1+1.15*math.sin(a)),F.p(u+1.15*math.cos(b),2.6,1+1.15*math.sin(b))])
 # Roof equipment is generic service massing; concealed arrangement unverified.
 for x,z in [(1716,-613),(1726,-613)]:
  B.box('nl-metal-paint',(x,5.95,z),(1.6,.5,1.1));B.box('nl-charcoal',(x,6.22,z),(1.45,.03,.95))
 return dict(key=KEY,name='NuLeaf Twain Avenue',center=[p.centroid.x,0,p.centroid.y],bounds=list(p.bounds),structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],hotelSources=[],routes=[dict(name='Public frontage approach',points=[[1722,.15,-595],[1722,.15,-600],[1722,.15,-604.5],[1715,.15,-604.5]])])
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
