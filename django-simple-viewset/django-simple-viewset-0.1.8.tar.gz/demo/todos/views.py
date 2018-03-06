from simple_viewset.views import ModelViewSet

from .models import Project, Task


class ProjectViewSet(ModelViewSet):
    model = Project


class TaskViewSet(ModelViewSet):
    model = Task
    list_display = ['project', 'title']
    detail_for = 'project'
