# WSGI Framework - Jahan

This is a simple WSGI (Web Server Gateway Interface) framework called Jahan. It provides a basic structure for building web applications in Python. It includes a Request object, a Response object, and a Router object for handling incoming HTTP requests and generating appropriate responses.

## How to Use:

1. Create an instance of the `Jahan` class and define your web application routes using the `add_route` method.

2. Define callback functions for each route. Each callback function should take a `Request` object as its first argument.

3. The callback function should process the request, generate a response (either a `Response` object or a `TemplateResponse` object), and return it.

4. Run the application using the `run()` method of the `Jahan` class.

5. The application will start serving at `http://127.0.0.1:8000/`. You can access the application in your web browser.

Demo application:
first clone the repository containing Jahan Framework
```bash
git clone https://github.com/faishal882/jahan-demo-app.git
``` 
It already has demo application built, After cloning the file structure must be in
```bash
demo_jahan_app/
    /app
      __init__.py
      src.py
      models.py
    /jahan (this folder contains the Framework)
      __init__.py
      /tests
        tests.py
      jahan.py
    /templates
      add_employee.html
      employees.html
    main.py
    ...
```
Please create and start and virtual enviornment before running the application
```bash
python -m venv <env-name>
```
In windows activate  virtual enviornment
```bash
<env-name>/Scripts/activate.bat
```
Install pre-run requirements
```bash
pip install -r requirements.txt
```
To run the application locally
```bash
python main.py
```

## Classes and Functions:

1. `Request` class:
   A wrapper for WSGI environment dictionaries. It provides read-only access to various properties of the HTTP request, such as query string parameters, request method, path, and WSGI environment.

2. `Response` class:
   A class for creating HTTP responses. It allows you to set the response body, status code, content type, and other response headers.

3. `TemplateResponse` class:
   An inherited class from `Response`. It allows you to render a Jinja2 template and use it as a response.

4. `Router` class:
   A class for storing URL routes and their corresponding callbacks. It provides methods to add new routes and match a URL path to a specific callback.

5. `Jahan` class:
   The main application class that represents a single web application. It includes a router to handle URL routing. It is a callable WSGI application.

## Methods and Properties:

1. `Request` class:

   - `get_qs`: Returns a dictionary of query string parameters provided by the user.
   - `get_post`: Returns a dictionary of data provided by the user via POST method.
   - `path`: Returns the path of the request.
   - `method`: Returns the method of the request (e.g., GET, POST, etc.).
   - `env`: Returns the whole WSGI environment passed in the request.

2. `Response` class:

   - `status`: Returns the HTTP status code and reason phrase of the response.
   - `__iter__()`: Iterates over the response body and yields data to be sent to the client.

3. `TemplateResponse` class:

   - `__iter__()`: Renders the Jinja2 template and yields the response body. Jinja2 templating engine is implemented, so context can be simply accessed in html using {{ context }}. For further documentation please visit offical documentation site of Jinja.

   ```
   TemplateResponse("template.html", context={"Name": "John"})
   ```

   In html file

   ```
   <p>{{ Name }}</p>
   ```

4. `Router` class:

   - `add_route(pattern, callback)`: Adds a new URL route with a corresponding callback function.
   - `match(path)`: Matches a URL path with a callback function from the routing table.

5. `Jahan` class:

   - `run()`: Starts the WSGI application with the built-in python wsgiref server.
   - `add_route(route)`: Adds a new route object to the router.The argument given should be regex.
     This is decorator method,
     Use:

   ```
   app = Jahan(__name__)

   @app.add_route(r"/$")
   def hello_world(request):
     pass
   ```

   In above code hello_world is added to url route `<your-domain-name>/` as callback function

## Application Workflow:

1. The `Jahan` class creates an instance of the `Router` class to store URL routes and their callbacks.

2. The user defines URL routes using the `add_route` decorator method of the `Jahan` class and provides corresponding callback functions.

3. When an HTTP request is received, the `application` method of the `Jahan` class is called.

4. The `Router` class matches the URL path of the request with a callback function from the routing table. Routing table stores all the url routes with its callback function

5. The matched callback function is called with a `Request` object as its argument.

6. The callback function processes the request, generates a response, and returns it as a `Response` object.

7. The `application` method sets the response status and headers, and iterates over the response body to send it to the client.

8. The WSGI server starts serving the application, and it continues to serve incoming requests until it is terminated.

## Dependencies:

The framework uses the following Python standard libraries and third-party modules:

- `re`: For regular expressions.
- `urllib`: For parsing query string and post data.
- `http` module: For handling HTTP status codes and reason phrases.
- `wsgiref.headers`: For handling response headers.
- `wsgiref.simple_server`: For creating a simple WSGI server.
- `jinja2.Template`: For rendering Jinja2 templates.



## jahan
A very simple WSGI webframework with python inspired from Flask

## Demo app
Please visit here<https://github.com/faishal882/jahan-demo-app> to test demo app built using Jahan and SQLAlchemy

## Clone Respository
clone jahan webframework repository in your local machine
```bash
git clone https://github.com/faishal882/jahan.git
```


## Setup
Ensure you have python 3.6+ installed.😊

A simple jahan app

```bash
from jahan.jahan import Response, Jahan

app = Jahan()

@app.add_route(r'/$')
def index(request, name):
    print(request, name)
    return Response(f'Hello world')

if __name__ == "__main__":
    app.run()
```

run the jahan application simply by going to the root folder of application and running command
```bash
python <file-name>
```
It will start a python inbuilt wsgiref server

To run the application with another wsgi server like waitress,
Paste this code block in end of your application main file
```bash
application = app.application
```

Now run the waitress server with the command
```bash
waitress-serve --listen*:8000 <file-name>:application
```
It will start the waitress server you can check by visiting http://127.0.0.1:8000/

## WARNING 😞
Please avoid using it in deployment as none of the secuurity protocol has been implemented, noe does error handling.
