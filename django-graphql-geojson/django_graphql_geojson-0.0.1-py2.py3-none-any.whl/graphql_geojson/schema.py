import graphene
from countries import models
from graphene import relay
from graphene_django.filter import DjangoFilterConnectionField

from .types import GeoJSONObjectType


class CountryNode(GeoJSONObjectType):

    class Meta:
        model = models.Country
        interfaces = [relay.Node]
        geojson_field = 'location'


class Query(graphene.ObjectType):
    countries = DjangoFilterConnectionField(CountryNode)

    def resolve_countries(self, info, **kwargs):
        return models.Country.objects.all()


schema = graphene.Schema(query=Query)
