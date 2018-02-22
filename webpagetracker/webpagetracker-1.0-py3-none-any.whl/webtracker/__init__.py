import requests, time, smtplib

# Service to track web pages and inform changes through email

class Webtracker(object):

    def __init__(self, host, port, email, pw, dest, url):
        self.host = host
        self.port = port
        self.email = email
        self.pw = pw
        self.dest = dest
        self.url = url
        self.server = None
        self.page = None

        self.startService()

    def startService(self):
        self.server = smtplib.SMTP('%s:%s' % (self.host, self.port))
        self.server.ehlo()
        self.server.starttls()
        self.server.login(self.email, self.pw)

    def sendEmail(self, subject, message):
        msg = '\r\n'.join([
            'From: %s' % self.email,
            'To: %s' % self.dest,
            'Subject: %s' % subject,
            '',
            message
            ])

        self.server.sendmail(self.email, self.dest, msg)

    def scrapPage(self):
        actualState = requests.get(self.url).content

        if not self.page:
            self.page = actualState

            self.sendEmail('Tracking service started', \
                    ('Your tracking service to %s started.' % (self.url)))

        elif actualState != self.page:
            self.page = actualState

            self.sendEmail('Your page changed', \
                    ('Page %s changed.' % (self.url)))

    def startTracking(self):
        while True:
            self.scrapPage()
            time.sleep(60)
