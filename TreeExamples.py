from TreeGenerator import make_tree, UVRange, \
    TrunkConfig, \
    BranchConfig, \
    FoliageConfig, \
    make_branch_count_function, \
    make_branch_length_factor_function, \
    make_branch_radius_function_linear
from random import randrange
from math import pi
from mathutils import Vector

def make_examples():
    print('\033c')
    print('--------------')
    print('TreeGenerator1')
    print('--------------')
    
    uv_foliage_green = UVRange(0.600, 0.655, 0.955)
    uv_foliage_yellow = UVRange(0.720, 0.655, 0.955)
    uv_foliage_orange = UVRange(0.782, 0.655, 0.955)
    uv_foliage_red = UVRange(0.157, 0.655, 0.955)
    uv_trunk_brown = UVRange(0.472, 0.855, 0.999)
    
    for seed in range(10):
        levels = randrange(2, 4)
        make_tree(seed,
                  Vector((seed * 10, 0, 0)),
                  f'TreeSphere{seed}',
                  join_objects=True,
                  trunk_config=TrunkConfig(
                      resolution=2,
                      height_min=1.0, height_max=2.5,
                      thickness_min=0.13, thickness_max=0.24,
                      base_thickness_factor=2.5,
                      angle_random_max=(0.15, 0.15),
                      randomize_ratio=0.5, randomize_offset=0.05,
                      colours=[uv_trunk_brown]),
                  branch_config=BranchConfig(
                      has_central_trunk=False,
                      levels=levels,
                      angle_random_max=(1.3, 0.15),
                      count_function=make_branch_count_function(2, 4),
                      length_function=make_branch_length_factor_function(2, 0.8, 0.25),
                      radius_function=make_branch_radius_function_linear(levels)),
                  foliage_configs=[
                      FoliageConfig(
                          mesh_names=['FoliageSphere.noimp'],
                          scale_min=0.7, scale_max=1.0,
                          randomize_ratio=1, randomize_offset=0.12,
                          angle_random_max=(0, 0, 2 * pi),
                          colours=[uv_foliage_yellow, uv_foliage_orange])
                  ])
        
        levels = randrange(2, 4)
        make_tree(seed,
                  Vector((seed * 10, 10, 0)),
                  f'TreeCube{seed}',
                  join_objects=True,
                  trunk_config=TrunkConfig(
                      resolution=0,
                      height_min=2.0, height_max=3.5,
                      thickness_min=0.13, thickness_max=0.24,
                      base_thickness_factor=1.25,
                      angle_random_max=(0.05, 0.15),
                      randomize_ratio=0.5, randomize_offset=0.05,
                      colours=[uv_trunk_brown]),
                  branch_config=BranchConfig(
                      has_central_trunk=True,
                      levels=levels,
                      angle_random_max=(0.5, 0.35),
                      count_function=make_branch_count_function(1, 3),
                      length_function=make_branch_length_factor_function(1, 1.0, 0.25),
                      radius_function=make_branch_radius_function_linear(levels)),
                  foliage_configs=[
                      FoliageConfig(
                          mesh_names=['FoliageCube.noimp'],
                          scale_min=0.4, scale_max=1,
                          randomize_ratio=1, randomize_offset=0.4,
                          angle_random_max=(0, 0, 2 * pi),
                          colours=[uv_foliage_green])
                  ])


        levels = randrange(2, 4)
        make_tree(seed,
                  Vector((seed * 10, 20, 0)),
                  f'TreeBushy{seed}',
                  join_objects=False,
                  trunk_config=TrunkConfig(
                      resolution=1,
                      height_min=2.0, height_max=3.5,
                      thickness_min=0.23, thickness_max=0.24,
                      base_thickness_factor=1.65,
                      angle_random_max=(0.05, 0.15),
                      randomize_ratio=0.5, randomize_offset=0.05,
                      colours=[uv_trunk_brown]),
                  branch_config=BranchConfig(
                      has_central_trunk=True,
                      levels=levels,
                      angle_random_max=(0.5, 0.35),
                      count_function=make_branch_count_function(0, 3),
                      length_function=make_branch_length_factor_function(2.0, 0.8, 0.5),
                      radius_function=make_branch_radius_function_linear(levels)),
                  foliage_configs=[
                      FoliageConfig(
                          mesh_names=['FoliageBushy.noimp'],
                          scale_min=0.8, scale_max=1.5,
                          randomize_ratio=1, randomize_offset=0.4,
                          angle_random_max=(0, 0, 2 * pi),
                          colours=[uv_foliage_green, uv_foliage_yellow])
                  ])

        levels = 2
        make_tree(seed,
                  Vector((seed * 10, 30, 0)),
                  f'Rhododendron{seed}',
                  join_objects=True,
                  trunk_config=TrunkConfig(
                      resolution=1,
                      height_min=0.05, height_max=0.2,
                      thickness_min=0.05, thickness_max=0.15,
                      base_thickness_factor=1.65,
                      angle_random_max=(0.05, 0.15),
                      randomize_ratio=0.5, randomize_offset=0.05,
                      colours=[uv_trunk_brown]),
                  branch_config=BranchConfig(
                      has_central_trunk=False,
                      levels=levels,
                      angle_random_max=(0.75, 0.05),
                      count_function=make_branch_count_function(3, 5),
                      length_function=make_branch_length_factor_function(1.5, 0.8, 0.25),
                      radius_function=make_branch_radius_function_linear(levels)),
                  foliage_configs=[
                      # Every leaf point will have foliage
                      FoliageConfig(
                          mesh_names=['FoliageRhododendron.noimp'],
                          scale_min=0.3, scale_max=0.5,
                          randomize_ratio=1, randomize_offset=0.15,
                          angle_random_max=(0.5, 0.5, 2 * pi),
                          colours=[uv_foliage_green]),
                      # AND every leaf point will have either a bud or a flower
                      FoliageConfig(
                          mesh_names=['FoliageRhododendronBud.noimp','FoliageRhododendronFlower.noimp'],
                          scale_min=0.13, scale_max=0.2,
                          randomize_ratio=1, randomize_offset=0.05,
                          angle_random_max=(0, 0, 2 * pi),
                          colours=[uv_foliage_red]),
                  ])
    