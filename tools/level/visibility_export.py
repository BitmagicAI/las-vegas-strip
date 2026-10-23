"""Separate render batches using existing room volumes; no new authoring required."""
import bpy,json,os,re,math,hashlib
import numpy as np
from pathlib import Path

def building(name):
 n=name.lower()
 for token,key in [('forum','caesars'),('planet hollywood','planet-hollywood'),('planet-hollywood','planet-hollywood'),('cosmopolitan','cosmopolitan'),('bellagio','bellagio'),('horseshoe','horseshoe'),('flamingo','flamingo'),('paris','paris'),('caesars','caesars'),('crystals','crystals'),('vdara','vdara'),('waldorf','waldorf'),('veer','veer'),('aria','aria')]:
  if token in n:return key
 return None

def export_visibility(path,data_path='build/level/vegas.mesh-level.json',manifest_path='src/work/vegas-visibility.json',stats_path='build/level/visibility-stats.json',version_path='src/work/vegas-asset-version.json',interior_cell=0):
 data=json.loads(Path(data_path).read_text());zones=[]
 for v in data['volumes']:
  tags=v.get('tags',[]);b=building(v['name'])
  if not b or not any(t in tags for t in ['indoors','interior','enclosed','hotel-room']):continue
  zones.append(dict(id='zone'+str(len(zones)),name=v['name'],building=b,center=v['position'],size=v['size'],yaw=v.get('yaw',0),windowed=any(t in tags for t in ['windowed','hotel-room','observation']),arrival='arrival' in tags,room='hotel-room' in tags,corridor='corridor' in v['name'].lower() or 'corridor' in tags))
 # Small windowed guest rooms take precedence over encompassing floor volumes.
 zones.sort(key=lambda z: (not z['room'],np.prod(z['size'])))
 doors=json.loads(Path('build/level/vegas.doors.json').read_text())
 extra=Path('build/arrival-reconstruction/extra-doors.json')
 if extra.exists():doors.extend(json.loads(extra.read_text()))
 overrides=Path('build/arrival-reconstruction/door-overrides.json')
 if overrides.exists():
  replacements=json.loads(overrides.read_text())
  for d in doors:
   if d['id'] in replacements:d.update(replacements[d['id']])
 portals=[]
 def at(p):
  result=set()
  for z in zones:
   d=np.array(p)-z['center'];a=z['yaw'];q=[math.cos(a)*d[0]-math.sin(a)*d[2],d[1],math.sin(a)*d[0]+math.cos(a)*d[2]]
   if all(abs(q[i])<=z['size'][i]/2+.05 for i in range(3)):result.add(z['building'])
  return result
 for d in doors:
  p=d['position'];a=d.get('rotationY',0);x,y,z=p['x'],p['y'],p['z'];normal=[math.sin(a),0,math.cos(a)]
  sides=[at([x+s*normal[0],y,z+s*normal[2]]) for s in [-1,1]]
  owners=sides[0]|sides[1]
  if owners:portals.append(dict(id=d['id'],position=[x,y,z],buildings=sorted(owners),exterior=not sides[0] or not sides[1]))
 # Short enclosed connectors may be represented by doorway/route records only.
 for p in portals:
  for q in portals:
   if p is not q and math.dist(p['position'],q['position'])<=8 and set(p['buildings'])!=set(q['buildings']):
    p['adjacent']=sorted(set(p.get('adjacent',[]))|set(q['buildings']))
 for p in portals:
  p['arrivals']=[]
  for z in zones:
   if not z['arrival']:continue
   dx=p['position'][0]-z['center'][0];dz=p['position'][2]-z['center'][2];c,s=math.cos(z['yaw']),math.sin(z['yaw'])
   if abs(c*dx-s*dz)<z['size'][0]/2 and abs(abs(s*dx+c*dz)-z['size'][2]/2)<2:p['arrivals'].append(z['id'])
 manifest=dict(version=2,zones=zones,portals=portals)
 Path(manifest_path).write_text(json.dumps(manifest,indent=2))
 bpy.context.view_layer.update();groups={};stats={}
 for obj in list(bpy.data.objects):
  if obj.type!='MESH':continue
  me=obj.data;nv=len(me.vertices)
  if not nv:continue
  # A windowed streamed room reveals the city beyond its owning tower shell.
  # Keep upper architecture separate from the ground-floor casino and streets.
  base_tower='bellagio' if 'Bellagio / curved main tower' in obj.name else ''
  bellagio_architecture=building(obj.name)=='bellagio'
  owner=obj.get('arrivalOwner') or building(obj.name)
  arrival_zone=next((z for z in zones if z['name']=='Arrival / '+str(owner)+' / '+str(obj.get('arrivalName',''))),None)
  guest_heights={'paris':10.7,'caesars':10.7,'cosmopolitan':17.9,'flamingo':14.3,'horseshoe':14.3,'planet-hollywood':14.3,'aria':14.3,'vdara':14.3,'waldorf':14.3}
  co=np.empty(nv*3);me.vertices.foreach_get('co',co);co=co.reshape((-1,3));matrix=np.array(obj.matrix_world);world=co@matrix[:3,:3].T+matrix[:3,3]
  game=world[:,[0,2,1]].copy();game[:,2]*=-1
  uv=me.uv_layers.active
  lo=game.min(axis=0);hi=game.max(axis=0)
  candidates=[]
  for z in zones:
   a=z['yaw'];c,s=math.cos(a),math.sin(a);half=np.array(z['size'])/2;zc=np.array(z['center']);ext=np.array([abs(c)*half[0]+abs(s)*half[2],half[1],abs(s)*half[0]+abs(c)*half[2]])+.65
   if np.all(hi>=zc-ext) and np.all(lo<=zc+ext):candidates.append((z,zc,half,c,s))
  # A freestanding cabinet next to an envelope boundary is still furniture,
  # not facade. Classify each complete cabinet by its center to keep it out of
  # the outdoor pass; no mesh simplification or collider changes are involved.
  furniture_zone=None
  if interior_cell and 'slot cabinet' in obj.name.lower():
   center=(lo+hi)/2
   for z,zc,half,c,s in candidates:
    d=center-zc;q=np.array([c*d[0]-s*d[2],d[1],s*d[0]+c*d[2]])
    if np.all(np.abs(q)<half):furniture_zone=z['id'];break
  # Classify each polygon, rather than a material batch that may cross resorts.
  buckets={}
  for poly in me.polygons:
   ids=list(poly.vertices);pts=game[ids];center=pts.mean(axis=0);zone='outside';kind='outside';tower=base_tower
   # Individually authored structural bays are separate from the main tower
   # mesh. They must also hide through streamed guest-room windows, including
   # the deeper Premier King rooms, without hiding other resorts' plaster.
   if bellagio_architecture and center[1]>=10.7:tower='bellagio'
   if owner in guest_heights and center[1]>=guest_heights[owner]:tower=owner
   # CityCenter source meshes batch both towers by material. Their east/west
   # footprints are disjoint in X, so assign ownership per polygon.
   if 'CityCenter / Veer /' in obj.name and center[1]>=17.9:tower='veer-east' if center[0]>-157 else 'veer-west'
   for z,zc,half,c,s in candidates:
    d=center-zc;q=np.array([c*d[0]-s*d[2],d[1],s*d[0]+c*d[2]])
    if np.any(np.abs(q)>half+.65):continue
    zone=z['id'];local=pts-np.array(z['center']);rx=local[:,0].copy();rz=local[:,2].copy();local[:,0]=c*rx-s*rz;local[:,2]=s*rx+c*rz
    kind='interior' if np.all(np.abs(local)<half-.32) else 'shell';break
   # Faceted roofs can rise above their room's nominal ceiling. Their explicit
   # shell role keeps them visible outdoors; interior details still use spatial
   # ownership so the same automatic culling policy applies to the new district.
   if obj.get('visibilityRole')=='shell' and zone!='outside':kind='shell'
   if furniture_zone:zone=furniture_zone;kind='interior'
   if arrival_zone:
    zone=arrival_zone['id'];kind=obj.get('visibilityRole','interior');tower=''
   material=obj.data.materials[poly.material_index].name if obj.data.materials else 'concrete'
   # Split the dense imported casino furniture, not cheap walls/signs. This
   # retains every triangle/UV while allowing unseen slot rows to be culled,
   # without multiplying draw batches throughout all the other resorts.
   cell=tuple(math.floor(float(v)/interior_cell) for v in center) if furniture_zone else ()
   buckets.setdefault((zone,kind,material,tower,cell),[]).append(poly)
  for key,polys in buckets.items():
   g=groups.setdefault(key,dict(v=[],f=[],uv=[],smooth=[]));used=sorted({i for p in polys for i in p.vertices});base=len(g['v']);lookup={i:base+j for j,i in enumerate(used)};g['v'].extend(tuple(world[i]) for i in used)
   for p in polys:
    g['f'].append(tuple(lookup[i] for i in p.vertices));g['smooth'].append(p.use_smooth);g['uv'].extend(tuple(uv.data[i].uv) if uv else (0,0) for i in p.loop_indices)
 bpy.ops.object.select_all(action='DESELECT');created=[]
 for (zone,kind,material,tower,cell),g in groups.items():
  name=f'VIS_{zone}_{kind}_{material}_{tower}'+('_cell'+','.join(map(str,cell)) if cell else '');me=bpy.data.meshes.new(name);me.from_pydata(g['v'],[],g['f']);me.update();uv=me.uv_layers.new();uv.data.foreach_set('uv',[c for p in g['uv'] for c in p]);me.materials.append(bpy.data.materials[material]);o=bpy.data.objects.new(name,me);bpy.context.scene.collection.objects.link(o);o['visibilityZone']=zone;o['visibilityKind']=kind;o.select_set(True);created.append(o)
  if tower:o['visibilityTower']=tower
  for p,smooth in zip(me.polygons,g['smooth']):p.use_smooth=smooth
  stats.setdefault(zone+':'+kind,dict(meshes=0,triangles=0));stats[zone+':'+kind]['meshes']+=1;stats[zone+':'+kind]['triangles']+=sum(len(f)-2 for f in g['f'])
 bpy.context.view_layer.objects.active=created[0]
 bpy.ops.export_scene.gltf(filepath=os.path.abspath(path),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_lights=False,export_cameras=False,export_extras=True)
 bpy.data.batch_remove(created)
 Path(stats_path).write_text(json.dumps(stats,indent=2));print('VISIBILITY EXPORT',len(zones),'zones',len(groups),'batches',flush=True)
 # Version changes only after the GLB is fully written. Local browser/loader
 # caches otherwise keep the previous hotel mesh across dev-server reloads.
 with open(path,'rb') as f:
  digest=hashlib.file_digest(f,'sha256').hexdigest()[:16]
 Path(version_path).write_text(json.dumps({'revision':digest})+'\n')
 return os.path.getsize(path)
