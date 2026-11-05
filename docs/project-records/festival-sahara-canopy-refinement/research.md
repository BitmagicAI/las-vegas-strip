# Festival / Sahara canopy baseline

Six matched neutral daylight images inspected. Festival front and canopy simplified, broader site surface missing; McDonalds canopy/arches present, arch lattice absent, supports lean, doors/sign detail coarse. No geometry edits.

p95 Festivalfront18.2/roof19.0/south17.9ms; McDonaldsfront18.2/under32.9/roof32.0ms. Slowbaselines retained. New reproducible .8m grid inset.35m:1008Festival+535canopy=1543supportsamples pass; originalignored462/239setsunavailable.10FestivalCPUgroundlegs and12canopyCPUlegs pass. Actualwalkbaseline next.

Official reference lead [Circus Circus Festival Grounds](https://www.circuscircus.com/festival-grounds/) found; visual inspection pending. It describes the venue, not enough to identify this specific auxiliary building’s function or hidden doors. FreshdatedMaps/officialphotographs follow afterGPUwalk.

17:25 correction: original Festival CPU test falsely passed XZ arrival while falling; retained its JSON and documented invalid heights (-60.97m etc). Actual baseline timed out at600s, no valid result. New scoped CPU audit follows the existing1.3m apron at .65m offset and requires vertical support:32legs pass. Corrected actual script uses these verified feet heights plus12unchanged canopy legs,44total. GPU92964 running /tmp/fs-actual-before-corrected.log. No geometrychanges; freshMaps waits GPU. Do not repeat old22leg successclaim.

## Fresh references and decisions — November 5

Corrected44actual baseline legs pass;8endpoint images inspected/saved. Canopy terminal views face close glazing, while six matched views supply architectural evidence.

[McDonalds February2026 Street View](https://www.google.com/maps/@?api=1&map_action=pano&pano=dq9urKzevlOrWwRD0H4T4Q&heading=335&pitch=4) inspected at closer zoom: white leaning supports, pale deep canopy, yellow arches with open diagonal lattice above roof. Extensive planted gravel/grass/shrubs and detached sign remain absent from authored scope. Camera address198E Sahara not target address. [Satellite](https://www.google.com/maps/@36.14397,-115.15508,21z/data=!3m1!1e3) confirms square equipment opening, broad roof and curved drive. No satellite capture date exposed. Official restaurant-specific photo search did not find a usable primary photo; do not substitute a different McDonalds location.

[Festival February2026 Street View](https://www.google.com/maps/@?api=1&map_action=pano&pano=s5QoHy8Ns9ZbshPreQVhQA&heading=180&pitch=3) shows low tan wall behind tall pale fence and planting. Hidden doors and function stay unverified. [Satellite](https://www.google.com/maps/@36.14333,-115.16000,21z/data=!3m1!1e3) visually inspected: stepped white roof, two square fan units, visible low winding service lines running beside equipment and along north edge, green south strip. Map label235 is not painted signage. [Operator page](https://www.circuscircus.com/festival-grounds/) and crowd overview photo inspected; it supports venue identity, not this building's exact function or interior. No thirdparty images committed.

Reversible choices: original .55m diagonal lattice spacing with .018m radius bars clipped inside both existing arch profiles above4.72m; existing arches and support collision retained. Festival .035m radius roof service runs at4.08m follow approximate visible paths, no asserted utility type. Keep all full-site, landscaping, hidden-access and interior gaps. This is detail refinement, not whole-block completion.
