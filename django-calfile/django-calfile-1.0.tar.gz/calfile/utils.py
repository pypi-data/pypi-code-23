import datetime
import vobject
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from email.mime.text import MIMEText

def convert_date(date_str):
    if not date_str:
        raise KeyError(_("Date parameter is missing!"))

    try:
        return datetime.datetime.strptime(date_str, settings.CALFILE_DF)
    except ValueError:
        raise ValueError(_(f"Could not convert parameter to date! data:{date_str}, format:{settings.CALFILE_DF}"))

    return None


def get_cal_serialize_file(start_date_str:str, end_date_str:str, summary="Summary"):
    start_date = convert_date(start_date_str)
    end_date = convert_date(end_date_str)
    cal = vobject.iCalendar()
    cal.add('method').value = 'PUBLISH'
    vevent = cal.add('vevent')
    vevent.add('dtstart').value = start_date
    vevent.add('dtend').value = end_date
    vevent.add('summary').value = summary
    vevent.add('uid').value = '1'
    vevent.add('dtstamp').value = datetime.datetime.now()
    
    return cal.serialize()


def get_part(start_date, end_date, summary="Summary", filename="calfile"):
    part = MIMEText(get_cal_serialize_file(start_date, end_date, summary), 'calendar')
    part.add_header('Filename', f'{filename}.ics')
    part.add_header('Content-Disposition', f'attachment; filename={filename}.ics')
    return part
