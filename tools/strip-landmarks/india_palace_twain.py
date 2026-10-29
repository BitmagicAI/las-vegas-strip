"""India Palace: original geometry from official/dated facade references; elevations estimated."""
from common import *
KEY='india-palace-twain';ID='way/390003971'
def build(B):
 p=footprint(ID);F=Frame(B,1915.68,-554.2,math.pi,y=0)
 B.property=KEY+'-exterior';B.source='podium/'+KEY;B.detail=0
 # Front entry recess is cut from the original shell and closed by a recessed glazed door.
 op=dict(p=F.p(-1,.14,0),yaw=math.pi,width=5.6,height=3.25)
 B.shell(p,.02,4.5,'ip-ochre',roof=False,openings=[op]);B.planar('ip-roof',p,4.48);B.planar('ip-paving',p,.14,True)
 F.box('ip-red',(5,3.15,-.1),(5.4,6.3,.45),True)
 F.box('ip-stone-base',(-1,4.2,.14),(7.0,2.15,.55))
 for u in [-4.15,2.15]:F.box('ip-stone-base',(u,1.65,.14),(.7,3.3,.55),True)
 # Individually staggered stone strips, with varied projection and length, no image copying.
 rng=random.Random(334)
 for row in range(42):
  h=.17+row*.122;u=-4.5
  while u<2.5:
   w=min(rng.uniform(.25,.72),2.5-u)
   if h>3.25 or u+w<=-3.8 or u>=1.8:
    F.box('ip-stone-'+str(rng.randrange(5)),(u+w/2,h,.44+rng.uniform(0,.025)),(max(.01,w-.015),.105,.07))
   u+=w
 # Recess back wall and asymmetric door as seen in the frontage photograph.
 F.box('ip-ochre',(-1,1.7,-1.08),(5.6,3.1,.14),True)
 F.box('ip-glass',(-3.05,1.30,-.98),(1.2,2.32,.05))
 for u in [-3.68,-2.42]:F.box('ip-frame',(u,1.3,-.92),(.055,2.4,.08))
 for h in [.13,2.49]:F.box('ip-frame',(-3.05,h,-.92),(1.3,.055,.08))
 F.box('ip-steel',(-2.55,1.24,-.86),(.04,.5,.05))
 F.box('ip-cream',(-.3,2.23,-.95),(2.8,.68,.07));F.text('India Palace',(-.3,2.23,-.89),.36,'ip-dark',back=True)
 # Right glazed bay has white mullions and a solid opaque backing.
 F.box('ip-glass',(5,1.66,.18),(3.7,2.95,.045))
 for u in [3.13,4.37,5.63,6.87]:F.box('ip-cream',(u,1.66,.23),(.065,3.02,.07))
 for h in [.16,2.45,3.16]:F.box('ip-cream',(5,h,.23),(3.8,.065,.07))
 # Thin cream suspended canopies, anchoring blocks and rods.
 for u,w,h in [(-1,7.4,3.6),(5,4.7,3.58),(-6.2,2.6,3.4)]:
  F.box('ip-cream',(u,h,.7),(w,.17,1.4))
  for off in [-w*.32,w*.32]:
   F.box('ip-cream',(u+off,h+1.08,.25),(.25,.25,.08))
   F.tube('ip-steel',(u+off,h+1.08,.30),(u+off,h+.10,1.28),.017,8)
 # Red panel joints and coping; low left wing distinct from taller right parapet.
 F.box('ip-cap',(5,6.33,-.05),(5.5,.09,.55));F.box('ip-cap',(-1,5.32,.12),(7.1,.08,.62))
 for u in [3.1,5,6.9]:F.box('ip-joint',(u,4.85,.135),(.012,2.8,.02))
 F.text('india palace',(5,5.45,.22),.55,'ip-cream',back=True)
 F.box('ip-dark',(-6.15,2,.10),(2.6,3.5,.08))
 F.box('ip-ochre',(-6.15,1.8,.17),(2.45,3.1,.06))
 for u in [-4.02,2.02,7.04]:
  F.box('ip-dark',(u,2.45,.55),(.11,.42,.12));F.box('ip-lamp',(u,2.22,.55),(.08,.04,.08))
 F.box('ip-paving',(0,.07,.75),(15.5,.14,1.5),True)
 # Side/rear servicing remains estimated and explicitly recorded.
 for u,v in [(-3,-6),(3,-12)]:
  F.box('ip-steel',(u,4.9,v),(1.7,.8,1.4));F.box('ip-dark',(u,5.33,v),(1.5,.06,1.2))
  for k in range(8):F.box('ip-frame',(u-.64+k*.18,5.37,v),(.035,.025,1.1))
 F.box('ip-dark',(1,1.3,-17.75),(1.2,2.4,.08))
 route=[F.p(-3.05,.14,v) for v in [2,1,.3,-.45]]
 return dict(key=KEY,name='India Palace Twain',center=[p.centroid.x,0,p.centroid.y],bounds=[p.bounds[0]-1,p.bounds[1]-3,p.bounds[2]+1,p.bounds[3]+1],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],hotelSources=[],routes=[dict(name='Recessed restaurant entrance and return',points=route)])
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
