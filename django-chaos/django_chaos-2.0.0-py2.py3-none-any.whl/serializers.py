# coding: utf-8
from collections import OrderedDict
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.reverse import reverse
from taggit_serializer.serializers import (
    TagListSerializerField,
    TaggitSerializer
)
from file_context.serializers import (
    FilesMixInSerializer,
)
from common.serializers import LinkSerializer
from .models import (
    Entrepreneur,
    Enterprise,
    ProjectType,
    Project,
    TaskStatus,
    Task,
    TaskAttachment,
    Reminder,
    Comment,
)
User = get_user_model()


class EntrepreneurAutoCompleteSerializer(serializers.ModelSerializer):

    """Auto complete serializer"""

    class Meta:
        model = Entrepreneur
        fields = (
            'id',
            'name'
        )


class EnterpriseSerializer(LinkSerializer,
                           FilesMixInSerializer):

    entrepreneurs = serializers.SerializerMethodField()
    project_count = serializers.SerializerMethodField()
    created_by = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    def get_entrepreneurs(self, obj):
        return [{'id': e.id, 'name': e.name} for e in obj.entrepreneurs.all()]

    def get_project_count(self, obj):
        return obj.projects.all().count()

    def get_links(self, obj):
        request = self.context.get('request')
        detailURL = reverse('project-detail', kwargs={'pk': obj.pk}, request=request)
        projectsURL = reverse('project-list', request=request) + '?enterprise={0}'.format(obj.pk)
        return OrderedDict([
            ('self', detailURL),
            ('projects', projectsURL),
        ])

    class Meta:

        model = Enterprise
        fields = (
            'id',
            'created_by',
            'date_created',
            'date_updated',
            'name',
            'description',
            'entrepreneurs',
            'files',
            'links',
            'project_count',
            'geometry',
        )
        extra_kwargs = {
            'projects': {'read_only': True}
        }


class EntrepreneurSerializer(LinkSerializer,
                             FilesMixInSerializer):

    enterprises = EnterpriseSerializer(many=True, read_only=True)

    created_by = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    def get_links(self, obj):
        request = self.context.get('request')
        detailURL = reverse('entrepreneur-detail', kwargs={'pk': obj.pk}, request=request)  # noqa
        return OrderedDict([
            ('self', detailURL),
        ])

    class Meta:
        model = Entrepreneur
        fields = (
            'id',
            'created_by',
            'date_created',
            'date_updated',
            'name',
            'nickname',
            'document_number',
            'description',
            'enterprises',
            'files',
            'links'
        )


class ProjectTypeSerializer(LinkSerializer):
    created_by = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:

        model = ProjectType
        fields = (
            'id',
            'created_by',
            'date_created',
            'date_updated',
            'code',
            'description',
        )


class ProjectSerializer(TaggitSerializer,
                        LinkSerializer,
                        FilesMixInSerializer):

    score = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    type_name = serializers.SerializerMethodField()
    responsible_name = serializers.SerializerMethodField()
    enterprise_name = serializers.SerializerMethodField()
    created_by = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    def get_score(self, obj):
        return obj.score

    def get_responsible_name(self, obj):
        if obj.responsible:
            return obj.responsible.get_username()
        else:
            return ''

    def get_type_name(self, obj):
        return obj.type.code

    def get_full_name(self, obj):
        return obj.full_name

    def get_enterprise_name(self, obj):

        if obj.enterprise:
            return obj.enterprise.name
        return ''

    def get_links(self, obj):

        request = self.context.get('request')
        detailURL = reverse('project-detail', kwargs={'pk': obj.pk}, request=request)
        tasksURL = reverse('task-list', request=request) + '?project={0}'.format(obj.pk)
        if obj.enterprise:
            enterpriseURL = reverse('enterprise-detail', kwargs={'pk': obj.enterprise.pk}, request=request)
        else:
            enterpriseURL = ''
        return OrderedDict([
            ('self', detailURL),
            ('enterprise', enterpriseURL),
            ('tasks', tasksURL),
            ('clone', detailURL + '/clone'),
            ('score', detailURL + '/score'),
        ])

    tags = TagListSerializerField()

    class Meta:

        model = Project
        fields = (
            'id',
            'created_by',
            'enterprise',
            'enterprise_name',
            'type',
            'type_name',
            'responsible',
            'responsible_name',
            'name',
            'full_name',
            'description',
            'template',
            'files',
            'tags',
            'links',
            'score',
            'geometry',
        )


class TaskStatusSerializer(LinkSerializer):
    created_by = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    def get_links(self, obj):

        request = self.context.get('request')
        detailUrl = reverse('task-status-detail', kwargs={'pk': obj.pk}, request=request)
        return {
            'self': detailUrl,
        }

    class Meta:
        model = TaskStatus
        fields = (
            'id',
            'created_by',
            'date_created',
            'date_updated',
            'code',
            'description',
            'color',
            'is_system_status',
            'is_closing_status',
            'links',
        )


class ReminderSerializer(LinkSerializer):

    user_name = serializers.SerializerMethodField()
    created_by = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    def get_links(self, obj):
        return {}

    def get_user_name(self, obj):
        if obj.user:
            return obj.user.get_username()
        else:
            return ''

    class Meta:
        model = Reminder
        fields = (
            'id',
            'created_by',
            'date_created',
            'date_updated',
            'content_type',
            'object_id',
            'user',
            'user_name',
            'is_recurring',
            'reminder_dates'
        )


class TaskSerializer(TaggitSerializer,
                     LinkSerializer,
                     FilesMixInSerializer):

    status_detail = serializers.SerializerMethodField()
    project_name = serializers.SerializerMethodField()
    responsible_name = serializers.SerializerMethodField()
    project_name = serializers.SerializerMethodField()
    parent_name = serializers.SerializerMethodField()

    created_by = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    def get_project_name(self, obj):
        if obj.project:
            return obj.project.full_name
        else:
            return ''

    def get_parent_name(self, obj):
        if obj.parent:
            return obj.parent.name
        return ''

    def get_responsible_name(self, obj):
        if obj.responsible:
            return obj.responsible.get_username()
        return ''

    def get_status_detail(self, obj):
        status = obj.status
        if not status:
            return {}
        return {
            'code': status.code,
            'color': status.color,
            'is_system_status': status.is_system_status,
            'is_closing_status': status.is_closing_status
        }

    def get_links(self, obj):

        request = self.context.get('request')
        detailUrl = reverse(
            'task-detail',
            kwargs={
                'pk': obj.pk
            },
            request=request
        )
        projectUrl = reverse(
            'project-detail',
            kwargs={
                'pk': obj.project_id
            },
            request=request
        )
        commentsUrl = reverse('comment-list', request=request) + '?task={0}'.format(obj.pk)
        return OrderedDict([
            ('self', detailUrl),
            ('project', projectUrl),
            ('comments', commentsUrl),
            ('change_status', detailUrl + '/change_status'),
            ('attach', detailUrl + '/attach'),
            ('detach', detailUrl + '/detach'),
            ('clone', detailUrl + '/clone'),
            ('score', detailUrl + '/score'),
            ('export', detailUrl + '/export'),
        ])

    tags = TagListSerializerField()

    class Meta:

        model = Task
        fields = (
            'id',
            'created_by',
            'date_created',
            'date_updated',
            'start_date',
            'end_date',
            'project',
            'project_name',
            'parent',
            'responsible',
            'responsible_name',
            'project_name',
            'parent_name',
            'status',
            'status_detail',
            'weight',
            'name',
            'description',
            'tags',
            'files',
            'links',
            'geometry'
        )


class CommentSerializer(LinkSerializer,
                        FilesMixInSerializer):

    author = serializers.SerializerMethodField()
    created_by = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    def get_author(self, obj):
        if obj.created_by:
            return obj.created_by.get_username()

    def get_links(self, obj):
        request = self.context.get('request')
        detailUrl = reverse(
            'comment-detail',
            kwargs={
                'pk': obj.pk
            },
            request=request
        )
        taskUrl = reverse(
            'task-detail',
            kwargs={
                'pk': obj.task_id
            },
            request=request
        )
        return OrderedDict([
            ('self', detailUrl),
            ('task', taskUrl),
        ])

    class Meta:
        model = Comment
        fields = (
            'id',
            'author',
            'created_by',
            'date_created',
            'date_updated',
            'task',
            'text',
            'files',
            'links'
        )


class TaskAttachmentSerializer(LinkSerializer):

    model_name = serializers.SerializerMethodField()
    created_by = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    def get_model_name(self, obj):
        return '{0}.{1}'.format(obj.content_type.app_label, obj.content_type.name)

    class Meta:
        model = TaskAttachment
        fields = (
            'id',
            'task',
            'created_by',
            'content_type',
            'object_id',
            'model_name'
        )


class TaskChangeSerializer(serializers.Serializer):

    task = TaskSerializer()
    initial_target = TaskSerializer()
    action = serializers.CharField(max_length=64)
    status = TaskStatusSerializer()


class ListAllocationSerializer(serializers.Serializer):

    """
    Serializer that allows you to control
    filter for allocations
    """

    project = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(),
        required=False
    )

    min_date = serializers.DateField(
        required=False
    )

    max_date = serializers.DateField(
        required=False
    )


class AllocationSerializer(serializers.Serializer):

    user = serializers.SerializerMethodField()
    user_id = serializers.SerializerMethodField()
    date_point = serializers.DateTimeField()
    tasks = TaskSerializer(many=True, read_only=True)
    weight = serializers.SerializerMethodField()

    def get_user(self, obj):
        if obj.user:
            return obj.user.get_username()
        else:
            return ''

    def get_user_id(self, obj):
        if obj.user:
            return obj.user.pk
        else:
            return ''

    def get_weight(self, obj):
        return obj.weight


class AttachDetachSerializer(serializers.Serializer):
    """
    Serializer that validates and helps
    to construct the required request data
    for attach and detach endpoints
    """

    model_name = serializers.CharField()
    model_id = serializers.IntegerField()

    class Meta:
        fields = '__all__'


class ChangeStatusSerializer(serializers.Serializer):

    """
    Serializer that validates and helps
    to construct the required request data
    for change-status endpoint
    """

    status = serializers.IntegerField()
    dry_run = serializers.BooleanField(required=False)

    class Meta:
        fields = '__all__'


class ProjectCloneSerializer(serializers.Serializer):

    new_name = serializers.CharField()
    new_enterprise = serializers.PrimaryKeyRelatedField(
        queryset=Enterprise.objects.all(),
        required=False,
        allow_null=True
    )
    new_type = serializers.PrimaryKeyRelatedField(
        queryset=ProjectType.objects.all(),
        required=False,
        allow_null=True
    )
    new_responsible = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        allow_null=True
    )
    new_date = serializers.DateTimeField(
        required=False,
        allow_null=True
    )
    new_status = serializers.PrimaryKeyRelatedField(
        queryset=TaskStatus.objects.all(),
        required=False,
        allow_null=True
    )
    keep_tasks = serializers.BooleanField(default=True)
    keep_comments = serializers.BooleanField(default=False)
    keep_attachments = serializers.BooleanField(default=False)
    keep_tags = serializers.BooleanField(default=True)

    class Meta:
        fields = '__all__'


class TaskCloneSerializer(serializers.Serializer):

    new_project = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.filter(template=False),
        required=False,
        allow_null=True,
    )
    new_node = serializers.PrimaryKeyRelatedField(
        queryset=Task.objects.all(),
        required=False,
        allow_null=True,
    )
    new_status = serializers.PrimaryKeyRelatedField(
        queryset=TaskStatus.objects.all(),
        required=False,
        allow_null=True,
    )
    new_responsible = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        allow_null=True,
    )

    new_date = serializers.DateTimeField(
        required=False,
        allow_null=True
    )
    keep_comments = serializers.BooleanField(default=False)
    keep_attachments = serializers.BooleanField(default=False)
    keep_tags = serializers.BooleanField(default=True)

    class Meta:
        fields = '__all__'
