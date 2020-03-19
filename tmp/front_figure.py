from humanav.humanav_renderer import HumANavRenderer
from dotmap import DotMap
import matplotlib.pyplot as plt
import numpy as np
from humanav.renderer_params import get_traversible_dir, get_sbpd_data_dir, get_surreal_mesh_dir, get_surreal_texture_dir


def create_params():
    p = DotMap()
    p.dataset_name = 'sbpd'
    p.building_name = 'area1'
    p.flip = False
    p.load_meshes = True
    p.load_traversible_from_pickle_file = False

    p.camera_params = DotMap(modalities=['rgb'],  # occupancy_grid, rgb, or disparity
                             width=224,
                             height=224,  # the remaining params are for rgb and depth only
                             z_near=.01,
                             z_far=20.0,
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
                            camera_elevation_degree=-10,  # camera tilt
                            delta_theta=1.0)
    
    # Traversible dir
    p.traversible_dir = get_traversible_dir()

    # HumANav Data Directory
    p.sbpd_data_dir = get_sbpd_data_dir()

    # Surreal Parameters
    p.surreal = DotMap(mode='train',
                       data_dir=get_surreal_mesh_dir(),
                       texture_dir=get_surreal_texture_dir(),
                       body_shapes_train=[519, 1320, 521, 523, 779, 365, 1198, 368],
                       body_shapes_test=[337, 944, 1333, 502, 344, 538, 413],
                       compute_human_traversible=False
                      )

    return p


def plot_front_figure_disparity():
    p = create_params()
    p.camera_params.width = 1024
    p.camera_params.height = 1024
    p.camera_params.fov_vertical = 75.
    p.camera_params.fov_horizontal = 75.
    p.building_name = 'area3'

    p.camera_params.modalities = ['disparity', 'rgb']
    r = HumANavRenderer.get_renderer(p)

    # Position(s) of the robot and the human
    # specified as [x (meters), y (meters), theta (radians)]
    # coordinates
    robot_pos = np.array([[7.5, 12., -1.3]])#np.pi/2.]])
    human_pos_3 = np.array([8.0, 9.75, np.pi/2.])
    xy_pos = robot_pos[:, :2]/.05

    identity_rng = np.random.RandomState(48)
    mesh_rng = np.random.RandomState(20)

    # Tell the renderer to load the human mesh at human_pos_3
    r.add_human_at_position_with_speed(human_pos_3, 0.7, identity_rng, mesh_rng)

    # Render some images with humans
    disparity_image_with_human, _, _ = r._get_depth_image(xy_pos, robot_pos[:, 2:3], xy_resolution=.05,
                                                          map_size=1500, pos_3=robot_pos[0, :3],
                                                          human_visible=True)

    rgb_image_with_human = r._get_rgb_image(xy_pos, robot_pos[:, 2:3], human_visible=True)

    fig = plt.figure(figsize=(10, 10), frameon=False)

    # Plot the Disparity Image
    #ax = fig.add_subplot(1, 1, 1)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.imshow(disparity_image_with_human[0, :, :, 0].astype(np.uint8), cmap='gray')
    ax.set_xticks([])
    ax.set_yticks([])
    with open('./website_front_figure/front_figure_disparity.png', 'wb') as outfile:
        fig.canvas.print_png(outfile)

    # Plot the RGB Image
    ax.clear()
    ax.imshow(rgb_image_with_human[0].astype(np.uint8))
    ax.set_xticks([])
    ax.set_yticks([])

    with open('./website_front_figure/front_figure_rgb.png', 'wb') as outfile:
        fig.canvas.print_png(outfile)


    # Plot the Topview
    dx, traversible = r.get_config()
    extent = [0., traversible.shape[1], 0., traversible.shape[0]]
    extent = .05*np.array(extent)
    ax.clear()
    ax.imshow(traversible, cmap='gray', origin='lower',
              extent=extent, vmin=-.5, vmax=1.5)

    # Plot the robot
    x, y, theta = robot_pos[0]
    ax.plot(x, y, 'bo', markersize=25, label='Robot')
    ax.quiver(x, y, np.cos(theta), np.sin(theta), scale=16.)

    # Plot the human
    ax.plot(*human_pos_3[:2], 'ro', markersize=25, label='Human')
    ax.quiver(*human_pos_3[:2], np.cos(human_pos_3[2]), np.sin(human_pos_3[2]), scale=16.)

    ax.legend(ncol=2, loc='upper center', fontsize=20)
    ax.set_xlim([x-5., x+5.])
    ax.set_ylim([y-5., y+5.])
    
    ax.set_xticks([])
    ax.set_yticks([])

    with open('./website_front_figure/front_figure_topview.png', 'wb') as outfile:
        fig.canvas.print_png(outfile)


if __name__ == '__main__':
    plot_front_figure_disparity()
