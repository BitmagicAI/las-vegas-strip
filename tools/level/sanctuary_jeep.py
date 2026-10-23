"""Local Blender-authored AL-01 electric patrol jeep and sanctuary charger.
Metres, game +Z forward. Body origin is the Bitmagic chassis centre; Wheel's
axle is +Y before the engine's cylinder alignment, steering and rolling pose.
"""
import bpy, math, os
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)
S=bpy.context.scene
mats={}
for n,c,metal,rough in [('olive',(.17,.21,.11),.45,.48),('edge',(.085,.11,.063),.35,.55),('sand',(.40,.39,.24),.2,.67),('black',(.012,.017,.020),.12,.64),('rubber',(.017,.022,.019),0,.9),('steel',(.25,.29,.30),.85,.25),('seat',(.052,.061,.048),0,.95),('glass',(.045,.10,.13),.25,.18),('white',(.78,.82,.68),.1,.58),('amber',(.9,.22,.014),.05,.25),('red',(.32,.01,.015),.05,.25),('cyan',(.04,.65,.76),.1,.2)]:
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if n in ['cyan','amber','red','white'] and n!='white':p.inputs['Emission Color'].default_value=(*c,1);p.inputs['Emission Strength'].default_value=1.5
 if n=='glass':p.inputs['Alpha'].default_value=.34;m.surface_render_method='BLENDED';m.use_backface_culling=False
 mats[n]=m

def root(n):
 o=bpy.data.objects.new(n,None);S.collection.objects.link(o);return o
body=root('Body');wheel=root('Wheel');charger=root('Charger');parent=body

def attach(o,n,m):
 o.name=n;o.parent=parent;o.data.materials.append(mats[m]);return o

def box(n,p,size,m='olive',bev=.025,rot=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=(p[0],-p[2],p[1]));o=bpy.context.object;o.dimensions=(size[0],size[2],size[1]);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.rotation_euler.z=rot;attach(o,n,m)
 if bev:
  mod=o.modifiers.new('Machined edges','BEVEL');mod.width=bev;mod.segments=3
  mod=o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
 return o

def rod(n,a,b,r,m='steel',verts=16):
 a=Vector((a[0],-a[2],a[1]));b=Vector((b[0],-b[2],b[1]));v=b-a
 bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=v.length,location=(a+b)/2);o=bpy.context.object;o.rotation_euler=v.to_track_quat('Z','Y').to_euler();attach(o,n,m)
 for f in o.data.polygons:f.use_smooth=len(f.vertices)==4
 return o

def plate(n,vs,m='olive'):
 mesh=bpy.data.meshes.new(n);mesh.from_pydata([(x,-z,y) for x,y,z in vs],[],[tuple(range(len(vs)))]);mesh.update();o=bpy.data.objects.new(n,mesh);S.collection.objects.link(o);attach(o,n,m);mod=o.modifiers.new('Plate thickness','SOLIDIFY');mod.thickness=.018;return o

def text(n,p,size=.13,yaw=0,m='white'):
 c=bpy.data.curves.new(n,'FONT');c.body=n;c.size=size;c.align_x='CENTER';c.extrude=.0006;o=bpy.data.objects.new(n,c);S.collection.objects.link(o);o.location=(p[0],-p[2],p[1]);o.rotation_euler=(math.pi/2,0,yaw);attach(o,n,m)

# Underbody battery armour, sill frame, short squared bonnet and open wheel arches.
box('Battery skid plate',(0,-.08,0),(1.58,.20,3.9),'black',.05)
box('Passenger floor',(0,.10,-.40),(1.74,.18,2.65),'edge')
box('Electric bonnet',(0,.45,1.18),(1.72,.48,1.34),'olive',.09)
box('Bonnet highlight',(0,.708,1.18),(1.69,.045,1.30),'sand',.02)
box('Front grille surround',(0,.35,1.92),(1.90,.60,.13),'olive')
box('Sealed electric grille',(0,.34,2.003),(1.02,.32,.05),'black',.025)
for x in [-.42,-.28,-.14,0,.14,.28,.42]:box('Grille fin',(x,.34,2.038),(.037,.29,.015),'edge',.004)
box('Front steel bumper',(0,.02,2.12),(2.12,.24,.24),'black',.06)
box('Rear bumper',(0,.0,-2.12),(2.08,.22,.22),'black',.045)
for x in [-.77,.77]:
 rod('LED headlamp bezel',(x,.42,1.98),(x,.42,2.07),.145,'black',32)
 rod('LED headlamp',(x,.42,2.071),(x,.42,2.085),.119,'white',32)
 box('Amber marker',(x,.16,2.075),(.19,.065,.045),'amber',.015)
 rod('Recovery eye',(x,-.06,2.12),(x,-.06,2.34),.057,'steel')
 box('Rear lamp',(x,.34,-2.065),(.18,.24,.04),'red')
for side in [-1,1]:
 x=side*.87
 box('Side lower rocker',(x,.14,-.37),(.16,.25,2.27),'edge')
 box('Rear quarter panel',(x,.49,-1.65),(.17,.76,.60),'olive')
 for z in [1.57,-1.57]:
  box('Wide wheel fender',(x,.29,z),(.58,.14,1.13),'edge',.04)
  for dz in [-.49,.49]:box('Fender trailing edge',(x,.08,z+dz),(.47,.38,.15),'edge')
 for z in [.25,-.69]:
  box('Door panel',(x,.55,z),(.075,.67,.89),'olive',.035)
  box('Door protection inset',(x+side*.047,.54,z),(.02,.30,.66),'sand',.035)
  box('Door handle',(x+side*.073,.79,z-.21),(.055,.045,.18),'black',.013)
  for y in [.37,.73]:box('Door hinge',(x+side*.05,y,z+.35),(.07,.075,.05),'steel',.005)
  plate('Side window',[(x,.92,z-.41),(x,1.39,z-.36),(x,1.39,z+.32),(x,.92,z+.43)],'glass')
 for z in [-1.15,-.21,.73]:rod('Cabin pillar',(x,.84,z),(side*.78,1.45,z-.10),.055,'edge')
 rod('Step rail',(side*1.025,-.14,-1.03),(side*1.025,-.14,.93),.055,'steel')
 rod('Mirror arm',(x,.96,.62),(side*1.14,1.02,.58),.022,'steel')
 box('Mirror housing',(side*1.16,1.06,.56),(.16,.24,.12),'black')
 box('Mirror glass',(side*1.16,1.06,.485),(.13,.19,.015),'steel',.01)
 box('Bonnet latch',(side*.82,.65,1.38),(.04,.07,.16),'black',.008)
text('AL-01',(.944,.64,-.60),.15,yaw=math.pi/2)
text('ELECTRIC',(.944,.37,-.60),.09,yaw=math.pi/2)
text('AL-01',(-.944,.64,-.60),.15,yaw=-math.pi/2)
text('ELECTRIC',(-.944,.37,-.60),.09,yaw=-math.pi/2)
box('Hard roof',(0,1.47,-.32),(1.80,.115,2.12),'olive',.06)
box('Roof rack tray',(0,1.57,-.34),(1.58,.08,1.69),'black',.03)
for x in [-.76,.76]:rod('Rack longitudinal',(x,1.68,-1.13),(x,1.68,.46),.03,'steel')
for z in [-1.1,-.77,-.44,-.11,.22,.46]:rod('Rack crossbar',(-.78,1.66,z),(.78,1.66,z),.025,'steel')
box('Field supplies',(0,1.77,-.68),(1.2,.32,.65),'sand',.055)
for x in [-.4,.4]:box('Cargo tie down',(x,1.95,-.68),(.045,.025,.70),'black',.004)
plate('Windscreen',[(-.82,.88,.77),(.82,.88,.77),(.77,1.40,.56),(-.77,1.40,.56)],'glass')
for x in [-.84,0,.84]:rod('Windscreen frame',(x,.88,.785),(x*.92,1.42,.56),.032,'edge')
rod('Windscreen base',(-.84,.88,.78),(.84,.88,.78),.038,'edge')
for x in [-.40,.40]:rod('Wiper',(x-.22,.915,.79),(x+.11,1.04,.735),.012,'black')
box('Dashboard',(0,.80,.42),(1.59,.22,.35),'black',.05)
box('Navigation display',(.21,.95,.23),(.34,.20,.05),'cyan',.02)
for x in [-.46,.46]:
 for z in [0,-.81]:
  box('Seat cushion',(x,.36,z),(.56,.17,.52),'seat',.085)
  box('Seat back',(x,.67,z-.22),(.55,.57,.17),'seat',.08)
  box('Head rest',(x,.99,z-.22),(.31,.22,.15),'seat',.06)
rod('Steering column',(.46,.69,.38),(.46,.96,.20),.035,'black')
bpy.ops.mesh.primitive_torus_add(major_radius=.16,minor_radius=.023,major_segments=32,minor_segments=8,location=(.46,-.20,.96));o=bpy.context.object;o.rotation_euler.x=1.05;attach(o,'Steering wheel','black')
box('Rear door',(0,.49,-1.91),(1.61,.91,.12),'olive',.035)
plate('Rear glass',[(-.78,.93,-1.37),(-.76,1.39,-1.34),(.76,1.39,-1.34),(.78,.93,-1.37)],'glass')
rod('Antenna',(-.72,1.55,-1.15),(-.76,2.3,-1.20),.009,'black',8)
box('Charge port',(.92,.35,-1.36),(.02,.18,.18),'cyan',.03)
# Engine wheel template, centred on the axle, high-contrast sidewall/tread detail.
parent=wheel
rod('Off-road tyre',(0,-.185,0),(0,.185,0),.46,'rubber',48)
for sign in [-1,1]:
 rod('Recessed rim',(0,sign*.185,0),(0,sign*.197,0),.275,'edge',32)
 rod('Wheel hub',(0,sign*.197,0),(0,sign*.224,0),.12,'steel',24)
 for i in range(8):
  a=i*math.tau/8;x=.185*math.sin(a);z=.185*math.cos(a)
  rod('Rim vent',(x,sign*.198,z),(x,sign*.202,z),.038,'black',10)
  rod('Lug nut',(.075*math.sin(a),sign*.226,.075*math.cos(a)),(.075*math.sin(a),sign*.242,.075*math.cos(a)),.013,'steel',6)
for i in range(36):
 a=i*math.tau/36
 for side in [-1,1]:
  o=box('Tyre tread',(.457*math.sin(a),side*.097,.457*math.cos(a)),(.11,.175,.033),'rubber',.008);o.rotation_euler.z=a
# Spare wheel is fixed to the rear door; rotating runtime wheels remain separate.
spare=wheel.copy();spare.name='Spare';S.collection.objects.link(spare);spare.parent=body;spare.location=(0,2.15,.61);spare.rotation_euler.x=math.pi/2
for child in list(wheel.children):
 c=child.copy();c.data=child.data;S.collection.objects.link(c);c.parent=spare
parent=charger
box('Charge pedestal',(0,.10,0),(.9,.20,.72),'steel')
box('Charging cabinet',(0,.95,0),(.68,1.72,.40),'edge',.065)
box('Charger hood',(0,1.88,.025),(.81,.16,.56),'olive',.06)
box('Display recess',(0,1.38,.222),(.49,.52,.05),'black',.025)
box('Ready light',(0,1.71,.247),(.41,.042,.025),'cyan',.008)
box('Connector holster',(.38,1.12,0),(.14,.32,.15),'black')
text('AFTERLIGHT',(0,1.51,.257),.072)
text('ELECTRIC / 01',(0,1.18,.26),.064)
text('CHARGE',(0,.73,.224),.115)
# A coiled cable hangs on the cabinet, never stretches after the jeep leaves.
for i in range(50):
 a=i*math.tau/50;b=(i+1)*math.tau/50
 rod('Coiled cable',(.29+.18*math.cos(a),.72+.31*math.sin(a),.28),(.29+.18*math.cos(b),.72+.31*math.sin(b),.28),.022,'black',8)
box('Plug',(.39,1.10,.28),(.09,.23,.12),'black',.025)
# Exports retain the three named reusable components at their authored origins.
bpy.ops.object.select_all(action='SELECT')
for o in list(bpy.context.selected_objects):
 if o.type=='FONT':bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH')
# Bake proportion correction into component-local mesh geometry (runtime batching
# intentionally strips root transforms). Keep the charger untouched.
from mathutils import Matrix
bpy.context.view_layer.update()
for root, transform in [(body, Matrix.Diagonal((.81,1,.86,1))), (wheel, Matrix.Diagonal((.8,.8,.64,1)))]:
 for obj in root.children_recursive:
  if obj.type != 'MESH': continue
  local = root.matrix_world.inverted() @ obj.matrix_world
  obj.data = obj.data.copy()
  obj.data.transform(local.inverted() @ transform @ local)
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath('build/vehicles/afterlight-jeep.blend'))
bpy.ops.export_scene.gltf(filepath=os.path.abspath('build/vehicles/afterlight-jeep.glb'),export_format='GLB',export_apply=True,export_yup=True,export_cameras=False,export_lights=False)
print('JEEP LOCAL ASSET READY',flush=True)
