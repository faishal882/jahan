import sys
import os
import unittest

# Add the parent directory of the current file to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from jahan import Jahan, Request, Response, TemplateResponse


class TestJahan(unittest.TestCase):

    def setUp(self):
        self.app = Jahan('test_app')
        self.app.router.add_route(r'^/$', self.home)
        self.app.router.add_route(r'^/hello/(\w+)/$', self.say_hello)
    
    def home(self, request):
        return Response('Welcome to Jahan!')
   
    def say_hello(self, request, name):
        return Response(f'Hello, {name}!')


    def test_home(self):
        response = self.app.application({'PATH_INFO': '/'}, self.start_response)
        _response = b''.join(list(response)).decode()
        self.assertEqual(_response, 'Welcome to Jahan!')

    def test_say_hello(self):
        response = self.app.application({'PATH_INFO': '/hello/Joe/'}, self.start_response)
        _response = b''.join(list(response)).decode()
        self.assertEqual(_response, 'Hello, Joe!')
    
    def start_response(self, status, headers):
        pass


if __name__ == '__main__':
    unittest.main()
