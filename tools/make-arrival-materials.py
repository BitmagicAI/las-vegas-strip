"""Original architectural material maps, deterministic and seamless."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import random,math
out=Path('build/arrival-reconstruction/textures');out.mkdir(parents=True,exist_ok=True)
N=1024
for name,base in [('marble',(207,201,189)),('stone',(165,158,144)),('wood',(91,52,30)),('granite',(25,31,33))]:
 rng=random.Random(name);im=Image.new('RGB',(N,N));pix=im.load()
 for y in range(N):
  for x in range(N):
   a=x*math.tau/N;b=y*math.tau/N
   if name=='wood':v=5*math.sin(a*28+1.3*math.sin(b)+.5*math.sin(b*3))+3*math.sin(a*83+2*math.sin(b))+rng.uniform(-2,2)
   elif name=='granite':v=rng.gauss(0,2)+2*math.sin(a*2+b)
   else:v=2.0*math.sin(a+1.5*math.sin(b))+1.5*math.sin(a*4+b*3)+rng.gauss(0,.7)
   pix[x,y]=tuple(max(0,min(255,int(c+v))) for c in base)
 if name=='marble':
  veins=Image.new('RGBA',(N,N));d=ImageDraw.Draw(veins)
  for i in range(11):
   x=rng.uniform(-N,N);y=rng.uniform(-N,N);pts=[]
   for j in range(120):pts.append((x+j*10,y+j*6+18*math.sin(j*.16)+5*math.sin(j*.62)))
   for dx in [-N,0,N]:
    for dy in [-N,0,N]:
     d.line([(xx+dx,yy+dy) for xx,yy in pts],fill=(116,110,102,40),width=2 if i%3 else 4)
  veins=veins.filter(ImageFilter.GaussianBlur(.6));im=Image.alpha_composite(im.convert('RGBA'),veins).convert('RGB')
 im.save(out/(name+'.png'))
print('Created four original 1024px surface maps')
