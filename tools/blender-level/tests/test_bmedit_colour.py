"""Blender-free checks of bmedit's colour maths: `python3 -m unittest discover -s tools/blender-level/tests`."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from bmedit.colour import distance, mix, parse_srgb, to_hex, to_linear  # noqa: E402


class ColourTest(unittest.TestCase):
    def test_parses_every_spelling_of_a_colour(self):
        self.assertEqual(parse_srgb('#ff8000'), (1.0, 128 / 255, 0.0))
        self.assertEqual(parse_srgb('f80'), (1.0, 136 / 255, 0.0))
        self.assertEqual(parse_srgb((255, 128, 0)), (1.0, 128 / 255, 0.0))
        self.assertEqual(parse_srgb((1.0, 0.5, 0.0)), (1.0, 0.5, 0.0))
        with self.assertRaises(ValueError):
            parse_srgb('#12')

    def test_stores_linear_and_reads_back_the_same_hex(self):
        # sRGB mid-grey is ~0.214 linear: the stored value must NOT be the picker's 0.5.
        r, g, b, a = to_linear('#808080')
        self.assertAlmostEqual(r, 0.2158, places=3)
        self.assertEqual(a, 1.0)
        for hex_colour in ('#eef3f7', '#3c7524', '#000000', '#ffffff'):
            self.assertEqual(to_hex(to_linear(hex_colour)), hex_colour)

    def test_distance_and_mix(self):
        self.assertEqual(distance('#ffffff', '#ffffff'), 0.0)
        self.assertLess(distance('#3c7524', '#3d7625'), 0.03)
        self.assertGreater(distance('#3c7524', '#eef3f7'), 0.5)
        self.assertEqual(mix('#000000', '#ffffff', 0.5), (0.5, 0.5, 0.5))
        self.assertEqual(mix('#000000', '#ffffff', 2.0), (1.0, 1.0, 1.0))


if __name__ == '__main__':
    unittest.main()
