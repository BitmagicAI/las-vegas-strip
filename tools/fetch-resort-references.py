"""Research-only reference boards; photographs are never shipped as game assets."""
import json,urllib.request,concurrent.futures
from pathlib import Path
from PIL import Image,ImageDraw
out=Path('build/hotels/resort-expansion');refs=json.loads((out/'references.json').read_text())
for row in refs:
 if row[0]=='vdara':row[2]='https://www.protocolsnow.com/wp-content/images/100116_vdara/hallway.jpg'
 if row[0]=='planet-hollywood':
  row[1]='https://lasvegasthenandnow.com/ultra-hip-room-review-planet-hollywood-las-vegas/'
  row[2]='https://milestomemories.com/wp-content/uploads/2018/12/Planet-Hollywood-1.jpg'
  row[3]='https://lasvegasthenandnow.com/wp-content/uploads/2024/01/Ultra-Hip-2-Queen-Beds-Planet-Hollywood-Las-Vegas-2048x1536.jpg'
(out/'references.json').write_text(json.dumps(refs,indent=2))
def download(item):
 key,kind,url=item;p=out/(key+'-'+kind+'.jpg')
 try:
  if not p.exists():
   req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
   data=urllib.request.urlopen(req,timeout=35).read();p.write_bytes(data)
  im=Image.open(p);im.load();return key,kind,'ok'
 except Exception as e:return key,kind,str(e)
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
 for result in pool.map(download,[(r[0],k,r[i]) for r in refs for i,k in [(2,'hall'),(3,'room')] if r[i]]):print(result,flush=True)
for kind in ['hall','room']:
 board=Image.new('RGB',(1440,1080),'#1c2025');d=ImageDraw.Draw(board)
 for i,r in enumerate(refs):
  x=(i%3)*480;y=(i//3)*360
  try:
   im=Image.open(out/(r[0]+'-'+kind+'.jpg')).convert('RGB');im.thumbnail((475,326));board.paste(im,(x,y+30))
  except:pass
  d.text((x+10,y+8),r[0]+' '+kind,fill='white')
 board.save(out/('reference-'+kind+'.jpg'))
