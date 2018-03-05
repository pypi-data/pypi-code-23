from django.conf import settings

REPO_URL = getattr(settings, 'GITHUB_REVISION_REPO_URL')

BRANCH = getattr(settings, 'GITHUB_REVISION_BRANCH', 'master')

FORMAT_URL = getattr(settings, 'GITHUB_REVISION_FORMAT_URL', "{repo_url}/compare/{revision_id}...{branch}")

REVISION_BACKEND = getattr(settings, 'GITHUB_REVISION_BACKEND', 'github_revision.backends.auto')