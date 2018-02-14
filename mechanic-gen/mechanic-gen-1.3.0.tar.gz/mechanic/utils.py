import logging

import flask


def api_enforce(request=None, response=None, many=False, code=200):
    def api_enforce_decorator(f):
        def wrapper(*args, **kwargs):
            logging.getLogger(__name__).debug('Before: %s' % kwargs)
            logging.getLogger(__name__).debug('Before: %s' % str(args))
            embed = flask.request.args.get('embed', '').split(',')
            etag = None

            if request:
                request_schema = request(many=many, context={'embed': embed})
                obj, errors = request_schema.load(flask.request.get_json())
                resp = f(*args, serialized_request_data=obj, **kwargs)
                logging.getLogger(__name__).debug('Request: %s' % str(obj))
            else:
                resp = f(*args, **kwargs)

            logging.getLogger(__name__).debug('Model(s): %s' % str(resp))

            if response:
                response_schema = response(many=many, context={'embed': embed})
                etag = getattr(resp, 'etag', None) if getattr(resp, 'etag', None) else None
                ret, errors = response_schema.dump(resp)
                logging.getLogger(__name__).debug('Response: %s' % str(ret))
            else:
                ret = resp
            logging.getLogger(__name__).debug('After')

            if etag:
                return flask.make_response(flask.jsonify(ret), code, {'ETag': etag})
            else:
                return flask.make_response(flask.jsonify(ret), code, {})
        return wrapper
    return api_enforce_decorator
