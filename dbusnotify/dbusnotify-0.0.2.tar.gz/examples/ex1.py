#!/usr/bin/env python3
import os
import time
from dbusnotify import Messenger, write, Icon

try:
    icon_dir = os.path.join(os.path.dirname(__file__), 'images')
except NameError:
    icon_dir = os.path.join(os.getcwd(), 'images')
pngpath = lambda x: os.path.join(icon_dir, x)

with Messenger() as m:
    m.title = str((2, 2.0))
    m.hints['x'] = 200
    m.hints['y'] = 200
    m.replace = True
    m.app_name = 'ex1'
    m.write('Test one')
    time.sleep(1)
    m.write('Test two')
    time.sleep(0.5)

z = Messenger(poptime=1, title='ex1', app_name='ex1', replace=True)
z.write('Test three')
time.sleep(0.5)
z.close_notification()
z.close()

exn = 'ex1_2'
with Messenger(icon=pngpath('applet-critical.png'), app_name=exn) as m:
    m.replace = True
    m.title = exn.upper()
    m.write('Test four')
time.sleep(0.5)
write('Test five', title=exn.upper(), app_name=exn, replace_last=True)
time.sleep(0.5)
write('Test six', title=exn.upper(), poptime=0.5, app_name=exn, replace_last=True)

exn = 'ex1_3'
write('Showing gtk-media-play icon', title=exn.upper(), app_name=exn,
      replace_last=True, icon='gtk-media-play')

write('Showing floppy icon', title=exn.upper(), app_name=exn,
      replace_last=True, icon=Icon.gtk.floppy)

write('<b>Here</b> are <u>format</u> <i>options</i>')

