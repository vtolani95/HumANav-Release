from __future__ import print_function
import logging
import numpy as np
import sys
if sys.version_info[0] == 2:
    from . import map_utils as mu
else:
    from humanav import map_utils as mu #py3

make_map = mu.make_map
resize_maps = mu.resize_maps
compute_traversibility = mu.compute_traversibility
add_human_to_traversible = mu.add_human_to_traversible
pick_largest_cc = mu.pick_largest_cc

class Building():
  def __init__(self, dataset, name, robot, env, flip=False):
    self.restrict_to_largest_cc = True
    self.robot = robot
    self.env = env

    # Load the building meta data.
    env_paths = dataset.load_building(name)
    materials_scale = 1.0
    self.materials_scale = materials_scale
    
    shapess = dataset.load_building_meshes(env_paths, 
      materials_scale=materials_scale)

    if flip: 
      for shapes in shapess: 
        shapes.flip_shape()
    
    vs = []
    for shapes in shapess:
      vs.append(shapes.get_vertices()[0])
    vs = np.concatenate(vs, axis=0)
    
    map = make_map(env.padding, env.resolution, vertex=vs, sc=100.)
    map = compute_traversibility(
      map, robot.base, robot.height, robot.radius, env.valid_min,
      env.valid_max, env.num_point_threshold, shapess=shapess, sc=100.,
      n_samples_per_face=env.n_samples_per_face)

    self.env_paths = env_paths 
    self.shapess = shapess
    self.map = map

    # The map object has _traversible (only the SBPD building)
    # and traversible (the current traversible which may include
    # space occupied by any humans in the environment)
    self.traversible = map.traversible*1

    self.name = name 
    self.flipped = flip
    self.renderer_entitiy_ids = []
    if self.restrict_to_largest_cc:
      self.traversible = pick_largest_cc(self.traversible)
      self.map._traversible = self.traversible
      self.map.traversible = self.traversible

    # Instance variable for storing human information
    self.human_mesh_info = None
    self.human_pos_3 = None
    self.human = None

  def set_r_obj(self, r_obj):
    self.r_obj = r_obj

  def load_building_into_scene(self, dedup_tbo=False):
    assert(self.shapess is not None)
    # Loads the scene.
    self.renderer_entitiy_ids += self.r_obj.load_shapes(self.shapess, dedup_tbo)
    # Free up memory, we dont need the mesh or the materials anymore.
    self.shapess = None

  def _transform_to_ego(self, world_vertices_n3, pos_3):
    """
    Transforms the world_vertices_n3 ([x, y, z])
    to the ego frame where pos_3 [x, y, theta]
    is the location of the origin in the world frame.
    """
    # Translate by X,Y
    ego_vertices_xy_n2 = world_vertices_n3[:, :2] - pos_3[:2]

    # Rotate by theta
    theta = -pos_3[2]
    R = np.array([[np.cos(theta), np.sin(theta)],
                 [-np.sin(theta), np.cos(theta)]])
    ego_vertices_xy_n2 = ego_vertices_xy_n2.dot(R)

    # Join the changed X, Y coordinates with
    # the unchanged Z coordinates
    ego_vertices_n3 = np.concatenate([ego_vertices_xy_n2, world_vertices_n3[:, 2:3]], axis=1)

    return ego_vertices_n3

  def _transform_to_world(self, ego_vertices_n3, pos_3):
    """
    Transforms the ego_vertices_n3 ([x, y, z])
    to the world frame where pos_3 [x, y, theta]
    is the location of the origin in the world frame.
    """
    ego_vertices_xy_n2 = ego_vertices_n3[:, :2]

    theta = pos_3[2]

    # Rotate by theta
    R = np.array([[np.cos(theta), np.sin(theta)],
                 [-np.sin(theta), np.cos(theta)]])
    world_vertices_xy_n2 = ego_vertices_xy_n2.dot(R)

    # Translate by X,Y
    world_vertices_xy_n2 += pos_3[:2]

    # Join the changed X, Y coordinates with
    # the unchanged Z coordinates
    world_vertices_n3 = np.concatenate([world_vertices_xy_n2, ego_vertices_n3[:, 2:3]], axis=1)

    return world_vertices_n3

  def _traversible_world_to_vertex_world(self, pos_3):
      """
      Convert an [x, y, theta] coordinate specified on
      the traversible map to a [x, y, theta] coordinate
      in the same coordinate frame as the meshes themselves
      """
      # Divide by 100 to convert origin back to meters
      # The mesh is stored in units of meters
      # So we just offset the human by the desired # meters
      xy_offset_map = self.map.origin/100. + pos_3[:2]

      pos_3 = np.array([xy_offset_map[0], xy_offset_map[1], pos_3[2]])
      return pos_3
  
  def load_human_into_scene(self, dataset, pos_3, speed, gender,
                            human_materials, body_shape, rng, dedup_tbo=False,
                            allow_repeat_humans=False):
    """
    Load a 'gendered' human mesh with 'body shape' and texture, 'human_materials',
    into a building at 'pos_3' with 'speed' in the static building.
    """
    self.human_pos_3 = pos_3*1.

    # Load the human mesh
    shapess, center_pos_3, human_mesh_info = \
            dataset.load_random_human(speed, gender, human_materials, body_shape, rng)

    self.human_mesh_info = human_mesh_info

    # Make sure the human's feet are actually on the ground in SBPD
    # (i.e. the minimum z coordinate is 0)
    z_offset = shapess[0].meshes[0].vertices[:, 2].min()
    shapess[0].meshes[0].vertices = np.concatenate([shapess[0].meshes[0].vertices[:, :2],
                                                    shapess[0].meshes[0].vertices[:, 2:3]-z_offset],
                                                   axis=1)

    # Make sure the human is in the canonical position
    # The centerpoint between the left and right foot should be (0, 0)
    # and the heading (average of the direction of the two feet) should be 0
    shapess[0].meshes[0].vertices = self._transform_to_ego(shapess[0].meshes[0].vertices,
                                                           center_pos_3)
    human_ego_vertices = shapess[0].meshes[0].vertices*1.

    # Move the human to the desired location
    pos_3 = self._traversible_world_to_vertex_world(pos_3)
    shapess[0].meshes[0].vertices = self._transform_to_world(shapess[0].meshes[0].vertices, pos_3)

    self.renderer_entitiy_ids += self.r_obj.load_shapes(shapess, dedup_tbo, allow_repeat_humans=allow_repeat_humans)

    # Update The Traversible
    if dataset.surreal_params.compute_human_traversible:
        map = self.map
        env = self.env
        robot= self.robot
        map = add_human_to_traversible(
          map, robot.base, robot.height, robot.radius, env.valid_min,
          env.valid_max, env.num_point_threshold, shapess=shapess, sc=100.,
            n_samples_per_face=env.n_samples_per_face, human_xy_center_2=pos_3[:2])

        self.traversible = map.traversible
        self.map = map
    self.human = shapess[0]
    self.human_ego_vertices = human_ego_vertices

  def remove_human(self):
      """
      Remove a human that has been loaded into the SBPD environment
      """
      # Delete the human mesh from memory
      self.r_obj.remove_human()

      # Remove the human from the list of loaded entities
      human_entitiy_ids = list(filter(lambda x: 'human' in x, self.renderer_entitiy_ids))

      # Only one human supported currently
      assert (len(human_entitiy_ids) <= 1)

      for human_entity_id in human_entitiy_ids:
          self.renderer_entitiy_ids.remove(human_entity_id)

      # Update the traversible to be human free
      self.map.traversible = self.map._traversible
      self.traversible = self.map._traversible

  def move_human_to_position_with_speed(self, dataset, pos_3, speed, gender,
                                        human_materials, body_shape, rng):
      """
      Removes the previously loaded human mesh,
      and loads a new one with the same gender, texture
      and body shape at pos_3 with speed_3.
      """
      # Remove the previous human
      self.remove_human()

      # Load a new human with the same speed, gender, texture, body shape
      self.load_human_into_scene(dataset, pos_3, speed, gender, human_materials, body_shape, rng)
 
  def to_actual_xyt(self, pqr):
    """Converts from node array to location array on the map."""
    out = pqr*1.
    # p = pqr[:,0:1]; q = pqr[:,1:2]; r = pqr[:,2:3];
    # out = np.concatenate((p + self.map.origin[0], q + self.map.origin[1], r), 1) 
    return out

  def set_building_visibility(self, visibility):
    self.r_obj.set_entity_visible(self.renderer_entitiy_ids, visibility)

  def set_human_visibility(self, visibility):
    human_entity_ids = list(filter(lambda x: 'human' in x, self.renderer_entitiy_ids))
    self.r_obj.set_entity_visible(human_entity_ids, visibility)

  def render_nodes(self, nodes, modality, perturb=None, aux_delta_theta=0., human_visible=True):
    # List of nodes to render.
    self.set_building_visibility(True)
    self.set_human_visibility(human_visible)
    if perturb is None:
      perturb = np.zeros((len(nodes), 4))

    imgs = []
    r = 2
    elevation_z = r * np.tan(np.deg2rad(self.robot.camera_elevation_degree))

    for i in range(len(nodes)):
      xyt = self.to_actual_xyt(nodes[i][np.newaxis,:]*1.)[0,:]
      lookat_theta = 3.0 * np.pi / 2.0 - (xyt[2]+perturb[i,2]+aux_delta_theta) * (self.robot.delta_theta)
      nxy = np.array([xyt[0]+perturb[i,0], xyt[1]+perturb[i,1]]).reshape(1, -1)
      nxy = nxy * self.map.resolution
      nxy = nxy + self.map.origin
      camera_xyz = np.zeros((1, 3))
      camera_xyz[...] = [nxy[0, 0], nxy[0, 1], self.robot.sensor_height]
      camera_xyz = camera_xyz / 100.
      lookat_xyz = np.array([-r * np.sin(lookat_theta),
                             -r * np.cos(lookat_theta), elevation_z])
      lookat_xyz = lookat_xyz + camera_xyz[0, :]
      self.r_obj.position_camera(camera_xyz[0, :].tolist(), lookat_xyz.tolist(), 
        [0.0, 0.0, 1.0])
      img = self.r_obj.render(modality, take_screenshot=True, output_type=0)
      img = [x for x in img if x is not None]
      img = np.concatenate(img, axis=2).astype(np.float32)
      if perturb[i,3]>0:
        img = img[:,::-1,:]
      imgs.append(img)

    self.set_building_visibility(False)
    return imgs
