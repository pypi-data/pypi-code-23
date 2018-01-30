from ePhone7.config.configure import cfg
from ePhone7.views import *
base_view.open_appium('main')
if user_view.becomes_present():
    base_view.touch_element_with_text('Voicemail')
    if voicemail_view.becomes_present():
        voicemail_view.get_screenshot_as_png('voicemail', cfg.test_screenshot_folder)
        print voicemail_view.get_tab_color('voicemail', 'New')
        print voicemail_view.get_tab_color('voicemail', 'Saved')
        print voicemail_view.get_tab_color('voicemail', 'Trash')
    else:
        print "voicemail view did not appear"
else:
    print "user view did not appear"
