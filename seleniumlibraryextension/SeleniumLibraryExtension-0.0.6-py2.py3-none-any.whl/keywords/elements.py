#!/usr/bin/env python
# -*- coding: utf-8 -*-

#    Copyright (c) 2017, 2018 Ying Jun <WandyYing@users.noreply.github.com>

from robot.api import logger
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webelement import WebElement
from SeleniumLibrary.keywords import ElementKeywords
from SeleniumLibrary.base import keyword

class ElementKeywordsExtension(ElementKeywords):

    def __init__(self, ctx):
        super(ElementKeywordsExtension, self).__init__(ctx)

    # @keyword
    def click_element(self, locator, skip_ready=False):
        """Clicks an element identified by ``locator``.

        Arguments:
        - ``locator``: The locator to find requested element. Key attributes for
                       arbitrary elements are ``id`` and ``name``. See `introduction` for
                       details about locating elements.
        - ``skip_ready``: A boolean flag to skip the wait for page ready. (Default False)

        Examples:
        | Click Element | css=div.class |
        | Click Element | css=div.class | True |
        """
        # pylint: disable=no-member
        self.info("Clicking element '%s'." % locator)
        self._get_element_and_scroll_into_view_on_iexplore(locator).click()
        if not skip_ready:
            # pylint: disable=no-member
            self._wait_until_page_ready()


    @keyword
    def click_element_js(self, locator):
        """JavaScript click element identified by `locator`.

        Examples:
        | Click Element Js | btn |
        """
        element = self.find_element(locator)
        self.info("JavaScript clicking element '%s'" % (locator))
        self.driver.execute_script("arguments[0].click();", element)