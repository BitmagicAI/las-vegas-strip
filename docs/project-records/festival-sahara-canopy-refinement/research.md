# Festival / Sahara canopy baseline

Six matched neutral daylight images inspected. Festival front and canopy simplified, broader site surface missing; McDonalds canopy/arches present, arch lattice absent, supports lean, doors/sign detail coarse. No geometry edits.

p95 Festivalfront18.2/roof19.0/south17.9ms; McDonaldsfront18.2/under32.9/roof32.0ms. Slowbaselines retained. New reproducible .8m grid inset.35m:1008Festival+535canopy=1543supportsamples pass; originalignored462/239setsunavailable.10FestivalCPUgroundlegs and12canopyCPUlegs pass. Actualwalkbaseline next.

Official reference lead [Circus Circus Festival Grounds](https://www.circuscircus.com/festival-grounds/) found; visual inspection pending. It describes the venue, not enough to identify this specific auxiliary building’s function or hidden doors. FreshdatedMaps/officialphotographs follow afterGPUwalk.

17:25 correction: original Festival CPU test falsely passed XZ arrival while falling; retained its JSON and documented invalid heights (-60.97m etc). Actual baseline timed out at600s, no valid result. New scoped CPU audit follows the existing1.3m apron at .65m offset and requires vertical support:32legs pass. Corrected actual script uses these verified feet heights plus12unchanged canopy legs,44total. GPU92964 running /tmp/fs-actual-before-corrected.log. No geometrychanges; freshMaps waits GPU. Do not repeat old22leg successclaim.
