"""Keep retained distant tree cards byte-exact through Blender re-export.
Blender can renormalize/reorder their imported attributes. This scoped helper
copies only existing LOD2 tree mesh accessors; transforms and new palms are untouched.
"""
import copy,json,struct

def preserve_cards(before,after):
 def read(raw):
  n=struct.unpack_from('<I',raw,12)[0]
  return json.loads(raw[20:20+n]),raw[28+n:]
 old,ob=read(before);new,nb=read(after);data=bytearray(nb)
 oldnodes={n.get('name'):n for n in old['nodes']}
 materials={m['name']:i for i,m in enumerate(new['materials'])}
 views={};accessors={};meshes={}
 def view(i):
  if i not in views:
   v=copy.deepcopy(old['bufferViews'][i]);assert v.get('buffer',0)==0
   data.extend(b'\0'*((-len(data))%4));offset=len(data)
   start=v.get('byteOffset',0);data.extend(ob[start:start+v['byteLength']])
   v['byteOffset']=offset;v['buffer']=0;views[i]=len(new['bufferViews']);new['bufferViews'].append(v)
  return views[i]
 def accessor(i):
  if i not in accessors:
   a=copy.deepcopy(old['accessors'][i]);assert 'sparse' not in a
   a['bufferView']=view(a['bufferView']);accessors[i]=len(new['accessors']);new['accessors'].append(a)
  return accessors[i]
 count=0
 for node in new['nodes']:
  name=node.get('name','')
  if not name.startswith('Flamingo garden tree ') or '/2/' not in name:continue
  prior=oldnodes.get(name)
  if prior is None:continue
  assert all(node.get(k)==prior.get(k) for k in ['matrix','translation','rotation','scale','extras'])
  i=prior['mesh']
  if i not in meshes:
   m=copy.deepcopy(old['meshes'][i])
   for p in m['primitives']:
    assert 'extensions' not in p and 'targets' not in p
    p['indices']=accessor(p['indices']);p['attributes']={k:accessor(v)for k,v in p['attributes'].items()}
    p['material']=materials[old['materials'][p['material']]['name']]
   meshes[i]=len(new['meshes']);new['meshes'].append(m)
  node['mesh']=meshes[i];count+=1
 new['buffers'][0]['byteLength']=len(data);data.extend(b'\0'*((-len(data))%4))
 j=json.dumps(new,separators=(',',':')).encode();j+=b' '*((-len(j))%4)
 result=struct.pack('<III',0x46546c67,2,28+len(j)+len(data))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(data),0x004e4942)+data
 return result,count
