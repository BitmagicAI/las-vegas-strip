"""Local mesh cinematic car. Metres, +Z forward. No level/world assets are rewritten."""
import bpy, math, os, json
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)
S=bpy.context.scene
OUT=os.path.abspath('build/film/storm');os.makedirs(OUT,exist_ok=True)
M={}
for n,c,metal,rough in [('Armor',(.10,.125,.071),.65,.34),('Inset',(.032,.045,.035),.65,.42),('Steel',(.17,.19,.205),.9,.25),('Black',(.013,.018,.02),.6,.30),('Rubber',(.012,.015,.016),0,.84),('Glass',(.017,.037,.052),.5,.12),('Leather',(.028,.025,.019),0,.8),('Letter',(.66,.62,.43),.1,.6),('Brake',(.42,.025,.012),.4,.35),('White',(.75,.86,1),.15,.16),('Red',(.65,.003,.008),.1,.18),('Amber',(.9,.18,.008),.1,.22)]:
 m=bpy.data.materials.new('Interceptor / '+n);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if n in ['White','Red','Amber']:p.inputs['Emission Color'].default_value=(*c,1);p.inputs['Emission Strength'].default_value=5 if n=='White' else 2
 M[n]=m

def root(n):
 o=bpy.data.objects.new(n,None);S.collection.objects.link(o);return o
body=root('InterceptorBody');parent=body

def link(o,n,m):o.name=n;o.parent=parent;o.data.materials.append(M[m]);return o

def box(n,p,d,m='Armor',bevel=.02):
 bpy.ops.mesh.primitive_cube_add(size=1,location=(p[0],-p[2],p[1]));o=bpy.context.object;o.dimensions=(d[0],d[2],d[1]);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);link(o,n,m)
 if bevel:
  b=o.modifiers.new('Edge catches','BEVEL');b.width=bevel;b.segments=3
  o.modifiers.new('Panel normals','WEIGHTED_NORMAL')
 return o

def mesh(n,vs,faces,m,bevel=0):
 g=bpy.data.meshes.new(n);g.from_pydata([(x,-z,y) for x,y,z in vs],[],faces);g.update();o=bpy.data.objects.new(n,g);S.collection.objects.link(o);link(o,n,m)
 if bevel:b=o.modifiers.new('Formed edges','BEVEL');b.width=bevel;b.segments=3;o.modifiers.new('Normals','WEIGHTED_NORMAL')
 return o

def rod(n,a,b,r,m='Steel',v=16):
 a=Vector((a[0],-a[2],a[1]));b=Vector((b[0],-b[2],b[1]));delta=b-a
 bpy.ops.mesh.primitive_cylinder_add(vertices=v,radius=r,depth=delta.length,location=(a+b)/2);o=bpy.context.object;o.rotation_euler=delta.to_track_quat('Z','Y').to_euler();link(o,n,m)
 for f in o.data.polygons:f.use_smooth=len(f.vertices)==4
 return o

def panel(n,vs,m='Armor'):return mesh(n,vs,[tuple(range(len(vs)))],m)
def loft(n,sections,m='Armor'):
 # transverse section z, width, lower height, shoulder, top centre
 vs=[]
 for z,w,lo,sh,top in sections:vs.extend([(-w,lo,z),(-w,sh,z),(-w*.80,top,z),(w*.80,top,z),(w,sh,z),(w,lo,z)])
 faces=[]
 for j in range(len(sections)-1):
  for i in range(6):faces.append((j*6+i,j*6+(i+1)%6,(j+1)*6+(i+1)%6,(j+1)*6+i))
 faces.extend([tuple(range(5,-1,-1)),tuple(range((len(sections)-1)*6,len(sections)*6))])
 return mesh(n,vs,faces,m,.028)

# Distinct long bonnet, fastback and low three-volume coupe: no block sitting through the wheels.
loft('Long vented bonnet',[(.65,.94,.64,.84,.89),(1.5,.98,.64,.77,.84),(2.3,.91,.57,.68,.72)])
loft('Rear haunch and deck',[(-2.35,.90,.52,.75,.79),(-1.7,1.0,.66,.91,.97),(-1.04,.98,.64,.89,.94)])
box('Floor chassis',(0,.31,-.15),(1.55,.20,4.25),'Black',.045)
box('Door cabin base',(0,.64,-.18),(1.90,.58,1.65),'Armor',.045)
loft('Fastback roof',[(-1.18,.74,1.10,1.27,1.33),(-.60,.78,1.21,1.40,1.46),(.18,.75,1.21,1.40,1.45)],'Armor')
panel('Swept windshield',[(-.86,.87,.77),(.86,.87,.77),(.74,1.385,.17),(-.74,1.385,.17)],'Glass')
panel('Rear window',[(-.75,1.29,-1.14),(.75,1.29,-1.14),(.89,.89,-1.85),(-.89,.89,-1.85)],'Glass')
for i in range(8):
 t=i/8;z=-1.20-t*.59;y=1.27-t*.35
 box('Fastback armored louver',(0,y,z),(1.53+t*.18,.035,.105),'Inset',.006)
for side in [-1,1]:
 panel('Side glazing',[(side*.87,.9,.64),(side*.745,1.385,.16),(side*.79,1.365,-.62),(side*.89,.9,-1.16)],'Glass')
 rod('A pillar',(side*.88,.84,.79),(side*.77,1.415,.16),.032,'Armor')
 rod('Roof gutter',(side*.77,1.425,.16),(side*.78,1.40,-.65),.024,'Steel')
 rod('B pillar',(side*.91,.89,-.79),(side*.79,1.36,-.65),.05,'Inset')
 rod('Window bottom',(side*.955,.875,-1.14),(side*.955,.875,.68),.022,'Steel')
 box('Armoured sill',(side*.99,.33,-.2),(.11,.14,1.93),'Inset',.016)
 box('Door applique',(side*.962,.65,-.23),(.025,.35,1.33),'Inset',.018)
 for z in [-.86,.46]:rod('Door panel seam',(side*.979,.43,z),(side*.979,.84,z),.004,'Black',8)
 box('Recessed door handle',(side*.986,.81,-.66),(.028,.032,.15),'Steel',.008)
 rod('Mirror stalk',(side*.94,.91,.44),(side*1.13,.99,.40),.019,'Steel')
 box('Aerodynamic mirror',(side*1.13,1.025,.38),(.16,.095,.25),'Black',.035)
 box('Mirror lens',(side*1.133,1.029,.255),(.12,.063,.008),'Steel',.006)
 rod('Side exhaust',(side*1.02,.25,-.73),(side*1.02,.25,.65),.053,'Black',24)
 rod('Exhaust tip',(side*1.02,.25,-.72),(side*1.08,.25,-.91),.057,'Steel',24)
 # Flared fender strip arcs leave the tyre openings real and empty.
 for zc in [1.52,-1.53]:
  vs=[]
  for i in range(25):
   a=math.pi*i/24;z=zc+math.cos(a)*.48;y=.415+math.sin(a)*.48
   vs.extend([(side*.89,y,z),(side*1.12,y+.035,z),(side*1.16,y-.025,z)])
  fs=[]
  for i in range(24):
   for k in range(2):fs.append((i*3+k,i*3+k+1,(i+1)*3+k+1,(i+1)*3+k))
  mesh('Rolled fender flare',vs,fs,'Armor',.012)
  for i in range(9):
   a=math.pi*i/8;rod('Fender rivet',(side*1.13,.453+math.sin(a)*.48,zc+math.cos(a)*.48),(side*1.151,.453+math.sin(a)*.48,zc+math.cos(a)*.48),.012,'Steel',8)
 for i in range(8):box('Bonnet gill',(side*.73,.871,1.19+i*.075),(.20,.012,.021),'Black',.005)
 for i in range(6):rod('Door armor bolt',(side*.974,.50+(i//3)*.27,-.7+(i%3)*.49),(side*.994,.50+(i//3)*.27,-.7+(i%3)*.49),.011,'Steel',8)
 # Visible roll cage through the dark glazing.
 rod('Roll cage upright',(side*.65,.45,-.8),(side*.65,1.30,-.7),.029,'Steel')
 rod('Roll cage diagonal',(side*.65,.48,-1.05),(-side*.65,1.28,-.74),.029,'Steel')
 box('Bucket seat',(side*.43,.61,-.47),(.44,.32,.50),'Leather',.075)
 box('Seat back',(side*.43,.95,-.79),(.42,.67,.13),'Leather',.07)
box('Roof cross brace',(0,1.325,-.70),(1.31,.06,.06),'Steel',.01)
# Intake, belt casing and finely ribbed compressor.
box('Blower casing',(0,.99,1.08),(.50,.20,.63),'Steel',.055)
for i in range(12):box('Blower cooling rib',(0,1.02,.83+i*.041),(.56,.10,.012),'Black',.003)
box('Air scoop',(0,1.15,1.24),(.65,.18,.46),'Black',.055)
for x in [-.205,0,.205]:rod('Intake butterfly',(x,1.15,1.46),(x,1.15,1.48),.075,'Steel',32)
# Layered nose, lights, reinforced bash plate and recovery frame.
box('Front fascia',(0,.54,2.25),(1.86,.28,.20),'Black',.03)
box('Slotted front grille',(0,.55,2.361),(.92,.17,.015),'Inset',.006)
for x in [-.41+i*.055 for i in range(16)]:box('Grille vertical fin',(x,.55,2.379),(.009,.165,.018),'Steel',.002)
for side in [-1,1]:
 for x in [.58,.79]:
  rod('Headlamp bezel',(side*x,.60,2.34),(side*x,.60,2.39),.094,'Steel',32)
  rod('Projector headlight',(side*x,.60,2.395),(side*x,.60,2.403),.073,'White',32)
 box('Indicator',(side*.81,.40,2.362),(.20,.048,.02),'Amber',.012)
 box('Tail light bar',(side*.62,.68,-2.378),(.52,.075,.025),'Red',.016)
 rod('Front tow point',(side*.7,.29,2.40),(side*.7,.29,2.54),.043,'Steel')
box('Reinforced wedge bumper',(0,.29,2.36),(2.05,.19,.27),'Inset',.035)
rod('Bull bar top',(-.88,.77,2.47),(.88,.77,2.47),.034,'Steel',24)
for x in [-.84,.84]:rod('Bull bar riser',(x,.30,2.46),(x,.77,2.47),.037,'Steel',24)
box('Rear diffuser',(0,.30,-2.31),(1.79,.18,.25),'Black',.035)
for x in [-.65,-.33,0,.33,.65]:box('Diffuser fin',(x,.20,-2.32),(.018,.15,.35),'Steel',.006)
box('Rear ducktail',(0,.85,-2.18),(1.84,.065,.27),'Inset',.018)
# Stencil identification on both doors.
for side in [-1,1]:
 cu=bpy.data.curves.new('Stencil','FONT');cu.body='NV / 07';cu.size=.13;cu.align_x='CENTER';cu.extrude=.0003
 o=bpy.data.objects.new('Door stencil',cu);S.collection.objects.link(o);o.location=(side*.985,.20,.635);o.rotation_euler=(math.pi/2,0,side*math.pi/2);link(o,'Door stencil','Letter')
# Independent wheels: local origin at axle, cylinder axis game X. Four copies in runtime.
parent=root('InterceptorWheel')
# Tyre ring with rounded tread profile via mesh, avoids torus doughnut silhouette.
vs=[];profile=[(-.165,.26),(-.18,.32),(-.15,.385),(-.11,.401),(.11,.401),(.15,.385),(.18,.32),(.165,.26)]
for x,r in profile:
 for j in range(64):a=j*math.tau/64;vs.append((x,math.cos(a)*r,math.sin(a)*r))
faces=[]
for k in range(len(profile)):
 for j in range(64):faces.append((k*64+j,k*64+(j+1)%64,((k+1)%len(profile))*64+(j+1)%64,((k+1)%len(profile))*64+j))
o=mesh('Tyre casing',vs,faces,'Rubber')
for f in o.data.polygons:f.use_smooth=True
for j in range(48):
 a=j*math.tau/48
 for side in [-1,1]:
  o=box('Directional tread block',(side*.080,math.cos(a)*.401,math.sin(a)*.401),(.125,.025,.037),'Rubber',.004)
  o.rotation_euler.x=a
for side in [-1,1]:
 rod('Recessed wheel rim',(side*.10,0,0),(side*.17,0,0),.264,'Black',48)
 rod('Metal bead lip',(side*.171,0,0),(side*.185,0,0),.267,'Steel',48)
 rod('Black recessed dish',(side*.186,0,0),(side*.189,0,0),.240,'Black',48)
 rod('Brake disc',(side*.14,0,0),(side*.145,0,0),.205,'Steel',48)
 for j in range(7):
  a=j*math.tau/7
  rod('Forged wheel spoke',(side*.195,math.cos(a)*.065,math.sin(a)*.065),(side*.195,math.cos(a+.08)*.24,math.sin(a+.08)*.24),.023,'Steel',8)
  rod('Lug nut',(side*.198,math.cos(a)*.062,math.sin(a)*.062),(side*.212,math.cos(a)*.062,math.sin(a)*.062),.013,'Letter',6)
 rod('Axle hub',(side*.19,0,0),(side*.212,0,0),.047,'Steel',32)
# Apply modifiers and batch static parts by material per component.
for group in [body,parent]:
 for o in list(group.children):
  bpy.context.view_layer.objects.active=o;o.select_set(True)
  if o.type=='FONT':bpy.ops.object.convert(target='MESH')
  for mod in list(o.modifiers):
   try:bpy.ops.object.modifier_apply(modifier=mod.name)
   except RuntimeError:pass
  o.select_set(False)
 for mat in M.values():
  obs=[o for o in group.children if o.type=='MESH' and o.data.materials and o.data.materials[0]==mat]
  if not obs:continue
  bpy.ops.object.select_all(action='DESELECT')
  for o in obs:o.select_set(True)
  bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();o=bpy.context.object;o.name=group.name+' / '+mat.name
  # Put every merged submesh in the component's coordinate frame.
  bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');o.select_set(False)
bpy.ops.export_scene.gltf(filepath=OUT+'/interceptor.glb',export_format='GLB',export_yup=True,export_apply=True)
bpy.ops.wm.save_as_mainfile(filepath=OUT+'/interceptor.blend')
print('INTERCEPTOR',OUT)
