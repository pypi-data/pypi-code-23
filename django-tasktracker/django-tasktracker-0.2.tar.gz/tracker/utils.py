# functions and constants

from tracker.models import Story, Task, Developer, SpentTime

MODELS = [Developer, Story, Task, SpentTime]
INDEX_NAVIGATION = ["stories", "tasks", "developers", "devtime"]
STORY_FIELD_NAMES = [
        'id',
        'name',
        'description',
        'estimate',
        'completed',
        ]
TASK_FIELD_NAMES = [
        'id',
        'name',
        'description',
        'iteration',
        'estimate',
        'completed',
        'developer',
        'parent_story',
        ]
DEVELOPER_FIELD_NAMES = [
        'id',
        'first_name',
        'last_name',
        ]
SPENTTIME_FIELD_NAMES = [
        'id',
        'comment',
        'duration',
        'parent_task',
        ]
DISPLAY_NAMES_DICT = {
    'id': 'Entry ID',
    'name': 'Name',
    'description': 'Description',
    'first_name': 'First name',
    'last_name': 'Last name',
    'estimate': 'Time estimate',
    'completed': 'Completed',
    'creation_date': 'Creation date',
    'iteration': 'Iteration',
    'developer': 'Developer',
    'parent_story': 'Parent story',
    'tasks': 'Tasks',
    'spent time': 'Spent time',
    'tasks estimated': 'Work time estimated in tasks',
    'est time': 'Total estimated time',
    }


def objects_to_attr(objects_list, field_names, extra_fields=[]):
    values = []
    for o in objects_list:
        ls = []
        for n in field_names:
            ls.append(getattr(o, n))
        for n in extra_fields:
            if n == 'tasks':
                ls.append(o.task_set)
            elif n == 'spent time':
                ls.append(o.get_spent_time())
            elif n == 'tasks estimated':
                ls.append(o.get_tasks_est_time())
            elif n == 'est time':
                ls.append(o.get_est_time())
        values.append(ls)
    return values


def get_linked_fields(field_names, links, extra_fields=[]):
    linked_fields = [0] * (len(field_names) + len(extra_fields))
    for v, n in links:
        if v in field_names:
            linked_fields[field_names.index(v)] = n
        elif v in extra_fields:
            linked_fields[extra_fields.index(v)] = n + len(field_names)
    return linked_fields


def get_links_targets(data_list, objects_list):
    for i, data in enumerate(data_list):
        for j, d in enumerate(data):
            value, link = d
            # Unpack RelatedManager
            if type(value) not in (str, int, bool):
                try:
                    value = ', '.join([str(d) for d in list(value.all())])
                    if not value:
                        value = 'None'
                except AttributeError:
                    pass
            if link:
                if isinstance(value, str) or isinstance(value, int):
                    link = (link, objects_list[i].id)
                else:
                    link = (link, value.id)
            else:
                link = (0, 0)
            data_list[i][j] = (value, link)
    return data_list


def build_data_list(links, field_names, objects_list, extra_fields=[]):
    """
    Builds a list composed of (field value, (link target group, target id))
    for each object in objects_list.
    """
    if not isinstance(objects_list, list):
        objects_list = list(objects_list)
    linked_fields = get_linked_fields(field_names, links, extra_fields)
    field_values = objects_to_attr(objects_list, field_names, extra_fields)
    data_list = [list(zip(i, linked_fields)) for i in field_values]
    data_list = get_links_targets(data_list, objects_list)
    return data_list


def get_display_names(field_names, extra_fields=[]):
    display_names = []
    for n in field_names + extra_fields:
        if n in DISPLAY_NAMES_DICT:
            display_names.append(DISPLAY_NAMES_DICT[n])
        else:
            display_names.append(n)
    return display_names


def get_model_field_names(model):
    """
    Generates all model field names. Names before id are due to relations
    from other objects. They can be accessed via obj.fieldname_set.all().
    For example tasks related to a story can be accessed with
    story.task_set.all()
    """
    return [str(o.name) for o in model._meta.get_fields()]
