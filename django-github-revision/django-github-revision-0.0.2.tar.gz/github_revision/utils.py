from django.utils.module_loading import import_string

from github_revision import settings
from github_revision.settings import FORMAT_URL, REPO_URL, BRANCH


def get_backend():
    return import_string(settings.REVISION_BACKEND)


def get_url(revision_id):
    return FORMAT_URL.format(repo_url=REPO_URL, revision_id=revision_id, branch=BRANCH)
