from __future__ import print_function
import sys
import httplib2
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

import os
import pytz

BASE_DIR = os.path.dirname(os.path.realpath(sys.argv[0]))
CLIENT_SECRET_FILE = 'calender_key.json' 
SCOPES = 'https://www.googleapis.com/auth/calendar'
scopes = [SCOPES]
APPLICATION_NAME = 'Google Calendar API Python'
    

class google_calendar_api:

    def build_service(self):
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            CLIENT_SECRET_FILE,
            SCOPES
            )
        
        http = credentials.authorize(httplib2.Http())

        service = build('calendar', 'v3', http=http, cache_discovery=False)

        return service


    def create_event(self, calendar_id, start, end, desc, ):

        service = self.build_service()
        event = service.events().insert(calendarId=calendar_id, body={
            'description':desc,
            'summary':desc,
            'start':{'dateTime':  start},
            'end':{'dateTime':  end},
        }).execute()
        return event['id']


    def update_event(self,calendar_id, event_id, start, end, desc):
        service = self.build_service()
        try:
            event = service.events().get(calendarId=calendar_id, eventId=event_id).execute()
        except HttpError as e:
            if e.resp.status==404:
                return self.create_event(calendar_id, start, end, desc)
        event["start"]={'dateTime':start}
        event["end"]={'dateTime':end}
        event["summary"]= desc
        event["description"]= desc
        updated_event = service.events().update(calendarId=calendar_id, eventId=event['id'], body=event).execute()
        return updated_event["id"]
