import urllib
from wsgiref.headers import Headers
import http as _http
import re
from wsgiref.simple_server import make_server
import string

############################ REQUEST OBJECT ###############################


class Request:
    """ 
    A wrapper for WSGI environment dictionaries. All methods are readble only
    """

    def __init__(self, environ):
        self.environ = environ

    @property
    def args(self):
        get_args = urllib.parse.parse_qs(self.environ['QUERY_STRING'])
        return {k: v[0] for k, v in get_args.items()}

    @property
    def path(self):
        return '/' + self.environ.get('PATH_INFO', '').lstrip('/')

    @property
    def method(self):
        return self.environ.get('REQUEST_METHOD')

    def __repr__(self):
        return '<%s: %s %s>' % (self.__class__.__name__, self.method, self.path)

########################### RESPONSE OBJECT ###############################


class Response:
    """ 
    Class for a response body and headers.
    :param body: The response body as one of the supported types.
    :param status: Either an HTTP status code (e.g. 200) or a status line
                       including the reason phrase (e.g. '200 OK').
    :param headers: A dictionary or a list of name-value pairs.
    """

    def __init__(self, response=None, status=200, charset='utf-8', content_type='text/html'):
        self.response = [] if response is None else response
        self.charset = charset
        self.headers = Headers()
        ctype = f'({content_type}; charset={charset})'
        self.headers.add_header('content-type', ctype)
        self._status = status

    @property
    def status(self):
        status_string = _http.client.responses.get(self._status, 'UNKNOWN')
        return f'{self._status} {status_string}'

    def __iter__(self):
        for k in self.response:
            if isinstance(k, bytes):
                yield k
            else:
                yield k.encode(self.charset)

    def __repr__(self):
        return f'<{self.__class__.__name__}: status: {self.status}>'


class TemplateResponse(Response):
    def __init__(self, template, context=None, **kwargs):
        super().__init__(**kwargs)
        self.template = template
        self.context = context

    def __iter__(self):
        template = string.Template(open(self.template).read())
        response = template.substitute(self.context)
        yield response.encode(self.charset)


class Router:
    def __init__(self):
        self.routing_table = []

    def add_route(self, patten, callback):
        self.routing_table.append((patten, callback))

    def match(self, path):
        for (pattern, callback) in self.routing_table:
            m = re.match(pattern, path)
            print("ROUTER>>>", pattern, path, callback, m.groups())
            if m:
                return (callback, m.groups())
        raise ModuleNotFoundError()
########################### ROUTER OBJECT ################################


class Router:
    """
    Class for storing url routes
    """

    def __init__(self):
        self.routing_table = []

    def add_route(self, patten, callback):
        self.routing_table.append((patten, callback))

    def match(self, path):
        for (pattern, callback) in self.routing_table:
            m = re.match(pattern, path)
            if m:
                return (callback, m.groups())
        raise ModuleNotFoundError()


############################################################################
# MAIN APPLICATION ##############                                     ######
############################################################################
class Jahan:
    """
    Each Jahan object represents a single, distinct web application and
    consists of routes, callbacks and configuration.
    Instances are callable WSGI applications.
    """

    def __init__(self):
        self.router = Router()

    def run(self, **kwargs):
        ''' Calls :func:`run` with the same parameters. '''
        run(self, **kwargs)

    def add_route(self, route):
        ''' Add a route object, but do not change the :data:`Route.app`
            attribute.'''
        def decorator(func):
            self.router.add_route(route, func)
            return func
        return decorator
        # return callback

    def application(self, enviorn, start_response):
        try:
            request = Request(enviorn)
            callback, args = self.router.match(request.path)
            response = callback(request, *args)
        except:
            response = Response("<h1>Not Found</h1>", status=404)

        start_response(response.status, response.headers.items())
        return iter(response)


def run(application, **kwargs):
    with make_server("", 8000, application.application) as httpd:
        print("Serving on http://127.0.0.1:8000/ ")
        print('Press CTRL + C to exit..')
        try:
            # Serve until process is killed
            httpd.serve_forever()
        except KeyboardInterrupt:
            print('exit')
