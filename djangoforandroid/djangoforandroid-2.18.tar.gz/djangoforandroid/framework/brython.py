import json
import cgi

########################################################################
class BrythonPostHandler:
    """"""

    #----------------------------------------------------------------------
    def __new__(self, environ, start_response):
        """"""

        if not environ['REQUEST_METHOD'] == 'POST':
            return b''

        post_env = environ.copy()
        post_env['QUERY_STRING'] = ''
        post = cgi.FieldStorage(
            fp=environ['wsgi.input'],
            environ=post_env,
            keep_blank_values=True
        )

        name = post['name'].value
        args = eval(post['args'].value)
        kwargs = eval(post['kwargs'].value)


        if name:
            v = getattr(self, name)(self, *args, **kwargs)

            #if isinstance(v, dict):
                #return JsonResponse(v)
            #else:
            if v is None:
                data = json.dumps({'__D4A__': 0,})
            #if v in [False, True]:
                #return JsonResponse({'__D4A__': int(v),})
            else:
                data = json.dumps({'__D4A__': v,})

        start_response('200 OK', [('Content-Type', 'aplication/json')])
        return [data.encode('utf-8')]


    #----------------------------------------------------------------------
    def test(self):
        """"""
        return 'ok'



#from django.http import JsonResponse
#from django.views.generic import View
#import datetime
#from djangoforandroid.framework.views import BrythonView


#from django.templatetags.static import static
#from django.urls import reverse


#########################################################################
#class Brython(BrythonView):
    #""""""

    ###----------------------------------------------------------------------
    ##def current_datetime(cls):
        ##now = datetime.datetime.now()
        ##return now


    ###----------------------------------------------------------------------
    ##def get_square(cls, a):
        ##""""""
        ##return a ** 2


    ##----------------------------------------------------------------------
    #def static(self, file):
        #""""""

        #return static(file)


    ##----------------------------------------------------------------------
    #def url(self, path):
        #""""""
        #return reverse(path)

