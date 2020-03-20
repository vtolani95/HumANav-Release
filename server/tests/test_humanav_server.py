from humanav_server import HumANavServer
import numpy as np

def test_humanav_server():
    server = HumANavServer()

    # Set the robot and human states
    robot_pos_3 = np.array([7.5, 12., -1.3])
    human_pos_3 = np.array([8.0, 9.75, np.pi/2.])

    human_speed = .7
    human_identity = server.get_new_human_identity(48)

    mesh_seed = 20

    # Render images
    server.render_images(robot_pos_3, human_pos_3, human_speed, human_identity, mesh_seed)
    
    # Render images without the human
    server.render_images(robot_pos_3, human_pos_3, human_speed, human_identity, mesh_seed, human_visible=False)

if __name__ == '__main__':
    test_humanav_server()
