"""Ground-level architectural review cameras, using the same GLBs as the game."""
import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
OUT=Path('build/strip-landmarks')
def pt(p):return Vector((p[0],-p[2],p[1]))
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
for meta in json.loads((OUT/'venues.json').read_text()):
 key=meta['key']
 if args and key not in args:continue
 bpy.ops.wm.read_factory_settings(use_empty=True)
 for layer in ['exterior','interior']:bpy.ops.import_scene.gltf(filepath=str((OUT/(key+'-'+layer+'.glb')).resolve()))
 # Include each arrival's existing tall tower in the same review views.
 if meta.get('building') in ['park-mgm','palazzo','treasure-island','harrahs']:
  before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(Path('build/highrises/exteriors.glb').resolve()))
  for ob in set(bpy.data.objects)-before:
   if ob.type=='MESH' and ob.get('property')!=meta['building']:bpy.data.objects.remove(ob,do_unlink=True)
 # The game instances these chairs after streaming the arena. Batch the same
 # four parts here so offline views show that runtime geometry too.
 if meta.get('seats'):
  verts=[];faces=[];base=[(-.5,-.5,-.5),(.5,-.5,-.5),(.5,.5,-.5),(-.5,.5,-.5),(-.5,-.5,.5),(.5,-.5,.5),(.5,.5,.5),(-.5,.5,.5)]
  quads=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
  for x,y,z,yaw in meta['seats']:
   co,si=math.cos(yaw),math.sin(yaw)
   for offset,size in [((0,0,0),(.48,.12,.46)),((0,.32,-.19),(.49,.66,.12)),((0,-.21,0),(.1,.36,.24)),((.27,.18,0),(.07,.06,.44))]:
    start=len(verts)
    for a,b,c in base:
     xx=a*size[0]+offset[0];yy=b*size[1]+offset[1];zz=c*size[2]+offset[2];verts.append(pt((x+co*xx+si*zz,y+yy,z-si*xx+co*zz)))
    faces.extend(tuple(start+i for i in q) for q in quads)
  mesh=bpy.data.meshes.new('Shared arena seating');mesh.from_pydata(verts,[],faces);obj=bpy.data.objects.new('Runtime arena seats',mesh);bpy.context.collection.objects.link(obj);mat=bpy.data.materials.new('Seat charcoal');mat.diffuse_color=(.032,.037,.039,1);mat.use_nodes=True;mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=mat.diffuse_color;mesh.materials.append(mat)
 s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=800;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=4
 s.world=bpy.data.worlds.new('Daylight');s.world.use_nodes=True;s.world.node_tree.nodes.get('Background').inputs[0].default_value=(.50,.65,.82,1);s.world.node_tree.nodes.get('Background').inputs[1].default_value=.45
 sun=bpy.data.lights.new('sun','SUN');sun.energy=2.5;sun.angle=.12;o=bpy.data.objects.new('sun',sun);s.collection.objects.link(o);o.rotation_euler=(.5,-.5,-.2)
 for l in meta['lights']:
  d=bpy.data.lights.new('ceiling pool','POINT');d.energy=l['power']*3;d.shadow_soft_size=1.;q=bpy.data.objects.new('ceiling pool',d);s.collection.objects.link(q);q.location=pt(l['p'])
 cam=bpy.data.objects.new('camera',bpy.data.cameras.new('camera'));s.collection.objects.link(cam);s.camera=cam;cam.data.clip_end=15000;s.view_settings.view_transform='AgX'
 bpy.ops.mesh.primitive_plane_add(size=1300,location=pt((meta['bounds'][0],-.03,meta['bounds'][1])));floor=bpy.context.object;m=bpy.data.materials.new('ground');m.diffuse_color=(.22,.20,.16,1);floor.data.materials.append(m)
 views=list(meta['views'])
 for name in views:
  v=meta['views'][name];cam.location=pt(v['eye']);cam.rotation_euler=(pt(v['target'])-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=23 if name=='lobby' else 30;s.render.filepath=str((OUT/(key+'-'+name+'-review.png')).resolve());bpy.ops.render.render(write_still=True)
