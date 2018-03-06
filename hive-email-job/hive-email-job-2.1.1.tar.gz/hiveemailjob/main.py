# -*- coding: utf-8 -*-
# __author__ = 'elkan1788@gmail.com'

from hiveemailjob.settings import ProjectConfig
from ppytools.csvhelper import write
from ppytools.emailclient import EmailClient
from ppytools.hiveclient import HiveClient
from ppytools.lang.timerhelper import timeMeter

import datetime
import logging
import sys
import time

logger = logging.getLogger(__name__)


def build_rk(ts):
    """
    Build HBase row key value
    :param ts: date time
    :return: row key
    """
    return hex(int(time.mktime(ts.timetuple())*1000))[2:]

def email_att(folder, name):
    return '{}/{}_{}.csv'.format(folder, name, datetime.datetime.now().strftime('%Y%m%d%H%M%S'))

@timeMeter()
def run(args):
    """
    Email Job program execute entrance
    :param args:
    1. job file file path
    2. start time, format: 2018-01-30 17:09:38 (not require)
    3. stop time (not require)
    :return: Empty
    """
    '''
    Read system args start
    '''

    args_len = len(args)
    if args_len is not 2 and args_len is not 4:
        logger.error('Enter args is error. Please check!!!')
        logger.error('1: job file path.')
        logger.error('2: start time, format: 2018-01-30 17:09:38(option)')
        logger.error('3: stop time(option)')
        sys.exit(1)
    elif args == 4:
        try:
            start_time = datetime.datetime.strptime(args[2], '%Y-%m-%d %H:%M:%S')
            stop_time = datetime.datetime.strptime(args[3], '%Y-%m-%d %H:%M:%S')
        except Exception, e:
            raise RuntimeError('Parse start or stop time failed!!!\n', e)
    else:
        stop_time = datetime.date.today()
        start_time = stop_time - datetime.timedelta(days=1)

    job_file = args[1]
    start_rk = build_rk(start_time)
    stop_rk = build_rk(stop_time)

    hive_conf = '/etc/pythoncfg/hive.ini'
    email_conf = '/etc/pythoncfg/email.ini'
    sets = ProjectConfig(hive_conf, email_conf, job_file)

    job_info = sets.getJobInfo()
    csv_folder = sets.getCSVFolder()
    logger.info('Now running %s Email Job...', job_info['title'])
    logger.info('Start time: %s', start_time)
    logger.info('Stop time: %s', stop_time)

    hc = HiveClient(**sets.getHiveConf())

    csv_file = sets.getCSVFile().items()
    csv_file.sort()
    file_list = []
    logger.info('File name list: ')
    for (k, v) in csv_file:
        logging.info('%s: %s', k, v)
        file_list.append(v)

    csv_head = sets.getCSVHead().items()
    csv_head.sort()
    head_list = []
    logger.info('CSV file head list: ')
    for (k, v) in csv_head:
        logging.info('%s: %s', k, v)
        head_list.append(v)

    hql_scripts = sets.getHQLScript().items()
    hql_scripts.sort()
    email_atts = []
    index = 0
    for (k, hql) in hql_scripts:
        logging.info('%s: %s', k, hql)
        result, size = hc.execQuery(hql.format(start_rk, stop_rk))
        if size is 0:
            logging.info('The above HQL script not found any data!!!')
        else:
            csv_file = email_att(csv_folder, file_list[index])
            email_atts.append(csv_file)
            write(csv_file, head_list[index].split(','), result)

        index += 1

    '''Flush Hive Server connected.
    '''
    hc.closeConn()

    email_sub = sets.getEmailInfo()['subject'] % start_time
    email_body = sets.getEmailInfo()['body']
    email_to = sets.getEmailInfo()['to'].split(';')
    email_cc = sets.getEmailInfo()['cc'].split(';')

    if len(email_atts) == 0:
        email_body = '抱歉当前未找到任何数据。\n\n' + email_body


    ec = EmailClient(**sets.getEmailServer())
    ec.send(email_to, email_cc, email_sub, email_body, email_atts, False)
    ec.quit()

    logger.info('Finished %s Email Job.', job_info['title'])