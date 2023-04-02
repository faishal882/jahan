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
    def get_qs(self):
        """
        method allows you to get data provided by user via GET method or else returns {}

           Use: request = Resquest()
              : requset.get_qs 
        """
        get_args = urllib.parse.parse_qs(self.environ['QUERY_STRING'])
        return {k: v[0] for k, v in get_args.items()}

    @property
    def get_post(self):
        """
        method allows you to get data provided by user via POST method or else returns {}

           Use: request = Resquest()
              : requset.get_post
        """
        data = ''
        try:
            length = int(self.environ.get('CONTENT_LENGTH', '0'))
        except ValueError:
            length = 0
        if length != 0:
            data = self.environ['wsgi.input'].read(length).decode('utf8')

        get_data = urllib.parse.parse_qs(data)
        return {k: v[0] for k, v in get_data.items()}

    @property
    def path(self):
        """
        returns path of request
        """
        return '/' + self.environ.get('PATH_INFO', '').lstrip('/')

    @property
    def method(self):
        """
        returns method of request
        """
        return self.environ.get('REQUEST_METHOD')

    @property
    def env(self):
        """
        returns whole wsgi enviornment passed in request
        """
        return self.environ

    def __repr__(self):
        return '<%s: %s %s queryset=%s>' % (self.__class__.__name__, self.method, self.path, self.get_qs)

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


####################### TEMPLATE RESPONSE OBJECT ######################
class TemplateResponse(Response):
    """ 
    Inherited class from Response.
    :param template: template to be returned as response.
    :param status: Either an HTTP status code (e.g. 200) or a status line
                       including the reason phrase (e.g. '200 OK').
    :param context: A dictionary of list-value pair to be inserted in template.
    """
    def __init__(self, template, context=None, **kwargs):
        super().__init__(**kwargs)
        self.template = template
        self.context = context

    def __iter__(self):
        template = string.Template(open(self.template).read())
        response = template.substitute(self.context)
        yield response.encode(self.charset)


########################### ROUTER OBJECT ################################
class Router:
    """
    Class for storing url routes
    :method add_route: for adding url routes.
    :method match: for matching url routes with given callback.
    """

    def __init__(self):
        self.routing_table = []

    def add_route(self, patten, callback):
        """
        Method for adding url routes
        :param pattern: regular expression eg: r'/$'.
        :param callback: function to be called when url route matches
        """
        self.routing_table.append((patten, callback))

    def match(self, path):
        """
        Method for matching url route with callback
        :param path: url pattern to be matgched with regular expression
        """
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
        """" Calls :func:`run` with the wsgi instance application. """
        run(self, **kwargs)

    def add_route(self, route):
        """"
        Add a route object, but do not change the :data:`Route.app` attribute.
        :param route: regular expression eg: r'/hello/$'
        """
        def decorator(func):
            self.router.add_route(route, func)
            return func
        return decorator
        # return callback

    def application(self, enviorn, start_response):
        """
        WSGI instance application, excepts enviorn and start_response to be passed by wsgi server
        """
        try:
            request = Request(enviorn)
            callback, args = self.router.match(request.path)
            response = callback(request, *args)
        except:
            response = Response("<h1>Not Found</h1>", status=404)

        start_response(response.status, response.headers.items())
        return iter(response)


def run(application, **kwargs):
    """
    Run the Jahan.application: WSGI instance with simple inbuilt wsgiref server.
    """
    with make_server("", 8000, application.application) as httpd:
        print("Serving on http://127.0.0.1:8000/ ")
        print('Press CTRL + C to exit..')
        try:
            # Serve until process is killed
            httpd.serve_forever()
        except KeyboardInterrupt:
            print('exit')
