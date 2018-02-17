import json
import requests

from commons import BASE_URL
from requests import ConnectionError


def store_chat_details_in_solr(param, message):

      data                 = param
      data["sender"]       = message.sender.username
      data["receiver"]     = message.receiver.username
      data["message_text"] = message.message_text
      data["message_id"]   = message.id
      data["created_date"] = message.created_at.strftime("%Y-%m-%dT%H:%M:%SZ")
      data["updated_date"] = message.updated_at.strftime("%Y-%m-%dT%H:%M:%SZ")

      if message.attachment:
            if message.attachment.attachment:
                  data["attachment"]       = message.attachment.attachment.url
                  data["asset_type"]       = message.attachment.asset_type
                  data["name"]             = message.attachment.name
            if message.attachment.cover_photo:
                  data["cover_photo"]      = message.attachment.cover_photo.url
                  data["cover_photo_name"] = message.attachment.cover_photo_name
            data["attachment_id"]    = message.attachment.id

      upload_chat_url = BASE_URL + "api/upload/chat/"

      try:
          response_data = requests.post(url=upload_chat_url,
              data=json.dumps(data),
              headers={"Content-Type": "application/json"})
      except ConnectionError as ce:
            pass

      return True
