"""Remove only the two mapped footways now owned by the Venetian reconstruction.
The collider provenance supplies exact triangle footprints. No road/county geometry
is regenerated. --glb also patches the existing raw GLB's index buffers in place.
"""
import sys,json,struct,shutil,math
from pathlib import Path
sys.path.insert(0,'build/south-strip/python')
import numpy as np
from shapely.geometry import LineString,Point
from shapely.ops import unary_union
from shapely.prepared import prep
origin=json.load(open('build/strip-survey/survey.json'))['summary']['origin']
raw=json.load(open('build/strip-survey/osm.json'))
lines=[]
for e in raw['elements']:
 if e['id'] in (1352089771,543728952):
  lines.append(LineString([(6378137*math.radians(p['lon']-origin[0])*math.cos(math.radians(origin[1])),-6378137*math.radians(p['lat']-origin[1])) for p in e['geometry']]))
# Swept fixtures (round tubes and luminous strips) have no one-to-one collider
# triangles. Clip their centroids only within these two source-owned corridors.
owned=prep(unary_union([line.buffer(2.25) for line in lines]))
def fixture(pts):
 x=sum(p[0] for p in pts)/3;z=sum(p[2] for p in pts)/3
 return 168<x<229 and -696<z<-607 and max(p[1] for p in pts)>.4 and owned.contains(Point(x,z))

OUT=Path('build/geographic-strip')
IDS=('1352089771/','543728952/')
def key(pts):return tuple(sorted((round(float(p[0]),2),round(float(p[2]),2)) for p in pts))
keys={}
for c in json.loads((OUT/'bridge-only-colliders.json').read_text()):
 if not c['id'].startswith(IDS):continue
 mat=c['id'].split('/')[-1];v=np.array(c['vertices']).reshape(-1,3);idx=np.array(c['indices']).reshape(-1,3)
 keys.setdefault(mat,set()).update(key(v[t]) for t in idx)
allkeys=set().union(*keys.values())
def remove_json():
 data=json.loads((OUT/'city-meshes.json').read_text());removed=0
 for g in data:
  if not g['material'].startswith('bridge-'):continue
  old=g['faces'];v=g['vertices'];g['faces']=[f for f in old if key([v[i] for i in f]) not in keys.get(g['material'],set()) and not fixture([v[i] for i in f])];removed+=len(old)-len(g['faces'])
 (OUT/'city-meshes.json').write_text(json.dumps(data,separators=(',',':')))
 cells=json.loads((OUT/'city-colliders.json').read_text());removed_c=0
 for c in cells:
  cx,cz=c['center']
  if not 0<cx<400 or not -900<cz<-400:continue
  v=np.array(c['vertices']).reshape(-1,3);idx=c['indices'];keep=[]
  for i in range(0,len(idx),3):
   t=idx[i:i+3]
   if key(v[t]) in allkeys:removed_c+=1
   else:keep.extend(t)
  c['indices']=keep
 (OUT/'city-colliders.json').write_text(json.dumps(cells,separators=(',',':')))
 print('Removed legacy Venetian footways:',removed,'visual triangles;',removed_c,'collision triangles')
def patch_glb():
 sys.path.insert(0,'tools/film');from clearance import node_matrix,CT,NC
 path=OUT/'city.glb';raw=path.read_bytes();n=struct.unpack_from('<I',raw,12)[0];j=json.loads(raw[20:20+n]);off=20+n;n2=struct.unpack_from('<I',raw,off)[0];blob=bytearray(raw[off+8:off+8+n2]);removed=0;changed=0
 def acc(i):
  a=j['accessors'][i];v=j['bufferViews'][a['bufferView']];dt=np.dtype(CT[a['componentType']]);nc=NC[a['type']];offset=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',dt.itemsize*nc)
  return np.ndarray((a['count'],nc),dt,buffer=blob,offset=offset,strides=(stride,dt.itemsize)).copy()
 def walk(i,parent):
  nonlocal removed,changed
  node=j['nodes'][i];M=parent@node_matrix(node)
  if 'mesh' in node:
   for p in j['meshes'][node['mesh']]['primitives']:
    name=j['materials'][p['material']].get('name','').split(' / ')[-1]
    if not name.startswith('bridge-'):continue
    pos=acc(p['attributes']['POSITION']);pos=pos@M[:3,:3].T+M[:3,3];idx=acc(p['indices']).reshape(-1,3)
    keep=np.array([key(pos[t]) not in keys.get(name,set()) and not fixture(pos[t]) for t in idx]);count=int((~keep).sum())
    if not count:continue
    # A primitive must keep its other, unrelated city footbridges.
    ix=idx[keep].astype('<u4').ravel();assert len(ix)>0
    offset=len(blob);blob.extend(ix.tobytes());view=len(j['bufferViews']);j['bufferViews'].append(dict(buffer=0,byteOffset=offset,byteLength=ix.nbytes,target=34963));p['indices']=len(j['accessors']);j['accessors'].append(dict(bufferView=view,componentType=5125,count=len(ix),type='SCALAR',min=[int(ix.min())],max=[int(ix.max())]));removed+=count;changed+=1
  for c in node.get('children',[]):walk(c,M)
 for scene in j['scenes']:
  for n in scene['nodes']:walk(n,np.eye(4))
 if changed:
  j['buffers'][0]['byteLength']=len(blob);js=json.dumps(j,separators=(',',':')).encode();js+=b' '*((-len(js))%4);blob+=b'\0'*((-len(blob))%4)
  tmp=path.with_suffix('.patch.glb');tmp.write_bytes(struct.pack('<III',0x46546c67,2,28+len(js)+len(blob))+struct.pack('<II',len(js),0x4e4f534a)+js+struct.pack('<II',len(blob),0x004e4942)+blob);tmp.replace(path)
 print('Raw city GLB:',removed,'target triangles removed in',changed,'primitives; other buffers preserved')
if __name__=='__main__':
 remove_json()
 if '--glb' in sys.argv:patch_glb()
