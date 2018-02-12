from django.shortcuts import render
from django.views.generic.edit import CreateView, DeleteView
from django.views.generic import ListView, DetailView
from django.urls import reverse_lazy

from tracker.models import Story, Task, Developer, SpentTime
from tracker import utils


def index(request):
    context = {'navigation': utils.INDEX_NAVIGATION,
               'title': 'Navigation'}
    return render(request, 'tracker/base.html', context)


class CustomListView(ListView):
    template_name = 'tracker/listview.html'
    extra_fields = []
    links = []
    add_url = []

    def get_context_data(self, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)
        context['title'] = self.title
        context['data_list'] = utils.build_data_list(
                                self.links,
                                self.field_names,
                                self.model.objects.all(),
                                self.extra_fields
                                )
        context['field_names'] = utils.get_display_names(
                                    self.field_names,
                                    self.extra_fields
                                    )
        context['add_url'] = self.add_url
        return context


class StoriesList(CustomListView):
    # During test class is implemented in context of working DB not test DB
    model = Story
    title = 'Stories list'
    links = [('name', 'story')]
    add_url = [('addstory', 'New story')]
    field_names = utils.STORY_FIELD_NAMES
    extra_fields = ['tasks', 'tasks estimated', 'spent time']


class TasksList(CustomListView):
    # During test class is implemented in context of working DB not test DB
    model = Task
    title = 'Tasks list'
    links = [('name', 'task'),
             ('developer', 'developer'),
             ('parent_story', 'story')]
    add_url = [('addtask', 'New task'), ('addspenttime', 'Add work time')]
    field_names = utils.TASK_FIELD_NAMES
    extra_fields = ['spent time']


class DevelopersList(CustomListView):
    model = Developer
    title = 'Developers list'
    links = [('first_name', 'developer'), ('last_name', 'developer')]
    add_url = [('adddeveloper', 'New developer')]
    field_names = utils.DEVELOPER_FIELD_NAMES


class DevelopersTime(CustomListView):
    model = Developer
    title = 'Developers time'
    links = [('first_name', 'developer'), ('last_name', 'developer')]
    field_names = utils.DEVELOPER_FIELD_NAMES[1:]
    extra_fields = ['est time', 'spent time']


class CustomDetailView(DetailView):
    template_name = 'tracker/details.html'
    has_status = False

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context['title'] = self.title
        context['return_target'] = self.return_target
        context['has_status'] = self.has_status
        context['object_iter'] = [
            (n, getattr(context['object'], n))
            for n in self.field_names
            ]
        return context

    def post(self, request, *args, **kwargs):
        o = self.get_object()
        o.completed = not o.completed
        o.save()
        return self.get(self, request)


class StoryDetails(CustomDetailView):
    model = Story
    pk_url_kwarg = 'story_id'
    title = 'Story details'
    return_target = 'stories'
    has_status = True
    field_names = utils.STORY_FIELD_NAMES


class TaskDetails(CustomDetailView):
    model = Task
    pk_url_kwarg = 'task_id'
    title = 'Task details'
    return_target = 'tasks'
    has_status = True
    field_names = utils.TASK_FIELD_NAMES


class DeveloperDetails(CustomDetailView):
    model = Developer
    pk_url_kwarg = 'developer_id'
    title = 'Developer details'
    return_target = 'developers'
    field_names = utils.DEVELOPER_FIELD_NAMES


class AddView(CreateView):
    template_name = "tracker/addform.html"

    def get_context_data(self, **kwargs):
        context = super(CreateView, self).get_context_data(**kwargs)
        context['title'] = self.title
        return context


class AddStory(AddView):
    model = Story
    # remove id and creation date fields from list
    fields = utils.STORY_FIELD_NAMES[1:-1]
    success_url = reverse_lazy('stories')
    title = 'Add new story'


class AddTask(AddView):
    model = Task
    # remove id from list
    fields = utils.TASK_FIELD_NAMES[1:]
    success_url = reverse_lazy('tasks')
    title = 'Add new task'


class AddDeveloper(AddView):
    model = Developer
    # remove id from list
    fields = utils.DEVELOPER_FIELD_NAMES[1:]
    success_url = reverse_lazy('developers')
    title = 'Add new developer'


class AddSpentTime(AddView):
    model = SpentTime
    # remove id from list
    fields = utils.SPENTTIME_FIELD_NAMES[1:]
    success_url = reverse_lazy('tasks')
    title = 'Add work time'


DEL_TEMPLATE = 'tracker/delete.html'
DEL_MODELS = [Story, Task, Developer, SpentTime]
DEL_KWARG = ['story_id', 'task_id', 'developer_id', 'time_id']
DEL_RETURN = ['stories', 'tasks', 'developers', 'tasks']


class DeleteStory(DeleteView):
    template_name = 'tracker/delete.html'
    model = Story
    pk_url_kwarg = 'story_id'
    success_url = reverse_lazy('stories')


class DeleteTask(DeleteView):
    template_name = 'tracker/delete.html'
    model = Task
    pk_url_kwarg = 'task_id'
    success_url = reverse_lazy('tasks')


class DeleteDeveloper(DeleteView):
    template_name = 'tracker/delete.html'
    model = Developer
    pk_url_kwarg = 'developer_id'
    success_url = reverse_lazy('developers')


class DeleteSpentTime(DeleteView):
    template_name = 'tracker/delete.html'
    model = SpentTime
    pk_url_kwarg = 'time_id'
    success_url = reverse_lazy('tasks')
