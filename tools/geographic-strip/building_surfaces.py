"""Exterior surfaces of overlapping OSM building volumes, with source ownership.

OSM building outlines and building:part are not separate visible solids where
volumes overlap. Keep only the union's exterior; at a shared face, the more
specific part owns the material. This handles duplicate outlines, podium/tower
junctions, and touching wings without offsets or changing surveyed footprints.
"""
from shapely import set_precision
from shapely.geometry import Polygon, LineString, Point, box
from shapely.ops import unary_union
from shapely.strtree import STRtree
from surface_geometry import triangles

def parts(g,kind='Polygon'):
    if g.is_empty:return []
    if g.geom_type==kind:return [g]
    return [p for child in getattr(g,'geoms',[]) for p in parts(child,kind)]

class BuildingSurfaces:
    def __init__(self,records):
        self.records=records
        self.by_id={r['id']:i for i,r in enumerate(records)}
        self.shapes=[set_precision(r['shape'],.001) for r in records]
        self.tree=STRtree(self.shapes)
        self.changed=set();self.wall_faces_removed=0;self.roof_area_removed=0

    def priority(self,i):
        r=self.records[i]
        return (bool(r.get('part')),r.get('kind')=='height',-self.shapes[i].area,r['id'])

    def wall(self,ident,a,b,base,top,access):
        i=self.by_id[ident];shape=self.shapes[i]
        line=LineString([a,b]);length=line.length
        if length<1e-6:return []
        cuts=[]
        # A millimetre snap makes common OSM boundaries identical. The buffer
        # is only a broad-phase tolerance; face ownership is checked below.
        for j in self.tree.query(line.buffer(.003)):
            if j==i:continue
            r=self.records[j];lo=max(base,r['base']);hi=min(top,r['height'])
            if hi<=lo:continue
            other=self.shapes[j]
            for segment in parts(line.intersection(other),'LineString'):
                if segment.length<.002:continue
                midpoint=segment.interpolate(.5,normalized=True)
                dx=(b[0]-a[0])/length;dz=(b[1]-a[1])/length
                normal=(-dz*.01,dx*.01)
                outside=Point(midpoint.x+normal[0],midpoint.y+normal[1])
                if shape.contains(outside):outside=Point(midpoint.x-normal[0],midpoint.y-normal[1])
                # Interior wall: both sides occupied. Same outward boundary:
                # emit just the highest-priority owner's surface.
                if other.contains(outside) or self.priority(j)>self.priority(i):
                    ts=[line.project(Point(p)) for p in segment.coords]
                    cuts.append(box(min(ts),lo,max(ts),hi))
        if not cuts:return access.wall(a,b,base,top)
        mask=unary_union(cuts);result=[]
        for vertices in access.wall(a,b,base,top):
            face=Polygon([(line.project(Point(v[0],v[2])),v[1]) for v in vertices])
            remaining=face.difference(mask)
            if remaining.area<face.area-1e-6:self.changed.add(ident);self.wall_faces_removed+=1
            for p in parts(remaining):
                for tri in triangles(p):
                    result.append([[line.interpolate(t).x,y,line.interpolate(t).y] for t,y in list(tri.exterior.coords)[:-1]])
        return result

    def roof(self,ident,shape,height):
        i=self.by_id[ident];cuts=[]
        for j in self.tree.query(shape):
            if j==i:continue
            r=self.records[j]
            # A higher solid occludes this roof; exact shared roofs have one
            # deterministic owner. Elevated volumes don't erase roofs below.
            if r['base']<=height and (r['height']>height+.001 or abs(r['height']-height)<=.001 and self.priority(j)>self.priority(i)):
                cuts.append(self.shapes[j])
        result=shape.difference(unary_union(cuts)) if cuts else shape
        removed=shape.area-result.area
        if removed>1e-6:self.changed.add(ident);self.roof_area_removed+=removed
        return result

    def report(self):
        return dict(normalizedBuildings=len(self.changed),clippedWallTriangles=self.wall_faces_removed,removedHiddenRoofArea=round(self.roof_area_removed,2))
