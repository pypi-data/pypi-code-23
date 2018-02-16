import calendar
from datetime import datetime


class Formatter:
    @staticmethod
    def format_slack_message(notebook_paragraphs):
        d = datetime.utcnow()
        unixtime = calendar.timegm(d.utctimetuple())
        msg_format = {
            "username": "Zeppelin-handy-helpers",
            "icon_emoji": ":zhh:",
            "attachments": [
                {
                    "fallback": "Scheduling job notification",
                    "color": "#36a64f",
                    "fields": [],
                    "footer": "Message provided by zeppelin_handy_helpers",
                    "ts": unixtime
                }
            ]
        }
        for n in notebook_paragraphs:
            msg_format['attachments'][0]['fields'].append(
                {'value': 'for notebook_id: ' + str(n[0]) + ' paragraph_id: ' + str(n[1]),
                 'title': 'execution ' + str(n[2]),
                 'short': False})
        return msg_format
