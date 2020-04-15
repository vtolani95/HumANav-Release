from humanav_server import HumANavServer
from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.request import Request
from pyramid.request import Response
import json
import numpy as np

humanav_server = HumANavServer()
print('Loaded Meshes\n')


def render_images(request):
    robot_pos_3 = np.array(request.json['robot_pos_3'])
    human_pos_3 = np.array(request.json['human_pos_3'])
    human_speed = request.json['human_speed']

    # Current Human Identity & the attributes we want to change
    human_identity = request.json['human_identity']

    change_human_gender = request.json['change_human_gender']
    change_human_texture = request.json['change_human_texture']
    change_body_shape = request.json['change_body_shape']
    identity_seed = request.json['identity_seed']

    # If changing the human gender we also have to change the texture
    if change_human_gender:
        change_human_texture = True

    # Seed used for determing the 'appearance' of the human
    mesh_seed = request.json['mesh_seed']

    # Check that the human & robot are not in the obstacle
    human_in_obstacle = humanav_server.check_pos_3_in_obstacle(human_pos_3)
    robot_in_obstacle = humanav_server.check_pos_3_in_obstacle(robot_pos_3)
    if human_in_obstacle or robot_in_obstacle:
        request.response.status = 400
        return 'Either the Human or Robot is Inside the Obstacle! Please fix and retry.'

    # Render the RGB, Depth, and Topview images (saves them locally on the server)
    # Returns a url which points to each image
    data = humanav_server.render_images(robot_pos_3, human_pos_3, human_speed,
                                        human_identity, change_human_gender,
                                        change_human_texture, change_body_shape,
                                        identity_seed, mesh_seed)

    # Clean up the data so it is JSON serializable
    data['human_identity']['body_shape'] = int(data['human_identity']['body_shape'])

    # Format to json
    data_json = json.dumps(data)

    return data_json

def get_new_human_texture(request):
    seed = request.json['seed']
    gender = request.json['gender']

    import pdb; pdb.set_trace()
    pass

def get_new_human_identity(request):
    try:
        params = request.json
    except json.decoder.JSONDecodeError:
        params = dict(request.params)

    if 'identity_seed' in params.keys():
        identity_seed = int(params['identity_seed'])
    else:
        import pdb; pdb.set_trace()
        pass

    #humanav_server = HumANavServer()
    human_identity = humanav_server.get_new_human_identity(identity_seed)

    # convert front np.int64 to native int to send over http
    human_identity['body_shape'] = int(human_identity['body_shape'])
    return human_identity


def hello_world(request):
    return 'Hello World'

# Needed for production server
config = Configurator()

# Add the /hello_world route
# For debugging connections with other servers
config.add_route('hello_world', '/hello_world')
config.add_view(hello_world, route_name='hello_world', renderer='json')

# add the /render_images route
config.add_route('render_images', '/render_images')
config.add_view(render_images, route_name='render_images', renderer='json')

# Add the /get_new_human_identity route
config.add_route('get_new_human_texture', '/get_new_human_texture')
config.add_view(get_new_human_texture, route_name='get_new_human_texture', renderer='json')

# Serve static assets
config.add_static_view(name='static_assets', path='/home/vtolani/Documents/Projects/HumANav/server/outdir')

def request_factory(environ):
    request = Request(environ)
    request.response = Response()
    request.response.headerlist = []
    request.response.headerlist.extend(
        (
            ('Access-Control-Allow-Origin', '*'),
            ('Content-Type', 'application/json')
        )
    )
    return request

config.set_request_factory(request_factory)

app = config.make_wsgi_app()


if __name__ == '__main__':
    server = make_server('0.0.0.0', 8080, app)
    server.serve_forever()
