# coding: utf-8
import copy
from rest_framework import serializers
from django_tilestache.polymorfic import (PolymorficSerializer,
                                          PolySerializer,)
from django_tilestache.models import Layer


class BoundsSerializer(serializers.Serializer):

    low = serializers.IntegerField(
        min_value=1,
        max_value=31
    )

    high = serializers.IntegerField(
        min_value=1,
        max_value=31
    )

    north = serializers.FloatField()

    west = serializers.FloatField()

    south = serializers.FloatField()

    east = serializers.FloatField()


class PreviewSerializer(serializers.Serializer):

    lat = serializers.FloatField(
        required=True
    )

    lon = serializers.FloatField(
        required=True
    )

    zoom = serializers.IntegerField(
        default=10
    )

    ext = serializers.CharField(
        max_length=16,
        default='png'
    )


class MetaTileSerializer(serializers.Serializer):

    rows = serializers.IntegerField(
        required=True,
        min_value=1
    )

    columns = serializers.IntegerField(
        required=True,
        min_value=1
    )

    buffer = serializers.IntegerField(
        required=True,
        min_value=0
    )


class BaseProviderSerializer(serializers.Serializer):

    name = serializers.CharField(max_length=64)

    def create(self, validated_data):
        self.data.update(validated_data)
        return self.data


class ProxyProviderSerializer(BaseProviderSerializer):

    url = serializers.CharField(
        max_length=512,
        required=True
    )

    timeout = serializers.IntegerField(
        required=False,
        min_value=1,
        max_value=60,
        allow_null=True
    )

    class Meta:
        fields = '__all__'


class ExternalProviderSerializer(BaseProviderSerializer):

    name = None  # removing the name fields, not needed

    klass = serializers.CharField(
        max_length=256,
        required=True,
        source='class'
    )

    kwargs = serializers.JSONField(
        required=False,
        allow_null=True
    )

    def _alias_field_name(self, data, original, changed):
        """
        this is a tremendous hack to maintain the
        attribute names on tilestache. external providers
        REQUIRE the name class, which is NOT a valid name
        for a DRF field
        """
        new_data = copy.deepcopy(data)
        if original in new_data:
            new_data[changed] = new_data[original]
            del new_data[original]
        return new_data

    def to_representation(self, obj):
        data = super(ExternalProviderSerializer, self).to_representation(obj)
        return self._alias_field_name(data, 'klass', 'class')

    def to_internal_value(self, data):
        data = self._alias_field_name(data, 'class', 'klass')
        return super(ExternalProviderSerializer, self).to_internal_value(data)

    class Meta:

        fields = ('klass', 'kwargs',)


class MapnikProviderSerializer(BaseProviderSerializer):

    mapfile = serializers.CharField(
        max_length=256,
        required=True
    )

    fonts = serializers.CharField(
        max_length=256,
        required=False,
        allow_null=True
    )

    scale_factor = serializers.FloatField(
        required=False,
        allow_null=True,
    )

    class Meta:

        fields = '__all__'


class VectorProviderSerializer(BaseProviderSerializer):

    driver = serializers.CharField(
        max_length=64,
        required=True
    )

    parameters = serializers.JSONField(
        required=True
    )

    properties = serializers.JSONField(
        required=False,
    )

    clipped = serializers.NullBooleanField(
        required=False,
    )

    projected = serializers.NullBooleanField(
        required=False,
    )

    precision = serializers.IntegerField(
        required=False,
        min_value=1,
        max_value=8
    )

    spacing = serializers.IntegerField(
        required=False
    )

    class Meta:
        fields = '__all__'


def can_serialize_vector(data, context):
    return 'name' in data and data['name'] == 'vector'


def can_serialize_proxy(data, context):
    return 'name' in data and data['name'] == 'proxy'


def can_serialize_mapnik(data, context):
    return 'name' in data and data['name'] == 'mapnik'


def can_serialize_external(data, context):
    return 'class' in data


class ProviderConfigSerializer(PolymorficSerializer):

    poly_serializers = (
        PolySerializer(ExternalProviderSerializer, can_serialize_external, can_serialize_external),
        PolySerializer(VectorProviderSerializer, can_serialize_vector, can_serialize_vector),
        PolySerializer(MapnikProviderSerializer, can_serialize_mapnik, can_serialize_mapnik),
        PolySerializer(ProxyProviderSerializer, can_serialize_proxy, can_serialize_proxy),
    )


class LayerSerializer(serializers.ModelSerializer):

    provider = ProviderConfigSerializer()

    metatile = MetaTileSerializer(
        required=False,
    )

    bounds = BoundsSerializer(
        required=False,
    )

    allowed_origin = serializers.CharField(
        max_length=256,
        required=False
    )

    preview = PreviewSerializer(
        required=False,
    )

    redirects = serializers.JSONField(
        required=False,
    )

    def create(self, validated_data):
        return Layer.objects.create(**validated_data)

    def update(self, instance, validated_data):

        nested_serializers = (
            ('provider', ProviderConfigSerializer),
            ('metatile', MetaTileSerializer),
            ('bounds', BoundsSerializer),
            ('preview', PreviewSerializer),
        )

        # this just iterates the nested serializers,
        # checks if there is data and it's valid.
        # if it's valid, set it back on the instance.
        # if it's not, it will raise an exception
        for key, serializer in nested_serializers:
            if key in validated_data:
                data = validated_data.pop(key)
                serializer = serializer(data=data)
                if serializer.is_valid(raise_exception=True):
                    setattr(instance, key, data)

        for k, v in validated_data.items():
            if hasattr(instance, k):
                setattr(instance, k, v)

        instance.save()
        return instance

    def _alias_field_name(self, data, original, changed):
        """
        this is a tremendous hack to maintain the
        attribute names on tilestache. external providers
        REQUIRE the name class, which is NOT a valid name
        for a DRF field
        """
        new_data = copy.deepcopy(data)
        if original in new_data:
            new_data[changed] = new_data[original]
            del new_data[original]
        return new_data

    def to_representation(self, obj):

        data = super(LayerSerializer, self).to_representation(obj)
        for k, v in data.items():
            if not v:
                del data[k]

        # this is here because we need allowed_origin to be allowed origin
        data = self._alias_field_name(data, 'cache_lifespan', 'cache lifespan')
        return self._alias_field_name(data, 'allowed_origin', 'allowed origin')

    class Meta:
        model = Layer
        fields = '__all__'
