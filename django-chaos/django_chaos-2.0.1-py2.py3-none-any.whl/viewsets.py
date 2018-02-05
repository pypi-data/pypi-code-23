# coding: utf-8
import logging
from datetime import timedelta
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from django.db.models import ProtectedError
from django.utils.translation import ugettext_lazy as _
from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route
from file_context.models import File
from .signals import (
    chaos_instance_updated,
    chaos_instance_deleted,
)
from .allocation import (
    AllocationHandler,
)
from .rest import (
    Responses
)
from .utils import (
    TaskHandler,
    get_model,
)
from .exporters import (
    XLSXTaskExport,
    ICALTaskExport,
)
from .models import (
    Entrepreneur,
    EntrepreneurHasEnterprise,
    Enterprise,
    ProjectType,
    Project,
    TaskStatus,
    Task,
    Comment,
    Reminder
)
from .filters import (
    EntrepreneurFilter,
    EnterpriseFilter,
    ProjectTypeFilter,
    ProjectFilter,
    TaskStatusFilter,
    TaskFilter,
    CommentFilter,
)
from .serializers import (
    EntrepreneurSerializer,
    EnterpriseSerializer,
    ProjectTypeSerializer,
    ProjectSerializer,
    TaskStatusSerializer,
    TaskSerializer,
    TaskAttachmentSerializer,
    TaskChangeSerializer,
    CommentSerializer,
    ReminderSerializer,
    AllocationSerializer,
    ChangeStatusSerializer,
    AttachDetachSerializer,
    ProjectCloneSerializer,
    TaskCloneSerializer,
    ListAllocationSerializer,
)
User = get_user_model()
logger = logging.getLogger(__name__)


def custom_update(self, viewset, request, pk=None, partial=False):
    """
    Custom update method. This does:
    * sends an update signal that includes the user - fired AFTER post_save.
    """
    try:
        user = request.user
        instance = self.get_object()
        if partial:
            result = super(viewset, self).update(request, **{'pk': pk, 'partial': partial})
        else:
            result = super(viewset, self).update(request, **{'pk': pk})
        chaos_instance_updated.send_robust(instance.__class__, instance=instance, user=user, data=request.data)
        return result
    except:
        logger.error('something bad happened while trying to update an object', exc_info=True)
        return Response('Cannot update object.')


def custom_destroy(self, viewset, request, pk=None):
    """
    Custom destroy
    * sends a signal that includes the user
    * prevents the destroy if the instance cannot be deleted
    """
    try:
        user = request.user
        instance = self.get_object()
        result = super(viewset, self).destroy(request, **{'pk': pk})
        chaos_instance_deleted.send_robust(instance.__class__, instance=instance, user=user)
        return result
    except ProtectedError:
        return Response('Cannot delete object because of protected foreign key relation',
                        status=status.HTTP_409_CONFLICT)


def handle_reminders(viewset, instance):
    request = viewset.request
    user = request.user
    reminders = request.data.get('reminders')
    task_ct = ContentType.objects.get_for_model(Task)
    if reminders:
        for r in reminders:
            try:
                delta = int(r['time_delta'])
            except:
                continue
            Reminder.objects.create(
                user=user,
                created_by=user,
                content_type=task_ct,
                object_id=instance.pk,
                time_delta=timedelta(days=delta)
            )


def handle_entrepreneurs(viewset, instance):
    request = viewset.request
    entrepreneurs = request.data.get('entrepreneurs')
    if not entrepreneurs:
        return
    instance.entrepreneurs.clear()
    for e_id in entrepreneurs:
        if not e_id:
            continue
        try:
            entrepreneur = Entrepreneur.objects.get(pk=e_id)
            EntrepreneurHasEnterprise.objects.create(
                entrepreneur=entrepreneur,
                enterprise=instance
            )
        except Entrepreneur.DoesNotExist:
            pass


def handle_files(viewset, instance):
    request = viewset.request
    files = request.data.get('files')
    if files:
        for file_id in files:
            try:
                file_instance = File.objects.get(pk=file_id)
                file_instance.attach(instance)
            except File.DoesNotExist:
                pass


class EntrepreneurViewSet(viewsets.ModelViewSet):

    queryset = Entrepreneur.objects.all()\
        .prefetch_related('enterprises')
    serializer_class = EntrepreneurSerializer
    filter_class = EntrepreneurFilter
    search_fields = (
        'name',
        'nickname',
        'document',
        'description',
    )

    def perform_create(self, serializer):
        super(EntrepreneurViewSet, self).perform_create(serializer)
        handle_files(self, serializer.instance)

    def partial_update(self, request, pk=None):
        return custom_update(self, EntrepreneurViewSet, request, pk, partial=True)

    def update(self, request, pk=None):
        return custom_update(self, EntrepreneurViewSet, request, pk)

    def destroy(self, request, pk=None):
        return custom_destroy(self, EntrepreneurViewSet, request, pk)


class EnterpriseViewSet(viewsets.ModelViewSet):

    queryset = Enterprise.objects.all()\
        .prefetch_related('entrepreneurs')\
        .select_related('created_by')
    serializer_class = EnterpriseSerializer
    filter_class = EnterpriseFilter
    search_fields = (
        'id',
        'name',
        'description',
    )

    def perform_update(self, serializer):
        super(EnterpriseViewSet, self).perform_update(serializer)
        handle_entrepreneurs(self, serializer.instance)

    def perform_create(self, serializer):
        """
        overrides perform_create to automagically
        treat files in the request :D
        """
        super(EnterpriseViewSet, self).perform_create(serializer)
        handle_files(self, serializer.instance)
        handle_entrepreneurs(self, serializer.instance)

    def partial_update(self, request, pk=None):
        return custom_update(self, EnterpriseViewSet, request, pk, partial=True)

    def update(self, request, pk=None):
        return custom_update(self, EnterpriseViewSet, request, pk)

    def destroy(self, request, pk=None):
        return custom_destroy(self, EnterpriseViewSet, request, pk)


class ProjectTypeViewSet(viewsets.ModelViewSet):

    queryset = ProjectType.objects.all()
    serializer_class = ProjectTypeSerializer
    filter_class = ProjectTypeFilter
    search_fields = (
        'id',
        'code',
        'description',
    )

    def partial_update(self, request, pk=None):
        return custom_update(self, ProjectTypeViewSet, request, pk, partial=True)

    def update(self, request, pk=None):
        return custom_update(self, ProjectTypeViewSet, request, pk)

    def destroy(self, request, pk=None):
        return custom_destroy(self, ProjectTypeViewSet, request, pk)


class BaseProjectViewSet(object):

    queryset = Project.objects.all()\
        .select_related('created_by')\
        .select_related('type')\
        .select_related('responsible')\
        .select_related('enterprise')\
        .prefetch_related('tags')
    serializer_class = ProjectSerializer
    filter_class = ProjectFilter
    search_fields = (
        'id',
        'name',
        'type',
        'responsible',
        'description',
        'tags',
    )

    @detail_route(methods=['post'])
    def clone(self, request, pk=None):
        project = self.get_object()
        pcs = ProjectCloneSerializer(data=request.data)
        if not pcs.is_valid():
            return Response(pcs.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            new_project = project.clone(
                pcs.validated_data.get('new_name'),
                pcs.validated_data.get('new_enterprise'),
                pcs.validated_data.get('new_type'),
                pcs.validated_data.get('new_responsible'),
                pcs.validated_data.get('new_date'),
                pcs.validated_data.get('new_status'),
                pcs.validated_data.get('keep_tasks'),
                pcs.validated_data.get('keep_comments'),
                pcs.validated_data.get('keep_attachments'),
                pcs.validated_data.get('keep_tags')
            )
            if new_project:
                project_serializer = ProjectSerializer(new_project, context={'request': request})
                return Response(project_serializer.data, status=status.HTTP_201_CREATED)
            else:
                logger.error('an internal exception ocurred while cloning a project')
                return Responses.server_error(_('Something bad happened while cloning project.'))
        except Exception as ex:
            message = ex.message if hasattr(ex, 'message') else ''
            logger.error('error while cloning project %s. error: %s', project, message, exc_info=True)
            return Responses.server_error(message)

    @detail_route(methods=['get'])
    def score(self, request, pk=None):
        project = self.get_object()
        return Response({'project': project.pk, 'score': project.score})

    def perform_create(self, serializer):
        """
        overrides perform_create to automagically
        treat files in the request :D
        """
        super(BaseProjectViewSet, self).perform_create(serializer)
        handle_files(self, serializer.instance)

    def partial_update(self, request, pk=None):
        return custom_update(self, BaseProjectViewSet, request, pk, partial=True)

    def update(self, request, pk=None):
        return custom_update(self, BaseProjectViewSet, request, pk)

    def destroy(self, request, pk=None):
        return custom_destroy(self, BaseProjectViewSet, request, pk)


class ProjectTemplateViewSet(BaseProjectViewSet, viewsets.ModelViewSet):

    queryset = Project.objects.filter(template=True)


class ProjectViewSet(BaseProjectViewSet, viewsets.ModelViewSet):

    queryset = Project.objects.filter(template=False)


class TaskStatusViewSet(viewsets.ModelViewSet):

    queryset = TaskStatus.objects.all()
    serializer_class = TaskStatusSerializer
    filter_class = TaskStatusFilter
    search_fields = (
        'id',
        'code',
        'description',
        'is_system_status',
        'is_closing_status'
    )

    def partial_update(self, request, pk=None):
        return custom_update(self, TaskStatusViewSet, request, pk, partial=True)

    def update(self, request, pk=None):
        return custom_update(self, TaskStatusViewSet, request, pk)

    def destroy(self, request, pk=None):
        return custom_destroy(self, TaskStatusViewSet, request, pk)


class TaskViewSet(viewsets.ModelViewSet):

    queryset = Task.objects.all()\
        .select_related('created_by')\
        .select_related('status')\
        .select_related('project__enterprise')\
        .select_related('project')\
        .select_related('responsible')\
        .prefetch_related('comments')\
        .prefetch_related('tags')
    serializer_class = TaskSerializer
    filter_class = TaskFilter
    search_fields = (
        'id',
        'project',
        'parent',
        'responsible',
        'status',
        'name',
        'description',
        'tags',
    )
    exporters = {
        'XLSX': XLSXTaskExport,
        'ICAL': ICALTaskExport,
    }

    @list_route(methods=['get'])
    def export(self, request, *args, **kwargs):
        extension = request.query_params.get('extension', 'XLSX')
        extension = extension.upper()
        queryset = self.filter_queryset(self.get_queryset())
        if extension not in self.exporters:
            return Responses.client_error()
        try:
            exporter = self.exporters[extension](publish_url=True, request=request)
            return exporter.respond(queryset)
        except Exception as ex:
            message = ex.message if hasattr(ex, 'message') else ''
            logger.error('error while trying to export tasks to %s format. error: ', extension, message, exc_info=True)
            return Responses.server_error()

    @detail_route(methods=['get'])
    def score(self, request, pk=None):
        task = self.get_object()
        return Response({'task': task.pk, 'score': task.score})

    @detail_route(methods=['post'])
    def clone(self, request, pk=None):
        task = self.get_object()
        tcs = TaskCloneSerializer(data=request.data)
        if not tcs.is_valid():
            return Response(tcs.errors, status=status.HTTP_400_BAD_REQUEST)

        new_project = tcs.validated_data.get('new_project')
        new_node = tcs.validated_data.get('new_node')
        new_status = tcs.validated_data.get('new_status')
        new_date = tcs.validated_data.get('new_date')
        new_responsible = tcs.validated_data.get('new_responsible')
        keep_comments = tcs.validated_data.get('keep_comments')
        keep_attachments = tcs.validated_data.get('keep_attachments')
        keep_tags = tcs.validated_data.get('keep_tags')

        try:
            new_task = task.clone(
                new_project,
                new_node,
                new_status,
                new_date,
                new_responsible,
                keep_comments,
                keep_attachments,
                keep_tags
            )
            if new_task:
                task_serializer = TaskSerializer(new_task)
                return Response(
                    task_serializer.data,
                    status=status.HTTP_201_CREATED
                )
            else:
                logger.error('an internal exception ocurred while cloning a task')
                return Responses.server_error(_('Something bad happened while cloning a task.'))
        except Exception as ex:
            message = ex.message if hasattr(ex, 'message') else ''
            logger.error('failed to clone task %s. error: %s', task, message, exc_info=True)
            return Responses.server_error(message)

    @detail_route(methods=['post'])
    def attach(self, request, pk=None):
        task = self.get_object()
        ads = AttachDetachSerializer(data=request.data)
        if not ads.is_valid():
            return Response(ads.errors, status=status.HTTP_400_BAD_REQUEST)
        model_name = ads.validated_data.get('model_name')
        model_id = ads.validated_data.get('model_id')
        model_class = get_model(model_name)
        if not model_class:
            return Responses.not_found('model not found')
        try:
            user = request.user if not request.user.is_anonymous else None
            model = model_class.objects.get(pk=model_id)
            attachment = task.attach(model, user=user)
            att_serializer = TaskAttachmentSerializer(attachment)
            return Response(att_serializer.data)
        except model_class.DoesNotExist:
            logger.warn('%s model with id %s does not exist', model_name, model_id)
            return Responses.not_found()
        except Exception as ex:
            message = ex.message if hasattr(ex.message) else ''
            logger.error('error while attaching %s - %s to %s. error: %s', model_name, model_id, task, message)
            return Responses.server_error(message)

    @detail_route(methods=['post'])
    def detach(self, request, pk=None):
        task = self.get_object()
        ads = AttachDetachSerializer(data=request.data)
        if not ads.is_valid():
            return Response(ads.errors, status=status.HTTP_400_BAD_REQUEST)
        model_name = ads.validated_data.get('model_name')
        model_id = ads.validated_data.get('model_id')
        model_class = get_model(model_name)
        if not model_class:
            return Responses.not_found('model not found')
        try:
            model = model_class.objects.get(pk=model_id)
            task.detach(model)
            return Responses.success('Detach succeeded')
        except model_class.DoesNotExist:
            logger.warn('model %s with id %s does not exist', model_name, model_id)  # noqa
            return Responses.not_found()
        except Exception as ex:
            message = ex.message if hasattr(ex, 'message') else ''
            logger.error('error while detaching %s - %s from %s. error: %s', model_name, model_id, task, message)  # noqa
            return Responses.server_error(message)

    @detail_route(methods=['post'])
    def change_status(self, request, pk=None):
        task = self.get_object()
        css = ChangeStatusSerializer(data=request.data)
        if not css.is_valid():
            logger.info('invalid request for change_status')
            return Response(css.errors, status=status.HTTP_400_BAD_REQUEST)

        change = css.validated_data
        user = None if request.user.is_anonymous() else request.user
        try:
            new_status = TaskStatus.objects.get(pk=change.get('status'))
            handler = TaskHandler()
            changes = handler.to_status(
                task=task,
                status=new_status,
                dry_run=change.get('dry_run', True),
                user=user
            )
            if not changes:
                logger.info('change_status is not allowed. from %s to %s.', task.status, new_status)
                return Responses.succeeded('No changes detected, no changes executed.')

            logger.info('executing status changes')
            flat_changes = TaskHandler.flatten(changes)
            change_serializer = TaskChangeSerializer(flat_changes, many=True)
            return Response(data=change_serializer.data)

        except TaskStatus.DoesNotExist:
            logger.warn('status selected by the user does not exist.')
            return Responses.not_found()
        except Exception as ex:
            error_msg = getattr(ex, 'message', '')
            logger.error('something wrong happened while trying to change task status. %s', error_msg, exc_info=True)
            return Responses.server_error(error_msg)

    def perform_create(self, serializer):
        """
        overrides perform_create to automagically
        treat files in the request :D
        """
        super(TaskViewSet, self).perform_create(serializer)
        handle_files(self, serializer.instance)
        handle_reminders(self, serializer.instance)

    def partial_update(self, request, pk=None):
        return custom_update(self, TaskViewSet, request, pk, partial=True)

    def update(self, request, pk=None):
        return custom_update(self, TaskViewSet, request, pk)

    def destroy(self, request, pk=None):
        return custom_destroy(self, TaskViewSet, request, pk)


class CommentViewSet(viewsets.ModelViewSet):

    queryset = Comment.objects.all()\
        .select_related('task')\
        .select_related('created_by')
    serializer_class = CommentSerializer
    filter_class = CommentFilter
    search_fields = (
        'id',
        'created_by',
        'task',
        'text',
    )

    def perform_create(self, serializer):
        """
        overrides perform_create to automagically
        treat files in the request :D
        """
        super(CommentViewSet, self).perform_create(serializer)
        handle_files(self, serializer.instance)

    def partial_update(self, request, pk=None):
        return custom_update(self, CommentViewSet, request, pk, partial=True)

    def update(self, request, pk=None):
        return custom_update(self, CommentViewSet, request, pk)

    def destroy(self, request, pk=None):
        return custom_destroy(self, CommentViewSet, request, pk)


class ReminderViewSet(viewsets.ModelViewSet):

    queryset = Reminder.objects.all()
    serializer_class = ReminderSerializer
    search_fields = (
        'user',
        'content_type',
        'object_id',
        'is_recurring'
    )

    def partial_update(self, request, pk=None):
        return custom_update(self, ReminderViewSet, request, pk, partial=True)

    def update(self, request, pk=None):
        return custom_update(self, ReminderViewSet, request, pk)

    def destroy(self, request, pk=None):
        return custom_destroy(self, ReminderViewSet, request, pk)


class AllocationViewSet(viewsets.ViewSet):

    """
    Viewset that allows you to see how your resources
    are allocated
    """

    def list(self, request):
        try:
            # TODO: does not work
            list_allocation_serializer = ListAllocationSerializer(data=request.data)
            if not list_allocation_serializer.is_valid():
                return Response(data=list_allocation_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            project = list_allocation_serializer.validated_data.get('project')
            min_date = list_allocation_serializer.validated_data.get('min_date')
            max_date = list_allocation_serializer.validated_data.get('max_date')

            users = User.objects.all()

            allocation_handler = AllocationHandler()
            allocations = allocation_handler.get_allocations(users, min_date, max_date, project)
            allocation_serial = AllocationSerializer(allocations, many=True)
            return Response(allocation_serial.data)
        except Exception as ex:
            message = ex.message if hasattr(ex, 'message') else ''
            logger.error('error while fetching list of allocations. Error: %s', message, exc_info=True)
            return Responses.server_error(message)

    def retrieve(self, request, pk=None):

        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Responses.not_found()

        try:
            las = ListAllocationSerializer(data=request.data)
            if not las.is_valid():
                return Response(data=las.errors, status=status.HTTP_400_BAD_REQUEST)

            project = las.validated_data.get('project')
            min_date = las.validated_data.get('min_date')
            max_date = las.validated_data.get('max_date')

            allocation_handler = AllocationHandler()
            allocations = allocation_handler.get_user_allocations(user, min_date, max_date, project)
            allocation_serializer = AllocationSerializer(allocations, many=True)
            return Response(allocation_serializer.data)
        except Exception as ex:
            message = ex.message if hasattr(ex, 'message') else ''
            logger.error('error while fetching allocation for user %s. Error: %s', user, message, exc_info=True)
            return Responses.server_error(message)
