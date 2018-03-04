# -*- coding: utf-8 -*-

from octo_drf.apps.base.serializers import BaseModelSerializer
from rest_framework import serializers
from .models import StaticBlock


class StaticBlockSerializer(BaseModelSerializer):

    image_fields = ['image1', 'image2', 'image3', 'image4']

    class Meta:
        model = StaticBlock
        fields = ('pk', 'order', 'title', 'announce',
                  'content', 'is_published',
                  )

class StaticBlockCountSerializerMixin(serializers.ModelSerializer):

    count_static_blocks = serializers.SerializerMethodField()

    def get_count_static_blocks(self, instance):
        return self.queryset.get(id=instance.id).count_static_block