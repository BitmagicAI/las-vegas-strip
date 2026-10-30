"""2601 Westwood source-only first pass; no shared city installer.
Main facade: November 2021 Street View; plan: owner's 2023 brochure.
Height and roof pitch estimated. Annex and public interior pending review.
"""
from common import *
KEY='westwood-2601'
COLORS={'w26-cream-stucco':'d5c9a5','w26-salmon-stucco':'b77568','w26-trim-paint':'eee5ce','w26-glass':'354345','w26-frame-paint':'9c9f93','w26-vent-paint':'9d9476','w26-roof-tile':'a56f51','w26-roof':'a9a69a','w26-canopy-paint':'9c5752','w26-paving-concrete':'918878'}
def build(B):
 B.property=KEY+'-exterior';B.source='commercial/'+KEY;B.detail=0
 p=footprint('way/1018431840')
 # Mapped footprint is wider than the brochure's 41 ft room bar. Preserve its
 # boundary for now; reconcile the roof/overhang before installation.
 coords=list(p.exterior.coords)
 a,b=max(zip(coords,coords[1:]),key=lambda ab:math.dist(*ab))
 dx,dz=b[0]-a[0],b[1]-a[1];yaw=math.atan2(-dz,dx)
 if math.cos(yaw)<0:yaw+=math.pi
 co,si=math.cos(yaw),math.sin(yaw)
 us=[x*co-z*si for x,z in coords];vs=[x*si+z*co for x,z in coords]
 u=(min(us)+max(us))/2;v=(min(vs)+max(vs))/2
 center=Point(u*co+v*si,-u*si+v*co)
 width=max(us)-min(us);depth=max(vs)-min(vs)
 F=Frame(B,center.x,center.y,yaw,y=0)
 B.shell(p,0,9.6,'w26-cream-stucco',roof=False)
 B.planar('w26-roof',p,9.55)
 # Cream facade with three-storey salmon arch panels and paired guest windows.
 # Front faces Westwood (positive local z); unseen rear repetition is inferred.
 for side in [-1,1]:
  z=side*(depth/2+.08)
  F.box('w26-trim-paint',(0,9.55,z),(width+.8,.18,.55))
  for bay in range(8):
   u=(bay-3.5)*width/8
   if side==1:
    F.box('w26-salmon-stucco',(u,4.25,z),(2.15,8.1,.10))
    # Rounded crown formed as an original planar fan, with projecting trim.
    points=[F.p(u,8.3,z+side*.07)]+[F.p(u+1.075*math.cos(t),8.3+1.075*math.sin(t),z+side*.07) for t in np.linspace(0,math.pi,17)]
    for j in range(1,len(points)-1):B.face('w26-salmon-stucco',[points[0],points[j],points[j+1]])
    F.arch(u,z+side*.16,2.4,9.5,'w26-trim-paint',.10,base=.15)
   for offset in [-2.5,2.5]:
    x=u+offset
    if abs(x)>width/2-1:continue
    for floor in range(3):
     y=1.55+floor*3.03
     # Entry canopy masks the central ground-floor bays in the reference.
     if side==1 and floor==0 and abs(x)<3.3:continue
     F.box('w26-frame-paint',(x,y,z+side*.10),(1.92,1.45,.12))
     F.box('w26-glass',(x,y,z+side*.18),(1.78,1.31,.045))
     F.box('w26-frame-paint',(x,y,z+side*.23),(.055,1.35,.04))
     F.box('w26-vent-paint',(x,y-1.02,z+side*.14),(1.2,.46,.12))
     for row in range(4):F.box('w26-frame-paint',(x,y-1.19+row*.10,z+side*.22),(1.15,.025,.04))
  # Sloped tile skirt; individual curved ribs supply actual silhouette relief.
  for x in np.arange(-width/2-.3,width/2+.3,.25):
   F.tube('w26-roof-tile',(x,9.67,side*(depth/2+.48)),(x,10.25,side*(depth/2-1.3)),.075,6)
 # Main arrival canopy, supports and closed glazing (interior not yet authored).
 z=depth/2
 F.box('w26-frame-paint',(0,1.55,z+.16),(4.2,3.1,.12),True)
 F.box('w26-glass',(0,1.55,z+.25),(4.0,2.95,.06))
 for x in [-2,0,2]:F.box('w26-frame-paint',(x,1.55,z+.3),(.075,3.05,.08))
 F.box('w26-canopy-paint',(0,3.65,z+2.2),(6.3,.60,4.4))
 F.box('w26-trim-paint',(0,3.65,z+4.43),(4.5,.48,.05))
 F.text('2601',(0,3.65,z+4.48),.3,'w26-frame-paint',back=True)
 for x in [-2.8,2.8]:F.box('w26-cream-stucco',(x,1.65,z+3.9),(.18,3.3,.18),True)
 return dict(key=KEY,name='2601 Westwood — source study',center=[center.x,4,center.y],bounds=list(p.bounds),structural=True,hotelSources=[],exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],sourceOnly=True,remaining=['Annex reference and geometry','Footprint depth reconciliation','Pool and entry ramp','Public interior','Optimization and installed validation'])
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
