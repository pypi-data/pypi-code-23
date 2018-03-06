from django.db import models


DEFAULT_PERMISSIONS = ('add', 'change', 'delete', 'read')


class Project(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['name']
        default_permissions = DEFAULT_PERMISSIONS

    def __str__(self):
        return self.name


class Task(models.Model):
    project = models.ForeignKey(Project, related_name='tasks')
    title = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['title']
        default_permissions = DEFAULT_PERMISSIONS

    def __str__(self):
        return self.title
