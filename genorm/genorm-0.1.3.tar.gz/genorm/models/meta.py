import inspect
from ..mapper import mapper
from ..attributes.base import AttributeAbstract, ColumnAttributeAbstract, KeyAttributeAbstract,\
    VirtualAttributeAbstract
from ..attributes.columns import ColumnIntegerAbstract, ColumnStringAbstract, ColumnBooleanAbstract, \
    ColumnDatetimeAbstract
from ..attributes.derived import AutoIncrement
from ..attributes.relationships import ForeignKey, ForeignKeyConstraintAbstract
from ..attributes.keys import IndexKey, UniqueKey
from ..attributes.views import AttributeView, ViewJoin
from ..exceptions import OrmModelDeclarationError
from ..funcs import DbFunctionAbstract
from .metastruct import OrmModelMetaStruct


class OrmModelMeta(type):
    def __init__(cls, name, bases, clsdict):
        from ..logs import OrmJournal

        super(OrmModelMeta, cls).__init__(name, bases, clsdict)
        if name in ('OrmModel', 'CompositeOrmModel', 'OrmModelMeta', 'OrmModelAbstract'):
            return

        # If this is not a declared model - returning
        mro_ = cls.mro()
        if len(mro_) <= 2:
            return

        # Initialize model
        meta_ = OrmModelMetaStruct(cls)
        cls.__meta__ = meta_
        for k in dir(cls):
            if not k.startswith('__') or not k.endswith('__'):
                continue
            k_meta_attr = k[2:-2]
            if not hasattr(meta_, k_meta_attr):
                continue
            if k_meta_attr in meta_.PROTECTED:
                raise OrmModelDeclarationError("Cannot declare '%s' using meta-maps!" % k)
            setattr(meta_, k_meta_attr, type.__getattribute__(cls, k))
        type.__setattr__(cls, 'log', OrmJournal(cls))
        mapper.map_model(cls)

        # Initialize declared at a time of class declaration attributes
        cls_keys_ = dir(cls)
        attrs_keys = list()
        for k in cls_keys_:
            if k.startswith('__') and k.endswith('__'):
                continue
            c = type.__getattribute__(cls, k)
            order = getattr(c, 'declaration_order', -1)
            attrs_keys.append((k, order))
        attrs_keys = [y[0] for y in sorted(attrs_keys, key=lambda x: x[1])]
        for k in attrs_keys:
            c = type.__getattribute__(cls, k)
            if not isinstance(c, AttributeAbstract):
                continue
            cls.__initattr__(k)

        # Initialize primary key
        pk = []
        pk_autoincrement = None
        attrs = cls.__meta__.get_real_attributes()
        for c in attrs:
            if not isinstance(c, ColumnAttributeAbstract):
                continue
            if not c.primary_key:
                continue
            if c.auto_increment and pk_autoincrement:
                raise OrmModelDeclarationError("OrmModel can be declared with only one AUTO_INCREMENT column!")
            pk.append(c.model_k)
            if c.auto_increment:
                pk_autoincrement = c.model_k
        # If no primary key defined by the OrmModel designer - we have no create it by ourselfs
        if not pk:
            pk_tbl_k = 'id'
            if hasattr(cls, pk_tbl_k):
                pk_tbl_k = 'pk'
            if hasattr(cls, pk_tbl_k):
                pk_tbl_k = 'id_'
            if hasattr(cls, pk_tbl_k):
                pk_tbl_k = 'pk_'
            if hasattr(cls, pk_tbl_k):
                raise OrmModelDeclarationError(
                    "MySQL based OrmModel must have PRIMARY KEY declared, but '%s' has no any defined"
                    " and ORM cannot declare corresponding attribute itself because suggested names"
                    " 'id', 'pk', 'id_' and 'pk_' are already occupied."
                )
            pk_c = AutoIncrement()
            pk_c.auto_created = True
            pk_c.declaration_order = 0
            pk_autoincrement = pk_tbl_k
            type.__setattr__(cls, pk_tbl_k, pk_c)
            cls.__initattr__(pk_tbl_k)
            pk.append(pk_tbl_k)
        meta_.primary_key = pk
        meta_.auto_increment = pk_autoincrement

        # If this is an userident model - declare it
        userident = type.__getattribute__(cls, '__meta__').userident
        if userident:
            if mapper.is_userident_model_set():
                raise OrmModelDeclarationError("there can be only one user ident model declared!")
            mapper.set_userident_model(cls)

        # Initialize attributes which must be post-initialized after whole OrmModel been declared
        cls_keys = dir(cls)
        for k in cls_keys:
            if k.startswith('__') and k.endswith('__'):
                continue
            c = type.__getattribute__(cls, k)
            if not isinstance(c, AttributeAbstract):
                continue
            c.on_model_declared()

        # Announce that this model is declared and call associated trigers
        mapper.model_declare(cls.__name__)

    def __initattr__(cls, k):
        c = type.__getattribute__(cls, k)
        c.model = cls
        c.model_k = k
        if isinstance(c, (ColumnAttributeAbstract, KeyAttributeAbstract)) and not c.tbl_k:
            c.tbl_k = k
        if isinstance(c, ColumnAttributeAbstract):
            if c.is_softdelete_key:
                if not isinstance(c,
                                  (ColumnIntegerAbstract,
                                   ColumnBooleanAbstract,
                                   ColumnDatetimeAbstract)):
                    raise TypeError((
                        "'is_softdelete_key' might be set for Integer, Boolean, "
                        " Date or DateTime column type only!"
                    ))
                elif cls.__meta__.soft_delete is not None:
                    raise Exception("'is_softdelete_key' might be set for only one column!")
                cls.__meta__.soft_delete = c
            if c.is_default_order:
                if c.is_default_order is True:
                    c.is_default_order = 'asc'
                elif not isinstance(c.is_default_order, str):
                    raise AttributeError("'is_default_order' must be True or a string of 'ASC' or 'DESC'!")
                elif c.is_default_order.upper() not in ('ASC', 'DESC'):
                    raise AttributeError("'is_default_order' must be True or a string of 'ASC' or 'DESC'!")
                cls.__meta__.default_order = (c, c.is_default_order.upper())
            if c.is_version_key:
                if not isinstance(c, (ColumnIntegerAbstract, ColumnDatetimeAbstract)):
                    raise TypeError((
                        "'is_version_key' might be set for Integer or Datetime column"
                        " types only!"
                    ))
                elif cls.__meta__.version_key is not None:
                    raise Exception("'is_version_key' might be set for only one column!")
                cls.__meta__.version_key = k
            if c.is_caption_key:
                if not isinstance(c, (ColumnStringAbstract, VirtualAttributeAbstract)):
                    raise TypeError("'is_caption_key' might be set for textual or custom data types only!")
                elif cls.__meta__.caption_key is not None:
                    raise Exception("'is_caption_key' might be set for only one column!")
                cls.__meta__.caption_key = k
            if c.is_value_key:
                if not isinstance(c, (ColumnAttributeAbstract, VirtualAttributeAbstract)):
                    raise TypeError("'is_value_key' might be set for column or custom data types only!")
                elif cls.__meta__.value_key is not None:
                    raise Exception("'is_value_key' might be set for only one column!")
                cls.__meta__.value_key = k
        elif isinstance(c, KeyAttributeAbstract):
            if isinstance(c, ForeignKeyConstraintAbstract):
                if isinstance(c, ForeignKey):
                    cls.__meta__.foreign_keys.append(k)
                    c.tbl_k = "%s_%s" % (cls.__name__.lower(), k)
                cls.__meta__.relationships.append(k)
            elif isinstance(c, UniqueKey):
                c.tbl_k = "%s_%s" % (cls.__name__.lower(), k)
                cls.__meta__.unique_keys.append(k)
            elif isinstance(c, IndexKey):
                c.tbl_k = "%s_%s" % (cls.__name__.lower(), k)
                cls.__meta__.index_keys.append(k)
        elif isinstance(c, DbFunctionAbstract):
            if getattr(c, 'is_caption_key', False):
                if cls.__meta__.caption_key is not None:
                    raise Exception("'is_caption_key' might be set for only one column!")
                cls.__meta__.caption_key = k
        c.on_declare()

    @property
    def table(cls):
        tablename = cls.__meta__.tablename or str(cls.__name__).lower()
        return tablename if not cls.__meta__.prefix else "%s_%s" % (cls.__meta__.prefix, tablename)

    def __settemplatedattr__(cls, key, value):
        type.__setattr__(cls, key, value)
        if key.startswith('__') and key.endswith('__'):
            k_meta_attr = key[2:-2]
            if hasattr(cls.__meta__, k_meta_attr):
                if k_meta_attr in cls.__meta__.PROTECTED:
                    raise OrmModelDeclarationError("Cannot declare '%s' using meta-maps!" % key)
                setattr(cls.__meta__, k_meta_attr, value)
            return
        cls.__initattr__(key)
        c = type.__getattribute__(cls, key)
        c.from_template()
        c.on_model_declared()

    def __setattr__(cls, key, value):
        type.__setattr__(cls, key, value)
        if key.startswith('__') and key.endswith('__'):
            k_meta_attr = key[2:-2]
            if hasattr(cls.__meta__, k_meta_attr):
                if k_meta_attr in cls.__meta__.PROTECTED:
                    raise OrmModelDeclarationError("Cannot declare '%s' using meta-maps!" % key)
                setattr(cls.__meta__, k_meta_attr, value)
            return
        cls.__initattr__(key)
        c = type.__getattribute__(cls, key)
        c.on_model_declared()

    def __setattrabs__(cls, k, v):
        pass

    def _delete_by_model(self, *args, **kwargs):
        from ..request import OrmDeleteRequest
        request = OrmDeleteRequest(self, *args, **kwargs)
        return request.go()

    def __getattribute__(self, item):
        if item == 'delete':
            return type.__getattribute__(self, '_delete_by_model')
        return type.__getattribute__(self, item)


class OrmModelTemplateMeta(type):
    def __init__(cls, name, bases, clsdict):
        super(OrmModelTemplateMeta, cls).__init__(name, bases, clsdict)
        mro_ = cls.mro()
        if len(mro_) <= 2:
            return
        cls_keys_ = dir(cls)
        for k in cls_keys_:
            if k.startswith('__') and k.endswith('__'):
                continue
            c = type.__getattribute__(cls, k)
            if not isinstance(c, AttributeAbstract):
                continue
            c.belongs_to_template = True
            c.model = cls
            c.model_k = k

    def __setattr__(cls, key, value):
        if isinstance(value, AttributeAbstract):
            value.belongs_to_template = True
            value.model = cls
            value.model_k = key
        type.__setattr__(cls, key, value)
        used_in_models = mapper.get_template_models(cls)
        if used_in_models:
            for model_name in used_in_models:
                model = mapper.get_model_by_name(model_name)
                if key.startswith('__') and key.endswith('__'):
                    k_meta_attr = key[2:-2]
                    if hasattr(model.__meta__, k_meta_attr) and not hasattr(model, key):
                        setattr(model.__meta__, k_meta_attr, value)
                        setattr(model, key, value)
                    continue
                if not hasattr(model, key):
                    model.__settemplatedattr__(key, value)
                    continue
                c = getattr(model, key)
                if not isinstance(c, AttributeAbstract):
                    continue
                if c.template_model is None or c.template_model != cls:
                    continue
                model.__settemplatedattr__(key, value)


class OrmViewMeta(type):
    def __init__(cls, name, bases, clsdict):
        from .base import OrmModel

        super(OrmViewMeta, cls).__init__(name, bases, clsdict)
        mro_ = cls.mro()
        if len(mro_) <= 2:
            return

        keys = dir(cls)
        if '__model__' not in keys:
            raise OrmModelDeclarationError(
                "OrmView requies attribute '__model__' to be set to the corresponding base Model!"
            )
        base_model = type.__getattribute__(cls, '__model__')
        if not inspect.isclass(base_model) or not issubclass(base_model, OrmModel):
            raise OrmModelDeclarationError(
                "OrmView requies attribute '__model__' to be set to the corresponding base Model!"
            )
        type.__setattr__(cls, '__joins__', list())
        type.__setattr__(cls, '__attrs__', list())

        # First initializing joins because them needed for correct attributes initilization
        for k in keys:
            if k.startswith('__') and k.endswith('__'):
                continue
            if k in ('where', 'having', 'order', 'group'):
                continue
            c = type.__getattribute__(cls, k)
            if not isinstance(c, ViewJoin):
                continue
            cls.__initattr__(k)

        # Initializing attributes
        for k in keys:
            if k.startswith('__') and k.endswith('__'):
                continue
            if k in ('where', 'having', 'order', 'group'):
                continue
            c = type.__getattribute__(cls, k)
            if isinstance(c, ViewJoin):
                continue
            cls.__initattr__(k)

    def __regattr__(cls, k):
        attrs = type.__getattribute__(cls, '__attrs__')
        joins = type.__getattribute__(cls, '__joins__')
        if k in joins:
            i = joins.index(k)
            del(joins[i])
        c = type.__getattribute__(cls, k)
        c.model = cls
        c.model_k = k
        if isinstance(c, AttributeView):
            c.on_view_metainit()
        if k in attrs:
            return
        attrs.append(k)

    def __regjoin__(cls, k):
        attrs = type.__getattribute__(cls, '__attrs__')
        joins = type.__getattribute__(cls, '__joins__')
        if k in attrs:
            i = attrs.index(k)
            del (attrs[i])
        c = type.__getattribute__(cls, k)
        c.model = cls
        c.model_k = k
        if k in joins:
            return
        joins.append(k)

    def __unreg__(cls, k):
        attrs = type.__getattribute__(cls, '__attrs__')
        joins = type.__getattribute__(cls, '__joins__')
        if k in attrs:
            i = attrs.index(k)
            del (attrs[i])
        if k in joins:
            i = joins.index(k)
            del (joins[i])

    def __initattr__(cls, k):
        from .base import OrmModel
        c = type.__getattribute__(cls, k)
        if isinstance(c, AttributeView):
            cls.__regattr__(k)
            return
        if isinstance(c, ViewJoin):
            cls.__regjoin__(k)
            return
        if isinstance(c, (tuple, list)) and len(c) == 2:
            model_ = c[0]
            k_ = c[1]
            if isinstance(model_, str) and isinstance(k_, str):
                if not mapper.has_model(model_):
                    cls.__unreg__(k)
                    return
                type.__setattr__(cls, k, AttributeView(model_, k_))
                cls.__regattr__(k)
                return
            elif inspect.isclass(model_) and issubclass(model_, OrmModel) and isinstance(k_, str):
                type.__setattr__(cls, k, AttributeView(model_.__name__, k_))
                cls.__regattr__(k)
                return
            else:
                cls.__unreg__(k)
                return
        elif isinstance(c, AttributeAbstract):
            model_ = c.model
            if model_ != type.__getattribute__(cls, '__model__'):
                raise OrmModelDeclarationError(
                    "OrmView requires attributes to be the same Model as base one (set using '__model__"
                    " property), or to be an attribute of one of ViewJoins (using AttributeView class and"
                    " ViewJoin's attribute name as first argument)!"
                )
            k_ = c.model_k
            type.__setattr__(cls, k, AttributeView(model_.__name__, k_))
            cls.__regattr__(k)
            return
        elif isinstance(c, str) and '.' in c and c.count('.') == 1:
            model_, k_ = c.split('.')
            if not mapper.has_model(model_):
                cls.__unreg__(k)
                return
            type.__setattr__(cls, k, AttributeView(model_, k_))
            cls.__regattr__(k)
            return
        cls.__unreg__(k)

    def __setattr__(self, key, value):
        super(OrmViewMeta, self).__setattr__(key, value)
        if key.startswith('__') and key.endswith('__'):
            return
        if key in ('where', 'having', 'order', 'group'):
            return
        self.__initattr__(key)

    def __delattr__(self, key):
        super(OrmViewMeta, self).__delattr__(key)
        self.__unreg__(key)

