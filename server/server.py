import sys
import io
import socket
import threading

__version__ = "1.0"

def check_header(key: str, headers: dict):
    """
    check for specified key in header dictionary,
    if not present defaults to empty value
     :params: key<str>, headers<dictionary> 
    """
    if key in headers:
        return
    else:
        headers[key] = ""
    return headers


def standarize_header(header: dict):
    """
    standarize the header from request    
     :params: headers<dictionary> 
    """
    keys = [
        'SERVER_PROTOCOL',
        'REQUEST_METHOD',
        'PATH_INFO',
        'Host',
        'Connection',
        'Content-Length',
        'Cache-Control',
        'Content-Type',
        'sec-ch-ua',
        'sec-ch-ua-platform',
        'sec-ch-ua-mobile',
        'Upgrade-Insecure-Requests',
        'User-Agent',
        'Accept',
        'Sec-Fetch-Site',
        'Sec-Fetch-Mode',
        'Sec-Fetch-User',
        'Sec-Fetch-Dest',
        'Accept-Encoding',
        'Accept-Language',
        'Cookie',
        'Referer',
    ]
    for key in keys:
        check_header(key, header)
    return header


def parse_header(request_str: str):
    """
    Function to parse the request header and body,
    header parsed into dict, body into str
    returns (header, body)
     :params: request_str<str> 
    """
    headers = {}
    body = ''
    if request_str != "":
        # Split request text into headers and body using the empty line as delimiter
        try:
            headers_text, body_text = request_str.strip().split('\r\n\r\n', 1)
        except:
            headers_text, body_text = request_str, ''

        # Parse headers
        lines = headers_text.strip().split('\n')
        method, path, http_version = lines[0].split()
        headers = {'REQUEST_METHOD': method,
                   'PATH_INFO': path, 'SERVER_PROTOCOL': http_version}
        for line in lines[1:]:
            if line:
                key, value = line.split(':', 1)
                headers[key.strip()] = value.strip()
        body = body_text
        return (headers, body)
    return (headers, body)


class WSGIServer:
    """
    WSGIServer that implements the Python WSGI protocol for running simple web applications on a local machine,
    such as might be done when testing or debugging an application. Note that this implementation may not cover
    all security issues, so it's best suited for local development and testing purposes.

    :param host: str, the host IP address or domain name where the server will listen for incoming connections.
    :param port: int, the port number on which the server will listen for incoming connections.
    :param app: WSGI application, a callable object conforming to the WSGI interface.
                It receives two arguments: 'environ' (a dictionary containing request details) and 'start_response'
                (a callable for sending the HTTP response status and headers).
    """

    def __init__(self, host: str, port: int, app):
        """
        Initialize the WSGIServer instance with the given host, port, and WSGI application.

        :param host: str, the host IP address or domain name where the server will listen for incoming connections.
        :param port: int, the port number on which the server will listen for incoming connections.
        :param app: WSGI application, a callable object conforming to the WSGI interface.
        """
        self.host = host
        self.port = port
        self.app = app

    def handle_request(self, client_socket):
        """
        Handle an incoming client request by parsing the request, invoking the provided WSGI application,
        and sending back the response to the client.

        :param client_socket: socket, the client socket representing the incoming connection.
        """
        response_sent = False
        request_data = b''
        while True:
            chunk = client_socket.recv(1024)
            if not chunk:
                break
            request_data += chunk
            if b'\r\n\r\n' in request_data:
                break

        request_text = request_data.decode()
        header, request_body = parse_header(request_text)
        request_input = io.BytesIO(request_body.encode())
        _header = standarize_header(header)
        path, query = '/', ''
        if _header:
            if '?' in _header['PATH_INFO']:
                path, query = _header['PATH_INFO'].split('?', 1)
            else:
                path, query = header['PATH_INFO'], ''
        if not response_sent:
            wsgi_env = {
                'SERVER_NAME': socket.getfqdn(self.host),
                'GATEWAY_INTERFACE': 'CGI/1.1',
                'REMOTE_HOST': str(self.host),
                'SERVER_PORT': str(self.port),
                'REQUEST_METHOD': _header['REQUEST_METHOD'],
                'CONTENT_LENGTH': _header['Content-Length'],
                'SCRIPT_NAME': '',
                'SERVER_SOFTWARE': 'WSGIServer/1.0',
                'SERVER_PROTOCOL': _header['SERVER_PROTOCOL'],
                'PATH_INFO': path,
                'QUERY_STRING': query,
                'CONTENT_TYPE': _header['Content-Type'],
                'HTTP_HOST': _header['Host'],
                'HTTP_CONNECTION': _header['Connection'],
                'HTTP_CACHE_CONTROL': _header['Cache-Control'],
                'HTTP_SEC_CH_UA': _header['sec-ch-ua'],
                'HTTP_SEC_CH_UA_MOBILE': _header['sec-ch-ua-mobile'],
                'HTTP_SEC_CH_UA_PLATFORM': _header['sec-ch-ua-platform'],
                'HTTP_UPGRADE_INSECURE_REQUESTS': _header['Upgrade-Insecure-Requests'],
                'HTTP_USER_AGENT': _header['User-Agent'],
                'HTTP_ACCEPT': _header['Accept'],
                'HTTP_SEC_FETCH_SITE': _header['Sec-Fetch-Site'],
                'HTTP_SEC_FETCH_MODE': _header['Sec-Fetch-Mode'],
                'HTTP_SEC_FETCH_USER': _header['Sec-Fetch-User'],
                'HTTP_SEC_FETCH_DEST': _header['Sec-Fetch-Dest'],
                'HTTP_ACCEPT_ENCODING': _header['Accept-Encoding'],
                'HTTP_ACCEPT_LANGUAGE': _header['Accept-Language'],
                'COOKIE': _header['Cookie'],
                'REFERER': _header['Referer'],
                'wsgi.input': request_input,
                'wsgi.errors': sys.stderr,
                'wsgi.version': (1, 0),
                'wsgi.async': False,
                'wsgi.run_once': False,
                'wsgi.url_scheme': 'http',
                'wsgi.multithread': True,
                'wsgi.multiprocess': False,
            }
            response = self.app(wsgi_env, self.start_response)
            try:
                self.send_response(client_socket, response)
                response_sent = True
            except ConnectionAbortedError:
                print("Client closed the connection unexpectedly.")
        # finally:
        client_socket.close()

    def start_response(self, status, response_headers):
        """
        Callback function for the WSGI application to set the response status and headers.

        :param status: str, the HTTP status code and message (e.g., '200 OK').
        :param response_headers: list of tuples, containing the response headers (e.g., [('Content-Type', 'text/html')]).
        """
        self.http_version = 'HTTP/1.1'
        self.status = status
        self.response_headers = response_headers

    def send_response(self, client_socket, response):
        """
        Send the HTTP response to the client.
        This method takes the response generated by the WSGI application and sends it back to the client through
        the provided client socket. The response includes the HTTP status line, headers, and the response body.
        """
        response_headers = [f"{key}: {value}" for key,
                            value in self.response_headers]
        response_headers.append("Connection: keep-alive")
        response_text = "\r\n".join(
            [self.http_version + " " + self.status] + response_headers + ["", ""])
        client_socket.sendall(response_text.encode())
        for data in response:
            client_socket.send(data)
        client_socket.close()

    def serve_forever(self):
        """
        Start the WSGI server and listen for incoming connections indefinitely until interrupted.
        """
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)

        try:
            while True:
                conn, addr = server_socket.accept()
                thread = threading.Thread(
                    target=self.handle_request, args=(conn,))
                thread.start()
        except KeyboardInterrupt:
            print("Server stopped by KeyboardInterrupt (Ctrl+C)")
        finally:
            server_socket.close()
