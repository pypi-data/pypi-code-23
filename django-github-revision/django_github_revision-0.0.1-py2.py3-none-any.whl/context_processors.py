from github_revision.utils import get_backend, get_url


def github_revision(request=None):
    backend = get_backend()
    revision_id = backend()
    url = get_url(revision_id)
    return {'github': {'url': url,
                       'revision_id': revision_id}}
