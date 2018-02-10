from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import os
from time import sleep
import pkg_resources

pkg_name = 'mark_utils'
geckodriver_file = 'web_driver/geckodriver'
CLASS, ID, XPATH, TAG, LINK = 'class', 'id', 'xpath', 'tag', 'link'


class Scraper():
    def __init__(self, delay=7, log=False):
        # Binary path
        path = pkg_resources.resource_filename(pkg_name, geckodriver_file)
        profile = webdriver.FirefoxProfile(path)
        profile.set_preference("browser.cache.disk.enable", False)
        profile.set_preference("browser.cache.memory.enable", False)
        profile.set_preference("browser.cache.offline.enable", False)
        profile.set_preference("network.http.use-cache", False)
        self.webBrowser = webdriver.Firefox(profile)

        self.delay = delay
        self.log = log
        self.log_file = 'geckodriver.log'

    def openUrl(self, url):
        self.webBrowser.get(url)
        if self.log:
            print('Page changed to : {}'.format(url))

    def make_target(type_, name):
        return dict(type=type_, name=name)

    def get_element_BY(self, target):
        if isinstance(target, dict):
            return self.get_single_element_BY(target)
        if isinstance(target, list):
            return self.get_multiple_element_BY(target)

    def get_single_element_BY(self, target):
        element = None
        try:
            _type = target['type']
            _target = target['name']

            if _type is CLASS:
                element = self.__get_element_by_class(_target)
            elif _type is ID:
                element = self.__get_element_by_id(_target)
            elif _type is XPATH:
                element = self.__get_element_by_xpath(_target)
            elif _type is TAG:
                element = self.__get_element_by_tag(_target)
            else:
                print('Error - Type ( {} ).'.format(_type))

        except e:
            print('Exception: {}. \n {} -> {} - is not present in the page: {}'.format(e, _type, _target,
                                                                                       self.webBrowser.current_url))

        finally:
            if self.log and element is not None:
                print('{} -> {} - founded correctly!'.format(_type, _target))
            return element

    def get_multiple_element_BY(self, target_list):
        result = []
        for target in target_list:
            result.append(self.get_single_element_BY(target))
        return result

    def __get_element_by_class(self, className):
        element = WebDriverWait(self.webBrowser, self.delay).until(
            EC.presence_of_element_located((By.CLASS_NAME, className)))
        return element

    def __get_element_by_id(self, idName):
        element = WebDriverWait(self.webBrowser, self.delay).until(
            EC.presence_of_element_located((By.ID, idName)))
        return element

    def __get_element_by_xpath(self, xPath):
        element = WebDriverWait(self.webBrowser, self.delay).until(
            EC.presence_of_element_located((By.XPATH, xPath)))
        return element

    def __get_element_by_tag(self, tagName):
        element = WebDriverWait(self.webBrowser, self.delay).until(
            EC.presence_of_element_located((By.TAG_NAME, tagName)))
        return element

    def get_nested_elements_from_root(self, list_target):
        first_target = list_target[0]
        nested_target = list_target[1:]

        element = self.get_single_element_BY(first_target)

        for target in nested_target:
            element = self.find_elements_BY(element, target)

        return element

    def get_nested_elements(self, element, list_target):
        for target in list_target:
            element = self.find_elements_BY(element, target)
        return element

    def find_elements_BY(self, element, target):
        nested_element = None
        try:
            _type = target['type']
            _target = target['name']

            if _type is CLASS:
                nested_element = self.__find_elements_by_class(
                    element, _target)
            if _type is ID:
                nested_element = self.__find_elements_by_id(element, _target)
            if _type is XPATH:
                nested_element = self.__find_elements_by_xpath(
                    element, _target)
            if _type is TAG:
                nested_element = self.__find_elements_by_tag(element, _target)
            if _type is LINK:
                nested_element = self.__find_elements_by_partial_link_text(
                    element, _target)

        except NoSuchElementException:
            print('{} -> {} - is not present in the page: {} !'.format(_type, _target,
                                                                       self.webBrowser.current_url))

        finally:
            if self.log and nested_element is not None:
                print('{} -> {} - founded correctly!'.format(_type, _target))
            return nested_element

    def __find_elements_by_class(self, element, className):
        nested_element = element.find_elements_by_class_name(className)
        return nested_element

    def __find_elements_by_id(self, element, idName):
        nested_element = element.find_elements_by_id(idName)
        return nested_element

    def __find_elements_by_xPath(self, element, xPath):
        nested_element = element.find_elements_by_xpath(xPath)
        return nested_element

    def __find_elements_by_tag(self, element, tagName):
        nested_element = element.find_elements_by_tag_name(tagName)
        return nested_element

    def __find_elements_by_partial_link_text(self, element, link_text=''):
        nested_element = element.find_element_by_partial_link_text(
            link_text).get_attribute('href')
        return nested_element

    def close(self):
        self.webBrowser.close()
        if os.path.isfile(self.log_file):
            sleep(2)
            os.remove(self.log_file)
        if self.log:
            print('WebDriver closed correctly.')
