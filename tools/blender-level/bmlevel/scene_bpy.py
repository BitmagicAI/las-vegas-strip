"""The Blender backend: real meshes, materials, text and the GLB export. Runs only inside Blender.

Every object is named and lives in the collection of the `context()` that made it, so the saved
.blend stays editable part by part. The GLB is the opposite: `export_glb` duplicates every mesh
into a scratch collection, joins the copies per material (one draw call each) and exports only
those — the named parts are untouched, which is why the .blend is saved BEFORE the export."""
from __future__ import annotations

import math
import os

import bmesh
import bpy
from mathutils import Vector

from bmlevel.core import blender_yaw, coplanar_overlaps, flat_to_points, from_blender, to_blender


class BpyScene:
    available = True

    def __init__(self) -> None:
        self.materials: dict[str, bpy.types.Material] = {}
        self._collection_stack: list[bpy.types.Collection] = []
        self.reset()

    # ---- scene lifecycle --------------------------------------------------

    def reset(self) -> None:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        self.materials.clear()
        self._collection_stack.clear()
        bpy.context.preferences.filepaths.save_version = 0

    @property
    def collection(self) -> bpy.types.Collection:
        return self._collection_stack[-1] if self._collection_stack else bpy.context.scene.collection

    def begin_collection(self, name: str) -> None:
        col = bpy.data.collections.new(name)
        self.collection.children.link(col)
        self._collection_stack.append(col)

    def end_collection(self) -> None:
        self._collection_stack.pop()

    # ---- materials --------------------------------------------------------

    def material(self, name, rgb, metal, roughness, glow, alpha) -> None:
        m = bpy.data.materials.new(name)
        m.use_nodes = True
        m.use_backface_culling = alpha >= 1
        p = m.node_tree.nodes['Principled BSDF']
        p.inputs['Base Color'].default_value = (*rgb, 1)
        p.inputs['Metallic'].default_value = metal
        p.inputs['Roughness'].default_value = roughness
        p.inputs['Alpha'].default_value = alpha
        if glow:
            p.inputs['Emission Color'].default_value = (*rgb, 1)
            p.inputs['Emission Strength'].default_value = glow
        if alpha < 1:
            m.surface_render_method = 'BLENDED'
        m.diffuse_color = (*rgb, alpha)
        self.materials[name] = m

    def _mat(self, name: str) -> bpy.types.Material:
        if name not in self.materials:
            raise KeyError(f'material {name!r} was never declared — call mat({name!r}, (r, g, b)) first')
        return self.materials[name]

    # ---- meshes -----------------------------------------------------------

    def _add_mesh(self, name: str, verts, faces, material: str) -> bpy.types.Object:
        mesh = bpy.data.meshes.new(name)
        mesh.from_pydata(verts, [], faces)
        mesh.update()
        obj = bpy.data.objects.new(name, mesh)
        self.collection.objects.link(obj)
        obj.data.materials.append(self._mat(material))
        return obj

    def box(self, name, world_pos, size, world_yaw, material, bevel) -> None:
        w, h, d = (float(s) for s in size)
        hx, hy, hz = w / 2, d / 2, h / 2  # Blender x = game x, Blender y = -game z (depth), Blender z = game y
        verts = [(-hx, -hy, -hz), (hx, -hy, -hz), (hx, hy, -hz), (-hx, hy, -hz), (-hx, -hy, hz), (hx, -hy, hz), (hx, hy, hz), (-hx, hy, hz)]
        faces = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
        obj = self._add_mesh(name, verts, faces, material)
        obj.location = to_blender(world_pos)
        obj.rotation_euler = (0.0, 0.0, blender_yaw(world_yaw))
        if bevel:
            bm = bmesh.new()
            bm.from_mesh(obj.data)
            bmesh.ops.bevel(bm, geom=list(bm.edges), offset=min(bevel, min(w, h, d) / 2.5), segments=2, affect='EDGES', clamp_overlap=True)
            bm.to_mesh(obj.data)
            bm.free()
            obj.data.update()

    def prism(self, name, world_vertices, material) -> None:
        pts = flat_to_points(world_vertices)
        n = len(pts) // 2
        verts = [to_blender(p) for p in pts]
        faces = [tuple(reversed(range(n))), tuple(range(n, 2 * n))] + [(i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n)]
        self._add_mesh(name, verts, faces, material)

    def hull(self, name, world_vertices, material) -> None:
        bm = bmesh.new()
        for p in flat_to_points(world_vertices):
            bm.verts.new(to_blender(p))
        bm.verts.ensure_lookup_table()
        res = bmesh.ops.convex_hull(bm, input=list(bm.verts))
        bmesh.ops.delete(bm, geom=[g for g in res['geom_interior'] if isinstance(g, bmesh.types.BMVert)], context='VERTS')
        mesh = bpy.data.meshes.new(name)
        bm.to_mesh(mesh)
        bm.free()
        mesh.update()
        obj = bpy.data.objects.new(name, mesh)
        self.collection.objects.link(obj)
        obj.data.materials.append(self._mat(material))

    def text(self, name, string, world_pos, world_yaw, size, material, extrude, both_faces) -> None:
        faces = [world_yaw, world_yaw + math.pi] if both_faces else [world_yaw]
        for i, yaw in enumerate(faces):
            curve = bpy.data.curves.new(f'{name}-{i}', type='FONT')  # Blender's bundled Bfont — no font file needed
            curve.body = string
            curve.size = size
            curve.extrude = extrude
            curve.align_x = 'CENTER'
            obj = bpy.data.objects.new(name if i == 0 else f'{name} (reverse)', curve)
            self.collection.objects.link(obj)
            obj.location = to_blender(world_pos)
            # A FONT lies in Blender XY facing +Z; stand it up so it faces game +Z at yaw 0, then yaw it.
            obj.rotation_euler = (math.pi / 2, 0.0, blender_yaw(yaw) + math.pi)
            obj.data.materials.append(self._mat(material))
            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)
            bpy.ops.object.convert(target='MESH')
            obj.select_set(False)

    # ---- output -----------------------------------------------------------

    def coplanar_overlaps(self) -> tuple[int, list[str]]:
        """Every mesh face in game space, keyed by material, through core's z-fighting check."""
        faces = []
        for obj in bpy.data.objects:
            if obj.type != 'MESH':
                continue
            m = obj.matrix_world
            mats = obj.data.materials
            for poly in obj.data.polygons:
                material = mats[poly.material_index].name if poly.material_index < len(mats) and mats[poly.material_index] else '?'
                faces.append(([from_blender(m @ obj.data.vertices[v].co) for v in poly.vertices], material))
        return coplanar_overlaps(faces)

    def save_blend(self, path: str) -> None:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(path))

    def export_glb(self, path: str) -> int:
        """Join duplicates per material and export those alone; the named parts stay as they are."""
        scratch = bpy.data.collections.new('__export__')
        bpy.context.scene.collection.children.link(scratch)
        by_material: dict[str, list[bpy.types.Object]] = {}
        for obj in list(bpy.data.objects):
            if obj.type != 'MESH' or obj.users_collection[0] is scratch:
                continue
            copy = obj.copy()
            copy.data = obj.data.copy()
            scratch.objects.link(copy)
            key = obj.data.materials[0].name if obj.data.materials else '__none__'
            by_material.setdefault(key, []).append(copy)
        bpy.ops.object.select_all(action='DESELECT')
        joined: list[bpy.types.Object] = []
        for key, objs in by_material.items():
            for o in objs:
                o.select_set(True)
            bpy.context.view_layer.objects.active = objs[0]
            if len(objs) > 1:
                bpy.ops.object.join()
            active = bpy.context.view_layer.objects.active
            active.name = f'Level_{key}'
            joined.append(active)
            bpy.ops.object.select_all(action='DESELECT')
        for o in joined:
            o.select_set(True)
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        bpy.ops.export_scene.gltf(
            filepath=os.path.abspath(path),
            export_format='GLB',
            use_selection=True,
            export_apply=True,
            export_yup=True,
            export_lights=False,
            export_cameras=False,
            export_materials='EXPORT',
        )
        for o in joined:
            bpy.data.objects.remove(o, do_unlink=True)
        bpy.data.collections.remove(scratch)
        return os.path.getsize(path)
