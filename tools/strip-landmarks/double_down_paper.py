"""Original layered bar ephemera: no copied photographs, logos or band artwork.
Pillow is an offline build dependency. Seeded output is repeatable across builds.
"""
from pathlib import Path
import random
from PIL import Image, ImageDraw, ImageFont

OUT = Path('build/strip-landmarks')

def make(kind):
    rng = random.Random(234 if kind == 'poster' else 235)
    size = 2048
    canvas = Image.new('RGB', (size, size), '#454039')
    words = ['LIVE', 'TONIGHT', 'LOUD', 'NO COVER', 'LAS VEGAS', 'AFTER HOURS', 'FRIDAY', 'SATURDAY', 'STEREO', 'ALL NIGHT']
    palettes = [('#c1b898','#252522'),('#a8a28e','#38382c'),('#a49d91','#252226'),('#923f38','#d9c5a4'),('#293e42','#bcafa0'),('#222324','#c8c1ae')]
    # All edges wrap, so repetition has no artificial straight seam. The 4m tile
    # has differently sized/rotated layers instead of a regular newspaper grid.
    for i in range(370):
        w = rng.randint(75,300); h = rng.randint(70,350)
        paper, ink = rng.choice(palettes)
        if kind == 'ceiling' and i % 3:
            w,h = rng.randint(110,210),rng.randint(48,85)
            paper,ink = '#9c9b7a','#424b3d'
        tile = Image.new('RGBA',(w,h),paper); d = ImageDraw.Draw(tile)
        d.rectangle((5,5,w-6,h-6),outline=ink,width=2)
        font = ImageFont.load_default(size=max(12,int(w*.13)))
        if kind == 'ceiling' and i % 3:
            # Fictional souvenir notes: ornamental oval and numerals, no currency scan.
            d.ellipse((w*.35,9,w*.65,h-10),outline=ink,width=3)
            d.text((10,h*.25),'LV',font=font,fill=ink)
            d.text((w*.77,h*.25),'01',font=font,fill=ink)
            for yy in range(12,h-10,5):
                d.line((w*.16,yy,w*.30,yy),fill=ink)
                d.line((w*.69,yy,w*.75,yy),fill=ink)
        else:
            word=rng.choice(words)
            d.text((w*.08,h*.08),word,font=font,fill=ink)
            cy=h*.47; r=min(w,h)*.23
            if i%3==0:
                d.ellipse((w/2-r,cy-r,w/2+r,cy+r),outline=ink,width=4)
                d.line((w*.2,cy+r,w*.8,cy-r),fill=ink,width=5)
            elif i%3==1:
                d.polygon([(w*.2,cy+r),(w*.42,cy-r),(w*.52,cy),(w*.8,cy-r),(w*.65,cy+r)],fill=ink)
            else:
                for q in range(5):
                    xx=w*.18+q*w*.14
                    d.rectangle((xx,cy-r,xx+w*.07,cy+r),fill=ink)
            for yy in range(int(h*.78),h-10,8):
                d.line((w*.1,yy,w*rng.uniform(.65,.9),yy),fill=ink,width=2)
        tile=tile.rotate(rng.uniform(-32,32),resample=Image.Resampling.BICUBIC,expand=True)
        x,y=rng.randrange(size),rng.randrange(size)
        for dx in [-size,0]:
            for dy in [-size,0]:canvas.paste(tile,(x+dx,y+dy),tile)
    OUT.mkdir(parents=True,exist_ok=True)
    canvas.save(OUT/f'doubleDown-{kind}-original.png')

if __name__ == '__main__':
    make('poster'); make('ceiling')
