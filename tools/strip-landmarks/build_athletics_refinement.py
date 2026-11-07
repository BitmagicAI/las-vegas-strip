"""Scoped construction equipment pass; inherited collision must stay byte-identical."""
from common import *
import athletics_stadium
key=athletics_stadium.KEY
collision=OUT/(key+'-exterior-collision.json');before=collision.read_bytes()
B=Meshes();athletics_stadium.exterior(B)
for label in B.labels:label['detail']=0
B.save_all()
changed=collision.read_bytes()!=before
if changed:collision.write_bytes(before)
assert not changed,'Inherited collision changed; restored'
print(key,sum(len(g['faces']) for g in B.groups.values()),'faces; collision byte-identical')
