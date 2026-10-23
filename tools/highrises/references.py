import json,concurrent.futures,urllib.request
from pathlib import Path
from PIL import Image,ImageDraw
p=Path('build/highrises/references');data=json.loads((p/'search.json').read_text())
def get(item):
 n,i,r=item;dest=p/(n.replace(' ','-')+f'-{i}.jpg')
 try:
  if not dest.exists():
   req=urllib.request.Request(r['url'],headers={'User-Agent':'Mozilla/5.0'})
   raw=urllib.request.urlopen(req,timeout=20).read();dest.write_bytes(raw)
  im=Image.open(dest);im.thumbnail((400,230));return n,i,im.copy()
 except Exception as e:return n,i,None
jobs=[(n,i,r) for n,rs in data.items() for i,r in enumerate(rs) if r['url']]
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:results=list(ex.map(get,jobs))
for start in range(0,len(data),8):
 names=list(data)[start:start+8];sheet=Image.new('RGB',(1200,8*255),'#20252a');d=ImageDraw.Draw(sheet)
 for y,n in enumerate(names):
  for nn,i,im in results:
   if nn==n and im:sheet.paste(im,(i*400,y*255+22))
  d.text((10,y*255+4),n,fill='white')
 sheet.save(p/f'contact-{start//8}.jpg')
print('Downloaded',sum(im is not None for _,_,im in results),'of',len(jobs))
