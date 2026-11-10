# Wynn parking deck scoped refinement

All seven installed daylight views and six actual-walk endpoint captures inspected. Gray parking deck and white repeated banks replace the corrugated-looking roof material on way111322083. Encore podium135291730 and Wynn retailpodium111322055 remain unchanged; their stale inventory ownership now points to the existing wynnEncoreExterior generator. No second geometry owner was introduced.

11localchecks passed,839existing lowroof support samples,24before/24afteractual keyboard rooflegs,9devsmoke stops without errors. Roof walks do not certify garage-to-lobby access. Source collision and labels are exact;85oldgroups exact,one roofmaterial group changed.91/92binarycells identical; unrelatedLOD drift restored.

Performance is variable: front p50 rose16.7→26.9ms (candidate17.3ms); roof22.3→23.6ms; Encore17→21ms; retail21.8→16.8ms; aerial19.3→16.7ms; lakefront16.6→19.2ms; club18.1→17.1ms. Static samples do not establish a speedup; slower samples are retained. No runtime code or light changes.

Original line layout is inferred:0.11m paint,2.7m stall pitch,5.2m depth. Existing20.04m roof height retained. Exact stall count, ramp slope, full access, roof equipment/weathering, storefronts, landscaping and public interiors remain unresolved. Thin lines alias at distance. No photorealism or whole-block claim.

Three initial cameras were obstructed/poorly framed and replaced before the accepted baseline. Rejected evidence retained. An initial raw comparison to the main checkout failed because its parent asset is stale; current baseline instead verified against the optimized manifest source hash and HEAD runtime LFS object. No other-session asset was overwritten.

For the release step: CDN/published-game checks and owner acceptance. No main merge, upload to CDN, publish or release.
