from enum import Enum


class SirenBase:
    pass


class Renderer:
    def __init__(self, entity):
        self.entity = entity

    def render(self):
        return self._render(self.entity)

    def _render(self, e):
        if isinstance(e, SirenBase):
            return self._render_object(e.__dict__)
        elif isinstance(e, dict):
            return self._render_dict(e)
        elif isinstance(e, list):
            return self._render_list(e)
        elif isinstance(e, Enum):
            return e.value
        elif hasattr(e, 'data'):
            return e.data
        else:
            return e

    def _render_list(self, e):
        return [self._render(v) for v in e if v is not None]

    def _render_dict(self, e):
        return {k: self._render(v) for k, v in e.items() if v is not None}

    def _render_object(self, e):
        return {k[1:]: self._render(v) for k, v in e.items() if v is not None}


# TODO: remove in next version
def to_renderable(entity):
    return Renderer(entity)


