#!/usr/bin/env python3
import dbusnotify

icons = [
    'audio-volume-muted',
    'audio-volume-low',
    'audio-volume-medium',
    'audio-volume-high',
]


# Make notifications for audio status
# replace previous notification
from time import sleep
for icon in icons:
    status = icon.split('-')[-1]
    dbusnotify.write(
        'Volume is <u>{}</u>'.format(status),
        title='Audio Status',
        icon=icon,
        replace_last=True,
    )
    sleep(1.0)


# Make notifications for audio status
# do not replace previous notification
for icon in icons:
    status = icon.split('-')[-1]
    dbusnotify.write(
        'Volume is <u>{}</u>'.format(status),
        title='Audio Status',
        icon=icon,
    )

