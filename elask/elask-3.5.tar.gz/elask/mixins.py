import math, json

from elask.manager import ESManager
from elasticsearch import Elasticsearch, helpers
from elasticsearch_dsl import A, Q, Search
from flask_restful import Api, Resource, abort, reqparse
from marshmallow import Schema


class CreateModelMixin(object):
    """
    Create a document instance.
    """
    def create(self, request):
        self.action = 'create'
        data = request.get_json()
        if hasattr(self, 'pre_save'):
            data = self.pre_save(request, data=data, mode='create')
        serializer = self.get_serializer_class()(strict=True)
        try:
            errors = serializer.validate(data)
        except Exception as e:
            return abort(400, message=e.messages)
        if errors.keys():
            return abort(400, message=errors)
        else:
            doc = self.model(
                meta={'index': self.index},
                **serializer.load(data).data
            )
        doc.save()
        if hasattr(self, 'post_save'):
            doc = self.post_save(request, doc=doc, mode='create')
        serializer = self.get_serializer_class()()
        result = doc.to_dict()
        result.update({'id': doc._id})
        data = serializer.dump(result)
        return data


class ListModelMixin(object):
    """
    Listing documents.
    """
    def list(self, request, *args, **kwargs):
        params = request.args.copy()
        self.action = 'list'
        # Get page_size
        try:
            page_size = int(params.get('page_size', 100))
        except Exception as general_exception:
            page_size = 100
        # Get page
        try:
            page = int(params.get('page', 1))
        except Exception as general_exception:
            page = 1
        # Get Sort
        try:
            sort = params.get('sort', None)
        except:
            sort = None

        client = ESManager().client
        search = Search(
            index=self.index,
            doc_type=self.doc_type
        ).using(client)
        _from = abs(page - 1) * page_size
        size = page * page_size
        if hasattr(self, 'filtering'):
            criteria = self.filtering(params)
            search_instance = search.query(criteria)
        else:
            search_instance = search.query()
        if sort is None:
            data = search_instance[_from:size].execute().to_dict()['hits']
        else:
            data = search_instance.sort(sort)[_from:size].execute().to_dict()['hits']
        total = data['total']
        end_num = (page) * page_size
        start_num = (abs(page - 1) * page_size) + 1
        next_page = page + 1
        if end_num > total:
            end_num = total
            next_page = None
        if page == 1:
            previous_page = None
        else:
            previous_page = page - 1
        results = []
        for item in data['hits']:
            temp = item['_source']
            temp.update({'id': item['_id']})
            results.append(temp)      
        serializer = self.get_serializer_class()(many=True)
        data = serializer.dumps(results)
        output = {
            'current_page': page,
            'page_size': page_size,
            'start_num': start_num,
            'end_num': end_num,
            'results': json.loads(data.data),
            'total_num': total,
            'previous_page': previous_page,
            'next_page': next_page,
            'last_page': int(math.ceil(total / float(page_size)))
        }
        return output


class RetrieveModelMixin(object):
    """
    Retrieve a document instance.
    """
    lookup_field = 'id'

    @property
    def _lookup_field(self):
        return getattr(self, 'lookup_field', 'id')

    def retrieve(self, request, *args, **kwargs):
        self.action = 'retrieve'
        params = request.args.copy()
        pk = kwargs.get(self._lookup_field)
        try:
            doc = self.model.get(**{
                'index':self.index,
                self.lookup_field:pk
            })
        except Exception as ex:
            return abort(404, message="Record Not Found")
        result = doc.to_dict()
        result.update({'id': doc._id})
        serializer = self.get_serializer_class()()
        data = serializer.dump(result)
        return data


class UpdateModelMixin(object):
    """
    Update a document instance.
    """
    lookup_field = 'id'

    @property
    def _lookup_field(self):
        return getattr(self, 'lookup_field', 'id')

    def update(self, request, *args, **kwargs):
        self.action = 'update'
        data = request.get_json()
        pk = kwargs.get(self._lookup_field, None)
        try:
            doc = self.model.get(**{
                'index':self.index,
                self.lookup_field:pk
            })
        except Exception as ex:
            return abort(404, message="Record Not Found")
        if hasattr(self, 'pre_save'):
            data = self.pre_save(request, data=data, mode='update')
        doc.update(**data)
        doc.save()
        if hasattr(self, 'post_save'):
            doc = self.post_save(request, doc=doc, mode='update')
        result = doc.to_dict()
        result.update({'id': doc._id})
        serializer = self.get_serializer_class()()
        data = serializer.dump(result)
        return data


class DestroyModelMixin(object):
    """
    Destroy a document
    """
    lookup_field = 'id'

    @property
    def _lookup_field(self):
        return getattr(self, 'lookup_field', 'id')

    def destroy(self, request, *args, **kwargs):
        self.action = 'destroy'
        pk = kwargs.get(self._lookup_field, None)
        try:
            doc = self.model.get(**{
                'index':self.index,
                self.lookup_field:pk
            })
        except Exception as ex:
            return abort(404, message="Record Not Found")
        if hasattr(self, 'pre_delete'):
            self.pre_delete(doc=doc)
        self.perform_destroy(doc)
        if hasattr(self, 'post_delete'):
            self.post_delete(doc=doc)
        return "Deleted Successfully"

    def perform_destroy(self, doc):
        doc.delete()
