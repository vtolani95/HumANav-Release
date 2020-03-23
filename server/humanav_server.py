from humanav.humanav_renderer import HumANavRenderer
from server_params import create_params
import matplotlib
matplotlib.use('tkAgg')
import matplotlib.pyplot as plt
import numpy as np
import os
import cv2
import datetime
import shutil


class HumANavServer(object):
    server = None

    def __init__(self):
        self.p = create_params()

        self.r = HumANavRenderer.get_renderer(self.p)
        self.fig = plt.figure(figsize=(10, 10), frameon=False)
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.dx = .05  # 5cm

        self.mesh_rng = np.random.RandomState()
        self.identity_rng = np.random.RandomState()

        _, traversible = self.r.get_config()
        extent = [0., traversible.shape[1], 0., traversible.shape[0]]
        self.extent = self.dx*np.array(extent)
        self.traversible = traversible

        self._outdir = './outdir'

        self.max_number_subdirs = 15

    def mkdir_if_missing(self, dirname):
        if not os.path.exists(dirname):
            os.makedirs(dirname)

    def get_outdir(self, robot_pos_3, human_pos_3, human_speed, identity, mesh_seed, human_visible=True):
        # Remove any unnecessary subdirs
        self._remove_unnecessary_subdirs()

        # Get the unique name for this subdirectory
        subdir = self._get_subdir(robot_pos_3, human_pos_3, human_speed, identity, mesh_seed, human_visible)
        outdir = os.path.join(self._outdir, subdir)

        self.mkdir_if_missing(outdir)
        return outdir

    def _remove_unnecessary_subdirs(self):
        img_dirs = os.listdir(self._outdir)
        if len(img_dirs) > self.max_number_subdirs:
            sorted_imgs_dirs = sorted(img_dirs, key=lambda x: datetime.datetime.strptime(x.split('_')[1], '%Y-%m-%d-%H-%M-%S'))

            # Remove the oldest sessions first
            while len(sorted_imgs_dirs) > self.max_number_subdirs:
                dirname = sorted_imgs_dirs.pop(0)
                shutil.rmtree(os.path.join(self._outdir, dirname))

    def _get_subdir(self, robot_pos_3, human_pos_3, human_speed, identity, mesh_seed, human_visible):
        current_time = 'session_%s' % (datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))

        # Construct a unqiue string for this set of parameters
        unique_str = '{:.2f}_{:.2f}_{:.2f}_'.format(*robot_pos_3)
        unique_str += '{:.2f}_{:.2f}_{:.2f}_'.format(*human_pos_3)
        unique_str += '{:.2f}_'.format(human_speed)

        gender = identity['human_gender']
        texture = identity['human_texture'][0].split('/')[-1].split('.')[0]
        body_shape = identity['body_shape']

        unique_str += '{:s}_{:s}_{:d}_'.format(gender, texture, body_shape)
        unique_str += '{:d}_'.format(mesh_seed)

        if human_visible:
            unique_str += 'with_human'
        else:
            unique_str += 'without_human'

        return os.path.join(current_time, unique_str)

    def render_images(self, robot_pos_3, human_pos_3, human_speed, human_identity, seed, human_visible=True):
        """
        Render the image from robot_pos_3 of the environment.
        The human is placed at human_pos_3 moving at human_speed.
        """
        if human_visible:
            # Seed the rng
            self.mesh_rng.seed(seed)

            # Sample a new human mesh and load it into the environment
            human_mesh_params = self.r.add_human_with_known_identity_at_position_with_speed(human_pos_3, human_speed, self.mesh_rng, human_identity, allow_repeat_humans=True)

        # Render the 3 image modalities
        robot_pos_13 = robot_pos_3[None]

        outdir = self.get_outdir(robot_pos_3, human_pos_3, human_speed, human_identity, seed, human_visible=human_visible)
        rgb_file = os.path.join(outdir, 'rgb.png')
        depth_file = os.path.join(outdir, 'depth.png')
        topview_file = os.path.join(outdir, 'topview.png')

        self._render_and_save_img_rgb(robot_pos_13, rgb_file, human_visible=human_visible)
        self._render_and_save_img_disparity(robot_pos_13, depth_file, human_visible=human_visible)
        self._render_and_save_img_topview(robot_pos_3, human_pos_3, topview_file, human_visible=human_visible)

        # Remove the human from the environment
        self.r.remove_human()

        # Return links to the images
        images = {'rgb': rgb_file,
                  'depth': depth_file,
                  'topview': topview_file}
        return images

    def get_new_human_identity(self, seed):
        """
        Get a new human identity.
        """
        # Seed the rng
        self.identity_rng.seed(seed)

        # Sample a new human identity
        identity = self.r.load_random_human_identity(self.identity_rng)

        # Return the identity
        return identity


    def _render_and_save_img_rgb(self, robot_pos_13, outfile, human_visible=True):
        dx = self.dx

        xy_pos_12 = robot_pos_13[:, :2]/dx

        # Render the image
        rgb_image = self.r._get_rgb_image(xy_pos_12, robot_pos_13[:, 2:3], human_visible=human_visible)

        # Plot and save the image
        self.ax.clear()
        self.ax.imshow(rgb_image[0].astype(np.uint8))

        self.ax.set_xticks([])
        self.ax.set_yticks([])

        with open(outfile, 'wb') as f:
            self.fig.canvas.print_png(f)


    def _render_and_save_img_disparity(self, robot_pos_13, outfile, human_visible=True):
        dx = self.dx

        xy_pos_12 = robot_pos_13[:, :2]/dx

        # Render the image
        depth_image, _, _ = self.r._get_depth_image(xy_pos_12, robot_pos_13[:, 2:3], xy_resolution=.05,
                                                    map_size=1500, pos_3=robot_pos_13[0, :3],
                                                    human_visible=human_visible)

        # Plot and save the image
        self.ax.clear()
        self.ax.imshow(depth_image[0, :, :, 0].astype(np.uint8), cmap='gray')

        self.ax.set_xticks([])
        self.ax.set_yticks([])

        with open(outfile, 'wb') as f:
            self.fig.canvas.print_png(f)


    def _render_and_save_img_topview(self, robot_pos_3, human_pos_3, outfile, human_visible=True):
        # Plot the Topview
        self.ax.clear()
        self.ax.imshow(self.traversible, cmap='gray', origin='lower',
                       extent=self.extent, vmin=-.5, vmax=1.5)

        # Plot the robot
        x, y, theta = robot_pos_3
        self.ax.plot(x, y, 'bo', markersize=25, label='Robot')
        self.ax.quiver(x, y, np.cos(theta), np.sin(theta), scale=16.)

        # Plot the human
        if human_visible:
            self.ax.plot(*human_pos_3[:2], 'ro', markersize=25, label='Human')
            self.ax.quiver(*human_pos_3[:2], np.cos(human_pos_3[2]), np.sin(human_pos_3[2]), scale=16.)

        self.ax.legend(ncol=2, loc='upper center', fontsize=20)

        self.ax.set_xlim([x-5., x+5.])
        self.ax.set_ylim([y-5., y+5.])
        self.ax.set_xticks([])
        self.ax.set_yticks([])

        with open(outfile, 'wb') as f:
            self.fig.canvas.print_png(f)

