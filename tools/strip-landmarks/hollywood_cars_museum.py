"""Hollywood Cars Museum warehouse, original exterior geometry.
Street View establishes the SOUTH entrance of way/225705142. The survey's
museum name on adjacent way/225705143 is not used for replacement ownership.
Heights, service-bay spacing and ramp dimensions remain inferred.
"""
from common import *
KEY='hollywood-cars-museum'
def build(B):
 B.property=KEY+'-exterior';B.source='podium/'+KEY;B.detail=0
 F=Frame(B,0,0,y=0);p=footprint('way/225705142');lo,zn,hi,zs=p.bounds;mid=(lo+hi)/2
 B.shell(p,.02,5.7,'hcm-metal-paint',roof=False)
 # Shallow industrial roof, hand-authored from the observed warehouse form.
 for half in [p.intersection(box(lo-1,zn-1,mid,zs+1)),p.intersection(box(mid,zn-1,hi+1,zs+1))]:
  for tri in triangles(half):
   B.upface('hcm-roof-paint',[(x,6.35-.65*min(1,abs(x-mid)/((hi-lo)/2)),z) for x,z in list(tri.exterior.coords)[:-1]])
 for x in np.arange(lo+.2,hi,.6):
  yy=6.35-.65*min(1,abs(x-mid)/((hi-lo)/2))+.012
  F.box('hcm-trim-paint',(float(x),yy,(zn+zs)/2),(.018,.025,zs-zn-.15))
 coords=list(p.exterior.coords)
 for a,b in zip(coords,coords[1:]):
  height=lambda x:6.35-.65*min(1,abs(x-mid)/((hi-lo)/2))
  # Upper closure follows the actual sloped roof instead of leaving open gables.
  for aa,bb in zip([a,((a[0]+b[0])/2,(a[1]+b[1])/2)], [((a[0]+b[0])/2,(a[1]+b[1])/2),b]):
   B.face('hcm-metal-paint',[(aa[0],5.7,aa[1]),(bb[0],5.7,bb[1]),(bb[0],height(bb[0]),bb[1]),(aa[0],height(aa[0]),aa[1])])
  L=math.dist(a,b);G=Frame(B,*a,math.atan2(-(b[1]-a[1]),b[0]-a[0]),y=0)
  out=1 if not p.covers(Point(G.p(L/2,0,.15)[::2])) else -1
  # Metre-scaled major corrugations; the fine finish is authored separately.
  for u in np.arange(.15,L,.28):G.box('hcm-rib-paint',(float(u),2.85,out*.035),(.035,5.66,.075))
  G.box('hcm-trim-paint',(L/2,5.70,out*.07),(L+.05,.14,.17))
  G.box('hcm-trim-paint',(L/2,.14,out*.05),(L,.18,.10))
  # Simple exterior drains are inferred service details, not surveyed positions.
  if L>40:
   for u in np.arange(7,L,24):
    G.tube('hcm-trim-paint',(float(u),.3,out*.13),(float(u),5.65,out*.13),.055,8)
 # South end is the museum arrival, with raised glazed entrance and ramp.
 # Keep signs original typography, not copied photographs or advertising art.
 S=Frame(B,mid,zs,0,y=0)
 S.box('hcm-stone',(0,2.8,.08),(hi-lo-.3,5.5,.15))
 S.box('hcm-sign-paint',(3.8,3.5,.19),(10.8,2.35,.10))
 S.text('MUSEUM',(3.8,3.83,.26),.83,'hcm-letter',back=True)
 S.text('HOLLYWOOD CARS',(3.8,2.96,.26),.38,'hcm-letter',back=True)
 S.box('hcm-frame-paint',(-6,1.65,.20),(2.65,2.65,.19))
 for dx in [-.64,.64]:
  S.box('hcm-glass',(-6+dx,1.65,.32),(1.20,2.47,.035))
  S.box('hcm-frame-paint',(-6+dx,1.57,.36),(1.20,.065,.045))
  S.box('hcm-metal',(-6+dx*.15,1.47,.40),(.045,.48,.05))
 S.box('hcm-sign-paint',(-6,3.35,.24),(4.4,.70,.16))
 S.text('ENTRANCE',(-6,3.35,.35),.38,'hcm-letter',back=True)
 # Closed exterior-only first pass. Do not pretend this is a playable gallery.
 S.box('hcm-concrete',(-6,.16,1.1),(4.2,.32,2.0),True)
 for side in [-1,1]:S.rail((-6+side*2.0,.2),(-6+side*2.0,2.0),y=1.40)
 # Wheelchair ramp from east to entrance landing, entirely on this site's court.
 pts=[S.p(-3.9,.32,.45),S.p(4.1,.04,.45),S.p(4.1,.04,1.85),S.p(-3.9,.32,1.85)]
 B.upface('hcm-concrete',pts,True)
 for z in [.45,1.85]:
  S.tube('hcm-metal',(-3.9,1.40,z),(4.1,1.12,z),.035,8)
  for t in np.linspace(0,1,6):
   x=-3.9+8*t;y=.32-.28*t;S.tube('hcm-metal',(x,y,z),(x,y+1.08,z),.026,8)
 # Narrow planting beds beneath the signs, with clipped hedge masses.
 for x in [mid+6.3,mid+9.3,mid+11.7]:
  F.box('hcm-concrete',(x,.08,zs+.42),(1.95,.16,.75),True)
  F.box('hcm-soil',(x,.17,zs+.42),(1.80,.04,.60))
  for dx in [-.55,0,.55]:B.sphere('hcm-hedge',(x+dx,.57,zs+.42),.45,10,6,scale=(1,.85,.75))
 # Roof equipment is an inferred, restrained service layer.
 for z in [zn+22,zn+57,zn+83]:
  F.box('hcm-metal-paint',(mid+4,6.26,z),(2.0,.6,1.3))
  for j in range(8):F.box('hcm-vent',(mid+4,6.57,z-.53+j*.15),(1.80,.02,.05))
 return dict(key=KEY,name='Hollywood Cars Museum',center=[p.centroid.x,0,p.centroid.y],bounds=[lo-2,zn-2,hi+2,zs+4],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[])
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
