import os
import smtplib

from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.MIMEMessage import MIMEMessage
from email import Encoders

def send_email(username, password, subject, message, recipient,  
               cc = None, bcc = None, reply_to = None, 
               attach = None, html = None, pre = False, 
               custom_headers = None, sender_name = None):
    ec = EmailClient(recipient = recipient, subject = subject, message = message,
                     cc = cc, bcc = bcc, reply_to = reply_to, attach = attach, html = html, pre = pre, 
                     custom_headers = custom_headers, sender_name=sender_name)
    ec.set_account_credentials(username = username, password = password)
    ec.run()


class EmailClient(object):
    
    def __init__(self, recipient, subject, message, 
                 cc = None, bcc = None, reply_to = None, 
                 attach = None, html = None, pre = False, 
                 custom_headers = None, 
                 sender_name = None
                 ):
        self.recipient = recipient
        self.subject = subject
        self.message = message
        self.cc = cc
        self.bcc = bcc
        self.reply_to = reply_to
        self.attach = attach
        self.html = html
        self.pre = pre
        self.custom_headers = custom_headers
        self.sender_name = sender_name 
        
        
        
    
        if self.message.find("<html>")>=0:
            self.html = self.message
    
    
        self.msg = None
    
    
    def set_account_credentials(self, username, password):
        
        self.username = username # also used to define who the email is from! (line 70)
        self.password = password
        
    
    def run(self):
        self.setup_email()
        self.send_email()
        
    def setup_email(self):
        recipient = self.recipient
        subject = self.subject
        message = self.message
        cc = self.cc
        bcc = self.bcc
        reply_to = self.reply_to
        attach = self.attach
        html = self.html
        pre = self.pre
        custom_headers = self.custom_headers
        
        
        
        
        msg = MIMEMultipart()
    
        sender_name = self.sender_name
        if sender_name == None:
            sender_name = self.username


        msg['From'] = sender_name
        msg['To'] = recipient
        msg['Subject'] = subject
     
        text = message
        to = [recipient]
        
        if cc:
            # cc gets added to the text header as well as list of recipients
            if type(cc) in [str, unicode]:
                msg.add_header('Cc', cc)
                cc = [cc]
            else:
                cc = ', '.join(cc)
                msg.add_header('Cc', cc)
            to += cc
     
        if bcc:
            # bcc does not get added to the headers, but is a recipient
            if type(bcc) in [str, unicode]:
                bcc = [bcc]
            to += bcc
     
        if reply_to:
            msg.add_header('Reply-To', reply_to)
     
        # Encapsulate the plain and HTML versions of the message body in an
        # 'alternative' part, so message agents can decide which they want to
        # display.
     
        if pre:
            html = "<pre>%s</pre>" % text
        if html:
            msgAlternative = MIMEMultipart('alternative')
            msg.attach(msgAlternative)
     
            msgText = MIMEText(text)
            msgAlternative.attach(msgText)
     
            # We reference the image in the IMG SRC attribute by the ID we give it
            # below
            msgText = MIMEText(html, 'html')
            msgAlternative.attach(msgText)
        else:
            msg.attach(MIMEText(text))
     
        if attach:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(open(attach, 'rb').read())
            Encoders.encode_base64(part)
            part.add_header('Content-Disposition',
                            'attachment; filename="%s"' % os.path.basename(attach))
            msg.attach(part)
     
        if custom_headers:
            for k, v in custom_headers.iteritems():
                msg.add_header(k, v)

        self.to = to
        self.msg = msg


    def send_email(self):
        
        if self.username == None or self.password == None:
            raise ValueError('need to st account credentials')
        
        if self.msg:
            mailServer = smtplib.SMTP("smtp.gmail.com", 587)
            mailServer.ehlo()
            mailServer.starttls()
            mailServer.ehlo()
            mailServer.login(self.username, self.password)
         
            mailServer.sendmail(self.username, self.to, self.msg.as_string())
            # Should be mailServer.quit(), but that crashes...
            mailServer.close()
        
        else:
            raise Exception('Please setup the email first!')

if __name__ == '__main__':
    

    message = '<html><h1>this is an email!<h1><html>'
    username = 'info@chaienergy.net'
    password = 'myChaiInfo89'
    subject= 'test12'
    
    recipient = 'ka@chaienergy.net'
    bcc = None
    sender_name = "Sender Name"
    
    send_email(username = username, password = password, subject='te', message=message,  recipient = recipient, bcc = bcc, sender_name = sender_name)