class _HttpRequest:
    def __init__(self, path, method, headers, path_params, query_params, body):
        self.path = path
        self.method = method
        self.headers = headers
        self.path_params = path_params
        self.query_params = query_params
        self.body = body
