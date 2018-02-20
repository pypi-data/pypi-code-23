from rest_framework import serializers
from .models import City, State, Country, CountryCode, Location


class CountryCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CountryCode
        fields = '__all__'


class CountrySerializer(serializers.ModelSerializer):
    code = CountryCodeSerializer(many=False)

    class Meta:
        model = Country
        fields = '__all__'


class StateSerializer(serializers.ModelSerializer):
    country = CountrySerializer(many=False)

    class Meta:
        model = State
        fields = '__all__'


class CitySerializer(serializers.ModelSerializer):
    state = StateSerializer(many=False)

    class Meta:
        model = City
        fields = '__all__'


class LocationSerializer(serializers.ModelSerializer):
    city = CitySerializer(many=False)

    class Meta:
        model = Location
        fields = '__all__'
