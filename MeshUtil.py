import bpy
import bmesh
from random import choice

ops = bpy.ops


def convert_curve_to_mesh(seed, name, randomize_ratio, randomize_offset, colours):
    ops.object.mode_set(mode='OBJECT')
    ops.object.select_all(action='DESELECT')
    ops.object.select_pattern(pattern=name)
    ops.object.shade_flat()
    ops.object.convert(target='MESH')
    ops.object.editmode_toggle()
    ops.mesh.select_all(action='SELECT')
    ops.mesh.remove_doubles(threshold=0.001)
    ops.object.mode_set(mode='OBJECT')

    object = bpy.data.objects[name]
    material = bpy.data.materials.get("GradientPaletteFlat")
    object.data.materials.append(material)

    randomize_mesh(seed, randomize_ratio, randomize_offset)
    set_mesh_uvs(object, choice(colours).random())
    
    
def randomize_mesh(seed, randomize_ratio, randomize_offset):
    ops.object.editmode_toggle()
    ops.mesh.select_all(action='DESELECT')
    ops.mesh.select_random(ratio=randomize_ratio, seed=seed)
    ops.transform.vertex_random(offset=randomize_offset, seed=seed)
    ops.object.mode_set(mode='OBJECT')


def set_mesh_uvs(object, uv):
    mesh = object.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.faces.ensure_lookup_table()

    uv_layer = bm.loops.layers.uv.verify()

    for face in bm.faces:
        for loop in face.loops:
            luv = loop[uv_layer]
            luv.uv = uv

    bm.to_mesh(mesh)
    
def join_meshes(name, object_names):
    ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = bpy.data.objects[name]
    for object_name in object_names:
        ops.object.select_pattern(pattern=object_name)
    ops.object.join()
