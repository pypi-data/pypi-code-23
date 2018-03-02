from .base import AttributeAbstract, DataAttributeAbstract
from ..exceptions import OrmParameterError
from ..funcs import DbFunctionAbstract


class ViewPropertyAbstract(DataAttributeAbstract):
    pass


class AttributeView(ViewPropertyAbstract):
    def __init__(self, o, k=None, **kwargs):
        super(AttributeView, self).__init__(**kwargs)
        self.func = None
        if isinstance(o, DbFunctionAbstract):
            self.func = o
            o = None
            k = None
        elif k is None:
            if isinstance(o, AttributeAbstract):
                k = o.model_k
                o = o.model.__name__
            elif isinstance(o, str):
                if '.' in o:
                    if o.count('.') != 1:
                        raise OrmParameterError(
                            "AttributeView requires first argument to be an attribute, be a name of the attribute of"
                            " the base Model or be in format 'Model.attr_name'!"
                        )
                    o, k = o.split('.')
                else:
                    k = o
                    o = None
        self.owner = o
        self.owner_k = k
        self.kw = kwargs

    def on_view_metainit(self):
        if not self.owner:
            return
        base_model = getattr(self.model, '__model__')
        if base_model.__name__ == self.owner:
            base_c = getattr(base_model, self.owner_k)
        elif self.owner in self.model.__joins__:
            jc = getattr(self.model, self.owner)
            base_c = getattr(jc.ref_model, self.owner_k)
        else:
            return
        ck = dir(base_c)
        for k in ck:
            if k.startswith('__') and k.endswith('__'):
                continue
            if k in self.kw:
                continue
            v = getattr(base_c, k)
            if not hasattr(self, k) or not getattr(self, k, None):
                setattr(self, k, v)


class ViewJoin(ViewPropertyAbstract):
    def __init__(self, ref_model, *args):
        super(ViewJoin, self).__init__()
        self.ref_model = ref_model
        self.args = args


