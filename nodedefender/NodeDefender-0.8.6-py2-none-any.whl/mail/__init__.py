from flask_mail import Mail
import logging
import NodeDefender
import NodeDefender.mail.decorators
import NodeDefender.mail.user
import NodeDefender.mail.group
import NodeDefender.mail.node
import NodeDefender.mail.icpe

logger = logging.getLogger(__name__)
logger.setLevel("INFO")

enabled = False

mail = Mail()

def load(app, loggHandler):
    global enabled
    mail.init_app(app)
    logger.addHandler(loggHandler)
    enabled = NodeDefender.config.mail.enabled()
    logger.info("Mail Service Enabled")
    return True

