"""Create a local, attributed OSM massing survey; never modifies the game world."""
import collections,json,math,re
from pathlib import Path
from heights import estimated_height
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'build/strip-survey'
d=json.loads((OUT/'osm.json').read_text())
BBOX=[36.079,-115.193,36.153,-115.147]
ORIGIN=[-115.173,36.116]
R=6378137

def xy(p):
 return [round(R*math.radians(p['lon']-ORIGIN[0])*math.cos(math.radians(ORIGIN[1])),3),round(R*math.radians(p['lat']-ORIGIN[1]),3)]

def numeric(v):
 if not v:return None
 v=str(v).strip();m=re.fullmatch(r'([\d.]+)\s*(m|ft|feet|\')?',v)
 if not m:return None
 return float(m[1])*(.3048 if m[2] in ('ft','feet',"'") else 1)

def join_rings(members):
 chains=[m['geometry'][:] for m in members if m['type']=='way' and m.get('geometry')]
 rings=[]
 while chains:
  line=chains.pop()
  while line[0]!=line[-1]:
   found=False
   for i,c in enumerate(chains):
    if line[-1]==c[0]:line.extend(c[1:])
    elif line[-1]==c[-1]:line.extend(c[-2::-1])
    elif line[0]==c[-1]:line=c[:-1]+line
    elif line[0]==c[0]:line=c[:0:-1]+line
    else:continue
    chains.pop(i);found=True;break
   if not found:break
  if len(line)>3 and line[0]==line[-1]:rings.append([xy(p) for p in line])
 return rings

def inside(p,ring):
 x,y=p;flag=False
 for a,b in zip(ring,ring[1:]):
  if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:flag=not flag
 return flag

els=d['elements'];raw=[e for e in els if 'building'in e.get('tags',{}) or 'building:part'in e.get('tags',{})]
# Relation outlines replace their member ways, avoiding duplicate roofs.
relations=[e for e in raw if e['type']=='relation' and e['tags'].get('type')=='multipolygon']
member_ids={m['ref'] for e in relations for m in e.get('members',[]) if m['type']=='way'}
features=[];skipped=[]
for e in raw:
 if e['type']=='way' and e['id'] in member_ids:continue
 if e['type']=='way':
  g=e.get('geometry',[]);polys=[[[xy(p) for p in g]]] if len(g)>3 and g[0]==g[-1] else []
 elif e in relations:
  outer=join_rings([m for m in e['members'] if m.get('role') in ('outer','')]);holes=join_rings([m for m in e['members'] if m.get('role')=='inner'])
  polys=[[ring]+[h for h in holes if inside(h[0],ring)] for ring in outer]
 else:polys=[]
 if not polys:skipped.append(f"{e['type']}/{e['id']}");continue
 t=e['tags'];h=numeric(t.get('height'));levels=numeric(t.get('building:levels'));kind='height' if h is not None else 'levels' if levels is not None else 'unknown'
 base=numeric(t.get('min_height'))
 if base is None:base=(numeric(t.get('building:min_level')) or 0)*3
 estimate,profile=estimated_height(t,levels,base)
 h=h if h is not None else estimate
 # Invalid elevations are kept in the report, not silently drawn upside-down.
 if not 0<=base<h<=1000:skipped.append(f"{e['type']}/{e['id']}: invalid height {base}/{h}");continue
 points=[p for poly in polys for ring in poly for p in ring];center=[sum(p[i] for p in points)/len(points) for i in (0,1)]
 features.append({'id':f"{e['type']}/{e['id']}",'name':t.get('name',t.get('building:part','Unnamed building')),'kind':kind,'height':h,'heightProfile':profile if kind!='height' else None,'base':base,'part':'building:part'in t,'polygons':polys,'center':center,'tags':t})
roads=[]
for e in els:
 t=e.get('tags',{})
 if e['type']!='way' or 'highway'not in t or t['highway'] in ('construction','proposed'):continue
 points=e.get('geometry',[]);segments=[];line=[]
 for p in points:
  if BBOX[0]<=p['lat']<=BBOX[2] and BBOX[1]<=p['lon']<=BBOX[3]:line.append(xy(p))
  else:
   if len(line)>1:segments.append(line)
   line=[]
 if len(line)>1:segments.append(line)
 for line in segments:roads.append({'class':t['highway'],'name':t.get('name',''),'points':line})
counts=collections.Counter(f['kind'] for f in features)
summary={'source':'OpenStreetMap via Overpass API','sourceURL':'https://www.openstreetmap.org/copyright','timestamp':d['osm3s']['timestamp_osm_base'],'bbox':BBOX,'origin':ORIGIN,'projection':'local equirectangular meters; east/north axes; flat datum; no terrain','rawBuildingRecords':len(raw),'renderedBuildingFeatures':len(features),'heightSource':dict(counts),'buildingParts':sum(f['part'] for f in features),'roadSegments':len(roads),'skipped':skipped,'notes':['Height tags are recorded values, not independently verified measurements.','Estimated ground storeys: residential 4.5 m, commercial 6 m, unclassified 5 m, utility 3 m, shelters 3.5 m; each additional tagged floor adds 3 m. Unknown floor counts assume one storey. Explicit height tags are unchanged.','Roof shapes, Veer lean, facade textures and terrain are not reconstructed in this coverage preview.','Building outlines and their overlapping parts may both be visible; raw OSM semantics require normalization for game integration.','Source freshness is the extract timestamp, not proof that every feature matches current conditions.']}
(OUT/'survey.json').write_text(json.dumps({'summary':summary,'buildings':features,'roads':roads},separators=(',',':')))
(OUT/'summary.json').write_text(json.dumps(summary,indent=2))
print(json.dumps({k:v for k,v in summary.items() if k not in ('skipped','notes')},indent=2));print('skipped',len(skipped))
