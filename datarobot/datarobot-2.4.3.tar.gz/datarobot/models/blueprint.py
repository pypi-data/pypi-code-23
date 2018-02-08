import trafaret as t

from datarobot.models.api_object import APIObject
from ..utils import deprecation_warning, encode_utf8_if_py2


class Blueprint(APIObject):
    """ A Blueprint which can be used to fit models

    Attributes
    ----------
    id : str
        the id of the blueprint
    processes : list of str
        the processes used by the blueprint
    model_type : str
        the model produced by the blueprint
    project_id : str
        the project the blueprint belongs to
    """
    _converter = t.Dict({
        t.Key('id', optional=True): t.String(),
        t.Key('processes', optional=True): t.List(t.String()),
        t.Key('model_type', optional=True): t.String(),
        t.Key('project_id', optional=True): t.String()
    }).allow_extra('*')

    def __init__(self, id=None, processes=None, model_type=None, project_id=None):
        if isinstance(id, dict):
            deprecation_warning('Blueprint instantiation from a dict',
                                deprecated_since_version='v2.3',
                                will_remove_version='v3.0',
                                message='Use Blueprint.from_data instead')
            self.__init__(**id)
        else:
            self.id = id
            self.processes = processes
            self.model_type = model_type
            self.project_id = project_id

    def __repr__(self):
        return encode_utf8_if_py2(u'Blueprint({})'.format(self.model_type))

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.id == other.id

    @classmethod
    def from_location(cls, path):
        raise NotImplementedError('Blueprints do not have a retrieve method in the API')
