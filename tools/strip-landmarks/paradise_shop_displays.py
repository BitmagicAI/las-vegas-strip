"""Original generic window display artwork. No third-party advertisements."""
from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import random
out=Path('build/strip-landmarks');out.mkdir(parents=True,exist_ok=True)
fontpath=next((p for p in ['/System/Library/Fonts/Supplemental/Arial Bold.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'] if Path(p).exists()),None)
font=ImageFont.truetype(fontpath,12) if fontpath else ImageFont.load_default(size=12)
for n,bg in enumerate(['#687d82','#977567','#89856c']):
 r=random.Random(240+n);im=Image.new('RGB',(512,512),bg);d=ImageDraw.Draw(im)
 for y in range(0,512,128):
  for x in range(0,512,128):
   color=r.choice(['#e6e0cc','#bebda7','#c8cac3']);d.rectangle((x+3,y+3,x+124,y+124),fill=color)
   d.rectangle((x+8,y+8,x+120,y+28),fill=r.choice(['#526a70','#734d4d','#596344']))
   d.text((x+12,y+10),r.choice(['WELCOME','LOCAL SHOP','OPEN DAILY','PARADISE']),font=font,fill='#ece8d5')
   for j in range(5):
    yy=y+35+j*6;d.line((x+12,yy,x+r.randrange(65,116),yy),fill='#5d5d52',width=2)
   d.ellipse((x+40,y+75,x+85,y+115),outline='#83785e',width=4)
   d.line((x+12,y+120,x+112,y+120),fill='#776859',width=2)
 im.save(out/('paradiseShop-display'+str(n)+'-original.png'))
