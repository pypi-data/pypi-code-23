#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 Truong Do <truongdq54@gmail.com>
#
from __future__ import print_function
import os
import kivy
kivy.require('1.0.6')  # replace with your current kivy version !

from kivy.uix.floatlayout import FloatLayout
from kivy.app import App
from kivy.properties import ObjectProperty, StringProperty
from kivy.core.window import Window
import sys
if sys.version_info[0] < 3:
    import vais
else:
    import vaisdemo.vais as vais
import threading
from multiprocessing import Process
from kivy.lang import Builder

Window.clearcolor = (1, 1, float(204) / 255, 1)
# add the following 2 lines to solve OpenGL 2.0 bug
from kivy import Config
Config.set('graphics', 'multisamples', '0')
root_dir = os.path.dirname(os.path.abspath(__file__))
Builder.load_file(os.path.join(root_dir, "controller_video.kv"))
class Controller(FloatLayout):
    '''Create a controller that receives a custom widget from the kv lang file.

    Add an action to be called from the kv lang file.
    '''
    asr_result = StringProperty()
    video_player_wid = ObjectProperty()
    asr_thread = None

    def run_asr(self):
        def on_result(output, is_final):
            if output:
                words = output.split()
                if len(words) > 15:
                    e = 0
                    new_words = []
                    for s in range(0, len(words), 15):
                        e = s + 15
                        new_words.append(" ".join(words[s:e]))
                    output = "\n".join(new_words)
            if output:
                self.asr_result = output
        with vais.VaisService("demo") as self.vais_engine:
            self.vais_engine.asr_callback = on_result
            self.vais_engine.asr()
        print("ASR stopped")

    def play_video(self):
        self.asr_result = "ASR started"
        self.video_player_wid.state = 'play'
        if self.asr_thread:
            self.vais_engine.capture._interrupt = True
        self.asr_thread = threading.Thread(target=self.run_asr)
        # self.asr_thread = Process(target=self.run_asr)
        self.asr_thread.start()

    def stop_video(self):
        if self.asr_thread:
            self.vais_engine.capture._interrupt = True
        self.asr_result = "Asr stopped"
        self.video_player_wid.state = 'pause'


class ControllerApp(App):

    def build(self):
        return Controller(asr_result='Choose one action below')

def main():
    ControllerApp().run()

if __name__ == '__main__':
    main()
