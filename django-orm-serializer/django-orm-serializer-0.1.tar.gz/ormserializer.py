from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.fields.files import ImageFieldFile, FileField, ImageField
from django.db.models.fields import DateField, DateTimeField, TimeField
from django.db.models.query import QuerySet
from django.db.models import Avg, ForeignKey
from itertools import chain
import datetime


class Serialize(object):
    """docstring for Serialize."""
    def __init__(self):
        super(Serialize, self).__init__()

    def serialize_to_dict(self, instance, cur_depth=1, max_depth=2):
        from django.db.models.fields.related import ManyToManyField
        if instance is None:
            return None
        #print(type(instance))
        metas = instance._meta
        data = {}

        for f in chain(metas.concrete_fields, metas.many_to_many):
            if isinstance(f, ManyToManyField):
                if cur_depth < max_depth:
                    data[str(f.name)] = [self.serialize_to_dict(tmp_object, cur_depth=cur_depth + 1, max_depth=max_depth) for tmp_object in f.value_from_object(instance)]
                else:

                    data[str(f.name)] = [tmp_object.id for tmp_object in f.value_from_object(instance)]

            elif isinstance(f, ForeignKey):
                if cur_depth < max_depth:
                    data[str(f.name)] = self.serialize_to_dict(getattr(instance, f.name, False), cur_depth + 1, max_depth=max_depth)
                else:
                    data[str(f.name)] = getattr(getattr(instance, f.name, False), "id", False)
            else:
                try:
                    #data[str(f.name)] = model_to_dict(getattr(instance, f.name, False))
                    #for n in data[str(f.name)]:
                    nv = getattr(instance, f.name, False)
                    typelist = (ImageField, ImageFieldFile, DateTimeField, DateField, TimeField, FileField)
                    if type(f) in typelist:
                        if str(nv) == "":
                            data[str(f.name)] = None
                        else:
                            data[str(f.name)] = str(nv)
                    elif type(f) == QuerySet:
                        data[str(f.name)] = self.serialize(nv)
                    else:
                        data[str(f.name)] = nv
                    #cur_depth += 1
                except Exception as e:
                    data[str(f.name)] = str(getattr(instance, f.name, False))
        return data

    def serialize_annotate(self, qset, groupfield, lesson_search_session=False, max_depth=2):
        ret = []
        try:
            for q in qset:
                dc = self.serialize_to_dict(q, max_depth=max_depth)
                dc[groupfield] = getattr(q, groupfield, False)
                if(lesson_search_session):
                    dc["upcoming_session"] = self.serialize_to_dict(q.edusession_lesson.filter(status='1', lessontype__slug="public", start_at__gte = datetime.datetime.now()).order_by('start_at').first())
                ret.append(dc.copy())
            return ret
        # except:
        except Exception as e:
            print(e)
            raise

    def serialize_annotate2(self, qset, groupfields):
        ret = []
        try:
            for q in qset:
                #print(q._meta.get_field("avg_reviews").verbose_name)
                dc = self.serialize_to_dict(q)
                for groupfield in groupfields:
                    dc[groupfield] = getattr(q, groupfield, False)
                ret.append(dc.copy())
            return ret
        except:
            raise

    def serialize(self, qset, max_depth=2):
        ret = []
        try:
            for q in qset:
                #print(q._meta.get_field("avg_reviews").verbose_name)
                ret.append(self.serialize_to_dict(q, max_depth=max_depth))
            return ret
        except:
            raise
