#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, absolute_import
import os
import sys

from io import BytesIO

import pytz
import telegram
import datetime

try:
    from pg_lock_monitor import monitor, cli
except ImportError:
    import monitor
    import cli


default_timezone = 'UTC'
default_encoding = 'utf-8'

tlg_report_name_pattern = 'pg_lock_report_%s.txt'


def stdout_print(text):
    sys.stdout.write((text + '\n').encode(default_encoding))


class TelegramBot(object):
    def __init__(self, token, chats, _encoding=default_encoding):
        self.bot = telegram.Bot(token=token)
        self.chats = chats
        self.encoding = _encoding

    def alert(self, caption, text_for_file, filename):
        if sys.version_info[0] == 2:
            caption = caption.encode(self.encoding)
            filename = filename.encode(self.encoding)
        buf = BytesIO()
        buf.write(text_for_file.encode(self.encoding))
        for chat_id in self.chats:
            buf.seek(0)
            self.bot.send_document(chat_id, buf, filename, caption=caption)
        buf.close()


def import_from_path(py_path):
    try:
        from importlib.machinery import SourceFileLoader
        return SourceFileLoader("config", py_path).load_module()
    except ImportError:
        import imp
        return imp.load_source('config', py_path)


def main():
    options = cli.parse_args()
    config = options.config
    duration = options.duration
    stdout_print('Конфигурационный файл - %s' % os.path.normpath(config))
    if not os.path.exists(config):
        stdout_print('Файл %s не существует' % os.path.normpath(config))
    else:
        cfg = import_from_path(config)
        timezone = pytz.timezone(getattr(cfg, 'TIMEZONE', 'UTC'))
        stdout_print('Временная зона - %s' % timezone)
        telegram_token = getattr(cfg, 'TELEGRAM_TOKEN', None)
        telegram_chats = getattr(cfg, 'TELEGRAM_CHATS', [])
        telegram_bot = TelegramBot(telegram_token, telegram_chats) if telegram_token else None
        dsn = "host='%(db_host)s' port=%(db_port)s dbname='%(db_name)s' user='%(db_user)s'" % {
            'db_host': cfg.DB_HOST,
            'db_port': cfg.DB_PORT,
            'db_name': cfg.DB_NAME,
            'db_user': cfg.DB_USER,
        }
        stdout_print('Подключение %s' % dsn)
        dsn += 'password=%(db_password)s' % {'db_password': cfg.DB_PASSWORD}
        report = monitor.get_lock_report(dsn, duration, tz=timezone)
        stdout_print(report or 'Блокировки продолжительностью более %s не зафиксированы' % duration)
        if report:
            report_name = tlg_report_name_pattern % datetime.datetime.now(tz=timezone).strftime('%Y-%m-%dT%H-%M-%S')
            alarm_msg = 'Зафиксированы блокировки в PostgreSQL.'
            telegram_bot.alert(alarm_msg, report, report_name)


if __name__ == '__main__':
    main()
