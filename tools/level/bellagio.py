"""Reference-led Bellagio architecture and ground-floor gameplay interior.
The high-rise is exterior only; every public and service room below it is real, walkable space.
"""
import math, os, random
import bpy
import numpy as np
from mathutils import Vector
from bmlevel.core import BoxCollider
from bmlevel import mat, context, prism, slab, wall, door, volume, link, landmark, lamp, spot, level, scene
from bellagio_podium import PODIUM_DOORS, wall_moulding_spans
from bellagio_arrival import build_arrival


def build_bellagio(api):
    box, decor, beam = api['box'], api['decor'], api['beam']
    rng = random.Random(1998)
    serial = [0]
    def uid(n):
        serial[0] += 1
        return f'Bellagio {serial[0]:05d} {n}'
    def mesh(n, verts, faces, material, smooth=False):
        me=bpy.data.meshes.new(uid(n));me.from_pydata([(v[0],-v[2],v[1]) for v in verts],[],faces);me.update()
        ob=bpy.data.objects.new(me.name,me);scene.collection.objects.link(ob);me.materials.append(bpy.data.materials[material])
        if smooth:
            for p in me.polygons:p.use_smooth=True
        if verts:level.visual_points.extend([tuple(min(v[i] for v in verts) for i in range(3)),tuple(max(v[i] for v in verts) for i in range(3))])
        return ob
    def lathe(n,x,z,profile,material,segments=32):
        vs=[(x+r*math.cos(i*math.tau/segments),y,z+r*math.sin(i*math.tau/segments)) for r,y in profile for i in range(segments)]
        fs=[(j*segments+i,j*segments+(i+1)%segments,(j+1)*segments+(i+1)%segments,(j+1)*segments+i) for j in range(len(profile)-1) for i in range(segments)]
        fs += [tuple(reversed(range(segments))),tuple(range((len(profile)-1)*segments,len(profile)*segments))]
        return mesh(n,vs,fs,material,True)
    def column(n,x,z,y=0,h=7,r=.48):
        lathe(n,x,z,[(r*1.45,y),(r*1.45,y+.18),(r*1.15,y+.27),(r,y+.55),(r*.82,y+h-.7),(r*1.15,y+h-.5),(r*1.4,y+h-.25),(r*1.4,y+h)],'b_travertine',24)
        level.colliders.append(BoxCollider(uid(n+' collider'),(x,y+h/2,z),(r*2,h,r*2),0,'environment'))
    def oriented_box(n,pos,size,material,yaw):
        decor(uid(n),pos,size,material,yaw=yaw,bevel=.018)
    def arch(n,pos,width,height,depth,yaw,material='b_travertine',glass='b_glass0',frame=.23):
        # Local x across opening; positive local z points out of the facade.
        x,y,z=pos;c,s=math.cos(yaw),math.sin(yaw)
        def P(u,v,w):return(x+c*u+s*w,y+v,z-s*u+c*w)
        r=width/2;spring=height-r;steps=18
        if glass:
            outline=[(-r,0),(r,0),(r,spring)]+[(r*math.cos(a),spring+r*math.sin(a)) for a in np.linspace(0,math.pi,steps+1)][1:]+[(-r,0)]
            mesh(n+' arched pane',[P(u,v,.01) for u,v in outline],[tuple(range(len(outline)))],glass)
        for side in [-1,1]:oriented_box(n+' jamb',P(side*(r+frame/2),spring/2,depth/2),(frame,spring,depth),material,yaw)
        for i in range(steps):
            a,b=math.pi*i/steps,math.pi*(i+1)/steps
            pts=[P(rr*math.cos(t),spring+rr*math.sin(t),w) for w in [0,depth] for rr,t in [(r,a),(r,b),(r+frame,b),(r+frame,a)]]
            mesh(n+' arch stone',pts,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],material)
        oriented_box(n+' keystone',P(0,height+.1,depth*.6),(.32,.56,depth*1.3),material,yaw)
        if glass:
            oriented_box(n+' transom',P(0,spring,.055),(width,.075,.08),'b_bronze',yaw)
            oriented_box(n+' mullion',P(0,spring*.5,.055),(.065,spring,.08),'b_bronze',yaw)
    def label(n,string,pos,yaw=0,size=.38):
        curve=bpy.data.curves.new(uid(n),'FONT');curve.body=string;curve.align_x='CENTER';curve.size=size;curve.extrude=.005
        font='/System/Library/Fonts/Supplemental/Times New Roman.ttf'
        if os.path.exists(font):curve.font=bpy.data.fonts.load(font,check_existing=True)
        ob=bpy.data.objects.new(curve.name,curve);scene.collection.objects.link(ob);ob.location=(pos[0],-pos[2],pos[1]);ob.rotation_euler=(math.pi/2,0,yaw);curve.materials.append(bpy.data.materials['b_bronze'])
        bpy.context.view_layer.update();me=bpy.data.meshes.new_from_object(ob.evaluated_get(bpy.context.evaluated_depsgraph_get()));out=bpy.data.objects.new(ob.name+' mesh',me);scene.collection.objects.link(out);out.matrix_world=ob.matrix_world.copy();bpy.data.objects.remove(ob,do_unlink=True)
    def wall_gaps(n,a,b,h,openings=(),material='b_plaster',thick=.55):
        dx,dz=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dz);yaw=math.atan2(-dz,dx)
        def seg(start,end,low,high):
            if end<=start:return
            t=(start+end)/2/length
            box(uid(n),(a[0]+dx*t,(low+high)/2,a[1]+dz*t),(end-start+.025,high-low,thick),material,yaw=yaw)
        cursor=0
        for at,w,hh in sorted(openings):
            seg(cursor,at-w/2,0,h);seg(at-w/2,at+w/2,hh,h);cursor=at+w/2
        seg(cursor,length,0,h)
    # Dedicated facade and interior palette. No giant brick pattern on a plaster high-rise.
    palette=[('b_plaster',(.67,.59,.45),0,.88,0),('b_travertine',(.72,.65,.51),0,.69,0),('b_shadowstone',(.37,.32,.25),0,.86,0),('b_bronze',(.24,.16,.075),.75,.33,0),('b_roof',(.29,.16,.095),0,.9,0),('b_water',(.025,.12,.115),.35,.16,0),('b_marble',(.64,.61,.52),.08,.3,0),('b_darkmarble',(.15,.16,.15),.12,.3,0),('b_walnut',(.09,.039,.021),0,.48,0),('b_felt',(.035,.12,.08),0,.95,0),('b_velvet',(.18,.032,.029),0,.84,0),('b_carpet',(.18,.055,.035),0,.95,0),('b_emissive',(1,.61,.24),0,.3,2)]
    for n,c,metal,rough,glow in palette:mat(n,c,metal=metal,roughness=rough,glow=glow)
    for i,c in enumerate([(.045,.078,.086),(.063,.088,.09),(.08,.098,.094),(.035,.046,.05),(.13,.14,.125)]):mat('b_glass'+str(i),c,metal=.24,roughness=.34+i*.04)
    for i,c in enumerate([(.5,.13,.025),(.75,.35,.065),(.10,.28,.33),(.33,.055,.025),(.5,.43,.2)]):mat('b_flower'+str(i),c,metal=.25,roughness=.22,glow=.17)
    # Packed exportable plaster/travertine/marble/carpet maps at 2K.
    n=2048;yy,xx=np.mgrid[:n,:n];randommap=np.random.default_rng(1998).random((n,n)).astype(np.float32)
    for name in ['b_plaster','b_travertine','b_marble','b_carpet']:
        m=bpy.data.materials[name];bs=m.node_tree.nodes['Principled BSDF'];base=np.array(bs.inputs['Base Color'].default_value[:3]);v=.9+.12*randommap
        if name=='b_plaster':v+=.035*np.sin(xx*.006+np.sin(yy*.004))+.025*np.cos(yy*.018)
        if name=='b_travertine':v+=.035*np.sin(yy*.22+np.sin(xx*.02)*4)+.035*np.cos(yy*.045)
        if name=='b_marble':v+=.10*np.sin(xx*.012+yy*.008+np.sin(xx*.004)*4);v*=np.where(np.abs(np.sin(xx*.006+yy*.01+np.sin(yy*.003)*2))<.035,.58,1)
        pixels=np.ones((n,n,4),np.float32);pixels[:,:,:3]=np.clip(base[None,None,:]*v[:,:,None],0,1)
        if name=='b_carpet':
            u=(xx%n)/n;w=(yy%n)/n;rosette=np.cos(u*math.tau*4+np.sin(w*math.tau*2)*2)*np.cos(w*math.tau*4+np.sin(u*math.tau*2)*2)
            mask=rosette>.65;pixels[mask,:3]=(.38,.25,.10)
            pixels[:,:,:3]*=(.75+.25*randommap[:,:,None])
        im=bpy.data.images.new(name+' surface',width=n,height=n);im.pixels.foreach_set(pixels.ravel());im.pack();tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im;m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
    z0=-18
    def front(u):return -159+18*(abs(u)/95)**2
    def frontframe(u,y,off=0):
        derivative=36*u/(95**2);yaw=math.pi/2+math.atan(derivative)
        return (front(u)+off*math.sin(yaw),y,z0+u+off*math.cos(yaw)),yaw
    with context('Bellagio / curved main tower'):
        for side in [-1,1]:
            for j in range(24):
                ua=side*(10+j*3.54);ub=side*(10+(j+1)*3.54);u=(ua+ub)/2;ua,ub=sorted([ua,ub]);h=86 if abs(u)<77 else 80
                outline=[(front(ua)-20,z0+ua),(front(ua),z0+ua),(front(ub),z0+ub),(front(ub)-20,z0+ub)]
                prism(uid('curved structural bay'),outline,8.3,h,'b_plaster')
                # Ground-floor arcades support the wings beyond the public podium.
                if z0+u < -76 or z0+u > 42:
                    column('wing arcade pier',front(u)-.65,z0+u,h=8.3,r=.62)
                    box(uid('wing arcade rear wall'),(front(u)-19.6,4.15,z0+u),(1.0,8.3,3.6),'b_plaster')
                    p,ya=frontframe(u,0,.08);arch('wing base arcade',p,2.1,8.1,.35,ya,glass=None,frame=.32)
                # Deep horizontal band profiles, with real soffits and shadow lines.
                for y,w,t,dep in [(10.5,3.58,.55,.35),(16,3.58,.8,.4),(59,3.58,.8,.55),(60,3.58,.38,.82),(h-.9,3.63,.4,.7),(h-.25,3.66,.32,1.0),(h+.2,3.67,.36,1.15)]:
                    p,ya=frontframe(u,y,dep/2);oriented_box('moulded cornice',p,(w,t,dep),'b_travertine',ya)
                for y in np.arange(18,58,3.2):
                    p,ya=frontframe(u,float(y),.035);oriented_box('deep window reveal',p,(2.18,2.45,.16),'b_shadowstone',ya)
                    p,ya=frontframe(u,float(y),.16);oriented_box('individual dark window',p,(1.91,2.19,.055),'b_glass'+str(rng.randrange(5)),ya)
                    for dy in [-1.25,1.25]:
                        p,ya=frontframe(u,float(y)+dy,.29);oriented_box('window head and sill',p,(2.28,.13,.42),'b_travertine',ya)
                    for du in [-1.08,1.08]:
                        p,ya=frontframe(u+du,float(y),.22);oriented_box('window stone reveal',p,(.14,2.5,.27),'b_travertine',ya)
                    p,ya=frontframe(u,float(y),.21);oriented_box('window mullion',p,(.055,2.25,.085),'b_bronze',ya)
                    p,ya=frontframe(u,float(y)-.45,.21);oriented_box('window transom',p,(1.94,.045,.085),'b_bronze',ya)
                # Upper order: pilasters and grouped windows beneath the arch-crowned loggia.
                crownbase=h-8.8
                for y in np.arange(62,crownbase-1,3.05):
                    p,ya=frontframe(u,float(y),.12);oriented_box('upper salon window',p,(2.03,2.42,.09),'b_glass'+str(rng.randrange(5)),ya)
                    p,ya=frontframe(u,float(y)-1.25,.24);oriented_box('upper salon sill',p,(2.23,.14,.36),'b_travertine',ya)
                p,ya=frontframe(u,crownbase,.17);arch('crown loggia',p,2.08,7.1,.34,ya,frame=.22)
                for du in [-1.55,1.55]:
                    p,ya=frontframe(u+du,(60+h)/2,.21);oriented_box('upper-order pilaster',p,(.25,h-60,.32),'b_travertine',ya)
                # Rear windows prevent the hotel becoming a blank cardboard facade.
                for y in np.arange(15,h-4,3.2):decor(uid('rear hotel window'),(front(u)-20.05,float(y),z0+u),(.08,2.0,2.05),'b_glass3')
                for uoff in [-1.15,0,1.15]:
                    p,ya=frontframe(u+uoff,h-.64,.64);oriented_box('roof dentil',p,(.26,.29,.35),'b_travertine',ya)
                # Small roof-setback plant, away from silhouette edge.
                if j%6==0:decor(uid('roof duct'),(front(u)-12,h+1,z0+u),(2.5,2,3),'steel')
        # Cylindrical central risalit: strong silhouette, not a rectangular tower with a sign.
        cx,cz=-164,z0
        lathe('rounded central tower',cx,cz,[(10.6,8.3),(10.6,89),(10.9,89.2),(10.9,90)],'b_plaster',72)
        for y in [15.8,59.0,60.0,87.7,88.8,90.1]:lathe('central ring cornice',cx,cz,[(10.65,y),(11.35,y+.14),(11.35,y+.4),(10.65,y+.56)],'b_travertine',72)
        for j in range(16):
            a=math.tau*j/16;normal=(math.cos(a),math.sin(a));yaw=math.atan2(normal[0],normal[1])
            for y in np.arange(18,85,3.2):
                p=(cx+10.69*normal[0],float(y),cz+10.69*normal[1]);oriented_box('rotunda window',p,(2.0,2.35,.12),'b_glass'+str(j%5),yaw)
                p=(cx+10.86*normal[0],float(y)-1.22,cz+10.86*normal[1]);oriented_box('rotunda window sill',p,(2.23,.14,.34),'b_travertine',yaw)
            p=(cx+10.8*normal[0],49,cz+10.8*normal[1]);oriented_box('rotunda engaged pier',p,(.25,66,.38),'b_travertine',yaw)
        # Open belvedere cupola: actual columns and arched gaps beneath the dome.
        lathe('cupola drum',cx,cz,[(7.4,90),(7.4,94),(8.0,94.15),(8,94.55),(7,94.8)],'b_travertine',64)
        for j in range(12):
            a=j*math.tau/12;px=cx+6.7*math.cos(a);pz=cz+6.7*math.sin(a)
            lathe('cupola column',px,pz,[(.33,94.6),(.44,94.8),(.3,95.1),(.27,99.1),(.44,99.4),(.44,99.7)],'b_travertine',16)
            aa=a+math.pi/12;p=(cx+6.7*math.cos(aa),96.2,cz+6.7*math.sin(aa));arch('cupola open arch',p,2.5,3.9,.28,math.atan2(math.cos(aa),math.sin(aa)),glass=None,frame=.26)
        lathe('cupola cap',cx,cz,[(7.6,100),(8.15,100.3),(8.15,100.65),(7.7,101)],'b_travertine',64)
        profile=[(7.6*math.cos(t),101+3.5*math.sin(t)) for t in np.linspace(0,math.pi/2,18)]
        lathe('copper cupola dome',cx,cz,profile,'b_roof',64)
        lathe('finial',cx,cz,[(.35,104.3),(.3,105),(.12,105.4),(.02,107)],'b_bronze',24)
    print('Bellagio curved tower and cupola built',flush=True)
    with context('Bellagio / playable podium'):
        slab('Bellagio public floor',(-161,-17),(60.6,118.6),'b_darkmarble',y=.012,thickness=.45)
        slab('Bellagio public ceiling',(-161,-17),(60.6,118.6),'b_plaster',y=8.5,thickness=.5)
        # All exterior openings have matching engine door leaves and collider records.
        wall_gaps('south facade',(-191,-76),(-131,-76),8,[(36,6,4.5)])
        wall_gaps('north facade',(-191,42),(-131,42),8)
        wall_gaps('lakefront facade',(-131,-76),(-131,42),8,[(110,5,4.5)])
        wall_gaps('service boundary',(-191,-76),(-191,42),8,[(18,3.4,3.2),(88,3.4,3.2)])
        for n,p,yaw,w,h in PODIUM_DOORS:
            door('bellagio_'+n,p,yaw=yaw,width=w,height=h,thickness=.18,animation='slide',auto_open_radius=7 if w>4 else 3.5)
        volume('bellagio_public_envelope',(-161,4,-17),(60,8,118),tags=['indoors','public'])
        # Open interior arcades divide lobby / gaming / gallery without sealing the routes.
        for z in [-44,26]:
            for x in [-186,-174,-150,-138]:column('casino arcade column',x,z,h=7.3,r=.5)
            decor(uid('arcade lintel'),(-161,7.6,z),(60, .7,1.0),'b_travertine')
            for x in [-180,-162,-144]:arch('interior arcade arch',(x,0,z),9.2,7.1,.48,0,glass=None,frame=.4)
        # Patterned gaming carpet with a wide marble circulation cross.
        decor(uid('casino carpet'),(-161,.026,-9),(56,.03,67),'b_carpet')
        for x in [-161]:decor(uid('main marble aisle'),(x,.056,-17),(5,.035,114),'b_marble')
        decor(uid('cross aisle'),(-163,.065,12),(57,.035,4.8),'b_marble')
        for x in [-164,-158]:decor(uid('aisle brass inlay'),(x,.082,-17),(.055,.02,114),'b_bronze')
        for z in [-42,24]:decor(uid('carpet border'),(-161,.068,z),(56,.025,.3),'b_bronze')
        # Lobby marble tiles, alternating diagonal inlays and a large round central medallion.
        for x in range(-187,-134,3):
            for z in range(-73,-45,3):decor(uid('lobby marble tile'),(x,.035,z),(2.94,.03,2.94),'b_marble')
        lathe('lobby floor medallion',-159,-60,[(5.6,.075),(5.6,.085)],'b_darkmarble',96)
        for rr in [4.8,5.0,5.45]:
            lathe('medallion brass ring',-159,-60,[(rr,.088),(rr,.1),(rr-.04,.1),(rr-.04,.088)],'b_bronze',96)
        # Coffered ceiling, plaster coves, brass-framed inset panels.
        for x in [-181,-169,-153,-141]:
            for z in range(-70,39,12):
                decor(uid('ceiling coffer'),(x,7.83,z),(9,.27,9),'b_shadowstone')
                decor(uid('coffer inner field'),(x,7.66,z),(8.3,.12,8.3),'b_plaster')
                for dz in [-4.2,4.2]:decor(uid('coffer gilt moulding'),(x,7.55,z+dz),(8.6,.13,.15),'b_bronze')
        for x in [-190.5,-131.5]:
            for h in [.18,1.12,6.9,7.45]:
                for lo,hi in wall_moulding_spans(x,h):
                    decor(uid('wall moulding'),(x,h,(lo+hi)/2),(.25,.16,hi-lo),'b_travertine')
        # Main columns carry the actual canopy; wide center and cross routes remain clear.
        for x in [-182,-140]:
            for z in [-31,-11,9]:column('gaming floor column',x,z,h=7.4,r=.45)
        # Reception is an articulated curved counter with bronze edge and back wall panels.
        for i in range(20):
            a=-1.2+i*2.4/20;b=-1.2+(i+1)*2.4/20
            outline=[(-179+rr*math.cos(t),-63+rr*math.sin(t)) for rr,t in [(5.1,a),(5.1,b),(6.0,b),(6.0,a)]]
            prism(uid('reception curved desk'),outline,.05,1.05,'b_walnut')
            prism(uid('reception marble countertop'),outline,1.05,1.17,'b_darkmarble')
        label('reception','R E C E P T I O N',(-189.65,3.25,-63),math.pi/2,.52)
        # Suspended glass garden: individually scalloped blown-glass disks, real 3D petals.
        for i in range(115):
            angle=rng.random()*math.tau;rr=math.sqrt(rng.random());x=-159+rr*10*math.cos(angle);z=-61+rr*7*math.sin(angle);y=7.0+rng.uniform(-.45,.25);rad=rng.uniform(.28,.9)
            verts=[(x,y+.22,z)];steps=96;rings=5
            for k in range(1,rings+1):
                t=k/rings
                for j in range(steps):
                    a=j*math.tau/steps;r=rad*t*(1+.12*t*math.sin(a*7+i));verts.append((x+r*math.cos(a),y+.22*(1-t)**2+.11*t*t*math.sin(a*7+i),z+r*math.sin(a)))
            faces=[(0,j+1,(j+1)%steps+1) for j in range(steps)]
            for k in range(rings-1):
                for j in range(steps):
                    a=1+k*steps+j;b=1+k*steps+(j+1)%steps;faces.append((a,b,b+steps,a+steps))
            mesh('scalloped glass flower',verts,faces,'b_flower'+str(i%5),True)
        # Bronze-ring chandeliers with hanging drops, absent pieces imply abandonment.
        for z in [-30,-8,14,34]:
            x=-161;lathe('chandelier ring',x,z,[(2.1,6.2),(2.1,6.35),(1.95,6.35),(1.95,6.2)],'b_bronze',48)
            for j in range(18):
                a=j*math.tau/18;px=x+2*math.cos(a);pz=z+2*math.sin(a)
                beam(uid('chandelier suspension'),(px,6.3,pz),(x,7.9,z),.015,'b_bronze',6)
                lathe('crystal drop',px,pz,[(.04,5.5),(.095,5.75),(.04,6.2)],'b_emissive',8)
            lamp(uid('casino warm light'),(x,6.0,z),'#ffce8d',160,27)
        for x in [-177,-147]:
            for z in [-24,-2,20]:lamp(uid('casino side light'),(x,5.8,z),'#ffd6a0',110,22)
        lamp('bellagio_lobby_light',(-159,6.1,-61),'#ffd6a3',220,30)
        spot('bellagio_lobby_accent',(-179,6.5,-63),(-173,.5,-63),'#ffe0ad',160,angle=1.1,cast_shadow=True)
        # Tall lower frontage windows and shallow balcony relief.
        for z in [-69,-58,-47,-36,-25,-14,-3,8,19]:arch('podium lake window',(-130.65,1,z),3.9,5.3,.25,math.pi/2,frame=.3)
        # Casino furniture: modeled cloth tables, brass rails, turned legs and upholstered stools.
        for x,z in [(-173,-28),(-181,-21),(-174,-7),(-181,0),(-174,22)]:
            level.colliders.append(BoxCollider(uid('poker table collider'),(x,.56,z),(4.4,1.12,4.4),0,'environment'))
            lathe('gaming table pedestal',x,z,[(.72,.0),(.72,.15),(.26,.35),(.32,.85)],'b_walnut',24)
            # Elliptical top, not a rectangular proxy.
            ob=lathe('poker table rail',x,z,[(2.25,.85),(2.35,.94),(2.35,1.08),(2.13,1.13)],'b_walnut',64)
            ob=lathe('poker table cloth',x,z,[(2.12,1.06),(2.12,1.11)],'b_felt',64)
            for j in range(7):
                a=j*math.tau/7;px=x+2.95*math.cos(a);pz=z+2.95*math.sin(a)
                lathe('gaming chair',px,pz,[(.34,0),(.34,.07),(.07,.10),(.065,.62),(.35,.65),(.35,.8)],'b_velvet',20)
                beam(uid('chair spine'),(px,.6,pz),(px,1.3,pz),.045,'b_bronze',8)
                # Chips and cards are small but actual tabletop geometry.
                lathe('chip stack',x+1.7*math.cos(a),z+1.7*math.sin(a),[(.055,1.12),(.055,1.19)],'b_flower'+str(j%5),12)
        # Import the generated manufactured cabinet once, then duplicate its real mesh/materials.
        slotfile='build/bellagio-v2/slot-machine.glb'
        if not os.path.exists(slotfile):raise FileNotFoundError('Casino slot asset has not been downloaded: '+slotfile)
        before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=os.path.abspath(slotfile));sources=[o for o in bpy.data.objects if o not in before and o.type=='MESH'];bpy.context.view_layer.update()
        points=[o.matrix_world@Vector(v) for o in sources for v in o.bound_box];low=Vector(tuple(min(p[i] for p in points) for i in range(3)));high=Vector(tuple(max(p[i] for p in points) for i in range(3)));scale=1.85/(high.z-low.z);center=(low+high)/2;origin=Vector((center.x,center.y,low.z))
        # Bake source transforms so preserving UVs and instancing does not depend on parent empties.
        templates=[]
        for o in sources:
            me=o.data.copy()
            for v in me.vertices:v.co=(o.matrix_world@v.co-origin)*scale
            templates.append(me)
        for o in list(bpy.data.objects):
            if o not in before:bpy.data.objects.remove(o,do_unlink=True)
        for row,z in enumerate([-32,-18,-4,20]):
            for col in range(10):
                px=-145 if col<5 else -151; pz=z+(col%5-2)*1.25
                for me in templates:
                    o=bpy.data.objects.new(uid('slot cabinet'),me);scene.collection.objects.link(o);o.location=(px,-pz,.02);o.rotation_euler.z=-math.pi/2;o['preserve_uv']=True
                # Matching collider stays beneath 2 m, with room to walk between banks.
                level.colliders.append(BoxCollider(uid('slot collision'),(px,.91,pz),(.92,1.82,1.1),0,'environment'))
                lathe('slot stool',px-1.05,pz,[(.28,0),(.28,.06),(.065,.12),(.065,.6),(.31,.63),(.31,.77)],'b_velvet',20)
        # Simple foreground table near south casino threshold, avoiding the main route.
        label('casino wayfinding','CASINO',(-161,6.6,-44),math.pi,.58)
        label('gallery wayfinding','NORTH GALLERY',(-161,6.6,26),math.pi,.5)
    print('Bellagio casino and lobby furnished',flush=True)
    with context('Bellagio / service rooms'):
        slab('Bellagio service floor',(-203,-17),(24.6,102.6),'b_darkmarble',y=.018)
        slab('Bellagio corridor ceiling',(-197,-17),(12.6,102.6),'b_plaster',y=4.65,thickness=.45)
        wall_gaps('corridor south',(-203,-68),(-191,-68),4.2)
        wall_gaps('corridor north',(-203,34),(-191,34),4.2)
        # Existing main boundary supplies east corridor wall; cover remaining exterior returns.
        wall_gaps('west service partitions',(-203,-68),(-203,34),4.2,[(10,2.2,2.9),(32,2.2,2.9),(54,2.2,2.9),(76,2.2,2.9)],material='b_shadowstone')
        volume('bellagio_service_envelope',(-197,2.1,-17),(12,4.2,102),tags=['indoors','service'])
        for name,z in [('staff_lounge',-58),('stores',-36),('medical',-14),('security',8)]:
            slab('Bellagio '+name+' ceiling',(-209,z),(12.6,16.6),'b_plaster',y=4.65,thickness=.45)
            wall_gaps(name+' west',(-215,z-8),(-215,z+8),4.2,material='b_shadowstone')
            wall_gaps(name+' south',(-215,z-8),(-203,z-8),4.2,material='b_shadowstone')
            wall_gaps(name+' north',(-215,z+8),(-203,z+8),4.2,material='b_shadowstone')
            door('bellagio_'+name,(-203,0,z),yaw=math.pi/2,width=2.2,height=2.9,thickness=.14,animation='hinge',auto_open_radius=3.2)
            volume('bellagio_'+name,(-209,2.1,z),(12,4.2,16),tags=['indoors','room',name])
            landmark('bellagio_'+name,(-208,.1,z),tags=['interior',name])
            label(name+' label',name.replace('_',' ').upper(),(-202.65,3.3,z),math.pi/2,.32)
            lamp('bellagio_'+name+'_lamp',(-209,3.8,z),'#d1dce0',65,15)
            decor(uid('wall dado'),(-214.6,1.1,z),(.15,.6,15.4),'b_walnut')
            for zz in [z-6,z+6]:
                decor(uid('wall light housing'),(-214.3,2.7,zz),(.25,.6,.45),'b_bronze')
                decor(uid('wall light diffuser'),(-214.1,2.7,zz),(.05,.4,.3),'b_emissive')
        # Door service rooms remain conventional; no solid fake furniture fills the entire room.
        for x in [-213,-206]:
            for z in [-41,-32]:
                box(uid('store shelving frame'),(x,1.25,z),(.55,2.5,3.6),'b_walnut')
                for y in [.2,.9,1.6,2.3]:
                    decor(uid('store shelf'),(x+.38,y,z),(1.1,.09,3.6),'steel')
                    for zz in [z-1.25,z-.55,z+.15,z+.85]:lathe('supply tin',x+.45,zz,[(.13,y+.06),(.13,y+.38)],'b_travertine',16)
        # Medical cot, mattress, steel frame, wall cabinet and folding screen.
        box(uid('medical cot'),(-212,.45,-17),(1.1,.75,2.4),'steel',bevel=.08)
        decor(uid('medical mattress'),(-212,.9,-17),(1.25,.18,2.5),'b_marble',bevel=.09)
        decor(uid('medical pillow'),(-212,1.06,-16.2),(1,.15,.5),'b_plaster',bevel=.09)
        box(uid('medical cabinet'),(-213,1.1,-8),(1.2,2.2,.75),'b_travertine',bevel=.06)
        # Staff lounge sofa: cushion, back, arms and visible legs.
        box(uid('lounge sofa back'),(-213,1,-62),(.45,1.5,3.8),'b_velvet',bevel=.15)
        for z in [-63.25,-62,-60.75]:decor(uid('sofa cushion'),(-212.5,.62,z),(1,.25,1.15),'b_velvet',bevel=.1)
        for z in [-64,-60]:box(uid('sofa arm'),(-212.6,.7,z),(1.3,.95,.3),'b_walnut',bevel=.09)
        box(uid('lounge coffee table'),(-209,.42,-62),(1.4,.8,2.4),'b_walnut',bevel=.08)
        # Security desk with screens, divider grille and locker bank.
        box(uid('security desk'),(-212,.7,5),(1.2,1.35,3.6),'b_walnut',bevel=.06)
        for z in [4,5.1,6.2]:
            decor(uid('security monitor'),(-212,1.7,z),(.15,.6,.85),'steel')
            decor(uid('security screen'),(-211.91,1.7,z),(.025,.48,.72),'b_glass0')
        for z in [10,11.1,12.2]:box(uid('security locker'),(-214,1.05,z),(.8,2.1,1),'steel',bevel=.06)
        for z in [-54,-30,-6,18]:
            decor(uid('service ceiling strip'),(-197,4.08,z),(3,.08,.15),'b_emissive')
            lamp(uid('service corridor light'),(-197,3.8,z),'#c9d8dd',75,20)
    with context('Bellagio / south arrival and lakefront'):
        # Glass arrival pavilion at the exposed lake-side portal. The old south
        # portico sits under the guest wing, so retains its low stone/roof profile.
        arrival=build_arrival()
        for c in arrival['colliders']:
            level.colliders.append(BoxCollider(c['name'],c['position'],c['size'],c['yaw'],c['group']))
        for light in arrival['lights']:
            lamp(light['name'],light['position'],light['color'],light['intensity'],light['distance'])
        for x in [-170,-140]:
            for z in [-91,-79]:column('portico column',x,z,h=6.1,r=.58)
        box(uid('portico roof'),(-155,6.45,-85),(33,.7,16),'b_travertine')
        for z,yaw in [(-93,math.pi),(-77,0)]:
            for x in [-165,-155,-145]:arch('portico open arch',(x,0,z),8.1,6,.42,yaw,glass=None,frame=.42)
        # Hipped roofs are full solids with sloping profiles, not boxes with pyramid hats.
        def hip(n,cx,cz,w,d,y,h):
            vs=[(cx-w/2,y,cz-d/2),(cx+w/2,y,cz-d/2),(cx+w/2,y,cz+d/2),(cx-w/2,y,cz+d/2),(cx, y+h,cz-d/2+3),(cx,y+h,cz+d/2-3)]
            mesh(n,vs,[(0,1,4),(1,2,5,4),(2,3,5),(3,0,4,5),(3,2,1,0)],'b_roof')
            # Individual tile ribs catch grazing light, with restrained thickness.
            for i in range(int(d/.55)):
                zz=cz-d/2+.3+i*.55
                if cz-d/2+3<zz<cz+d/2-3:
                    for side in [-1,1]:beam(uid('terracotta roof roll'),(cx,y+h+.035,zz),(cx+side*w/2,y+.035,zz),.045,'b_roof',6)
        hip('arrival pavilion roof',-155,-85,34,17,6.8,2.4)
        for cz in [-54,-10]:
            box(uid('lakefront restaurant'),(-125.5,3.6,cz),(10.6,7.2,22),'b_plaster')
            hip('restaurant hipped roof',-125.5,cz,12,24,7.3,3)
            for zz in [cz-7,cz,cz+7]:arch('restaurant tall arched window',(-120.1,1,zz),4.2,5.4,.26,math.pi/2,frame=.32)
            lathe('restaurant lantern',-125.5,cz,[(1.8,10),(1.8,11.3),(2.0,11.5),(1.4,12.2),(.2,13)],'b_travertine',32)
        # Shaped lake, ring fountain plumbing and dimensional balustrade.
        cx,cz=-90,-10;rx,rz=27,69;N=96
        verts=[(cx,.045,cz)]+[(cx+rx*math.cos(a),.045,cz+rz*math.sin(a)) for a in np.linspace(0,math.tau,N,endpoint=False)]
        mesh('remaining fountain water',verts,[(0,i+1,(i+1)%N+1) for i in range(N)],'b_water')
        for i in range(N):
            a=i*math.tau/N;b=(i+1)*math.tau/N
            # Curved retaining wall expressed as convex masonry segments with overlapping ends.
            pts=[(cx+(rx+rr)*math.cos(t),cz+(rz+rr)*math.sin(t)) for rr,t in [(0,a),(0,b),(.85,b),(.85,a)]]
            prism(uid('lake coping'),pts,0,.45,'b_travertine')
            mid=(a+b)/2;px=cx+(rx+.45)*math.cos(mid);pz=cz+(rz+.45)*math.sin(mid)
            lathe('shore baluster',px,pz,[(.13,.45),(.14,.58),(.065,.73),(.11,.91),(.08,1.18),(.15,1.23)],'b_travertine',12)
            beam(uid('shore handrail'),(cx+(rx+.45)*math.cos(a),1.25,cz+(rz+.45)*math.sin(a)),(cx+(rx+.45)*math.cos(b),1.25,cz+(rz+.45)*math.sin(b)),.10,'b_travertine',8)
        for i in range(58):
            a=i*math.tau/58;x=cx+17*math.cos(a);z=cz+47*math.sin(a)
            lathe('fountain nozzle',x,z,[(.11,.07),(.11,.19),(.055,.26)],'b_bronze',12)
        # Evidence of collapse is modeled broken masonry and fallen rails, away from route centerlines.
        for i in range(90):
            x=rng.uniform(-188,-136);z=rng.choice([rng.uniform(-98,-95),rng.uniform(46,49)])
            h=rng.uniform(.12,.48);decor(uid('fallen cornice fragment'),(x,h/2,z),(rng.uniform(.2,1.1),h,rng.uniform(.2,.7)),'b_travertine',yaw=rng.random()*6.28,bevel=.07)
        for i in range(7):
            z=-60+i*17
            if z>18:continue  # Keep fallen railing out of the covered arrival court.
            beam(uid('broken frontage rail'),(-120,0.3,z),(-121.2,.45,z+1.9),.07,'b_bronze',8)
    # Traversal samples are floor-level waypoints; architectural envelopes above validate ceilings.
    points={'bellagio_south_path':(-111,-103),'bellagio_arcade_approach':(-136,-99.4),'bellagio_arrival':(-155,-99.4),'bellagio_portico':(-155,-85),'bellagio_lobby_route':(-155,-61),'bellagio_lobby_north':(-161,-48),'bellagio_casino_south':(-161,-37),'bellagio_casino_mid':(-161,-10),'bellagio_casino_cross':(-161,12),'bellagio_gallery':(-161,34),'bellagio_east_exit':(-123,34),'bellagio_north_path':(-123,78),'bellagio_north_return':(-66,96),'bellagio_service_approach':(-184,-51),'bellagio_service_lobby':(-184,-58),'bellagio_corridor_south':(-197,-58),'bellagio_corridor_stores':(-197,-36),'bellagio_corridor_medical':(-197,-14),'bellagio_corridor_security':(-197,8),'bellagio_corridor_north':(-197,12),'bellagio_service_casino':(-184,12)}
    for n,(x,z) in points.items():volume(n,(x,1.5,z),(2.2,3,2.2),roofed=False,tags=['route','bellagio'])
    routes=[['food_exit','bellagio_south_path','bellagio_arcade_approach','bellagio_arrival','bellagio_portico','bellagio_lobby_route','bellagio_lobby_north','bellagio_casino_south','bellagio_casino_mid','bellagio_casino_cross','bellagio_gallery','bellagio_east_exit','bellagio_north_path','bellagio_north_return','west_north'],['bellagio_lobby_north','bellagio_service_approach','bellagio_service_lobby','bellagio_corridor_south','bellagio_corridor_stores','bellagio_corridor_medical','bellagio_corridor_security','bellagio_corridor_north','bellagio_service_casino','bellagio_casino_cross']]
    for chain in routes:
        for a,b in zip(chain,chain[1:]):link(a,b)
    for room,route in [('staff_lounge','bellagio_corridor_south'),('stores','bellagio_corridor_stores'),('medical','bellagio_corridor_medical'),('security','bellagio_corridor_security')]:link(route,'bellagio_'+room,door='bellagio_'+room)
    landmark('bellagio_front_view',(-42,.2,-18),tags=['viewpoint'])
    landmark('bellagio_entrance',(-155,.1,-85),tags=['entrance'])
    landmark('bellagio_casino',(-161,.1,-10),tags=['casino'])
    landmark('bellagio_gallery',(-161,.1,34),tags=['exit'])
    print('Bellagio rooms, lake and route graph complete',flush=True)
    return {'foodPosition':[-208,.1,-36],'foodTitle':'BELLAGIO / PROVISIONS','hordePosition':[-209,0,-58],'hordeExits':[[-202,.1,-58],[-197,.1,-49]],'interiorBounds':{'minX':-216,'maxX':-130,'minZ':-77,'maxZ':43}}
