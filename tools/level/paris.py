"""Paris Las Vegas: Bordeaux frontage, Eiffel lattice and accessible observation deck."""
import math, random
import bpy
from mathutils import Matrix
from bmlevel import mat, context, slab, prism, door, volume, link, landmark, lamp, level, scene
from bmlevel.core import BoxCollider, HullCollider


def build_paris(api):
    box,decor,beam=api['box'],api['decor'],api['beam']
    serial=0
    def uid(s):
        nonlocal serial
        serial+=1;return f'Paris {serial:05d} {s}'
    def D(s,p,size,m='p_stone',**kw):return decor(uid(s),p,size,m,**kw)
    def B(s,p,size,m='p_stone',**kw):return box(uid(s),p,size,m,**kw)
    def line(s,a,b,r=.06,m='p_iron'):beam(uid(s),a,b,r,m,8)
    def mesh(s,vs,fs,m):
        me=bpy.data.meshes.new(uid(s));me.from_pydata([(x,-z,y) for x,y,z in vs],[],fs);me.update();ob=bpy.data.objects.new(me.name,me);scene.collection.objects.link(ob);me.materials.append(bpy.data.materials[m]);level.visual_points.extend(vs);return ob
    def lathe(s,x,z,profile,m,n=48):
        vs=[(x+r*math.cos(i*math.tau/n),y,z+r*math.sin(i*math.tau/n)) for r,y in profile for i in range(n)]
        fs=[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(len(profile)-1) for i in range(n)]
        fs +=[tuple(reversed(range(n))),tuple(range((len(profile)-1)*n,len(profile)*n))]
        return mesh(s,vs,fs,m)
    def capture():
        return (set(bpy.data.objects),len(level.colliders),len(level.volumes),len(level.landmarks),len(level.lights),len(level.visual_points))
    def rotate_part(mark,cx,cz,angle):
        # One transform for art AND physics/metadata; never rotate just the GLB.
        c,si=math.cos(angle),math.sin(angle)
        def P(p):
            x,y,z=p;dx,dz=x-cx,z-cz
            return (cx+c*dx+si*dz,y,cz-si*dx+c*dz)
        bpy.context.view_layer.update()
        transform=Matrix.Translation((cx,-cz,0)) @ Matrix.Rotation(angle,4,'Z') @ Matrix.Translation((-cx,cz,0))
        for ob in set(bpy.data.objects)-mark[0]:ob.matrix_world=transform @ ob.matrix_world
        for collider in level.colliders[mark[1]:]:
            if isinstance(collider,BoxCollider):collider.position=P(collider.position);collider.yaw+=angle
            else:collider.vertices=[v for i in range(0,len(collider.vertices),3) for v in P(collider.vertices[i:i+3])]
        for records,start in [(level.volumes,mark[2]),(level.landmarks,mark[3]),(level.lights,mark[4])]:
            for item in records[start:]:
                item.position=P(item.position)
                if hasattr(item,'yaw'):item.yaw+=angle
                if hasattr(item,'target'):item.target=P(item.target)
        level.visual_points[mark[5]:]=[P(p) for p in level.visual_points[mark[5]:]]
    def roof(s,x,z,w,d,y,h,material='p_slate'):
        vs=[(x+sx*ww/2,yy,z+sz*dd/2) for ww,dd,yy in [(w,d,y),(w*.73,d*.83,y+h*.8),(w*.70,d*.80,y+h)] for sx,sz in [(-1,-1),(1,-1),(1,1),(-1,1)]]
        fs=[(3,2,1,0),(8,9,10,11)]+[(k*4+i,k*4+(i+1)%4,(k+1)*4+(i+1)%4,(k+1)*4+i) for k in range(2) for i in range(4)]
        mesh(s,vs,fs,material)
        D('roof ridge',(x,y+h+.12,z),(w*.73,.25,d*.83),'p_zinc')
    def arch(x,y,z,w,h,yaw= -math.pi/2,pane=True):
        c,s=math.cos(yaw),math.sin(yaw)
        def P(u,v,o):return (x+c*u+s*o,y+v,z-s*u+c*o)
        r=w/2;spring=h-r
        if pane:
            D('recessed window',P(0,spring/2,0),(w,spring,.10),'p_glass',yaw=yaw)
            pts=[P(0,spring,0)]+[P(r*math.cos(i*math.pi/24),spring+r*math.sin(i*math.pi/24),0) for i in range(25)]
            mesh('arched glass',pts,[tuple(range(len(pts)))],'p_glass')
        for side in [-1,1]:D('arch pier',P(side*(r+.15),spring/2,.12),(.3,spring,.35),yaw=yaw)
        for i in range(24):
            a,b=i*math.pi/24,(i+1)*math.pi/24
            vs=[P(rr*math.cos(t),spring+rr*math.sin(t),o) for o in [-.05,.3] for rr,t in [(r,a),(r,b),(r+.3,b),(r+.3,a)]]
            mesh('voussoir',vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'p_stone')
        D('arch keystone',P(0,h+.05,.22),(.45,.5,.5),yaw=yaw)
        if pane:
            D('window transom',P(0,spring,.1),(w,.06,.08),'p_iron',yaw=yaw)
            D('window mullion',P(0,spring/2,.1),(.06,spring,.08),'p_iron',yaw=yaw)
    for n,c,m,r,g in [('p_stone',(.73,.68,.55),0,.72,0),('p_wall',(.61,.55,.44),0,.88,0),('p_slate',(.045,.19,.30),.35,.6,0),('p_zinc',(.22,.28,.33),.7,.4,0),('p_iron',(.44,.37,.27),.7,.52,0),('p_gilt',(.63,.38,.09),.75,.35,0),('p_glass',(.04,.08,.10),.4,.25,0),('p_red',(.30,.025,.03),0,.9,0),('p_blue',(.025,.08,.32),.2,.5,0),('p_light',(1,.59,.18),.2,.3,2)]:mat(n,c,metal=m,roughness=r,glow=g)
    # Reuse packed mineral textures, keeping a consistent real-world stone palette.
    for target,source in [('p_stone','b_travertine'),('p_wall','b_plaster')]:
        src=bpy.data.materials[source];dst=bpy.data.materials[target];bs=dst.node_tree.nodes.get('Principled BSDF')
        for node in src.node_tree.nodes:
            if node.type=='TEX_IMAGE':
                tex=dst.node_tree.nodes.new('ShaderNodeTexImage');tex.image=node.image;dst.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color']);break
    with context('Paris / Bordeaux hotel'):
        # Articulated tall wings with projecting pavilion ends, steep blue mansards and dormers.
        wing_specs=[(173,-75+direction*29,16,60,96,angle) for angle in [-30,30] for direction in [-1,1]]
        wing_specs += [(173,-75+direction*57,22,16,99,angle) for angle in [-30,30] for direction in [-1,1]]
        wing_specs += [(173,-75,25,25,103,0)]
        for x,z,w,d,h,angle in wing_specs:
            wing=capture()
            B('hotel stone body',(x,h/2,z),(w,h,d),'p_wall')
            for yy in [9,13,28,62,h-2,h]:D('profiled cornice',(x,yy,z),(w+.9,.55,d+.9))
            roof('mansard roof',x,z,w+1.7,d+1.7,h+.3,10)
            for side in [-1,1]:
                xx=x+side*(w/2+.12)
                for zz in range(int(z-d/2+3),int(z+d/2-1),4):
                    for yy in range(16,int(h-3),3):
                        D('window recess',(xx,yy,zz),(.18,2.15,1.9),'p_glass')
                        D('window sill',(xx+side*.16,yy-1.15,zz),(.45,.14,2.25))
                        if yy%3==1:D('window center bar',(xx+side*.13,yy,zz),(.09,2.15,.045),'p_zinc')
                    D('engaged pilaster',(xx+side*.06,(h+12)/2,zz-1.7),(.27,h-12,.26))
                    D('dormer body',(xx-side*1.6,h+2.2,zz),(2.2,3.7,2.6))
                    arch(xx+side*.03,h+.8,zz,1.45,2.7,math.pi/2 if side>0 else -math.pi/2)
                    roof('dormer cap',xx-side*1.4,zz,3,3,h+4,1.5)
            for zz in [z-d/2-.1,z+d/2+.1]:
                for xx in range(int(x-w/2+3),int(x+w/2-1),4):
                    for yy in range(16,int(h-3),3):D('end facade window',(xx,yy,zz),(1.9,2.15,.15),'p_glass')
            # Sculpted dormer crowns and a layered pavilion roofline.
            for zz in range(int(z-d/2+4),int(z+d/2-1),8):
                arch(x-w/2-.30,h+1,zz,2.8,5.8)
                lathe('dormer crest',x-w/2-.38,zz,[(.35,h+7.0),(.5,h+7.4),(.25,h+7.8),(.07,h+8.4)],'p_stone',16)
            for zz in [z-d/2,z+d/2]:
                for xx in [x-w/2,x+w/2]:lathe('roof finial',xx,zz,[(.4,h+5),(.35,h+7),(.08,h+10)],'p_gilt',16)
            rotate_part(wing,173,-75,math.radians(angle))
    with context('Paris / casino and French street'):
        slab('Paris casino floor',(105,-35),(66.6,90.6),'b_darkmarble',y=.015,thickness=.4)
        slab('Paris casino ceiling',(105,-35),(66.6,90.6),'p_wall',y=8.5,thickness=.5)
        # West entrance 6m wide, north exit 5m wide.
        for za,zb in [(-80,-42),(-36,10)]:B('west envelope',(72,4,(za+zb)/2),(.6,8,zb-za+.03),'p_wall')
        B('entry header',(72,6.4,-39),(.65,3.2,6.05),'p_wall')
        B('east envelope',(138,4,-35),(.6,8,90),'p_wall')
        B('south envelope',(105,4,-80),(66,8,.6),'p_wall')
        for xa,xb in [(72,117.5),(122.5,138)]:B('north envelope',((xa+xb)/2,4,10),(xb-xa+.03,8,.6),'p_wall')
        B('north exit header',(120,6.4,10),(5.05,3.2,.65),'p_wall')
        door('paris_west_entrance',(72,0,-39),yaw=math.pi/2,width=6,height=4.8,animation='slide',auto_open_radius=7)
        door('paris_north_exit',(120,0,10),width=5,height=4.8,animation='slide',auto_open_radius=6)
        volume('paris_casino_envelope',(105,4,-35),(66,8,90),tags=['indoors','casino'])
        # Continuous Louvre-style frontage; a single tall end pavilion replaces the repeated huts.
        B('Louvre street upper facade',(70.6,12,-65),(10,7,30),'p_wall')
        B('Louvre lower facade',(65.7,4,-65),(.65,8,30),'p_wall')
        for z in [-76,-70,-64,-58,-52]:
            arch(65.25,.7,z,3.5,5.8)
            arch(65.25,9,z,2.8,5.5)
            for dz in [-2.1,2.1]:D('Louvre facade pilaster',(65,11.9,z+dz),(.55,6.3,.38))
            D('Louvre window pediment',(65,14.8,z),(.8,.38,3.4))
        for y in [7.9,8.7,15.9,16.6]:D('Louvre continuous cornice',(69,y,-65),(12,.4,31))
        for z in range(-79,-49):
            lathe('Louvre parapet baluster',64.5,z,[(.12,16.8),(.16,17),(.10,17.4),(.14,17.8)],'p_stone',12)
        D('Louvre parapet rail',(64.5,18,-65),(.4,.25,31))
        # Recessed connecting gallery behind the front Eiffel foot keeps the portal legible.
        B('connecting gallery upper',(73,11,-38),(3,5,24),'p_wall')
        for z in [-47,-40,-33,-27]:arch(71.3,9,z,3.5,4)
        D('connecting gallery cornice',(72,14,-38),(5,.5,25))
        # Opera-style pavilion: paired columns, balustrade and a ribbed copper dome.
        B('opera upper pavilion',(71,15,-9),(10,13,25),'p_wall')
        B('opera lower facade',(65.7,4,-9),(.65,8,25),'p_wall')
        for z in [-19,-14,-9,-4,1]:
            arch(65.3,.8,z,3.1,5.8)
            arch(65.3,9,z,2.7,7.8)
            for dz in [-1.85,1.85]:
                lathe('opera paired column',64.8,z+dz,[(.32,8.5),(.32,8.8),(.21,9.1),(.20,17.5),(.34,17.8),(.34,18.2)],'p_stone',20)
        for y,w in [(8.2,27),(18.4,28),(19.3,29),(20.1,28)]:D('opera entablature',(69,y,-9),(13,.55,w))
        for z in range(-22,5):
            lathe('opera baluster',63.0,z,[(.1,20.4),(.15,20.6),(.09,21),(.12,21.4)],'p_stone',12)
        D('opera balustrade cap',(63,21.5,-9),(.35,.18,27))
        profile=[(8.4,21.0),(8.4,22.0),(7.8,22.6),(7.1,23.8),(5.8,25.2),(3.9,26.4),(1.2,27.3),(.2,28.0)]
        lathe('opera copper dome',74,-9,profile,'p_zinc',64)
        for i in range(24):
            a=i*math.tau/24
            for (r,y),(rr,yy) in zip(profile,profile[1:]):line('opera dome rib',(74+r*math.cos(a),y,-9+r*math.sin(a)),(74+rr*math.cos(a),yy,-9+rr*math.sin(a)),.065,'p_gilt')
        mesh('opera central pediment',[(62.3,20.3,-19),(62.3,20.3,1),(62.3,25.5,-9),(63,20.3,-19),(63,20.3,1),(63,25.5,-9)],[(0,2,1),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)],'p_stone')
        arch(62.1,21,-9,4,3.2)
        for z in [-21,3]:
            lathe('opera corner cupola',65,z,[(1.5,20.3),(1.5,22),(1.2,23),(.5,24),(.15,24.8)],'p_stone',32)
        D('opera terrace canopy',(60.5,5.7,-9),(7,.4,27),'p_zinc')
        for z in [-21,-15,-3,3]:lathe('terrace column',58,z,[(.26,0),(.26,.3),(.17,5.4),(.30,5.6)],'p_stone',16)
        # Tall Louvre-like left roof pavilion and broad sculpted central dormer.
        B('south entrance pavilion upper',(71,16,-70),(10,15,16),'p_wall')
        roof('south steep pavilion',71,-70,13,19,23.5,8)
        arch(65.6,14,-70,4.0,7.8)
        D('south pavilion cornice',(65.8,23,-70),(1,.8,18))
        arch(65.5,24,-70,3.5,7)
        for z in [-76,-64]:lathe('south pavilion roof crest',66,z,[(.45,24),(.4,25),(.15,28)],'p_stone',20)
        # Roof services and raised skylights read from the observation deck.
        for x in [106,128]:
            for z in [-69,-10]:
                D('roof skylight curb',(x,8.8,z),(8,.65,9),'p_zinc')
                roof('glazed roof lantern',x,z,7,8,9.1,2)
                for dz in [-3,-1,1,3]:D('roof glazing',(x,10.77,z+dz),(4,.06,1.2),'p_glass')
        for z in [-75,-7]:
            for x in [116,121]:D('roof ventilation',(x,9,z),(2.7,1.2,2.8),'p_zinc')
        # Grand west portal with paired columns and deep pediment.
        for z in [-44,-34]:
            lathe('entry column',69,z,[(.6,0),(.6,.3),(.42,.6),(.36,6.6),(.6,6.8),(.6,7.1)],'p_stone')
        D('entrance entablature',(69,7.6,-39),(3,1,12))
        mesh('portal pediment',[(67.4,8.1,-45),(67.4,8.1,-33),(67.4,10,-39),(68.1,8.1,-45),(68.1,8.1,-33),(68.1,10,-39)],[(0,2,1),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)],'p_stone')
        api['text']('Paris entry','P A R I S',(67.35,7.35,-39),'p_gilt',yaw=-math.pi/2,size=.65)
        # Casino avenues stay clear around the lift and under the tower's real steel legs.
        D('casino carpet',(105,.045,-35),(63,.04,87),'b_carpet')
        D('entry marble avenue',(103,.09,-39),(62,.04,6),'b_marble')
        D('north marble avenue',(120,.1,-12),(5,.04,43),'b_marble')
        for x in [80,105,130]:
            for z in [-70,-14,2]:
                lathe('interior column',x,z,[(.5,0),(.5,.2),(.32,.5),(.3,7.3),(.55,7.5),(.55,8)],'p_stone',24)
        for x in [83,108,130]:
            for z in [-64,-12]:
                B('roulette pedestal',(x,.55,z),(1.1,1.1,1.1),'b_walnut')
                lathe('roulette table',x,z,[(2.2,1),(2.2,1.15)],'b_walnut')
                lathe('green table felt',x,z,[(2,1.15),(2,1.17)],'b_felt')
                lathe('roulette bowl',x,z,[(.62,1.17),(.70,1.27),(.52,1.31)],'p_gilt')
                for j in range(7):
                    a=j*math.tau/7;lathe('velvet stool',x+2.7*math.cos(a),z+2.7*math.sin(a),[(.28,0),(.1,.5),(.38,.65),(.38,.8)],'p_red',16)
        # Small banks of abandoned gaming cabinets, every screen and control shelf modeled.
        for z in [-72,-57,0]:
            for x in [92,94,96,110,112,114]:
                B('slot machine cabinet',(x,.95,z),(1.1,1.9,.8),'p_iron')
                D('slot screen',(x,1.43,z-.43),(.82,.8,.08),'p_blue')
                D('slot brass frame',(x,1.91,z-.43),(1,.09,.13),'p_gilt')
                D('slot controls',(x,.88,z-.6),(1,.14,.5),'p_zinc')
                for dx in [-.3,0,.3]:D('slot illuminated reel',(x+dx,1.44,z-.49),(.16,.35,.035),'p_light')
        for z in [-65,-20,2]:
            for x in [86,115,132]:
                D('ceiling coffer',(x,7.8,z),(10,.25,10),'p_stone')
                lathe('chandelier',x,z,[(1.2,6.4),(1.3,6.6),(1.1,6.8)],'p_gilt')
                for j in range(12):
                    a=j*math.tau/12;line('crystal pendant',(x+1.2*math.cos(a),5.8,z+1.2*math.sin(a)),(x+1.2*math.cos(a),6.5,z+1.2*math.sin(a)),.05,'p_light')
                lamp(uid('casino chandelier'),(x,5.9,z),'#ffcf93',120,24)
        landmark('paris_hide',(131,.1,-72),tags=['horde-hide','future-mission'])
        landmark('paris_supplies',(131,.1,-64),tags=['supply-staging'])
        for z in [-76,-73]:B('abandoned supplies',(134,.6,z),(2.4,1.2,1),'b_walnut')
    print('Paris hotel and casino built',flush=True)
    tower_mark=capture()
    with context('Paris / Eiffel Tower'):
        cx,cz=93,-39
        # Each leg is a tapered four-chord truss, with web bracing on all four faces.
        tiers=[(0,30,5.2),(12,20,4.8),(28,11,4.4),(57,7.2,2.8),(92,5.0,1.9),(132,2.8,1.3),(140,2.5,1.15)]
        for sx,sz in [(-1,-1),(-1,1),(1,-1),(1,1)]:
            B('masonry leg foundation',(cx+sx*30,.7,cz+sz*30),(6,1.4,6))
            for k in range(len(tiers)-1):
                ya,ra,wa=tiers[k];yb,rb,wb=tiers[k+1];steps=max(3,math.ceil((yb-ya)/3))
                def P(t,u,v):
                    rr=ra+(rb-ra)*t;ww=wa+(wb-wa)*t
                    return(cx+sx*rr+u*ww/2,ya+(yb-ya)*t,cz+sz*rr+v*ww/2)
                corners=[(-1,-1),(1,-1),(1,1),(-1,1)]
                for u,v in corners:line('tower truss chord',P(0,u,v),P(1,u,v),.38 if k<3 else .24)
                for j in range(steps):
                    a,b=j/steps,(j+1)/steps
                    for idx,(u,v) in enumerate(corners):
                        uu,vv=corners[(idx+1)%4]
                        line('leg lattice diagonal',P(a,u,v),P(b,uu,vv),.16 if k<3 else .105)
                        line('leg lattice cross',P(a,uu,vv),P(b,u,v),.16 if k<3 else .105)
                        line('leg horizontal tie',P(a,u,v),P(a,uu,vv),.15 if k<3 else .10)
                for j in range(steps+1):
                    for u,v in corners:
                        D('truss junction gusset',P(j/steps,u,v),(.78 if k<3 else .5,.75 if k<3 else .55,.78 if k<3 else .5),'p_iron')
                if k<2:
                    pts=[P(t,u,v) for t in [0,1] for u,v in corners]
                    level.colliders.append(HullCollider(uid('solid lower leg'),[c for p in pts for c in p]))
            # Discrete warm lamps on the main chords, no giant glowing bars.
            for y,r,w in tiers[:-1]:D('tower accent lamp',(cx+sx*r,y+1,cz+sz*r),(.22,.28,.22),'p_light')
        # The iconic curved base arches between each pair of splayed feet.
        for axis in [0,1]:
            for side in [-1,1]:
                for offset in [0,.85]:
                    pts=[]
                    for j in range(41):
                        t=j/40;u=-28+56*t;y=3+21*math.sin(math.pi*t)**.68+offset
                        pts.append((cx+u,y,cz+side*(29-17*math.sin(math.pi*t))) if axis==0 else (cx+side*(29-17*math.sin(math.pi*t)),y,cz+u))
                    for a,b in zip(pts,pts[1:]):line('curved Eiffel arch',a,b,.30)
                for j in range(1,40):
                    t=j/40;u=-28+56*t;y=3+21*math.sin(math.pi*t)**.68
                    p=(cx+u,y,cz+side*(29-17*math.sin(math.pi*t))) if axis==0 else (cx+side*(29-17*math.sin(math.pi*t)),y,cz+u)
                    line('arch web',p,(p[0],p[1]+.85,p[2]),.07)
        # Broad lower galleries; lattice becomes one narrowing shaft above the second floor.
        for y,r in [(28,16),(57,9)]:
            B('lower Eiffel platform',(cx,y,cz),(r*2,1.1,r*2),'p_iron')
            for side in [-1,1]:
                D('gallery cornice',(cx,y-.7,cz+side*r),(r*2+.5,.3,.5),'p_gilt')
                D('gallery cornice',(cx+side*r,y-.7,cz),(.5,.3,r*2+.5),'p_gilt')
                for i in range(-int(r)+1,int(r),2):
                    D('gallery window',(cx+i,y+1.4,cz+side*(r-.2)),(1.4,2,.15),'p_glass')
                    D('gallery window',(cx+side*(r-.2),y+1.4,cz+i),(.15,2,1.4),'p_glass')
            # Hipped restaurant canopy and exposed deep lattice girders.
            roof('Eiffel gallery hipped roof',cx,cz,r*2+.8,r*2+.8,y+2.6,2.5 if y==28 else 1.1,'p_iron')
            for axis in [0,1]:
                for side in [-1,1]:
                    for j in range(-int(r),int(r)):
                        def G(u,v):return (cx+u,v,cz+side*r) if axis==0 else (cx+side*r,v,cz+u)
                        line('gallery diamond girder',G(j,y-2.4),G(j+1,y-.6),.06)
                        line('gallery diamond girder',G(j+1,y-2.4),G(j,y-.6),.06)
                    line('gallery lower chord',G(-r,y-2.4),G(r,y-2.4),.16)
                    line('gallery upper chord',G(-r,y-.6),G(r,y-.6),.16)

        for y in range(60,132,4):
            r=7.2+(2.8-7.2)*(y-57)/75;rr=7.2+(2.8-7.2)*(y+4-57)/75
            for side in [-1,1]:
                line('upper shaft X',(cx-r,y,cz+side*r),(cx+rr,y+4,cz+side*rr),.18)
                line('upper shaft X',(cx+r,y,cz+side*r),(cx-rr,y+4,cz+side*rr),.18)
                line('upper shaft X',(cx+side*r,y,cz-r),(cx+side*rr,y+4,cz+rr),.18)
                line('upper shaft X',(cx+side*r,y,cz+r),(cx+side*rr,y+4,cz-rr),.18)
        # Visible central elevator guides and intermediate machinery.
        for z in [cz-1.4,cz+1.4]:line('elevator guide',(cx+1,8,z),(cx+1,140,z),.09,'p_zinc')
        # Compact chamfered octagonal deck. The old 16 m square cap overwhelmed the spire.
        outline=[(-5.2,-6.2),(5.2,-6.2),(6.2,-5.2),(6.2,5.2),(5.2,6.2),(-5.2,6.2),(-6.2,5.2),(-6.2,-5.2)]
        deck=[(cx+x,cz+z) for x,z in outline]
        prism('Paris Eiffel observation deck',deck,139.6,140,'p_iron')
        prism('Paris Eiffel observation canopy',deck,143.85,144.1,'p_iron')
        for a,b in zip(outline,outline[1:]+outline[:1]):
            dx,dz=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dz);yaw=math.atan2(-dz,dx)
            B('observation safety curb',(cx+(a[0]+b[0])/2,140.16,cz+(a[1]+b[1])/2),(length+.08,.32,.18),'p_iron',yaw=yaw)
            level.colliders.append(BoxCollider(uid('observation safety cage'),(cx+(a[0]+b[0])/2,141.95,cz+(a[1]+b[1])/2),(length+.08,3.9,.13),yaw,'environment'))
            for j in range(math.ceil(length/.3)+1):
                t=j/math.ceil(length/.3);x=cx+a[0]+dx*t;z=cz+a[1]+dz*t
                line('deck wire vertical',(x,140,z),(x,143.9,z),.012)
            for y in [140.3+i*.3 for i in range(12)]:line('deck wire horizontal',(cx+a[0],y,cz+a[1]),(cx+b[0],y,cz+b[1]),.012)
            for t in [0,.5]:
                x=cx+a[0]+dx*t;z=cz+a[1]+dz*t
                line('observation mullion',(x,140,z),(x,143.9,z),.085)
            line('observation handrail',(cx+a[0],141.1,cz+a[1]),(cx+b[0],141.1,cz+b[1]),.055)
            line('crown lower cornice',(cx+a[0],139.5,cz+a[1]),(cx+b[0],139.5,cz+b[1]),.13)
            line('crown upper cornice',(cx+a[0],144,cz+a[1]),(cx+b[0],144,cz+b[1]),.13)
        # Flared ribs visibly support the observation gallery.
        for i in range(8):
            a=i*math.tau/8
            line('observation support rib',(cx+2.7*math.cos(a),134,cz+2.7*math.sin(a)),(cx+6.1*math.cos(a),139.6,cz+6.1*math.sin(a)),.17)
        # Smaller cabins leave a generous circuit around the gallery.
        for y in [0,140]:
            B('lift back',(95,y+1.55,cz),(.2,3.1,3.3),'p_zinc')
            for dz in [-1.65,1.65]:B('lift side',(93,y+1.55,cz+dz),(4,3.1,.16),'p_zinc')
            B('lift ceiling',(93,y+3.2,cz),(4.2,.2,3.5),'p_iron')
            D('lift floor',(93,y+.055,cz),(4,.07,3.3),'p_zinc')
            D('elevator call panel',(91.2,y+1.3,cz+1.52),(.28,.5,.1),'p_gilt')
            D('elevator call lamp',(91.15,y+1.4,cz+1.46),(.1,.12,.03),'p_light')
            api['text']('lift signage','OBSERVATION / 140 M' if y==0 else 'CASINO / GROUND',(90.85,y+2.65,cz),'p_light',yaw=-math.pi/2,size=.22)
            landmark('paris_lift_ground' if y==0 else 'paris_lift_top',(92.5,y+.25,cz),yaw=-math.pi/2,tags=['elevator'])
            lamp(uid('lift lighting'),(92,y+2.6,cz),'#ffe2b4',65,9)
        # Open domed lantern with curved meridians and diamond wire, then a stepped finial.
        profile=[(4.5,144.2),(4.5,146.5),(4.1,148.4),(3.0,150.2),(1.5,151.5),(.55,152.2)]
        for i in range(24):
            a=i*math.tau/24;aa=(i+1)*math.tau/24
            for (r,y),(rr,yy) in zip(profile,profile[1:]):
                P=lambda rad,h,ang:(cx+rad*math.cos(ang),h,cz+rad*math.sin(ang))
                line('lantern curved rib',P(r,y,a),P(rr,yy,a),.075)
                line('lantern diamond',P(r,y,a),P(rr,yy,aa),.025)
                line('lantern diamond',P(r,y,aa),P(rr,yy,a),.025)
                line('lantern hoop',P(r,y,a),P(r,y,aa),.055)
        lathe('spire lantern core',cx,cz,[(.7,144),(.7,151),(1.1,151.2),(1.1,152),(.6,152.3),(.6,155),(.95,155.2),(.95,155.5),(.45,157),(.13,158)],'p_iron',32)
        line('Eiffel antenna',(cx,158,cz),(cx,165,cz),.09,'p_zinc')
        level.visual_points.append((cx,165,cz))
        D('aviation light',(cx,163,cz),(.18,.24,.18),'p_light')
        for z in [-42.5,-35.5]:
            lathe('observation telescope stand',88,z,[(.3,140),(.12,141),(.22,141.2)],'p_zinc',20)
            line('observation telescope',(87.7,141.5,z),(88.4,141.3,z),.17,'p_zinc')
        for n,x,z in [('w',89,-39),('nw',89,-35),('n',93,-35),('ne',97,-35),('e',97,-39),('se',97,-43),('s',93,-43),('sw',89,-43)]:
            volume('paris_deck_'+n,(x,141.8,z),(1.5,3.6,1.5),roofed=False,tags=['observation','route'])
        for a,b in zip(['w','nw','n','ne','e','se','s','sw'],['nw','n','ne','e','se','s','sw','w']):link('paris_deck_'+a,'paris_deck_'+b)
        volume('paris_observation_envelope',(cx,141.9,cz),(11.8,3.8,11.8),tags=['observation','enclosed'])
        volume('paris_lift_top',(92.5,141.5,cz),(2,3,2),roofed=False,tags=['elevator'])
        link('paris_deck_w','paris_lift_top')
        volume('paris_lift_ground',(92.5,1.5,cz),(2,3,2),roofed=False,tags=['elevator','indoors'])
        volume('paris_lift_approach',(88,1.5,cz),(2,3,2),roofed=False,tags=['route'])
    rotate_part(tower_mark,93,-39,math.pi/4)
    with context('Paris / Arc de Triomphe'):
        ax,az=88,39
        # 28 m-wide, 24 m-high monument, with an 11 m vaulted drive-through opening.
        for side in [-1,1]:
            B('Arc massive pier',(ax,8.25,az+side*9.75),(13,16.5,8.5),'p_stone')
            D('Arc pier plinth',(ax,.5,az+side*9.75),(14,1,9),'p_stone')
            for x in [ax-6.7,ax+6.7]:
                D('Arc inset relief panel',(x,7,az+side*9.6),(.18,7.5,5.7),'p_wall')
                for dz in [-3.1,3.1]:D('Arc relief border',(x,7,az+side*9.6+dz),(.3,8,.25))
                # Layered low relief shield and laurel forms, kept architectural at this scale.
                for j in range(9):
                    t=j*math.pi/8
                    D('Arc laurel relief',(x-.1,7+2.2*math.sin(t),az+side*9.6+2*math.cos(t)),(.42,.7,.45),'p_stone')
                D('Arc relief shield',(x-.12,6.8,az+side*9.6),(.45,2.5,1.9),'p_stone')
        B('Arc attic',(ax,20.4,az),(13,7.8,28),'p_stone')
        # Convex voussoir strips close the spandrels over the rounded vault.
        for j in range(32):
            a,b=j*math.pi/32,(j+1)*math.pi/32
            z1,z2=az+5.5*math.cos(a),az+5.5*math.cos(b)
            y1,y2=11+5.5*math.sin(a),11+5.5*math.sin(b)
            vs=[(x,y,z) for x in [ax-6.5,ax+6.5] for y,z in [(y1,z1),(y2,z2),(18,z2),(18,z1)]]
            mesh('Arc vaulted stone wedge',vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'p_stone')
            level.colliders.append(HullCollider(uid('Arc vault collider'),[c for v in vs for c in v]))
        for x,yaw in [(ax-6.7,-math.pi/2),(ax+6.7,math.pi/2)]:
            arch(x,0,az,11,16.5,yaw,pane=False)
            for side in [-1,1]:
                D('Arc attic frieze',(x,20,az+side*9),(.3,2.4,7),'p_wall')
                for dz in range(-3,4):D('Arc carved frieze block',(x-.15,20,az+side*9+dz),(.4,.85,.45),'p_stone')
        for y,h,w,d in [(16.6,.5,29,14),(17.3,.4,29.5,14.5),(23.3,.6,30,15),(24.1,.45,30.5,15.5)]:D('Arc layered cornice',(ax,y,az),(d,h,w),'p_stone')
        for z in range(az-14,az+15):D('Arc cornice dentil',(ax-7.2,22.8,z),(.6,.55,.45),'p_stone')
        landmark('paris_arc',(ax,0,az),tags=['landmark','walkthrough'])
        for n,x in [('west',61),('vault',88),('east',112)]:volume('paris_arc_'+n,(x,1.5,az),(3,3,3),roofed=False,tags=['route'])
        link('east_center','paris_arc_west');link('paris_arc_west','paris_arc_vault');link('paris_arc_vault','paris_arc_east');link('paris_arc_east','paris_exit')
    # Blue and gold balloon at the right-hand end of the frontage, beyond the opera pavilion.
    with context('Paris / balloon'):
        x,z=48,45
        lathe('balloon support',x,z,[(1,0),(.8,12),(2,13)],'p_gilt')
        profile=[(2.8,13),(4,15),(6,20),(6.7,24),(6,28),(4,31),(.4,33)]
        lathe('blue Montgolfier balloon',x,z,profile,'p_blue',64)
        for i in range(16):
            a=i*math.tau/16
            for (r,y),(rr,yy) in zip(profile,profile[1:]):line('balloon gold rib',(x+r*math.cos(a),y,z+r*math.sin(a)),(x+rr*math.cos(a),yy,z+rr*math.sin(a)),.085,'p_gilt')
        for y,r in [(15,4.1),(24,6.8),(28,6.1)]:lathe('balloon gilt band',x,z,[(r,y),(r,y+.2)],'p_gilt',64)
        api['text']('Paris balloon wordmark','Paris',(x-6.85,23,z),'p_light',yaw=-math.pi/2,size=1.7)
    for n,p in [('paris_street',(61,1.5,-39)),('paris_entry',(78,1.5,-39)),('paris_aisle',(120,1.5,-39)),('paris_north',(120,1.5,3)),('paris_exit',(120,1.5,17)),('paris_egress_corner',(115,1.5,-3))]:volume(n,p,(3,3,3),roofed=False,tags=['route'])
    link('east_center','paris_street');link('paris_street','paris_entry',door='paris_west_entrance');link('paris_entry','paris_lift_approach');link('paris_lift_approach','paris_lift_ground')
    # Route around the lift's rear wall, via the north side of the casino.
    volume('paris_cross_aisle',(80,1.5,-29),(3,3,3),roofed=False,tags=['route'])
    volume('paris_cross_east',(120,1.5,-29),(3,3,3),roofed=False,tags=['route'])
    link('paris_entry','paris_cross_aisle');link('paris_cross_aisle','paris_cross_east');link('paris_cross_east','paris_egress_corner');link('paris_egress_corner','paris_north');link('paris_north','paris_exit',door='paris_north_exit')
    print('Paris Eiffel Tower and observation routes built',flush=True)
    return {'towerCenter':[93,0,-39],'observationHeight':140,'height':165,'towerYaw':math.pi/4,'hotelWingYaw':[-math.pi/6,math.pi/6],'hotelFootprint':'X','hotelCore':[173,0,-75],'balloon':[48,0,45],'arc':[88,0,39],'liftGround':[93-.5/math.sqrt(2),.25,-39+.5/math.sqrt(2)],'liftTop':[93-.5/math.sqrt(2),140.25,-39+.5/math.sqrt(2)],'entrance':[72,0,-39]}
