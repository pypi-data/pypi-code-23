# sample to send emails

import smtplib
from email.message import EmailMessage

            msg = EmailMessage()
            msg.set_content(txt)
            msg['Subject'] = subject
            msg['To'] = self.mailto
            msg['From'] = self.mailfrm
            s = smtplib.SMTP('localhost')
            s.send_message(msg)
            s.quit()

