# Research and baseline review

Read on 2026-11-05. Sources are reference only; no third-party imagery is redistributed.

- [Culinary Health Fund contacts](https://www.culinaryhealthfund.org/contacts/?lang=en) lists Advocacy at 515 East Saint Louis Avenue, Building C. This supports the building identity, not present-day facade lettering or interior geometry.
- [Official diabetes passport](https://www.culinaryhealthfund.org/pdf-diabetes-passport-english_pdf/) identifies a Building C education room. No usable room dimensions or circulation plan was established; do not invent a public interior from this text.
- [Nevada tobacco retailer list, November 2025 path](https://tax.nv.gov/wp-content/uploads/2025/11/Licensed-Tobacco-Retail-Accounts.pdf) lists City Market & Liquor at 515 E Oakey Blvd. Supports historical business/address identity only, not current storefront appearance.

All six installed neutral daylight baseline views were inspected: office front arcade, rear doors/steps, roof/forecourt; market front, rear and roof. Existing office front has angular paving fragments and simplified cornice; market has plain storefront stripes and unverified rear service details. No changes selected yet. Existing dated Maps references remain in the building records; fresh visual reference inspection is next after the GPU walk finishes.

Initial actual office walk reached the first ramp endpoint in X/Z at feet y=0.632, but failed a mistaken expected y=0.12 (ground-apron value). The modeled ramp/terrace is y=0.6, consistent with CPU walk feet about0.67 including controller offset. Corrected the three elevated waypoints to0.6, keeping identical X/Z and tolerance. Original failure report retained in before/walk-initial-height-expectation-error.json. Market six legs passed in the initial run. Corrected whole-route result pending.

## Visual references inspected 2026-11-05

- [City Market panorama](https://www.google.com/maps/@?api=1&map_action=pano&pano=9zbf84J5Pg6tjoYYS2-r2g&heading=0&pitch=0), image label January 2022, snapped36.151381,-115.1511372. Red roof, white fascia, blue/white/red storefront bands, central aluminum double door with narrow transom; two small dark flood fixtures above the roof flanking the sign. Vending fixtures and advertisements remain omitted. No newer appearance claim.
- [Building C panorama](https://www.google.com/maps/@?api=1&map_action=pano&pano=WV1MrJhVP2ijyOcYXcalxw&heading=60&pitch=0), image label February 2022, snapped36.1482074,-115.1535465. Zoomed frontage shows pale entry-tower arched infills with dark surrounds, red hip cap, layered white cornice over arcade. This contrasts with existing green tower glazing and white arch trim. Fence, pylon and complex parking remain outside this small pass.

## Decisions for the owner

Correct tower arch surrounds/infill and add two shallow cornice bands using existing materials. Keep tower, circulation and roof dimensions. At City Market add the narrow glazed transom and two non-emitting rooftop flood housings; no new scene lights. Fixture bodies0.40×0.23×0.18m, stems0.31m; arch surround radius0.065m and cornice projections0.14/0.22m are inferred approximations from the photos, not survey measurements. Preserve roads, apron footprint, collision and interiors. Do not infer room layout from the official education-room reference.

Corrected baseline actual route12/12legs passed and all four endpoint PNGs visually inspected: office terrace/return, market outward/return. They establish short entrance circulation, not a full perimeter or driving review. Source support164samples and12CPUlegs passed. The initial height-expectation error remains archived.
