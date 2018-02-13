from util import build_headers


class AbstractApi:
    def get_headers(self):
        header_raw = '''
            Host: %s
            Connection: keep-alive
            Content-Length: 19542
            X-CSRF-Token:
            Origin: http://%s
            X-Requested-With: XMLHttpRequest
            User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36
            Content-Type: application/json; charset=UTF-8;
            Accept: */*
            Referer: http://%s/
            Accept-Encoding: gzip, deflate
            Accept-Language: ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7
            Cookie: %s
        ''' % (self.domain, self.domain, self.domain, self.cookie)

        return build_headers(header_raw)