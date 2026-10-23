"""Remove the old Arc accidentally classified into Eiffel's exterior material batches.
Only the isolated old Arc envelope south of the Eiffel base is affected. Existing
interior batches and the Eiffel structure/ride are untouched. Repeated runs safe.
"""
import json,struct
from pathlib import Path
p=Path('build/geographic-strip/detailed.glb');raw=p.read_bytes();n=struct.unpack_from('<I',raw,12)[0];j=json.loads(raw[20:20+n]);tail=bytearray(raw[20+n:]);removed=0
fmt={5123:'H',5125:'I',5126:'f'};size={5123:2,5125:4,5126:4}
def read(aid,components):
 a=j['accessors'][aid];v=j['bufferViews'][a['bufferView']];kind=a['componentType'];stride=v.get('byteStride',size[kind]*components);off=8+v.get('byteOffset',0)+a.get('byteOffset',0)
 return [struct.unpack_from('<'+fmt[kind]*components,tail,off+i*stride) for i in range(a['count'])],off,kind
for node in j['nodes']:
 e=node.get('extras',{})
 if e.get('geographicOwner')!='eiffel' or e.get('visibilityKind')!='outside' or 'mesh' not in node:continue
 for primitive in j['meshes'][node['mesh']]['primitives']:
  vs,_,_=read(primitive['attributes']['POSITION'],3);ix,off,kind=read(primitive['indices'],1);ix=[v[0] for v in ix];keep=[]
  for k in range(0,len(ix),3):
   ids=ix[k:k+3]
   if all(60<=vs[i][0]<=100 and vs[i][1]<40 and 433<=vs[i][2]<=475 for i in ids):removed+=1
   else:keep.extend(ids)
  if not keep:node.pop('mesh',None);continue
  struct.pack_into('<'+fmt[kind]*len(keep),tail,off,*keep);j['accessors'][primitive['indices']]['count']=len(keep)
s=json.dumps(j,separators=(',',':')).encode();s+=b' '*((-len(s))%4)
p.write_bytes(struct.pack('<III',0x46546c67,2,20+len(s)+len(tail))+struct.pack('<II',len(s),0x4e4f534a)+s+tail)
print('Removed misclassified old Arc triangles:',removed)
