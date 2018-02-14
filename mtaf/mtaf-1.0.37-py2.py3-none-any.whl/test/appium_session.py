from time import sleep
from lib.android_actions import android_actions
android_actions.open_appium('query_device')
print "opened appium"
# returned_caps = base_view.driver.capabilities
# sleep(5)
# base_view.close_appium()
# print "closed appium"
#
# sleep(15)
# base_view.open_appium('caps_arg', caps_arg=returned_caps)
# print "reopened appium (1)"
# returned_caps = base_view.driver.capabilities
# sleep(5)
# base_view.close_appium()
# print "closed appium"
#
# sleep(15)
# base_view.open_appium('caps_arg', caps_arg=returned_caps)
# print "reopened appium (2)"
# returned_caps = base_view.driver.capabilities
# sleep(5)
# base_view.close_appium()
# print "closed appium"
