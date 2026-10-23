"""Original stylized incised ornament, not a transcription or photo texture."""
from PIL import Image,ImageDraw,ImageFilter
import numpy as np
from pathlib import Path
W,H=768,3072
mask=Image.new('L',(W,H),0);d=ImageDraw.Draw(mask)
for row in range(48):
 for col in range(5):
  x=60+col*132;y=20+row*63;w=113;h=49
  def line(ps):d.line([(x+a*w,y+b*h)for a,b in ps],fill=220,width=3,joint='curve')
  def oval(a,b,c,e):d.ellipse((x+a*w,y+b*h,x+c*w,y+e*h),outline=220,width=3)
  k=(row*5+col*3)%8
  if k==0:
   oval(.34,.05,.62,.42);line([(.48,.42),(.48,.95)]);line([(.18,.58),(.78,.58)])
  elif k==1:
   line([(.1,.65),(.25,.42),(.52,.36),(.85,.60),(.65,.76),(.35,.77),(.1,.65)]);oval(.42,.48,.59,.70);line([(.65,.76),(.8,.95)]);line([(.35,.77),(.28,.94)])
  elif k==2:
   line([(.12,.75),(.25,.3),(.45,.2),(.65,.35),(.90,.25),(.75,.5),(.55,.55),(.72,.82),(.4,.84),(.12,.75)]);line([(.4,.84),(.3,.98)]);line([(.65,.84),(.6,.98)])
  elif k==3:
   for yy in [.25,.5,.75]:line([(.05,yy),(.2,yy-.15),(.35,yy),(.5,yy-.15),(.65,yy),(.8,yy-.15),(.95,yy)])
  elif k==4:
   oval(.35,.02,.55,.27);line([(.45,.27),(.44,.64),(.22,.95)]);line([(.44,.64),(.70,.95)]);line([(.45,.36),(.2,.50),(.1,.2)]);line([(.45,.36),(.7,.50),(.85,.25)])
  elif k==5:
   line([(.1,.95),(.45,.05),(.9,.95),(.1,.95)]);line([(.45,.05),(.45,.95)])
  elif k==6:
   d.rounded_rectangle((x+20,y+3,x+w-20,y+h-3),radius=12,outline=220,width=3)
   line([(.35,.25),(.65,.25),(.65,.75),(.35,.75),(.35,.25)]);oval(.43,.4,.57,.6)
  else:
   for xx in [.25,.5,.75]:line([(xx,.95),(xx,.1),(xx-.1,.25),(xx+.1,.4),(xx,.55)])
 # Fine horizontal dividers and three inscribed columns.
 d.line((68,y+h+7,W-68,y+h+7),fill=110,width=2)
mask=mask.filter(ImageFilter.GaussianBlur(1))
a=np.asarray(mask,dtype=np.float32)/255
rng=np.random.default_rng(722);noise=rng.normal(0,1.8,(H,W));base=np.zeros((H,W,3),dtype=np.uint8)
for i,c in enumerate([191,183,158]):base[:,:,i]=np.clip(c+noise-a*23,0,255)
height=1-a*.5;dy,dx=np.gradient(height);normal=np.stack([-dx*3,dy*3,np.ones_like(dx)],axis=2);normal/=np.linalg.norm(normal,axis=2,keepdims=True)
p=Path('build/strip-landmarks/textures');p.mkdir(exist_ok=True)
Image.fromarray(base).save(p/'luxor-obelisk-original-stone.png')
Image.fromarray(np.uint8((normal*.5+.5)*255)).save(p/'luxor-obelisk-original-normal.png')
