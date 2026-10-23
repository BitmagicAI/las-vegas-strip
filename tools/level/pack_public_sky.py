"""Repack only the Paris sky image after Blender's UV-corrected export.

Appending a buffer view retains every existing geometry/accessor byte offset.
The staged blend holds the same packed image for future complete exports.
"""
from pathlib import Path
import hashlib,json,struct
p=Path('build/hotels/staged-vegas.glb')
raw=p.read_bytes();magic,version,total=struct.unpack_from('<III',raw)
assert magic==0x46546c67 and version==2 and total==len(raw)
n,kind=struct.unpack_from('<II',raw,12);assert kind==0x4e4f534a
doc=json.loads(raw[20:20+n]);start=20+n
n,kind=struct.unpack_from('<II',raw,start);assert kind==0x004e4942
binary=bytearray(raw[start+8:start+8+n]);assert start+8+n==len(raw)
assert len(doc['buffers'])==1 and 'uri' not in doc['buffers'][0]
image=next(im for im in doc['images'] if im.get('name')=='paris-sky')
png=Path('build/public-resorts/textures/paris-sky.png').read_bytes()
view={'buffer':0,'byteOffset':len(binary),'byteLength':len(png)}
doc['bufferViews'].append(view);image['bufferView']=len(doc['bufferViews'])-1;image['mimeType']='image/png'
binary.extend(png);doc['buffers'][0]['byteLength']=len(binary)
binary.extend(b'\0'*((-len(binary))%4))
j=json.dumps(doc,separators=(',',':')).encode();j+=b' '*((-len(j))%4)
out=struct.pack('<III',magic,version,28+len(j)+len(binary))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(binary),0x004e4942)+binary
assert bytes(binary[view['byteOffset']:view['byteOffset']+view['byteLength']])==png
tmp=p.with_suffix('.next.glb');tmp.write_bytes(out);tmp.replace(p)
revision={'revision':hashlib.sha256(out).hexdigest()[:16]}
for target in ['build/hotels/staged-asset-version.json','src/work/hotels/streamed-asset-version.json']:
 Path(target).write_text(json.dumps(revision)+'\n')
print('Repacked local Paris sky:',revision)
