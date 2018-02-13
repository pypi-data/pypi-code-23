from time import time
import mtaf_logging
from trace import Trace
from selenium_actions import SeleniumActions
from appium import webdriver
from appium.webdriver.common.touch_action import TouchAction
from selenium.common.exceptions import WebDriverException
from user_exception import UserException as Ux
from time import strftime, localtime
from PIL import Image
import os
from ADB import ADB
import re
from requests import ConnectionError
import six

log = mtaf_logging.get_logger('mtaf.android_actions')

selenium_url = "http://localhost:4723/wd/hub"


class AndroidActions(SeleniumActions):
    driver = None
    adb = ADB()

    def open_browser(self, browser=None):
        raise Ux('open_browser method not available using Appium')

    def close_browser(self):
        raise Ux('close_browser method not available using Appium')

    def open_appium(self, connect_timeout=10):
        if len(self.adb.get_devices()) == 0:
            raise Ux("no ADB device")
        output = self.adb.run_cmd('shell dumpsys window windows')
        package = re.match('(?ms).*mCurrentFocus=\S+\s+\S+\s+([^/]+)([^}]+)', output).group(1)
        activity = re.match('(?ms).*mCurrentFocus=\S+\s+\S+\s+([^/]+)/([^}]+)', output).group(2)
        device_name = self.adb.run_cmd('shell getprop ro.product.model').strip()
        platform_version = self.adb.run_cmd('shell getprop ro.build.version.release').strip()
        caps = {
                "appPackage": package,
                "appActivity": activity,
                "autoLaunch": False,
                "automationName": "Appium",
                "deviceName": device_name,
                "newCommandTimeout": 1200,
                "noReset": True,
                "platformName": "Android",
                "platformVersion": platform_version
            }
        start_time = time()
        while time() - start_time < connect_timeout:
            try:
                AndroidActions.driver = webdriver.Remote(selenium_url, caps)
                break
            except WebDriverException:
                log.info("retrying webdriver.Remote(%s, %s)" % (selenium_url, caps))
            except ConnectionError as e:
                six.print_("ConnectionError attempting to connect to appium server: %s" % e)
                raise Ux("ConnectionError attempting to connect to appium server")
        else:
            raise Ux("failed to connect webdriver.Remote within %s seconds" % connect_timeout)

    @Trace(log)
    def close_appium(self):
        if self.driver is None:
            log.debug('appium is already closed')
        else:
            log.debug('closing appium')
            try:
                logcat = self.driver.get_log('logcat')
                timestamp = strftime('%m_%d_%y-%H_%M_%S', localtime())
                logdir = os.getenv('MTAF_LOG_DIR', 'log')
                with open('%s/logcat_%s.log' % (logdir, timestamp), 'w') as f:
                    for line in [item['message'] for item in logcat]:
                        f.write(line.encode('utf-8') + '\n')
                # self.driver.quit()
            except WebDriverException:
                log.debug("got WebDriverException, assuming appium already closed")
            AndroidActions.driver = None

    @Trace(log)
    def get_element_color_and_count(self, screenshot_dir, filebase, elem, cropped_suffix='', color_list_index=1):
        im = Image.open(os.path.join(screenshot_dir, filebase + '.png'))
        # calculate image crop points from element location['x'], location['y'], size['height'] and size['width']
        location = elem.location
        size = elem.size
        min_x = location['x']
        min_y = location['y']
        lim_x = min_x + size['width']
        lim_y = min_y + size['height']
        # print "min_x = %s, min_y = %s, lim_x = %s, lim_y = %s" % (min_x, min_y, lim_x, lim_y)
        # (x1, y1, x2, y2) = (min_y, 600-lim_x, lim_y, 600-min_x)
        (x1, y1, x2, y2) = (min_x, min_y, lim_x, lim_y)
        crop_points = [int(i) for i in (x1, y1, x2, y2)]
        # print "crop_points: " + repr(crop_points)
        cropped = im.crop(crop_points)
        cropped.save(os.path.join(screenshot_dir, 'cropped%s.png' % cropped_suffix))
        color_band = Image.new('RGBA', (crop_points[2] - crop_points[0], crop_points[3] - crop_points[1]), 'yellow')
        im.paste(color_band, crop_points, 0)
        im.save(os.path.join(screenshot_dir, filebase + '_after.png'))
        return self.get_image_color(cropped, color_list_index)

    @Trace(log)
    def get_image_color(self, image, color_list_index):
        colors = image.getcolors(1000000)
        # print "# of colors: %s" % len(colors)
        if len(colors) > color_list_index:
            current_color_and_count = sorted(colors, reverse=True, key=lambda x: x[0])[color_list_index]
            current_color = list(current_color_and_count[1])[:-1]
            current_count = current_color_and_count[0]
            return current_color + [current_count]
        else:
            return None

    @Trace(log)
    def get_cropped_color(self, img_path, crop_points):
        im = Image.open(img_path)
        cropped = im.crop(crop_points)
        (n, (r, g, b, depth)) = max(cropped.getcolors(1000), key=lambda x: x[0])
        return [r, g, b]

    @Trace(log)
    def keyevent(self, code):
        log.debug("sending keyevent(%s)" % code)
        self.driver.keyevent(code)

    @Trace(log)
    def hide_keyboard(self):
        self.driver.hide_keyboard()

    @Trace(log)
    def long_press(self, element=None, x=None, y=None, duration=1000):
        TouchAction(self.driver).long_press(element, x, y, duration).perform()

    @Trace(log)
    def long_press_scroll(self, origin_el, destination_el):
        TouchAction(self.driver).long_press(origin_el).move_to(destination_el).release().perform()

    @Trace(log)
    def short_press_scroll(self, origin_el, destination_el):
        TouchAction(self.driver).press(origin_el).move_to(destination_el).release().perform()

    @Trace(log)
    def swipe(self, origin_x, origin_y, destination_x, destination_y, duration_ms=500):
        self.driver.swipe(origin_x, origin_y, destination_x, destination_y, duration_ms)

    @Trace(log)
    def long_press_swipe(self, x1, y1, x2, y2, duration=500):
        TouchAction(self.driver).long_press(x=x1, y=y1, duration=duration).move_to(x=x2, y=y2).release().perform()

    @Trace(log)
    def tap(self, positions, duration=200):
        self.driver.tap(positions, duration)

    @Trace(log)
    def get_screenshot_as_file(self, filepath, scale=None):
        self.driver.get_screenshot_as_file(filepath)
        im = Image.open(filepath)
        if im.getbbox()[2] == 1024:
            log.debug("rotating screenshot -90 degrees")
            im = im.rotate(-90, expand=True)
        if scale is not None:
            bbox = im.getbbox()
            log.debug("im.getbbox() = %s" % repr(bbox))
            im.thumbnail((int(bbox[2] * scale), int(bbox[3] * scale)), Image.ANTIALIAS)
        log.debug("saving rotated screenshot to %s" % filepath)
        im.save(filepath)

    @Trace(log)
    def get_current_activity(self):
        return self.driver.current_activity

    @Trace(log)
    def wait_activity(self, activity, timeout):
        return self.driver.wait_activity(activity, timeout)


android_actions = AndroidActions()
