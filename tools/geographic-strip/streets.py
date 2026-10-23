"""Physical street sections and pedestrian bridge kits, in game-space metres."""
import json, math
import numpy as np
import mapbox_earcut
from pathlib import Path
from shapely.geometry import Polygon, LineString, Point, box, shape
from shapely.ops import unary_union, transform, triangulate, substring
from shapely import make_valid
from shapely.prepared import prep
from shapely.strtree import STRtree
from shapely.geometry.polygon import orient
from surface_geometry import triangles, tiles, ROAD_Y, WALK_Y, SLAB_BOTTOM, street_y

SPHERE_BRIDGE = 1197488766
PUBLIC = {'primary', 'secondary', 'tertiary', 'unclassified', 'residential', 'living_street'}

def county_geometry(root, origin):
    folder = root / 'build/geographic-strip/county'
    if not (folder / 'pavement.geojson').exists():
        return Polygon(), Polygon(), dict(pavement=0, sidewalks=0)
    radius = 6378137
    def project(x, y, z=None):
        return (radius * math.radians(x-origin[0]) * math.cos(math.radians(origin[1])),
                -radius * math.radians(y-origin[1]))
    bounds = box(*project(-115.193,36.153), *project(-115.147,36.079))
    def geometry(f):
        return make_valid(transform(project, shape(f['geometry']))).intersection(bounds)
    pavement = json.loads((folder/'pavement.geojson').read_text())['features']
    road = unary_union([geometry(f).buffer(0) for f in pavement]).buffer(0).simplify(.04,preserve_topology=True)
    concrete = json.loads((folder/'concrete.geojson').read_text())['features']
    metadata = json.loads((folder/'concrete-metadata.json').read_text())
    domain = next(f['domain']['codedValues'] for f in metadata['fields'] if f['name']=='SWWIDTH')
    widths = {d['code']: float(d['name'].rstrip("'"))*.3048 for d in domain if d['name']!='UNKNOWN'}
    sidewalks=[]
    for f in concrete:
        if f['properties']['TYPE'] not in (1,2,6,16): continue
        line=geometry(f); width=widths.get(f['properties']['SWWIDTH'],1.8)
        # County concrete lines include curb alignments: reserve the recorded
        # width on the non-carriageway side, clipped against mapped pavement.
        sidewalks.append(line.buffer(width, resolution=6).difference(road))
    return road, unary_union(sidewalks), dict(pavement=len(pavement),sidewalks=len(sidewalks))


class StreetBuilder:
    def __init__(self, mesh, phys, polygons, cell=160):
        self.mesh=mesh; self.phys=phys; self.polygons=polygons; self.cell=cell
        self.stats=dict(bridgeWays=0,coveredWays=0,railPanels=0,supports=0,sidewalkArea=0,curbRamps=0)
        self.bridge_checks=[]
        self.indoor=Polygon();self.access_footprint=Polygon()

    def emit(self, material, vertices, faces, collision=False):
        x=sum(p[0] for p in vertices)/len(vertices);z=sum(p[2] for p in vertices)/len(vertices)
        key=f'{math.floor(x/self.cell)},{math.floor(z/self.cell)}'
        self.mesh(key,material,vertices,faces)
        if collision:
            self.collision_material=material
            self.phys(key,vertices,faces)

    def beam(self, a, b, width, height, material, collision=False):
        dx,dz=b[0]-a[0],b[2]-a[2];length=math.hypot(dx,dz)
        if length<.0001:
            nx,nz=width/2,0;tx,tz=0,width/2
            vertices=[[a[0]+sx*nx+sz*tx,y,a[2]+sx*nz+sz*tz] for y in [a[1],b[1]] for sx,sz in [(-1,-1),(-1,1),(1,1),(1,-1)]]
        else:
            nx,nz=-dz/length*width/2,dx/length*width/2
            vertices=[[p[0]+side*nx,p[1]+dy,p[2]+side*nz] for dy in [-height/2,height/2] for p,side in [(a,-1),(b,-1),(b,1),(a,1)]]
        faces=[[0,2,1],[0,3,2],[4,5,6],[4,6,7],[0,1,5],[0,5,4],[1,2,6],[1,6,5],[2,3,7],[2,7,6],[3,0,4],[3,4,7]]
        if length>=.0001:faces=[f[::-1] for f in faces]
        self.emit(material,vertices,faces,collision)

    def triangles(self,p):
        yield from triangles(p)

    def slab(self, polygon, top, bottom, material, collision=True, walls=True, tops=True):
        """Closed slab with upward top winding; top/bottom may be height fields."""
        ty=top if callable(top) else lambda x,z:top
        by=bottom if callable(bottom) else lambda x,z:bottom
        for p in self.polygons(polygon):
            if p.area<1e-9:continue
            p=orient(p,sign=-1)  # Outer walls face out; hole walls face into holes.
            for tri in self.triangles(p) if tops else []:
                pts=list(tri.exterior.coords)[:-1]
                self.emit(material,[[x,ty(x,z),z] for x,z in pts],[[0,2,1]],collision)
                if material!='sidewalk':self.emit(material,[[x,by(x,z),z] for x,z in pts],[[0,1,2]],collision)
            for ring in [p.exterior,*p.interiors] if walls else []:
                for (x,z),(xx,zz) in zip(ring.coords,list(ring.coords)[1:]):
                    self.emit(material,[[x,by(x,z),z],[xx,by(xx,zz),zz],[xx,ty(xx,zz),zz],[x,ty(x,z),z]],[[0,1,2],[0,2,3]],collision)

    def paved_slab(self, polygon, top, material, collision=True):
        # Tessellate in collision-cell-sized pieces, but close only actual
        # outside/hole boundaries. No duplicate internal walls or coplanar caps.
        for p in tiles(polygon,self.cell):
            self.slab(p,top,SLAB_BOTTOM,material,collision,walls=False)
        self.slab(polygon,top,SLAB_BOTTOM,material,collision,tops=False)

    def sidewalks(self, polygon, carriageway, ramps):
        self.stats['sidewalkArea']=round(polygon.area)
        ramp_union=unary_union(ramps).buffer(0) if ramps else Polygon()
        ramp_union=ramp_union.intersection(carriageway.buffer(1.6).difference(carriageway)).simplify(.04,preserve_topology=True)
        normal=polygon.difference(ramp_union).simplify(.04,preserve_topology=True)
        edges=[]
        for p in self.polygons(carriageway):
            for ring in [p.exterior,*p.interiors]:
                points=list(ring.coords)
                edges.extend(LineString(points[i:i+9]) for i in range(0,len(points)-1,8))
        edge_tree=STRtree(edges)
        def top(x,z):
            point=Point(x,z);nearest=edge_tree.nearest(point)
            return ROAD_Y+(WALK_Y-ROAD_Y)*min(1,point.distance(edges[nearest])/1.5)
        # Chunk before tessellation to prevent long skinny triangles across blocks.
        for p in self.polygons(normal):
            x0,z0,x1,z1=p.bounds
            for x in range(math.floor(x0/80),math.floor(x1/80)+1):
                for z in range(math.floor(z0/80),math.floor(z1/80)+1):
                    self.slab(p.intersection(box(x*80,z*80,(x+1)*80,(z+1)*80)),WALK_Y,SLAB_BOTTOM,'sidewalk',walls=False)
            self.slab(p,WALK_Y,SLAB_BOTTOM,'sidewalk',tops=False)
        print('Level sidewalks complete',flush=True)
        for p in self.polygons(polygon.intersection(ramp_union)):
            # Tessellated grade transition meets the asphalt without a blocking lip.
            x0,z0,x1,z1=p.bounds
            for cx in range(math.floor(x0/80),math.floor(x1/80)+1):
                for cz in range(math.floor(z0/80),math.floor(z1/80)+1):
                    for piece in self.polygons(p.intersection(box(cx*80,cz*80,(cx+1)*80,(cz+1)*80))):
                        ax,az,bx,bz=piece.bounds
                        for x in range(math.floor(ax/2),math.ceil(bx/2)):
                            for z in range(math.floor(az/2),math.ceil(bz/2)):
                                self.slab(piece.intersection(box(x*2,z*2,(x+1)*2,(z+1)*2)),top,-.08,'sidewalk',walls=False)
            self.slab(p,top,-.08,'sidewalk',tops=False)
            self.stats['curbRamps']+=1

    def bridge(self, r, elevations, joins, road_clearance, all_walks):
        pts=r['points'];line=LineString(pts);width=r['width'];covered=r['id']==SPHERE_BRIDGE or r['tags'].get('covered')=='yes'
        walking=r['highway'] in ('footway','path','pedestrian','steps')
        thickness=.42 if walking else .65
        heights=[street_y(h) for h in r.get('heights',[elevations[n] for n in r['nodes']])]
        distances=[0]
        for a,b in zip(pts,pts[1:]):distances.append(distances[-1]+math.dist(a,b))
        landing=[]
        for i,n in enumerate(r['nodes']):
            level=r.get('heights',[0]*len(r['nodes']))[i]
            widths=[branch['width']/2+.45 for branch in joins[n] if branch['id']!=r['id'] and branch['highway'] in ('footway','path','pedestrian') and not branch.get('verticalLink') and max(branch.get('heights',[0]))-min(branch.get('heights',[0]))<.1 and abs(branch.get('heights',[0]*len(branch['nodes']))[branch['nodes'].index(n)]-level)<.2]
            pad=max(widths+[0]) if walking and r['highway']=='steps' else 0
            if walking and r['highway']=='steps' and self.indoor.covers(Point(pts[i])):
                # Stop the incline before the concourse slab, including its
                # entrance vestibule; otherwise the slab becomes a low ceiling.
                for part in getattr(line.intersection(self.indoor),'geoms',[line.intersection(self.indoor)]):
                    if not part.is_empty and part.distance(Point(pts[i]))<.1:pad=max(pad,part.length+.3)
            landing.append(pad)
        if r['highway']=='steps':
            budget=max(0,line.length-abs(heights[-1]-heights[0])/.85)
            total=landing[0]+landing[-1]
            if total>budget:
                landing[0]*=budget/total;landing[-1]*=budget/total
        def at(s):
            if r['highway']=='steps':
                t=max(0,min(1,(s-landing[0])/max(.001,line.length-landing[0]-landing[-1])));p=line.interpolate(s)
                return [p.x,heights[0]+(heights[-1]-heights[0])*t,p.y]
            i=next((i for i in range(len(distances)-1) if distances[i+1]>=s-1e-6),len(distances)-2)
            length=distances[i+1]-distances[i]
            start=min(landing[i],length*.45);end=min(landing[i+1],length*.45)
            t=max(0,min(1,(s-distances[i]-start)/max(.0001,length-start-end)));p=line.interpolate(s)
            return [p.x,heights[i]+(heights[i+1]-heights[i])*t,p.y]
        samples=sorted(set([*distances,*[min(line.length,j*2.0) for j in range(math.ceil(line.length/2)+1)]]))
        for i in range(len(distances)-1):
            length=distances[i+1]-distances[i]
            samples.extend([distances[i]+min(landing[i],length*.45),distances[i+1]-min(landing[i+1],length*.45)])
        if r['highway']=='steps':samples.extend([landing[0],line.length-landing[-1]])
        samples=sorted(set(samples))
        other=[]
        if walking:
            for node in r['nodes']:
                for branch in joins[node]:
                    if branch['id']!=r['id'] and branch['highway'] in ('footway','path','pedestrian','steps') and not branch.get('verticalLink') and abs(branch.get('heights',[0]*len(branch['nodes']))[branch['nodes'].index(node)]-r.get('heights',[0]*len(r['nodes']))[r['nodes'].index(node)])<.2:
                        other.append(LineString(branch['points']).buffer(branch['width']/2+.2))
        # Adjacent landings often have separate OSM nodes. Rail only the outer
        # perimeter of their common walking surface, not every source polyline.
        if walking and max(heights)-min(heights)<.1:
            if not hasattr(self,'walk_tree'):
                self.walk_ways=list({branch['id']:branch for branches in joins.values() for branch in branches if branch['highway'] in ('footway','path','pedestrian','steps')}.values())
                self.walk_lines=[LineString(branch['points']) for branch in self.walk_ways];self.walk_tree=STRtree(self.walk_lines)
            for index in self.walk_tree.query(line.buffer(width/2+18)):
                branch=self.walk_ways[index]
                if branch['id']==r['id'] or branch['highway'] not in ('footway','path','pedestrian','steps') or branch.get('verticalLink'):continue
                bl=self.walk_lines[index]
                if bl.distance(line)>width/2+branch['width']/2+.6:continue
                bh=branch.get('heights',[0]*len(branch['points']))
                if max(bh)-min(bh)<.1 and abs(bh[0]+.035-heights[0])<.2:other.append(bl.buffer(branch['width']/2+.4))
                elif branch['highway']=='steps':
                    if abs(bh[0]+.035-heights[0])<.2:other.append(substring(bl,0,min(3.5,bl.length*.4)).buffer(branch['width']/2+.4))
                    if abs(bh[-1]+.035-heights[0])<.2:other.append(substring(bl,max(0,bl.length-3.5),bl.length).buffer(branch['width']/2+.4))
        openings=unary_union(other) if other else Polygon()
        for lo,hi in zip(samples,samples[1:]):
            a,b=at(lo),at(hi);dx,dz=b[0]-a[0],b[2]-a[2];length=math.hypot(dx,dz)
            if length<.001:continue
            nx,nz=-dz/length,dx/length
            # Mitered strip closes corners without a triangular gap on the bends.
            def cross(s,p):
                before=at(max(0,s-.1));after=at(min(line.length,s+.1));tx,tz=after[0]-before[0],after[2]-before[2];den=math.hypot(tx,tz)
                mx,mz=-tz/den,tx/den;factor=min(1.5,1/max(.5,mx*nx+mz*nz))
                return [[p[0]+sign*mx*width*.5*factor,p[1],p[2]+sign*mz*width*.5*factor] for sign in (-1,1)]
            aa,bb=cross(lo,a),cross(hi,b);top=[aa[0],bb[0],bb[1],aa[1]]
            # Negative height under approach ramps is clipped at the ground datum.
            bottom=[[p[0],max(-.15,p[1]-thickness),p[2]] for p in top]
            if not (walking and min(a[1],b[1])>5.9 and self.indoor.contains(Point((a[0]+b[0])/2,(a[2]+b[2])/2))):self.emit('bridge-deck',bottom+top,[[4,6,5],[4,7,6],[0,1,2],[0,2,3],[0,4,5],[0,5,1],[1,5,6],[1,6,2],[2,6,7],[2,7,3],[3,7,4],[3,4,0]],True)
            if walking and r['highway']=='steps' and abs(b[1]-a[1])>.015:
                count=max(1,math.ceil(abs(b[1]-a[1])/.16))
                for k in range(count):
                    t=(k+.5)/count;xx=a[0]+dx*t;zz=a[2]+dz*t;yy=a[1]+(b[1]-a[1])*t+.025
                    self.beam([xx-dx/count/2,yy,zz-dz/count/2],[xx+dx/count/2,yy,zz+dz/count/2],width-.12,.035,'bridge-metal' if r['tags'].get('conveying') else 'bridge-concrete')
            if not walking:
                self.emit('road',[[p[0],p[1]+.008,p[2]] for p in top],[[0,2,1],[0,3,2]])
            if walking:
                self.bridge_checks.append(dict(way=r['id'],point=at((lo+hi)/2),width=width,covered=covered))
                for side in (0,1):
                    p,q=aa[side],bb[side];mid=Point((p[0]+q[0])/2,(p[2]+q[2])/2)
                    if openings.contains(mid) or self.indoor.contains(mid) or max(p[1],q[1])<.28:continue
                    def lifted(v,h):return [v[0],v[1]+h,v[2]]
                    self.beam(lifted(p,.10),lifted(q,.10),.17,.20,'bridge-concrete',True)
                    self.beam(lifted(p,1.12),lifted(q,1.12),.11,.09,'bridge-metal',True)
                    self.beam(lifted(p,1.07),lifted(q,1.07),.045,.025,'bridge-light')
                    self.beam(lifted(p,.2),lifted(p,1.14),.075,.075,'bridge-metal')
                    self.beam(lifted(p,.65),lifted(q,.65),.025,.84,'bridge-glass',True)
                    self.stats['railPanels']+=1
                    if covered:
                        self.beam(lifted(p,0),lifted(p,3.1),.14,.14,'bridge-metal',True)
                        self.beam(lifted(p,1.2),lifted(q,3.05),.065,.065,'bridge-metal')
                        self.beam(lifted(p,2.1),lifted(q,2.1),.025,1.76,'bridge-glass',True)
                if covered:
                    roof=[[p[0],p[1]+3.14,p[2]] for p in top]+[[p[0],p[1]+3.30,p[2]] for p in top]
                    self.emit('bridge-roof',roof,[[4,6,5],[4,7,6],[0,1,2],[0,2,3],[0,4,5],[0,5,1],[1,5,6],[1,6,2],[2,6,7],[2,7,3],[3,7,4],[3,4,0]],True)
                    self.beam([aa[0][0],aa[0][1]+3.08,aa[0][2]],[aa[1][0],aa[1][1]+3.08,aa[1][2]],.14,.14,'bridge-metal')
            elif min(a[1],b[1])>1:
                for side in (0,1):
                    p,q=aa[side],bb[side];self.beam([p[0],p[1]+.45,p[2]],[q[0],q[1]+.45,q[2]],.25,.9,'bridge-concrete',True)
        if walking:
            for s in [min(line.length-1,2),*range(18,int(line.length-2),24),max(1,line.length-2)]:
                p=at(s)
                if p[1]<2 or self.access_footprint.contains(Point(p[0],p[2])) or road_clearance.intersects(Point(p[0],p[2]).buffer(.8)):continue
                # Support beneath its own deck, never in a lane below it.
                self.beam([p[0],0,p[2]],[p[0],p[1]-thickness,p[2]],.8,.8,'bridge-concrete',True)
                self.stats['supports']+=1
            self.stats['bridgeWays']+=1
            self.stats['coveredWays']+=int(covered)
