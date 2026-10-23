import json,math,copy
from pathlib import Path
from mapping import *
from clipping import subtract_boxes,convex_triangles
OUT=ROOT/'build/geographic-strip'
def read(p):return json.loads((BASE/p).read_text())
def save(name,data):(OUT/name).write_text(json.dumps(data,indent=2))
def mapped(p,key):
 if isinstance(p,dict):q=point([p['x'],p.get('y',0),p['z']],key);return dict(x=q[0],y=q[1],z=q[2])
 return point(p,key)
def volume(v,key):
 q=copy.deepcopy(v);q['position']=point(v['position'],key);a=v.get('yaw',0);vx=vector([math.cos(a),0,-math.sin(a)],key);vz=vector([math.sin(a),0,math.cos(a)],key)
 q['yaw']=yaw(a,key);q['size']=[v['size'][0]*math.hypot(vx[0],vx[2]),v['size'][1],v['size'][2]*math.hypot(vz[0],vz[2])];return q
src=read('build/hotels/staged-vegas.mesh-level.json');out=copy.deepcopy(src);out['colliders']=[];unmapped=[]
for c in src['colliders']:
 n=c['name'].lower()
 if any(k in n for k in ['continuous foundation','district edge','district ground','citycenter / streets']):continue
 k=owner(c['name'],center(c))
 if not k:unmapped.append(c['name']);continue
 if k=='cosmopolitan':continue
 q=collider(c,k)
 if k=='crystals' and q['shape'] in ('trimesh','convexHull'):
  boxes=veer_openings()
  if q['shape']=='convexHull':q['indices']=convex_triangles(q['vertices']);q['shape']='trimesh'
  v=q['vertices'];vs=[];ids=[]
  for i in range(0,len(q['indices']),3):
   face=[v[j*3:j*3+3] for j in q['indices'][i:i+3]]
   for poly in subtract_boxes(face,boxes):
    n=len(vs)//3;vs.extend(c for p in poly for c in p)
    for j in range(1,len(poly)-1):ids.extend([n,n+j,n+j+1])
  if not ids:continue
  q['vertices']=vs;q['indices']=ids
 out['colliders'].append(q)
# Native boxes stay small enough for stable capsule contact at map coordinates.
# A kilometre-wide thin box produces penetration in Rapier's character sweeps.
for x in range(-2350,2550,250):
 for z in range(-4400,4300,250):
  sx=min(250,2550-x);sz=min(250,4300-z)
  out['colliders'].append(dict(name=f'OSM district foundation {x},{z}',shape='box',position=[x+sx/2,-.52,z+sz/2],size=[sx+.04,1,sz+.04],yaw=0))
for key in ['landmarks','lights','volumes']:
 out[key]=[]
 for v in src[key]:
  k=owner(v['name'],v['position'])
  if not k:continue
  if key=='volumes':q=volume(v,k)
  else:
   q=copy.deepcopy(v);q['position']=point(q['position'],k)
   if 'target'in q:q['target']=point(q['target'],k)
   if 'yaw'in q:q['yaw']=yaw(q['yaw'],k)
  out[key].append(q)
out['extras']['geographicStrip']=True;out['extras']['source']='OSM 2026-10-03; © OpenStreetMap contributors, ODbL';out['extras']['mapOrigin']=[-115.173,36.116]
save('detailed.mesh-level.json',out);save('unmapped-legacy-colliders.json',unmapped)

recipes=read('src/work/hotels/towers.json')
for t in recipes:
 k=t['id'] if t['building']=='veer' else t['building'];a,b,c,d=TRANSFORMS[k]['linear'];co,si=math.cos(t['yaw']),math.sin(t['yaw'])
 t['linear']=[a*co-b*si,a*si+b*co,c*co-d*si,c*si+d*co];t['origin']=point(t['origin'],k);t['yaw']=yaw(t['yaw'],k)
save('towers.json',recipes)
review=read('src/work/public-resorts/review.json')
for shot in review:
 k=owner(shot['name'],shot['position']);shot['position']=point(shot['position'],k);shot['target']=point(shot['target'],k)
# Actual mapped road viewpoints, in addition to all existing resort comparisons.
for name,pos,target in [('OSM / Afterlight plaza',[-47,2,305],[-295,25,321]),('OSM / Bellagio and Paris',[12,2,410],[90,35,401]),('OSM / CityCenter',[-10,2,1010],[-335,65,962]),('OSM / South Strip',[13,2,2870],[13,14,2600]),('OSM / North Strip',[1315,2,-3400],[1380,20,-3580])]:review.append(dict(name=name,position=pos,target=target))
save('review.json',review)

missions=read('src/work/vegas-missions.json')
missions['safeZone']['center']=point(missions['safeZone']['center'],'sanctuary')
for v in missions['supplies']:
 k={'food':'bellagio','medicine':'medicine','weapons':'weapons','ammo':'ammo'}[v['type'] if 'type'in v else v['id']]
 for key in ['position']:
  if key in v:v[key]=point(v[key],k)
for v in missions['hides']:
 k={'food':'bellagio','medicine':'medicine','weapons':'weapons','ammo':'ammo','north_garage':'medicine','south_casino':'weapons'}[v['id']]
 for key in ['position','exit']:
  if key in v:v[key]=point(v[key],k)
 v['exits']=[point(p,k) for p in v.get('exits',[])]
for name,route in missions['routes'].items():
 k=owner(name)
 q=point([route[0],0,route[1]],k or owner('',[route[0],0,route[1]]) or 'sanctuary');missions['routes'][name]=[q[0],q[2]]
for section in ['bellagio','paris','caesars','cosmopolitan']:
 if section not in missions:continue
 for field,value in missions[section].items():
  k='eiffel' if section=='paris' and field in ['towerCenter','liftGround','liftTop'] else section
  if field=='mapNorth':continue
  if field=='hordeExits':missions[section][field]=[point(p,section) for p in value];continue
  if isinstance(value,list) and len(value)==3 and all(isinstance(x,(int,float)) for x in value):missions[section][field]=point(value,k)
 if section=='paris':missions[section]['towerYaw']=yaw(missions[section]['towerYaw'],'eiffel')
 if 'interiorBounds'in missions[section]:
  b=missions[section]['interiorBounds'];pp=[point([x,0,z],section) for x in [b['minX'],b['maxX']] for z in [b['minZ'],b['maxZ']]];missions[section]['interiorBounds']=dict(minX=min(p[0] for p in pp),maxX=max(p[0] for p in pp),minZ=min(p[2] for p in pp),maxZ=max(p[2] for p in pp))
save('vegas-missions.json',missions)

world=read('src/work/world.json');doors=world['worldProfileData']['doors']
for d in doors:
 p=d['position'];k=owner(d.get('id',''),[p['x'],p.get('y',0),p['z']])
 if not k:raise RuntimeError('Unassigned door '+str(d))
 angle=d.get('rotationY',0);v=vector([math.cos(angle),0,-math.sin(angle)],k);sx=math.hypot(v[0],v[2]);d['position']=mapped(p,k);d['rotationY']=math.atan2(-v[2],v[0])
 for field in ['width','slideDistance']:
  if field in d:d[field]*=sx
 if 'scale'in d and isinstance(d['scale'],dict):d['scale']['x']*=sx
save('doors.json',doors)
save('anchors.json',dict(sanctuary=point([-42,0,0],'sanctuary'),companion=point([-38,.53,3],'sanctuary'),jeep=point([-40,.51,2],'sanctuary'),charger=point([-43,.51,5],'sanctuary'),transforms=TRANSFORMS))

manifest=OUT/'source-visibility.json'
if manifest.exists():
 vis=json.loads(manifest.read_text())
 for z in vis['zones']:
  k=owner(z['name'],z['center']);z['sourceCenter']=z['center'];z['sourceSize']=z['size'];z['sourceYaw']=z['yaw'];z['geoTransform']=TRANSFORMS[k]
  q=volume(dict(position=z['center'],size=z['size'],yaw=z['yaw']),k);z['center']=q['position'];z['size']=q['size'];z['yaw']=q['yaw']
 for p in vis['portals']:
  k=owner(p['id'],p['position']);p['position']=point(p['position'],k)
 save('visibility.json',vis)
print('Mapped',len(out['colliders']),'colliders,',len(doors),'doors,',len(recipes),'guest cores;',len(unmapped),'discarded unrelated legacy colliders')
