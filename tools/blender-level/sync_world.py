#!/usr/bin/env python3
"""Carry a built level's doors and spawn into the game's world.json.

    python3 tools/blender-level/sync_world.py build/level/hut.doors.json build/level/hut.mesh-level.json src/work/world.json
        [--level-id <id>] [--keep-spawn] [--keep-terrain]

- doors: upserts `worldProfileData.doors[]` by id. The build owns the geometry fields (position,
  rotationY, width, height, thickness) and the animation; creator-owned fields on an existing
  entry — kind, keyId, assetId, color, autoOpenRadius, maxOpenAngleDeg — survive unless the
  build sets them. Doors in world.json that the build no longer has are reported, never deleted.
- spawn: the `spawn` landmark becomes playerSpawnPosition / playerSpawnRotation (skip: --keep-spawn).
- terrain: sets `terrain.shape` to 'none' so no voxel ground is built under the level (skip:
  --keep-terrain).

A script rather than jq because the merge rule IS the point.
"""
import json
import sys

BUILD_OWNED = ('position', 'rotationY', 'width', 'height', 'thickness', 'animation')


def merge_doors(existing: list, built: list, level_id: str | None) -> tuple[list, dict]:
    by_id = {d['id']: dict(d) for d in existing}
    added, updated = [], []
    for door in built:
        entry = by_id.get(door['id'])
        if entry is None:
            entry = dict(door)
            added.append(door['id'])
        else:
            for key in BUILD_OWNED:
                entry[key] = door[key]
            for key in ('kind', 'autoOpenRadius'):
                if key in door and key not in entry:
                    entry[key] = door[key]
            updated.append(door['id'])
        if level_id:
            entry['levelId'] = level_id
        by_id[door['id']] = entry
    built_ids = {d['id'] for d in built}
    orphans = [d['id'] for d in existing if d['id'] not in built_ids]
    return list(by_id.values()), {'added': added, 'updated': updated, 'orphans': orphans}


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print(__doc__, file=sys.stderr)
        return 2
    doors_path, level_path, world_path = argv[:3]
    level_id = argv[argv.index('--level-id') + 1] if '--level-id' in argv else None
    with open(doors_path) as f:
        built_doors = json.load(f)
    with open(level_path) as f:
        level = json.load(f)
    with open(world_path) as f:
        world = json.load(f)
    profile = world.setdefault('worldProfileData', {})

    profile['doors'], report = merge_doors(profile.get('doors', []), built_doors, level_id)
    print(f"doors: {len(report['added'])} added, {len(report['updated'])} updated" + (f", not in this build: {', '.join(report['orphans'])}" if report['orphans'] else ''))

    spawn = next((l for l in level.get('landmarks', []) if l['name'] == 'spawn'), None)
    if spawn and '--keep-spawn' not in argv:
        x, y, z = spawn['position']
        profile['playerSpawnPosition'] = {'x': x, 'y': y, 'z': z}
        profile['playerSpawnRotation'] = spawn.get('yaw', 0.0)
        print(f'spawn: playerSpawnPosition ({x}, {y}, {z}) yaw {spawn.get("yaw", 0.0)}')
    elif not spawn:
        print('spawn: no `spawn` landmark in the level — playerSpawnPosition left as is')

    if '--keep-terrain' not in argv:
        terrain = profile.setdefault('terrain', {})
        if terrain.get('shape') != 'none':
            terrain['shape'] = 'none'
            print("terrain: shape set to 'none' (no voxel ground under the level)")

    with open(world_path, 'w') as f:
        json.dump(world, f, indent=2)
        f.write('\n')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
