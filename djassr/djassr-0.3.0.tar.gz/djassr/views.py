try:
    from urllib.parse import quote_plus
except ImportError:
    from urllib import quote_plus
import uuid
import os
import time

from django.conf import settings
from rest_framework import generics
import boto3

from . import serializers


_DEFAULT_EXPIRE = 60  # seconds
DEFAULT_EXPIRE = getattr(settings, 'DJASSR_DEFAULT_EXPIRE', _DEFAULT_EXPIRE)


class BaseGetSignature(generics.CreateAPIView):

    def __init__(self):
        s3_bucket = os.environ.get('S3_BUCKET', None)
        assert s3_bucket is not None, '''You must provide a bucket name, as an environment variable `S3_BUCKET`'''
        self._bucket_name = s3_bucket
        self._s3_client = boto3.client('s3')

    def _call_custom_post(self, data):
        try:
            self.custom_post(self.request, data)
        except NotImplementedError:
            pass

    def _get_expires(self, valid):
        return int(time.time() + int(valid))

    def _get_object_name_base(self, data):
        return data.get(self.object_name_key)

    def _get_signature(self, data, object_name, expires):
        params = {
            'Bucket': self._bucket_name,
            'Key': object_name,
        }
        params.update(self.get_params(data))
        url = self._s3_client.generate_presigned_url(
            self.client_method,
            ExpiresIn=expires,
            Params=params,
        )
        return url

    def _get_signed_url(self, data):
        return self.get_signed_url(*self._get_signed_url_base(data))

    def _get_signed_url_base(self, data):
        object_name = self.get_object_name(
            self._get_object_name_base(data)
        )
        expires = self.get_expires()
        signed_url = self._get_signature(data, object_name, expires)
        signed_url = {'signed_url': signed_url}
        return (data, signed_url, object_name)

    def custom_post(self, request, data):
        raise NotImplementedError("Must override custom_post")

    def get_expires(self):
        return self._get_expires(DEFAULT_EXPIRE)

    def get_object_name(self, object_name):
        return object_name

    def get_params(self, data, *args, **kwargs):
        return {}

    def get_signed_url(self, data, signed_url, object_name):
        return signed_url

    def create(self, request, *args, **kwargs):
        response = super(BaseGetSignature, self).create(request, *args, **kwargs)
        data = self._get_signed_url(response.data)
        self._call_custom_post(data)
        response.data.update(data)
        return response


class GetPUTSignature(BaseGetSignature):
    serializer_class = serializers.PUTSignatureSerializer

    ACL = 'private'
    client_method = 'put_object'
    object_name_key = 'file_name'

    def _get_acl(self):
        return self.ACL

    def _get_headers(self, mime_type):
        headers = {'content-type': mime_type}
        return headers

    def _get_mime_type(self, data):
        return data['mime_type']

    def _get_url(self, object_name):
        # url = self.url.format(self._bucket_name, object_name)
        # return url
        pass

    def get_object_name(self, object_name):
        new_file_name = str(uuid.uuid4())
        if object_name:
            new_file_name += '.' + object_name.split('.')[-1]

        object_name = quote_plus(new_file_name)
        return object_name

    def get_params(self, data):
        params = {}
        mime_type = self._get_mime_type(data)
        if mime_type is not None:
            params.update({'ContentType': mime_type})
        acl = self._get_acl()
        if acl is not None:
            params.update({'ACL': self.ACL})
        return params

    def get_signed_url(self, data, signed_url, object_name):
        signed_url.update({
            'headers': self._get_headers(self._get_mime_type(data)),
            'url': self._get_url(object_name),
            'object_name': object_name
        })
        return signed_url


class GetGETSignature(BaseGetSignature):

    serializer_class = serializers.GETSignatureSerializer

    client_method = 'get_object'
    object_name_key = 'object_name'
