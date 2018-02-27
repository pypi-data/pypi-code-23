from fortnum import Fortnum


class ApiQuery(Fortnum):
    def get_queryset(self, model, language, key=None):
        raise NotImplementedError()


class APIQueries(Fortnum):
    item_class = ApiQuery

    class all(ApiQuery):
        def get_queryset(self, model, language, key=None):
            return model.objects.all()

    class roots(ApiQuery):
        def get_queryset(self, model, language, key=None):
            return model.objects.root_nodes()

    class children(ApiQuery):
        def get_queryset(self, model, language, key=None):
            concept = model.objects.get(key=key, translate=False)
            return concept.get_children(translate=True)

    class family(ApiQuery):
        def get_queryset(self, model, language, key=None):
            concept = model.objects.get(key=key, translate=False)
            return concept.get_family(translate=True)

    class descendants(ApiQuery):
        def get_queryset(self, model, language, key=None):
            concept = model.objects.get(key=key, translate=False)
            return concept.get_descendants(translate=True)