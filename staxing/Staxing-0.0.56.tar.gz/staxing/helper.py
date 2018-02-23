"""OpenStax Python helper for common actions."""

import calendar
import datetime
import inspect
import os
import re

from autochomsky import chomsky
from builtins import FileNotFoundError
from datetime import timedelta
from itertools import repeat
from random import randint
from requests import HTTPError
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome import options, service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as expect
from selenium.webdriver.support.ui import Select, WebDriverWait
from time import sleep
from urllib.parse import urlparse, ParseResult

try:
    from staxing.assignment import Assignment
except ImportError:  # pragma: no cover
    from assignment import Assignment
try:
    from staxing.page_load import SeleniumWait as Page
except ImportError:  # pragma: no cover
    from page_load import SeleniumWait as Page

__version__ = '0.0.43'


class Helper(object):
    """Primary parent control class."""

    CONDENSED_WIDTH = 767  # pixels wide
    DEFAULT_WAIT_TIME = 15  # seconds
    CAPABILITIES = {
        'android': DesiredCapabilities.ANDROID,
        'chrome': DesiredCapabilities.CHROME,
        'firefox': DesiredCapabilities.FIREFOX,
        'headlesschrome': DesiredCapabilities.CHROME,
        'htmlunit': DesiredCapabilities.HTMLUNIT,
        'htmlunitwithjs': DesiredCapabilities.HTMLUNITWITHJS,
        'internetexplorer': DesiredCapabilities.INTERNETEXPLORER,
        'ipad': DesiredCapabilities.IPAD,
        'iphone': DesiredCapabilities.IPHONE,
        'microsoftedge': DesiredCapabilities.EDGE,
        'opera': DesiredCapabilities.OPERA,
        'safari': DesiredCapabilities.SAFARI,
    }

    def __init__(self,
                 driver_type='chrome',
                 capabilities=None,
                 pasta_user=None,
                 wait_time=DEFAULT_WAIT_TIME,
                 remote_driver='',
                 existing_driver=None,
                 **kwargs):
        """Class constructor."""
        if driver_type == 'saucelabs' and pasta_user is None:
            raise TypeError('A Sauce Labs user is required for remote testing')
        self.pasta = pasta_user
        self.remote_driver = remote_driver
        self.driver_type = driver_type.lower()
        if existing_driver:
            self.driver = existing_driver
        else:
            driver = driver_type if not pasta_user else 'saucelabs'
            self.driver = self.run_on(
                driver_type=driver,
                pasta_user=self.pasta,
                capabilities=capabilities)
            self.driver.implicitly_wait(wait_time)
        self.wait = WebDriverWait(self.driver, wait_time)
        self.wait_time = wait_time
        self.page = Page(self.driver, self.wait_time)
        super(Helper, self).__init__()

    def __enter__(self):
        """Entry point."""
        return self

    def __del__(self):
        """Class destructor."""
        self.delete()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Class exitor."""
        self.delete()

    def delete(self):
        """Webdriver destructor."""
        self.wait = None
        try:
            self.driver.quit()
        except Exception:
            pass

    @classmethod
    def default_capabilities(cls, browser='chrome'):
        """Return the default browser capabilities."""
        browser = browser.lower()
        browser = ''.join(browser.split())
        return Helper.CAPABILITIES[browser].copy()

    def run_on(self, driver_type, pasta_user=None, capabilities={}):
        """Webdriver activation.

        driver_type (string): web browser type
        pasta_user (PastaSauce): optional API access for saucelabs
        capabilities (dict): browser settings; copy object to avoid overwrite
            Defaults:
                DesiredCapabilities.ANDROID.copy()
                DesiredCapabilities.CHROME.copy()
                DesiredCapabilities.EDGE.copy()
                DesiredCapabilities.FIREFOX.copy()
                DesiredCapabilities.HTMLUNIT.copy()
                DesiredCapabilities.HTMLUNITWITHJS.copy()
                DesiredCapabilities.INTERNETEXPLORER.copy()
                DesiredCapabilities.IPAD.copy()
                DesiredCapabilities.IPHONE.copy()
                DesiredCapabilities.ORERA.copy()
                DesiredCapabilities.SAFARI.copy()
            Keys:
                platform
                browserName
                version
                javascriptEnabled
        wait (int): standard time, in seconds, to wait for Selenium commands
        opera_driver (string): Chromium location
        """
        if pasta_user:
            driver = 'saucelabs'
        elif driver_type and 'chrome' not in driver_type:
            driver = driver_type
        else:
            option_set = options.Options()
            option_set.add_argument('disable-infobars')
            option_set.add_argument('disable-geolocation')
            option_set.add_experimental_option(
                'prefs', {
                    'credentials_enable_service': False,
                    'profile': {
                        'password_manager_enabled': False
                    }
                }
            )
            if 'headless' in driver_type:
                option_set.add_argument('headless')
                driver = 'headlesschrome'
            else:
                driver = 'chrome'
        try:
            return {
                'firefox': lambda: webdriver.Firefox(),
                'chrome': lambda: webdriver.Chrome(
                    chrome_options=option_set),
                'headlesschrome': lambda: webdriver.Chrome(
                    chrome_options=option_set),
                'ie': lambda: webdriver.Ie(),
                'opera': lambda: self.start_opera(self.opera_driver),
                'safari': lambda: webdriver.Safari(),
                'saucelabs': lambda: webdriver.Remote(
                    command_executor=(
                        'http://%s:%s@ondemand.saucelabs.com:80/wd/hub' %
                        (pasta_user.get_user(), pasta_user.get_access_key())),
                    desired_capabilities=capabilities),
            }[driver]()
        except WebDriverException as err:
            raise FileNotFoundError(err)
        except Exception as err:
            raise err

    def start_opera(self, location):
        """Opera initiator."""
        webdriver_service = service.Service(location)
        webdriver_service.start()
        return webdriver.Remote(
            webdriver_service.service_url,
            DesiredCapabilities.OPERA.copy()
        )

    def change_wait_time(self, new_wait):
        """Change the max action wait time."""
        if new_wait <= 0:
            raise ValueError('Wait time must be greater than zero (0).')
        self.driver.implicitly_wait(new_wait)
        self.wait = WebDriverWait(self.driver, new_wait)
        self.wait_time = new_wait

    def date_string(self, day_delta=0, str_format='%m/%d/%Y'):
        """System date format pass-through."""
        return Assignment().to_date_string(day_delta, str_format)

    def get(self, url):
        """Return the current URL."""
        self.driver.get(url)
        self.page.wait_for_page_load()

    def get_window_size(self, dimension=None):
        """Return the current window dimensions."""
        get_size = self.driver.get_window_size()
        if not dimension:
            return get_size
        if dimension not in get_size:
            raise IndexError('Unknown dimension: %s' % dimension)
        return get_size[dimension]

    def set_window_size(self, width=0, height=0, maximize=False):
        """Attempt to change the browser window size."""
        if maximize:
            self.driver.maximize_window()
        elif width >= 1 and height >= 1:
            self.driver.set_window_size(width, height)
            sleep(1.0)
        return self.get_window_size()

    def set_window_position(self, x_=0, y_=0):
        """Move the browser window anchor."""
        if x_ >= 0 and y_ >= 0:
            self.driver.set_window_position(x_, y_)
            sleep(1.0)

    def sleep(self, seconds=1.0):
        """Stop execution for the specified time in seconds."""
        sleep(seconds)

    def find(self, by, value):
        """Find element."""
        return self.driver.find_element(by=by, value=value)

    def find_all(self, by, value):
        """Find elements."""
        return self.driver.find_elements(by=by, value=value)

    def scroll_to(self, target):
        """Scroll the browser window to bring the target into view."""
        Assignment.scroll_to(self.driver, target)
        return target

    def url_parse(self, site):
        """Parse the url into a valid url."""
        parse = list(
            urlparse(
                site if urlparse(site).scheme
                else '%s%s' % ('//', site)
            )
        )
        parse[0] = b'https'
        for index, value in enumerate(parse):
            parse[index] = value.decode('utf-8') if isinstance(value, bytes) \
                else value
        parse = ParseResult(*parse)
        return parse.geturl()


class User(Helper):
    """User parent class."""

    CONDENSED_WIDTH = Helper.CONDENSED_WIDTH
    DEFAULT_WAIT_TIME = Helper.DEFAULT_WAIT_TIME

    def __init__(self,
                 username,
                 password,
                 site='https://tutor-qa.openstax.org',
                 email=None,
                 email_username=None,
                 email_password=None,
                 driver_type='chrome',
                 capabilities=None,
                 pasta_user=None,
                 wait_time=DEFAULT_WAIT_TIME,
                 opera_driver='',
                 existing_driver=None,
                 **kwargs):
        """
        Base user constructor.

        username (string): website username
        password (string): website password
        site (string): website URL
        driver_type (string): web browser type
        pasta_user (PastaSauce): optional API access for saucelabs
        capabilities (dict): browser settings; copy object to avoid overwrite
            Defaults:
                DesiredCapabilities.ANDROID.copy()
                DesiredCapabilities.CHROME.copy()
                DesiredCapabilities.EDGE.copy()
                DesiredCapabilities.FIREFOX.copy()
                DesiredCapabilities.HTMLUNIT.copy()
                DesiredCapabilities.HTMLUNITWITHJS.copy()
                DesiredCapabilities.INTERNETEXPLORER.copy()
                DesiredCapabilities.IPAD.copy()
                DesiredCapabilities.IPHONE.copy()
                DesiredCapabilities.ORERA.copy()
                DesiredCapabilities.PHANTOMJS.copy()
                DesiredCapabilities.SAFARI.copy()
            Keys:
                platform
                browserName
                version
                javascriptEnabled
        wait (int): standard time, in seconds, to wait for Selenium commands
        opera_driver (string): Chromium location
        """
        self.username = username
        self.password = password
        self.url = self.url_parse(site)
        self.email = email
        self.email_username = email_username
        self.email_password = email_password
        self.assign = Assignment()
        self.course_dates = (None, None)
        super(User, self).__init__(driver_type=driver_type,
                                   capabilities=capabilities,
                                   pasta_user=pasta_user,
                                   wait_time=wait_time,
                                   opera_driver=opera_driver,
                                   existing_driver=existing_driver,
                                   **kwargs)

    def accept_contract(self):
        """Contract acceptance for Terms of Service and the Privacy Policy."""
        checkbox_id = 'agreement_i_agree' if 'accounts' in \
            self.current_url() else 'i_agree'
        try:
            target = self.find(By.ID, checkbox_id)
            self.scroll_to(target)
            target.click()
            target = self.find(By.ID, 'agreement_submit')
            self.scroll_to(target)
            target.click()
        except Exception as e:
            raise e

    def login(self, url=None, username=None, password=None):
        """Tutor login control.

        If parameters are not passed, log in using the class values.
        Branching to deal with standard or compact screen widths

        username (string): website username
        password (string): website password
        url (string): website URL
        """
        username = self.username if not username else username
        password = self.password if not password else password
        url_address = self.url if not url else self.url_parse(url)
        # open the URL
        self.get(url_address)
        if 'tutor' in url_address:
            login = self.wait.until(
                expect.presence_of_element_located(
                    (By.CSS_SELECTOR, '.login')
                )
            )
            self.scroll_to(login)
            login.click()
            self.page.wait_for_page_load()
        elif 'exercises' in url_address:
            self.find(By.LINK_TEXT, 'Sign in').click()
            self.page.wait_for_page_load()
        src = self.driver.page_source
        text_located = re.search(r'openstax', src.lower())
        self.sleep(1)
        if not text_located:
            raise LoginError('Non-OpenStax URL: %s' % self.driver.current_url)
        # enter the username and password
        self.find(By.ID, 'login_username_or_email').send_keys(username)
        self.find(By.CSS_SELECTOR, '.primary').click()
        self.find(By.ID, 'login_password').send_keys(password)
        self.find(By.CSS_SELECTOR, '.primary').click()
        self.page.wait_for_page_load()
        # check if a password change is required
        if 'reset your password' in self.driver.page_source.lower():
            try:
                self.find(By.ID, 'set_password_password') \
                    .send_keys(self.password)
                self.find(By.ID, 'set_password_password_confirmation') \
                    .send_keys(self.password)
                self.find(By.CSS_SELECTOR, '.primary').click()
                self.sleep(1)
                self.find(By.CSS_SELECTOR, '.primary').click()
            except Exception as e:
                raise e
        self.page.wait_for_page_load()
        source = self.driver.page_source.lower()
        while 'terms of use' in source or 'privacy policy' in source:
            self.accept_contract()
            self.page.wait_for_page_load()
            source = self.driver.page_source.lower()
        return self

    def logout(self):
        """Logout control."""
        url_address = self.current_url()
        if 'tutor' in url_address:
            self.tutor_logout()
        elif 'accounts' in url_address:
            self.accounts_logout()
        elif 'exercises' in url_address:
            self.exercises_logout()
        else:
            raise HTTPError('Not an OpenStax URL')

    def current_url(self):
        """Return the current browser URL."""
        return self.driver.current_url

    def goto_course_list(self):
        """Go to the course picker."""
        long_wait = WebDriverWait(self.driver, 30)
        try:
            long_wait.until(
                expect.presence_of_element_located(
                    (By.ID, 'ox-react-root-container')
                )
            )
            if 'tutor' in self.current_url():
                self.find(By.CSS_SELECTOR, '.ui-brand-logo').click()
                self.page.wait_for_page_load()
            else:
                raise HTTPError('Not currently on an OpenStax Tutor webpage:' +
                                ' %s' % self.current_url())
        except Exception as ex:
            raise ex

    def get_course_list(self, closed=False):
        """Return a list of available courses."""
        self.wait.until(
            expect.visibility_of_element_located(
                (By.TAG_NAME, 'h1')
            )
        )
        courses = self.find_all(
            By.CSS_SELECTOR,
            '.my-courses-current-section .my-courses-item'
        )
        if len(courses) == 0:
            print('No courses found')
            return []
        for position, course in enumerate(courses):
            print('%s : "%s"' % (position, course.get_attribute('data-title')))
        return courses

    def open_action_menu(self):
        """Course action menu opener."""
        self.wait.until(
            expect.visibility_of_element_located(
                (By.ID, 'actions-menu')
            )
        ).click()

    def open_user_menu(self):
        """Hamburger (user) menu opener."""
        self.wait.until(
            expect.visibility_of_element_located(
                (By.ID, 'user-menu')
            )
        ).click()

    def goto_menu_item(self, item):
        """Go to a specific user menu item."""
        if item.lower() == 'my account' or item.lower() == 'log out':
            self.open_user_menu()
        else:
            self.open_action_menu()
        print('Select menu item %s' % item)
        self.wait.until(
            expect.element_to_be_clickable(
                (By.LINK_TEXT, item)
            )
        ).click()
        self.page.wait_for_page_load()

    def tutor_logout(self):
        """Tutor logout helper."""
        self.open_user_menu()
        self.wait.until(
            expect.visibility_of_element_located(
                (By.CSS_SELECTOR, 'input[type=submit]')
            )
        ).click()
        self.page.wait_for_page_load()

    def accounts_logout(self):
        """OS Accounts logout helper."""
        self.find(By.CSS_SELECTOR, '.sign-out').click()
        self.page.wait_for_page_load()

    def execises_logout(self):
        """Exercises logout helper."""
        wait = WebDriverWait(self.driver, 3)
        try:
            wait.until(
                expect.element_to_be_clickable(
                    (By.ID, 'navbar-dropdown')
                )
            ).click()
            wait.until(
                expect.element_to_be_clickable(
                    (By.CSS_SELECTOR, '[type="submit"]')
                )
            ).click()
            self.page.wait_for_page_load()
        except NoSuchElementException:
            # Different page, but uses the same logic and link text
            self.find(By.CSS_SELECTOR, '[data-method]').click()

    def is_modal_present(self, by, value):
        try:
            self.find(by, value)
        except Exception:
            return False
        return True

    def close_beta_windows(self):
        """Close the beta windows if it shows."""
        store_wait = self.wait_time
        self.change_wait_time(1)
        while self.is_modal_present(By.CLASS_NAME,
                                    'joyride-tooltip__button--primary'):
            self.sleep(0.5)
            self.find(By.CLASS_NAME, 'joyride-tooltip__button--primary') \
                .click()
        try:
            self.find(By.XPATH, '//button[span[text()="Submit"]]')
        except Exception:
            pass
        try:
            self.find(By.CSS_SELECTOR, '.onboarding-nag')
            responses = self.find_all(By.CSS_SELECTOR, '.footer .btn')
            responses[randint(0, len(responses) - 1)].click()
            self.find(By.CSS_SELECTOR, '.footer.got-it button').click()
        except Exception:
            # onboarding nag isn't shown
            pass
        # reset wait time
        self.change_wait_time(store_wait)

    def select_course(self, title=None, appearance=None):
        """Select course."""
        print('Select course "%s" / "%s"' % (title, appearance))
        if 'dashboard' not in self.current_url():
            # If not at the dashboard, try to load it
            self.goto_course_list()
        if 'dashboard' not in self.current_url():
            # Only has one course and the user is at the dashboard so return
            print('Single course; select course complete')
            return
        if appearance:
            if 'sociology' in appearance.lower():
                appearance = 'intro_sociology'
            elif 'biology' in appearance.lower():
                appearance = 'college_biology'
            else:
                appearance = 'college_physics'
        if title:
            uses_option = 'title'
            course = title
        elif appearance:
            uses_option = 'appearance'
            course = appearance
        else:
            raise LoginError('Unknown course selection "%s"' %
                             title if title else appearance, None)
        select = self.wait.until(
            expect.element_to_be_clickable(
                (
                    By.XPATH,
                    '//div[@data-%s="%s"]//a' % (uses_option, course)
                )
            )
        )
        print('Course: %s - %s' % (title if title else appearance,
                                   select.get_attribute('href')))
        self.close_beta_windows()
        select.click()
        self.page.wait_for_page_load()
        self.close_beta_windows()
        # agree the terms of use
        try:
            old_wait = self.wait_time
            self.change_wait_time(1.5)
            self.find(By.CLASS_NAME, 'btn-primary').click()
        except Exception:
            pass
        finally:
            if old_wait != self.wait_time:
                self.change_wait_time(old_wait)
        return self

    def view_reference_book(self):
        """Access the reference book."""
        try:
            # try the calendar button
            self.find(
                By.CSS_SELECTOR,
                '.calendar-header .view-reference-guide') \
                .click()
            return
        except Exception:
            pass
        # try the user menu link
        self.goto_menu_item('Browse the Book')


class Teacher(User):
    """User extention for teachers."""

    CONDENSED_WIDTH = User.CONDENSED_WIDTH
    DEFAULT_WAIT_TIME = User.DEFAULT_WAIT_TIME

    def __init__(self,
                 use_env_vars=False,
                 existing_driver=None,
                 driver_type='chrome',
                 **kwargs):
        """Teacher initialization with User pass-through."""
        if use_env_vars:
            if not kwargs:
                kwargs = {}
            kwargs['username'] = os.getenv('TEACHER_USER')
            kwargs['password'] = os.getenv('TEACHER_PASSWORD')
            kwargs['site'] = os.getenv('SERVER_URL')
            kwargs['email'] = os.getenv('TEST_EMAIL_ACCOUNT')
            kwargs['email_username'] = os.getenv('TEST_EMAIL_USER')
            kwargs['email_password'] = os.getenv('TEST_EMAIL_PASSWORD')
        super(Teacher, self).__init__(existing_driver=existing_driver,
                                      driver_type=driver_type,
                                      **kwargs)

    def switch_user(self, username):
        """Switch username during chained actions."""
        self.username = username
        return self

    def add_assignment(self, assignment, args):
        """Add an assignment."""
        print('Assignment: %s' % args['title'])
        self.goto_calendar()
        self.assign.open_assignment_menu(self.driver)
        self.assign.add[assignment](
            driver=self.driver,
            name=args['title'],
            description=args['description'] if 'description' in args else '',
            periods=args['periods'],
            state=args['status'],
            url=args['url'] if 'url' in args else None,
            reading_list=args['reading_list'] if 'reading_list' in args
            else None,
            problems=args['problems'] if 'problems' in args else None,
            feedback=args['feedback'] if 'feedback' in args else None
        )

    def change_assignment(self, assignment, args):
        """Alter an existing assignment."""
        print('Assignment: %s' % args['title'])
        self.goto_calendar()
        self.assign.edit[assignment](
            driver=self.driver,
            name=args['title'],
            description=args['description'],
            periods=args['periods'],
            state=args['status'],
            url=args['url'] if 'url' in args else None,
            reading_list=args['reading_list'] if 'reading_list' in args else
            None,
            problems=args['problems'] if 'problems' in args else None,
            feedback=args['feedback'] if 'feedback' in args else None,
        )

    def delete_assignment(self, assignment, args):
        """Delete an existing assignment (if available)."""
        print('Assignment: %s' % args['title'])
        self.goto_calendar()
        self.assign.remove[assignment](
            driver=self.driver,
            name=args['title'],
            description=args['description'] if 'description' in args else None,
            periods=args['periods'] if 'periods' in args else None,
            state=args['status'] if 'status' in args else None,
            url=args['url'] if 'url' in args else None,
            reading_list=args['reading_list'] if 'reading_list' in args else
            None,
            problems=args['problems'] if 'problems' in args else None,
            feedback=args['feedback'] if 'feedback' in args else None,
        )

    def goto_calendar(self):
        """Return the teacher to the calendar dashboard."""
        if not self.current_url().endswith('/t'):
            self.goto_menu_item('Dashboard')
        self.page.wait_for_page_load()

    def goto_performance_forecast(self):
        """Access the performance forecast page."""
        self.goto_menu_item('Performance Forecast')
        timer = 0
        while timer < 10:
            try:
                print('Wait for forecast load try %s of 10' % (timer + 1))
                self.wait.until(
                    expect.visibility_of_element_located(
                        (By.CLASS_NAME, 'guide-container')
                    )
                )
                timer = 10
            except Exception:
                timer = timer + 1

    def goto_student_scores(self):
        """Access the student scores page."""
        self.goto_menu_item('Student Scores')

    def goto_course_roster(self):
        """Access the course roster page."""
        self.goto_menu_item('Course Roster')

    def goto_course_settings(self):
        """Access the course settings page."""
        self.goto_menu_item('Course Settings')

    def get_course_sections(self):
        """Return the list of course sections currently active."""
        if 'roster' not in self.current_url():
            self.goto_course_roster()
        try:
            self.find(By.CSS_SELECTOR, '.no-periods-message')
            return []
        except Exception:
            pass
        tabs = self.find_all(By.CSS_SELECTOR, '.nav-tabs h2')
        return [tab.get_attribute('innerHTML') for tab in tabs]

    def add_course_section(self, section_name):
        """Add a section to the course."""
        if 'roster' not in self.current_url():
            self.goto_course_roster()
        self.find(By.CSS_SELECTOR, '.add-period').click()
        self.wait.until(
            expect.visibility_of_element_located(
                (By.CSS_SELECTOR, '.form-control')
            )
        ).send_keys(section_name)
        self.find(By.CSS_SELECTOR, '.-edit-period-confirm').click()

    def get_enrollment_code(self, section_name=None, random=False):
        """Return the enrollment code for a class section."""
        if 'settings' not in self.current_url():
            self.goto_course_settings()

        try:
            self.find(By.CSS_SELECTOR, '.direct-links-only')
        except Exception:
            print('Switch board to direct access URLs')
            direct_enrollment = self.find(By.CSS_SELECTOR, '[role=tab]')
            if direct_enrollment.get_attribute('aria-selected') != 'true':
                direct_enrollment.click()
                self.find(By.CSS_SELECTOR, '.modal-footer button').click()

        enrollment_urls = self.find_all(By.CSS_SELECTOR, '[readonly]')
        if section_name:
            enrollment_url = self.find(
                By.XPATH,
                '//label[contains(text(), "%s")]/input' % section_name
            ).get_attribute('value')
        else:
            enrollment_urls = self.find_all(By.CSS_SELECTOR, '[readonly]')
            position = randint(0, 0 if not random else len(enrollment_urls))
            enrollment_url = enrollment_urls[position] \
                .get_attribute('value')

        return enrollment_url

    def get_book_sections(self):
        """Return a list of book sections."""
        self.close_beta_windows()
        sleep(1)
        self.goto_calendar()
        self.assign.open_assignment_menu(self.driver)
        self.find(By.LINK_TEXT, 'Add Reading').click()
        self.page.wait_for_page_load()
        self.wait.until(
            expect.element_to_be_clickable(
                (By.ID, 'reading-select')
            )
        ).click()
        self.page.wait_for_page_load()
        for chapter in \
                self.find_all(By.CSS_SELECTOR, 'div.chapter-heading > a'):
            if chapter.get_attribute('aria-expanded') != 'true':
                self.scroll_to(chapter)
                sleep(0.25)
                chapter.click()
        sections = self.find_all(By.CSS_SELECTOR, '.section .chapter-section')
        section_list = []
        for section in sections:
            section_list.append(section.text)
        print('Section options: %s' % str(section_list))
        self.goto_calendar()
        return section_list

    def get_course_begin_end(self):
        """Return the course start and end dates as timedate objects."""
        if 'course' not in self.current_url():
            raise CourseSelectionError('No course selected')
        self.goto_course_settings()
        self.find(By.LINK_TEXT, 'DATES AND TIME').click()
        course_time_periods = self.find_all(
            By.CSS_SELECTOR,
            '.dates-and-times div'
        )
        if len(course_time_periods) < 3:
            raise CourseSelectionError(
                'Course start and end dates not found',
                None
            )
        dates = course_time_periods[1].get_attribute('innerHTML')
        begin = dates.split('>')[3].split('<')[0]
        end = dates.split('>')[7].split('<')[0]
        print('Course start: "%s"  Course end: "%s"' % (begin, end))
        self.goto_calendar()
        return (datetime.datetime.strptime(begin, '%m/%d/%Y'),
                datetime.datetime.strptime(end, '%m/%d/%Y'))

    def date_is_valid(self, date):
        """Return boolean if end_date >= date >= start_date."""
        print('Date validity check: {0} : {1}'.format(str(date), type(date)))
        if not isinstance(date, datetime.date):
            date = datetime.strptime(date, '%m/%d/%Y')
        date = datetime.datetime(date.year, date.month, date.day)
        start, end = self.get_course_begin_end()
        delta = timedelta(0)
        print('{0} <= {1} <= {2}'.format(str(start), str(date), str(end)))
        if date - start == delta or end - date == delta:
            return True
        return date > start and date < end

    def get_month_number(self, month):
        """Take a string month and return its numberic."""
        months = {v: k for k, v in enumerate(calendar.month_name)}
        return months[month]

    def get_month_year(self):
        """Break a date string into a month year tuple."""
        calendar_heading = self.find(
            By.CSS_SELECTOR,
            '.calendar-header-label'
        )
        Assignment.scroll_to(self.driver, calendar_heading)
        calendar_date = calendar_heading.text
        month, year = calendar_date.split(' ')
        return self.get_month_number(month), int(year)

    def rotate_calendar(self, target):
        """Rotate the teacher calendar to a specific month and year."""
        cal_month, cal_year = self.get_month_year()
        target_date = datetime.datetime.strptime(target, '%m/%d/%Y').date()
        if cal_year == target_date.year and cal_month == target_date.month:
            return
        if cal_year < target_date.year or \
                (cal_year == target_date.year and
                 cal_month < target_date.month):
            arrow = 'fa-caret-right'
        elif cal_year > target_date.year or \
                (cal_year == target_date.year and
                 cal_month > target_date.month):
            arrow = 'fa-caret-left'
        self.find(By.CLASS_NAME, arrow).click()
        sleep(0.2)
        self.rotate_calendar(target)

    def enable_debug_mode(self):
        """Enable spy mode for training wheels."""
        self.find(By.CLASS_NAME, 'debug-toggle-link').click()
        sleep(1)
        return self


class Student(User):
    """User extention for students."""

    CONDENSED_WIDTH = User.CONDENSED_WIDTH
    DEFAULT_WAIT_TIME = User.DEFAULT_WAIT_TIME

    def __init__(self,
                 use_env_vars=False,
                 existing_driver=None,
                 driver_type='chrome',
                 **kwargs):
        """Student initialization with User pass-through."""
        if use_env_vars:
            if not kwargs:
                kwargs = {}
            kwargs['username'] = os.getenv('STUDENT_USER')
            kwargs['password'] = os.getenv('STUDENT_PASSWORD')
            kwargs['site'] = os.getenv('SERVER_URL')
            kwargs['email'] = os.getenv('TEST_EMAIL_ACCOUNT')
            kwargs['email_username'] = os.getenv('TEST_EMAIL_USER')
            kwargs['email_password'] = os.getenv('TEST_EMAIL_PASSWORD')
        super(Student, self).__init__(existing_driver=existing_driver,
                                      driver_type=driver_type,
                                      **kwargs)

    def goto_dashboard(self):
        """Go to current work."""
        self.goto_menu_item('Dashboard')

    def pay_for_student(self,
                        street, city, state, zip_,
                        card, exp, cvv, billing_zip):
        """Pay for student access."""
        if 'free trial for' in self.driver.source:

            self.find(By.CLASS_NAME, 'btn-primary').click()
            self.wait.until(
                expect.visibility_of_element_located(
                    (By.CSS_SELECTOR, 'div.checkout')
                )
            )
            self.find(By.CSS_SELECTOR, '[name=street_address]') \
                .send_keys(street)
            self.find(By.CSS_SELECTOR, '[name=city]') \
                .send_keys(city)
            select = Select(self.driver.find_element_by_name('state'))
            if len(state) == 2:
                select.select_by_value(state.upper())
            else:
                select.select_by_visible_text(state.title())
            self.find(By.CSS_SELECTOR, '[name=zip_code]') \
                .send_keys(zip_)
            self.driver.switch_to.frame(
                self.scroll_to(
                    self.find(By.ID, 'braintree-hosted-field-number')))
            self.find(By.ID, 'credit-card-number') \
                .send_keys(card)
            self.driver.switch_to.frame(
                self.find(By.ID, 'braintree-hosted-field-expirationDate'))
            self.find(By.ID, 'expiration') \
                .send_keys(exp)
            self.driver.switch_to.frame(
                self.find(By.ID, 'braintree-hosted-field-cvv'))
            self.find(By.ID, 'cvv') \
                .send_keys(cvv)
            self.driver.switch_to.frame(
                self.find(By.ID, 'braintree-hosted-field-postalCode'))
            self.find(By.ID, 'postal-code') \
                .send_keys(billing_zip)
            self.driver.switch_to.default_content()
            self.find(By.CLASS_NAME, 'purchase').click()
            self.wait.until(
                expect.visibility_of_element_located(
                    (By.CSS_SELECTOR, '.order-complete')
                )
            )
            self.scroll_to(self.find(By.CSS_SELECTOR, 'footer button')).click()

    def work_assignment(self):
        """Work an assignment."""
        if '/courses/' not in self.current_url():
            self.find(By.XPATH, '//a[contains(@class,"na")]')
        self.wait.until(
            expect.element_to_be_clickable(
                (By.LINK_TEXT, 'All Past Work')
            )
        )
        raise NotImplementedError(inspect.currentframe().f_code.co_name)

    def goto_past_work(self):
        """View work for previous weeks."""
        self.goto_dashboard()
        self.wait.until(
            expect.element_to_be_clickable(
                (By.LINK_TEXT, 'All Past Work')
            )
        ).click()
        self.page.wait_for_page_load()

    def goto_performance_forecast(self):
        """View the student performance forecast."""
        self.goto_menu_item('Performance Forecast')

    def practice(self, practice_set='weakest'):
        """Complete a set of up to 5 practice problems."""
        options = []
        self.goto_dashboard()
        # Wait for the student performance meters to load
        try:
            print('Loading Performance Forecast')
            WebDriverWait(self.driver, 60).until(
                expect.staleness_of(
                    (By.CLASS_NAME, 'is-loading')
                )
            )
        except Exception:
            pass
        finally:
            self.sleep(2)
        # Select a section or the weakest topic to practice
        options.append(
            self.wait.until(
                expect.visibility_of_element_located(
                    (By.CLASS_NAME, 'practice')
                )
            )
        )
        if practice_set == 'weakest':
            options[0].click()
            self.page.wait_for_page_load()
        else:
            try:
                sections = self.find_all(
                    By.XPATH,
                    '//button[contains(@aria-describedby,' +
                    '"progress-bar-tooltip-")]'
                )
                for section in sections:
                    options.append(section)
            except Exception:
                pass
            finally:
                options[randint(0, len(options) - 1)].click()
                self.page.wait_for_page_load()
        # How many questions are there? (default = 5)
        breadbox = self.wait.until(
            expect.presence_of_element_located(
                (By.CLASS_NAME, 'task-breadcrumbs')
            )
        )
        crumbs = breadbox.find_elements(By.TAG_NAME, 'span')
        # Answer each assessment
        for _ in repeat(None, len(crumbs) - 1):
            self.answer_assessment()
        # Finish the practice
        self.wait.until(
            expect.element_to_be_clickable(
                (By.XPATH, '//a[contains(text(),"Dashboard") and' +
                 ' contains(@class,"btn")]')
            )
        ).click()
        self.page.wait_for_page_load()

    def answer_assessment(self):
        """Answer a Tutor assessment."""
        self.wait.until(
            expect.presence_of_element_located(
                (By.CLASS_NAME, 'openstax-question')
            )
        )
        text = chomsky(1, 500)
        wt = self.wait_time
        try:
            self.change_wait_time(3)
            text_block = self.find(By.XPATH, '//textarea')
            self.change_wait_time(wt)
            print('Enter free response')
            Assignment.send_keys(self.driver, text_block, text)
            self.find(By.CLASS_NAME, 'continue').click()
        except Exception:
            self.change_wait_time(wt)
            print('Skip free response')
        finally:
            self.page.wait_for_page_load()
        answers = self.find_all(By.CLASS_NAME, 'answer-letter')
        self.sleep(0.8)
        rand = randint(0, len(answers) - 1)
        answer = chr(ord('a') + rand)
        print('Selecting %s' % answer)
        self.scroll_to(answers[0])
        if answer == 'a':
            self.driver.execute_script('window.scrollBy(0, -160);')
        elif answer == 'd':
            self.driver.execute_script('window.scrollBy(0, 160);')
        answers[rand].click()
        self.sleep(1.0)
        self.wait.until(
            expect.element_to_be_clickable(
                (By.XPATH, '//button[span[text()="Submit"]]')
            )
        ).click()
        self.wait.until(
            expect.element_to_be_clickable(
                (By.CLASS_NAME, 'continue')
            )
        ).click()
        self.page.wait_for_page_load()


class Admin(User):
    """User extention for administrators."""

    CONDENSED_WIDTH = User.CONDENSED_WIDTH
    DEFAULT_WAIT_TIME = User.DEFAULT_WAIT_TIME

    def __init__(self, use_env_vars=False, existing_driver=None,
                 driver_type='chrome', **kwargs):
        """Administrator initialization with User pass-through."""
        if use_env_vars:
            if not kwargs:
                kwargs = {}
            kwargs['username'] = os.getenv('ADMIN_USER')
            kwargs['password'] = os.getenv('ADMIN_PASSWORD')
            kwargs['site'] = os.getenv('SERVER_URL')
            kwargs['email'] = os.getenv('TEST_EMAIL_ACCOUNT')
            kwargs['email_username'] = os.getenv('TEST_EMAIL_USER')
            kwargs['email_password'] = os.getenv('TEST_EMAIL_PASSWORD')
        super(Admin, self).__init__(existing_driver=existing_driver,
                                    driver_type=driver_type,
                                    **kwargs)
        extension = '' if self.url.endswith('/') else '/'
        self.base = self.url + extension + 'admin'

    def goto_admin_control(self):
        """Access the administrator controls."""
        self.get('%s' % self.base)

    def goto_catalog_offerings(self):
        """Access the catalog."""
        self.get('%s%s' % (self.base, '/catalog_offerings'))

    def goto_course_list(self):
        """Access the course list."""
        self.get('%s%s' % (self.base, '/courses'))

    def goto_school_list(self):
        """Access the school list."""
        self.get('%s%s' % (self.base, '/school'))

    def goto_district_list(self):
        """Access the district list."""
        self.get('%s%s' % (self.base, '/districts'))

    def goto_tag_list(self):
        """Access the tag list."""
        self.get('%s%s' % (self.base, '/tags'))

    def goto_ecosystems(self):
        """Access the ecosystem list."""
        self.get('%s%s' % (self.base, '/ecosystems'))

    def goto_terms_and_contracts(self):
        """Access the terms and contracts list."""
        self.get('%s%s' % (self.url, '/fine_print'))

    def goto_contracts(self):
        """Access the targeted contracts."""
        self.get('%s%s' % (self.base, '/targeted_contracts'))

    def goto_course_stats(self):
        """Access the course stats."""
        self.get('%s%s' % (self.base, '/stats/courses'))

    def goto_concept_coach_stats(self):
        """Access the Concept Coach stats."""
        self.get('%s%s' % (self.base, '/stats/concept_coach'))

    def goto_user_list(self):
        """Access the user list."""
        self.get('%s%s' % (self.base, '/users'))

    def goto_jobs(self):
        """Access the jobs list."""
        self.get('%s%s' % (self.base, '/jobs'))

    def goto_research_data(self):
        """Access the researcher data."""
        self.get('%s%s' % (self.base, '/research_data'))

    def goto_salesforce_control(self):
        """Access the Salesforce controls."""
        self.get('%s%s' % (self.base, '/salesforce'))

    def goto_system_settings(self):
        """Access the system settings."""
        self.get('%s%s' % (self.base, '/settings'))

    def goto_system_notifications(self):
        """Access the system notifications."""
        self.get('%s%s' % (self.base, '/notifications'))


class ContentQA(User):
    """User extention for content users."""

    CONDENSED_WIDTH = User.CONDENSED_WIDTH
    DEFAULT_WAIT_TIME = User.DEFAULT_WAIT_TIME

    def __init__(self, use_env_vars=False, existing_driver=None,
                 driver_type='chrome', **kwargs):
        """Content analyst initialization with User pass-through."""
        if use_env_vars:
            if not kwargs:
                kwargs = {}
            kwargs['username'] = os.getenv('CONTENT_USER')
            kwargs['password'] = os.getenv('CONTENT_PASSWORD')
            kwargs['site'] = os.getenv('SERVER_URL')
            kwargs['email'] = os.getenv('TEST_EMAIL_ACCOUNT')
            kwargs['email_username'] = os.getenv('TEST_EMAIL_USER')
            kwargs['email_password'] = os.getenv('TEST_EMAIL_PASSWORD')
        super(ContentQA, self).__init__(existing_driver=existing_driver,
                                        driver_type=driver_type,
                                        **kwargs)


class Webview(Helper):
    """Webview navigation and control."""

    CONDENSED_WIDTH = Helper.CONDENSED_WIDTH
    DEFAULT_WAIT_TIME = Helper.DEFAULT_WAIT_TIME

    def __init__(self,
                 driver_type='chrome',
                 capabilities=None,
                 pasta_user=None,
                 wait_time=DEFAULT_WAIT_TIME,
                 remote_driver='',
                 existing_driver=None,
                 **kwargs):
        """Webview constructor."""
        self.course_dates = (None, None)
        super(Webview, self).__init__(driver_type=driver_type,
                                      capabilities=capabilities,
                                      pasta_user=pasta_user,
                                      wait_time=wait_time,
                                      existing_driver=existing_driver,
                                      **kwargs)

    def goto_section(self, section_name=None, section_number=None):
        """Go to a specific page module."""
        raise NotImplementedError(inspect.currentframe().f_code.co_name)

    def next(self):
        """Go to the next page module."""
        raise NotImplementedError(inspect.currentframe().f_code.co_name)

    def previous(self):
        """Go to the previous page module."""
        raise NotImplementedError(inspect.currentframe().f_code.co_name)


class CourseSelectionError(Exception):
    """Course selection failure exception."""

    def __init__(self, msg='', err=None):
        """Exception initializer."""
        self.msg = msg
        self.__traceback__ = err

    def __repr__(self):
        """Return __str__ print."""
        return self.__str__()

    def __str__(self):
        """String representation of the exception."""
        try:
            return str(self.msg).join(str(self.__traceback__))
        except Exception as e:
            return str(type(e)).join(str(e))


class LoginError(Exception):
    """Login error exception."""

    def __init__(self, msg='', err=None):
        """Exception initializer."""
        self.msg = msg
        self.__traceback__ = err

    def __repr__(self):
        """Return __str__ print."""
        return self.__str__()

    def __str__(self):
        """String representation of the exception."""
        try:
            return str(self.msg).join(str(self.__traceback__))
        except Exception as e:
            return str(type(e)).join(str(e))


class WebDriverTypeException(WebDriverException):
    """Exception for unknown WebDriver types."""

    def __init__(self, msg='', err=None):
        """Exception initializer."""
        self.msg = msg
        self.__traceback__ = err

    def __repr__(self):
        """Return __str__ print."""
        return self.__str__()

    def __str__(self):
        """String representation of the exception."""
        try:
            return str(self.msg).join(str(self.__traceback__))
        except Exception as e:
            return str(type(e)).join(str(e))


if __name__ == '__main__':  # pragma: no cover
    # execute if run as a script
    initialization = Helper
