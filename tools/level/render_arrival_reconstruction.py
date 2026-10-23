import bpy,json,sys,math
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,'tools/level')
from arrival_architecture import materials
bpy.ops.wm.open_mainfile(filepath=str(Path('build/hotels/staged-vegas.blend').resolve()))
p=Path('build/hotels/staged-vegas.mesh-level.json');data=json.loads(p.read_text())
for v in data['volumes']:
 if 'arrival' in v.get('tags',[]) and v['name'].count(' / ')==1:
  name=v['name'].split(' / ')[1];owner='crystals' if name.startswith('veer') else 'bellagio' if name.startswith('bellagio') else name;v['name']='Arrival / '+owner+' / '+name
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True;s.render.resolution_x=1280;s.render.resolution_y=850;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX'
s.world=bpy.data.worlds.new('neutral sky review');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.45,.52,.60,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.45
lights=[]
for rec in data['lights']:
 if rec.get('type')!='point':continue
 ld=bpy.data.lights.new(rec['name'],'POINT');o=bpy.data.objects.new(ld.name,ld);s.collection.objects.link(o);x,y,z=rec['position'];o.location=(x,-z,y);ld.energy=rec['intensity']*17;ld.shadow_soft_size=.6;col=rec['color'].lstrip('#');ld.color=tuple(int(col[i:i+2],16)/255 for i in [0,2,4]);lights.append(o)
bpy.ops.object.light_add(type='SUN');sun=bpy.context.object;sun.rotation_euler=(.45,-.4,-.8);sun.data.energy=2
bpy.ops.object.camera_add();cam=bpy.context.object;s.camera=cam;cam.data.lens=22;cam.data.clip_end=1000
specs=json.loads(Path('build/arrival-reconstruction/report.json').read_text())['properties'];selected=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['crystals','waldorf','paris']
objects=[]
for o in s.objects:
 if o.type!='MESH':continue
 v=[o.matrix_world@Vector(p) for p in o.bound_box];objects.append((o,[min(p[i] for p in v) for i in range(3)],[max(p[i] for p in v) for i in range(3)]))
out=Path('build/arrival-reconstruction/renders');out.mkdir(exist_ok=True)
for name in selected:
 spec=specs[name];ox,oy,oz=spec['origin'];a=spec['yaw'];c,si=math.cos(a),math.sin(a)
 def world(x,y,z):return Vector((ox+c*x+si*z,-oz+si*x-c*z,oy+y))
 for label,p,t in [('entrance',(0,1.85,-14),(0,5,5)),('inside',(0,1.85,2.5),(0,3.4,min(21,spec['dimensions'][1])) )]:
  cam.location=world(*p);cam.rotation_euler=(world(*t)-cam.location).to_track_quat('-Z','Y').to_euler()
  for o,lo,hi in objects:o.hide_render=lo[0]>ox+120 or hi[0]<ox-120 or lo[1]>-oz+120 or hi[1]<-oz-120 or lo[2]>42
  for o in lights:o.hide_render=(o.location-cam.location).length>75
  s.render.filepath=str((out/(name+'-'+label+'.png')).resolve());bpy.ops.render.render(write_still=True);print('RENDERED',name,label,flush=True)
