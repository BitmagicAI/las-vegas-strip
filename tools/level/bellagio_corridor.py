"""Bellagio Tower renovated guest corridor, based on MGM/visitor photographs.

Six-metre repeating bay, existing 1.30m room openings at x=+/-1.85m. The
walkway narrows to 2.90m between the projecting wallpaper piers; recessed
door reveals keep the original room connections. All decorative detail is
non-colliding. Door leaf is a shared visual attached to the existing moving
door, and the terminal console is instantiated only once per guest corridor.
"""
import sys,math,json
from pathlib import Path
import bpy,numpy as np
sys.path.insert(0,'tools/level')
from bellagio_premier import b,box,tube,lathe,mesh,coord,noise

OUT=Path('build/hotels');REVIEW=OUT/'bellagio-corridor'

def texture(name,pixels):
    h,w=pixels.shape[:2];im=bpy.data.images.new(name,w,h,alpha=True)
    rgba=np.ones((h,w,4),dtype=np.float32);rgba[:,:,:3]=np.clip(pixels,0,1)
    im.pixels.foreach_set(rgba.ravel());im.filepath_raw=str((REVIEW/'textures'/f'{name}.png').resolve())
    im.file_format='PNG';im.save();im.pack();return im

def mapped(name,im):
    m=b.scene.materials[name];nt=m.node_tree;t=nt.nodes.new('ShaderNodeTexImage');t.image=im
    nt.links.new(t.outputs['Color'],nt.nodes['Principled BSDF'].inputs['Base Color'])

def textile_noise(h,w,rows,cols,seed):
    """Periodic woven variation, including at both ends of a repeated bay."""
    rng=np.random.default_rng(seed);a=rng.random((rows,cols))
    y=np.arange(h)/h*rows;x=np.arange(w)/w*cols
    iy=y.astype(int);ix=x.astype(int);fy=y-iy;fx=x-ix
    fy=fy*fy*(3-2*fy);fx=fx*fx*(3-2*fx)
    across=a[:,ix%cols]*(1-fx)+a[:,(ix+1)%cols]*fx
    return across[iy%rows]*(1-fy[:,None])+across[(iy+1)%rows]*fy[:,None]

def palette():
    for name,color,rough,metal,glow in [
        ('bc_wall',(.57,.52,.45),.96,0,0),('bc_cream',(.73,.71,.65),.88,0,0),
        ('bc_ceiling',(.32,.30,.27),.95,0,0),('bc_wood',(.045,.036,.028),.43,0,0),
        ('bc_door',(.32,.30,.29),.58,0,0),('bc_panel',(.41,.39,.36),.54,0,0),
        ('bc_brass',(.51,.36,.16),.33,.82,0),('bc_nickel',(.52,.53,.52),.22,.88,0),
        ('bc_carpet',(.13,.21,.31),1,0,0),('bc_shade',(.85,.78,.61),.72,0,.28),
        ('emissive_bc_crystal',(.88,.82,.69),.30,.12,.65),('bc_black',(.012,.016,.018),.55,0,0),
        ('bc_art',(.78,.76,.70),.92,0,0),('bc_stone',(.25,.23,.20),.28,.08,0),
        ('bc_petal',(.58,.10,.29),.85,0,0),('bc_green',(.13,.24,.07),.90,0,0)]:
        b.mat(name,color,roughness=rough,metal=metal,glow=glow)
    # A seamless photographic-style woven wallpaper, authored rather than
    # shipping or flattening the source photo onto the architectural model.
    n=1024;v,u=np.mgrid[0:n,0:n]/n
    weave=np.sin(u*math.tau*179)*.018+np.sin(v*math.tau*257)*.02
    ribs=np.sin(u*math.tau*8+.48*textile_noise(n,n,130,18,300))
    grain=.15*textile_noise(n,n,450,70,301)+.07*textile_noise(n,n,65,22,302)
    wall=np.array([.57,.525,.455])+weave[:,:,None]+(.044*ribs+grain-.11)[:,:,None]
    mapped('bc_wall',texture('taupe_woven_wallcovering',wall))
    # Water-ripple carpet. Periodic longitudinal coordinates make the pattern
    # continuous across repeated modules, with a large elliptical motif at doors.
    h,w=2048,1024;v,u=np.mgrid[0:h,0:w]/np.array([h,w])[:,None,None]
    x=(u-.5)*3.8;z=(v-.5)*6
    radius=np.sqrt((x/.97)**2+(6/math.pi*np.sin(z*math.pi/6)/.85)**2)
    phase=radius*37+1.6*(textile_noise(h,w,18,30,410)-.5)+.6*(textile_noise(h,w,72,110,411)-.5)
    phase+=2.1*(textile_noise(h,w,820,490,412)-.5)
    ripple=(np.sin(phase)+1)*.5
    ink=np.array([[.055,.11,.27],[.16,.25,.39],[.40,.43,.45],[.71,.69,.62],[.43,.38,.31]])
    ix=np.digitize(ripple,[.20,.43,.66,.90]);carpet=ink[ix]
    fuzz=(np.sin(u*math.tau*477)*np.sin(v*math.tau*837))*.027
    mapped('bc_carpet',texture('blue_ivory_ripple_carpet',carpet+fuzz[:,:,None]))
    # Original charcoal study for the terminal vignette (not a copied artwork).
    n=512;v,u=np.mgrid[0:n,0:n]/n;paper=np.full((n,n,3),(.78,.76,.70))
    for k in range(13):
        cx=.48+.16*np.sin(v*7+k*.47)+.05*np.sin(v*23+k)
        line=np.abs(u-cx)<.0028
        paper[line]=(.09,.085,.075)
    mapped('bc_art',texture('charcoal_water_study',paper))

def uvs():
    for o in list(bpy.data.objects):
        if o.type!='MESH':continue
        uv=o.data.uv_layers.active or o.data.uv_layers.new(name='CorridorUV')
        for p in o.data.polygons:
            mat=o.data.materials[p.material_index].name
            for li in p.loop_indices:
                v=o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co
                x,y,z=v.x,v.z,-v.y
                if mat=='bc_carpet':q=((x+1.9)/3.8,(z+3)/6)
                elif mat=='bc_wall':q=(z/.9,y/2.4) if abs(p.normal.x)>.5 else (x/.9,y/2.4)
                elif mat=='bc_art':q=(x/.83+.5,(y-1.49)/1.10)
                else:q=(x,y) if abs(p.normal.y)>.5 else (z,y)
                uv.data[li].uv=q

def finish(name):
    bpy.context.view_layer.update();uvs()
    count=sum(len(o.data.polygons) for o in bpy.data.objects if o.type=='MESH')
    b.spawn((0,.025,0));b.export(str(OUT),name)
    Path('src/work/hotels/'+name+'.json').write_text((OUT/(name+'.mesh-level.json')).read_text())
    return {'name':name,'polygons':count,'bytes':(OUT/(name+'.glb')).stat().st_size,'colliders':len(b.level.colliders)}

def ring(name,y,z,r,thick,material):
    tube(name,[(r*math.cos(a),y,z+r*math.sin(a)) for a in np.linspace(0,math.tau,65)[:-1]],thick,material,True)

def sconce(side,z):
    x=side*1.395
    disc=lathe('round brass sconce backplate',(0,0,0),[(-.018,.092),(.018,.092)],'bc_brass',32)
    disc.rotation_euler.y=math.pi/2;disc.location=coord((x,2.21,z))
    tube('sconce wall arm',[(x,2.21,z),(side*1.23,2.21,z)],.017,'bc_brass')
    lathe('sconce tapered spindle',(side*1.23,1.64,z),[(0,.009),(.56,.021),(.65,.023)],'bc_brass',24)
    lathe('linen cylindrical shade',(side*1.22,2.27,z),[(0,.078),(.28,.092),(.30,.092)],'bc_shade',24)
    lathe('sconce collar',(side*1.22,2.25,z),[(0,.045),(.034,.045)],'bc_brass',24)

def corridor():
    b.reset();palette()
    b.slab('continuous ripple carpet floor',(0,0),(3.8,6),'bc_carpet',thickness=.18)
    box('corridor structural ceiling',(0,3.5,0),(3.8,.2,6),'bc_cream',0,True)
    for side in [-1,1]:
        for z in [-2,2]:
            box('projecting wallpaper pier',(side*1.70,1.70,z),(.50,3.40,2),'bc_wall',0,True)
            box('dark skirting',(side*1.424,.08,z),(.06,.16,2),'bc_wood',.008)
            box('skirting bead',(side*1.41,.175,z),(.055,.035,2),'bc_wood',.008)
        for z in [-.825,.825]:
            box('recessed door jamb wall',(side*1.85,1.7,z),(.2,3.4,.35),'bc_wall',0,True)
        box('recessed door header',(side*1.85,3.025,0),(.20,.75,1.3),'bc_wall',0,True)
        # Layered dark mouldings have real depth and no duplicate wall faces.
        for z in [-.708,.708]:
            box('outer dark door architrave',(side*1.708,1.365,z),(.08,2.73,.11),'bc_wood',.009)
            box('architrave inner bead',(side*1.655,1.365,z),(.035,2.73,.025),'bc_wood',.005)
        for y in [2.715,2.78]:box('stepped overdoor moulding',(side*1.685,y,0),(.11,.07,1.57),'bc_wood',.01)
        for z in [-1.15,1.15]:sconce(side,z)
        box('side ceiling soffit',(side*1.34,3.255,0),(.32,.29,6),'bc_cream',0)
        box('ceiling perimeter fillet',(side*1.16,3.145,0),(.05,.045,6),'bc_cream',.008)
    box('grey ceiling tray',(0,3.374,0),(2.36,.025,6),'bc_ceiling',0)
    for z,w in [(0,.18),(-2.94,.12),(2.94,.12)]:box('coffer crossbeam',(0,3.255,z),(2.38,.29,w),'bc_cream',0)
    for z in [-1.5,1.5]:
        lathe('flush brass ceiling mount',(0,3.29,z),[(0,.13),(.06,.13)],'bc_brass',32)
        lathe('warm drum diffuser',(0,3.115,z),[(0,.32),(.155,.32)],'bc_shade',48)
        for y in [3.105,3.275]:ring('brass drum rim',y,z,.342,.013,'bc_brass')
        for y in [3.155,3.225]:ring('geometric brass band',y,z,.335,.007,'bc_brass')
        for i in range(12):
            a=i*math.tau/12
            tube('drum brass upright',[(.338*math.cos(a),3.115,z+.338*math.sin(a)),(.338*math.cos(a),3.265,z+.338*math.sin(a))],.009,'bc_brass')
        for i in range(28):
            a=i*math.tau/28
            lathe('faceted crystal drop',(.29*math.cos(a),3.052,z+.29*math.sin(a)),[(0,.014),(.025,.03),(.065,.021)],'emissive_bc_crystal',6)
        b.lamp(f'warm ceiling pool {z}',(0,2.86,z),'#ffebce',intensity=10,distance=6)
    b.volume('guest corridor',(0,1.5,0),(2.8,3,5.6),tags=['indoors','corridor','unroofed'])
    return finish('bellagio-corridor')

def door():
    b.reset();palette()
    # Door origin at collider centre. This entire visual follows the animated
    # kinematic leaf; both sides are detailed, with flush lower hardware.
    box('painted door leaf',(0,0,0),(1.285,2.63,.13),'bc_door',.007)
    for side in [-1,1]:
        for y,h in [(-.88,.48),(-.20,.56),(.70,1.02)]:
            box('recessed door panel',(0,y,side*.073),(1.04,h,.012),'bc_panel',.006)
            for x in [-.542,.542]:box('panel stile',(x,y,side*.080),(.033,h+.07,.025),'bc_door',.005)
            for yy in [y-h/2-.02,y+h/2+.02]:box('panel rail',(0,yy,side*.080),(1.10,.032,.025),'bc_door',.005)
        box('keycard lock plate',(.47,-.24,side*.105),(.115,.31,.035),'bc_nickel',.012)
        box('keycard reader',(.47,-.155,side*.127),(.08,.09,.012),'bc_black',.009)
        tube('lever handle',[(.47,-.28,side*.13),(.47,-.28,side*.19),(.32,-.28,side*.20)],.018,'bc_nickel')
        box('peephole',(.0,.37,side*.081),(.025,.025,.018),'bc_nickel',.008)
    return finish('bellagio-door')

def end():
    b.reset();palette()
    box('corridor terminal wall',(0,1.7,-.12),(3.8,3.4,.20),'bc_cream',0,True)
    box('terminal skirting',(0,.09,.015),(3.7,.18,.06),'bc_wood',.008)
    box('console stone top',(0,.88,.32),(1.32,.045,.42),'bc_stone',.015,True)
    for x in [-.54,-.36,-.18,0,.18,.36,.54]:
        tube('looped brass console leg',[(x,.87,.14),(x,.13,.14),(x,.075,.27),(x,.13,.48),(x,.87,.48)],.013,'bc_brass')
    box('charcoal artwork frame',(0,2.06,.018),(.99,1.29,.055),'bc_wood',.006)
    box('paper and charcoal study',(0,2.06,.051),(.83,1.10,.012),'bc_art',0)
    lathe('ceramic flower vase',(0,.91,.29),[(0,.105),(.24,.105),(.27,.075)],'bc_cream',32)
    for k in range(11):
        a=k*2.39;x=.25*math.cos(a);z=.29+.10*math.sin(a);y=1.34+.17*math.sin(k*.8)
        tube('flower stem',[(0,1.02,.29),(x*.6,y-.12,z),(x,y,z)],.007,'bc_green')
        for j in range(5):
            t=j*math.tau/5
            lathe('flower petal',(x+.026*math.cos(t),y,z+.026*math.sin(t)),[(0,.032),(.018,.048),(.04,.019)],'bc_petal',8)
    return finish('bellagio-corridor-end')

def export_corridor_set():
    (REVIEW/'textures').mkdir(parents=True,exist_ok=True)
    report=[corridor(),door(),end()]
    (REVIEW/'model-report.json').write_text(json.dumps(report,indent=2));print(report,flush=True)

if __name__=='__main__':export_corridor_set()
