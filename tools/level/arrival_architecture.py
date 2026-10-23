"""Architectural mesh vocabulary in metre-scale arrival-local coordinates.
Local +Z points indoors. Materials and authored detail are shared, never per-frame.
"""
import bpy,bmesh,math,random
from pathlib import Path
from mathutils import Vector
PI=math.pi;TAU=math.tau
FACES=[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)]
def material(name,c,metal=0,rough=.5,emission=0,alpha=1,texture=None):
 name='arrival_'+name;m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*c,alpha);bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough;bs.inputs['Alpha'].default_value=alpha
 bs.inputs['Emission Color'].default_value=(*c,1);bs.inputs['Emission Strength'].default_value=emission;m.diffuse_color=(*c,alpha);m.use_backface_culling=False
 if alpha<1:m.surface_render_method='DITHERED'
 if texture:
  n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=bpy.data.images.load(str(Path(texture).resolve()),check_existing=True);n.image.pack();m.node_tree.links.new(n.outputs['Color'],bs.inputs['Base Color'])
 return m

def materials():
 for n,c,met,r,e,a in [
 ('plaster',(.84,.81,.73),0,.75,0,1),('white',(.92,.92,.90),0,.46,0,1),('stone',(.66,.61,.51),0,.55,0,1),('marble',(.80,.77,.69),0,.22,0,1),('black',(.022,.027,.031),.18,.24,0,1),('granite',(.041,.048,.051),.1,.15,0,1),('bronze',(.22,.14,.073),.72,.28,0,1),('gold',(.67,.47,.21),.74,.27,0,1),('silver',(.61,.65,.66),.84,.22,0,1),('wood',(.29,.125,.048),0,.39,0,1),('walnut',(.10,.038,.018),0,.34,0,1),('red',(.40,.021,.024),.08,.35,0,1),('sage',(.085,.16,.135),.55,.32,0,1),('teal',(.09,.19,.21),0,.7,0,1),('fabric',(.68,.66,.58),0,.88,0,1),('linen',(.89,.88,.83),0,.83,0,1),('lime',(.49,.57,.13),0,.82,0,1),('leaf',(.11,.21,.087),0,.85,0,1),('leaflight',(.24,.32,.14),0,.9,0,1),('soil',(.055,.034,.018),0,1,0,1),('warm',(.99,.85,.62),0,.4,1.1,1),('cool',(.70,.88,1),0,.4,1.1,1),('violet',(.32,.04,.72),.08,.35,1.0,1),('pink',(.9,.04,.24),.05,.3,1.0,1),('blue',(.015,.16,.52),.1,.32,.7,1),('crystal',(.83,.88,.91),.38,.15,.23,1),('glass',(.61,.74,.77),.25,.16,0,.13),('mirror',(.34,.40,.43),.94,.12,0,1)]:material(n,c,met,r,e,a)
 for n in ['marble','stone','wood','granite']:
  p=Path('build/arrival-reconstruction/textures')/(n+'.png')
  if p.exists():
   m=bpy.data.materials['arrival_'+n];bs=m.node_tree.nodes.get('Principled BSDF');tx=m.node_tree.nodes.new('ShaderNodeTexImage');tx.image=bpy.data.images.load(str(p.resolve()),check_existing=True);tx.image.pack();m.node_tree.links.new(tx.outputs['Color'],bs.inputs['Base Color'])

class Builder:
 def __init__(self,name,owner,origin,yaw,width,depth,height,reserved=None):
  self.name=name;self.owner=owner;self.origin=origin;self.yaw=yaw;self.w=width;self.d=depth;self.h=height;self.groups={};self.colliders=[];self.lights=[];self.reserved=reserved or (lambda p:False);self.role='interior';self.components=0
 def world(self,p):
  c,s=math.cos(self.yaw),math.sin(self.yaw);x,y,z=p;return(self.origin[0]+c*x+s*z,self.origin[1]+y,self.origin[2]-s*x+c*z)
 def mesh(self,vs,fs,m,smooth=False):
  world=[self.world(v) for v in vs];center=tuple(sum(v[i] for v in world)/len(world) for i in range(3))
  if self.role=='interior' and center[1]>.3 and (self.reserved(center) or any(self.reserved(v) for v in world)):return
  k=(self.role,m);g=self.groups.setdefault(k,[[],[],[]]);b=len(g[0]);g[0].extend(world);g[1].extend(tuple(b+i for i in f) for f in fs);g[2].extend([smooth]*len(fs));self.components+=1
 def box(self,p,s,m='plaster',a=0,solid=False,bevel=0):
  c,si=math.cos(a),math.sin(a);w,h,d=[v/2 for v in s]
  vs=[(p[0]+c*x+si*z,p[1]+y,p[2]-si*x+c*z) for x in [-w,w] for y in [-h,h] for z in [-d,d]]
  if bevel:
   bm=bmesh.new();ve=[bm.verts.new(v) for v in vs]
   for f in FACES:bm.faces.new([ve[i] for i in f])
   bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bmesh.ops.bevel(bm,geom=list(bm.edges),offset=min(bevel,min(s)/3),segments=2,affect='EDGES');bm.verts.ensure_lookup_table();bm.verts.index_update();self.mesh([tuple(v.co) for v in bm.verts],[tuple(v.index for v in f.verts) for f in bm.faces],m);bm.free()
  else:self.mesh(vs,FACES,m)
  if solid and not any(self.reserved(self.world(v)) for v in vs):self.proxy('structure',p,s,a)
 def proxy(self,name,p,s,a=0):
  # A component omitted around the streamed stair core must not leave behind
  # an invisible furniture collider.
  c,si=math.cos(a),math.sin(a)
  samples=[p]+[(p[0]+c*x+si*z,p[1]+y,p[2]-si*x+c*z) for x in [-s[0]/2,s[0]/2] for y in [-s[1]/2,s[1]/2] for z in [-s[2]/2,s[2]/2]]
  if self.role=='interior' and any(self.reserved(self.world(v)) for v in samples):return
  self.colliders.append(dict(name='Arrival / '+self.name+' / '+name+' '+str(len(self.colliders)),shape='box',position=list(self.world(p)),size=list(s),yaw=self.yaw+a))
 def tube(self,pts,r,m,closed=False,sides=8):
  pts=[Vector(p) for p in pts];vs=[]
  for i,p in enumerate(pts):
   t=(pts[(i+1)%len(pts)]-pts[i-1]).normalized() if closed or 0<i<len(pts)-1 else (pts[min(i+1,len(pts)-1)]-pts[max(i-1,0)]).normalized();u=t.cross(Vector((0,1,0)) if abs(t.y)<.9 else Vector((1,0,0))).normalized();v=t.cross(u)
   vs.extend(tuple(p+r*(u*math.cos(j*TAU/sides)+v*math.sin(j*TAU/sides))) for j in range(sides))
  fs=[(i*sides+j,i*sides+(j+1)%sides,((i+1)%len(pts))*sides+(j+1)%sides,((i+1)%len(pts))*sides+j) for i in range(len(pts) if closed else len(pts)-1) for j in range(sides)]
  if not closed:fs.extend([tuple(reversed(range(sides))),tuple((len(pts)-1)*sides+j for j in range(sides))])
  self.mesh(vs,fs,m,True)
 def lathe(self,p,profile,m='gold',N=32,sx=1,sz=1):
  vs=[(p[0]+r*math.cos(i*TAU/N)*sx,p[1]+y,p[2]+r*math.sin(i*TAU/N)*sz) for r,y in profile for i in range(N)];fs=[(k*N+i,k*N+(i+1)%N,(k+1)*N+(i+1)%N,(k+1)*N+i) for k in range(len(profile)-1) for i in range(N)];
  if abs(profile[0][1]-profile[-1][1])<1e-6 and abs(profile[0][0]-profile[-1][0])>1e-6:
   k=len(profile)-1;fs.extend((k*N+i,k*N+(i+1)%N,(i+1)%N,i) for i in range(N))
  else:fs.extend([tuple(reversed(range(N))),tuple((len(profile)-1)*N+i for i in range(N))])
  self.mesh(vs,fs,m,True)
 def ring(self,p,r,width=.06,m='gold',rx=1,rz=1):self.lathe(p,[(r,0),(r,.025),(r-width,.025),(r-width,0)],m,64,rx,rz)
 def text(self,words,p,size=.3,width=10,m='gold',yaw=PI):
  cu=bpy.data.curves.new('arrival lettering','FONT');cu.body=words;cu.align_x='CENTER';cu.align_y='CENTER';cu.size=size;cu.resolution_u=4;cu.extrude=.002
  o=bpy.data.objects.new('arrival lettering',cu);bpy.context.scene.collection.objects.link(o);me=bpy.data.meshes.new_from_object(o.evaluated_get(bpy.context.evaluated_depsgraph_get()));xs=[v.co.x for v in me.vertices]
  if xs:
   scale=min(1,width/max(.01,max(xs)-min(xs)));c,s=math.cos(yaw),math.sin(yaw);self.mesh([(p[0]+c*v.co.x*scale+s*v.co.z,p[1]+v.co.y,p[2]-s*v.co.x*scale+c*v.co.z) for v in me.vertices],[tuple(f.vertices) for f in me.polygons],m)
  bpy.data.objects.remove(o,do_unlink=True);bpy.data.meshes.remove(me);bpy.data.curves.remove(cu)
 def frame(self,p,w,h,m='gold',t=.045,yaw=0):
  c,s=math.cos(yaw),math.sin(yaw)
  for x in [-w/2,w/2]:self.box((p[0]+c*x,p[1],p[2]-s*x),(t,h,t),m,yaw)
  for y in [-h/2,h/2]:self.box((p[0],p[1]+y,p[2]),(w,t,t),m,yaw)
 def light(self,p,power=55,color='#ffe7c7',distance=16):self.lights.append(dict(name='Arrival / '+self.name+' / light '+str(len(self.lights)),type='point',position=list(self.world(p)),color=color,intensity=power,distance=distance,decay=2))
 def downlight(self,p,r=.11):
  self.lathe(p,[(r,0),(r,.025)],'black',16);self.lathe((p[0],p[1]-.014,p[2]),[(r*.74,0),(r*.74,.008)],'warm',16)
 def arch(self,p,w,h,m='gold',r=.09):
  spring=h-w/2;self.tube([(p[0]-w/2,p[1],p[2]),(p[0]-w/2,p[1]+spring,p[2])]+[(p[0]+w/2*math.cos(PI-i*PI/40),p[1]+spring+w/2*math.sin(i*PI/40),p[2]) for i in range(41)]+[(p[0]+w/2,p[1],p[2])],r,m)
 def column(self,x,z,h=6,r=.4,classic=False,m='marble'):
  self.lathe((x,0,z),[(r*1.3,0),(r*1.3,.16),(r*1.12,.24),(r,.38),(r*.85,h-.65),(r,h-.55),(r*1.35,h-.3),(r*1.4,h)],m)
  self.proxy('column',(x,h/2,z),(r*2,h,r*2))
  if classic:
   for i in range(16):
    a=i*TAU/16;self.tube([(x+r*.94*math.cos(a),.44,z+r*.94*math.sin(a)),(x+r*.84*math.cos(a),h-.75,z+r*.84*math.sin(a))],.022,'gold',sides=5)
   for i in range(8):
    a=i*TAU/8
    for j in [-1,1]:self.tube([(x+math.cos(a)*(r+.1)+math.sin(a)*j*.16*math.cos(t),h-.46+.16*math.sin(t),z+math.sin(a)*(r+.1)-math.cos(a)*j*.16*math.cos(t)) for t in [k*TAU/24 for k in range(25)]],.045,'gold',sides=6)
 def sofa(self,x,z,w=2.6,m='fabric',yaw=0):
  def bp(p,s,mat,bev=.06):
   c,si=math.cos(yaw),math.sin(yaw);self.box((x+c*p[0]+si*p[2],p[1],z-si*p[0]+c*p[2]),s,mat,yaw,bevel=bev)
  bp((0,.24,0),(w,.25,.88),'walnut');bp((0,.51,0),(w-.24,.28,.83),m,.11);bp((0,.84,.36),(w-.05,.74,.24),m,.10)
  for dx in [-w/2+.11,w/2-.11]:bp((dx,.64,0),(.23,.59,.96),m,.08)
  for dx in [-w*.32,0,w*.32]:bp((dx,.70,.13),(.40,.42,.16),'linen',.075)
  self.proxy('sofa',(x,.46,z),(w,.80,1.0),yaw)
 def planter(self,x,z,h=3.8,r=.48,m='white'):
  self.lathe((x,0,z),[(r*.65,0),(r*.75,.08),(r,1.04),(r*.96,1.12),(r*.82,1.12)],m);self.lathe((x,1.08,z),[(r*.83,0),(r*.83,.01)],'soil',24)
  self.tube([(x,1.1,z),(x+.05,h-.45,z)],.048,'wood')
  for i in range(24):
   a=i*2.4;yy=1.9+(i%7)*.24;rr=.45+(i%4)*.17;ex=x+math.cos(a)*rr;ez=z+math.sin(a)*rr
   self.tube([(x,yy-.5,z),(ex,yy,ez)],.014,'wood',sides=5)
   for j in range(3):
    q=a+j*1.1;cx=ex+.2*math.cos(q);cz=ez+.2*math.sin(q);self.mesh([(ex,yy,ez),(cx-.14*math.sin(q),yy+.10,cz+.14*math.cos(q)),(ex+.5*math.cos(q),yy+.2,ez+.5*math.sin(q)),(cx+.14*math.sin(q),yy+.03,cz-.14*math.cos(q))],[(0,1,2),(0,2,3)],'leaf' if i%3 else 'leaflight')
 def vase(self,x,z,y=1.2):
  self.lathe((x,y,z),[(.15,0),(.24,.2),(.20,.55),(.10,.7),(.16,.73)],'gold',24)
  for i in range(18):
   a=i*2.4;ex=x+math.cos(a)*(.1+i%3*.08);ez=z+math.sin(a)*(.1+i%4*.07);yy=y+.9+i%5*.065
   self.tube([(x,y+.5,z),(ex,yy,ez)],.008,'leaf',sides=4)
   self.lathe((ex,yy,ez),[(0,-.04),(.055,0),(.08,.04),(.035,.1)],'linen' if i%4 else 'pink',8)
 def counter(self,x,z,w=8,yaw=0,m='walnut',label='RECEPTION'):
  c,s=math.cos(yaw),math.sin(yaw)
  def b(p,size,mat,bev=0):self.box((x+c*p[0]+s*p[2],p[1],z-s*p[0]+c*p[2]),size,mat,yaw,bevel=bev)
  b((0,.6,0),(w,1.08,1.15),m,.045);b((0,1.15,0),(w+.16,.09,1.3),'granite',.025);b((0,.18,-.61),(w-.2,.025,.025),'warm');b((0,.10,0),(w-.25,.10,1.05),'black')
  for i in range(int(w/2)):
   dx=(i-(int(w/2)-1)/2)*2;b((dx,1.32,.22),(.38,.25,.055),'black');b((dx,1.17,.09),(.28,.025,.22),'black');b((dx,.69,-.585),(1.75,.70,.035),'stone' if m=='marble' else m)
  self.proxy('counter',(x,.65,z),(w,1.16,1.2),yaw)
  for end in [-1,1]:self.vase(x+c*end*(w/2-.55),z-s*end*(w/2-.55),1.20)
 def chandelier(self,x,z,y=6,r=1.5,drop=1.8,style='crystal'):
  self.tube([(x,y+.6,z),(x,y,z)],.025,'bronze');self.ring((x,y,z),r,.06,'gold')
  if style=='rods':
   for k in range(3):
    rr=r-k*.23
    for i in range(64):
     a=i*TAU/64;xx=x+rr*math.cos(a);zz=z+rr*math.sin(a);self.tube([(xx,y,zz),(xx,y-drop+.15*k,zz)],.019,'gold',sides=6);self.lathe((xx,y-drop+.15*k,zz),[(.025,0),(.025,.04)],'warm',8)
  else:
   for k in range(4):
    rr=r*(1-.21*k);yy=y-k*.22;self.ring((x,yy,z),rr,.03,'gold')
    for i in range(32-k*5):
     a=i*TAU/(32-k*5);xx=x+rr*math.cos(a);zz=z+rr*math.sin(a)
     for j in range(4+k):self.lathe((xx,yy-j*drop/(7+k),zz),[(0,0),(.047,-.06),(.035,-.12),(0,-.17)],'crystal',6)
  self.light((x,y-drop-.4,z),75,distance=19)
 def floor(self,m='marble',tile=1.4):
  # The guest entrance and its approach own their existing floor height.
  # Subtract them rather than layering a second slab over the stair landing.
  rects=[(-self.w/2,self.w/2,0,self.d)]
  for hx0,hx1,hz0,hz1 in getattr(self,'floor_exclusions',[]):
   next_rects=[]
   for x0,x1,z0,z1 in rects:
    a,b=max(x0,hx0),min(x1,hx1);c,d=max(z0,hz0),min(z1,hz1)
    if a>=b or c>=d:next_rects.append((x0,x1,z0,z1));continue
    next_rects.extend(r for r in [(x0,a,z0,z1),(b,x1,z0,z1),(a,b,z0,c),(a,b,d,z1)] if r[1]-r[0]>.01 and r[3]-r[2]>.01)
   rects=next_rects
  for x0,x1,z0,z1 in rects:
   self.box(((x0+x1)/2,.035,(z0+z1)/2),(x1-x0,.07,z1-z0),m)
   self.proxy('floor finish',((x0+x1)/2,.015,(z0+z1)/2),(x1-x0,.11,z1-z0))
  # Real staggered grout lines, sub-centimetre recesses rather than broad stripes.
   for x in [(-self.w/2)+i*tile for i in range(1,int(self.w/tile))]:
    if x0<x<x1:self.box((x,.073,(z0+z1)/2),(.008,.005,z1-z0),'stone')
   for z in [i*tile for i in range(1,int(self.d/tile))]:
    if z0<z<z1:self.box(((x0+x1)/2,.073,z),(x1-x0,.005,.008),'stone')
 def sidewalls(self,m='marble',openings=True):
  # Interrupt the lounge walls for lateral routes into the existing casino.
  for side in [-1,1]:
   for start,end in [(0,self.d*.33),(self.d*.33+4,self.d*.72),(self.d*.72+4,self.d)]:
    if end<=start:continue
    self.box((side*(self.w/2+.12),self.h/2,(start+end)/2),(.24,self.h,end-start),m,solid=True)
    for y in [.14,1.12,self.h-.2]:self.box((side*(self.w/2-.025),y,(start+end)/2),(.08,.10,end-start),'gold' if m=='marble' else 'bronze')
   self.box((side*(self.w/2+.12),self.h-.35,self.d/2),(.3,.7,self.d),m)
 def ceiling(self,m='plaster'):
  self.box((0,self.h+.06,self.d/2),(self.w+.3,.16,self.d+.2),m)
  for side in [-1,1]:self.box((side*(self.w/2-.20),self.h-.17,self.d/2),(.05,.045,self.d),'warm')
 def coffer(self,x,z,w,d,y=None,m='white'):
  y=y or self.h-.15;self.box((x,y+.06,z),(w,.10,d),m)
  for offset,thick,dep,mat in [(0,.12,.20,'stone'),(.18,.055,.13,'gold'),(.30,.10,.06,m)]:
   for sign in [-1,1]:self.box((x+sign*(w/2-offset),y-dep/2,z),(thick,dep,d-2*offset),mat);self.box((x,y-dep/2,z+sign*(d/2-offset)),(w-2*offset,dep,thick),mat)
 def glass_front(self,height=7,width=None,frame='black',doorwidth=5,doorheight=4.2,dooroffset=0):
  w=width or self.w;old=self.role;self.role='shell'
  blocked=[(a,b) for a,b,c,d in getattr(self,'floor_exclusions',[]) if c<.1 and d>-.1]
  def spans(x0,x1):
   result=[(x0,x1)]
   for a,b in blocked:
    result=[piece for lo,hi in result for piece in ([(lo,hi)] if hi<=a or lo>=b else [(lo,min(hi,a)),(max(lo,b),hi)]) if piece[1]-piece[0]>.01]
   return result
  # The fixed curtain wall genuinely replaces the old opaque facade.
  # Existing guest cores can meet this facade; do not run new glass through them.
  for x0,x1 in spans(-w/2,dooroffset-doorwidth/2)+spans(dooroffset+doorwidth/2,w/2):
   self.box(((x0+x1)/2,height/2,0),(x1-x0,height,.035),'glass');self.proxy('fixed glazing',((x0+x1)/2,height/2,0),(x1-x0,height,.08))
  self.box((dooroffset,(height+doorheight)/2,0),(doorwidth,height-doorheight,.035),'glass')
  for x in sorted(set([-w/2,w/2,dooroffset-doorwidth/2,dooroffset+doorwidth/2]+[i*2.1 for i in range(-int(w/4.2),int(w/4.2)+1) if abs(i*2.1-dooroffset)>doorwidth/2])):
   if not any(a<x<b for a,b in blocked):self.box((x,height/2,-.045),(.075,height,.15),frame)
  for y in [doorheight]+[doorheight+2.3*i for i in range(1,int((height-doorheight)/2.3)+1)]+[height]:
   for x0,x1 in spans(-w/2,w/2):self.box(((x0+x1)/2,y,-.045),(x1-x0,.07,.17),frame)
  self.box((dooroffset,.025,-.05),(doorwidth,.035,.35),'silver')
  for x in [dooroffset-doorwidth/2-.15,dooroffset+doorwidth/2+.15]:self.box((x,doorheight/2,-.12),(.10,doorheight+.1,.22),frame)
  self.role=old
 def finish(self):
  made=[]
  for (role,m),(vs,fs,sm) in self.groups.items():
   name=f'Arrival / {self.name} / {role} / {m}';me=bpy.data.meshes.new(name);me.from_pydata([(x,-z,y) for x,y,z in vs],[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.materials.append(bpy.data.materials['arrival_'+m]);ob=bpy.data.objects.new(name,me);bpy.context.scene.collection.objects.link(ob)
   ob['visibilityRole']=role;ob['arrivalOwner']=self.owner;ob['arrivalName']=self.name
   uv=me.uv_layers.new(name='ArrivalUV')
   for f,smooth in zip(me.polygons,sm):
    f.use_smooth=smooth;axis=max(range(3),key=lambda i:abs(f.normal[i]));axes=[i for i in range(3) if i!=axis]
    for j in f.loop_indices:
     p=me.vertices[me.loops[j].vertex_index].co;uv.data[j].uv=(p[axes[0]]/(2 if m=='wood' else 3.2),p[axes[1]]/(2 if m=='wood' else 3.2))
   made.append(ob)
  return made
