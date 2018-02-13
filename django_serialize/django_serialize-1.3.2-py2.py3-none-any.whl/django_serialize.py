import logging
import django
import decimal
import datetime
import copy

from packaging import version

logger = logging.getLogger(__name__)

DJANGO_VER = version.parse(django.get_version())
if DJANGO_VER < version.parse('1.9'):
    MANY_TO_ONE_REL_TYPE = 'django.db.models.fields.related.ManyToOneRel'
    RELATED_MGR_TYPE = 'django.db.models.fields.related.RelatedManager'
elif DJANGO_VER >= version.parse('1.9'):
    MANY_TO_ONE_REL_TYPE = 'django.db.models.fields.reverse_related.ManyToOneRel'
    RELATED_MGR_TYPE = 'django.db.models.fields.related_descriptors.RelatedManager'
else:
    raise Exception('should never be here')
ONE_TO_ONE_TYPE = 'django.db.models.fields.related.OneToOneField'


def model_to_dict(
        model_obj,
        deep=True,
        include_paths={},
        exclude_paths={},
        path=[],
        type_converters={},
):
    if not model_obj:
        return None
    RELATED_OBJ_TYPE = "django.db.models.related.RelatedObject"
    RELATED_TYPES = [RELATED_OBJ_TYPE, MANY_TO_ONE_REL_TYPE]

    model_as_dict = copy.copy(model_obj.__dict__)
    model_fieldnames = [fld.name for fld in model_obj._meta.get_fields()]
    def should_exclude_field(_fieldname):
        return _fieldname not in model_fieldnames or \
            include_paths and \
            ((isinstance(include_paths, list) and _fieldname not in include_paths) or \
             (isinstance(include_paths, dict) and _fieldname not in include_paths.keys()))
    exclusion_fieldname_list = [fieldname for fieldname in model_as_dict.keys() if should_exclude_field(fieldname)]
    model_as_dict = exclude_from_dict(model_as_dict, exclusion_fieldname_list)
    # logger.debug(pprint.pformat({
    #     'path': path,
    #     'include_paths': include_paths,
    #     'model_as_dict': model_as_dict,
    # }))
    for field_name in model_fieldnames:
        curr_path = path + [field_name]
        next_include_paths = {}
        if include_paths:
            can_recurse = False
            if isinstance(include_paths, dict):
                next_include_paths = include_paths.get(field_name)
                can_recurse = bool(next_include_paths)
            elif isinstance(include_paths, list):
                next_include_paths = True
                can_recurse = field_name in include_paths
            elif isinstance(include_paths, bool):
                can_recurse = False
            else:
                raise Exception("unrecognized include path type of '%s'" % type(include_paths))
            if not can_recurse:
                continue
        next_exclude_paths = exclude_paths.get(field_name, {})
        if isinstance(next_exclude_paths, bool):
            if next_exclude_paths:
                continue
        field = model_obj._meta.get_field(field_name)
        try:
            field_value = model_obj.__getattribute__(field_name)
        except AttributeError:
            continue
        # logger.debug(pprint.pformat({
        #     'path': curr_path,
        #     'field_type': class_fullname(type(field)),
        #     'include_paths': include_paths,
        #     'next_include_paths': next_include_paths,
        # }))
        # logger.debug("path = %s; field type = %s" % (curr_path, class_fullname(type(field))))
        type_converter = type_converters.get(class_fullname(type(field_value)))
        if deep and class_fullname(type(field)) in RELATED_TYPES and class_fullname(type(field_value)) == RELATED_MGR_TYPE:
            model_as_dict[field_name] = [
                model_to_dict(
                    child,
                    path=curr_path,
                    include_paths=next_include_paths,
                    exclude_paths=next_exclude_paths,
                ) for child in field_value.all()]
        elif deep and class_fullname(type(field)) == ONE_TO_ONE_TYPE and not isinstance(field_value, int):
            # F. Henard 1/26/15 - Checking for int because in django 1.7 the id of the one-to-one relation is of type OneToOneField
            model_as_dict[field_name] = model_to_dict(
                field_value,
                path=curr_path,
                include_paths=next_include_paths,
                exclude_paths=next_exclude_paths,
            )
        elif deep and class_fullname(type(field)) == 'django.db.models.fields.related.ForeignKey' and include_paths and include_paths.get(field_name):
            # only include a ForeignKey relationship if it has been explicitly requested in the
            # include paths.
            # line below: don't recurse the reverse relationship
            exclude_reverse = {field.rel.name: True}
            next_exclude_paths = next_exclude_paths.update(exclude_reverse) if next_exclude_paths else exclude_reverse
            model_as_dict[field_name] = model_to_dict(
                field_value,
                path=curr_path,
                include_paths=next_include_paths,
                exclude_paths={field.rel.name: True},
            )
        elif isinstance(field_value, decimal.Decimal):
            model_as_dict[field_name] = float(field_value)
        elif type(field_value) == datetime.datetime:
            supplied_dt_cvtr = type_converters.get('datetime.datetime')
            model_as_dict[field_name] = supplied_dt_cvtr(field_value) if supplied_dt_cvtr else field_value.isoformat()
        elif type_converter:
            model_as_dict[field_name] = type_converter(field_value)
    return model_as_dict


# Save a model object from a json string
def deep_deserialize(json_str, model_obj_type):
    import six
    import json
    if json_str is None or not isinstance(json_str, six.string_types) or len(json_str) == 0:
        return None
    return deep_deserialize_from_dict(json.loads(json_str), model_obj_type)


# Save a model object from a dictionary object
def deep_deserialize_from_dict(dikt, model_obj_type):

    def recursive_delete(obj_to_delete, parent_fk_field_name):
        for field in obj_to_delete._meta.get_fields():
            if class_fullname(type(field)) == "django.db.models.related.RelatedObject":
                for child in obj_to_delete.__getattribute__(field.name).all():
                    recursive_delete(child, field.field.name)
        obj_to_delete.delete()

    if not dikt:
        return None
    # logger.debug("model obj type = %s" % model_obj_type)
    # import pprint; logger.debug("before: %s" % pprint.pformat(dikt))
    FOREIGN_KEY_FIELD_TYPE = "django.db.models.fields.related.ForeignKey"
    CHILD_FIELD_TYPE = "django.db.models.related.RelatedObject"
    CHILD_FIELD_TYPES = [
        CHILD_FIELD_TYPE,
        MANY_TO_ONE_REL_TYPE,
    ]
    DATE_TIME_FIELD_TYPE = "django.db.models.fields.DateTimeField"
    DECIMAL_FIELD = "django.db.models.fields.DecimalField"
    model_fields = model_obj_type._meta.get_fields()
    # dikt_copy = copy.copy(dikt)
    # for input_field_name in dikt_copy.keys():
    #     # delete all fields in input dict that don't exist in the model
    #     if input_field_name not in [f.name for f in model_fields]:
    #         del dikt_copy[input_field_name]
    dikt_copy = {}
    model_field_names = [f.name for f in model_fields]
    for input_field_name in dikt:
        if input_field_name in model_field_names:
            dikt_copy[input_field_name] = dikt[input_field_name]
    child_fields = []
    for field in model_fields:
        field_type_str = class_fullname(type(field))
        # logger.debug('field_type_str = %s' % field_type_str)
        if field.name in dikt_copy.keys():
            if field_type_str == FOREIGN_KEY_FIELD_TYPE:
                if field.name.endswith("_id") and field.name[:-len("_id")] in dikt_copy.keys():
                    # as of django 1.7 the fk id field is included
                    del dikt_copy[field.name]
                else:
                    dikt_copy[field.name] = field.related_model.objects.get(pk=dikt_copy[field.name])
            elif field_type_str == ONE_TO_ONE_TYPE:
                oto_child_obj = deep_deserialize_from_dict(copy.deepcopy(dikt[field.name]), field.related_model)
                dikt_copy[field.name] = oto_child_obj
            elif field_type_str in CHILD_FIELD_TYPES:
                child_fields.append(field)
                del dikt_copy[field.name]
            elif field_type_str == DATE_TIME_FIELD_TYPE and field.auto_now_add and dikt_copy[field.name] is None:
                del dikt_copy[field.name]
            elif field_type_str == DECIMAL_FIELD and dikt_copy[field.name]:
                # cast floats to str for decimal field
                dikt_copy[field.name] = decimal.Decimal(str(dikt_copy[field.name]))
    # import pprint; logger.debug("after: %s" % pprint.pformat(dikt_copy))
    if "id" in dikt_copy.keys() and dikt_copy["id"] is not None:
        matching_instances = model_obj_type.objects.filter(id=dikt_copy["id"])
        if matching_instances.count() != 1:
            raise Exception("There should be one instance of type: %s id: %s, there are %s" % (model_obj_type, dikt_copy["id"], matching_instances.count()))
        matching_instances.update(**dikt_copy)
        instance = matching_instances.all()[0]
    else:
        instance = model_obj_type(**dikt_copy)
    # try:
    instance.clean()
    instance.save()
    # except IntegrityError, ie:
    #     raise
    # logger.debug("child fields = %s"%child_fields
    for child_field in child_fields:
        child_field_name = child_field.get_accessor_name()
        old_children = instance.__getattribute__(child_field_name).all()
        old_children_ids = set([child.id for child in old_children])
        new_children_ids = set([child_dikt.get("id", None) for child_dikt in dikt[child_field_name]])
        ids_diff = old_children_ids - new_children_ids
        for old_child in old_children:
            if old_child.id in ids_diff:
                recursive_delete(old_child, child_field.field.name)
        for new_child_dict in dikt[child_field_name]:
            # logger.debug("recursing into %s"%child_field.get_accessor_name()
            if child_field.field.name not in new_child_dict.keys() or new_child_dict[child_field.field.name] is None:
                new_child_dict[child_field.field.name] = instance.id
            deep_deserialize_from_dict(copy.deepcopy(new_child_dict), child_field.related_model)
    return instance


def exclude_from_dict(dikt, keys_to_exclude):
    import copy
    result = copy.deepcopy(dikt)
    for key_to_exclude in keys_to_exclude:
        if key_to_exclude in result:
            del result[key_to_exclude]
    return result


def class_fullname(clazz):
    return clazz.__module__ + "." + clazz.__name__
