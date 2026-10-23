"""The Venetian's public interiors, laid out to the official resort map (2026-10-23). World metres: X east, Y up, Z south.

Sources (viewed for reference, never redistributed; docs/project-records/venetian-floorplans-2026-10-09.md):
- the official resort map, Levels 1 and 2 (venetianlasvegas.com/content/dam/venetian/resort/map.pdf);
- openly licensed photographs on Wikimedia Commons (Category:The Grand Canal Shoppes, "Venetian Hallway", "The Venetian
  Lobby", "Great Hall of The Venetian", "St. Mark's Square, The Venetian hotel", "The very European street lamps...").

Registration. The Venetian half of the Level 2 map is drawn axis-aligned and close to scale: map pixel (u, v) on the
2000 x 1272 page is world z = -811 + 0.41 (u - 1290), x = 436 - 0.41 (v - 400) (map left = north, top = east). The
Rialto lands within 10 m of the built bridge. The Level 1 page is drawn looser (its Expo box sits 140 px higher and its two
axes disagree), so Level 1 follows the map's topology and is fitted zone by zone inside the podium footprint
(relation/7770314, x 201..441, z -811..-459) and to the doors that already exist: the Doge's Palace entrance (225, -690),
the porte-cochere (227, -575), the hotel tower lobbies (250.6, -618.4) and (247.9, -492.7), the Rialto's upper gallery
(225.85, -644, y 6.24) and the east terrace door (438.6, -734, y 7.24). Residuals and decisions are in
docs/project-records/venetian-interiors-2026-10-23/README.md.

Every zone is an axis-aligned rectangle (x0, z0, x1, z1) unless it says otherwise; the builders shape what is inside.
"""

L1 = 0.24          # casino level (ground)
L2 = 7.24          # Grand Canal Shoppes (the east terrace door's level); the Rialto gallery joins at 6.24 by steps
PODIUM_TOP = 17.0  # the podium shell's top (build.py): every interior stays under it

# ---------------------------------------------------------------- what is already there (2026-10-23 survey)
# The podium shell (build.py, exterior): walls on relation/7770314 minus the three palazzi, 0.15..17 m, roof at 17.
# Its west wall runs at x 223.3..225.8 from z -757 to -631 (the palace frontage, with the palace door's 11 x 6.2 m glazed
# opening around (225.0, -685.14)); at z -631 it turns east to (251.2, -630.4) and then runs south at x ~250 (z -630.4
# .. -460). West of that wall and south of z -631 is OUTSIDE: the forecourt (x 223..250, z -631..-597) and the
# porte-cochere block (way/115776190, x 204..250, z -597..-553, a closed shell). A notch (x 224..242.5, z -657.8..-650.6)
# is outside too. A light-well hole in the podium roof sits over x 242.9..253.5, z -701.4..-681.6 (walls above 12.6 m).
# The hotel system owns tower 1's ground floor: its streamed lobby (build/hotels/venetian-1-lobby) is a 4 m gallery from
# the door on the podium's west wall at (250.7, -618.4) east to x 293.3 (z -620.4..-616.4, 4.8 m high), then an 84 m lobby
# room x 293.3..376.9, z -627.9..-608.9, 7.0 m high. Nothing of ours may enter x 250.5..377.2, z -628.1..-608.7 below 7.1 m.
# The Palazzo (way/180584269) starts at z ~-806 north of the podium; its street facades stand at x 318..378, z -868..-836.
HOTEL_LOBBY = dict(x0=250.5, z0=-628.1, x1=377.2, z1=-608.7, top=7.1)
PALACE_DOOR = (224.996, -685.139)          # the 'Venetian Grand Colonnade' portal (exterior-owned), facing +x
PODIUM_WEST_X = 225.8                       # inner faces of our west walls stay east of this (palace frontage)

# ---------------------------------------------------------------- Level 1 (L1 = 0.24)
# The Great Hall: the Strip entrance behind the Doge's Palace: a double-height hall with an oval fresco in a coffered,
# gilded ceiling, shopfronts, the GRAND CANAL SHOPPES sign, a stair up to the Scenic Overlook, and a 16 m arch east into
# the casino.
GREAT_HALL = dict(x0=225.8, z0=-707.5, x1=288.0, z1=-666.0, y=L1, height=12.0, door=PALACE_DOOR)
# The Scenic Overlook: a Level 2 balcony along the Great Hall's west wall (behind the palace loggia), continuing south as a
# gallery to the Rialto landing. Built with the Great Hall (it belongs to the lobby's GLB).
SCENIC_OVERLOOK = dict(x0=226.0, z0=-706.0, x1=232.0, z1=-648.0, y=L2)
# The Rialto landing: the bridge's upper gallery door (225.85, -644, y 6.24, facing +x) opens onto this mezzanine; steps
# rise 1 m to L2 for the overlook (north) and the Rialto street (east).
RIALTO_LANDING = dict(x0=225.85, z0=-652.0, x1=240.0, z1=-636.0, y=6.24)
RIALTO_GALLERY = (225.85, -644.0, 6.24)
# Arrivals: a vestibule under the landing with glazed doors in the podium wall onto the forecourt (a new portal at
# ARRIVALS_DOOR, facing north into the building).
ARRIVALS = dict(x0=224.0, z0=-652.0, x1=240.0, z1=-631.2, y=L1, height=5.7)
ARRIVALS_DOOR = (232.0, -630.75)
# The hotel lobby: east from the arrivals along the barrel-vaulted colonnade (diagonal checker marble floor, paired
# columns, fresco panels in the vault) to the domed rotunda with the Armillary Sphere, the front desk hall east of it.
COLONNADE = dict(x0=240.0, z0=-647.0, x1=316.0, z1=-633.0, y=L1, height=11.0)
ROTUNDA = dict(cx=328.0, cz=-640.0, r=11.0, y=L1, dome=15.0)        # dome top 15.24, under the podium roof
FRONT_DESK = dict(x0=339.0, z0=-652.0, x1=372.0, z1=-630.0, y=L1, height=7.0)
# The casino: east of the Great Hall, under the Shoppes. Coffered ceilings with fresco ovals and Murano chandeliers, slot
# banks, table pits, the cage, a high-limit salon; the rotunda opens into its south side. Ceiling 6.04: the canal bed
# above sits at 6.3.
CASINO = dict(x0=288.0, z0=-760.0, x1=392.0, z1=-652.0, y=L1, height=5.8)
# Restaurant Row: north from the casino to the podium's north wall.
RESTAURANT_ROW = dict(x0=336.0, z0=-805.0, x1=352.0, z1=-760.0, y=L1, height=6.0)
# The escalators from the casino up to St Mark's Square (an opening in the square's floor, x 375..383, z -742..-737).
ESCALATOR = dict(x0=375.0, x1=383.0, z_bottom=-726.0, z_top=-742.0)
# (The Waterfall Atrium, at the Palazzo end of Restaurant Row, stands inside the Palazzo's footprint where its street
# facades are; it is left for a pass that rebuilds that edge of the Palazzo. Restaurant Row ends at the podium wall.)

# ---------------------------------------------------------------- Level 2: the Grand Canal Shoppes
def map2(u, v):
    """Level 2 map pixel (u, v) -> world (x, z)."""
    return 436 - .41 * (v - 400), -811 + .41 * (u - 1290)

# The canal: from the Gondola Ride by the Waterfall Atrium east along the main street, then a loop around the island
# block. Centreline as world (x, z) points, 8.4 m of water between quays.
CANAL_WIDTH = 8.4
CANAL = [map2(1330, 678), map2(1400, 686), map2(1470, 680), map2(1515, 664), map2(1530, 640), map2(1532, 600),
         map2(1545, 588), map2(1610, 588), map2(1624, 602), map2(1624, 640), map2(1612, 652), map2(1545, 652)]
CANAL_LOOP_FROM = 6          # points 6.. close back onto point 4's bend: the island block sits inside the loop
# St Mark's Square: open onto the canal's east quay (map u 1400..1470, v 520..650), under a dusk sky, arcades on three
# sides; the Expo lobby access at its east end.
ST_MARKS = dict(x0=331.0, z0=-770.0, x1=396.0, z1=-735.0, y=L2)
# Streets (walkable, building fronts on both sides). Each is a polyline of world (x, z) with a width.
STREETS = [
    dict(name='canal east quay', pts=[map2(1340, 650), map2(1400, 652), map2(1500, 640)], width=7.0),
    dict(name='canal west quay', pts=[map2(1340, 706), map2(1470, 708), map2(1515, 690)], width=5.0),
    # Level 2 keeps off the double-height Great Hall (x 225.8..288, z -707.5..-666) and the lobby's vaults (x 224..372,
    # z -652..-628): from the canal loop the Rialto street runs in the band between them (z -666..-652) to the landing.
    dict(name='rialto street', pts=[(330.0, -659.0), (240.0, -659.0)], width=14.0),
    dict(name='to the east terrace', pts=[(372.0, -712.0), (410.0, -726.0), (438.6, -734.0)], width=7.0),
]
EAST_TERRACE = (438.6, -734.0, L2)
SKY_HEIGHT = 9.6          # painted sky above the L2 street (L2 + 9.6 = 16.84, just under the podium top)
SQUARE_SKY_HEIGHT = 9.4   # St Mark's: a darker dusk sky
