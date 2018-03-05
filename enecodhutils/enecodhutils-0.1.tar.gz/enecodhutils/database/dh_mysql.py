import logging
import MySQLdb


def get_last_processed(db_host, db_user_name, db_password, db_schema, db_port, last_processed_time, data_source):
    """
    This Function will provide the last processed date/time for the given datasource/filename.
    :param db_host: The database hostname/Ip Address.
    :type db_host: String
    :param db_user_name: The database username
    :type db_user_name: String
    :param db_password: The database password
    :type db_password: String
    :param db_schema: The database schema
    :type db_schema: String
    :param db_port: The database port
    :type db_port: Integer
    :param last_processed_time: empty  processed files list
    :type last_processed_time: List of datetime.
    :param data_source: Name of the source
    :return: last_processed_time: The last processed_time for the data_source.
    """
    logging.info('DH_Utils: Fetching last processed time from database')
    with MySQLdb.connect(host=db_host, user=db_user_name,
                         passwd=db_password, db=db_schema,
                         port=db_port).cursor() as cursor:
        query = "select file_date from applications_inventory where data_source='{}'".format(data_source)
        cursor.execute(query)
        for row in cursor.fetchall():
            last_processed_time.append(row[0])
    logging.info('DH_Utils: Finished fetching last processed time from database')
    return last_processed_time


def update_processed_time(db_host, db_user_name, db_password, db_schema, db_port, file_date, processed_time,
                          data_source):
    """
    This Function will update the processed_time in MySQL database for the given data_source.
    :param db_host: The database hostname/Ip Address.
    :type db_host: String
    :param db_user_name: The database username
    :type db_user_name: String
    :param db_password: The database password
    :type db_password: String
    :param db_schema: The database schema
    :type db_schema: String
    :param db_port: The database port
    :type db_port: Integer
    :param file_date: Processed file date.
    :type file_date: String
    :param processed_time: Processed time of the file.
    :param data_source: Name of the data source.
    :return: No return value.
    """
    logging.info('DH_Utils: Updating current processed time and file_date into database')
    with MySQLdb.connect(host=db_host, user=db_user_name,
                         passwd=db_password, db=db_schema,
                         port=db_port).cursor() as cursor:
        query = "update applications_inventory set file_date='{}', processed_time='{}'" \
                "where data_source='{}'".format(file_date, processed_time, data_source)
        cursor.execute(query)
        cursor.execute('commit')
    logging.info('DH_Utils: Finished updating current processed time and file_date into database')


def get_err_count(db_host, db_user_name, db_password, db_schema, db_port, data_source):
    """
    Get the error count for the current process
    :param db_host: The database hostname/Ip Address.
    :type db_host: String
    :param db_user_name: The database username
    :type db_user_name: String
    :param db_password: The database password
    :type db_password: String
    :param db_schema: The database schema
    :type db_schema: String
    :param db_port: The database port
    :type db_port: Integer
    :param data_source: The data_source for the current process.
    :type data_source: String
    :return count: Int
    """
    count = 0
    logging.info('DH_Utils: Getting error count if any for the current process.')
    with MySQLdb.connect(host=db_host, user=db_user_name,
                         passwd=db_password, db=db_schema,
                         port=db_port).cursor() as cursor:
        query = "select errors from applications_inventory " \
                "where data_source='{}'".format(data_source)
        cursor.execute(query)
        for row in cursor.fetchall():
            count = row[0]
    logging.info('DH_Utils: Finished getting error count for the current process.')
    return count


def update_err_count(db_host, db_user_name, db_password, db_schema, db_port, count, status, data_source):
    """
    Set error count for the given process
    :param db_host: The database hostname/Ip Address.
    :type db_host: String
    :param db_user_name: The database username
    :type db_user_name: String
    :param db_password: The database password
    :type db_password: String
    :param db_schema: The database schema
    :type db_schema: String
    :param db_port: The database port
    :type db_port: Integer
    :param count: The error count.
    :type count: Int
    :param status: The process status to be updated
    :type status: Int
    :param data_source: The data_source for the current process.
    :type data_source: String
    :type count: Int
    """
    logging.info('DH_Utils: Updating error count, status for the current process into database')
    with MySQLdb.connect(host=db_host, user=db_user_name,
                         passwd=db_password, db=db_schema,
                         port=db_port).cursor() as cursor:
        query = "update applications_inventory set errors='{}', status='{}'" \
                "where data_source='{}'".format(str(count), str(status), data_source)
        cursor.execute(query)
        cursor.execute('commit')
    logging.info('DH_Utils: Finished updating error count, status for the current process into database')
