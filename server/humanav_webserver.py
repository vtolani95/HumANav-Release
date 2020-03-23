from humanav_server import HumANavServer
from wsgiref.simple_server import make_server
from pyramid.config import Configurator
import json
import numpy as np

humanav_server = HumANavServer()
print('Loaded Meshes\n')


def render_images(request):
    robot_pos_3 = np.array(request.json['robot_pos_3'])
    human_pos_3 = np.array(request.json['human_pos_3'])
    human_speed = request.json['human_speed']
    human_identity = request.json['human_identity']
    human_visible = request.json['human_visible']

    if 'mesh_seed' in request.json.keys():
        mesh_seed = request.json['mesh_seed']
    else:
        import pdb; pdb.set_trace()


    # Render the RGB, Depth, and Topview images (saves them locally on the server)
    # Returns a url which points to each image
    img_urls = humanav_server.render_images(robot_pos_3, human_pos_3, human_speed,
                                            human_identity, mesh_seed, human_visible=human_visible)

    # Format to json
    img_urls_json = json.dumps(img_urls)

    return img_urls_json

def get_new_human_identity(request):
    params = request.json
    if 'identity_seed' in params.keys():
        identity_seed = params['identity_seed']
    else:
        import pdb; pdb.set_trace()
        pass

    #humanav_server = HumANavServer()
    human_identity = humanav_server.get_new_human_identity(identity_seed)

    # convert front np.int64 to native int to send over http
    human_identity['body_shape'] = int(human_identity['body_shape'])
    return human_identity

if __name__ == '__main__':
    with Configurator() as config:
        # Add routes

        # add the /render_images route
        config.add_route('render_images', '/render_images')
        config.add_view(render_images, route_name='render_images', renderer='json')

        # Add the /get_new_human_identity route
        config.add_route('get_new_human_identity', '/get_new_human_identity')
        config.add_view(get_new_human_identity, route_name='get_new_human_identity', renderer='json')

        app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 5000, app)
    server.serve_forever()
