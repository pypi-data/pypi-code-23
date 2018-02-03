import smtplib
import os

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from tornado.escape import xhtml_escape
from tornado import template


__all__ = ["PyeMailer", "ServerConfig", "Message", "TextMessage", "TemplateMessage"]


class ServerConfig(object):
    """Holds smtp server config. By default uses smtp.ucsd.edu which as of today 06/07/2017 does not require login."""
    def __init__(self, smtp_server_name, port=25, username=None, password=None):
        """
        :param smtp_server_name: Name of the smtp server
        :type smtp_server_name: str
        :param port: port number to connect smtp on
        :type port: int
        :param username: username to login to the smtp server as
        :type username: str
        :param password: password for username to login to the smtp server as
        :type password: str
        """
        self.smtp_server_name = smtp_server_name
        self.smtp_server_port = port
        self.username = username
        self.password = password

    def connect(self):
        """
        Creates a connection to the smtp server.
        :return: SMTP connection object to use SMTP functionality
        :rtype: SMTP
        """
        smtp_server = smtplib.SMTP(self.smtp_server_name, self.smtp_server_port)

        if self.username is not None and self.password is not None:
            smtp_server.login(self.username, self.password)

        return smtp_server


class Message(object):
    """Generic email message class"""
    def __init__(self, from_email=None, to_email=None, subject=None):
        self.from_email = from_email
        self.to_email = to_email
        self.subject = subject

    def compose(self):
        pass


class TextMessage(Message):
    """Class to represent a plain text email message"""
    def __init__(self, from_email=None, to_email=None, subject=None, plain_text=None):
        """
        :param from_email: email address to send email from
        :type from_email: str
        :param to_email: email address(es) to send email to
        :type to_email: str, list
        :param subject: subject of the email
        :type subject: str
        :param plain_text: message of the email
        :type plain_text: str
        """
        Message.__init__(self)

        self.from_email = from_email
        self.to_email = to_email
        self.subject = subject
        self.plain_text = plain_text

    def compose(self, from_email=None, to_email=None, subject=None, plain_text=None):
        """
        Creates a plain text email message body.

        :param from_email: email address to send email from
        :type from_email: str
        :param to_email: email address(es) to send email to
        :type to_email: str, list
        :param subject: subject of the email
        :type subject: str
        :param plain_text: message of the email
        :type plain_text: str
        :return: complete email message as a string
        :rtype: str
        """
        self.from_email = from_email or self.from_email
        self.to_email = to_email or self.to_email
        self.subject = subject or self.subject
        self.plain_text = plain_text or self.plain_text

        message = MIMEMultipart('alternative')

        if self.plain_text is not None:
            message.attach(MIMEText(self.plain_text, 'plain', 'utf8'))

        message.add_header('Content-Transfer-Encoding', 'base64')

        message['Subject'] = self.subject
        message['From'] = self.from_email

        if isinstance(self.to_email, list):
            message['To'] = ', '.join(self.to_email)
        else:
            message['To'] = self.to_email

        return message.as_string()

class TemplateMessage(Message):
    """Class to represent email message based on a tornado template."""
    def escape_context(self, context):
        """
        Recursively escape all strings in context.

        :param context: data to escape
        :type context: dict, list, str
        :return: same object type as input with all strings properly escaped for use in templates
        :rtype: dict, list, str
        """
        if isinstance(context, dict):
            return {key: self.escape_context(value) for key, value in context.items()}
        elif isinstance(context, list):
            return [self.escape_context(element) for element in context]
        elif isinstance(context, str):
            return xhtml_escape(context)
        else:
            return context

    def __init__(self, from_email=None, to_email=None, subject=None, html_template_path=None, html_context=None):
        """
        :param from_email: address to send email from
        :type from_email: str
        :param to_email: address(es) to send email to
        :type to_email: str, list
        :type subject: str
        :param html_context: data used to render html template
        :param html_template_path: relative path to the html template file
        :type html_template_path: str
        :param subject: subject line of the email
        :type html_context: dict
        """
        Message.__init__(self)

        self.from_email = from_email
        self.to_email = to_email
        self.subject = subject
        self.html_template_path = html_template_path
        self.html_context = html_context

        # this files current path
        current_file_dir = os.path.dirname(os.path.realpath('__file__'))

        # append and resolve relative path to template file path
        self.html_template_path = os.path.join(current_file_dir, self.html_template_path)

        # get directory name of template file (used for tornado template.Loader)
        self.html_template_dir = os.path.dirname(self.html_template_path)

        # get the filename of the template
        self.html_template_filename = os.path.basename(self.html_template_path)

        # check if the template file exists before proceeding
        if not os.path.isfile(self.html_template_path):
            raise ValueError("Could not find template file: {}".format(self.html_template_path))

        # load the template
        self.html_template = template.Loader(self.html_template_dir).load(self.html_template_filename)

    def compose(self, from_email=None, to_email=None, subject=None, html_template_path=None, html_context=None):
        """
        Generates a html email message based on a template and optional data.

        :param from_email: address to send email from
        :type from_email: str
        :param to_email: address(es) to send email to
        :type to_email: str, list
        :param subject: subject line of the email
        :type subject: str
        :param html_template_path: relative path (from this file not other importing this file) to the html template file 
        :type html_template_path: str
        :param html_context: data used to render html template
        :type html_context: dict
        :return: fully rendered html template with optional data
        :rtype: str
        """
        self.from_email = from_email or self.from_email
        self.to_email = to_email or self.to_email
        self.subject = subject or self.subject
        self.html_template_path = html_template_path or self.html_template_path
        self.html_context = html_context or self.html_context

        # this files current path
        current_file_dir = os.path.dirname(os.path.realpath('__file__'))

        # append and resolve relative path to template file path
        self.html_template_path = os.path.join(current_file_dir, self.html_template_path)

        # get directory name of template file (used for tornado template.Loader)
        self.html_template_dir = os.path.dirname(self.html_template_path)

        # get the filename of the template
        self.html_template_filename = os.path.basename(self.html_template_path)

        # check if the template file exists before proceeding
        if not os.path.isfile(self.html_template_path):
            raise ValueError("Could not find template file: {}".format(self.html_template_path))

        # load the template
        self.html_template = template.Loader(self.html_template_dir).load(self.html_template_filename)

        # if there is data for the template make sure it's properly escaped (string values)
        if self.html_context is not None:
            self.html_context = self.escape_context(self.html_context)

        # create the email message
        message = MIMEMultipart('alternative')

        message.add_header('Content-Transfer-Encoding', 'base64')

        message['Subject'] = self.subject
        message['From'] = self.from_email

        if isinstance(self.to_email, list):
            message['To'] = ', '.join(self.to_email)
        else:
            message['To'] = self.to_email

        # unpack the dict into keyword arguments. e.g {"key1": 1, "key2": 2} -> key1=1, key2=2
        html = self.html_template.generate(**self.html_context)

        # attach rendered html to message as html
        message.attach(MIMEText(html, "html", "utf-8"))

        return message.as_string()


class PyeMailer(object):
    """A generic email module that can send regular text emails, or template driven emails."""
    def __init__(self, server_config):
        """
        :param server_config: smtp server configuration object with data for connecting to the smtp server.
        :type server_config: ServerConfig
        """
        if server_config is None:
            raise ValueError("parameter: server_config is required")

        if not isinstance(server_config, ServerConfig):
            raise ValueError("parameter: server_config is not of type ServerConfig")

        self.smtp = server_config.connect()

    def send(self, message):
        """
        Send an email over smtp.
        :param message: the Message (TextMessage, TemplateMessage) object of the email to send.
        :type message: TextMessage, TemplateMessage
        :return: None
        :rtype: None
        """
        if not message:
            raise ValueError("parameter: message is required")

        if not isinstance(message, Message):
            raise ValueError("parameter: message should be of type Message (TextMessage, TemplateMessage)")

        self.smtp.sendmail(message.from_email, message.to_email, message.compose())


# if __name__ == "__main__":
#     from random import randrange

#     print("Creating ServerConfig.")
#     config = ServerConfig('smtp.myserver.com')

#     print("Creating html context")
#     context = {
#         "NAME": "Bob",
#         "POWERBALL_NUMBERS": [randrange(1, 27) for x in range(5)]
#     }

#     print("Creating plain text message")
#     # create a text message
#     # msg = TextMessage("username@email.com", ["username2@email.com", "username3@email.com"], "This is a test", "I'm an awesome email")

#     # create a message from data and a template
#     msg = TemplateMessage("username@email.com", ["username@email.com"], "Test Template Email", "./templates/my_template.html", context)

#     print("Creating emailer")
#     pyemailer = PyeMailer(config)

#     print("Sending email")
#     pyemailer.send(msg)
