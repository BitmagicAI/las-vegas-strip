"""Original, seamless architectural textures drawn from the reference palette."""
from PIL import Image,ImageDraw,ImageFilter
from pathlib import Path
import random,math,sys
OUT=Path('build/public-resorts/textures');OUT.mkdir(parents=True,exist_ok=True)
palettes={
 'bellagio':('#251714',['#af884c','#6e4930','#b7a272']),
 'paris':('#233344',['#8f8974','#a38351','#56788c']),
 'caesars':('#322624',['#bbaa82','#746b5b','#897453']),
 'flamingo':('#3a253d',['#ba5487','#977499','#5b475f','#ba9a64']),
 'horseshoe':('#322923',['#ae9470','#d2be96','#6d5041']),
 'planet-hollywood':('#262536',['#756675','#a15c62','#bd9169','#505573']),
 'aria':('#302b27',['#a98c5b','#807661','#d2b078']),
}
for key,(bg,colors) in palettes.items():
 if '--sky-only' in sys.argv:continue
 im=Image.new('RGB',(1024,1024),bg);d=ImageDraw.Draw(im);rng=random.Random(key)
 if key in ['horseshoe','aria','caesars']:
  for i in range(26):
   x=rng.randrange(1024);y=rng.randrange(1024);rx=rng.randrange(55,210);ry=rng.randrange(45,175)
   for dx in [-1024,0,1024]:
    for dy in [-1024,0,1024]:
     for j in range(3):d.arc((x-rx+j*13+dx,y-ry+j*10+dy,x+rx-j*13+dx,y+ry-j*10+dy),rng.randrange(30),320,fill=colors[i%len(colors)],width=4)
 else:
  for i in range(200):
   x=rng.randrange(1024);y=rng.randrange(1024);r=rng.randrange(12,45);a=rng.random()*math.tau
   pts=[(x+math.cos(a+t)*r,y+math.sin(a+t)*r*.5) for t in [j*math.tau/8 for j in range(8)]]
   for dx in [-1024,0,1024]:
    for dy in [-1024,0,1024]:d.polygon([(xx+dx,yy+dy) for xx,yy in pts],fill=colors[i%len(colors)])
 # Fine woven grain, deterministic and baked so no expensive runtime noise.
 pix=im.load()
 for y in range(1024):
  for x in range(1024):
   v=rng.randint(-7,7)+(2 if (x+y)%3==0 else 0);pix[x,y]=tuple(max(0,min(255,c+v)) for c in pix[x,y])
 im.save(OUT/(key+'-carpet.png'))
# Original sky mural, broad hand-painted cloud-like fields; no photo redistribution.
im=Image.new('RGB',(1024,1024));p=im.load()
for y in range(1024):
 for x in range(1024):
  # Integer-frequency waves wrap exactly at the image boundary. Broad mural
  # patches must not expose a square seam when seen from the casino floor.
  a=x*math.tau/1024;b=y*math.tau/1024
  v=math.sin(a+.7*math.sin(2*b))*math.cos(b)+.35*math.sin(3*a-2*b)+.12*math.sin(7*a+3*b)
  v=max(0,min(1,(v+.12)/1.15));v=v*v*(3-2*v)
  p[x,y]=(int(103+142*v),int(151+94*v),int(178+64*v))
tiled=Image.new('RGB',(3072,3072))
for x in range(3):
 for y in range(3):tiled.paste(im,(x*1024,y*1024))
tiled.filter(ImageFilter.GaussianBlur(10)).crop((1024,1024,2048,2048)).save(OUT/'paris-sky.png')
