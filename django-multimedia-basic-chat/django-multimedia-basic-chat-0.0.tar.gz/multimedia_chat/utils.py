import json
import requests
from rest_framework import status
from requests import ConnectionError
from rest_framework.response import Response
from commons import (
    BASE_URL,
    error_conf,
)
from cv360.mobile.opty import response_translator as rst


def get_chat_details(data,user):

    get_chat_detail_url = BASE_URL + "api/chat/data/"

    try:
        response_data = requests.post(url=get_chat_detail_url,
                                     data=json.dumps(data),
                                     headers={"Content-Type": "application/json"})
    except ConnectionError as ce:
        return Response(error_conf.UNABLE_TO_REACH_CORE,
                        status=status.HTTP_412_PRECONDITION_FAILED)

    if response_data.status_code == 200:
        return response_data.json()
