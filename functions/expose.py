import functools
import json
import threading
from http.server import HTTPServer
from typing import Any, Callable

import requests
from flask import Flask, jsonify, request


def expose(func: Callable[..., Any], methods: [str], port: int = 8080, hostname: str = "localhost",
           route: str = "/") -> Callable[..., Any]:
    """
    Decorator to expose a function as an HTTP endpoint.

    Args:
        func: The function to be exposed.
        methods: A list of HTTP methods allowed for accessing the endpoint.
        port: The port number on which the server will listen (default: 8080).
        hostname: The hostname or IP address on which the server will run (default: "localhost").
        route: The URL route at which the endpoint will be accessible (default: "/").

    Returns:
        The decorated function that acts as the endpoint.

    Notes:
        This decorator creates a Flask application and configures a route for the provided function,
        making it accessible via HTTP requests. The decorated function is wrapped to handle incoming
        requests and call the original function with the parsed JSON arguments.

        The web server is run in a separate thread, allowing it to be non-blocking and run concurrently
        with the rest of the code.

        Partial functions `expose_all`, `expose_get`, `expose_post`, `expose_put`, and `expose_delete`
        are provided as convenience functions with pre-configured HTTP methods.
    """

    app = Flask(__name__)

    @app.route(route, methods=methods)
    def wrapper() -> Any:
        return jsonify(func(json.loads(request.json)))

    def run_server():
        web_server = HTTPServer((hostname, port), app)
        print("Server started http://%s:%s" % (hostname, port))
        try:
            web_server.serve_forever()
        except TypeError:
            pass
        except KeyboardInterrupt:
            pass

    threading.Thread(target=run_server).start()

    return wrapper


expose_all = functools.partial(expose, methods=['GET', 'POST', 'PUT', 'DELETE'])
expose_get = functools.partial(expose, methods=['GET'])
expose_post = functools.partial(expose, methods=['POST'])
expose_put = functools.partial(expose, methods=['PUT'])
expose_delete = functools.partial(expose, methods=['DELETE'])

jsonParam = {
    "Id": 78912,
    "Customer": "Jason Sweet",
    "Quantity": 1,
    "Price": 18.00
}


@expose_get
def param():
    if jsonParam is not None:
        try:
            print(jsonParam)
        except TypeError:
            print(TypeError, "\n The provided parameters were of the incorrect type.")
    else:
        print("No JSON was provided.")

    r = requests.post('http://localhost:8080/', json={
        "Id": 78912,
        "Customer": "Jason Sweet",
        "Quantity": 1,
        "Price": 18.00
    })

    print(f"Status Code: {r.status_code}, Response: {r.json()}")


param()
