"""Platinum Hotel: surveyed plans, 2024 Earth exterior views, separate parking podium."""
from common import *
from building_surfaces import BuildingSurfaces
from forum_shops import facade_frame
KEY='platinum';IDS=['way/135298867','way/543423254']
class Closed:
 def wall(self,a,b,lo,hi):return [[(a[0],lo,a[1]),(b[0],lo,b[1]),(b[0],hi,b[1])],[(a[0],lo,a[1]),(b[0],hi,b[1]),(a[0],hi,a[1])]]
def exterior(B):
 B.property=KEY+'-exterior';B.source='platinum';B.detail=0
 tower=footprint(IDS[1]);parent=footprint(IDS[0]);garage=parent.intersection(box(860,242,900.5,295)).difference(tower);lobby=parent.difference(tower).difference(garage)
 rs=[dict(id='tower',shape=tower,base=0,height=50),dict(id='garage',shape=garage,base=0,height=12.4),dict(id='lobby',shape=lobby,base=0,height=6)]
 surf=BuildingSurfaces(rs);pool=box(876,253,884,268)
 for r in rs:
  kind,h=r['id'],r['height']
  for pp in parts(r['shape']):
   ps=list(pp.exterior.coords)
   for a,b in zip(ps,ps[1:]):
    L=math.dist(a,b)
    if L<.05:continue
    F,_,nx,nz=facade_frame(B,a,b,pp,0);ux,uz=(b[0]-a[0])/L,(b[1]-a[1])/L;line=LineString([a,b]);ts=surf.wall(kind,a,b,0,h,Closed());region=unary_union([Polygon([(line.project(Point(v[0],v[2])),v[1]) for v in t]) for t in ts])
    def patch(mat,x0,y0,x1,y1,off=.07):
     if x1<=x0 or y1<=y0:return
     for q in parts(region.intersection(box(x0,y0,x1,y1))):
      for t in triangles(q):B.face(mat,[(a[0]+ux*x+nx*off,y,a[1]+uz*x+nz*off) for x,y in list(t.exterior.coords)[:-1]])
    for t in ts:B.face('pt-shadow',t,True)
    patch('pt-white',0,0,L,h)
    if kind=='tower':
     long=L>29;center=L/2;core=L>60
     if core:patch('pt-blue',center-12,12.4,center+12,50,.12)
     elif L>15 and abs(nz)>.8:patch('pt-blue',0,6,L,50,.12)
     n=max(1,round(L/4.3));w=L/n
     if L>5:
      for k in range(n):
       x=(k+.5)*w;inCore=core and abs(x-center)<12
       for y in np.arange(13.3,48,2.8):
        patch('pt-glass',x-w*.32,y,x+w*.32,y+2.05,.19)
        patch('pt-sill',x-w*.35,y-.09,x+w*.35,y,.25)
        patch('pt-frame',x-.025,y,x+.025,y+2.05,.24)
        # Physical balconies only where the surrounding footprint is clear.
        if long and not inCore and k%2==0:
         q=line.interpolate(x);cx,cz=q.x+nx*.6,q.y+nz*.6;bw=w*.7
         pts=[(cx+ux*u+nx*v,cz+uz*u+nz*v) for u,v in [(-bw/2,-.55),(bw/2,-.55),(bw/2,.65),(-bw/2,.65)]];bal=Polygon(pts)
         if tower.intersection(bal).area>.08:continue
         B.shell(bal,y-.2,y-.07,'pt-white')
         for yy in [y+.25,y+.9]:B.tube('pt-rail',(cx-ux*bw/2+nx*.6,yy,cz-uz*bw/2+nz*.6),(cx+ux*bw/2+nx*.6,yy,cz+uz*bw/2+nz*.6),.024,6)
         for u in np.arange(-bw/2,bw/2+.01,.35):B.tube('pt-rail',(cx+ux*u+nx*.6,y,cz+uz*u+nz*.6),(cx+ux*u+nx*.6,y+.9,cz+uz*u+nz*.6),.012,5)
      if core:
       patch('pt-glass',center-4,18,center+4,47,.2)
       for y in np.arange(18,47,1.4):patch('pt-frame',center-4,y,center+4,y+.05,.27)
       for x in np.arange(center-4,center+4.1,1.6):patch('pt-frame',x,18,x+.045,47,.27)
       F.text('PLATINUM',(L/2,48.4,-.5),1.6,'pt-letter')
      if long:
       for y in [2,5,8,11]:patch('pt-shadow',1,y,L-1,y+1.4,.17)
       for x in np.arange(1,L,6):patch('pt-white',x,0,min(L,x+.45),12.4,.22)
     patch('pt-sill',0,49.4,L,50,.24)
    elif kind=='garage':
     for y in [1.1,4.2,7.3]:patch('pt-shadow',.5,y,L-.5,y+1.8,.15)
     for x in np.arange(.2,L,5):patch('pt-white',x,0,min(L,x+.45),10,.21)
     for x in np.arange(.6,L-1,3):patch('pt-glass',x,10.2,min(x+1.8,L),11.65,.16)
    else:
     for x in np.arange(.5,L-1,2.4):
      patch('pt-glass',x,.3,min(L,x+1.8),4.7,.16)
      patch('pt-frame',x+.85,.3,min(L,x+.9),4.7,.22)
     patch('pt-blue',0,5.05,L,5.5,.23)
   roof=surf.roof(kind,pp,h)
   if kind=='garage':roof=roof.difference(pool.buffer(.45))
   B.planar('pt-roof',roof,h+.025,True)
   for a,b in zip(ps,ps[1:]):
    F,L,_,_=facade_frame(B,a,b,pp,0);F.box('pt-white',(L/2,h+.35,0),(L,.7,.25),True)
 # Raised roof service enclosure and screened equipment, inside the surveyed shell.
 crown=tower.intersection(box(900,234,924,271)).buffer(-1)
 B.shell(crown,50.03,52.5,'pt-blue')
 for z in np.arange(244,269,8):B.box('pt-service',(913,53,z),(4,.9,3))
 B.planar('pt-coping',pool.buffer(.45),12.53,True);B.planar('platinum_pool',pool,12.55)
 for z in np.arange(251,274,3):B.box('pt-chair',(887,12.8,z),(1.2,.5,1.9))
 # Front arrival canopy (pedestrian scale; opening access remains separately tracked).
 F=Frame(B,903,199.5,0,y=0);F.box('pt-blue',(0,4.7,-1.6),(10,.4,4.8),True)
 for x in [-4.6,4.6]:F.box('pt-white',(x,2.25,-3.5),(.3,4.5,.3),True)
 F.text('PLATINUM',(0,4.75,-4.05),.5,'pt-letter')
 return dict(key=KEY,name='Platinum Hotel and Spa',center=[905,0,246],bounds=list(parent.bounds),structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],views={})
