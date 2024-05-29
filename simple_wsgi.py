def app(environ, start_response):
    method = environ["REQUEST_METHOD"]
    if method == "POST":
        try:
            size = int(environ.get("CONTENT_LENGTH", 0))
        except ValueError:
            size = 0
        post_params = environ["wsgi.input"].read(size).decode("utf-8")
    else:
        post_params = ""

    get_params = environ["QUERY_STRING"]

    response_body = f"GET parameters: {get_params}\nPOST parameters: {post_params}"

    status = "200 OK"
    headers = [("Content-Type", "text/plain")]
    start_response(status, headers)
    return [response_body.encode("utf-8")]


if __name__ == "__main__":
    from wsgiref.simple_server import make_server

    srv = make_server("localhost", 8081, app)
    srv.serve_forever()
