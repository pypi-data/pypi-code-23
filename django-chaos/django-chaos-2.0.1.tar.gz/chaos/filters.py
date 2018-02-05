# coding: utf-8
from django.db.models import Q
import rest_framework_filters as filters
from rest_framework_filters.filterset import LOOKUP_SEP
from .models import (
    Entrepreneur,
    Enterprise,
    ProjectType,
    Project,
    TaskStatus,
    Task,
    Comment,
)
from datetime import datetime


class TagsFilter(filters.CharFilter):
    def filter(self, qs, value):
        if value:
            tags = [tag.strip() for tag in value.split(',')]
            qs = qs.filter(tags__name__in=tags).distinct()
        return qs


class EntrepreneurFilter(filters.FilterSet):

    class Meta:
        model = Entrepreneur
        fields = {
            'id': ['exact'],
            'name': ['exact', 'icontains'],
            'nickname': ['exact', 'icontains'],
            'document_number': ['exact', 'icontains'],
        }


class EnterpriseFilter(filters.FilterSet):

    entrepreneurs = filters.RelatedFilter(
        EntrepreneurFilter,
        field_name='entrepreneurs',
        queryset=Entrepreneur.objects.all()
    )

    class Meta:
        model = Enterprise
        fields = {
            'name': ['exact', 'startswith', 'icontains'],
            'description': ['icontains'],
        }


class ProjectTypeFilter(filters.FilterSet):

    class Meta:
        model = ProjectType
        fields = {
            'id': ['exact'],
            'code': ['exact', 'startswith', 'icontains'],
            'description': ['exact', 'startswith', 'icontains']
        }


class ProjectFilter(filters.FilterSet):

    class Meta:
        model = Project
        fields = {
            'id': ['exact'],
            'enterprise': ['exact'],
            'name': ['exact', 'startswith', 'icontains'],
            'type': ['exact'],
            'responsible': ['exact'],
            'description': ['icontains'],
        }


class TaskStatusFilter(filters.FilterSet):

    class Meta:
        model = TaskStatus
        fields = {
            'id': ['exact'],
            'code': ['exact', 'startswith', 'icontains'],
            'description': ['exact', 'startswith', 'icontains'],
            'is_system_status': ['exact'],
            'is_closing_status': ['exact']
        }


class TaskFilter(filters.FilterSet):

    start_date = filters.CharFilter(name='start_date', method='filter_start_date')
    end_date = filters.CharFilter(name='end_date', method='filter_end_date')
    root_task = filters.BooleanFilter(name='parent', method='filter_is_root_task')

    status = filters.RelatedFilter(
        TaskStatusFilter,
        name='status',
        queryset=TaskStatus.objects.all()
    )
    tags = TagsFilter(name="tags")

    def filter_start_date(self, qs, name, value):
        datetime_object = datetime.strptime(value, '%d/%m/%Y %H:%M')
        return qs.filter(Q(start_date__gte=datetime_object) | Q(end_date__gte=datetime_object))

    def filter_end_date(self, qs, name, value):
        datetime_object = datetime.strptime(value, '%d/%m/%Y %H:%M')
        return qs.filter(Q(end_date__lte=datetime_object) | Q(start_date__lte=datetime_object))

    def filter_is_root_task(self, qs, name, value):
        lookup = LOOKUP_SEP.join([name, 'isnull'])
        return qs.filter(**{lookup: value})

    class Meta:
        model = Task
        fields = {
            'id': ['exact'],
            'project': ['exact'],
            'root_task': ['exact'],
            'parent': ['exact'],
            'responsible': ['exact'],
            'status': ['exact'],
            'name': ['exact', 'startswith', 'icontains'],
            'description': ['icontains'],
        }


class CommentFilter(filters.FilterSet):

    class Meta:
        model = Comment
        fields = {
            'id': ['exact'],
            'created_by': ['exact'],
            'task': ['exact'],
            'text': ['icontains']
        }
