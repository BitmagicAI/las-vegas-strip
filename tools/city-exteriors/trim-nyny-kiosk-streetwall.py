"""Blender: remove only the obsolete synthetic streetwall bay covering the kiosk.
Never reload an old whole-city scene: edit the current highrise source in place.
"""
import bpy,bmesh,json,shutil,hashlib,sys
from pathlib import Path
root=Path.cwd();hi=root/'build/highrises';bak=root/'.bitmagic/city-exterior-backups/nyny-kiosk-streetwall-2026-10-21';bak.mkdir(parents=True,exist_ok=True)
for n in ['exteriors.blend','exteriors.glb','new-york-collision.json']:
 if not (bak/n).exists():shutil.copy2(hi/n,bak/n)
bpy.ops.wm.open_mainfile(filepath=str((bak if '--repair-first-pass' in sys.argv else hi)/'exteriors.blend'))
# All six faces of the old bay and its decorations lie in this small box.
# The retained podium has long triangles extending outside it and is not selected.
def inside(v):return -49.751<v[0]<-34.899 and 1548.999<-v[1]<1573.001 and -.001<v[2]<18.301
report=[]
for o in list(bpy.data.objects):
 if o.get('property')!='new-york' or o.get('source')!='way/115661793':continue
 if o.type=='FONT':
  if any(abs(o.location.y+z)<.01 for z in [1555,1567]):
   report.append(dict(object=o.name,label=True));bpy.data.objects.remove(o,do_unlink=True)
 elif o.type=='MESH':
  bm=bmesh.new();bm.from_mesh(o.data);faces=[f for f in bm.faces if all(inside(o.matrix_world@v.co) for v in f.verts) and not all(abs((o.matrix_world@v.co).y+1573)<.001 for v in f.verts)]
  if faces:
   report.append(dict(object=o.name,removed=len(faces)));bmesh.ops.delete(bm,geom=faces,context='FACES');bm.to_mesh(o.data);o.data.update()
  bm.free()
# Original synthetic boxes were authored non-solid. Remove any equivalent stale
# collision faces only if their complete triangle is inside the same bay volume.
p=hi/'new-york-collision.json';c=json.loads(p.read_text());v=c['vertices'];idx=c['indices'];keep=[];removed=0
for i in range(0,len(idx),3):
 t=idx[i:i+3]
 if all(inside((v[j*3],-v[j*3+2],v[j*3+1])) for j in t):removed+=1
 else:keep.extend(t)
c['indices']=keep;p.write_text(json.dumps(c,separators=(',',':')))
bpy.ops.wm.save_as_mainfile(filepath=str(hi/'exteriors.blend'))
bpy.ops.export_scene.gltf(filepath=str(hi/'exteriors.glb'),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
(hi/'version.json').write_text(json.dumps(dict(revision=hashlib.sha256((hi/'exteriors.glb').read_bytes()).hexdigest()[:16])))
Path('build/city-exteriors/nyny-kiosk-streetwall-trim.json').write_text(json.dumps(dict(meshes=report,collisionTrianglesRemoved=removed,scope='Two synthetic bays at z=1555 and1567; retained podium, hotel towers, Liberty, coaster, interiors unchanged.'),indent=2))
print('KIOSK BAY TRIM',report,removed,flush=True)
