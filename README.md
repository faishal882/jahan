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
