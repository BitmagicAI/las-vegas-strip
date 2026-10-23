"""Ground-cover layers with explicit provenance, clipped to the public streets.

County median outlines are reliable geometry, but their concrete curb material
does NOT identify the planting inside. Unclassified wide islands use gravel;
green surfaces require OSM vegetation tags. Park boundaries alone aren't lawns.
"""
import json, math
from collections import defaultdict
from shapely.geometry import Polygon, LineString, Point, box, shape, mapping
from shapely.ops import unary_union, polygonize, transform
from shapely import make_valid
from surface_geometry import polygons, BED_Y, WALK_Y


def projection(origin):
    def project(x, y, z=None):
        return (6378137 * math.radians(x-origin[0]) * math.cos(math.radians(origin[1])),
                -6378137 * math.radians(y-origin[1]))
    return project


def county_medians(root, origin):
    folder = root/'build/geographic-strip/county'
    project = projection(origin)
    features = json.loads((folder/'concrete.geojson').read_text())['features']
    lines = [transform(project, shape(f['geometry'])) for f in features if f['properties'].get('TYPE') == 10]
    # These are curb perimeter lines, not centerlines. Polygonize closed rings,
    # including rings split over several records; never buffer open lines into
    # guessed planting areas.
    rings = list(polygonize(unary_union(lines)))
    return unary_union([p for p in rings if p.area > .1]).buffer(0)


def source_cover(root, origin):
    path = root/'build/geographic-strip/landcover/osm.json'
    raw = json.loads(path.read_text())
    project = projection(origin)
    def coords(g):
        return [project(v['lon'], v['lat']) for v in g if 'lat' in v]
    def area(e):
        if e['type'] == 'way':
            points = coords(e.get('geometry', []))
            if len(points) > 3 and points[0] == points[-1]:
                return make_valid(Polygon(points)).buffer(0)
        elif e['type'] == 'relation':
            rings = defaultdict(list)
            for member in e.get('members', []):
                points = coords(member.get('geometry', []))
                if len(points) > 1:
                    rings[member.get('role') or 'outer'].append(LineString(points))
            outer = unary_union(list(polygonize(unary_union(rings['outer']))))
            inner = unary_union(list(polygonize(unary_union(rings['inner']))))
            return outer.difference(inner)
        return Polygon()
    classes = defaultdict(list)
    records = []
    for e in raw['elements']:
        tags = e.get('tags', {})
        values = set(tags.get(k, '') for k in ['landuse', 'natural', 'landcover'])
        if values & {'grass', 'meadow', 'grassland'} or tags.get('golf') in ('fairway', 'green', 'rough', 'tee'):
            kind = 'grass'
        elif values & {'wood', 'forest', 'trees'}:
            kind = 'woodland'
        elif values & {'scrub', 'shrubbery', 'heath', 'flowerbed', 'greenery'} or tags.get('leisure') == 'garden':
            kind = 'planting'
        elif values & {'gravel', 'sand', 'bare_ground'}:
            kind = 'gravel'
        else:
            continue
        geometry = area(e)
        if geometry.is_empty:
            continue
        classes[kind].append(geometry)
        records.append(dict(id=f"{e['type']}/{e['id']}", kind=kind, area=round(geometry.area, 2)))
    return {k: unary_union(v).buffer(0) for k, v in classes.items()}, records


def landscape(root, origin, road, walk, median, excluded, street, flat):
    sources, records = source_cover(root, origin)
    # Preserve data coverage bounds even when a golf-course way crosses them.
    project = projection(origin)
    bounds = box(*project(-115.193,36.153), *project(-115.147,36.079))
    center = median.buffer(-.35).difference(excluded).difference(road).buffer(0)
    curb = median.difference(center).difference(excluded).difference(road)
    hardscape = unary_union([road, walk, curb, excluded])
    available = bounds.difference(hardscape)
    layers = {}
    used = Polygon()
    for kind in ['grass', 'planting', 'woodland', 'gravel']:
        p = sources.get(kind, Polygon()).intersection(available).difference(used).buffer(0)
        layers[kind] = p
        used = unary_union([used, p])
    # Curbed islands can be very narrow. A 35 cm rim leaves tiny traffic
    # separators entirely concrete and reserves the wider centers as beds.
    median_beds = center.difference(walk)
    unknown = median_beds.difference(used)
    layers['gravel'] = unary_union([layers['gravel'], unknown])
    street.paved_slab(curb, WALK_Y, 'median-curb')
    for kind, geometry in layers.items():
        # Tops are separate from terrain and paving, with buried, closed edges.
        street.paved_slab(geometry, BED_Y, kind)
    # Small shrub groups give mapped planted beds volume. These are artistic
    # dressing inside actual polygons, not claims about individual plant sites.
    shrubs = 0
    for p in polygons(layers['planting']):
        if p.area < 3:
            continue
        inner = p.buffer(-.7)
        if inner.is_empty:
            continue
        ax, az, bx, bz = inner.bounds
        spacing = 8 if p.area < 1500 else 13
        candidates = [inner.representative_point()]
        candidates += [Point(x+spacing*.37,z+spacing*.63)
            for x in range(math.floor(ax/spacing)*spacing,math.ceil(bx/spacing)*spacing,spacing)
            for z in range(math.floor(az/spacing)*spacing,math.ceil(bz/spacing)*spacing,spacing)]
        for point in candidates:
            if not inner.contains(point):
                continue
            x,z=point.x,point.y
            seed = int(abs(x*173+z*337))
            radius = .5+(seed%7)*.065
            height = .45+(seed%5)*.08
            verts=[[x,BED_Y+height,z]]
            for ring_y,r in [(height*.5,radius),(0,radius*.7)]:
                verts += [[x+math.cos(i*math.tau/7)*r,BED_Y+ring_y,z+math.sin(i*math.tau/7)*r] for i in range(7)]
            faces=[]
            for i in range(7):
                a,b=1+i,1+(i+1)%7
                faces += [[0,b,a],[a,b,b+7],[a,b+7,a+7]]
            street.emit('shrub',verts,faces)
            shrubs+=1
    output=root/'build/geographic-strip/landcover'
    report=dict(source='OSM vegetation polygons + Clark County TYPE=10 median boundaries',
        osmAreas=len(records), medianPolygons=len(list(polygons(median))),
        areas={k:round(p.area,2) for k,p in layers.items()},
        medianCurbArea=round(curb.area,2),unclassifiedMedianGravelArea=round(unknown.area,2),
        shrubClusters=shrubs,
        notes=['Unclassified median fill is gravel, not an assertion of grass.',
               'Shrub placement is decorative within mapped gardens; individual trees have not been reconstructed.',
               'OSM park polygons without ground-cover tags do not become invented lawns.'])
    (output/'report.json').write_text(json.dumps(report,indent=2))
    (output/'features.json').write_text(json.dumps(records,separators=(',',':')))
    return layers, curb, report
