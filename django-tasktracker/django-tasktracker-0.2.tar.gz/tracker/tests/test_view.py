from copy import deepcopy

from django.test import TestCase
from django.urls import reverse

from tracker.tests import test_utils


class CommonViewTests(object):
    def test_links_and_title(self):
        """
        Test for presence of key page components.
        """
        response = self.client.get(self.response_url)
        for l in self.links:
            self.assertContains(response, 'href="/tracker/'+l+'"',
                                msg_prefix="Missing "+l+" list url.")
        for c in self.content:
            self.assertContains(response, c,
                                msg_prefix='Missing text: '+c)


class CommonListViewTests(CommonViewTests):

    def test_links_and_title(self):
        super().test_links_and_title()
        response = self.client.get(self.response_url)
        self.assertContains(response, 'No data found.',
                            msg_prefix='No empty database message.')

    def test_list_representation(self):
        """
        Checks for presence of data entries and links.
        """
        test_utils.create_test_database()
        response = self.client.get(self.response_url)
        for n, s in enumerate(self.test_list, 1):
            for i in s:
                if isinstance(i, str) or isinstance(i, int):
                    tm = i
                else:
                    tm = i.name
                self.assertContains(
                    response,
                    tm,
                    msg_prefix='Incomplete data representation.')
            for l, o in self.list_links:
                link_id = str(n)
                if o:
                    link_id = str(s[o])
                self.assertContains(
                    response,
                    'href="/tracker/' + l + link_id + '/"',
                    msg_prefix='Missing link to object: ' + l + link_id)


class IndexViewTests(TestCase, CommonViewTests):
    response_url = reverse('index')
    links = ['stories/', 'tasks/', 'developers/', 'devtime/']
    content = ['Navigation', 'stories', 'tasks', 'developers', 'devtime']


class StoriesListViewTests(TestCase, CommonListViewTests):
    response_url = reverse('stories')
    links = ['stories/add/', '']
    content = ['Stories list', 'New story', 'Back to index']
    test_list = test_utils.TEST_STORIES
    list_links = [('stories/', 0), ]


class TasksListViewTests(TestCase, CommonListViewTests):
    response_url = reverse('tasks')
    links = ['tasks/add/', '']
    content = ['Tasks list', 'New task', 'Add work time', 'Back to index']
    test_list = deepcopy(test_utils.TEST_TASKS)
    list_links = [('tasks/', 0), ('stories/', 5)]


class DevelopersListViewTests(TestCase, CommonListViewTests):
    response_url = reverse('developers')
    links = ['developers/add/', '']
    content = ['Developers list', 'New developer', 'Back to index']
    test_list = test_utils.TEST_DEVELOPERS
    list_links = [('developers/', 0)]


class DevelopersTimeTests(TestCase, CommonListViewTests):
    response_url = reverse('devtime')
    links = ['']
    content = ['Developers time', 'Back to index']
    test_list = test_utils.TEST_DEVELOPERS[1:]
    list_links = [('developers/', 0)]
