# coding: utf-8
from rest_framework import routers
from file_context.viewsets import FileViewSet
from .viewsets_autocomplete import (
    EntrepreneurAutoCompleteViewSet,
)
from .viewsets import (
    EntrepreneurViewSet,
    EnterpriseViewSet,
    ProjectTypeViewSet,
    ProjectViewSet,
    ProjectTemplateViewSet,
    TaskStatusViewSet,
    TaskViewSet,
    CommentViewSet,
    AllocationViewSet,
    ReminderViewSet,
)


router = routers.DefaultRouter(trailing_slash=False)
router.register(r'entrepreneurs', EntrepreneurViewSet)
router.register(r'enterprises', EnterpriseViewSet)
router.register(r'project-types', ProjectTypeViewSet)
router.register(r'projects', ProjectViewSet)
router.register(r'templates', ProjectTemplateViewSet, base_name='templates')
router.register(r'task-status', TaskStatusViewSet, base_name='task-status')
router.register(r'tasks', TaskViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'allocations', AllocationViewSet, base_name='allocations')
router.register(r'files', FileViewSet)
router.register(r'reminders', ReminderViewSet)
router.register(r'ac/entrepreneurs', EntrepreneurAutoCompleteViewSet)
