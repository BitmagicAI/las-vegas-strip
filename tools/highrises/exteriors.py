"""Survey-aligned facades: one owner per surface, no source box overlay."""
import json,sys,math,collections
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon,Point,LineString,box
from shapely.ops import unary_union
sys.path.insert(0,'tools/geographic-strip')
from building_surfaces import BuildingSurfaces,parts
from surface_geometry import triangles
OUT=Path('build/highrises');plans=json.loads((OUT/'plan.json').read_text());meshes={};collisions={};signs=[]
def emit(key,mat,lod,pts,faces,source=''):
 g=meshes.setdefault((key,mat,lod,source),dict(property=key,material=mat,lod=lod,source=source,vertices=[],faces=[]));n=len(g['vertices']);g['vertices'].extend(pts);g['faces'].extend([[n+i for i in f] for f in faces])
def face(key,mat,lod,pts,source=''):emit(key,mat,lod,pts,[[0,i,i+1] for i in range(1,len(pts)-1)],source)
def collision(key,pts):
 g=collisions.setdefault(key,dict(vertices=[],indices=[]));n=len(g['vertices'])//3;g['vertices'].extend(c for p in pts for c in p);g['indices'].extend(n+i for i in range(len(pts)))
def world(t,x,y,z):
 a,b,c,d=t['linear'];o=t['origin'];return [o[0]+a*x+b*z,o[1]+y,o[2]+c*x+d*z]
def local(t,x,z):
 a,b,c,d=t['linear'];o=t['origin'];x-=o[0];z-=o[2];det=a*d-b*c;return ((d*x-b*z)/det,(a*z-c*x)/det)
class Access:
 def __init__(self,p):self.p=p
 def wall(self,a,b,lo,hi):
  line=LineString([a,b]);L=line.length;region=box(0,lo,L,hi)
  for t in self.p['towers']:
   aa=local(t,*a);bb=local(t,*b);dl=LineString([aa,bb]);zone=box(-2.5,t['lobbyFront']-12,2.5,-5.0)
   connection=t.get('publicConnection')
   if connection:
    side,at,width=connection['side'],connection['at'],connection['width'];zone=zone.union(box(min(side*8.9,side*26),at-width/2,max(side*8.9,side*26),at+width/2))
   for seg in parts(dl.intersection(zone),'LineString'):
    u=[dl.project(Point(q))/max(dl.length,.001)*L for q in seg.coords];region=region.difference(box(min(u),0,max(u),4.7))
  return [[[line.interpolate(x).x,y,line.interpolate(x).y] for x,y in list(tri.exterior.coords)[:-1]] for poly in parts(region) for tri in triangles(poly)]
def block(p,t,name,center,size,solid=False):
 x,y,z=center;w,h,d=[v/2 for v in size]
 corners=[world(t,x+sx*w,y+sy*h,z+sz*d) for sx,sy,sz in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
 for ids in [(0,3,2,1),(4,5,6,7),(0,4,7,3),(1,2,6,5),(3,7,6,2),(0,1,5,4)]:
  vs=[corners[i] for i in ids];face(p['key'],name,0,vs,t['source'])
  if solid:collision(p['key'],[vs[i] for i in [0,1,2,0,2,3]])
for p in plans:
 key=p['key'];records=[]
 for t in p['towers']:
  entry=t['lobbyFront']
  block(p,t,'stone',(0,-.4,entry-5.8),(4.8,.8,12),True)
  block(p,t,'stone',(0,4.8,entry-1.5),(8,.25,3.8),True)
  for sign in [-1,1]:
   block(p,t,'frame',(sign*3.5,2.34,entry-2.8),(.3,4.68,.3),True)

 for f in p['features']:
  if f['id']=='way/43875964':continue  # Authored Venetian Campanile owns this source.
  shape=unary_union([Polygon([(x,-z) for x,z in q[0]],[[(x,-z) for x,z in ring] for ring in q[1:]]).buffer(0) for q in f['polygons']]);records.append(dict(f,shape=shape))
 surface=BuildingSurfaces(records);access=Access(p)
 for r,shape in zip(records,surface.shapes):
  source=r['id'];h=r['height'];base=r['base'];family=p['family']
  if source=='way/27858544':
   for poly in parts(shape):
    center=poly.centroid
    for a,b in zip(list(poly.exterior.coords),list(poly.exterior.coords)[1:]):
     pts=[[a[0],0,a[1]],[b[0],0,b[1]],[center.x,h,center.y]];face(key,'glass',0,pts,source);collision(key,pts)
     for level in range(1,28):
      t=level/28;s=t+.002
      pts=[[center.x+(v[0]-center.x)*(1-q),h*q,center.y+(v[1]-center.y)*(1-q)] for v,q in [(a,t),(b,t),(b,s),(a,s)]];face(key,'frame',1,pts,source)
   continue
  if source=='way/135457469':
   cx,cz=shape.centroid.coords[0]
   # Tripod shaft, saucer-shaped observation deck and antenna at surveyed height.
   profile=[(0,12),(215,8),(224,23),(244,27),(257,24),(271,9),(285,5),(h,0.2)]
   for (y,rad),(yy,rr) in zip(profile,profile[1:]):
    for i in range(48):
     a=i*math.tau/48;b=(i+1)*math.tau/48
     pts=[[cx+rrr*math.cos(t),v,cz+rrr*math.sin(t)] for v,rrr,t in [(y,rad,a),(y,rad,b),(yy,rr,b),(yy,rr,a)]];face(key,'glass' if 244<=y<257 else 'stone',0,pts,source)
   continue
  for poly in parts(shape):
   for ring in [poly.exterior,*poly.interiors]:
    for a,b in zip(list(ring.coords),list(ring.coords)[1:]):
     line=LineString([a,b]);L=line.length
     if L<.1:continue
     ux,uz=(b[0]-a[0])/L,(b[1]-a[1])/L;nx,nz=-uz,ux
     mid=line.interpolate(.5,normalized=True)
     if shape.contains(Point(mid.x+nx*.02,mid.y+nz*.02)):nx=-nx;nz=-nz
     visible=surface.wall(source,a,b,base,h,access)
     region=unary_union([Polygon([(line.project(Point(v[0],v[2])),v[1]) for v in tri]) for tri in visible])
     for tri in visible:face(key,('stone-'+str(records.index(r)%5) if key=='new-york' else 'stone') if family in ['classical','deco','balcony','strat'] else 'glass',0,tri,source);collision(key,tri)
     def patch(mat,x0,y0,x1,y1,offset=.055,lod=1):
      if x1<=x0 or y1<=y0:return
      geom=region.intersection(box(x0,y0,x1,y1))
      for q in parts(geom):
       for tri in triangles(q):
        pts=[[a[0]+ux*x+nx*offset,y,a[1]+uz*x+nz*offset] for x,y in list(tri.exterior.coords)[:-1]];face(key,mat,lod,pts,source)
     step=3.6 if h<125 else 3.8;cols=max(1,round(L/(3.1 if family=='classical' else 2.1)));cw=L/cols
     if family in ['classical','deco','balcony','strat']:
      for y in np.arange(max(base,7.2),h-2,step):
       for j in range(cols):patch('glass',j*cw+.28,y+.42,(j+1)*cw-.28,min(y+step-.42,h-.6),.045)
     # Recessed glazing and raised spandrels are separated by centimetres, never coplanar.
     for y in np.arange(max(base,7.2),h-.3,step):
      patch('frame',0,y,L,min(y+(.18 if family in ['bronze','green','dark','blue'] else .12),h),.08)
      if family=='balcony':
       patch('stone',0,y+.06,L,y+.34,.22)
       patch('glass',0,y+.35,L,y+1.05,.26)
       patch('frame',0,y+1.06,L,y+1.12,.28)
     for j in range(cols+1):
      w=.14 if family in ['gold','classical','deco'] else .055
      patch('frame',j*cw-w/2,max(base,7.2),j*cw+w/2,h-.25,.085)
     patch('accent' if family=='red' else 'stone',0,h-.8,L,h,.13,lod=0)
     if family=='red':
      for j in [0,L-1.3]:patch('accent',j,base,j+1.3,h,.15,lod=0)
     if family=='rio':
      for j in np.arange(0,L,15):patch('accent',j,base,j+2.3,h,.13,lod=0)
     if key in ['wynn','encore']:
      for y in np.arange(max(base,10),h-1,11.4):patch('stone',0,y,L,y+.32,.16,lod=0)
     if family in ['classical','deco']:
      patch('stone',0,h-4,L,h-3.7,.17,lod=0)
      for j in np.arange(0,L,9):patch('stone',j,h-10,j+.50,h,.12)
   for q in parts(surface.roof(source,poly,h)):
    for tri in triangles(q):face(key,'roof',0,[[x,h,z] for x,z in list(tri.exterior.coords)[:-1]],source)
  # Longest exterior edge carries scaled roof signage, kept below the roofline.
  poly=max(parts(shape),key=lambda p:p.area);a,b=max(zip(list(poly.exterior.coords),list(poly.exterior.coords)[1:]),key=lambda ab:math.dist(*ab));L=math.dist(a,b)
  if L>18 and shape.area>900:signs.append(dict(property=key,source=source,text=p['name'].upper(),a=a,b=b,height=h-3,width=min(L*.65,60)))
 (OUT/(key+'-collision.json')).write_text(json.dumps(collisions.get(key,dict(vertices=[],indices=[])),separators=(',',':')))
 print(key,'facades ready',flush=True)
(OUT/'meshes.json').write_text(json.dumps(list(meshes.values()),separators=(',',':')));(OUT/'signs.json').write_text(json.dumps(signs))
print('Facade batches',len(meshes),'triangles',sum(len(g['faces']) for g in meshes.values()))
