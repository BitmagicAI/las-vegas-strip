"""Compile OSM into local render/collision cells and deterministic resort mappings."""
import json,math,collections,heapq,re,sys
from pathlib import Path
import numpy as np
from functools import lru_cache
from shapely.geometry import Polygon,LineString,Point,box
from shapely.ops import unary_union,triangulate,nearest_points
from shapely.strtree import STRtree
from shapely.prepared import prep
from mapping import *
from streets import StreetBuilder, county_geometry, PUBLIC, SPHERE_BRIDGE
from pedestrian_access import AccessPlanner, correct_heights
from surface_geometry import triangles as surface_triangles, ROAD_Y, WALK_Y, street_y
from landcover import county_medians, landscape
from building_surfaces import BuildingSurfaces
from shapely.geometry import mapping as geojson_mapping
OUT=ROOT/'build/geographic-strip';OUT.mkdir(exist_ok=True)
SURVEY=json.loads((ROOT/'build/strip-survey/survey.json').read_text());RAW=json.loads((ROOT/'build/strip-survey/osm.json').read_text())
CELL=160
meshes={};physics=collections.defaultdict(lambda:dict(vertices=[],indices=[]));report={}
def mesh(key,mat,vertices,faces):
 if not faces:return
 g=meshes.setdefault((key,mat),dict(vertices=[],faces=[],material=mat,cell=key));n=len(g['vertices']);g['vertices'].extend(vertices);g['faces'].extend([[i+n for i in f] for f in faces])
def phys(key,vertices,faces):
 if not faces:return
 g=physics[key];n=len(g['vertices'])//3;g['vertices'].extend(v for p in vertices for v in p);g['indices'].extend(n+i for f in faces for i in f)
def polygons(g):
 if g.is_empty:return []
 if g.geom_type=='Polygon':return [g]
 return [p for x in getattr(g,'geoms',[]) for p in polygons(x)]
def flat(g,y,mat,collision=False):
 if g.is_empty:return
 x0,z0,x1,z1=g.bounds
 tiles=[]
 for ix in range(math.floor(x0/CELL),math.floor(x1/CELL)+1):
  for iz in range(math.floor(z0/CELL),math.floor(z1/CELL)+1):
   tile=box(ix*CELL,iz*CELL,(ix+1)*CELL,(iz+1)*CELL)
   if g.intersects(tile):tiles.extend(polygons(g.intersection(tile)))
 print('Surface',mat,len(tiles),'cells',flush=True)
 for p in tiles:
  for tri in surface_triangles(p):
   coords=list(tri.exterior.coords)[:-1];v=[[x,y,z] for x,z in coords];c=tri.centroid;key=f'{math.floor(c.x/CELL)},{math.floor(c.y/CELL)}'
   # Shapely XY CCW is downward in X/Z. Reverse to upward in game space.
   f=[[0,2,1]];mesh(key,mat,v,f)
   if collision:phys(key,v,f)
def building_mesh(poly,h,base,mat,ident,tags):
 roof=tags.get('roof:shape','flat')
 try:rise=float(tags.get('roof:height','0'))
 except ValueError:rise=0
 for p in polygons(poly):
  # Roof shapes are driven by OSM tags. Unknown forms stay flat instead of
  # inventing architectural details. A low ring count keeps skyline meshes cheap.
  c=p.centroid;key=f'{math.floor(c.x/CELL)},{math.floor(c.y/CELL)}'
  x0,z0,x1,z1=p.bounds;span=min(x1-x0,z1-z0)
  rise=min(h-base,max(0,rise or (span*.30 if roof in ('dome','pyramidal') else 0)))
  if tags.get('shape')=='spherical_cutted':rise=h-base
  shaped=roof in ('pyramidal','dome') and not p.interiors and p.equals(p.convex_hull)
  eave=h-rise if shaped else h
  roofmat=style_material(tags,True,mat)
  verts=[];faces=[]
  for ring in [p.exterior,*p.interiors]:
   a=list(ring.coords)
   for (x,z),(xx,zz) in zip(a,a[1:]):
    
    for triangle in building_surfaces.wall(ident,(x,z),(xx,zz),base,eave,access):
     n=len(verts);verts.extend(triangle);faces.append([n,n+1,n+2])
  mesh(key,mat,verts,faces);phys(key,verts,faces)
  verts=[];faces=[]
  if shaped:
   a=list(p.exterior.coords)[:-1]
   # Convert to clockwise for the same outward winding as the side walls.
   if p.exterior.is_ccw:a.reverse()
   levels=1 if roof=='pyramidal' else 8
   for j in range(levels+1):
    t=j/levels;scale=1-t if roof=='pyramidal' else math.cos(t*math.pi/2);yy=eave+rise*(t if roof=='pyramidal' else math.sin(t*math.pi/2))
    verts.extend([[c.x+(x-c.x)*scale,yy,c.y+(z-c.y)*scale] for x,z in a])
   n=len(a)
   for j in range(levels):
    for i in range(n):
     k=j*n+i;kk=j*n+(i+1)%n;faces.extend([[k,kk,kk+n],[k,kk+n,k+n]])
  else:
   roof_shape=building_surfaces.roof(ident,p,h)
   for roof_piece in polygons(roof_shape):
    for t in surface_triangles(roof_piece):
     a=list(t.exterior.coords)[:-1];n=len(verts);verts.extend([[x,h,z] for x,z in a]);faces.append([n,n+2,n+1])
  if access.tree.query(p).size:
   clipped=[];triangles=[]
   for face in faces:
    for tri in access.roof_triangle([verts[i] for i in face]):
     offset=len(clipped);clipped.extend(tri);triangles.append([offset,offset+1,offset+2])
   verts,faces=clipped,triangles
  mesh(key,roofmat,verts,faces);phys(key,verts,faces)

# OSM Buildings' GeoJSON conventions preserve these same source attributes.
# This importer uses the OSM records directly; no tile service or code dependency.
styles={}
def style_material(tags,roof=False,fallback='building-estimated'):
 prefix='roof' if roof else 'building'
 color=tags.get(prefix+':colour',tags.get(prefix+':color','')).lower()
 material=tags.get(prefix+':material',tags.get('building:facade:material',tags.get('building:cladding',''))).lower()
 colors={'black':'#20252c','white':'#dad9d2','grey':'#777c80','gray':'#777c80','gold':'#b19c61','beige':'#b9af96','brown':'#806f5a','red':'#995844','blue':'#577788','green':'#5a7770','silver':'#adb4b7'}
 color=colors.get(color,color)
 if not re.fullmatch(r'#[0-9a-f]{6}',color):color='#65808b' if material in ('glass','mirror') else ''
 if not color and not material:return fallback
 name='tag/'+(color or 'default')+'/'+material
 styles[name]=dict(color=color or '#9b998e',material=material)
 return name

# Trim background only where the authored architecture actually occupies space.
# The rest of a large resort's OSM envelope remains a low-detail wing.
source=json.loads((BASE/'build/hotels/staged-vegas.mesh-level.json').read_text());cuts=[]
for v in source['volumes']:
 key=owner(v['name'],v['position'])
 if not key or not any(t in v.get('tags',[]) for t in ['indoors','interior','public','enclosed']):continue
 x,y,z=v['position'];sx,sy,sz=v['size'];a=v.get('yaw',0);c,s=math.cos(a),math.sin(a)
 pp=[point([x+c*xx+s*zz,y,z-s*xx+c*zz],key) for xx,zz in [(-sx/2,-sz/2),(-sx/2,sz/2),(sx/2,sz/2),(sx/2,-sz/2)]]
 cuts.append(Polygon([(p[0],p[2]) for p in pp]).buffer(2))
objects=json.loads((OUT/'objects.json').read_text())
for o in objects:
 if o['max'][1]<20:continue
 lo,hi=o['min'],o['max'];p=[(lo[i]+hi[i])/2 for i in range(3)];key=owner(o['name'],p)
 if not key:continue
 if (hi[0]-lo[0])*(hi[2]-lo[2])<8:continue
 pp=[point([x,0,z],key) for x,z in [(lo[0],lo[2]),(lo[0],hi[2]),(hi[0],hi[2]),(hi[0],lo[2])]];cuts.append(Polygon([(p[0],p[2]) for p in pp]).buffer(.8))
# Reserve the actual arrival suite and a twelve-metre public approach. A source
# OSM podium outline must not reseal the authored glass entrance just outside
# its interior volume. The far remainder of the podium still supplies massing.
for name,spec in json.loads((ROOT/'build/arrival-reconstruction/report.json').read_text())['properties'].items():
 key=owner(name);ox,y,oz=spec['origin'];w,depth,h=spec['dimensions'];co,si=math.cos(spec['yaw']),math.sin(spec['yaw'])
 ps=[point([ox+co*x+si*z,y,oz-si*x+co*z],key) for x in [-w/2-1,w/2+1] for z in [-12,depth+3]]
 cuts.append(Polygon([(ps[i][0],ps[i][2]) for i in [0,1,3,2]]))
# Keep the sanctuary, entry approaches and depot grounds clear.
for k in ['sanctuary','medicine','weapons','ammo']:
 b=TRANSFORMS[k]['target'];cuts.append(box(*b).buffer(2))
# Streamed high-rise circulation owns this exact footprint, including any
# intersecting low podium. Do not leave the old podium collider across its door.
for t in json.loads(Path('src/work/hotels/highrise-towers.json').read_text())+json.loads(Path('src/work/hotels/landmark-towers.json').read_text()):
 a,b,c,d=t['linear'];ox,oy,oz=t['origin'];front=-5.25-6*t['bays']
 def mapped(x,z):return (ox+a*x+b*z,oz+c*x+d*z)
 cuts.append(Polygon([mapped(x,z) for x,z in [(-9.6,front),(-9.6,5.4),(9.6,5.4),(9.6,front)]]))
 cuts.append(Polygon([mapped(x,z) for x,z in [(-2.5,t['lobbyFront']-12),(-2.5,front),(2.5,front),(2.5,t['lobbyFront']-12)]]))
cut=unary_union(cuts).buffer(.1)
print('Replacement cut ready',len(cuts),flush=True)

ORIGIN=SURVEY['summary']['origin'];R=6378137
def coord(p):return (R*math.radians(p['lon']-ORIGIN[0])*math.cos(math.radians(ORIGIN[1])),-R*math.radians(p['lat']-ORIGIN[1]))
DRIVE={'motorway','motorway_link','trunk','trunk_link','primary','primary_link','secondary','secondary_link','tertiary','tertiary_link','unclassified','residential','living_street','service'}
WALK={'footway','path','pedestrian','steps'}
roads=[];graph=collections.defaultdict(list);positions={};elev={};nodeways=collections.defaultdict(list)
for e in RAW['elements']:
 t=e.get('tags',{});cl=t.get('highway');geom=e.get('geometry');nodes=e.get('nodes')
 if e['id'] in (1352089771,543728952):continue  # Authored Rialto and plaza own these footways.
 if e['type']!='way' or cl not in DRIVE|WALK or not geom or len(geom)<2 or not nodes:continue
 if t.get('indoor')=='yes' or 'level'in t and t.get('level') not in ('0','0;1') or t.get('tunnel') in ('yes','building_passage') and cl not in DRIVE:continue
 if t.get('access')=='no' or t.get('area')=='yes':continue
 # Parking aisles stay present, but are narrower than a public through road.
 try:w=float(re.match(r'[\d.]+',t.get('width',''))[0])
 except (TypeError,ValueError):
  try:lanes=int(t.get('lanes','').split(';')[0])
  except ValueError:lanes=0
  w=lanes*3.4 if lanes and cl in DRIVE else {'motorway':11,'motorway_link':5,'primary':10.2,'secondary':7,'tertiary':7,'unclassified':6.5,'residential':6,'service':4.5,'footway':2.8,'path':2.2,'pedestrian':6,'steps':2.8}.get(cl,6)
 if cl in WALK and t.get('bridge')=='yes' and t.get('golf')!='cartpath':w=max(w,4.8 if LineString([coord(p) for p in geom]).length>12 else 2.8)
 if cl=='steps' and not t.get('width'):w=1.2 if t.get('conveying') else 1.8
 if e['id']==SPHERE_BRIDGE:w=5.5
 w=max(1.4,min(w,34));pts=[coord(p) for p in geom]
 if LineString(pts).length<.2:continue
 try:layer=int(t.get('layer','0'))
 except ValueError:layer=0
 deck=max(1,layer)*6 if t.get('bridge') in ('yes','viaduct') else 0
 # Elevated pedestrian walks are independent from the drive network.
 rec=dict(id=e['id'],name=t.get('name',''),highway=cl,width=w,nodes=nodes,points=pts,bridge=bool(deck),tags=t)
 roads.append(rec)
 for n,p in zip(nodes,pts):positions[n]=p;elev[n]=max(elev.get(n,0),deck);nodeways[n].append(rec)
 for a,b in zip(nodes,nodes[1:]):
  length=math.dist(positions[a],positions[b]);graph[a].append((b,length));graph[b].append((a,length))
# Propagate road bridge grades only on the driving graph. Pedestrian bridges
# have steeper stair/ramp approaches and terminate at ground-level road nodes;
# they must not lift the carriageway underneath them.
elev={n:0.0 for n in positions};drive_nodes={n for r in roads if r['highway'] in DRIVE for n in r['nodes']}
for driving in (True,False):
 g=collections.defaultdict(list);height={}
 ground_anchors=set()
 if not driving:
  for r in roads:
   if r['highway']!='steps':continue
   ends=[r['nodes'][0],r['nodes'][-1]]
   upper=[n for n in ends if any(branch['bridge'] for branch in nodeways[n])]
   if len(upper)==1:
    lower=ends[1] if upper[0]==ends[0] else ends[0]
    if not any(branch['highway']=='steps' and branch['id']!=r['id'] for branch in nodeways[lower]):ground_anchors.add(lower)
 for r in roads:
  if (r['highway'] in DRIVE)!=driving:continue
  try:layer=max(1,int(r['tags'].get('layer','1')))
  except ValueError:layer=1
  seed=6*layer if r['bridge'] else 0
  for n in r['nodes']:height[n]=max(height.get(n,0),seed)
  slope=.065 if driving else .65 if r['highway']=='steps' else .14
  for a,b in zip(r['nodes'],r['nodes'][1:]):
   cost=math.dist(positions[a],positions[b])*slope;g[a].append((b,cost));g[b].append((a,cost))
 queue=[(-v,n) for n,v in height.items() if v];heapq.heapify(queue)
 while queue:
  neg,n=heapq.heappop(queue);h=-neg
  if h<height[n]-1e-8:continue
  for other,cost in g[n]:
   h2=max(0,h-cost)
   if not driving and (other in drive_nodes or other in ground_anchors):h2=0
   if h2>height[other]+.0001:height[other]=h2;heapq.heappush(queue,(-h2,other))
 for n,h in height.items():
  if driving or n not in drive_nodes:elev[n]=max(elev[n],h)
correct_heights(roads,elev)
replacement_ids={ident for t in TRANSFORMS.values() for ident in t['osm']} | {'way/976405284'} | set(json.loads(Path('build/highrises/replacement-ids.json').read_text())) | set(json.loads(Path('build/south-strip/replacement-ids.json').read_text())) | set(json.loads(Path('build/strip-landmarks/replacement-ids.json').read_text())) | (set(json.loads(Path('build/resort-blocks/cosmo/replacement-ids.json').read_text())) if Path('build/resort-blocks/cosmo/replacement-ids.json').exists() else set()) | (set(json.loads(Path('build/resort-blocks/bellagio/replacement-ids.json').read_text())) if Path('build/resort-blocks/bellagio/replacement-ids.json').exists() else set()) | (set(json.loads(Path('build/resort-blocks/paris/replacement-ids.json').read_text())) if Path('build/resort-blocks/paris/replacement-ids.json').exists() else set())  # Authored assets own shell, entrances and collision.
access=AccessPlanner(SURVEY,roads,cut,replacement_ids)
access.emit(OUT)
county_road,county_walk,county_counts=county_geometry(ROOT,ORIGIN)
county_coverage=county_road.buffer(.5)
print('County pavement / sidewalk records',county_counts,flush=True)
road_polys=[];walk_polys=[];elevated=[];drivegraph=collections.defaultdict(list);marked=[];yellow=[];crossings=[];ramps=[];public=[]
street=StreetBuilder(mesh,phys,polygons,CELL)
intersections=unary_union([Point(positions[n]).buffer(7) for n,ways in nodeways.items() if len([r for r in ways if r['highway'] in DRIVE])>=3])
for r in roads:
 pts=r['points'];line=LineString(pts);h=r.get('heights',[elev[n] for n in r['nodes']])
 if max(h)<.015:
  poly=line.buffer(r['width']/2,cap_style=1,join_style=1,resolution=8)
  if r['highway'] in DRIVE:
   # County pavement supplies real edges; use the OSM buffer where it has no coverage.
   if line.difference(county_coverage).length>line.length*.15:road_polys.append(poly)
   if r['highway'] in PUBLIC:public.append(line.buffer(r['width']/2+14,resolution=6))
   if r['highway']=='service':ramps.append(poly.buffer(1.5))
  else:
   walk_polys.append(poly)
   if r['tags'].get('footway')=='crossing' or r['tags'].get('crossing'):
    crossings.append((line,r['width']));ramps.append(poly.buffer(2))
 elif not r.get('verticalLink'):elevated.append(r)
 if r['highway'] in DRIVE:
  for a,b in zip(r['nodes'],r['nodes'][1:]):
   d=math.dist(positions[a],positions[b]);direction=r['tags'].get('oneway','yes' if r['highway'] in ('motorway','motorway_link') or r['tags'].get('junction')=='roundabout' else 'no')
   if direction!='-1':drivegraph[a].append((b,d,r['id']))
   if direction not in ('yes','1','true'):drivegraph[b].append((a,d,r['id']))
 # Lane stripes are clipped away from intersections below.
 if r['highway'] in {'primary','secondary','tertiary','motorway'} and max(h)<.015 and r['width']>=6:
  try:lanes=max(1,int(r['tags'].get('lanes','2').split(';')[0]))
  except ValueError:lanes=max(1,round(r['width']/3.4))
  oneway=r['tags'].get('oneway') in ('yes','1','true','-1')
  for lane in range(1,lanes):
   offset=-r['width']/2+r['width']*lane/lanes
   strip=line.offset_curve(offset,quad_segs=8)
   if strip.is_empty or strip.geom_type!='LineString':continue
   if not oneway and lane==lanes//2:
    for d in [-.11,.11]:yellow.append(strip.offset_curve(d).buffer(.045,cap_style=2))
   else:
    for distance in np.arange(5,strip.length-4,12):
     a=strip.interpolate(float(distance));b=strip.interpolate(min(float(distance)+4,strip.length));marked.append(LineString([a,b]).buffer(.065,cap_style=2))
print('Road buffers',len(road_polys),len(walk_polys),len(elevated),flush=True)
medians=county_medians(ROOT,ORIGIN)
road_union=unary_union([county_road,*road_polys]).difference(medians).buffer(0)
public_area=unary_union(public)
mapped_walk=unary_union([county_walk,*walk_polys])
sidewalk_fallback=road_union.buffer(2.4,resolution=8).difference(road_union).intersection(public_area)
walk_union=unary_union([mapped_walk,sidewalk_fallback]).difference(road_union).difference(cut.buffer(.2)).difference(medians).buffer(0)
# Public carriageways take precedence over low-detail building outlines, but
# not detailed resort architecture (the placement audit reports any conflict).
blocked=unary_union([road_union.buffer(.3),walk_union])
street.paved_slab(road_union,ROAD_Y,'road')
print('Road surface triangles',sum(len(g['faces']) for g in meshes.values()),flush=True)
street.sidewalks(walk_union,road_union,ramps)
print('Sidewalks complete',street.stats,flush=True)
# Add verges only beside roads without separate mapped sidewalks. This does not
# invent shortcuts through blocks: the OSM pedestrian network stays explicit.
flat(road_union.buffer(3.2,resolution=6).difference(road_union).difference(walk_union).difference(medians),.018,'verge')
flat(road_union.difference(road_union.buffer(-.24)).intersection(public_area),ROAD_Y+.006,'gutter')
flat(unary_union(marked).intersection(road_union).difference(intersections),ROAD_Y+.010,'paint')
flat(unary_union(yellow).intersection(road_union).difference(intersections),ROAD_Y+.011,'yellow-paint')
zebras=[]
for line,width in crossings:
 for d in np.arange(.3,line.length,.9):
  p=line.interpolate(float(d));q=line.interpolate(min(line.length,float(d)+.5));zebras.append(LineString([p,q]).buffer(max(1.2,width/2),cap_style=2))
flat(unary_union(zebras).intersection(road_union),ROAD_Y+.013,'paint')
road_clearance=prep(unary_union([road_union,*[LineString(r['points']).buffer(r['width']/2+1) for r in elevated if r['highway'] in DRIVE]]))
street.indoor=unary_union([access.upper_mask,access.ramp_mask]);street.access_footprint=unary_union([p['void'] for p in access.plans]).buffer(.8)
for r in elevated:street.bridge(r,elev,nodeways,road_clearance,walk_union)
(OUT/'street-details.json').write_text(json.dumps(dict(county=county_counts,**street.stats,bridgeChecks=street.bridge_checks),separators=(',',':')))
# Broad hotel aprons connect the fitted entrances to the actual pedestrian paths.
# Their flat surfaces add no individual collision bodies (shared ground does).
flat(cut.difference(road_union).difference(walk_union),.009,'plaza')

# Vegetation is classified separately from pavement. Large parent hotel
# footprints and the authored arrival areas are excluded so gardens don't
# appear inside buildings or cross their entrances.
building_footprints=unary_union([Polygon([(x,-z) for x,z in p[0]],
 [[(x,-z) for x,z in ring] for ring in p[1:]]).buffer(0)
 for f in SURVEY['buildings'] if f['base']<1 for p in f['polygons']])
landscape_layers,median_curbs,landscape_report=landscape(ROOT,ORIGIN,road_union,walk_union,medians,unary_union([cut,building_footprints]),street,flat)
layers={'road':road_union,'sidewalk':walk_union,'median-curb':median_curbs,**landscape_layers}
(OUT/'surface-layers.geojson').write_text(json.dumps(dict(type='FeatureCollection',features=[
 dict(type='Feature',properties=dict(kind=k),geometry=geojson_mapping(p)) for k,p in layers.items()]),separators=(',',':')))

replacement_ids={ident for t in TRANSFORMS.values() for ident in t['osm']} | {'way/976405284'} | set(json.loads(Path('build/highrises/replacement-ids.json').read_text())) | set(json.loads(Path('build/south-strip/replacement-ids.json').read_text())) | set(json.loads(Path('build/strip-landmarks/replacement-ids.json').read_text())) | (set(json.loads(Path('build/resort-blocks/cosmo/replacement-ids.json').read_text())) if Path('build/resort-blocks/cosmo/replacement-ids.json').exists() else set()) | (set(json.loads(Path('build/resort-blocks/bellagio/replacement-ids.json').read_text())) if Path('build/resort-blocks/bellagio/replacement-ids.json').exists() else set()) | (set(json.loads(Path('build/resort-blocks/paris/replacement-ids.json').read_text())) if Path('build/resort-blocks/paris/replacement-ids.json').exists() else set())  # Authored assets own shell, entrances and collision.
@lru_cache(maxsize=None)
def local_mask(ix,iz):
 tile=box(ix*CELL,iz*CELL,(ix+1)*CELL,(iz+1)*CELL)
 return unary_union([cut.intersection(tile),blocked.intersection(tile)])
def trim_background(shape):
 x0,z0,x1,z1=shape.bounds
 masks=[local_mask(x,z) for x in range(math.floor(x0/CELL),math.floor(x1/CELL)+1) for z in range(math.floor(z0/CELL),math.floor(z1/CELL)+1)]
 return shape.difference(unary_union(masks))
kept=clipped=removed=0;heightcounts=collections.Counter();features=[];building_records=[]
for f in SURVEY['buildings']:
 if f['id'] in replacement_ids:removed+=1;continue
 shape=unary_union([Polygon([(x,-z) for x,z in p[0]],[[(x,-z) for x,z in ring] for ring in p[1:]]).buffer(0) for p in f['polygons']])
 if shape.is_empty:continue
 remaining=trim_background(shape)
 if remaining.is_empty or remaining.area<1:removed+=1;continue
 if remaining.area<shape.area-.2:clipped+=1
 # Parent footprints remain podiums; tall building parts own their silhouette.
 h=f['height'];base=f['base']
 # Named data corrections only where source tagging demonstrably assigns a
 # tower height to its low podium, recorded in this report rather than hidden.
 if f['id']=='way/134795273':h=18
 if f['id']=='way/116867081':h=15
 mat='building-tagged' if f['kind']=='height' else 'building-estimated'
 if f['tags'].get('building') in ('garage','garages','roof','shed'):mat='utility'
 mat=style_material(f['tags'],False,mat)
 building_records.append(dict(f,shape=remaining,height=h,material=mat));heightcounts[f['kind']]+=1;kept+=1
 features.append(dict(id=f['id'],name=f['name'],height=h,heightSource=f['kind'],heightProfile=f.get('heightProfile'),area=round(remaining.area,2)))
building_surfaces=BuildingSurfaces(building_records)
for i,f in enumerate(building_records):
 building_mesh(building_surfaces.shapes[i],f['height'],f['base'],f['material'],f['id'],f['tags'])
(OUT/'building-surfaces-report.json').write_text(json.dumps(building_surfaces.report(),indent=2))
print('Building surface normalization',building_surfaces.report(),flush=True)
# Flat support is continuous over the district. Grade changes are separately
# collidable streamed decks. Terrain elevation is intentionally not invented.
mesh('base','ground',[[-2350,-.02,-4400],[2550,-.02,-4400],[2550,-.02,4300],[-2350,-.02,4300]],[[0,2,1],[0,3,2]])
# Graph proof for an uninterrupted surface route along Las Vegas Boulevard.
blvd={n for r in roads if 'Las Vegas Boulevard' in r['name'] and r['highway'] in DRIVE for n in r['nodes']}
start=min(blvd,key=lambda n:math.dist(positions[n],coord({'lat':36.082,'lon':-115.1728})));end=min(blvd,key=lambda n:math.dist(positions[n],coord({'lat':36.1473,'lon':-115.1569})))
def route(start,end):
 dist={start:0};prev={};q=[(0,start)]
 while q:
  d,n=heapq.heappop(q)
  if d!=dist[n]:continue
  if n==end:break
  for nn,l,w in drivegraph[n]:
   cost=d+l*(1 if nn in blvd else 3)
   if cost<dist.get(nn,1e30):dist[nn]=cost;prev[nn]=(n,w);heapq.heappush(q,(cost,nn))
 if end not in dist:raise RuntimeError('Strip road graph is disconnected')
 out=[];n=end
 while n!=start:out.append(n);n=prev[n][0]
 out.append(start);out.reverse();return out
path=route(start,end);distance=sum(math.dist(positions[a],positions[b]) for a,b in zip(path,path[1:]));route_points=[[positions[n][0],street_y(elev[n]),positions[n][1]] for n in path]
(OUT/'city-materials.json').write_text(json.dumps(styles))
(OUT/'city-meshes.json').write_text(json.dumps(list(meshes.values()),separators=(',',':')))
(OUT/'city-colliders.json').write_text(json.dumps([dict(id=k,center=[(int(k.split(',')[0])+.5)*CELL,(int(k.split(',')[1])+.5)*CELL],**v) for k,v in physics.items()],separators=(',',':')))
(OUT/'road-network.json').write_text(json.dumps(dict(origin=ORIGIN,roads=[dict(id=r['id'],name=r['name'],highway=r['highway'],width=r['width'],points=[[p[0],street_y(h),p[1]] for h,p in zip(r.get('heights',[elev[n] for n in r['nodes']]),r['points'])],nodes=r['nodes'],oneway=r['tags'].get('oneway','no'),access=r['tags'].get('access','public'),bridge=r['bridge']) for r in roads],stripRoute=route_points),separators=(',',':')))
(OUT/'replacements.json').write_text(json.dumps(list(TRANSFORMS.values()),indent=2))
(OUT/'building-index.json').write_text(json.dumps(features,separators=(',',':')))
# Preserve the authored Rialto connection when regenerating the base map,
# including the opening through the adjoining elevated walkway's railing.
if (Path('build/strip-landmarks/venues.json').exists() and (OUT/'bridge-only-colliders.json').exists()):
 import runpy
 runpy.run_path('tools/strip-landmarks/remove_old_rialto.py')
report=dict(source=SURVEY['summary'],buildings=kept,trimmedBuildings=clipped,replacedBuildings=removed,remainingHeightSources=dict(heightcounts),roadWays=len(roads),driveWays=sum(r['highway'] in DRIVE for r in roads),pedestrianWays=sum(r['highway'] in WALK for r in roads),elevatedWays=len(elevated),renderCells=len(meshes),collisionCells=len(physics),triangles=sum(len(g['faces']) for g in meshes.values()),stripRouteMeters=round(distance,1),stripRouteNodes=len(path),notes=['OSM footprints and centerlines are source geometry; road widths use tags then lane count then class defaults.','Layer-based overpass elevation and 6.5% transition grades are approximations, not surveyed elevation.','Parent Horseshoe envelope reduced to a 15 m podium; separate tower parts remain.','Explicitly replaced OSM features are omitted entirely to avoid solid blocks inside detailed models.','Authored detailed resort envelopes are fitted reconstructions, not exact OSM polygon tessellations.'])
(OUT/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k not in ('source','notes')},indent=2))

# The lakefront replacement owns the basin. Reapply its terrain cut after every
# full city rebuild, before compacting collision and exporting the city GLB.
if Path('build/resort-blocks/bellagio/version.json').exists():
 import subprocess
 subprocess.run([sys.executable,'tools/resort-blocks/cut_bellagio_lake.py'],check=True)
