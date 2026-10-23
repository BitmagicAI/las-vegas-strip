"""Original, seamless Sphere-style video content. No third-party footage/assets."""
import numpy as np, subprocess, math, json
from pathlib import Path
from PIL import Image
OUT=Path('build/sphere');OUT.mkdir(exist_ok=True)
W,H,FPS,SECONDS=2048,1024,24,24
u=np.linspace(-np.pi,np.pi,W,endpoint=False,dtype=np.float32)[None,:]
v=np.linspace(np.pi/2,-np.pi/2,H,dtype=np.float32)[:,None]
x=np.cos(v)*np.sin(u);y=np.sin(v)+np.zeros_like(u);z=np.cos(v)*np.cos(u)
# Spatial patterns on the sphere wrap at the longitude seam.
noise=sum(np.sin((x*7.1+y*3.3+z*5.7)*k+np.cos(z*4.2*k-y*5.1*k))*a for k,a in [(1,.5),(2,.25),(4,.13),(8,.07),(16,.03)])
led=np.ones((H,W),np.float32);led[::4,:]*=.92;led[:,::4]*=.92

def eye(t):
    # Two opposing eyes make the animation readable around the skyline.
    lon=np.angle(np.exp(1j*(u+2.1-.10*np.sin(t*2*np.pi/SECONDS))))
    lon=np.where(abs(lon)>np.pi/2,np.angle(np.exp(1j*(lon-np.pi))),lon)
    xx=lon*np.cos(v);yy=v-.12-.045*np.cos(t*2*np.pi/SECONDS)
    r=np.sqrt(xx*xx+yy*yy);a=np.arctan2(yy,xx)
    iris=np.clip((.36-r)*90,0,1);pupil=np.clip((.12+.013*np.sin(t*2*np.pi/SECONDS)-r)*110,0,1)
    fibres=.5+.5*np.sin(a*155+np.sin(a*29)*3+r*40+noise*6)
    glow=np.exp(-((r-.25)/.075)**2)
    base=np.stack([.58+.10*noise+np.zeros_like(xx),.63+.10*noise+np.zeros_like(xx),.68+.10*noise+np.zeros_like(xx)],-1)
    iriscol=np.stack([.02+fibres*.10+glow*.08,.10+fibres*.35+glow*.30,.16+fibres*.55+glow*.27],-1)
    c=base*(1-iris[...,None])+iriscol*iris[...,None]
    c=c*(1-pupil[...,None])+.004*pupil[...,None]
    shine=np.exp(-((xx+.085)**2+(yy-.12)**2)/.0015)*iris
    c+=shine[...,None]*.65
    # Gentle lid blink, once per eye segment (no strobing).
    blink=np.exp(-((t-4.8)/.16)**2)
    aperture=.50*(1-blink)+.015
    lid=np.clip((abs(yy)+.18*xx*xx-aperture)*40,0,1)
    c=c*(1-lid[...,None])+np.array([.035,.095,.15])*lid[...,None]
    return c

def planet(t):
    terrain=noise+.10*np.sin(x*9+z*8+t*.16)
    land=np.clip((terrain-.04)*13,0,1)
    ocean=np.stack([.025+0*x,.11+0*x,.23+0*x],-1)
    earth=np.stack([.10+terrain*.09,.24+terrain*.18,.13+terrain*.08],-1)
    c=ocean*(1-land[...,None])+earth*land[...,None]
    clouds=np.clip(np.sin(x*10+z*6+t*.19+noise*5)*.4+np.cos(y*14-z*11+t*.13)*.25-.35,0,1)*.85
    c=c*(1-clouds[...,None])+np.array([.82,.89,.94])*clouds[...,None]
    ice=np.clip((abs(y)-.83)*7,0,1);c=c*(1-ice[...,None])+ice[...,None]*.72
    return c*(.63+.37*np.clip(x*-.6+y*.6-z*.6,0,1))[...,None]

def ribbons(t):
    phase=t*2*np.pi/SECONDS
    q=np.sin(4*u+2.2*np.sin(3*v+phase)+phase)+np.cos(3*v-2*phase)
    q2=np.sin(3*u-5*v+2*phase)
    c=np.stack([.08+.58*np.exp(-(q-.7)**2*8),.05+.60*np.exp(-(q+.4)**2*4),.18+.70*np.exp(-(q2)**2*6)],-1)
    return c

def interior(t):
    phase=t*2*np.pi/SECONDS
    # A continuous astronomical panorama with slowly flowing aurora.
    wave=np.sin(u*4+phase+np.sin(v*4-phase))*.17
    aur=np.exp(-((v-.25-wave)/.15)**2)
    stars=(np.sin(x*840+y*552+z*974)*np.sin(z*791-y*638+x*711)>.997).astype(np.float32)
    horizon=np.exp(-((v+.60)/.05)**2)
    return np.stack([.004+aur*.08+stars*.6+horizon*.10,.01+aur*.45+stars*.65+horizon*.30,.035+aur*.55+stars*.75+horizon*.55],-1)

def encode(name,fn):
    enc=subprocess.Popen(['ffmpeg','-y','-hide_banner','-loglevel','error','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{W}x{H}','-framerate',str(FPS),'-i','-','-an','-c:v','libx264','-preset','fast','-crf','21','-pix_fmt','yuv420p','-movflags','+faststart',str(OUT/(name+'.mp4'))],stdin=subprocess.PIPE)
    for i in range(FPS*SECONDS):
        c=fn(i/FPS);frame=(np.clip(c*(led[...,None] if name=='exosphere' else 1)*1.3,0,1)*255).astype(np.uint8)
        if i==0:Image.fromarray(frame).save(OUT/(name+'-poster.jpg'),quality=94)
        enc.stdin.write(frame.tobytes())
        if i%(FPS*6)==0:print(name,i//FPS,flush=True)
    enc.stdin.close()
    if enc.wait():raise RuntimeError('video encoding failed')

def exterior(t):
    # Cosine crossfades make the 24-second edit loop without a hard cut.
    phase=t/8;idx=int(phase)%3;fraction=phase-int(phase)
    funcs=[eye,planet,ribbons];a=funcs[idx](t)
    if fraction>.75:
        w=(1-math.cos((fraction-.75)*4*math.pi))/2
        a=a*(1-w)+funcs[(idx+1)%3](t)*w
    return a
encode('exosphere',exterior);encode('immersive',interior)
(OUT/'media.json').write_text(json.dumps({'exterior':'exosphere.mp4','exteriorPoster':'exosphere-poster.jpg','interior':'immersive.mp4','interiorPoster':'immersive-poster.jpg','fps':FPS,'duration':SECONDS,'attribution':'Original procedural artwork for Vegas: Afterlight; not official Sphere programming.'},indent=2))
