# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from . import models
from rest_framework import serializers
from django.contrib.auth.models import User
headers = {'content-type': 'application/json'}


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Tag
        fields = ('id', 'name')

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = ('id', 'name')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')

class PostSerializer(serializers.ModelSerializer):
    # publisher = UserSerializer()
    class Meta:
        model = models.Post
        fields = ('id', 'title', 'abstract', 'raw', 'content', 'attachment',
                  'update_time', 'pub_time', 'tags', 'categories', 'publisher', 'is_draft',
                  'keyword', 'cover', 'degree', 'source', 'reserve_one', 'reserve_two')

class PostDetailSerializer(PostSerializer):
    tags = TagSerializer(many=True)
    categories = CategorySerializer(many=True)
    publisher = UserSerializer()





