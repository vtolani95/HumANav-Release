from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response

def hello_world(request):
    return Response('<h1>Hello world!</h1>')

# Move the application object here.
# Create a configurator to make *wsgi app(lication)*
config = Configurator()
config.add_view(hello_world)

# The "app" object to be exposed
app = config.make_wsgi_app()

# If run directly, still construct a [development]
# server process and start serving on port #8080. 
if __name__ == '__main__':
    server = make_server('0.0.0.0', 8080, app)
    server.serve_forever()
