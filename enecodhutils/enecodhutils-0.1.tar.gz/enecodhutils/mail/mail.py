import smtplib
import logging
from time import sleep
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_mail(error_message, host, port, sender, password, job_name, recipient):
    """
    Sends email alerts whenever a job fails.
    :param error_message: Contains the error description
    :type error_message: String
    :param host: The SMTP host
    :type host: String
    :param port: The SMTP port
    :type port: Integer
    :param sender: The email address of the sender
    :type sender: String
    :param password: The password of the sender
    :type password: String
    :param job_name: The name of the job
    :type job_name: String
    :param recipient: The email address list of the recipients
    :type recipient: List
    :return: No return
    """
    smtp_server = smtplib.SMTP(host, port)
    try:
        smtp_server.starttls()
        smtp_server.login(sender, password)
        message = "Hi Team," + "\n" + "\n" + job_name + " job got failed with below error at time" + " " + \
                  datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S') + "\n" + "\n" + error_message + "\n" + "\n" + \
                  "Thanks" + "\n" + "Data-hub"
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = recipient
        msg['Subject'] = job_name + " Job Failed at " + datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        msg.attach(MIMEText(message, 'plain'))
        smtp_server.send_message(msg)
    except Exception as e:
        logging.info('Send status email failed')
        logging.info(ValueError('Error/exception thrown by sendEmail function: {}'.format(str(e))))
    finally:
        smtp_server.quit()


def send_mail_times(count, err, host, port, sender, password, job_name, recipient, sleep_time=10):
    """
    This function will send error based on count
    :param count: number of times error came
    :type count: Integer
    :param err: error message
    :type err: String
    :param host: The SMTP host
    :type host: String
    :param port: The SMTP port
    :type port: Integer
    :param sender: The email address of the sender
    :type sender: String
    :param password: The password of the sender
    :type password: String
    :param job_name: The name of the job
    :type job_name: String
    :param recipient: The email address list of the recipients
    :type recipient: List
    :param sleep_time: The sleep time between each error. Default value is 10 (optional)
    :type sleep_time: Integer
    :return: return the count of error
    """
    if count == 0:
        send_mail(str(err), host, port, sender, password, job_name, recipient)
        return count
    else:
        if count >= 24:
            send_mail(str(err), host, port, sender, password, job_name, recipient)
            count = 0
            return count
        sleep(sleep_time)
    return count
