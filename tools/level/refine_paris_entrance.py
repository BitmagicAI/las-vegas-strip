"""Apply reviewed base/entry refinements to the built scene (also authored in paris.py)."""
import bpy,os,ast,json
bpy.ops.wm.open_mainfile(filepath=os.path.abspath('build/level/vegas.blend'))
bpy.context.view_layer.update()
removed=[];bases=[]
for o in list(bpy.data.objects):
 if o.type!='MESH' or 'Paris ' not in o.name:continue
 if 'hotel stone body' in o.name:
  old=o.dimensions.z;h=o.location.z+old/2
  for v in o.data.vertices:v.co.z*=h/old
  o.location.z=h/2;o.data.update();bases.append(o.name)
 if not any(s in o.name for s in ['arched glass','recessed window','window transom','window mullion','arch pier','voussoir','arch keystone']):continue
 vs=[o.matrix_world@v.co for v in o.data.vertices]
 if min(v.x for v in vs)>68 and max(v.x for v in vs)<71 and min(v.z for v in vs)>.5 and max(v.z for v in vs)<7 and min(-v.y for v in vs)>-44 and max(-v.y for v in vs)<-34:
  removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
assert len(bases)==4,(len(bases),bases)
assert len(removed)>50,len(removed)
p='build/level/vegas.mesh-level.json';j=json.load(open(p))
for c in j['colliders']:
 if 'Paris ' in c['name'] and 'hotel stone body' in c['name']:
  h=c['position'][1]+c['size'][1]/2;c['position'][1]=h/2;c['size'][1]=h
json.dump(j,open(p,'w'),indent=2)
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath('build/level/vegas.blend'))
src=ast.parse(open('tools/level/vegas.py').read());fn=next(n for n in src.body if isinstance(n,ast.FunctionDef) and n.name=='fast_export')
exec(compile(ast.Module(body=[fn],type_ignores=[]),'fast_export','exec'))
fast_export('build/level/vegas.glb')
print('REFINED',len(bases),'grounded hotel masses;',len(removed),'entrance window parts removed',flush=True)
