from humanav.humanav_renderer import HumANavRenderer
from humanav.render.swiftshader_renderer import HumanShape
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

    def get_outdir(self, session_dir, robot_pos_3, human_pos_3, human_speed, identity, mesh_seed, human_visible=True):
        # Remove any unnecessary subdirs
        self._remove_unnecessary_subdirs()

        # Get the unique name for this subdirectory
        subdir = self._get_subdir(robot_pos_3, human_pos_3, human_speed, identity, mesh_seed)
        if human_visible:
            human_visible_str = 'human_visible'
        else:
            human_visible_str = 'human_not_visible'
        outdir = os.path.join(self._outdir, session_dir, subdir, human_visible_str)

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

    def _get_session_name(self):
        """
        Construct a unique session name using the current time.
        """
        session_name = 'session_%s' % (datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))
        return session_name

    def _get_subdir(self, robot_pos_3, human_pos_3, human_speed, identity, mesh_seed):

        # Construct a unqiue string for this set of parameters
        unique_str = '{:.2f}_{:.2f}_{:.2f}_'.format(*robot_pos_3)
        unique_str += '{:.2f}_{:.2f}_{:.2f}_'.format(*human_pos_3)
        unique_str += '{:.2f}_'.format(human_speed)

        gender = identity['human_gender']
        texture = identity['human_texture'][0].split('/')[-1].split('.')[0]
        body_shape = identity['body_shape']

        unique_str += '{:s}_{:s}_{:d}_'.format(gender, texture, body_shape)
        unique_str += '{:d}_'.format(mesh_seed)

        return unique_str

    def check_pos_3_in_obstacle(self, pos_3):
        pos_2_xy_map = np.round(pos_3[:2]/self.dx).astype(np.int32)
        return not self.traversible[pos_2_xy_map[1], pos_2_xy_map[0]]

    def render_images(self, robot_pos_3, human_pos_3, human_speed, human_identity, change_human_gender,
                      change_human_texture, change_body_shape, identity_seed, mesh_seed):
        """
        Render the image from robot_pos_3 of the environment.
        The human is placed at human_pos_3 moving at human_speed.
        """
        human_identity = self.get_human_identity(human_identity, change_human_gender, change_human_texture, change_body_shape, identity_seed)
        #human_identity = self.get_new_human_identity(identity_seed)

        session_dir = self._get_session_name()
        img_urls_human_visible = self._render_images(session_dir, robot_pos_3, human_pos_3,
                                                     human_speed, human_identity, mesh_seed, human_visible=True)
        img_urls_human_not_visible = self._render_images(session_dir, robot_pos_3, human_pos_3,
                                                         human_speed, human_identity, mesh_seed, human_visible=False)

        topview_unoccupied_file = os.path.join(self._outdir, session_dir, 'topview_unoccupied.png')
        self._render_and_save_img_topview(robot_pos_3, human_pos_3, topview_unoccupied_file, human_visible=False, robot_visible=False)
        topview_unoccupied_file_for_web = 'static_assets/{:s}'.format(topview_unoccupied_file[len('./outdir/'):])

        data = {'human_visible': img_urls_human_visible,
                'human_not_visible': img_urls_human_not_visible,
                'topview_unoccupied': topview_unoccupied_file_for_web,
                'human_identity': human_identity}
        return data

    def _render_images(self, session_dir, robot_pos_3, human_pos_3, human_speed, human_identity, seed, human_visible=True):
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

        outdir = self.get_outdir(session_dir, robot_pos_3, human_pos_3, human_speed, human_identity, seed, human_visible=human_visible)


        rgb_file = os.path.join(outdir, 'rgb.png')
        depth_file = os.path.join(outdir, 'depth.png')
        topview_file = os.path.join(outdir, 'topview.png')

        self._render_and_save_img_rgb(robot_pos_13, rgb_file, human_visible=human_visible)
        self._render_and_save_img_disparity(robot_pos_13, depth_file, human_visible=human_visible)
        self._render_and_save_img_topview(robot_pos_3, human_pos_3, topview_file, human_visible=human_visible)

        # Remove the human from the environment
        self.r.remove_human()

        outdir_for_web = 'static_assets/{:s}'.format(outdir[len('./outdir/'):])
        rgb_file = os.path.join(outdir_for_web, 'rgb.png')
        depth_file = os.path.join(outdir_for_web, 'depth.png')
        topview_file = os.path.join(outdir_for_web, 'topview.png')

        # Return links to the images
        images = {'rgb': rgb_file,
                  'depth': depth_file,
                  'topview': topview_file}
        return images

    def get_human_identity(self, human_identity, change_human_gender,
                           change_human_texture, change_body_shape, identity_seed):
        """
        Get a new human identity. Or return the old one
        if nothing is changed.
        """
        # Seed the RNG
        self.identity_rng.seed(identity_seed)

        if change_human_gender:
            human_identity['human_gender'] = {'male': 'female',
                                              'female': 'male'}[human_identity['human_gender']]

        if change_human_texture:
            human_identity['human_texture'] = HumanShape.get_random_materials(self.r.p.surreal.texture_dir,
                                                                              self.r.p.surreal.mode,
                                                                              human_identity['human_gender'],
                                                                              self.identity_rng, load_materials=False)


        if change_body_shape:
            human_identity['body_shape'] = self.identity_rng.choice(self.p.surreal.body_shapes_train)

        return human_identity

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


    def _render_and_save_img_topview(self, robot_pos_3, human_pos_3, outfile, human_visible=True, robot_visible=True):
        # Plot the Topview
        self.ax.clear()
        self.ax.imshow(self.traversible, cmap='gray', origin='lower',
                       extent=self.extent, vmin=-.5, vmax=1.5)

        # Plot the robot
        x, y, theta = robot_pos_3
        if robot_visible:
            self.ax.plot(x, y, 'bo', markersize=25, label='Camera')
            self.ax.quiver(x, y, np.cos(theta), np.sin(theta), scale=16.)

        # Plot the human
        if human_visible:
            self.ax.plot(*human_pos_3[:2], 'ro', markersize=25, label='Human')
            self.ax.quiver(*human_pos_3[:2], np.cos(human_pos_3[2]), np.sin(human_pos_3[2]), scale=16.)

        if robot_visible or human_visible:
            self.ax.legend(ncol=2, loc='upper center', fontsize=20)

        self.ax.set_xlim([x-5., x+5.])
        self.ax.set_ylim([y-5., y+5.])
        self.ax.set_xticks([])
        self.ax.set_yticks([])

        with open(outfile, 'wb') as f:
            self.fig.canvas.print_png(f)

