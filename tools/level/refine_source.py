p='tools/level/vegas.py';s=open(p).read()
s=s.replace("def text(name,*args,**kwargs):return _text(scene.collection.name+' / '+name,*args,**kwargs)","""def text(name,string,pos,material,yaw=0,size=.5,extrude=.01,both_faces=False):
 # One opaque-backed sign, facing the requested game direction. No overlaid mirrored glyphs.
 curve=bpy.data.curves.new(name,'FONT');curve.body=string;curve.size=size;curve.extrude=extrude;curve.align_x='CENTER'
 obj=bpy.data.objects.new(scene.collection.name+' / '+name,curve);scene.collection.objects.link(obj);obj.location=(pos[0],-pos[2],pos[1]);obj.rotation_euler=(math.pi/2,0,yaw);curve.materials.append(bpy.data.materials[material])
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();mesh=bpy.data.meshes.new_from_object(obj.evaluated_get(dg));obj.data=mesh
""")
start=s.index("  for j in range(9):")
end=s.index("  beam('street lamp'",start)
s=s[:start]+"""  verts=[];faces=[]
  for j in range(11):
   a=j*math.tau/11;length=random.uniform(4,6);base=len(verts)
   for k in range(17):
    t=k/16;rr=length*t;cy=9+2.2*math.sin(t*math.pi)-2*t*t
    width=.42*math.sin(math.pi*t)**.6
    for side in [-1,1]:verts.append((x+.8+rr*math.cos(a)+side*width*math.sin(a),-(z+.4+rr*math.sin(a)-side*width*math.cos(a)),cy))
   for k in range(16):faces.append((base+k*2,base+k*2+1,base+k*2+3,base+k*2+2))
   for k in range(2,16):
    t=k/16;rr=length*t;cy=9+2.2*math.sin(t*math.pi)-2*t*t;wid=.85*math.sin(math.pi*t)
    for side in [-1,1]:
     b=len(verts);verts.extend([(x+.8+rr*math.cos(a),-(z+.4+rr*math.sin(a)),cy),(x+.8+(rr+.2)*math.cos(a),-(z+.4+(rr+.2)*math.sin(a)),cy-.03),(x+.8+(rr+.6)*math.cos(a)+side*wid*math.sin(a),-(z+.4+(rr+.6)*math.sin(a)-side*wid*math.cos(a)),cy-.45)])
     faces.append((b,b+1,b+2))
  me=bpy.data.meshes.new('palm fronds');me.from_pydata(verts,[],faces);ob=bpy.data.objects.new('palm fronds',me);bpy.context.scene.collection.objects.link(ob);me.materials.append(bpy.data.materials['foliage'])
"""+s[end:]
# Signs at opposite entrances each face away from their arcade.
s=s.replace("accent,size=.72,both_faces=True)","accent,yaw=0 if zz>0 else math.pi,size=.72)")
s=s.replace("'emissive_amber',size=3,both_faces=True)","'emissive_amber',yaw=math.pi,size=3)")
s=s.replace("'emissive_pink',size=7,both_faces=True)","'emissive_pink',yaw=math.pi,size=7)")
# Damage skin on front-facing facades, with angular spalls, exposed reinforcement and rubble aprons.
key='# Per-face world UVs'
idx=s.index(key)
s=s[:idx]+"""print('Adding architectural decay',flush=True)
for cx,cz,w,d,h in [(-163,-18,37,54,86),(-151,-100,30,98,72),(-155,66,30,98,72),(163,-76,39,126,74),(162,101,54,72,56),(133,223,110,44,64),(-150,222,92,48,82)]:
 frontx=cx+(w/2+.09 if cx<0 else -w/2-.09)
 for i in range(12):
  zz=cz+random.uniform(-d*.45,d*.45);yy=random.uniform(5,h*.8);sh=random.uniform(5,17);sw=random.uniform(2,5)
  # Charred, irregular strips break up repetitive window grids.
  verts=[(frontx,-(zz-sw),yy-sh/2),(frontx,-(zz+sw),yy-sh*.4),(frontx,-(zz+sw*.5),yy+sh/2),(frontx,-(zz-sw*.2),yy+sh*.3)]
  me=bpy.data.meshes.new('fire scarring');me.from_pydata(verts,[],[(0,1,2,3),(3,2,1,0)]);o=bpy.data.objects.new('fire-damaged facade',me);bpy.context.scene.collection.objects.link(o);me.materials.append(bpy.data.materials['soot'])
 for i in range(45):
  zz=cz+random.uniform(-d/2,d/2);xx=frontx+(1 if cx<0 else -1)*random.uniform(1,8);hh=random.uniform(.2,1.3)
  decor('facade rubble '+str(cx)+' '+str(i),(xx,hh/2,zz),(random.uniform(.4,2),hh,random.uniform(.5,2.2)),'concrete',yaw=random.random()*6.28,bevel=.13)
 for i in range(8):
  zz=cz+random.uniform(-d/2,d/2)
  beam('exposed roof rebar',(frontx,h,zz),(frontx+random.uniform(-1,1),h+random.uniform(1.5,3.5),zz+.7),.035,'rust',5)
# Split the broad sidewalks with long tiled promenade strips and service gutters.
for xx in [-43,41]:
 for zz in range(-278,282,4):
  if abs(zz)<25 and xx<0:continue
  decor('promenade panel '+str(xx)+' '+str(zz),(xx,.07,zz),(8,.08,3.9),'limestone')
# Fast export constructs one combined mesh per material without thousands of operator graph updates.
def fast_export(path):
 bpy.context.view_layer.update();groups={}
 for obj in list(bpy.data.objects):
  if obj.type!='MESH':continue
  key=obj.data.materials[0].name if obj.data.materials else 'concrete'
  g=groups.setdefault(key,{'v':[],'f':[],'uv':[]});base=len(g['v']);g['v'].extend([tuple(obj.matrix_world@v.co) for v in obj.data.vertices])
  uvs=obj.data.uv_layers.active
  for poly in obj.data.polygons:
   g['f'].append(tuple(base+i for i in poly.vertices));g['uv'].extend([tuple(uvs.data[i].uv) if uvs else (0,0) for i in poly.loop_indices])
 bpy.ops.object.select_all(action='DESELECT');created=[]
 for name,g in groups.items():
  me=bpy.data.meshes.new('export '+name);me.from_pydata(g['v'],[],g['f']);me.update();uv=me.uv_layers.new();uv.data.foreach_set('uv',[c for pair in g['uv'] for c in pair]);me.materials.append(bpy.data.materials[name]);o=bpy.data.objects.new('Level_'+name,me);bpy.context.scene.collection.objects.link(o);o.select_set(True);created.append(o)
 bpy.context.view_layer.objects.active=created[0]
 bpy.ops.export_scene.gltf(filepath=os.path.abspath(path),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_lights=False,export_cameras=False)
 for o in created:bpy.data.objects.remove(o,do_unlink=True)
 return os.path.getsize(path)
scene.export_glb=fast_export
bpy.context.view_layer.update()
"""+s[idx:]
open(p,'w').write(s)
