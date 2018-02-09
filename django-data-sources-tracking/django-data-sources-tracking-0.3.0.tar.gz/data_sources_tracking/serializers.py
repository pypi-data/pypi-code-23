# -*- coding: utf-8 -*-
from genomix.fields import DisplayChoiceField
from rest_framework import serializers

from . import choices, models


class FileSerializer(serializers.ModelSerializer):
    """Serializer for Files."""

    type = DisplayChoiceField(choices=choices.FILE_TYPES)

    class Meta:
        model = models.File
        fields = (
            'id', 'name', 'description', 'url', 'path',
            'type', 'relative_path',
            'active', 'created', 'modified',
        )
