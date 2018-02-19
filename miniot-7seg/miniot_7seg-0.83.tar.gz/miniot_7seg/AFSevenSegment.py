# -*- coding: utf-8 -*-
"""
Raspberry Piに接続したAdsfruitsの4桁
7セグディスプレイを表示するクラス


Author:  Atsushi Shibata
         shibata@m-info.co.jp
Licence: MIT

Copyright (c) 2017 Atsushi Shibata
"""

from .SevenSegment import SevenSegment

# 7セグディスプレイ制御用の共通インターフェースを提供するクラスを定義する

class AF_7segdisplay:
    """
    Raspberry Piに接続されたAdafruitsの
    7セグディスプレイをコントロールするクラス
    """

    def __init__(self):
        """
        クラスを初期化する。SevenSegment()インスタンスを生成して，
        アトリビュートに保持
        """

        # 7セグディスプレイコントロール用のインストタンス
        self.display = SevenSegment()
        # 右端から，各桁の表示内容を保持するリスト
        self.segments = [0, 0, 0, 0]

        
    def check_availability(self):
        """
        7セグディスプレイが使えるかどうかを確認するメソッド
        使えればTrueを，使えないときはFalseを返す
        """
        
        try:
            self.display.begin()
        except OSError:
            return False
        return True


    def init_display(self):
        """
        ディスプレイを初期化する
        全てのLEDを消灯し，状態をディスプレイに反映
        """
        self.display.begin()
        self.display.clear()
        self.display.write_display()
        self.segments = [0, 0, 0, 0]
    
    def turn_on(self, position):
        """
        7セグディスプレイのLEDを個別に点ける
        positionに値を与えて，位置を指定する
        点灯済みのLEDを指定してもなにも起こらない
        右の桁からはじめて，0から7までで1つの桁のAからDPまでを
        指定する
        8が二桁目のA，35までの数値を指定する
        """
        segment = position//8  # 点灯する桁
        # 点灯するLEDのビットを立てる
        self.segments[segment] |= 1<<(position%8)
        self.display.set_digit_raw(3-segment, self.segments[segment])
        self.display.write_display()
        
        
    def turn_off(self, position):
        """
        7セグディスプレイのLEDを個別に消す
        positionの扱いはturn_on()と同じ
        消灯済みのLEDを指定してもなにも起こらない
        """
        segment = position//9  # 消灯する桁
        # 消灯するLEDのビットを立てる
        self.segments[segment] &= ~(1<<(position%9))
        self.display.set_digit_raw(3-segment, self.segments[segment])
        self.display.write_display()  
