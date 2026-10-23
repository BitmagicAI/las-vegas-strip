"""Colour maths for bmedit, free of bpy so plain python3 tests cover it.

Scripts speak sRGB — the numbers a colour picker shows, as `'#d8e4ea'`, `(216, 228, 234)` or
`(0.85, 0.89, 0.92)`. Blender's float colour attributes and glTF's COLOR_0 are LINEAR, so every
value is converted once on the way in and back on the way out. Storing sRGB numbers as linear is
what turned early forged levels pastel.
"""
from __future__ import annotations

from typing import Sequence, Union

Colour = Union[str, Sequence[float]]


def srgb_to_linear(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def linear_to_srgb(c: float) -> float:
    c = max(0.0, min(1.0, c))
    return c * 12.92 if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def parse_srgb(colour: Colour) -> tuple[float, float, float]:
    """'#rrggbb', 0-255 ints or 0-1 floats → sRGB floats in 0..1."""
    if isinstance(colour, str):
        h = colour.lstrip('#')
        if len(h) == 3:
            h = ''.join(ch * 2 for ch in h)
        if len(h) != 6:
            raise ValueError(f'colour {colour!r} is not #rgb or #rrggbb')
        return (int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255)
    values = [float(v) for v in colour][:3]
    if len(values) != 3:
        raise ValueError(f'colour {colour!r} needs three channels')
    if any(v > 1.0 for v in values):
        values = [v / 255 for v in values]
    return (values[0], values[1], values[2])


def to_linear(colour: Colour) -> tuple[float, float, float, float]:
    r, g, b = parse_srgb(colour)
    return (srgb_to_linear(r), srgb_to_linear(g), srgb_to_linear(b), 1.0)


def to_hex(linear: Sequence[float]) -> str:
    """A stored linear colour as the sRGB hex a script would write."""
    return '#' + ''.join(f'{round(linear_to_srgb(c) * 255):02x}' for c in linear[:3])


def distance(a: Colour, b: Colour) -> float:
    """Distance between two sRGB colours, 0..~1.7; under 0.1 reads as 'the same colour'."""
    pa, pb = parse_srgb(a), parse_srgb(b)
    return sum((x - y) ** 2 for x, y in zip(pa, pb)) ** 0.5


def mix(a: Colour, b: Colour, t: float) -> tuple[float, float, float]:
    """sRGB blend of two colours; t=0 is a, t=1 is b."""
    pa, pb = parse_srgb(a), parse_srgb(b)
    t = max(0.0, min(1.0, t))
    return (pa[0] + (pb[0] - pa[0]) * t, pa[1] + (pb[1] - pa[1]) * t, pa[2] + (pb[2] - pa[2]) * t)
