import traceback
from concurrent import futures

from netboy.curl.boy import CurlBoy
from netboy.selenium.chrome.boy import ChromeBoy as SeleniumChromeBoy
from netboy.chrome.boy import ChromeBoy
from netboy.util.aop_wrapper import pre_process, post_process
from netboy.util.grouper import grouper_it
from netboy.util.payload import Payload


class Boy:
    def __init__(self, **kwargs):
        pass

    def run(self, payload):
        pass

    def get(self, url, **kwargs):
        pass

    def post(self, url, **kwargs):
        pass

    def close(self):
        pass


class ConcurrentBoy:
    def run(self, payload):
        data = payload.get('data')
        info = payload.get('info')
        mode = info.get('mode', 'normal')
        if 'multi' in mode or 'process' in mode or 'thread' in mode:
            return self._run_multi(data, info, mode)
        return self._run_simple(data, info)

    def run1(self, payload):
        payload = {
            'selenium': SeleniumChromeBoy,
            'chrome': ChromeBoy,
            'curl': CurlBoy
        }
        spider = payload.get('spider')
        payload = pre_process(payload)
        url = payload.get('url')
        # mode = payload.get('mode', 'quick')
        if not url:
            return None
        a = spider()
        r = a.run(payload)
        r = post_process(payload, r)
        a.close()
        return r

    def _run_multi(self, data, info, mode='process'):
        results = []
        for chunked_data in grouper_it(data, info.get('chunk_size', 10)):
            result = self._run(chunked_data, info, mode)
            results.extend(result)
        return results

    def _run_simple(self, data, info):
        results = []
        for chunked_data in grouper_it(data, 4):
            info['max_workers'] = 2
            result = self._run(chunked_data, info, 'thread')
            results.extend(result)
        return results

    def _run(self, data, info, mode='process'):
        Executor = futures.ThreadPoolExecutor if 'thread' in mode else futures.ProcessPoolExecutor
        results = []
        with Executor(max_workers=info.get("max_workers")) as executor:
            future_to_url = {}
            for i, payload in enumerate(data):
                d = {'url': payload} if type(payload) is str else payload
                # d.update(info)
                Payload.update(d, info, ['max_workers, chunk_size'])
                future_to_url[executor.submit(self.run1, d)] = d

            for future in futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    data = future.result()
                except Exception as exc:
                    print('%r generated an exception: %s' % (url, exc))
                    traceback.print_tb(exc.__traceback__)
                else:
                    results.append(data)
        return results

    def view(self, results, filters):
        scene = []
        for result in results:
            updated = {key: result.get(key) for key in filters}
            scene.append(updated)
        return scene
