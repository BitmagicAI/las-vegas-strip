# Luxor obelisk relief refinement

Issue197 / draft PR459 against next. Corrects the repeated pedestal figures from five to four on both faces, corroborated by October2024 north/south Street View and a September2019 north photograph. All relief geometry is original. Continuous carved profiles replace the rounded segmented bodies; headdress, collar, brow/eyes, nose, mouth and kilt lines are modeled. The raised lettering is enlarged and given a warm metal backing.

The existing140ft overall height, inferred tunnel clearance and all collision geometry are retained. Existing decorative glyph texture is reused, not a historical transcription. Fine facial accuracy and full Luxor landscape remain deferred; no scan-quality or whole-resort completion claim.

Four baseline cameras (front first) and four installed views personally inspected. A separate clean baseline performance run replaced a trial captured while reference tabs were open. Initial export failed on missing procedural texture sources while Blender returned0; only this model's original texture generator was rerun, and subsequent exports use --python-exit-code1. First actual front view exposed mismatched letter fonts; exporter corrected the material-name prefix so blue face and gold backing share the same font. Corrected front capture and normal walkthrough are pending.

14,156 source triangles with zero degenerate faces. Collision JSON and packed collision remain byte-identical.1,473 packed-collision route samples pass. Typecheck and three applicable tests pass. No geographic export or bake yet. Complete step7, final matching captures and LFS accounting before readiness. Published validation belongs to the owner's release step.
