from humanav.humanav_renderer import HumANavRenderer
from dotmap import DotMap
import matplotlib.pyplot as plt
import numpy as np
from humanav.renderer_params import create_params as create_base_params

def create_params():
    p = create_base_params()

	# Set any custom parameters
    p.building_name = 'area3'

    p.camera_params.width = 1024
    p.camera_params.height = 1024
    p.camera_params.fov_vertical = 75.
    p.camera_params.fov_horizontal = 75.

    # The camera is assumed to be mounted on a robot at fixed height
    # and fixed pitch. See humanav/renderer_params.py for more information

    # Tilt the camera 10 degree down from the horizontal axis
    p.robot_params.camera_elevation_degree = -10

    p.camera_params.modalities = ['rgb', 'disparity']
    return p


def test_humanav():
    p = create_params()

    r = HumANavRenderer.get_renderer(p)
    dx_cm, traversible = r.get_config()

    # Convert the grid spacing to units of meters. Should be 5cm for the S3DIS data
    dx_m = dx_cm/100.

    # Compute the real_world extent (in meters) of the traversible
    extent = [0., traversible.shape[1], 0., traversible.shape[0]]
    extent = np.array(extent)*dx_m

    # Set the identity seed. This is used to sample a random human identity
    # (gender, texture, body shape)
    identity_rng = np.random.RandomState(48)

    # Set the Mesh seed. This is used to sample the actual mesh to be loaded
    # which reflects the pose of the human skeleton.
    mesh_rng = np.random.RandomState(20)

    # State of the camera and the human. 
    # Specified as [x (meters), y (meters), theta (radians)] coordinates
    camera_pos_13 = np.array([[7.5, 12., -1.3]])
    human_pos_3 = np.array([8.0, 9.75, np.pi/2.])

    # Speed of the human in m/s
    human_speed = 0.7

    # Tell the renderer to load a random human at a specified state and speed
    r.add_human_at_position_with_speed(human_pos_3, human_speed, identity_rng, mesh_rng)

	# Convert from real world units to grid world units
    camera_grid_world_pos_12 = camera_pos_13[:, :2]/dx_m

    # Render RGB and Depth Images. The shape of the resulting
    # image is (1 (batch), m (width), k (height), c (number channels))
    rgb_image_with_human_1mk3 = r._get_rgb_image(camera_grid_world_pos_12, camera_pos_13[:, 2:3], human_visible=True)

    depth_image_with_human_1mk1, _, _ = r._get_depth_image(camera_grid_world_pos_12, camera_pos_13[:, 2:3], xy_resolution=.05, map_size=1500, pos_3=camera_pos_13[0, :3], human_visible=True)

    fig = plt.figure(figsize=(30, 10))

    # Plot the 5x5 meter occupancy grid centered around the camera
    ax = fig.add_subplot(1, 3, 1)
    ax.imshow(traversible, extent=extent, cmap='gray',
              vmin=-.5, vmax=1.5, origin='lower')

    # Plot the camera
    ax.plot(camera_pos_13[0, 0], camera_pos_13[0, 1], 'bo', markersize=10, label='Camera')
    ax.quiver(camera_pos_13[0, 0], camera_pos_13[0, 1], np.cos(camera_pos_13[0, 2]), np.sin(camera_pos_13[0, 2]))
    # Plot the human
    ax.plot(human_pos_3[0], human_pos_3[1], 'ro', markersize=10, label='Human')
    ax.quiver(human_pos_3[0], human_pos_3[1], np.cos(human_pos_3[2]), np.sin(human_pos_3[2]))

    ax.legend()
    ax.set_xlim([camera_pos_13[0, 0]-5., camera_pos_13[0, 0]+5.])
    ax.set_ylim([camera_pos_13[0, 1]-5., camera_pos_13[0, 1]+5.])
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title('Topview')

    # Plot the RGB Image
    ax = fig.add_subplot(1, 3, 2)
    ax.imshow(rgb_image_with_human_1mk3[0].astype(np.uint8))
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title('RGB')

    # Plot the Depth Image
    ax = fig.add_subplot(1, 3, 3)
    ax.imshow(depth_image_with_human_1mk1[0, :, :, 0].astype(np.uint8), cmap='gray')
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title('Depth')

    fig.savefig('example1.png', bbox_inches='tight', pad_inches=0)

if __name__ == '__main__':
    test_humanav()
