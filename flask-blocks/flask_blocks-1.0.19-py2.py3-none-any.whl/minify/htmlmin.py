import flask
import functools


def use(mime=[]):
    return _minify(_minify_html_string, mime)


def _minify(run_minifier, mime=[]):
    def i(f):
        @functools.wraps(f)
        def decorated(*args, **kwargs):
            response = f(*args, **kwargs)
            if isinstance(response, str):
                return run_minifier(response)

            if isinstance(response, flask.Response):
                if response.content_type in mime:
                    data = response.get_data(as_text=True)
                    minified = run_minifier(data)
                    response.set_data(minified)
                    return response

            # The response won't be minified, because the MIME is not among the
            # list of MIME types to minify.
            return response

        return decorated

    return i


def _minify_html_string(text):
    import htmlmin
    return htmlmin.minify(text, remove_optional_attribute_quotes=False)
