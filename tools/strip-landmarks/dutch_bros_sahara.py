"""Original site-specific Dutch Bros Sahara exterior; dimensions fitted from dated views."""
from common import *
KEY='dutch-bros-sahara';IDS=['way/943068958']
def build(B):
 B.property=KEY+'-exterior';B.source='retail/'+KEY;B.detail=0
 R=Frame(B,-1004.8,-3123.85,0,y=0)
 # Mapped northwest projection is a canopy, not enclosed restaurant floor area.
 main=R.poly([(-4.3,0),(4.3,0),(4.3,12.65),(1.7,12.65),(1.7,12.96),(-4.3,12.96)])
 B.shell(main,.02,4.7,'db-stucco',roof=False);B.planar('db-membrane',main,4.7)
 for a,b in zip(list(main.exterior.coords),list(main.exterior.coords)[1:]):
  dx,dz=b[0]-a[0],b[1]-a[1];F=Frame(B,(a[0]+b[0])/2,(a[1]+b[1])/2,math.atan2(-dz,dx),y=0);L=math.hypot(dx,dz)
  F.box('db-coping',(0,4.72,0),(L+.12,.16,.3))
  F.box('db-stone',(0,.52,0),(L,1.0,.16))
  F.box('db-cap',(0,1.05,0),(L,.09,.23))
 # Blue corrugated north/east parapet fields and taller cream address pier.
 R.box('db-blue',(-.5,3.25,-.13),(7.7,4.4,.15))
 for u in np.arange(-4.3,3.36,.18):R.box('db-rib',(float(u),3.25,-.225),(.045,4.4,.035))
 R.box('db-coping',(-.5,5.48,-.14),(7.85,.14,.35))
 R.box('db-stucco',(3.65,3.13,.28),(1.35,6.26,1.0),True)
 R.box('db-coping',(3.65,6.29,.28),(1.5,.10,1.12))
 R.text('3121',(3.65,4.38,-.26),.3,'db-letter')
 # Original simplified windmill silhouette, no copied image texture.
 R.box('db-letter',(3.65,5.31,-.28),(.10,.68,.03))
 for a in [math.pi/4,-math.pi/4]:
  pts=[]
  for x,y in [(-.48,-.055),(.48,-.055),(.48,.055),(-.48,.055)]:pts.append(R.p(3.65+x*math.cos(a)-y*math.sin(a),5.52+x*math.sin(a)+y*math.cos(a),-.30))
  B.face('db-letter',pts)
 R.text('DUTCH BROS',(-.55,4.36,-.26),.62,'db-letter')
 for i,(mat,w) in enumerate([('db-red',3.1),('db-yellow',3.6),('db-lightblue',4.1)]):R.box(mat,(-.55,3.89-i*.12,-.26),(w,.065,.035))
 # Flat west canopy on stone piers. Upper deck, fascia and undersoffit separated.
 R.box('db-membrane',(-4.8,3.28,2.8),(9.2,.14,6.2),True)
 for u in [-9.35,-.25]:R.box('db-smoothalloy',(u,3.20,2.8),(.15,.32,6.3))
 for v in [-.35,5.95]:R.box('db-smoothalloy',(-4.8,3.20,v),(9.25,.32,.15))
 for u,v in [(-9.15,.0),(-9.15,5.65),(-4.65,5.65)]:
  R.box('db-stone',(u,.7,v),(.74,1.4,.74),True);R.box('db-cap',(u,1.43,v),(.86,.10,.86));R.box('db-smoothalloy',(u,2.29,v),(.28,1.65,.28),True)
  for row in range(7):
   for col in range(3):
    for side in [-1,1]:R.box('db-stone'+str((row+col)%3),(u-.25+col*.25,.1+row*.18,v+side*.38),(.23,.16,.035))
 for v in [.5,2.8,5.1]:R.box('db-soffit',(-4.8,3.185,v),(8.9,.035,.05))
 # Walk-up glazing on west wall and pickup glazing on east wall; service-only windows.
 for x,side in [(-4.35,-1),(4.35,1)]:
  for v in ([2.4] if side<0 else [5.0,9.0]):
   R.box('db-glass',(x,1.98,v),(.07,1.45,2.1))
   for z in [v-1.09,v,v+1.09]:R.box('db-mullion',(x+side*.06,1.98,z),(.1,1.58,.055))
   for y in [1.20,2.77]:R.box('db-mullion',(x+side*.06,y,v),(.11,.07,2.23))
   R.box('db-smoothalloy',(x+side*.28,1.16,v),(.62,.10,2.4))
 # Solid staff door on rear; inferred fitted service detail, not a public entry.
 R.box('db-mullion',(-2.5,1.17,13.03),(1.12,2.3,.07));R.box('db-smoothalloy',(-2.5,1.17,13.08),(.99,2.16,.035))
 R.tube('db-cap',(-2.13,1.1,13.11),(-2.13,1.4,13.11),.018,6)
 # Canopy walking surface remains at street datum, no curb blocking approach.
 R.box('db-paving',(-6.85,.14,2.8),(4.6,.28,6.35),True)
 B.upface('db-paving',[R.p(-9.1,.28,5.98),R.p(-4.6,.28,5.98),R.p(-4.6,0,7.5),R.p(-9.1,0,7.5)],True)
 for v in [.1,2.2,4.3,5.9]:R.box('db-joint',(-6.85,.284,v),(4.5,.006,.014))
 for u in [-7.9,-5.7]:R.box('db-joint',(u,.284,2.8),(.014,.006,6.2))
 for v in [3,8.3]:
  R.box('db-equipment',(0,5.05,v),(1.8,.7,1.6));R.box('db-smoothalloy',(0,5.43,v),(1.9,.10,1.7))
  for z in np.arange(v-.6,v+.61,.16):R.box('db-mullion',(0,5.49,float(z)),(1.55,.025,.045))
 for v in [2,10]:
  R.tube('db-pipe',(4.43,.1,v),(4.43,4.7,v),.045,8)
 routes=[dict(name='Open west canopy walk-up',points=[R.p(-6.8,.28,-2),R.p(-6.8,.28,1),R.p(-6.8,.28,3),R.p(-6.8,.28,5.8),R.p(-6.8,0,8)]),dict(name='East pickup lane',points=[R.p(6.5,0,-2),R.p(6.5,0,4),R.p(6.5,0,10),R.p(6.5,0,15)])]
 return dict(key=KEY,name='Dutch Bros West Sahara',center=[-1007,0,-3117],bounds=list(footprint(IDS[0]).bounds),structural=True,hotelSources=[],exteriorOnly=True,portals=[],zones=[],lights=[],routes=routes)
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
