try:
    from functools import lru_cache
except Exception:
    from functools32 import lru_cache


@lru_cache()
def sha():
    from menhir.gitutils import head_commit, sha
    return sha(head_commit(repo()))


@lru_cache()
def branch():
    from menhir.gitutils import branch
    return branch(repo())


@lru_cache()
def repo():
    from menhir.gitutils import repo
    return repo()


def image(info, path):
    repo = info.get('docker', {}).get('repository')
    if repo:
        return '%s/%s:%s' % (
            repo,
            info['project-name'],
            sha()
        )
