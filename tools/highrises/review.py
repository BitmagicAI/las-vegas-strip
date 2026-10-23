"""Local Blender review: mapped exteriors and representative guest spaces."""
import bpy,json,math,sys
from pathlib import Path
from mathutils import Vector
OUT=Path('build/highrises/review');OUT.mkdir(exist_ok=True,parents=True)
plans=json.loads(Path('build/highrises/plan.json').read_text())
def point(p):return Vector((p[0],-p[2],p[1]))
def setup():
 s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True
 s.render.resolution_x=1100;s.render.resolution_y=740;s.render.resolution_percentage=100
 s.world=bpy.data.worlds.new('Review daylight');s.world.use_nodes=True
 bg=s.world.node_tree.nodes.get('Background');bg.inputs[0].default_value=(.48,.58,.70,1);bg.inputs[1].default_value=.65
 ld=bpy.data.lights.new('sun','SUN');lo=bpy.data.objects.new('sun',ld);s.collection.objects.link(lo);ld.energy=2;ld.angle=.15;lo.rotation_euler=(.5,-.4,-.4)
 cam=bpy.data.objects.new('review camera',bpy.data.cameras.new('review camera'));s.collection.objects.link(cam);s.camera=cam;cam.data.clip_end=16000
 s.view_settings.view_transform='AgX';return s,cam
def shot(s,cam,name,eye,target,lens=24):
 cam.location=point(eye);cam.rotation_euler=(point(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens
 s.render.filepath=str((OUT/(name+'.png')).resolve());bpy.ops.render.render(write_still=True);print('SHOT',name,flush=True)
keys=['wynn','fontainebleau','new-york','turnberry-place','resorts-world','luxor']
if '--' in sys.argv:keys=sys.argv[sys.argv.index('--')+1:]
for key in keys:
 p=next(p for p in plans if p['key']==key)
 bpy.ops.wm.open_mainfile(filepath=str(Path('build/highrises/exteriors.blend').resolve()))
 for o in bpy.data.objects:o.hide_render=o.get('property')!=key
 s,cam=setup();verts=[o.matrix_world@Vector(v) for o in bpy.data.objects if o.type=='MESH' and not o.hide_render for v in o.bound_box]
 x0,x1=min(v.x for v in verts),max(v.x for v in verts);z0,z1=-max(v.y for v in verts),-min(v.y for v in verts);h=max(v.z for v in verts);cx,cz=(x0+x1)/2,(z0+z1)/2
 d=max(x1-x0,z1-z0,h)*1.65
 shot(s,cam,key+'-exterior',(cx+d,h*.40,cz+d*.65),(cx,h*.45,cz),32)
for key in keys[:4]:
 p=next(p for p in plans if p['key']==key);t=p['towers'][0]
 for kind in ['room','corridor','lobby']:
  name=t['id']+'-lobby' if kind=='lobby' else key+'-'+kind
  bpy.ops.wm.open_mainfile(filepath=str(Path('build/hotels/'+name+'.blend').resolve()));s,cam=setup()
  meta=json.loads(Path('build/hotels/'+name+'.mesh-level.json').read_text())
  for light in meta['lights']:
   ld=bpy.data.lights.new(light['name'],'POINT');ld.energy=light['intensity']*16;ld.shadow_soft_size=.35
   lo=bpy.data.objects.new(light['name'],ld);s.collection.objects.link(lo);lo.location=point(light['position'])
  if kind=='room':shot(s,cam,name,(.5,1.65,.15),(5.4,1.2,-1.1),20)
  elif kind=='corridor':shot(s,cam,name,(.3,1.65,2.8),(0,1.5,-2.8),22)
  else:
   f=-5.25-6*t['bays'];shot(s,cam,name,(1,1.65,f+1),(0,2.3,f+14),20)
