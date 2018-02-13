import requests_mock
import prequest

url = 'https://data.boston.gov/'
url2 = 'https://foo.bar/'


def test_get_success_returns_200():
    with requests_mock.Mocker() as m:
        m.get(url, text='resp')
        m.get(prequest.Prequest.PARENT_API_URL.format(url, False))
        resp = prequest.get(url)

        assert resp.text == 'resp'
        assert resp.status_code == 200


def test_prequest_get_success_calls_aws_with_correct_url():
    with requests_mock.Mocker() as m:
        m.get(url)
        m.get(prequest.Prequest.PARENT_API_URL.format(url, False))
        prequest.get(url)
        last_request = m.last_request

        assert last_request.url == prequest.Prequest.PARENT_API_URL.format(url, False)


def test_only_get_calls_aws():
    with requests_mock.Mocker() as m:
        m.put(url)
        m.post(url)
        m.delete(url)
        m.get(prequest.Prequest.PARENT_API_URL.format(url, False))

        prequest.put(url)
        prequest.post(url)
        prequest.delete(url)

        assert m.call_count == 3


def test_get_404_calls_cache():
    with requests_mock.Mocker() as m:
        m.get(url, status_code=404)
        m.get(prequest.Prequest.PARENT_API_URL.format(url, True), json={'url': url2})
        m.get(url2)
        resp = prequest.get(url)

        assert resp.url == url2
        assert resp.status_code == 200


def test_get_500_calls_cache():
    with requests_mock.Mocker() as m:
        m.get(url, status_code=500)
        m.get(prequest.Prequest.PARENT_API_URL.format(url, True), json={'url': url2})
        m.get(url2)
        resp = prequest.get(url)

        assert resp.url == url2
        assert resp.status_code == 200


def test_get_fail_and_cache_fail_returns_original_resp():
    with requests_mock.Mocker() as m:
        m.get(url, status_code=500)
        m.get(prequest.Prequest.PARENT_API_URL.format(url, True), json={'url': url2}, status_code=404)
        m.get(url2)
        resp = prequest.get(url)

        assert resp.url == url
        assert resp.status_code == 500
