
import socket

if socket.gethostname() == 'arch':
    from djangoforandroid.framework.views import BrythonView as PostHandler
else:
    from djangoforandroid.framework.brython.wsgi_handler import BrythonPostHandler as PostHandler


#from django.core import serializers
#from django.conf import settings

import json

#from .models import PitonCell
import os
import socket


########################################################################
class Brython(PostHandler):
    """"""



    #----------------------------------------------------------------------
    def get_config(self):
        """"""

        #config = PitonConfig.objects.all().first()

        #if config is None:
            #config = PitonConfig()
            #config.save()

        return {}


    #----------------------------------------------------------------------
    def cells(self):
        """"""
        return []
        #return json.loads(serializers.serialize("json", PitonCell.objects.all()))



    #----------------------------------------------------------------------
    def save_cell(self, pk=None, code=''):
        """"""
        #try:
            #cell = PitonCell.objects.get(pk=pk)
        #except:
            #cell = PitonCell()

        #code = code.replace('\\\\n', '\n')
        #cell.code = code

        #cell.save()
        #return cell.pk
        return 0


    #----------------------------------------------------------------------
    def save_ide(self, path, code):
        """"""

        with open(os.path.join(*path), 'wb') as file:
            code = code.replace('\\\\n', '\n')
            file.write(code.encode())
            file.close()



    #----------------------------------------------------------------------
    def remove_cell(self, pk):
        """"""
        #try:
            #cell = PitonCell.objects.get(pk=pk)
            #cell.delete()

        #except:
            #pass


    #----------------------------------------------------------------------
    def path(self):
        """"""
        #startpath = settings.APP_DIR
        startpath = self.get_path()

        tree = []
        for root, dirs, files in os.walk(startpath):
            level = root.replace(startpath, '').count(os.sep)
            files = list(filter(lambda e:e.endswith(".py"), files))
            if files:
                tree.append((level, os.path.basename(root), files, root))

        return tree

    #----------------------------------------------------------------------
    def get_path(self):
        """"""


        paths = [
            '/storage/emulated/0',
            '/storage/emulated/legacy',
            '/sdcard',
            '.',
        ]

        APP_DIR = None
        for path in paths:
            if os.path.exists(path):
                APP_DIR = "{}/{}".format(path, 'Scientific-Python')
                APP_DIR = os.path.abspath(APP_DIR)
                try:
                    os.makedirs(APP_DIR, exist_ok=True)
                    break
                except:
                    pass

        #return ""
        return APP_DIR



    #----------------------------------------------------------------------
    def read(self, path, filename):
        """"""
        with open(os.path.join(path, filename), 'rb') as file:
            code = file.read()
        return code.decode()


    #----------------------------------------------------------------------
    def new_file(self, path, filename):
        """"""
        file = open(os.path.join(path, filename), 'wb')
        file.close()


    #----------------------------------------------------------------------
    def get_examples(self):
        """"""
        from .examples import snippets
        return {s['name']:s for s in snippets}


    #----------------------------------------------------------------------
    def local_ip(self):
        """"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('yeisoncardona.com', 0))
            return s.getsockname()[0]
        except:
            return None