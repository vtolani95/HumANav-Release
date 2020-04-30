from dotmap import DotMap
import numpy as np
import os


def create_params():
    p = DotMap()
    p.dataset_name = 'sbpd'
    p.building_name = 'area1'
    p.flip = False
    p.load_meshes = True
    p.load_traversible_from_pickle_file = True

    p.camera_params = DotMap(modalities=['rgb'],  # rgb or disparity
                             width=64,
                             height=64,
                             z_near=.01, # near plane clipping distance
                             z_far=20.0, # far plane clipping distance
                             fov_horizontal=90.,
                             fov_vertical=90.,
                             img_channels=3,
                             im_resize=1.,
                             max_depth_meters=np.inf)

    # The robot is modeled as a solid cylinder
    # of height, 'height', with radius, 'radius',
    # base at height 'base' above the ground
    # The robot has a camera at height
    # 'sensor_height' pointing at 
    # camera_elevation_degree degrees vertically
    # from the horizontal plane.
    p.robot_params = DotMap(radius=18,
                            base=10,
                            height=100,
                            sensor_height=80,
                            camera_elevation_degree=-45,  # camera tilt
                            delta_theta=1.0)

    # Traversible dir
    p.traversible_dir = get_traversible_dir()

    # SBPD Data Directory
    p.sbpd_data_dir = get_sbpd_data_dir()

    # Surreal Parameters
    p.surreal = DotMap(mode='train',
                       data_dir=get_surreal_mesh_dir(),
                       texture_dir=get_surreal_texture_dir(),
                       body_shapes_train=[519, 1320, 521, 523, 779, 365, 1198, 368],
                       body_shapes_test=[337, 944, 1333, 502, 344, 538, 413],
                       compute_human_traversible=False,
                       render_humans_in_gray_only=False
                      )

    return p

def get_path_to_humanav():
    return '/PATH/TO/HumANav'

def get_traversible_dir():
    return os.path.join(get_path_to_humanav(), 'sd3dis/stanford_building_parser_dataset/traversibles')

def get_sbpd_data_dir():
    return os.path.join(get_path_to_humanav(),'sd3dis/stanford_building_parser_dataset')

def get_surreal_mesh_dir():
    return os.path.join(get_path_to_humanav(), 'surreal/code/human_meshes')

def get_surreal_texture_dir():
    return os.path.join(get_path_to_humanav(), 'surreal/code/human_textures')
