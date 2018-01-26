# coding: utf-8

# flake8: noqa

"""
    Tts API

    Description  # noqa: E501

    OpenAPI spec version: 2.0.0
    Contact: cloudsupport@telestream.net
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


from __future__ import absolute_import

# import apis into sdk package
from telestream_cloud_tts.api.tts_api import TtsApi

# import ApiClient
from telestream_cloud_tts.api_client import ApiClient
from telestream_cloud_tts.configuration import Configuration
# import models into sdk package
from telestream_cloud_tts.models.corpora_collection import CorporaCollection
from telestream_cloud_tts.models.corpus import Corpus
from telestream_cloud_tts.models.error_response import ErrorResponse
from telestream_cloud_tts.models.extra_file import ExtraFile
from telestream_cloud_tts.models.fragment import Fragment
from telestream_cloud_tts.models.fragment_variant import FragmentVariant
from telestream_cloud_tts.models.job import Job
from telestream_cloud_tts.models.job_result import JobResult
from telestream_cloud_tts.models.jobs_collection import JobsCollection
from telestream_cloud_tts.models.project import Project
from telestream_cloud_tts.models.projects_collection import ProjectsCollection
from telestream_cloud_tts.models.result import Result
from telestream_cloud_tts.models.upload_session import UploadSession
from telestream_cloud_tts.models.video_upload_body import VideoUploadBody
from .models.uploader import Uploader