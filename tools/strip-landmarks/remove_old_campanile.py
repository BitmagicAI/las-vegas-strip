"""Remove only the superseded generic Campanile; preserve prior detailed resorts."""
import bpy,json,hashlib
from pathlib import Path
p=Path('build/highrises');bpy.ops.wm.open_mainfile(filepath=str((p/'exteriors.blend').resolve()))
for o in list(bpy.data.objects):
 if o.get('source')=='way/43875964':bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.wm.save_as_mainfile(filepath=str((p/'exteriors.blend').resolve()))
bpy.ops.export_scene.gltf(filepath=str((p/'exteriors.glb').resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
(p/'version.json').write_text(json.dumps({'revision':hashlib.sha256((p/'exteriors.glb').read_bytes()).hexdigest()[:16]}))
f=p/'venetian-collision.json';c=json.loads(f.read_text());indices=[]
for i in range(0,len(c['indices']),3):
 ids=c['indices'][i:i+3];ps=[c['vertices'][j*3:j*3+3] for j in ids]
 if all(139<x<161 and -625<z<-602 for x,y,z in ps):continue
 indices+=ids
c['indices']=indices;f.write_text(json.dumps(c,separators=(',',':')))
