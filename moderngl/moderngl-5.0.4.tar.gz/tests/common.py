import moderngl

_static = {
    'context': None,
}


def get_context() -> moderngl.Context:
    ctx = _static.get('context')

    if ctx is None:
        ctx = moderngl.create_standalone_context(size=(100, 100))
        _static['context'] = ctx

    return ctx
