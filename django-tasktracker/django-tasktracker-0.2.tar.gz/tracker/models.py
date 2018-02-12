from django.db import models
from django.db.models import Sum


class Developer(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)

    def __str__(self):
        return '%s %s' % (self.first_name, self.last_name)

    def get_tasks(self):
        return list(self.task_set.all())

    def get_spent_time(self):
        d = SpentTime.objects.filter(
                parent_task__developer__id=self.id).aggregate(
                    Sum('duration'))
        if d['duration__sum']:
            return d['duration__sum']
        else:
            return 0

    def get_est_time(self):
        d = Task.objects.filter(developer__id=self.id).aggregate(
            Sum('estimate'))
        if d['estimate__sum']:
            return d['estimate__sum']
        else:
            return 0


class Story(models.Model):
    name = models.CharField(max_length=30)
    description = models.TextField(max_length=500, blank=True)
    estimate = models.IntegerField()
    completed = models.BooleanField(default=False)
    creation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def get_tasks(self):
        return list(self.task_set.all())

    def get_tasks_est_time(self):
        d = Task.objects.filter(parent_story__id=self.id).aggregate(
            Sum('estimate'))
        if d['estimate__sum']:
            return d['estimate__sum']
        else:
            return 0

    def get_spent_time(self):
        d = SpentTime.objects.filter(
            parent_task__parent_story__id=self.id).aggregate(
            Sum('duration'))
        if d['duration__sum']:
            return d['duration__sum']
        else:
            return 0


class Task(models.Model):
    name = models.CharField(max_length=30)
    description = models.TextField(max_length=500, blank=True)
    estimate = models.IntegerField()
    iteration = models.IntegerField()
    completed = models.BooleanField(default=False)
    developer = models.ForeignKey(Developer, on_delete=models.CASCADE)
    parent_story = models.ForeignKey(Story, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def get_st_objects(self):
        return list(self.spenttime_set.all())

    def get_spent_time(self):
        d = self.spenttime_set.all().aggregate(Sum('duration'))
        if d['duration__sum']:
            return d['duration__sum']
        else:
            return 0

    def get_est_time(self):
        return self.estimate


class SpentTime(models.Model):
    comment = models.CharField(max_length=200, blank=True)
    duration = models.IntegerField()
    parent_task = models.ForeignKey(Task, on_delete=models.CASCADE)

    def __str__(self):
        return self.comment
