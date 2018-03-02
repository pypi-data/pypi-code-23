from inspect import isclass
from collections import OrderedDict
import copy
from .exceptions import OrmParameterError, OrmModelDeclarationError, OrmManagementError


class Mapper(object):
    def __init__(self):
        self.models = dict()
        self.templates = dict()
        self.models_declared = list()
        self.templates_models = dict()
        self.models_templates = dict()
        self.userident_model = None
        self.many2many = OrderedDict()
        self.m2m_map = {}
        self.m2m_c = {}
        self._on_model_declare = dict()

    def validate_all(self):
        for model_name in self.models:
            model = self.models[model_name]
            model_attrs = model.__meta__.get_attributes()
            for attr in model_attrs:
                if not hasattr(attr, 'validate'):
                    continue
                attr.validate()

    def map_template(self, template):
        self.templates[template.__name__] = template

    def has_template(self, name):
        return name in self.templates

    def get_template_by_name(self, name):
        return None if name not in self.templates else self.templates[name]

    def unmap_template(self, name):
        if name not in self.templates:
            return
        if name in self.templates_models:
            raise OrmManagementError("cannot unmap template '%s' because it is already used in Models!" % name)
        del(self.templates[name])

    def is_model_templated_with(self, model, template):
        model_ = model if isinstance(model, str) else model.__name__
        template_ = template if isinstance(template, str) else template.__name__
        if not self.has_template(template_):
            return False
        return template_ in self.models_templates[model_]

    def map_model(self, model):
        self.models[model.__name__] = model

    def has_model(self, name):
        return name in self.models

    def unmap_model(self, name):
        if name not in self.models:
            return
        del(self.models[name])
        if name in self.models_declared:
            del(self.models_declared[self.models_declared.index(name)])
        if name in self.models_templates:
            for template in self.models_templates[name]:
                if template not in self.templates_models or name not in self.templates_models[template]:
                    continue
                del(self.templates_models[template][self.templates_models[template].index(name)])

    def get_model_by_name(self, name):
        return None if name not in self.models else self.models[name]

    def get_models_for_migrate(self, tag=None):
        for_migrate = dict()
        for k in self.models:
            if self.models[k].__meta__.tag is not None and self.models[k].__meta__.tag != tag:
                continue
            for_migrate[k] = self.models[k]
        return for_migrate

    def model_declare(self, model_name):
        if model_name not in self.models_declared:
            self.models_declared.append(model_name)
        self.call_on_model_declare(model_name)

    def register_on_model_declare(self, model_name, callback, *args, **kwargs):
        if model_name not in self._on_model_declare:
            self._on_model_declare[model_name] = list()
        self._on_model_declare[model_name].append((callback, args, kwargs))
        if model_name in self.models_declared:
            self.call_on_model_declare(model_name)

    def call_on_model_declare(self, model_name):
        if model_name not in self._on_model_declare or not self._on_model_declare[model_name]:
            return
        for trigger in self._on_model_declare[model_name]:
            callback = trigger[0]
            args = trigger[1]
            kwargs = trigger[2]
            callback(*args, **kwargs)
        self._on_model_declare[model_name] = list()

    def is_model_declared(self, model_name):
        return model_name in self.models

    def register_templated_model(self, template, model):
        if not isinstance(template, str):
            template = template.__name__
        if not isinstance(model, str):
            model = model.__name__
        if template not in self.templates_models:
            self.templates_models[template] = list()
        if model not in self.templates_models[template]:
            self.templates_models[template].append(model)
        if model not in self.models_templates:
            self.models_templates[model] = list()
        if template not in self.models_templates[model]:
            self.models_templates[model].append(template)

    def is_model_templated(self, model):
        if not isinstance(model, str):
            model = model.__name__
        return model in self.models_templates

    def is_template_used(self, template):
        if not isinstance(template, str):
            template = template.__name__
        return template in self.templates_models

    def get_template_models(self, template):
        if not isinstance(template, str):
            template = template.__name__
        return None if template not in self.templates_models else self.templates_models[template]

    def get_model_templates(self, model):
        if not isinstance(model, str):
            model = model.__name__
        return None if not model or model not in self.models_templates else self.models_templates[model]

    def set_userident_model(self, model):
        self.userident_model = model

    def get_userident_model(self):
        return self.userident_model

    def is_userident_model_set(self):
        return bool(self.userident_model is not None)

    def _many2many_create(self, key):
        from .models.base import OrmModel
        from .attributes.base import ColumnAttributeAbstract
        from .attributes.relationships import ForeignKey

        m2m_c = self.m2m_c[key][0]
        fk_ondelete = m2m_c.on_delete
        model_name = "%s_2_%s" % (key[0], key[1])
        table_name = model_name.lower()
        model_a = self.get_model_by_name(key[0])
        model_b = self.get_model_by_name(key[1])
        pk_a = model_a.__meta__.get_primary_key()
        pk_b = model_b.__meta__.get_primary_key()
        if not pk_a or not pk_b:
            raise OrmModelDeclarationError(
                "'ManyToMany' requires that both first and second models have primary key declared!"
            )
        m2m_attributes = {
            '__prefix__': None,
            '__tablename__': table_name
        }
        decl_order = 0
        fk_a_l = list()
        fk_a_r = list()
        fk_b_l = list()
        fk_b_r = list()
        for c in pk_a:
            k_ = "%s_%s" % (str(key[0]).lower(), c.model_k)
            attribute_class = c.base_type or c.__class__
            c_ = attribute_class()
            c_.__dict__ = copy.deepcopy(c.__dict__)
            c_.model_k = k_
            c_.tbl_k = k_
            c_.primary_key = True
            c_.auto_increment = False
            c_.nullable = False
            c_.default = None
            c_.parent_model_k = c.model_k
            c_.parent_tbl_k = c.tbl_k
            c_.parent_model = c.model
            c_.declaration_order = decl_order
            m2m_attributes[k_] = c_
            fk_a_l.append(c_)
            fk_a_r.append(c)
            decl_order += 10
        for c in pk_b:
            k_ = "%s_%s" % (str(key[1]).lower(), c.model_k)
            attribute_class = c.base_type or c.__class__
            c_ = attribute_class()
            c_.__dict__ = copy.deepcopy(c.__dict__)
            c_.model_k = k_
            c_.tbl_k = k_
            c_.primary_key = True
            c_.auto_increment = False
            c_.nullable = False
            c_.default = None
            c_.parent_model_k = c.model_k
            c_.parent_tbl_k = c.tbl_k
            c_.parent_model = c.model
            c_.declaration_order = decl_order
            m2m_attributes[k_] = c_
            fk_b_l.append(c_)
            fk_b_r.append(c)
            decl_order += 10
        fk_a = ForeignKey(fk_a_l, fk_a_r, on_delete=fk_ondelete)
        fk_b = ForeignKey(fk_b_l, fk_b_r, on_delete=fk_ondelete)
        m2m_attributes['ibfk_a_'] = fk_a
        m2m_attributes['ibfk_b_'] = fk_b
        m2m_model = type(model_name, (OrmModel,), m2m_attributes)
        m2m_model.__m2m_columns__ = {
            key[0]: [],
            key[1]: []
        }
        attrs = dir(m2m_model)
        for k in attrs:
            if k.startswith('__') and k.endswith('__'):
                continue
            c = getattr(m2m_model, k)
            if not isinstance(c, ColumnAttributeAbstract):
                continue
            if c.parent_model == model_a:
                m2m_model.__m2m_columns__[key[0]].append(c)
            else:
                m2m_model.__m2m_columns__[key[1]].append(c)
        self.many2many[key] = m2m_model
        for c in self.m2m_c[key]:
            c.validate(m2m_model)

    def _many2many_on_model_declared(self, model):
        model_name = model.__name__ if not isinstance(model, str) else model
        if model_name not in self.m2m_map:
            return
        key = self.m2m_map[model_name]
        if not self.is_model_declared(key[0]) or not self.is_model_declared(key[1]):
            return
        self._many2many_create(key)

    def register_many2many(self, c, model_a, model_b):
        m2m_key = (model_a, model_b)
        if m2m_key not in self.m2m_c:
            self.m2m_c[m2m_key] = list()
        if c not in self.m2m_c[m2m_key]:
            self.m2m_c[m2m_key].append(c)
        if m2m_key in self.many2many:
            return m2m_key
        self.many2many[m2m_key] = None
        self.m2m_map[model_a] = m2m_key
        self.m2m_map[model_b] = m2m_key
        self.register_on_model_declare(model_a, self._many2many_on_model_declared, model_a)
        self.register_on_model_declare(model_b, self._many2many_on_model_declared, model_b)
        return m2m_key

    def get_many2many_junction_model(self, key):
        if key not in self.many2many:
            return None
        return self.many2many[key]

    def get_many2many_model_by_c(self, c):
        from .attributes.relationships import ManyToMany
        if not isinstance(c, ManyToMany):
            raise OrmParameterError(
                "'mapper'.'get_many2many_model_by_c' requires ManyToMany relationship attribute to be given!"
            )
        key = (c.model_a, c.model_b)
        return self.get_many2many_junction_model(key)

    @staticmethod
    def define_attribute_model(parent_model, model_k, attributes):
        from .models.base import OrmModel
        from .attributes.derived import BigAutoIncrement
        from .attributes.relationships import ForeignKey, FK_ONDELETE_CASCADE
        model_name = "%s_%s" % (parent_model.__name__, model_k)
        table_name = model_name.lower()
        model_attrs = {
            '__prefix__': None,
            '__tablename__': table_name,
            'id': BigAutoIncrement()
        }
        model_attrs['id'].declaration_order = 0
        decl_order = 10
        parent_pk = parent_model.__meta__.get_primary_key()
        fk_l = list()
        fk_r = list()
        for c in parent_pk:
            k_ = "parent_%s" % c.model_k
            attribute_class = c.base_type or c.__class__
            c_ = attribute_class()
            c_.__dict__ = copy.deepcopy(c.__dict__)
            c_.model_k = k_
            c_.tbl_k = k_
            c_.primary_key = False
            c_.auto_increment = False
            c_.nullable = False
            c_.default = None
            c_.parent_model_k = c.model_k
            c_.parent_tbl_k = c.tbl_k
            c_.parent_model = c.model
            c_.declaration_order = decl_order
            model_attrs[k_] = c_
            fk_l.append(c_)
            fk_r.append(c)
            decl_order += 10
        for k in attributes:
            c = attributes[k]
            model_attrs[k] = c() if isclass(c) else c
        fk = ForeignKey(fk_l, fk_r, on_delete=FK_ONDELETE_CASCADE)
        model_attrs['ibfk_parent'] = fk
        return type(model_name, (OrmModel,), model_attrs)


mapper = Mapper()
