"""Blender-free checks of bmlevel: `python3 -m unittest discover -s tools/blender-level/tests`.

Runs the example level through the null backend and checks the invariants the engine relies on:
the axis round trip, collider records that match what was built, the door records' shape
(exactly the engine's DoorDefinition), the JSON the exporter writes, review cameras, and the
world.json merge.
"""
import importlib
import json
import math
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from bmlevel import core  # noqa: E402


def fresh_bmlevel():
    import bmlevel
    bmlevel.reset()
    return bmlevel


class CoordinateTests(unittest.TestCase):
    def test_axis_round_trip(self):
        for p in ((1, 2, 3), (-4.5, 0, 9), (0, -1, 0)):
            self.assertEqual(core.from_blender(core.to_blender(p)), tuple(float(v) for v in p))

    def test_forward_at_yaw_matches_the_engine_convention(self):
        x, z = core.rotate_xz(0, 1, math.pi / 2)
        self.assertAlmostEqual(x, 1.0)
        self.assertAlmostEqual(z, 0.0)

    def test_frames_compose(self):
        outer = core.Frame((10, 0, 0), math.pi / 2)
        inner = outer.child((0, 0, 2), 0.0)
        wx, wy, wz = inner.world((0, 1, 0))
        self.assertAlmostEqual(wx, 12.0)
        self.assertAlmostEqual(wy, 1.0)
        self.assertAlmostEqual(wz, 0.0)

    def test_box_corners_rotate(self):
        corners = core.box_corners((0, 0, 0), (2, 2, 4), math.pi / 2)
        xs = sorted(round(c[0], 6) for c in corners)
        self.assertEqual(xs[0], -2.0)
        self.assertEqual(xs[-1], 2.0)

    def test_concave_outline_is_rejected(self):
        with self.assertRaises(ValueError):
            core.require_convex_outline('L', [(0, 0), (2, 0), (2, 1), (1, 1), (1, 2), (0, 2)])
        core.require_convex_outline('tri', [(0, 0), (2, 0), (1, 2)])

    def test_hex_color(self):
        self.assertEqual(core.hex_color((1, 0.5, 0)), '#ff8000')
        self.assertEqual(core.hex_color('#ABCDEF'), '#abcdef')
        with self.assertRaises(ValueError):
            core.hex_color('red')


def quad(y, x0, x1, z0, z1):
    """An up-facing rectangle at height y (counter-clockwise seen from above)."""
    return [(x0, y, z1), (x1, y, z1), (x1, y, z0), (x0, y, z0)]


class CoplanarOverlapTests(unittest.TestCase):
    def test_a_stripe_laid_flush_on_a_floor_is_reported_with_both_materials(self):
        count, where = core.coplanar_overlaps([(quad(0, -5, 5, -5, 5), 'floor'), (quad(0, -1, 1, -0.1, 0.1), 'stripe')])
        self.assertEqual(count, 1)
        self.assertEqual(where, ['(0.00, 0.00, 0.00) stripe vs floor'])

    def test_lifting_the_stripe_1_cm_clears_it(self):
        self.assertEqual(core.coplanar_overlaps([(quad(0, -5, 5, -5, 5), 'floor'), (quad(0.01, -1, 1, -0.1, 0.1), 'stripe')])[0], 0)

    def test_one_material_and_opposite_facings_are_not_reported(self):
        floor = quad(0, -5, 5, -5, 5)
        self.assertEqual(core.coplanar_overlaps([(floor, 'floor'), (quad(0, -1, 1, -1, 1), 'floor')])[0], 0)
        self.assertEqual(core.coplanar_overlaps([(floor, 'floor'), (list(reversed(quad(0, -1, 1, -1, 1))), 'rug')])[0], 0)

    def test_side_by_side_faces_in_one_plane_are_not_reported(self):
        self.assertEqual(core.coplanar_overlaps([(quad(0, 0, 1, 0, 1), 'a'), (quad(0, 1, 2, 0, 1), 'b')])[0], 0)


class ExampleLevelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bm = fresh_bmlevel()
        example = importlib.import_module('example_level')
        example.build()
        cls.level = cls.bm.level
        cls.out = tempfile.mkdtemp()
        cls.paths = cls.bm.export(cls.out, 'hut')
        with open(cls.paths['level']) as f:
            cls.level_json = json.load(f)
        with open(cls.paths['doors']) as f:
            cls.doors_json = json.load(f)

    def test_counts(self):
        self.assertEqual(len(self.level.doors), 2)
        self.assertEqual(len(self.level.volumes), 4)
        self.assertEqual(len(self.level.links), 3)
        self.assertGreater(len(self.level.colliders), 20)
        self.assertTrue(any(l.name == 'spawn' for l in self.level.landmarks))

    def test_solid_boxes_become_colliders_and_decor_does_not(self):
        names = {c.name for c in self.level.colliders}
        self.assertIn('table', names)
        self.assertIn('west', names)
        self.assertNotIn('rug', names)
        self.assertNotIn('lamp shade', names)
        for c in self.level.colliders:
            if c.name == 'table':
                self.assertEqual(c.group, 'environment')

    def test_stairs_emit_a_ramp_hull_and_rails(self):
        hulls = {c.name for c in self.level.colliders if isinstance(c, core.HullCollider)}
        self.assertIn('porch steps ramp', hulls)
        self.assertIn('porch steps rail L', hulls)
        self.assertEqual(len(self.level.stairs), 1)

    def test_door_records_are_door_definitions(self):
        for d in self.doors_json:
            self.assertEqual(set(d), {'id', 'position', 'rotationY', 'width', 'height', 'thickness', 'kind', 'animation'})
            self.assertEqual(set(d['position']), {'x', 'y', 'z'})
        inner = next(d for d in self.doors_json if d['id'] == 'inner')
        self.assertAlmostEqual(inner['rotationY'], 1.5707963)
        self.assertEqual(inner['animation'], 'hinge')

    def test_yawed_door_jambs_flank_the_opening(self):
        jambs = [c for c in self.level.colliders if c.name.startswith('inner jamb')]
        self.assertEqual(len(jambs), 2)
        zs = sorted(c.position[2] for c in jambs)
        self.assertLess(zs[0], -0.6)
        self.assertGreater(zs[1], 0.6)
        for c in jambs:
            self.assertAlmostEqual(c.position[0], 4.0)

    def test_mesh_level_json_shape(self):
        j = self.level_json
        self.assertEqual(j['format'], core.MESH_LEVEL_FORMAT)
        self.assertEqual(j['version'], core.MESH_LEVEL_VERSION)
        self.assertEqual(j['units'], 'meters')
        self.assertEqual(set(j), {'format', 'version', 'units', 'colliders', 'volumes', 'landmarks', 'lights', 'extras'})
        for c in j['colliders']:
            self.assertIn(c['shape'], ('box', 'convexHull'))
            if c['shape'] == 'convexHull':
                self.assertEqual(len(c['vertices']) % 3, 0)
                self.assertGreaterEqual(len(c['vertices']), 12)
        self.assertEqual(len(j['extras']['links']), 3)
        self.assertIn('unroofed', next(v for v in j['volumes'] if v['name'] == 'porch')['tags'])
        spot = next(l for l in j['lights'] if l['type'] == 'spot')
        self.assertEqual(set(spot), {'name', 'type', 'position', 'target', 'color', 'intensity', 'angle', 'penumbra', 'castShadow'})

    def test_native_height_and_summary(self):
        self.assertAlmostEqual(self.level.native_height(), 4.8, places=2)
        summary = self.level.summary('hut', 'build/level/hut.glb')
        self.assertIn('--keep-glb --asset-id level-hut --height 4.8', summary)

    def test_review_cameras(self):
        shots = core.review_cameras(self.level_json, self.doors_json)
        names = [s['name'] for s in shots]
        self.assertEqual(names[0], 'overview')
        self.assertIn('door-front-a', names)
        self.assertIn('door-inner-b', names)
        self.assertIn('stairs-porch steps', names)
        self.assertEqual(sum(1 for n in names if n.startswith('volume-')), 4)

    def test_duplicate_names_are_refused(self):
        bm = fresh_bmlevel()
        bm.mat('m', (1, 1, 1))
        bm.box('twice', (0, 0, 0), (1, 1, 1), 'm')
        bm.box('twice', (3, 0, 0), (1, 1, 1), 'm')
        with self.assertRaises(ValueError):
            bm.level.mesh_level_json()

    def test_link_to_unknown_volume_is_refused_at_export(self):
        bm = fresh_bmlevel()
        bm.mat('m', (1, 1, 1))
        bm.volume('a', (0, 1, 0), (2, 2, 2))
        bm.link('a', 'nowhere')
        with self.assertRaises(ValueError):
            bm.export(tempfile.mkdtemp(), 'x')


class SyncWorldTests(unittest.TestCase):
    def test_merge_keeps_creator_fields_and_reports_orphans(self):
        sync = importlib.import_module('sync_world')
        existing = [
            {'id': 'front', 'position': {'x': 0, 'y': 0, 'z': 0}, 'rotationY': 0, 'width': 1, 'height': 2, 'thickness': 0.1, 'kind': 'locked', 'keyId': 'brass', 'animation': 'slide', 'color': '#123456'},
            {'id': 'gone', 'position': {'x': 9, 'y': 0, 'z': 0}, 'rotationY': 0, 'width': 1, 'height': 2, 'thickness': 0.1, 'kind': 'plain', 'animation': 'slide'},
        ]
        built = [
            {'id': 'front', 'position': {'x': 1, 'y': 1.1, 'z': -3}, 'rotationY': 0.5, 'width': 1.4, 'height': 2.2, 'thickness': 0.1, 'kind': 'plain', 'animation': 'hinge'},
            {'id': 'new', 'position': {'x': 4, 'y': 1, 'z': 0}, 'rotationY': 0, 'width': 1.2, 'height': 2, 'thickness': 0.1, 'kind': 'plain', 'animation': 'slide'},
        ]
        merged, report = sync.merge_doors(existing, built, None)
        front = next(d for d in merged if d['id'] == 'front')
        self.assertEqual(front['kind'], 'locked')
        self.assertEqual(front['keyId'], 'brass')
        self.assertEqual(front['color'], '#123456')
        self.assertEqual(front['position'], {'x': 1, 'y': 1.1, 'z': -3})
        self.assertEqual(front['animation'], 'hinge')
        self.assertEqual(report, {'added': ['new'], 'updated': ['front'], 'orphans': ['gone']})
        self.assertEqual({d['id'] for d in merged}, {'front', 'gone', 'new'})


class ShotSpecTests(unittest.TestCase):
    """`--shot` specs: the ad-hoc camera review.py aims from the level JSON."""

    LEVEL = {
        'colliders': [{'shape': 'box', 'position': [0, 0, 0], 'size': [10, 1, 10], 'yaw': 0}],
        'landmarks': [{'name': 'spawn', 'position': [1, 0.1, 2], 'yaw': 0, 'tags': []}],
        'volumes': [{'name': 'hall', 'position': [0, 1.75, 0], 'size': [12, 3.5, 8], 'yaw': 0, 'tags': []}],
    }
    DOORS = [{'id': 'north', 'position': {'x': 0, 'y': 1.1, 'z': -4}, 'rotationY': 0, 'width': 1.4, 'height': 2.2}]

    def test_landmark_is_an_eye_at_the_from_end_and_the_thing_at_the_to_end(self):
        self.assertEqual(core.resolve_point('landmark:spawn', self.LEVEL, as_eye=True), (1, 0.1 + core.EYE_HEIGHT, 2))
        self.assertEqual(core.resolve_point('landmark:spawn', self.LEVEL), (1, 1.1, 2))

    def test_volume_from_is_eye_height_above_its_floor_and_to_is_its_centre(self):
        self.assertEqual(core.resolve_point('volume:hall', self.LEVEL, as_eye=True), (0, 1.75 - 1.75 + core.EYE_HEIGHT, 0))
        self.assertEqual(core.resolve_point('volume:hall', self.LEVEL), (0, 1.75, 0))

    def test_door_from_is_eye_height_above_its_threshold(self):
        self.assertEqual(core.resolve_point('door:north', self.LEVEL, self.DOORS, as_eye=True), (0, 1.1 - 1.1 + core.EYE_HEIGHT, -4))
        self.assertEqual(core.resolve_point('door:north', self.LEVEL, self.DOORS), (0, 1.1, -4))

    def test_raw_coordinates_are_used_exactly_at_either_end(self):
        self.assertEqual(core.resolve_point('3, -1.5,7', self.LEVEL, as_eye=True), (3.0, -1.5, 7.0))
        self.assertEqual(core.resolve_point('3,-1.5,7', self.LEVEL), (3.0, -1.5, 7.0))

    def test_an_unknown_name_lists_the_known_ones(self):
        with self.assertRaises(ValueError) as raised:
            core.resolve_point('landmark:altar', self.LEVEL)
        self.assertIn('spawn', str(raised.exception))
        with self.assertRaises(ValueError):
            core.resolve_point('nonsense', self.LEVEL)

    def test_a_shot_without_a_target_looks_at_the_level_centre(self):
        shot = core.custom_shot('landmark:spawn', 1, self.LEVEL, self.DOORS)
        self.assertEqual(shot['name'], 'shot-1')
        self.assertEqual(shot['kind'], 'persp')
        self.assertEqual(shot['target'], core.level_center(self.LEVEL))
        self.assertNotIn('fov', shot)

    def test_a_from_to_shot_carries_both_ends_and_the_fov(self):
        shot = core.custom_shot('landmark:spawn -> volume:hall', 2, self.LEVEL, self.DOORS, fov=70)
        self.assertEqual(shot['name'], 'shot-2')
        self.assertEqual(shot['position'], (1, 0.1 + core.EYE_HEIGHT, 2))
        self.assertEqual(shot['target'], (0, 1.75, 0))
        self.assertEqual(shot['fov'], 70)
        self.assertEqual(shot['spec'], 'landmark:spawn -> volume:hall')


if __name__ == '__main__':
    unittest.main()
