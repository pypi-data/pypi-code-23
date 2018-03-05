""" email sending 
"""

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib


def email(FROM,
          TO,
          subject="",
          text="",
          html="",
          SMTP='127.0.0.1',
          LOGIN=[],
          sender="",
          replyto="",
          attachments={}):
    """send a multipart plain text (or html) message, using given SMTP
  - Optional LOGIN (ie SMTP validation) must give (<user>,<password>)
  - allows for a list of recipients in TO: each gets a separate email, ie bcc

  - attachment expects a dictionary of {filename:content}
  """
    if not (FROM and TO and SMTP):
        #   print "EMAIL DISABLED >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
        return  # email is disabled or invalid, so do nothing
    # set up our message
    root = MIMEMultipart('related')
    root['Subject'] = subject
    if sender:
        root['From'] = '"%s" <%s>' % (sender, FROM)
    else:
        root['From'] = FROM
    if replyto:
        root['Reply-To'] = replyto
    if isinstance(TO, str):
        TO = [TO]
    root.preamble = 'This is a multi-part message in MIME format.'
    # add our alternative versions
    alt = MIMEMultipart('alternative')
    root.attach(alt)
    if html:
        alt.attach(MIMEText(html, 'html'))
    else:
        alt.attach(MIMEText(text))

    # include attachments
    for filename, content in list(attachments.items()):
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(content)
        encoders.encode_base64(part)
        part.add_header('Content-Disposition',
                        'attachment; filename=%s' % filename)
        root.attach(part)

    # send our message(s)
    try:
        smtp = smtplib.SMTP()
        smtp.connect(SMTP)
        if LOGIN:
            smtp.login(*LOGIN)
        for t in TO:
            try:
                root['To'] = t
                smtp.sendmail(FROM, t, root.as_string())
                #        print "SENT: FROM=",FROM,' TO=',t,' ROOT=', root.as_string()
                del root[
                    'To']  # need to del this, as the message class __setitem__ appends rather than replaces
            except:
                print("SENDMAIL REFUSAL: FROM=", FROM, ' TO=', t, ' ROOT=',
                      root.as_string())
        smtp.quit()
    except:
        print("SMTP CONNECT ERROR: FROM=", FROM, ' TO=', TO, ' ROOT=',
              root.as_string())
