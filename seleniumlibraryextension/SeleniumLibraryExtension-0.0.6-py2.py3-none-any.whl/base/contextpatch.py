#!/usr/bin/env python
# -*- coding: utf-8 -*-

#    Copyright (c) 2017, 2018 Ying Jun <WandyYing@users.noreply.github.com>

import time
from SeleniumLibrary.base.context import ContextAware

class ContextPatch(object):
    def __init__(self):
        pass

    def find_element(self, locator, tag=None, required=True, parent=None):
        """Find element matching `locator`.

        :param locator: Locator to use when searching the element.
            See library documentation for the supported locator syntax.
        :type locator: str or selenium.webdriver.remote.webelement.WebElement
        :param tag: Limit searching only to these elements.
        :type tag: str
        :param required: Raise `ElementNotFound` if element not found when
            true, return `None` otherwise.
        :type required: True or False
        :param parent: Optional parent `WebElememt` to search child elements
            from. By default search starts from the root using `WebDriver`.
        :type parent: selenium.webdriver.remote.webelement.WebElement
        :return: Found `WebElement` or `None` if element not found and
            `required` is false.
        :rtype: selenium.webdriver.remote.webelement.WebElement
        :raises SeleniumLibrary.errors.ElementNotFound: If element not found
            and `required` is true.
        """
        element = self.element_finder.find(locator, tag, True, required, parent)
        if element:
            # script = """
            #         element = arguments[0];
            #         original_style = element.getAttribute('style');
            #         element.setAttribute('style', original_style + "; background: green; border: 2px solid red;");
            #         setTimeout(function(){
            #             element.setAttribute('style', original_style);
            #     }, 300);
            #     element.scrollIntoView();
            #  """
            script = """
                    element = arguments[0];
                    original_style = element.getAttribute('style');
                    element.setAttribute('style', original_style + "box-shadow: 0px 0px 6px 6px rgba(0, 255, 0, 1);");
                    setTimeout(function(){
                        element.setAttribute('style', original_style);
                }, 300);
                """
            self.driver.execute_script(script, element)
            print("find&highlight&sleep")
            time.sleep(0.310)
        return element

    ContextAware.find_element = find_element