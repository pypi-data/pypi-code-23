# coding: utf-8
from __future__ import unicode_literals, print_function
import os

import datetime
from io import BytesIO
from collections import namedtuple, defaultdict

import psycopg2
import pytz

sql_dir = os.path.join(os.path.dirname(__file__), 'sql')

BackendProcess = namedtuple('BackendProcess', ['pid', 'backend_start', 'xact_start', 'state_change',
                                               'query_start', 'query', 'blocked_by', 'wait_event_type',
                                               'wait_event', 'lock_mode'])

BlockingProcess = namedtuple('BlockingProcess', ['pid', 'backend_start', 'xact_start',
                                                 'query_start', 'query', 'state',
                                                 'is_blocked', 'blockers', 'locks'])

wait_event_type_verbose = defaultdict(lambda: 'неизвестный тип')
wait_event_type_verbose.update({
    'LWLockNamed': 'именованная легкая блокировка',
    'LWLockTranche': 'группа связанных легких блокировок',
    'Lock': 'тяжелая блокировка',
    'BufferPin': 'блокировка буфера данных',
})

state_verbose = defaultdict(lambda: 'неизвестный статус')
state_verbose.update({
    'active': 'выполняется',
    'idle': 'ожидание команды от клиента',
    'idle in transaction': 'находится в транзакции, ничего не выполняет',
    'idle in transaction (aborted)': 'прерывание транзакции',
    'fastpath function call': 'выполняется fast-path функция',
    'disabled': 'отключен сбор информации',
})


def read_sql_file(sql_file_path):
    full_path = os.path.join(sql_dir, sql_file_path)
    with open(full_path, 'r') as sql_file:
        return sql_file.read()


def get_file_from_text(text):
    buf = BytesIO()
    buf.write(text)
    buf.seek(0)
    return buf


def get_lock_report(pg_dsn, duration, tz=pytz.utc):
    duration = datetime.timedelta(seconds=duration)
    blocked_processes_sql = read_sql_file('get_blocked.sql')
    blocking_process_sql = read_sql_file('get_blocking.sql')
    connection = psycopg2.connect(dsn=pg_dsn)
    try:
        cursor = connection.cursor()
        try:
            cursor.execute(blocked_processes_sql)
            blocked_backends = [BackendProcess(*r) for r in cursor.fetchall()]
            blocked_backends = list(filter(lambda b: (b.state_change is not None)
                                      and (datetime.datetime.now(tz=tz) - b.state_change >= duration), blocked_backends))
        finally:
            cursor.close()
        report = 'Заблокированы процессы:\n' if blocked_backends else ''
        for i, blocked in enumerate(blocked_backends):
            report += '%3d. PID: %d;\n' \
                   '     Cоединение: %s;\n' \
                   '     Начало транзакции: %s;\n' \
                   '     Начало запроса: %s;\n' \
                   '     Запрос: %s\n' \
                   '     Длительность блокировки: %s;\n' \
                   '     Тип блокировки: %s;\n' \
                   '     Ожидаемое событие: %s;\n' \
                   '     Режим блокировки: %s;\n' \
                   % (i+1, blocked.pid,
                      blocked.backend_start.astimezone(tz),
                      blocked.xact_start.astimezone(tz),
                      blocked.query_start.astimezone(tz),
                      blocked.query,
                      datetime.datetime.now(tz=tz) - blocked.state_change,
                      wait_event_type_verbose[blocked.wait_event_type],
                      blocked.wait_event, blocked.lock_mode, )
            report += '     Кем заблокирован:\n'
            cursor = connection.cursor()
            try:
                cursor.execute(blocking_process_sql, (blocked.blocked_by, ))
                blocking_backends = [BlockingProcess(*r) for r in cursor.fetchall()]
            finally:
                cursor.close()
            for j, blocking_process in enumerate(blocking_backends):
                report += '     %3d. PID: %d;\n' \
                       '          Начало транзакции: %s;\n' \
                       '          Начало запроса: %s;\n' \
                       '          Запрос: %s\n' \
                       '          Состояние: %s;\n' \
                       '          Заблокирован: %s %s;\n' \
                       '          Выставляемые блоки: %s;\n' \
                       % (j+1, blocking_process.pid,
                          blocking_process.xact_start.astimezone(tz) if blocking_process.xact_start else '',
                          blocking_process.query_start.astimezone(tz) if blocking_process.query_start else '',
                          blocking_process.query,
                          state_verbose[blocking_process.state],
                          'да' if blocking_process.is_blocked else 'нет',
                          blocking_process.blockers,
                          blocking_process.locks, )
        return report
    finally:
        connection.close()
