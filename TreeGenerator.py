import bpy
from dataclasses import dataclass
from typing import Tuple, Callable, List
from math import sin, cos, pi, pow
from random import random, randrange, uniform, seed as random_seed, choice
from mathutils import Vector, Euler
from PrintUtil import print_bezier_point, print_spline, print_splines
from MeshUtil import convert_curve_to_mesh, randomize_mesh, set_mesh_uvs, join_meshes

ops = bpy.ops

def switch_to_object_mode():
    if bpy.context.active_object:
        ops.object.mode_set(mode='OBJECT')


def remove_object(name):
    print(f'remove_object({name})')
    switch_to_object_mode()

    if name in bpy.data.objects:
        obj = bpy.data.objects[name]
        ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        ops.object.delete(use_global=False)


@dataclass
class PointReference:
    is_trunk: bool
    spline_index: int
    point_index: int

@dataclass
class UVRange:
    x: float
    y_min: float
    y_max: float    

    def random(self):
        return (self.x, uniform(self.y_min, self.y_max))


@dataclass
class TrunkConfig:
    """
    This configuration object determines how the first segment of the tree trunk will be constructed.
    
    Attributes:
        resolution            Used when converting curve to mesh. Higher values make round trunk and branches; lower values make square trunk and branches.
        height_min   
        height_max            Trunk height will be a random value between height_min and height_max.
        thickness_min
        thickness_max         Trunk thickness will be a random value between thickness_min and thickness_max.
        base_thickness_factor Very base of trunk will be base_thickness_factor times the random thickness.
        angle_random_max      The trunk will be rotated using this Tuple, between [-X, -Y] and [X, Y].      
        randomize_ratio       The ratio of mesh vertices that will be randomly moved after convertion of curve to mesh.
        randomize_offset      The offset of the random movement of mesh vertices.
        colours               The entire trunk will be UV mapped using a random UVRange object from this list.
    """
    resolution: int
    height_min: float
    height_max: float
    thickness_min: float
    thickness_max: float
    base_thickness_factor: float
    angle_random_max: Tuple[float, float]
    randomize_ratio: float
    randomize_offset: float
    colours: List[UVRange]

@dataclass
class BranchConfig:
    """
    This configuration object determines how the branches will be constructed.
    
    Attributes:
        has_central_trunk     If True, a central vertical trunk will be added to the tree
        levels                The number of levels of branches to generate
        angle_random_max      The branches will be rotated using this Tuple (A, B) around the Z-axis, between [-B] and [B]. The branch will be angled up and down between 0 and [A]. Yes, this is confusing. 
        count_function        Function that takes a level and returns the number of branches at that level. Called once per level.
        length_function       Function that takes a level and returns the length of each branch at that level. Called once per branch.
        radius_function       Function that takes a level and returns the radius (ratio) of each branch at that level. Called once per level.
    """
    has_central_trunk: bool
    levels: int
    angle_random_max: Tuple[float, float]
    count_function: Callable[[int], int]
    length_function: Callable[[int], float]
    radius_function: Callable[[int], float]

@dataclass
class FoliageConfig:
    """
    This configuration object determines how the foliage will be constructed.
    
    Attributes:
        mesh_names            List of mesh names to randomly select from at each foliage location.
        scale_min
        scale_max             Each mesh will be randomly scaled between scale_min and scale_max.
        randomize_ratio       The ratio of mesh vertices that will be randomly moved for each duplicated mesh.
        randomize_offset      The offset of the random movement of mesh vertices.
        angle_random_max      The foliage meshes will be rotated using this Tuple, between [-X, -Y, -Z] and [X, Y, Z].      
        colours               Each mesh will be UV mapped using a random UVRange object from this list.
    """
    mesh_names: List[str]
    scale_min: float
    scale_max: float
    randomize_ratio: float
    randomize_offset: float
    angle_random_max: Tuple[float, float, float]
    colours: List[UVRange]

def make_trunk(seed,
               root,
               name,
               config):
    print(f'make_trunk {seed}, {config}')

    switch_to_object_mode()
    ops.curve.primitive_bezier_curve_add(location=root, enter_editmode=True)

    so = bpy.context.active_object
    so.name = name
    so.data.bevel_resolution = config.resolution
    so.data.use_fill_caps = True

    height = uniform(config.height_min, config.height_max)
    thickness = uniform(config.thickness_min, config.thickness_max)
    angle_x = uniform(-config.angle_random_max[0], config.angle_random_max[0])
    angle_y = uniform(-config.angle_random_max[1], config.angle_random_max[1])
    so.data.bevel_depth = thickness

    spline = so.data.splines[0]

    point0 = spline.bezier_points[0]
    point0.co = (0, 0, 0)
    point0.radius = config.base_thickness_factor

    point1 = spline.bezier_points[1]
    point1.co = (height * sin(angle_x), height * sin(angle_y), height)

    ops.curve.select_all(action='SELECT')
    ops.curve.handle_type_set(type='VECTOR')
    ops.curve.select_all(action='DESELECT')

    print_splines(so)

    return PointReference(True, 0, 1)


def extend_trunk(root,
                 so,
                 level,
                 point_reference,
                 length_function,
                 radius_function):
    length = length_function(level)
    ops.curve.select_all(action='DESELECT')
    spline = so.data.splines[point_reference.spline_index]
    point = spline.bezier_points[point_reference.point_index]
    point.select_control_point = True
    offset = Vector((0, 0, length))
    location = root + point.co + offset
    ops.curve.vertex_add(location=location)
    point = spline.bezier_points[-1]
    point.radius = radius_function(level)
    return PointReference(True, so.data.splines.values().index(spline), spline.bezier_points.values().index(point))


def make_branches(root,
                  level,
                  point_reference,
                  config):
    count = config.count_function(level)
    radius = config.radius_function(level)
    print(f'make_branches(root={root}, level={level}, point_reference={point_reference}, config={config}) count={count}, radius={radius}')
    so = bpy.context.active_object
    print(so)

    branch_top_references = []

    if point_reference.is_trunk and config.has_central_trunk:
        branch_top_references.append(extend_trunk(root, so, level, point_reference, config.length_function, config.radius_function))

    uniform_twist = uniform(0, 2 * pi)

    for index in range(count):
        length = config.length_function(level)
        print(f'Adding branch {index} length {length}')
        ops.curve.select_all(action='DESELECT')

        spline = so.data.splines[point_reference.spline_index]
        point = spline.bezier_points[point_reference.point_index]
        print(f'point: {point} {point.co}')
        point.select_control_point = True

        ops.curve.split()
        spline = so.data.splines[-1]
        point = spline.bezier_points[-1]
        point.select_control_point = True

        rotation_z = ((index / count) * 2 * pi) + uniform_twist
        rotation_z += uniform(-config.angle_random_max[1], config.angle_random_max[1])
        rotation_y = uniform(0, config.angle_random_max[0])
        offset = Vector((length, 0, 0))
        offset.rotate(Euler((0, -rotation_y, rotation_z)))
        location = root + point.co + offset
        print(f'point: {point.co} rotation_z: {rotation_z} Offset: {offset} Location: {location}')
        ops.curve.vertex_add(location=location)

        point = spline.bezier_points[-1]
        point.radius = radius 

        branch_top_reference = PointReference(False, so.data.splines.values().index(spline),
                                              spline.bezier_points.values().index(point))
        branch_top_references.append(branch_top_reference)

    print('After adding branches')
    print_splines(so)
    return branch_top_references



def make_foliage(root,
                 tree_name,
                 foliage_name,
                 branch_top_references,
                 config):
    print(
        f'add_foliage(root={root}, tree_name={tree_name}, foliage_name={foliage_name}, branch_top_references={branch_top_references}, config={config})')

    switch_to_object_mode()
    
    remove_object(foliage_name)

    tree_object = bpy.data.objects[tree_name]

    ops.object.select_all(action='DESELECT')
    ops.mesh.primitive_plane_add(enter_editmode=True, location=root)
    ops.mesh.delete(type='VERT')
    aggregate_object = bpy.context.active_object
    aggregate_object.name = foliage_name
    switch_to_object_mode()

    for branch_top_reference in branch_top_references:
        print(f'Adding foliage mesh for branch {branch_top_reference}')
        spline = tree_object.data.splines[branch_top_reference.spline_index]
        point = spline.bezier_points[branch_top_reference.point_index]
        source_object = bpy.data.objects[choice(config.mesh_names)]
        relative_location = root - source_object.location + point.co
        location = root + point.co
        scale = uniform(config.scale_min, config.scale_max)

        ops.object.select_all(action='DESELECT')
        source_object.select_set(True)
        ops.object.duplicate_move(TRANSFORM_OT_translate={"value": relative_location})
        ops.transform.resize(value=(scale, scale, scale))
        duplicated_object = bpy.context.selected_objects[0]
        duplicated_object.rotation_euler = (uniform(-config.angle_random_max[0], config.angle_random_max[0]),
                                            uniform(-config.angle_random_max[1], config.angle_random_max[1]),
                                            uniform(-config.angle_random_max[2], config.angle_random_max[2]))

        bpy.context.view_layer.objects.active = duplicated_object
        randomize_mesh(randrange(100), config.randomize_ratio, config.randomize_offset)
        set_mesh_uvs(duplicated_object, choice(config.colours).random())

        bpy.context.view_layer.objects.active = aggregate_object
        aggregate_object.select_set(True)
        duplicated_object.select_set(True)
        ops.object.join()

    switch_to_object_mode()
    ops.object.shade_flat()
    

def make_branch_length_factor_function(base_length, factor, random_factor):
    def length_function(level):
        return base_length * pow(factor + uniform(-random_factor, random_factor), level)

    return length_function


def default_branch_length_function(level):
    return 0.5


def make_branch_count_function(min, max):
    def count_function(level):
        return randrange(min, max + 1)

    return count_function


def make_branch_radius_function_linear(level_max):
    def radius_function(level):
        return 1 - (level / level_max)

    return radius_function


def make_tree(seed: int,
              root: Vector,
              name: str,
              join_objects: bool,
              trunk_config: TrunkConfig,
              branch_config: BranchConfig,
              foliage_configs: [FoliageConfig]) -> None:
    """
    See examples in TreeExamples.py for examples of trees.
    
    :param seed: passed to random_seed(). If you pass the same seed with the same parameters, you will get the same tree.
    :param root: Vector where the tree will be placed 
    :param name: What would you like to call your lovely tree?
    :param join_objects: If True, trunk and foliage meshes will be joined into one object. If False, they will be separate objects.
    :param trunk_config: see TrunkConfig
    :param branch_config: see BranchConfig
    :param foliage_configs: see FoliageConfig. Array of FoliageConfig objects. See the Rhododendron example to see how to use this for foliage, flowers and buds.
    :return: 
    """
    
    random_seed(seed)

    remove_object(name)

    print(f'***make_tree(seed:{seed}, root:{root}, name:{name}, trunk_config:{trunk_config}, branch_config:{branch_config}, foliage_configs:{foliage_configs})***')
    trunk_top_reference = make_trunk(seed, root, name, trunk_config)
    branch_top_references = [trunk_top_reference]
    object_names = [name]

    for branch_level in range(1, branch_config.levels + 1):
        print(f'**make branches level {branch_level}**')
        next_level_references = []
        for branch_top_reference in branch_top_references:
            new_references = make_branches(root,
                                           branch_level,
                                           branch_top_reference,
                                           branch_config)
            for new_reference in new_references:
                next_level_references.append(new_reference)

        branch_top_references = next_level_references

    for index, foliage_config in enumerate(foliage_configs):
        foliage_name = f'{name}Foliage{index}'
        object_names.append(foliage_name)
        make_foliage(root, name, foliage_name, branch_top_references, foliage_config)

    convert_curve_to_mesh(seed, name, trunk_config.randomize_ratio, trunk_config.randomize_offset, trunk_config.colours)

    if join_objects:
        join_meshes(name, object_names)