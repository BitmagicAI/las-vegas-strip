"""Allegiant shell: surveyed perimeter and ETFE roof outline; Earth2022 references."""
from common import *
KEY='allegiantStadium';IDS=['way/691478555','way/1249542290']
STADIUM=footprint(IDS[0])
LOGOS=[r['id'] for r in SURVEY if r['part'] and r['height']==67 and STADIUM.contains(Point(r['center'][0],-r['center'][1]))]
IDS+=LOGOS
def exterior(B):
 B.property=KEY+'-exterior';B.source='allegiant-stadium';B.detail=0
 p=footprint(IDS[0]);inner=footprint(IDS[1]);cx,cz=p.centroid.x,p.centroid.y
 N=240;ring=p.exterior;pts=[ring.interpolate(ring.length*i/N) for i in range(N)]
 def v(i,y,out=0):
  q=pts[i%N];dx,dz=q.x-cx,q.y-cz;d=math.hypot(dx,dz);s=.94+.06*math.sin(min(y,62)/62*math.pi/2)
  return (cx+dx*s+dx/d*out,y,cz+dz*s+dz/d*out)
 def band(fn,width,mat,out=.12):
  for i in range(N):
   y0,y1=fn(i/N),fn((i+1)/N);B.face(mat,[v(i,y0,out),v(i+1,y1,out),v(i+1,y1+width,out),v(i,y0+width,out)])
 for i in range(N):
  for lo in range(0,62,2):
   hi=lo+2;B.face('as-glass' if hi<16 else 'as-black',[v(i,lo),v(i+1,lo),v(i+1,hi),v(i,hi)],True)
 # Panel seams and the two sweeping silver ribbons follow the same curved shell.
 for y in np.arange(10,62,3):band(lambda t,y=y:y,.075,'as-joint',.08)
 for i in range(N):B.path('as-joint',[v(i,y,.1) for y in np.arange(8,63,6)],.026,4)
 band(lambda t:30+19*math.sin(t*math.tau*2+.3),.32,'as-silver',.4)
 band(lambda t:31+19*math.sin(t*math.tau*2+2.8),.25,'as-silver',.4)
 band(lambda t:60.9,.7,'as-silver',.18)
 # North lanai glazing occupies the broad north opening; four structural door leaves.
 for i in range(N):
  a,b=v(i,20,.22),v(i+1,20,.22)
  if (a[2]+b[2])/2<cz-120 and abs((a[0]+b[0])/2-cx)<39:
   for y in range(20,44,2):B.face('as-lanai',[v(i,y,.22),v(i+1,y,.22),v(i+1,y+2,.22),v(i,y+2,.22)])
   B.path('as-frame',[v(i,y,.38) for y in range(20,45,2)],.07,6)
   for y in [25,30,35,40]:B.path('as-frame',[v(i,y,.3),v(i+1,y,.3)],.06,6)
 # Real roof ownership: the central membrane is not another coplanar solid building.
 B.planar('as-roof',p.difference(inner),62,True)
 ir=inner.exterior;ip=[ir.interpolate(ir.length*i/N) for i in range(N)]
 def roof(i,r):q=ip[i%N];return(cx+(q.x-cx)*r,69-7*r*r,cz+(q.y-cz)*r)
 for j in range(12):
  r0,r1=j/12,(j+1)/12
  for i in range(N):
   vs=[roof(i,r0),roof(i,r1),roof(i+1,r1)] if j==0 else [roof(i,r0),roof(i,r1),roof(i+1,r1),roof(i+1,r0)]
   B.upface('as-etfe',vs,True)
 def roofy(x,z):
  dx,dz=x-cx,z-cz;d=math.hypot(dx,dz)
  if d<.01:return 69
  ray=LineString([(cx,cz),(cx+dx/d*400,cz+dz/d*400)]);hit=ir.intersection(ray)
  if hit.is_empty:return 62
  points=list(hit.geoms) if hasattr(hit,'geoms') else [hit];rad=max(math.hypot(q.x-cx,q.y-cz) for q in points if q.geom_type=='Point')
  return 69-7*(d/rad)**2
 for x in np.arange(inner.bounds[0]+2,inner.bounds[2],4):
  segment=inner.intersection(LineString([(x,inner.bounds[1]-1),(x,inner.bounds[3]+1)]))
  if segment.geom_type!='LineString':continue
  ps=[segment.interpolate(t) for t in np.linspace(0,segment.length,max(3,math.ceil(segment.length/5)))];B.path('as-rib',[(q.x,roofy(q.x,q.y)+.12,q.y) for q in ps],.075,5)
 # Ground-level entry piers and recessed glazed doors, no new city roads.
 for i in range(0,N,4):
  q=v(i,0,1.0);B.box('as-pier',(q[0],3.5,q[2]),(.32,7,.32),True)
 for signz,yaw in [(cz-139,0),(cz+141,math.pi)]:
  F=Frame(B,cx,signz,yaw,y=0);F.text('allegiant stadium',(0,13,-.8),2.3,'as-letter')
 # Mapped branding outlines are paint, not full-height building extrusions.
 for ident in LOGOS:
  color=BYID[ident]['tags'].get('roof:colour','').lower();mat='as-yellow' if color=='#ffff00' else 'as-orange' if color=='#ff8000' else 'as-letter'
  B.planar(mat,footprint(ident),62.07)
 return dict(key=KEY,name='Allegiant Stadium',center=[cx,0,cz],bounds=list(p.bounds),structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],views={})
