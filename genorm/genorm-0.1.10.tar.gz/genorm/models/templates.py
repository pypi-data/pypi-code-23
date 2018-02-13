import copy
from pc23 import metaclass
from .meta import OrmModelTemplateMeta
from ..mapper import mapper
from ..attributes.base import AttributeAbstract
from ..exceptions import OrmParameterError


def with_model_template(*args):
    """ Decorator applying ORM templates to the end Model """
    def wrapper(cls):
        declaration_order = 0
        extra_attrs = list()
        keys_list = list()
        meta_data = dict()
        for template in args:
            if not issubclass(template, OrmModelTemplate):
                raise OrmParameterError(
                    "'with_model_template' requires that given Model's be a type of OrmModelTemplate!"
                )
            t_keys = dir(template)
            for k in t_keys:
                if k.startswith('__') and k.endswith('__'):
                    k_meta_attr = k[2:-2]
                    if hasattr(cls.__meta__, k_meta_attr) and not hasattr(cls, k) and k_meta_attr not in meta_data:
                        meta_data[k_meta_attr] = getattr(template, k)
                    continue
                if k in keys_list:
                    continue
                keys_list.append(k)
                c = getattr(template, k)
                extra_attrs.append((k, c, getattr(c, 'declaration_order', -1), template))
            mapper.register_templated_model(template, cls)
        extra_attrs = sorted(extra_attrs, key=lambda x: x[2])
        for attr in extra_attrs:
            k, co, decl_order, template = attr
            if hasattr(cls, k) and not getattr(getattr(cls, k), 'auto_created', False):
                continue
            c = copy.deepcopy(co)
            if isinstance(c, AttributeAbstract):
                c.declaration_order = declaration_order
                declaration_order += 1
                c.template_model = template
                c.template_k = k
            cls.__settemplatedattr__(k, c)
        for k in meta_data:
            setattr(cls.__meta__, k, meta_data[k])
            setattr(cls, '__%s__' % k, meta_data[k])
        return cls
    return wrapper


def use_model_template(base_model, *args):
    return with_model_template(*args)(base_model)


@metaclass(OrmModelTemplateMeta)
class OrmModelTemplate(object):
    pass


