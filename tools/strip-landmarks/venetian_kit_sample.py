"""A test scene for venetian_kit.py (not part of the game): a street of house fronts under the painted sky, a vaulted
colonnade bay, a canal with a bridge, lamps and furniture. build_venetian_interior.py sample --export, then
venetian_review.py render vikit --dir build/venetian-interiors/kit"""
import math
from common import Frame
import venetian_kit as K


def build(B):
    B.property = 'vikit-interior'; B.source = 'kit'; B.detail = 0
    G = Frame(B, 0, 0, 0, y=0)
    # street 12 m wide along +z, house rows both sides, sky
    K.box(G, 'vi-street-flags', (0, -.1, 20), (12, .2, 40), True)
    K.house_row(Frame(B, -6, 40, math.pi / 2, y=0), 0, 40, 9.6, seed=1)
    K.house_row(Frame(B, 6, 0, -math.pi / 2, y=0), 0, 40, 9.6, seed=4)
    K.face(G, 'vi-sky-day', [(-7, 9.6, 0), (7, 9.6, 0), (7, 9.6, 40), (-7, 9.6, 40)])
    for z in range(4, 40, 9):
        for s in (-1, 1): K.lamp_post(G, s * 4.6, z, 0, 3 if z % 2 else 5)
    K.cafe_set(G, -3, 12, 0, 4, 'vi-umbrella-blue'); K.cafe_set(G, 2.5, 26, 0, 3)
    K.planter(G, -4.5, 33); K.planter(G, 4.5, 7, topiary=False)
    # a colonnade bay with a barrel vault (x 20..34, z 0..24)
    C = Frame(B, 27, 0, 0, y=0)
    K.box(C, 'vi-checker', (0, -.1, 12), (14, .2, 24), True)
    for z in [3, 9, 15, 21]:
        for x in [-5.4, 5.4]: K.column(C, x, z, 6.6, .36)
    for x in [-5.4, 5.4]: K.entablature(C if x < 0 else Frame(B, 27, 24, math.pi, y=0), -12, 12, 6.6, 'vi-limestone', 'vi-coffer-cream', 'vi-gilt-plain', x if x < 0 else 5.4)
    K.barrel_vault(C, -6.4, 6.4, 0, 24, 8.4, 3)
    K.chandelier(C, 0, 13.6, 12, 1.3)
    # a canal with a bridge and a balustrade (x -30..-16)
    W = Frame(B, -23, 0, 0, y=0)
    K.face(W, 'water', [(-4.2, -.55, 0), (4.2, -.55, 0), (4.2, -.55, 30), (-4.2, -.55, 30)])
    for s in (-1, 1):
        K.box(W, 'vi-street-flags', (s * 7, -.1, 15), (5.6, .2, 30), True)
        K.canal_edge(W, (s * 4.2, 0) if s < 0 else (s * 4.2, 30), (s * 4.2, 30) if s < 0 else (s * 4.2, 0), 0, -.55)
    K.stone_bridge(Frame(B, -23, 15, 0, y=0), 11, 3.2, 1.3, opening_half=4.3)
    for z in [5, 25]: K.mooring_pole(W, 3.6, z, -.6, 2.2)
    K.balustrade_line(W, (-9.6, 2), (-9.6, 28), 0, 1.0)
    K.murano_lamp(W, 7, 6)
    for z in (8, 22, 34): G.light(0, 7, z, 0xffe7c8, 260, 24)
    C.light(0, 8, 12, 0xffe2c0, 300, 22); W.light(0, 5, 15, 0xffe8d0, 260, 24)
    return [dict(key='vikit', name='Venetian kit sample', bounds=[-40, -5, 40, 45], portals=[], zones=[], anchor=(0, -5, 0),
                 views={'vi-street': dict(eye=[0, 1.7, 1.5], target=[0, 4.5, 30]),
                        'vi-facade': dict(eye=[-1, 2.5, 18], target=[6, 4.5, 20], lens=20),
                        'vi-vault': dict(eye=[27, 1.7, 1], target=[27, 7, 20]),
                        'vi-canal': dict(eye=[-23, 1.2, 1], target=[-23, 1.5, 20]),
                        'vi-capital': dict(eye=[24.5, 5.8, 6.5], target=[21.6, 6.2, 9])})]
