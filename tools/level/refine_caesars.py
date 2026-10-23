import bpy,sys,os,json,ast
from pathlib import Path
sys.path.insert(0,'tools/level');sys.path.insert(0,'tools/blender-level')
from caesars import curved_crown_geometry
from geometry_quality import orient_closed_solids
bpy.ops.wm.open_mainfile(filepath=os.path.abspath('build/level/vegas.blend'))
for o in bpy.data.objects:
    if 'curved central hotel bay' in o.name:
        half=max(abs(v.co.y) for v in o.data.vertices)
        for v in o.data.vertices:v.co.y*=3.1/half
        o.data.update()
if not bpy.data.objects.get('Caesars continuous curved roof crown'):
    vs,fs=curved_crown_geometry();me=bpy.data.meshes.new('Caesars continuous curved roof crown');me.from_pydata([(x,-z,y) for x,y,z in vs],[],fs);me.update();ob=bpy.data.objects.new(me.name,me);bpy.context.scene.collection.objects.link(ob);me.materials.append(bpy.data.materials['c_stone'])
p=Path('build/level/vegas.mesh-level.json');data=json.loads(p.read_text())
for c in data['colliders']:
    if 'curved central hotel bay' in c['name']:c['size'][2]=6.2
for name,pos,color,intensity,distance in [('Caesars service emergency',[-166,3.5,195],'#c88548',35,18),('Caesars supply room light',[-176,4,185],'#d4b584',25,12)]:
    if not any(l.get('name')==name for l in data['lights']):data['lights'].append({'name':name,'type':'point','position':pos,'color':color,'intensity':intensity,'distance':distance,'decay':2})
p.write_text(json.dumps(data,indent=2))
orient_closed_solids();bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath('build/level/vegas.blend'))
source=ast.parse(Path('tools/level/vegas.py').read_text());fn=next(n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=='fast_export');exec(compile(ast.Module(body=[fn],type_ignores=[]),'vegas.py','exec'));fast_export('build/level/vegas.glb')
print('Caesars curved facade seams closed and corridor lighting added',flush=True)
