"""The recording backend: same surface as BpyScene, builds nothing. Used by `--dry-run` and by
the unit tests, so a level script's counts, colliders and JSON can be checked without Blender."""
from __future__ import annotations


class NullScene:
    available = False

    def __init__(self) -> None:
        self.objects: list[dict] = []
        self.materials: dict[str, dict] = {}
        self.collections: list[str] = []

    def reset(self) -> None:
        self.objects.clear()
        self.materials.clear()
        self.collections.clear()

    def material(self, name, rgb, metal, roughness, glow, alpha) -> None:
        self.materials[name] = {'rgb': tuple(rgb), 'metal': metal, 'roughness': roughness, 'glow': glow, 'alpha': alpha}

    def begin_collection(self, name: str) -> None:
        self.collections.append(name)

    def end_collection(self) -> None:
        pass

    def box(self, name, world_pos, size, world_yaw, material, bevel) -> None:
        self.objects.append({'kind': 'box', 'name': name, 'position': tuple(world_pos), 'size': tuple(size), 'yaw': world_yaw, 'material': material, 'bevel': bevel})

    def prism(self, name, world_vertices, material) -> None:
        self.objects.append({'kind': 'prism', 'name': name, 'vertices': list(world_vertices), 'material': material})

    def hull(self, name, world_vertices, material) -> None:
        self.objects.append({'kind': 'hull', 'name': name, 'vertices': list(world_vertices), 'material': material})

    def text(self, name, string, world_pos, world_yaw, size, material, extrude, both_faces) -> None:
        self.objects.append({'kind': 'text', 'name': name, 'text': string, 'position': tuple(world_pos), 'yaw': world_yaw, 'size': size, 'material': material, 'both_faces': both_faces})

    def coplanar_overlaps(self) -> tuple[int, list[str]]:
        return 0, []   # no geometry without Blender; the real build reports flush faces

    def save_blend(self, path: str) -> None:
        pass

    def export_glb(self, path: str) -> int:
        return 0
