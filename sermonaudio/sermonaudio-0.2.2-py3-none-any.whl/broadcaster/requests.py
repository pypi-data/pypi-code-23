import base64
import requests
from sermonaudio import get_base_url, get_request_headers, session
from posixpath import join as posixjoin

URL_PATH_BROADCASTER = 'broadcaster'


def create_sermon(full_title: str,
                  speaker_name: str,
                  preach_date: str,
                  accept_additional_charges: bool,
                  display_title: str = None,
                  subtitle: str = '',
                  bible_text: str = '',
                  more_info_text: str = '',
                  event_type: str = 'Sunday Service',
                  language_code: str = 'en',
                  keywords: str = ''):
    """Creates a sermon record."""
    data = {
        'acceptAdditionalCharges': accept_additional_charges,
        'fullTitle': full_title,
        'displayTitle': display_title,
        'subtitle': subtitle,
        'speakerName': speaker_name,
        'preachDate': preach_date,
        'bibleText': bible_text,
        'eventType': event_type,
        'languageCode': language_code,
        'moreInfoText': more_info_text,
        'keywords': ' '.join(keywords)
        }

    broadcaster_create_endpoint = 'create_sermon'

    url = posixjoin(get_base_url(), URL_PATH_BROADCASTER, broadcaster_create_endpoint)

    r = session.post(url, data=data, headers=get_request_headers())

    response_json = r.json()

    if 'errors' in response_json:
        return False, str(response_json), None
    else:
        message = response_json['message'] if 'message' in response_json.keys() else None
        return response_json['success'], message, response_json['sermonID']


def upload_audio(sermon_id: str,
                 filename,
                 file_content):  # pragma: no cover
    """Attaches audio to a sermon.

    Pass in a bytes-like object for file content. The result is automatically encoded."""

    data = {'sermonID': sermon_id,
            'filename': filename,
            'fileData': base64.b64encode(file_content).decode('utf-8')
            }

    broadcaster_upload_endpoint = 'upload_audio'
    url = posixjoin(get_base_url(), URL_PATH_BROADCASTER, broadcaster_upload_endpoint)

    r = session.post(url,
                     json=data,
                     headers=get_request_headers())
    
    return r.status_code == 200
