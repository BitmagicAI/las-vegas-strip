"""Keep mapped Veer shafts clear through the separately fitted Crystals roof."""
import bpy,json,numpy as np
from mathutils import Matrix
from clipping import subtract_boxes
from mapping import TRANSFORMS,veer_openings


def carve_meshes():
 t=TRANSFORMS['crystals'];a,b,c,d=t['linear'];tx,tz=t['translation'];assert b==c==0
 boxes=[([(lo[0]-tx)/a,lo[1],(lo[2]-tz)/d],[(hi[0]-tx)/a,hi[1],(hi[2]-tz)/d]) for lo,hi in veer_openings()]
 count=0
 for obj in list(bpy.data.objects):
  if obj.type!='MESH' or not obj.name.startswith('CityCenter / Crystals /'):continue
  me=obj.data;me.calc_loop_triangles();world=obj.matrix_world;positions=[[p.x,p.z,-p.y] for v in me.vertices for p in [world@v.co]]
  if not positions or max(p[1] for p in positions)<.22:continue
  verts=[];faces=[];uvs=[];mats=[];smooth=[];uv=me.uv_layers.active
  for tri in me.loop_triangles:
   face=[positions[i]+list(uv.data[j].uv if uv else (0,0)) for i,j in zip(tri.vertices,tri.loops)]
   for poly in subtract_boxes(face,boxes):
    n=len(verts);verts.extend((p[0],-p[2],p[1]) for p in poly);uvs.extend(p[3:] for p in poly);faces.append(tuple(range(n,n+len(poly))));mats.append(tri.material_index);smooth.append(tri.use_smooth)
  new=bpy.data.meshes.new(me.name+' / mapped shafts');new.from_pydata(verts,[],faces);new.update()
  for material in me.materials:new.materials.append(material)
  uv=new.uv_layers.new();uv.data.foreach_set('uv',[c for p in uvs for c in p])
  for p,mat,s in zip(new.polygons,mats,smooth):p.material_index=mat;p.use_smooth=s
  obj.data=new;obj.matrix_world=Matrix.Identity(4);count+=1
 print('Carved mapped Veer shafts through',count,'Crystals mesh batches',flush=True)
