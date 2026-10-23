"""Photo-referenced Bellagio Tower Premier King, authored in metres.

References/observations: build/hotels/bellagio-premier/REFERENCES.md.
The 8 x 6 m envelope fits the existing six-metre guest-room bay; the entry
and bathroom are adapted to its centre doorway. All detail is authored here,
not projected photographs. Textures, meshes, and materials are shared by the
streamed instances. Only structural surfaces and major furniture collide.
Run in Blender: --background --python-exit-code 1 --python this_file.py
"""
import sys, math, json, random
from pathlib import Path
import bpy, bmesh, numpy as np
from mathutils import Vector
sys.path.insert(0, 'tools/blender-level')
import bmlevel as b
from bmlevel.core import BoxCollider

OUT = Path('build/hotels')
REVIEW = OUT / 'bellagio-premier'
DEPTH = 8.0

def coord(p): return (p[0], -p[2], p[1])
def material(name, rgb, rough=.65, metal=0, glow=0, alpha=1):
    b.mat(name, rgb, roughness=rough, metal=metal, glow=glow, alpha=alpha)

def mesh(name, points, faces, mat, smooth=False):
    me=bpy.data.meshes.new(name); me.from_pydata([coord(p) for p in points], [], faces); me.update()
    bm=bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces)); bm.to_mesh(me); bm.free()
    ob=bpy.data.objects.new(name,me); b.scene.collection.objects.link(ob); me.materials.append(b.scene.materials[mat])
    for f in me.polygons: f.use_smooth=smooth
    return ob

def box(name,p,s,mat,bevel=.015,solid=False):
    if name in bpy.data.objects:name += ' '+str(len(bpy.data.objects))
    b.box(name,p,s,mat,solid=solid,bevel=min(bevel,min(s)*.35))
    return bpy.data.objects.get(name)

def proxy(name,p,s):
    b.level.colliders.append(BoxCollider(name,p,s,0,None))

def tube(name,points,r,mat,closed=False):
    cu=bpy.data.curves.new(name,'CURVE'); cu.dimensions='3D'; cu.resolution_u=2; cu.bevel_depth=r; cu.bevel_resolution=2
    sp=cu.splines.new('POLY'); sp.points.add(len(points)-1)
    for v,p in zip(sp.points,points): v.co=(*coord(p),1)
    sp.use_cyclic_u=closed
    ob=bpy.data.objects.new(name,cu); b.scene.collection.objects.link(ob); cu.materials.append(b.scene.materials[mat])
    bpy.ops.object.select_all(action='DESELECT'); ob.select_set(True); bpy.context.view_layer.objects.active=ob; bpy.ops.object.convert(target='MESH'); ob.select_set(False)
    return ob

def lathe(name,p,profile,mat,n=48,scale=(1,1,1),caps=True):
    pts=[(p[0]+r*math.cos(a)*scale[0],p[1]+h*scale[1],p[2]+r*math.sin(a)*scale[2]) for h,r in profile for a in [j*math.tau/n for j in range(n)]]
    faces=[(i*n+j,i*n+(j+1)%n,(i+1)*n+(j+1)%n,(i+1)*n+j) for i in range(len(profile)-1) for j in range(n)]
    if caps:faces += [tuple(reversed(range(n))),tuple((len(profile)-1)*n+j for j in range(n))]
    return mesh(name,pts,faces,mat,True)

def cushion(name,p,s,mat):
    # Closed superellipsoid gives upholstery a soft silhouette without bevel
    # subdivision pinching or overlapping stepped layers at the corners.
    def sp(v,e=.30):return math.copysign(abs(v)**e,v)
    n,m=32,16;points=[(0,-s[1]/2,0)]
    for j in range(1,m):
        a=-math.pi/2+math.pi*j/m
        for i in range(n):
            t=i*math.tau/n
            x=s[0]/2*sp(math.cos(a))*sp(math.cos(t));z=s[2]/2*sp(math.cos(a))*sp(math.sin(t))
            y=s[1]/2*sp(math.sin(a))
            if mat=='pk_linen':y+=.0025*math.sin(x*37+z*21)*math.cos(z*29)*math.cos(a)
            points.append((x,y,z))
    points.append((0,s[1]/2,0));top=len(points)-1
    faces=[(0,1+(i+1)%n,1+i) for i in range(n)]
    for j in range(m-2):
        for i in range(n):faces.append((1+j*n+i,1+j*n+(i+1)%n,1+(j+1)*n+(i+1)%n,1+(j+1)*n+i))
    faces += [(top,1+(m-2)*n+i,1+(m-2)*n+(i+1)%n) for i in range(n)]
    ob=mesh(name,points,faces,mat,True);ob.location=coord(p)
    return ob

def noise(n,grid,seed):
    rng=np.random.default_rng(seed); a=rng.random((grid+1,grid+1)).astype(np.float32)
    v=np.linspace(0,grid,n,endpoint=False); ix=v.astype(int); f=v-ix; f=f*f*(3-2*f)
    x=a[:,ix]*(1-f)+a[:,ix+1]*f
    return (x[ix,:]*(1-f[:,None])+x[ix+1,:]*f[:,None]).astype(np.float32)

def texture(name,pixels):
    n,m=pixels.shape[:2]; image=bpy.data.images.new(name,m,n,alpha=True)
    rgba=np.ones((n,m,4),dtype=np.float32);rgba[:,:,:3]=np.clip(pixels,0,1)
    image.pixels.foreach_set(rgba.ravel()); image.filepath_raw=str((REVIEW/'textures'/f'{name}.png').resolve());image.file_format='PNG';image.save();image.pack()
    return image

def textured(mat,image):
    m=b.scene.materials[mat]; nt=m.node_tree; tex=nt.nodes.new('ShaderNodeTexImage');tex.image=image
    nt.links.new(tex.outputs['Color'],nt.nodes['Principled BSDF'].inputs['Base Color'])

def textures():
    (REVIEW/'textures').mkdir(parents=True,exist_ok=True)
    n=1024; yy,xx=np.mgrid[0:n,0:n]/n
    # Bellagio's irregular taupe/ivory water-ripple carpet, never a checkerboard.
    v=.57*noise(n,12,4)+.27*noise(n,31,5)+.16*noise(n,78,7)
    field=np.sin((yy+v*.37)*math.tau*15)+.5*np.sin(xx*math.tau*9+v*17)
    mask=np.clip((field-.15)*5+.5,0,1)
    carpet=np.array([.245,.247,.235])+mask[:,:,None]*np.array([.31,.28,.225])
    carpet += (noise(n,260,3)[:,:,None]-.5)*.055
    textured('pk_carpet',texture('water-ripple-carpet',carpet))
    v=noise(n,7,9)*.13+noise(n,21,1)*.035
    vein=np.abs(np.sin((xx*.9+yy*.3+v)*math.tau*6))
    marble=np.ones((n,n,3))*[.82,.81,.76]-np.exp(-vein[:,:,None]*40)*[.25,.26,.26]
    marble+=(noise(n,100,8)[:,:,None]-.5)*.045
    textured('pk_marble',texture('ivory-veined-stone',marble))
    grain=noise(n,60,14)*.06+np.sin(xx*600+noise(n,9,8)*7)*.025
    textured('pk_wood',texture('smoked-oak-grain',np.ones((n,n,3))*[.22,.235,.235]+grain[:,:,None]))
    # Abstract horizontal water artwork, authored from the reference's palette.
    bands=.5+.5*np.sin(yy*45+noise(n,25,42)*2)
    blue=np.clip(.3+.55*np.sin(yy*9)+noise(n,20,41)*.2,0,1)
    mural=np.array([.77,.79,.77]) - blue[:,:,None]*np.array([.48,.39,.27])
    mural += bands[:,:,None]*.075
    textured('pk_mural',texture('water-horizon-artwork',mural))
    n=512; yy,xx=np.mgrid[0:n,0:n];rng=np.random.default_rng(10)
    weave=(np.sin(xx*math.pi/2)*np.cos(yy*math.pi/2)*.035+rng.random((n,n))*.02)
    for mat,col in [('pk_blue',[.22,.40,.43]),('pk_linen',[.88,.865,.82]),('pk_wall',[.59,.58,.54])]:
        textured(mat,texture(mat+'-woven',np.ones((n,n,3))*col+weave[:,:,None]))

def uv_project():
    scale={'pk_carpet':2.7,'pk_marble':1.2,'pk_wood':1,'pk_blue':.33,'pk_linen':.4,'pk_wall':.7}
    for ob in bpy.data.objects:
        if ob.type!='MESH' or ob.data.uv_layers:continue
        uv=ob.data.uv_layers.new(name='RoomUV');mat=ob.data.materials[0].name
        for poly in ob.data.polygons:
            axis=max(range(3),key=lambda i:abs(poly.normal[i]));axes=[i for i in range(3) if i!=axis]
            for li in poly.loop_indices:
                v=ob.matrix_world@ob.data.vertices[ob.data.loops[li].vertex_index].co
                if mat=='pk_mural':uv.data[li].uv=((v.x-3.87)/2.1,(v.z-1.38)/1.30)
                else:uv.data[li].uv=(v[axes[0]]/scale.get(mat,1),v[axes[1]]/scale.get(mat,1))

def trim_frame(name,x,y,z,w,h,mat='pk_white',th=.018):
    for xx in [x-w/2,x+w/2]:box(name+' stile',(xx,y,z),(th,h,th),mat,.004)
    for yy in [y-h/2,y+h/2]:box(name+' rail',(x,yy,z),(w,th,th),mat,.004)

def build_room():
    b.reset();random.seed(42)
    for name,col,rough,metal in [
        ('pk_wall',(.59,.58,.54),.95,0),('pk_white',(.82,.81,.75),.70,0),
        ('pk_carpet',(.4,.38,.33),.99,0),('pk_marble',(.82,.81,.76),.25,0),
        ('pk_darkstone',(.03,.038,.04),.25,.15),('pk_wood',(.22,.23,.23),.52,0),
        ('pk_brass',(.56,.43,.24),.26,.8),('pk_chrome',(.65,.70,.72),.18,.95),
        ('pk_blue',(.22,.40,.43),.94,0),('pk_linen',(.88,.86,.82),.98,0),
        ('pk_headboard',(.58,.54,.44),.9,0),('pk_black',(.012,.018,.022),.25,.15),
        ('pk_mirror',(.58,.65,.68),.12,.95),('pk_mural',(.36,.48,.58),.9,0),
        ('pk_ceramic',(.90,.89,.84),.21,0),('pk_leaf',(.075,.19,.11),.72,0),
        ('pk_flower',(.41,.09,.26),.8,0)]:material(name,col,rough,metal)
    material('pk_emissive',(.97,.88,.70),.65,glow=1.1)
    material('glass_window_pk',(.65,.79,.86),.15,alpha=.10)
    textures()
    # Floor elevations match the corridor exactly; decorative tiles replace,
    # rather than overlay, the room-floor surface. ~47 m² within party walls.
    b.slab('bedroom carpet',(5.475,0),(4.95,5.85),'pk_carpet',thickness=.18)
    b.slab('foyer stone',(1.525,1.175),(2.95,3.50),'pk_marble',thickness=.18)
    b.slab('bathroom stone',(1.525,-1.75),(2.95,2.35),'pk_marble',thickness=.18)
    box('ceiling',(4.025,3.50,0),(7.95,.20,6),'pk_white',0,True)
    for z in [-2.9625,2.9625]:
        box('party wall '+str(z),(4.025,1.75,z),(7.95,3.5,.075),'pk_wall',0,True)
        box('painted skirting',(4.025,.085,z-math.copysign(.055,z)),(7.95,.17,.065),'pk_white')
        for y,w,h in [(3.26,.13,.17),(3.37,.23,.08)]:box('stepped crown',(4.025,y,z-math.copysign(.09,z)),(7.95,h,w),'pk_white')
    for z in [-2.64,2.64]:box('window pier',(8,1.70,z),(.18,3.4,.65),'pk_wall',0,True)
    box('window sill wall',(8,.31,0),(.18,.62,4.68),'pk_wall',0,True)
    box('window header',(8,3.24,0),(.18,.32,4.68),'pk_white',0,True)
    box('window glazing',(8.018,1.85,0),(.045,2.38,4.66),'glass_window_pk',0,True)
    for y in [.65,3.06]:box('window horizontal frame',(7.94,y,0),(.13,.065,4.70),'pk_brass')
    for z in [-2.34,0,2.34]:box('window mullion',(7.94,1.85,z),(.13,2.43,.05),'pk_brass')
    box('stone window stool',(7.88,.635,0),(.34,.065,4.70),'pk_marble')
    # Rippling curtain fabric is mesh, not stacks of rectangular rods.
    for side in [-1,1]:
        points=[];rows=22;cols=72
        for j in range(rows+1):
            y=.07+3.09*j/rows
            for i in range(cols+1):
                z=side*(1.91+.88*i/cols);x=7.72+.060*math.sin(i/cols*math.tau*9)+.012*math.cos(j*.55+i*.3)
                points.append((x,y,z))
        faces=[(j*(cols+1)+i,j*(cols+1)+i+1,(j+1)*(cols+1)+i+1,(j+1)*(cols+1)+i) for j in range(rows) for i in range(cols)]
        ob=mesh('pleated blackout drape',points,faces,'pk_linen',True);ob.data.materials[0].use_backface_culling=False
    box('concealed drapery pelmet',(7.62,3.24,0),(.28,.20,5.7),'pk_white')
    # Entry wardrobe and marble foyer inset.
    box('built in closet',(.62,1.43,2.48),(1.12,2.86,.84),'pk_wood',.03,True)
    for x in [.33,.88]:
        box('wardrobe mirror',(x,1.52,2.04),(.49,2.28,.022),'pk_mirror')
        box('wardrobe handle',(x+(.18 if x<.5 else -.18),1.12,1.994),(.026,.28,.043),'pk_brass')
    # Inset tile pieces sit flush and own their patch; no coplanar floor decals.
    # A thin raised inlay is 3 mm high, below controller step tolerance.
    for x in [.4,.82,1.24,1.66,2.08,2.50]:
        for z in [.14,.56,.98]:
            if int(round((x-.4)/.42)+round((z-.14)/.42))%2==0:
                box('foyer dark marble inlay',(x,.0015,z),(.416,.003,.416),'pk_darkstone',0)
    for z in [-.10,1.22]:box('foyer inset border',(1.45,.002,z),(2.55,.004,.028),'pk_darkstone',0)
    # Bathroom door opening x=1.15..2.25, from the foyer on its +Z side.
    box('bath front pier',(.60,1.7,-.64),(1.10,3.4,.14),'pk_white',0,True)
    box('bath front return',(2.66,1.7,-.64),(.82,3.4,.14),'pk_white',0,True)
    box('bath doorway lintel',(1.70,3.02,-.64),(1.10,.76,.14),'pk_white',0,True)
    box('bath bedroom partition',(3.02,1.7,-1.83),(.14,3.4,2.30),'pk_wall',0,True)
    for x in [1.11,2.29]:box('bath jamb',(x,1.33,-.55),(.09,2.66,.09),'pk_white')
    box('bath door head',(1.7,2.65,-.55),(1.28,.10,.09),'pk_white')
    # The door is stored open flat along the return, outside the walking path.
    box('bath pocket door leaf',(2.67,1.28,-.545),(.69,2.5,.045),'pk_wood',.012)
    box('bath pocket pull',(2.37,1.0,-.51),(.025,.20,.025),'pk_brass')
    bathroom()
    bedroom()
    b.lamp('bedroom warm ambient',(5.15,2.95,.3),'#fff0d4',intensity=17,distance=7)
    b.lamp('window daylight',(7.5,2.55,.1),'#dae8f5',intensity=13,distance=6)
    b.lamp('bed sconces',(4.9,1.9,-2.35),'#ffe4b8',intensity=8,distance=4)
    b.lamp('bath vanity light',(1.8,2.3,-1.9),'#fff1dc',intensity=14,distance=3.8)
    b.lamp('entry downlight',(1.4,2.95,.6),'#ffebd2',intensity=7,distance=3)
    b.volume('Premier King room',(4,1.5,0),(7.9,3,5.85),tags=['indoors','hotel-room'])
    b.spawn((.4,.025,0));uv_project()

def bathroom():
    # Large-format shower tile, mosaic pan, frameless glass, drain and fittings.
    for iz in range(5):
        for iy in range(7):box('shower wall tile',(.088,.23+iy*.435,-.87-iz*.43),(.025,.429,.424),'pk_marble',.004)
    box('shower pan',(.57,.025,-1.79),(.97,.05,2.10),'pk_marble',.01,True)
    for i in range(8):
        for j in range(17):
            box('mosaic grout',(.13+i*.12,.052,-2.81+j*.12),(.009,.004,.115),'pk_white',0)
    box('shower drain',(.55,.058,-2.35),(.15,.007,.15),'pk_chrome',.007)
    for i in range(5):box('drain slot',(.50+i*.025,.062,-2.35),(.009,.005,.11),'pk_black',0)
    box('shower screen',(1.09,1.20,-2.16),(.016,2.30,1.48),'glass_window_pk',0,True)
    for y in [.10,1.10,2.28]:box('shower glass clamp',(1.07,y,-2.85),(.055,.065,.065),'pk_chrome')
    tube('shower riser',[(.17,1.02,-2.52),(.17,2.27,-2.52),(.40,2.32,-2.52)],.019,'pk_chrome')
    lathe('rain shower',(.43,2.29,-2.52),[(0,.12),(.026,.12)],'pk_chrome')
    tube('hand shower hose',[(.16,1.2,-1.9),(.24,.7,-1.85),(.3,.64,-1.85),(.33,1.6,-1.85)],.011,'pk_chrome')
    box('thermostatic mixer',(.12,1.1,-2.11),(.07,.15,.26),'pk_chrome',.03)
    box('shower niche',(.11,1.38,-1.25),(.09,.45,.39),'pk_darkstone',.01)
    for z in [-1.36,-1.22]:lathe('shampoo bottle',(.20,1.22,z),[(0,.033),(.12,.033),(.13,.016),(.16,.016)],'pk_ceramic',24)
    # Twin inset basins: an actual curved bowl, no fake flat sink rectangle.
    cabinet=box('vanity cabinet',(2.08,.60,-2.60),(1.65,.48,.55),'pk_white',.025,True)
    for x in [1.28,2.87]:box('vanity brass leg',(x,.45,-2.36),(.035,.87,.035),'pk_brass')
    box('vanity open shelf',(2.08,.19,-2.60),(1.64,.04,.54),'pk_wood')
    counter=box('vanity slab',(2.08,.88,-2.6),(1.76,.065,.66),'pk_marble',.015)
    # Cut actual openings in stone and cabinetry. Curved ceramic bowls continue
    # beneath the countertop instead of placing a flat disk over the sink.
    for x in [1.68,2.49]:
        cutter=lathe('temporary basin cut',(x,.74,-2.57),[(0,.217),(.30,.217)],'pk_ceramic',48,(1,1,.74))
        for ob in [cabinet,counter]:
            bpy.context.view_layer.objects.active=ob
            mod=ob.modifiers.new('Basin opening','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
            bpy.ops.object.modifier_apply(modifier=mod.name)
        bpy.data.objects.remove(cutter,do_unlink=True)
        lathe('inset ceramic basin',(x,.918,-2.57),[(0,.235),(.005,.218),(-.025,.206),(-.085,.17),(-.135,.07),(-.14,.019)],'pk_ceramic',48,(1,1,.74),False)
        lathe('basin waste',(x,.781,-2.57),[(0,.024),(.004,.024)],'pk_chrome',24)
        tube('basin tap',[(x, .92,-2.82),(x,1.09,-2.82),(x,1.13,-2.64),(x,1.10,-2.64)],.016,'pk_brass')
        for dx in [-.09,.09]:lathe('tap lever',(x+dx,.92,-2.81),[(0,.028),(.05,.025)],'pk_brass',24)
        # Overlapping illuminated mother-of-pearl rings, inset metal mirrors.
        pts=[(x+.425*math.cos(a),1.76+.53*math.sin(a),-2.867) for a in [i*math.tau/96 for i in range(96)]]
        tube('illuminated mirror surround',pts,.025,'pk_emissive',True)
        ring=[(x+.393*math.cos(a),1.76+.497*math.sin(a),-2.868) for a in [i*math.tau/96 for i in range(96)]]
        mirror=mesh('oval mirror',ring,[tuple(range(96))],'pk_mirror')
        # An open face has no unambiguous outside for normal recalculation.
        # Orient both mirrors toward the bathroom, which is Blender -Y.
        if mirror.data.polygons[0].normal.y>0:
            mirror.data.polygons[0].flip();mirror.data.update()
        for i in range(40):
            a=i*math.tau/40
            box('pearl mirror mosaic',(x+.448*math.cos(a),1.76+.554*math.sin(a),-2.875),(.031,.030,.016),'pk_ceramic',.006)
        trim_frame('vanity brass drawer',x,.61,-2.305,.68,.30,'pk_brass',.012)
    for x in [1.34,2.83]:
        tube('towel bar',[(x-.085,.77,-2.23),(x+.085,.77,-2.23)],.013,'pk_chrome')
        cushion('hanging hand towel',(x,.52,-2.225),(.16,.45,.034),'pk_linen')
    for i in range(3):cushion('folded bath towel',(2.06,.24+i*.048,-2.50),(.38,.049,.27),'pk_linen')
    lathe('tissue box',(1.29,.935,-2.6),[(0,.06),(.10,.06)],'pk_ceramic',4)
    for x in [2.10,2.19]:lathe('amenity bottle',(x,.94,-2.70),[(0,.024),(.12,.024),(.13,.013),(.15,.013)],'pk_ceramic',20)
    # WC, porcelain pedestal, rounded seat, cistern and flush.
    lathe('toilet pedestal',(2.62,.0,-1.16),[(0,.18),(.08,.18),(.30,.13),(.38,.23)],'pk_ceramic',40,(1,1,1.2))
    lathe('toilet bowl',(2.62,.35,-1.16),[(0,.19),(.09,.25),(.13,.25),(.14,.20),(.06,.12)],'pk_ceramic',48,(1,1,1.3))
    proxy('toilet proxy',(2.62,.28,-1.14),(.51,.56,.78))
    cushion('toilet seat',(2.62,.50,-1.16),(.49,.044,.61),'pk_ceramic')
    box('toilet cistern',(2.62,.60,-.88),(.48,.59,.20),'pk_ceramic',.07)
    box('flush button',(2.73,.78,-1.00),(.07,.026,.018),'pk_chrome')
    lathe('bath waste bin',(2.84,.0,-1.92),[(0,.10),(.26,.11),(.28,.11)],'pk_chrome',32)
    # Recessed fixture and geometric brass ceiling pendant.
    for a in [i*math.tau/4+math.pi/4 for i in range(4)]:
        tube('bath ceiling pendant',[(1.7,3.31,-1.5),(1.7+.34*math.cos(a),3.03,-1.5+.34*math.sin(a)),(1.7,2.89,-1.5)],.012,'pk_brass')
    lathe('bath pendant diffuser',(1.7,2.99,-1.5),[(0,.10),(.045,.1)],'pk_emissive',32)

def bedroom():
    # Bespoke head wall and rounded channeled bed; +Z is toward foot/media wall.
    box('headwall art',(4.95,2.08,-2.916),(2.17,1.36,.026),'pk_mural',0)
    box('headboard dark frame',(4.95,.94,-2.79),(2.15,1.39,.13),'pk_wood',.16)
    for i in range(7):cushion('padded headboard channel',(4.03+i*.307,.97,-2.695),(.301,1.27,.14),'pk_headboard')
    box('bed shadow plinth',(4.95,.14,-1.55),(1.87,.27,2.21),'pk_wood',.07,True)
    cushion('upholstered bed base',(4.95,.32,-1.55),(2.01,.25,2.23),'pk_headboard')
    cushion('king mattress',(4.95,.57,-1.55),(2,.28,2.15),'pk_linen')
    proxy('bed mattress collision',(4.95,.40,-1.55),(2.02,.80,2.19))
    # Duvet is a draped quad mesh: crown, thick rolled fold, hanging sides and
    # foot drop with irregular edge/wrinkles; deliberately no rigid white slab.
    xs=[-1.07,-1.025,-.96,-.80,-.60,-.40,-.20,0,.20,.40,.60,.80,.96,1.025,1.07]
    zs=[-2.03,-1.95,-1.84,-1.68,-1.50,-1.30,-1.10,-.90,-.70,-.49,-.40,-.35]
    pts=[]
    for z in zs:
        for x in xs:
            side=max(0,(abs(x)-.97)/.10);foot=max(0,(z+.48)/.13)
            h=.78-.41*max(side,foot)+.014*math.sin(x*23+z*7)+.008*math.sin(z*46+x*8)
            pts.append((4.95+x,h,z))
    cols=len(xs);faces=[(j*cols+i,j*cols+i+1,(j+1)*cols+i+1,(j+1)*cols+i) for j in range(len(zs)-1) for i in range(cols-1)]
    ob=mesh('draped white duvet',pts,faces,'pk_linen',True)
    sol=ob.modifiers.new('duvet thickness','SOLIDIFY');sol.thickness=.012
    bpy.context.view_layer.objects.active=ob;bpy.ops.object.modifier_apply(modifier=sol.name)
    cushion('folded duvet turn',(4.95,.795,-2.03),(2.0,.06,.30),'pk_linen')
    for row,z in enumerate([-2.37,-2.17]):
        for x in [4.46,5.43]:
            p=cushion('plump king pillow',(x,.84+row*.06,z),(.83,.19,.47),'pk_linen')
            p.rotation_euler.x=math.radians(12 if row else 22)
    # Foot bench's curved X legs and blue upholstered seat.
    cushion('blue bed bench',(4.95,.52,.00),(1.36,.15,.48),'pk_blue')
    box('bench brass rim',(4.95,.426,.00),(1.35,.025,.47),'pk_brass',.012)
    for x in [4.43,5.47]:
        for sign in [-1,1]:tube('swept X bench leg',[(x,.05,sign*.24),(x,.16,sign*.10),(x,.25,0),(x,.37,-sign*.18),(x,.43,-sign*.20)],.020,'pk_brass')
    tube('bench lower stretcher',[(4.43,.11,0),(5.47,.11,0)],.018,'pk_brass')
    proxy('foot bench',(4.95,.30,0),(1.38,.60,.50))
    for x in [3.51,6.39]:
        box('bedside architectural panel',(x,1.77,-2.89),(.69,2.87,.060),'pk_white')
        trim_frame('panel moulding',x,1.91,-2.843,.50,2.20,'pk_white',.028)
        oval=[(x+.17*math.cos(a),1.95+.58*math.sin(a),-2.825) for a in [i*math.tau/60 for i in range(60)]]
        tube('bedside oval moulding',oval,.012,'pk_white',True)
        box('nightstand carcass',(x,.47,-2.49),(.69,.65,.65),'pk_wood',.032,True)
        box('nightstand stone top',(x,.823,-2.49),(.72,.052,.69),'pk_marble')
        for y in [.46,.67]:
            box('nightstand drawer',(x,y,-2.15),(.61,.18,.030),'pk_white')
            box('drawer brass pull',(x,y,-2.12),(.14,.018,.03),'pk_brass')
        for xx in [x-.31,x+.31]:box('nightstand brass foot',(xx,.12,-2.22),(.027,.24,.027),'pk_brass')
        box('reading sconce plate',(x,1.79,-2.78),(.15,.28,.025),'pk_brass',.03)
        tube('sconce arm',[(x,1.75,-2.77),(x,1.75,-2.54),(x,1.91,-2.54)],.017,'pk_brass')
        lathe('sconce alabaster',(x,1.88,-2.54),[(0,.07),(.27,.065)],'pk_emissive',32)
        for dx in [-.18,.16]:box('bedside switch',(x+dx,1.03,-2.81),(.10,.09,.018),'pk_chrome')
    box('bedwall soffit',(4.95,3.18,-2.70),(2.58,.17,.50),'pk_white')
    for x in [4.32,5.58]:lathe('recessed bed downlight',(x,3.08,-2.62),[(0,.058),(.01,.058)],'pk_emissive',24)
    box('bedside phone',(3.51,.887,-2.39),(.24,.065,.17),'pk_black',.025)
    box('telephone handset',(3.51,.937,-2.43),(.21,.03,.053),'pk_black',.02)
    for ix in range(3):
        for iz in range(4):box('telephone key',(3.46+ix*.035,.925,-2.35+iz*.017),(.02,.007,.01),'pk_white',0)
    box('alarm clock',(6.37,.88,-2.47),(.18,.075,.1),'pk_black')
    # Window seating: scalloped curved loveseat, separate seat cushions,
    # upholstery piping, brass feet, stone cocktail table, floor lamp.
    cx,cz=7.06,-1.78
    for x in [cx-.55,cx+.55]:
        for z in [cz-.27,cz+.27]:lathe('loveseat tapered foot',(x,0,z),[(0,.023),(.16,.033)],'pk_brass',16)
    cushion('loveseat underseat',(cx,.26,cz),(1.37,.23,.77),'pk_blue')
    for x in [cx-.32,cx+.32]:cushion('loveseat seat cushion',(x,.46,cz+.08),(.65,.16,.66),'pk_blue')
    for i in range(11):
        a=math.pi*.08+i/10*math.pi*.84
        x=cx+.65*math.cos(a);z=cz-.40*math.sin(a)
        ob=cushion('scalloped loveseat back',(x,.76,z),(.175,.67,.16),'pk_blue');ob.rotation_euler.z=a-math.pi/2
    proxy('loveseat',(cx,.40,cz),(1.46,.8,.94))
    cushion('loveseat accent cushion',(6.68,.71,-1.68),(.36,.36,.13),'pk_linen')
    lathe('cocktail marble top',(6.87,.54,-.69),[(0,.42),(.035,.42)],'pk_marble',64)
    for a in [0,math.tau/3,math.tau*2/3]:tube('cocktail table leg',[(6.87+.33*math.cos(a),.05,-.69+.33*math.sin(a)),(6.87+.33*math.cos(a),.54,-.69+.33*math.sin(a))],.015,'pk_brass')
    proxy('cocktail table',(6.87,.29,-.69),(.77,.58,.77))
    flower_vase(6.87,.58,-.69)
    lathe('floor lamp base',(7.56,0,-2.35),[(0,.18),(.035,.18),(.06,.09)],'pk_brass')
    tube('floor lamp stem',[(7.56,.05,-2.35),(7.56,1.58,-2.35)],.019,'pk_brass')
    lathe('linen lampshade',(7.56,1.40,-2.35),[(0,.23),(.035,.23),(.43,.16),(.44,.16)],'pk_emissive')
    # Activity table + woven chair + round ottoman on the other window side.
    lathe('activity table pedestal',(7.02,.03,1.73),[(0,.31),(.04,.31),(.10,.20),(.53,.10),(.68,.20)],'pk_white')
    lathe('activity marble tabletop',(7.02,.73,1.73),[(0,.55),(.045,.55)],'pk_marble',64)
    proxy('activity table',(7.02,.39,1.73),(1.0,.78,1.0))
    for x in [7.51,7.95]:
        for z in [1.35,1.82]:tube('chair wood leg',[(x,.01,z),(x,.46,z)],.027,'pk_wood')
    cushion('activity chair seat',(7.69,.49,1.60),(.48,.11,.52),'pk_linen')
    box('activity chair back',(7.90,.84,1.60),(.075,.58,.51),'pk_wood',.03)
    cushion('chair inset upholstery',(7.847,.87,1.60),(.039,.39,.37),'pk_linen')
    lathe('ottoman brass plinth',(6.10,0,1.74),[(0,.31),(.07,.31)],'pk_brass')
    lathe('round upholstered ottoman',(6.10,.07,1.74),[(0,.315),(.30,.315),(.36,.28)],'pk_blue')
    lathe('ottoman top cushion',(6.10,.43,1.74),[(0,.31),(.065,.31),(.09,.26)],'pk_headboard')
    proxy('ottoman',(6.10,.27,1.74),(.62,.54,.62))
    # Media wall: rounded cabinet matching the photo, bronze bands, ribbed end
    # panels, minibar door, drawers and large television on white panelling.
    box('media wall panel',(4.95,1.79,2.909),(2.9,2.93,.04),'pk_white')
    trim_frame('media wall moulding',4.95,2.07,2.871,2.68,1.98)
    box('TV bezel',(4.95,1.94,2.822),(1.50,.88,.05),'pk_black',.025)
    box('inactive TV screen',(4.95,1.94,2.789),(1.44,.813,.012),'pk_darkstone',.004)
    box('TV standby diode',(5.60,1.525,2.778),(.009,.005,.004),'pk_emissive',0)
    box('media cabinet',(4.95,.49,2.54),(2.65,.91,.64),'pk_wood',.19,True)
    for y in [.09,.74]:box('media cabinet brass band',(4.95,y,2.53),(2.67,.027,.66),'pk_brass',.16)
    box('media cabinet dark top',(4.95,.96,2.53),(2.70,.055,.68),'pk_darkstone',.17)
    for x in [4.30,4.90,5.50]:
        box('cabinet inset',(x,.49,2.207),(.53,.64,.020),'pk_wood',.015)
        box('cabinet pull',(x,.75,2.172),(.16,.017,.04),'pk_brass')
    for x in [3.69+i*.038 for i in range(9)]+[5.96+i*.038 for i in range(9)]:
        box('fluted cabinet front',(x,.46,2.198),(.012,.63,.015),'pk_brass',.004)
    box('room information folio',(4.26,1.005,2.55),(.25,.028,.32),'pk_wood',.008)
    for i in range(2):
        lathe('water glass',(5.45+i*.17,.994,2.48),[(0,.032),(.105,.039)],'glass_window_pk',24)
    box('outlet plate',(3.1,.36,2.895),(.13,.16,.02),'pk_white')
    for x in [3.07,3.13]:box('outlet aperture',(x,.36,2.878),(.014,.031,.012),'pk_black',0)

def flower_vase(x,y,z):
    lathe('porcelain bud vase',(x,y,z),[(0,.06),(.12,.065),(.17,.036),(.20,.036)],'pk_ceramic',32)
    for i in range(7):
        a=i*2.4;px=x+.09*math.cos(a);pz=z+.09*math.sin(a);py=y+.30+(i%3)*.045
        tube('flower stem',[(x,y+.16,z),(px,py,pz)],.003,'pk_leaf')
        for j in range(5):
            ang=j*math.tau/5
            lathe('orchid petal',(px+.022*math.cos(ang),py,pz+.022*math.sin(ang)),[(0,.025),(.013,.019),(.02,.005)],'pk_flower',12)

def export_room():
    build_room();b.export(str(OUT),'bellagio-room')
    Path('src/work/hotels/bellagio-room.json').write_text((OUT/'bellagio-room.mesh-level.json').read_text())
    report={'reference':'Bellagio Tower Premier King, 2021 remodel','depth':DEPTH,'width':6,'colliders':len(b.level.colliders),
        'authoredObjects':len([o for o in bpy.data.objects if o.type=='MESH']),
        'triangles':sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in bpy.data.objects if o.type=='MESH'),
        'materialBatches':len(b.scene.materials),'glbBytes':(OUT/'bellagio-room.glb').stat().st_size}
    (REVIEW/'model-report.json').write_text(json.dumps(report,indent=2));print(report,flush=True)

if __name__=='__main__':export_room()
