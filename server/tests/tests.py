import unittest
import sys
import os


# Add the parent directory of the current file to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from server import parse_header


class TestParsingFunctions(unittest.TestCase):

    def test_parse_header(self):
        # Test case for a simple request header with no body
        request_str = "GET / HTTP/1.1\r\nHost: localhost\r\nConnection: keep-alive\r\n\r\n"
        headers, body = parse_header(request_str)
        expected_headers = {
            'REQUEST_METHOD': 'GET',
            'PATH_INFO': '/',
            'SERVER_PROTOCOL': 'HTTP/1.1',
            'Host': 'localhost',
            'Connection': 'keep-alive'
        }
        self.assertEqual(headers, expected_headers)
        self.assertEqual(body, '')

    def test_parse_header_with_body(self):
        # Test case for a request header with a body
        request_str = "POST /submit HTTP/1.1\r\nHost: localhost\r\nConnection: keep-alive\r\nContent-Length: 10\r\n\r\nHello World"
        headers, body = parse_header(request_str)
        expected_headers = {
            'REQUEST_METHOD': 'POST',
            'PATH_INFO': '/submit',
            'SERVER_PROTOCOL': 'HTTP/1.1',
            'Host': 'localhost',
            'Connection': 'keep-alive',
            'Content-Length': '10'
        }
        self.assertEqual(headers, expected_headers)
        self.assertEqual(body, 'Hello World')


if __name__ == '__main__':
    unittest.main()
