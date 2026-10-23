/** Local filming: every distance-based level of detail held at full detail while a take runs (the owner, 2026-10-08:
 * "use maximum LOD at all times when rendering, there's quite a lot of LOD popping going on when the camera moves").
 * The selections are throttled to wall-clock time, which the frame recorder stretches, so blocks swapped every few frames.
 * Read by CityLod, CityDetailRanges, GroveLod, StripLandmarks and BigAppleCoaster; set by the film host. */
export const filmDetail={full:false};
