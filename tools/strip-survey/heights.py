"""Placeholder heights in metres; these are estimates, never surveyed values.

The creator supplied local one-storey ranges of 4–5 m residential and
4.5–7 m commercial. Use rounded midpoints and a neutral 5 m for untyped
footprints. Do not infer extra storeys from footprint area.
"""
RESIDENTIAL = {'house', 'detached', 'semidetached_house', 'terrace', 'residential',
               'apartments', 'bungalow', 'dormitory'}
COMMERCIAL = {'commercial', 'retail', 'office', 'industrial', 'warehouse', 'hotel',
              'supermarket', 'kiosk', 'public', 'civic', 'school', 'hospital'}
SMALL = {'garage', 'garages', 'shed', 'hut', 'service', 'outbuilding'}
SHELTER = {'roof', 'carport'}
BUSINESSES = {'restaurant', 'fast_food', 'casino', 'bar', 'cafe', 'bank',
              'pharmacy', 'theatre', 'cinema', 'conference_centre', 'fuel'}


def height_profile(tags):
    # A roof-only part should not inherit the use of its surrounding hotel.
    kind = tags.get('building:part', '')
    if kind in ('', 'yes'):
        kind = tags.get('building', '')
    if kind in SMALL:
        return 'utility', 3.0
    if kind in SHELTER or tags.get('amenity') == 'shelter':
        return 'shelter', 3.5
    use = tags.get('building:use', kind)
    if use in RESIDENTIAL:
        return 'residential', 4.5
    if (use in COMMERCIAL or tags.get('shop') not in (None, '', 'no')
            or tags.get('amenity') in BUSINESSES
            or tags.get('tourism') in ('hotel', 'motel', 'museum')):
        return 'commercial', 6.0
    return 'unclassified', 5.0


def estimated_height(tags, levels=None, base=0):
    profile, first_storey = height_profile(tags)
    if levels is None:
        return base + first_storey, profile
    # Existing upper-storey estimate remains 3 m; only the ground storey
    # gains the allowance for structure/parapet and taller public spaces.
    return first_storey + max(0, levels - 1) * 3.0, profile
