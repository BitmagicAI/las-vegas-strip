"""Bellagio tower colours (sRGB hex) and finishes; shared by the block export and the tower preview (no dependencies).
Cream body, white bands and crown, light patina roofs, after the owner's 2026-10-08 Google Earth reference."""
COLORS={'bel-cream':'ecd9ae','bel-white':'f3f0e8','bel-frame':'ebe7dc','bel-glass':'2c3537','bel-mullion':'a19f97','bel-patina':'94c4c8','bel-deck':'6b7072','bel-dome':'dde2e2'}
def finish(k,bs):
 if k=='bel-glass':bs.inputs['Metallic'].default_value=.18;bs.inputs['Roughness'].default_value=.2
 elif k=='bel-patina':bs.inputs['Metallic'].default_value=.08;bs.inputs['Roughness'].default_value=.55
 elif k.startswith('bel-'):bs.inputs['Roughness'].default_value=.78
