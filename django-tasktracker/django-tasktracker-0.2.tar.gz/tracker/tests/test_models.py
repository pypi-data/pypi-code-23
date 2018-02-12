from django.test import TestCase

from tracker.models import Story, Task, SpentTime, Developer
from tracker.tests import test_utils


class ModelTestCase(TestCase):
    def setUp(self):
        test_utils.create_test_database()


class StoryModelTests(ModelTestCase):
    def test_get_tasks(self):
        for n, s in enumerate(test_utils.TEST_STORIES, 1):
            expected_output = []
            for i, t in enumerate(test_utils.TEST_TASKS, 1):
                if t[-1] == n:
                    expected_output.append(Task.objects.get(pk=i))
            self.assertEqual(list(Story.objects.get(pk=n).get_tasks()),
                             expected_output)

    def test_get_tasks_est_time(self):
        for n, s in enumerate(test_utils.TEST_STORIES, 1):
            expected_output = 0
            for t in test_utils.TEST_TASKS:
                if t[-1] == n:
                    expected_output += t[2]
            story = Story.objects.get(pk=n)
            self.assertEqual(story.get_tasks_est_time(), expected_output)

    def test_get_spent_time(self):
        """
        Tests get_spent_time method for Story model.
        """
        for n, s in enumerate(test_utils.TEST_STORIES, 1):
            expected_output = 0
            for i, t in enumerate(test_utils.TEST_TASKS, 1):
                if t[-1] == n:
                    for j, sp in enumerate(test_utils.TEST_SPENTTIME, 1):
                        if i == sp[-1]:
                            expected_output += sp[1]
            self.assertEqual(Story.objects.get(pk=n).get_spent_time(),
                             expected_output)


class DeveloperModelTests(ModelTestCase):
    def test_get_tasks(self):
        for n, t in enumerate(test_utils.TEST_DEVELOPERS, 1):
            expected_output = []
            for i, st in enumerate(test_utils.TEST_TASKS, 1):
                if n == st[-2]:
                    expected_output.append(Task.objects.get(pk=i))
            self.assertEqual(Developer.objects.get(pk=n).get_tasks(),
                             expected_output)

    def test_get_spent_time(self):
        for n, t in enumerate(test_utils.TEST_DEVELOPERS, 1):
            expected_output = 0
            for i, st in enumerate(test_utils.TEST_TASKS, 1):
                if n == st[-2]:
                    expected_output += Task.objects.get(pk=i).get_spent_time()
            self.assertEqual(Developer.objects.get(pk=n).get_spent_time(),
                             expected_output)

    def test_get_est_time(self):
        for n, t in enumerate(test_utils.TEST_DEVELOPERS, 1):
            expected_output = 0
            for i, st in enumerate(test_utils.TEST_TASKS, 1):
                if n == st[-2]:
                    expected_output += Task.objects.get(pk=i).estimate
            self.assertEqual(Developer.objects.get(pk=n).get_est_time(),
                             expected_output)


class TaskModelTests(ModelTestCase):
    def test_get_st_objects(self):
        for n, t in enumerate(test_utils.TEST_TASKS, 1):
            expected_output = []
            for i, st in enumerate(test_utils.TEST_SPENTTIME, 1):
                if n == st[-1]:
                    expected_output.append(SpentTime.objects.get(pk=i))
            self.assertEqual(Task.objects.get(pk=n).get_st_objects(),
                             expected_output)

    def test_get_spent_time(self):
        for n, t in enumerate(test_utils.TEST_TASKS, 1):
            expected_output = 0
            task = Task.objects.get(pk=n)
            for sp in task.get_st_objects():
                expected_output += sp.duration
            self.assertEqual(task.get_spent_time(), expected_output)

    def test_get_est_time(self):
        for n, t in enumerate(test_utils.TEST_TASKS, 1):
            expected_output = 0
            task = Task.objects.get(pk=n)
            expected_output = task.estimate
            self.assertEqual(task.get_est_time(), expected_output)


class SpentTimeModelTests(ModelTestCase):
    def test_entry_creation_deletion(self):
        """
        Creates new entry in database. Tests it's attributes and removes entry.
        """
        d1 = Developer(first_name='a', last_name='b')
        d1.save()
        s = Story(name='ts', description='asd', estimate=6)
        s.save()
        t = Task(name='ta',
                 description='few',
                 estimate=486,
                 iteration=1,
                 developer=d1,
                 parent_story=s,
                 )
        t.save()
        test_data = [45, 'Some commenting.', t]
        st = SpentTime(duration=test_data[0],
                       comment=test_data[1],
                       parent_task=test_data[2]
                       )
        st.save()
        st = SpentTime.objects.get(pk=st.id)
        st_id = st.id
        self.assertEqual(st.duration, test_data[0])
        self.assertEqual(st.comment, test_data[1])
        self.assertEqual(st.parent_task, test_data[2])
        st.delete()
        self.assertRaises(SpentTime.DoesNotExist,
                          SpentTime.objects.get, pk=st_id)
