#!/usr/bin/python2.7
# -*- coding:utf-8 -*-
######################################################################################
### purpose use python interface to write SQL for some databases or some data things
### Just for fun and make my job  easier
### author by Jake Liang at Maywide 20180201
###
#sections
#oracle
#hive
#sftp

import cx_Oracle
import ConfigParser
import os
import sys
import logging
import subprocess
import datetime
import calendar
import pyhs2
import paramiko
import ftplib

class ssh(object):
    def __init__(self, servername=None):
        ################load config info########################
        if servername != None:
            self.get_config(servername)

    def __del__(self):
        pass

    def get_config(self, servername):
        ################get oracle database info#################
        # set the config file
        try:
            config_path = "/usr1/config/"
            config_filename = "ssh_config.ini"
            config = ConfigParser.ConfigParser()
            config.readfp(open(config_path + config_filename, "rb"))
            self.host = config.get(servername, "host")
            self.port = int(config.get(servername, "port"))
            self.user = config.get(servername, "user")
            self.passwd = config.get(servername, "passwd")
        except Exception, e:
            printImmediately("failed to load configure")
            printImmediately(e.args[0])
            exit(1)

    def connect_ssh(self, host=None, port=None, user=None, passwd=None):
        'this is use the paramiko connect the host,return conn'
        if host != None:
            self.host = host
        if port != None:
            self.port = port
        if user != None:
            self.user = user
        if passwd != None:
            self.passwd = passwd
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.ssh.connect(self.host, self.port, self.user, self.passwd, allow_agent=True)
            printImmediately("Server %s SSH connect successful" % (self.host))

        except Exception, e:
            print(e.args[0])
            return None

    def exec_command(self, cmd):
        if not self.ssh:
            printImmediately("Server %s SSH not connect")
            exit(-1)
        stdin, stdout, stderr = self.ssh.exec_command(cmd)
        printImmediately(stdout.read())

class oracle(object):
    def __init__(self, servername):

        ################check python script running or not########################
        self.check_running_status()
        ################load config info########################
        self.get_config(servername)
        ################set logging########################
        self.logger = self.set_logger()

        self.write_log("########PROGRAM START: pid = %d ########" % (self.pid))

    def __del__(self):
        self.conn_colse()
        self.write_log("########PROGRAM END: pid = %d ########" % (self.pid))

    # check script process
    def check_running_status(self):
        ################forbid to run script if there already running one###############
        self.pid = os.getpid()
        dirname, filename = os.path.split(os.path.abspath(sys.argv[0]))
        cmd = 'ps -ef | grep -v grep | grep -v ' + str(self.pid) + ' | grep -w ' + filename
        child1 = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        msg = child1.stdout.read()
        child1.wait()
        if msg != '':
            printImmediately("%s is already running.!!!\n" % (filename))
            exit(1)

    #################################################################################################
    # get config
    def get_config(self, servername):
        ################get oracle database info#################
        # set the config file
        try:
            config_path = "/usr1/config/"
            config_filename = "DbConfig.ini"
            config = ConfigParser.ConfigParser()
            config.readfp(open(config_path + config_filename, "rb"))
            self.host = config.get(servername, "host")
            self.port = int(config.get(servername, "port"))
            self.user = config.get(servername, "user")
            self.passwd = config.get(servername, "passwd")
            self.sid = config.get(servername, "sid")
        except Exception, e:
            self.write_log("failed to load configure")
            self.write_log(e.args[0])
            exit(1)

    #################################################################################################
    # set log info
    def set_logger(self):
        try:
            dirname, filename = os.path.split(os.path.abspath(sys.argv[0]))
            if not os.path.exists("/usr1/log/python/oracle/"):
                os.mkdir("/usr1/log/python/oracle/")
            logdir = '/usr1/log/python/oracle/'
            logfile = logdir + str(filename) + '.log'
            logging.basicConfig(level=logging.DEBUG,
                                format='%(asctime)s %(levelname)s: %(message)s',
                                datefmt='%Y%m%d %H:%M:%S',
                                filename=logfile,
                                filemode='a')
            # StreamHandler，将INFO级别或更高的日志信息打印到标准错误，并将其添加到当前的日志处理对象#
            console = logging.StreamHandler()
            console.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s:%(levelname)s: %(message)s')
            console.setFormatter(formatter)
            logging.getLogger('').addHandler(console)
            return logging
        except Exception, e:
            self.write_log("failed to set logging")
            self.write_log(e.args[0])
            exit(1)

    #################################################################################################
    # you can write log by using this function
    def write_log(self, log_text):
        self.logger.debug(log_text)

    #################################################################################################
    # connect the oracle database
    def connect(self):
        try:
            tns = self.user + "/" + self.passwd + "@" + self.host + ":" + str(self.port) + "/" + self.sid
            self.write_log(tns)
            self.conn = cx_Oracle.connect(tns)
            self.cursor = self.conn.cursor()
            self.write_log("connection to ORACLE DATABASE succeeded")
        except Exception, e:
            self.write_log("connection to ORACLE DATABASE failed")
            self.write_log(e.args[0])
            exit(1)

    ##################################################################################################
    # execute a sql
    def execute_sql(self, sql):
        try:
            self.logger.info('\n<EXEC_SQL>:\n' + sql + ';\n</EXEC_SQL>')
            self.cursor.execute(sql)
            rows = self.cursor.rowcount
            if rows != None:
                self.logger.info('SQL executed successfully, %s rows affected.' % (rows))
            else:
                self.logger.info('SQL executed successfully, no rows affected.')
        except Exception, e:
            self.write_log("Executing SQL failed")
            self.write_log(e.args[0])
            exit(1)

    def execute_select(self, sql):
         try:
             self.logger.info('\n<EXEC_SQL>:\n' + sql + ';\n</EXEC_SQL>')
             self.cursor.execute(sql)
             rows = self.cursor.rowcount
             data = self.cursor.fetchall()
             if rows != None:
                 self.logger.info('SQL executed successfully, %s rows affected.' % (rows))
                 return data
             else:
                 self.logger.info('SQL executed successfully, no rows affected.')
         except Exception, e:
             self.write_log("Executing SQL failed")
             self.write_log(e.args[0])
             exit(1)

    #batch execute SQLs

    def batch_execute_sql(self, batch_sql):
        sql_list = batch_sql.split(';')
        for single_sql in sql_list:
            sql = single_sql.strip()
            if sql != '':
                if '#DEBUG:' in sql:
                    self.write_log(sql.replace('#DEBUG:', ''))
                elif '#IGNORE_ERROR:' in sql:
                    try:
                        self.write_log(sql)
                        self.logger.info('\n<EXEC_SQL>:\n\t' + sql + ';\n</EXEC_SQL>')
                        sql2 = sql.replace("#IGNORE_ERROR:", '')
                        self.cursor.execute(sql2)
                        rows = self.cursor.rowcount
                        if rows != None:
                            self.logger.info('SQL executed successfully, %s rows affected.' % (rows))
                        else:
                            self.logger.info('SQL executed successfully, no rows affected.')
                    except Exception, e:
                        sql2 = sql.replace("#IGNORE_ERROR:", '')
                        self.write_log("IGNORE EXECUTE ERROR %s" % sql2)
                        continue
                else:
                    self.execute_sql(sql)

    #################################################################################################
    # disconnect from the database
    def conn_colse(self):
        self.conn.close()

class hive(object):
    def __init__(self, servername):

        ################check python script running or not########################
        self.check_running_status()
        ################load config info########################
        self.get_config(servername)
        ################set logging########################
        self.logger = self.set_logger()

        self.write_log("########PROGRAM START: pid = %d ########" % (self.pid))

    def __del__(self):
        self.conn_close()
        self.write_log("########PROGRAM END: pid = %d ########" % (self.pid))

    # check script process
    def check_running_status(self):
        ################forbid to run script if there already running one###############
        self.pid = os.getpid()
        dirname, filename = os.path.split(os.path.abspath(sys.argv[0]))
        cmd = 'ps -ef | grep -v grep | grep -v ' + str(self.pid) + ' | grep -w ' + filename
        child1 = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        msg = child1.stdout.read()
        child1.wait()
        if msg != '':
            print "%s is already running.!!!\n" % (filename)
            exit(1)

    #################################################################################################
    # get config
    def get_config(self, servername):
        ################get oracle database info#################
        # set the config file
        try:
            config_path = "/usr1/config/"
            config_filename = "DbConfig.ini"
            config = ConfigParser.ConfigParser()
            config.readfp(open(config_path + config_filename, "rb"))
            self.host = config.get(servername, "host")
            self.port = int(config.get(servername, "port"))
            self.user = config.get(servername, "user")
            self.passwd = config.get(servername, "passwd")
            self.database = config.get(servername, "database")
        except Exception, e:
            self.write_log("failed to load configure")
            self.write_log(e.args[0])
            exit(1)

    #################################################################################################
    # set log info
    def set_logger(self):
        try:
            dirname, filename = os.path.split(os.path.abspath(sys.argv[0]))
            if not os.path.exists("/usr1/log/python/hive/"):
                os.mkdir("/usr1/log/python/hive/")
            logdir = '/usr1/log/python/hive/'
            logfile = logdir + str(filename) + '.log'
            logging.basicConfig(level=logging.DEBUG,
                                format='%(asctime)s[line:%(lineno)d] %(levelname)s: %(message)s',
                                datefmt='%Y%m%d %H:%M:%S',
                                filename=logfile,
                                filemode='a')
            # StreamHandler，将INFO级别或更高的日志信息打印到标准错误，并将其添加到当前的日志处理对象#
            console = logging.StreamHandler()
            console.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s:%(levelname)s: %(message)s')
            console.setFormatter(formatter)
            logging.getLogger('').addHandler(console)
            return logging
        except Exception, e:
            self.write_log("failed to set logging")
            self.write_log(e.args[0])
            exit(1)

    #################################################################################################
    # you can write log by using this function
    def write_log(self, log_text):
        self.logger.debug(log_text)

    #################################################################################################
    # connect the oracle database
    def connect(self):
        try:
            self.conn = pyhs2.connect(host=self.host,
                                      port=self.port,
                                      authMechanism='PLAIN',
                                      user=self.user,
                                      password=self.passwd,
                                      database=self.database,
                                      )
            self.cursor = self.conn.cursor()
            self.write_log("connection to HIVE succeeded")
        except Exception, e:
            self.write_log("connection to HIVE failed")
            self.write_log(e.args[0])
            exit(1)

    ##################################################################################################
    # execute a sql
    def execute_sql(self, sql):
        try:
            self.logger.info('\n<EXEC_SQL>:\n\t' + sql + ';\n</EXEC_SQL>')
            self.cursor.execute(sql)
            #rows = self.cursor.rowcount
            #if rows != None:
            #    self.logger.info('SQL executed successfully, %s rows affected.' % (rows))
            #else:
            #    self.logger.info('SQL executed successfully, no rows affected.')
            self.write_log("SQL executed successfully")
        except Exception, e:
            self.write_log("Executing SQL failed")
            self.write_log(e.args[0])
            exit(1)

    #batch execute SQLs

    def batch_execute_sql(self, batch_sql):
        sql_list = batch_sql.split(';')
        for single_sql in sql_list:
            sql = single_sql.strip()
            if sql != '':
                if '#DEBUG:' in sql:
                    self.write_log(sql.replace('#DEBUG:', ''))
                else:
                    self.execute_sql(sql)


    def execute_select(self, sql):
        try:
            self.cursor.execute(sql)
            rows = self.cursor.fetchall()
            return rows[0][0]
        except Exception, e:
            self.write_log("Executing SQL failed")
            self.write_log(e.args[0])
            exit(1)

    #################################################################################################
    # disconnect from the database
    def conn_close(self):
        self.conn.close()

class sftp(object):
    def __init__(self, servername=None):
        ################load config info########################
        if servername != None:
            self.get_config(servername)

    def __del__(self):
        pass

    def get_config(self, servername):
        ################get oracle database info#################
        # set the config file
        try:
            config_path = "/usr1/config/"
            config_filename = "sftp_config.ini"
            config = ConfigParser.ConfigParser()
            config.readfp(open(config_path + config_filename, "rb"))
            self.host = config.get(servername, "host")
            self.port = int(config.get(servername, "port"))
            self.user = config.get(servername, "user")
            self.passwd = config.get(servername, "passwd")
        except Exception, e:
            printImmediately("failed to load configure")
            printImmediately(e.args[0])
            exit(1)

    def sftp_conn(self, host=None, port=None, user=None, passwd=None):
        try:
            if host != None:
                self.host = host
            if port != None:
                self.port = port
            if user != None:
                self.user = user
            if passwd != None:
                self.passwd = passwd
            t = paramiko.Transport((self.host, self.port))
            t.connect(username=self.user, password=self.passwd)
            self.sftp = paramiko.SFTPClient.from_transport(t)
        except Exception, e:
            printImmediately("connect sftp host:%s port:%s failed" % (self.host, self.passwd))
            printImmediately(e.args[0])
            exit(1)

    def sftp_put(self, localpath, remotepath):
        self.sftp.put(localpath, remotepath + ".filepart")
        self.sftp.rename(remotepath + ".filepart", remotepath)
        printImmediately("SFTP from %s to %s successful." % (localpath, remotepath))

    def sftp_get(self, remotepath, localpath):
        self.sftp.get(remotepath, localpath + ".filepart")
        os.rename(localpath + ".filepart", localpath)
        printImmediately("SFTP from %s to %s successful." % (remotepath, localpath))




#common functions
def addDays(pDate, pDelta):
    date = datetime.datetime.strptime(pDate, '%Y%m%d')
    delta = datetime.timedelta(days=pDelta)
    n_days = date + delta
    return n_days.strftime('%Y%m%d')


def addMonths(pDate, pDelta):
    sourcedate = datetime.datetime.strptime(pDate, '%Y%m%d')
    month = sourcedate.month - 1 + pDelta
    year = int(sourcedate.year + month / 12)
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year, month)[1])
    return datetime.date(year, month, day).strftime('%Y%m%d')


def getLastDateOfMonth(pDate):
    date = datetime.datetime.strptime(pDate, '%Y%m%d')
    #delta = datetime.timedelta(days=-1)
    firstDayWeekDay, monthRange = calendar.monthrange(date.year, date.month)
    monthlastday = datetime.date(date.year, date.month, monthRange)
    return monthlastday.strftime('%Y%m%d')


def getFirstDateOfMonth(pDate):
    date = datetime.datetime.strptime(pDate, '%Y%m%d')
    monthfirstday = datetime.date(date.year, date.month, 1)
    return monthfirstday.strftime('%Y%m%d')


def getWeekday(pDate):
    # Monday is 0
    date = datetime.datetime.strptime(pDate, '%Y%m%d')
    weekday = date.weekday()
    return weekday


def getWeekdayEng(pDate):
    # Monday is 0
    date = datetime.datetime.strptime(pDate, '%Y%m%d')
    weekday = date.weekday()
    if weekday == 0: return 'Monday'
    if weekday == 1: return 'Tuesday'
    if weekday == 2: return 'Wednesday'
    if weekday == 3: return 'Thursday'
    if weekday == 4: return 'Friday'
    if weekday == 5: return 'Saturday'
    if weekday == 6: return 'Sunday'

def printImmediately(str):
    print(str)
    sys.stdout.flush()

def execute_shell_cmd(cmd):
    p1 = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    p1.communicate()

class ftp(object):
    def __init__(self, servername=None):
        ################load config info########################
        if servername != None:
            self.get_config(servername)

    def __del__(self):
        pass

    def get_config(self, servername):
        ################get oracle database info#################
        # set the config file
        try:
            config_path = "/usr1/config/"
            config_filename = "ftp_config.ini"
            config = ConfigParser.ConfigParser()
            config.readfp(open(config_path + config_filename, "rb"))
            self.host = config.get(servername, "host")
            self.port = int(config.get(servername, "port"))
            self.user = config.get(servername, "user")
            self.passwd = config.get(servername, "passwd")
        except Exception, e:
            printImmediately("failed to load configure")
            printImmediately(e.args[0])
            exit(1)

    def login(self):
        try:
            self.ftp = ftplib.FTP()  # 实例化FTP对象
            self.ftp.connect(self.host, self.port)
            self.ftp.login(self.user, self.passwd) ##登录
            printImmediately("Login successful")
            printImmediately("Current path: %s" % (self.ftp.pwd()))
        except Exception, e:
            printImmediately("Failed to login")
            printImmediately(e.args[0])
            exit(1)

    def ftp_download(self, remote_file, local_file):
        '''以二进制形式下载文件'''
        buffer_size = 1024  # 设置缓冲器大小
        fp = open(local_file + ".filepart", 'wb')
        self.ftp.retrbinary('RETR %s' % remote_file, fp.write, buffer_size)
        os.rename(local_file + ".filepart", local_file)
        printImmediately("Download file from %s to %s successful" % (local_file,local_file))
        fp.close()


    def ftp_upload(self, local_file, remote_file):
        '''以二进制形式上传文件'''
        buffer_size = 1024  # 设置缓冲器大小
        fp = open(local_file, 'rb')
        self.ftp.storbinary('STOR ' + remote_file + ".filepart", fp, buffer_size)
        self.ftp.rename(remote_file + ".filepart", remote_file)
        printImmediately("Upload file from %s to %s successful" % (local_file, remote_file))
        fp.close()