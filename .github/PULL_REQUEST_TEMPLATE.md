Task: `<task-id>` · Closes #<issue>

## What changed
<!-- One paragraph, then the list of files or assets that changed. -->

## Evidence
<!-- Before/after game captures from the same cameras, walk/collision audit output, probe numbers. -->

## Checklist
- [ ] The task's "Done when" list is met (`node tools/tasks/pick.mjs show <task-id>`)
- [ ] `bitmagic check` (or `npx tsc --noEmit`) passes, and the game loads with `bitmagic dev`
- [ ] Relevant `tests/*.test.mjs` pass: `node --import ./tools/ts-register.mjs tests/<name>.test.mjs`
- [ ] Changed GLBs are re-optimized, their `version.json` revision is bumped, and `python3 tools/release/asset-pack.py list` is re-run
- [ ] The block record's `remaining` list and evidence are updated; `python3 tools/resort-blocks/review.py` passes; `python3 tools/tasks/build-board.py` is re-run
- [ ] No runtime light added, removed or hidden; no per-frame JS arrays or allocations (AGENTS.md)
- [ ] No third-party photos, plans or screenshots committed; sources are linked in the record
- [ ] I agree to license this contribution under the repository's terms (LICENSE, LICENSE-CONTENT.md, LICENSE-DATA.md)
