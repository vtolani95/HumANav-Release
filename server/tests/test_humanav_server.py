import numpy as np
import requests

def test_humanav_server():
    from humanav_server import HumANavServer
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

def test_humanav_webserver():
    base_url = 'http://localhost:5000'

    # Set the robot and human states
    robot_pos_3 = np.array([7.5, 12., -1.3])
    human_pos_3 = np.array([8.0, 9.75, np.pi/2.])

    human_speed = .7

    data = {'identity_seed': 48}
    human_identity = requests.get('{:s}/get_new_human_identity'.format(base_url), json=data).json()

    mesh_seed = 20
    data = {'robot_pos_3': robot_pos_3.tolist(),
            'human_pos_3': human_pos_3.tolist(),
            'human_speed': human_speed,
            'human_identity': human_identity,
            'mesh_seed': mesh_seed,
            'human_visible': True}

    img_urls = requests.get('{:s}/render_images'.format(base_url), json=data).json()

    # Change the body shape and position 
    # but keep the texture the same
    data['human_identity']['body_shape'] = 519
    data['human_identity']['gender']  = 'female'
    data['mesh_seed'] = 22
    data['human_visible'] = True

    img_urls = requests.get('{:s}/render_images'.format(base_url), json=data).json()

    # Get a new identity of human
    data = {'identity_seed': 36}
    human_identity = requests.get('{:s}/get_new_human_identity'.format(base_url), json=data).json()

    mesh_seed = 10
    data = {'robot_pos_3': robot_pos_3.tolist(),
            'human_pos_3': human_pos_3.tolist(),
            'human_speed': human_speed,
            'human_identity': human_identity,
            'mesh_seed': mesh_seed,
            'human_visible': True}

    img_urls = requests.get('{:s}/render_images'.format(base_url), json=data).json()

    # Render an image without the human
    data['human_visible'] = False
    img_urls = requests.get('{:s}/render_images'.format(base_url), json=data).json()

    # Render the original human
    data = {'identity_seed': 48}
    human_identity = requests.get('{:s}/get_new_human_identity'.format(base_url), json=data).json()

    mesh_seed = 20
    data = {'robot_pos_3': robot_pos_3.tolist(),
            'human_pos_3': human_pos_3.tolist(),
            'human_speed': human_speed,
            'human_identity': human_identity,
            'mesh_seed': mesh_seed,
            'human_visible': True}

    img_urls = requests.get('{:s}/render_images'.format(base_url), json=data).json()

if __name__ == '__main__':
    #test_humanav_server()
    test_humanav_webserver()
