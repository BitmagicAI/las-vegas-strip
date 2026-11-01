# Resorts World Hilton arrival pass, PR452

The original Hilton arrival canopy replaces the generic solid northern podium projection. Its broad bronze roof, paired pale piers, inset ceiling panels, square lanterns and island palms/benches follow the linked official photographs and January2025 Street View. The dimensions, registration and planting counts are estimates. No reference pixels are used as game textures.

The existing high-rise guest entrance remains. The rear wall is closed; this pass does not claim a new public lobby. Conrad/Crockfords, Strip frontage and the pool terrace retain their existing geometry. All discrepancies remain in the block record.

## Rebuild

- The full exterior builder calls `resorts_world_arrival.apply` after the existing model. For a scoped repeat, `resorts_world_arrival.py` reads the saved pre-pass model in `.bitmagic/city-exterior-backups/rw-arrival`.
- After geographic source rebuilding, run `tools/city-exteriors/install-rw-arrival.py` before the geographic export/packing. It cuts only building materials and above-ground building collision within the Hilton mask; roads, ground and the separate high-rise guest-entry kit remain.
- Export the changed exterior and geographic cells with `--preserve-surfaces`, optimize level then WebP, pack collisions, install optimized candidates, bake once, and stage.
- Run the scoped geometry/collision audits and the normal walking probe, then all step7 checks. Use identical cameras in `probe-rw-arrival.js` for comparisons.

The initial Hilton baseline camera was obstructed by the adjacent garage. It was corrected and the complete baseline recaptured before installation. Initial preview exposed the retained generic six-metre city shell; both its faces and collision are removed in the same PR before final review.

## For the release step

CDN upload and published cold-load checks remain with the owner before next merges to main. They do not block the local merge.
