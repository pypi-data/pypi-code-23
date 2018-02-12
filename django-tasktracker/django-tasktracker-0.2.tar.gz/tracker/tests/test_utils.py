# test constants and general functions
from tracker.models import Story, Task, SpentTime, Developer
from tracker import utils

PAGE_NAMES = [
    "Navigation",
    "Stories list",
    "Developers list",
    "Tasks list",
    "Developers time",
    ]
PAGE_LINKS = [
    ["stories", "developers", "tasks", "devtime"],
    ["New story"],
    ["New developer"],
    ["New task", "Add work time"],
    [""],
    ]
RETURN = "Back to index"
MODELS_LIST_FOR_TEST = [
    utils.STORY_FIELD_NAMES[1:-1],
    utils.DEVELOPER_FIELD_NAMES[1:],
    utils.TASK_FIELD_NAMES[1:],
    ]
TEST_STORIES = [
    ['Empty story', '', 0],
    ['Test entry', 'This story has one task', 852],
    ['Last story', 'This story has four tasks. Busy one.', 23],
    ]
TEST_DEVELOPERS = [
    ['Marlow', 'Smith'],
    ['Vardenis', 'Pavardenis'],
    ['Abc', 'Def'],
    ['Mostly', 'Meh']
    ]
TEST_TASKS = [
    ['First task', 'Afda efeava faeefa.', 45, 1, 1, 2],
    ['Second task', 'fdaoenio aioe ane eavfe.', 12, 1, 3, 3],
    ['Second task', 'fdaoenio aioe ane eavfe.', 15, 2, 4, 3],
    ['Third task', 'Are you sure?', 45, 1, 1, 3],
    ['Final task', 'You hope it is.', 60, 5, 4, 3],
    ]
TEST_SPENTTIME = [
    ['', 5, 1],
    ['Coding', 78, 1],
    ['Sleeping', 20, 5],
    ['', 9, 2],
    ['s', 47, 3],
    ['a', 99, 3],
    ['d', 15, 5],
    ['maybe', 1, 1],
    ['tests', 19, 2],
    ]
# Altering task data representation for selenium tests
TEST_TASK = (TEST_TASKS[0][0:4] + [0] + [
             ' '.join(TEST_DEVELOPERS[0][0:2]),
             TEST_STORIES[0][0],
             ]
             )
MODELS_TEST_DATA = [TEST_STORIES[0], TEST_DEVELOPERS[0], TEST_TASK]


def create_test_database():
    for s in TEST_STORIES:
        story = create_story(*s)
        story.save()
    for d in TEST_DEVELOPERS:
        developer = create_developer(*d)
        developer.save()
    for t in TEST_TASKS:
        task = create_task(*t)
        task.save()
    for st in TEST_SPENTTIME:
        spent = create_spent_time(*st)
        spent.save()


def create_story(n, d, e):
    return Story(name=n, description=d, estimate=e)


def create_developer(f, l):
    return Developer(first_name=f, last_name=l)


def create_task(n, d, e, i, dev, p):
    return Task(name=n, description=d, estimate=e, iteration=i,
                developer=Developer.objects.get(pk=dev),
                parent_story=Story.objects.get(pk=p))


def create_spent_time(c, dur, p):
    return SpentTime(comment=c, duration=dur,
                     parent_task=Task.objects.get(pk=p))
