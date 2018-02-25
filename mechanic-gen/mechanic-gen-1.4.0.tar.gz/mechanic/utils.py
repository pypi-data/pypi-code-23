import flask
import werkzeug.exceptions


def api_enforce(request=None, response=None, many=False, code=200, auth_bearer=True):
    def api_enforce_decorator(f):
        def wrapper(*args, **kwargs):
            if auth_bearer and not flask.request.headers.get('Authorization', '').startswith('Bearer'):
                msg = 'Authorization Bearer token not present in header. Expected format: Authorization: Bearer <token>'
                raise werkzeug.exceptions.Unauthorized(msg)
            embed = flask.request.args.get('embed', '').split(',')
            for k, v in flask.request.args.items():
                kwargs[k] = v
            etag = None

            if request:
                request_schema = request(many=many, context={'embed': embed})
                obj, errors = request_schema.load(flask.request.get_json())
                resp = f(*args, serialized_request_data=obj, **kwargs)
            else:
                resp = f(*args, **kwargs)

            if response:
                response_schema = response(many=many, context={'embed': embed})
                etag = getattr(resp, 'etag', None) if getattr(resp, 'etag', None) else None
                ret, errors = response_schema.dump(resp)
            else:
                ret = resp

            if etag:
                return flask.make_response(flask.jsonify(ret), code, {'ETag': etag})
            else:
                return flask.make_response(flask.jsonify(ret), code, {})
        return wrapper
    return api_enforce_decorator
