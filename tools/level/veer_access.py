"""Permanent wayfinding from Crystals public doors to the streamed Veer stairs.
Decorative geometry only: the existing lobby floors, shafts and door leaves own
collision. Keep the six-metre mall gallery and native 1.78m doors clear.
"""
import bpy, bmesh, math, json
from pathlib import Path
from mathutils import Vector

PREFIX='CityCenter / Crystals / Veer access / '
FACES=[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)]

def build():
    groups={}
    for name,color,metal,glow in [
        ('va_charcoal',(.025,.055,.063),.38,0),
        ('va_champagne',(.56,.43,.19),.70,0),
        ('va_steel',(.36,.43,.44),.68,0),
        ('va_letter',(.88,.79,.54),.10,.35),
        ('va_light',(.90,.87,.71),.0,1.8)]:
        mat=bpy.data.materials.get(name) or bpy.data.materials.new(name)
        mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF')
        bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Metallic'].default_value=metal
        bs.inputs['Roughness'].default_value=.4
        bs.inputs['Emission Color'].default_value=(*color,1);bs.inputs['Emission Strength'].default_value=glow
        mat.diffuse_color=(*color,1)
    def mesh(vertices,faces,material,role='interior'):
        g=groups.setdefault((material,role),{'v':[],'f':[]});base=len(g['v'])
        g['v'] += [(x,-z,y) for x,y,z in vertices]
        g['f'] += [tuple(base+i for i in face) for face in faces]
    def transform(p,origin,yaw):
        x,y,z=p;c,s=math.cos(yaw),math.sin(yaw)
        return (origin[0]+c*x+s*z,origin[1]+y,origin[2]-s*x+c*z)
    def box(p,size,material,yaw=0,role='interior'):
        w,h,d=[v/2 for v in size]
        mesh([transform((x,y,z),p,yaw) for x in [-w,w] for y in [-h,h] for z in [-d,d]],FACES,material,role)
    def text(words,p,size,yaw=0,max_width=10,role='interior'):
        curve=bpy.data.curves.new('Veer lettering','FONT');curve.body=words;curve.align_x='CENTER';curve.align_y='CENTER'
        curve.size=size;curve.resolution_u=5;curve.extrude=.004
        ob=bpy.data.objects.new('Veer lettering',curve);bpy.context.scene.collection.objects.link(ob)
        bpy.context.view_layer.update();me=bpy.data.meshes.new_from_object(ob.evaluated_get(bpy.context.evaluated_depsgraph_get()))
        xs=[v.co.x for v in me.vertices];scale=min(1,max_width/max(.001,max(xs)-min(xs)))
        mesh([transform((v.co.x*scale,v.co.y,v.co.z),p,yaw) for v in me.vertices],[tuple(f.vertices) for f in me.polygons],'va_letter',role)
        bpy.data.objects.remove(ob,do_unlink=True);bpy.data.meshes.remove(me)
    def panel(p,yaw,lines,width=6,role='interior',arrows=None,hanging=False):
        box(p,(width,1.22,.18),'va_charcoal',yaw,role)
        for y in [-.59,.59]:box(transform((0,y,.105),p,yaw),(width,.035,.045),'va_champagne',yaw,role)
        for i,line in enumerate(lines):text(line,transform((0,.26-i*.49,.105),p,yaw),.34 if i==0 else .20,yaw,width-1.1,role)
        if arrows:
            # A readable mesh arrow, independent of font glyph coverage.
            for direction,row in arrows:
                y=.26-row*.49;cx=-width/2+.45
                points=[(-.23,-.045),(.08,-.045),(.08,-.14),(.27,0),(.08,.14),(.08,.045),(-.23,.045)]
                theta={'right':0,'left':math.pi,'up':math.pi/2}[direction]
                cs,sn=math.cos(theta),math.sin(theta)
                verts=[transform((cx+cs*x-sn*yy,y+sn*x+cs*yy,.112),p,yaw) for x,yy in points]
                mesh(verts,[tuple(range(len(verts)))],'va_letter',role)
        if hanging:
            for x in [-width*.32,width*.32]:box(transform((x,(6.03-p[1]+.61)/2,0),p,yaw),(.03,6.03-p[1]-.61,.03),'va_steel',yaw,role)

    # Street signs on the actual Crystals doors. There is deliberately no false
    # residential door in the leaning tower curtain wall eighteen metres above.
    panel((-93,5.25,470.39),0,['VEER RESIDENCES','ENTER CRYSTALS  /  EAST + WEST TOWERS'],7.5,'shell')
    panel((-31.60,5.25,381),math.pi/2,['VEER RESIDENCES','ENTRANCES INSIDE CRYSTALS'],7.5,'shell')
    # Each change of direction has a sign seen from the incoming walk direction.
    panel((-93,3.9,456.6),0,['VEER EAST','VEER WEST  /  CONTINUE AHEAD'],5,arrows=[('left',0),('up',1)],hanging=True)
    panel((-93,3.9,450.2),math.pi,['VEER EAST','RESIDENCES  /  STAIRS'],5,arrows=[('right',0)],hanging=True)
    panel((-89,3.9,381),math.pi/2,['VEER RESIDENCES','FOLLOW THE SOUTH ARCADE'],5,arrows=[('left',0)],hanging=True)
    panel((-92,3.9,394),math.pi,['VEER WEST','VEER EAST  /  CONTINUE AHEAD'],5,arrows=[('right',0),('up',1)],hanging=True)
    panel((-93,3.9,399),0,['VEER WEST','RESIDENTIAL ENTRANCE'],5,arrows=[('left',0)],hanging=True)
    panel((-160,3.9,397),math.pi/2,['VEER WEST','RESIDENTIAL ENTRANCE'],5,arrows=[('left',0)],hanging=True)
    panel((-163,3.9,419),math.pi,['VEER WEST','RESIDENCES  /  STAIRS'],5,arrows=[('right',0)],hanging=True)
    towers=json.loads(Path('src/work/hotels/towers.json').read_text())
    for t in towers:
        if t['set']!='veer':continue
        x,_,z=t['origin'];front=x+5.65;side='EAST' if t['id']=='veer-east' else 'WEST'
        # Champagne verticals and a shallow illuminated canopy frame the
        # existing stair leaf. All new jambs sit beyond the native clear width.
        for dz in [-1.30,1.30]:
            box((front,1.57,z+dz),(.26,3.0,.32),'va_champagne')
            box((front+.145,1.57,z+dz),(.028,2.84,.045),'va_light')
        box((front,3.13,z),(.28,.22,2.92),'va_champagne')
        panel((front+.05,4.05,z),math.pi/2,['V E E R',side+' RESIDENCES'],6)
        box((front+.8,4.88,z),(2.2,.18,6.7),'va_charcoal')
        box((front+1.75,4.78,z),(.04,.04,6.3),'va_light')
        for dz in [-2.9,2.9]:
            # Slats are flush to existing solid shaft piers, away from entry.
            for k in range(6):box((front-.04,1.6,z+dz+(k-2.5)*.085),(.16,2.85,.035),'va_steel')
        text('APARTMENTS  /  LEVELS 7 - 40',(front+.15,3.34,z),.14,math.pi/2,4.7)
    made=[]
    for (material,role),g in groups.items():
        me=bpy.data.meshes.new(PREFIX+material);me.from_pydata(g['v'],[],g['f']);me.update()
        bm=bmesh.new();bm.from_mesh(me)
        # Recalculate closed trim solids; lettering and arrow planes retain
        # their authored outward-facing orientation.
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
        me.materials.append(bpy.data.materials[material]);ob=bpy.data.objects.new(PREFIX+material+' / '+role,me)
        bpy.context.scene.collection.objects.link(ob);ob['visibilityRole']=role;made.append(ob)
    return made

if __name__=='__main__':
    import hashlib
    path=Path('build/hotels/shell-report.json');report=json.loads(path.read_text())
    for name,digest in report['sourceSHA256'].items():
        with open('build/level/'+name,'rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==digest,'Source changed since staging'
    for file in ['build/level/vegas.blend','build/hotels/staged-vegas.blend']:
        bpy.ops.wm.open_mainfile(filepath=str(Path(file).resolve()))
        bpy.data.batch_remove([o for o in bpy.data.objects if o.name.startswith(PREFIX)])
        build();bpy.ops.wm.save_as_mainfile(filepath=str(Path(file).resolve()))
    with open('build/level/vegas.blend','rb') as f:report['sourceSHA256']['vegas.blend']=hashlib.file_digest(f,'sha256').hexdigest()
    report['repairs']=list(dict.fromkeys(report.get('repairs',[])+['veer-residential-wayfinding']))
    path.write_text(json.dumps(report,indent=2));print('Veer entrance surrounds and public approach signs installed',flush=True)
