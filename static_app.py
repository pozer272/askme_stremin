def static_app(environ, start_response):
    status = "200 OK"
    response_headers = [("Content-type", "text/html")]
    start_response(status, response_headers)
    with open("/home/user/ask_pupkin/static/sample.html", "rb") as f:
        return [f.read()]


if __name__ == "__main__":
    from wsgiref.simple_server import make_server

    server = make_server("localhost", 8001, static_app)
    server.serve_forever()
