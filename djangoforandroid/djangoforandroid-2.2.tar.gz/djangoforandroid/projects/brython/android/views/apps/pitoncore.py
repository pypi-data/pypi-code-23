from browser import document, html
from websocket import WebSocket
import random
import json

from datetime import datetime


########################################################################
class PitonCore(WebSocket):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """"""

        ip_list = ["localhost:8888",
                   "piton.yeisoncardona.com",
                   "piton.yeisoncardona.com:8888",
                   "104.131.123.113",
                   "104.131.123.113:8888"]

        self.ip_list = ["ws://{}/ws".format(ip) for ip in ip_list]

        self.user_id = "".join([random.choice(list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')) for i in range(32)])

        super().__init__(self.ip_list.pop(0))


    #----------------------------------------------------------------------
    def on_message(cls, evt):
        """"""
        data = json.loads(evt.data)

        if hasattr(cls, "piton_{}".format(data['type'])):
            getattr(cls, "piton_{}".format(data['type']))(data)

        else:
            print("No {}".format("piton_{}".format(data['type'])))


        #eval("cls.piton_#{result.type}(cls, result)")


        #if data.get('type', None) == 'log':
            #if data.get('message', None) == 'tornado_ok':
                #print("registering...")
                #cls.send("register;{}".format(cls.user_id))

            #else:
                #print(data['message'])

        print(data)


    #----------------------------------------------------------------------
    def piton_log(cls, data):
        """"""
        if data.get('message', None) == 'tornado_ok':
            print("registering...")
            cls.send("register;{}".format(cls.user_id))

        else:
            print(data['message'])


    #----------------------------------------------------------------------
    def piton_out(self, data):
        """"""
        id = data['id']
        out = data['out']

        if out:
            code_out = document.select(".piton-stdout-{}".format(id))[0]
            code_out.text = out
            code_out.style = {'display': 'block',}


        parent_images = document.select("#codeblock-block-{} .image-out".format(id))[0]
        if data['image']:

            if not data['animation']:

                for image_id in data['images_id']:

                    src = "http://{}/image.jpeg?id={}&user={}&{}".format(self.ip, image_id, self.user_id, datetime.now().timestamp())
                    img = html.IMG(Class="piton-plot".format(id), src=src, crossOrigin='anonymous')
                    parent_images <= img


            elif data['animation']:
                for image_id in data['images_id']:

                    src = "http://{}/animation.mp4?id={}&user={}&{}".format(self.ip, image_id, self.user_id, datetime.now().timestamp())

                    #html = "<img crossOrigin='anonymous' class='image-out image-out-#{id} image-zoom' src='#{src}'>"
                    #html = "<video crossOrigin='anonymous' class='image-out image-out-#{id} image-zoom' style='width: 100%;' autoplay loop muted>
                    #<source src='#{src}' type='video/mp4'>
                    #</video>"

                    img = html.VIDEO(Class="piton-plot", autoplay=True, loop=True, muted=True, crossOrigin='anonymous')
                    img <= html.SOURCE(src=src, type='video/mp4')


                    #$(".editor-container-#{id} .code-out .image-out-placeholder").before(html)


                    parent_images <= img



    #----------------------------------------------------------------------
    def on_close(cls, evt):
        """"""
        super().__init__(cls.ip_list.pop(0))


    #----------------------------------------------------------------------
    def interprete(cls, code="", id=0):
        """"""
        parent_images = document.select("#codeblock-block-{} .image-out".format(id))[0]
        parent_images.html = ''

        cls.send("interprete;{};{}".format(id, code))
