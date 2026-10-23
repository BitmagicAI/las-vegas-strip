"""Arcade support piers replacing obsolete filled mapped bridge extrusion.
Existing arcade/road datum retained; pier positions are structural estimates
restricted to non-road ground between the authored road corridors.
"""
from common import *
KEY='bellagioArcadePiers'
def exterior(B):
 B.property=KEY+'-exterior';B.source='bellagio-arcade-supports';B.detail=0
 j=json.load(open('build/resort-blocks/bellagio/south-arrival-report.json'))
 roads=unary_union([LineString([(q[0],q[2])for q in r['points']]).buffer(r['width']/2+1.2)for r in j['roads']])
 walk=[(-57,588),(-106,583),(-137,565),(-167,545),(-190,529)];points=[]
 for a,b in zip(walk,walk[1:]):
  l=LineString([a,b]);yaw=-math.atan2(b[1]-a[1],b[0]-a[0])
  for d in np.arange(6,l.length,12):
   p=l.interpolate(d)
   if roads.intersects(p.buffer(1.1)):continue
   F=Frame(B,p.x,p.y,yaw,y=0);points.append([p.x,p.y])
   F.box('bap-stone',(0,.3,0),(1.65,.6,1.65),True)
   F.box('bap-cream',(0,3.2,0),(1.05,5.2,1.05),True)
   F.box('bap-cream',(0,6.05,0),(1.3,.5,4.3),True)
   for y in [.65,5.65]:F.box('bap-trim',(0,y,0),(1.2,.12,1.2))
 # Mapped roof pavilions belong at the existing elevated walkway datum.
 walkpoly=unary_union([LineString([a,b]).buffer(2.2,cap_style=2,join_style=2) for a,b in zip(walk,walk[1:])]);samples=[]
 for ident in ['way/823658733','way/823658732','way/823658731']:
  p=footprint(ident);cx,cz=p.centroid.coords[0];outer=p.buffer(.28,join_style=2)
  B.shell(p.difference(walkpoly),6.3,6.8,'bap-stone',roof=False)
  B.planar('bap-stone',p.difference(walkpoly),6.8,True)
  # Raised hip roof covers the old corridor gable, without coplanar exterior faces.
  for a,c in zip(list(outer.exterior.coords),list(outer.exterior.coords)[1:]):
   B.upface('bap-roof-terracotta',[(a[0],10.5,a[1]),(c[0],10.5,c[1]),(cx,13.2,cz)])
  # Down-facing soffit outside retained corridor.
  for q in parts(p.difference(walkpoly)):
   for t in triangles(q):
    vv=[(x,10.25,z) for x,z in list(t.exterior.coords)[:-1]]
    if np.cross(np.array(vv[1])-vv[0],np.array(vv[2])-vv[0])[1]>0:vv.reverse()
    B.face('bap-cream',vv)
  from forum_shops import facade_frame
  for a,c in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
   F,L,nx,nz=facade_frame(B,a,c,p,0)
   F.box('bap-trim',(L/2,10.3,0),(L,.25,.28))
   edge=LineString([a,c]).difference(walkpoly.buffer(.06))
   for seg in getattr(edge,'geoms',[edge]):
    if seg.is_empty or seg.length<.15:continue
    aa,bb=list(seg.coords)[0],list(seg.coords)[-1];le=math.dist(aa,bb);yaw=-math.atan2(bb[1]-aa[1],bb[0]-aa[0]);G=Frame(B,(aa[0]+bb[0])/2,(aa[1]+bb[1])/2,yaw,y=0)
    G.box('bap-cream',(0,7.34,0),(le,1.08,.18),True);G.box('bap-trim',(0,7.9,0),(le,.12,.28))
  for x,z in list(p.exterior.coords)[:-1]:
   B.box('bap-cream',(x,8.55,z),(.42,3.5,.42),True)
   B.box('bap-trim',(x,10.08,z),(.61,.28,.61))
   if not roads.intersects(Point(x,z).buffer(.8)):
    B.box('bap-stone',(x,.3,z),(1.15,.6,1.15),True);B.box('bap-cream',(x,3.3,z),(.65,5.4,.65),True)
  B.lathe('bap-trim',(cx,cz),[(13.15,.13),(13.5,.09),(13.65,0)],12)
  for x in np.arange(p.bounds[0]+.4,p.bounds[2],.8):
   for z in np.arange(p.bounds[1]+.4,p.bounds[3],.8):
    if p.buffer(-.3).contains(Point(x,z)):samples.append([float(x),7.7,float(z)])
 Path('build/city-exteriors/bellagio-pavilion-samples.json').write_text(json.dumps(samples))
 Path('build/city-exteriors/bellagio-arcade-pier-points.json').write_text(json.dumps(points))
 return dict(key=KEY,name='Bellagio covered arcade supports',center=[-125,0,556],bounds=[-192,522,-57,591],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
