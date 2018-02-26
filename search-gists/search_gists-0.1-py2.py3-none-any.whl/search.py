from gist_search.utils import get_gists


def search_gists(username, description=None, file_name=None):
    if not description and not file_name:
        print("At least one serach parameter must be specified")
        return

    gists = get_gists(username)
    if gists is None:
        print("Couldn't find gists for user: {}".format(username))
        return

    results = []
    for gist in gists:
        if description and description not in gist['description'].lower():
            continue
        if file_name:
            matched = False
            for fname, fbody in gist['files'].items():
                if file_name in fname:
                    matched = True
                    break
            if not matched:
                continue
        results.append(gist)

    return results
