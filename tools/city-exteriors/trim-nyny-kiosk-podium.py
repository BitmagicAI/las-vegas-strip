"""Blender: carve the mapped open arrival canopy out of the retained podium only."""
import bpy,bmesh,json,shutil,hashlib
from pathlib import Path
from mathutils import Vector
hi=Path('build/highrises');bak=Path('.bitmagic/city-exterior-backups/nyny-kiosk-podium-2026-10-21');bak.mkdir(parents=True,exist_ok=True)
for n in ['exteriors.blend','exteriors.glb','new-york-collision.json']:
 if not (bak/n).exists():shutil.copy2(hi/n,bak/n)
planes=[(0,-52.5,1),(0,-34,-1),(1,-1,1),(1,9.5,-1),(2,1549,1),(2,1573,-1)]
def clip(poly,axis,value,sign):
 out=[]
 for a,c in zip(poly,poly[1:]+poly[:1]):
  da=(a[axis]-value)*sign;dc=(c[axis]-value)*sign
  if da>=-1e-8:out.append(a)
  if da*dc<0:
   t=da/(da-dc);out.append([a[j]+(c[j]-a[j])*t for j in range(3)])
 return out
def affected(q):return max(v[0]for v in q)>-52.5 and min(v[0]for v in q)<-34 and max(v[2]for v in q)>1549 and min(v[2]for v in q)<1573 and max(v[1]for v in q)>.5 and min(v[1]for v in q)<9.5
def outside(q):
 pending=q;out=[]
 for axis,val,sign in planes:
  if not pending:break
  part=clip(pending,axis,val,-sign)
  for j in range(1,len(part)-1):
   t=[part[0],part[j],part[j+1]]
   if (Vector(t[1])-Vector(t[0])).cross(Vector(t[2])-Vector(t[0])).length>1e-8:out.append(t)
  pending=clip(pending,axis,val,sign)
 return out
bpy.ops.wm.open_mainfile(filepath=str(hi.resolve()/'exteriors.blend'));count=0
for o in bpy.data.objects:
 if o.type!='MESH' or o.get('property')!='new-york' or o.get('source')!='way/115661793':continue
 bm=bmesh.new();bm.from_mesh(o.data)
 for f in list(bm.faces):
  q=[o.matrix_world@v.co for v in f.verts];q=[[v.x,v.z,-v.y]for v in q]
  if not affected(q):continue
  mat=f.material_index;pieces=outside(q);bm.faces.remove(f);count+=1
  for t in pieces:
   verts=[bm.verts.new(o.matrix_world.inverted()@Vector((v[0],-v[2],v[1])))for v in t];nf=bm.faces.new(verts);nf.material_index=mat
 bm.to_mesh(o.data);bm.free();o.data.update()
p=hi/'new-york-collision.json';c=json.loads(p.read_text());vs=[];idx=[];nv=c['vertices'];nc=0
for i in range(0,len(c['indices']),3):
 q=[nv[j*3:j*3+3]for j in c['indices'][i:i+3]];pieces=[q]
 if affected(q):pieces=outside(q);nc+=1
 for t in pieces:
  n=len(vs)//3;vs.extend(a for v in t for a in v);idx.extend([n,n+1,n+2])
c['vertices']=vs;c['indices']=idx;p.write_text(json.dumps(c,separators=(',',':')))
bpy.ops.wm.save_as_mainfile(filepath=str(hi.resolve()/'exteriors.blend'))
bpy.ops.export_scene.gltf(filepath=str(hi.resolve()/'exteriors.glb'),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
(hi/'version.json').write_text(json.dumps(dict(revision=hashlib.sha256((hi/'exteriors.glb').read_bytes()).hexdigest()[:16])))
Path('build/city-exteriors/nyny-kiosk-podium-trim.json').write_text(json.dumps(dict(facesCut=count,collisionFacesCut=nc,scope='NYNY podium only, canopy footprint wall/roof faces reaching above .5m; existing ground, guest interior, towers, coaster preserved.'),indent=2));print('KIOSK PODIUM TRIM',count,nc)
