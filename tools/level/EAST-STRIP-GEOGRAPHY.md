# East Strip geography correction

Reference: [official Las Vegas Monorail map](https://www.lvmonorail.com/wp-content/uploads/2024/04/LVMC_CustomerServiceMap_11x8.5_1223.pdf).
North is negative game Z, positive Blender Y. North to south: Flamingo, Horseshoe, Paris, Planet Hollywood. Cromwell occupies the real intersection frontage but is not yet modeled.

The compressed game parcels are:
- Flamingo: (145, -237), north of Flamingo Road at Z=-166.
- Horseshoe: (110, -116), north of Paris, immediately south of the road. Its footprint is compressed to 36 × 62 m to clear the detailed Paris X-shaped tower.
- Paris: existing detailed geometry unchanged; hotel core (173, -75).
- Planet Hollywood: (131, 218), south of Paris and opposite Cosmopolitan. The generic skyline block has been replaced by the reference-based folded tower and rounded wings in `finish_resort_exteriors.py`; the playable podium now extends X=65–198 and Z=173–274.

`correct_east_strip.py` patches the incremental saved Blender scene once and updates collision data. Labels, fins, fire scarring and facade debris follow their hotels. `vegas.py` also contains corrected coordinates for subsequent fresh builds.

The localhost preview loads the updated local GLB. The user requested local-only development; do not upload assets or publish without a new explicit request.
