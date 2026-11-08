# Atomic Golf south terrace refinement

Two mapped buildings retained: clubhouse way/1213440758 and south terrace way/1553042969. This bounded pass changes upper terrace glass and adds two original static ceiling fans and a dark soffit. Twenty-nine source groups and all labels are unchanged; the split glass group retains every triangle. Lower ground glazing remains unchanged. No collision or access change.

Fresh Google October2025 panorama, contractor entrance photograph and lighting-supplier terrace photograph were inspected. The official Cosmic Lounge image depicts an interior and was deliberately not used as terrace furniture evidence. References and inferred dimensions are in references.md. No third-party photos, plans or textures are copied.

Decisions for the owner: use the existing clear-rail material family with alpha0.16/roughness0.19, preserving the exact guard geometry; infer two static8blade fans within the existing footprint. Fan count and positions are not surveyed. Keep the existing roof and add a dark visual underside. Structural levels and all public vertical-access gaps remain.

Before3matching daylightviews and6actualperimeterwalklegs passed and were visually inspected. Candidate3views inspected: main facade unchanged, upper rails now transparent, two fans visible against dark ceiling. Optimization3,308,860->1,010,688bytes,61,822triangles retained,0textures; standardWebPpass executed and skips textureless models. Shared materials unchanged; validator0errors/0warnings. Installed validation is pending; see checkpoint.

For the release step: CDN and published-game checks belong to the owner. No main merge, release, publish, CDN upload or settings changes.

One shared bake complete; unrelated GoldCoast/Wyndham LOD blocks restored before staging, atomicGolf-only change accepted.91/92cells byte-identical, onlycell-1_-5.bin changed;collision JSON unchanged.13local checks passed. First legacy collision test lacked its ignored fixture in this worktree; restored original236/220samples from maincheckout (same collision hash), archived both fixtures and failed attempt, then resumed checks7–12 without repeating passed checks. After3views running session47009 /tmp/atomic-after.log. Pending actualafterwalk/smoke/performance/finalarchive/PR555.

Focused terrace control16.7/19.5ms median/p95 versus installed repeat16.8/17.8ms: initial tail increase did not reproduce. Both extra captures inspected; originalcell/asset replacement requests verified. All initial results retained.

Final bounded validation:13localchecks,236+220collision samples,6before+6after actualperimeterlegs and9smokestops passed. Three installeddaylightviews inspected.91/92cells unchanged, onlycell-1_-5.bin changed. Initial missingcollisionfixture failure preserved; originalfixtures restored frommaincheckout and archived, then checkresumed. Allgeneratedcaptures indexed. Performance evidence andlimits inperformance.json. No publicverticalaccess/full-block claim. Ready for LFS audit andPR555 merge.
