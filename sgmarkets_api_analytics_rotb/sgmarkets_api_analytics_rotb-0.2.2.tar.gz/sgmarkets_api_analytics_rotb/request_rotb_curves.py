
from timeit import default_timer as timer
from IPython.display import Markdown

from ._util import Util
from .response_rotb_curves import ResponseRotbCurves


class RequestRotbCurves:
    """
    """

    def __init__(self):
        """
        """
        dic_url = {'base_url': 'https://analytics-api.sgmarkets.com',
                   'service': '/rotb',
                   'endpoint': '/v1/curves'}
        self.url = Util.build_url(dic_url)

    def info(self):
        """
        """
        md = """
A RequestRotbCurves object has the properties:
+ `url`: {}

and the methods:
+ `call_api()` to make the request to the url
        """.format(self.url)
        return Markdown(md)

    def call_api(self,
                 api,
                 debug=False):
        """
        See https://analytics-api.sgmarkets.com/rotb/swagger/ui/index#!/Curves/Curves_Curves
        """
        t0 = timer()
        print('calling API...')
        raw_response = api.get(self.url)
        t1 = timer()
        print('done in {:.2f} s'.format(t1 - t0))
        if debug:
            print('*** START DEBUG ***\n{}\n*** END DEBUG ***'.format(raw_response))
        response = ResponseRotbCurves(raw_response)
        return response
