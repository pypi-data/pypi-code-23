# functional test performed with Selenium
from django.test import LiveServerTestCase

from selenium import webdriver
from selenium.webdriver.support.ui import Select

from tracker.tests import test_utils


class NavigatingTestCase(LiveServerTestCase):

    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.get("http:/127.0.0.1:8000/tracker/")
        super().setUp()

    def tearDown(self):
        self.driver.quit()
        super().tearDown()

    def test_page(self):
        driver = self.driver
        self.assertIn(test_utils.PAGE_NAMES[0], driver.page_source)
        # page navigation and presence of key links
        for n, link in enumerate(test_utils.PAGE_LINKS[0], 1):
            self.assertIn(link, driver.page_source)
            driver.find_element_by_link_text(link).click()
            self.assertIn(test_utils.PAGE_NAMES[n], driver.page_source)
            for link_in_page in test_utils.PAGE_LINKS[n]:
                self.assertIn(link_in_page, driver.page_source)
            self.assertIn(test_utils.RETURN, driver.page_source)
            driver.find_element_by_link_text(test_utils.RETURN).click()
        # creation of test data and testing for it's presence
        for n, link in enumerate(test_utils.PAGE_LINKS[0][:-1], 1):
            driver.find_element_by_link_text(link).click()
            driver.find_element_by_link_text(
                test_utils.PAGE_LINKS[n][0]).click()
            self.assertIn('Add new', driver.page_source)
            for target, value in zip(
                        test_utils.MODELS_LIST_FOR_TEST[n-1],
                        test_utils.MODELS_TEST_DATA[n-1]):
                elem = driver.find_element_by_name(target)
                if elem.tag_name == 'select':
                    elem = Select(elem)
                    elem.select_by_visible_text(value)
                else:
                    elem.send_keys(str(value))
            driver.find_element_by_xpath("//input[@value='Save']").click()
            for value in test_utils.MODELS_TEST_DATA[n-1]:
                self.assertIn(str(value), driver.page_source)
            driver.find_element_by_link_text(test_utils.RETURN).click()
        # removing test data
        for n, link in reversed(list(
                    enumerate(test_utils.PAGE_LINKS[0][:-1], 1))
                    ):
            object_name = test_utils.MODELS_TEST_DATA[n-1][0]
            driver.find_element_by_link_text(link).click()
            driver.find_element_by_link_text(object_name).click()
            driver.find_element_by_link_text('Delete').click()
            driver.find_element_by_xpath("//input[@value='Confirm']").click()
            self.assertNotIn(object_name, driver.page_source)
            driver.find_element_by_link_text(test_utils.RETURN).click()
