"""Photo-led public architecture, applied incrementally to the current local stage.

Door leaves, shell walls, guest-core cutouts and public routes retain ownership.
All small decorative geometry is batched and has no physics body.
"""
import bpy,bmesh,math,json,random
from pathlib import Path
from mathutils import Vector
ROOT=Path('build/public-resorts');BASE=ROOT/'before';OUT=Path('build/hotels')
bpy.ops.wm.open_mainfile(filepath=str((BASE/'staged-vegas.blend').resolve()))
data=json.loads((BASE/'staged-vegas.mesh-level.json').read_text())
towers=json.loads(Path('src/work/hotels/towers.json').read_text())
inventory={x['name']:x for x in json.loads((ROOT/'inventory.json').read_text())}
groups={};colliders=[];removed=[];counts={};P='';ROLE='interior';rng=random.Random(8367)
FACES=[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)]
def mat(n,c,metal=0,rough=.5,glow=0,texture=None):
 n='pr_'+n;m=bpy.data.materials.get(n) or bpy.data.materials.new(n);m.use_nodes=True;m.diffuse_color=(*c,1)
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*c,1);bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough
 bs.inputs['Emission Color'].default_value=(*c,1);bs.inputs['Emission Strength'].default_value=glow
 if texture:
  tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str((ROOT/'textures'/texture).resolve()),check_existing=True);tex.image.pack();m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
 return n
for n,c,metal,rough,glow in [
 ('ivory',(.76,.70,.58),0,.55,0),('white',(.88,.87,.80),0,.42,0),('champagne',(.70,.56,.32),.65,.3,0),('gold',(.65,.42,.13),.72,.30,0),('black',(.025,.03,.034),.1,.27,0),('darkwood',(.095,.046,.025),0,.4,0),('walnut',(.26,.12,.055),0,.43,0),('warmwood',(.47,.27,.13),0,.4,0),('silver',(.56,.63,.64),.78,.26,0),('glass',(.16,.29,.34),.48,.22,0),('greeniron',(.07,.19,.16),.52,.38,0),('sageglass',(.40,.57,.51),.32,.28,0),('plum',(.16,.025,.13),.05,.45,0),('red',(.44,.025,.045),.05,.4,0),('blue',(.025,.045,.13),.05,.5,0),('pink',(.9,.035,.30),.1,.3,.65),('violet',(.35,.045,.7),.1,.3,.6),('cyan',(.025,.40,.75),.08,.35,.55),('warm',(.95,.80,.49),.05,.3,1.4),('crystal',(.84,.86,.96),.35,.22,.42),('leaf',(.065,.20,.085),0,.85,0),('lime',(.43,.53,.12),0,.65,0),('rose',(.70,.13,.31),0,.6,0)]:mat(n,c,metal,rough,glow)
for prop in ['bellagio','paris','caesars','flamingo','horseshoe','planet-hollywood','aria']:mat(prop+'carpet',(1,1,1),rough=.95,texture=prop+'-carpet.png')
mat('sky',(1,1,1),rough=1,texture='paris-sky.png')
def material(n):return n if n.startswith('pr_') else 'pr_'+n
def tr(p,o=(0,0,0),a=0):
 x,y,z=p;c,s=math.cos(a),math.sin(a);return (o[0]+c*x+s*z,o[1]+y,o[2]-s*x+c*z)
def reserved(p,pad=0):
 for t in towers:
  x=p[0]-t['origin'][0];z=p[2]-t['origin'][2];c,s=math.cos(t['yaw']),math.sin(t['yaw']);xx=c*x-s*z;zz=s*x+c*z
  if abs(xx)<4.05+pad and -5.5-pad<zz<5.5+pad and -.2<p[1]<t['firstGuestFloor']*3.6+.5:return True
 return False
def mesh(n,vs,fs,m,role=None):
 # Keep newly suspended decor outside streamed shafts; the existing shell
 # already has precise, tested openings and remains the structural ceiling.
 center=tuple(sum(p[i] for p in vs)/len(vs) for i in range(3))
 if ROLE=='interior' and (reserved(center) or any(reserved(v) for v in vs)):return
 k=(P,role or ROLE,material(m));g=groups.setdefault(k,dict(v=[],f=[]));b=len(g['v']);g['v'].extend(vs);g['f'].extend(tuple(b+i for i in f) for f in fs);counts[P]=counts.get(P,0)+1
def box(n,p,s,m='ivory',a=0,solid=False):
 w,h,d=[v/2 for v in s];vs=[tr((x,y,z),p,a) for x in [-w,w] for y in [-h,h] for z in [-d,d]]
 if ROLE=='interior' and (reserved(p) or any(reserved(v) for v in vs)):return
 mesh(n,vs,FACES,m)
 if solid:colliders.append(dict(name=f'Public design / {P} / {n} / {len(colliders):04}',shape='box',position=list(p),size=list(s),yaw=a))
def beam(n,a,b,r,m='gold',sides=8):
 va,vb=Vector(a),Vector(b);dr=(vb-va).normalized();u=dr.cross(Vector((0,1,0)))
 if u.length<.01:u=dr.cross(Vector((1,0,0)))
 u.normalize();v=dr.cross(u).normalized();vs=[tuple(p+r*(u*math.cos(i*math.tau/sides)+v*math.sin(i*math.tau/sides))) for p in [va,vb] for i in range(sides)]
 fs=[tuple(reversed(range(sides))),tuple(range(sides,sides*2))]+[(i,(i+1)%sides,(i+1)%sides+sides,i+sides) for i in range(sides)];mesh(n,vs,fs,m)
def lathe(n,x,z,profile,m='gold',N=40,scale=(1,1)):
 vs=[(x+r*math.cos(i*math.tau/N)*scale[0],y,z+r*math.sin(i*math.tau/N)*scale[1]) for r,y in profile for i in range(N)]
 fs=[(k*N+i,k*N+(i+1)%N,(k+1)*N+(i+1)%N,(k+1)*N+i) for k in range(len(profile)-1) for i in range(N)];mesh(n,vs,fs,m)
def ring(x,y,z,rx,rz,width,m='gold',height=.12):lathe('ring',x,z,[(1,y-height/2),(1,y+height/2),(1-width/rx,y+height/2),(1-width/rx,y-height/2),(1,y-height/2)],m,64,(rx,rz))
def path(n,pts,r=.05,m='gold'):
 for a,b in zip(pts,pts[1:]):beam(n,a,b,r,m)
def text(words,p,size=.4,a=0,m='gold',width=10):
 cu=bpy.data.curves.new('Public lettering','FONT');cu.body=words;cu.align_x='CENTER';cu.align_y='CENTER';cu.size=size;cu.resolution_u=3;cu.extrude=.003
 o=bpy.data.objects.new('Public lettering',cu);bpy.context.scene.collection.objects.link(o);bpy.context.view_layer.update();me=bpy.data.meshes.new_from_object(o.evaluated_get(bpy.context.evaluated_depsgraph_get()));xs=[v.co.x for v in me.vertices];sc=min(1,width/max(.001,max(xs)-min(xs)))
 mesh('lettering',[tr((v.co.x*sc,v.co.y,v.co.z),p,a) for v in me.vertices],[tuple(f.vertices) for f in me.polygons],m)
 bpy.data.objects.remove(o,do_unlink=True);bpy.data.meshes.remove(me)
def panel(p,w,h,a=0,m='gold',thick=.05):
 for dx in [-w/2,w/2]:box('panel stile',tr((dx,0,0),p,a),(thick,h,.065),m,a)
 for dy in [-h/2,h/2]:box('panel rail',tr((0,dy,0),p,a),(w,thick,.065),m,a)
def arch(p,w,h,a=0,m='ivory',r=.12):
 spring=h-w/2
 pts=[tr((-w/2,0,0),p,a),tr((-w/2,spring,0),p,a)]+[tr((w/2*math.cos(math.pi-i*math.pi/32),spring+w/2*math.sin(i*math.pi/32),0),p,a) for i in range(33)]+[tr((w/2,0,0),p,a)]
 path('arched moulding',pts,r,m)
def column(x,z,h=6,r=.38,m='ivory'):
 lathe('column',x,z,[(0,.075),(r*1.45,.075),(r*1.45,.3),(r*1.1,.4),(r,.65),(r*.85,h-.5),(r*1.5,h-.4),(r*1.5,h),(0,h)],m,24)
 box('column collision',(x,h/2,z),(r*2,h,r*2),m,solid=True)
def chandelier(x,z,y=7,r=1.5,drop=1.8,style='crystal'):
 ring(x,y,z,r,r,.13,'gold',.17)
 for k in range(3):
  rr=r*(1-k*.27);yy=y-k*drop*.32;ring(x,yy,z,rr,rr,.045,'champagne',.08)
  for i in range(20-k*4):
   a=i*math.tau/(20-k*4);px=x+rr*math.cos(a);pz=z+rr*math.sin(a)
   lathe('crystal pendant',px,pz,[(.035,yy),(.07,yy-.20),(.04,yy-drop*.36),(0,yy-drop*.43)],'crystal',6)
 beam('chandelier suspension',(x,y,z),(x,y+.8,z),.045,'gold')
def medallion(x,z,r,m='black',y=.155):
 for rr in [r,r-.25,r-.75]:ring(x,y,z,rr,rr,.055,m,.012)
 for i in range(24):
  a=i*math.tau/24;mesh('stone medallion',[(x+r2*math.cos(a2),y+.004,z+r2*math.sin(a2)) for r2,a2 in [(r-.3,a),(r-.3,a+.05),(r-.65,a+.05),(r-.65,a)]],[(0,1,2,3)],m)
def desk(x,z,w=12,m='darkwood',a=0,front='ivory'):
 box('reception base',(x,.63,z),(w,1.11,1.55),m,a,True);box('reception stone top',(x,1.24,z),(w+.22,.12,1.75),'black',a)
 for xx in [(-w/2+1)+i*2 for i in range(int(w/2))]:
  p=tr((xx,.68,.795),(x,0,z),a);box('counter raised field',p,(1.8,.72,.055),front,a);panel(tr((xx,.68,.833),(x,0,z),a),1.55,.56,a,'champagne')
  box('registration terminal',tr((xx,1.49,-.2),(x,0,z),a),(.55,.40,.12),'black',a)
def vase(x,z,y=1.32,r=.28):
 lathe('urn',x,z,[(r*.55,y),(r,y+.18),(r*1.12,y+.64),(r*.6,y+.88),(r*.78,y+.97)],'ivory',16)
 for i in range(12):
  a=i*2.4;px=x+math.cos(a)*r*1.7;pz=z+math.sin(a)*r*1.7;yy=y+1.2+(i%3)*.21
  beam('flower stem',(x,y+.6,z),(px,yy,pz),.018,'leaf',5)
  lathe('flower bloom',px,pz,[(0,yy-.11),(.18,yy),(.15,yy+.16),(0,yy+.22)],'rose' if i%3 else 'white',7)
def seating(x,z,w=3,m='ivory',a=0):
 box('sofa base',(x,.36,z),(w,.52,.95),m,a,True);box('sofa back',tr((0,.85,.43),(x,0,z),a),(w,.78,.24),m,a)
 for dx in [-w/2+.14,w/2-.14]:box('sofa arm',tr((dx,.65,0),(x,0,z),a),(.23,.65,1.02),m,a)
 for dx in [-w*.26,0,w*.26]:box('sofa cushion',tr((dx,.66,-.03),(x,0,z),a),(w*.25,.14,.73),m,a)
def tree(x,z,r=.6,h=4,planter='red'):
 lathe('planter',x,z,[(0,.075),(r*.75,.075),(r,1.25),(0,1.25)],planter,16)
 beam('tree trunk',(x,1.1,z),(x+.12,h,z),.07,'darkwood')
 for i in range(13):
  a=i*2.4;xx=x+.85*math.cos(a);zz=z+.85*math.sin(a);yy=h-.6+(i%3)*.45
  beam('branch',(x,h-.8,z),(xx,yy,zz),.035,'darkwood',5)
  lathe('leaf cluster',xx,zz,[(0,yy-.4),(.45,yy),(.3,yy+.35),(0,yy+.5)],'leaf',7)
def facade_frame(o,yaw,w=6,h=4.5,m='gold'):
 for xx in [-w/2-.24,w/2+.24]:box('door jamb',tr((xx,h/2,0),o,yaw),(.28,h,.35),m,yaw)
 box('door transom',tr((0,h+.15,0),o,yaw),(w+.8,.3,.4),m,yaw)
 # Decorative side lights terminate outside the real sliding door opening.
 for xx in [-w/2-1.3,w/2+1.3]:
  box('sidelight',tr((xx,h/2,-.10),o,yaw),(1.6,h,.12),'glass',yaw)
  panel(tr((xx,h/2,.015),o,yaw),1.55,h-.18,yaw,m,.09)
def canopy(o,yaw,w=18,d=8,y=6,m='black'):
 box('canopy roof',tr((0,y,d/2),o,yaw),(w,.40,d),m,yaw)
 for xx in [-w/2+.55,w/2-.55]:
  box('canopy pier',tr((xx,y/2,d-.7),o,yaw),(.65,y,.65),m,yaw,True)
 for zz in [i*d/6 for i in range(1,6)]:box('canopy light',tr((0,y-.24,zz),o,yaw),(w-1,.05,.08),'warm',yaw)
 facade_frame(o,yaw)
def ceiling_coffer(x,z,y,w,d,m='ivory',border='gold'):
 box('coffer field',(x,y+.15,z),(w,.12,d),m)
 for dx in [-w/2,w/2]:box('coffer edge',(x+dx,y,z),(.18,.27,d+.18),border)
 for dz in [-d/2,d/2]:box('coffer edge',(x,y,z+dz),(w,.27,.18),border)
def recolor(o,slot,matname):
 mats=o.data.materials
 if matname not in [m.name if m else '' for m in mats]:mats.append(bpy.data.materials[matname])
 idx=[m.name if m else '' for m in mats].index(matname)
 for p in o.data.polygons:
  if slot(p):p.material_index=idx
def uv_world(o):
 uv=o.data.uv_layers.get('PublicUV') or o.data.uv_layers.new(name='PublicUV');o.data.uv_layers.active=uv
 for f in o.data.polygons:
  axis=max(range(3),key=lambda i:abs(f.normal[i]));axes=[i for i in range(3) if i!=axis]
  scale=40 if o.data.materials[f.material_index].name=='pr_sky' else 6
  for j in f.loop_indices:
   v=o.matrix_world@o.data.vertices[o.data.loops[j].vertex_index].co;uv.data[j].uv=(v[axes[0]]/scale,v[axes[1]]/scale)

# Replace just obsolete furnishing and suspended treatments. Structural objects
# and their carefully cut guest-core voids are never reconstructed here.
for o in list(bpy.context.scene.objects):
 if o.type!='MESH':continue
 n=o.name.lower();info=inventory.get(o.name);kill=False
 if n.startswith('interiors /'):
  if info and info['hi'][1]<4.1:
   for x,z,w in [(81,-25,10),(-41,267,13),(157,-251,14),(120,-91,10),(78,201,14)]:
    if all(info['lo'][i]>v0 and info['hi'][i]<v1 for i,v0,v1 in [(0,x-w/2-.5,x+w/2+.5),(2,z-1,z+1)]):kill=True
  kill=kill or ('registration' in n or any(word in n for word in ['chandelier','ceiling inset','coffer molding'])) and not ('forum' in n)
 if n.startswith('bellagio') and ('reception curved desk' in n or 'reception marble countertop' in n):kill=True
 if n.startswith('caesars') and 'casino chandelier' in n:kill=True
 if 'co_crystal' in n and n.startswith('cosmopolitan'):kill=True
 if n.startswith('exterior /') and any(k in n for k in ['flamingo','planet hollywood','horseshoe']):
  if any(k in n for k in ['entrance canopy','canopy pier','canopy light','barrel canopy']):kill=True
  if n.startswith('exterior / horseshoe /') and 'horseshoe glyphs' in n and info and info['hi'][1]<7 and info['hi'][2]<-150:kill=True
 if n.startswith('citycenter / aria / interior / light'):kill=True
 if n.startswith('citycenter /') and '/ reception glyphs' in n:kill=True
 if n.startswith('citycenter / vdara / interior /') and any(n.endswith('/ '+k) for k in ['wood','marble','black']):kill=True
 if n.startswith('citycenter / waldorf / interior /') and any(n.endswith('/ '+k) for k in ['wood','marble','black']):kill=True
 if kill:removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True);continue
 if not info:continue
 key=next((k for k in ['bellagio','paris','caesars','flamingo','horseshoe','planet hollywood','aria'] if k in n),None)
 if key and ('carpet' in n or any(m and ('carpet' in m.name) for m in o.data.materials)):
  target='pr_'+key.replace(' ','-')+'carpet';old={i for i,m in enumerate(o.data.materials) if m and ('carpet' in n or 'carpet' in m.name)}
  recolor(o,lambda f: f.material_index in old and all((o.matrix_world@o.data.vertices[i].co).z<.22 for i in f.vertices),target);uv_world(o)
 # Flat bright PH ceiling becomes dark over the colorful luminous columns.
 if 'planet hollywood ceiling' in n:recolor(o,lambda f:True,'pr_black')
 # Existing Paris casino sky is part of its identifiable indoor street design.
 if 'paris' in n and 'ceiling' in n and 'casino' in n:recolor(o,lambda f:True,'pr_sky');uv_world(o)
data['colliders']=[c for c in data['colliders'] if c['name'] not in removed and not (c['name'].startswith('CityCenter /') and any(n in c['name'] for n in ['VDARA desk','ARIA desk','WALDORF ASTORIA desk']))]

# BELLAGIO: preserve the vaulted entrance and glass garden; enrich the check-in
# wall and carved counter using the repeated arched garden openings in photos.
P='bellagio'
desk(-179,-61,24,'darkwood',math.pi/2,'ivory')
for z in [-69,-65,-61,-57,-53]:
 box('reception garden backing',(-190.30,3.8,z),(.10,4.1,3.25),'blue')
 arch((-190.12,1.55,z),3.35,4.6,math.pi/2,'ivory',.19)
 for y in [1.35,6.3,6.6]:box('reception dado',(-190.04,y,z),(.24,.16,4),'champagne')
 vase(-179,z,1.32,.3)

# PARIS: ornate registration salon and a green iron/glass arrival canopy.
P='paris';ROLE='shell';o=(72,.075,-39);a=-math.pi/2
facade_frame(o,a,6,4.8,'greeniron')
for j in range(13):
 zz=j*.8
 pts=[tr((xx,6.0+1.7*math.cos(xx/12*math.pi/2),zz),o,a) for xx in [-12+i*.5 for i in range(49)]]
 path('Art Nouveau canopy rib',pts,.075,'greeniron')
for i in range(24):
 x0=-12+i; x1=x0+1;y0=6+1.7*math.cos(x0/12*math.pi/2);y1=6+1.7*math.cos(x1/12*math.pi/2)
 mesh('green glass canopy',[tr(p,o,a) for p in [(x0,y0,0),(x1,y1,0),(x1,y1,9.7),(x0,y0,9.7)]],[(0,1,2,3),(3,2,1,0)],'sageglass')
for xx in [-11.5,11.5]:
 for zz in [1,9]:column(*[tr((xx,0,zz),o,a)[i] for i in [0,2]],h=6.1,r=.24,m='greeniron')
for xx in range(-11,12,2):
 path('iron scroll',[tr((xx+.55*math.cos(t),5.82+.55*math.sin(t),9.78),o,a) for t in [i*math.tau/24 for i in range(25)]],.055,'greeniron')
text('P A R I S',tr((0,6.65,9.91),o,a),.74,a,'gold',8)
ROLE='interior';desk(81,-25,10,'ivory',math.pi,'ivory')
box('registration marble inlay',(81,.15,-28),(17.8,.025,16),'ivory')
for x in [74.5,77.1,79.7,82.3,84.9,87.5]:
 for z in [-34,-31.4,-28.8,-26.2,-23.6]:
  box('lobby marble diamond',(x,.169,z),(.40,.008,.40),'glass',math.pi/4)
for z in [-34.5,-21.5]:box('salon floor border',(81,.17,z),(17,.012,.10),'champagne')
for x in [77,85]:
 for z in [-30,-22]:ceiling_coffer(x,z,7.2,7.5,7.5,'ivory','gold')
box('registration salon wall',(81,3.55,-19.7),(16.5,6.9,.20),'ivory')
for x in [74.5,78.8,83.1,87.4]:
 panel((x,3.8,-19.85),3.65,4.6,math.pi,'gold',.07)
 box('salon pilaster',(x+2,3.45,-20.02),(.36,6.7,.30),'ivory')
 box('gilt capital',(x+2,6.55,-20.04),(.63,.34,.38),'gold')
for x in [77.5,84.5]:chandelier(x,-24,6.95,1.35,1.65)
for x in [77,85]:vase(x,-25,1.3,.2)
text('LA RECEPTION',(81,5.85,-19.86),.43,math.pi,'gold',8)
# Blue vaulted promenades and stone arch/pier rhythm, with real Eiffel legs kept.
for z in [-54,-8,3]:
 for x in [103,126]:
  ceiling_coffer(x,z,7.4,12,8,'sky','ivory')
for z in [-62,-47,-15,0]:
 for x in [74,136]:
  if not reserved((x,3,z),.5):
   box('French street pilaster',(x,3.2,z),(.65,6.3,.65),'ivory')
   box('street pier capital',(x,6.25,z),(1.0,.3,1.0),'gold')

# CAESARS: concentric coffered arrival dome, Roman mosaic and Augustus.
P='caesars';cx,cz=-115,-240
lathe('shallow arrival dome',cx,cz,[(r,7.92-1.22*(r/12.4)**2) for r in [i*12.4/24 for i in range(25)]],'ivory',64,(1,.72))
for rr in [12.4,11.9,9.6,7.2,4.8]:ring(cx,7.83-1.22*(rr/12.4)**2,cz,rr,rr*.72,.18,'champagne',.15)
for lo,hi in [(9.85,11.62),(7.45,9.30),(5.10,6.90)]:
 for i in range(32):
  a=i*math.tau/32+.025;b=(i+1)*math.tau/32-.025
  vs=[(cx+r*math.cos(t),7.78-1.22*(r/12.4)**2,cz+r*.72*math.sin(t)) for r,t in [(lo,a),(hi,a),(hi,b),(lo,b)]]
  mesh('radial inset coffer',vs,[(0,1,2,3)],'warmwood');path('coffer gilt edge',vs+[vs[0]],.028,'gold')
lathe('arrival marble medallion',cx,cz,[(0,.151),(9.4,.151),(9.4,.148),(0,.148)],'ivory',96)
medallion(cx,cz,9.1,'black',.16);chandelier(cx,cz,7.15,2.2,2.05)
for x,z in [(-125,-250),(-101,-250),(-126,-229),(-100,-229)]:column(x,z,7.8,.46,'gold')
# The statue is offset from the 6m entry avenue and garden turn.
sx,sz=-118,-232
lathe('Augustus marble plinth',sx,sz,[(0,.1),(1.0,.1),(1.05,.3),(1.0,1.45),(.84,1.57),(0,1.57)],'black',32)
box('statue collision',(sx,2.7,sz),(1.7,5.2,1.5),'ivory',solid=True)
# Sculpted drapery silhouette, limbs and head replace the box proxy above.
# Remove its visual box while retaining one simple obstacle collider.
g=groups[(P,ROLE,'pr_ivory')];g['v']=g['v'][:-8];g['f']=g['f'][:-6]
lathe('Roman toga',sx,sz,[(.25,1.55),(.58,1.7),(.5,2.75),(.45,3.3),(.7,4.15),(.5,4.45),(.2,4.55)],'ivory',16,(1,.70))
lathe('statue head',sx,sz,[(.12,4.45),(.29,4.65),(.30,4.95),(.21,5.15),(0,5.22)],'ivory',16,(1,.88))
path('raised imperial arm',[(sx-.5,4.15,sz),(sx-1.0,4.55,sz),(sx-1.35,5.3,sz+.2)],.17,'ivory')
path('lower arm',[(sx+.5,4.1,sz),(sx+.75,3.55,sz+.2),(sx+.62,3.25,sz+.35)],.17,'ivory')
for i in range(9):
 a=i*math.tau/9;path('toga pleat',[(sx+.48*math.cos(a),1.7,sz+.34*math.sin(a)),(sx+.32*math.cos(a+.4),2.75,sz+.25*math.sin(a+.4)),(sx+.57*math.cos(a),4.0,sz+.34*math.sin(a))],.045,'white')
ROLE='shell'
for z in [-251,-247,-237,-233]:ceiling_coffer(-85,z,9.7,5,3.5,'ivory','gold')
facade_frame((-92,.075,-242),math.pi/2,6,4.8,'gold')
ROLE='interior'
for x in [-136,-150]:
 for z in [-250,-229]:ceiling_coffer(x,z,7.45,10,7,'ivory','champagne');chandelier(x,z,7.1,1.2,1.5)

# COSMOPOLITAN: black/gold lobby and eight illuminated digital columns.
P='cosmopolitan';ROLE='shell';o=(-29,.075,242);a=math.pi/2
canopy(o,a,18,4.8,6.0,'black')
box('LED entry crown',tr((0,7.55,.35),o,a),(18,2.9,.35),'blue',a)
for i in range(30):box('LED color bars',tr((-8.7+i*.60,7.55,.57),o,a),(.32,2.8,.06),'violet' if i%3 else 'cyan',a)
text('THE COSMOPOLITAN',tr((0,5.32,.66),o,a),.66,a,'crystal',16)
ROLE='interior';desk(-41,267,12,'red',math.pi,'red')
box('black marble reception floor',(-43,.145,257),(22,.026,23),'black')
for x in [-53,-48,-43,-38,-33]:box('gold floor inlay',(x,.163,257),(.045,.008,22),'champagne')
for z in [246,251,256,261,266]:box('gold floor cross inlay',(-43,.163,z),(21,.008,.045),'champagne')
box('reception digital wall',(-42,3.2,272.6),(22,5.8,.20),'black')
for x in range(-52,-31):
 for y in [1.8,2.5,3.2,3.9,4.6]:box('registration art tile',(x,y,272.45),(.93,.62,.06),['blue','cyan','violet','glass'][(x+int(y*10))%4])
for x in [-51,-35]:
 for z in [249,254,259,264]:
  box('digital column core',(x,2.68,z),(1.18,5.2,1.18),'black',solid=True)
  for a in [0,math.pi/2,math.pi,3*math.pi/2]:
   for iy in range(8):
    for ix in [-.32,.32]:
     pp=tr((ix,.48+iy*.57,.602),(x,0,z),a);box('video tessera',pp,(.59,.53,.018),['cyan','blue','violet','champagne','glass'][(iy+int(abs(x))+int(z)+int(ix*10))%5],a)
for x in [-52,-44,-36]:
 for z in [250,257,264]:ceiling_coffer(x,z,7.7,7.4,6.4,'black','champagne')
# Dense draped crystal strands describe the enclosing Chandelier silhouette.
cx,cz=-59,218
for i in range(100):
 a=i*math.tau/100
 pts=[]
 for k in range(11):
  y=2.3+k*.53;r=4.7+.75*math.sin(k/10*math.pi)
  pts.append((cx+r*math.cos(a),y,cz+r*.78*math.sin(a)))
 path('Chandelier bead strand',pts,.018,'crystal')
 for k in [1,3,5,7,9]:
  px,yy,pz=pts[k];lathe('cut crystal',px,pz,[(0,yy-.07),(.045,yy),(.025,yy+.07),(0,yy+.12)],'crystal',5)
for y in [3.8,6.3,7.75]:ring(cx,y,cz,5.05,3.95,.09,'champagne')
for z in [216.3,219.7]:
 for x in [-60.3,-59,-57.7]:box('bar illuminated fascia',(x,.85,z),(1.16,.70,.06),'violet')
for x in [-157,-141,-107,-91]:
 for z in [209,260]:ceiling_coffer(x,z,7.8,12,9,'black','champagne');chandelier(x,z,7.55,1.25,1.3)

# FLAMINGO: feathered pink entrance, white reception and colored ceiling bands.
P='flamingo';ROLE='shell';o=(90,.075,-237);a=-math.pi/2
canopy(o,a,18,7,5.45,'pink')
for i in range(17):
 angle=-1.27+i*2.54/16;dx=math.sin(angle)*6.6;dy=math.cos(angle)*5.3
 pts=[tr((dx*t,5.4+dy*t,7.12+math.sin(t*math.pi)*.3),o,a) for t in [j/20 for j in range(21)]];path('neon feather',pts,.055,'pink')
text('Flamingo',tr((0,6.05,7.3),o,a),1.25,a,'warm',13)
canopy((145,.075,-215),0,12,4,5.4,'pink')
ROLE='interior';desk(157,-251,13,'ivory',0,'white')
box('registration timber wall',(157,3.4,-257.5),(18,6.5,.3),'walnut')
for x in [150.5,157,163.5]:
 box('checkin sign',(x,3.8,-257.30),(3.5,1.35,.10),'ivory');text('Flamingo',(x,3.8,-257.22),.50,0,'pink',3.2)
for x in [148,166]:
 box('reception pilaster',(x,3.35,-252),(1.0,6.5,1.0),'ivory')
 for h in [.25,5.9,6.4]:box('white capital',(x,h,-252),(1.35,.18,1.35),'white')
for i,m in enumerate(['pink','warm','cyan','violet']):ring(121,8.8+i*.21,-237,24-i*2,13-i*1.3,.85,m,.18)
for x in [104,122,140]:
 for z in [-250,-222]:ceiling_coffer(x,z,9.65,14,8,'black','champagne')

# HORSESHOE: red arrival arch, illuminated drum pylons and long casino coffers.
P='horseshoe';ROLE='shell';o=(110,.075,-147);a=math.pi
canopy(o,a,15,6.4,5.8,'red')
for xx in [-6.6,6.6]:
 q=tr((xx,0,5.8),o,a);column(q[0],q[2],6.5,.67,'crystal')
 for y in [1,2,3,4,5,6]:ring(q[0],y,q[2],.76,.76,.045,'black')
for zz in [0,2.5,5.8]:arch(tr((0,0,zz),o,a),13.4,8.2,a,'white',.16)
text('HORSESHOE',tr((0,7.0,6.65),o,a),.77,a,'warm',12)
pts=[tr((1.2*math.cos(t),9.0+1.3*math.sin(t),6.6),o,a) for t in [math.pi*.20+i*math.pi*1.60/48 for i in range(49)]];path('gold horseshoe emblem',pts,.16,'gold')
ROLE='interior';desk(120,-91,8.5,'walnut',math.pi,'ivory')
for z in [-96,-106,-116,-126]:
 ceiling_coffer(110,z,9.45,6.8,8.8,'ivory','darkwood');chandelier(110,z,9.05,1.6,2.1)
 for x in [97,123]:ceiling_coffer(x,z,8.2,7,8.8,'ivory','darkwood')
for x in [117,120,123]:
 box('checkin kiosk',(x,1.2,-96),(1.0,2.15,.65),'black',solid=True)
 box('kiosk display',(x,1.72,-96.345),(.7,.65,.02),'cyan')

# PLANET HOLLYWOOD: luminous columns, faceted ceiling and oval escalator lobby.
P='planet-hollywood';ROLE='shell';o=(65,.075,218);a=-math.pi/2
canopy(o,a,19,7,6.0,'black')
for i in range(23):
 x=-9+i*.8;path('LED fan',[tr((x,5.73,.2),o,a),tr((x*.53,5.55,6.8),o,a)],.055,'pink' if i%3 else 'crystal')
text('planet hollywood',tr((0,6.77,7.05),o,a),.91,a,'warm',17)
canopy((174,.075,274),0,14,4,5.5,'black')
ROLE='interior';desk(78,201,13,'black',0,'plum')
box('violet reception wall',(78,3.8,196),(15,7.3,.3),'violet')
for ix in range(25):
 for iy in range(8):
  x=71+ix*.58;y=.7+iy*.79
  lathe('reception honeycomb',x,196.18,[(.21,y),(.21,y+.015)],'black',6) if False else None
  # Flat hexagon relief on the vertical illuminated backdrop.
  vs=[(x+.25*math.cos(k*math.tau/6),y+.25*math.sin(k*math.tau/6),196.18) for k in range(6)]
  mesh('hexagonal wall cell',vs,[tuple(range(6))],'black')
for x in [73,78,83]:
 box('checkin screen',(x,3.6,196.28),(1.5,2.4,.1),'black');panel((x,3.6,196.35),1.7,2.6,0,'champagne',.08)
for i in range(4):ring(82,10.0-i*.32,232,11-i*1.45,17-i*1.7,.48,'violet' if i%2 else 'ivory',.18)
for x in [73,92]:
 for z in [227,239]:chandelier(x,z,7.6,1.0,3.4)
for x in [99,119,142,163]:
 for z in [192,244]:
  box('luminous casino column',(x,4.75,z),(1.05,9.3,1.05),'warm',solid=True)
  for y in [i*.35+.3 for i in range(27)]:box('column dark band',(x,y,z),(1.1,.09,1.1),'black')
for x in [112,138,160]:
 for z in [204,230]:
  ceiling_coffer(x,z,10.8,18,18,'black','champagne');ring(x,9.75,z,3,3,.15,'pink')
  lathe('illuminated orb',x,z,[(0,7.7),(.7,7.95),(1,8.45),(.8,9.1),(0,9.45)],'violet',20)

# ARIA: layered arrival canopy, registration's silver river and sculptural coves.
P='aria';ROLE='shell';o=(-244,.075,448);a=math.pi/2
facade_frame(o,a,5,4.2,'silver')
for j in range(16):
 zz=-23+j*3
 path('arrival soffit slat',[(-244,7.63,448+zz),(-229,7.63+.015*zz*zz,448+zz)],.09,'warmwood')
for z in [428,469]:tree(-236,z,.7,4.5,'ivory')
ROLE='interior'
# Replace the former straight desk's faces, leaving all structural batches alone.
for o in list(bpy.context.scene.objects):
 if not o.name.startswith('CityCenter / Aria / interior /'):continue
 bm=bmesh.new();bm.from_mesh(o.data);gone=[]
 for f in bm.faces:
  ps=[o.matrix_world@v.co for v in f.verts]
  if all(-276<p.x<-254 and 431<-p.y<435 and p.z<2.2 for p in ps):gone.append(f)
 bmesh.ops.delete(bm,geom=gone,context='FACES');bm.to_mesh(o.data);bm.free()
data['colliders']=[c for c in data['colliders'] if not ('Aria' in c['name'] and 'reception' in c['name'].lower())]
desk(-265,433,19,'black',0,'black')
box('river artwork glass wall',(-265,5.1,427.3),(30,9.6,.20),'glass')
for x in range(-279,-249,4):box('timber registration mullion',(x,5.1,427.46),(.22,9.6,.22),'warmwood')
river=[(-279+i*1.1,6.5+.6*math.sin(i*.7)+.3*math.sin(i*2.2),427.7) for i in range(26)]
path('Silver River main course',river,.12,'silver')
for i in [3,6,11,16,20,23]:
 x,y,z=river[i];path('tributary',[(x,y,z),(x+.65,y+.8,z),(x+.28,y+1.8,z),(x+1.15,y+2.3,z)],.065,'silver')
text('A R I A',(-265,.73,433.88),.29,0,'champagne',3)
for x in [-273,-266,-258]:vase(x,433,1.34,.24)
for x in [-273,-253]:
 for z in [440,459]:tree(x,z,.6,4,'ivory')
for z in [437,451,465]:
 ceiling_coffer(-265,z,10.6,30,10,'warmwood','ivory')
 for x in range(-277,-252,2):
  pts=[(x+.7*math.sin(t*math.pi),10.33,-0+z-4+8*t) for t in [k/12 for k in range(13)]];path('perforated lobby screen',pts,.035,'black')
for x in [-434,-410,-385,-355,-326,-299]:
 for z in [361,389,421,452,480]:
  ring(x,11.25,z,8.2,4.3,.47,'warmwood',.22)
  ring(x,11.06,z,7.8,3.95,.05,'warm',.045)
  for j in range(5):path('ARIA ceiling petal',[(x-6+i*.75,11.4+.3*math.sin(i*math.pi/16),z+(j-2)*.65+math.sin(i*math.pi/16)) for i in range(17)],.045,'ivory')
  box('casino carpet inset',(x,.125,z),(19,.024,19),'ariacarpet')

# VDARA: tall quiet reception, dark lacquer and geometric rainbow artwork.
P='vdara';ROLE='shell';o=(-299,.075,273);a=0
facade_frame(o,a,5,4.2,'silver')
for j in range(14):
 t=-.9+j*1.8/13;pts=[(-307+r*math.sin(t),6.65+.02*(r-20)**2,270+r*math.cos(t)) for r in range(13,30)]
 path('Vdara curved canopy rib',pts,.095,'silver')
ROLE='interior';desk(-327,223,16,'black',0,'black')
text('V D A R A',(-327,.74,223.87),.24,0,'champagne',4)
box('lobby limestone floor',(-309,.145,241),(92,.02,61),'ivory')
for x in range(-354,-262,4):box('limestone grout',(x,.16,241),(.025,.006,61),'champagne')
for z in range(212,272,4):box('limestone grout',(-309,.16,z),(92,.006,.025),'champagne')
box('reception wood backdrop',(-327,4.0,215),(24,7.8,.35),'darkwood')
box('geometric mural canvas',(-327,4.4,215.23),(17,4.7,.12),'ivory')
for cx,sgn in [(-331,1),(-323,-1)]:
 for j,m in enumerate(['violet','warm','red','blue','lime']):
  rr=4.25-j*.5
  paint='paint_'+m
  if not bpy.data.materials.get('pr_'+paint):mat(paint,tuple(bpy.data.materials['pr_'+m].diffuse_color)[:3],rough=.9)
  vs=[(cx+r*math.cos(t),2.14+r*.96*math.sin(t),215.34+j*.006) for r in [rr,rr-.43] for t in [i*math.pi/64 for i in range(65)]]
  mesh('interlocking artwork arc',vs,[(k,k+1,k+66,k+65) for k in range(64)],paint)
for x in [-333,-321]:vase(x,223,1.32,.28)
for x,z in [(-281,255),(-310,265),(-343,234)]:seating(x,z,4,'ivory');tree(x+3,z,.6,4.3,'black')
for x in [-336,-314,-281]:
 for z in [232,260]:ceiling_coffer(x,z,10.8,16,14,'ivory','warmwood')

# WALDORF: red lacquer entry, brass screens and black-inlaid white marble.
P='waldorf';ROLE='shell'
for o,a in [((-40,.075,576),math.pi/2),((-125,.075,576),-math.pi/2)]:
 canopy(o,a,12,4,5.6,'ivory');facade_frame(o,a,5,4.2,'silver')
 for xx in [-4.4,4.4]:box('red lacquer entry',tr((xx,2.8,.24),o,a),(2.5,5.55,.20),'red',a)
 text('WALDORF ASTORIA',tr((0,5.0,4.1),o,a),.46,a,'black',10)
ROLE='interior';desk(-99,594,13,'ivory',math.pi/2,'ivory')
text('WALDORF ASTORIA',(-98.12,.76,594),.25,math.pi/2,'black',8)
box('arrival white marble floor',(-82.5,.145,578),(83,.02,84),'white')
for x in range(-123,-40,4):box('marble joint',(x,.16,578),(.026,.006,84),'ivory')
for z in range(538,621,4):box('marble joint',(-82.5,.16,z),(83,.006,.026),'ivory')
for x in [-54,-68,-82,-96]:
 for z in [567.8,584.2]:
  box('arrival gallery pier',(x,4,z),(.65,7.8,.8),'ivory',solid=True)
  panel((x+.34,4,z),.6,7.4,math.pi/2,'champagne',.045)
 box('arrival gallery lintel',(x,7.93,576),(.66,.22,17.2),'champagne')
 ceiling_coffer(x-4.9,576,8.15,8.7,16.2,'ivory','champagne')
 medallion(x-5,576,4,'black',.168)
 for yy,rr in [(7.9,1.35),(7.55,1.05),(7.25,.72)]:ring(x-5,yy,576,rr,rr,.08,'gold')
for x in [-120,-105,-68,-53]:
 box('north marble panel',(x,4.9,535.7),(12,9.5,.10),'ivory')
 panel((x,4.9,535.81),11.5,8.9,0,'champagne',.04)
for x,z in [(-74,570),(-91,550),(-96,578)]:medallion(x,z,6,'black')
for z in [550,563,583,594]:
 for x in [-114,-55]:
  box('marble pier',(x,4.3,z),(1.05,8.4,1.05),'ivory',solid=True)
  for j in range(13):box('brass room divider',(x+(j-6)*.18,3.4,z+.72),(.045,6.5,.08),'champagne')
for x,z in [(-62,557),(-107,566),(-62,588),(-106,584)]:seating(x,z,3.8,'blue');vase(x,z-2,.075,.42)
for z in [548,565,585]:
 for yy,rr in [(8.3,2.5),(7.9,1.9),(7.55,1.3)]:ring(-82,yy,z,rr,rr,.10,'gold')
 for i in range(48):
  a=i*math.tau/48;beam('chandelier gold rod',(-82+2.45*math.cos(a),7.6,z+2.45*math.sin(a)),(-82+2.45*math.cos(a),8.55,z+2.45*math.sin(a)),.028,'gold',5)

# CRYSTALS / VEER: preserve the folded roof and treehouse, enrich the residential
# arrival lounges with the white seating, lime ottoman and red planters in photos.
P='crystals';ROLE='shell'
for o,a in [((-32,.075,381),math.pi/2),((-93,.075,470),0)]:
 facade_frame(o,a,5,4.2,'silver')
 vs=[tr(p,o,a) for p in [(-7,5.1,0),(7,5.1,0),(5,6.8,4),(-5,5.5,5)]];mesh('folded entry blade',vs,[(0,1,2,3),(3,2,1,0)],'silver')
 for xx in [-6,6]:box('entry blade support',tr((xx,2.55,1),o,a),(.14,5.1,.14),'silver',a)
ROLE='interior'
for t in towers:
 if t['set']!='veer':continue
 x=t['origin'][0]+12;z=t['origin'][2]
 for dz in [-7,7]:
  seating(x,z+dz,3.3,'white',math.pi/2);tree(x-2.7,z+dz,.6,4.0,'red')
  box('lime ottoman',(x+1.9,.43,z+dz),(1.5,.73,1.6),'lime',solid=True)
 for dz in [-4.8,4.8]:
  beam('residential glass fin',(x-3,.15,z+dz),(x-3,5.7,z+dz),.065,'silver')
  box('residential art wall',(x-3,3,z+dz),(.14,5.4,2.2),'white')
  for y in [1.4,2.3,3.2,4.1]:ring(x-3,y,z+dz,.45,.45,.08,'champagne')
# Cool glass ice shafts at the already modeled water garden, plus warm treehouse ribs.
for i in range(11):
 x=-124+(i%4)*1.1;z=365+(i//4)*1.15;h=2.1+(i%3)*.6
 lathe('ice installation',x,z,[(.24,.4),(.32,h),(.22,h+.12)],'sageglass',8)
for y,rx,rz in [(5.7,5.8,4.5),(10.7,8.1,6.3),(14.8,6.4,5.0)]:ring(-127,y,414,rx,rz,.06,'warm',.05)

# One mesh per resort/material. The established exporter further separates
# exterior shells, public interior zones and the upper tower window occluders.
for (prop,role,m),g in groups.items():
 name=f'Public design / {prop} / {role} / {m}';me=bpy.data.meshes.new(name);me.from_pydata([(x,-z,y) for x,y,z in g['v']],[],g['f']);me.update()
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 me.materials.append(bpy.data.materials[m]);o=bpy.data.objects.new(name,me);bpy.context.scene.collection.objects.link(o)
 if role=='shell':o['visibilityRole']='shell'
 uv_world(o)
data['colliders'].extend(colliders)
data.setdefault('extras',{})['publicResortDesign']=dict(version=1,properties=sorted(counts),referenceDocument='build/public-resorts/DESIGN.md')
(OUT/'staged-vegas.mesh-level.json').write_text(json.dumps(data,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str((OUT/'staged-vegas.blend').resolve()))
(ROOT/'build-report.json').write_text(json.dumps(dict(components=counts,batches=len(groups),newColliders=colliders,removed=removed,triangles=sum(sum(len(f)-2 for f in g['f']) for g in groups.values())),indent=2))
print('PUBLIC RESORTS BUILT',counts,len(groups),len(colliders),flush=True)
