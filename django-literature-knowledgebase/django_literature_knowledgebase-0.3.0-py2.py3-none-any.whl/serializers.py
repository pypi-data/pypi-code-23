# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model

from genomix.fields import DisplayChoiceField, UserRelatedField
from rest_framework import serializers

from . import choices, models


class ArticleSerializer(serializers.ModelSerializer):
    """Serializer for Articles."""

    source = DisplayChoiceField(choices=choices.SOURCES)
    user = UserRelatedField(queryset=get_user_model().objects.all())

    class Meta:
        model = models.Article
        fields = (
            'id', 'source', 'identifier', 'active', 'description',
            'article_url', 'fetch_url', 'summary_url',
            'user', 'created', 'modified',
        )
