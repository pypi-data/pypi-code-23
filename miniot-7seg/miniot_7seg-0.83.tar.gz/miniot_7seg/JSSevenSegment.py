# -*- coding: utf-8 -*-
"""
Jupyter NotebookにJavaScriptベースの4桁
7セグディスプレイを表示するクラス


Author:  Atsushi Shibata
         shibata@m-info.co.jp
Licence: MIT

Copyright (c) 2017 Atsushi Shibata
"""


import os
import ipywidgets as widgets
from IPython.display import display, Javascript


class JS_7segdisplay:
    """
    JavaScriptベースの7セグディスプレイを
    Jupyter Notebook内に表示，コントロールするクラス
    """
    COUNTER = 0

    _led_body = """<div id="led_body{0}" style="width: 50%;"></div>"""


    _initialize_template = """
    {0}
    $("#led_body{1}").sevenSeg({{ digits:4, value: '    ' }});
    """

    _turn_template = """
    $("#led_body{0}").sevenSeg({{ '{1}': {2} }});
    """


    def __init__(self):
        """
        クラスを初期化する。7セグディスプレイの表示内容を
        リストとしてアトリビュートに保持
        """

        # 右端から，各桁の表示内容を保持するリスト
        self.segments = [0, 0, 0, 0]


    def check_availability(self):
        """
        互換性保持用のメソッド。常にTrueを返す
        """
        return True


    def init_display(self):
        """
        ディスプレイを初期化する
        全てのLEDを消灯した状態でディスプレイを表示
        """
        # モジュールのベースディレクトリを取得
        based = os.path.dirname(__file__)

        # knockout-jsを読み込み
        # JSの実体のパスを取得
        jspath = os.path.join(based, 'js/knockout-2.2.1.js')
        knockout = open(jspath).read()
        display(Javascript(knockout))

        # ID用のカウンタを増加
        self.COUNTER += 1

        # LED用のエレメントを表示
        display(widgets.HTML(self._led_body.format(self.COUNTER)))

        # JSの実体のパスを取得
        jspath = os.path.join(based, 'js/sevenSeg.js')
        sevenseg = open(jspath).read()

        # LED用のエレメントを表示
        jsbody = self._initialize_template.format(sevenseg, self.COUNTER)
        display(Javascript(jsbody))


    def turn_on(self, position):
        """
        7セグディスプレイのLEDを個別に点ける
        positionに値を与えて，位置を指定する
        点灯済みのLEDを指定してもなにも起こらない
        右の桁からはじめて，0から7までで1つの桁のAからDPまでを
        指定する
        8が二桁目のA，35までの数値を指定する
        """
        jsbody = self._turn_template.format(self.COUNTER, 'on', position)
        display(Javascript(jsbody))


    def turn_off(self, position):
        """
        7セグディスプレイのLEDを個別に消す
        positionの扱いはturn_on()と同じ
        消灯済みのLEDを指定してもなにも起こらない
        """
        jsbody = self._turn_template.format(self.COUNTER, 'off', position)
        display(Javascript(jsbody))


